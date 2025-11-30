# Stage 3: Architecture Document

**Created**: 2025-11-30
**Status**: Phase 1 - Planning

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (SvelteKit)                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐  ┌──────────────────────────────────────────────┐│
│  │ VerticalNav  │  │              Main Content Area               ││
│  │              │  │  ┌────────────────────────────────────────┐  ││
│  │  📁 Projects │  │  │            ProjectsTab                 │  ││
│  │  💬 Chat     │  │  │  ┌─────────────┬──────────────────┐    │  ││
│  │  📄 Docs     │  │  │  │ ProjectList │ ProjectDetails   │    │  ││
│  │  ⚙️ Settings │  │  │  │             │                  │    │  ││
│  │              │  │  │  │ CreateForm  │ ConversationList │    │  ││
│  │              │  │  │  │             │ DocumentList     │    │  ││
│  │              │  │  │  └─────────────┴──────────────────┘    │  ││
│  │              │  │  └────────────────────────────────────────┘  ││
│  └──────────────┘  └──────────────────────────────────────────────┘│
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                      Stores (Svelte)                          │  │
│  │  projects.ts │ conversations.ts │ documents.ts │ ui.ts        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                      API Client (fetch)                       │  │
│  │  projects.ts │ conversations.ts │ documents.ts                │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/REST
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         BACKEND (FastAPI)                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      API Routes                              │   │
│  │  /api/projects │ /api/conversations │ /api/documents        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                    │                                │
│                                    ▼                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      Services                                │   │
│  │  ProjectService │ ConversationService │ DocumentService     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                    │                                │
│                                    ▼                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      Database (SQLite)                       │   │
│  │  projects │ conversations │ messages │ documents             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### Frontend Components

```
src/lib/components/
├── VerticalNav.svelte          # Left icon navigation (existing, modify)
├── tabs/
│   ├── ProjectsTab.svelte      # NEW: Dual-panel projects view
│   ├── ChatTab.svelte          # Existing chat interface
│   ├── DocumentsTab.svelte     # Existing documents view
│   └── SettingsTab.svelte      # Existing settings
├── projects/
│   ├── ProjectList.svelte      # NEW: List of projects with counts
│   ├── ProjectItem.svelte      # NEW: Single project row
│   ├── ProjectDetails.svelte   # NEW: Right panel details
│   ├── CreateProjectForm.svelte # NEW: Form to create project
│   ├── EditProjectForm.svelte  # NEW: Form to edit project
│   ├── DeleteProjectDialog.svelte # NEW: Confirmation modal
│   ├── ProjectContextMenu.svelte # NEW: Right-click menu
│   ├── ColorPicker.svelte      # NEW: Color selection grid
│   └── IconPicker.svelte       # NEW: Icon selection grid
├── chat/
│   ├── ChatHeader.svelte       # Modify: Add project dropdown
│   └── ConversationItem.svelte # Modify: Add right-click menu
└── shared/
    ├── BackButton.svelte       # NEW: "← Back to Projects" button
    └── DragHandle.svelte       # NEW: Drag indicator for reorder
```

### Component Hierarchy

```
+page.svelte
└── VerticalNav
    ├── ProjectsTab (when 📁 selected)
    │   ├── ProjectList
    │   │   ├── ProjectItem (many)
    │   │   │   └── DragHandle
    │   │   └── CreateProjectForm (when creating)
    │   ├── ProjectDetails (when project selected)
    │   │   ├── ConversationList (clickable)
    │   │   └── DocumentList (clickable)
    │   ├── EditProjectForm (modal)
    │   ├── DeleteProjectDialog (modal)
    │   └── ProjectContextMenu (floating)
    │
    ├── ChatTab (when 💬 selected)
    │   └── ChatHeader
    │       └── ProjectDropdown (move feature)
    │
    └── DocumentsTab (when 📄 selected)
```

---

## State Management

### Projects Store (Extended)

```typescript
// src/lib/stores/projects.ts

interface ProjectState {
  projects: Project[];
  selectedProjectId: number | null;
  projectDetails: ProjectDetails | null;
  isLoading: boolean;
  error: string | null;
}

interface Project {
  id: number;
  name: string;
  description: string | null;
  color: string;
  icon: string;
  is_default: boolean;
  conversation_count: number;
  document_count: number;
  sort_order: number;
  last_used_at: string;
  created_at: string;
  updated_at: string;
}

interface ProjectDetails {
  project: Project;
  conversations: ConversationSummary[];
  documents: DocumentSummary[];
}

// Actions
export const projectsStore = {
  // Existing
  loadProjects: async () => {...},
  setCurrentProject: (id: number) => {...},

  // New for Stage 3
  selectProject: (id: number) => {...},
  loadProjectDetails: async (id: number) => {...},
  createProject: async (data: CreateProjectRequest) => {...},
  updateProject: async (id: number, data: UpdateProjectRequest) => {...},
  deleteProject: async (id: number, action: 'move' | 'delete') => {...},
  reorderProjects: async (projectIds: number[]) => {...},
};
```

### UI Store (Navigation State)

```typescript
// src/lib/stores/ui.ts

interface UIState {
  activeTab: 'projects' | 'chat' | 'documents' | 'settings';
  previousTab: string | null;  // For back navigation
  contextMenu: {
    visible: boolean;
    x: number;
    y: number;
    targetId: number | null;
    targetType: 'project' | 'conversation' | null;
  };
}
```

---

## Database Schema Changes

### Projects Table (Modified)

```sql
-- Add new columns to projects table
ALTER TABLE projects ADD COLUMN color VARCHAR(20) DEFAULT 'blue';
ALTER TABLE projects ADD COLUMN icon VARCHAR(20) DEFAULT 'folder';
ALTER TABLE projects ADD COLUMN is_default BOOLEAN DEFAULT FALSE;
ALTER TABLE projects ADD COLUMN sort_order INTEGER DEFAULT 0;

-- Create index for sorting
CREATE INDEX idx_projects_sort_order ON projects(sort_order);

-- Ensure Default project exists
INSERT OR IGNORE INTO projects (id, name, description, color, icon, is_default, sort_order)
VALUES (1, 'Default', 'Default project for quick chats', 'gray', 'folder', TRUE, 0);
```

### Migration Strategy

1. Create Alembic migration for new columns
2. Run migration on startup
3. Check/create Default project on startup
4. Backfill existing projects with default color/icon

---

## API Route Structure

### Backend Routes

```python
# app/api/projects.py

router = APIRouter(prefix="/api/projects", tags=["Projects"])

@router.get("")
async def list_projects(sort: str = "recent") -> ProjectListResponse:
    """List all projects with counts."""

@router.post("/create")
async def create_project(data: ProjectCreate) -> ProjectResponse:
    """Create a new project."""

@router.get("/{project_id}")
async def get_project(project_id: int) -> ProjectResponse:
    """Get single project by ID."""

@router.get("/{project_id}/details")
async def get_project_details(project_id: int) -> ProjectDetailsResponse:
    """Get project with conversations and documents."""

@router.patch("/{project_id}")
async def update_project(project_id: int, data: ProjectUpdate) -> ProjectResponse:
    """Update project fields."""

@router.delete("/{project_id}")
async def delete_project(project_id: int, action: str) -> DeleteResponse:
    """Delete project with move or delete action."""

@router.patch("/reorder")
async def reorder_projects(data: ReorderRequest) -> ReorderResponse:
    """Update project order."""
```

```python
# app/api/conversations.py (extension)

@router.patch("/{conversation_id}/move")
async def move_conversation(conversation_id: int, data: MoveRequest) -> ConversationResponse:
    """Move conversation to different project."""
```

---

## URL Routing (SvelteKit)

### Route Structure

```
/                           → Redirects to /projects or last active tab
/projects                   → Projects tab (list view)
/projects/{id}              → Projects tab with specific project selected
/chat                       → Chat tab (conversation list)
/chat/{conversationId}      → Chat tab with specific conversation open
/documents                  → Documents tab
/settings                   → Settings tab
```

### Navigation Flow

```
User clicks [→] on chat in ProjectDetails:
  1. Update URL to /chat/{conversationId}
  2. Store previousTab = 'projects'
  3. Switch activeTab to 'chat'
  4. Load conversation

User clicks "← Back to Projects":
  1. Check previousTab ('projects')
  2. Navigate to /projects/{lastSelectedProjectId}
  3. Restore projects view
```

---

## Drag & Drop Implementation

### Using svelte-dnd-action

```typescript
// ProjectList.svelte
import { dndzone } from 'svelte-dnd-action';

let items = $projectsStore.projects;

function handleDndConsider(e) {
  items = e.detail.items;
}

function handleDndFinalize(e) {
  items = e.detail.items;
  // Save new order to backend
  projectsStore.reorderProjects(items.map(p => p.id));
}

<div use:dndzone={{items}} on:consider={handleDndConsider} on:finalize={handleDndFinalize}>
  {#each items as project (project.id)}
    <ProjectItem {project} />
  {/each}
</div>
```

---

## Context Menu Implementation

### Using Svelte Stores + Portal

```typescript
// ProjectContextMenu.svelte
<script>
  import { contextMenu } from '$lib/stores/ui';

  function handleEdit() {
    // Open edit form
    contextMenu.close();
  }

  function handleDelete() {
    // Open delete dialog
    contextMenu.close();
  }
</script>

{#if $contextMenu.visible && $contextMenu.targetType === 'project'}
  <div
    class="context-menu"
    style="left: {$contextMenu.x}px; top: {$contextMenu.y}px"
  >
    <button on:click={handleEdit}>Edit</button>
    <button on:click={handleDelete}>Delete</button>
  </div>
{/if}
```

---

## Color & Icon Constants

### Shared Constants File

```typescript
// src/lib/constants/project.ts

export const PROJECT_COLORS = [
  { name: 'red', hex: '#EF4444', label: 'Red' },
  { name: 'orange', hex: '#F97316', label: 'Orange' },
  { name: 'yellow', hex: '#EAB308', label: 'Yellow' },
  { name: 'green', hex: '#22C55E', label: 'Green' },
  { name: 'blue', hex: '#3B82F6', label: 'Blue' },
  { name: 'purple', hex: '#8B5CF6', label: 'Purple' },
  { name: 'gray', hex: '#6B7280', label: 'Gray' },
  { name: 'black', hex: '#1F2937', label: 'Black' },
] as const;

export const PROJECT_ICONS = [
  { name: 'folder', emoji: '📁', label: 'Folder' },
  { name: 'shield', emoji: '🛡️', label: 'Security' },
  { name: 'document', emoji: '📄', label: 'Document' },
  { name: 'chart', emoji: '📊', label: 'Analytics' },
  { name: 'flask', emoji: '🧪', label: 'Research' },
  { name: 'briefcase', emoji: '💼', label: 'Business' },
  { name: 'target', emoji: '🎯', label: 'Goals' },
  { name: 'star', emoji: '⭐', label: 'Favorites' },
] as const;
```

---

## Responsive Design

### Breakpoints

```css
/* Mobile: < 768px */
@media (max-width: 767px) {
  .projects-tab {
    /* Single column - toggle between list and details */
    flex-direction: column;
  }

  .project-list {
    /* Full width when visible */
    width: 100%;
  }

  .project-details {
    /* Full width, shown when project selected */
    width: 100%;
    /* Back button to return to list */
  }
}

/* Tablet: 768px - 1024px */
@media (min-width: 768px) and (max-width: 1024px) {
  .project-list { width: 40%; }
  .project-details { width: 60%; }
}

/* Desktop: > 1024px */
@media (min-width: 1025px) {
  .project-list { width: 300px; }
  .project-details { flex: 1; }
}
```

---

## Testing Strategy

### Unit Tests (Vitest)
- Store actions (create, update, delete, reorder)
- API client functions
- Utility functions (color/icon helpers)

### Component Tests (Playwright)
- ProjectList renders correctly
- CreateProjectForm validation
- ColorPicker/IconPicker selection
- Context menu positioning

### E2E Tests (Playwright)
- Full CRUD workflow
- Move conversation between projects
- Drag & drop reorder
- Navigation with back button
- Responsive layout changes

---

## Security Considerations

1. **CSRF Protection**: All mutations require CSRF token
2. **Input Validation**: Name/description length limits
3. **Authorization**: Projects belong to user (future multi-user)
4. **Default Project**: Cannot be deleted (enforced backend)

---

## Performance Considerations

1. **Lazy Loading**: Load project details only when selected
2. **Optimistic UI**: Update UI before API confirms (reorder, move)
3. **Debounce**: Debounce reorder API calls during drag
4. **Caching**: Cache project list, invalidate on mutations

---

*Architecture document complete. Ready for Super-AI review.*
