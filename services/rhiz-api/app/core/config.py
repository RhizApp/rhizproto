"""
Comprehensive configuration management for Rhiz Protocol
Centralized settings with environment-based overrides and validation
"""

import os
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from pydantic import BaseSettings, Field, validator
from pydantic.env_settings import SettingsSourceCallable


class DatabaseSettings(BaseSettings):
    """Database configuration"""
    
    url: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost/rhizprotocol",
        description="Database URL with async driver"
    )
    pool_size: int = Field(default=20, description="Connection pool size")
    max_overflow: int = Field(default=30, description="Max pool overflow")
    pool_timeout: int = Field(default=30, description="Pool timeout in seconds")
    pool_recycle: int = Field(default=3600, description="Pool recycle time in seconds")
    echo: bool = Field(default=False, description="Enable SQL logging")
    
    class Config:
        env_prefix = "DB_"


class RedisSettings(BaseSettings):
    """Redis configuration"""
    
    url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis URL"
    )
    max_connections: int = Field(default=20, description="Max Redis connections")
    decode_responses: bool = Field(default=True, description="Decode Redis responses")
    socket_timeout: int = Field(default=5, description="Socket timeout in seconds")
    retry_on_timeout: bool = Field(default=True, description="Retry on timeout")
    
    class Config:
        env_prefix = "REDIS_"


class TrustEngineSettings(BaseSettings):
    """Trust engine configuration"""
    
    enable_privacy: bool = Field(default=True, description="Enable differential privacy")
    privacy_epsilon: float = Field(default=1.0, description="Privacy epsilon parameter")
    max_network_depth: int = Field(default=3, description="Max network propagation depth")
    cache_ttl: int = Field(default=3600, description="Trust metrics cache TTL")
    
    # Algorithm weights
    direct_weight: float = Field(default=0.7, description="Direct metrics weight")
    network_weight: float = Field(default=0.3, description="Network propagation weight")
    
    # Temporal decay parameters
    decay_half_life_days: int = Field(default=365, description="Temporal decay half-life")
    min_decay_factor: float = Field(default=0.1, description="Minimum decay factor")
    
    @validator("direct_weight", "network_weight")
    def validate_weights(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Weights must be between 0.0 and 1.0")
        return v
    
    class Config:
        env_prefix = "TRUST_"


class PathfindingSettings(BaseSettings):
    """Pathfinding configuration"""
    
    default_algorithm: str = Field(default="astar", description="Default pathfinding algorithm")
    max_hops: int = Field(default=6, description="Maximum hops in path")
    min_strength: float = Field(default=0.5, description="Minimum relationship strength")
    cache_ttl: int = Field(default=1800, description="Path cache TTL in seconds")
    
    # A* algorithm parameters
    heuristic_weight: float = Field(default=1.0, description="A* heuristic weight")
    path_diversity_factor: float = Field(default=0.1, description="Path diversity bonus")
    
    @validator("default_algorithm")
    def validate_algorithm(cls, v):
        allowed = ["astar", "dijkstra", "bfs"]
        if v not in allowed:
            raise ValueError(f"Algorithm must be one of {allowed}")
        return v
    
    class Config:
        env_prefix = "PATH_"


class SecuritySettings(BaseSettings):
    """Security and cryptography configuration"""
    
    signature_required: bool = Field(default=True, description="Require signatures")
    signature_timeout: int = Field(default=300, description="Signature timeout in seconds")
    did_cache_ttl: int = Field(default=3600, description="DID document cache TTL")
    
    # Allowed DID methods
    allowed_did_methods: List[str] = Field(
        default=["did:plc", "did:web"],
        description="Allowed DID methods"
    )
    
    # PLC directory URL
    plc_directory_url: str = Field(
        default="https://plc.directory",
        description="PLC directory URL"
    )
    
    class Config:
        env_prefix = "SECURITY_"


class APISettings(BaseSettings):
    """API server configuration"""
    
    host: str = Field(default="0.0.0.0", description="API host")
    port: int = Field(default=8000, description="API port")
    workers: int = Field(default=1, description="Number of workers")
    reload: bool = Field(default=False, description="Enable auto-reload")
    
    # CORS settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        description="Allowed CORS origins"
    )
    cors_credentials: bool = Field(default=True, description="Allow credentials")
    
    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(default=100, description="Requests per minute")
    
    class Config:
        env_prefix = "API_"


class LoggingSettings(BaseSettings):
    """Logging configuration"""
    
    level: str = Field(default="INFO", description="Log level")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    
    # File logging
    log_file: Optional[str] = Field(default=None, description="Log file path")
    max_file_size: int = Field(default=10485760, description="Max log file size (10MB)")
    backup_count: int = Field(default=5, description="Number of backup files")
    
    # Structured logging
    json_format: bool = Field(default=False, description="Use JSON format")
    include_trace_id: bool = Field(default=True, description="Include trace IDs")
    
    @validator("level")
    def validate_level(cls, v):
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v.upper()
    
    class Config:
        env_prefix = "LOG_"


class MonitoringSettings(BaseSettings):
    """Monitoring and metrics configuration"""
    
    enabled: bool = Field(default=True, description="Enable monitoring")
    metrics_endpoint: str = Field(default="/metrics", description="Metrics endpoint")
    health_endpoint: str = Field(default="/health", description="Health endpoint")
    
    # Performance monitoring
    trace_requests: bool = Field(default=True, description="Trace HTTP requests")
    trace_database: bool = Field(default=True, description="Trace database queries")
    trace_cache: bool = Field(default=False, description="Trace cache operations")
    
    # External monitoring
    prometheus_enabled: bool = Field(default=False, description="Enable Prometheus metrics")
    jaeger_enabled: bool = Field(default=False, description="Enable Jaeger tracing")
    
    class Config:
        env_prefix = "MONITORING_"


class RhizProtocolSettings(BaseSettings):
    """
    Comprehensive Rhiz Protocol configuration
    
    Combines all subsystem settings with environment-based overrides
    """
    
    # Application metadata
    app_name: str = Field(default="Rhiz Protocol API", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    app_env: str = Field(default="development", description="Environment")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Component settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    trust_engine: TrustEngineSettings = Field(default_factory=TrustEngineSettings)
    pathfinding: PathfindingSettings = Field(default_factory=PathfindingSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    api: APISettings = Field(default_factory=APISettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    
    # Lexicon and schema settings
    lexicon_base_path: Path = Field(
        default=Path("lexicons"),
        description="Base path for lexicon schemas"
    )
    
    @validator("app_env")
    def validate_environment(cls, v):
        allowed = ["development", "staging", "production", "test"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.app_env == "production"
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.app_env == "development"
    
    def is_testing(self) -> bool:
        """Check if running in test mode"""
        return self.app_env == "test"
    
    def get_database_url(self) -> str:
        """Get database URL with environment-specific overrides"""
        if self.is_testing():
            # Use test database
            return self.database.url.replace("/rhizprotocol", "/rhizprotocol_test")
        return self.database.url
    
    def get_redis_url(self) -> str:
        """Get Redis URL with environment-specific overrides"""
        if self.is_testing():
            # Use test Redis database
            return self.redis.url.replace("/0", "/1")
        return self.redis.url
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary (excluding sensitive data)"""
        data = self.dict()
        
        # Remove sensitive information
        sensitive_keys = ["password", "secret", "key", "token"]
        
        def clean_dict(d: Dict[str, Any]) -> Dict[str, Any]:
            cleaned = {}
            for k, v in d.items():
                if any(sensitive in k.lower() for sensitive in sensitive_keys):
                    cleaned[k] = "***REDACTED***"
                elif isinstance(v, dict):
                    cleaned[k] = clean_dict(v)
                else:
                    cleaned[k] = v
            return cleaned
        
        return clean_dict(data)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> tuple[SettingsSourceCallable, ...]:
            """Customize settings sources priority"""
            return (
                init_settings,
                env_settings,
                file_secret_settings,
            )


# Global settings instance
settings = RhizProtocolSettings()


def get_settings() -> RhizProtocolSettings:
    """Get settings instance (for dependency injection)"""
    return settings


def reload_settings() -> RhizProtocolSettings:
    """Reload settings from environment"""
    global settings
    settings = RhizProtocolSettings()
    return settings