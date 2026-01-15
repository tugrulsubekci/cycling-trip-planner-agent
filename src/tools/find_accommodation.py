"""Tool for finding accommodation near a location."""

import logging

from langchain.tools import tool
from pydantic import BaseModel, Field

logger: logging.Logger = logging.getLogger(__name__)


class FindAccommodationInput(BaseModel):
    """Input schema for find_accommodation tool."""

    location: str = Field(description="Location to search near (city, coordinates, or address)")
    accommodation_type: str = Field(
        default="all",
        description="Type of accommodation: camping, hostels, hotels, or all",
    )


@tool(args_schema=FindAccommodationInput)
def find_accommodation(location: str, accommodation_type: str = "all") -> str:
    """Find places to stay near a location (camping, hostels, hotels)."""
    logger.info(
        "find_accommodation called - location: %s, accommodation_type: %s",
        location,
        accommodation_type,
    )

    try:
        result = (
            f"Accommodation options near {location}:\n"
            f"- Type: {accommodation_type}\n"
            "- Results: [To be searched]\n"
            "Note: This is a placeholder. Actual implementation pending."
        )
        return result
    except Exception as e:
        logger.error(
            "find_accommodation error - location: %s, accommodation_type: %s, error: %s",
            location,
            accommodation_type,
            str(e),
            exc_info=True,
        )
        raise
