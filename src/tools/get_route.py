"""Tool for getting cycling route between two points."""

import logging
import math

from langchain.tools import tool
from pydantic import BaseModel, Field

from src.data.mock_data import find_route_fuzzy, load_routes

logger: logging.Logger = logging.getLogger(__name__)


class GetRouteInput(BaseModel):
    """Input schema for get_route tool."""

    start_point: str = Field(description="Starting location (city, coordinates, or address)")
    end_point: str = Field(description="Destination location (city, coordinates, or address)")
    daily_average_km: float = Field(
        description=(
            "Daily average cycling distance in kilometers "
            "(required for calculating estimated days)"
        ),
        gt=0,
    )


@tool(args_schema=GetRouteInput)
def get_route(start_point: str, end_point: str, daily_average_km: float) -> str:
    """Get cycling route between two points (distance, estimated days, waypoints)."""
    logger.info(
        "get_route called - start_point: %s, end_point: %s, daily_average_km: %.1f",
        start_point,
        end_point,
        daily_average_km,
    )

    try:
        # Load routes from mock data
        routes = load_routes()

        # Find matching route using fuzzy matching
        route = find_route_fuzzy(start_point, end_point, routes)

        if not route:
            return (
                f"No route found from {start_point} to {end_point}.\n"
                "Please check the location names and try again."
            )

        # Extract route information
        distance_km = route.get("distance_km", 0)
        waypoints = route.get("waypoints", [])
        difficulty = route.get("difficulty", "unknown")
        description = route.get("description", "")

        # Calculate estimated days (rounded up)
        estimated_days = math.ceil(distance_km / daily_average_km)

        # Format waypoints with km distances
        if waypoints:
            waypoint_parts = []
            for waypoint in waypoints:
                if isinstance(waypoint, dict):
                    name = waypoint.get("name", "Unknown")
                    km = waypoint.get("km", 0)
                    waypoint_parts.append(f"{name} ({km} km)")
                else:
                    # Fallback for unexpected format
                    waypoint_parts.append(str(waypoint))
            waypoints_str = " → ".join(waypoint_parts)
        else:
            waypoints_str = "No waypoints"

        # Capitalize difficulty for display
        difficulty_display = difficulty.capitalize() if difficulty != "unknown" else "Unknown"

        # Build result string
        start = route.get("start_point")
        end = route.get("end_point")
        result = (
            f"Route from {start} to {end}:\n"
            f"- Distance: {distance_km} km\n"
            f"- Estimated days: {estimated_days} days "
            f"(based on {daily_average_km:.1f} km/day average)\n"
            f"- Difficulty: {difficulty_display}\n"
            f"- Waypoints: {waypoints_str}"
        )

        if description:
            result += f"\n- Description: {description}"

        return result
    except Exception as e:
        logger.error(
            "get_route error - start_point: %s, end_point: %s, daily_average_km: %.1f, error: %s",
            start_point,
            end_point,
            daily_average_km,
            str(e),
            exc_info=True,
        )
        raise
