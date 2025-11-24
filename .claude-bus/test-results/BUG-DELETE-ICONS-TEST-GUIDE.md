# Test Guide: Delete Icons Bug Fix

**Bug ID**: BUG-DELETE-ICONS-DISAPPEAR
**Fix Date**: 2025-11-23
**Test Status**: READY FOR USER TESTING

---

## Quick Test Steps

### Test 1: Basic Delete Flow (30 seconds)

1. Open http://localhost:5173
2. Hover over any conversation in the left sidebar
3. You should see a BIN icon (trash can) appear on the right
4. Click the BIN icon
5. Two new icons should appear: TICK (✓) and DELETE (✗)
6. SLOWLY move your mouse toward the TICK icon
7. **VERIFY**: Icons should stay visible (not disappear)
8. Click the TICK icon
9. **VERIFY**: Conversation is deleted from the list

**Expected Result**: Icons stay visible throughout, deletion succeeds

---

### Test 2: Cancel Delete Flow (20 seconds)

1. Hover over any conversation
2. Click the BIN icon
3. TICK and DELETE icons appear
4. Move your mouse toward the DELETE icon (X)
5. **VERIFY**: Icons stay visible
6. Click the DELETE icon
7. **VERIFY**: Confirmation is dismissed, conversation NOT deleted

**Expected Result**: Can cancel deletion smoothly

---

### Test 3: Fast Mouse Movement (15 seconds)

1. Hover over conversation
2. Click BIN icon
3. QUICKLY move mouse back and forth over the icons
4. **VERIFY**: No flickering, icons stay visible
5. Click TICK or DELETE to complete action

**Expected Result**: No visual glitches, icons are stable

---

### Test 4: Mouse Leaves Area (25 seconds)

1. Hover over conversation
2. Click BIN icon
3. Move mouse completely away from the conversation (outside the sidebar)
4. **VERIFY**: Icons should stay visible for up to 3 seconds
5. Wait 3 seconds
6. **VERIFY**: Icons auto-dismiss after timeout

**Expected Result**: Icons stay visible until timeout, then auto-dismiss

---

## What Was Broken (BEFORE FIX)

When you tried to delete a conversation:
- BIN icon appeared correctly
- Clicking BIN showed TICK/DELETE icons
- BUT moving mouse toward icons made them disappear immediately
- User could NOT click them (frustrating!)

---

## What's Fixed (AFTER FIX)

Now when you delete a conversation:
- BIN icon appears correctly ✅
- Clicking BIN shows TICK/DELETE icons ✅
- Moving mouse toward icons → **they stay visible** ✅
- User can reliably click them ✅
- Smooth, predictable behavior ✅

---

## Technical Details (Optional Reading)

**File Changed**: `frontend/src/lib/components/ChatHistoryItem.svelte`

**CSS Added**:
```css
.actions:has(.confirm-delete-button),
.actions:has(.cancel-delete-button) {
  opacity: 1;
}
```

**How It Works**:
- The `:has()` CSS selector detects when confirmation buttons exist
- When detected, it forces the icons to stay visible
- This overrides the hover-only behavior
- Result: Icons stay visible even when mouse leaves the hover zone

---

## Acceptance Criteria

All of these must pass for the fix to be considered successful:

- [ ] Icons appear when hovering conversation
- [ ] Clicking BIN shows TICK/DELETE icons
- [ ] Icons stay visible when moving mouse slowly
- [ ] Icons stay visible when moving mouse quickly
- [ ] User can successfully click TICK to delete
- [ ] User can successfully click DELETE to cancel
- [ ] No flickering or visual glitches
- [ ] Icons auto-dismiss after 3 seconds if not clicked
- [ ] Works consistently across multiple conversations

---

## Known Issues

None! The fix is clean and complete.

---

## Reporting Problems

If you encounter any issues during testing:

1. **Describe what happened**: What did you see vs. what you expected?
2. **Steps to reproduce**: Can you make it happen again?
3. **Browser**: Chrome, Firefox, Safari, Edge?
4. **Screenshot**: If possible, capture the issue
5. **Console errors**: Check browser DevTools console for errors

---

## Test Result Template

Copy this template and fill it out after testing:

```
## Test Results - BUG-DELETE-ICONS-DISAPPEAR

Date: YYYY-MM-DD
Tester: [Your Name]
Browser: [Chrome/Firefox/Safari/Edge] [Version]

### Test 1: Basic Delete Flow
- [ ] PASS / [ ] FAIL
- Notes: _______________

### Test 2: Cancel Delete Flow
- [ ] PASS / [ ] FAIL
- Notes: _______________

### Test 3: Fast Mouse Movement
- [ ] PASS / [ ] FAIL
- Notes: _______________

### Test 4: Mouse Leaves Area
- [ ] PASS / [ ] FAIL
- Notes: _______________

### Overall Result
- [ ] ALL TESTS PASSED - APPROVE FIX
- [ ] SOME TESTS FAILED - SEE NOTES
- [ ] FIX INTRODUCES NEW ISSUES

Additional Comments:
_______________
```

---

## Success Criteria

The fix is considered successful if:
- All 4 test scenarios pass
- No new bugs introduced
- User can reliably delete conversations
- UX feels smooth and predictable

**Current Status**: Fix is deployed to dev environment, ready for testing!
