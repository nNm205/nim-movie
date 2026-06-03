"""Smoke test for AI Chatbot RAG schema migration (task 3.3).

Verifies that the Alembic migration `491a1fba608a_add_chat_and_vectors`
was applied successfully to the configured Supabase Postgres database.

Checks (Requirements 2.1, 3.1):
1. Tables `chat_sessions`, `chat_messages`, `movie_embeddings` exist
   in the `public` schema (queried via `information_schema.tables`).
2. Index `ix_movie_embeddings_embedding` exists on `movie_embeddings`
   and uses `ivfflat` access method with `vector_cosine_ops` opclass
   (queried via `pg_indexes` + `pg_class` + `pg_am`).
3. Index `uq_movie_embeddings_chunk` exists on `movie_embeddings`
   and is backed by a UNIQUE constraint on
   (source_type, source_id, chunk_index).

Usage:
    cd backend
    python -m scripts.smoke_test_chat_schema

Exit code 0 on success, 1 on any assertion failure.
"""
from __future__ import annotations

import sys
from typing import Iterable

from sqlalchemy import text

from app.database.session import engine


REQUIRED_TABLES = ("chat_sessions", "chat_messages", "movie_embeddings")
EMBEDDING_INDEX = "ix_movie_embeddings_embedding"
UNIQUE_CHUNK_INDEX = "uq_movie_embeddings_chunk"


def _print_section(title: str) -> None:
    print()
    print(f"=== {title} ===")


def _check_tables(conn) -> list[str]:
    """Return list of error strings (empty when all tables present)."""
    rows = conn.execute(
        text(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = ANY(:names)
            ORDER BY table_name
            """
        ),
        {"names": list(REQUIRED_TABLES)},
    ).fetchall()
    found = {r[0] for r in rows}
    print(f"Tables present in public schema: {sorted(found)}")
    errors = []
    for name in REQUIRED_TABLES:
        if name not in found:
            errors.append(f"Missing table: {name}")
    return errors


def _check_embedding_index(conn) -> list[str]:
    """Verify ix_movie_embeddings_embedding exists and is ivfflat."""
    errors: list[str] = []

    pg_indexes_row = conn.execute(
        text(
            """
            SELECT schemaname, tablename, indexname, indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
              AND tablename = 'movie_embeddings'
              AND indexname = :name
            """
        ),
        {"name": EMBEDDING_INDEX},
    ).fetchone()
    if pg_indexes_row is None:
        errors.append(
            f"pg_indexes: index '{EMBEDDING_INDEX}' not found on movie_embeddings"
        )
        return errors

    print(f"pg_indexes row for {EMBEDDING_INDEX}:")
    print(f"  schema    = {pg_indexes_row[0]}")
    print(f"  table     = {pg_indexes_row[1]}")
    print(f"  indexname = {pg_indexes_row[2]}")
    print(f"  indexdef  = {pg_indexes_row[3]}")

    am_row = conn.execute(
        text(
            """
            SELECT am.amname
            FROM pg_class c
            JOIN pg_index i ON i.indexrelid = c.oid
            JOIN pg_am am ON am.oid = c.relam
            WHERE c.relname = :name
            """
        ),
        {"name": EMBEDDING_INDEX},
    ).fetchone()
    if am_row is None:
        errors.append(f"pg_class: index '{EMBEDDING_INDEX}' not found")
    else:
        amname = am_row[0]
        print(f"  access method = {amname}")
        if amname != "ivfflat":
            errors.append(
                f"Expected ivfflat for {EMBEDDING_INDEX}, got '{amname}'"
            )

    indexdef = pg_indexes_row[3] or ""
    if "vector_cosine_ops" not in indexdef:
        errors.append(
            f"Expected vector_cosine_ops in indexdef of {EMBEDDING_INDEX}, "
            f"got: {indexdef}"
        )

    return errors


def _check_unique_chunk_index(conn) -> list[str]:
    """Verify uq_movie_embeddings_chunk exists, is unique on the right cols."""
    errors: list[str] = []

    pg_indexes_row = conn.execute(
        text(
            """
            SELECT schemaname, tablename, indexname, indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
              AND tablename = 'movie_embeddings'
              AND indexname = :name
            """
        ),
        {"name": UNIQUE_CHUNK_INDEX},
    ).fetchone()
    if pg_indexes_row is None:
        errors.append(
            f"pg_indexes: index '{UNIQUE_CHUNK_INDEX}' not found "
            f"on movie_embeddings"
        )
        return errors

    print(f"pg_indexes row for {UNIQUE_CHUNK_INDEX}:")
    print(f"  schema    = {pg_indexes_row[0]}")
    print(f"  table     = {pg_indexes_row[1]}")
    print(f"  indexname = {pg_indexes_row[2]}")
    print(f"  indexdef  = {pg_indexes_row[3]}")

    info_row = conn.execute(
        text(
            """
            SELECT i.indisunique,
                   array_agg(a.attname ORDER BY array_position(i.indkey, a.attnum))
            FROM pg_class c
            JOIN pg_index i ON i.indexrelid = c.oid
            JOIN pg_attribute a ON a.attrelid = i.indrelid
                                AND a.attnum = ANY(i.indkey)
            WHERE c.relname = :name
            GROUP BY i.indisunique
            """
        ),
        {"name": UNIQUE_CHUNK_INDEX},
    ).fetchone()
    if info_row is None:
        errors.append(f"pg_class: index '{UNIQUE_CHUNK_INDEX}' not found")
    else:
        is_unique, cols = info_row[0], list(info_row[1])
        print(f"  is_unique = {is_unique}")
        print(f"  columns   = {cols}")
        if not is_unique:
            errors.append(
                f"Expected {UNIQUE_CHUNK_INDEX} to be UNIQUE, got non-unique"
            )
        expected_cols = ["source_type", "source_id", "chunk_index"]
        if cols != expected_cols:
            errors.append(
                f"Expected columns {expected_cols} on {UNIQUE_CHUNK_INDEX}, "
                f"got {cols}"
            )

    return errors


def main() -> int:
    print("Connecting to Supabase Postgres via DATABASE_URL ...")
    all_errors: list[str] = []
    with engine.connect() as conn:
        _print_section("Check 1: required tables exist")
        all_errors.extend(_check_tables(conn))

        _print_section("Check 2: ivfflat index ix_movie_embeddings_embedding")
        all_errors.extend(_check_embedding_index(conn))

        _print_section("Check 3: unique index uq_movie_embeddings_chunk")
        all_errors.extend(_check_unique_chunk_index(conn))

    print()
    if all_errors:
        print("SMOKE TEST FAILED")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print("SMOKE TEST PASSED: schema migration verified on Supabase.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
