"""Configuration management for ClinicalTrials MCP Server."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Server configuration
    mcp_server_host: str = "0.0.0.0"
    mcp_server_port: int = 8000
    mcp_server_name: str = "ClinicalTrials-MCP"
    
    # ClinicalTrials.gov API
    clinical_trials_api_base_url: str = "https://clinicaltrials.gov/api/v2"
    
    # Logging
    log_level: str = "INFO"
    
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 60
    
    # Timeout settings
    http_timeout_seconds: int = 30
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
