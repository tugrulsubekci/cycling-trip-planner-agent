"""Tests for get_elevation_profile tool."""

from unittest.mock import patch

import pytest

from src.tools.get_elevation_profile import (
    calculate_difficulty_rating,
    get_elevation_profile,
)


class TestGetElevationProfile:
    """Tests for get_elevation_profile tool."""

    @patch("src.tools.get_elevation_profile.find_elevation")
    def test_get_elevation_profile_single_location(self, mock_find_elevation, mock_elevation_data):
        """Test elevation retrieval for single location."""
        mock_find_elevation.return_value = mock_elevation_data

        result = get_elevation_profile.func(location="Paris")

        assert isinstance(result, dict)
        assert result["location"] == "Paris"
        assert result["elevation_m"] == 35.0

    @patch("src.tools.get_elevation_profile.find_elevation")
    def test_get_elevation_profile_single_location_not_found(self, mock_find_elevation):
        """Test single location elevation not found."""
        mock_find_elevation.return_value = None

        result = get_elevation_profile.func(location="Unknown")

        assert isinstance(result, str)
        assert "Elevation data not found" in result

    @patch("src.tools.get_elevation_profile.find_elevation")
    @patch("src.tools.get_elevation_profile.find_route_fuzzy")
    @patch("src.tools.get_elevation_profile.load_routes")
    def test_get_elevation_profile_route(
        self, mock_load_routes, mock_find_route, mock_find_elevation
    ):
        """Test route elevation profile."""
        mock_load_routes.return_value = []
        mock_find_route.return_value = {
            "start_point": "Paris",
            "end_point": "London",
            "distance_km": 100.0,
            "waypoints": [
                {"name": "Calais", "km": 50.0},
                {"name": "Dover", "km": 100.0},
            ],
        }
        mock_find_elevation.side_effect = [
            {"location": "Calais", "elevation_m": 10.0},
            {"location": "Dover", "elevation_m": 50.0},
        ]

        result = get_elevation_profile.func(start_point="Paris", end_point="London")

        assert isinstance(result, dict)
        assert result["start_point"] == "Paris"
        assert result["end_point"] == "London"
        assert result["distance_km"] == 100.0
        assert "total_elevation_gain" in result
        assert "total_elevation_loss" in result
        assert "max_elevation" in result
        assert "min_elevation" in result
        assert "difficulty_rating" in result

    @patch("src.tools.get_elevation_profile.find_elevation")
    @patch("src.tools.get_elevation_profile.find_route_fuzzy")
    @patch("src.tools.get_elevation_profile.load_routes")
    def test_get_elevation_profile_route_not_found(
        self, mock_load_routes, mock_find_route, mock_find_elevation
    ):
        """Test route elevation profile when route not found."""
        mock_load_routes.return_value = []
        mock_find_route.return_value = None
        mock_find_elevation.return_value = None

        result = get_elevation_profile.func(start_point="Unknown", end_point="Unknown")

        assert isinstance(result, str)
        assert "No route found" in result

    @patch("src.tools.get_elevation_profile.find_elevation")
    @patch("src.tools.get_elevation_profile.find_route_fuzzy")
    @patch("src.tools.get_elevation_profile.load_routes")
    def test_get_elevation_profile_missing_elevation_data(
        self, mock_load_routes, mock_find_route, mock_find_elevation
    ):
        """Test route elevation profile with missing elevation data."""
        mock_load_routes.return_value = []
        mock_find_route.return_value = {
            "start_point": "Paris",
            "end_point": "London",
            "distance_km": 100.0,
            "waypoints": [{"name": "Calais", "km": 50.0}],
        }
        mock_find_elevation.return_value = None

        result = get_elevation_profile.func(start_point="Paris", end_point="London")

        assert isinstance(result, str)
        assert "Elevation data not found" in result

    def test_get_elevation_profile_no_parameters(self):
        """Test elevation profile with no parameters."""
        result = get_elevation_profile.func()

        assert isinstance(result, str)
        assert "Please provide either" in result

    @patch("src.tools.get_elevation_profile.find_elevation")
    @patch("src.tools.get_elevation_profile.find_route_fuzzy")
    @patch("src.tools.get_elevation_profile.load_routes")
    def test_get_elevation_profile_difficulty_rating(
        self, mock_load_routes, mock_find_route, mock_find_elevation
    ):
        """Test difficulty rating calculation."""
        mock_load_routes.return_value = []
        mock_find_route.return_value = {
            "start_point": "Paris",
            "end_point": "London",
            "distance_km": 100.0,
            "waypoints": [
                {"name": "Start", "km": 0.0},
                {"name": "End", "km": 100.0},
            ],
        }

        # Test Easy (< 10 m/km)
        mock_find_elevation.side_effect = [
            {"location": "Start", "elevation_m": 0.0},
            {"location": "End", "elevation_m": 500.0},  # 500m gain / 100km = 5 m/km (Easy)
        ]
        result = get_elevation_profile.func(start_point="Paris", end_point="London")
        assert result["difficulty_rating"] == "Easy"

        # Test Moderate (10-30 m/km)
        mock_find_elevation.side_effect = [
            {"location": "Start", "elevation_m": 0.0},
            {"location": "End", "elevation_m": 2000.0},  # 2000m gain / 100km = 20 m/km (Moderate)
        ]
        result = get_elevation_profile.func(start_point="Paris", end_point="London")
        assert result["difficulty_rating"] == "Moderate"

        # Test Hard (30-50 m/km)
        mock_find_elevation.side_effect = [
            {"location": "Start", "elevation_m": 0.0},
            {"location": "End", "elevation_m": 4000.0},  # 4000m gain / 100km = 40 m/km (Hard)
        ]
        result = get_elevation_profile.func(start_point="Paris", end_point="London")
        assert result["difficulty_rating"] == "Hard"

        # Test Very Hard (>= 50 m/km)
        mock_find_elevation.side_effect = [
            {"location": "Start", "elevation_m": 0.0},
            {"location": "End", "elevation_m": 6000.0},  # 6000m gain / 100km = 60 m/km (Very Hard)
        ]
        result = get_elevation_profile.func(start_point="Paris", end_point="London")
        assert result["difficulty_rating"] == "Very Hard"


class TestCalculateDifficultyRating:
    """Tests for calculate_difficulty_rating helper function."""

    def test_calculate_difficulty_rating_easy(self):
        """Test Easy difficulty rating."""
        assert calculate_difficulty_rating(5.0) == "Easy"
        assert calculate_difficulty_rating(9.9) == "Easy"

    def test_calculate_difficulty_rating_moderate(self):
        """Test Moderate difficulty rating."""
        assert calculate_difficulty_rating(10.0) == "Moderate"
        assert calculate_difficulty_rating(29.9) == "Moderate"

    def test_calculate_difficulty_rating_hard(self):
        """Test Hard difficulty rating."""
        assert calculate_difficulty_rating(30.0) == "Hard"
        assert calculate_difficulty_rating(49.9) == "Hard"

    def test_calculate_difficulty_rating_very_hard(self):
        """Test Very Hard difficulty rating."""
        assert calculate_difficulty_rating(50.0) == "Very Hard"
        assert calculate_difficulty_rating(100.0) == "Very Hard"
