"""Tool for getting elevation profile and terrain difficulty."""

import logging

from langchain.tools import tool
from pydantic import BaseModel, Field

logger: logging.Logger = logging.getLogger(__name__)


class GetElevationProfileInput(BaseModel):
    """Input schema for get_elevation_profile tool."""

    location: str = Field(description="Location or route to analyze")
    route_segment: str | None = Field(
        default=None,
        description="Optional specific route segment",
    )


@tool(args_schema=GetElevationProfileInput)
def get_elevation_profile(location: str, route_segment: str | None = None) -> str:
    """Get terrain difficulty including elevation gain and difficulty rating."""
    logger.info(
        "get_elevation_profile called - location: %s, route_segment: %s",
        location,
        route_segment,
    )

    try:
        segment_info = f" (segment: {route_segment})" if route_segment else ""
        result = (
            f"Elevation profile for {location}{segment_info}:\n"
            "- Elevation gain: [To be calculated]\n"
            "- Difficulty rating: [To be calculated]\n"
            "- Profile data: [To be retrieved]\n"
            "Note: This is a placeholder. Actual implementation pending."
        )
        return result
    except Exception as e:
        logger.error(
            "get_elevation_profile error - location: %s, route_segment: %s, error: %s",
            location,
            route_segment,
            str(e),
            exc_info=True,
        )
        raise
