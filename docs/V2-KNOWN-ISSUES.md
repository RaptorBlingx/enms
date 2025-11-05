# EnMS v2 - Known Issues & Bug Log

**Document Version:** 1.0  
**Last Updated:** November 5, 2025  
**Purpose:** Track bugs discovered during Phase 0 validation, before v3 transformation

---

## 🔴 Critical Bugs (FIXED)

### BUG-001: Multi-Energy Baseline Cross-Contamination
**Discovered:** November 5, 2025  
**Status:** ✅ FIXED (commit 6201a10)  
**Severity:** CRITICAL  

**Description:**
Multi-energy machines (e.g., Boiler-1 with electricity, natural_gas, steam) were sharing a single baseline model across all energy sources. This caused identical predictions regardless of energy source.

**Root Cause:**
- `energy_baselines` table lacked `energy_source_id` column
- Unique constraint was `(machine_id, model_version)` instead of `(machine_id, energy_source_id, model_version)`
- Service layer didn't pass energy_source_id to database functions

**Evidence:**
```json
// BEFORE FIX - All identical (WRONG)
Boiler-1 Electrical System (electricity): 166.09 kWh
Boiler-1 Natural Gas Burner (natural_gas): 166.09 kWh
Boiler-1 Steam Production (steam): 166.09 kWh

// AFTER FIX - Separate models (CORRECT)
Boiler-1 Electrical System: model_id=ace72e48...
Boiler-1 Natural Gas Burner: model_id=47a9efcc...
Boiler-1 Steam Production: model_id=1db6e0dd...
```

**Fix Implementation:**
1. Database migration 010: Added `energy_source_id UUID` column to `energy_baselines`
2. Updated unique constraint to include energy_source_id
3. Modified `database.py`: `save_baseline_model()`, `get_active_baseline_model()`, `deactivate_baseline_models()`
4. Modified `baseline_service.py`: `train_baseline()`, `predict_energy()`, `list_baseline_models()`
5. Updated API routes: `ovos_training.py` and `baseline.py`

**Files Changed:**
- `database/migrations/010-fix-multi-energy-baselines.sql`
- `analytics/database.py` (3 functions)
- `analytics/services/baseline_service.py` (3 functions)
- `analytics/api/routes/baseline.py`
- `analytics/api/routes/ovos_training.py`

**Tests Added:**
- `test_data_sanity.py::TestMultiEnergyMachines::test_boiler_three_energy_sources_independent`
- `test_data_sanity.py::TestMultiEnergyMachines::test_multi_energy_model_list_correct`

**Impact:**
- **Before:** Incorrect predictions for multi-energy machines (data integrity issue)
- **After:** Each energy source has independent model (correct behavior)

**Verification:**
- ✅ 58/58 tests passing
- ✅ Boiler-1 has 3 separate models with distinct IDs
- ✅ Predictions now use correct model per energy source

---

## 🟡 Minor Issues (DEFERRED)

*No minor issues discovered during Phase 0 validation.*

---

## 🟢 Enhancements (FUTURE)

### ENHANCEMENT-001: Natural Gas & Steam Data Collection
**Status:** FUTURE  
**Priority:** Low  

**Description:**
Multi-energy machines (Boiler-1, Furnace-1) have SEUs for natural_gas and steam, but no actual data tables exist (`natural_gas_readings`, `steam_readings`). Currently all training uses electricity data.

**Current Behavior:**
- Models train successfully but all use `energy_readings` table (electricity)
- No validation that energy source matches data source

**Recommendation:**
- Defer to Phase 2 or Phase 6 (data layer expansion)
- Not blocking v3 transformation
- Add tables when multi-energy data collection implemented

---

## 📊 Phase 0 Test Results

**Test Suite:** 58 total tests  
**Status:** ✅ ALL PASSING  

**Breakdown:**
- 27 integration tests (existing OVOS regression suite)
- 18 sanity tests (data quality validation)
- 13 consistency tests (API cross-validation)

**Test Files:**
- `tests/test_ovos_regression_endpoints.py` (27 tests)
- `tests/test_data_sanity.py` (18 tests)
- `tests/test_api_consistency.py` (13 tests)

**Execution Time:** ~67 seconds (full suite)

---

## 🎯 Phase 0 Conclusion

**Critical Bugs Found:** 1  
**Critical Bugs Fixed:** 1  
**Minor Bugs Found:** 0  
**Foundation Status:** ✅ SOLID

**Confidence Level:** HIGH - Safe to proceed with v3 transformation

**Next Phase:** Phase 1 (API Cleanup & Refactoring)

---

## 📝 Notes

- All fixes committed with `v2-bugfix:` prefix for traceability
- Migration 010 applied to production database
- No breaking changes to existing API contracts
- Backward compatibility maintained (UUID-based patterns still work)

**Last Review:** November 5, 2025
