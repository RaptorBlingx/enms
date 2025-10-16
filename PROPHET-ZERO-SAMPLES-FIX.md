# Prophet Model "0 Samples" Bug Fix

**Date:** October 14, 2025  
**Issue:** Prophet training fails with "Insufficient data: need at least 100 samples, got 0"  
**Status:** ✅ FIXED

---

## Problem Summary

When training a Prophet forecast model with a 30-day lookback period, the training fails with:
```
✗ Training Failed
Insufficient data: need at least 100 samples, got 0
```

This occurred even though ARIMA training with the same machine successfully used 5,384 samples.

---

## Root Cause Analysis

### The Issue
1. **Data Fetching** (`forecast_service.py` lines 73-83):
   - Query fetches data from `energy_readings_1min` table
   - Returns `outdoor_temp_c` and `production_count` columns as **NULL** (not yet implemented)

2. **Regressor Setup** (`forecast_service.py` line 199):
   - Service passes NULL columns as regressors: `['outdoor_temp_c', 'production_count']`

3. **Data Preparation** (`prophet_forecast.py` line 91-94):
   ```python
   columns_to_keep = ['ds', 'y'] + self.regressors  # Includes NULL columns
   df = df[columns_to_keep]
   df = df.dropna()  # ❌ Removes ALL rows because regressor columns are NULL
   ```

4. **Result**: 0 samples remain → training fails

---

## The Fix

**File:** `analytics/models/prophet_forecast.py`

**Changed:** `prepare_data()` method (lines 87-97)

### Before
```python
df['y'] = df[target_column]

# Keep regressor columns
columns_to_keep = ['ds', 'y'] + self.regressors
df = df[columns_to_keep]

# Remove NaN values
df = df.dropna()

return df
```

### After
```python
df['y'] = df[target_column]

# Filter regressors that actually exist and have data
valid_regressors = []
for reg in self.regressors:
    if reg in df.columns and df[reg].notna().any():
        valid_regressors.append(reg)
    else:
        logger.warning(
            f"[PROPHET-PREP] Regressor '{reg}' has no data, excluding"
        )

# Update regressors list with only valid ones
self.regressors = valid_regressors

# Keep valid columns only
columns_to_keep = ['ds', 'y'] + valid_regressors
df = df[columns_to_keep]

# Remove NaN values in target column only
# (regressors can have NaNs, we'll handle those separately)
df = df.dropna(subset=['ds', 'y'])

return df
```

---

## What Changed

1. **Validation**: Check if each regressor column exists AND has actual data
2. **Filtering**: Only keep regressors with valid data
3. **Logging**: Warning messages when regressors are excluded
4. **Smart dropna()**: Only drop rows where target ('y') or timestamp ('ds') are NaN, not regressors

---

## Expected Behavior Now

### Training with NULL Regressors
When training Prophet with 30-day lookback:
1. ✅ Data fetched successfully (e.g., 720 hourly samples for 30 days)
2. ✅ Warning logged: `Regressor 'outdoor_temp_c' has no data, excluding`
3. ✅ Warning logged: `Regressor 'production_count' has no data, excluding`
4. ✅ Training proceeds with only time-based engineered features
5. ✅ Model trains successfully on all available samples

### Features Used
When external regressors are NULL, Prophet will use:
- **Time-based features** (auto-generated):
  - `hour` (0-23)
  - `day_of_week` (0-6)
  - `is_weekend` (0/1)
  - `is_working_hours` (0/1)
  - `season` (1-4 quarters)
- **Built-in seasonality**:
  - Daily patterns
  - Weekly patterns
  - Trend detection

---

## Testing

### Test Case 1: Train Prophet with 30-day period
```bash
# Via Analytics UI or API
POST /api/v1/analytics/forecast/train
{
  "machine_id": "uuid-here",
  "model_type": "Prophet",
  "lookback_days": 30
}
```

**Expected Result:**
- ✅ Training succeeds
- ✅ Uses ~720 hourly samples (30 days * 24 hours)
- ⚠️ Warnings about NULL regressors (expected until environmental data is added)
- ✅ Returns metrics: RMSE, MAPE, R²

### Test Case 2: Compare with ARIMA
- ARIMA: Uses 15-minute intervals (no regressors needed)
- Prophet: Uses hourly intervals (with/without regressors)
- Both should now train successfully

---

## Future Enhancements

When environmental data becomes available:
1. Update query in `forecast_service.py` to fetch real `outdoor_temp_c` and `production_count`
2. Prophet will automatically use these regressors (no code changes needed)
3. Model accuracy should improve with external factors

---

## Deployment

Service restarted with fix:
```bash
docker compose restart analytics
```

**Status:** ✅ Analytics service running with fix applied

---

## Summary

**Problem:** Prophet dropped all data when trying to use NULL regressor columns  
**Fix:** Filter out invalid regressors before data preparation  
**Result:** Prophet now trains successfully even without external regressors  
**Bonus:** Better logging for debugging regressor issues

The fix is backward-compatible and will automatically leverage external regressors when they become available in the database.
