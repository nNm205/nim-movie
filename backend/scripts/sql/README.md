# SQL scripts cho Supabase

Thư mục này chứa SQL chạy trực tiếp trong **Supabase Dashboard → SQL Editor**.

## File

| File | Mục đích | Trạng thái |
|------|----------|------------|
| `01_core_schema.sql` | Tạo `users`, `reviews`, `watchlist`. Khớp với Alembic migration `71e9b7e48873`. | Stable |
| `02_chat_and_vectors.sql` | Tạo `chat_sessions`, `chat_messages`, `movie_embeddings` (pgvector) cho spec `ai-chatbot-rag`. | **Preview** — sẽ thay bằng Alembic migration ở Phase 2 |

## Thứ tự chạy

1. Vào Supabase Dashboard → SQL Editor → New query.
2. Paste nội dung `01_core_schema.sql` → **Run**.
3. (Tuỳ chọn) Stamp Alembic ở local để đồng bộ revision:
   ```
   cd backend
   alembic stamp 71e9b7e48873
   ```
4. Paste nội dung `02_chat_and_vectors.sql` → **Run** (chỉ khi bạn muốn dựng sẵn schema cho chatbot trước khi Phase 2 hoàn tất).

## Alternative: dùng Alembic thay vì SQL trực tiếp

Cách "đúng" với setup dự án:

```
cd backend
alembic upgrade head
```

Lệnh này đọc `DATABASE_URL` từ `.env` và áp dụng migration `71e9b7e48873`. Khi spec `ai-chatbot-rag` qua Phase 2, sẽ có thêm migration cho chat tables — chạy lại `alembic upgrade head` là xong.

## Verify sau khi chạy

```
cd backend
python -m scripts.test_supabase_connection
```

Script sẽ in danh sách bảng và xác nhận pgvector đã bật.

## Lưu ý về dimension của embedding

`02_chat_and_vectors.sql` đặt `VECTOR(384)` cho `sentence-transformers/all-MiniLM-L6-v2`. Nếu bạn đổi `EMBEDDING_PROVIDER=openai`, sửa thành `VECTOR(1536)` rồi drop/recreate bảng (vì Postgres không cho `ALTER COLUMN TYPE` qua các vector dimension khác nhau).
