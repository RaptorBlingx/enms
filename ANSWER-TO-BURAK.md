# Answer to Burak's Connection Issue

**Date:** October 21, 2025  
**Issue:** "Connection refused" error on port 8001

---

## 🔍 What's Happening

Your error shows:
```
port=8001: Connection refused
```

**This is NOT the rate limiting we just added.** If it was rate limiting, you'd get:
- HTTP 429 "Too Many Requests" error
- A response from the server (not connection refused)

**This IS a network/configuration issue** - you're trying to connect to the wrong URL.

---

## ❌ The Problem

You're using:
```
http://10.33.10.109:8001
```

Port 8001 is blocked for external access (firewall/network policy). It's only for internal/development use.

---

## ✅ The Solution

You need to change your **base URL** in your OVOS skill configuration.

### Find This in Your Code:

Look for where you initialize the API client. It might be in:
- `__init__.py`
- A config file (`.env`, `config.yaml`, `settings.py`)
- The skill's configuration

It will look something like:
```python
self.base_url = "http://10.33.10.109:8001"
# or
API_URL = "http://10.33.10.109:8001"
# or
self.api_client = SomeClient(base_url="http://10.33.10.109:8001")
```

### Change It To:

```python
self.base_url = "http://10.33.10.109:8080/api/analytics"
```

---

## 📝 Code Changes Needed

### Your Current Code:
```python
@intent_handler("GetRecentAnomalies.intent")
def handle_get_recent_anomalies(self, _: Message) -> None:
    """Get recent anomalies."""
    payload, error = self._get_json("/anomaly/recent?machine_id=c0000000-0000-0000-0000-000000000001")
    # ...
```

This calls `self._get_json()` which must use a base URL somewhere.

### Find Where Base URL is Set:

Look for the `_get_json()` method definition or the class `__init__()`:

```python
class YourSkill:
    def __init__(self):
        self.base_url = "http://10.33.10.109:8001"  # ❌ CHANGE THIS
        # ...
    
    def _get_json(self, endpoint):
        url = f"{self.base_url}/api/v1{endpoint}"  # Builds full URL
        response = requests.get(url)
        # ...
```

### Change To:

```python
class YourSkill:
    def __init__(self):
        self.base_url = "http://10.33.10.109:8080/api/analytics"  # ✅ CORRECT
        # ...
    
    def _get_json(self, endpoint):
        url = f"{self.base_url}/api/v1{endpoint}"  # Now builds correct URL
        # Results in: http://10.33.10.109:8080/api/analytics/api/v1/anomaly/recent
        response = requests.get(url)
        # ...
```

---

## 🧪 Test It

After changing the base URL, test from your OVOS machine:

```bash
# Test health endpoint
curl http://10.33.10.109:8080/api/analytics/api/v1/health

# Should return:
{
  "service": "EnMS Analytics Service",
  "status": "healthy",
  ...
}
```

If that works, your OVOS skill will work too!

---

## 📋 Complete URL Mapping

When you use `self._get_json("/anomaly/recent?...")`:

| Your Code | Old URL (Broken) | New URL (Working) |
|-----------|------------------|-------------------|
| `/anomaly/recent` | `http://10.33.10.109:8001/api/v1/anomaly/recent` ❌ | `http://10.33.10.109:8080/api/analytics/api/v1/anomaly/recent` ✅ |
| `/machines?search=X` | `http://10.33.10.109:8001/api/v1/machines?search=X` ❌ | `http://10.33.10.109:8080/api/analytics/api/v1/machines?search=X` ✅ |
| `/ovos/summary` | `http://10.33.10.109:8001/api/v1/ovos/summary` ❌ | `http://10.33.10.109:8080/api/analytics/api/v1/ovos/summary` ✅ |

---

## ❓ Why This Change?

**Port 8001** is for direct access (blocked by firewall for security)

**Port 8080** is the nginx proxy that provides:
- ✅ Security (firewall allows it)
- ✅ Rate limiting (protects server from overload)
- ✅ Load balancing (can add more servers)
- ✅ Logging (centralized request logs)

**You were working 30 minutes ago** because either:
1. You were testing from the server itself (localhost works)
2. The firewall rule was just applied
3. Network policy changed

---

## 🎯 TL;DR for Burak

1. Find where you set `base_url` in your OVOS skill code
2. Change from `http://10.33.10.109:8001` to `http://10.33.10.109:8080/api/analytics`
3. Save and restart your OVOS skill
4. Test again

**That's it!** The error will disappear.

---

## 📞 If Still Not Working

If you still get errors after changing the URL:

1. **Test connectivity from your machine:**
   ```bash
   curl http://10.33.10.109:8080/api/analytics/api/v1/health
   ```

2. **Check if you can reach the server:**
   ```bash
   ping 10.33.10.109
   ```

3. **Check if port 8080 is open:**
   ```bash
   telnet 10.33.10.109 8080
   ```

4. **Share the new error message** - it will be different from "Connection refused"

---

**Status:** ✅ Solution ready - waiting for Burak to update base URL
