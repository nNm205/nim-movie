from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # =========================================================
    # Database
    # =========================================================
    DATABASE_URL: str
    DB_ECHO: bool = False

    # =========================================================
    # Auth
    # =========================================================
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # =========================================================
    # TMDB
    # =========================================================
    TMDB_URL: str
    TMDB_API_KEY: str

    # =========================================================
    # AI Chatbot — Embedding
    # =========================================================
    # 384 cho `sentence-transformers/all-MiniLM-L6-v2` (local),
    # 1536 cho `text-embedding-3-small` (openai).
    EMBEDDING_PROVIDER: Literal["local", "openai"]
    EMBEDDING_DIMENSION: int

    # =========================================================
    # AI Chatbot — LLM
    # =========================================================
    LLM_PROVIDER: Literal["openai", "gemini", "groq"]
    LLM_MODEL: str
    OPENAI_API_KEY: str
    GOOGLE_API_KEY: str
    GROQ_API_KEY: str
    LLM_TIMEOUT_SECONDS: int

    # =========================================================
    # AI Chatbot — RAG
    # =========================================================
    RAG_TOP_K: int
    RAG_TOKEN_BUDGET: int
    RAG_MIN_SIMILARITY: float
    PERSONALIZATION_TOKEN_BUDGET: int

    # =========================================================
    # AI Chatbot — Cache TTL (seconds)
    # =========================================================
    CACHE_TTL_EMBEDDING_SECONDS: int
    CACHE_TTL_RETRIEVAL_SECONDS: int

    # =========================================================
    # AI Chatbot — Rate limit
    # =========================================================
    CHAT_RATE_LIMIT_PER_MINUTE: int
    CHAT_RATE_LIMIT_PER_HOUR: int

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
