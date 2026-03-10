from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Order Platform"
    API_V1_PREFIX: str = "/api/v1"
    ENV: str = "local"

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    LOG_LEVEL: str = "INFO"

    model_config = ConfigDict(
        env_file=".env",
        extra="allow",
    )


settings = Settings()