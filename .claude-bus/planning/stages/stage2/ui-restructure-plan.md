# UI Restructure Plan: Vertical Tabs + Theme System

**Date**: 2025-11-29
**Status**: PLANNING
**Estimated Changes**: 15-20 files

---

## Overview

Restructure the GPT-OSS UI with:
1. **Vertical Tab Navigation** (left side) - maximize chat vertical space
2. **Global Theme System** - Dark, Matrix (black/green), Light themes
3. **Project-Centric Workflow** - Select project first, then access features

---

## New Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│ [Project: XXX ▼]  [🌙 Theme Toggle]                             │
├────────┬────────────────────────────────────────────────────────┤
│        │                                                        │
│  💬    │                                                        │
│  Chat  │                                                        │
│        │              Main Content Area                         │
│  📄    │              (Chat / Documents / Settings)             │
│  Docs  │                                                        │
│        │                                                        │
│  ⚙️    │                                                        │
│  Set   │                                                        │
│        │                                                        │
├────────┴────────────────────────────────────────────────────────┤
│                     [Input Area - Chat Only]                     │
└─────────────────────────────────────────────────────────────────┘
```

**Key Changes**:
- Sidebar becomes narrow icon bar (vertical tabs)
- Conversation history moves inside Chat tab
- Documents panel becomes full-height content area
- Project selector at top, prominent

---

## Theme System Design

### CSS Variables Approach

```css
:root[data-theme="dark"] {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-tertiary: #334155;
  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --border: rgba(255, 255, 255, 0.1);
  --accent: #3b82f6;
  --accent-hover: #60a5fa;
}

:root[data-theme="matrix"] {
  --bg-primary: #0a0a0a;
  --bg-secondary: #0d1a0d;
  --bg-tertiary: #1a2e1a;
  --text-primary: #00ff41;
  --text-secondary: #00cc33;
  --text-muted: #00992a;
  --border: rgba(0, 255, 65, 0.2);
  --accent: #00ff41;
  --accent-hover: #33ff66;
}

:root[data-theme="light"] {
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --bg-tertiary: #f1f5f9;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --text-muted: #94a3b8;
  --border: #e2e8f0;
  --accent: #3b82f6;
  --accent-hover: #2563eb;
}
```

### Theme Store

```typescript
// src/lib/stores/theme.ts
type Theme = 'dark' | 'matrix' | 'light';

const STORAGE_KEY = 'gpt-oss-theme';

function createThemeStore() {
  const stored = localStorage.getItem(STORAGE_KEY) as Theme || 'dark';
  const { subscribe, set, update } = writable<Theme>(stored);

  return {
    subscribe,
    setTheme: (theme: Theme) => {
      localStorage.setItem(STORAGE_KEY, theme);
      document.documentElement.setAttribute('data-theme', theme);
      set(theme);
    },
    toggle: () => {
      update(current => {
        const themes: Theme[] = ['dark', 'matrix', 'light'];
        const next = themes[(themes.indexOf(current) + 1) % themes.length];
        localStorage.setItem(STORAGE_KEY, next);
        document.documentElement.setAttribute('data-theme', next);
        return next;
      });
    }
  };
}
```

---

## Implementation Tasks

### Phase 1: Theme System Foundation (4 files)

| # | File | Action |
|---|------|--------|
| 1 | `src/lib/stores/theme.ts` | CREATE - Theme store with localStorage persistence |
| 2 | `src/app.css` | MODIFY - Add CSS variables for all 3 themes |
| 3 | `src/routes/+layout.svelte` | MODIFY - Initialize theme on mount, add data-theme to html |
| 4 | `src/lib/components/ThemeToggle.svelte` | CREATE - Theme toggle button component |

### Phase 2: Layout Restructure (5 files)

| # | File | Action |
|---|------|--------|
| 5 | `src/lib/components/VerticalNav.svelte` | CREATE - Vertical tab navigation (Chat/Docs/Settings icons) |
| 6 | `src/lib/components/TopBar.svelte` | CREATE - Project selector + theme toggle |
| 7 | `src/routes/+page.svelte` | MODIFY - New layout with VerticalNav + TopBar |
| 8 | `src/lib/stores/navigation.ts` | CREATE - Active tab store |
| 9 | `src/lib/components/Sidebar.svelte` | MODIFY - Integrate into Chat tab as conversation list |

### Phase 3: Content Areas (4 files)

| # | File | Action |
|---|------|--------|
| 10 | `src/lib/components/tabs/ChatTab.svelte` | CREATE - Chat interface + conversation history |
| 11 | `src/lib/components/tabs/DocumentsTab.svelte` | CREATE - Full document management panel |
| 12 | `src/lib/components/tabs/SettingsTab.svelte` | CREATE - Project settings (extracted from modal) |
| 13 | `src/lib/components/ChatInterface.svelte` | MODIFY - Use theme variables |

### Phase 4: Update All Components for Theme (6+ files)

| # | File | Action |
|---|------|--------|
| 14 | `src/lib/components/MessageList.svelte` | MODIFY - Theme variables |
| 15 | `src/lib/components/UserMessage.svelte` | MODIFY - Theme variables |
| 16 | `src/lib/components/AssistantMessage.svelte` | MODIFY - Theme variables |
| 17 | `src/lib/components/MessageInput.svelte` | MODIFY - Theme variables |
| 18 | `src/lib/components/documents/*.svelte` | MODIFY - Theme variables (all document components) |
| 19 | `src/lib/components/modals/*.svelte` | MODIFY - Theme variables (all modals) |

### Phase 5: Testing & Polish

| # | Task |
|---|------|
| 20 | Visual test all 3 themes |
| 21 | Test tab navigation |
| 22 | Test project workflow |
| 23 | Update existing tests |

---

## Component Details

### VerticalNav.svelte

```svelte
<nav class="vertical-nav">
  <button class:active={$activeTab === 'chat'} on:click={() => setTab('chat')}>
    <ChatIcon />
    <span class="tooltip">Chat</span>
  </button>
  <button class:active={$activeTab === 'documents'} on:click={() => setTab('documents')}>
    <DocumentIcon />
    <span class="tooltip">Documents</span>
  </button>
  <button class:active={$activeTab === 'settings'} on:click={() => setTab('settings')}>
    <SettingsIcon />
    <span class="tooltip">Settings</span>
  </button>
</nav>

<style>
  .vertical-nav {
    width: 64px;
    background: var(--bg-secondary);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    padding: 1rem 0;
    gap: 0.5rem;
  }
</style>
```

### TopBar.svelte

```svelte
<header class="top-bar">
  <ProjectSelector />
  <div class="spacer"></div>
  <ThemeToggle />
</header>

<style>
  .top-bar {
    height: 56px;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    padding: 0 1rem;
    gap: 1rem;
  }
</style>
```

---

## Migration Strategy

### Step 1: Non-Breaking Theme Addition
- Add CSS variables without breaking current styles
- Theme store works, but defaults to current appearance
- Existing components unchanged initially

### Step 2: Layout Restructure
- New layout components created
- Old layout coexists temporarily
- Feature flag or route switch

### Step 3: Component Migration
- Migrate components one-by-one to use CSS variables
- Test each component in all 3 themes
- Remove hardcoded colors

### Step 4: Cleanup
- Remove old layout code
- Remove feature flags
- Final visual polish

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking existing UI | Incremental migration with feature flags |
| CSS specificity conflicts | Use CSS variables consistently, avoid `!important` |
| localStorage not available | Fallback to default theme |
| Mobile responsiveness | Test at each step, maintain breakpoints |

---

## Acceptance Criteria

1. ✅ Three themes work correctly (Dark, Matrix, Light)
2. ✅ Theme persists across page reloads
3. ✅ Theme applies to ALL UI elements (sidebar, chat, modals, etc.)
4. ✅ Vertical tabs navigate between Chat/Documents/Settings
5. ✅ Project must be selected before uploading documents
6. ✅ Chat has maximum vertical space
7. ✅ Mobile responsive (tabs collapse or stack)
8. ✅ All existing tests pass
9. ✅ Performance: No layout shift on theme change

---

## Estimated Timeline

| Phase | Files | Complexity |
|-------|-------|------------|
| Phase 1: Theme Foundation | 4 | Low |
| Phase 2: Layout Restructure | 5 | Medium |
| Phase 3: Content Areas | 4 | Medium |
| Phase 4: Component Migration | 6+ | Low (repetitive) |
| Phase 5: Testing | - | Low |

**Total**: ~20 files, Medium complexity

---

## Ready for Implementation

Proceed with this plan? (User approval required)
