"""Application configuration using pydantic-settings."""
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App metadata
    app_name: str = "ai-factory"
    app_version: str = "1.1.0"
    debug: bool = False

    # Database
    database_url: str = "sqlite+aiosqlite:///./ai_factory.db"

    # GitHub
    github_token: Optional[str] = None
    github_user: str = "ALANDVO"
    github_email: str = "alanvo@gmail.com"

    # Local paths
    base_dir: str = "~/ai-factory/repos"
    log_file: str = "~/ai-factory/pushed.log"
    state_file: str = "~/ai-factory/state.json"

    # Keycloak / OIDC
    keycloak_url: Optional[str] = None
    keycloak_realm: Optional[str] = None
    keycloak_client_id: Optional[str] = None
    keycloak_client_secret: Optional[str] = None
    oidc_issuer_url: Optional[str] = None

    # LLM providers
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    llm_base_url: Optional[str] = None
    llm_api_key: Optional[str] = None

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @property
    def base_path(self) -> Path:
        return Path(self.base_dir).expanduser()

    @property
    def log_path(self) -> Path:
        return Path(self.log_file).expanduser()

    @property
    def state_path(self) -> Path:
        return Path(self.state_file).expanduser()


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()