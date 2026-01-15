"""Tool for getting cycling route between two points."""

import logging

from langchain.tools import tool
from pydantic import BaseModel, Field

logger: logging.Logger = logging.getLogger(__name__)


class GetRouteInput(BaseModel):
    """Input schema for get_route tool."""

    start_point: str = Field(description="Starting location (city, coordinates, or address)")
    end_point: str = Field(description="Destination location (city, coordinates, or address)")


@tool(args_schema=GetRouteInput)
def get_route(start_point: str, end_point: str) -> str:
    """Get cycling route between two points (distance, estimated days, waypoints)."""
    logger.info(
        "get_route called - start_point: %s, end_point: %s",
        start_point,
        end_point,
    )

    try:
        result = (
            f"Route from {start_point} to {end_point}:\n"
            "- Distance: [To be calculated]\n"
            "- Estimated days: [To be calculated]\n"
            "- Waypoints: [To be calculated]\n"
            "Note: This is a placeholder. Actual implementation pending."
        )
        return result
    except Exception as e:
        logger.error(
            "get_route error - start_point: %s, end_point: %s, error: %s",
            start_point,
            end_point,
            str(e),
            exc_info=True,
        )
        raise
