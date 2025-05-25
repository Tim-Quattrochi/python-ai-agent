"""Weather tool for getting weather information."""

import os
import requests
from typing import Dict, Any
from .base import Tool
import logging

logger = logging.getLogger(__name__)


class WeatherTool(Tool):
    """Tool for getting weather information."""

    def __init__(self):
        super().__init__(
            name="weather",
            description="Get weather information for any location. Operations: current, forecast"
        )
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"

        if not self.api_key:
            logger.warning(
                "OPENWEATHER_API_KEY not set. Weather operations will be limited.")

    def execute(self, operation: str, **kwargs) -> str:
        """Execute weather operations."""
        try:
            if operation == "current":
                return self._get_current_weather(kwargs.get('location'))
            elif operation == "forecast":
                return self._get_forecast(kwargs.get('location'), kwargs.get('days', 5))
            elif operation == "help":
                return self._get_help()
            else:
                return f"❌ Unknown operation '{operation}'. Available: current, forecast, help"
        except Exception as e:
            logger.error(f"Weather tool error: {e}")
            return f"❌ Error executing {operation}: {str(e)}"

    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for weather tool parameters."""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["current", "forecast", "help"],
                    "description": "The weather operation to perform"
                },
                "location": {
                    "type": "string",
                    "description": "City name or coordinates (lat,lon) for weather lookup"
                },
                "days": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 16,
                    "default": 5,
                    "description": "Number of days for forecast (1-16)"
                }
            },
            "required": ["operation"],
            "additionalProperties": False
        }

    def _get_current_weather(self, location: str) -> str:
        """Get current weather for a location."""
        if not location:
            return "❌ Error: Location is required for weather lookup"

        if not self.api_key:
            return "❌ Error: OpenWeather API key not configured. Set OPENWEATHER_API_KEY in .env file"

        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric'
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Format weather data nicely
            weather_info = f"🌤️ **Weather in {data['name']}, {data['sys']['country']}**\n\n"
            weather_info += f"🌡️ **Temperature:** {data['main']['temp']}°C (feels like {data['main']['feels_like']}°C)\n"
            weather_info += f"📝 **Description:** {data['weather'][0]['description'].title()}\n"
            weather_info += f"💧 **Humidity:** {data['main']['humidity']}%\n"
            weather_info += f"🌪️ **Wind:** {data.get('wind', {}).get('speed', 0)} m/s\n"
            weather_info += f"👁️ **Visibility:** {data.get('visibility', 'N/A')} meters\n"
            weather_info += f"🌅 **Sunrise:** {self._format_time(data['sys']['sunrise'])}\n"
            weather_info += f"🌇 **Sunset:** {self._format_time(data['sys']['sunset'])}"

            logger.info(f"Retrieved weather for {location}")
            return weather_info

        except requests.exceptions.RequestException as e:
            error_msg = f"❌ Error fetching weather data: {str(e)}"
            logger.error(error_msg)
            return error_msg
        except KeyError as e:
            error_msg = f"❌ Error parsing weather data: Missing field {str(e)}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"❌ Unexpected error getting weather: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def _get_forecast(self, location: str, days: int = 5) -> str:
        """Get weather forecast for a location."""
        if not location:
            return "❌ Error: Location is required for weather forecast"

        if not self.api_key:
            return "❌ Error: OpenWeather API key not configured. Set OPENWEATHER_API_KEY in .env file"

        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric',
                # API returns 8 forecasts per day, max 40
                'cnt': min(days * 8, 40)
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            forecast_info = f"📅 **{days}-Day Weather Forecast for {data['city']['name']}, {data['city']['country']}**\n\n"

            # Group forecasts by day
            daily_forecasts = {}
            for forecast in data['list']:
                date = forecast['dt_txt'].split(' ')[0]
                if date not in daily_forecasts:
                    daily_forecasts[date] = []
                daily_forecasts[date].append(forecast)

            # Show forecast for each day
            for i, (date, forecasts) in enumerate(list(daily_forecasts.items())[:days]):
                if i > 0:
                    forecast_info += "\n"

                # Get average temp for the day
                temps = [f['main']['temp'] for f in forecasts]
                avg_temp = sum(temps) / len(temps)
                max_temp = max(temps)
                min_temp = min(temps)

                # Get most common weather description
                descriptions = [f['weather'][0]['description']
                                for f in forecasts]
                main_description = max(
                    set(descriptions), key=descriptions.count)

                forecast_info += f"📆 **{date}**\n"
                forecast_info += f"   🌡️ {min_temp:.1f}°C - {max_temp:.1f}°C (avg: {avg_temp:.1f}°C)\n"
                forecast_info += f"   📝 {main_description.title()}\n"

            logger.info(f"Retrieved {days}-day forecast for {location}")
            return forecast_info

        except requests.exceptions.RequestException as e:
            error_msg = f"❌ Error fetching forecast data: {str(e)}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"❌ Unexpected error getting forecast: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def _format_time(self, timestamp: int) -> str:
        """Format Unix timestamp to readable time."""
        try:
            from datetime import datetime
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%H:%M")
        except:
            return "N/A"

    def _get_help(self) -> str:
        """Return help information for the weather tool."""
        return """🌤️ **Weather Tool Help**

**Operations:**
• `current` - Get current weather for a location
• `forecast` - Get weather forecast (default 5 days)
• `help` - Show this help message

**Examples:**
• "Get current weather for New York"
• "What's the weather like in London?"
• "Show me a 3-day forecast for Tokyo"
• "Current weather in San Francisco"

**Setup:**
To use this tool, you need an OpenWeatherMap API key:
1. Sign up at https://openweathermap.org/api
2. Get your free API key
3. Add it to your .env file: `OPENWEATHER_API_KEY=your_key_here`
"""
