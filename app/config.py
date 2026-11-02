"""
Application Configuration Module.

Loads environment variables and sets default values for application-wide configurations,
such as database URLs, JWT secret keys, Celery, and S3 storage.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings configuration class using Pydantic Settings.
    """
    APP_NAME: str = "Employee Management System"
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = "postgres://postgres:postgres@localhost:5432/inventory_db"

    # Celery & S3 / MinIO Configuration Fields
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    aws_access_key_id: str = "minioadmin"
    aws_secret_access_key: str = "minioadmin"
    aws_default_region: str = "us-east-1"
    s3_bucket_name: str = "my-local-bucket"
    s3_endpoint_url: str = "http://localhost:9000"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignores any extra environment variables instead of crashing


settings = Settings()