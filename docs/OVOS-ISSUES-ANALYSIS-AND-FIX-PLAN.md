# OVOS Integration Issues - Analysis & Fix Plan

**Date:** December 17, 2025  
**Status:** ❌ **4 Critical Issues Identified**

---

## 🔍 Issue Summary

Based on user testing, we have 4 distinct problems:

| Query | Expected | Actual | Status |
|-------|----------|--------|--------|
| "top energy consumers" | ✅ List of top consumers | ✅ Correct list | **WORKING** |
| "any anomalies today?" | List of today's anomalies | "Connection error" | ❌ **BROKEN** |
| "Forecast Compressor-1 next 4 hours" | 4-hour forecast for Compressor-1 | Tomorrow's factory-wide forecast | ❌ **WRONG INTENT** |
| "Show me KPIs for Compressor-1 today" | KPI metrics for Compressor-1 | "Connection error" | ❌ **BROKEN** |

---

## 🔴 ISSUE #1 & #4: Connection Errors (Anomalies & KPIs)

### Root Cause

**API Endpoints Don't Exist!**

The skill is trying to call endpoints that aren't implemented in the analytics API:

```python
# Skill tries to call:
GET /api/v1/anomaly/recent  ❌ 404 Not Found
GET /api/v1/anomaly/active  ❌ 404 Not Found  
GET /api/v1/kpis/{machine_id}  ❌ 404 Not Found (guessing based on pattern)
```

### Evidence

```bash
$ curl http://172.18.0.1:8001/api/v1/anomaly/recent
{"detail": "Not Found"}

$ curl http://172.18.0.1:8001/api/v1/anomalies/today
{"detail": "Not Found"}
```

### Documented API Endpoints (from ENMS-API-DOCUMENTATION-FOR-OVOS.md)

Looking at the attached documentation, the anomaly endpoints ARE documented:
- `GET /api/v1/anomaly/recent` - Get recent anomalies
- `POST /api/v1/anomaly/detect` - Run anomaly detection
- `GET /api/v1/anomaly/active` - Get active/unresolved anomalies

**BUT** these endpoints might not be implemented in the actual analytics service!

### Fix Options

**Option A: Implement Missing Endpoints (Recommended)**
```python
# In analytics/api/routes/anomaly.py or create new file
@router.get("/anomaly/recent")
async def get_recent_anomalies(
    hours: int = 24,
    severity: Optional[str] = None,
    machine_id: Optional[str] = None
):
    # Query anomalies table
    # Return last N hours of anomalies
    pass

@router.get("/anomaly/active")
async def get_active_anomalies():
    # Query unresolved anomalies
    pass
```

**Option B: Use Existing Endpoints**
Check if there are alternative endpoints that provide this data:
- `/api/v1/analytics/anomalies` ?
- `/api/v1/factory/summary` (has anomaly count but not details)

**Option C: Disable These Features Temporarily**
Update skill to gracefully handle missing endpoints with better error messages.

---

## 🔴 ISSUE #2: Wrong Forecast Intent

### The Problem

**Query:** "Forecast energy demand for Compressor-1 next 4 hours"

**Expected Behavior:**
- Intent: `short_term_forecast` or `machine_forecast`
- Machine: "Compressor-1"
- Time range: next 4 hours
- API call: `GET /api/v1/forecast/short-term?machine_id={id}&hours=4`

**Actual Behavior:**
- Intent: `long_term_forecast` or `general_forecast`
- Machine: ❌ Not extracted or ignored
- Time range: ❌ "next 4 hours" not recognized
- API call: `GET /api/v1/forecast/tomorrow` (factory-wide)
- Response: Tomorrow's factory forecast (wrong!)

### Root Cause Analysis

1. **Intent Classification Failure**
   - Heuristic patterns didn't match "next 4 hours" as short-term
   - "forecast" keyword matched long-term forecast pattern
   - Machine name "Compressor-1" extracted but not used

2. **Entity Extraction Issues**
   - Time range "next 4 hours" not parsed correctly
   - Should extract: `{hours: 4, relative: "next"}`
   - Entity validator might be failing

3. **Intent Routing Logic**
   - Skill defaulted to factory-wide forecast when machine-specific fails
   - No validation that machine entity is actually used

### Fix Plan

#### Step 1: Fix Heuristic Patterns

```python
# In enms_ovos_skill/lib/heuristic_router.py

# CURRENT (probably):
r'\b(?:forecast|predict|anticipate)\b.*\b(?:tomorrow|next\s+(?:week|month))\b'

# SHOULD BE:
r'\b(?:forecast|predict|anticipate)\b.*\b(?:next\s+\d+\s+hours?|next\s+few\s+hours)\b'  # short-term
r'\b(?:forecast|predict|anticipate)\b.*\b(?:tomorrow|next\s+(?:day|week|month))\b'  # long-term
```

#### Step 2: Improve Entity Extraction

```python
# In enms_ovos_skill/lib/entity_extractor.py

# Add time range extraction for "next X hours":
time_range_pattern = r'next\s+(\d+)\s+(hour|day|week)s?'
# Extract: {"value": 4, "unit": "hours", "relative": "next"}
```

#### Step 3: Add Intent Validation

```python
# In enms_ovos_skill/__init__.py

if intent.intent == IntentType.SHORT_TERM_FORECAST:
    if not intent.machine:
        # Upgrade to machine forecast needed
        return {'error': 'Please specify which machine to forecast'}
    
    if not intent.time_range or not intent.time_range.hours:
        # Default to 4 hours if not specified
        hours = 4
    else:
        hours = intent.time_range.hours
    
    data = self._run_async(
        self.api_client.get_short_term_forecast(
            machine_id=machine_id,
            hours=hours
        )
    )
```

---

## 🎯 Comprehensive Fix Strategy

### Phase 1: Fix API Endpoints (Critical - Day 1)

**Priority:** 🔥 **HIGH** - Blocking user queries

1. ✅ Check which endpoints exist in analytics
2. ❌ Implement missing endpoints:
   - `GET /api/v1/anomaly/recent`
   - `GET /api/v1/anomaly/active`
   - `GET /api/v1/kpis/{machine_id}` (if needed)
3. ✅ Test endpoints with curl
4. ✅ Update skill to use correct endpoints

**Files to Modify:**
- `humanergy/analytics/api/routes/anomaly.py` (create if doesn't exist)
- `humanergy/analytics/main.py` (register router)

**Estimated Time:** 4-6 hours

---

### Phase 2: Fix Intent Classification (High - Day 1-2)

**Priority:** 🔶 **HIGH** - Wrong responses confuse users

1. ✅ Audit heuristic patterns for forecast intents
2. ✅ Add time range patterns ("next 4 hours", "next few hours")
3. ✅ Improve entity extraction for relative time
4. ✅ Add validation that machine entities are used when present
5. ✅ Test with comprehensive query set

**Files to Modify:**
- `ovos-llm/enms-ovos-skill/enms_ovos_skill/lib/heuristic_router.py`
- `ovos-llm/enms-ovos-skill/enms_ovos_skill/lib/entity_extractor.py`
- `ovos-llm/enms-ovos-skill/enms_ovos_skill/__init__.py` (handler validation)

**Estimated Time:** 6-8 hours

---

### Phase 3: Comprehensive Testing (Day 2-3)

**Priority:** 🔷 **MEDIUM** - Prevent regressions

1. ✅ Create test query dataset (50-100 queries)
2. ✅ Run queries through skill
3. ✅ Log intent classification results
4. ✅ Measure accuracy (target: 95%+)
5. ✅ Document edge cases
6. ✅ Create regression test suite

**Reference:** Use `docs/1by1.md` test plan structure

**Estimated Time:** 8-12 hours

---

### Phase 4: Error Handling Improvements (Day 3)

**Priority:** 🔵 **LOW** - Nice to have

1. ✅ Better error messages ("Anomaly detection not available" instead of "Connection error")
2. ✅ Graceful degradation (suggest alternatives)
3. ✅ User-friendly responses

**Estimated Time:** 2-4 hours

---

## 📊 Detailed Analysis of Each Issue

### Issue #1: "any anomalies today?" → Connection Error

**Skill Logic Flow:**
```
1. User: "any anomalies today?"
2. Heuristic: Match "anomaly" keyword → IntentType.ANOMALY_DETECTION
3. Entity: time_range="today"
4. Handler: Calls self.api_client.get_recent_anomalies(hours=24)
5. API Client: GET /api/v1/anomaly/recent
6. Response: 404 Not Found
7. Exception: httpx.HTTPStatusError
8. Catch: Return "Connection error" generic message
```

**Fix:**
```python
# In analytics/api/routes/anomaly.py
@router.get("/anomaly/recent")
async def get_recent_anomalies(
    hours: int = Query(24, description="Hours to look back"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    machine_id: Optional[str] = Query(None, description="Filter by machine")
):
    """Get recent anomalies from anomalies table"""
    query = """
        SELECT 
            a.id,
            a.machine_id,
            m.machine_name,
            a.timestamp,
            a.severity,
            a.anomaly_score,
            a.metric_name,
            a.expected_value,
            a.actual_value,
            a.status
        FROM anomalies a
        JOIN machines m ON a.machine_id = m.id
        WHERE a.timestamp > NOW() - INTERVAL '%s hours'
    """
    if severity:
        query += f" AND a.severity = '{severity}'"
    if machine_id:
        query += f" AND a.machine_id = '{machine_id}'"
    query += " ORDER BY a.timestamp DESC LIMIT 50"
    
    # Execute query and return results
    # ...
```

---

### Issue #4: "Show me KPIs for Compressor-1 today" → Connection Error

**Similar to Issue #1** - API endpoint doesn't exist.

**Check if endpoint exists:**
```bash
curl http://172.18.0.1:8001/api/v1/kpis?machine_id=xxx
curl http://172.18.0.1:8001/api/v1/machines/{id}/kpis
```

**If not, implement:**
```python
@router.get("/machines/{machine_id}/kpis")
async def get_machine_kpis(
    machine_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Calculate KPIs for specific machine
    - Energy efficiency
    - Utilization rate  
    - Cost per unit
    - Performance index
    """
    # Call existing calculate_kpis function
    # Return formatted results
```

---

### Issue #2: Forecast Query Mismatch

**Detailed Flow:**
```
1. User: "Forecast energy demand for Compressor-1 next 4 hours"

2. Heuristic Router:
   Pattern matched: r'\bforecast\b'
   No specific "short-term" or "next X hours" pattern
   → Classified as: general_forecast or long_term_forecast ❌

3. Entity Extractor:
   Machine: "Compressor-1" ✅ EXTRACTED
   Time: "next 4 hours" ❌ NOT EXTRACTED (only handles "tomorrow", "next week")
   
4. Intent Handler:
   Intent: long_term_forecast
   Machine: "Compressor-1" (present but ignored)
   Logic: if intent == long_term_forecast → get_tomorrow_forecast()
   
5. API Call:
   GET /api/v1/forecast/tomorrow
   → Returns factory-wide forecast ❌ WRONG

6. Response Formatter:
   Uses tomorrow's factory data
   Ignores machine entity
   → "Tomorrow's factory-wide forecast is..." ❌ WRONG
```

**What SHOULD Happen:**
```
1. User: "Forecast energy demand for Compressor-1 next 4 hours"

2. Heuristic Router:
   Pattern: r'forecast.*next\s+(\d+)\s+hours?' 
   → Classified as: SHORT_TERM_FORECAST ✅

3. Entity Extractor:
   Machine: "Compressor-1" ✅
   Time: {hours: 4, relative: "next"} ✅
   
4. Intent Handler:
   Intent: SHORT_TERM_FORECAST
   Machine: Find ID for "Compressor-1"
   
5. API Call:
   GET /api/v1/forecast/short-term?machine_id={id}&hours=4
   → Returns 4-hour forecast for Compressor-1 ✅

6. Response Formatter:
   "Compressor-1 is forecast to consume X kWh over the next 4 hours..." ✅
```

---

## 🛠️ Implementation Checklist

### Immediate Actions (Today)

- [ ] Check which anomaly endpoints exist in analytics
- [ ] Check which KPI endpoints exist
- [ ] Implement missing endpoints (or find alternatives)
- [ ] Test endpoints with curl
- [ ] Restart analytics service
- [ ] Test problematic queries again

### Short-term (This Week)

- [ ] Audit all heuristic patterns in skill
- [ ] Add short-term forecast patterns
- [ ] Improve time range entity extraction
- [ ] Add entity validation in handlers
- [ ] Create test query dataset
- [ ] Run comprehensive testing

### Long-term (Next Week)

- [ ] Implement full test suite (like 1by1.md)
- [ ] Document all supported query patterns
- [ ] Add error message improvements
- [ ] Performance optimization
- [ ] User feedback collection

---

## 📝 Next Steps

**Recommended Order:**

1. **Start with API Endpoints** (quickest win)
   - Find or implement anomaly/recent endpoint
   - Test: `curl http://172.18.0.1:8001/api/v1/anomaly/recent`
   - Retry query: "any anomalies today?"

2. **Fix Forecast Intent** (highest impact)
   - Add short-term patterns
   - Test: "Forecast Compressor-1 next 4 hours"
   - Verify correct API called

3. **Comprehensive Testing**
   - Create test dataset
   - Run all queries
   - Measure accuracy

---

## 🎯 Success Criteria

**When are we done?**

- ✅ "any anomalies today?" returns actual anomaly data
- ✅ "Show me KPIs for Compressor-1 today" returns KPI metrics
- ✅ "Forecast Compressor-1 next 4 hours" returns 4-hour machine forecast
- ✅ 95%+ intent accuracy on test dataset
- ✅ <300ms average response time
- ✅ All 20+ intent types working correctly

---

**Created:** December 17, 2025  
**Status:** Ready for implementation
