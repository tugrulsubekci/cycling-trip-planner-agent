"""Tests for find_accommodation tool."""

from unittest.mock import patch

from src.tools.find_accommodation import find_accommodation


class TestFindAccommodation:
    """Tests for find_accommodation tool."""

    @patch("src.tools.find_accommodation.find_accommodations")
    def test_find_accommodation_success(self, mock_find_accommodations, mock_accommodation_data):
        """Test successful accommodation search."""
        mock_find_accommodations.return_value = mock_accommodation_data

        result = find_accommodation.func("Paris", "all")

        assert isinstance(result, dict)
        assert result["location"] == "Paris"
        assert result["filter_type"] == "All types"
        assert result["count"] == 3
        assert len(result["accommodations"]) == 3

    @patch("src.tools.find_accommodation.find_accommodations")
    def test_find_accommodation_filter_camping(self, mock_find_accommodations):
        """Test filtering by camping type."""
        mock_find_accommodations.return_value = [
            {
                "name": "Test Camping",
                "type": "camping",
                "location": "Paris",
                "price_per_night": 15.0,
                "currency": "EUR",
            }
        ]

        result = find_accommodation.func("Paris", "camping")

        assert result["filter_type"] == "Camping"
        assert result["count"] == 1
        assert result["accommodations"][0]["type"] == "camping"

    @patch("src.tools.find_accommodation.find_accommodations")
    def test_find_accommodation_default_type(
        self, mock_find_accommodations, mock_accommodation_data
    ):
        """Test default accommodation_type parameter."""
        mock_find_accommodations.return_value = mock_accommodation_data

        result = find_accommodation.func("Paris")

        assert result["filter_type"] == "All types"

    @patch("src.tools.find_accommodation.find_accommodations")
    def test_find_accommodation_not_found(self, mock_find_accommodations):
        """Test when accommodations are not found."""
        mock_find_accommodations.return_value = []

        result = find_accommodation.func("Unknown", "all")

        assert isinstance(result, str)
        assert "No accommodations found" in result

    @patch("src.tools.find_accommodation.find_accommodations")
    def test_find_accommodation_with_rating(self, mock_find_accommodations):
        """Test accommodation with rating."""
        mock_find_accommodations.return_value = [
            {
                "name": "Test Hotel",
                "type": "hotel",
                "location": "Paris",
                "price_per_night": 80.0,
                "currency": "EUR",
                "rating": 4.8,
                "description": "Nice hotel",
            }
        ]

        result = find_accommodation.func("Paris", "hotel")

        assert result["accommodations"][0]["rating"] == 4.8
        assert result["accommodations"][0]["description"] == "Nice hotel"
