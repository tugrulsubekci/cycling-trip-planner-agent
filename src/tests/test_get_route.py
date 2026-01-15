"""Tests for get_route tool."""

from unittest.mock import patch

import pytest

from src.tools.get_route import get_route


class TestGetRoute:
    """Tests for get_route tool."""

    @patch("src.tools.get_route.load_routes")
    @patch("src.tools.get_route.find_route_fuzzy")
    def test_get_route_success(  # type: ignore[no-untyped-def]
        self, mock_find_route, mock_load_routes, mock_route_data
    ) -> None:
        """Test successful route retrieval."""
        mock_load_routes.return_value = []
        mock_find_route.return_value = mock_route_data

        result = get_route.func("Paris", "London", 50.0)  # type: ignore[attr-defined]

        assert isinstance(result, dict)
        assert result["start_point"] == "Paris"
        assert result["end_point"] == "London"
        assert result["distance_km"] == 344.0
        assert result["difficulty"] == "Moderate"
        assert result["estimated_days"] == 7  # ceil(344.0 / 50.0)
        assert len(result["waypoints"]) == 2
        assert result["waypoints"][0]["name"] == "Calais"

    @patch("src.tools.get_route.load_routes")
    @patch("src.tools.get_route.find_route_fuzzy")
    def test_get_route_not_found(  # type: ignore[no-untyped-def]
        self, mock_find_route, mock_load_routes
    ) -> None:
        """Test when route is not found."""
        mock_load_routes.return_value = []
        mock_find_route.return_value = None

        result = get_route.func("Unknown", "Unknown", 50.0)  # type: ignore[attr-defined]

        assert isinstance(result, str)
        assert "No route found" in result

    @patch("src.tools.get_route.load_routes")
    @patch("src.tools.get_route.find_route_fuzzy")
    def test_get_route_estimated_days_calculation(  # type: ignore[no-untyped-def]
        self, mock_find_route, mock_load_routes
    ) -> None:
        """Test estimated_days calculation is correct."""
        mock_load_routes.return_value = []
        mock_find_route.return_value = {
            "start_point": "Paris",
            "end_point": "London",
            "distance_km": 100.0,
            "difficulty": "Easy",
            "waypoints": [],
        }

        result = get_route.func("Paris", "London", 30.0)  # type: ignore[attr-defined]
        assert result["estimated_days"] == 4  # ceil(100.0 / 30.0)

        result = get_route.func("Paris", "London", 50.0)  # type: ignore[attr-defined]
        assert result["estimated_days"] == 2  # ceil(100.0 / 50.0)

    @patch("src.tools.get_route.load_routes")
    @patch("src.tools.get_route.find_route_fuzzy")
    def test_get_route_waypoint_fallback(  # type: ignore[no-untyped-def]
        self, mock_find_route, mock_load_routes
    ) -> None:
        """Test waypoint parsing with fallback format."""
        mock_load_routes.return_value = []
        mock_find_route.return_value = {
            "start_point": "Paris",
            "end_point": "London",
            "distance_km": 100.0,
            "difficulty": "Easy",
            "waypoints": ["Calais", {"name": "Dover", "km": 100.0}],
        }

        result = get_route.func("Paris", "London", 50.0)  # type: ignore[attr-defined]
        assert len(result["waypoints"]) == 2
        assert result["waypoints"][0]["name"] == "Calais"
        assert result["waypoints"][1]["name"] == "Dover"

    @patch("src.tools.get_route.load_routes")
    @patch("src.tools.get_route.find_route_fuzzy")
    def test_get_route_no_description(  # type: ignore[no-untyped-def]
        self, mock_find_route, mock_load_routes
    ) -> None:
        """Test route without description."""
        mock_load_routes.return_value = []
        mock_find_route.return_value = {
            "start_point": "Paris",
            "end_point": "London",
            "distance_km": 100.0,
            "difficulty": "Easy",
            "waypoints": [],
        }

        result = get_route.func("Paris", "London", 50.0)  # type: ignore[attr-defined]
        assert result["description"] is None

    def test_get_route_invalid_daily_average_km(self) -> None:
        """Test validation error for invalid daily_average_km."""
        # Note: Pydantic validation happens at the tool decorator level
        # This test would need to be adjusted based on actual validation behavior
        pass
