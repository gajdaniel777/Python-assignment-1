from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./subledger.db"
    app_title: str = "SubLedger"
    app_version: str = "1.0.0"


settings = Settings()
