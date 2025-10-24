from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = "AI Lead Research"
    environment: str = Field("development", env="ENVIRONMENT")

    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4.1", env="OPENAI_MODEL")

    database_url: str = Field("sqlite:///./data/ai_leads.db", env="DATABASE_URL")
    max_lead_attempts: int = Field(6, env="MAX_LEAD_ATTEMPTS")
    min_leads_per_batch: int = Field(3, env="MIN_LEADS_PER_BATCH")

    log_level: str = Field("INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
