from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    """Application settings, read from the repo-root .env file or the environment."""

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    groq_api_key: str = ""
    groq_model: str = "qwen/qwen3.8-27b"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "documents"
    embedding_model: str = "intfloat/multilingual-e5-base"
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
