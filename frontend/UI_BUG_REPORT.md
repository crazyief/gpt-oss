# UI Rendering Bug Report
**Date**: 2025-11-30
**Reporter**: Frontend-Agent
**Status**: IN PROGRESS

## Critical Bugs Found

### 1. Documents Tab Not Rendering (CRITICAL)
**Symptom**: When clicking Documents tab, the main content area remains completely blank.

**Root Cause**: HMR error "[HMR][Svelte] Unrecoverable HMR error in <DocumentsTab>" indicates module load failure.

**Evidence**:
- Console shows: `[ERROR] Unhandled promise rejection`
- DocumentsTab component never reaches `onMount` lifecycle (console.log never fires)
- Tab panel `<div id="documents-panel">` is not rendered in DOM
- Error occurs during module compilation, not component mounting

**Fixes Applied**:
1. ✅ Fixed documents store structure mismatch (unified state interface)
2. ✅ Updated DocumentList to use store directly instead of props
3. ✅ Fixed promise rejection handling in DocumentsTab.onMount
4. ✅ Added projectId prop to DocumentUploader component

**Still Failing**: Component still not rendering after fixes

**Next Steps**:
- Check for circular import dependencies
- Verify all imported components exist and compile
- Check TypeScript compilation errors
- Simplify DocumentsTab to minimal version to isolate issue

### 2. Settings Tab Not Tested
**Status**: PENDING
**Priority**: HIGH

### 3. Duplicate Tooltips (FIXED)
**Status**: RESOLVED
**Fix**: Removed duplicate `title` attributes from VerticalNav.svelte

## Files Modified

### D:\gpt-oss\frontend\src\lib\stores\documents.ts
**Changes**:
- Restructured from separate stores to unified `DocumentsState` interface
- Changed `documents` from `writable<Document[]>` to `writable<DocumentsState>`
- Updated all store functions to work with unified state
- Fixed all derived stores to access `$state.documents`

**Impact**: BREAKING CHANGE for components using old store structure

### D:\gpt-oss\frontend\src\lib\components\documents\DocumentList.svelte
**Changes**:
- Removed `projectId` and `documents` props
- Added direct store imports and subscriptions
- Moved download/delete logic into component (was using events)
- Now fully self-contained

**Impact**: Component no longer needs props, uses stores directly

### D:\gpt-oss\frontend\src\lib\components\tabs\DocumentsTab.svelte
**Changes**:
- Added error handling to `loadDocuments` promise
- Added `projectId` prop to DocumentUploader
- Added console.log debugging statements
- Wrapped async subscribe callback to prevent unhandled rejections

**Impact**: Should prevent HMR crashes, but still not working

### D:\gpt-oss\frontend\src\lib\components\tabs\SettingsTab.svelte
**Status**: Already had correct `toast` import (no changes needed)

### D:\gpt-oss\frontend\src\lib\components\VerticalNav.svelte
**Changes**:
- Removed duplicate `title` attributes (was causing double tooltips)

**Impact**: Cleaner tooltip behavior

## TypeScript Errors Detected

**Errors from `npm run check`**:
1. MessageContent.svelte: Type errors with `Element.style` (needs type assertion)
2. DocumentPanel.svelte: Importing old `documentsLoading`, `documentsError` (doesn't use new store structure)
3. Multiple test files: Using old store exports
4. Document type issues: `stored_filename` property doesn't exist

**Note**: DocumentPanel.svelte is NOT used in new tab-based layout, can be ignored

## Current State

### Working:
- ✅ Chat Tab renders perfectly
- ✅ Vertical navigation with icons
- ✅ Project selector
- ✅ Theme toggle
- ✅ Top bar

### Broken:
- ❌ Documents Tab (completely blank, HMR error)
- ❓ Settings Tab (not tested yet)

### Partially Working:
- ⚠️ Tab switching (works for Chat, fails for Documents)

## Test Results

**Browser**: Chrome DevTools MCP
**URL**: http://localhost:18173

**Test 1: Chat Tab**
- ✅ Renders sidebar with conversation list
- ✅ Shows "Start a Conversation" empty state
- ✅ New Chat button visible
- ✅ Search input present

**Test 2: Documents Tab**
- ❌ Click on Documents tab → blank screen
- ❌ No content rendered
- ❌ Console error: HMR crash
- ❌ Unhandled promise rejection

**Test 3: Settings Tab**
- ⏭️ Not tested (waiting for Documents fix)

## Recommended Next Actions

1. **Immediate**: Check for circular imports in DocumentsTab and its dependencies
2. **Immediate**: Verify all component imports are valid
3. **Immediate**: Create minimal DocumentsTab to isolate issue
4. **High**: Run full TypeScript check and fix all errors
5. **Medium**: Test Settings tab once Documents is working
6. **Low**: Clean up unused DocumentPanel component

## Known Issues to Address Later

- DocumentPanel.svelte uses old store structure (not used, can remove)
- MessageContent.svelte has TypeScript type errors
- Test files need updating for new store structure
- Document type definition missing `stored_filename` in some test fixtures
