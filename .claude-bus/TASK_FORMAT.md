# Task Format Specification

## Task File Structure
Each task is a JSON file in `.claude-bus/tasks/` with this format:

```json
{
  "id": "task-001",
  "type": "development|planning|review|deploy",
  "title": "Brief description",
  "description": "Detailed requirements",
  "assignee": "PM|Super|Backend|Frontend|QA|Doc",
  "status": "pending|in-progress|completed|blocked",
  "priority": "high|medium|low",
  "dependencies": ["task-id-1", "task-id-2"],
  "created_at": "2024-11-15T10:00:00Z",
  "updated_at": "2024-11-15T10:00:00Z",
  "context": {
    "files": ["file paths relevant to task"],
    "requirements": ["specific requirements"],
    "acceptance_criteria": ["what defines completion"]
  },
  "result": {
    "output": "Task completion details",
    "files_created": ["list of created files"],
    "files_modified": ["list of modified files"]
  }
}
```

## Agent Communication Protocol

### Request Help
Create file in `.claude-bus/help/request-{timestamp}.json`:
```json
{
  "from": "agent-name",
  "type": "technical|planning|review",
  "urgency": "high|medium|low",
  "problem": "Description of the problem",
  "context": "Relevant context",
  "attempted_solutions": ["what was tried"]
}
```

### Code Storage
Save code in `.claude-bus/code/{feature}/` for agent collaboration.

### Event Logging
Append to `.claude-bus/events.jsonl`:
```json
{"timestamp": "ISO8601", "agent": "name", "action": "task_started|task_completed|help_requested", "details": {}}
```