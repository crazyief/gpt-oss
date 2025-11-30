# Stage 3 Frontend Implementation Status

**Date**: 2025-11-30
**Agent**: Frontend-Agent
**Status**: Foundation Complete, UI Components Ready for Implementation

---

## Completed Tasks

### TASK-F12: Projects Store Extensions ✅ COMPLETE
**Files Modified**:
- `D:\gpt-oss\frontend\src\lib\stores\projects.ts` - Fully rewritten with new interface
- `D:\gpt-oss\frontend\src\lib\stores\navigation.ts` - Added 'projects' tab type
- `D:\gpt-oss\frontend\src\lib\types\index.ts` - Extended Project interface + new Stage 3 types
- `D:\gpt-oss\frontend\src\lib\config.ts` - Added Stage 3 API endpoints
- `D:\gpt-oss\frontend\src\lib\services\api\projects.ts` - Added getProjectDetails(), reorderProjects()
- `D:\gpt-oss\frontend\src\lib\constants\project.ts` - NEW: Color and icon constants

**New Store Interface**:
```typescript
interface ProjectsState {
  items: Project[];
  selectedProjectId: number | null;  // NEW
  projectDetails: ProjectDetails | null;  // NEW
  isLoading: boolean;
  error: string | null;
}
```

**New Store Actions**:
- `selectProject(id)` - Select project for ProjectsTab
- `setProjectDetails(details)` - Store fetched project details
- `reorderProjects(orderedProjects)` - Update project order
- Updated `updateProject()` to sync projectDetails
- Updated `removeProject()` to clear selection if deleted

---

## Implementation Summary

### Foundation Layer (100% Complete)

#### 1. Type System
**File**: `src/lib/types/index.ts`

Extended `Project` interface with Stage 3 fields:
```typescript
export interface Project {
  // Existing fields
  id: number;
  name: string;
  description: string | null;

  // Stage 3 additions
  color?: string;  // Color name (red, blue, green, etc.)
  icon?: string;  // Icon name (folder, shield, document, etc.)
  is_default?: boolean;  // True for Default project
  sort_order?: number;  // For manual ordering
  document_count?: number;
  last_used_at?: string;
}
```

New types added:
- `ProjectDetails` - Project + conversations + documents
- `ConversationSummary` - For project details view
- `DocumentSummary` - For project details view
- `CreateProjectFormData` - Form data for creating projects
- `UpdateProjectFormData` - Form data for updating projects
- `DeleteProjectAction` - 'move' | 'delete'
- `MoveConversationRequest` - Move conversation to project
- `ReorderProjectsRequest` - Reorder projects

#### 2. Constants
**File**: `src/lib/constants/project.ts` (NEW)

```typescript
export const PROJECT_COLORS = [
  { name: 'red', hex: '#EF4444', label: 'Red' },
  { name: 'orange', hex: '#F97316', label: 'Orange' },
  // ... 8 colors total
];

export const PROJECT_ICONS = [
  { name: 'folder', emoji: '📁', label: 'Folder' },
  { name: 'shield', emoji: '🛡️', label: 'Security' },
  // ... 8 icons total
];
```

Helper functions:
- `getColorHex(name)` - Get color hex by name
- `getIconEmoji(name)` - Get icon emoji by name

#### 3. API Configuration
**File**: `src/lib/config.ts`

Added endpoints:
```typescript
projects: {
  // ... existing endpoints
  update: (id) => `/api/projects/${id}`,  // NEW
  details: (id) => `/api/projects/${id}/details`,  // NEW
  reorder: '/api/projects/reorder'  // NEW
},
conversations: {
  // ... existing endpoints
  move: (id) => `/api/conversations/${id}/move`  // NEW
}
```

#### 4. API Client
**File**: `src/lib/services/api/projects.ts`

Updated functions:
- `updateProject()` - Now accepts color & icon fields
- `getProjectDetails(id)` - NEW: Fetch project with conversations & documents
- `reorderProjects(projectIds)` - NEW: Save manual project order

#### 5. Navigation Store
**File**: `src/lib/stores/navigation.ts`

```typescript
export type Tab = 'projects' | 'chat' | 'documents' | 'settings';
```

---

## Remaining Tasks (UI Components)

### TASK-F01: Add Projects Icon to VerticalNav (P0)
**Status**: NOT STARTED
**Estimated Time**: 30 minutes

**File**: `src/lib/components/VerticalNav.svelte`

**Changes Needed**:
1. Add 'projects' to `tabs` array (currently only has chat, documents, settings)
2. Add folder icon SVG as first tab button
3. Add active state styling
4. Handle click to switch to projects tab
5. Update `handleKeyDown()` to include projects in navigation

**Code Template**:
```svelte
<!-- Projects Tab (add as FIRST button) -->
<button
  type="button"
  class="nav-item"
  class:active={$activeTab === 'projects'}
  on:click={() => handleTabClick('projects')}
  on:keydown={(e) => handleKeyDown(e, 'projects')}
  role="tab"
  id="projects-tab"
  aria-selected={$activeTab === 'projects'}
  aria-controls="projects-panel"
  tabindex={$activeTab === 'projects' ? 0 : -1}
  data-testid="nav-projects"
>
  <!-- Folder icon -->
  <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
  </svg>
  <span class="nav-tooltip">Projects</span>
</button>
```

---

### TASK-F02: Create ProjectsTab Component (P0)
**Status**: NOT STARTED (BLOCKER for F03, F04, F05)
**Estimated Time**: 3 hours

**File**: `src/lib/components/tabs/ProjectsTab.svelte` (NEW)

**Component Structure**:
```svelte
<script lang="ts">
  import ProjectList from '$lib/components/projects/ProjectList.svelte';
  import ProjectDetails from '$lib/components/projects/ProjectDetails.svelte';
  import CreateProjectForm from '$lib/components/projects/CreateProjectForm.svelte';
  import { projects } from '$lib/stores/projects';

  let showCreateForm = false;
</script>

<div class="projects-tab" data-testid="projects-tab">
  <div class="projects-layout">
    <!-- Left Panel: Project List -->
    <aside class="project-list-panel">
      <ProjectList on:create={() => showCreateForm = true} />
    </aside>

    <!-- Right Panel: Project Details or Create Form -->
    <main class="project-details-panel">
      {#if showCreateForm}
        <CreateProjectForm on:cancel={() => showCreateForm = false} />
      {:else if $projects.selectedProjectId}
        <ProjectDetails />
      {:else}
        <!-- Empty state -->
        <div class="empty-state">
          <p>Select a project to view details</p>
        </div>
      {/if}
    </main>
  </div>
</div>

<style>
  .projects-tab {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
  }

  .projects-layout {
    display: flex;
    flex: 1;
    overflow: hidden;
  }

  .project-list-panel {
    width: 300px;
    border-right: 1px solid var(--border-primary);
    overflow-y: auto;
  }

  .project-details-panel {
    flex: 1;
    overflow-y: auto;
    padding: 1.5rem;
  }

  /* Mobile: single column */
  @media (max-width: 768px) {
    .project-list-panel {
      width: 100%;
      border-right: none;
    }

    .project-details-panel {
      display: none; /* Or show as overlay */
    }
  }
</style>
```

---

### TASK-F03: ProjectList Component (P1)
**Status**: NOT STARTED
**Estimated Time**: 2 hours

**File**: `src/lib/components/projects/ProjectList.svelte` (NEW)

**Component Requirements**:
- Display `$sortedProjects` from store
- "+ New Project" button at top
- Each project shows: icon emoji, name, conversation count, document count
- Click to select project (`projects.selectProject(id)`)
- Visual highlight for selected project
- Default project always at bottom

---

### TASK-F04: ProjectDetails Component (P1)
**Status**: NOT STARTED
**Estimated Time**: 2 hours

**File**: `src/lib/components/projects/ProjectDetails.svelte` (NEW)

**Component Requirements**:
- Display selected project info (from `$projects.projectDetails`)
- Show icon (large), name, description
- Edit and Delete buttons
- List conversations with [→] buttons
- List documents with [→] buttons
- Empty states for no conversations/documents
- Call `getProjectDetails()` API when project selected

---

### TASK-F05: CreateProjectForm Component (P1)
**Status**: NOT STARTED
**Estimated Time**: 2 hours

**File**: `src/lib/components/projects/CreateProjectForm.svelte` (NEW)

**Component Requirements**:
- Form fields: name (required), description, color picker, icon picker
- Use `PROJECT_COLORS` and `PROJECT_ICONS` from constants
- Validation: name cannot be empty
- Create button calls `createProject()` API
- Cancel button emits event to close form
- Show loading state during creation
- On success: add to store, select new project, close form

---

### TASK-F06: EditProjectForm Component (P2)
**Status**: NOT STARTED
**Estimated Time**: 1 hour

**File**: `src/lib/components/projects/EditProjectForm.svelte` (NEW)

**Component Requirements**:
- Same as CreateProjectForm but pre-filled with existing data
- Save button calls `updateProject()` API
- Cancel button discards changes

---

### TASK-F07: ProjectContextMenu Component (P2)
**Status**: NOT STARTED
**Estimated Time**: 1.5 hours

**File**: `src/lib/components/projects/ProjectContextMenu.svelte` (NEW)

**Component Requirements**:
- Right-click menu on project items
- Menu options: Edit, Delete
- Position menu at cursor (x, y coordinates)
- Close on click outside
- Hide Delete option for Default project
- Use Svelte portal or absolute positioning

---

### TASK-F08: DeleteProjectDialog Component (P1)
**Status**: NOT STARTED
**Estimated Time**: 1 hour

**File**: `src/lib/components/projects/DeleteProjectDialog.svelte` (NEW)

**Component Requirements**:
- Modal confirmation dialog
- Radio options: "Move to Default" or "Delete All"
- Show conversation and document counts
- Confirm and Cancel buttons
- Call `deleteProject(id, action)` API with chosen action
- On success: remove from store, clear selection

---

### TASK-F09: Move Chat Feature (P1)
**Status**: NOT STARTED
**Estimated Time**: 2 hours

**Files to Modify**:
- `src/lib/components/Sidebar.svelte` - Add context menu to conversations
- `src/lib/components/ChatHeader.svelte` - Add project dropdown

**Component Requirements**:
- Right-click on conversation → "Move to..." submenu
- Header dropdown shows all projects
- Call `/api/conversations/{id}/move` endpoint
- Update conversation's project_id in store
- Show toast confirmation

---

### TASK-F10: Project Drag & Drop Reorder (P2)
**Status**: NOT STARTED
**Estimated Time**: 2 hours

**File**: `src/lib/components/projects/ProjectList.svelte` (modify)

**Component Requirements**:
- Install `svelte-dnd-action` package
- Add drag handle to project items
- Visual feedback during drag
- Call `reorderProjects()` API on drop
- Optimistic UI update
- Default project cannot be dragged (always at bottom)

**Package Installation**:
```bash
npm install svelte-dnd-action
```

---

### TASK-F11: Navigation with Back Button (P1)
**Status**: NOT STARTED
**Estimated Time**: 1.5 hours

**Files to Modify**:
- `src/lib/components/ChatHeader.svelte` - Add "← Back to Projects" button
- `src/lib/components/tabs/DocumentsTab.svelte` - Add back button if navigated from projects

**Component Requirements**:
- Track navigation source in store
- Show back button when navigated from ProjectDetails
- Click restores projects tab and selected project
- Browser back button works (URL routing with SvelteKit)

---

## Integration with +page.svelte

**File**: `src/routes/+page.svelte`

Add ProjectsTab to the main layout:

```svelte
<script lang="ts">
  import ProjectsTab from '$lib/components/tabs/ProjectsTab.svelte';
  // ... existing imports
</script>

<main id="main-content" class="content-area">
  {#if $activeTab === 'projects'}
    <div id="projects-panel" role="tabpanel" aria-labelledby="projects-tab" tabindex="0">
      <ProjectsTab />
    </div>
  {:else if $activeTab === 'chat'}
    <!-- existing ChatTab -->
  {:else if $activeTab === 'documents'}
    <!-- existing DocumentsTab -->
  {:else if $activeTab === 'settings'}
    <!-- existing SettingsTab -->
  {/if}
</main>
```

---

## Backend API Assumptions

The frontend is ready to consume these backend APIs (which may not be implemented yet):

### Existing APIs (assume working)
- `GET /api/projects/list` - Returns projects with counts
- `POST /api/projects/create` - Create project
- `GET /api/projects/{id}` - Get single project

### New APIs (Stage 3, may need backend implementation)
- `PATCH /api/projects/{id}` - Update project (name, description, color, icon)
- `DELETE /api/projects/{id}?action=move|delete` - Delete with move or delete action
- `GET /api/projects/{id}/details` - Get project with conversations & documents
- `PATCH /api/projects/reorder` - Reorder projects (body: `{ project_ids: [3, 1, 2] }`)
- `PATCH /api/conversations/{id}/move` - Move conversation to project (body: `{ project_id: 5 }`)

### Fallback Strategy
If backend APIs are not ready:
- Use mock data in components
- Add `// TODO: Call real API when backend ready` comments
- Implement UI state management first
- Replace mocks with real API calls later

---

## Testing Requirements

### E2E Tests Needed (QA-Agent)
1. **Project CRUD**:
   - Create project with all fields
   - Edit project (name, color, icon)
   - Delete project (both move and delete actions)
   - Default project cannot be deleted

2. **Project Navigation**:
   - Click Projects tab
   - Select project shows details
   - Click [→] on conversation navigates to chat
   - Back button returns to projects

3. **Move Chat**:
   - Move via right-click menu
   - Move via header dropdown
   - Chat appears in new project

4. **Drag Reorder**:
   - Drag project to new position
   - Order persists after refresh
   - Default project stays at bottom

### Component Tests Needed
- `ProjectList` renders projects correctly
- `CreateProjectForm` validates name field
- `ColorPicker` selects color
- `IconPicker` selects icon
- `DeleteProjectDialog` shows correct counts

---

## File Structure Summary

```
frontend/src/lib/
├── constants/
│   └── project.ts ✅ CREATED
├── types/
│   └── index.ts ✅ MODIFIED (extended)
├── config.ts ✅ MODIFIED (added endpoints)
├── stores/
│   ├── projects.ts ✅ REWRITTEN (full Stage 3 support)
│   └── navigation.ts ✅ MODIFIED (added 'projects' tab)
├── services/api/
│   └── projects.ts ✅ MODIFIED (added getProjectDetails, reorderProjects)
└── components/
    ├── VerticalNav.svelte ⏳ TODO (add projects icon)
    ├── tabs/
    │   ├── ProjectsTab.svelte ⏳ TODO (P0 blocker)
    │   ├── ChatTab.svelte (existing)
    │   ├── DocumentsTab.svelte (existing)
    │   └── SettingsTab.svelte (existing)
    └── projects/ ⏳ NEW FOLDER
        ├── ProjectList.svelte ⏳ TODO
        ├── ProjectDetails.svelte ⏳ TODO
        ├── CreateProjectForm.svelte ⏳ TODO
        ├── EditProjectForm.svelte ⏳ TODO
        ├── DeleteProjectDialog.svelte ⏳ TODO
        ├── ProjectContextMenu.svelte ⏳ TODO
        ├── ColorPicker.svelte ⏳ TODO (reusable component)
        └── IconPicker.svelte ⏳ TODO (reusable component)
```

---

## Next Steps

### Immediate Priority (P0 - Blockers)
1. **TASK-F01**: Add Projects icon to VerticalNav (30 min)
2. **TASK-F02**: Create ProjectsTab component skeleton (3 hours)

### High Priority (P1 - Core Features)
3. **TASK-F03**: ProjectList component
4. **TASK-F04**: ProjectDetails component
5. **TASK-F05**: CreateProjectForm component
6. **TASK-F08**: DeleteProjectDialog component
7. **TASK-F09**: Move Chat feature
8. **TASK-F11**: Navigation with Back Button

### Medium Priority (P2 - Enhancements)
9. **TASK-F06**: EditProjectForm component
10. **TASK-F07**: ProjectContextMenu component
11. **TASK-F10**: Drag & Drop reorder

---

## Blockers

### Backend APIs Not Ready
If backend APIs are not implemented yet, frontend can proceed with:
- Mock data in components
- Loading states
- Error handling
- Full UI implementation

Backend can implement APIs in parallel. Once ready, replace mock calls with real API calls.

### No Known Frontend Blockers
All required dependencies are available:
- Svelte/SvelteKit (existing)
- TypeScript (existing)
- Tailwind CSS (existing)
- svelte-dnd-action (needs `npm install`)

---

## Success Criteria

Stage 3 is complete when:
- ✅ All 12 frontend tasks implemented
- ✅ Projects tab visible and functional
- ✅ Can create, edit, delete projects
- ✅ Can move conversations between projects
- ✅ Can navigate from projects to chat/documents
- ✅ Default project cannot be deleted
- ✅ All E2E tests passing
- ✅ Mobile responsive design works
- ✅ Code quality: max 500 lines per .svelte file, 400 lines per .ts file
- ✅ All interactive elements have data-testid attributes

---

**Report Generated**: 2025-11-30
**Next Review**: After Phase 2 (Development) complete
