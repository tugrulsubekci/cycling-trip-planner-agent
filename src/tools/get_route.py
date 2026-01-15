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


class Waypoint(BaseModel):
    """Waypoint along a route."""

    name: str = Field(description="Name of the waypoint location")
    km: float = Field(description="Distance in kilometers from start to this waypoint")


class GetRouteOutput(BaseModel):
    """Output schema for get_route tool."""

    start_point: str = Field(description="Starting location")
    end_point: str = Field(description="Destination location")
    distance_km: float = Field(description="Total distance in kilometers")
    estimated_days: int = Field(description="Estimated number of days based on daily average")
    difficulty: str = Field(description="Difficulty level of the route")
    waypoints: list[Waypoint] = Field(description="List of waypoints along the route")
    description: str | None = Field(default=None, description="Route description")


@tool(args_schema=GetRouteInput)
def get_route(start_point: str, end_point: str, daily_average_km: float) -> dict:  # type: ignore[return-value]
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
        waypoints_data = route.get("waypoints", [])
        difficulty = route.get("difficulty", "unknown")
        description = route.get("description", "")

        # Calculate estimated days (rounded up)
        estimated_days = math.ceil(distance_km / daily_average_km)

        # Build waypoints list
        waypoints = []
        for waypoint in waypoints_data:
            if isinstance(waypoint, dict):
                waypoints.append(
                    Waypoint(
                        name=waypoint.get("name", "Unknown"),
                        km=waypoint.get("km", 0),
                    )
                )
            else:
                # Fallback for unexpected format
                waypoints.append(Waypoint(name=str(waypoint), km=0))

        # Build structured output
        start = route.get("start_point")
        end = route.get("end_point")
        output = GetRouteOutput(
            start_point=start or start_point,
            end_point=end or end_point,
            distance_km=distance_km,
            estimated_days=estimated_days,
            difficulty=difficulty,
            waypoints=waypoints,
            description=description if description else None,
        )

        # Return structured data as dict
        return output.model_dump()
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
