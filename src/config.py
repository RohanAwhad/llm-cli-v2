from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings loaded from environment variables or .env file."""
    
    # API keys
    LANGFUSE_PUBLIC_KEY: str
    LANGFUSE_SECRET_KEY: str
    GEMINI_API_KEY: str
    BRAVE_SEARCH_AI_API_KEY: str
    
    # Configure settings to load from .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Create settings instance
settings = Settings()
