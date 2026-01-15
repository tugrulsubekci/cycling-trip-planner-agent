"""FastAPI routes for Cycling Trip Planner Agent."""

import logging
import os
import uuid

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field, SecretStr

from src.agent.planner import CyclingTripPlannerAgent

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger: logging.Logger = logging.getLogger(__name__)

# Create router
router: APIRouter = APIRouter()

# Create agent instance once at module level
# Agent is stateless - state is managed by checkpointer via thread_id
agent = CyclingTripPlannerAgent()


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
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@router.get("/hello-ai")
async def hello_ai() -> dict[str, str]:
    """Hello AI endpoint using Anthropic API via LangChain."""
    # Check if API key is set
    api_key: str | None = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY environment variable is not set")
        raise HTTPException(
            status_code=500,
            detail="ANTHROPIC_API_KEY environment variable is not set",
        )

    try:
        # Initialize ChatAnthropic model
        model = ChatAnthropic(  # type: ignore[call-arg]
            model_name="claude-sonnet-4-5",
            api_key=SecretStr(api_key),
        )

        # Send a simple hello prompt
        response = await model.ainvoke("Say hello and introduce yourself briefly.")
        message_content = response.content if hasattr(response, "content") else str(response)
        message_str = message_content if isinstance(message_content, str) else str(message_content)

        return {"message": message_str}

    except Exception as e:
        logger.error(f"Error calling Anthropic API: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error calling Anthropic API: {str(e)}",
        ) from e


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Chat endpoint for cycling trip planning."""
    try:
        # Generate thread_id if not provided
        thread_id = request.thread_id or str(uuid.uuid4())

        # Use module-level agent instance
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
