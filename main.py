"""Main FastAPI application for Cycling Trip Planner Agent."""

import logging

from fastapi import FastAPI

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
