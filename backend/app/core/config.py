from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="RAGDesk", alias="APP_NAME")
    app_env: Literal["development", "test", "production"] = Field(
        default="development", alias="APP_ENV"
    )
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    cors_origins: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")

    # Database
    database_url: str = Field(
        default="postgresql+psycopg://ragdesk:ragdesk_dev_password@localhost:5432/ragdesk",
        alias="DATABASE_URL",
    )

    # JWT Authentication
    jwt_secret_key: str = Field(
        default="dev-secret-key-change-in-production-32-chars",
        alias="JWT_SECRET_KEY",
    )
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=1440, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    # AI Providers (Configurable by environment; never hardcode API keys)
    llm_provider: Literal["mock", "gemini", "openai"] = Field(
        default="mock", alias="LLM_PROVIDER"
    )
    embedding_provider: Literal["mock", "gemini", "openai"] = Field(
        default="mock", alias="EMBEDDING_PROVIDER"
    )
    embedding_dimension: int = Field(default=768, alias="EMBEDDING_DIMENSION")

    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_llm_model: str = Field(default="gemini-2.5-flash", alias="GEMINI_LLM_MODEL")
    gemini_embedding_model: str = Field(
        default="text-embedding-004", alias="GEMINI_EMBEDDING_MODEL"
    )

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_llm_model: str = Field(default="gpt-4o-mini", alias="OPENAI_LLM_MODEL")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small", alias="OPENAI_EMBEDDING_MODEL"
    )

    # RAG & Guardrails
    chunk_size: int = Field(default=800, ge=100, le=4000, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=150, ge=0, le=1000, alias="CHUNK_OVERLAP")
    retrieval_top_k: int = Field(default=4, ge=1, le=20, alias="RETRIEVAL_TOP_K")
    similarity_threshold: float = Field(
        default=0.65, ge=0.0, le=1.0, alias="SIMILARITY_THRESHOLD"
    )
    chat_history_window: int = Field(default=6, ge=0, le=20, alias="CHAT_HISTORY_WINDOW")

    # Limits
    max_upload_size_mb: int = Field(default=10, ge=1, le=50, alias="MAX_UPLOAD_SIZE_MB")
    chat_rate_limit_per_minute: int = Field(
        default=20, ge=1, le=300, alias="CHAT_RATE_LIMIT_PER_MINUTE"
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
