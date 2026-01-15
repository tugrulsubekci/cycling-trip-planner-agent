"""Pytest fixtures shared across test modules."""

from typing import Any

import pytest


@pytest.fixture
def mock_route_data() -> dict[str, Any]:
    """Mock route data for testing."""
    return {
        "start_point": "Paris",
        "end_point": "London",
        "distance_km": 344.0,
        "difficulty": "Moderate",
        "description": "A scenic route from Paris to London",
        "waypoints": [
            {"name": "Calais", "km": 288.0},
            {"name": "Dover", "km": 344.0},
        ],
    }


@pytest.fixture
def mock_accommodation_data() -> list[dict[str, Any]]:
    """Mock accommodation data for testing."""
    return [
        {
            "name": "Test Camping",
            "type": "camping",
            "location": "Paris",
            "price_per_night": 15.0,
            "currency": "EUR",
            "rating": 4.0,
            "description": "A nice camping site",
        },
        {
            "name": "Test Hostel",
            "type": "hostel",
            "location": "Paris",
            "price_per_night": 25.0,
            "currency": "EUR",
            "rating": 4.5,
        },
        {
            "name": "Test Hotel",
            "type": "hotel",
            "location": "Paris",
            "price_per_night": 80.0,
            "currency": "EUR",
            "rating": 4.8,
        },
    ]


@pytest.fixture
def mock_weather_data() -> dict[str, Any]:
    """Mock weather data for testing."""
    return {
        "location": "Paris",
        "month": "July",
        "avg_temperature_c": 19.0,
        "min_temperature_c": 15.0,
        "max_temperature_c": 24.0,
        "precipitation_mm": 58.0,
        "rainy_days": 8,
        "conditions": "Mild and pleasant",
        "cycling_suitability": "Good",
    }


@pytest.fixture
def mock_visa_data() -> dict[str, Any]:
    """Mock visa data for testing."""
    return {
        "destination": "Turkey",
        "nationality": "US",
        "visa_required": True,
        "visa_type": "e-Visa",
        "processing_time": "Immediate",
        "duration_of_stay": "90 days",
        "cost_usd": 50.0,
        "notes": "Can be obtained online",
    }


@pytest.fixture
def mock_elevation_data() -> dict[str, Any]:
    """Mock elevation data for testing."""
    return {
        "location": "Paris",
        "elevation_m": 35.0,
    }


@pytest.fixture
def mock_poi_data() -> list[dict[str, Any]]:
    """Mock points of interest data for testing."""
    return [
        {
            "name": "Eiffel Tower",
            "category": "historical",
            "location": "Paris",
            "description": "Iconic tower",
            "rating": 4.8,
            "distance_from_center_km": 0.0,
        },
        {
            "name": "Louvre Museum",
            "category": "cultural",
            "location": "Paris",
            "description": "World-famous museum",
            "rating": 4.9,
            "distance_from_center_km": 1.0,
        },
    ]
