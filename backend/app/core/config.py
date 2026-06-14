from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "kaoyan-guide"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"

    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "root"
    MYSQL_DATABASE: str = "kaoyan_guide"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    JWT_ALGORITHM: str = "HS256"

    DATA_DIR: str = "../data"
    RAW_DATA_DIR: str = "../data/raw"
    PROCESSED_DATA_DIR: str = "../data/processed"
    OCR_DATA_DIR: str = "../data/ocr"

    EMBEDDING_DIM: int = 1536
    LLM_PROVIDER: str = "mock"
    EMBEDDING_PROVIDER: str = "mock"
    AUTO_CREATE_TABLES: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb4"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
