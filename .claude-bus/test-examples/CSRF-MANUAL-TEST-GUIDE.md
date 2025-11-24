# CSRF Frontend - Quick Testing Guide

**Status**: Ready for testing (awaiting backend CSRF endpoint)
**Testing Time**: ~15 minutes

---

## Quick Start

### 1. Start Services

```bash
# Terminal 1: Backend
cd D:\gpt-oss
docker-compose up

# Terminal 2: Frontend
cd D:\gpt-oss\frontend
npm run dev
```

### 2. Open Browser

- Navigate to: http://localhost:3000
- Open DevTools (F12)
- Go to Console tab

---

## Test 1: Token Fetch (2 min)

**Purpose**: Verify token loads and caches correctly

```javascript
// Run in browser console:

// Check preload worked
console.log('Token cached:', sessionStorage.getItem('csrf_token'));
console.log('Token expiry:', new Date(parseInt(sessionStorage.getItem('csrf_token_expiry'))));

// Manual fetch (should use cache)
const { csrfClient } = await import('/src/lib/services/api/index.ts');
const token = await csrfClient.getToken();
console.log('Token:', token);
```

**Expected**:
- ✅ Token is a long string
- ✅ Expiry is ~1 hour from now
- ✅ No network request (uses cache)

---

## Test 2: Auto-Injection (3 min)

**Purpose**: Verify tokens auto-inject on POST requests

**Steps**:
1. Open Network tab (F12 → Network)
2. Filter by "Fetch/XHR"
3. Create a new project:
   - Click "New Project" button
   - Enter name: "CSRF Test"
   - Click Create
4. In Network tab, find POST to `/api/projects/create`
5. Check Headers → Request Headers

**Expected**:
- ✅ Header: `X-CSRF-Token: [your-token]`
- ✅ Status: 201 Created
- ✅ Project created successfully

---

## Test 3: Token Refresh (3 min)

**Purpose**: Verify auto-refresh on token expiry

```javascript
// Run in console:

// Manually expire token
sessionStorage.setItem('csrf_token_expiry', '0');
console.log('Token expired');

// Try creating a project (via UI)
// Watch console output
```

**Expected**:
- ✅ Console logs: "CSRF token expired, refreshing..."
- ✅ Network shows 2 requests to `/api/csrf-token`
- ✅ Request succeeds after retry

---

## Test 4: Page Refresh (2 min)

**Purpose**: Verify token survives page refresh

```javascript
// Before refresh:
const token1 = sessionStorage.getItem('csrf_token');
console.log('Before:', token1);

// Press F5 to refresh page

// After refresh:
const token2 = sessionStorage.getItem('csrf_token');
console.log('After:', token2);
console.log('Same:', token1 === token2);
```

**Expected**:
- ✅ Token is the same before/after
- ✅ No network request on page load (uses cache)

---

## Test 5: New Tab (2 min)

**Purpose**: Verify token cleared on tab close

**Steps**:
1. Note token: `console.log(sessionStorage.getItem('csrf_token'))`
2. Close tab
3. Open new tab → http://localhost:3000
4. Check token: `console.log(sessionStorage.getItem('csrf_token'))`

**Expected**:
- ✅ Token is `null` in new tab
- ✅ Network request fetches new token

---

## Test 6: GET Skips CSRF (2 min)

**Purpose**: Verify safe methods don't waste tokens

**Steps**:
1. Clear network tab
2. Navigate to project list (triggers GET)
3. Click on project (triggers GET conversations)
4. Check request headers

**Expected**:
- ✅ No `X-CSRF-Token` header on GET requests
- ✅ Requests succeed without token

---

## Troubleshooting

### Token Fetch Fails

```bash
# Check backend is ready:
curl http://localhost:8000/api/csrf-token

# Should return:
# {"csrf_token": "..."}
```

**If fails**:
- Check backend is running: `docker-compose ps`
- Check backend logs: `docker-compose logs backend`
- Check CORS settings allow localhost:3000

### 403 Errors

**Symptoms**: Requests fail with 403 even after retry

**Check**:
1. Backend CSRF middleware is active
2. Token validation logic is correct
3. Header name is `X-CSRF-Token` (case-sensitive)

### Cache Not Working

**Symptoms**: Token fetched on every request

**Check**:
1. SessionStorage is enabled (not disabled in browser)
2. No errors in console
3. Expiry timestamp is valid:
   ```javascript
   const exp = sessionStorage.getItem('csrf_token_expiry');
   console.log('Expiry date:', new Date(parseInt(exp)));
   ```

---

## Quick Health Check

Run this snippet to verify everything works:

```javascript
// Comprehensive CSRF health check
async function csrfHealthCheck() {
  const { csrfClient } = await import('/src/lib/services/api/index.ts');

  console.group('CSRF Health Check');

  // 1. Token fetch
  try {
    const token = await csrfClient.getToken();
    console.log('✅ Token fetch:', token.substring(0, 20) + '...');
  } catch (e) {
    console.error('❌ Token fetch failed:', e);
  }

  // 2. Cache check
  const cached = sessionStorage.getItem('csrf_token');
  console.log(cached ? '✅ Cache working' : '❌ Cache empty');

  // 3. Expiry check
  const expiry = sessionStorage.getItem('csrf_token_expiry');
  const expiryDate = new Date(parseInt(expiry));
  const valid = expiryDate > new Date();
  console.log(valid ? '✅ Token valid' : '❌ Token expired');
  console.log('   Expires:', expiryDate.toLocaleString());

  // 4. Network check
  try {
    const response = await fetch('http://localhost:8000/api/csrf-token');
    console.log(response.ok ? '✅ Endpoint reachable' : '❌ Endpoint error');
  } catch (e) {
    console.error('❌ Network error:', e.message);
  }

  console.groupEnd();
}

// Run health check
csrfHealthCheck();
```

**Expected Output**:
```
CSRF Health Check
  ✅ Token fetch: a1b2c3d4e5f6...
  ✅ Cache working
  ✅ Token valid
     Expires: 11/24/2025, 3:45:00 PM
  ✅ Endpoint reachable
```

---

## Test Results Template

Copy this to report results:

```markdown
## CSRF Frontend Test Results

**Date**: 2025-11-24
**Tester**: [Your Name]
**Environment**: Dev (localhost)

| Test | Status | Notes |
|------|--------|-------|
| Token Fetch | [ ] PASS / [ ] FAIL | |
| Auto-Injection | [ ] PASS / [ ] FAIL | |
| Token Refresh | [ ] PASS / [ ] FAIL | |
| Page Refresh | [ ] PASS / [ ] FAIL | |
| New Tab Clear | [ ] PASS / [ ] FAIL | |
| GET Skips CSRF | [ ] PASS / [ ] FAIL | |

**Issues Found**:
-

**Screenshots**:
- Network tab: [link]
- Console output: [link]

**Overall Status**: [ ] READY FOR QA / [ ] NEEDS FIXES
```

---

**Testing Checklist**:
- [ ] All 6 tests passed
- [ ] No console errors
- [ ] Network tab shows correct headers
- [ ] Token persists across refresh
- [ ] Token cleared on tab close
- [ ] Screenshots captured

**Next Step**: Report results to PM-Architect-Agent
