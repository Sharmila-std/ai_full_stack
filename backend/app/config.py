from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    DATABASE_URL: str = Field(default="postgresql://postgres:postgres@localhost:5432/influencer_crm")
    SERPER_API_KEY: str = Field(default="")
    YOUTUBE_API_KEY: str = Field(default="")
    GROQ_API_KEY: str = Field(default="")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
