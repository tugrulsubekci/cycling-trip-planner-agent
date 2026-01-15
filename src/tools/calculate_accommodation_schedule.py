"""Tool for calculating accommodation schedules based on periodic patterns."""

import logging
import re

from langchain.tools import tool
from pydantic import BaseModel, Field

logger: logging.Logger = logging.getLogger(__name__)


class CalculateAccommodationScheduleInput(BaseModel):
    """Input schema for calculate_accommodation_schedule tool."""

    total_nights: int = Field(description="Total number of nights for the trip")
    preference_pattern: str = Field(
        description=(
            "Pattern describing when to use special accommodation type "
            "(e.g., 'every 4th night', 'every 3 nights')"
        )
    )
    accommodation_type: str = Field(
        description="Type of accommodation to use on special nights (hostel, hotel, camping)"
    )
    default_type: str = Field(
        default="camping",
        description="Default accommodation type for nights not matching the pattern",
    )


class CalculateAccommodationScheduleOutput(BaseModel):
    """Output schema for calculate_accommodation_schedule tool."""

    total_nights: int = Field(description="Total number of nights")
    schedule: dict[int, str] = Field(
        description="Mapping of night number (1-indexed) to accommodation type"
    )
    special_nights: list[int] = Field(
        description="List of night numbers where special accommodation type is used"
    )
    pattern_interpretation: str = Field(
        description="Human-readable interpretation of the pattern"
    )


def parse_pattern(pattern: str) -> int | None:
    """
    Parse a pattern string to extract the period number.

    Examples:
        "every 4th night" -> 4
        "every 3 nights" -> 3
        "every 5th night" -> 5
    """
    # Match patterns like "every 4th night", "every 3 nights", etc.
    match = re.search(r"every\s+(\d+)(?:th|rd|st|nd)?\s+night", pattern.lower())
    if match:
        return int(match.group(1))

    # Match patterns like "every 3 nights" (without ordinal)
    match = re.search(r"every\s+(\d+)\s+nights?", pattern.lower())
    if match:
        return int(match.group(1))

    return None


@tool(args_schema=CalculateAccommodationScheduleInput)
def calculate_accommodation_schedule(
    total_nights: int,
    preference_pattern: str,
    accommodation_type: str,
    default_type: str = "camping",
) -> dict:
    """
    Calculate which nights should use a specific accommodation type based on a periodic pattern.

    This tool prevents hallucination by mathematically calculating the correct nights.
    For example, "every 4th night" means nights 4, 8, 12, 16, etc.

    Args:
        total_nights: Total number of nights for the trip
        preference_pattern: Pattern like "every 4th night" or "every 3 nights"
        accommodation_type: Type to use on special nights (hostel, hotel, camping)
        default_type: Default type for other nights (default: camping)

    Returns:
        Dictionary with schedule mapping and special nights list
    """
    logger.info(
        (
            "calculate_accommodation_schedule called - total_nights: %d, "
            "pattern: %s, type: %s, default: %s"
        ),
        total_nights,
        preference_pattern,
        accommodation_type,
        default_type,
    )

    try:
        # Parse the pattern to extract the period
        period = parse_pattern(preference_pattern)

        if period is None:
            error_msg = (
                f"Could not parse pattern '{preference_pattern}'. "
                "Expected format: 'every Xth night' or 'every X nights' (e.g., 'every 4th night')."
            )
            logger.error("Pattern parsing failed - pattern: %s", preference_pattern)
            return {"error": error_msg}

        if period <= 0:
            error_msg = f"Period must be positive, got {period}"
            logger.error("Invalid period - period: %d", period)
            return {"error": error_msg}

        if total_nights <= 0:
            error_msg = f"Total nights must be positive, got {total_nights}"
            logger.error("Invalid total_nights - total_nights: %d", total_nights)
            return {"error": error_msg}

        # Calculate which nights should use the special accommodation type
        # "every 4th night" means nights 4, 8, 12, 16, ...
        special_nights = [
            night for night in range(period, total_nights + 1, period) if night <= total_nights
        ]

        # Build the schedule: all nights default to default_type,
        # except special_nights which use accommodation_type
        schedule: dict[int, str] = {}
        for night in range(1, total_nights + 1):
            schedule[night] = accommodation_type if night in special_nights else default_type

        # Create human-readable interpretation
        if special_nights:
            nights_str = ", ".join(map(str, special_nights))
            pattern_interpretation = (
                f"Using {accommodation_type} on nights {nights_str} "
                f"(every {period}th night), {default_type} on all other nights."
            )
        else:
            pattern_interpretation = (
                f"Pattern 'every {period}th night' results in no special nights "
                f"for a {total_nights}-night trip. Using {default_type} for all nights."
            )

        output = CalculateAccommodationScheduleOutput(
            total_nights=total_nights,
            schedule=schedule,
            special_nights=special_nights,
            pattern_interpretation=pattern_interpretation,
        )

        logger.info(
            "calculate_accommodation_schedule completed - special_nights: %s",
            special_nights,
        )

        # Return structured data as dict
        return output.model_dump()
    except Exception as e:
        logger.error(
            "calculate_accommodation_schedule error - total_nights: %d, pattern: %s, error: %s",
            total_nights,
            preference_pattern,
            str(e),
            exc_info=True,
        )
        raise
