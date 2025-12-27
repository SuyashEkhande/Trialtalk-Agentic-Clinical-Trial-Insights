"""Configuration for Streamlit UI."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """UI settings."""
    
    agent_api_url: str = "http://localhost:8001"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()
