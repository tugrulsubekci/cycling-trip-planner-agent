"""Tool for estimating budget for a cycling trip."""

import logging

from langchain.tools import tool
from pydantic import BaseModel, Field

logger: logging.Logger = logging.getLogger(__name__)


class EstimateBudgetInput(BaseModel):
    """Input schema for estimate_budget tool."""

    route: str = Field(description="Route or trip description")
    duration_days: int | None = Field(default=None, description="Estimated duration in days")
    accommodation_preference: str | None = Field(
        default=None,
        description="Accommodation preference (camping, hostels, hotels, mixed)",
    )


@tool(args_schema=EstimateBudgetInput)
def estimate_budget(
    route: str,
    duration_days: int | None = None,
    accommodation_preference: str | None = None,
) -> str:
    """Estimate budget for a cycling trip including accommodation and food."""
    logger.info(
        "estimate_budget called - route: %s, duration_days: %s, accommodation_preference: %s",
        route,
        duration_days,
        accommodation_preference,
    )

    try:
        duration_info = f" ({duration_days} days)" if duration_days else ""
        accommodation_info = f" ({accommodation_preference})" if accommodation_preference else ""
        result = (
            f"Budget estimate for {route}{duration_info}{accommodation_info}:\n"
            "- Accommodation: [To be calculated]\n"
            "- Food: [To be calculated]\n"
            "- Other expenses: [To be calculated]\n"
            "- Total: [To be calculated]\n"
            "Note: This is a placeholder. Actual implementation pending."
        )
        return result
    except Exception as e:
        logger.error(
            (
                "estimate_budget error - route: %s, duration_days: %s, "
                "accommodation_preference: %s, error: %s"
            ),
            route,
            duration_days,
            accommodation_preference,
            str(e),
            exc_info=True,
        )
        raise
