"""Main FastAPI application entry point for Cycling Trip Planner Agent."""

import logging

from dotenv import load_dotenv
from fastapi import FastAPI

from src.api import routes

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger: logging.Logger = logging.getLogger(__name__)

# Create FastAPI app instance
app: FastAPI = FastAPI(
    title="Cycling Trip Planner Agent",
    description="A FastAPI application for planning cycling trips",
    version="0.1.0",
)

# Include router from routes module
app.include_router(routes.router)
