# Cycling Trip Planner Agent

An intelligent AI-powered agent that helps cyclists plan multi-day trips by orchestrating route planning, accommodation booking, weather analysis, budget estimation, and travel logistics.

## Agent Tools

The agent has access to eight specialized tools, each designed to handle a specific aspect of trip planning:

- **`get_route`**: Gets cycling route information including distance, estimated days, waypoints, and difficulty between two points
- **`find_accommodation`**: Searches for accommodation options (camping, hostels, hotels) near a specified location
- **`calculate_accommodation_schedule`**: Calculates which nights should use special accommodation types based on periodic patterns (e.g., "every 4th night")
- **`get_weather`**: Retrieves typical weather data for a location and month to assess cycling suitability
- **`get_elevation_profile`**: Provides elevation profiles and terrain difficulty ratings for routes or locations
- **`get_points_of_interest`**: Finds interesting places (historical, natural, cultural) along routes or near locations
- **`check_visa_requirements`**: Determines visa requirements for travelers based on destination and nationality
- **`estimate_budget`**: Calculates comprehensive trip budgets including accommodation, food, maintenance, and miscellaneous costs

## Technology Stack

### Core Framework & Libraries

- **LangChain**: Framework chosen for its robust agent orchestration, tool integration, and message handling capabilities
- **LangChain Anthropic**: Official integration library providing seamless connection to Anthropic's Claude models
- **LangGraph**: Graph-based agent framework selected for managing complex agent workflows and state persistence
- **Pydantic**: Data validation library chosen for type-safe data models and automatic schema generation

### Development & Utilities

- **Python-dotenv**: Environment variable management library used for secure configuration handling
- **RapidFuzz**: Fast fuzzy string matching library selected for handling location name variations in user queries
- **Rich**: Terminal formatting library chosen for enhanced console application user experience
- **httpx**: Modern HTTP client library selected for async API calls in the console application

### Testing & Quality

- **pytest/pytest-cov/pytest-mock**: Testing framework chosen for comprehensive test coverage and mocking capabilities
- **Mypy**: Static type checker selected to enforce type safety and catch errors before runtime
- **Ruff**: Fast Python linter and formatter chosen to replace multiple tools (flake8, black, isort) for better performance

## Model Selection: Claude Sonnet 4.5

We selected Anthropic's Claude Sonnet 4.5 as the foundation model for this agent for several critical reasons:

**Superior Reasoning Capabilities**: Claude excels at complex multi-step reasoning required for trip planning, where the agent must understand user intent, break down the problem into sub-tasks, and orchestrate multiple tools in the correct sequence.

**Excellent Tool Use**: Claude's function calling capabilities are among the best in the industry, with reliable tool selection and parameter extraction that minimizes errors in tool invocation.

**Structured Output Adherence**: The model demonstrates strong adherence to structured output requirements, which is critical when tools must return consistent, parseable data structures.

**Instruction Following**: Claude's ability to follow system prompts precisely helps prevent hallucination of distances, dates, or locations—a critical requirement when presenting factual trip information to users.

**Safety & Reliability**: Anthropic's focus on safety and reliability aligns perfectly with travel planning accuracy needs, where incorrect information could lead to real-world travel problems.

**Context Window**: Claude's large context window supports long conversation histories with detailed trip information, allowing users to refine and iterate on their plans over multiple interactions.

## Temperature = 0: Deterministic Output

The agent is configured with `temperature=0` to ensure deterministic, reproducible responses. This design decision is critical for several reasons:

**Consistency**: Trip planning requires consistent responses—the same query should produce the same result, especially for critical data like distances, dates, and budgets.

**Reliability**: By eliminating randomness, we guarantee consistent tool calling behavior across identical queries, making the system more predictable and debuggable.

**Accuracy**: Lower temperature reduces the risk of hallucination by making the model more deterministic in its responses, ensuring it relies on tool outputs rather than generating creative but potentially incorrect information.

**User Trust**: Deterministic behavior builds user confidence, as they can expect reliable, factual information when planning their trips.

## Architectural Decisions

### Comprehensive Logging

The application implements structured logging at INFO level throughout the agent lifecycle. Every tool call, agent decision, and error is logged with contextual information including timestamps, tool names, thread IDs, and message previews. This logging strategy enables:

- **Traceability**: Full audit trail of agent decisions and tool usage
- **Debugging**: Easy identification of issues in complex multi-tool workflows
- **Monitoring**: Ability to track agent performance and identify patterns

### InMemorySaver Checkpointer

We chose LangGraph's `InMemorySaver` for conversation state persistence. This decision balances simplicity with functionality:

- **No External Dependencies**: Eliminates the need for databases or external storage systems
- **Thread-based Conversations**: Enables maintaining conversation context across multiple interactions via thread IDs
- **Lightweight**: Keeps the system simple while providing essential state management
- **Development Speed**: Faster iteration without database setup or migrations

For production deployments, this could be easily swapped for a persistent checkpointer (PostgreSQL, MongoDB) without changing the agent logic.

### Middleware Pattern: ToolErrorHandlerMiddleware

Custom middleware wraps all tool executions to provide graceful error handling:

- **User-friendly Errors**: Transforms technical exceptions into actionable error messages
- **Agent Resilience**: Prevents tool errors from crashing the entire agent workflow
- **Error Logging**: Captures detailed error information for debugging while presenting clean messages to users
- **Consistent Error Format**: Ensures all tool errors follow the same response pattern

### Singleton Agent Pattern

The agent instance is created once and reused across all requests via FastAPI's dependency injection:

- **Efficiency**: Avoids expensive re-initialization on every request
- **State Consistency**: Ensures all requests use the same agent configuration
- **Resource Management**: Single model instance reduces memory footprint

### Thread-based Conversations

Each conversation is identified by a `thread_id`, allowing users to:

- **Continue Conversations**: Maintain context across multiple API calls
- **Multiple Sessions**: Support multiple concurrent users with separate conversation threads
- **State Persistence**: Conversation history is maintained in the checkpointer per thread

### Structured Tool Outputs

All tools return Pydantic models rather than raw dictionaries:

- **Type Safety**: Compile-time validation of tool outputs
- **Consistent Structure**: Guaranteed data shape across all tool responses
- **Documentation**: Self-documenting schemas via Pydantic's field descriptions
- **IDE Support**: Better autocomplete and type checking in development

## Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows PowerShell:**
```bash
venv\Scripts\Activate.ps1
```

**Windows CMD:**
```bash
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Upgrade pip (Recommended)

Before installing dependencies, it's recommended to upgrade pip to the latest version:

```bash
python.exe -m pip install --upgrade pip
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
ANTHROPIC_API_KEY=your_api_key_here
MODEL_NAME=claude-sonnet-4-5
API_URL=http://localhost:8000
LOG_LEVEL=INFO
CONSOLE_LOG_LEVEL=WARNING
```

### 6. Run the Application

```bash
uvicorn main:app --reload
```

The API will be available at:
- **API**: `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`

### 7. Run Console Application (Optional)

For an interactive terminal experience:

```bash
python console_app.py
```

## API Endpoints

### Chat Endpoint

- **URL**: `/chat`
- **Method**: `POST`
- **Description**: Main chat endpoint for trip planning conversations
- **Request Body**:
  ```json
  {
    "thread_id": "optional-thread-id",
    "message": "Plan a cycling trip from Paris to Berlin"
  }
  ```
- **Response**:
  ```json
  {
    "thread_id": "generated-or-provided-thread-id",
    "message": "Agent response with trip plan..."
  }
  ```

## Development Tools

### Code Formatting

Format code using Ruff:

```bash
ruff format .
```

### Linting

Check code for linting issues:

```bash
ruff check .
```

### Type Checking

Run type checking with Mypy:

```bash
mypy src/
```

### Running Tests

Execute the test suite:

```bash
pytest
```

With coverage:

```bash
pytest --cov=src --cov-report=html
```

## Project Structure

```
cycling-trip-planner-agent/
├── main.py                      # FastAPI application entry point
├── console_app.py               # Interactive console application
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Project configuration (Ruff, Mypy)
├── src/
│   ├── agent/
│   │   ├── __init__.py
│   │   └── planner.py          # Agent logic and orchestration
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # FastAPI route definitions
│   ├── tools/                  # Agent tools (8 tools)
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── get_route.py
│   │   ├── find_accommodation.py
│   │   ├── calculate_accommodation_schedule.py
│   │   ├── get_weather.py
│   │   ├── get_elevation_profile.py
│   │   ├── get_points_of_interest.py
│   │   ├── check_visa_requirements.py
│   │   └── estimate_budget.py
│   ├── data/                   # Mock data and data loading
│   │   ├── __init__.py
│   │   ├── mock_data.py
│   │   ├── mock_routes.json
│   │   ├── mock_accommodations.json
│   │   ├── mock_weather.json
│   │   ├── mock_elevation.json
│   │   ├── mock_points_of_interest.json
│   │   └── mock_visa.json
│   ├── tests/                  # Test suite
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_get_route.py
│   │   ├── test_find_accommodation.py
│   │   ├── test_calculate_accommodation_schedule.py
│   │   ├── test_get_weather.py
│   │   ├── test_get_elevation_profile.py
│   │   ├── test_get_points_of_interest.py
│   │   ├── test_check_visa_requirements.py
│   │   └── test_estimate_budget.py
│   ├── config.py               # Configuration management
│   ├── logging_config.py       # Logging setup
│   ├── constants.py            # Application constants
│   └── __init__.py
└── README.md                   # This file
```

## Future Development

Given more time, we would focus on the following enhancements:

### Model Evaluation

Implement comprehensive evaluation metrics to assess model accuracy and measure hallucination rates in trip planning scenarios. This would involve creating a test suite of trip planning queries with expected outputs, tracking metrics like:
- Tool selection accuracy
- Parameter extraction correctness
- Hallucination frequency (when model invents data instead of using tools)
- Response quality scores

### UI Card Visualization

Transform tool outputs into visually appealing UI cards for better user experience in frontend applications. Instead of raw JSON responses, the API could return structured card data with:
- Route visualization cards with maps and elevation charts
- Accommodation cards with images and ratings
- Weather cards with icons and forecasts
- Budget breakdown cards with charts

### Streaming Support

Implement streaming responses to provide real-time feedback about tool usage and agent reasoning to frontend users. This would enable:
- Progressive response rendering as the agent thinks
- Real-time tool execution notifications
- Step-by-step reasoning display
- Better perceived performance and user engagement

### Tool Calling Cache

Implement caching mechanism for tool calls to improve performance and reduce redundant API calls. Tools called with the same input can directly return results from cache, eliminating unnecessary computations and external API requests.

## Notes

- The `.gitignore` file already includes `venv/` so the virtual environment will not be committed to version control
- All code is fully type annotated for better code quality and IDE support
- The agent uses mock data for demonstration purposes; in production, these would be replaced with real API integrations
- Conversation state is stored in memory; for production, consider using a persistent checkpointer
