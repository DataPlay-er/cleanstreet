"""
config.py — Single source of truth for all environment-driven settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import secrets

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

   # Application
    app_name: str = "CleanSight Auth Service"
    environment: str = "development"          # "development" | "production"
    debug: bool = False

    # Database (PostgreSQL)
    database_url: str                         # REQUIRED — no default

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret_key: str                       # REQUIRED — no default

    jwt_algorithm: str = "HS256"

    # Access token: short-lived — only valid long enough to make one request
    # cycle; refresh token handles session continuity.
    jwt_access_token_expire_minutes: int = 15

    # Refresh token: longer lived, stored securely on the client
    jwt_refresh_token_expire_days: int = 7

    # Rate limiting (Redis-backed)
    # ------------------------------------------------------------------ #
    # Max failed login attempts before lockout
    rate_limit_max_attempts: int = 5

    # Lockout window in seconds (15 minutes)
    rate_limit_window_seconds: int = 900

    # Password policy
    password_min_length: int = 12
    password_require_uppercase: bool = True
    password_require_digit: bool = True
    password_require_special: bool = True

    cors_origins: list[str] = ["http://localhost:5173"]   # Vite dev server

    # Validation
    @field_validator("jwt_secret_key")
    @classmethod
    def jwt_secret_key_must_be_strong(cls, v: str) -> str:
        """
        Reject weak keys at startup — better to crash early than to
        run with an insecure secret.
        """
        if len(v) < 64:
            raise ValueError(
                "JWT_SECRET_KEY must be at least 64 characters. "
                "Generate one with: python -c \"import secrets; print(secrets.token_hex(64))\""
            )
        return v

    @field_validator("environment")
    @classmethod
    def environment_must_be_valid(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

settings = Settings()