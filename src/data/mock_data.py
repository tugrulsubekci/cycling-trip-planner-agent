"""Mock data loader and route finder for Cycling Trip Planner."""

import json
import logging
from pathlib import Path
from typing import Any

from rapidfuzz import fuzz

logger: logging.Logger = logging.getLogger(__name__)

# Path to the mock routes JSON file
MOCK_ROUTES_PATH = Path(__file__).parent / "mock_routes.json"

# Minimum similarity threshold for fuzzy matching (70%)
SIMILARITY_THRESHOLD = 70


def normalize_location(location: str) -> str:
    """Normalize location name for comparison (lowercase only)."""
    return location.lower().strip()


def load_routes() -> list[dict[str, Any]]:
    """Load routes from the mock_routes.json file."""
    try:
        with open(MOCK_ROUTES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            routes = data.get("routes", [])
            logger.info("Loaded %d routes from mock data", len(routes))
            return routes
    except FileNotFoundError:
        logger.error("Mock routes file not found: %s", MOCK_ROUTES_PATH)
        return []
    except json.JSONDecodeError as e:
        logger.error("Error parsing mock routes JSON: %s", str(e))
        return []
    except Exception as e:
        logger.error("Error loading mock routes: %s", str(e))
        return []


def find_route_fuzzy(
    start_point: str, end_point: str, routes: list[dict[str, Any]]
) -> dict[str, Any] | None:
    """Find a route using fuzzy matching on start and end points."""
    normalized_start = normalize_location(start_point)
    normalized_end = normalize_location(end_point)

    best_match: dict[str, Any] | None = None
    best_score = 0

    for route in routes:
        route_start = normalize_location(route.get("start_point", ""))
        route_end = normalize_location(route.get("end_point", ""))

        # Calculate similarity scores for both start and end points
        start_similarity = fuzz.ratio(normalized_start, route_start)
        end_similarity = fuzz.ratio(normalized_end, route_end)

        # Average similarity score
        avg_similarity = (start_similarity + end_similarity) / 2

        # Both start and end must have reasonable similarity
        if (
            start_similarity >= SIMILARITY_THRESHOLD
            and end_similarity >= SIMILARITY_THRESHOLD
            and avg_similarity > best_score
        ):
            best_score = avg_similarity
            best_match = route

    if best_match:
        logger.info(
            "Found route match - start: %s, end: %s, similarity: %.1f%%",
            start_point,
            end_point,
            best_score,
        )
    else:
        logger.warning(
            "No route found matching - start: %s, end: %s",
            start_point,
            end_point,
        )

    return best_match
