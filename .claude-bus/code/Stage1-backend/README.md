# GPT-OSS Backend API

FastAPI backend for the GPT-OSS local AI knowledge assistant.

## Features

- RESTful API with automatic OpenAPI documentation
- SQLAlchemy ORM with SQLite (WAL mode) and PostgreSQL support
- Server-Sent Events (SSE) for real-time LLM streaming
- Pydantic validation for type-safe request/response handling
- Comprehensive test coverage with pytest

## Requirements

- Python 3.11.9+ (NOT 3.12 due to async_generators regression)
- llama.cpp HTTP server running on localhost:8080

## Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize database:
```bash
# Database is automatically initialized on first startup
# Tables are created in ./data/gpt_oss.db
```

## Running

### Development Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (when implemented)
```bash
docker-compose up -d backend
```

## Testing

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_database_models.py -v
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── models/
│   │   └── database.py      # SQLAlchemy models
│   ├── schemas/
│   │   ├── project.py       # Pydantic schemas for projects
│   │   ├── conversation.py  # Pydantic schemas for conversations
│   │   └── message.py       # Pydantic schemas for messages
│   ├── db/
│   │   └── session.py       # Database session management
│   ├── api/                 # API route handlers
│   └── services/            # Business logic
├── tests/                   # Unit and integration tests
├── requirements.txt         # Python dependencies
└── .env.example            # Environment variable template
```

## Database Schema

### Projects
- id (PK)
- name
- description
- created_at, updated_at, deleted_at
- metadata (JSON)

### Conversations
- id (PK)
- project_id (FK, nullable)
- title
- created_at, updated_at, deleted_at
- last_message_at
- message_count
- metadata (JSON)

### Messages
- id (PK)
- conversation_id (FK)
- role (user|assistant)
- content (text)
- created_at
- reaction (thumbs_up|thumbs_down|null)
- parent_message_id (FK, self-referential)
- token_count, model_name, completion_time_ms
- metadata (JSON)

## Configuration

All configuration is via environment variables (see `.env.example`):

- `DATABASE_URL`: SQLAlchemy connection string
- `LLM_API_URL`: llama.cpp HTTP API endpoint
- `CORS_ORIGINS`: Allowed CORS origins (comma-separated)
- `DEBUG`: Enable debug mode
- `MAX_MESSAGE_LENGTH`: Maximum message length (default: 10000)

## Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "llm_service": "connected"
}
```

## License

See main project LICENSE file.
