"""
Configuration and settings for Rhiz API
Uses pydantic-settings for environment variable management
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="Rhiz Protocol API", alias="API_APP_NAME")
    app_env: Literal["development", "staging", "production"] = Field(
        default="development", alias="API_ENV"
    )
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, alias="API_DEBUG")
    log_level: Literal["debug", "info", "warning", "error", "critical"] = Field(
        default="info", alias="LOG_LEVEL"
    )

    # Server
    host: str = Field(default="0.0.0.0", alias="API_HOST")
    port: int = Field(default=8000, alias="API_PORT")
    workers: int = Field(default=4, alias="API_WORKERS")

    # Security
    secret_key: str = Field(..., alias="API_SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    cors_origins: list[str] = Field(
        default=["http://localhost:3000"], alias="API_CORS_ORIGINS"
    )

    # Database
    database_url: PostgresDsn = Field(..., alias="DATABASE_URL")
    database_pool_size: int = Field(default=20, alias="DATABASE_POOL_SIZE")
    database_echo: bool = Field(default=False, alias="DATABASE_ECHO")

    # Redis
    redis_url: RedisDsn = Field(..., alias="REDIS_URL")
    redis_ttl: int = Field(default=3600, alias="REDIS_TTL")  # seconds

    # AT Protocol
    atproto_pds_url: str = Field(default="https://bsky.social", alias="ATPROTO_PDS_URL")
    atproto_firehose_url: str = Field(
        default="wss://bsky.network", alias="ATPROTO_FIREHOSE_URL"
    )
    atproto_did: str | None = Field(default=None, alias="ATPROTO_DID")
    atproto_handle: str | None = Field(default=None, alias="ATPROTO_HANDLE")
    atproto_password: str | None = Field(default=None, alias="ATPROTO_PASSWORD")

    # OpenAI
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo-preview", alias="OPENAI_MODEL")

    # Feature Flags
    enable_agent_coordination: bool = Field(default=True, alias="ENABLE_AGENT_COORDINATION")
    enable_firehose_ingest: bool = Field(default=True, alias="ENABLE_FIREHOSE_INGEST")
    enable_trust_decay: bool = Field(default=True, alias="ENABLE_TRUST_DECAY")

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, alias="RATE_LIMIT_WINDOW")  # seconds

    # Graph Settings
    max_graph_hops: int = Field(default=6, alias="MAX_GRAPH_HOPS")
    min_trust_strength: float = Field(default=0.5, alias="MIN_TRUST_STRENGTH")
    pathfinding_timeout: int = Field(default=30, alias="PATHFINDING_TIMEOUT")  # seconds

    # Cache Settings
    cache_backend: str = Field(default="memory", alias="CACHE_BACKEND")  # "memory" or "redis"
    cache_default_ttl: int = Field(default=3600, alias="CACHE_DEFAULT_TTL")  # 1 hour
    cache_max_memory_size: int = Field(default=10000, alias="CACHE_MAX_MEMORY_SIZE")  # keys
    
    # Internal API (for event pipeline)
    internal_api_key: str = Field(default="dev-internal-key-change-in-prod", alias="INTERNAL_API_KEY")

    @property
    def database_url_string(self) -> str:
        """Get database URL as string"""
        return str(self.database_url)

    @property
    def redis_url_string(self) -> str:
        """Get Redis URL as string"""
        return str(self.redis_url)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()  # type: ignore


# Global settings instance
settings = get_settings()

