-- =============================================================================
-- nim-movie : core schema (users, reviews, watchlist)
-- =============================================================================
-- File này khớp 100% với Alembic migration:
--   backend/app/database/migrations/versions/71e9b7e48873_initial_commit.py
--
-- Cách chạy:
--   1) Vào Supabase Dashboard -> SQL Editor -> New query
--   2) Paste toàn bộ file này -> Run
--   3) Stamp Alembic ở local để Alembic không sinh lại 3 bảng:
--        cd backend
--        alembic stamp 71e9b7e48873
--      Sau bước này, các migration mới có thể chạy bằng `alembic upgrade head`.
--
-- Có thể chạy lại nhiều lần (idempotent qua `IF NOT EXISTS`).
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- users
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.users (
    id               SERIAL                      PRIMARY KEY,
    email            VARCHAR                     NOT NULL,
    username         VARCHAR                     NOT NULL,
    hashed_password  VARCHAR                     NOT NULL,
    role             VARCHAR                     NOT NULL DEFAULT 'user',
    is_active        BOOLEAN                     NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMP WITH TIME ZONE    NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMP WITH TIME ZONE    NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email    ON public.users (email);
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON public.users (username);
CREATE        INDEX IF NOT EXISTS ix_users_id       ON public.users (id);

-- -----------------------------------------------------------------------------
-- reviews
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.reviews (
    id           SERIAL                      PRIMARY KEY,
    user_id      INTEGER                     NOT NULL REFERENCES public.users (id),
    movie_id     INTEGER                     NOT NULL,
    rating       INTEGER                     NOT NULL,
    review_text  TEXT                        NULL,
    created_at   TIMESTAMP WITH TIME ZONE    NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMP WITH TIME ZONE    NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_movie_review UNIQUE (user_id, movie_id),
    CONSTRAINT check_rating_range   CHECK (rating >= 1 AND rating <= 10)
);

-- -----------------------------------------------------------------------------
-- watchlist
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.watchlist (
    id             SERIAL                      PRIMARY KEY,
    user_id        INTEGER                     NOT NULL REFERENCES public.users (id),
    movie_id       INTEGER                     NOT NULL,
    added_at       TIMESTAMP WITH TIME ZONE    NOT NULL DEFAULT NOW(),
    progress       INTEGER                     NOT NULL DEFAULT 0,
    last_watched   TIMESTAMP WITH TIME ZONE    NULL,
    is_completed   BOOLEAN                     NOT NULL DEFAULT FALSE,
    CONSTRAINT uq_user_movie_watchlist UNIQUE (user_id, movie_id),
    CONSTRAINT check_progress_range    CHECK (progress >= 0 AND progress <= 100)
);

CREATE INDEX IF NOT EXISTS ix_watchlist_id ON public.watchlist (id);

-- -----------------------------------------------------------------------------
-- alembic_version : đánh dấu migration đã chạy để Alembic không sinh lại
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

INSERT INTO public.alembic_version (version_num)
VALUES ('71e9b7e48873')
ON CONFLICT (version_num) DO NOTHING;

COMMIT;
