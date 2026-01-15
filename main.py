"""Main FastAPI application for Cycling Trip Planner Agent."""

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from langchain_anthropic import ChatAnthropic

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger: logging.Logger = logging.getLogger(__name__)

app: FastAPI = FastAPI(
    title="Cycling Trip Planner Agent",
    description="A FastAPI application for planning cycling trips",
    version="0.1.0",
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint returning hello world message."""
    logger.info("Root endpoint accessed")
    return {"message": "Hello World"}


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    logger.info("Health check endpoint accessed")
    return {"status": "ok"}


@app.get("/hello-ai")
async def hello_ai() -> dict[str, str]:
    """Hello AI endpoint using Anthropic API via LangChain."""
    logger.info("Hello AI endpoint accessed")

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
        model = ChatAnthropic(
            model="claude-sonnet-4-5",
            api_key=api_key,
        )

        # Send a simple hello prompt
        response = await model.ainvoke("Say hello and introduce yourself briefly.")
        message_content = response.content if hasattr(response, "content") else str(response)

        logger.info("Successfully received response from Anthropic API")
        return {"message": message_content}

    except Exception as e:
        logger.error(f"Error calling Anthropic API: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error calling Anthropic API: {str(e)}",
        ) from e
