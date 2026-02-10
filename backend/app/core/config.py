from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Order Platform"
    API_V1_PREFIX: str = "/api/v1"
    ENV: str = "local"

    # Database (we only actually use DATABASE_URL in code)
    DATABASE_URL: str

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = ConfigDict(
        env_file=".env",
        extra="allow",  # 🔥 THIS IS THE FIX
    )


settings = Settings()
