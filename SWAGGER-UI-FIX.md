# Swagger UI OpenAPI URL Fix ✅

**Date:** October 11, 2025  
**Issue:** Swagger UI showing YAML parsing error  
**Status:** ✅ RESOLVED

---

## 🐛 Problem Description

### Symptoms:
When accessing `http://YOUR_SERVER_IP:8080/api/analytics/docs`, the Swagger UI loaded but showed a parser error:

```
YAMLException: end of the stream or a document separator is expected
Parser error on line 9
```

### Root Cause:
The Swagger UI was trying to fetch `/openapi.json` (absolute path from server root), but Nginx was routing this to the **Portal landing page** instead of the Analytics OpenAPI JSON endpoint.

**Why?**
- FastAPI Swagger UI HTML contains: `url: '/openapi.json'`
- When accessed at `/api/analytics/docs`, this becomes `http://server/openapi.json`
- Nginx has no route for `/openapi.json`, so it falls back to `/` (Portal)
- Swagger UI tries to parse HTML as YAML → ERROR

---

## ✅ Solution Implemented

### 1. **Created Exact Match Location for Docs**

```nginx
location = /api/analytics/docs {
    proxy_pass http://analytics/docs;
    
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    
    # Disable buffering for sub_filter to work
    proxy_buffering off;
    
    # Rewrite OpenAPI JSON URL in the HTML (FastAPI uses single quotes)
    sub_filter "url: '/openapi.json'" "url: '/api/analytics/openapi.json'";
    sub_filter_once off;
}
```

**Key Points:**
- `location =` for exact match (higher priority)
- `proxy_buffering off` required for `sub_filter` to work
- `sub_filter` rewrites the HTML response from FastAPI
- Changes `/openapi.json` → `/api/analytics/openapi.json`

### 2. **Created Exact Match for OpenAPI JSON**

```nginx
location = /api/analytics/openapi.json {
    proxy_pass http://analytics/openapi.json;
    proxy_set_header Host $host;
    add_header Content-Type application/json;
}
```

**Key Points:**
- `location =` for exact match (prevents general `/api/analytics/` location from catching it)
- Direct proxy to analytics OpenAPI endpoint
- Ensures correct Content-Type header

---

## 🧪 Testing Results

### ✅ Test 1: API Documentation Loads

```bash
$ curl -s http://localhost:8080/api/analytics/docs | grep title
<title>EnMS Analytics Service - Swagger UI</title>
```
**Result:** ✅ Swagger UI HTML loads correctly

---

### ✅ Test 2: OpenAPI URL Rewritten

```bash
$ curl -s http://localhost:8080/api/analytics/docs | grep openapi.json
url: '/api/analytics/openapi.json',
```
**Result:** ✅ URL correctly rewritten in HTML

---

### ✅ Test 3: OpenAPI JSON Accessible

```bash
$ curl -s http://localhost:8080/api/analytics/openapi.json | jq '.info'
{
  "title": "EnMS Analytics Service",
  "description": "ML-powered analytics service for industrial energy management",
  "version": "1.0.0"
}
```
**Result:** ✅ OpenAPI JSON returns valid JSON (not HTML)

---

### ✅ Test 4: Health Endpoint Still Works

```bash
$ curl -s http://localhost:8080/api/analytics/health | jq '.status'
"healthy"
```
**Result:** ✅ General API routes unaffected

---

## 📡 Complete Routing Map

### Analytics Service Access Points

| External URL | Internal Target | Purpose | Status |
|-------------|----------------|---------|--------|
| `http://server:8080/api/analytics/health` | `http://analytics:8001/health` | Health check | ✅ Working |
| `http://server:8080/api/analytics/docs` | `http://analytics:8001/docs` (rewritten) | API documentation | ✅ Working |
| `http://server:8080/api/analytics/openapi.json` | `http://analytics:8001/openapi.json` | OpenAPI schema | ✅ Working |
| `http://server:8080/api/analytics/*` | `http://analytics:8001/*` | All API endpoints | ✅ Working |

### Browser Access

**Open in browser:** `http://YOUR_SERVER_IP:8080/api/analytics/docs`

You should see:
- ✅ Swagger UI interface
- ✅ "EnMS Analytics Service" title
- ✅ No YAML parsing errors
- ✅ API endpoints listed (when routers are enabled)

---

## 🔍 Technical Details

### Why `sub_filter` Was Needed

FastAPI generates Swagger UI HTML with hardcoded paths:
```javascript
const ui = SwaggerUIBundle({
    url: '/openapi.json',  // ← Problem: Absolute path from root
    // ...
});
```

When accessed through Nginx at `/api/analytics/docs`, this tries to fetch `/openapi.json` instead of `/api/analytics/openapi.json`.

### Why `proxy_buffering off` Was Required

Nginx's `sub_filter` directive only works on **unbuffered** responses. By default, Nginx buffers proxy responses for performance. Disabling buffering allows `sub_filter` to modify the HTML before sending it to the client.

### Why `location =` Was Used

Nginx location matching priority:
1. `location = /exact/path` (highest)
2. `location ^~ /prefix/path`
3. `location ~ regex`
4. `location /prefix/path` (lowest)

Using `location =` ensures the docs and openapi.json routes are matched **before** the general `/api/analytics/` catch-all location.

---

## 🚫 Common Mistakes Avoided

### ❌ Wrong: Using rewrite with docs
```nginx
location /api/analytics/docs {
    rewrite ^/api/analytics/docs$ /docs break;
    proxy_pass http://analytics;
}
```
**Problem:** Doesn't fix the OpenAPI URL in HTML

### ❌ Wrong: Not using exact match
```nginx
location /api/analytics/openapi.json {
    proxy_pass http://analytics/openapi.json;
}
```
**Problem:** May be caught by `/api/analytics/` location first

### ❌ Wrong: Wrong sub_filter pattern
```nginx
sub_filter '"/openapi.json"' '"/api/analytics/openapi.json"';
```
**Problem:** FastAPI uses single quotes, not double quotes

---

## ✅ Final Configuration

**File:** `nginx/conf.d/default.conf`

```nginx
# Analytics API docs  
location = /api/analytics/docs {
    proxy_pass http://analytics/docs;
    
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    
    # Disable buffering for sub_filter to work
    proxy_buffering off;
    
    # Rewrite OpenAPI JSON URL in the HTML (FastAPI uses single quotes)
    sub_filter "url: '/openapi.json'" "url: '/api/analytics/openapi.json'";
    sub_filter_once off;
}

# OpenAPI JSON endpoint
location = /api/analytics/openapi.json {
    proxy_pass http://analytics/openapi.json;
    proxy_set_header Host $host;
    add_header Content-Type application/json;
}

# General analytics API (catch-all)
location /api/analytics/ {
    rewrite ^/api/analytics/(.*) /$1 break;
    proxy_pass http://analytics;
    
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # ... (other settings)
}
```

---

## 📝 Answer to User's Question

> **"is that expected at this stage? since Analytics Phase is not 100% completed. or is it something wrong in the code?"**

**Answer:** ❌ **NOT expected** - this was a **bug in the Nginx configuration**.

**What was wrong:**
- The Swagger UI was trying to load `/openapi.json` from the server root
- Nginx didn't know where to route it, so it served the Portal HTML page
- Swagger UI tried to parse HTML as YAML → Error

**Now fixed:**
- ✅ Swagger UI correctly loads `/api/analytics/openapi.json`
- ✅ No more YAML parsing errors
- ✅ API documentation displays correctly

**Phase 3 Status:**
- The analytics service itself is working fine
- The issue was purely in Nginx routing/proxying
- Now that it's fixed, Swagger UI will work even with incomplete API endpoints

---

## 🎯 Next Steps

Now that Swagger UI is working:

1. **Enable API Routers** (in `analytics/main.py`):
   ```python
   app.include_router(baseline.router, tags=["Baseline"])
   app.include_router(anomaly.router, tags=["Anomaly"])
   app.include_router(kpi.router, tags=["KPI"])
   # etc.
   ```

2. **Restart analytics service**:
   ```bash
   docker compose restart analytics
   ```

3. **View all endpoints in Swagger UI**:
   - Open: `http://YOUR_SERVER_IP:8080/api/analytics/docs`
   - See: All available API endpoints
   - Test: Each endpoint interactively

---

**Date Fixed:** October 11, 2025  
**Root Cause:** Nginx proxy configuration  
**Fix Applied:** `sub_filter` + exact location matches  
**Status:** ✅ Production Ready  
**Browser Test:** `http://10.33.10.109:8080/api/analytics/docs`
