from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ticketing"
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
