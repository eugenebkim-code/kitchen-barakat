from typing import Any, List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Kitchen Barakat"
    TZ: str = "Asia/Seoul"
    DEBUG: bool = False

    # Telegram Bot
    BOT_TOKEN: str
    ADMIN_TELEGRAM_IDS: Union[str, List[int]] = []
    OWNER_CHAT_ID: str = ""

    # Security
    KITCHEN_WS_SECRET: str
    CORS_ORIGINS: Union[str, List[str]] = ["*"]

    # Database
    DATABASE_URL: str

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Any) -> str:
        # No fallback to a local SQLite file here on purpose: the container's
        # filesystem is wiped on every Railway redeploy, so silently falling
        # back would look like working, then quietly lose all data (menu,
        # orders, users) on the next deploy. Fail loudly instead.
        if not v or not isinstance(v, str):
            raise ValueError("DATABASE_URL is required and must point to a persistent database")

        db_url = str(v).strip()
        # Handle quoted strings if any
        if (db_url.startswith('"') and db_url.endswith('"')) or (db_url.startswith("'") and db_url.endswith("'")):
            db_url = db_url[1:-1].strip()

        if not db_url:
            raise ValueError("DATABASE_URL is required and must point to a persistent database")

        # Convert Postgres URL provided by Railway to AsyncPG driver
        if db_url.startswith("postgres://"):
            return db_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
            return db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        return db_url

    # Business Defaults
    DEFAULT_DELIVERY_FEE: int = 3000
    BANK_NAME: str = "KB Kookmin Bank"
    BANK_ACCOUNT: str = "123-4567-890123"
    BANK_HOLDER: str = "KIM OWNER"

    @field_validator("ADMIN_TELEGRAM_IDS", mode="before")
    @classmethod
    def parse_admin_ids(cls, v: Any) -> List[int]:
        if isinstance(v, int):
            return [v]
        if isinstance(v, str):
            if not v.strip():
                return []
            return [int(x.strip()) for x in v.split(",") if x.strip().isdigit()]
        if isinstance(v, list):
            return [int(x) for x in v]
        return []

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if not v.strip():
                return ["*"]
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
