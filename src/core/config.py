"""Configuration management with Pydantic."""
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with validation."""
    
    # Twitter API
    twitter_bearer_token: Optional[str] = Field(None, description="Twitter API Bearer Token")
    twitter_client_id: Optional[str] = Field(None, description="Twitter Client ID")
    twitter_client_secret: Optional[str] = Field(None, description="Twitter Client Secret")
    
    # Twitter OAuth 1.0a (for posting)
    twitter_api_key: Optional[str] = Field(None, description="Twitter API Key")
    twitter_api_secret: Optional[str] = Field(None, description="Twitter API Secret")
    twitter_access_token: Optional[str] = Field(None, description="Twitter Access Token")
    twitter_access_token_secret: Optional[str] = Field(None, description="Twitter Access Token Secret")
    
    # Ollama
    ollama_host: str = Field("http://localhost:11434", description="Ollama host URL")
    ollama_model: str = Field("qwen3:14b", description="Ollama model name")
    
    # GitHub
    github_token: Optional[str] = Field(None, description="GitHub API token (optional)")
    
    # OpenRouter (future use)
    openrouter_api_key: Optional[str] = Field(None, description="OpenRouter API key (optional)")
    
    # Additional AI APIs
    gemini_api_key: Optional[str] = Field(None, description="Google Gemini API key (optional)")
    mistral_api_key: Optional[str] = Field(None, description="Mistral API key (optional)")
    
    # App settings
    tweet_interval_hours: int = Field(4, description="Hours between tweets")
    max_trending_repos: int = Field(10, description="Max repos to fetch")
    screenshot_timeout: int = Field(30, description="Screenshot timeout in seconds")
    
    # Directories
    data_dir: str = Field("data", description="Data directory")
    logs_dir: str = Field("logs", description="Logs directory")
    screenshots_dir: str = Field("screenshots", description="Screenshots directory")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields in .env


# Global settings instance
settings = Settings()