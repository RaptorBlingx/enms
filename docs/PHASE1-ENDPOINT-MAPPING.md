# Phase 1: API Endpoint Mapping (v2 → v3)

**Date:** November 5, 2025  
**Status:** IN PROGRESS  
**Purpose:** Map all `/ovos/*` endpoints to new RESTful naming

---

## 📋 Endpoint Audit Results

### Current `/ovos/*` Endpoints (ovos_training.py)
File: `analytics/api/routes/ovos_training.py`  
Router prefix: `/api/v1/ovos`

| Current Endpoint | Method | Purpose | New Endpoint (v3) |
|-----------------|--------|---------|-------------------|
| `/train-baseline` | POST | Train baseline via SEU name | `/api/v1/baseline/train-seu` |
| `/energy-sources` | GET | List available energy sources | `/api/v1/energy-sources` |
| `/seus` | GET | List all SEUs | `/api/v1/seus` |

### Current `/ovos/*` Endpoints (ovos.py)
File: `analytics/api/routes/ovos.py`  
Router prefix: `/api/v1`

| Current Endpoint | Method | Purpose | New Endpoint (v3) |
|-----------------|--------|---------|-------------------|
| `/ovos/summary` | GET | Factory-level summary | `/api/v1/factory/summary` |
| `/ovos/top-consumers` | GET | Top energy consumers | `/api/v1/analytics/top-consumers` |
| `/ovos/machines/{machine_name}/status` | GET | Machine status by name | `/api/v1/machines/status/{machine_name}` |
| `/ovos/forecast/tomorrow` | GET | Next-day energy forecast | `/api/v1/forecast/short-term` |

### Endpoints with "OVOS" Tag Only (no path change needed)
These endpoints don't have `/ovos/` in path, just tagged for OVOS usage:

| File | Endpoint | Current Path | Action |
|------|----------|--------------|--------|
| `kpi.py` | KPI endpoints | `/api/v1/kpi/*` | Remove "OVOS" tag only |
| `multi_energy.py` | Multi-energy | `/api/v1/machines/*` | Remove "OVOS" tag only |

---

## 🎯 Refactoring Strategy

### Phase 1.1: Route File Reorganization

#### 1. Create New Route Files
- [x] **ovos_training.py** → Extract to multiple files:
  - `seus.py` - SEU management endpoints
  - Keep training in `baseline.py` (merge train-seu endpoint)
  - Keep energy sources in `energy_sources.py` (already exists)

#### 2. Update Existing Files
- [ ] **ovos.py** → Distribute endpoints:
  - `/ovos/summary` → `factory.py` (new file)
  - `/ovos/top-consumers` → `analytics.py` (new file)
  - `/ovos/machines/{name}/status` → `machines.py` (existing)
  - `/ovos/forecast/tomorrow` → `forecast.py` (existing)

#### 3. Tag Cleanup
- [ ] Remove "OVOS" tags from all endpoints
- [ ] Replace with domain-specific tags: "Factory", "Analytics", "SEU", "Baseline"

---

## 📝 Implementation Plan

### Step 1: Create `seus.py` (NEW)
**Purpose:** Centralized SEU management  
**Extract from:** `ovos_training.py::get_seus()`

```python
# analytics/api/routes/seus.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/seus", tags=["SEU Management"])
async def list_seus():
    """List all Significant Energy Uses (ISO 50001)"""
    # Move logic from ovos_training.py
    pass
```

### Step 2: Create `factory.py` (NEW)
**Purpose:** Factory-level analytics  
**Extract from:** `ovos.py::get_summary()`

```python
# analytics/api/routes/factory.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/factory/summary", tags=["Factory Analytics"])
async def get_factory_summary():
    """Get factory-level energy summary"""
    # Move logic from ovos.py
    pass
```

### Step 3: Create `analytics.py` (NEW)
**Purpose:** General analytics endpoints  
**Extract from:** `ovos.py::get_top_consumers()`

```python
# analytics/api/routes/analytics.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/analytics/top-consumers", tags=["Analytics"])
async def get_top_consumers():
    """Get top energy consuming machines"""
    # Move logic from ovos.py
    pass
```

### Step 4: Update `baseline.py`
**Action:** Add train-seu endpoint  
**Extract from:** `ovos_training.py::train_baseline()`

```python
# Add to existing baseline.py
@router.post("/baseline/train-seu", tags=["Baseline"])
async def train_baseline_via_seu(request: TrainBaselineRequest):
    """Train baseline using SEU name (voice-friendly)"""
    # Move logic from ovos_training.py
    pass
```

### Step 5: Update `machines.py`
**Action:** Add status-by-name endpoint  
**Extract from:** `ovos.py::get_machine_status_by_name()`

```python
# Add to existing machines.py
@router.get("/machines/status/{machine_name}", tags=["Machines"])
async def get_machine_status_by_name(machine_name: str):
    """Get machine status by name (instead of UUID)"""
    # Move logic from ovos.py
    pass
```

### Step 6: Update `forecast.py`
**Action:** Rename `/forecast/tomorrow` → `/forecast/short-term`  
**Extract from:** `ovos.py::forecast_tomorrow()`

```python
# Update existing forecast.py
@router.get("/forecast/short-term", tags=["Forecast"])
async def get_short_term_forecast(hours: int = 24):
    """Get short-term energy forecast (default 24 hours)"""
    # Move logic from ovos.py, make hours flexible
    pass
```

---

## 🔄 Backward Compatibility Layer

### Approach: Route Aliases with Deprecation Warnings

```python
# In main.py or deprecated_routes.py
from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

deprecated_router = APIRouter()

@deprecated_router.post("/ovos/train-baseline")
async def deprecated_train_baseline(request: Request, response: Response):
    """
    DEPRECATED: Use /api/v1/baseline/train-seu instead
    This endpoint will be removed on January 1, 2026
    """
    response.headers["Warning"] = '299 - "Deprecated endpoint. Use /api/v1/baseline/train-seu"'
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = "2026-01-01T00:00:00Z"
    
    # Forward to new endpoint
    return await baseline.train_baseline_via_seu(request)
```

### Deprecation Timeline
- **November 5 - December 31, 2025:** Both old and new endpoints work (warnings added)
- **January 1 - February 1, 2026:** Old endpoints return 410 Gone with migration guide
- **February 1, 2026:** Old endpoints removed completely

---

## ✅ Success Criteria

- [ ] Zero endpoints contain `/ovos/` in path
- [ ] Zero endpoints tagged with "OVOS" (use domain tags instead)
- [ ] All old endpoints still work via aliases (302 redirect or forward)
- [ ] Deprecation warnings added to all old endpoints
- [ ] 58/58 tests still passing
- [ ] New tests for new endpoint paths added
- [ ] BURAK-API-MIGRATION-GUIDE.md created
- [ ] Swagger UI organized with new tags

---

## 📊 Files to Modify

### New Files (Create)
- [ ] `analytics/api/routes/seus.py`
- [ ] `analytics/api/routes/factory.py`
- [ ] `analytics/api/routes/analytics.py`
- [ ] `analytics/api/routes/deprecated.py` (backward compatibility)
- [ ] `docs/BURAK-API-MIGRATION-GUIDE.md`

### Existing Files (Modify)
- [ ] `analytics/api/routes/baseline.py` (add train-seu endpoint)
- [ ] `analytics/api/routes/machines.py` (add status-by-name)
- [ ] `analytics/api/routes/forecast.py` (rename tomorrow → short-term)
- [ ] `analytics/api/routes/kpi.py` (remove OVOS tags)
- [ ] `analytics/api/routes/multi_energy.py` (remove OVOS tags)
- [ ] `analytics/main.py` (update router registrations)

### Files to Delete (After deprecation period)
- [ ] `analytics/api/routes/ovos_training.py` (logic moved to other files)
- [ ] `analytics/api/routes/ovos.py` (logic moved to other files)

---

## 🧪 Testing Strategy

### 1. Update Existing Tests
- [ ] `tests/test_ovos_regression_endpoints.py` → Update to use new paths
- [ ] Keep backward compatibility tests (verify old paths still work)

### 2. Add New Tests
- [ ] `tests/test_seus_api.py` - Test new SEUs endpoints
- [ ] `tests/test_factory_api.py` - Test new factory endpoints
- [ ] `tests/test_deprecation_warnings.py` - Verify warnings present

### 3. Integration Tests
- [ ] End-to-end workflow with new endpoints
- [ ] Verify all 58 existing tests pass with new paths

---

**Next Action:** Start creating new route files (seus.py, factory.py, analytics.py)
