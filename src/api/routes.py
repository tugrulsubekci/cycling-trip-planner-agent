"""FastAPI routes for Cycling Trip Planner Agent."""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.agent.planner import CyclingTripPlannerAgent
from src.config import get_settings
from src.logging_config import setup_logging

# Get settings and configure logging
settings = get_settings()
setup_logging(level=settings.log_level)

logger: logging.Logger = logging.getLogger(__name__)

# Create router
router: APIRouter = APIRouter()

# Agent dependency - creates agent instance per request or reuses singleton
_agent_instance: CyclingTripPlannerAgent | None = None


def get_agent() -> CyclingTripPlannerAgent:
    """Get or create agent instance (singleton pattern for dependency injection)."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = CyclingTripPlannerAgent()
    return _agent_instance


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    thread_id: str | None = Field(
        default=None,
        description="Optional thread ID. If not provided, a new one will be generated.",
    )
    message: str = Field(..., description="User's message to the agent")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    thread_id: str = Field(..., description="Thread ID (newly generated or existing)")
    message: str = Field(..., description="Agent's response message")


@router.get("/")
async def root() -> dict[str, str]:
    """Root endpoint returning hello world message."""
    return {"message": "Hello World"}


@router.get("/health")
async def health(agent: CyclingTripPlannerAgent = Depends(get_agent)) -> dict[str, str]:
    """Health check endpoint with agent status verification."""
    try:
        # Verify agent is initialized
        if agent is None:
            return {"status": "error", "message": "Agent not initialized"}

        # Check if API key is available (agent initialization requires it)
        settings = get_settings()
        api_key_available = settings.anthropic_api_key is not None

        if api_key_available:
            return {
                "status": "ok",
                "agent": "initialized",
                "api_key": "available",
            }
        else:
            return {
                "status": "error",
                "agent": "initialized",
                "api_key": "not_available",
            }
    except Exception as e:
        logger.error(f"Health check error: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"Health check failed: {str(e)}",
        }


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    agent: CyclingTripPlannerAgent = Depends(get_agent),
) -> ChatResponse:
    """Chat endpoint for cycling trip planning."""
    try:
        # Generate thread_id if not provided
        thread_id = request.thread_id or str(uuid.uuid4())

        # Use agent from dependency injection
        response_message = await agent.invoke(request.message, thread_id=thread_id)

        return ChatResponse(
            thread_id=thread_id,
            message=response_message,
        )
    except ValueError as e:
        logger.error(
            "Value error in chat endpoint - thread_id: %s, error: %s",
            request.thread_id or "unknown",
            str(e),
        )
        raise HTTPException(
            status_code=400,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(
            "Error in chat endpoint - thread_id: %s, error: %s, error_type: %s",
            request.thread_id or "unknown",
            str(e),
            type(e).__name__,
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}",
        ) from e
