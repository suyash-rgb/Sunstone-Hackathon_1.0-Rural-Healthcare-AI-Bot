# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

# Pydantic's PostgresDsn type can be used for stricter validation if desired, 
# but a simple str is sufficient for a generic connection string.

class Settings(BaseSettings):
    # Core Application Settings
    APP_NAME: str = "FastAPI Backend"
    ENVIRONMENT: str = "development"
    
    # Database Settings
    DATABASE_URL: str 
    
    # Configuration for Pydantic Settings
    # This tells BaseSettings to look for a .env file
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding='utf-8',
        case_sensitive=True # Good practice for environment variables
    )

# Instantiate the settings object (singleton pattern is often used for settings)
settings = Settings()