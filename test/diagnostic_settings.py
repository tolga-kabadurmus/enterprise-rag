"""Validated environment configuration for local service diagnostics."""

from pydantic import AnyHttpUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class S3DiagnosticSettings(BaseSettings):
    """RustFS/S3 connection settings used by the local diagnostic script."""

    model_config = SettingsConfigDict(
        env_prefix="S3_",
        env_file="dev-envs/diagnostics.env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    endpoint_url: AnyHttpUrl
    access_key_id: str = Field(min_length=1)
    secret_access_key: SecretStr
    region: str = Field(default="us-east-1", min_length=1)


class QdrantDiagnosticSettings(BaseSettings):
    """Qdrant connection settings used by the local diagnostic script."""

    model_config = SettingsConfigDict(
        env_prefix="QDRANT_",
        env_file="dev-envs/diagnostics.env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    url: AnyHttpUrl
    api_key: SecretStr
