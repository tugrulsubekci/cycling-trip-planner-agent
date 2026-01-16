# Cycling Trip Planner Agent

An intelligent AI-powered agent that helps cyclists plan multi-day trips by orchestrating route planning, accommodation booking, weather analysis, budget estimation, and travel logistics.

## Agent Tools

The agent has access to eight specialized tools:

- **`get_route`**: Gets cycling route information including distance, estimated days, waypoints, and difficulty between two points
- **`find_accommodation`**: Searches for accommodation options (camping, hostels, hotels) near a specified location
- **`calculate_accommodation_schedule`**: Calculates which nights should use special accommodation types based on periodic patterns (e.g., "every 4th night")
- **`get_weather`**: Retrieves typical weather data for a location and month to assess cycling suitability
- **`get_elevation_profile`**: Provides elevation profiles and terrain difficulty ratings for routes or locations
- **`get_points_of_interest`**: Finds interesting places (historical, natural, cultural) along routes or near locations
- **`check_visa_requirements`**: Determines visa requirements for travelers based on destination and nationality
- **`estimate_budget`**: Calculates comprehensive trip budgets including accommodation, food, maintenance, and miscellaneous costs

## Technology Stack

**Core Framework**: LangChain, LangChain Anthropic, LangGraph, Pydantic

**Development & Utilities**: Python-dotenv, RapidFuzz, Rich, httpx

**Testing & Quality**: pytest/pytest-cov/pytest-mock, Mypy, Ruff

## Model Selection: Claude Sonnet 4.5

We selected Anthropic's Claude Sonnet 4.5 as the foundation model for its superior reasoning capabilities, excellent tool use, and strong adherence to structured outputs. Claude's ability to follow system prompts precisely helps prevent hallucination of distances, dates, or locations—critical for reliable trip planning.

The model's large context window supports long conversation histories, allowing users to refine and iterate on their plans over multiple interactions.

## Temperature = 0: Deterministic Output

The agent is configured with `temperature=0` to ensure deterministic, reproducible responses. This eliminates randomness, guaranteeing consistent tool calling behavior and reducing the risk of hallucination—essential for reliable trip planning where accuracy is critical.

## Architectural Decisions

**RISEN Framework**: The system prompt follows RISEN (Role, Instructions, Steps, End Goal, Narrowing) for structured prompt engineering, ensuring the agent never invents data and always relies on tool outputs.

**Comprehensive Logging**: Structured logging at INFO level throughout the agent lifecycle enables traceability, debugging, and performance monitoring.

**InMemorySaver Checkpointer**: Chosen for simplicity and thread-based conversation management. Can be swapped for persistent storage (PostgreSQL, MongoDB) in production.

**ToolErrorHandlerMiddleware**: Custom middleware provides graceful error handling, transforming technical exceptions into user-friendly messages while maintaining agent resilience.

**Singleton Agent Pattern**: Agent instance is created once and reused via FastAPI dependency injection for efficiency and consistency.

**Thread-based Conversations**: Each conversation identified by `thread_id` enables context persistence across multiple API calls.

**Structured Tool Outputs**: All tools return Pydantic models for type safety, consistent structure, and better IDE support.

## Setup Instructions

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   ```

2. **Activate Virtual Environment**
   - Windows PowerShell: `venv\Scripts\Activate.ps1`
   - Windows CMD: `venv\Scripts\activate.bat`
   - Linux/Mac: `source venv/bin/activate`

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**

   Create a `.env` file in the project root:
   ```env
   ANTHROPIC_API_KEY=your_api_key_here
   MODEL_NAME=claude-sonnet-4-5
   API_URL=http://localhost:8000
   LOG_LEVEL=INFO
   CONSOLE_LOG_LEVEL=WARNING
   ```

5. **Run the Application**
   ```bash
   uvicorn main:app --reload
   ```

   API available at `http://localhost:8000` (Interactive docs: `/docs`, Alternative: `/redoc`)

6. **Run Console Application (Optional)**
   ```bash
   python console_app.py
   ```

## API Endpoints

**POST `/chat`** - Main chat endpoint for trip planning conversations

Request:
```json
{
  "thread_id": "optional-thread-id",
  "message": "Plan a cycling trip from Paris to Berlin"
}
```

Response:
```json
{
  "thread_id": "generated-or-provided-thread-id",
  "message": "Agent response with trip plan..."
}
```

## Development Tools

- **Format**: `ruff format .`
- **Lint**: `ruff check .`
- **Type Check**: `mypy src/`
- **Test**: `pytest` (with coverage: `pytest --cov=src --cov-report=html`)

## Future Development

- **Model Evaluation**: Comprehensive evaluation metrics to assess accuracy and hallucination rates
- **UI Card Visualization**: Transform tool outputs into visually appealing cards (routes, accommodations, weather, budgets)
- **Streaming Support**: Real-time feedback about tool usage and agent reasoning
- **Tool Calling Cache**: Caching mechanism to reduce redundant API calls

## Notes

- Code is fully type annotated. The agent uses mock data for demonstration; in production, replace with real API integrations. Conversation state is stored in memory; consider persistent checkpointer for production.
