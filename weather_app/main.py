import flet as ft
import asyncio
from weather_service import WeatherService, WeatherServiceError
from config import Config


class WeatherApp:
    """Main Weather Application class."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.setup_page()
        self.build_ui()

    def setup_page(self):
        """Configure page settings."""
        self.page.title = Config.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 20
        
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = Config.APP_HEIGHT
        self.page.window.resizable = False
        self.page.window.center()

    def build_ui(self):
        
        self.title = ft.Text("Weather App", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)
        
        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Toggle theme",
            on_click=self.toggle_theme,
        )

        title_row = ft.Row(
            [self.title, self.theme_button],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self.city_input = ft.TextField(
            label="Enter city name",
            hint_text="e.g., London, Tokyo, New York",
            prefix_icon=ft.Icons.LOCATION_CITY,
            autofocus=True,
            on_submit=self.on_search, 
        )

        self.search_button = ft.ElevatedButton(
            "Get Weather",
            icon=ft.Icons.SEARCH,
            on_click=self.on_search,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE_700),
        )

        self.weather_container = ft.Container(
            visible=False,
            opacity=0.0,
            animate_opacity=300,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=20,
        )

        self.error_message = ft.Text("", color=ft.Colors.RED_700, visible=False)

        self.loading = ft.ProgressRing(visible=False, width=30, height=30)

        self.page.add(
            ft.Column(
                [
                    title_row,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.city_input,
                    self.search_button,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.loading,
                    self.error_message,
                    self.weather_container,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                scroll=ft.ScrollMode.ADAPTIVE 
            )
        )
        self.page.update()

    def toggle_theme(self, e):
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE
        self.page.update()

    def on_search(self, e):
        self.page.run_task(self.get_weather) 

    async def get_weather(self):
        city = self.city_input.value.strip()

        if not city:
            self.show_error("Please enter a city name")
            return

        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.page.update()

        try:
            weather_data = await self.weather_service.get_weather(city)
            await self.display_weather(weather_data)

        except WeatherServiceError as e:
            self.show_error(str(e))
        except Exception as e:
            self.show_error(f"A general error occurred: {e}")

        finally:
            self.loading.visible = False
            self.page.update()

    async def display_weather(self, data: dict):
        
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp = data.get("main", {}).get("temp", 0)
        feels_like = data.get("main", {}).get("feels_like", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        description = data.get("weather", [{}])[0].get("description", "").title()
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        wind_speed = data.get("wind", {}).get("speed", 0)
        unit = "°C" if Config.UNITS == "metric" else "°F"

        self.weather_container.content = ft.Column(
            [
                ft.Text(f"{city_name}, {country}", size=24, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        ft.Image(src=f"https://openweathermap.org/img/wn/{icon_code}@2x.png", 
                                 width=100, height=100), 
                        ft.Text(description, size=20, italic=True),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),

                ft.Text(
                    f"{temp:.1f}{unit}",
                    size=48,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_900,
                ),

                ft.Text(f"Feels like {feels_like:.1f}{unit}", size=16, color=ft.Colors.GREY_700),
                ft.Divider(),

                ft.Row(
                    [
                        self.create_info_card(ft.Icons.WATER_DROP, "Humidity", f"{humidity}%"),
                        self.create_info_card(ft.Icons.AIR, "Wind Speed", f"{wind_speed} m/s"),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        self.weather_container.visible = True
        self.weather_container.opacity = 0.0
        self.error_message.visible = False
        self.page.update()

        await asyncio.sleep(0.05) 
        self.weather_container.opacity = 1.0
        self.page.update()


    def create_info_card(self, icon, label, value):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=30, color=ft.Colors.BLUE_700),
                    ft.Text(label, size=12, color=ft.Colors.GREY_600),
                    ft.Text(value, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=15,
            width=150,
            shadow=ft.BoxShadow(
                blur_radius=10, 
                spread_radius=1, 
                color=ft.Colors.BLACK54, 
                offset=ft.Offset(0, 5),
            )
        )

    def show_error(self, message: str):
        self.error_message.value = f"❌ {message}"
        self.error_message.visible = True
        self.weather_container.visible = False
        self.page.update()


def main(page: ft.Page):
    try:
        WeatherApp(page)
    except ValueError as e:
        page.add(ft.Text(f"Configuration Error: {e}", color=ft.Colors.RED_900))
        page.update()


if __name__ == "__main__":
    ft.app(target=main)