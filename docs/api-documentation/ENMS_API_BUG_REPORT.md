# EnMS API Bug Report: Data Inconsistency Between Endpoints

**Date:** November 17, 2025  
**Reported by:** Burak (OVOS Integration Team)  
**Severity:** HIGH - Data integrity issue  
**Status:** CONFIRMED

## Summary

The `/analytics/top-consumers` endpoint returns **different energy values** than the actual time-series endpoints (`/timeseries/energy` and `/timeseries/multi-machine/energy`) for the **same machine** and **same time period**.

## Evidence

### Test Parameters (Same for all tests)
- **Time Range:** 2025-11-16T13:56:00Z to 2025-11-17T13:56:00Z (24 hours)
- **Machine:** Boiler-1 (UUID: e9fcad45-1f7b-4425-8710-c368a681f15e)
- **Interval:** 1 hour

### Test Results

#### Test 1: `/api/v1/timeseries/energy` (Individual Query)
```bash
curl -s "http://10.33.10.109:8001/api/v1/timeseries/energy?\
machine_id=e9fcad45-1f7b-4425-8710-c368a681f15e&\
start_time=2025-11-16T13:56:00Z&\
end_time=2025-11-17T13:56:00Z&\
interval=1hour"
```

**Result:**
- Data points: 25
- **Total Energy: 66,081.4 kWh** ✓

#### Test 2: `/api/v1/analytics/top-consumers` (Ranking)
```bash
curl -s "http://10.33.10.109:8001/api/v1/analytics/top-consumers?\
metric=energy&\
start_time=2025-11-16T13:56:00Z&\
end_time=2025-11-17T13:56:00Z&\
limit=5"
```

**Result:**
- Boiler-1 rank: #1
- **Total Energy: 66,294.96 kWh** ❌ (213.6 kWh MORE!)

#### Test 3: `/api/v1/timeseries/multi-machine/energy` (Comparison)
```bash
curl -s "http://10.33.10.109:8001/api/v1/timeseries/multi-machine/energy?\
machine_ids=e9fcad45-1f7b-4425-8710-c368a681f15e,c0000000-0000-0000-0000-000000000001&\
start_time=2025-11-16T13:56:00Z&\
end_time=2025-11-17T13:56:00Z&\
interval=1hour"
```

**Result:**
- Boiler-1: **66,081.4 kWh** ✓
- Compressor-1: 1,053.9 kWh

## Analysis

### Consistency Matrix

| Endpoint | Boiler-1 Energy | Matches? |
|----------|----------------|----------|
| `/timeseries/energy` | 66,081.4 kWh | ✓ Baseline |
| `/timeseries/multi-machine/energy` | 66,081.4 kWh | ✓ Consistent |
| `/analytics/top-consumers` | **66,294.96 kWh** | ❌ **+213.6 kWh (+0.32%)** |

### Data Discrepancy
- **Absolute difference:** 213.56 kWh
- **Percentage difference:** 0.32%
- **Pattern:** Top-consumers endpoint consistently returns **MORE** energy

## Root Cause Hypothesis

Possible causes:
1. **Different SQL aggregation logic** - `/analytics/top-consumers` might be using different time bucketing
2. **Timezone handling** - Endpoint might be converting timestamps differently
3. **Data source difference** - Reading from different tables or views
4. **Caching issue** - Stale data in analytics cache
5. **Rounding/precision** - Different floating-point precision handling

## Impact on OVOS Integration

### User Experience Problem
User asks: "How much energy did Boiler-1 use in the last 24 hours?"

**Scenario 1:** Query via "top 3 consumers"
- Response: "Boiler-1 used **66,294.96 kWh**"

**Scenario 2:** Query via "Boiler-1 energy last 24 hours"  
- Response: "Boiler-1 used **66,081.4 kWh**"

**Problem:** User gets **different answers** for the **same question!**

This breaks user trust in the system and makes debugging impossible.

## Recommendation

### For EnMS Team
1. **Investigate SQL queries** in `/analytics/top-consumers` implementation
2. **Compare with** `/timeseries/energy` query logic
3. **Ensure same** time range interpretation (start/end inclusive/exclusive)
4. **Verify** timezone handling consistency
5. **Add unit tests** to ensure all endpoints return same totals for same period

### For OVOS Team (Temporary Workaround)
Until fixed, we should:
1. **Use only `/timeseries/energy`** for individual machine queries (✓ reliable)
2. **Use only `/timeseries/multi-machine/energy`** for comparisons (✓ reliable)
3. **Avoid `/analytics/top-consumers`** until EnMS team fixes the inconsistency

## Test Command for EnMS Team

```bash
# Quick verification script
START='2025-11-16T13:56:00Z'
END='2025-11-17T13:56:00Z'
MACHINE='e9fcad45-1f7b-4425-8710-c368a681f15e'

echo "=== Individual Query ==="
curl -s "http://10.33.10.109:8001/api/v1/timeseries/energy?\
machine_id=$MACHINE&start_time=$START&end_time=$END&interval=1hour" \
  | jq '.data_points | map(.value) | add'

echo "=== Top Consumers Query ==="
curl -s "http://10.33.10.109:8001/api/v1/analytics/top-consumers?\
metric=energy&start_time=$START&end_time=$END&limit=5" \
  | jq '.ranking[] | select(.machine_name=="Boiler-1") | .value'

echo "=== Multi-Machine Query ==="
curl -s "http://10.33.10.109:8001/api/v1/timeseries/multi-machine/energy?\
machine_ids=$MACHINE&start_time=$START&end_time=$END&interval=1hour" \
  | jq '.machines[0].data_points | map(.value) | add'
```

**Expected:** All three values should be **EXACTLY** the same.  
**Actual:** Top consumers returns +213.6 kWh more.

## Next Steps

1. **Report to EnMS team** - Share this document
2. **Get SQL query comparison** - Request queries from both endpoints
3. **Wait for fix** - EnMS team to patch the discrepancy
4. **Verify fix** - Re-run test commands above
5. **Update OVOS code** - Once verified, can use all endpoints confidently

---

**Contact:** Burak (OVOS Integration)  
**EnMS API Version:** v3  
**Test Environment:** http://10.33.10.109:8001
