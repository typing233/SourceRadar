import secrets
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    DATABASE_URL: str = "sqlite:///./data/sourceradar.db"
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "SourceRadar <noreply@sourceradar.dev>"
    # Comma-separated list of allowed CORS origins. Use "*" for all (dev only).
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"


def _get_settings() -> Settings:
    s = Settings()
    if not s.SECRET_KEY:
        import warnings
        s.SECRET_KEY = secrets.token_hex(32)
        warnings.warn(
            "SECRET_KEY is not set; using a random key. Set SECRET_KEY in .env for production.",
            stacklevel=2,
        )
    return s


settings = _get_settings()
