# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Core Application Settings
    APP_NAME: str = "ArogyaMitra API Backend"
    ENVIRONMENT: str = "development"
    
    # Database Settings
    DATABASE_URL: Optional[str] = None
    
    # Ola Maps API Settings
    OLA_MAPS_KRUTRIM_CLOUD_API_KEY: Optional[str] = None
    OLA_MAPS_KRUTRIM_CLOUD_API_BASE_URL: str = "https://api.olamaps.io"

    @property
    def resolved_ola_maps_api_key(self) -> str:
        return self.OLA_MAPS_KRUTRIM_CLOUD_API_KEY or ""

    @property
    def resolved_ola_maps_base_url(self) -> str:
        return self.OLA_MAPS_KRUTRIM_CLOUD_API_BASE_URL or "https://api.olamaps.io"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
