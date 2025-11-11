import httpx
from typing import Dict
from config import Config


class WeatherServiceError(Exception):
    pass


class WeatherService:

    def __init__(self):
        self.api_key = Config.API_KEY
        self.base_url = Config.BASE_URL
        self.forecast_url = Config.FORECAST_URL
        self.timeout = Config.TIMEOUT

    async def _fetch_data(self, url: str, city: str) -> Dict:
        if not city:
            raise WeatherServiceError("City name cannot be empty")

        params = {
            "q": city,
            "appid": self.api_key,
            "units": Config.UNITS,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)

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
                        f"Error fetching data: {response.status_code}"
                    )

                return response.json()

        except httpx.TimeoutException:
            raise WeatherServiceError(
                "Request timed out. Check your internet connection."
            )
        except httpx.ConnectError:
            raise WeatherServiceError(
                "Could not connect to the weather service API."
            )
        except Exception as e:
            raise WeatherServiceError(f"An unexpected error occurred: {e}")

    async def get_current_weather(self, city: str) -> Dict:
        return await self._fetch_data(self.base_url, city)

    async def get_5day_forecast(self, city: str) -> Dict:
        return await self._fetch_data(self.forecast_url, city)