from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    APP_ENV: str = "development"

    # Database
    DATABASE_URL: str


def make_settings() -> "Settings":
    """Lazy settings"""
    settings = Settings()
    return settings
