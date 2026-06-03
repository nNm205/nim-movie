-- =============================================================================
-- nim-movie : chat & vector store schema (PREVIEW cho spec ai-chatbot-rag)
-- =============================================================================
-- ⚠ Đây là bản preview dựa trên Requirements (Phase 1) của spec ai-chatbot-rag.
--   Schema có thể được tinh chỉnh khi sang Phase 2 (Design). Khi đó sẽ có một
--   Alembic migration chính thức thay thế file này. Nếu bạn dùng file này
--   trước, hãy nhớ drop và tạo lại bằng migration để đồng bộ với Alembic.
--
-- File phụ thuộc:
--   - 01_core_schema.sql phải được chạy trước (cần bảng users, reviews).
--   - Extension `vector` (pgvector) phải được bật. Bạn có thể bật bằng:
--       Supabase Dashboard -> Database -> Extensions -> "vector" -> Enable
--     hoặc giữ dòng CREATE EXTENSION ở dưới đây.
--
-- Cấu hình embedding dimension:
--   - 384  cho `sentence-transformers/all-MiniLM-L6-v2` (mặc định, local)
--   - 1536 cho OpenAI `text-embedding-3-small`
--   File này đặt VECTOR(384) cho mặc định local. Đổi nếu bạn dùng OpenAI.
--
-- Cách chạy:
--   1) Vào Supabase Dashboard -> SQL Editor -> New query
--   2) Paste toàn bộ file này -> Run
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- Extensions
-- -----------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS vector;
-- pgcrypto cho hàm gen_random_uuid() (Supabase đã enable mặc định, để chắc chắn)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- -----------------------------------------------------------------------------
-- chat_sessions
--   Khớp Requirement 2.1: id UUID PK, user_id FK, title VARCHAR(120), timestamps
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.chat_sessions (
    id          UUID                        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     INTEGER                     NOT NULL REFERENCES public.users (id) ON DELETE CASCADE,
    title       VARCHAR(120)                NULL,
    created_at  TIMESTAMP WITH TIME ZONE    NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE    NOT NULL DEFAULT NOW()
);

-- Truy vấn list session của user, sort theo updated_at DESC (Requirement 1.5)
CREATE INDEX IF NOT EXISTS ix_chat_sessions_user_updated
    ON public.chat_sessions (user_id, updated_at DESC);

-- -----------------------------------------------------------------------------
-- chat_messages
--   Khớp Requirement 2.2
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.chat_messages (
    id              BIGSERIAL                   PRIMARY KEY,
    session_id      UUID                        NOT NULL REFERENCES public.chat_sessions (id) ON DELETE CASCADE,
    role            VARCHAR(16)                 NOT NULL,
    content         TEXT                        NOT NULL,
    citations       JSONB                       NULL,
    tokens_input    INTEGER                     NULL,
    tokens_output   INTEGER                     NULL,
    metadata        JSONB                       NULL,           -- chứa { partial: bool, error: ... } theo Requirement 5.4 / 9.7
    created_at      TIMESTAMP WITH TIME ZONE    NOT NULL DEFAULT NOW(),
    CONSTRAINT chat_messages_role_check CHECK (role IN ('user', 'assistant', 'system'))
);

-- Truy vấn message của một session theo created_at ASC (Requirement 1.6)
CREATE INDEX IF NOT EXISTS ix_chat_messages_session_created
    ON public.chat_messages (session_id, created_at);

-- -----------------------------------------------------------------------------
-- movie_embeddings (Vector Store)
--   Khớp Requirement 3.1
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.movie_embeddings (
    id            BIGSERIAL                   PRIMARY KEY,
    source_type   VARCHAR(16)                 NOT NULL,
    source_id     BIGINT                      NOT NULL,
    chunk_index   INTEGER                     NOT NULL,
    content       TEXT                        NOT NULL,
    embedding     VECTOR(384)                 NOT NULL,         -- đổi 1536 nếu dùng OpenAI
    metadata      JSONB                       NULL,
    created_at    TIMESTAMP WITH TIME ZONE    NOT NULL DEFAULT NOW(),
    CONSTRAINT movie_embeddings_source_type_check CHECK (source_type IN ('movie', 'review')),
    CONSTRAINT uq_movie_embeddings_chunk UNIQUE (source_type, source_id, chunk_index)
);

-- ANN index cho cosine similarity. ivfflat cần ANALYZE / lists tuning sau khi
-- ingest đủ data. Lists=100 hợp lý cho < 1M rows; với corpus nhỏ có thể giảm.
CREATE INDEX IF NOT EXISTS ix_movie_embeddings_embedding
    ON public.movie_embeddings
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Hỗ trợ tra ngược theo source (cập nhật / xóa cache theo Requirement 6.5)
CREATE INDEX IF NOT EXISTS ix_movie_embeddings_source
    ON public.movie_embeddings (source_type, source_id);

COMMIT;

-- -----------------------------------------------------------------------------
-- Sau khi ingest dữ liệu, chạy lệnh sau để tối ưu ivfflat index (cần một lần):
--   ANALYZE public.movie_embeddings;
-- Nếu corpus phình > 100k rows, cân nhắc tăng `lists` (drop + recreate index).
-- -----------------------------------------------------------------------------
