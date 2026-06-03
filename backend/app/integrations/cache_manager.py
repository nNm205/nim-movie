"""In-memory cache manager for the AI Chatbot RAG feature.

Implements:
- ``CacheManager`` Protocol with ``get`` / ``set`` / ``delete`` /
  ``invalidate_pattern`` (Requirements 6.1-6.5).
- ``InMemoryCacheManager``: thread-safe dict with TTL, lazy expiry on
  ``get``, and a daemon background sweep thread that runs every
  ``sweep_interval_seconds`` (default 60s) to evict expired entries.
- ``set_with_metadata(key, value, ttl_seconds, metadata)`` so the retrieval
  cache can attach ``source_ids`` and be invalidated by a predicate when an
  Indexing_Job re-indexes those sources (Requirement 6.5).
- ``get_cache_manager()``: process-wide singleton factory.

Key conventions used by callers (documented for reference; the cache itself
treats keys as opaque strings):

- Embedding cache:  ``embed:{provider}:{sha256(text)}``                (TTL 3600s)
- Retrieval cache:  ``rag:retrieve:{provider}:{sha256(embedding)}:{k}`` (TTL 600s)
  Value typically = list of retrieved chunks; metadata =
  ``{"source_ids": [(source_type, source_id), ...]}``.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# Protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class CacheManager(Protocol):
    """Cache abstraction. In-memory now; can be swapped for Redis later."""

    def get(self, key: str) -> Any | None:
        """Return cached value for ``key`` or ``None`` if missing/expired."""
        ...

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Store ``value`` under ``key`` with a lifetime of ``ttl_seconds``."""
        ...

    def delete(self, key: str) -> None:
        """Remove ``key`` from the cache. No-op if absent."""
        ...

    def invalidate_pattern(
        self, predicate: Callable[[str, Any], bool]
    ) -> int:
        """Remove every entry where ``predicate(key, metadata)`` is truthy.

        For entries written via :meth:`InMemoryCacheManager.set_with_metadata`,
        the predicate receives the attached metadata dict. For entries written
        via plain :meth:`set`, the predicate receives an empty dict.

        Returns the number of entries removed by the predicate.
        """
        ...


# ---------------------------------------------------------------------------
# Internal entry representation
# ---------------------------------------------------------------------------


@dataclass
class _CacheEntry:
    value: Any
    expires_at: float  # monotonic clock seconds
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# In-memory implementation
# ---------------------------------------------------------------------------


class InMemoryCacheManager:
    """Thread-safe in-memory cache with TTL, lazy expiry, and periodic sweep.

    - All operations are guarded by a single ``threading.Lock``. Operations are
      O(1) for ``get`` / ``set`` / ``delete`` and O(n) for sweep / invalidate.
    - ``get`` performs lazy expiry: if the entry is past its TTL it is dropped
      and ``None`` is returned.
    - A daemon background thread wakes every ``sweep_interval_seconds`` and
      removes any expired entries to keep memory usage bounded for keys that
      are written but never read again. The thread is a daemon so it never
      blocks process exit; it can also be stopped explicitly via
      :meth:`shutdown`.
    """

    def __init__(self, sweep_interval_seconds: float = 60.0) -> None:
        self._store: dict[str, _CacheEntry] = {}
        self._lock = threading.Lock()
        self._sweep_interval = float(sweep_interval_seconds)
        self._stop_event = threading.Event()
        self._sweep_thread: Optional[threading.Thread] = None
        if self._sweep_interval > 0:
            self._start_sweep_thread()

    # -- background sweep ---------------------------------------------------

    def _start_sweep_thread(self) -> None:
        thread = threading.Thread(
            target=self._sweep_loop,
            name="InMemoryCacheManager-sweep",
            daemon=True,
        )
        thread.start()
        self._sweep_thread = thread

    def _sweep_loop(self) -> None:
        # ``Event.wait`` returns True when the event is set (shutdown),
        # False on timeout (one sweep interval elapsed).
        while not self._stop_event.wait(self._sweep_interval):
            try:
                self._sweep_expired()
            except Exception:
                # Swallow errors so the daemon thread never dies silently and
                # leaves the cache without periodic eviction.
                continue

    def _sweep_expired(self) -> int:
        now = time.monotonic()
        with self._lock:
            expired = [k for k, e in self._store.items() if e.expires_at <= now]
            for k in expired:
                del self._store[k]
            return len(expired)

    # -- core API -----------------------------------------------------------

    def get(self, key: str) -> Any | None:
        now = time.monotonic()
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            if entry.expires_at <= now:
                # Lazy expiry on get.
                del self._store[key]
                return None
            return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        if ttl_seconds <= 0:
            # Non-positive TTL means "do not cache" — drop any existing entry.
            self.delete(key)
            return
        expires_at = time.monotonic() + ttl_seconds
        with self._lock:
            self._store[key] = _CacheEntry(value=value, expires_at=expires_at)

    def set_with_metadata(
        self,
        key: str,
        value: Any,
        ttl_seconds: int,
        metadata: dict[str, Any],
    ) -> None:
        """Store a value alongside metadata used for predicate invalidation.

        Used by the RAG retrieval cache to attach ``source_ids`` so that when
        an :class:`IndexingJob` re-indexes a set ``S`` of sources it can call
        :meth:`invalidate_pattern` to drop every retrieval cache entry that
        references any ``(source_type, source_id) ∈ S`` (Requirement 6.5).
        """
        if ttl_seconds <= 0:
            self.delete(key)
            return
        expires_at = time.monotonic() + ttl_seconds
        # Defensive copy so callers mutating their dict don't corrupt cache state.
        meta_copy: dict[str, Any] = dict(metadata) if metadata else {}
        with self._lock:
            self._store[key] = _CacheEntry(
                value=value,
                expires_at=expires_at,
                metadata=meta_copy,
            )

    def delete(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def invalidate_pattern(
        self, predicate: Callable[[str, Any], bool]
    ) -> int:
        """Remove every entry where ``predicate(key, metadata)`` is truthy.

        ``metadata`` is the dict supplied to :meth:`set_with_metadata`, or an
        empty dict for entries written via plain :meth:`set`. Expired entries
        encountered during the scan are dropped but do not count toward the
        returned removal count, which reflects only predicate-driven removals.
        """
        now = time.monotonic()
        removed = 0
        with self._lock:
            keys_to_remove: list[str] = []
            expired_keys: list[str] = []
            for k, entry in self._store.items():
                if entry.expires_at <= now:
                    expired_keys.append(k)
                    continue
                try:
                    if predicate(k, entry.metadata):
                        keys_to_remove.append(k)
                except Exception:
                    # A faulty predicate must not corrupt the cache.
                    continue
            for k in expired_keys:
                del self._store[k]
            for k in keys_to_remove:
                del self._store[k]
            removed = len(keys_to_remove)
        return removed

    # -- helpers / housekeeping --------------------------------------------

    def clear(self) -> None:
        """Drop every entry. Intended for tests."""
        with self._lock:
            self._store.clear()

    def __len__(self) -> int:
        # Includes entries that have expired but not yet been swept; good
        # enough for diagnostics, not for correctness checks.
        with self._lock:
            return len(self._store)

    def __contains__(self, key: str) -> bool:
        return self.get(key) is not None

    def shutdown(self) -> None:
        """Stop the background sweep thread.

        Safe to call multiple times. The thread is a daemon so calling this
        is optional, but tests benefit from deterministic teardown.
        """
        self._stop_event.set()
        thread = self._sweep_thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=2.0)


# ---------------------------------------------------------------------------
# Singleton factory
# ---------------------------------------------------------------------------


_singleton: Optional[InMemoryCacheManager] = None
_singleton_lock = threading.Lock()


def get_cache_manager() -> InMemoryCacheManager:
    """Return the process-wide singleton :class:`InMemoryCacheManager`.

    Initialized lazily on first call. Thread-safe via double-checked locking.
    """
    global _singleton
    if _singleton is None:
        with _singleton_lock:
            if _singleton is None:
                _singleton = InMemoryCacheManager()
    return _singleton


def reset_cache_manager() -> None:
    """Reset the singleton, shutting down the previous instance if any.

    Intended for tests; calling this in production code will drop the cache.
    """
    global _singleton
    with _singleton_lock:
        if _singleton is not None:
            _singleton.shutdown()
        _singleton = None


__all__ = [
    "CacheManager",
    "InMemoryCacheManager",
    "get_cache_manager",
    "reset_cache_manager",
]
