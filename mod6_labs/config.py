import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    BASE_URL = os.getenv(
        "OPENWEATHER_BASE_URL", 
        "https://api.openweathermap.org/data/2.5/weather"
    )
    FORECAST_URL = os.getenv(
        "OPENWEATHER_FORECAST_URL",
        "https://api.openweathermap.org/data/2.5/forecast"
    )

    APP_TITLE = "Flet Enhanced Weather App"
    APP_WIDTH = 450
    APP_HEIGHT = 750

    UNITS = "metric"  
    TIMEOUT = 10 

    @classmethod
    def validate(cls):
        if not cls.API_KEY or cls.API_KEY == "your_api_key_here":
            raise ValueError(
                "OPENWEATHER_API_KEY not found or default value used. "
                "Please check your .env file."
            )
        return True

Config.validate()