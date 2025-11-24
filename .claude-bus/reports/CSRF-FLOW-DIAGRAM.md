# CSRF Token Flow Diagram

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Application                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              App Startup (+layout.svelte)                │  │
│  │                                                           │  │
│  │   onMount() ──► preloadCsrfToken()                       │  │
│  │                      │                                    │  │
│  │                      ▼                                    │  │
│  │                csrfClient.getToken()                     │  │
│  │                      │                                    │  │
│  │                      ├─► Check in-memory cache           │  │
│  │                      │   (valid? → return)               │  │
│  │                      │                                    │  │
│  │                      ├─► Check sessionStorage            │  │
│  │                      │   (valid? → restore → return)     │  │
│  │                      │                                    │  │
│  │                      └─► Fetch from backend              │  │
│  │                          (/api/csrf-token)               │  │
│  │                          │                                │  │
│  │                          ▼                                │  │
│  │                      Save to cache                        │  │
│  │                      - Memory: token + expiry             │  │
│  │                      - SessionStorage: token + expiry     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              User Action (e.g., Create Project)           │  │
│  │                                                           │  │
│  │   projects.createProject(name)                           │  │
│  │        │                                                  │  │
│  │        ▼                                                  │  │
│  │   apiRequest('/api/projects/create', {                   │  │
│  │     method: 'POST',                                       │  │
│  │     body: JSON.stringify({ name })                        │  │
│  │   })                                                      │  │
│  │        │                                                  │  │
│  │        ▼                                                  │  │
│  │   ┌─────────────────────────────────────────┐            │  │
│  │   │ Is method POST/PUT/DELETE/PATCH?        │            │  │
│  │   └─────────────────────────────────────────┘            │  │
│  │        │                  │                               │  │
│  │     YES │               NO │ (GET/HEAD/OPTIONS)           │  │
│  │        │                  └─► Send request (no CSRF)      │  │
│  │        ▼                                                  │  │
│  │   csrfClient.getToken()                                  │  │
│  │        │                                                  │  │
│  │        ▼                                                  │  │
│  │   Add header: X-CSRF-Token: [token]                      │  │
│  │        │                                                  │  │
│  │        ▼                                                  │  │
│  │   fetch(url, options)                                    │  │
│  │        │                                                  │  │
│  │        ├─► 2xx Success ───► Return response              │  │
│  │        │                                                  │  │
│  │        ├─► 403 + "CSRF" error                            │  │
│  │        │        │                                         │  │
│  │        │        ▼                                         │  │
│  │        │   csrfClient.refreshToken()                     │  │
│  │        │        │                                         │  │
│  │        │        ├─► Clear cache                          │  │
│  │        │        └─► Fetch new token                      │  │
│  │        │             │                                    │  │
│  │        │             ▼                                    │  │
│  │        │        Retry request (ONCE)                     │  │
│  │        │             │                                    │  │
│  │        │             ├─► Success ───► Return             │  │
│  │        │             └─► Fail ──────► Error              │  │
│  │        │                                                  │  │
│  │        └─► Other errors ───► Error handling              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Backend API                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  GET /api/csrf-token                                             │
│    ├─► Generate random token                                    │
│    ├─► Store in session                                         │
│    └─► Return {"csrf_token": "..."}                             │
│                                                                  │
│  POST/PUT/DELETE/PATCH /api/*                                   │
│    ├─► Extract X-CSRF-Token header                              │
│    ├─► Validate against session token                           │
│    ├─► Match? ──► Process request                               │
│    └─► No match? ──► 403 {"detail": "CSRF validation failed"}   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Token Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                        Token Lifecycle                           │
└─────────────────────────────────────────────────────────────────┘

  App Load
     │
     ▼
  ┌─────────────────┐
  │ Token Missing?  │
  └─────────────────┘
     │         │
  YES│      NO │
     │         └─► Check Expiry
     │                 │
     │              VALID│    EXPIRED│
     │                 │         │
     ▼                 ▼         ▼
  Fetch from ◄────────────── Fetch from
  Backend                      Backend
     │                           │
     └───────────┬───────────────┘
                 │
                 ▼
         ┌──────────────┐
         │ Cache Token  │
         │ - Memory     │
         │ - Session    │
         └──────────────┘
                 │
                 ▼
         ┌──────────────┐
         │ Set Expiry   │
         │ (now + 1hr)  │
         └──────────────┘
                 │
                 ▼
         ┌──────────────┐
         │ Ready to Use │
         └──────────────┘
                 │
                 ├─► API Requests (use cached token)
                 │
                 ├─► Page Refresh (restore from sessionStorage)
                 │
                 ├─► 1 hour passes (auto-fetch new token)
                 │
                 └─► Tab Close (clear sessionStorage)
```

---

## Cache Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                     Cache Hierarchy                              │
└─────────────────────────────────────────────────────────────────┘

  Request Token
       │
       ▼
  ┌──────────────────────┐
  │ L1: In-Memory Cache  │  ◄─── Fastest (~0.5ms)
  │ - this.token         │
  │ - this.tokenExpiry   │
  └──────────────────────┘
       │ MISS
       ▼
  ┌──────────────────────┐
  │ L2: SessionStorage   │  ◄─── Fast (~1-2ms)
  │ - csrf_token         │
  │ - csrf_token_expiry  │
  └──────────────────────┘
       │ MISS
       ▼
  ┌──────────────────────┐
  │ L3: Backend API      │  ◄─── Slow (~50-100ms)
  │ GET /api/csrf-token  │
  └──────────────────────┘
       │
       ▼
  Update All Caches
  (L1 + L2)
```

---

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Error Handling Strategy                       │
└─────────────────────────────────────────────────────────────────┘

  API Request
       │
       ▼
  ┌──────────────────────┐
  │ Response Status?     │
  └──────────────────────┘
       │
       ├─► 2xx Success ───────────► Return Data
       │
       ├─► 403 Forbidden
       │     │
       │     ├─► Error contains "CSRF"?
       │     │        │
       │     │     YES│    NO│
       │     │        │      └─► Standard 403 Error
       │     │        │
       │     │        ▼
       │     │   ┌───────────────────┐
       │     │   │ Refresh Token     │
       │     │   │ (csrfClient       │
       │     │   │  .refreshToken()) │
       │     │   └───────────────────┘
       │     │        │
       │     │        ▼
       │     │   ┌───────────────────┐
       │     │   │ Retry Request     │
       │     │   │ (with new token)  │
       │     │   └───────────────────┘
       │     │        │
       │     │        ├─► Success ───► Return Data
       │     │        └─► Fail ──────► Error Toast
       │     │
       │     └─► Show Error Toast
       │
       ├─► 4xx/5xx Errors ────────► Error Toast + Throw
       │
       └─► Network Error ─────────► Error Toast + Throw
```

---

## Multi-Tab Behavior

```
┌─────────────────────────────────────────────────────────────────┐
│                     Multi-Tab Scenarios                          │
└─────────────────────────────────────────────────────────────────┘

  TAB 1                  TAB 2                  TAB 3
    │                      │                      │
    ├─► Load App          │                      │
    │   Fetch Token        │                      │
    │   Cache: Token A     │                      │
    │                      │                      │
    │                      ├─► Load App          │
    │                      │   Use Cache: Token A │
    │                      │   (from session)     │
    │                      │                      │
    │                      │                      ├─► Load App
    │                      │                      │   Use Cache: Token A
    │                      │                      │   (from session)
    │                      │                      │
    ├─► API Request        │                      │
    │   Use Token A        │                      │
    │                      │                      │
    │                      ├─► API Request        │
    │                      │   Use Token A        │
    │                      │                      │
    │                      │                      ├─► API Request
    │                      │                      │   Use Token A
    │                      │                      │
    ├─► Token Expires      │                      │
    │   Fetch Token B      │                      │
    │   Update Cache       │                      │
    │                      │                      │
    │                      ├─► API Request        │
    │                      │   Still uses Token A │ ◄─ Independent cache
    │                      │   (not synced)       │
    │                      │                      │
    │                      │   Token Expires      │
    │                      │   Fetch Token C      │
    │                      │   Update Cache       │
    │                      │                      │
    ├─► Close Tab          │                      │
    │   (cache persists)   │                      │
    │                      │                      │
    │                      ├─► Close Tab          │
    │                      │   (cache persists)   │
    │                      │                      │
    │                      │                      ├─► Close Tab
    │                      │                      │   (cache cleared)
    │                      │                      │
    │                      │                      ├─► Open New Tab
    │                      │                      │   Cache EMPTY
    │                      │                      │   Fetch Token D
```

**Key Points**:
- ✅ Each tab has independent cache (no sync)
- ✅ SessionStorage shared across tabs (same token initially)
- ✅ Tokens diverge after first refresh in each tab
- ✅ Cache cleared when ALL tabs closed

---

## Security Threat Model

```
┌─────────────────────────────────────────────────────────────────┐
│                      Threat Analysis                             │
└─────────────────────────────────────────────────────────────────┘

  ┌───────────────────────────────────────────────────────────┐
  │ Attack: CSRF (Cross-Site Request Forgery)                 │
  ├───────────────────────────────────────────────────────────┤
  │ Scenario: Attacker tricks user into submitting form       │
  │ Mitigation: ✅ Token required on all state-changing reqs  │
  │ Status: PROTECTED                                         │
  └───────────────────────────────────────────────────────────┘

  ┌───────────────────────────────────────────────────────────┐
  │ Attack: XSS (Cross-Site Scripting)                        │
  ├───────────────────────────────────────────────────────────┤
  │ Scenario: Attacker injects JS to steal token from storage │
  │ Mitigation: ⚠️ CSP headers, input sanitization           │
  │ Status: PARTIALLY PROTECTED (depends on CSP)             │
  └───────────────────────────────────────────────────────────┘

  ┌───────────────────────────────────────────────────────────┐
  │ Attack: Man-in-the-Middle (MITM)                          │
  ├───────────────────────────────────────────────────────────┤
  │ Scenario: Attacker intercepts token in transit            │
  │ Mitigation: ✅ HTTPS only in production                   │
  │ Status: PROTECTED (with HTTPS)                           │
  └───────────────────────────────────────────────────────────┘

  ┌───────────────────────────────────────────────────────────┐
  │ Attack: Token Replay                                      │
  ├───────────────────────────────────────────────────────────┤
  │ Scenario: Attacker reuses stolen token                    │
  │ Mitigation: ⚠️ 1-hour expiry, session binding            │
  │ Status: PARTIALLY PROTECTED (short window)               │
  └───────────────────────────────────────────────────────────┘
```

---

## Performance Metrics

```
┌─────────────────────────────────────────────────────────────────┐
│                    Performance Profile                           │
└─────────────────────────────────────────────────────────────────┘

  Cache Hit/Miss Rates:

    First Load:      MISS (fetch from backend)  ~100ms
    2nd Request:     HIT  (in-memory cache)     ~0.5ms  ◄── 200x faster
    Page Refresh:    HIT  (sessionStorage)      ~2ms    ◄── 50x faster
    After 1 Hour:    MISS (expired)             ~100ms
    New Tab:         MISS (empty cache)         ~100ms

  Network Overhead:

    Tokens/Session:  1-2 fetches per hour
    Bandwidth:       ~200 bytes/fetch
    Total/Session:   ~400 bytes (negligible)

  Storage Usage:

    In-Memory:       128 bytes (2 strings)
    SessionStorage:  128 bytes (2 entries)
    Total:           256 bytes (negligible)
```

---

**End of Diagram Documentation**
