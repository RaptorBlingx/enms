# Quick Fix Needed - Timeseries Column Name Error

**Error:** `column "timestamp" does not exist`

**Location:** `/home/ubuntu/enms/analytics/api/routes/timeseries.py`

**Issue:** The timeseries endpoints are querying for `timestamp` column, but the database table uses a different column name (likely `time` or `ts`).

---

## 🔍 To Fix:

### 1. Check the actual column name in database:
```bash
docker exec -it enms-postgres psql -U raptorblingx -d enms -c "\d energy_data"
```

### 2. Update timeseries.py queries:
The SQL queries need to use the correct column name:
- If table uses `time` instead of `timestamp`
- If table uses `ts` instead of `timestamp`

### 3. Check these endpoints in timeseries.py:
- `get_energy_timeseries()` - line ~150
- `get_power_timeseries()` - line ~250
- `get_sec_timeseries()` - line ~350

Replace `timestamp` with the correct column name from the database schema.

---

## ✅ Good News

All routes are registered correctly! The only issue is:
1. Column name mismatch in SQL queries (easy fix)
2. Possibly missing aggregated data (may need to wait for simulator)

Once these are fixed, all charts will load properly.

---

**This is exactly why we test incrementally!** 🎯
