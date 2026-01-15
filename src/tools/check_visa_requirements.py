"""Tool for checking visa requirements for travel."""

import logging

from langchain.tools import tool
from pydantic import BaseModel, Field

from src.data.mock_data import find_visa_requirements

logger: logging.Logger = logging.getLogger(__name__)


class CheckVisaRequirementsInput(BaseModel):
    """Input schema for check_visa_requirements tool."""

    destination: str = Field(description="Destination country or countries")
    nationality: str = Field(description="Traveler's nationality or passport country")


@tool(args_schema=CheckVisaRequirementsInput)
def check_visa_requirements(destination: str, nationality: str) -> str:
    """Check visa requirements for travel to a destination country."""
    logger.info(
        "check_visa_requirements called - destination: %s, nationality: %s",
        destination,
        nationality,
    )

    try:
        # Find visa requirements using fuzzy matching
        visa_data = find_visa_requirements(destination, nationality)

        if not visa_data:
            return (
                f"No visa requirements data found for {nationality} travelers to {destination}.\n"
                "Please check the destination country and nationality, and try again."
            )

        # Extract visa information
        visa_required = visa_data.get("visa_required", False)
        visa_type = visa_data.get("visa_type", "Unknown")
        processing_time = visa_data.get("processing_time", "Unknown")
        duration_of_stay = visa_data.get("duration_of_stay", "Unknown")
        cost_usd = visa_data.get("cost_usd")
        notes = visa_data.get("notes")

        # Format result string
        result = f"Visa requirements for {nationality} travelers to {destination}:\n"
        result += f"- Visa required: {'Yes' if visa_required else 'No'}\n"
        result += f"- Visa type: {visa_type}\n"
        result += f"- Processing time: {processing_time}\n"
        result += f"- Duration of stay: {duration_of_stay}\n"

        # Add cost if available
        if cost_usd is not None:
            result += f"- Cost: ${cost_usd} USD\n"

        # Add notes if available
        if notes:
            result += f"- Notes: {notes}"

        return result
    except Exception as e:
        logger.error(
            "check_visa_requirements error - destination: %s, nationality: %s, error: %s",
            destination,
            nationality,
            str(e),
            exc_info=True,
        )
        raise
