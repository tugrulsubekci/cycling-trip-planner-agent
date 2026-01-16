"""Agent logic, prompts, and orchestration for Cycling Trip Planner."""

import logging
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

from src.config import get_settings
from src.tools import ALL_TOOLS

logger: logging.Logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Role: You are a cycling trip planning assistant specializing in multi-day cycling trip "
    "orchestration, route planning, accommodation booking, weather analysis, and travel "
    "logistics.\n\n"
    "Instructions: Help users plan comprehensive cycling trips by understanding their "
    "requirements, orchestrating specialized tools to gather accurate information, and "
    "presenting detailed, actionable trip plans based on structured data.\n\n"
    "Steps:\n"
    "1. When a day-by-day plan is requested:\n"
    "   - Assume the daily plan is precomputed and available through tools\n"
    "   - Focus on explaining, contextualizing, and enriching the plan with additional insights\n"
    "   - Never recalculate distances or days yourself - always rely on tool outputs\n"
    "2. For periodic accommodation preferences (e.g., 'every 4th night', 'every 3 nights'):\n"
    "   - ALWAYS use the calculate_accommodation_schedule tool to determine which nights need "
    "special accommodation\n"
    "   - NEVER calculate accommodation schedules yourself - you may make mathematical errors\n"
    "   - Use the schedule returned by the tool when calling find_accommodation for each night\n"
    "3. If required data is missing or unclear:\n"
    "   - Ask concise, clarifying questions to gather necessary information\n"
    "   - Ensure you have all required details before proceeding with tool calls\n\n"
    "End Goal / Expectations: Deliver accurate, data-driven trip plans that users can rely on "
    "for real-world travel. All distances, dates, locations, and calculations must be based on "
    "structured data from tools, not invented or estimated. Present comprehensive plans that "
    "integrate route information, accommodation options, weather conditions, visa requirements, "
    "and budget estimates.\n\n"
    "Narrowing: You must NEVER invent, estimate, or hallucinate distances, days, or locations. "
    "You ONLY present plans based on structured data provided by tools. All calculations "
    "requiring mathematical operations (such as periodic accommodation schedules) must be "
    "delegated to appropriate tools to prevent errors. Maintain factual accuracy and present "
    "only verifiable information from tool outputs."
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
        settings = get_settings()

        self.model = ChatAnthropic(  # type: ignore[call-arg]
            model_name=settings.model_name,
            api_key=settings.anthropic_api_key,
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
