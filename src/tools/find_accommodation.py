"""Tool for finding accommodation near a location."""

import logging

from langchain.tools import tool
from pydantic import BaseModel, Field

from src.data.mock_data import find_accommodations

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
        # Find accommodations using fuzzy matching
        accommodations = find_accommodations(location, accommodation_type)

        if not accommodations:
            type_info = f" (type: {accommodation_type})" if accommodation_type != "all" else ""
            return (
                f"No accommodations found near {location}{type_info}.\n"
                "Please check the location name and try again."
            )

        # Build result string
        type_display = (
            accommodation_type.capitalize() if accommodation_type != "all" else "All types"
        )
        result = f"Accommodation options near {location}:\n"
        result += f"- Filter: {type_display}\n"
        result += f"- Found: {len(accommodations)} option(s)\n\n"

        # Format each accommodation
        for i, acc in enumerate(accommodations, 1):
            acc_name = acc.get("name", "Unknown")
            acc_type = acc.get("type", "unknown").capitalize()
            price = acc.get("price_per_night", 0)
            currency = acc.get("currency", "EUR")
            rating = acc.get("rating")
            description = acc.get("description", "")

            result += f"{i}. {acc_name}\n"
            result += f"   Type: {acc_type}\n"
            result += f"   Price: {price} {currency}/night\n"
            if rating:
                result += f"   Rating: {rating}/5.0\n"
            if description:
                result += f"   Description: {description}\n"
            result += "\n"

        return result.strip()
    except Exception as e:
        logger.error(
            "find_accommodation error - location: %s, accommodation_type: %s, error: %s",
            location,
            accommodation_type,
            str(e),
            exc_info=True,
        )
        raise
