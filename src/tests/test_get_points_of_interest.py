"""Tests for get_points_of_interest tool."""

from unittest.mock import patch

import pytest

from src.tools.get_points_of_interest import get_points_of_interest


class TestGetPointsOfInterest:
    """Tests for get_points_of_interest tool."""

    @patch("src.tools.get_points_of_interest.find_points_of_interest")
    def test_get_points_of_interest_success(self, mock_find_poi, mock_poi_data):
        """Test successful POI retrieval."""
        mock_find_poi.return_value = mock_poi_data

        result = get_points_of_interest.func("Paris")

        assert isinstance(result, dict)
        assert result["location"] == "Paris"
        assert result["count"] == 2
        assert len(result["points"]) == 2
        assert result["points"][0]["name"] == "Eiffel Tower"

    @patch("src.tools.get_points_of_interest.find_points_of_interest")
    def test_get_points_of_interest_with_category(self, mock_find_poi):
        """Test POI retrieval with category filter."""
        mock_find_poi.return_value = [
            {
                "name": "Eiffel Tower",
                "category": "historical",
                "location": "Paris",
                "description": "Iconic tower",
                "rating": 4.8,
            }
        ]

        result = get_points_of_interest.func("Paris", category="historical")

        assert result["filter_category"] == "historical"
        assert result["count"] == 1
        assert result["points"][0]["category"] == "historical"

    @patch("src.tools.get_points_of_interest.find_points_of_interest")
    def test_get_points_of_interest_not_found(self, mock_find_poi):
        """Test when POI data is not found."""
        mock_find_poi.return_value = []

        result = get_points_of_interest.func("Unknown")

        assert isinstance(result, str)
        assert "No points of interest found" in result

    @patch("src.tools.get_points_of_interest.find_points_of_interest")
    def test_get_points_of_interest_with_rating(self, mock_find_poi, mock_poi_data):
        """Test POI with rating and distance."""
        mock_find_poi.return_value = mock_poi_data

        result = get_points_of_interest.func("Paris")

        assert result["points"][0]["rating"] == 4.8
        assert result["points"][0]["distance_from_center_km"] == 0.0
