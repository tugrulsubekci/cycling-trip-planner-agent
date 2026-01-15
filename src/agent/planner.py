"""Agent logic, prompts, and orchestration for Cycling Trip Planner."""

import logging
import os
from collections.abc import Awaitable, Callable

from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware
from langchain.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain.tools.tool_node import ToolCallRequest
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage
from langchain_core.runnables.config import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.pregel import Pregel
from langgraph.types import Command
from pydantic import SecretStr

from src.tools import ALL_TOOLS

logger: logging.Logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a cycling trip planning assistant."
    "You do NOT invent distances, days, or locations."
    "You ONLY present plans based on structured data provided to you."
    "When a day-by-day plan is requested:"
    "- Assume the daily plan is precomputed"
    "- Focus on explaining, contextualizing, and enriching it"
    "- Never recalculate distances or days yourself"
    "For periodic accommodation preferences (e.g., 'every 4th night', 'every 3 nights'):"
    "- ALWAYS use the calculate_accommodation_schedule tool to determine "
    "which nights need special accommodation"
    "- NEVER calculate accommodation schedules yourself - you may make mathematical errors"
    "- Use the schedule returned by the tool when calling find_accommodation for each night"
    "If required data is missing, ask concise clarifying questions."
)

class ToolErrorHandlerMiddleware(AgentMiddleware):
    """Middleware to handle tool execution errors with custom messages."""

    async def awrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], Awaitable[ToolMessage | Command]],
    ) -> ToolMessage | Command:
        """Handle tool execution errors with custom messages (async version)."""
        tool_name = request.tool_call.get("name", "unknown")
        tool_call_id = request.tool_call.get("id", "unknown")

        try:
            result = await handler(request)
            # Log successful tool execution
            logger.info(
                "Tool completed - tool_name: %s, tool_call_id: %s",
                tool_name,
                tool_call_id,
            )
            return result
        except Exception as exc:
            # Log tool execution error
            logger.error(
                "Tool execution error - tool_name: %s, tool_call_id: %s, error: %s, error_type: %s",
                tool_name,
                tool_call_id,
                str(exc),
                type(exc).__name__,
                exc_info=True,
            )
            return ToolMessage(
                content=f"Tool error: Please check your input and try again. ({exc})",
                tool_call_id=tool_call_id,
            )

    def wrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
    ) -> ToolMessage | Command:
        """Handle tool execution errors with custom messages (sync version)."""
        tool_name = request.tool_call.get("name", "unknown")
        tool_call_id = request.tool_call.get("id", "unknown")

        try:
            result = handler(request)
            # Log successful tool execution
            logger.info(
                "Tool completed - tool_name: %s, tool_call_id: %s",
                tool_name,
                tool_call_id,
            )
            return result
        except Exception as exc:
            # Log tool execution error
            logger.error(
                "Tool execution error - tool_name: %s, tool_call_id: %s, error: %s, error_type: %s",
                tool_name,
                tool_call_id,
                str(exc),
                type(exc).__name__,
                exc_info=True,
            )
            return ToolMessage(
                content=f"Tool error: Please check your input and try again. ({exc})",
                tool_call_id=tool_call_id,
            )


class CyclingTripPlannerAgent:
    """Cycling Trip Planner Agent using LangChain."""

    def __init__(self) -> None:
        api_key: str | None = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

        self.model = ChatAnthropic(  # type: ignore[call-arg]
            model_name="claude-sonnet-4-5",
            api_key=SecretStr(api_key),
            temperature=0,
        )
        self.checkpointer = InMemorySaver()

        self.agent: Pregel = create_agent(
            model=self.model,
            tools=ALL_TOOLS,
            middleware=[ToolErrorHandlerMiddleware()],
            checkpointer=self.checkpointer,
        )

        logger.info("CyclingTripPlannerAgent initialized")

    async def invoke(self, message: str, thread_id: str) -> str:
        """Invoke the agent with a user message."""
        message_preview = message[:100] + "..." if len(message) > 100 else message
        logger.info(
            "Agent invocation started - thread_id: %s, message_length: %d, message_preview: %s",
            thread_id,
            len(message),
            message_preview,
        )

        try:
            # Check if this is a new thread by checking checkpointer state
            config: RunnableConfig = RunnableConfig(configurable={"thread_id": thread_id})
            checkpoint = await self.checkpointer.aget(config)
            is_new_thread = checkpoint is None or not checkpoint.get("channel_values", {}).get(
                "messages", []
            )

            # Only add SystemMessage for new threads to avoid
            # "multiple non-consecutive system messages" error
            # For existing threads, checkpointer already has the conversation history
            messages: list[SystemMessage | HumanMessage]
            if is_new_thread:
                messages = [
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(content=message),
                ]
            else:
                messages = [HumanMessage(content=message)]

            # Log before agent call
            logger.info(
                "Calling agent.ainvoke - thread_id: %s, messages_count: %d",
                thread_id,
                len(messages),
            )

            response = await self.agent.ainvoke({"messages": messages}, config=config)

            content = self._extract_content(response)

            # Log successful response
            content_preview = content[:100] + "..." if len(content) > 100 else content
            logger.info(
                (
                    "Agent response generated successfully - thread_id: %s, "
                    "response_length: %d, response_preview: %s"
                ),
                thread_id,
                len(content),
                content_preview,
            )
            return content
        except Exception as exc:
            logger.error(
                "Error invoking agent - thread_id: %s, error: %s, error_type: %s",
                thread_id,
                str(exc),
                type(exc).__name__,
                exc_info=True,
            )
            raise

    @staticmethod
    def _extract_content(response: dict[str, list[BaseMessage] | str] | AIMessage) -> str:
        if isinstance(response, AIMessage):
            content = response.content
            return content if isinstance(content, str) else str(content)
        if isinstance(response, dict):
            if "messages" in response and response["messages"]:
                last_message = response["messages"][-1]
                if isinstance(last_message, AIMessage):
                    content = last_message.content
                    return content if isinstance(content, str) else str(content)
                if hasattr(last_message, "content"):
                    content = last_message.content
                    return content if isinstance(content, str) else str(content)
            if "output" in response:
                return str(response["output"])
        return str(response)
