# Error Handling Guide for GPT-OSS Backend

**Quick Reference**: How to use structured exceptions in API endpoints

---

## Import the Exception Classes

```python
from app.exceptions import (
    ProjectNotFoundError,
    ConversationNotFoundError,
    DocumentNotFoundError,
    StreamSessionNotFoundError,
    ValidationError,
    FileValidationError,
    DatabaseError,
    LLMServiceError,
    LLMTimeoutError,
    FileSystemError,
    handle_database_error
)
```

---

## Common Patterns

### 1. Resource Not Found (404)

**Before**:
```python
project = ProjectService.get_project_by_id(db, project_id)
if not project:
    raise HTTPException(status_code=404, detail="Project not found")
```

**After**:
```python
project = ProjectService.get_project_by_id(db, project_id)
if not project:
    raise ProjectNotFoundError(project_id)
```

**Response**:
```json
{
  "error_code": "PROJECT_NOT_FOUND",
  "message": "Project with ID 123 not found. It may have been deleted.",
  "details": {
    "project_id": 123
  }
}
```

---

### 2. Validation Errors (400)

**Before**:
```python
if not files:
    raise HTTPException(status_code=400, detail="No files provided")
```

**After**:
```python
if not files:
    raise ValidationError("No files provided. Please select at least one file to upload.")
```

**Response**:
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "No files provided. Please select at least one file to upload.",
  "details": {}
}
```

**With Field Context**:
```python
raise ValidationError(
    "Project name is required",
    field="name"
)
```

**Response**:
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Project name is required",
  "details": {
    "field": "name"
  }
}
```

---

### 3. Database Errors (500)

**Before**:
```python
try:
    project = ProjectService.create_project(db, project_data)
    return project
except Exception as e:
    logger.error(f"Failed to create project: {e}")
    raise HTTPException(status_code=500, detail="Failed to create project")
```

**After**:
```python
try:
    project = ProjectService.create_project(db, project_data)
    return project
except Exception as e:
    handle_database_error("create project", e)
```

**Benefits**:
- Automatically logs full exception details
- Returns user-friendly error message
- Includes operation context in response
- Structured details for debugging

**Response**:
```json
{
  "error_code": "DATABASE_ERROR",
  "message": "Database operation failed: create project. Please try again.",
  "details": {
    "operation": "create project",
    "exception_type": "IntegrityError",
    "exception_message": "..."
  }
}
```

---

### 4. File System Errors (500)

**Before**:
```python
if not file_path.exists():
    raise HTTPException(status_code=404, detail="File not found on disk")
```

**After**:
```python
if not file_path.exists():
    raise FileSystemError(
        operation="download document",
        file_path=str(file_path)
    )
```

**Response**:
```json
{
  "error_code": "FILE_SYSTEM_ERROR",
  "message": "File system operation failed: download document. Please try again.",
  "details": {
    "operation": "download document",
    "file_path": "/uploads/1/abc123_report.pdf"
  }
}
```

---

### 5. LLM Service Errors (503)

**Usage**:
```python
from app.exceptions import LLMServiceError, LLMTimeoutError

# Connection error
raise LLMServiceError(
    "LLM service is not available. Please ensure llama.cpp is running.",
    llm_url=settings.LLM_API_URL
)

# Timeout error
raise LLMTimeoutError(timeout_seconds=60)
```

**Responses**:
```json
// Service error
{
  "error_code": "LLM_SERVICE_ERROR",
  "message": "LLM service error: LLM service is not available. Please ensure llama.cpp is running.",
  "details": {
    "llm_url": "http://localhost:18080"
  }
}

// Timeout error
{
  "error_code": "LLM_TIMEOUT",
  "message": "LLM service timed out after 60 seconds. Please try a shorter message or try again later.",
  "details": {
    "timeout_seconds": 60
  }
}
```

---

## All Available Exception Classes

| Exception Class | Status Code | Error Code | Use Case |
|-----------------|-------------|------------|----------|
| `ProjectNotFoundError(project_id)` | 404 | PROJECT_NOT_FOUND | Project not found or soft-deleted |
| `ConversationNotFoundError(conversation_id)` | 404 | CONVERSATION_NOT_FOUND | Conversation not found |
| `DocumentNotFoundError(document_id)` | 404 | DOCUMENT_NOT_FOUND | Document not found |
| `StreamSessionNotFoundError(session_id)` | 404 | STREAM_SESSION_NOT_FOUND | Stream session expired |
| `ValidationError(message, field?)` | 400 | VALIDATION_ERROR | Request validation failed |
| `FileValidationError(filename, reason)` | 400 | FILE_VALIDATION_ERROR | File upload validation failed |
| `DatabaseError(operation, details?)` | 500 | DATABASE_ERROR | Database operation failed |
| `LLMServiceError(message, llm_url?)` | 503 | LLM_SERVICE_ERROR | LLM service communication failed |
| `LLMTimeoutError(timeout_seconds)` | 504 | LLM_TIMEOUT | LLM service timed out |
| `FileSystemError(operation, file_path?)` | 500 | FILE_SYSTEM_ERROR | File system operation failed |

---

## Client-Side Error Handling

### TypeScript Example

```typescript
import { api } from './api';

interface GPTOSSError {
  error_code: string;
  message: string;
  details: Record<string, any>;
}

async function deleteProject(projectId: number) {
  try {
    await api.delete(`/api/projects/${projectId}`);
    toast.success('Project deleted');
  } catch (error: any) {
    const errorData = error.response?.data as GPTOSSError;

    switch (errorData?.error_code) {
      case 'PROJECT_NOT_FOUND':
        toast.error('Project not found. It may have been already deleted.');
        break;

      case 'DATABASE_ERROR':
        toast.error('Database error. Please try again.');
        console.error('Database error details:', errorData.details);
        break;

      default:
        toast.error(errorData?.message || 'An error occurred');
    }
  }
}
```

### Axios Error Interceptor

```typescript
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const errorData = error.response?.data as GPTOSSError;

    if (errorData?.error_code) {
      // Structured error from backend
      console.error(`[${errorData.error_code}] ${errorData.message}`, errorData.details);

      // Log to error tracking service (Sentry, etc.)
      logError({
        code: errorData.error_code,
        message: errorData.message,
        details: errorData.details,
        status: error.response?.status
      });
    }

    return Promise.reject(error);
  }
);
```

---

## Testing Error Responses

### Manual Testing with curl

```bash
# Test 404 error
curl -i http://localhost:8000/api/projects/999999

# Expected response:
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "detail": {
    "error_code": "PROJECT_NOT_FOUND",
    "message": "Project with ID 999999 not found. It may have been deleted.",
    "details": {
      "project_id": 999999
    }
  }
}

# Test validation error
curl -i -X POST http://localhost:8000/api/projects/1/documents/upload \
  -F "files="

# Expected response:
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "detail": {
    "error_code": "VALIDATION_ERROR",
    "message": "No files provided. Please select at least one file to upload.",
    "details": {}
  }
}
```

### Unit Testing

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_project_not_found_error():
    """Test that non-existent project returns structured error"""
    response = client.get("/api/projects/999999")

    assert response.status_code == 404
    error_data = response.json()["detail"]

    assert error_data["error_code"] == "PROJECT_NOT_FOUND"
    assert "999999" in error_data["message"]
    assert error_data["details"]["project_id"] == 999999

def test_validation_error():
    """Test that validation errors return structured error"""
    response = client.post(
        "/api/projects/1/documents/upload",
        files=[]
    )

    assert response.status_code == 400
    error_data = response.json()["detail"]

    assert error_data["error_code"] == "VALIDATION_ERROR"
    assert "No files provided" in error_data["message"]
```

---

## Best Practices

### 1. Always Provide Actionable Error Messages

**Bad**:
```python
raise ValidationError("Invalid input")
```

**Good**:
```python
raise ValidationError(
    "Project name must be between 1 and 100 characters. Current length: 150."
)
```

---

### 2. Include Relevant Context in Details

**Bad**:
```python
raise FileSystemError("File not found")
```

**Good**:
```python
raise FileSystemError(
    operation="download document",
    file_path=str(file_path)
)
```

---

### 3. Use Specific Exception Classes

**Bad**:
```python
raise GPTOSSException(
    status_code=404,
    error_code="NOT_FOUND",
    message="Resource not found"
)
```

**Good**:
```python
raise ProjectNotFoundError(project_id)
```

---

### 4. Log Before Raising (for Database Errors)

**Use the helper function**:
```python
try:
    # database operation
except Exception as e:
    handle_database_error("operation name", e)
    # Automatically logs and raises DatabaseError
```

---

### 5. Don't Expose Internal Details

**Bad**:
```python
raise LLMServiceError(
    f"SQL Error: {sql_query} failed with {exception}"
)
```

**Good**:
```python
handle_database_error("create project", exception)
# Logs full details internally, returns generic message to user
```

---

## Migration Checklist

When adding a new API endpoint, ensure:

- [ ] Import relevant exception classes
- [ ] Replace all `HTTPException` with structured exceptions
- [ ] Use `handle_database_error()` for database operations
- [ ] Provide actionable error messages
- [ ] Include relevant context in `details`
- [ ] Test error responses manually
- [ ] Add unit tests for error cases

---

**Last Updated**: 2025-11-30
**Author**: Backend-Agent
