from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

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
    # Ingestion is synchronous and embeds on CPU, so a long PDF would outlast
    # a typical host's request timeout. Tune after deploying.
    max_pages: int = 20
    # NoDecode so a plain comma-separated CORS_ORIGINS works in a hosting
    # dashboard; the default would demand a JSON array.
    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


settings = Settings()
