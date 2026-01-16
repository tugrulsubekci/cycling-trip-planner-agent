"""Tool for estimating budget for a cycling trip."""

import logging
import math
from collections import defaultdict

from langchain.tools import tool
from pydantic import BaseModel, Field

from src.constants import (
    BIKE_MAINTENANCE_PER_KM,
    CAMPING_PRICE,
    CURRENCY_RATES,
    DAILY_FOOD_COST,
    DEFAULT_ACCOMMODATION_PRICE,
    HOSTEL_PRICE,
    HOTEL_PRICE,
    MISCELLANEOUS_PER_DAY,
)
from src.data.mock_data import (
    find_accommodations,
    find_route_fuzzy,
    find_visa_requirements,
    load_routes,
)

logger: logging.Logger = logging.getLogger(__name__)


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


class AccommodationBreakdownItem(BaseModel):
    """Individual accommodation breakdown item."""

    waypoint_name: str = Field(description="Name of the waypoint location")
    price_per_night: float = Field(description="Price per night")
    currency: str = Field(description="Currency code")
    nights: int = Field(description="Number of nights")
    total_cost: float = Field(description="Total cost")
    is_estimated: bool = Field(description="Whether this is an estimated price")


class AccommodationBudgetItem(BaseModel):
    """Accommodation budget details."""

    total_eur: float = Field(description="Total accommodation cost in EUR")
    breakdown: list[AccommodationBreakdownItem] = Field(
        description="Breakdown by waypoint/location"
    )
    currency_details: dict[str, float] = Field(
        description="Total costs by currency (excluding EUR)"
    )


class FoodBudgetItem(BaseModel):
    """Food budget details."""

    total_eur: float = Field(description="Total food cost in EUR")
    daily_cost_eur: float = Field(description="Daily food cost in EUR")
    days: int = Field(description="Number of days")


class VisaBudgetItem(BaseModel):
    """Visa budget details."""

    cost_usd: float = Field(description="Visa cost in USD (0 if not required or free)")
    cost_eur: float = Field(description="Visa cost in EUR")
    info: str = Field(description="Visa information message")


class OtherExpensesItem(BaseModel):
    """Other expenses budget details."""

    total_eur: float = Field(description="Total other expenses in EUR")
    bike_maintenance_eur: float = Field(description="Bike maintenance cost in EUR")
    bike_maintenance_per_km: float = Field(description="Bike maintenance cost per km")
    distance_km: float = Field(description="Total distance in km")
    miscellaneous_eur: float = Field(description="Miscellaneous expenses in EUR")
    miscellaneous_per_day: float = Field(description="Miscellaneous expenses per day")
    days: int = Field(description="Number of days")


class EstimateBudgetOutput(BaseModel):
    """Output schema for estimate_budget tool."""

    start_point: str = Field(description="Starting location")
    end_point: str = Field(description="Destination location")
    route_distance_km: float = Field(description="Total route distance in kilometers")
    estimated_days: int = Field(description="Estimated number of days")
    accommodation: AccommodationBudgetItem = Field(description="Accommodation budget details")
    food: FoodBudgetItem = Field(description="Food budget details")
    visa: VisaBudgetItem = Field(description="Visa budget details")
    other_expenses: OtherExpensesItem = Field(description="Other expenses budget details")
    total_eur: float = Field(description="Total budget in EUR")
    total_usd: float = Field(description="Total budget in USD")


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
) -> dict:
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
        accommodation_breakdown_items: list[AccommodationBreakdownItem] = []
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

                nights = nights_per_stop if i < num_stops - 1 else (
                    estimated_days - (nights_per_stop * (num_stops - 1))
                )

                if acc_price_info:
                    price, currency = acc_price_info
                    total_cost = price * nights
                    accommodation_total_eur += convert_to_eur(total_cost, currency)
                    accommodation_by_currency[currency] += total_cost
                    accommodation_breakdown_items.append(
                        AccommodationBreakdownItem(
                            waypoint_name=waypoint_name,
                            price_per_night=price,
                            currency=currency,
                            nights=nights,
                            total_cost=total_cost,
                            is_estimated=False,
                        )
                    )
                else:
                    # Estimate based on preference if no data
                    estimated_price = DEFAULT_ACCOMMODATION_PRICE
                    if accommodation_preference:
                        pref = accommodation_preference.lower()
                        if pref == "camping":
                            estimated_price = CAMPING_PRICE
                        elif pref == "hostel":
                            estimated_price = HOSTEL_PRICE
                        elif pref == "hotel":
                            estimated_price = HOTEL_PRICE
                    total_cost = estimated_price * nights
                    accommodation_total_eur += total_cost
                    accommodation_by_currency["EUR"] += total_cost
                    accommodation_breakdown_items.append(
                        AccommodationBreakdownItem(
                            waypoint_name=waypoint_name,
                            price_per_night=estimated_price,
                            currency="EUR",
                            nights=nights,
                            total_cost=total_cost,
                            is_estimated=True,
                        )
                    )
        else:
            # No waypoints or single waypoint - estimate based on total days
            estimated_price = DEFAULT_ACCOMMODATION_PRICE
            if accommodation_preference:
                pref = accommodation_preference.lower()
                if pref == "camping":
                    estimated_price = CAMPING_PRICE
                elif pref == "hostel":
                    estimated_price = HOSTEL_PRICE
                elif pref == "hotel":
                    estimated_price = HOTEL_PRICE
            accommodation_total_eur = estimated_price * estimated_days
            accommodation_by_currency["EUR"] = accommodation_total_eur
            accommodation_breakdown_items.append(
                AccommodationBreakdownItem(
                    waypoint_name="Estimated",
                    price_per_night=estimated_price,
                    currency="EUR",
                    nights=estimated_days,
                    total_cost=accommodation_total_eur,
                    is_estimated=True,
                )
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

        # Build currency details (excluding EUR)
        currency_details = {
            curr: amount
            for curr, amount in sorted(accommodation_by_currency.items())
            if curr != "EUR"
        }

        # Build structured output
        output = EstimateBudgetOutput(
            start_point=start_point,
            end_point=end_point,
            route_distance_km=distance_km,
            estimated_days=estimated_days,
            accommodation=AccommodationBudgetItem(
                total_eur=accommodation_total_eur,
                breakdown=accommodation_breakdown_items,
                currency_details=currency_details,
            ),
            food=FoodBudgetItem(
                total_eur=food_total_eur,
                daily_cost_eur=DAILY_FOOD_COST,
                days=estimated_days,
            ),
            visa=VisaBudgetItem(
                cost_usd=visa_total_usd,
                cost_eur=visa_total_eur,
                info=visa_info,
            ),
            other_expenses=OtherExpensesItem(
                total_eur=other_total_eur,
                bike_maintenance_eur=bike_maintenance_eur,
                bike_maintenance_per_km=BIKE_MAINTENANCE_PER_KM,
                distance_km=distance_km,
                miscellaneous_eur=miscellaneous_eur,
                miscellaneous_per_day=MISCELLANEOUS_PER_DAY,
                days=estimated_days,
            ),
            total_eur=total_eur,
            total_usd=total_usd,
        )

        # Return structured data as dict
        return output.model_dump()

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
