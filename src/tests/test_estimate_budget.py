"""Tests for estimate_budget tool."""

from unittest.mock import patch

import pytest

from src.tools.estimate_budget import (
    convert_eur_to_usd,
    convert_to_eur,
    estimate_budget,
)


class TestEstimateBudget:
    """Tests for estimate_budget tool."""

    @patch("src.tools.estimate_budget.find_visa_requirements")
    @patch("src.tools.estimate_budget.find_accommodations")
    @patch("src.tools.estimate_budget.find_route_fuzzy")
    @patch("src.tools.estimate_budget.load_routes")
    def test_estimate_budget_with_daily_average_km(
        self, mock_load_routes, mock_find_route, mock_find_accommodations, mock_find_visa
    ):
        """Test budget estimation with daily_average_km."""
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
        mock_find_accommodations.return_value = [
            {
                "name": "Test Hotel",
                "type": "hotel",
                "location": "Calais",
                "price_per_night": 80.0,
                "currency": "EUR",
            }
        ]
        mock_find_visa.return_value = None

        result = estimate_budget.func("Paris", "London", daily_average_km=50.0)

        assert isinstance(result, dict)
        assert result["start_point"] == "Paris"
        assert result["end_point"] == "London"
        assert result["route_distance_km"] == 100.0
        assert result["estimated_days"] == 2  # ceil(100.0 / 50.0)
        assert "accommodation" in result
        assert "food" in result
        assert "visa" in result
        assert "other_expenses" in result
        assert "total_eur" in result
        assert "total_usd" in result

    @patch("src.tools.estimate_budget.find_visa_requirements")
    @patch("src.tools.estimate_budget.find_accommodations")
    @patch("src.tools.estimate_budget.find_route_fuzzy")
    @patch("src.tools.estimate_budget.load_routes")
    def test_estimate_budget_with_duration_days(
        self, mock_load_routes, mock_find_route, mock_find_accommodations, mock_find_visa
    ):
        """Test budget estimation with duration_days."""
        mock_load_routes.return_value = []
        mock_find_route.return_value = {
            "start_point": "Paris",
            "end_point": "London",
            "distance_km": 100.0,
            "waypoints": [],
        }
        mock_find_accommodations.return_value = []
        mock_find_visa.return_value = None

        result = estimate_budget.func("Paris", "London", duration_days=5)

        assert result["estimated_days"] == 5

    @patch("src.tools.estimate_budget.find_visa_requirements")
    @patch("src.tools.estimate_budget.find_accommodations")
    @patch("src.tools.estimate_budget.find_route_fuzzy")
    @patch("src.tools.estimate_budget.load_routes")
    def test_estimate_budget_route_not_found(
        self, mock_load_routes, mock_find_route, mock_find_accommodations, mock_find_visa
    ):
        """Test budget estimation when route is not found."""
        mock_load_routes.return_value = []
        mock_find_route.return_value = None
        mock_find_accommodations.return_value = []
        mock_find_visa.return_value = None

        result = estimate_budget.func("Unknown", "Unknown", duration_days=5)

        assert isinstance(result, str)
        assert "No route found" in result

    @patch("src.tools.estimate_budget.find_visa_requirements")
    @patch("src.tools.estimate_budget.find_accommodations")
    @patch("src.tools.estimate_budget.find_route_fuzzy")
    @patch("src.tools.estimate_budget.load_routes")
    def test_estimate_budget_no_duration_or_daily_km(
        self, mock_load_routes, mock_find_route, mock_find_accommodations, mock_find_visa
    ):
        """Test budget estimation without duration or daily_average_km."""
        mock_load_routes.return_value = []
        mock_find_route.return_value = {
            "start_point": "Paris",
            "end_point": "London",
            "distance_km": 100.0,
            "waypoints": [],
        }
        mock_find_accommodations.return_value = []
        mock_find_visa.return_value = None

        result = estimate_budget.func("Paris", "London")

        assert isinstance(result, str)
        assert "duration_days or daily_average_km must be provided" in result

    @patch("src.tools.estimate_budget.find_visa_requirements")
    @patch("src.tools.estimate_budget.find_accommodations")
    @patch("src.tools.estimate_budget.find_route_fuzzy")
    @patch("src.tools.estimate_budget.load_routes")
    def test_estimate_budget_visa_cost(
        self, mock_load_routes, mock_find_route, mock_find_accommodations, mock_find_visa
    ):
        """Test visa cost calculation."""
        mock_load_routes.return_value = []
        mock_find_route.return_value = {
            "start_point": "Paris",
            "end_point": "London",
            "distance_km": 100.0,
            "waypoints": [],
        }
        mock_find_accommodations.return_value = []
        mock_find_visa.return_value = {
            "destination": "Turkey",
            "nationality": "US",
            "visa_required": True,
            "cost_usd": 50.0,
        }

        result = estimate_budget.func(
            "Paris", "London", duration_days=5, destination="Turkey", nationality="US"
        )

        assert result["visa"]["cost_usd"] == 50.0
        assert result["visa"]["cost_eur"] > 0

    @patch("src.tools.estimate_budget.find_visa_requirements")
    @patch("src.tools.estimate_budget.find_accommodations")
    @patch("src.tools.estimate_budget.find_route_fuzzy")
    @patch("src.tools.estimate_budget.load_routes")
    def test_estimate_budget_accommodation_preference(
        self,
        mock_load_routes,
        mock_find_route,
        mock_find_accommodations,
        mock_find_visa,
    ):
        """Test accommodation preference filtering."""
        mock_load_routes.return_value = []
        mock_find_route.return_value = {
            "start_point": "Paris",
            "end_point": "London",
            "distance_km": 100.0,
            "waypoints": [{"name": "Calais", "km": 100.0}],
        }
        mock_find_accommodations.return_value = [
            {
                "name": "Test Camping",
                "type": "camping",
                "location": "Calais",
                "price_per_night": 15.0,
                "currency": "EUR",
            },
            {
                "name": "Test Hotel",
                "type": "hotel",
                "location": "Calais",
                "price_per_night": 80.0,
                "currency": "EUR",
            },
        ]
        mock_find_visa.return_value = None

        result = estimate_budget.func(
            "Paris", "London", duration_days=2, accommodation_preference="camping"
        )

        assert len(result["accommodation"]["breakdown"]) > 0


class TestEstimateBudgetCurrencyConversion:
    """Tests for currency conversion functions in estimate_budget."""

    def test_convert_to_eur_eur(self):
        """Test EUR to EUR conversion."""
        assert convert_to_eur(100.0, "EUR") == 100.0

    def test_convert_to_eur_usd(self):
        """Test USD to EUR conversion."""
        # 1 EUR = 1.1 USD, so 110 USD = 100 EUR
        result = convert_to_eur(110.0, "USD")
        assert abs(result - 100.0) < 0.01

    def test_convert_to_eur_gbp(self):
        """Test GBP to EUR conversion."""
        # 1 EUR = 0.85 GBP, so 85 GBP = 100 EUR
        result = convert_to_eur(85.0, "GBP")
        assert abs(result - 100.0) < 0.01

    def test_convert_eur_to_usd(self):
        """Test EUR to USD conversion."""
        # 1 EUR = 1.1 USD, so 100 EUR = 110 USD
        result = convert_eur_to_usd(100.0)
        assert abs(result - 110.0) < 0.01

    def test_convert_to_eur_unknown_currency(self):
        """Test conversion with unknown currency (should return as-is)."""
        result = convert_to_eur(100.0, "XXX")
        assert result == 100.0
