"""Tool for getting points of interest near a location or route."""

import logging

from langchain.tools import tool
from pydantic import BaseModel, Field

from src.data.mock_data import find_points_of_interest

logger: logging.Logger = logging.getLogger(__name__)


class GetPointsOfInterestInput(BaseModel):
    """Input schema for get_points_of_interest tool."""

    location: str = Field(description="Location or route to search for points of interest")
    category: str | None = Field(
        default=None,
        description="Optional category filter (e.g., historical, natural, cultural)",
    )


@tool(args_schema=GetPointsOfInterestInput)
def get_points_of_interest(location: str, category: str | None = None) -> str:
    """Find points of interest near a location or along a route."""
    logger.info(
        "get_points_of_interest called - location: %s, category: %s",
        location,
        category,
    )

    try:
        # Find points of interest using fuzzy matching
        pois = find_points_of_interest(location, category)

        if not pois:
            category_info = f" (category: {category})" if category else ""
            return (
                f"No points of interest found near {location}{category_info}.\n"
                "Please check the location name and try again."
            )

        # Build result string
        category_display = (
            category.capitalize() if category else "All categories"
        )
        result = f"Points of interest near {location}:\n"
        result += f"- Filter: {category_display}\n"
        result += f"- Found: {len(pois)} point(s) of interest\n\n"

        # Format each POI
        for i, poi in enumerate(pois, 1):
            poi_name = poi.get("name", "Unknown")
            poi_category = poi.get("category", "unknown").capitalize()
            description = poi.get("description", "")
            rating = poi.get("rating")
            distance = poi.get("distance_from_center_km")

            result += f"{i}. {poi_name}\n"
            result += f"   Category: {poi_category}\n"
            if description:
                result += f"   Description: {description}\n"
            if rating:
                result += f"   Rating: {rating}/5.0\n"
            if distance is not None:
                result += f"   Distance from center: {distance} km\n"
            result += "\n"

        return result.strip()
    except Exception as e:
        logger.error(
            "get_points_of_interest error - location: %s, category: %s, error: %s",
            location,
            category,
            str(e),
            exc_info=True,
        )
        raise
