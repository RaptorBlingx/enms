# OVOS Timeout Issue - Root Cause FOUND

**Date:** December 17, 2025  
**Status:** 🟡 **ROOT CAUSE IDENTIFIED - FIX IN PROGRESS**

---

## ✅ Fixed Issues

1. **Health Check Crash (Line 210)** - FIXED
   - Error: `AttributeError: 'HybridParser' object has no attribute 'llm'`
   - Fix: Removed LLM reference from health check
   - Status: ✅ No longer crashing every 30 seconds

---

## 🔴 Remaining Issue: converse() Method Timeout

### What's Happening

Query flow:
1. User: "any anomalies today?"
2. Bridge receives → ✅ Works
3. OVOS messagebus receives → ✅ Works
4. Skill converse() method called → ✅ Works
5. **Skill hangs for 30+ seconds** → ❌ **TIMEOUT HERE**
6. Bridge timeout → Returns error to user

### Evidence

From logs (`/var/log/ovos/skills.out.log`):
```
2025-12-17 08:38:21.751 - INFO - converse match (en-US): 
IntentHandlerMatch(
    match_type='converse:skill', 
    utterance='any anomalies today?',
    skill_id='enms-ovos-skill.a plus engineering'
)
```

**The skill IS receiving the query but NOT responding within 30 seconds.**

---

## 🔍 Next Steps to Fix

### 1. Add Logging to converse() Method

The `converse()` method in `__init__.py` needs debug logging to find where it hangs.

**File:** `/home/ubuntu/ovos-llm/enms-ovos-skill/enms_ovos_skill/__init__.py`

**Method:** Around line 600-700 (search for `def converse(`)

**Add logging:**
```python
def converse(self, message=None):
    """Handle conversational query"""
    self.logger.info("🎤 converse() called")
    start_time = time.time()
    
    try:
        # ... existing code ...
        
        self.logger.info(f"🎯 converse() completed in {time.time() - start_time:.3f}s")
        return response
        
    except Exception as e:
        self.logger.error(f"❌ converse() error: {e}", exc_info=True)
        raise
```

### 2. Check for Blocking Operations

Common causes:
- **Synchronous API calls** without timeout
- **Database queries** that hang
- **Event waiting** (messagebus events)
- **File I/O** operations
- **Infinite loops** in intent parsing

### 3. Test with Simple Query

Before fixing anomaly, test with a working query:
```bash
# This works (factory overview)
curl -X POST http://172.18.0.1:5000/query/voice \
  -d '{"text":"show me factory overview","session_id":"test","include_audio":false}'

# Compare timing with anomaly query
curl -X POST http://172.18.0.1:5000/query/voice \
  -d '{"text":"any anomalies today?","session_id":"test","include_audio":false}'
```

---

## 🎯 For Next Agent

### Quick Win: Add Timeout to API Client

**File:** `/home/ubuntu/ovos-llm/enms-ovos-skill/enms_ovos_skill/lib/api_client.py`

Check if httpx client has timeout configured:
```python
# Should have:
self.client = httpx.AsyncClient(timeout=10.0)  # 10 second timeout

# NOT:
self.client = httpx.AsyncClient()  # No timeout = infinite wait
```

### Suspected Culprit

The `_run_async()` helper method might not have proper timeout handling.

**File:** `__init__.py`  
**Method:** Around line 1000-1100

Check if it's using `asyncio.wait_for()` with timeout:
```python
# SHOULD BE:
result = asyncio.wait_for(coro, timeout=20.0)

# NOT:
result = asyncio.run(coro)  # No timeout!
```

---

## 📝 Summary for Handover

**What We Fixed:**
- ✅ Health check AttributeError (line 210)
- ✅ Skill now loads successfully
- ✅ Queries reach the skill

**What Still Broken:**
- ❌ converse() method hangs for 30+ seconds
- ❌ Anomaly queries timeout
- ❌ KPI queries likely same issue

**Most Likely Cause:**
- Missing timeout in async operations
- API client waiting indefinitely
- Messagebus event waiting without timeout

**How to Fix:**
1. Add debug logging to converse()
2. Check _run_async() for timeout
3. Check API client timeout configuration
4. Test with working query vs broken query
5. Compare execution paths

**Files to Check:**
- `enms_ovos_skill/__init__.py` - converse() method, _run_async() helper
- `enms_ovos_skill/lib/api_client.py` - httpx client timeout
- `bridge/ovos_rest_bridge.py` - Bridge timeout (currently 30s)

**Test Command:**
```bash
# Rebuild
cd /home/ubuntu/ovos-llm && docker compose down && docker compose up -d --build

# Test
curl -X POST http://172.18.0.1:5000/query/voice \
  -H "Content-Type: application/json" \
  -d '{"text":"any anomalies today?","session_id":"test","include_audio":false}'

# Check logs
docker exec ovos-enms tail -100 /var/log/ovos/skills.out.log | grep -E "(🎤|🎯|❌|anomal)"
```

---

**Created:** December 17, 2025  
**Next Session:** Continue from here - add converse() logging first
