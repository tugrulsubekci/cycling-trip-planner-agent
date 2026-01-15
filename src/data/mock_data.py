"""Mock data loader and route finder for Cycling Trip Planner."""

import json
import logging
from pathlib import Path
from typing import Any

from rapidfuzz import fuzz

logger: logging.Logger = logging.getLogger(__name__)

# Path to the mock routes JSON file
MOCK_ROUTES_PATH = Path(__file__).parent / "mock_routes.json"

# Path to the mock accommodations JSON file
MOCK_ACCOMMODATIONS_PATH = Path(__file__).parent / "mock_accommodations.json"

# Minimum similarity threshold for fuzzy matching (70%)
SIMILARITY_THRESHOLD = 70


def normalize_location(location: str) -> str:
    """Normalize location name for comparison (lowercase only)."""
    return location.lower().strip()


def load_routes() -> list[dict[str, Any]]:
    """Load routes from the mock_routes.json file."""
    try:
        with open(MOCK_ROUTES_PATH, encoding="utf-8") as f:
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


def load_accommodations() -> list[dict[str, Any]]:
    """Load accommodations from the mock_accommodations.json file."""
    try:
        with open(MOCK_ACCOMMODATIONS_PATH, encoding="utf-8") as f:
            data = json.load(f)
            accommodations = data.get("accommodations", [])
            logger.info("Loaded %d accommodations from mock data", len(accommodations))
            return accommodations
    except FileNotFoundError:
        logger.error("Mock accommodations file not found: %s", MOCK_ACCOMMODATIONS_PATH)
        return []
    except json.JSONDecodeError as e:
        logger.error("Error parsing mock accommodations JSON: %s", str(e))
        return []
    except Exception as e:
        logger.error("Error loading mock accommodations: %s", str(e))
        return []


def find_accommodations(
    location: str,
    accommodation_type: str = "all",
    accommodations: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Find accommodations using fuzzy matching on location name."""
    if accommodations is None:
        accommodations = load_accommodations()

    normalized_location = normalize_location(location)
    normalized_type = accommodation_type.lower().strip()

    # Normalize accommodation type for filtering
    type_mapping = {
        "camping": "camping",
        "camp": "camping",
        "hostel": "hostel",
        "hostels": "hostel",
        "hotel": "hotel",
        "hotels": "hotel",
        "all": "all",
    }
    filter_type = type_mapping.get(normalized_type, "all")

    matching_accommodations: list[dict[str, Any]] = []
    location_similarities: dict[str, float] = {}

    for accommodation in accommodations:
        accommodation_location = normalize_location(accommodation.get("location", ""))
        accommodation_type_value = accommodation.get("type", "").lower()

        # Calculate similarity score for location
        location_similarity = fuzz.ratio(normalized_location, accommodation_location)

        # Check if location matches and type matches (if filter is specified)
        if location_similarity >= SIMILARITY_THRESHOLD:
            # Filter by type if specified
            if filter_type == "all" or accommodation_type_value == filter_type:
                # Add accommodation with its similarity score for sorting
                matching_accommodations.append(accommodation)
                # Store similarity score for this location (use max if multiple)
                location_key = accommodation_location
                if (
                    location_key not in location_similarities
                    or location_similarity > location_similarities[location_key]
                ):
                    location_similarities[location_key] = location_similarity

    # Sort by location similarity (descending) and then by price (ascending)
    matching_accommodations.sort(
        key=lambda acc: (
            -location_similarities.get(
                normalize_location(acc.get("location", "")), 0
            ),
            acc.get("price_per_night", float("inf")),
        )
    )

    if matching_accommodations:
        logger.info(
            "Found %d accommodations matching - location: %s, type: %s",
            len(matching_accommodations),
            location,
            accommodation_type,
        )
    else:
        logger.warning(
            "No accommodations found matching - location: %s, type: %s",
            location,
            accommodation_type,
        )

    return matching_accommodations
