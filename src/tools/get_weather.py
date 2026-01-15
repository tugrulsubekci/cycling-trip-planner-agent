"""Tool for getting typical weather for a location and month."""

import logging

from langchain.tools import tool
from pydantic import BaseModel, Field

from src.data.mock_data import find_weather

logger: logging.Logger = logging.getLogger(__name__)


class GetWeatherInput(BaseModel):
    """Input schema for get_weather tool."""

    location: str = Field(description="Location to get weather for (city, coordinates, or address)")
    month: str = Field(description="Month name or number (e.g., January or 1)")


@tool(args_schema=GetWeatherInput)
def get_weather(location: str, month: str) -> str:
    """Get typical weather for a location and month."""
    logger.info(
        "get_weather called - location: %s, month: %s",
        location,
        month,
    )

    try:
        # Find weather data using fuzzy matching
        weather_data = find_weather(location, month)

        if not weather_data:
            return (
                f"No weather data found for {location} in {month}.\n"
                "Please check the location name and month, and try again."
            )

        # Extract weather information
        avg_temp = weather_data.get("avg_temperature_c", 0)
        min_temp = weather_data.get("min_temperature_c", 0)
        max_temp = weather_data.get("max_temperature_c", 0)
        precipitation = weather_data.get("precipitation_mm", 0)
        rainy_days = weather_data.get("rainy_days", 0)
        conditions = weather_data.get("conditions", "Unknown")
        suitability = weather_data.get("cycling_suitability", "Unknown")

        # Format result string
        result = f"Weather for {location} in {month}:\n"
        result += f"- Average Temperature: {avg_temp}°C (min: {min_temp}°C, max: {max_temp}°C)\n"
        result += f"- Precipitation: {precipitation}mm\n"
        result += f"- Rainy Days: {rainy_days} days\n"
        result += f"- Conditions: {conditions}\n"
        result += f"- Cycling Suitability: {suitability}"

        return result
    except Exception as e:
        logger.error(
            "get_weather error - location: %s, month: %s, error: %s",
            location,
            month,
            str(e),
            exc_info=True,
        )
        raise
