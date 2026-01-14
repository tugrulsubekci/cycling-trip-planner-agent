# Cycling Trip Planner Agent

A FastAPI application for planning cycling trips with full type annotations and comprehensive logging.

## Features

- FastAPI framework with async support
- Fully type annotated codebase
- Comprehensive logging system
- Code quality tools (Ruff, Mypy)
- Editor configuration for consistent coding style

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

### 5. Run the Application

```bash
uvicorn main:app --reload
```

The API will be available at:
- **API**: `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`

## API Endpoints

### Root Endpoint

- **URL**: `/`
- **Method**: `GET`
- **Description**: Returns a hello world message
- **Response**: `{"message": "Hello World"}`

### Health Check

- **URL**: `/health`
- **Method**: `GET`
- **Description**: Health check endpoint
- **Response**: `{"status": "ok"}`

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
mypy main.py
```

## Logging

The application uses Python's `logging` module with the following configuration:

- **Log Level**: INFO (default)
- **Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Date Format**: `%Y-%m-%d %H:%M:%S`

All endpoints log their access with INFO level. Logs include timestamps, logger name, log level, and the message.

## Code Quality Tools

- **Ruff**: Fast linter and formatter (replaces flake8, black, isort)
- **Mypy**: Static type checker for Python
- **EditorConfig**: Ensures consistent coding styles across editors

All tools are configured in `pyproject.toml` and `.editorconfig`.

## Project Structure

```
cycling-trip-planner-agent/
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Project configuration (Ruff, Mypy)
├── .editorconfig        # Editor configuration
└── README.md           # This file
```

## Requirements

- Python 3.10 or higher
- Virtual environment (recommended)

## Notes

- The `.gitignore` file already includes `venv/` so the virtual environment will not be committed to version control.
- All code is fully type annotated for better code quality and IDE support.