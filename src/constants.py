"""Shared constants for Cycling Trip Planner Agent."""

# Model Configuration
DEFAULT_MODEL_NAME = "claude-sonnet-4-5"

# Timeout Configuration (in seconds)
DEFAULT_CHAT_TIMEOUT = 120.0  # 2 minutes for long-running agent operations
DEFAULT_HEALTH_CHECK_TIMEOUT = 5.0  # 5 seconds for health checks

# Data Matching Configuration
SIMILARITY_THRESHOLD = 70  # Minimum similarity percentage for fuzzy matching

# Currency Exchange Rates (for budget estimation)
# These are simplified rates and should be updated for production use
CURRENCY_RATES = {
    "EUR": 1.0,
    "USD": 1.1,  # 1 EUR = 1.1 USD
    "GBP": 0.85,  # 1 EUR = 0.85 GBP
    "DKK": 7.45,  # 1 EUR = 7.45 DKK
    "CZK": 25.0,  # 1 EUR = 25.0 CZK
}

# Daily Cost Estimates (in EUR)
DAILY_FOOD_COST = 40.0  # Average daily food cost
BIKE_MAINTENANCE_PER_KM = 0.1  # Maintenance cost per km
MISCELLANEOUS_PER_DAY = 15.0  # Miscellaneous expenses per day

# Accommodation Price Estimates (in EUR)
DEFAULT_ACCOMMODATION_PRICE = 25.0  # Default accommodation price per night
CAMPING_PRICE = 15.0  # Camping price per night
HOSTEL_PRICE = 25.0  # Hostel price per night
HOTEL_PRICE = 80.0  # Hotel price per night

# API Endpoints
HEALTH_ENDPOINT = "/health"
CHAT_ENDPOINT = "/chat"
