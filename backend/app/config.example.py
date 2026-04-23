from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # MySQL Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "your_password"
    DB_NAME: str = "mydb"

    # PostgreSQL Vector Database (for RAG)
    VECTOR_DB_HOST: str = "localhost"
    VECTOR_DB_PORT: int = 5432
    VECTOR_DB_USER: str = "postgres"
    VECTOR_DB_PASSWORD: str = "your_password"
    VECTOR_DB_NAME: str = "postgres"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # LLM (Doubao)
    LLM_API_KEY: str = "your-api-key"
    LLM_API_URL: str = "https://ark.cn-beijing.volces.com/api/v3"
    LLM_MODEL_NAME: str = "doubao-seed-2-0-lite-260215"

    # Embedding Model (DashScope)
    DASHSCOPE_API_KEY: str = "your-api-key"
    EMBEDDING_MODEL: str = "text-embedding-v4"
    EMBEDDING_DIMENSION: int = 1024

    # Vision LLM for Food Recognition
    VISION_LLM_API_KEY: str = "your-api-key"
    VISION_LLM_MODEL: str = "qwen-vl-plus"
    VISION_LLM_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def VECTOR_DATABASE_URL(self) -> str:
        return f"postgresql+psycopg2://{self.VECTOR_DB_USER}:{self.VECTOR_DB_PASSWORD}@{self.VECTOR_DB_HOST}:{self.VECTOR_DB_PORT}/{self.VECTOR_DB_NAME}"

    class Config:
        env_file = ".env"


settings = Settings()
