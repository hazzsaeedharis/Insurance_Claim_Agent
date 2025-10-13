"""
Centralized configuration management for Insurance Claim Agent.
Uses Pydantic Settings for type-safe configuration with environment variable support.
"""

import os
from typing import Optional, Dict, Any, List
from functools import lru_cache
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    """Database configuration settings."""
    
    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=5432, env="DB_PORT")
    database: str = Field(default="insurance_claims", env="DB_NAME")
    username: str = Field(default="insurance_admin", env="DB_USER")
    password: str = Field(default="dev_password_123", env="DB_PASSWORD")
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    
    @property
    def url(self) -> str:
        """Get database URL."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @property
    def async_url(self) -> str:
        """Get async database URL."""
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    model_config = SettingsConfigDict(env_prefix="DB_", extra="ignore")


class MinioConfig(BaseSettings):
    """MinIO configuration settings."""
    
    endpoint: str = Field(default="localhost:9000", env="MINIO_ENDPOINT")
    access_key: str = Field(default="minioadmin", env="MINIO_ACCESS_KEY")
    secret_key: str = Field(default="minioadmin123", env="MINIO_SECRET_KEY")
    secure: bool = Field(default=False, env="MINIO_SECURE")
    bucket_name: str = Field(default="insurance-documents", env="MINIO_BUCKET")
    region: str = Field(default="us-east-1", env="MINIO_REGION")
    
    model_config = SettingsConfigDict(env_prefix="MINIO_", extra="ignore")


class RedisConfig(BaseSettings):
    """Redis configuration settings."""
    
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    db: int = Field(default=0, env="REDIS_DB")
    decode_responses: bool = Field(default=True, env="REDIS_DECODE_RESPONSES")
    
    @property
    def url(self) -> str:
        """Get Redis URL."""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"
    
    model_config = SettingsConfigDict(env_prefix="REDIS_", extra="ignore")


class RabbitMQConfig(BaseSettings):
    """RabbitMQ configuration settings."""
    
    host: str = Field(default="localhost", env="RABBITMQ_HOST")
    port: int = Field(default=5672, env="RABBITMQ_PORT")
    username: str = Field(default="rabbitmq", env="RABBITMQ_USER")
    password: str = Field(default="rabbitmq123", env="RABBITMQ_PASS")
    vhost: str = Field(default="insurance", env="RABBITMQ_VHOST")
    
    @property
    def url(self) -> str:
        """Get RabbitMQ URL."""
        return f"amqp://{self.username}:{self.password}@{self.host}:{self.port}/{self.vhost}"
    
    model_config = SettingsConfigDict(env_prefix="RABBITMQ_", extra="ignore")


class KeycloakConfig(BaseSettings):
    """Keycloak configuration settings."""
    
    server_url: str = Field(default="http://localhost:8080", env="KEYCLOAK_URL")
    realm: str = Field(default="insurance-claims", env="KEYCLOAK_REALM")
    client_id: str = Field(default="insurance-api", env="KEYCLOAK_CLIENT_ID")
    client_secret: Optional[str] = Field(default=None, env="KEYCLOAK_CLIENT_SECRET")
    admin_username: str = Field(default="admin", env="KEYCLOAK_ADMIN")
    admin_password: str = Field(default="admin123", env="KEYCLOAK_ADMIN_PASSWORD")
    
    model_config = SettingsConfigDict(env_prefix="KEYCLOAK_", extra="ignore")


class ServiceDiscovery(BaseSettings):
    """Service discovery configuration."""
    
    claims_service_url: str = Field(default="http://localhost:8001", env="CLAIMS_SERVICE_URL")
    document_service_url: str = Field(default="http://localhost:8002", env="DOCUMENT_SERVICE_URL")
    ocr_service_url: str = Field(default="http://localhost:8003", env="OCR_SERVICE_URL")
    processing_service_url: str = Field(default="http://localhost:8004", env="PROCESSING_SERVICE_URL")
    
    # Service ports for local development
    claims_service_port: int = Field(default=8001, env="CLAIMS_SERVICE_PORT")
    document_service_port: int = Field(default=8002, env="DOCUMENT_SERVICE_PORT")
    ocr_service_port: int = Field(default=8003, env="OCR_SERVICE_PORT")
    processing_service_port: int = Field(default=8004, env="PROCESSING_SERVICE_PORT")
    
    model_config = SettingsConfigDict(env_prefix="SERVICE_", extra="ignore")


class OCRConfig(BaseSettings):
    """OCR service configuration."""
    
    tesseract_languages: List[str] = Field(default=["eng", "deu"], env="OCR_LANGUAGES")
    tesseract_config: str = Field(default="--oem 3 --psm 6", env="TESSERACT_CONFIG")
    max_file_size_mb: int = Field(default=10, env="OCR_MAX_FILE_SIZE_MB")
    supported_formats: List[str] = Field(
        default=["pdf", "png", "jpg", "jpeg", "tiff", "bmp"],
        env="OCR_SUPPORTED_FORMATS"
    )
    preprocessing_enabled: bool = Field(default=True, env="OCR_PREPROCESSING")
    
    @validator("tesseract_languages", pre=True)
    def parse_languages(cls, v):
        if isinstance(v, str):
            return v.split(",")
        return v
    
    model_config = SettingsConfigDict(env_prefix="OCR_", extra="ignore")


class SecurityConfig(BaseSettings):
    """Security configuration."""
    
    jwt_secret: str = Field(default="dev-secret-key-change-in-production", env="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_minutes: int = Field(default=60, env="JWT_EXPIRATION_MINUTES")
    jwt_issuer: str = Field(default="insurance-claims-api", env="JWT_ISSUER")
    jwt_audience: str = Field(default="insurance-claims", env="JWT_AUDIENCE")
    
    # CORS settings
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    
    # API Key settings
    api_key_header: str = Field(default="X-API-Key", env="API_KEY_HEADER")
    require_api_key: bool = Field(default=False, env="REQUIRE_API_KEY")
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return v.split(",")
        return v
    
    model_config = SettingsConfigDict(env_prefix="SECURITY_", extra="ignore")


class AppConfig(BaseSettings):
    """Main application configuration."""
    
    # Environment settings
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    service_name: str = Field(default="insurance-claims", env="SERVICE_NAME")
    
    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # Metrics settings
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    
    # Feature flags
    fraud_detection_enabled: bool = Field(default=True, env="FEATURE_FRAUD_DETECTION")
    auto_approval_enabled: bool = Field(default=True, env="FEATURE_AUTO_APPROVAL")
    ml_classification_enabled: bool = Field(default=False, env="FEATURE_ML_CLASSIFICATION")
    
    # Business rules
    max_auto_approval_amount: float = Field(default=5000.0, env="MAX_AUTO_APPROVAL_AMOUNT")
    fraud_score_threshold: float = Field(default=0.7, env="FRAUD_SCORE_THRESHOLD")
    
    # File upload settings
    max_upload_size_mb: int = Field(default=10, env="MAX_UPLOAD_SIZE_MB")
    allowed_file_types: List[str] = Field(
        default=["pdf", "jpg", "jpeg", "png", "tiff"],
        env="ALLOWED_FILE_TYPES"
    )
    
    @validator("allowed_file_types", pre=True)
    def parse_file_types(cls, v):
        if isinstance(v, str):
            return v.split(",")
        return v
    
    @validator("environment")
    def validate_environment(cls, v):
        allowed = ["development", "staging", "production", "testing"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra env vars not defined in this class
    )


class Settings:
    """Main settings class that aggregates all configuration."""
    
    def __init__(self):
        self.app = AppConfig()
        self.database = DatabaseConfig()
        self.minio = MinioConfig()
        self.redis = RedisConfig()
        self.rabbitmq = RabbitMQConfig()
        self.keycloak = KeycloakConfig()
        self.services = ServiceDiscovery()
        self.ocr = OCRConfig()
        self.security = SecurityConfig()
    
    def get_service_url(self, service_name: str) -> str:
        """Get URL for a specific service."""
        service_map = {
            "claims": self.services.claims_service_url,
            "documents": self.services.document_service_url,
            "ocr": self.services.ocr_service_url,
            "processing": self.services.processing_service_url,
        }
        return service_map.get(service_name, "")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert all settings to dictionary."""
        return {
            "app": self.app.model_dump(),
            "database": self.database.model_dump(exclude={"password"}),
            "minio": self.minio.model_dump(exclude={"secret_key"}),
            "redis": self.redis.model_dump(exclude={"password"}),
            "rabbitmq": self.rabbitmq.model_dump(exclude={"password"}),
            "keycloak": self.keycloak.model_dump(exclude={"client_secret", "admin_password"}),
            "services": self.services.model_dump(),
            "ocr": self.ocr.model_dump(),
            "security": self.security.model_dump(exclude={"jwt_secret"}),
        }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Example usage
if __name__ == "__main__":
    settings = get_settings()
    
    print("Current Configuration:")
    print(f"Environment: {settings.app.environment}")
    print(f"Database URL: {settings.database.url}")
    print(f"MinIO Endpoint: {settings.minio.endpoint}")
    print(f"Redis URL: {settings.redis.url}")
    print(f"Claims Service: {settings.get_service_url('claims')}")
    
    # Print all settings (with sensitive data masked)
    import json
    print("\nAll Settings:")
    print(json.dumps(settings.to_dict(), indent=2))

