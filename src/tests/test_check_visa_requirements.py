"""Tests for check_visa_requirements tool."""

from unittest.mock import patch

import pytest

from src.tools.check_visa_requirements import check_visa_requirements


class TestCheckVisaRequirements:
    """Tests for check_visa_requirements tool."""

    @patch("src.tools.check_visa_requirements.find_visa_requirements")
    def test_check_visa_requirements_success(self, mock_find_visa, mock_visa_data):
        """Test successful visa requirements check."""
        mock_find_visa.return_value = mock_visa_data

        result = check_visa_requirements.func("Turkey", "US")

        assert isinstance(result, dict)
        assert result["destination"] == "Turkey"
        assert result["nationality"] == "US"
        assert result["visa_required"] is True
        assert result["visa_type"] == "e-Visa"
        assert result["cost_usd"] == 50.0

    @patch("src.tools.check_visa_requirements.find_visa_requirements")
    def test_check_visa_requirements_not_required(self, mock_find_visa):
        """Test visa not required scenario."""
        mock_find_visa.return_value = {
            "destination": "France",
            "nationality": "US",
            "visa_required": False,
            "visa_type": "Not required",
            "processing_time": "N/A",
            "duration_of_stay": "90 days",
            "cost_usd": None,
        }

        result = check_visa_requirements.func("France", "US")

        assert result["visa_required"] is False
        assert result["cost_usd"] is None

    @patch("src.tools.check_visa_requirements.find_visa_requirements")
    def test_check_visa_requirements_not_found(self, mock_find_visa):
        """Test when visa data is not found."""
        mock_find_visa.return_value = None

        result = check_visa_requirements.func("Unknown", "Unknown")

        assert isinstance(result, str)
        assert "No visa requirements data found" in result
