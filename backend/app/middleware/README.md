# Middleware Architecture

## Overview

GPT-OSS uses 4 middleware layers for security, performance, and reliability. This document explains the architecture, execution order, and troubleshooting.

## Middleware Stack

### Execution Order (Request → Response)

```
Incoming Request
    ↓
1. CSRF Protection      ← Validates token (first to execute)
    ↓
2. Request Size Limit   ← Rejects oversized payloads
    ↓
3. Rate Limiting        ← Enforces request limits
    ↓
4. CORS                 ← Handles preflight, adds headers
    ↓
5. Application Routes   ← Business logic
    ↓
6. CORS                 ← Adds response headers
    ↓
7. Rate Limiting        ← Adds X-RateLimit headers
    ↓
8. Request Size Limit   ← (no response processing)
    ↓
9. CSRF Protection      ← (no response processing)
    ↓
Outgoing Response
```

### Registration Order (Reverse of Execution)

In `backend/app/main.py`, middleware is registered in **reverse order** of execution:

```python
# 1. CORS (registered first, executes last on request path)
app.add_middleware(CORSMiddleware, ...)

# 2. Rate Limiting
app.middleware("http")(rate_limit_middleware)

# 3. Request Size Limiting
app.add_middleware(RequestSizeLimitMiddleware, ...)

# 4. CSRF Protection (registered last, executes first on request path)
app.add_middleware(CSRFProtectionMiddleware, ...)
```

**CRITICAL**: This order is validated at startup via `validate_middleware_order()`.

---

## Middleware Layers

### 1. CSRF Protection (First to Execute)

**File**: `csrf_protection.py`
**Purpose**: Prevent Cross-Site Request Forgery attacks

**When**: All POST/PUT/DELETE/PATCH requests
**Exempt**: GET, HEAD, OPTIONS, `/api/csrf-token`, `/health`

**Behavior**:
- Validates `X-CSRF-Token` header using cryptographic signatures
- Returns 403 if token missing/invalid/expired
- Allows token refresh on expiry (1-hour TTL)

**Security Features**:
- Cryptographically signed tokens (prevents forgery)
- Time-limited tokens (prevents replay attacks)
- Header-based transmission (more secure than query params)

**Configuration** (in `app/config.py`):
```python
CSRF_SECRET_KEY: str = "..."           # Change in production!
CSRF_TOKEN_LOCATION: str = "header"
CSRF_HEADER_NAME: str = "X-CSRF-Token"
CSRF_MAX_AGE: int = 3600               # 1 hour
```

---

### 2. Request Size Limiter

**File**: `request_size_limiter.py`
**Purpose**: Prevent DoS attacks via large payloads

**Limits**: 10 MB max request size
**Returns**: 413 Payload Too Large if exceeded

**Why 10MB**:
- Adequate for document uploads (PDFs, Excel, Word)
- Small enough to prevent memory exhaustion attacks
- Configurable via `max_size` parameter

**Implementation**:
```python
app.add_middleware(RequestSizeLimitMiddleware, max_size=10_000_000)
```

---

### 3. Rate Limiter

**File**: `rate_limiter.py`
**Purpose**: Prevent abuse via request flooding

**Limits**:
- Chat endpoints (`/api/chat`): **10 req/min** per IP
- Other endpoints: **60 req/min** per IP

**Returns**: 429 Too Many Requests if exceeded

**Security**:
- IP-based tracking with X-Forwarded-For validation
- Only trusts X-Forwarded-For from known proxies (prevents IP spoofing)
- In-memory storage (resets on restart)
- Periodic cleanup (every 5 minutes) to prevent memory leaks

**Response Headers**:
```
X-RateLimit-Remaining: 45
Retry-After: 60
```

**Configuration** (in `rate_limiter.py`):
```python
self.limits = {
    "/api/chat": (10, 60),        # 10 requests per 60 seconds
    "/api/conversations": (60, 60),
    "/api/projects": (60, 60),
    "/api/messages": (100, 60),
    "default": (100, 60),
}
```

---

### 4. CORS (Last to Execute)

**Library**: FastAPI `CORSMiddleware`
**Purpose**: Allow cross-origin requests from frontend

**Configuration**:
- Allowed origins: `http://localhost:3000`, `http://127.0.0.1:3000`
- Allowed methods: All (`*`)
- Allowed headers: All (`*`)
- Credentials: `True`

**Special Behavior**:
- Handles OPTIONS preflight requests automatically
- Returns `Access-Control-Allow-Origin` header
- Validates origin against whitelist

**Why CORS executes last**:
- OPTIONS preflight requests don't have CSRF tokens
- CORS needs to handle OPTIONS BEFORE CSRF sees them
- If CSRF executed after CORS, it would block OPTIONS requests

---

## Why Order Matters

### CORS MUST come after CSRF (in execution order)

**Scenario**: Browser sends OPTIONS preflight before POST request

#### ✅ Correct Order (CORS registered before CSRF):
```
1. Request: OPTIONS /api/projects/create
2. CSRF middleware: "OPTIONS is safe method, skip validation"
3. CORS middleware: "Handle preflight, return 200 OK with headers"
4. Response: 200 OK ✅
5. Browser sends actual POST request
```

#### ❌ Wrong Order (CSRF registered before CORS):
```
1. Request: OPTIONS /api/projects/create
2. CORS middleware: "Try to handle preflight..."
3. CSRF middleware: "No token! Block with 403"
4. Response: 403 Forbidden ❌
5. Browser never sends POST (preflight failed)
```

### Rate Limiting before CSRF

**Reason**: Cheaper to rate limit than validate tokens

```
✅ Efficient order:
1. Check IP → fast (O(1) hash lookup)
2. If over limit → reject (no expensive token validation)

❌ Inefficient order:
1. Validate token → expensive (cryptographic signature check)
2. Check IP → rate limit after expensive work
```

### Size Limiting before Rate Limiting

**Reason**: Reject oversized requests before counting them

```
✅ Prevents DoS:
1. Check Content-Length → fast
2. If > 10MB → reject (doesn't count against rate limit)

❌ Allows DoS:
1. Count request against rate limit
2. Check size later
3. Attacker can exhaust rate limit with oversized junk
```

---

## Startup Validation

The `validate_middleware_order()` function runs at startup to verify correct order.

**Location**: `backend/app/main.py`

**What it checks**:
1. CSRF middleware is registered
2. CORS middleware is registered
3. CORS is registered BEFORE CSRF (in code)

**Logs**:
```
✅ Middleware order validated: CORS (reg index 0) → CSRF (reg index 3).
   Execution order: CSRF executes first, then CORS handles preflight.
```

**If order is wrong**:
```
❌ MIDDLEWARE ORDER ERROR: CORS (registration index 3) is registered AFTER
   CSRF (registration index 0). This will break CORS preflight requests!
   CORS must be registered BEFORE CSRF in code.
⚠️  APPLICATION MAY NOT WORK CORRECTLY - MIDDLEWARE ORDER ISSUE
```

**Note**: Validation logs errors but doesn't crash the app. Fix the order in `main.py` if you see this error.

---

## Testing Middleware Order

### Test 1: OPTIONS Preflight (Should Pass)

```bash
curl -v -X OPTIONS http://localhost:8000/api/projects/create \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,X-CSRF-Token"
```

**Expected**:
```
< HTTP/1.1 200 OK
< access-control-allow-origin: http://localhost:3000
< access-control-allow-credentials: true
< access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
< access-control-allow-headers: ...
```

**If fails with 403**: CSRF middleware is blocking OPTIONS → middleware order is wrong.

---

### Test 2: POST Without CSRF (Should Fail)

```bash
curl -v -X POST http://localhost:8000/api/projects/create \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:3000" \
  -d '{"name": "Test Project"}'
```

**Expected**:
```
< HTTP/1.1 403 Forbidden
{
  "detail": "CSRF token missing. Include X-CSRF-Token header.",
  "error_type": "csrf_error"
}
```

**If passes**: CSRF middleware is not working → check registration.

---

### Test 3: POST With CSRF (Should Work)

```bash
# Step 1: Get CSRF token
TOKEN=$(curl -s http://localhost:8000/api/csrf-token | jq -r .csrf_token)

# Step 2: Make request with token
curl -v -X POST http://localhost:8000/api/projects/create \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:3000" \
  -H "X-CSRF-Token: $TOKEN" \
  -d '{"name": "Test Project", "description": "Testing CSRF"}'
```

**Expected**:
```
< HTTP/1.1 201 Created
{
  "id": "...",
  "name": "Test Project",
  ...
}
```

**If fails with 403**: Token validation is broken → check CSRF_SECRET_KEY in config.

---

### Test 4: Rate Limiting

```bash
# Send 15 requests rapidly to /api/chat (limit: 10/min)
for i in {1..15}; do
  curl -s -X POST http://localhost:8000/api/chat/chat \
    -H "Content-Type: application/json" \
    -H "X-CSRF-Token: $TOKEN" \
    -d '{"conversation_id": "test", "content": "Hello"}' &
done
wait
```

**Expected**: First 10 succeed, last 5 return:
```
< HTTP/1.1 429 Too Many Requests
< Retry-After: 60
{
  "detail": "Rate limit exceeded. Please try again later.",
  "error_type": "rate_limit_error"
}
```

---

### Test 5: Request Size Limit

```bash
# Create a 15MB payload (exceeds 10MB limit)
python3 -c "print('a' * 15_000_000)" > /tmp/big_payload.json

curl -v -X POST http://localhost:8000/api/projects/create \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: $TOKEN" \
  --data @/tmp/big_payload.json
```

**Expected**:
```
< HTTP/1.1 413 Payload Too Large
{
  "detail": "Request body too large (limit: 10000000 bytes)",
  "error_type": "request_size_error"
}
```

---

## Troubleshooting

### Problem: CORS errors in browser console

**Symptoms**:
```
Access to fetch at 'http://localhost:8000/api/...' from origin
'http://localhost:3000' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

**Possible Causes**:
1. **CORS middleware not registered**
   - Check `main.py` for `app.add_middleware(CORSMiddleware, ...)`
2. **Wrong origin in config**
   - Check `CORS_ORIGINS` in `.env` or `config.py`
   - Should include `http://localhost:3000`
3. **Middleware order wrong**
   - Check startup logs for middleware order validation error
   - CORS must be registered BEFORE CSRF

**Fix**:
```python
# In main.py, ensure CORS is registered BEFORE CSRF
app.add_middleware(CORSMiddleware, ...)  # First
# ... other middleware ...
app.add_middleware(CSRFProtectionMiddleware, ...)  # Last
```

---

### Problem: All requests fail with 403

**Symptoms**: Every POST/PUT/DELETE request returns 403 Forbidden

**Possible Causes**:
1. **No CSRF token sent**
   - Frontend must fetch token from `/api/csrf-token`
   - Include token in `X-CSRF-Token` header
2. **Token expired**
   - Tokens expire after 1 hour
   - Fetch new token if requests start failing
3. **Wrong secret key**
   - Token generated with different secret than validator uses
   - Check `CSRF_SECRET_KEY` is consistent

**Fix**:
```typescript
// Frontend: Fetch token before requests
const tokenResp = await fetch('http://localhost:8000/api/csrf-token');
const { csrf_token } = await tokenResp.json();

// Include in requests
await fetch('http://localhost:8000/api/projects/create', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': csrf_token,
  },
  body: JSON.stringify({ name: 'Project' }),
});
```

---

### Problem: OPTIONS requests fail

**Symptoms**: Browser preflight requests fail with 403

**Cause**: CSRF middleware is blocking OPTIONS before CORS handles them

**Fix**: Ensure CORS middleware is registered BEFORE CSRF in `main.py`

```python
# ✅ Correct order
app.add_middleware(CORSMiddleware, ...)       # First
app.add_middleware(CSRFProtectionMiddleware, ...)  # Last

# ❌ Wrong order
app.add_middleware(CSRFProtectionMiddleware, ...)  # First
app.add_middleware(CORSMiddleware, ...)       # Last
```

---

### Problem: Rate limiting not working

**Symptoms**: Can send 1000s of requests without getting 429

**Possible Causes**:
1. **Middleware not registered**
   - Check for `app.middleware("http")(rate_limit_middleware)` in `main.py`
2. **X-Forwarded-For spoofing**
   - If behind proxy, attacker can spoof IP
   - Update `TRUSTED_PROXIES` in `config.py`

**Fix**:
```python
# config.py
TRUSTED_PROXIES: set = {
    "127.0.0.1",
    "::1",
    "172.18.0.1",  # Docker gateway
    "10.0.0.1",    # Your nginx proxy IP
}
```

---

## Configuration Reference

### Environment Variables

**.env file**:
```bash
# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# CSRF
CSRF_SECRET_KEY=your-secret-key-change-in-production-32-chars-minimum

# Debug (enables verbose logging)
DEBUG=false
```

### Code Configuration

**Rate limits** (in `rate_limiter.py`):
```python
self.limits = {
    "/api/chat": (10, 60),        # 10 req/min
    "/api/conversations": (60, 60),
    "/api/projects": (60, 60),
    "/api/messages": (100, 60),
    "default": (100, 60),
}
```

**Request size limit** (in `main.py`):
```python
app.add_middleware(RequestSizeLimitMiddleware, max_size=10_000_000)  # 10MB
```

**CSRF settings** (in `config.py`):
```python
CSRF_SECRET_KEY: str = "..."
CSRF_TOKEN_LOCATION: str = "header"
CSRF_HEADER_NAME: str = "X-CSRF-Token"
CSRF_MAX_AGE: int = 3600  # 1 hour
```

---

## Security Best Practices

### Production Deployment Checklist

- [ ] Change `CSRF_SECRET_KEY` to a strong random value (32+ characters)
- [ ] Set `DEBUG=false` in production
- [ ] Update `CORS_ORIGINS` to match production frontend domain
- [ ] Add production proxy IPs to `TRUSTED_PROXIES`
- [ ] Monitor rate limiting headers in logs
- [ ] Set up alerts for excessive 403/429 responses
- [ ] Review middleware order validation logs on startup

### Monitoring

**Log queries to check for attacks**:

```bash
# Excessive 403s (CSRF attacks)
grep "403 Forbidden" /var/log/gpt-oss/backend.log | wc -l

# Excessive 429s (DoS attempts)
grep "429 Too Many Requests" /var/log/gpt-oss/backend.log | wc -l

# Failed CSRF validations
grep "CSRF: Token validation failed" /var/log/gpt-oss/backend.log
```

---

## Performance Considerations

### Memory Usage

**Rate Limiter**:
- In-memory storage grows with number of unique IPs
- Periodic cleanup runs every 5 minutes
- Each IP entry: ~200 bytes
- 10,000 IPs = ~2 MB memory (acceptable)

**CSRF Tokens**:
- Stateless (no server-side storage)
- Cryptographically signed
- Memory usage: negligible

### Latency

**Overhead per request**:
- CSRF validation: ~0.5ms (cryptographic check)
- Rate limiting: ~0.1ms (hash lookup)
- Request size check: ~0.05ms (header check)
- CORS: ~0.2ms (header processing)

**Total middleware overhead**: ~1ms per request (negligible)

---

## Future Improvements (Stage 2+)

- [ ] Redis-based rate limiting (distributed, multi-instance)
- [ ] Sliding window rate limiting (more accurate)
- [ ] Per-user rate limits (after authentication)
- [ ] Rate limit response headers (X-RateLimit-Limit, X-RateLimit-Reset)
- [ ] IP reputation scoring (auto-ban malicious IPs)
- [ ] Web Application Firewall (WAF) rules
- [ ] DDoS mitigation (challenge-response)

---

## References

- [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [FastAPI Middleware Documentation](https://fastapi.tiangolo.com/tutorial/middleware/)
- [CORS Specification](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [Rate Limiting Algorithms](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)
