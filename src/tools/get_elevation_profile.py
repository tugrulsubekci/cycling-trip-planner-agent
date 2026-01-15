"""Tool for getting elevation profile and terrain difficulty."""

import logging

from langchain.tools import tool
from pydantic import BaseModel, Field

from src.data.mock_data import find_elevation, find_route_fuzzy, load_routes

logger: logging.Logger = logging.getLogger(__name__)


class GetElevationProfileInput(BaseModel):
    """Input schema for get_elevation_profile tool."""

    location: str | None = Field(
        default=None,
        description="Single location to get elevation for (use this OR start_point + end_point)",
    )
    start_point: str | None = Field(
        default=None,
        description="Starting location for route elevation profile (use with end_point)",
    )
    end_point: str | None = Field(
        default=None,
        description="Destination location for route elevation profile (use with start_point)",
    )


def calculate_difficulty_rating(elevation_gain_per_km: float) -> str:
    """Calculate difficulty rating based on elevation gain per kilometer."""
    if elevation_gain_per_km < 10:
        return "Easy"
    elif elevation_gain_per_km < 30:
        return "Moderate"
    elif elevation_gain_per_km < 50:
        return "Hard"
    else:
        return "Very Hard"


@tool(args_schema=GetElevationProfileInput)
def get_elevation_profile(
    location: str | None = None,
    start_point: str | None = None,
    end_point: str | None = None,
) -> str:
    """Get terrain difficulty including elevation gain and difficulty rating."""
    logger.info(
        "get_elevation_profile called - location: %s, start_point: %s, end_point: %s",
        location,
        start_point,
        end_point,
    )

    try:
        # If route is provided (start_point + end_point), calculate route elevation profile
        if start_point and end_point:
            # Load routes and find matching route
            routes = load_routes()
            route = find_route_fuzzy(start_point, end_point, routes)

            if not route:
                return (
                    f"No route found from {start_point} to {end_point}.\n"
                    "Please check the location names and try again."
                )

            # Get route information
            distance_km = route.get("distance_km", 0)
            waypoints = route.get("waypoints", [])

            if not waypoints or distance_km == 0:
                return (
                    f"Route from {start_point} to {end_point} found but "
                    "missing waypoints or distance data."
                )

            # Get elevations for all waypoints
            waypoint_elevations: list[dict[str, float]] = []
            missing_elevations: list[str] = []

            for waypoint in waypoints:
                if isinstance(waypoint, dict):
                    waypoint_name = waypoint.get("name", "")
                    elevation_data = find_elevation(waypoint_name)

                    if elevation_data:
                        elevation_m = elevation_data.get("elevation_m", 0)
                        waypoint_elevations.append(
                            {"name": waypoint_name, "elevation_m": elevation_m}
                        )
                    else:
                        missing_elevations.append(waypoint_name)

            if missing_elevations:
                missing_cities = ", ".join(missing_elevations)
                return (
                    f"Elevation data not found for the following cities: {missing_cities}.\n"
                    "Cannot calculate elevation profile."
                )

            if len(waypoint_elevations) < 2:
                return (
                    "Insufficient elevation data to calculate profile. "
                    "Need at least 2 waypoints."
                )

            # Calculate elevation metrics
            total_elevation_gain = 0.0
            total_elevation_loss = 0.0
            elevations = [wp["elevation_m"] for wp in waypoint_elevations]
            max_elevation = max(elevations)
            min_elevation = min(elevations)

            # Find max and min elevation waypoint names
            max_elevation_waypoint = next(
                wp["name"]
                for wp in waypoint_elevations
                if wp["elevation_m"] == max_elevation
            )
            min_elevation_waypoint = next(
                wp["name"]
                for wp in waypoint_elevations
                if wp["elevation_m"] == min_elevation
            )

            # Calculate elevation gain and loss between waypoints
            for i in range(len(waypoint_elevations) - 1):
                current_elevation = waypoint_elevations[i]["elevation_m"]
                next_elevation = waypoint_elevations[i + 1]["elevation_m"]
                elevation_change = next_elevation - current_elevation

                if elevation_change > 0:
                    total_elevation_gain += elevation_change
                else:
                    total_elevation_loss += abs(elevation_change)

            # Calculate elevation gain per kilometer
            elevation_gain_per_km = (total_elevation_gain / distance_km) if distance_km > 0 else 0.0
            difficulty_rating = calculate_difficulty_rating(elevation_gain_per_km)

            # Build elevation profile string
            profile_parts = []
            for wp in waypoint_elevations:
                profile_parts.append(f"{wp['name']} ({wp['elevation_m']:.0f} m)")
            profile_str = " → ".join(profile_parts)

            # Format result string
            result = (
                f"Elevation Profile for {start_point} to {end_point}:\n"
                f"- Distance: {distance_km} km\n"
                f"- Total Elevation Gain: {total_elevation_gain:.0f} m\n"
                f"- Total Elevation Loss: {total_elevation_loss:.0f} m\n"
                f"- Maximum Elevation: {max_elevation:.0f} m ({max_elevation_waypoint})\n"
                f"- Minimum Elevation: {min_elevation:.0f} m ({min_elevation_waypoint})\n"
                f"- Average Gradient: {elevation_gain_per_km:.1f} m/km\n"
                f"- Difficulty Rating: {difficulty_rating}\n"
                f"- Elevation Profile:\n  {profile_str}"
            )

            return result

        # If single location is provided, return city elevation
        elif location:
            elevation_data = find_elevation(location)

            if not elevation_data:
                return (
                    f"Elevation data not found for {location}.\n"
                    "Please check the location name and try again."
                )

            elevation_m = elevation_data.get("elevation_m", 0)

            result = (
                f"Elevation Profile for {location}:\n"
                f"- Base Elevation: {elevation_m} m above sea level"
            )

            return result

        else:
            return (
                "Please provide either:\n"
                "- A single location name, OR\n"
                "- Both start_point and end_point for a route elevation profile."
            )

    except Exception as e:
        logger.error(
            "get_elevation_profile error - location: %s, start_point: %s, end_point: %s, error: %s",
            location,
            start_point,
            end_point,
            str(e),
            exc_info=True,
        )
        raise
