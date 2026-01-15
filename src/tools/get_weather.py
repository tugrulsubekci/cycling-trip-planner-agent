"""Tool for getting typical weather for a location and month."""

import logging

from langchain.tools import tool
from pydantic import BaseModel, Field

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
        result = (
            f"Weather for {location} in {month}:\n"
            "- Temperature: [To be retrieved]\n"
            "- Precipitation: [To be retrieved]\n"
            "- Conditions: [To be retrieved]\n"
            "Note: This is a placeholder. Actual implementation pending."
        )
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
