import requests # For API call
from datetime import datetime
from zoneinfo import ZoneInfo

COORDS = {
    'Los Angeles': (34.060257, -118.23433),
    'Houston': (29.7633, -95.3633),
    'New York': (40.7143, -74.006)
}

icon_map = {
    0: "01",                        # Clear sky
    1: "02", 2: "02", 3: "03",      # Partly cloudy
    45: "50", 48: "50",             # Fog
    51: "09", 53: "09", 55: "09",   # Drizzle
    61: "10", 63: "10", 65: "10",   # Rain
    71: "13", 73: "13", 75: "13",   # Snow
    80: "09", 81: "09", 82: "09",   # Showers
    95: "11",                       # Thunderstorm
  }

weather_desc = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Drizzle: Light",
    53: "Drizzle: Moderate",
    55: "Drizzle: Dense",
    56: "Freezing Drizzle: Light",
    57: "Freezing Drizzle: Dense",
    61: "Rain: Slight",
    63: "Rain: Moderate",
    65: "Rain: Heavy",
    66: "Freezing Rain: Light",
    67: "Freezing Rain: Heavy",
    71: "Snow fall: Slight",
    73: "Snow fall: Moderate",
    75: "Snow fall: Heavy",
    77: "Snow grains",
    80: "Rain showers: Slight",
    81: "Rain showers: Moderate",
    82: "Rain showers: Violent",
    85: "Snow showers: Slight",
    86: "Snow showers: Heavy",
    95: "Thunderstorm: Slight or moderate",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

def getCurrentWeather(city):
    current_weather = {}
    lat, long = COORDS[city]
    city_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&current=temperature_2m,is_day,weather_code,wind_speed_10m,wind_direction_10m,relative_humidity_2m&timezone=auto&forecast_days=1&wind_speed_unit=mph&temperature_unit=fahrenheit"
    response = requests.get(city_url)
    if response.status_code == 200:
        response_json = response.json()
        timezone = response_json['timezone']
        data = response_json['current']
        current_weather['timezone'] = response_json['timezone']
        current_weather['temp'] = data['temperature_2m']
        wicon_suffix = 'd' if data['is_day'] else 'n'
        current_weather['weather_desc'] = weather_desc[data['weather_code']]
        current_weather['wicon'] = f"https://openweathermap.org/img/wn/{icon_map[data['weather_code']]}{wicon_suffix}@2x.png"
        current_weather['wind_speed'] = data['wind_speed_10m']
        current_weather['wind_direction'] = data['wind_direction_10m']
        current_weather['humidity'] = data['relative_humidity_2m']
        
    else:
        raise ConnectionError(f'Weather API request failed with status code: {response.status_code}.')

    return current_weather

