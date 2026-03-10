from pydantic_settings import BaseSettings
from pydantic import ConfigDict, model_validator


class Settings(BaseSettings):
    APP_NAME: str = "Order Platform"
    API_V1_PREFIX: str = "/api/v1"
    ENV: str = "local"

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "order_platform"
    POSTGRES_USER: str = "order_user"
    POSTGRES_PASSWORD: str

    DATABASE_URL: str = ""

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    LOG_LEVEL: str = "INFO"

    @model_validator(mode="after")
    def assemble_database_url(self) -> "Settings":
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return self

    model_config = ConfigDict(
        env_file=".env",
        extra="allow",
    )


settings = Settings()