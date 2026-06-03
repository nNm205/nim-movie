from __future__ import annotations

import sys
import time
from urllib.parse import urlparse

from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.database.session import SessionLocal, engine

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
DIM = "\033[2m"
RESET = "\033[0m"

def ok(msg: str) -> None:
    print(f"{GREEN}[OK]{RESET} {msg}")


def warn(msg: str) -> None:
    print(f"{YELLOW}[WARN]{RESET} {msg}")


def fail(msg: str) -> None:
    print(f"{RED}[FAIL]{RESET} {msg}")


def info(msg: str) -> None:
    print(f"{CYAN}[..]{RESET} {msg}")

def _redact_url(url: str) -> str:
    try:
        parsed = urlparse(url)
        if parsed.password:
            netloc = parsed.netloc.replace(f":{parsed.password}@", ":***@")
            return parsed._replace(netloc=netloc).geturl()
    except Exception:
        pass
    return url


def _is_placeholder(url: str) -> bool:
    return "<PROJECT_REF>" in url or "<PASSWORD>" in url or "<REGION>" in url

def check_env() -> bool:
    info("Kiểm tra DATABASE_URL trong .env")
    if not settings.DATABASE_URL:
        fail("DATABASE_URL trống")
        return False
    if _is_placeholder(settings.DATABASE_URL):
        fail(
            "DATABASE_URL vẫn là placeholder. Hãy điền connection string thật từ "
            "Supabase Dashboard -> Project Settings -> Database -> Connection string."
        )
        return False
    ok(f"DATABASE_URL = {_redact_url(settings.DATABASE_URL)}")
    return True


def check_raw_connection() -> bool:
    info("Kết nối raw qua SQLAlchemy engine và đo latency")
    try:
        start = time.perf_counter()
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version()")).scalar()
            conn.execute(text("SELECT 1"))
        elapsed_ms = (time.perf_counter() - start) * 1000
    except SQLAlchemyError as exc:
        fail(f"Không kết nối được: {exc.__class__.__name__}: {exc}")
        return False

    ok(f"Kết nối thành công ({elapsed_ms:.0f} ms)")
    print(f"   {DIM}{version}{RESET}")
    return True


def check_pgvector() -> bool:
    info("Kiểm tra extension pgvector (cần cho spec AI Chatbot RAG)")
    try:
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
            ).first()
            available = conn.execute(
                text("SELECT default_version FROM pg_available_extensions WHERE name = 'vector'")
            ).first()
    except SQLAlchemyError as exc:
        fail(f"Không truy vấn được pg_extension: {exc}")
        return False

    if row is not None:
        ok(f"pgvector đã bật, version {row[0]}")
        return True

    if available is not None:
        warn(
            f"pgvector có sẵn (version {available[0]}) nhưng CHƯA bật. "
            f"Vào Supabase Dashboard -> Database -> Extensions -> bật 'vector', "
            f"hoặc chạy: CREATE EXTENSION IF NOT EXISTS vector;"
        )
    else:
        warn("pgvector không có trong pg_available_extensions ở instance này")
    return True  


def check_tables() -> bool:
    info("Liệt kê bảng trong schema public")
    try:
        inspector = inspect(engine)
        tables = sorted(inspector.get_table_names(schema="public"))
    except SQLAlchemyError as exc:
        fail(f"Không inspect được schema: {exc}")
        return False

    if not tables:
        warn("Schema public trống. Chạy `alembic upgrade head` để tạo bảng.")
        return True

    ok(f"Tìm thấy {len(tables)} bảng:")
    for name in tables:
        print(f"   - {name}")
    return True


def check_orm_session() -> bool:
    info("Mở SessionLocal và chạy SELECT 1")
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT 1")).scalar()
        if result != 1:
            fail(f"SELECT 1 trả về {result!r}, expected 1")
            return False
        ok("ORM session hoạt động bình thường")
        return True
    except SQLAlchemyError as exc:
        fail(f"ORM session lỗi: {exc}")
        return False
    finally:
        db.close()

def main() -> int:
    print(f"{CYAN}=== Supabase / Postgres connection smoke test ==={RESET}\n")

    if not check_env():
        return 1

    checks = [
        check_raw_connection,
        check_pgvector,
        check_tables,
        check_orm_session,
    ]
    failures = 0
    for fn in checks:
        print()
        if not fn():
            failures += 1

    print()
    if failures == 0:
        ok("Tất cả check đã pass.")
        return 0
    fail(f"{failures} check thất bại.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
