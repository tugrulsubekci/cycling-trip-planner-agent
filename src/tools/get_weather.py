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


class GetWeatherOutput(BaseModel):
    """Output schema for get_weather tool."""

    location: str = Field(description="Location for weather data")
    month: str = Field(description="Month for weather data")
    avg_temperature_c: float = Field(description="Average temperature in Celsius")
    min_temperature_c: float = Field(description="Minimum temperature in Celsius")
    max_temperature_c: float = Field(description="Maximum temperature in Celsius")
    precipitation_mm: float = Field(description="Precipitation in millimeters")
    rainy_days: int = Field(description="Number of rainy days")
    conditions: str = Field(description="Weather conditions description")
    cycling_suitability: str = Field(description="Cycling suitability rating")


@tool(args_schema=GetWeatherInput)
def get_weather(location: str, month: str) -> dict:
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

        # Build structured output
        output = GetWeatherOutput(
            location=location,
            month=month,
            avg_temperature_c=weather_data.get("avg_temperature_c", 0),
            min_temperature_c=weather_data.get("min_temperature_c", 0),
            max_temperature_c=weather_data.get("max_temperature_c", 0),
            precipitation_mm=weather_data.get("precipitation_mm", 0),
            rainy_days=weather_data.get("rainy_days", 0),
            conditions=weather_data.get("conditions", "Unknown"),
            cycling_suitability=weather_data.get("cycling_suitability", "Unknown"),
        )

        # Return structured data as dict
        return output.model_dump()
    except Exception as e:
        logger.error(
            "get_weather error - location: %s, month: %s, error: %s",
            location,
            month,
            str(e),
            exc_info=True,
        )
        raise
