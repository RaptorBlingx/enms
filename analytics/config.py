"""
EnMS Analytics Service - Configuration
========================================
Manages environment variables and application settings.

Author: EnMS Team
Phase: 3 - Analytics & ML
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Service Information
    SERVICE_NAME: str = "EnMS Analytics Service"
    SERVICE_VERSION: str = "1.0.0"
    API_PORT: int = 8001
    API_PREFIX: str = "/api/v1"
    
    # Database Configuration
    DATABASE_HOST: str = "postgres"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "enms"
    DATABASE_USER: str = "raptorblingx"
    DATABASE_PASSWORD: str = "raptorblingx"
    DATABASE_MIN_POOL_SIZE: int = 5
    DATABASE_MAX_POOL_SIZE: int = 20
    
    # Model Storage
    MODEL_STORAGE_PATH: str = "/app/models/saved"
    
    # ML Model Configuration
    BASELINE_MIN_SAMPLES: int = 50  # Adjusted for hourly aggregates (50 hours = ~2 days minimum)
    BASELINE_MIN_R2: float = 0.80
    BASELINE_MIN_PVALUE: float = 0.05
    
    # Anomaly Detection Configuration
    ANOMALY_CONTAMINATION: float = 0.1
    ANOMALY_WARNING_THRESHOLD: float = 2.0  # Standard deviations
    ANOMALY_CRITICAL_THRESHOLD: float = 3.0  # Standard deviations
    
    # Forecasting Configuration
    FORECAST_SHORT_TERM_HOURS: int = 1
    FORECAST_MEDIUM_TERM_HOURS: int = 24
    FORECAST_LONG_TERM_DAYS: int = 7
    
    # KPI Configuration
    ENERGY_COST_PEAK_RATE: float = 0.20  # USD per kWh
    ENERGY_COST_OFFPEAK_RATE: float = 0.10  # USD per kWh
    CARBON_EMISSION_FACTOR: float = 0.45  # kg CO2 per kWh
    
    # Scheduler Configuration
    SCHEDULER_ENABLED: bool = True
    SCHEDULER_TIMEZONE: str = "UTC"
    
    # Job Schedules (cron format)
    JOB_BASELINE_RETRAIN_SCHEDULE: str = "0 2 * * 0"  # Sunday 02:00
    JOB_ANOMALY_DETECT_SCHEDULE: str = "5 * * * *"    # Every hour at :05
    JOB_KPI_CALCULATE_SCHEDULE: str = "30 0 * * *"    # Daily at 00:30
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # or "text"
    
    # Security (Phase 7)
    JWT_SECRET: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    
    # CORS Configuration
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    @property
    def database_url(self) -> str:
        """Construct async database URL."""
        return (
            f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )
    
    @property
    def database_url_asyncpg(self) -> str:
        """Construct asyncpg database URL."""
        return (
            f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )
    
    def get_peak_hours(self) -> tuple:
        """Get peak hours for time-of-use tariff (08:00-20:00)."""
        return (8, 20)
    
    def is_peak_hour(self, hour: int) -> bool:
        """Check if given hour is peak time."""
        peak_start, peak_end = self.get_peak_hours()
        return peak_start <= hour < peak_end


# Global settings instance
settings = Settings()


# Ensure model storage directory exists
os.makedirs(settings.MODEL_STORAGE_PATH, exist_ok=True)