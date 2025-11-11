# Weather Application - Module 6 Lab

## Student Information
- **Name**: John Louie B. Bagaporo
- **Student ID**: 231002305
- **Course**: CCCS 106
- **Section**: 3A

## Project Overview
[Brief description of your weather app and what it does]

## Features Implemented
- Search History
- Temperature Unit Toggle
- Weather Location Icons and Colors
- 5-Day Weather Forecast


### Base Features
- [✔] City search functionality
- [✔] Current weather display
- [✔] Temperature, humidity, wind speed
- [✔] Weather icons
- [✔] Error handling
- [✔] Modern UI with Material Design


### Enhanced Features
1. **Temperature Unit Toggle (°C / °F)**
   - This feature uses a Flet Switch to let the user change the displayed temperature unit between Celsius and Fahrenheit. It was included for basic user accessibility. Technically, when the switch is flipped, the code updates the global (Config.UNITS) variable and immediately tells the app to fetch the weather data again. This is done to avoid local temperature conversions, which can be messy. By re-requesting the data, the OpenWeatherMap API handles the accurate unit conversion for us.

2. **Search History**
   - The app stores the last 10 searched city names in a file (search_history.json). This is displayed in a Flet Dropdown so the user can quickly search a city again without re-typing. This feature demonstrates file persistence (saving data between sessions) using Python's json module. When a new city is added, the code checks if it already exists, removes the old entry, and adds the new one to the top to ensure the list stays in Most Recently Used (MRU) order.

3. **5-Day Forecast Display**
    - The application fetches the full forecast data, which is hourly. It then processes this data to show only one clear entry per day for the next five days, usually picking the midday forecast. This keeps the display clean and provides the user with the necessary future outlook without showing too much unnecessary detail.

4. **Weather Condition Colors and Emojis**
    - The main weather display container now changes its background color based on the weather (e.g., yellow for sun, blue for rain). This provides a fast display. The coloring is controlled by a function that reads the weather's numerical condition ID from the API. This function uses simple range checks (like 300 <= ID < 600) to group similar conditions (drizzle, light rain) together and assign a single color, simplifying the complex mapping process.

## Screenshots
![What pops up at first opening](mod6_screenshots/MainGist.png)
![Search History](mod6_screenshots/SearchHistory.png)
![Search Results](mod6_screenshots/SearchHistory.png)
![Theme and Temperature Unit Toggle](mod6_screenshots/ThemeNTempUnitToggle.png)
![Display of the Five Day Forecast](mod6_screenshots/FiveDayForecast.png)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions
```bash
# Clone the repository
git clone https://github.com/<username>/cccs106-projects.git
cd cccs106-projects/mod6_labs

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your OpenWeatherMap API key to .env