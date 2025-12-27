"""Configuration management for ClinicalTrial Agent."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Gemini API
    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"
    gemini_api_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    
    # MCP Server
    mcp_server_url: str = "http://localhost:8000"
    
    # Agent parameters
    agent_temperature: float = 0.7
    agent_max_tokens: int = 2048
    conversation_memory_window: int = 10
    
    # API Server
    agent_api_host: str = "0.0.0.0"
    agent_api_port: int = 8001
    
    #  Logging
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
