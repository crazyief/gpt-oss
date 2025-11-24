# GPT-OSS API Documentation

**Version**: Stage 1 - Foundation
**Last Updated**: 2025-11-18
**Base URL**: http://localhost:8000
**API Type**: REST + SSE Streaming

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Error Handling](#error-handling)
4. [Project Endpoints](#project-endpoints)
5. [Conversation Endpoints](#conversation-endpoints)
6. [Message Endpoints](#message-endpoints)
7. [Chat Endpoints](#chat-endpoints)
8. [Health Check](#health-check)
9. [Rate Limits](#rate-limits)
10. [Changelog](#changelog)

---

## Overview

The GPT-OSS API provides RESTful endpoints for managing projects, conversations, and messages, plus Server-Sent Events (SSE) streaming for real-time chat interactions.

### API Design Principles

- **RESTful**: Standard HTTP methods (GET, POST, PATCH, DELETE)
- **JSON**: All request/response bodies use JSON
- **Streaming**: SSE for real-time token-by-token responses
- **CORS**: Enabled for localhost:3000 (configurable)
- **Validation**: Pydantic schemas enforce type safety

### Interactive Documentation

**Swagger UI**: http://localhost:8000/docs
**ReDoc**: http://localhost:8000/redoc

---

## Authentication

**Stage 1**: No authentication required (local development)

**Future Stages**:
- Stage 6: JWT-based authentication
- Headers: `Authorization: Bearer <token>`

---

## Error Handling

### Standard Error Response

All errors return this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success (GET, PATCH) | Project retrieved successfully |
| 201 | Created (POST) | Project created |
| 204 | No Content (DELETE) | Project deleted |
| 400 | Bad Request | Invalid JSON or validation error |
| 404 | Not Found | Project ID does not exist |
| 422 | Unprocessable Entity | Pydantic validation failed |
| 500 | Internal Server Error | Database or LLM service error |

### Validation Errors (422)

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "name"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {"min_length": 1}
    }
  ]
}
```

---

## Project Endpoints

### Create Project

**POST** `/api/projects/create`

Create a new project.

**Request Body**:
```json
{
  "name": "IEC 62443 Analysis",
  "description": "Security standards compliance review"
}
```

**Validation**:
- `name`: Required, 1-200 characters
- `description`: Optional, max 1000 characters

**Response** (201 Created):
```json
{
  "id": 1,
  "name": "IEC 62443 Analysis",
  "description": "Security standards compliance review",
  "created_at": "2025-11-18T10:30:00",
  "updated_at": "2025-11-18T10:30:00",
  "metadata": {}
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/projects/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "IEC 62443 Analysis",
    "description": "Security standards compliance review"
  }'
```

---

### Get Project by ID

**GET** `/api/projects/{project_id}`

Retrieve a single project by ID.

**Path Parameters**:
- `project_id`: Integer, must be > 0

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "IEC 62443 Analysis",
  "description": "Security standards compliance review",
  "created_at": "2025-11-18T10:30:00",
  "updated_at": "2025-11-18T10:30:00",
  "metadata": {}
}
```

**Errors**:
- `404`: Project not found

**Example**:
```bash
curl http://localhost:8000/api/projects/1
```

---

### Get Project Statistics

**GET** `/api/projects/{project_id}/stats`

Get conversation and message counts for a project.

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "IEC 62443 Analysis",
  "description": "Security standards compliance review",
  "created_at": "2025-11-18T10:30:00",
  "updated_at": "2025-11-18T10:30:00",
  "metadata": {},
  "conversation_count": 5,
  "total_message_count": 42,
  "last_activity": "2025-11-18T14:20:00"
}
```

**Example**:
```bash
curl http://localhost:8000/api/projects/1/stats
```

---

### List All Projects

**GET** `/api/projects/`

Retrieve all projects with pagination.

**Query Parameters**:
- `skip`: Integer, offset (default: 0)
- `limit`: Integer, max results (default: 100)

**Response** (200 OK):
```json
{
  "projects": [
    {
      "id": 1,
      "name": "IEC 62443 Analysis",
      "description": "Security standards compliance review",
      "created_at": "2025-11-18T10:30:00",
      "updated_at": "2025-11-18T10:30:00",
      "metadata": {}
    }
  ],
  "total_count": 1
}
```

**Example**:
```bash
# Get first 10 projects
curl http://localhost:8000/api/projects/?skip=0&limit=10

# Get next 10 projects
curl http://localhost:8000/api/projects/?skip=10&limit=10
```

---

### Update Project

**PATCH** `/api/projects/{project_id}`

Update project name or description.

**Request Body** (all fields optional):
```json
{
  "name": "Updated Project Name",
  "description": "Updated description"
}
```

**Validation**:
- `name`: 1-200 characters (if provided)
- `description`: max 1000 characters (if provided)

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "Updated Project Name",
  "description": "Updated description",
  "created_at": "2025-11-18T10:30:00",
  "updated_at": "2025-11-18T14:45:00",
  "metadata": {}
}
```

**Example**:
```bash
curl -X PATCH http://localhost:8000/api/projects/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Project Name"}'
```

---

### Delete Project

**DELETE** `/api/projects/{project_id}`

Delete a project and all associated conversations/messages.

**Warning**: This is a CASCADE delete. All conversations and messages will be permanently deleted.

**Response** (204 No Content):
```
(Empty response body)
```

**Example**:
```bash
curl -X DELETE http://localhost:8000/api/projects/1
```

---

## Conversation Endpoints

### Create Conversation

**POST** `/api/conversations/create`

Create a new conversation within a project.

**Request Body**:
```json
{
  "project_id": 1,
  "title": "CR 2.11 Analysis"
}
```

**Validation**:
- `project_id`: Required, must exist
- `title`: Required, 1-200 characters

**Response** (201 Created):
```json
{
  "id": 1,
  "project_id": 1,
  "title": "CR 2.11 Analysis",
  "created_at": "2025-11-18T10:35:00",
  "updated_at": "2025-11-18T10:35:00",
  "metadata": {}
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/conversations/create \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "title": "CR 2.11 Analysis"
  }'
```

---

### Get Conversation by ID

**GET** `/api/conversations/{conversation_id}`

Retrieve a single conversation.

**Response** (200 OK):
```json
{
  "id": 1,
  "project_id": 1,
  "title": "CR 2.11 Analysis",
  "created_at": "2025-11-18T10:35:00",
  "updated_at": "2025-11-18T10:35:00",
  "metadata": {}
}
```

**Example**:
```bash
curl http://localhost:8000/api/conversations/1
```

---

### List Conversations in Project

**GET** `/api/projects/{project_id}/conversations`

Get all conversations in a project.

**Query Parameters**:
- `skip`: Integer, offset (default: 0)
- `limit`: Integer, max results (default: 100)

**Response** (200 OK):
```json
{
  "conversations": [
    {
      "id": 1,
      "project_id": 1,
      "title": "CR 2.11 Analysis",
      "created_at": "2025-11-18T10:35:00",
      "updated_at": "2025-11-18T10:35:00",
      "metadata": {}
    }
  ],
  "total_count": 1
}
```

**Example**:
```bash
curl http://localhost:8000/api/projects/1/conversations
```

---

### Update Conversation

**PATCH** `/api/conversations/{conversation_id}`

Update conversation title.

**Request Body**:
```json
{
  "title": "Updated Conversation Title"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "project_id": 1,
  "title": "Updated Conversation Title",
  "created_at": "2025-11-18T10:35:00",
  "updated_at": "2025-11-18T14:50:00",
  "metadata": {}
}
```

**Example**:
```bash
curl -X PATCH http://localhost:8000/api/conversations/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Conversation Title"}'
```

---

### Delete Conversation

**DELETE** `/api/conversations/{conversation_id}`

Delete a conversation and all associated messages.

**Warning**: CASCADE delete. All messages will be permanently deleted.

**Response** (204 No Content):
```
(Empty response body)
```

**Example**:
```bash
curl -X DELETE http://localhost:8000/api/conversations/1
```

---

## Message Endpoints

### Get Message by ID

**GET** `/api/messages/{message_id}`

Retrieve a single message.

**Response** (200 OK):
```json
{
  "id": 1,
  "conversation_id": 1,
  "role": "user",
  "content": "What is IEC 62443-4-2 CR 2.11?",
  "created_at": "2025-11-18T10:40:00",
  "reaction": null,
  "parent_message_id": null,
  "token_count": 12,
  "model_name": null,
  "completion_time_ms": null,
  "metadata": {}
}
```

**Example**:
```bash
curl http://localhost:8000/api/messages/1
```

---

### List Messages in Conversation

**GET** `/api/conversations/{conversation_id}/messages`

Get all messages in a conversation.

**Query Parameters**:
- `skip`: Integer, offset (default: 0)
- `limit`: Integer, max results (default: 100)

**Response** (200 OK):
```json
{
  "messages": [
    {
      "id": 1,
      "conversation_id": 1,
      "role": "user",
      "content": "What is IEC 62443-4-2 CR 2.11?",
      "created_at": "2025-11-18T10:40:00",
      "reaction": null,
      "parent_message_id": null,
      "token_count": 12,
      "model_name": null,
      "completion_time_ms": null,
      "metadata": {}
    },
    {
      "id": 2,
      "conversation_id": 1,
      "role": "assistant",
      "content": "IEC 62443-4-2 CR 2.11 is...",
      "created_at": "2025-11-18T10:40:05",
      "reaction": "thumbs_up",
      "parent_message_id": null,
      "token_count": 150,
      "model_name": "mistral-small-24b",
      "completion_time_ms": 1250,
      "metadata": {}
    }
  ],
  "total_count": 2
}
```

**Example**:
```bash
curl http://localhost:8000/api/conversations/1/messages
```

---

### Update Message Reaction

**PATCH** `/api/messages/{message_id}/reaction`

Add or remove a reaction to a message.

**Request Body**:
```json
{
  "reaction": "thumbs_up"
}
```

**Available Reactions**:
- `"thumbs_up"`: Like this message
- `"thumbs_down"`: Dislike this message
- `null`: Remove reaction

**Response** (200 OK):
```json
{
  "id": 2,
  "conversation_id": 1,
  "role": "assistant",
  "content": "IEC 62443-4-2 CR 2.11 is...",
  "created_at": "2025-11-18T10:40:05",
  "reaction": "thumbs_up",
  "parent_message_id": null,
  "token_count": 150,
  "model_name": "mistral-small-24b",
  "completion_time_ms": 1250,
  "metadata": {}
}
```

**Example**:
```bash
# Add thumbs up
curl -X PATCH http://localhost:8000/api/messages/2/reaction \
  -H "Content-Type: application/json" \
  -d '{"reaction": "thumbs_up"}'

# Remove reaction
curl -X PATCH http://localhost:8000/api/messages/2/reaction \
  -H "Content-Type: application/json" \
  -d '{"reaction": null}'
```

---

## Chat Endpoints

### Stream Chat Response (SSE)

**POST** `/api/chat/stream`

Send a message and receive streaming response via Server-Sent Events.

**Request Body**:
```json
{
  "conversation_id": 1,
  "message": "What is IEC 62443-4-2 CR 2.11?"
}
```

**Validation**:
- `conversation_id`: Required, must exist
- `message`: Required, 1-10,000 characters

**Response**: SSE stream with multiple events

**Event Types**:

#### 1. Token Event
```
event: token
data: {"token": "The", "message_id": 2, "session_id": "abc123"}

event: token
data: {"token": " requirement", "message_id": 2, "session_id": "abc123"}

event: token
data: {"token": " CR", "message_id": 2, "session_id": "abc123"}
```

#### 2. Complete Event
```
event: complete
data: {"message_id": 2, "token_count": 150, "completion_time_ms": 1250}
```

#### 3. Error Event
```
event: error
data: {"error": "LLM service unavailable", "error_type": "service_error"}
```

**Example (curl)**:
```bash
curl -N -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": 1,
    "message": "What is IEC 62443-4-2 CR 2.11?"
  }'
```

**Example (JavaScript)**:
```javascript
const eventSource = new EventSource(
  'http://localhost:8000/api/chat/stream',
  {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      conversation_id: 1,
      message: 'What is IEC 62443-4-2 CR 2.11?'
    })
  }
);

eventSource.addEventListener('token', (event) => {
  const data = JSON.parse(event.data);
  console.log('Token:', data.token);
  // Append token to UI
});

eventSource.addEventListener('complete', (event) => {
  const data = JSON.parse(event.data);
  console.log('Complete:', data);
  eventSource.close();
});

eventSource.addEventListener('error', (event) => {
  const data = JSON.parse(event.data);
  console.error('Error:', data.error);
  eventSource.close();
});
```

**Example (Python)**:
```python
import requests
import json

response = requests.post(
    'http://localhost:8000/api/chat/stream',
    headers={'Content-Type': 'application/json'},
    json={
        'conversation_id': 1,
        'message': 'What is IEC 62443-4-2 CR 2.11?'
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            data = json.loads(line[6:])
            print(data)
```

**Performance Targets**:
- First token latency: < 2000ms (Stage 1: ~270ms)
- Total stream time: < 5000ms (Stage 1: ~419ms for short responses)

---

## Health Check

### Get Service Health

**GET** `/health`

Check if backend and LLM services are healthy.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "database": "connected",
  "llm_service": "available",
  "version": "1.0.0",
  "stage": "Stage 1 - Foundation"
}
```

**Example**:
```bash
curl http://localhost:8000/health
```

---

## Rate Limits

**Stage 1**: No rate limits (local development)

**Future Stages**:
- Stage 6: Rate limiting per user/IP
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`

---

## Changelog

### Stage 1 - Foundation (2025-11-18)

**Initial Release**:
- Project CRUD endpoints
- Conversation CRUD endpoints
- Message retrieval and reactions
- SSE streaming chat
- Health check endpoint

**Performance**:
- API response time: 3-17ms (P50)
- SSE first token: 270ms
- SSE total stream: 419ms
- Database: SQLite with WAL mode

**Security**:
- CORS enabled for localhost:3000
- SQL injection prevention (parameterized queries)
- XSS prevention (input sanitization)
- Input validation (Pydantic schemas)

### Stage 2 - Planned Features

- Document upload endpoints
- RAG query endpoints
- Knowledge graph visualization
- Message regeneration
- Message editing

---

## Appendix: Complete Endpoint Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/projects/create` | Create project |
| GET | `/api/projects/{id}` | Get project |
| GET | `/api/projects/{id}/stats` | Get project stats |
| GET | `/api/projects/` | List projects |
| PATCH | `/api/projects/{id}` | Update project |
| DELETE | `/api/projects/{id}` | Delete project |
| POST | `/api/conversations/create` | Create conversation |
| GET | `/api/conversations/{id}` | Get conversation |
| GET | `/api/projects/{id}/conversations` | List conversations |
| PATCH | `/api/conversations/{id}` | Update conversation |
| DELETE | `/api/conversations/{id}` | Delete conversation |
| GET | `/api/messages/{id}` | Get message |
| GET | `/api/conversations/{id}/messages` | List messages |
| PATCH | `/api/messages/{id}/reaction` | Update reaction |
| POST | `/api/chat/stream` | Stream chat (SSE) |
| GET | `/health` | Health check |

---

**Document Version**: 1.0
**Stage**: Stage 1 - Foundation
**Next Update**: After Stage 2 completion (RAG endpoints)
