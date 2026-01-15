"""Tool definitions and exports for Cycling Trip Planner."""

from src.tools.calculate_accommodation_schedule import calculate_accommodation_schedule
from src.tools.check_visa_requirements import check_visa_requirements
from src.tools.estimate_budget import estimate_budget
from src.tools.find_accommodation import find_accommodation
from src.tools.get_elevation_profile import get_elevation_profile
from src.tools.get_points_of_interest import get_points_of_interest
from src.tools.get_route import get_route
from src.tools.get_weather import get_weather

__all__ = [
    "calculate_accommodation_schedule",
    "check_visa_requirements",
    "estimate_budget",
    "find_accommodation",
    "get_elevation_profile",
    "get_points_of_interest",
    "get_route",
    "get_weather",
    "REQUIRED_TOOLS",
    "OPTIONAL_TOOLS",
    "ALL_TOOLS",
]

ALL_TOOLS = [
    get_route,
    find_accommodation,
    calculate_accommodation_schedule,
    get_weather,
    get_elevation_profile,
    get_points_of_interest,
    check_visa_requirements,
    estimate_budget,
]
