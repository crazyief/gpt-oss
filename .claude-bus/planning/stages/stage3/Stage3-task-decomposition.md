# Stage 3: Task Decomposition

**Created**: 2025-11-30
**Status**: Phase 1 - Planning
**Total Tasks**: 24 tasks across Backend, Frontend, and Testing

---

## Task Overview by Component

| Component | Tasks | Priority |
|-----------|-------|----------|
| Backend API | 8 | High |
| Frontend UI | 12 | High |
| Testing | 4 | Medium |
| **Total** | **24** | |

---

## Backend Tasks (8)

### TASK-B01: Extend Project Model
**Priority**: P0 (Blocker)
**Assigned**: Backend-Agent
**Effort**: 2 hours

- Add fields to Project model:
  - `color: String` (default: "blue")
  - `icon: String` (default: "folder")
  - `is_default: Boolean` (default: false, prevents deletion when true)
  - `sort_order: Integer` (for manual ordering)
  - `updated_at: DateTime` (for recent sorting)
  - `last_used_at: DateTime` (derived: MAX of conversation/document activity)
- Create Alembic migration
- Update Pydantic schemas
- Note: `last_used_at` is calculated at query time, not stored

### TASK-B02: Default Project Auto-Creation
**Priority**: P0 (Blocker)
**Assigned**: Backend-Agent
**Effort**: 1 hour

- On app startup, ensure "Default" project exists
- If not, create with:
  - name: "Default"
  - description: "Default project for quick chats"
  - is_default: true (new field, prevents deletion)
- Reject DELETE requests for default project (400 error)

### TASK-B03: Project CRUD Extensions
**Priority**: P1
**Assigned**: Backend-Agent
**Effort**: 2 hours

- `PATCH /api/projects/{id}` - Update name, description, color, icon
- `DELETE /api/projects/{id}` with query param:
  - `?action=move` → Move chats/docs to Default
  - `?action=delete` → Delete everything
- Validate cannot delete Default project

### TASK-B04: Project Ordering API
**Priority**: P2
**Assigned**: Backend-Agent
**Effort**: 1 hour

- `PATCH /api/projects/reorder` - Accept array of project IDs in new order
- Update `sort_order` field for each
- Return updated project list

### TASK-B05: Move Conversation API
**Priority**: P1
**Assigned**: Backend-Agent
**Effort**: 1 hour

- `PATCH /api/conversations/{id}/move`
- Request body: `{ "project_id": 123 }`
- Update conversation's project_id
- Return updated conversation

### TASK-B06: Project Details Endpoint
**Priority**: P1
**Assigned**: Backend-Agent
**Effort**: 1 hour

- `GET /api/projects/{id}/details`
- Return:
  - Project info (name, desc, color, icon)
  - Conversations list (id, title, updated_at)
  - Documents list (id, filename, size, type)
  - Counts (chat_count, doc_count)

### TASK-B07: Project List with Counts
**Priority**: P1
**Assigned**: Backend-Agent
**Effort**: 1 hour

- Update `GET /api/projects` to include:
  - conversation_count
  - document_count
  - last_used_at (most recent chat/doc activity)
- Support `?sort=recent` query param

### TASK-B08: Backend Unit Tests
**Priority**: P1
**Assigned**: Backend-Agent
**Effort**: 2 hours

- Test project CRUD extensions
- Test default project protection
- Test move conversation
- Test project ordering
- Test cascade delete vs move

---

## Frontend Tasks (12)

### TASK-F01: Add Projects Icon to VerticalNav
**Priority**: P0 (Blocker)
**Assigned**: Frontend-Agent
**Effort**: 30 min

- Add 📁 folder icon to VerticalNav
- Position: First icon (above Chat)
- Active state styling
- Click navigates to projects view

### TASK-F02: Create ProjectsTab Component
**Priority**: P0 (Blocker)
**Assigned**: Frontend-Agent
**Effort**: 3 hours

- Dual-panel layout (list + details)
- Responsive: collapses on mobile
- Empty state when no projects selected
- Loading states

### TASK-F03: ProjectList Component
**Priority**: P1
**Assigned**: Frontend-Agent
**Effort**: 2 hours

- Display projects with icon, name, counts
- "+ New Project" button at top
- Click to select project
- Visual indicator for selected project
- Default project always visible

### TASK-F04: ProjectDetails Component
**Priority**: P1
**Assigned**: Frontend-Agent
**Effort**: 2 hours

- Show project icon (large), name, description
- Edit button (opens form)
- Delete button (opens confirmation)
- List conversations with [→] buttons
- List documents with [→] buttons

### TASK-F05: CreateProjectForm Component
**Priority**: P1
**Assigned**: Frontend-Agent
**Effort**: 2 hours

- Form fields: name, description, color picker, icon picker
- Color picker: 8 preset colors
- Icon picker: 8 preset icons
- Validation (name required)
- Create and Cancel buttons

### TASK-F06: EditProjectForm Component
**Priority**: P2
**Assigned**: Frontend-Agent
**Effort**: 1 hour

- Same as CreateProjectForm but pre-filled
- Save and Cancel buttons
- Can be triggered from ProjectDetails

### TASK-F07: ProjectContextMenu Component
**Priority**: P2
**Assigned**: Frontend-Agent
**Effort**: 1.5 hours

- Right-click on project shows menu
- Options: Edit, Delete
- Position menu at cursor
- Close on click outside

### TASK-F08: DeleteProjectDialog Component
**Priority**: P1
**Assigned**: Frontend-Agent
**Effort**: 1 hour

- Modal dialog
- Radio options: Move to Default / Delete All
- Warning text with counts
- Confirm and Cancel buttons
- Disable Delete All if only Default project

### TASK-F09: Move Chat Feature
**Priority**: P1
**Assigned**: Frontend-Agent
**Effort**: 2 hours

- Add "Move to..." to chat context menu (in sidebar)
- Add project dropdown in ChatHeader
- Call move API
- Show toast on success
- Update stores

### TASK-F10: Project Drag & Drop Reorder
**Priority**: P2
**Assigned**: Frontend-Agent
**Effort**: 2 hours

- Drag handle on project items
- Visual feedback during drag
- Drop to reorder
- Save new order to backend
- Optimistic UI update

### TASK-F11: Navigation with Back Button
**Priority**: P1
**Assigned**: Frontend-Agent
**Effort**: 1.5 hours

- When clicking [→] on chat/doc, switch tabs
- Add "← Back to Projects" in ChatHeader/DocumentsHeader
- Ensure browser back button works (URL routing)
- Track navigation history

### TASK-F12: Projects Store
**Priority**: P0 (Blocker)
**Assigned**: Frontend-Agent
**Effort**: 1 hour

- Extend existing projects store:
  - Add `selectedProjectId`
  - Add `projectDetails` for selected project
  - Add actions: selectProject, createProject, updateProject, deleteProject, reorderProjects
  - Add moveConversation action

---

## Testing Tasks (4)

### TASK-T01: E2E - Project CRUD
**Priority**: P1
**Assigned**: QA-Agent
**Effort**: 2 hours

- Test create project with all fields
- Test edit project
- Test delete project (both options)
- Test Default project cannot be deleted

### TASK-T02: E2E - Project Navigation
**Priority**: P1
**Assigned**: QA-Agent
**Effort**: 2 hours

- Test clicking Projects tab
- Test selecting project shows details
- Test [→] navigation to chat/document
- Test back navigation (button + browser)

### TASK-T03: E2E - Move Chat
**Priority**: P1
**Assigned**: QA-Agent
**Effort**: 1 hour

- Test move via right-click menu
- Test move via header dropdown
- Test chat appears in new project
- Test chat removed from old project

### TASK-T04: E2E - Drag Reorder
**Priority**: P2
**Assigned**: QA-Agent
**Effort**: 1 hour

- Test drag project to new position
- Test order persists after refresh
- Test Default project position

---

## Task Dependencies

```
TASK-B01 (Model) ──┬──→ TASK-B02 (Default) ──→ TASK-B03 (CRUD)
                   │
                   ├──→ TASK-B04 (Ordering)
                   │
                   └──→ TASK-F12 (Store) ──┬──→ TASK-F01 (Nav)
                                           │
                                           ├──→ TASK-F02 (Tab) ──→ TASK-F03 (List)
                                           │                   └──→ TASK-F04 (Details)
                                           │
                                           └──→ TASK-F05 (Create) ──→ TASK-F06 (Edit)
```

---

## Development Phases

### Phase 2a: Core Structure (Day 1-2)
- TASK-B01: Extend Project Model
- TASK-B02: Default Project Auto-Creation
- TASK-F12: Projects Store
- TASK-F01: Add Projects Icon
- TASK-F02: Create ProjectsTab Component

### Phase 2b: CRUD Operations (Day 2-3)
- TASK-B03: Project CRUD Extensions
- TASK-B06: Project Details Endpoint
- TASK-B07: Project List with Counts
- TASK-F03: ProjectList Component
- TASK-F04: ProjectDetails Component
- TASK-F05: CreateProjectForm Component
- TASK-F08: DeleteProjectDialog Component

### Phase 2c: Advanced Features (Day 3-4)
- TASK-B04: Project Ordering API
- TASK-B05: Move Conversation API
- TASK-F06: EditProjectForm Component
- TASK-F07: ProjectContextMenu Component
- TASK-F09: Move Chat Feature
- TASK-F10: Project Drag & Drop
- TASK-F11: Navigation with Back

### Phase 2d: Testing & Polish (Day 4-5)
- TASK-B08: Backend Unit Tests
- TASK-T01: E2E Project CRUD
- TASK-T02: E2E Navigation
- TASK-T03: E2E Move Chat
- TASK-T04: E2E Drag Reorder

---

## Estimated Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| Phase 2a | 1.5 days | 5 tasks (foundation) |
| Phase 2b | 1.5 days | 7 tasks (CRUD) |
| Phase 2c | 1.5 days | 7 tasks (features) |
| Phase 2d | 1 day | 5 tasks (testing) |
| **Total** | **5.5 days** | **24 tasks** |

---

*Task decomposition complete. Ready for Super-AI review.*
