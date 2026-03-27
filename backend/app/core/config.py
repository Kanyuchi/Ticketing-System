from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ticketing"

    @model_validator(mode="after")
    def _normalize_database_url(self):
        """Ensure database_url uses asyncpg driver for async SQLAlchemy."""
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        self.database_url = url
        return self
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_publishable_key: str = ""

    frontend_url: str = "http://localhost:3000"

    sendgrid_api_key: str = ""
    from_email: str = "tickets@proofoftalk.io"

    google_sheets_credentials_file: str = ""
    google_sheets_id: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
