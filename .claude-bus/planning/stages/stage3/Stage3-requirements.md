# Stage 3: Project Management UI - Requirements

**Created**: 2025-11-30
**Status**: Phase 1 - Planning
**Owner**: PM-Architect-Agent

---

## Overview

Stage 3 focuses on enhancing the Project Management UI with a dual-panel interface, allowing users to organize their work into projects with associated chats and documents.

## User Stories

### US-001: Project Creation
> As a user, I want to create a new project with a name, description, color, and icon so I can organize my work visually.

### US-002: Default Project
> As a user, I want a Default Project that always exists so I can start chatting immediately without setup.

### US-003: Project Navigation
> As a user, I want to click a Projects folder icon in the left nav to see all my projects in a dual-panel view.

### US-004: View Project Details
> As a user, I want to click a project and see its description, conversations, and documents in the right panel.

### US-005: Navigate to Chat/Document
> As a user, I want to click [→] on a chat or document to open it, with easy back navigation.

### US-006: Move Chat Between Projects
> As a user, I want to move a chat from one project to another using right-click menu or header dropdown.

### US-007: Delete Project
> As a user, I want to delete a project and choose whether to move contents to Default or delete everything.

### US-008: Rename/Edit Project
> As a user, I want to rename a project inline (quick) or edit all fields in a form.

### US-009: Reorder Projects
> As a user, I want my projects sorted by recent use, but also able to drag-reorder to pin favorites.

---

## Design Decisions (User Approved)

| # | Decision | Choice |
|---|----------|--------|
| 1 | Project Creation UI | Inline form in right panel |
| 2 | Default Project | Always exists, cannot delete |
| 3 | Moving Chats | Right-click menu + Header dropdown |
| 4 | Document Scope | Documents tied to Project only |
| 5 | Navigation [→] | Switch tab + Easy back (browser + UI arrow) |
| 6 | Project Fields | Name + Description + Color + Icon |
| 7 | Delete Project | Let user choose (move to Default or delete all) |
| 8 | Project Order | Recent first + drag to reorder |
| 9 | Rename Project | Inline edit + Full edit form |

---

## UI Wireframes

### Main Layout with Projects Tab
```
┌──┬────────────────────────────────────────────┐
│📁│ PROJECTS                                    │
│💬│ ┌──────────────┬───────────────────────────┐│
│📄│ │ + New Project│ 📁 Selected Project       ││
│⚙️│ │              │                           ││
│  │ │ 📁 Project A◀│ Description:              ││
│  │ │    5💬 12📄  │ "User's description..."   ││
│  │ │              │                           ││
│  │ │ 📁 Project B │ CONVERSATIONS (5)         ││
│  │ │    3💬 8📄   │ 💬 Chat title 1    [→]   ││
│  │ │              │ 💬 Chat title 2    [→]   ││
│  │ │ 📁 Default   │                           ││
│  │ │    2💬 0📄   │ DOCUMENTS (12)            ││
│  │ │              │ 📄 filename.pdf    [→]   ││
│  │ └──────────────┴───────────────────────────┘│
└──┴────────────────────────────────────────────┘
```

### Create Project Form (Right Panel)
```
┌──────────────────────────────────────────────┐
│  CREATE NEW PROJECT                          │
│                                              │
│  Name:                                       │
│  [________________________________]          │
│                                              │
│  Description:                                │
│  [________________________________]          │
│  [________________________________]          │
│                                              │
│  Color:                                      │
│  🔴 🟠 🟡 🟢 🔵 🟣 ⚫ ⚪                      │
│                                              │
│  Icon:                                       │
│  📁 🔒 📋 🏭 🔬 💼 📊 🎯                      │
│                                              │
│  [Cancel]                    [Create Project]│
└──────────────────────────────────────────────┘
```

### Right-Click Menu on Chat
```
💬 Chat Title  [right-click]
               ┌─────────────────┐
               │ Open            │
               │ ─────────────── │
               │ Move to...    → │ → 📁 Default
               │                 │   📁 Project A
               │                 │   📁 Project B
               │ ─────────────── │
               │ Rename          │
               │ Delete          │
               └─────────────────┘
```

### Chat Header with Project Dropdown
```
┌─────────────────────────────────────────────────┐
│ ← Back  │  💬 Chat Title    📁 Project A ▼     │
│         │                   ┌────────────────┐  │
│         │                   │ 📁 Default     │  │
│         │                   │ 📁 Project A ✓ │  │
│         │                   │ 📁 Project B   │  │
│         │                   └────────────────┘  │
├─────────────────────────────────────────────────┤
│  (chat messages)                                │
└─────────────────────────────────────────────────┘
```

### Delete Project Dialog
```
┌─────────────────────────────────────────────────┐
│  ⚠️ Delete "Project A"?                         │
│                                                 │
│  This project has 3 chats and 5 documents.      │
│                                                 │
│  ○ Move everything to Default Project           │
│  ○ Delete everything permanently                │
│                                                 │
│  [Cancel]                         [Confirm]     │
└─────────────────────────────────────────────────┘
```

---

## Functional Requirements

### FR-001: Projects Tab in Navigation
- Add 📁 icon to VerticalNav component
- Clicking opens the Projects dual-panel view
- Icon should indicate active state when selected

### FR-002: Project List Panel (Left)
- Display all projects with icon, name, chat count, doc count
- **Default project always appears at the END of the list and CANNOT be reordered**
- "+ New Project" button at top
- Click to select and show details in right panel
- Right-click for context menu (rename, delete) - not available for Default project delete
- Drag to reorder user-created projects (persisted to backend)
- **Sort Mode**: When sorted by "recent", projects ordered by last activity; when "manual", user drag order applies

### FR-003: Project Details Panel (Right)
- Show project icon, name, description
- Edit button to open edit form
- List of conversations with [→] buttons
- List of documents with [→] buttons
- Empty state when no chats/docs

### FR-004: Create Project Flow
- Click "+ New Project" → form appears in right panel
- Required: Name
- Optional: Description, Color, Icon (defaults provided)
- Cancel returns to previous view
- Create saves and selects new project

### FR-005: Edit Project Flow
- Double-click name for inline rename
- Click "Edit" button for full form (name, desc, color, icon)
- Save updates project
- Cancel discards changes

### FR-006: Delete Project Flow
- Right-click → Delete (or delete button)
- Confirmation dialog with options:
  - Move contents to Default Project
  - Delete contents permanently
- Cannot delete Default Project (disable/hide option)

### FR-007: Move Chat Between Projects
- Right-click on chat → "Move to..." submenu
- OR: In chat view, header dropdown to select project
- Update immediately, show toast confirmation

### FR-008: Navigate to Chat/Document
- Click [→] on chat → switch to Chat tab, open that conversation
- Click [→] on document → switch to Documents tab, show document
- "← Back to Projects" link in new view
- Browser back button works (proper URL routing)

### FR-009: Project Order & Persistence
- Default sort: Last used (most recent first)
- Manual reorder via drag & drop
- Order saved to backend per user
- Default Project cannot be reordered (always exists)

---

## Non-Functional Requirements

### NFR-001: Performance
- Project list loads in < 500ms
- Drag reorder feels instant (optimistic UI)
- Navigation transitions < 300ms

### NFR-002: Accessibility
- All interactive elements keyboard accessible
- Proper ARIA labels for icons
- Focus management on panel switches

### NFR-003: Responsive Design
- Dual-panel collapses to single panel on mobile
- Touch-friendly drag handles
- Context menu works on mobile (long-press)

---

## Out of Scope

- Document text extraction
- AI/LLM analysis of documents
- Standards parsing (IEC 62443, etc.)
- Knowledge graphs
- Search within projects

---

## Dependencies

- Stage 2 complete (document upload/download working)
- Existing project CRUD APIs (may need extensions)
- Existing conversation APIs (need project association)

---

## Acceptance Criteria

1. [ ] User can see Projects tab (📁) in left navigation
2. [ ] User can create project with name, description, color, icon
3. [ ] Default Project always exists and cannot be deleted
4. [ ] User can view project details (description, chats, docs)
5. [ ] User can navigate to chat/document with easy back navigation
6. [ ] User can move chat between projects (right-click + header dropdown)
7. [ ] User can delete project (choose: move or delete contents)
8. [ ] User can rename project (inline + form)
9. [ ] User can reorder projects (drag & drop)
10. [ ] All E2E tests pass
11. [ ] Mobile responsive design works

---

*Document approved by user on 2025-11-30*
