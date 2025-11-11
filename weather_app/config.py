# config.py
"""Configuration management for the Weather App."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration."""

    # API Configuration
    API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    BASE_URL = os.getenv(
        "OPENWEATHER_BASE_URL", 
        "https://api.openweathermap.org/data/2.5/weather"
    )

    # App Configuration
    APP_TITLE = "Flet Weather App"
    APP_WIDTH = 400
    APP_HEIGHT = 600

    # API Settings
    UNITS = "metric"  # Options: metric (°C), imperial (°F), or standard (K)
    TIMEOUT = 10  # seconds

    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        if not cls.API_KEY or cls.API_KEY == "your_api_key_here":
            raise ValueError(
                "OPENWEATHER_API_KEY not found or default value used. "
                "Please check your .env file."
            )
        return True

# Validate configuration on import
Config.validate()