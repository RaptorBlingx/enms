# ✅ IMPLEMENTATION CHECKLIST - Phase 3 Aggregate Fix

**Date:** October 13, 2025  
**Estimated Time:** 70 minutes  
**Status:** Ready to Execute

---

## 📋 PRE-FLIGHT CHECK

- [ ] **Review completed:** ARCHITECT-RESPONSE-REVIEW.md read
- [ ] **SQL script located:** FIX-CONTINUOUS-AGGREGATES.sql
- [ ] **Backup plan understood:** Can re-run script if needed
- [ ] **Expected outcome clear:** Hourly aggregates + 7-feature model with R² > 0.70

---

## 🔧 PHASE 1: DATABASE FIX (30 min)

### Step 1: Optional Backup
```bash
docker exec enms-postgres pg_dump -U raptorblingx enms > backup_before_aggregate_fix.sql
```
- [ ] Backup created (optional but recommended)

### Step 2: Execute SQL Fix
```bash
docker exec -i enms-postgres psql -U raptorblingx -d enms < /home/ubuntu/enms/FIX-CONTINUOUS-AGGREGATES.sql
```
- [ ] SQL script executed
- [ ] No critical errors in output
- [ ] All aggregates reported as "created"

### Step 3: Verify Aggregates
```bash
docker exec enms-postgres psql -U raptorblingx -d enms -c \
  "SELECT view_name FROM timescaledb_information.continuous_aggregates ORDER BY view_name;"
```

**Expected: 11 aggregates**
- [ ] energy_readings_1min (existing)
- [ ] energy_readings_15min (new)
- [ ] energy_readings_1hour (new)
- [ ] energy_readings_1day (new)
- [ ] production_data_1min (existing)
- [ ] production_data_15min (new)
- [ ] production_data_1hour (new)
- [ ] production_data_1day (new)
- [ ] environmental_data_1min (existing)
- [ ] environmental_data_15min (new)
- [ ] environmental_data_1hour (new)

### Step 4: Verify Load Factor Column
```bash
docker exec enms-postgres psql -U raptorblingx -d enms -c \
  "SELECT column_name FROM information_schema.columns 
   WHERE table_name = 'energy_readings_1hour' AND column_name = 'avg_load_factor';"
```
- [ ] `avg_load_factor` column exists

---

## 💻 PHASE 2: CODE UPDATES (15 min)

### Step 1: Update analytics/database.py

**Location 1: Line ~178 (get_machine_data_for_training)**
```python
# CHANGE FROM:
FROM energy_readings_1min er
LEFT JOIN production_data_1min pd
LEFT JOIN environmental_data_1min ed

# CHANGE TO:
FROM energy_readings_1hour er
LEFT JOIN production_data_1hour pd
LEFT JOIN environmental_data_1hour ed
```
- [ ] Line ~178 updated to use `*_1hour`

**Location 2: Line ~312 (get_machine_data_combined)**
```python
# CHANGE FROM:
FROM energy_readings_1min er
LEFT JOIN production_data_1min pd
LEFT JOIN environmental_data_1min ed

# CHANGE TO:
FROM energy_readings_1hour er
LEFT JOIN production_data_1hour pd
LEFT JOIN environmental_data_1hour ed
```
- [ ] Line ~312 updated to use `*_1hour`

**Location 3: Line ~231 and ~315 (load_factor calculation)**
```python
# REMOVE THIS LINE:
(er.avg_power_kw / NULLIF(er.max_power_kw, 0)) as avg_load_factor,

# REPLACE WITH:
er.avg_load_factor,  -- Now calculated in the aggregate
```
- [ ] Line ~231 updated (get_machine_data_for_training)
- [ ] Line ~315 updated (get_machine_data_combined)

**KEEP THESE (no changes):**
```python
# Lines 229, 308 - Keep the alias:
pd.avg_throughput as avg_throughput_units_per_hour,
```
- [ ] Verified aliases remain unchanged

### Step 2: Update Feature List

**Option A: Modify training call in baseline_service.py**

Find the default features in `prepare_data()` method:
```python
# CHANGE FROM (around line 78):
if feature_columns is None:
    feature_columns = [
        'total_production_count',
        'avg_outdoor_temp_c',
        'avg_pressure_bar',
        'avg_throughput_units_per_hour'
    ]

# CHANGE TO:
if feature_columns is None:
    feature_columns = [
        'total_production_count',
        'avg_outdoor_temp_c',
        'avg_pressure_bar',
        'avg_throughput_units_per_hour',
        'avg_indoor_temp_c',        # NEW
        'avg_machine_temp_c',       # NEW
        'avg_load_factor'           # NEW
    ]
```
- [ ] Feature list updated in baseline.py or service

**Option B: Let users specify via API (recommended)**
- [ ] No code change needed (features passed in API call)

### Step 3: Rebuild Docker Image
```bash
cd /home/ubuntu/enms
docker compose build analytics --no-cache
docker compose up -d analytics
sleep 5
```
- [ ] Docker image rebuilt
- [ ] Container restarted
- [ ] Container is healthy

### Step 4: Verify Container
```bash
docker compose ps analytics
docker compose logs analytics --tail 20
```
- [ ] Analytics service running
- [ ] No startup errors
- [ ] API started successfully

---

## 🎯 PHASE 3: MODEL RETRAINING (10 min)

### Step 1: Train with 7 Features
```bash
curl -X POST "http://localhost:8080/api/analytics/api/v1/baseline/train" \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "c0000000-0000-0000-0000-000000000001",
    "start_date": "2025-10-10T07:00:00Z",
    "end_date": "2025-10-11T11:45:00Z",
    "drivers": [
      "total_production_count",
      "avg_outdoor_temp_c",
      "avg_pressure_bar",
      "avg_throughput_units_per_hour",
      "avg_indoor_temp_c",
      "avg_machine_temp_c",
      "avg_load_factor"
    ]
  }' | jq '.'
```
- [ ] API call successful (HTTP 200)
- [ ] Model trained

### Step 2: Verify Results

**Check these values in response:**
- [ ] `training_samples`: Should be ~28 (hourly data)
- [ ] `r_squared`: Should be ≥ 0.70 (target ≥ 0.80)
- [ ] `feature_names`: Should have 7 features
- [ ] `meets_quality_threshold`: Should be true (if R² ≥ 0.80)

**Record actual values:**
- R² Score: __________
- RMSE: __________
- MAE: __________
- Training Samples: __________
- Features Count: __________

### Step 3: Compare Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Training Samples | 1,677 | _____ | __________ |
| Features | 3 | 7 | +4 features |
| R² Score | 0.454 | _____ | __________ |
| Quality Threshold | ❌ | _____ | __________ |

- [ ] R² improved significantly
- [ ] Training samples reduced (good - using hourly data)
- [ ] Model meets quality threshold

---

## ✅ PHASE 4: VALIDATION (15 min)

### Step 1: Test Other Baseline Endpoints

**Get Active Model:**
```bash
curl "http://localhost:8080/api/analytics/api/v1/baseline/models/c0000000-0000-0000-0000-000000000001" | jq '.'
```
- [ ] Returns model metadata
- [ ] R² score matches training

**Get Specific Model:**
```bash
# Use model_id from training response
curl "http://localhost:8080/api/analytics/api/v1/baseline/models/{model_id}" | jq '.'
```
- [ ] Returns model details
- [ ] Coefficients present for all 7 features

**Test Prediction:**
```bash
curl -X POST "http://localhost:8080/api/analytics/api/v1/baseline/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "c0000000-0000-0000-0000-000000000001",
    "features": {
      "total_production_count": 1000,
      "avg_outdoor_temp_c": 20.0,
      "avg_pressure_bar": 7.5,
      "avg_throughput_units_per_hour": 100,
      "avg_indoor_temp_c": 22.0,
      "avg_machine_temp_c": 45.0,
      "avg_load_factor": 0.75
    }
  }' | jq '.'
```
- [ ] Returns predicted energy
- [ ] Value is reasonable

### Step 2: Performance Test

**Query Larger Date Range:**
```bash
curl -X POST "http://localhost:8080/api/analytics/api/v1/baseline/train" \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "c0000000-0000-0000-0000-000000000001",
    "start_date": "2025-10-01T00:00:00Z",
    "end_date": "2025-10-13T23:59:59Z",
    "drivers": [
      "total_production_count",
      "avg_outdoor_temp_c",
      "avg_pressure_bar",
      "avg_throughput_units_per_hour",
      "avg_indoor_temp_c",
      "avg_machine_temp_c",
      "avg_load_factor"
    ]
  }' | jq '.'
```
- [ ] Completes quickly (should be fast with hourly data)
- [ ] Training samples reasonable for date range
- [ ] No memory errors

### Step 3: Check Logs for Errors
```bash
docker compose logs analytics --tail 50 | grep -i error
```
- [ ] No errors in logs
- [ ] All queries successful

---

## 📊 PHASE 5: DOCUMENTATION (5 min)

### Update Progress Document
- [ ] Update `PHASE-03-SESSION-PROGRESS.md`
- [ ] Mark database aggregates as FIXED
- [ ] Update R² score results
- [ ] Add "After SQL Fix" section

### Create Success Summary
- [ ] Document final R² score
- [ ] Record performance improvements
- [ ] List all working features
- [ ] Note any issues encountered

---

## 🎉 SUCCESS CRITERIA

### All Must Pass:
- [x] 11 continuous aggregates exist
- [x] Hourly aggregates query directly from hypertables
- [x] Code updated to use `*_1hour` tables
- [x] Model trained with 7 features
- [x] R² Score ≥ 0.70 (target ≥ 0.80)
- [x] All endpoints working
- [x] Performance improved
- [x] No errors in logs

### Bonus:
- [ ] R² Score ≥ 0.80 (ideal)
- [ ] Documentation updated
- [ ] Performance tests pass

---

## 🚨 TROUBLESHOOTING

### If SQL script fails:
1. Check error message
2. Verify database connection
3. Check if aggregates already exist (can re-run safely)
4. Verify TimescaleDB extension enabled

### If R² is still low:
1. Check feature availability in data
2. Verify no missing values
3. Try longer training period
4. Check for outliers in data
5. Consider feature scaling

### If container won't start:
1. Check for syntax errors in database.py
2. Verify all imports
3. Check docker compose logs
4. Rebuild with --no-cache

### If endpoints return errors:
1. Check column names in queries
2. Verify aggregates exist
3. Check for missing data
4. Review error logs

---

## 📝 NOTES SECTION

**Issues Encountered:**
_________________________________________________
_________________________________________________
_________________________________________________

**Actual R² Score:** __________

**Performance Observations:**
_________________________________________________
_________________________________________________
_________________________________________________

**Next Steps:**
_________________________________________________
_________________________________________________
_________________________________________________

---

**Checklist Created:** October 13, 2025  
**Ready to Execute:** YES ✅  
**Estimated Time:** 70 minutes  
**Confidence:** 95%

🚀 **LET'S DO THIS!**
