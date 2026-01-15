"""Tool for getting points of interest near a location or route."""

import logging

from langchain.tools import tool
from pydantic import BaseModel, Field

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
        category_info = f" (category: {category})" if category else ""
        result = (
            f"Points of interest near {location}{category_info}:\n"
            "- Results: [To be searched]\n"
            "- Count: [To be calculated]\n"
            "Note: This is a placeholder. Actual implementation pending."
        )
        return result
    except Exception as e:
        logger.error(
            "get_points_of_interest error - location: %s, category: %s, error: %s",
            location,
            category,
            str(e),
            exc_info=True,
        )
        raise
