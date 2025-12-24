# OVOS Integration - Reality Check & Fix Plan

**Date:** December 17, 2025  
**Status:** 🔴 **CRITICAL ISSUES FOUND**

---

## 🎯 Current Situation

### What's Working ✅
- **Infrastructure**: OVOS bridge, nginx routing, containers - ALL GOOD
- **API Endpoints**: Anomaly, KPI, Forecast endpoints **EXIST and WORK**
- **Simple Queries**: "top energy consumers", "factory overview" - **WORKING**

### What's Broken ❌
- **Anomaly Query**: "any anomalies today?" → **TIMEOUT (30+ seconds)**
- **KPI Query**: "Show me KPIs for Compressor-1 today" → **TIMEOUT**
- **Forecast Query**: "Forecast Compressor-1 next 4 hours" → **Wrong intent routing**

---

## 🔍 Root Cause Analysis

### Issue #1: Skill Processing TIMEOUTS

**Evidence:**
```bash
# Nginx logs show upstream timeout:
2025/12/17 08:11:50 [error] upstream timed out (110: Operation timed out)

# Direct OVOS bridge test:
$ curl http://172.18.0.1:5000/query/voice -d '{"text":"any anomalies today?",...}'
{"success":false,"response":"Sorry, I didn't receive a response in time..."}
```

**What's Happening:**
1. User: "any anomalies today?"
2. Heuristic: Matches `anomaly_detection` intent ✅
3. Skill handler calls: `api_client.get_recent_anomalies()` ✅
4. API returns data instantly (tested: <100ms) ✅
5. **SOMEWHERE in the skill, processing hangs** ❌
6. Bridge timeout: 30 seconds → returns timeout error
7. Nginx timeout: 30 seconds → HTML error page

**Possible Causes:**
- Skill handler has infinite loop or blocking call
- Response formatting stuck
- Entity extraction hanging
- Database call in skill (shouldn't exist)
- LLM fallback being triggered unnecessarily

### Issue #2: Intent Routing Problems

**Query:** "Forecast energy demand for Compressor-1 next 4 hours"

**What Should Happen:**
- Intent: `FORECAST` with machine + time_range
- Time: Extract "next 4 hours" → `{hours: 4}`
- Machine: Extract "Compressor-1" → Find ID
- Call: `/api/v1/forecast/short-term?machine_id=xxx&hours=4`

**What's Happening:**
- Intent: Generic `FORECAST` without proper entity extraction
- Machine: Extracted but not validated/used
- Time: "next 4 hours" not recognized
- Call: Wrong endpoint or wrong parameters
- Result: Factory-wide forecast instead of machine-specific

---

## 📊 API vs Skill Comparison

### What The Skill Expects (api_client.py)

| Intent | Method | Endpoint Called | Status |
|--------|--------|----------------|---------|
| anomaly_detection | `get_recent_anomalies()` | `GET /anomaly/recent` | ✅ Exists |
| anomaly_detection | `get_active_anomalies()` | `GET /anomaly/active` | ✅ Exists |
| kpi | `get_all_kpis()` | `GET /kpi/all` | ✅ Exists |
| forecast | `forecast_demand()` | `GET /forecast/demand` | ✅ Exists |
| forecast | `get_forecast()` | `GET /forecast/short-term` | ✅ Exists |

**Conclusion:** **ALL API ENDPOINTS EXIST!** The problem is NOT missing endpoints.

### API Test Results

```bash
# Anomaly endpoint - WORKS
$ curl http://172.18.0.1:8001/api/v1/anomaly/recent?limit=5
{"total_count": 0, "filters": {...}, "anomalies": []}
→ ✅ 200 OK, <100ms

# KPI endpoint - WORKS  
$ curl "http://172.18.0.1:8001/api/v1/kpi/all?machine_id=c0...001&start=...&end=..."
{"machine_id": "c0...001", "kpis": {...}}
→ ✅ 200 OK, <200ms

# Forecast endpoint - WORKS
$ curl http://172.18.0.1:8001/api/v1/forecast/short-term
{"forecast": [...]}
→ ✅ 200 OK, <300ms
```

---

## 🚨 The Real Problem

**This is NOT an API problem. This is a SKILL LOGIC problem.**

The skill is:
1. **Timing out** on certain intents (anomaly, KPI)
2. **Routing incorrectly** on others (forecast)
3. **Spending too much time** processing responses

### Diagnostic Test Plan

1. **Add Logging to Skill Handlers**
   - Log when intent handler starts
   - Log API request being made
   - Log API response received
   - Log response formatting
   - Log final output
   - **Find where the 30+ second delay happens**

2. **Test Each Handler Independently**
   - Import skill class
   - Call handler directly with mock intent
   - Measure time at each step
   - Identify the bottleneck

3. **Check Intent Routing**
   - Log heuristic matches
   - Log entity extraction results
   - Log which handler is called
   - Verify correct flow

---

## 🛠️ Fix Strategy

### Phase 1: Diagnose Timeout (URGENT - 2-4 hours)

**Goal:** Find where the 30+ second delay occurs

**Tasks:**
1. Add debug logging to skill `__init__.py` handlers
2. Add timing measurements (`time.time()` before/after each step)
3. Run failing queries and capture logs
4. Identify the blocking operation

**Files to Check:**
- `/home/ubuntu/ovos-llm/enms-ovos-skill/enms_ovos_skill/__init__.py`
  - Lines 1420-1500: Anomaly detection handler
  - Lines for KPI handler
- `/home/ubuntu/ovos-llm/enms-ovos-skill/enms_ovos_skill/lib/api_client.py`
  - Async operations - are they being awaited correctly?

**Expected Findings:**
- Handler not returning response
- Infinite loop in response formatting
- Blocking I/O operation
- LLM fallback being triggered (300-500ms but shouldn't happen)

### Phase 2: Fix Intent Routing (HIGH - 4-6 hours)

**Goal:** Machine-specific queries route to correct handlers with correct parameters

**Tasks:**
1. Audit heuristic patterns in `intent_parser.py`
2. Add time range extraction for "next X hours"
3. Validate machine entity extraction
4. Add entity usage validation in handlers
5. Test forecast queries

**Files to Modify:**
- `/home/ubuntu/ovos-llm/enms-ovos-skill/enms_ovos_skill/lib/heuristic_router.py`
- `/home/ubuntu/ovos-llm/enms-ovos-skill/enms_ovos_skill/lib/time_parser.py`
- `/home/ubuntu/ovos-llm/enms-ovos-skill/enms_ovos_skill/__init__.py` (handlers)

### Phase 3: Comprehensive Testing (MEDIUM - 6-8 hours)

**Goal:** 95%+ accuracy across all intent types

**Tasks:**
1. Create test query dataset (50-100 queries)
2. Run systematic tests
3. Measure accuracy and latency
4. Document failures
5. Iterate fixes

**Reference:** Use structure from `docs/1by1.md` test protocol

---

## 📝 Immediate Next Steps

### Step 1: Add Debug Logging (30 minutes)

Add comprehensive logging to skill handlers:

```python
# In enms_ovos_skill/__init__.py

elif intent.intent == IntentType.ANOMALY_DETECTION:
    logger.info(f"🔍 ANOMALY_DETECTION handler started")
    start_time = time.time()
    
    logger.info(f"📞 Calling API: get_recent_anomalies()")
    api_start = time.time()
    data = self._run_async(self.api_client.get_recent_anomalies(...))
    api_duration = time.time() - api_start
    logger.info(f"✅ API returned in {api_duration:.2f}s: {len(data.get('anomalies', []))} anomalies")
    
    logger.info(f"🎨 Formatting response...")
    format_start = time.time()
    response = self._format_anomaly_response(data)
    format_duration = time.time() - format_start
    logger.info(f"✅ Response formatted in {format_duration:.2f}s")
    
    total_duration = time.time() - start_time
    logger.info(f"🎯 Total handler time: {total_duration:.2f}s")
    
    return response
```

### Step 2: Test and Capture Logs (15 minutes)

```bash
# Restart container to pick up logging
cd /home/ubuntu/ovos-llm
docker compose down
docker compose up -d

# Wait for startup
sleep 10

# Test anomaly query
curl -X POST http://172.18.0.1:5000/query/voice \
  -H "Content-Type: application/json" \
  -d '{"text":"any anomalies today?","session_id":"debug1","include_audio":false}'

# Capture logs
docker logs ovos-enms --tail 200 | grep -E "(🔍|📞|✅|🎨|🎯|ERROR|TIMEOUT)"
```

### Step 3: Analyze and Fix (2-3 hours)

Based on log output:
- If API call is fast but formatting is slow → Fix formatter
- If API call never completes → Fix async/await
- If handler never returns → Fix control flow
- If LLM is being called → Fix heuristic patterns

---

## 🎯 Success Criteria

**When are we done?**

1. ✅ "any anomalies today?" returns in <2 seconds
2. ✅ "Show me KPIs for Compressor-1 today" returns in <3 seconds  
3. ✅ "Forecast Compressor-1 next 4 hours" returns machine-specific 4-hour forecast
4. ✅ All intent types have <5 second response time (95th percentile)
5. ✅ 95%+ intent accuracy on test dataset

---

## 🧪 Test Commands

### Working Queries (Baseline)
```bash
# Factory overview - WORKS
curl -X POST http://172.18.0.1:5000/query/voice \
  -d '{"text":"show me factory overview","session_id":"test1","include_audio":false}'
→ Should return in <1 second

# Top consumers - WORKS  
curl -X POST http://172.18.0.1:5000/query/voice \
  -d '{"text":"top energy consumers","session_id":"test2","include_audio":false}'
→ Should return in <1 second
```

### Failing Queries (TO FIX)
```bash
# Anomaly - TIMEOUT
curl -X POST http://172.18.0.1:5000/query/voice \
  -d '{"text":"any anomalies today?","session_id":"test3","include_audio":false}'
→ Currently: 30+ second timeout
→ Expected: <2 seconds

# KPI - TIMEOUT
curl -X POST http://172.18.0.1:5000/query/voice \
  -d '{"text":"Show me KPIs for Compressor-1 today","session_id":"test4","include_audio":false}'
→ Currently: 30+ second timeout  
→ Expected: <3 seconds

# Forecast - WRONG INTENT
curl -X POST http://172.18.0.1:5000/query/voice \
  -d '{"text":"Forecast energy demand for Compressor-1 next 4 hours","session_id":"test5","include_audio":false}'
→ Currently: Returns factory-wide forecast
→ Expected: Returns Compressor-1 4-hour forecast
```

---

## 📚 Key Files Reference

### Skill Logic
- **Main handlers:** `/home/ubuntu/ovos-llm/enms-ovos-skill/enms_ovos_skill/__init__.py`
- **Intent parser:** `/home/ubuntu/ovos-llm/enms-ovos-skill/enms_ovos_skill/lib/intent_parser.py`
- **Heuristic router:** `/home/ubuntu/ovos-llm/enms-ovos-skill/enms_ovos_skill/lib/heuristic_router.py`
- **API client:** `/home/ubuntu/ovos-llm/enms-ovos-skill/enms_ovos_skill/lib/api_client.py`
- **Models:** `/home/ubuntu/ovos-llm/enms-ovos-skill/enms_ovos_skill/lib/models.py`

### API Documentation
- **Complete API reference:** `/home/ubuntu/humanergy/docs/api-documentation/ENMS-API-DOCUMENTATION-FOR-OVOS.md`
- **Endpoints confirmed working:**
  - `GET /api/v1/anomaly/recent` ✅
  - `GET /api/v1/anomaly/active` ✅
  - `GET /api/v1/kpi/all` ✅
  - `GET /api/v1/forecast/short-term` ✅

### Testing
- **Test protocol:** `/home/ubuntu/humanergy/docs/test-protocol.md.instructions.md`
- **1by1 test plan:** `/home/ubuntu/humanergy/docs/1by1.md` (if exists)

---

## 🔧 Tools for Debugging

```bash
# Check skill logs
docker logs ovos-enms --tail 200 -f

# Check nginx logs  
docker logs enms-nginx --tail 100 | grep error

# Check analytics logs
docker logs enms-analytics --tail 100

# Test API directly
curl http://172.18.0.1:8001/api/v1/anomaly/recent?limit=5

# Test OVOS bridge directly
curl -X POST http://172.18.0.1:5000/query/voice \
  -H "Content-Type: application/json" \
  -d '{"text":"test query","session_id":"debug","include_audio":false}'

# Check container status
docker ps | grep -E "(ovos|enms)"

# Restart OVOS container
cd /home/ubuntu/ovos-llm && docker compose restart
```

---

## 💡 Key Insights

1. **API is NOT the problem** - All endpoints exist and work fast (<300ms)
2. **Skill processing is the bottleneck** - 30+ second timeouts
3. **Some intents work perfectly** - Factory overview, top consumers
4. **Others timeout completely** - Anomalies, KPIs  
5. **Intent routing needs work** - Machine-specific queries failing

**Conclusion:** This is a **skill code quality issue**, not an integration issue. The infrastructure is solid, but the skill handlers need debugging and optimization.

---

**Next Action:** Add debug logging to skill handlers and capture timeout location.

**Priority:** 🔥 **URGENT** - Blocking all anomaly/KPI queries
