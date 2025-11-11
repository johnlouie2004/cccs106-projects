import flet as ft
import asyncio
from datetime import datetime
import json
from pathlib import Path
from weather_service import WeatherService, WeatherServiceError
from config import Config


class WeatherApp:

    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.current_city = ""
        
        self.history_file = Path("search_history.json")
        self.search_history = self._load_history()

        self.setup_page()
        self.build_ui()
        
    def _load_history(self):
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def _save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.search_history, f)

    def _add_to_history(self, city: str):
        city = city.strip()
        if not city:
            return
            
        if city in self.search_history:
            self.search_history.remove(city)

        self.search_history.insert(0, city)
        self.search_history = self.search_history[:10]
        self._save_history()
        self._update_history_dropdown()

    def _update_history_dropdown(self):
        self.history_dropdown.options = [
            ft.dropdown.Option(city) for city in self.search_history
        ]
        self.page.update()
    
    def _on_history_select(self, e):
        if e.control.value:
            self.city_input.value = e.control.value
            self.current_city = e.control.value
            self.page.run_task(self.get_weather)
            e.control.value = None
            self.page.update()
            

    def setup_page(self):
        self.page.title = Config.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 20
        self.page.scroll = ft.ScrollMode.ADAPTIVE 
        
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = Config.APP_HEIGHT
        self.page.window.resizable = True
        self.page.window.center()

    def build_ui(self):        
        self.title = ft.Text("Weather App", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)
        
        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Toggle theme",
            on_click=self.toggle_theme,
        )

        self.unit_toggle = ft.Switch(
            label="°C / °F",
            value=False,
            tooltip="Toggle temperature unit",
            on_change=self.toggle_units,
        )

        title_row = ft.Row(
            [self.title, self.theme_button],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self.city_input = ft.TextField(
            label="Enter city name",
            hint_text="Format should be [City], [Country (ISO Alpha-2)]",
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

        self.history_dropdown = ft.Dropdown(
            label="Search History",
            hint_text="Select a recent city",
            options=[ft.dropdown.Option(city) for city in self.search_history],
            on_change=self._on_history_select,
            width=200
        )
        
        self.loading = ft.ProgressRing(visible=False, width=30, height=30)
        self.error_message = ft.Text("", color=ft.Colors.RED_700, visible=False)

        self.current_weather_container = ft.Container(
            visible=False,
            opacity=0.0,
            animate_opacity=300,
            bgcolor=ft.Colors.BLUE_50, 
            border_radius=10,
            padding=20,
        )

        self.forecast_container = ft.Container(
            visible=False,
            opacity=0.0,
            animate_opacity=300,
            border_radius=10,
            margin=ft.margin.only(top=20),
            padding=ft.padding.all(10),
            content=ft.Column(
                [
                    ft.Text("5-Day Forecast", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                    ft.Divider(),
                    ft.Column(scroll=ft.ScrollMode.ADAPTIVE),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        self.page.add(
            ft.Column(
                [
                    title_row,
                    ft.Row([self.history_dropdown, ft.Container(width=10), self.unit_toggle], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    self.city_input,
                    ft.Row([self.search_button], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    self.loading,
                    self.error_message,
                    self.current_weather_container,
                    self.forecast_container,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )
        )
        self.page.update()


    def _get_weather_theme(self, condition_id: int):
        
        if 200 <= condition_id < 300: # Thunderstorm
            return ft.Colors.BLUE_GREY_100, "🌩️ Thunderstorm"
        elif 300 <= condition_id < 600: # Drizzle/Rain
            return ft.Colors.BLUE_200, "🌧️ Rainy"
        elif 600 <= condition_id < 700: # Snow
            return ft.Colors.LIGHT_BLUE_50, "❄️ Snowy"
        elif 700 <= condition_id < 800: # Atmosphere (Mist, Smoke, Haze)
            return ft.Colors.GREY_300, "🌫️ Hazy"
        elif condition_id == 800: # Clear
            return ft.Colors.YELLOW_100, "☀️ Clear Sky"
        elif 801 <= condition_id < 900: # Clouds
            return ft.Colors.BLUE_GREY_50, "☁️ Cloudy"
        else:
            return ft.Colors.BLUE_50, "Unknown"


    def toggle_theme(self, e):
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE
        self.page.update()

    def toggle_units(self, e):
        Config.UNITS = "imperial" if e.control.value else "metric"
        unit_symbol = "F" if Config.UNITS == "imperial" else "C"
        self.page.title = f"Flet Weather App (°{unit_symbol})"
        self.page.update()
        
        if self.current_city:
            self.page.run_task(self.get_weather)

    def on_search(self, e):
        self.current_city = self.city_input.value.strip()
        self.page.run_task(self.get_weather) 

    async def get_weather(self):
        city = self.current_city

        if not city:
            self.show_error("Please enter a city name")
            return

        self.loading.visible = True
        self.error_message.visible = False
        self.current_weather_container.visible = False
        self.forecast_container.visible = False
        self.page.update()

        try:
            current_task = self.weather_service.get_current_weather(city)
            forecast_task = self.weather_service.get_5day_forecast(city)
            
            current_data, forecast_data = await asyncio.gather(current_task, forecast_task)
            
            self._add_to_history(city) 
            
            self.display_current_weather(current_data)
            self.display_5day_forecast(forecast_data)

        except WeatherServiceError as e:
            self.show_error(str(e))
        except Exception as e:
            self.show_error(f"A general error occurred: {e}")

        finally:
            self.loading.visible = False
            self.page.update()

    def display_current_weather(self, data: dict):
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp = data.get("main", {}).get("temp", 0)
        feels_like = data.get("main", {}).get("feels_like", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        weather_info = data.get("weather", [{}])[0]
        icon_code = weather_info.get("icon", "01d")
        condition_id = weather_info.get("id", 800) 
        wind_speed = data.get("wind", {}).get("speed", 0)
        
        new_color, emoji_desc = self._get_weather_theme(condition_id)
        self.current_weather_container.bgcolor = new_color
        
        unit = "°F" if Config.UNITS == "imperial" else "°C"
        wind_unit = "mph" if Config.UNITS == "imperial" else "m/s"

        self.current_weather_container.content = ft.Column(
            [
                ft.Text(f"{city_name}, {country}", size=24, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        ft.Image(src=f"https://openweathermap.org/img/wn/{icon_code}@2x.png", 
                                 width=100, height=100), 
                        ft.Text(f"{emoji_desc}", size=20, italic=True),
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
                        self.create_info_card(ft.Icons.AIR, "Wind Speed", f"{wind_speed:.1f} {wind_unit}"),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        self.current_weather_container.visible = True
        self.current_weather_container.opacity = 0.0
        self.page.update()
        asyncio.get_event_loop().call_later(0.05, lambda: self._animate_fade(self.current_weather_container))


    def display_5day_forecast(self, data: dict):
        
        forecast_list = data.get("list", [])
        daily_forecast = self._process_forecast_data(forecast_list)
        
        forecast_cards = []
        unit = "°F" if Config.UNITS == "imperial" else "°C"

        for entry in daily_forecast:
            day_name = entry["day"]
            temp = entry["temp"]
            icon = entry["icon"]
            description = entry["description"]
            
            card = ft.Container(
                content=ft.Row(
                    [
                        ft.Text(day_name, size=16, weight=ft.FontWeight.BOLD, width=80),
                        ft.Image(src=f"https://openweathermap.org/img/wn/{icon}@2x.png", width=50, height=50),
                        ft.Text(description, size=14, color=ft.Colors.GREY_700, expand=True),
                        ft.Text(f"{temp:.0f}{unit}", size=18, weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                padding=ft.padding.symmetric(vertical=5, horizontal=10),
                border=ft.border.only(bottom=ft.border.BorderSide(0.5, ft.Colors.BLACK12)),
            )
            forecast_cards.append(card)
        
        forecast_col = self.forecast_container.content.controls[2]
        forecast_col.controls = forecast_cards
        
        self.forecast_container.visible = True
        self.forecast_container.opacity = 0.0
        self.page.update()
        
        asyncio.get_event_loop().call_later(0.05, lambda: self._animate_fade(self.forecast_container))

    def _process_forecast_data(self, forecast_list):
        daily_data = {}
        today = datetime.now().date()
        
        for item in forecast_list:
            dt_txt = datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S')
            day = dt_txt.date()

            if day == today:
                continue

            if day not in daily_data or abs(dt_txt.hour - 12) < abs(daily_data[day]['dt'].hour - 12):
                daily_data[day] = {
                    'dt': dt_txt,
                    'day': dt_txt.strftime('%A'),
                    'temp': item['main']['temp'],
                    'icon': item['weather'][0]['icon'],
                    'description': item['weather'][0]['description'].title(),
                }

        return list(daily_data.values())[:5]


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

    def _animate_fade(self, control: ft.Container):
        control.opacity = 1.0
        self.page.update()

    def show_error(self, message: str):
        self.error_message.value = f"❌ {message}"
        self.error_message.visible = True
        self.current_weather_container.visible = False
        self.forecast_container.visible = False
        self.page.update()


def main(page: ft.Page):
    try:
        WeatherApp(page)
    except ValueError as e:
        page.add(ft.Text(f"Configuration Error: {e}", color=ft.Colors.RED_900))
        page.update()


if __name__ == "__main__":
    ft.app(target=main)