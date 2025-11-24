# GPT-OSS User Manual

**Version**: Stage 1 - Foundation
**Last Updated**: 2025-11-18
**Target Audience**: End users, testers, project managers

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Creating Projects](#creating-projects)
4. [Managing Conversations](#managing-conversations)
5. [Chat Interface](#chat-interface)
6. [Message Features](#message-features)
7. [Troubleshooting](#troubleshooting)
8. [Keyboard Shortcuts](#keyboard-shortcuts)
9. [FAQ](#faq)

---

## Introduction

GPT-OSS is a local AI knowledge assistant system built with LightRAG for cybersecurity document analysis. The system provides:

- **Privacy-first**: All processing happens locally on your machine
- **Chat interface**: Natural language interaction with AI assistant
- **Project organization**: Separate contexts for different topics
- **Conversation history**: Full chat history with search capabilities
- **Source transparency**: All AI responses include citations (future stages)

### Key Features (Stage 1)

- Create and manage multiple projects
- Start conversations within projects
- Real-time chat with local LLM (Mistral Small 24B)
- SSE streaming responses (token-by-token)
- Message reactions (thumbs up/down)
- Conversation search and filtering
- Markdown rendering with syntax highlighting

---

## Getting Started

### Prerequisites

Before using GPT-OSS, ensure all services are running:

1. **Backend API**: http://localhost:8000
2. **LLM Service**: http://localhost:8080
3. **Frontend**: http://localhost:3000 (when using dev server)

### Verify Services

Check service health:

```bash
# Backend health check
curl http://localhost:8000/health

# LLM service health check
curl http://localhost:8080/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "llm_service": "available"
}
```

### First-Time Setup

1. **Start all services** (see Setup Guide for details)
2. **Open frontend** in your browser: http://localhost:3000
3. **Create your first project** using the sidebar
4. **Start chatting!**

---

## Creating Projects

Projects are top-level containers for organizing related conversations.

### Create a New Project

**Via UI** (when frontend is running):
1. Click the **"New Project"** button in the sidebar
2. Enter project name (e.g., "IEC 62443 Analysis")
3. Add optional description
4. Click **"Create"**

**Via API**:
```bash
curl -X POST http://localhost:8000/api/projects/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "IEC 62443 Analysis",
    "description": "Security standards compliance review"
  }'
```

### View Project Details

**Via UI**:
- Click on a project in the sidebar to view conversations
- Project name and description shown at the top

**Via API**:
```bash
# Get project by ID
curl http://localhost:8000/api/projects/1

# Get project stats
curl http://localhost:8000/api/projects/1/stats
```

Response includes:
- Project name, description, creation date
- Total conversations count
- Total messages count
- Last activity timestamp

### Update Project

**Via API**:
```bash
curl -X PATCH http://localhost:8000/api/projects/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Project Name",
    "description": "Updated description"
  }'
```

### Delete Project

**Warning**: Deleting a project will CASCADE delete all conversations and messages.

**Via API**:
```bash
curl -X DELETE http://localhost:8000/api/projects/1
```

---

## Managing Conversations

Conversations are chat sessions within a project.

### Create a New Conversation

**Via UI**:
1. Select a project from the sidebar
2. Click **"New Conversation"** button
3. Enter conversation title (e.g., "CR 2.11 Analysis")
4. Click **"Create"**

**Via API**:
```bash
curl -X POST http://localhost:8000/api/conversations/create \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "title": "CR 2.11 Analysis"
  }'
```

### Switch Between Conversations

**Via UI**:
- Click on any conversation in the project's conversation list
- Active conversation is highlighted

### View Conversation Messages

**Via API**:
```bash
# Get all messages in conversation
curl http://localhost:8000/api/conversations/1/messages

# Get conversation details
curl http://localhost:8000/api/conversations/1
```

### Update Conversation Title

**Via API**:
```bash
curl -X PATCH http://localhost:8000/api/conversations/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Conversation Title"
  }'
```

### Delete Conversation

**Warning**: Deleting a conversation will CASCADE delete all messages.

**Via API**:
```bash
curl -X DELETE http://localhost:8000/api/conversations/1
```

---

## Chat Interface

### Sending Messages

**Via UI**:
1. Select an active conversation
2. Type your message in the text input box at the bottom
3. Press **Enter** or click **"Send"** button

**Via API (SSE Streaming)**:
```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": 1,
    "message": "What is IEC 62443-4-2 CR 2.11?"
  }'
```

### Understanding SSE Streaming

GPT-OSS uses **Server-Sent Events (SSE)** for real-time streaming responses.

**Benefits**:
- Token-by-token streaming (see response as it's generated)
- Low latency (first token in ~270ms)
- Cancellable (stop generation mid-stream)

**Event Types**:

1. **Token Event** (most frequent):
   ```json
   {
     "type": "token",
     "token": "The",
     "message_id": 42,
     "session_id": "abc123"
   }
   ```

2. **Complete Event** (when done):
   ```json
   {
     "type": "complete",
     "message_id": 42,
     "token_count": 150,
     "completion_time_ms": 1250
   }
   ```

3. **Error Event** (on failure):
   ```json
   {
     "type": "error",
     "error": "LLM service unavailable",
     "error_type": "service_error"
   }
   ```

### Message Display

**User Messages**:
- Displayed on the right side (if UI uses that pattern)
- Your username or avatar shown
- Timestamp displayed

**Assistant Messages**:
- Displayed on the left side
- AI assistant icon shown
- Markdown-formatted content
- Code blocks with syntax highlighting
- Token count and generation time shown

### Markdown Support

GPT-OSS supports full Markdown formatting:

**Headers**:
```markdown
# Heading 1
## Heading 2
### Heading 3
```

**Lists**:
```markdown
- Bullet point 1
- Bullet point 2

1. Numbered item 1
2. Numbered item 2
```

**Code Blocks**:
````markdown
```python
def hello_world():
    print("Hello, world!")
```
````

**Emphasis**:
```markdown
**Bold text**
*Italic text*
~~Strikethrough~~
```

**Links**:
```markdown
[Link text](https://example.com)
```

**Tables**:
```markdown
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
```

---

## Message Features

### Message Reactions

**Add Reaction** (Via API):
```bash
curl -X PATCH http://localhost:8000/api/messages/42/reaction \
  -H "Content-Type: application/json" \
  -d '{
    "reaction": "thumbs_up"
  }'
```

**Available Reactions**:
- `thumbs_up` - Like this message
- `thumbs_down` - Dislike this message
- `null` - Remove reaction

**Remove Reaction**:
```bash
curl -X PATCH http://localhost:8000/api/messages/42/reaction \
  -H "Content-Type: application/json" \
  -d '{
    "reaction": null
  }'
```

### Message Regeneration (Future Feature)

**Planned for Stage 2**:
- Click "Regenerate" button on assistant messages
- Creates new response with same prompt
- Preserves message history (tree structure)

### Message Editing (Future Feature)

**Planned for Stage 2**:
- Edit user messages after sending
- Creates new conversation branch
- Original message preserved

---

## Troubleshooting

### Chat Not Responding

**Problem**: Message sent but no response appears

**Possible Causes**:
1. LLM service is down
2. Network connection lost
3. Backend API crashed

**Solutions**:

1. **Check LLM service**:
   ```bash
   curl http://localhost:8080/health
   ```
   If unhealthy: restart llama.cpp service

2. **Check backend logs**:
   ```bash
   docker-compose logs backend
   ```

3. **Restart services**:
   ```bash
   docker-compose restart backend llama
   ```

### Slow Response Times

**Problem**: First token takes >2 seconds to arrive

**Possible Causes**:
1. GPU memory insufficient
2. Model not loaded in VRAM
3. CPU-only mode (very slow)

**Solutions**:

1. **Check GPU status**:
   ```bash
   nvidia-smi
   ```

2. **Reduce context length** in `docker-compose.yml`:
   ```yaml
   command:
     - -c 16384  # Reduce from 32768
   ```

3. **Reduce GPU layers** (if memory limited):
   ```yaml
   command:
     - -ngl 50  # Reduce from 99
   ```

### Messages Not Saving

**Problem**: Messages disappear after refresh

**Possible Causes**:
1. Database connection lost
2. Transaction rollback
3. Disk full

**Solutions**:

1. **Check database file**:
   ```bash
   ls -lh data/gpt_oss.db
   ```

2. **Check disk space**:
   ```bash
   df -h
   ```

3. **Check backend logs** for SQL errors:
   ```bash
   docker-compose logs backend | grep -i "sql"
   ```

### CORS Errors

**Problem**: Frontend shows "CORS policy blocked" errors

**Possible Causes**:
1. Frontend running on non-localhost domain
2. Backend CORS not configured for frontend origin

**Solutions**:

1. **Verify frontend URL** matches CORS_ORIGINS in `backend/app/config.py`:
   ```python
   CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
   ```

2. **Add custom origin** via environment variable:
   ```bash
   export CORS_ORIGINS="http://localhost:3000,http://192.168.1.100:3000"
   docker-compose restart backend
   ```

---

## Keyboard Shortcuts

**Note**: Keyboard shortcuts are implemented in the frontend UI.

### Chat Interface

| Shortcut | Action |
|----------|--------|
| `Enter` | Send message (when input focused) |
| `Shift+Enter` | New line in message input |
| `Ctrl+K` or `Cmd+K` | Focus search box (planned) |
| `Esc` | Cancel message generation (planned) |

### Navigation

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` or `Cmd+N` | New conversation (planned) |
| `Ctrl+/` or `Cmd+/` | Toggle sidebar (planned) |
| `Up/Down` | Navigate conversation list (planned) |

---

## FAQ

### Q: Can I use GPT-OSS offline?

**A**: Yes! GPT-OSS runs entirely locally. Once all services are started, no internet connection is required. The LLM model, databases, and backend all run on your machine.

### Q: How much disk space does GPT-OSS require?

**A**: Minimum requirements:
- **LLM Model**: 20-30 GB (Mistral Small 24B Q6_K)
- **Docker Images**: 5-10 GB
- **Database**: Grows with usage (start at ~1 MB)
- **Total**: ~50 GB recommended

### Q: What GPU is required?

**A**: Recommended GPUs:
- **RTX 4070 or better** (8GB+ VRAM) - Good performance
- **RTX 5090** (32GB VRAM) - Excellent performance
- **No GPU**: CPU-only mode works but is 10-20x slower

### Q: Can I switch to a different LLM model?

**A**: Yes! Edit `docker-compose.yml` and change the llama service model path:
```yaml
command:
  - --model
  - /models/your-model-name.gguf
```

Restart the llama service:
```bash
docker-compose restart llama
```

### Q: How do I backup my data?

**A**: Backup these directories:
```bash
# Database (all projects, conversations, messages)
cp -r data/ backup/data/

# Uploaded documents (future stages)
cp -r uploads/ backup/uploads/

# RAG data (vector embeddings, knowledge graphs - future stages)
cp -r rag_data/ backup/rag_data/
```

### Q: Can multiple users use GPT-OSS simultaneously?

**A**: Stage 1 is single-user. Multi-user support is planned for Stage 6 with:
- User authentication
- Per-user projects
- Access control

### Q: How do I upgrade from SQLite to PostgreSQL?

**A**: See Setup Guide for PostgreSQL migration instructions. Summary:
1. Export SQLite data
2. Uncomment postgres service in docker-compose.yml
3. Update DATABASE_URL in backend config
4. Import data to PostgreSQL
5. Restart backend

### Q: Where can I find API documentation?

**A**: See `docs/api-documentation.md` or visit http://localhost:8000/docs for interactive Swagger UI.

### Q: How do I report bugs?

**A**: Create issues in `.claude-bus/notifications/user-alerts.jsonl` or contact your system administrator.

---

## Appendix: File Locations

### Database
- **SQLite**: `./data/gpt_oss.db`
- **WAL files**: `./data/gpt_oss.db-wal`, `./data/gpt_oss.db-shm`

### Logs
- **Backend**: `docker-compose logs backend`
- **LLM Service**: `docker-compose logs llama`
- **All Services**: `docker-compose logs -f`

### Configuration
- **Backend Config**: `backend/app/config.py`
- **Docker Compose**: `docker-compose.yml`
- **Frontend Config**: `frontend/src/lib/config.ts` (when implemented)

---

**Document Version**: 1.0
**Stage**: Stage 1 - Foundation
**Next Update**: After Stage 2 completion (RAG features)
