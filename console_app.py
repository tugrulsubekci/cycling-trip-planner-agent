"""Interactive console application for Cycling Trip Planner Agent."""

import asyncio
import logging
import sys

import httpx
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from src.config import get_settings
from src.constants import CHAT_ENDPOINT
from src.logging_config import setup_logging

# Get settings and configure logging
settings = get_settings()
setup_logging(level=settings.console_log_level)

logger: logging.Logger = logging.getLogger(__name__)

# Create Rich console instance
console = Console()

# API Configuration
API_URL = settings.effective_api_url
CHAT_ENDPOINT_URL = f"{API_URL}{CHAT_ENDPOINT}"


def print_welcome() -> None:
    """Display welcome banner."""
    welcome_text = Text()
    welcome_text.append("🚴 ", style="bold cyan")
    welcome_text.append("Cycling Trip Planner Agent", style="bold white")
    welcome_text.append("\n", style="reset")
    welcome_text.append("Ask me anything about planning your cycling trip!", style="dim")

    console.print(Panel(welcome_text, border_style="cyan", padding=(1, 2)))
    console.print()


def print_goodbye() -> None:
    """Display goodbye message."""
    console.print("\n[bold cyan]👋 Happy cycling! Safe travels![/bold cyan]\n")


def print_separator() -> None:
    """Print a visual separator between interactions."""
    console.print("[dim]" + "─" * 60 + "[/dim]")


async def send_chat_message(
    client: httpx.AsyncClient,
    message: str,
    thread_id: str | None,
) -> tuple[str, str]:
    """
    Send a chat message to the API endpoint.

    Args:
        client: HTTP client instance
        message: User's message
        thread_id: Optional thread ID for conversation continuity

    Returns:
        Tuple of (thread_id, response_message)

    Raises:
        httpx.HTTPStatusError: For HTTP 4xx/5xx errors
        httpx.RequestError: For network errors
    """
    try:
        response = await client.post(
            CHAT_ENDPOINT_URL,
            json={"thread_id": thread_id, "message": message},
            timeout=settings.chat_timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data["thread_id"], data["message"]
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP {e.response.status_code}"
        if e.response.status_code == 400:
            error_msg += ": Bad request. Please check your input."
        elif e.response.status_code == 500:
            error_msg += ": Server error. Please try again later."
        else:
            try:
                detail = e.response.json().get("detail", str(e))
                error_msg += f": {detail}"
            except Exception:
                error_msg += f": {str(e)}"
        raise httpx.HTTPStatusError(error_msg, request=e.request, response=e.response) from e
    except httpx.RequestError as e:
        raise httpx.RequestError(
            f"Network error: Could not connect to API at {CHAT_ENDPOINT_URL}. "
            f"Make sure the server is running. Error: {str(e)}",
            request=e.request,
        ) from e


async def main() -> None:
    """Main interactive loop for the console application."""
    # Display welcome message
    print_welcome()

    # Initialize thread_id (will be set after first API call)
    thread_id: str | None = None

    # Create HTTP client
    async with httpx.AsyncClient() as client:
        # Test connection to API
        try:
            console.print(f"[dim]Connecting to API at {API_URL}...[/dim]")
            health_response = await client.get(
                f"{API_URL}/health", timeout=settings.health_check_timeout
            )
            health_response.raise_for_status()
            console.print("[green]✓ Connected to API[/green]\n")
        except httpx.RequestError as e:
            console.print(
                f"[bold red]Connection Error:[/bold red] Could not connect to API at {API_URL}",
                style="red",
            )
            console.print(
                "[yellow]Please make sure the API server is running. "
                "You can set CHAT_API_URL or API_URL environment variable "
                "to change the API URL.[/yellow]"
            )
            logger.error(f"API connection error: {e}", exc_info=True)
            sys.exit(1)
        except httpx.HTTPStatusError as e:
            console.print(
                f"[bold red]API Error:[/bold red] API returned status {e.response.status_code}",
                style="red",
            )
            logger.error(f"API health check error: {e}", exc_info=True)
            sys.exit(1)

        # Interactive loop
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("[bold cyan]You[/bold cyan]")

                # Check for exit commands
                if user_input.lower().strip() in ["exit", "quit", "q"]:
                    print_goodbye()
                    break

                # Skip empty input
                if not user_input.strip():
                    continue

                # Show loading indicator
                with console.status("[bold yellow]Thinking...", spinner="dots"):
                    try:
                        # Send message to API
                        thread_id, response = await send_chat_message(
                            client, user_input, thread_id
                        )
                    except httpx.HTTPStatusError as e:
                        console.print(
                            f"[bold red]API Error:[/bold red] {str(e)}",
                            style="red",
                        )
                        logger.error(f"API HTTP error: {e}", exc_info=True)
                        continue
                    except httpx.RequestError as e:
                        console.print(
                            f"[bold red]Network Error:[/bold red] {str(e)}",
                            style="red",
                        )
                        console.print(
                            "[yellow]Please check your connection and make sure "
                            "the API server is running.[/yellow]",
                        )
                        logger.error(f"API request error: {e}", exc_info=True)
                        continue
                    except Exception as e:
                        console.print(
                            f"[bold red]Error:[/bold red] {str(e)}",
                            style="red",
                        )
                        logger.error(f"Unexpected error: {e}", exc_info=True)
                        continue

                # Render markdown response
                console.print()
                console.print(
                    Panel(
                        Markdown(response),
                        border_style="green",
                        title="Agent",
                        padding=(1, 2),
                    )
                )
                console.print()
                print_separator()
                console.print()

            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                console.print("\n[yellow]Interrupted. Type 'exit' or 'quit' to exit.[/yellow]\n")
                continue
            except EOFError:
                # Handle Ctrl+D (EOF)
                print_goodbye()
                break


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_goodbye()
        sys.exit(0)
