"""Main FastAPI application entry point for Cycling Trip Planner Agent."""

import logging

from fastapi import FastAPI

from src.api import routes
from src.config import get_settings
from src.logging_config import setup_logging

# Get settings and configure logging
settings = get_settings()
setup_logging(level=settings.log_level)

logger: logging.Logger = logging.getLogger(__name__)

# Create FastAPI app instance
app: FastAPI = FastAPI(
    title="Cycling Trip Planner Agent",
    description="A FastAPI application for planning cycling trips",
    version="0.1.0",
)

# Include router from routes module
app.include_router(routes.router)
