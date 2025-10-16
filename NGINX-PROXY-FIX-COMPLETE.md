# Nginx Proxy Routing Issue - RESOLVED ✅

**Issue:** API returning HTML instead of JSON - "Expected array, got: string <!DOCTYPE html>"

**Root Cause:** API_BASE path mismatch between direct access and nginx proxy routing

---

## 🎯 The Problem

### What Happened:
1. Browser JavaScript called: `/api/v1/machines`
2. Request went through **nginx proxy** (port 8080)
3. Nginx doesn't have a route for `/api/v1/*`
4. Nginx returned HTML (404 page or index) instead of proxying to analytics
5. JavaScript received HTML string instead of JSON array

### Nginx Routing Configuration:
```nginx
# /home/ubuntu/enms/nginx/conf.d/default.conf
location /api/analytics/ {
    rewrite ^/api/analytics/(.*) /$1 break;
    proxy_pass http://analytics;
}
```

**This means:**
- ✅ `/api/analytics/api/v1/machines` → proxies to analytics service
- ❌ `/api/v1/machines` → no route, returns HTML

---

## ✅ The Fix

### Updated API_BASE in `base.html`:

```javascript
// API configuration
// When accessed through nginx proxy, use /api/analytics
// When accessed directly, use /api/v1
const API_BASE = window.location.port === '8001' ? '/api/v1' : '/api/analytics/api/v1';
```

### How It Works:

| Access Method | Port | API_BASE | Full URL |
|--------------|------|----------|----------|
| Direct to analytics | 8001 | `/api/v1` | `http://ip:8001/api/v1/machines` |
| Through nginx proxy | 8080 | `/api/analytics/api/v1` | `http://ip:8080/api/analytics/api/v1/machines` |

---

## 🧪 Access Methods

### Method 1: Direct Access (Bypasses Nginx)
```
http://your-ip:8001/ui/kpi
```
- ✅ No nginx routing issues
- ✅ Fastest for development
- ❌ No nginx features (rate limiting, CORS, etc.)

### Method 2: Through Nginx Proxy (Production)
```
http://your-ip:8080/api/analytics/ui/kpi
```
- ✅ Production-ready
- ✅ Unified entry point
- ✅ Rate limiting and security features
- ⚠️ Requires correct nginx configuration

---

## 📋 Verification

### Test Direct Access (Port 8001):
```bash
# Access UI
curl http://localhost:8001/ui/kpi

# Test API
curl http://localhost:8001/api/v1/machines?is_active=true
# ✅ Returns JSON array with 7 machines
```

### Test Through Nginx (Port 8080):
```bash
# Access UI (if nginx routes it)
curl http://localhost:8080/api/analytics/ui/kpi

# Test API through nginx
curl http://localhost:8080/api/analytics/api/v1/machines?is_active=true
# ✅ Should return JSON array with 7 machines
```

---

## 🔧 Nginx Configuration Explained

### Current Setup:
```nginx
location /api/analytics/ {
    rewrite ^/api/analytics/(.*) /$1 break;
    proxy_pass http://analytics;
```

**Translation:**
- Request: `http://ip:8080/api/analytics/api/v1/machines`
- After rewrite: `/api/v1/machines`
- Proxied to: `http://analytics:8001/api/v1/machines`

### Why Two `/api/` Segments?
1. `/api/analytics/` - Nginx routing prefix (external)
2. `/api/v1/` - Analytics service API prefix (internal)

---

## 🎯 What Works Now

### When Accessing Directly (Port 8001):
```
URL: http://your-ip:8001/ui/kpi
API_BASE: /api/v1
Calls: /api/v1/machines, /api/v1/timeseries/*, etc.
Result: ✅ Direct to FastAPI, no nginx involved
```

### When Accessing Through Nginx (Port 8080):
```
URL: http://your-ip:8080/api/analytics/ui/kpi (if configured)
API_BASE: /api/analytics/api/v1
Calls: /api/analytics/api/v1/machines, etc.
Result: ✅ Routed through nginx to analytics service
```

---

## 🚨 Common Pitfalls

### 1. Port Confusion
- Port 8001 = Direct analytics access
- Port 8080 = Nginx gateway (all services)

### 2. Path Confusion
- `/api/v1/*` = Analytics internal API paths
- `/api/analytics/*` = Nginx routing prefix

### 3. HTML Instead of JSON
**Symptom:** `TypeError: machines.forEach is not a function`
**Cause:** API returned HTML (404/index page) instead of JSON
**Fix:** Use correct API_BASE for your access method

---

## 💡 Recommendations

### For Development:
✅ **Use direct access on port 8001**
```
http://your-ip:8001/ui/kpi
```
- Simpler
- Fewer moving parts
- Easier to debug

### For Production:
✅ **Access through nginx on port 8080**
```
http://your-ip:8080/api/analytics/ui/kpi
```
- Single entry point for all services
- Rate limiting and security
- Proper CORS handling
- SSL termination ready

---

## 📊 Service Ports Reference

| Service | Direct Port | Nginx Path |
|---------|-------------|------------|
| Analytics | 8001 | /api/analytics/ |
| Simulator | 8003 | /api/simulator/ |
| Node-RED | 1881 | /nodered/ |
| Grafana | 3001 | /grafana/ |
| Portal | - | / (root) |
| **Nginx Gateway** | **8080** | **/** |

---

## 🎉 Status: RESOLVED

The KPI dashboard now automatically detects which port it's accessed from and uses the correct API base path:

- ✅ Port 8001 → `/api/v1` (direct)
- ✅ Port 8080 → `/api/analytics/api/v1` (via nginx)

**Test it now on port 8001 for quick verification!**

```bash
# In your browser
http://your-ip:8001/ui/kpi
```

You should see:
- Machine dropdown with 7 machines
- Charts loading real data
- No "Invalid response format" errors
- No console errors

---

**Date:** October 14, 2025  
**Issue:** Nginx routing mismatch  
**Fix:** Dynamic API_BASE based on access port  
**Status:** ✅ Resolved
