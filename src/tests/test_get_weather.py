"""Tests for get_weather tool."""

from unittest.mock import patch

import pytest

from src.tools.get_weather import get_weather


class TestGetWeather:
    """Tests for get_weather tool."""

    @patch("src.tools.get_weather.find_weather")
    def test_get_weather_success(self, mock_find_weather, mock_weather_data):
        """Test successful weather retrieval."""
        mock_find_weather.return_value = mock_weather_data

        result = get_weather.func("Paris", "July")

        assert isinstance(result, dict)
        assert result["location"] == "Paris"
        assert result["month"] == "July"
        assert result["avg_temperature_c"] == 19.0
        assert result["min_temperature_c"] == 15.0
        assert result["max_temperature_c"] == 24.0
        assert result["precipitation_mm"] == 58.0
        assert result["rainy_days"] == 8

    @patch("src.tools.get_weather.find_weather")
    def test_get_weather_not_found(self, mock_find_weather):
        """Test when weather data is not found."""
        mock_find_weather.return_value = None

        result = get_weather.func("Unknown", "January")

        assert isinstance(result, str)
        assert "No weather data found" in result

    @patch("src.tools.get_weather.find_weather")
    def test_get_weather_month_variations(self, mock_find_weather, mock_weather_data):
        """Test weather retrieval with different month formats."""
        mock_find_weather.return_value = mock_weather_data

        # These should all work (normalization happens in find_weather)
        get_weather.func("Paris", "1")
        get_weather.func("Paris", "January")
        get_weather.func("Paris", "jan")

        # The actual normalization is in mock_data.find_weather
        # Here we just verify the function is called
        assert mock_find_weather.call_count == 3
