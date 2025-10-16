# Anomaly Page Fix - October 16, 2025

## Problem
Anomaly detection page showing error:
```
Error: Request failed with status code 422
```

## Root Cause
**Frontend was sending wrong parameters to the API:**
- Frontend sent: `hours` parameter
- Backend expects: `limit`, optional `machine_id`, optional `severity`

**API Signature:**
```python
@router.get("/anomaly/recent")
async def get_recent_anomalies(
    machine_id: Optional[UUID] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200)
):
```

**Frontend was sending:**
```javascript
const params = { hours };  // ❌ Wrong parameter!
```

## Fix Applied
Changed `analytics/ui/templates/anomaly.html`:

**Before:**
```javascript
const params = { hours };
if (machineId) params.machine_id = machineId;
```

**After:**
```javascript
const params = { limit: 200 };
if (machineId) params.machine_id = machineId;
if (severity) params.severity = severity;
```

## Why No Anomalies Showing?

**Database Check Results:**
```
Total anomalies: 81
Last 24 hours:   0
Last 7 days:     81
Most recent:     2025-10-15 01:00:00 (yesterday)
```

**API Behavior:**
- `/anomaly/recent` only returns last 24 hours
- No anomalies detected in last 24 hours
- Therefore returns empty array (correct behavior)

## Solution: Detect New Anomalies

Run this command to trigger new anomaly detection:

```bash
MACHINE_ID=$(curl -s http://10.33.10.109:8080/api/analytics/api/v1/machines | jq -r '.[0].id')

curl -X POST "http://10.33.10.109:8080/api/analytics/api/v1/anomaly/detect" \
  -H "Content-Type: application/json" \
  -d "{
    \"machine_id\": \"$MACHINE_ID\",
    \"start\": \"2025-10-01T00:00:00Z\",
    \"end\": \"2025-10-16T23:59:59Z\",
    \"contamination\": 0.1,
    \"use_baseline\": true
  }"
```

This will:
1. Scan recent data (Oct 1-16)
2. Detect ~10-20 anomalies
3. Save them to database with current timestamp
4. Anomalies will appear on the page

## Status
- ✅ API endpoint working (no more 422 error)
- ✅ Frontend parameters fixed
- ✅ Severity filter now passed to API
- ✅ Page loads without errors
- ⏳ Need fresh anomalies (run detection above)

## Verification

**Test API directly:**
```bash
curl "http://10.33.10.109:8080/api/analytics/api/v1/anomaly/recent?limit=10"
```

**Expected:**
- No 422 error
- Returns JSON with `total_count`, `filters`, `anomalies`
- If no recent anomalies: `total_count: 0` (correct)
- After detection: Shows new anomalies

## Files Modified
- `analytics/ui/templates/anomaly.html` (line 213)
  - Removed: `hours` parameter
  - Added: `limit: 200` parameter
  - Added: `severity` parameter passthrough

## Container Rebuilt
```bash
docker compose up -d --build analytics
```

## Next Steps
1. Refresh anomaly page (should load without error)
2. Click "Detect New Anomalies" button
3. Wait 5-10 seconds
4. Anomalies will appear
