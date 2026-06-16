from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "learning-growth-system"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"

    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    DATABASE_URL: str | None = None
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "learning_app"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "learning_growth"

    REDIS_URL: str | None = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    JWT_ALGORITHM: str = "HS256"

    DATA_DIR: str = "../data"
    RAW_DATA_DIR: str = "../data/raw"
    PROCESSED_DATA_DIR: str = "../data/processed"
    OCR_DATA_DIR: str = "../data/ocr"
    LOCAL_IMPORT_ROOT: str | None = None
    ALLOW_LOCAL_IMPORTS: bool = True

    LLM_PROVIDER: str = "mock"
    LLM_API_KEY: str | None = None
    LLM_BASE_URL: str | None = None
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TIMEOUT_SECONDS: int = 60
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 1200
    EMBEDDING_PROVIDER: str = "mock"
    EMBEDDING_API_KEY: str | None = None
    EMBEDDING_BASE_URL: str | None = None
    EMBEDDING_MODEL: str = "text-embedding-v4"
    EMBEDDING_DIMENSION: int | None = None
    EMBEDDING_DIM: int | None = None
    EMBEDDING_BATCH_SIZE: int = 32
    EMBEDDING_TIMEOUT_SECONDS: int = 30
    REDIS_VECTOR_INDEX_NAME: str = "idx:learning:chunks"
    REDIS_VECTOR_KEY_PREFIX: str = "learning:chunk"
    REDIS_VECTOR_DISTANCE_METRIC: str = "COSINE"
    AUTO_CREATE_TABLES: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"mysql+pymysql://{quote_plus(self.MYSQL_USER)}:{quote_plus(self.MYSQL_PASSWORD)}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{quote_plus(self.MYSQL_DATABASE)}?charset=utf8mb4"
        )

    @property
    def redis_url(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL
        auth = f":{quote_plus(self.REDIS_PASSWORD)}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def embedding_dimension(self) -> int:
        return self.EMBEDDING_DIMENSION or self.EMBEDDING_DIM or 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
