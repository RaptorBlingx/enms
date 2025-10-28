# OVOS Baseline Training Bug - Fix Plan

**Date:** October 27, 2025  
**Priority:** HIGH  
**Status:** ✅ ROOT CAUSE IDENTIFIED + FIX PLAN READY

---

## Executive Summary

**You were 100% RIGHT!** ✅

- **Your memory:** Previous baselines achieved 97-99% accuracy
- **Current OVOS:** Only 47-85% accuracy
- **Root cause:** OVOS endpoint uses incomplete feature set + buggy query builder

---

## Root Cause Analysis

### What I Found

#### 1. ✅ Two Different Baseline Systems Exist

**Old System** (`POST /baseline/train`):
- Uses: `baseline_service.py`
- Features: 6 features with auto-selection (`avg_load_factor`, `avg_machine_temp_c`, `avg_throughput`, etc.)
- Aggregation: `energy_readings_1hour` (hourly data)
- Results: **R² = 0.97-0.99 (97-99%)**

**New OVOS System** (`POST /ovos/train-baseline`):
- Uses: `seu_baseline_service.py`  
- Features: Only basic features (`production_count`, `outdoor_temp_c`)
- Aggregation: `energy_readings_1day` (daily data)
- Results: **R² = 0.47-0.85 (47-85%)**

#### 2. ✅ Simulator Data is GOOD (Not the Bug)

Tested old endpoint with current simulator data:
```bash
POST /baseline/train
Result: R² = 0.9750 (97.5%) with 404 samples
Features: total_production_count, avg_outdoor_temp_c, avg_pressure_bar, 
          avg_throughput_units_per_hour, avg_machine_temp_c, avg_load_factor
```

**Conclusion:** Simulator generates realistic data with strong correlations!

#### 3. ❌ OVOS Missing Critical Features

**Features in old baselines (97% accuracy):**
- ✅ `total_production_count`
- ✅ `avg_outdoor_temp_c`
- ✅ `avg_pressure_bar`
- ✅ `avg_throughput_units_per_hour`
- ✅ `avg_machine_temp_c`
- ✅ `avg_load_factor` ← **MOST IMPORTANT**

**Features available in OVOS:**
- ✅ `production_count`
- ✅ `outdoor_temp_c`  
- ✅ `pressure_bar`
- ✅ `avg_throughput`
- ✅ `machine_temp_c`
- ❌ `avg_load_factor` ← **MISSING FROM energy_source_features TABLE**

#### 4. ❌ Query Builder Bug

File: `analytics/services/feature_discovery.py`

**Problem:** Hardcoded feature-to-table mapping doesn't cover all features:

```python
# Line ~230 - Hardcoded mapping (incomplete!)
feature_to_column_map = {
    'production_count': 'total_production_count',
    'outdoor_temp_c': 'avg_outdoor_temp_c',
    'consumption_kwh': 'total_energy_kwh',
    'avg_power_kw': 'avg_power_kw',
    'peak_demand_kw': 'peak_demand_kw'
}
# Missing: avg_load_factor, avg_throughput, machine_temp_c, etc!
```

**Result:** Features not in the map cause SQL errors like:
```
column er.avg_throughput does not exist
HINT: Perhaps you meant to reference the column "pd.avg_throughput"
```

---

## Test Results

### Before Fix
```bash
# Test 1: Basic features
Features: ["production_count", "outdoor_temp_c"]
Result: R² = 0.47 (47%) ❌

# Test 2: Add pressure
Features: ["production_count", "outdoor_temp_c", "pressure_bar"]
Result: R² = 0.85 (85%) ⚠️

# Test 3: Old endpoint (same data)
Endpoint: POST /baseline/train (auto-select features)
Result: R² = 0.975 (97.5%) ✅
```

### After Partial Fix
```bash
# Added avg_load_factor to energy_source_features table
INSERT INTO energy_source_features (...) VALUES (..., 'avg_load_factor', ...)

# Now visible in feature list
curl /api/v1/ovos/energy-sources
Result: 22 features (was 21) ✅

# But query builder still broken
Features: ["production_count", "avg_load_factor"]
Result: "column er.avg_load_factor does not exist" ❌
```

---

## The Fix

### Option 1: Quick Fix - Use Old Baseline Endpoint (RECOMMENDED)

**Pros:**
- ✅ Works NOW (no code changes)
- ✅ 97-99% accuracy
- ✅ Auto-selects best features
- ✅ Battle-tested code

**Cons:**
- ⚠️ Different API format (not voice-optimized)
- ⚠️ Requires machine_id instead of seu_name

**Implementation:**
```python
# In OVOS skill, instead of:
POST /ovos/train-baseline
{
  "seu_name": "Compressor-1",
  "energy_source": "electricity",
  "features": ["production_count", "outdoor_temp_c"],
  "year": 2025
}

# Use:
POST /baseline/train
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "start_date": "2025-01-01T00:00:00Z",
  "end_date": "2025-12-31T23:59:59Z",
  "drivers": null  # Auto-select best features
}
```

**Effort:** 30 minutes (update OVOS skill to use old endpoint)

---

### Option 2: Fix OVOS Endpoint (PROPER FIX)

**Step 1: Fix Query Builder**

File: `analytics/services/feature_discovery.py`

**Current bug (line ~305):**
```python
for feat_name in requested_features:
    if feat_name == 'production_count':
        select_parts.append(f"pd.{aggregate_column} as {feat_name}")
    elif feat_name == 'outdoor_temp_c':
        select_parts.append(f"ed.{aggregate_column} as {feat_name}")
    # ... only handles 5-6 features!
```

**Fixed version:**
```python
# Get feature metadata dynamically
feature_metadata = await self.get_feature_metadata(
    energy_source_id=energy_source_id,
    feature_names=requested_features
)

for feat in requested_features:
    meta = feature_metadata.get(feat)
    if not meta:
        continue
        
    # Determine table alias based on source_table
    if meta.source_table == 'energy_readings':
        alias = 'er'
    elif meta.source_table == 'production_data':
        alias = 'pd'
    elif meta.source_table == 'environmental_data':
        alias = 'ed'
    else:
        continue
    
    # Use aggregation function from metadata
    agg_func = meta.aggregation_function
    col = meta.source_column
    
    if agg_func == 'AVG':
        select_parts.append(f"{alias}.{col} as {feat}")
    elif agg_func == 'SUM':
        select_parts.append(f"{alias}.{col} as {feat}")
    # ... handle all aggregation types dynamically
```

**Step 2: Use Hourly Aggregates**

Change from `energy_readings_1day` to `energy_readings_1hour`:
```python
# Old: Too coarse (16 samples from 16 days)
from_clause = "FROM energy_readings_1day er"

# New: Fine-grained (384 samples from 16 days)
from_clause = "FROM energy_readings_1hour er"
```

**Step 3: Add All Missing Features**

Run SQL to register missing features:
```sql
-- avg_load_factor (DONE)
INSERT INTO energy_source_features (...) VALUES (..., 'avg_load_factor', ...);

-- Add more if needed
-- (Check what's in energy_readings_1hour but not in energy_source_features)
```

**Effort:** 4-6 hours (code rewrite + testing)

---

### Option 3: Make OVOS Use Old Service Internally

**Concept:** Keep OVOS API format, but internally call `baseline_service` instead of `seu_baseline_service`

**Pros:**
- ✅ Voice-optimized API format
- ✅ 97-99% accuracy (uses proven code)
- ✅ Minimal code changes

**Cons:**
- ⚠️ Need to map SEU → machine_id
- ⚠️ Need to convert date ranges

**Implementation:**
```python
# In analytics/api/routes/ovos_training.py

from services.baseline_service import BaselineService

@router.post("/train-baseline")
async def train_baseline_ovos(request: OVOSTrainRequest):
    # Step 1: Get SEU details
    seu = await get_seu_by_name(request.seu_name, request.energy_source)
    
    # Step 2: Get machine_id from SEU
    machine_id = seu['machine_ids'][0]  # Assume 1 machine per SEU
    
    # Step 3: Convert year to date range
    start_date = datetime(request.year, 1, 1)
    end_date = datetime(request.year, 12, 31, 23, 59, 59)
    
    # Step 4: Call OLD baseline service (proven code)
    result = await BaselineService.train_baseline(
        machine_id=machine_id,
        start_date=start_date,
        end_date=end_date,
        drivers=None  # Auto-select best features
    )
    
    # Step 5: Format response for voice
    return OVOSTrainingResponse(
        success=True,
        message=f"{request.seu_name} baseline trained. R-squared {result['r_squared']:.2f}",
        r_squared=result['r_squared'],
        ...
    )
```

**Effort:** 2 hours (wrapper code + testing)

---

## Recommendations

### Immediate Action (Today)

**Option 3: Make OVOS use old service** ← **BEST CHOICE**

**Why:**
- ✅ 2 hours work (you have time today)
- ✅ Gets 97-99% accuracy immediately
- ✅ Keeps voice-friendly API format
- ✅ No need to fix complex query builder
- ✅ Proven, battle-tested code

**Steps:**
1. Modify `analytics/api/routes/ovos_training.py`
2. Import `baseline_service`
3. Add wrapper to convert OVOS request → old service call
4. Test with existing data
5. Update documentation with new accuracy (97%+)

**Testing:**
```bash
# Before fix
curl POST /ovos/train-baseline {...}
Result: R² = 0.47 ❌

# After fix
curl POST /ovos/train-baseline {...}
Result: R² = 0.975 ✅ (internally calls proven baseline_service)
```

### Medium-Term (Next Week)

**Fix query builder properly (Option 2)**

- Rewrite `feature_discovery.py` to be fully dynamic
- Add comprehensive tests
- Document the feature system
- Add validation for all 22 electricity features

### Long-Term (Next Month)

**Unify the two systems**

- Merge `baseline_service` and `seu_baseline_service`
- Single codebase with both APIs
- Consistent feature handling
- Better maintainability

---

## Data Migration - NOT NEEDED ✅

**Question:** "do we have to modify the previous data?"

**Answer:** NO! ✅

**Reasons:**
1. Simulator data is GOOD (proven by 97% accuracy with old endpoint)
2. All necessary features exist in continuous aggregates
3. Historical baselines are valid (0.97-0.99 R²)
4. Problem is code, not data

**What we have:**
- ✅ 16 days of high-quality simulated data (Oct 10-27)
- ✅ All features computed in aggregates (`avg_load_factor`, etc.)
- ✅ Strong correlations exist (production → energy)
- ✅ 97-99% accuracy achievable with current data

**No data migration or regeneration needed!**

---

## Next Steps

### Step 1: Implement Option 3 (2 hours)

```bash
cd /home/ubuntu/enms/analytics/api/routes
# Edit ovos_training.py to use baseline_service internally
```

### Step 2: Test

```bash
# Test OVOS endpoint with wrapper
curl -X POST http://localhost:8001/api/v1/ovos/train-baseline \
  -H "Content-Type: application/json" \
  -d '{
    "seu_name": "Compressor-1",
    "energy_source": "electricity",
    "features": ["production_count", "outdoor_temp_c"],
    "year": 2025
  }'

# Expected: R² >= 0.95 (95%+)
```

### Step 3: Update Documentation

- Change examples from 47% → 97% accuracy
- Add note: "OVOS uses proven baseline engine (97-99% accuracy)"
- Update feature recommendations

### Step 4: Deploy

```bash
docker-compose restart analytics
# Test with Burak/OVOS
```

---

## Summary

### What We Know
- ✅ Simulator data is GOOD (97% accuracy possible)
- ✅ Old baseline system works perfectly
- ❌ OVOS system has incomplete features + buggy query builder

### The Fix
**Use Option 3:** Make OVOS call old baseline service internally

**Effort:** 2 hours  
**Result:** 97-99% accuracy  
**Data migration:** NOT needed  

### Your Options

**A) Quick fix (2 hours, 97% accuracy):**
- Wrap old service in OVOS API ← **RECOMMENDED**

**B) Proper fix (6 hours, 97% accuracy):**
- Rewrite query builder completely

**C) Workaround (30 min, 97% accuracy):**
- Tell OVOS to use `/baseline/train` instead of `/ovos/train-baseline`

**My recommendation: Option A (Option 3 in detailed plan)**

Want me to implement it now?
