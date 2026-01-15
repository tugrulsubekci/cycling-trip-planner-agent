"""Tool for estimating budget for a cycling trip."""

import logging
import math
from collections import defaultdict

from langchain.tools import tool
from pydantic import BaseModel, Field

from src.data.mock_data import (
    find_accommodations,
    find_route_fuzzy,
    find_visa_requirements,
    load_routes,
)

logger: logging.Logger = logging.getLogger(__name__)

# Currency exchange rates (simplified, for budget estimation)
CURRENCY_RATES = {
    "EUR": 1.0,
    "USD": 1.1,  # 1 EUR = 1.1 USD
    "GBP": 0.85,  # 1 EUR = 0.85 GBP
    "DKK": 7.45,  # 1 EUR = 7.45 DKK
    "CZK": 25.0,  # 1 EUR = 25.0 CZK
}

# Daily cost estimates (in EUR)
DAILY_FOOD_COST = 40.0  # Average daily food cost
BIKE_MAINTENANCE_PER_KM = 0.1  # Maintenance cost per km
MISCELLANEOUS_PER_DAY = 15.0  # Miscellaneous expenses per day


class EstimateBudgetInput(BaseModel):
    """Input schema for estimate_budget tool."""

    start_point: str = Field(description="Starting location (city, coordinates, or address)")
    end_point: str = Field(description="Destination location (city, coordinates, or address)")
    duration_days: int | None = Field(
        default=None,
        description="Estimated duration in days (if not provided, will be calculated)",
    )
    daily_average_km: float | None = Field(
        default=None,
        description=(
            "Daily average cycling distance in kilometers "
            "(required if duration_days not provided)"
        ),
    )
    accommodation_preference: str | None = Field(
        default=None,
        description="Accommodation preference (camping, hostels, hotels, mixed)",
    )
    destination: str | None = Field(
        default=None, description="Destination country for visa requirements (optional)"
    )
    nationality: str | None = Field(
        default=None, description="Traveler's nationality for visa requirements (optional)"
    )


def convert_to_eur(amount: float, currency: str) -> float:
    """Convert amount from given currency to EUR."""
    if currency == "EUR":
        return amount
    if currency in CURRENCY_RATES:
        # Convert to EUR
        if currency == "USD":
            return amount / CURRENCY_RATES["USD"]
        elif currency == "GBP":
            return amount / CURRENCY_RATES["GBP"]
        elif currency == "DKK":
            return amount / CURRENCY_RATES["DKK"]
        elif currency == "CZK":
            return amount / CURRENCY_RATES["CZK"]
    # Default: assume same as EUR if unknown
    logger.warning("Unknown currency: %s, assuming EUR equivalent", currency)
    return amount


def convert_eur_to_usd(amount_eur: float) -> float:
    """Convert EUR amount to USD."""
    return amount_eur * CURRENCY_RATES["USD"]


def get_accommodation_price(
    accommodations: list[dict], accommodation_preference: str | None
) -> tuple[float, str] | None:
    """Get accommodation price based on preference. Returns (price, currency) or None."""
    if not accommodations:
        return None

    # Normalize preference
    pref = accommodation_preference.lower().strip() if accommodation_preference else "mixed"

    if pref == "mixed" or pref == "all" or not accommodation_preference:
        # Use cheapest option
        cheapest = min(accommodations, key=lambda x: x.get("price_per_night", float("inf")))
        return (cheapest.get("price_per_night", 0), cheapest.get("currency", "EUR"))

    # Filter by type
    filtered = [acc for acc in accommodations if acc.get("type", "").lower() == pref]
    if not filtered:
        # Fallback to cheapest if preference not available
        cheapest = min(accommodations, key=lambda x: x.get("price_per_night", float("inf")))
        return (cheapest.get("price_per_night", 0), cheapest.get("currency", "EUR"))

    # Use cheapest of filtered
    cheapest = min(filtered, key=lambda x: x.get("price_per_night", float("inf")))
    return (cheapest.get("price_per_night", 0), cheapest.get("currency", "EUR"))


@tool(args_schema=EstimateBudgetInput)
def estimate_budget(
    start_point: str,
    end_point: str,
    duration_days: int | None = None,
    daily_average_km: float | None = None,
    accommodation_preference: str | None = None,
    destination: str | None = None,
    nationality: str | None = None,
) -> str:
    """Estimate budget for a cycling trip.

    Includes accommodation, food, visa, and other expenses.
    """
    logger.info(
        (
            "estimate_budget called - start_point: %s, end_point: %s, duration_days: %s, "
            "daily_average_km: %s, accommodation_preference: %s, destination: %s, nationality: %s"
        ),
        start_point,
        end_point,
        duration_days,
        daily_average_km,
        accommodation_preference,
        destination,
        nationality,
    )

    try:
        # Load and find route
        routes = load_routes()
        route = find_route_fuzzy(start_point, end_point, routes)

        if not route:
            return (
                f"No route found from {start_point} to {end_point}.\n"
                "Please check the location names and try again."
            )

        # Extract route information
        distance_km = route.get("distance_km", 0)
        waypoints = route.get("waypoints", [])

        # Calculate duration
        if duration_days is None:
            if daily_average_km is None or daily_average_km <= 0:
                return (
                    "Error: Either duration_days or daily_average_km must be provided "
                    "to calculate the budget."
                )
            duration_days = math.ceil(distance_km / daily_average_km)
        estimated_days = duration_days

        # Calculate accommodation costs
        accommodation_total_eur = 0.0
        accommodation_breakdown: list[str] = []
        accommodation_by_currency: dict[str, float] = defaultdict(float)

        if waypoints and len(waypoints) > 1:
            # Calculate nights per waypoint segment
            # We'll stay at each waypoint except the last one
            num_stops = len(waypoints) - 1
            nights_per_stop = max(1, estimated_days // num_stops) if num_stops > 0 else 0

            for i, waypoint in enumerate(waypoints[:-1]):  # Exclude last waypoint
                waypoint_name = (
                    waypoint.get("name") if isinstance(waypoint, dict) else str(waypoint)
                )
                if not waypoint_name:
                    continue

                # Find accommodations for this waypoint
                acc_type = accommodation_preference or "all"
                accommodations = find_accommodations(waypoint_name, acc_type)
                acc_price_info = get_accommodation_price(accommodations, accommodation_preference)

                if acc_price_info:
                    price, currency = acc_price_info
                    nights = nights_per_stop if i < num_stops - 1 else (
                        estimated_days - (nights_per_stop * (num_stops - 1))
                    )
                    total_cost = price * nights
                    accommodation_total_eur += convert_to_eur(total_cost, currency)
                    accommodation_by_currency[currency] += total_cost
                    accommodation_breakdown.append(
                        f"  {waypoint_name}: {price:.2f} {currency}/night × {nights} nights = "
                        f"{total_cost:.2f} {currency}"
                    )
                else:
                    # Estimate based on preference if no data
                    estimated_price = 25.0  # Default EUR
                    if accommodation_preference:
                        pref = accommodation_preference.lower()
                        if pref == "camping":
                            estimated_price = 15.0
                        elif pref == "hostel":
                            estimated_price = 25.0
                        elif pref == "hotel":
                            estimated_price = 80.0
                    nights = nights_per_stop if i < num_stops - 1 else (
                        estimated_days - (nights_per_stop * (num_stops - 1))
                    )
                    total_cost = estimated_price * nights
                    accommodation_total_eur += total_cost
                    accommodation_by_currency["EUR"] += total_cost
                    accommodation_breakdown.append(
                        f"  {waypoint_name}: {estimated_price:.2f} EUR/night × {nights} nights = "
                        f"{total_cost:.2f} EUR (estimated)"
                    )
        else:
            # No waypoints or single waypoint - estimate based on total days
            estimated_price = 25.0  # Default EUR
            if accommodation_preference:
                pref = accommodation_preference.lower()
                if pref == "camping":
                    estimated_price = 15.0
                elif pref == "hostel":
                    estimated_price = 25.0
                elif pref == "hotel":
                    estimated_price = 80.0
            accommodation_total_eur = estimated_price * estimated_days
            accommodation_by_currency["EUR"] = accommodation_total_eur
            accommodation_breakdown.append(
                f"  Estimated: {estimated_price:.2f} EUR/night × {estimated_days} days = "
                f"{accommodation_total_eur:.2f} EUR"
            )

        # Calculate food costs
        food_total_eur = DAILY_FOOD_COST * estimated_days

        # Calculate visa costs
        visa_total_usd = 0.0
        visa_info = ""
        if destination and nationality:
            visa_data = find_visa_requirements(destination, nationality)
            if visa_data:
                visa_cost = visa_data.get("cost_usd", 0)
                if visa_cost and visa_cost > 0:
                    visa_total_usd = visa_cost
                    visa_info = f"Visa required: {visa_total_usd:.2f} USD"
                else:
                    visa_info = "No visa cost (visa not required or free)"
            else:
                visa_info = "Visa information not available"
        elif destination or nationality:
            visa_info = "Both destination and nationality required for visa cost calculation"

        # Convert visa cost to EUR
        visa_total_eur = visa_total_usd / CURRENCY_RATES["USD"] if visa_total_usd > 0 else 0.0

        # Calculate other expenses
        bike_maintenance_eur = BIKE_MAINTENANCE_PER_KM * distance_km
        miscellaneous_eur = MISCELLANEOUS_PER_DAY * estimated_days
        other_total_eur = bike_maintenance_eur + miscellaneous_eur

        # Calculate total
        total_eur = accommodation_total_eur + food_total_eur + visa_total_eur + other_total_eur
        total_usd = convert_eur_to_usd(total_eur)

        # Build result string
        result = f"Budget Estimate for {start_point} to {end_point}:\n"
        result += f"- Route: {distance_km} km, {estimated_days} days\n\n"

        # Accommodation breakdown
        result += f"Accommodation: {accommodation_total_eur:.2f} EUR\n"
        if accommodation_breakdown:
            result += "\n".join(accommodation_breakdown) + "\n"
        if accommodation_by_currency:
            currency_lines = []
            for curr, amount in sorted(accommodation_by_currency.items()):
                if curr != "EUR":
                    currency_lines.append(f"  ({amount:.2f} {curr})")
            if currency_lines:
                result += "  " + " ".join(currency_lines) + "\n"
        result += "\n"

        # Food
        food_line = (
            f"Food: {food_total_eur:.2f} EUR "
            f"({DAILY_FOOD_COST:.2f} EUR/day × {estimated_days} days)\n\n"
        )
        result += food_line

        # Visa
        if visa_info:
            if visa_total_usd > 0:
                result += f"Visa: {visa_total_usd:.2f} USD ({visa_total_eur:.2f} EUR)\n"
            else:
                result += f"Visa: {visa_info}\n"
            result += "\n"

        # Other expenses
        result += f"Other Expenses: {other_total_eur:.2f} EUR\n"
        result += f"  - Bike maintenance: {bike_maintenance_eur:.2f} EUR "
        result += f"({BIKE_MAINTENANCE_PER_KM:.2f} EUR/km × {distance_km} km)\n"
        result += f"  - Miscellaneous: {miscellaneous_eur:.2f} EUR "
        result += f"({MISCELLANEOUS_PER_DAY:.2f} EUR/day × {estimated_days} days)\n\n"

        # Total
        result += f"Total: {total_eur:.2f} EUR / {total_usd:.2f} USD"

        return result

    except Exception as e:
        logger.error(
            (
                "estimate_budget error - start_point: %s, end_point: %s, duration_days: %s, "
                "daily_average_km: %s, accommodation_preference: %s, destination: %s, "
                "nationality: %s, error: %s"
            ),
            start_point,
            end_point,
            duration_days,
            daily_average_km,
            accommodation_preference,
            destination,
            nationality,
            str(e),
            exc_info=True,
        )
        raise
