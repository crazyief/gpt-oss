# Stage 3: API Contracts

**Created**: 2025-11-30
**Status**: Phase 1 - Planning
**Base URL**: `/api`

---

## Summary of Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/projects` | List all projects with counts |
| POST | `/projects/create` | Create new project |
| GET | `/projects/{id}` | Get project by ID |
| GET | `/projects/{id}/details` | Get project with chats & docs |
| PATCH | `/projects/{id}` | Update project |
| DELETE | `/projects/{id}` | Delete project |
| PATCH | `/projects/reorder` | Reorder projects |
| PATCH | `/conversations/{id}/move` | Move chat to project |

---

## Endpoint Details

### 1. GET /projects

**Description**: List all projects with conversation and document counts.

**Query Parameters**:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| sort | string | "recent" | Sort order: "recent", "name", "manual" |

**Response** (200 OK):
```json
{
  "projects": [
    {
      "id": 1,
      "name": "Default",
      "description": "Default project for quick chats",
      "color": "gray",
      "icon": "folder",
      "is_default": true,
      "conversation_count": 5,
      "document_count": 0,
      "sort_order": 0,
      "last_used_at": "2025-11-30T10:00:00Z",
      "created_at": "2025-11-01T00:00:00Z",
      "updated_at": "2025-11-30T10:00:00Z"
    },
    {
      "id": 2,
      "name": "Security Audit",
      "description": "IEC 62443 compliance analysis",
      "color": "blue",
      "icon": "shield",
      "is_default": false,
      "conversation_count": 3,
      "document_count": 12,
      "sort_order": 1,
      "last_used_at": "2025-11-30T09:30:00Z",
      "created_at": "2025-11-15T10:00:00Z",
      "updated_at": "2025-11-30T09:30:00Z"
    }
  ],
  "total": 2
}
```

---

### 2. POST /projects/create

**Description**: Create a new project.

**Request Body**:
```json
{
  "name": "My New Project",
  "description": "Optional description",
  "color": "blue",
  "icon": "folder"
}
```

**Validation**:
- `name`: Required, 1-100 characters
- `description`: Optional, max 500 characters
- `color`: Optional, one of: "red", "orange", "yellow", "green", "blue", "purple", "gray", "black"
- `icon`: Optional, one of: "folder", "shield", "document", "chart", "flask", "briefcase", "target", "star"

**Response** (201 Created):
```json
{
  "id": 3,
  "name": "My New Project",
  "description": "Optional description",
  "color": "blue",
  "icon": "folder",
  "is_default": false,
  "conversation_count": 0,
  "document_count": 0,
  "sort_order": 2,
  "created_at": "2025-11-30T10:15:00Z",
  "updated_at": "2025-11-30T10:15:00Z"
}
```

**Errors**:
- 400: Invalid request body (name too long, invalid color, etc.)
- 409: Project with same name already exists

---

### 3. GET /projects/{id}

**Description**: Get a single project by ID.

**Response** (200 OK):
```json
{
  "id": 2,
  "name": "Security Audit",
  "description": "IEC 62443 compliance analysis",
  "color": "blue",
  "icon": "shield",
  "is_default": false,
  "conversation_count": 3,
  "document_count": 12,
  "sort_order": 1,
  "created_at": "2025-11-15T10:00:00Z",
  "updated_at": "2025-11-30T09:30:00Z"
}
```

**Errors**:
- 404: Project not found

---

### 4. GET /projects/{id}/details

**Description**: Get project with its conversations and documents.

**Response** (200 OK):
```json
{
  "project": {
    "id": 2,
    "name": "Security Audit",
    "description": "IEC 62443 compliance analysis",
    "color": "blue",
    "icon": "shield",
    "is_default": false,
    "created_at": "2025-11-15T10:00:00Z",
    "updated_at": "2025-11-30T09:30:00Z"
  },
  "conversations": [
    {
      "id": 10,
      "title": "Zone analysis discussion",
      "message_count": 15,
      "created_at": "2025-11-20T10:00:00Z",
      "updated_at": "2025-11-30T09:00:00Z"
    },
    {
      "id": 11,
      "title": "CR 2.11 requirements",
      "message_count": 8,
      "created_at": "2025-11-22T14:00:00Z",
      "updated_at": "2025-11-29T16:00:00Z"
    }
  ],
  "documents": [
    {
      "id": 5,
      "original_filename": "IEC62443-4-2.pdf",
      "file_size": 2048576,
      "file_type": "pdf",
      "uploaded_at": "2025-11-15T10:30:00Z"
    },
    {
      "id": 6,
      "original_filename": "compliance_checklist.xlsx",
      "file_size": 51200,
      "file_type": "xlsx",
      "uploaded_at": "2025-11-16T11:00:00Z"
    }
  ],
  "conversation_count": 2,
  "document_count": 2
}
```

**Errors**:
- 404: Project not found

---

### 5. PATCH /projects/{id}

**Description**: Update project fields.

**Request Body** (all fields optional):
```json
{
  "name": "Updated Name",
  "description": "Updated description",
  "color": "green",
  "icon": "chart"
}
```

**Response** (200 OK):
```json
{
  "id": 2,
  "name": "Updated Name",
  "description": "Updated description",
  "color": "green",
  "icon": "chart",
  "is_default": false,
  "conversation_count": 3,
  "document_count": 12,
  "sort_order": 1,
  "created_at": "2025-11-15T10:00:00Z",
  "updated_at": "2025-11-30T10:20:00Z"
}
```

**Errors**:
- 400: Invalid request body
- 400: Cannot modify Default project's is_default flag
- 404: Project not found
- 409: Project with same name already exists

---

### 6. DELETE /projects/{id}

**Description**: Delete a project with options for handling contents.

**Query Parameters**:
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| action | string | Yes | "move" (to Default) or "delete" (permanently) |

**Examples**:
- `DELETE /projects/2?action=move` → Moves chats/docs to Default, deletes project
- `DELETE /projects/2?action=delete` → Deletes everything permanently

**Response** (200 OK):
```json
{
  "message": "Project deleted successfully",
  "action": "move",
  "moved_conversations": 3,
  "moved_documents": 12
}
```

or

```json
{
  "message": "Project deleted successfully",
  "action": "delete",
  "deleted_conversations": 3,
  "deleted_documents": 12
}
```

**Errors**:
- 400: Missing action parameter
- 400: Invalid action (not "move" or "delete")
- 400: Cannot delete Default project
- 404: Project not found

---

### 7. PATCH /projects/reorder

**Description**: Update the order of projects.

**Request Body**:
```json
{
  "project_ids": [3, 2, 1]
}
```

The array represents the new order (first = top of list).
Note: Default project (id=1) position can be included but typically stays at consistent position.

**Response** (200 OK):
```json
{
  "message": "Projects reordered successfully",
  "projects": [
    { "id": 3, "name": "Project C", "sort_order": 0 },
    { "id": 2, "name": "Project B", "sort_order": 1 },
    { "id": 1, "name": "Default", "sort_order": 2 }
  ]
}
```

**Errors**:
- 400: Invalid project_ids (empty, contains non-existent IDs)
- 400: Missing some project IDs (all must be included)

---

### 8. PATCH /conversations/{id}/move

**Description**: Move a conversation to a different project.

**Request Body**:
```json
{
  "project_id": 3
}
```

**Response** (200 OK):
```json
{
  "id": 10,
  "title": "Zone analysis discussion",
  "project_id": 3,
  "message_count": 15,
  "created_at": "2025-11-20T10:00:00Z",
  "updated_at": "2025-11-30T10:25:00Z"
}
```

**Errors**:
- 400: Invalid project_id
- 404: Conversation not found
- 404: Target project not found

---

## Data Models (Updated)

### Project Model
```python
class Project(Base):
    __tablename__ = "projects"

    id: int                    # Primary key
    name: str                  # Project name (required, unique)
    description: str | None    # Optional description
    color: str                 # Color code (default: "blue")
    icon: str                  # Icon name (default: "folder")
    is_default: bool           # True for Default project only
    sort_order: int            # Manual ordering (0 = first)
    created_at: datetime       # Creation timestamp
    updated_at: datetime       # Last update timestamp

    # Relationships
    conversations: List[Conversation]
    documents: List[Document]
```

### Available Colors
```python
VALID_COLORS = [
    "red",      # #EF4444
    "orange",   # #F97316
    "yellow",   # #EAB308
    "green",    # #22C55E
    "blue",     # #3B82F6
    "purple",   # #8B5CF6
    "gray",     # #6B7280
    "black"     # #1F2937
]
```

### Available Icons
```python
VALID_ICONS = [
    "folder",    # 📁 Default folder
    "shield",    # 🛡️ Security
    "document",  # 📄 Documents
    "chart",     # 📊 Analytics
    "flask",     # 🧪 Research
    "briefcase", # 💼 Business
    "target",    # 🎯 Goals
    "star"       # ⭐ Favorites
]
```

---

## CSRF Token Handling

All mutating endpoints (POST, PATCH, DELETE) require CSRF token:
- Header: `X-CSRF-Token: <token>`
- Token obtained from: `GET /api/csrf-token`

---

## Error Response Format

All errors follow this format:
```json
{
  "detail": "Error message here"
}
```

Common HTTP status codes:
- 400: Bad Request (validation error)
- 404: Not Found
- 409: Conflict (duplicate name)
- 500: Internal Server Error

---

*API contracts complete. Ready for Super-AI review.*
