# weather_service.py
"""Weather API service layer."""

import httpx
from typing import Dict
from config import Config


class WeatherServiceError(Exception):
    """Custom exception for weather service errors."""
    pass


class WeatherService:
    """Service for fetching weather data from OpenWeatherMap."""

    def __init__(self):
        self.api_key = Config.API_KEY
        self.base_url = Config.BASE_URL
        self.timeout = Config.TIMEOUT

    async def get_weather(self, city: str) -> Dict:
        """
        Fetches current weather data for a given city asynchronously.
        """
        city = city.strip()
        if not city:
            raise WeatherServiceError("City name cannot be empty")

        # Build request parameters
        params = {
            "q": city,
            "appid": self.api_key,
            "units": Config.UNITS,
        }

        try:
            # Make async HTTP request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.base_url, params=params)

                # Check for HTTP errors
                if response.status_code == 404:
                    raise WeatherServiceError(
                        f"City '{city}' not found. Please check the spelling."
                    )
                elif response.status_code == 401:
                    raise WeatherServiceError(
                        "Invalid API key. Please check your configuration."
                    )
                elif response.status_code != 200:
                    raise WeatherServiceError(
                        f"Error fetching weather data: {response.status_code}"
                    )

                # Parse JSON response
                data = response.json()
                return data

        except httpx.TimeoutException:
            raise WeatherServiceError(
                "Request timed out. Check your internet connection."
            )
        except httpx.ConnectError:
            raise WeatherServiceError(
                "Could not connect to the weather service API."
            )
        except Exception as e:
            # Catch all other exceptions
            raise WeatherServiceError(f"An unexpected error occurred: {e}")