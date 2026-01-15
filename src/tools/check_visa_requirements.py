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


class CheckVisaRequirementsOutput(BaseModel):
    """Output schema for check_visa_requirements tool."""

    destination: str = Field(description="Destination country")
    nationality: str = Field(description="Traveler's nationality")
    visa_required: bool = Field(description="Whether a visa is required")
    visa_type: str = Field(description="Type of visa required")
    processing_time: str = Field(description="Processing time for visa application")
    duration_of_stay: str = Field(description="Allowed duration of stay")
    cost_usd: float | None = Field(default=None, description="Cost of visa in USD")
    notes: str | None = Field(default=None, description="Additional notes about visa requirements")


@tool(args_schema=CheckVisaRequirementsInput)
def check_visa_requirements(destination: str, nationality: str) -> dict:
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

        # Build structured output
        output = CheckVisaRequirementsOutput(
            destination=destination,
            nationality=nationality,
            visa_required=visa_data.get("visa_required", False),
            visa_type=visa_data.get("visa_type", "Unknown"),
            processing_time=visa_data.get("processing_time", "Unknown"),
            duration_of_stay=visa_data.get("duration_of_stay", "Unknown"),
            cost_usd=visa_data.get("cost_usd"),
            notes=visa_data.get("notes"),
        )

        # Return structured data as dict
        return output.model_dump()
    except Exception as e:
        logger.error(
            "check_visa_requirements error - destination: %s, nationality: %s, error: %s",
            destination,
            nationality,
            str(e),
            exc_info=True,
        )
        raise
