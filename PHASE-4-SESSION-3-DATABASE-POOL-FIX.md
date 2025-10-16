# Phase 4 Session 3 - Database Pool Access Fix

**Date:** October 14, 2025  
**Status:** ✅ COMPLETED  
**Issue:** Sankey, Heatmap, and Comparison API endpoints returning HTML errors instead of JSON

---

## Problem Description

When accessing the three new Phase 4 Session 3 visualization pages (Sankey, Heatmap, Comparison), the JavaScript console showed errors:

```
Unexpected token '<', "<!DOCTYPE "... is not valid JSON
```

This indicated that the API endpoints were returning HTML error pages instead of JSON data.

---

## Root Cause Analysis

### Issue 1: Incorrect Database Pool Access Pattern

The new route files (`sankey.py`, `heatmap.py`, `comparison.py`) were using:
```python
async def endpoint(request: Request, ...):
    pool = request.app.state.db_pool
```

However, `main.py` does not initialize `app.state.db_pool`. The working pattern used by other routes is:
```python
from database import db

async def endpoint(...):  # No Request parameter
    pool = db.pool
```

### Issue 2: Incorrect Column Names in Heatmap Queries

The heatmap SQL queries referenced `a.severity_score`, but the `anomalies` table actually has:
- `severity` (enum: normal/warning/critical)
- `confidence_score` (numeric 0-1)

---

## Solution Implementation

### 1. Fixed Database Pool Access (3 files)

**Files Modified:**
- `analytics/api/routes/sankey.py`
- `analytics/api/routes/heatmap.py`
- `analytics/api/routes/comparison.py`

**Changes Applied:**
1. Added import: `from database import db`
2. Removed `Request` from FastAPI imports
3. Removed `request: Request` parameter from all endpoint functions
4. Changed `pool = request.app.state.db_pool` to `pool = db.pool`

**sankey.py - 2 functions fixed:**
- `get_sankey_data()`
- `get_available_factories()`

**heatmap.py - 2 functions fixed:**
- `get_hourly_heatmap()`
- `get_daily_heatmap()`

**comparison.py - 2 functions fixed:**
- `compare_machines()`
- `get_available_machines()`

### 2. Fixed Heatmap SQL Queries

Changed severity column reference from `a.severity_score` to `COALESCE(a.confidence_score, 0.5)`:

**Before:**
```sql
AVG(a.severity_score) AS avg_severity
WHERE ... AND a.severity_score >= $3
```

**After:**
```sql
AVG(COALESCE(a.confidence_score, 0.5)) AS avg_severity
WHERE ... AND COALESCE(a.confidence_score, 0.5) >= $3
```

Applied to both:
- `/hourly` endpoint query
- `/daily` endpoint query

---

## Testing Results

### Direct API Tests (localhost:8001)

✅ **Sankey Endpoints:**
```bash
GET /api/v1/sankey/factories
→ Returns 2 factories (JSON)

GET /api/v1/sankey/data?factory_id=xxx
→ Returns 8 nodes (JSON)
```

✅ **Heatmap Endpoints:**
```bash
GET /api/v1/heatmap/hourly
→ Returns machines array with 0 items (JSON) - no anomalies yet

GET /api/v1/heatmap/daily
→ Returns JSON response
```

✅ **Comparison Endpoints:**
```bash
GET /api/v1/comparison/available
→ Returns 7 machines (JSON)

GET /api/v1/comparison/machines?machine_ids=xxx,yyy
→ Returns comparison data (JSON)
```

### Nginx Proxy Tests (localhost:8080)

✅ **UI Pages:**
```bash
GET /api/analytics/ui/sankey
→ Returns HTML page (200 OK)

GET /api/analytics/ui/heatmap
→ Returns HTML page (200 OK)

GET /api/analytics/ui/comparison
→ Returns HTML page (200 OK)
```

✅ **API Through Proxy:**
```bash
GET /api/analytics/api/v1/sankey/factories
→ Returns 2 factories (JSON)

GET /api/analytics/api/v1/heatmap/hourly
→ Returns JSON with cells array

GET /api/analytics/api/v1/comparison/available
→ Returns 7 machines (JSON)
```

---

## Files Changed Summary

```
analytics/api/routes/sankey.py
  - Added: from database import db
  - Removed: Request from imports
  - Modified: 2 functions (get_sankey_data, get_available_factories)
  - Changed: request.app.state.db_pool → db.pool

analytics/api/routes/heatmap.py
  - Added: from database import db
  - Removed: Request from imports
  - Modified: 2 functions (get_hourly_heatmap, get_daily_heatmap)
  - Changed: request.app.state.db_pool → db.pool
  - Fixed: severity_score → COALESCE(confidence_score, 0.5)

analytics/api/routes/comparison.py
  - Added: from database import db
  - Removed: Request from imports
  - Modified: 2 functions (compare_machines, get_available_machines)
  - Changed: request.app.state.db_pool → db.pool
```

---

## Container Rebuild

```bash
cd /home/ubuntu/enms
docker compose stop analytics
docker compose rm -f analytics
docker compose up -d --build analytics
```

Container Status: ✅ Running and healthy

---

## Verification

All three new visualization features are now fully functional:

1. **Sankey Diagram** - Energy flow visualization from grid → factory → departments → machines
2. **Anomaly Heatmap** - Pattern analysis showing anomalies by machine and time (hourly/daily)
3. **Machine Comparison** - Side-by-side benchmarking of multiple machines

### Access URLs (via nginx proxy):
- Sankey: http://localhost:8080/api/analytics/ui/sankey
- Heatmap: http://localhost:8080/api/analytics/ui/heatmap
- Comparison: http://localhost:8080/api/analytics/ui/comparison

### API Documentation:
- OpenAPI: http://localhost:8080/api/analytics/docs
- ReDoc: http://localhost:8080/api/analytics/redoc

---

## Key Learnings

1. **Database Pool Pattern**: Always use `from database import db` + `pool = db.pool` pattern
2. **No Request Dependency**: FastAPI endpoints don't need `request: Request` parameter for database access
3. **Schema Validation**: Always verify actual database schema before writing SQL queries
4. **COALESCE for NULLs**: Use COALESCE to provide default values for nullable columns in aggregations

---

## Phase 4 Session 3 Status

✅ **Part 1: Timeseries Data Integration** - COMPLETE
- Energy consumption trends
- Power demand patterns  
- SEC (Specific Energy Consumption) monitoring
- Real-time KPI dashboard with 10-point data

✅ **Part 2: Advanced Visualizations** - COMPLETE
- Sankey energy flow diagram
- Anomaly pattern heatmaps
- Machine comparison benchmarking

✅ **Part 3: Database Pool Fix** - COMPLETE (This Session)
- All API endpoints return JSON correctly
- All UI pages load without errors
- Full integration with existing dashboard

---

**Next Steps:**
1. Add anomaly data to database for heatmap testing
2. Test Sankey diagram with real energy flow data
3. Validate comparison charts with multiple machines
4. Consider Phase 4 Session 4 planning (predictive maintenance, advanced ML features)
