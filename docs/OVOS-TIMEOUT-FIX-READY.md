# OVOS Timeout Issue - ROOT CAUSE & FIX

**Date:** 2025-12-17  
**Status:** ✅ ROOT CAUSE IDENTIFIED | 🔧 FIX READY TO APPLY

---

## 🎯 ROOT CAUSE

**Problem:** Skill timeout (45s) exceeds bridge timeout (30s)

**Location:** `/home/ubuntu/ovos-llm/enms-ovos-skill/enms_ovos_skill/__init__.py` line 273

```python
def _run_async(self, coro, timeout_seconds: float = 45.0):  # ❌ 45s is too long!
```

**Why This Causes "Connection Error":**

1. User asks: "any anomalies today?"
2. Bridge sends query to skill via messagebus
3. Skill `converse()` → `_process_query()` → `_call_enms_api()`
4. `_call_enms_api()` calls `_run_async(api_client.get_recent_anomalies())`
5. `_run_async()` waits up to **45 seconds** for response
6. **Bridge only waits 30 seconds** then returns "Connection error" to portal
7. Skill still processing in background (wasting resources)

**Timeline:**
```
T+0ms:    User query received
T+50ms:   Skill converse() called
T+100ms:  _run_async() starts waiting
...
T+30000ms: Bridge timeout → Returns "Connection error" ❌
...  
T+45000ms: Skill timeout (too late, bridge already gave up)
```

---

## ✅ Architecture Validation (OVOS Official Docs)

Fetched official OVOS documentation:
- **converse() method:** [502-converse](https://openvoiceos.github.io/ovos-technical-manual/502-converse/) - IS OFFICIAL ✅
- **@intent_handler decorator:** [401-skill_structure](https://openvoiceos.github.io/ovos-technical-manual/401-skill_structure/) - IS OFFICIAL ✅
- **Hybrid approach (converse + intent handlers):** VALID PATTERN ✅

**Conclusion:** Your architecture is correct. Problem is purely timeout mismatch.

---

## 🔧 THE FIX

### Change Required

**File:** `/home/ubuntu/ovos-llm/enms-ovos-skill/enms_ovos_skill/__init__.py`  
**Line:** 273

```python
# OLD (45 seconds - TOO LONG):
def _run_async(self, coro, timeout_seconds: float = 45.0):

# NEW (20 seconds - leaves 10s buffer):
def _run_async(self, coro, timeout_seconds: float = 20.0):
```

**Rationale:**
- Bridge waits 30s for complete response
- Skill should timeout at 20s to return error **before** bridge timeout
- Leaves 10s buffer for processing + response formatting
- API endpoints tested at <300ms, so 20s is very generous

---

## 📊 Expected Behavior After Fix

### Scenario 1: Fast API (<10s) - Most Common
```
User: "any anomalies today?"
Skill: Calls API → receives data in 500ms
Bridge: Receives response in 1s total
Portal: Shows anomaly data ✅
```

### Scenario 2: Slow API (10-20s) - Rare
```
User: "any anomalies today?"
Skill: Calls API → waits 15s (slow network)
Bridge: Receives response in 16s total
Portal: Shows anomaly data ✅
```

### Scenario 3: Timeout at Skill (20-30s) - Graceful Error
```
User: "any anomalies today?"
Skill: Timeout at 20s → returns error message
Bridge: Receives error response in 21s
Portal: Shows "API took too long, please try again" ✅
Better than silent timeout!
```

### Scenario 4: Both timeout (>30s) - Same as before
```
User: "any anomalies today?"
Skill: Timeout at 20s, tries to send error
Bridge: Timeout at 30s anyway
Portal: Shows "Connection error" ⚠️
(Same as before, but skill logged timeout for debugging)
```

---

## 🧪 Testing Plan

### Step 1: Apply Fix
```bash
cd /home/ubuntu/ovos-llm/enms-ovos-skill
# Edit line 273 in enms_ovos_skill/__init__.py
# Change 45.0 → 20.0
```

### Step 2: Rebuild Container
```bash
cd /home/ubuntu/ovos-llm
docker compose down
docker compose up -d --build
# Wait 20 seconds for skill to load
```

### Step 3: Test Queries
```bash
# Test previously failing queries
curl -X POST http://172.18.0.1:5000/query/voice \
  -H "Content-Type: application/json" \
  -d '{"text":"any anomalies today?","session_id":"test1","include_audio":false}'

curl -X POST http://172.18.0.1:5000/query/voice \
  -H "Content-Type: application/json" \
  -d '{"text":"Show me KPIs for Compressor-1 today","session_id":"test2","include_audio":false}'
```

**Expected:** Both should return within 20-25 seconds (not 30+)

### Step 4: Check Logs
```bash
docker exec ovos-enms tail -f /var/log/ovos/skills.out.log | grep -E "converse|timeout|async_operation"
```

**Expected:** Should see either:
- Response within 20s (success) ✅
- "async_operation_timeout" at ~20s (graceful timeout) ✅

---

## 📝 Additional Verification (Optional)

### Check API Client Timeout

**File:** `/home/ubuntu/ovos-llm/enms-ovos-skill/enms_ovos_skill/lib/api_client.py`

Should already have:
```python
self.client = httpx.AsyncClient(timeout=10.0)
```

This is **separate** from `_run_async()` timeout:
- `httpx timeout=10.0`: Individual HTTP request max time
- `_run_async timeout=20.0`: Total async operation max time (may include multiple requests)

**If missing:** Add `timeout=10.0` to AsyncClient initialization.

---

## 📂 Files Modified

1. ✅ `/home/ubuntu/ovos-llm/enms-ovos-skill/enms_ovos_skill/__init__.py`
   - Line 210: Health check fix (already applied)
   - Line 273: Timeout reduction (needs apply)

---

## 🔗 References

- **OVOS Converse Docs:** https://openvoiceos.github.io/ovos-technical-manual/502-converse/
- **OVOS Skill Structure:** https://openvoiceos.github.io/ovos-technical-manual/401-skill_structure/
- **OVOS Skills & Intents:** https://openvoiceos.github.io/ovos-technical-manual/399-intents/
- **Bridge Timeout:** `bridge/ovos_rest_bridge.py` ~line 104 (`response_timeout = 30`)

---

## 🎯 Ready to Apply

**Command to execute:**
```bash
cd /home/ubuntu/ovos-llm/enms-ovos-skill
# Use replace_string_in_file tool to change line 273:
# OLD: timeout_seconds: float = 45.0
# NEW: timeout_seconds: float = 20.0
```
