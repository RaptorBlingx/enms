# Model Performance Route Review - Issues & Fixes

**File:** `analytics/api/routes/model_performance.py`  
**Date:** October 15, 2025  
**Status:** ⚠️ NEEDS FIXES

---

## Issues Identified

### 1. Database Pool Access Pattern ❌
**Problem:** Using `request.app.state.db_pool` (doesn't exist in our setup)  
**Occurrences:** 14 locations  
**Fix Required:** Change to `from database import db` + `pool = db.pool`

**Lines with issue:**
- Line 136, 223, 307, 383, 453, 512, 569 (and duplicates)

### 2. Missing Import ❌
**Problem:** No `from database import db` import at top of file  
**Fix Required:** Add import statement

### 3. Request Parameter Not Needed ❌
**Problem:** All route functions have `request: Request` parameter  
**Fix Required:** Remove Request parameter from function signatures

### 4. Helper Functions Need Connection Parameter ⚠️
**Problem:** Helper functions like `detect_drift()`, `create_drift_alert()` expect connection  
**Status:** Need to verify these exist and are called correctly

### 5. UUID Type Handling ⚠️
**Problem:** Query parameters use `str` but database expects UUID  
**Fix Required:** Convert strings to UUID objects before database queries

---

## Required Changes

### Change 1: Add Import
```python
# At top of file, after other imports
from database import db
```

### Change 2: Remove Request Import (if not used elsewhere)
```python
# Change this:
from fastapi import APIRouter, Query, HTTPException, Request, BackgroundTasks

# To this (if Request not needed elsewhere):
from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
```

### Change 3: Fix All Route Functions
Pattern to apply to all routes:

**Before:**
```python
@router.post("/metrics/record")
async def record_performance_metric(
    request: Request,
    model_id: str = Query(...),
    ...
):
    pool = request.app.state.db_pool
```

**After:**
```python
@router.post("/metrics/record")
async def record_performance_metric(
    model_id: str = Query(...),
    ...
):
    pool = db.pool
```

### Change 4: Fix UUID Handling
**Before:**
```python
model_id: str = Query(...)
# Then used directly in query
WHERE id = $1", model_id
```

**After:**
```python
from uuid import UUID
model_id: str = Query(...)
# Convert to UUID
model_uuid = UUID(model_id)
WHERE id = $1", model_uuid
```

---

## Routes to Fix

1. `POST /metrics/record` - Line 118
2. `GET /metrics/{machine_id}` - Line 213
3. `GET /drift/check/{machine_id}` - Line 297
4. `POST /retrain/trigger` - Line 373
5. `POST /ab-test/start` - Line 443
6. `GET /ab-test/{test_id}/status` - Line 502
7. `GET /alerts/active` - Line 559

Total: 7 route functions need fixing

---

## Additional Issues to Check

### Missing Helper Functions
Need to verify these helper functions exist:
- `detect_drift(conn, model_id, model_type, machine_id, metrics)`
- `create_drift_alert(conn, model_id, model_type, machine_id, model_version, drift_result, metrics)`
- `should_trigger_training(conn, model_id, model_type, machine_id)`
- `record_training_trigger(conn, ...)`
- `get_model_metrics_during_test(conn, model_id, start, end)`
- `determine_winner(model_a_metrics, model_b_metrics)`
- `execute_training(job_id, model_type, machine_id)`

**Status:** Some are defined in file, some may be missing

### JSON/JSONB Handling
**Check:** Ensure JSONB fields are properly serialized/deserialized
- `metrics` field in queries
- `alert_details` field
- `metadata` fields

---

## Systematic Fix Plan

1. ✅ Add `from database import db` import
2. ✅ Remove `Request` from imports (if not needed)
3. ✅ Fix all 7 route functions:
   - Remove `request: Request` parameter
   - Change `pool = request.app.state.db_pool` to `pool = db.pool`
4. ✅ Add UUID conversion where needed
5. ✅ Test each endpoint after fixing
6. ✅ Verify helper functions work correctly

---

## Testing Checklist

After fixes:
- [ ] POST /metrics/record - Test recording metrics
- [ ] GET /metrics/{machine_id} - Test retrieving metrics
- [ ] GET /drift/check/{machine_id} - Test drift detection
- [ ] POST /retrain/trigger - Test training trigger
- [ ] POST /ab-test/start - Test starting A/B test
- [ ] GET /ab-test/{test_id}/status - Test A/B test status
- [ ] GET /alerts/active - Test alert retrieval

---

**Priority:** HIGH - Must fix before testing  
**Estimated Time:** 30 minutes  
**Impact:** All model performance endpoints currently non-functional
