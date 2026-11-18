"""
Application configuration.

All settings are loaded from environment variables (via a .env file in
development). Nothing sensitive is hard-coded here — see .env.example
at the repo root for the variables this app expects.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "Trading Journal API"
    ENVIRONMENT: str = "development"  # development | production

    # --- Database ---
    # Example: postgresql+psycopg2://user:password@localhost:5432/trading_journal
    DATABASE_URL: str

    # --- Auth ---
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # --- Encryption for stored broker credentials ---
    # A Fernet key (generate with cryptography.fernet.Fernet.generate_key())
    CREDENTIAL_ENCRYPTION_KEY: str

    # --- Alpaca (paper trading only in this project) ---
    ALPACA_PAPER_BASE_URL: str = "https://paper-api.alpaca.markets"
    ALPACA_API_KEY: str
    ALPACA_SECRET_KEY: str
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
