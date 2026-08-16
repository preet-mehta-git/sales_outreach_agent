import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AI Restaurant & Cafe Sales Engine"
    ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Outreach Safety Default (Rule 1.9 & Rule 54)
    OUTREACH_MODE: str = "DRY_RUN"  # DRY_RUN | LIVE
    
    # Target campaign default configuration
    DEFAULT_INDUSTRY: str = "restaurant_cafe"
    DEFAULT_CITY: str = "Ahmedabad"
    DEFAULT_STATE: str = "Gujarat"
    DEFAULT_COUNTRY: str = "India"
    
    # Database
    DATABASE_URL: str = "sqlite:///./sales_engine.db"
    
    # Third-party Provider API Keys (Optional in Dev / Mock mode)
    GOOGLE_PLACES_API_KEY: str | None = None
    SERP_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    
    # Minimum score threshold for qualification
    QUALIFICATION_THRESHOLD: int = 70
    PRIORITY_THRESHOLD: int = 80
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
