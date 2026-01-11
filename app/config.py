"""
Configuration module menggunakan Pydantic Settings.
Membaca environment variables dari .env file.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings dari environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Cohere API
    cohere_api_key: str

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/rag_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 20
    redis_socket_timeout: int = 5
    redis_connect_timeout: int = 10
    redis_retry_attempts: int = 3
    redis_health_check_interval: int = 30

    # Embedding & LLM Models
    embedding_model: str = "embed-multilingual-v3.0"
    llm_model: str = "command-a-03-2025"

    # Chunking
    chunk_size: int = 500
    chunk_overlap: int = 100

    # Retrieval
    top_k: int = 5
    rrf_k: int = 60

    # Cache TTL
    cache_ttl: int = 3600
    chat_history_ttl: int = 86400

    # Application
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Menggunakan lru_cache untuk singleton pattern.
    """
    return Settings()
