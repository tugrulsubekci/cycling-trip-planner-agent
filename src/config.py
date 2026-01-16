"""Centralized configuration management for Cycling Trip Planner Agent."""

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import SecretStr

# Load environment variables from .env file
load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    # Anthropic API Configuration
    anthropic_api_key: SecretStr

    # Model Configuration
    model_name: str

    # API Configuration
    api_url: str
    chat_api_url: str | None

    # Timeout Configuration (in seconds)
    chat_timeout: float
    health_check_timeout: float

    # Logging Configuration
    log_level: str
    console_log_level: str

    @property
    def effective_api_url(self) -> str:
        """Get effective API URL (chat_api_url if set, otherwise api_url)."""
        return self.chat_api_url or self.api_url


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

    return Settings(
        anthropic_api_key=SecretStr(api_key),
        model_name=os.getenv("MODEL_NAME", "claude-sonnet-4-5"),
        api_url=os.getenv("API_URL", "http://localhost:8000"),
        chat_api_url=os.getenv("CHAT_API_URL"),
        chat_timeout=float(os.getenv("CHAT_TIMEOUT", "120.0")),
        health_check_timeout=float(os.getenv("HEALTH_CHECK_TIMEOUT", "5.0")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        console_log_level=os.getenv("CONSOLE_LOG_LEVEL", "WARNING"),
    )
