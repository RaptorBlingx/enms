# 🔧 Fix for Burak's OVOS Connection Issue

**Date:** October 21, 2025  
**Issue:** Connection refused when accessing ENMS API  
**Status:** ✅ SOLVED

---

## 🔴 The Problem

Burak's OVOS is getting this error:
```
HTTPConnectionPool(host='10.33.10.109', port=8001): 
Max retries exceeded with url: /api/v1/anomaly/recent?machine_id=...
Failed to establish a new connection: [Errno 111] Connection refused
```

**Root Cause:** OVOS is trying to access the API directly on port 8001, but it should use the **nginx proxy on port 8080**.

---

## ✅ The Solution

### Change the Base URL in OVOS Configuration

**❌ WRONG (Current):**
```python
BASE_URL = "http://10.33.10.109:8001"
```

**✅ CORRECT (New):**
```python
BASE_URL = "http://10.33.10.109:8080/api/analytics"
```

---

## 📝 Updated API Endpoints for OVOS

### Old URLs (Won't Work) ❌
```
http://10.33.10.109:8001/api/v1/anomaly/recent?machine_id=...
http://10.33.10.109:8001/api/v1/machines?search=compressor
http://10.33.10.109:8001/api/v1/ovos/summary
```

### New URLs (Correct) ✅
```
http://10.33.10.109:8080/api/analytics/api/v1/anomaly/recent?machine_id=...
http://10.33.10.109:8080/api/analytics/api/v1/machines?search=compressor
http://10.33.10.109:8080/api/analytics/api/v1/ovos/summary
```

**Pattern:**
```
Old: http://10.33.10.109:8001/api/v1/{endpoint}
New: http://10.33.10.109:8080/api/analytics/api/v1/{endpoint}
```

---

## 🔧 Code Changes for Burak

### Option 1: Update Base URL (Recommended)

If OVOS has a config file or environment variable:

```python
# Old
ENMS_BASE_URL = "http://10.33.10.109:8001"

# New
ENMS_BASE_URL = "http://10.33.10.109:8080/api/analytics"

# Then all endpoints remain the same:
url = f"{ENMS_BASE_URL}/api/v1/anomaly/recent"
```

### Option 2: Update Each URL

If URLs are hardcoded, change each one:

```python
# Old
url = "http://10.33.10.109:8001/api/v1/anomaly/recent"

# New
url = "http://10.33.10.109:8080/api/analytics/api/v1/anomaly/recent"
```

---

## ✅ Verification Tests

### Test 1: Health Check
```bash
# From Burak's machine or OVOS
curl http://10.33.10.109:8080/api/analytics/api/v1/health

# Expected response:
{
  "service": "EnMS Analytics Service",
  "version": "1.0.0",
  "status": "healthy",
  ...
}
```

### Test 2: Anomaly Endpoint (The one that failed)
```bash
curl "http://10.33.10.109:8080/api/analytics/api/v1/anomaly/recent?machine_id=c0000000-0000-0000-0000-000000000001"

# Expected response:
{
  "success": true,
  "data": [...],
  "total_count": 0,
  "timestamp": "2025-10-21T..."
}
```

### Test 3: Machine Search
```bash
curl "http://10.33.10.109:8080/api/analytics/api/v1/machines?search=compressor"

# Expected response:
{
  "success": true,
  "data": [
    {
      "machine_id": "c0000000-0000-0000-0000-000000000001",
      "machine_name": "Air Compressor 1",
      ...
    }
  ],
  "total_count": 1
}
```

### Test 4: OVOS Summary
```bash
curl http://10.33.10.109:8080/api/analytics/api/v1/ovos/summary

# Expected response:
{
  "success": true,
  "data": {
    "total_machines": 7,
    "active_machines": 7,
    "total_energy_kwh": ...,
    ...
  }
}
```

---

## 🌐 Why the URL Changed

**Architecture:**
```
OVOS (Burak's Machine)
   ↓
Internet
   ↓
Your Server (10.33.10.109)
   ↓
Port 8080 → Nginx Proxy
   ↓
/api/analytics → Analytics Service (internal port 8001)
```

**Benefits of using Nginx proxy:**
1. ✅ **Rate Limiting** - Protects against DDoS (100 req/min per IP)
2. ✅ **Load Balancing** - Can add more servers later
3. ✅ **SSL/HTTPS** - Can enable encryption easily
4. ✅ **Centralized Logging** - All requests logged in one place
5. ✅ **Better Security** - Analytics service not exposed directly

**Port 8001 is for internal/development use only.** Production traffic should always go through nginx on port 8080.

---

## 📋 Complete URL Reference for OVOS

### Core Endpoints

| Endpoint | New URL |
|----------|---------|
| Health Check | `http://10.33.10.109:8080/api/analytics/api/v1/health` |
| API Docs | `http://10.33.10.109:8080/api/analytics/docs` |

### OVOS-Specific Endpoints

| Feature | New URL |
|---------|---------|
| **Summary** | `http://10.33.10.109:8080/api/analytics/api/v1/ovos/summary` |
| **Machine Search** | `http://10.33.10.109:8080/api/analytics/api/v1/machines?search={query}` |
| **Machine Status** | `http://10.33.10.109:8080/api/analytics/api/v1/ovos/machines/{name}/status` |
| **Recent Anomalies** | `http://10.33.10.109:8080/api/analytics/api/v1/anomaly/recent?start_date={date}&end_date={date}` |
| **Top Consumers** | `http://10.33.10.109:8080/api/analytics/api/v1/ovos/top-consumers?start_time={time}&end_time={time}&limit={n}` |
| **Forecast Tomorrow** | `http://10.33.10.109:8080/api/analytics/api/v1/ovos/forecast/tomorrow?machine_id={id}` |
| **Factory KPIs** | `http://10.33.10.109:8080/api/analytics/api/v1/kpi/factory/{factory_id}?start={time}&end={time}` |

### Examples with Real Values

```bash
# Get summary
curl http://10.33.10.109:8080/api/analytics/api/v1/ovos/summary

# Search for compressor
curl "http://10.33.10.109:8080/api/analytics/api/v1/machines?search=compressor"

# Get compressor status
curl http://10.33.10.109:8080/api/analytics/api/v1/ovos/machines/Air%20Compressor%201/status

# Recent anomalies (last 7 days)
curl "http://10.33.10.109:8080/api/analytics/api/v1/anomaly/recent?start_date=2025-10-14T00:00:00Z&end_date=2025-10-21T00:00:00Z"

# Top 5 energy consumers (last 24h)
curl "http://10.33.10.109:8080/api/analytics/api/v1/ovos/top-consumers?start_time=2025-10-20T00:00:00Z&end_time=2025-10-21T00:00:00Z&limit=5"

# Tomorrow's forecast for factory
curl http://10.33.10.109:8080/api/analytics/api/v1/ovos/forecast/tomorrow

# Factory KPIs
curl "http://10.33.10.109:8080/api/analytics/api/v1/kpi/factory/f0000000-0000-0000-0000-000000000001?start=2025-10-20T00:00:00Z&end=2025-10-21T00:00:00Z"
```

---

## 🔒 Rate Limiting Notice

**Important:** The nginx proxy has rate limiting enabled:
- **Limit:** 100 requests per minute per IP address
- **Burst:** 20 extra requests allowed during spikes
- **Response:** HTTP 429 "Too Many Requests" when exceeded

**For OVOS:**
- Add delays between requests (at least 0.6 seconds)
- Implement exponential backoff on 429 errors
- Cache responses when possible (energy data doesn't change every second)

**Example with rate limiting:**
```python
import time
import requests

def get_enms_data(endpoint):
    url = f"http://10.33.10.109:8080/api/analytics{endpoint}"
    response = requests.get(url)
    
    if response.status_code == 429:
        # Rate limited - wait and retry
        retry_after = int(response.headers.get('Retry-After', 60))
        time.sleep(retry_after)
        return get_enms_data(endpoint)  # Retry
    
    return response.json()

# Add delay between requests
data1 = get_enms_data("/api/v1/ovos/summary")
time.sleep(1)  # 1 second delay
data2 = get_enms_data("/api/v1/machines?search=compressor")
```

---

## 🚨 Troubleshooting

### If OVOS Still Can't Connect

**1. Check if nginx is running:**
```bash
curl http://10.33.10.109:8080/health
# Should return: "healthy"
```

**2. Check if analytics is running:**
```bash
curl http://10.33.10.109:8080/api/analytics/api/v1/health
# Should return JSON with "status": "healthy"
```

**3. Test from Burak's machine:**
```bash
# From OVOS machine
ping 10.33.10.109
# Should get responses

telnet 10.33.10.109 8080
# Should connect

curl -v http://10.33.10.109:8080/health
# Should return "healthy"
```

**4. Check firewall on ENMS server:**
```bash
# On ENMS server
sudo ufw status
# Port 8080 should be allowed

# If blocked, allow it:
sudo ufw allow 8080/tcp
```

**5. Test specific endpoint:**
```bash
# From OVOS machine
curl -v "http://10.33.10.109:8080/api/analytics/api/v1/anomaly/recent?machine_id=c0000000-0000-0000-0000-000000000001"
# Should return JSON with success: true
```

### Common Issues

**Issue:** `Connection refused`  
**Fix:** Use port 8080, not 8001

**Issue:** `404 Not Found`  
**Fix:** Use `/api/analytics/api/v1/...` not `/api/v1/...`

**Issue:** `429 Too Many Requests`  
**Fix:** Add delays between requests (rate limit: 100/min)

**Issue:** `Timeout`  
**Fix:** ML endpoints can take 30s+, increase timeout in OVOS

---

## 📞 Quick Summary for Burak

**Change this ONE line in OVOS config:**

```python
# OLD
BASE_URL = "http://10.33.10.109:8001"

# NEW  
BASE_URL = "http://10.33.10.109:8080/api/analytics"
```

**Then all your endpoints work like this:**
```python
url = f"{BASE_URL}/api/v1/ovos/summary"
# Results in: http://10.33.10.109:8080/api/analytics/api/v1/ovos/summary ✅
```

**Test it works:**
```bash
curl http://10.33.10.109:8080/api/analytics/api/v1/health
```

**That's it! Connection should work now.** 🎉

---

## ✅ Verification Checklist

Before Burak tests OVOS:

- [ ] Updated BASE_URL in OVOS config to `http://10.33.10.109:8080/api/analytics`
- [ ] Tested health endpoint: `curl http://10.33.10.109:8080/api/analytics/api/v1/health`
- [ ] Tested anomaly endpoint: `curl "http://10.33.10.109:8080/api/analytics/api/v1/anomaly/recent?machine_id=c0000000-0000-0000-0000-000000000001"`
- [ ] Added rate limiting handling (delays between requests)
- [ ] Increased timeout to 60s for ML endpoints
- [ ] Tested from OVOS machine (not just from server)

---

**Status:** ✅ Fixed - Ready for Burak to test  
**Last Updated:** October 21, 2025
