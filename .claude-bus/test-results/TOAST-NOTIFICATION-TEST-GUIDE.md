# Toast Notification Test Guide

**Date**: 2025-11-24
**Priority**: HIGH (Production Blocker Fix)
**Issues Fixed**: BUG-QA-005, BUG-QA-006

## Quick Start

```bash
cd /d/gpt-oss/frontend

# Start development server
npm run dev

# In another terminal, ensure backend is running
cd /d/gpt-oss
docker-compose up -d backend
```

Visit: http://localhost:3000

## Test Scenarios

### 1. Success Toasts (Green)

#### Test: Create Project
1. Click "New Project" button
2. Enter project name
3. Click "Create"
4. **Expected**: Green toast appears top-right: "Project {name} created successfully"
5. **Duration**: Disappears after 3 seconds

#### Test: Delete Project
1. Click trash icon on any project
2. Confirm deletion
3. **Expected**: Green toast: "Project deleted successfully"

#### Test: Create Conversation
1. Open a project
2. Click "New Chat" button
3. **Expected**: Green toast: "New conversation started"

#### Test: Update Conversation
1. Right-click conversation → Rename
2. Enter new title
3. Press Enter
4. **Expected**: Green toast: "Conversation updated"

#### Test: Delete Conversation
1. Right-click conversation → Delete
2. Confirm
3. **Expected**: Green toast: "Conversation deleted"

### 2. Error Toasts (Red)

#### Test: Network Error
1. Stop the backend: `docker-compose stop backend`
2. Try to create a project
3. **Expected**: Red toast: "Network error. Please check your connection."
4. **Duration**: Disappears after 5 seconds

#### Test: 404 Error
1. Manually navigate to non-existent resource (edit URL to invalid ID)
2. **Expected**: Red toast: "Failed to load {resource}: Resource not found."

#### Test: Validation Error
1. Try to create project with empty name
2. **Expected**: Red toast with validation message from backend

### 3. Warning Toasts (Amber)

#### Test: SSE Reconnection
1. Start a chat conversation
2. Temporarily disconnect network (airplane mode or disable network adapter)
3. **Expected**: Amber toast appears: "Reconnecting... (1/5)"
4. Re-enable network
5. **Expected**: Connection restored, toast disappears

#### Test: Multiple Retries
1. Keep network disconnected longer
2. **Expected**: Sequential toasts: "Reconnecting... (2/5)", "Reconnecting... (3/5)", etc.
3. After 5 failures: Red toast: "Unable to connect after multiple retries..."

### 4. Edge Cases

#### Test: Multiple Errors Simultaneously
1. Stop backend
2. Click delete on 3 different projects rapidly
3. **Expected**: 3 red error toasts stack vertically (not overlapping)

#### Test: Toast Persistence
1. Trigger error toast
2. Immediately navigate to different page
3. **Expected**: Toast should clear on navigation (or stay if error is critical)

#### Test: Long Error Messages
1. Trigger backend error with long message (>100 chars)
2. **Expected**: Toast expands to show full message (max-width: 500px)
3. Text should wrap, not overflow

### 5. Cross-browser Testing

Test in:
- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari (if available)
- [ ] Mobile browser (responsive)

For each browser, verify:
- Toast appears top-right
- Colors are correct (green/red/amber/blue)
- Text is readable
- Auto-dismiss works
- Manual dismiss (X button) works

### 6. Accessibility

#### Test: Keyboard Navigation
1. Trigger toast
2. Press Tab repeatedly
3. **Expected**: Focus moves to toast dismiss button
4. Press Enter
5. **Expected**: Toast dismisses

#### Test: Screen Reader
1. Enable screen reader (NVDA/JAWS/VoiceOver)
2. Trigger toast
3. **Expected**: Screen reader announces toast message

### 7. Configuration Verification

#### Test: Development vs Production URLs
```bash
# Development mode
npm run dev
# Open DevTools → Network tab
# Check API calls go to localhost:8000

# Production build
npm run build
npm run preview
# Check what URL would be used (should use .env.production)
```

#### Test: Environment Variables
```bash
# Create .env.local (overrides .env.development)
echo "VITE_API_URL=http://localhost:9000" > .env.local

# Restart dev server
npm run dev

# API calls should now go to localhost:9000
```

## Expected Toast Messages Reference

### Success Messages (3s duration)
- "Project {name} created successfully"
- "Project deleted successfully"
- "New conversation started"
- "Conversation updated"
- "Conversation deleted"

### Error Messages (5s duration)
- "Network error. Please check your connection."
- "Failed to load {resource}: {http error message}"
- "Failed to create {resource}: {http error message}"
- "Failed to delete {resource}: {http error message}"
- "Failed to update {resource}: {http error message}"

### Warning Messages (4s duration)
- "Reconnecting... (1/5)"
- "Reconnecting... (2/5)"
- ... up to 5

### HTTP Error Translations
| Status | User-Friendly Message |
|--------|----------------------|
| 400 | "Invalid request. Please check your input." |
| 401 | "Authentication required. Please log in." |
| 403 | "Access denied. You do not have permission." |
| 404 | "Resource not found." |
| 409 | "Conflict. Resource already exists." |
| 413 | "Request too large. Please reduce file size." |
| 422 | "Validation failed. Please check your input." |
| 429 | "Too many requests. Please slow down." |
| 500 | "Server error. Please try again later." |
| 502 | "Bad gateway. Server is temporarily unavailable." |
| 503 | "Service unavailable. Please try again later." |
| 504 | "Gateway timeout. Request took too long." |

## Manual Test Checklist

- [ ] All success toasts appear and auto-dismiss
- [ ] All error toasts appear with correct messages
- [ ] Network errors show generic "check connection" message
- [ ] HTTP errors show user-friendly messages (not status codes)
- [ ] SSE reconnection shows retry count
- [ ] Max retries shows final error message
- [ ] Multiple toasts stack vertically
- [ ] Toasts don't block UI interaction
- [ ] Dismiss button works
- [ ] Auto-dismiss timing is correct
- [ ] Mobile responsive (text wraps, readable)
- [ ] Cross-browser compatible
- [ ] Keyboard accessible
- [ ] Screen reader compatible

## Known Issues

None. All tests should pass.

## Rollback Instructions

If toast notifications cause issues:

```bash
cd /d/gpt-oss/frontend

# Restore original files from backup
mv src/lib/services/api-client.ts.backup src/lib/services/api-client.ts
mv src/lib/services/sse-client.ts.backup src/lib/services/sse-client.ts

# Remove toast package
npm uninstall @zerodevx/svelte-toast

# Revert layout changes
git checkout src/routes/+layout.svelte

# Restart dev server
npm run dev
```

## Success Criteria

✅ All toasts appear at correct position (top-right)
✅ All toasts have correct colors (green/red/amber/blue)
✅ All toasts auto-dismiss after correct duration
✅ No hardcoded localhost:8000 URLs (except in config.ts fallback)
✅ TypeScript compilation succeeds (no new errors)
✅ Build succeeds (`npm run build`)
✅ No console errors in browser
✅ User-friendly error messages (no technical jargon)
✅ Network errors detected and displayed
✅ SSE retry logic shows progress
✅ Cross-browser compatible
✅ Mobile responsive
✅ Accessible (keyboard + screen reader)
