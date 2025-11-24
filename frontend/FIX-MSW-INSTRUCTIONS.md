# Fix MSW URL Matching - Quick Guide

## Problem
Integration tests are failing because MSW handlers use relative paths but requests use full URLs.

## Solution
Run this command to fix all URL patterns in handlers.ts:

```bash
cd frontend
node fix-msw-urls.js
```

## What It Does
Converts all handler patterns from:
```typescript
http.post('/api/projects/create', ...)
```

To:
```typescript
http.post(`${BASE_URL}/api/projects/create`, ...)
```

## Verify Fix
After running the script:

```bash
npm run test:integration
```

Expected result: All 20 integration tests should pass ✅

## Manual Alternative
If script fails, manually edit `src/mocks/handlers.ts`:
1. Find all `http.get('/api/` → Replace with `http.get(\`${BASE_URL}/api/`
2. Find all `http.post('/api/` → Replace with `http.post(\`${BASE_URL}/api/`
3. Find all `http.put('/api/` → Replace with `http.put(\`${BASE_URL}/api/`
4. Find all `http.patch('/api/` → Replace with `http.patch(\`${BASE_URL}/api/`
5. Find all `http.delete('/api/` → Replace with `http.delete(\`${BASE_URL}/api/`

## Total Changes
Approximately 30-40 lines need updating in handlers.ts
