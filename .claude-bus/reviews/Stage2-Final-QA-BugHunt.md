# Stage 2 Final QA Bug Hunt Report

**Date**: 2025-11-30
**QA Agent**: QA-Agent
**Review Type**: Final Bug Hunt (Pre-Release)
**Scope**: All files modified since commit 353398f

---

## Executive Summary

This report documents bugs, issues, and code quality concerns found during the final QA review of Stage 2. The review focused on finding subtle bugs that may have been missed during development and testing.

**Total Issues Found**: 18
- **P1 (Critical)**: 2
- **P2 (Major)**: 7
- **P3 (Minor)**: 9

---

## P1 - CRITICAL BUGS

### BUG-001: Race Condition in SettingsTab Project Loading
**File**: `D:\gpt-oss\frontend\src\lib\components\tabs\SettingsTab.svelte`
**Lines**: 40-47

**Description**:
The component has both an `onMount` and a reactive statement that call `loadProject()`. If `currentProjectId` changes rapidly (e.g., user quickly switches projects), both can trigger simultaneously causing race conditions and potential stale data display.

**Code**:
```svelte
onMount(() => {
    loadProject();  // Called on mount
});

// Reload when project changes
$: if ($currentProjectId !== null) {
    loadProject();  // Also called reactively - RACE CONDITION
}
```

**Impact**: User may see stale project data or experience UI flickering when switching projects quickly.

**Recommended Fix**:
```svelte
let loadAbortController: AbortController | null = null;

async function loadProject() {
    if ($currentProjectId === null) return;

    // Cancel previous load
    if (loadAbortController) {
        loadAbortController.abort();
    }
    loadAbortController = new AbortController();

    isLoading = true;
    try {
        project = await fetchProject($currentProjectId);
        editedName = project.name;
    } catch (error) {
        if (error.name !== 'AbortError') {
            toast.error('Failed to load project settings');
        }
    } finally {
        isLoading = false;
    }
}

// Only use reactive statement (remove onMount)
$: if ($currentProjectId !== null) {
    loadProject();
}
```

---

### BUG-002: Memory Leak - setTimeout Not Cleared in ChatHistoryItem
**File**: `D:\gpt-oss\frontend\src\lib\components\ChatHistoryItem.svelte`
**Lines**: 66-71

**Description**:
The `setTimeout` for auto-hiding delete confirmation is never cleared if the component unmounts or if the user deletes the item. This can cause errors when trying to update state on an unmounted component.

**Code**:
```svelte
function handleDeleteClick(event: Event) {
    event.stopPropagation();
    if (!showDeleteConfirm) {
        showDeleteConfirm = true;
        setTimeout(() => {
            showDeleteConfirm = false;  // May run after unmount!
        }, 3000);
    }
}
```

**Impact**: Memory leak and potential "cannot update state on unmounted component" errors.

**Recommended Fix**:
```svelte
import { onDestroy } from 'svelte';

let deleteConfirmTimeout: ReturnType<typeof setTimeout> | null = null;

function handleDeleteClick(event: Event) {
    event.stopPropagation();
    if (!showDeleteConfirm) {
        showDeleteConfirm = true;
        if (deleteConfirmTimeout) clearTimeout(deleteConfirmTimeout);
        deleteConfirmTimeout = setTimeout(() => {
            showDeleteConfirm = false;
        }, 3000);
    }
}

onDestroy(() => {
    if (deleteConfirmTimeout) clearTimeout(deleteConfirmTimeout);
});
```

---

## P2 - MAJOR BUGS

### BUG-003: Unhandled Promise Rejection in ProjectSelector
**File**: `D:\gpt-oss\frontend\src\lib\components\ProjectSelector.svelte`
**Lines**: 230-255

**Description**:
The `handleDeleteProject` function catches errors but the `confirm()` dialog can throw if blocked by browser settings. Additionally, the error is displayed in a local `error` variable but then auto-cleared, which might confuse users if they don't see it.

**Code**:
```svelte
async function handleDeleteProject(projectId: number) {
    // ...
    const confirmed = confirm(`...`);  // Can throw in some contexts
    // ...
    error = err instanceof Error ? err.message : 'Failed to delete project';
    setTimeout(() => {
        error = null;  // Clears error too fast for user to read
    }, 3000);
}
```

**Impact**: Error handling inconsistent with toast-based error handling elsewhere in the app.

**Recommended Fix**: Use toast notifications instead of local error state for consistency, and handle potential confirm() failures.

---

### BUG-004: Double Toast Auto-Dismiss in toast.ts
**File**: `D:\gpt-oss\frontend\src\lib\stores\toast.ts`
**Lines**: 112-123 (and similar in error/warning/info)

**Description**:
The toast functions both pass `duration` to the library AND set up a manual `setTimeout` for auto-dismiss. This causes toasts to be dismissed twice, potentially causing issues with toast IDs.

**Code**:
```typescript
export function success(message: string, duration?: number): number {
    const actualDuration = duration ?? defaultDurations.success;
    const id = svelteToast.push(message, {
        ...themes.success,
        duration: actualDuration  // Library handles this
    });
    // Manual auto-dismiss as fallback (DUPLICATE!)
    setTimeout(() => {
        svelteToast.pop(id);  // Called twice - once by library, once here
    }, actualDuration);
    return id;
}
```

**Impact**: Toasts may be dismissed twice, causing console warnings or unexpected behavior.

**Recommended Fix**: Remove the manual setTimeout since the library already handles auto-dismiss:
```typescript
export function success(message: string, duration?: number): number {
    const actualDuration = duration ?? defaultDurations.success;
    return svelteToast.push(message, {
        ...themes.success,
        duration: actualDuration
    });
}
```

---

### BUG-005: Missing Error Handling in DocumentsTab loadDocuments
**File**: `D:\gpt-oss\frontend\src\lib\components\tabs\DocumentsTab.svelte`
**Lines**: 50-54

**Description**:
The `handleDocumentUploaded` function calls `loadDocuments` without awaiting it or catching errors, which means any errors during reload are silently ignored.

**Code**:
```svelte
function handleDocumentUploaded() {
    if ($currentProjectId !== null) {
        loadDocuments($currentProjectId);  // Not awaited, errors ignored
    }
}
```

**Impact**: If document reload fails after upload, user sees stale document list with no error indication.

**Recommended Fix**:
```svelte
async function handleDocumentUploaded() {
    if ($currentProjectId !== null) {
        try {
            await loadDocuments($currentProjectId);
        } catch (error) {
            console.error('Failed to reload documents:', error);
            // Store already handles error state
        }
    }
}
```

---

### BUG-006: Dynamic Import in DocumentList Delete Handler
**File**: `D:\gpt-oss\frontend\src\lib\components\documents\DocumentList.svelte`
**Lines**: 106-118

**Description**:
The delete handler uses dynamic import inside the function, which is inefficient and can fail if the module path is wrong. The `loadDocuments` function is already available at the top level.

**Code**:
```svelte
async function handleDelete(documentId: number) {
    // ...
    // Reload documents to update list
    const { loadDocuments } = await import('$lib/stores/documents');  // Inefficient!
    await loadDocuments(projectId);
}
```

**Impact**: Slightly slower delete operations and potential import failures.

**Recommended Fix**: Import `loadDocuments` at the top of the file:
```svelte
import { documents as documentsStore, loadDocuments } from '$lib/stores/documents';
```

---

### BUG-007: Missing aria-current Value in ChatHistoryItem
**File**: `D:\gpt-oss\frontend\src\lib\components\ChatHistoryItem.svelte`
**Line**: 108

**Description**:
The `aria-current` attribute is set to `"true"` or `"false"` as strings, but the `aria-current` spec expects values like `"page"`, `"step"`, `"location"`, `"date"`, `"time"`, or `"true"` (boolean). The `"false"` value is not valid.

**Code**:
```svelte
aria-current={isActive ? 'true' : 'false'}
```

**Impact**: Screen readers may not correctly announce the active state.

**Recommended Fix**:
```svelte
aria-current={isActive ? 'true' : undefined}
```
Or use a more specific value:
```svelte
aria-current={isActive ? 'location' : undefined}
```

---

### BUG-008: Keyboard Navigation Bug in VerticalNav
**File**: `D:\gpt-oss\frontend\src\lib\components\VerticalNav.svelte`
**Lines**: 49-61

**Description**:
The keyboard navigation logic for skipping disabled tabs has a bug. The condition `tabs[idx] === 'chat' || isProjectSelected` will always be true for 'chat' regardless of the loop iteration, potentially causing an infinite loop or wrong tab selection.

**Code**:
```svelte
if (newTab !== 'chat' && !isProjectSelected) {
    for (let i = 0; i < tabs.length; i++) {
        const idx = (newIndex + i) % tabs.length;
        if (tabs[idx] === 'chat' || isProjectSelected) {  // BUG: logic error
            setTab(tabs[idx]);
            break;
        }
    }
}
```

**Impact**: Arrow key navigation may not work correctly when some tabs are disabled.

**Recommended Fix**:
```svelte
if (newTab !== 'chat' && !isProjectSelected) {
    // Find next enabled tab (only 'chat' is enabled when no project)
    setTab('chat');
} else {
    setTab(newTab);
}
```

---

### BUG-009: CSS Hardcoded Colors in DocumentList
**File**: `D:\gpt-oss\frontend\src\lib\components\documents\DocumentList.svelte`
**Lines**: 246-400

**Description**:
The DocumentList component uses hardcoded `rgba(255, 255, 255, ...)` colors instead of CSS variables. This breaks theming - the component will look wrong in light theme.

**Code**:
```css
.document-count {
    color: rgba(255, 255, 255, 0.8);  /* Hardcoded white */
}
.filter-select {
    border: 1px solid rgba(255, 255, 255, 0.2);
    background: rgba(255, 255, 255, 0.05);
    color: rgba(255, 255, 255, 0.9);
}
```

**Impact**: DocumentList component will have poor contrast/visibility in light theme.

**Recommended Fix**: Use CSS variables:
```css
.document-count {
    color: var(--text-secondary);
}
.filter-select {
    border: 1px solid var(--border-primary);
    background: var(--bg-tertiary);
    color: var(--text-primary);
}
```

---

## P3 - MINOR BUGS

### BUG-010: Console.log Left in Production Code
**File**: `D:\gpt-oss\frontend\src\lib\components\tabs\DocumentsTab.svelte`
**Lines**: 20-21

**Description**:
Debug console.log statements are left in production code.

**Code**:
```svelte
console.log('[DocumentsTab] Component mounted, currentProjectId:', $currentProjectId);
// ...
console.log('[DocumentsTab] Project ID changed:', projectId);
```

**Impact**: Console noise in production.

**Recommended Fix**: Remove or replace with logger utility.

---

### BUG-011: Missing Type Annotation in handleSort
**File**: `D:\gpt-oss\frontend\src\lib\components\documents\DocumentList.svelte`
**Line**: 187

**Description**:
The `handleSort` function parameter type could be more specific.

**Code**:
```typescript
function handleSort(column: typeof sortColumn) {
```

**Impact**: TypeScript inference works, but explicit type would be clearer.

**Recommended Fix**:
```typescript
function handleSort(column: 'name' | 'type' | 'size' | 'date') {
```

---

### BUG-012: SVG Cancel Icon Path Error in ChatHistoryItem
**File**: `D:\gpt-oss\frontend\src\lib\components\ChatHistoryItem.svelte`
**Line**: 150

**Description**:
The cancel button SVG has a path that draws an X but with coordinates that go outside the viewBox.

**Code**:
```svelte
<path d="M15 5L5 15M5 5l15 15" .../>  <!-- l15 15 goes outside 20x20 viewBox -->
```

**Impact**: The X icon may render incorrectly in some browsers.

**Recommended Fix**:
```svelte
<path d="M15 5L5 15M5 5l10 10" .../>
```

---

### BUG-013: Missing Loading State Reset in SettingsTab
**File**: `D:\gpt-oss\frontend\src\lib\components\tabs\SettingsTab.svelte`
**Lines**: 64-82

**Description**:
When project deletion succeeds, the `isDeleting` flag is reset in `finally` block, but if `currentProjectId.set(null)` is called, the component may not update correctly since the project is null.

**Code**:
```svelte
async function handleDelete() {
    // ...
    currentProjectId.set(null);  // This may cause re-render
    conversations.setConversations([]);
    activeTab.setTab('chat');
    // finally block runs after navigation
}
```

**Impact**: Minor - potential UI state inconsistency during navigation.

**Recommended Fix**: Set navigation/state before cleanup:
```svelte
async function handleDelete() {
    // ...
    try {
        await deleteProject(project.id);
        activeTab.setTab('chat');  // Navigate first
        currentProjectId.set(null);
        conversations.setConversations([]);
        toast.success('Project deleted successfully');
    } // ...
}
```

---

### BUG-014: Potential XSS in toast.ts getErrorMessage
**File**: `D:\gpt-oss\frontend\src\lib\stores\toast.ts`
**Lines**: 297-310

**Description**:
The `getErrorMessage` function returns error strings that may come from server responses. If these are rendered as HTML in toasts, there's a potential XSS risk.

**Code**:
```typescript
if (error?.detail) {
    return typeof error.detail === 'string' ? error.detail : 'An error occurred.';
}
if (error?.message) {
    return error.message;  // Could contain malicious HTML
}
```

**Impact**: Low risk if toasts only render text, but worth sanitizing.

**Recommended Fix**: Sanitize output or ensure toast library escapes HTML.

---

### BUG-015: Inconsistent Button Type Attributes
**File**: `D:\gpt-oss\frontend\src\lib\components\tabs\SettingsTab.svelte`
**Lines**: 115, 151, 158, 168

**Description**:
Some buttons have `type="button"` and some don't. Buttons inside forms default to `type="submit"` which can cause unexpected form submissions.

**Code**:
```svelte
<button class="save-btn" on:click={handleSave}>  <!-- Missing type -->
// vs
<button type="button" on:click={() => (showDeleteConfirm = true)}>
```

**Impact**: Potential unexpected form submission behavior.

**Recommended Fix**: Add `type="button"` to all buttons.

---

### BUG-016: Missing Focus Trap in CreateProjectModal
**File**: `D:\gpt-oss\frontend\src\lib\components\modals\CreateProjectModal.svelte`

**Description**:
The modal doesn't trap focus - users can tab outside the modal to elements behind the overlay.

**Impact**: Accessibility issue for keyboard users.

**Recommended Fix**: Implement focus trap using a library like `focus-trap` or manual implementation.

---

### BUG-017: CSS Selector Specificity Issue
**File**: `D:\gpt-oss\frontend\src\routes\+page.svelte`
**Line**: 96-98

**Description**:
The CSS selector `header[role="banner"]` targets an element with role="banner", but the `<header>` element in the template doesn't have this role attribute.

**Code**:
```css
header[role="banner"] {
    flex-shrink: 0;
}
```
```svelte
<header>
    <TopBar />
</header>
```

**Impact**: CSS rule never applies (dead code).

**Recommended Fix**: Either add the role or simplify the selector:
```css
header {
    flex-shrink: 0;
}
```

---

### BUG-018: Unsubscribe Variable Initialized Outside onMount
**File**: `D:\gpt-oss\frontend\src\lib\components\ProjectSelector.svelte`
**Lines**: 39, 125, 143-147

**Description**:
The `unsubscribe` variable is used in module scope but assigned inside `onMount`. This is correct but the variable declaration is far from its usage, and there's a potential issue if the component is used with SSR.

**Code**:
```svelte
let unsubscribe: Unsubscriber;  // Line 39

// Line 125 - inside module scope, not onMount!
unsubscribe = conversations.subscribe((state) => {
    // ...
});

onDestroy(() => {
    if (unsubscribe) {
        unsubscribe();
    }
});
```

**Impact**: The subscription is created at module evaluation time, not component mount time. This could cause issues with SSR or if the store is not available.

**Recommended Fix**: Move subscription inside `onMount`:
```svelte
onMount(async () => {
    // ... existing code ...

    // Move subscription here
    unsubscribe = conversations.subscribe((state) => {
        const currentCount = state.items.length;
        if (!isLoading && projects.length > 0 && currentCount !== previousConversationCount) {
            previousConversationCount = currentCount;
            loadProjects();
        }
    });
});
```

---

## Code Quality Issues (Not Bugs)

### CQ-001: SettingsTab Near 400-Line Limit
**File**: `D:\gpt-oss\frontend\src\lib\components\tabs\SettingsTab.svelte`
**Lines**: 399

The file is at 399 lines, right at the 400-line limit. Consider extracting the delete confirmation dialog into a separate component.

### CQ-002: Inconsistent Error Handling Patterns
Some components use `toast.error()`, others use local error state, and others use `logger.error()`. Consider standardizing on one pattern.

### CQ-003: Missing TypeScript Strict Null Checks
Several places use `!` non-null assertions or have potential null issues:
- `$currentProjectId!` assumptions
- `project!.name` without null checks

### CQ-004: No Loading State for Initial Project Fetch in TopBar
The TopBar component doesn't show any loading state while ProjectSelector is fetching initial projects.

### CQ-005: Test File Not Updated
The `documents.test.ts` file was modified but the tests may not cover all the new functionality added in Stage 2.

---

## Summary by File

| File | P1 | P2 | P3 | Total |
|------|----|----|----|----|
| SettingsTab.svelte | 1 | 0 | 2 | 3 |
| ChatHistoryItem.svelte | 1 | 1 | 1 | 3 |
| ProjectSelector.svelte | 0 | 1 | 1 | 2 |
| toast.ts | 0 | 1 | 1 | 2 |
| DocumentsTab.svelte | 0 | 1 | 1 | 2 |
| DocumentList.svelte | 0 | 2 | 1 | 3 |
| VerticalNav.svelte | 0 | 1 | 0 | 1 |
| CreateProjectModal.svelte | 0 | 0 | 1 | 1 |
| +page.svelte | 0 | 0 | 1 | 1 |
| **Total** | **2** | **7** | **9** | **18** |

---

## Recommendations

1. **Fix P1 bugs immediately** - Race conditions and memory leaks can cause production issues
2. **Address P2 bugs before release** - These affect user experience and accessibility
3. **Schedule P3 bugs for next iteration** - Minor issues that don't block release
4. **Standardize error handling** - Choose one pattern (toast, local state, or logger) and use consistently
5. **Add CSS variable usage to DocumentList** - Required for theme support
6. **Consider component extraction** - SettingsTab is at line limit

---

**QA Sign-off**: This review is complete. The codebase is functional but has several issues that should be addressed. P1 bugs should be fixed before Stage 2 completion.

**Reviewer**: QA-Agent
**Date**: 2025-11-30
