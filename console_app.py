"""Interactive console application for Cycling Trip Planner Agent."""

import asyncio
import logging
import sys
import uuid

from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from src.agent.planner import CyclingTripPlannerAgent

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.WARNING,  # Reduce console noise
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger: logging.Logger = logging.getLogger(__name__)

# Create Rich console instance
console = Console()


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


async def main() -> None:
    """Main interactive loop for the console application."""
    try:
        # Initialize agent
        console.print("[dim]Initializing agent...[/dim]")
        agent = CyclingTripPlannerAgent()
        console.print("[green]✓ Agent initialized[/green]\n")

        # Generate unique thread_id for this session
        thread_id = str(uuid.uuid4())

        # Display welcome message
        print_welcome()

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
                        # Invoke agent
                        response = await agent.invoke(user_input, thread_id=thread_id)
                    except Exception as e:
                        console.print(
                            f"[bold red]Error:[/bold red] {str(e)}",
                            style="red",
                        )
                        logger.error(f"Agent invocation error: {e}", exc_info=True)
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

    except ValueError as e:
        # Handle missing API key
        console.print(f"[bold red]Configuration Error:[/bold red] {str(e)}", style="red")
        console.print(
            "[yellow]Please make sure ANTHROPIC_API_KEY is set in your "
            ".env file or environment.[/yellow]"
        )
        sys.exit(1)
    except Exception as e:
        # Handle other initialization errors
        console.print(f"[bold red]Initialization Error:[/bold red] {str(e)}", style="red")
        logger.error(f"Initialization error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_goodbye()
        sys.exit(0)
