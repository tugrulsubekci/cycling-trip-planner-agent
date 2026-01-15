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


class AccommodationItem(BaseModel):
    """Individual accommodation item."""

    name: str = Field(description="Name of the accommodation")
    type: str = Field(description="Type of accommodation (camping, hostel, hotel)")
    price_per_night: float = Field(description="Price per night")
    currency: str = Field(description="Currency code (EUR, USD, etc.)")
    rating: float | None = Field(default=None, description="Rating out of 5.0")
    description: str | None = Field(default=None, description="Description of the accommodation")


class FindAccommodationOutput(BaseModel):
    """Output schema for find_accommodation tool."""

    location: str = Field(description="Location searched")
    filter_type: str = Field(description="Filter type applied (all, camping, hostels, hotels)")
    count: int = Field(description="Number of accommodations found")
    accommodations: list[AccommodationItem] = Field(description="List of accommodation options")


@tool(args_schema=FindAccommodationInput)
def find_accommodation(location: str, accommodation_type: str = "all") -> dict:
    """Find places to stay near a location (camping, hostels, hotels)."""
    logger.info(
        "find_accommodation called - location: %s, accommodation_type: %s",
        location,
        accommodation_type,
    )

    try:
        # Find accommodations using fuzzy matching
        accommodations_data = find_accommodations(location, accommodation_type)

        if not accommodations_data:
            type_info = f" (type: {accommodation_type})" if accommodation_type != "all" else ""
            return (
                f"No accommodations found near {location}{type_info}.\n"
                "Please check the location name and try again."
            )

        # Build structured output
        accommodation_items = [
            AccommodationItem(
                name=acc.get("name", "Unknown"),
                type=acc.get("type", "unknown"),
                price_per_night=acc.get("price_per_night", 0),
                currency=acc.get("currency", "EUR"),
                rating=acc.get("rating"),
                description=acc.get("description"),
            )
            for acc in accommodations_data
        ]

        type_display = (
            accommodation_type.capitalize() if accommodation_type != "all" else "All types"
        )
        output = FindAccommodationOutput(
            location=location,
            filter_type=type_display,
            count=len(accommodation_items),
            accommodations=accommodation_items,
        )

        # Return structured data as dict
        return output.model_dump()
    except Exception as e:
        logger.error(
            "find_accommodation error - location: %s, accommodation_type: %s, error: %s",
            location,
            accommodation_type,
            str(e),
            exc_info=True,
        )
        raise
