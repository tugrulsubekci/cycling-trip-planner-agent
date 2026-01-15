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


class POIItem(BaseModel):
    """Individual point of interest item."""

    name: str = Field(description="Name of the point of interest")
    category: str = Field(description="Category of the point of interest")
    description: str | None = Field(default=None, description="Description of the POI")
    rating: float | None = Field(default=None, description="Rating out of 5.0")
    distance_from_center_km: float | None = Field(
        default=None, description="Distance from city center in kilometers"
    )


class GetPointsOfInterestOutput(BaseModel):
    """Output schema for get_points_of_interest tool."""

    location: str = Field(description="Location searched")
    filter_category: str | None = Field(
        default=None, description="Category filter applied (if any)"
    )
    count: int = Field(description="Number of points of interest found")
    points: list[POIItem] = Field(description="List of points of interest")


@tool(args_schema=GetPointsOfInterestInput)
def get_points_of_interest(location: str, category: str | None = None) -> dict:
    """Find points of interest near a location or along a route."""
    logger.info(
        "get_points_of_interest called - location: %s, category: %s",
        location,
        category,
    )

    try:
        # Find points of interest using fuzzy matching
        pois_data = find_points_of_interest(location, category)

        if not pois_data:
            category_info = f" (category: {category})" if category else ""
            return (
                f"No points of interest found near {location}{category_info}.\n"
                "Please check the location name and try again."
            )

        # Build structured output
        poi_items = [
            POIItem(
                name=poi.get("name", "Unknown"),
                category=poi.get("category", "unknown"),
                description=poi.get("description"),
                rating=poi.get("rating"),
                distance_from_center_km=poi.get("distance_from_center_km"),
            )
            for poi in pois_data
        ]

        output = GetPointsOfInterestOutput(
            location=location,
            filter_category=category,
            count=len(poi_items),
            points=poi_items,
        )

        # Return structured data as dict
        return output.model_dump()
    except Exception as e:
        logger.error(
            "get_points_of_interest error - location: %s, category: %s, error: %s",
            location,
            category,
            str(e),
            exc_info=True,
        )
        raise
