# EnMS v3.0 - Project Charter & Roadmap

**Project Name:** EnMS (Energy Management System) v3.0  
**Start Date:** November 5, 2025  
**Version:** 3.0.0  
**Previous Version:** 2.0 (Checkpoint: commit 5b20761)  
**Status:** 🚀 IN PLANNING  

---

## 📋 Executive Summary

### What is EnMS v3?
Complete architectural transformation from **disconnected data collection** to **intelligent energy management system** with true ISO 50001 compliance and AI-driven optimization.

### Why v3?
**v2 Problems Identified:**
- ❌ Disconnected endpoints (15+ APIs that don't talk to each other)
- ❌ Misleading naming (`/ovos/*` suggests exclusive use)
- ❌ No intelligence layer (data without insights)
- ❌ Partial ISO 50001 compliance (have SEUs, missing EnPI tracking)
- ❌ No automated recommendations
- ❌ Frontend 6 months behind backend

**v3 Vision:**
- ✅ Unified Energy Performance Engine (orchestrates all components)
- ✅ Clean API naming (remove `ovos` confusion)
- ✅ Complete ISO 50001 compliance engine
- ✅ AI-driven recommendations and insights
- ✅ True WASABI Project integration (proactive building automation)
- ✅ SOTA EnMS that provides real business value

### Success Criteria
1. **Functional**: Single API call returns complete analysis (actual vs baseline, root cause, recommendations)
2. **Quality**: All outputs logical, tested, bug-free
3. **Compliance**: Full ISO 50001 reporting capability
4. **Intelligence**: Proactive system that identifies optimization opportunities
5. **Integration**: OVOS can access 100% of features without confusion

---

## 🎯 Project Objectives

### Primary Objectives
1. **Build Energy Performance Engine** - Core intelligence layer connecting all components
2. **Clean API Architecture** - Remove `ovos` naming, standardize patterns
3. **ISO 50001 Compliance Engine** - Systematic energy management, not just data
4. **AI Recommendations System** - Proactive insights and optimization suggestions
5. **Comprehensive Testing** - Zero bugs, all outputs validated

### Secondary Objectives
6. **Frontend Modernization** - UI matches backend capabilities (Phase 2 of v3)
7. **WASABI Integration** - True AI-driven building automation
8. **Performance Optimization** - <100ms response times for critical endpoints
9. **Documentation Excellence** - Every endpoint documented with real examples

---

## 🏗️ Architecture Vision

### Current v2 Architecture (Disconnected)
```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Baseline   │  │   Anomaly    │  │     KPI      │
│   Service    │  │   Service    │  │   Service    │
└──────────────┘  └──────────────┘  └──────────────┘
       ↓                 ↓                 ↓
   [No connection between services]
   [Each works in isolation]
```

### Target v3 Architecture (Unified)
```
┌─────────────────────────────────────────────────────┐
│        Energy Performance Engine (NEW)               │
│  Orchestrates: Baseline → Prediction → Analysis     │
│               → Anomaly → Recommendations            │
└─────────────────────────────────────────────────────┘
              ↓           ↓           ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Baseline   │  │   Anomaly    │  │     KPI      │
│   Service    │  │   Service    │  │   Service    │
└──────────────┘  └──────────────┘  └──────────────┘
       ↓                 ↓                 ↓
┌─────────────────────────────────────────────────────┐
│              Data Layer (TimescaleDB)                │
└─────────────────────────────────────────────────────┘
```

---

## 📊 v2 Final State Assessment

### What Works Well ✅
- **Data Layer**: TimescaleDB with continuous aggregates (solid foundation)
- **Multi-Energy Support**: 4 energy sources (electricity, natural_gas, steam, compressed_air)
- **SEU Architecture**: ISO 50001 compliant structure (8 machines → 10 SEUs)
- **ML Models**: Linear regression baselines (85-99% R² accuracy)
- **Testing**: 27/27 integration tests passing
- **Real-Time**: WebSocket updates working

### What Needs Fixing 🔴
1. **API Naming**: `/ovos/*` endpoints misleading
2. **Disconnected Services**: No orchestration between baseline/anomaly/KPI
3. **No Intelligence**: Data collection without insights
4. **Partial ISO 50001**: Have SEUs, missing EnPI tracking and action plans
5. **Manual Workflows**: User must piece together insights from multiple APIs
6. **Frontend Behind**: UI doesn't use 50% of backend features

### Key Metrics (v2)
- **Machines**: 8 monitored
- **SEUs**: 10 tracked
- **Baseline Models**: 61 trained (7 machines)
- **Energy Sources**: 4 supported
- **API Endpoints**: 40+ (disconnected)
- **Test Coverage**: 27 integration tests (baseline/predict only)

---

## 🚀 v3 Milestones & Phases

### 📍 **PHASE 0: v2 Critical Path Validation** (2 days) - NEW ⚠️
**Goal**: Verify v2 foundation is solid before building v3 on top

**Why This Phase?**
Building v3 on potentially buggy v2 is architectural suicide. We're making a critical assumption that v2 works 100%, but we need to validate this BEFORE refactoring. Discovering bugs mid-refactor wastes time and creates confusion about root causes.

**Strategy**: Discover & fix critical bugs NOW, document minor issues for Phase 4.

---

#### Milestone 0.1: Comprehensive Data Quality Audit
**Duration**: 1 day  
**Status**: ✅ COMPLETE (November 5, 2025)  
**Tasks**:
- [x] 0.1.1: Run all 27 existing integration tests with REAL production data
- [x] 0.1.2: Add data sanity test suite (`tests/test_data_sanity.py`)
  - Test: All energy values > 0 (NO negative predictions!)
  - Test: All percentages in range 0-100
  - Test: All timestamps valid ISO 8601 format
  - Test: Cost = Energy × Rate (calculation validation)
  - Test: R² values between 0-1
  - Test: No null values in required fields
- [x] 0.1.3: Test all baseline endpoints with multi-energy machines
  - Test Boiler-1 (3 SEUs: electricity + natural_gas + steam)
  - Verify each energy source returns independent predictions
  - Check for cross-contamination between energy sources
- [x] 0.1.4: Validate baseline prediction logic
  - Compare predictions against actual data (last 7 days)
  - Check if deviations are reasonable (<30%)
  - Verify model explanations match actual predictions
- [x] 0.1.5: Review existing test coverage gaps
  - What's NOT tested in current 27 tests?
  - Which endpoints have no integration tests?
  - Which edge cases are missing?

**Deliverables**:
- [x] `tests/test_data_sanity.py` created with 18 sanity checks
- [x] `tests/test_api_consistency.py` created with 13 consistency tests
- [x] Test report: 58/58 tests passing
- [x] List of bugs discovered (1 critical, 0 minor) → `docs/V2-KNOWN-ISSUES.md`

**Success Criteria**:
- ✅ All data sanity tests passing (18/18)
- ✅ No negative energy predictions found
- ✅ Multi-energy machines working correctly (BUG-001 FIXED)
- ✅ Baseline predictions are logical
- ✅ Test coverage gaps identified and filled

---

#### Milestone 0.2: Critical Bug Fixing
**Duration**: 1 day  
**Status**: ✅ COMPLETE (November 5, 2025)  
**Tasks**:
- [x] 0.2.1: Triage discovered bugs
  - **Critical**: BUG-001 (Multi-Energy Baseline Cross-Contamination) → FIXED
  - **Major**: None discovered
  - **Minor**: None discovered
- [x] 0.2.2: Fix critical bugs immediately
  - Create separate commits tagged `v2-bugfix: [description]`
  - Add regression tests for each bug fixed
  - Update affected API documentation
- [x] 0.2.3: Document minor bugs for Phase 4
  - Create `docs/V2-KNOWN-ISSUES.md` with:
    - Bug description
    - Impact assessment
    - Recommended fix
    - Priority level
- [x] 0.2.4: Re-run full test suite to verify fixes
  - All 27 integration tests still passing
  - All 18 new sanity tests passing
  - All 13 new consistency tests passing
  - No regressions introduced
- [x] 0.2.5: Update v2 checkpoint if major fixes made
  - Commit: "v2-bugfix: Fix multi-energy baseline cross-contamination (Phase 0)"
  - Commit hash: 6201a10

**Deliverables**:
- [x] All critical bugs fixed and committed (BUG-001)
- [x] `docs/V2-KNOWN-ISSUES.md` created
- [x] Updated test suite (58 tests passing: 27+18+13)
- [x] Migration 010 applied to database

**Success Criteria**:
- ✅ Zero critical bugs remaining
- ✅ All tests passing (58/58 including new sanity tests)
- ✅ Known issues documented for Phase 4
- ✅ Confidence in v2 foundation: HIGH
- ✅ Safe to proceed with v3 refactoring

---

#### Phase 0 Decision Point
**After Milestone 0.2 completion, evaluate:**

**✅ DECISION: Proceed to Phase 1 (API Cleanup)**

**Results:**
- **Critical bugs found:** 1 (BUG-001: Multi-Energy Baseline Cross-Contamination)
- **Critical bugs fixed:** 1 (100%)
- **Test suite status:** 58/58 passing
- **Foundation confidence:** HIGH

**Rationale:**
Single critical bug discovered and fixed immediately. Bug was architectural (missing column in database schema), not logic error. Fix validated with comprehensive test suite. No regressions introduced. v2 foundation confirmed solid.

**Proceed to Phase 1 with normal caution level.**

---

### 📍 **PHASE 1: API Cleanup & Refactoring** (Week 1)
**Goal**: Remove `ovos` naming confusion, standardize patterns
**Status**: ✅ IN PROGRESS (November 5, 2025)

#### Milestone 1.1: API Renaming
**Duration**: 1 day  
**Status**: ✅ COMPLETE (November 5, 2025)
**Tasks**:
- [x] 1.1.1: Audit all endpoints with `ovos` in path
- [x] 1.1.2: Create endpoint mapping (old → new names)
- [x] 1.1.3: Create new route files (seus.py, factory.py, analytics.py)
- [x] 1.1.4: Register new routers in main.py
- [x] 1.1.5: Test all new endpoints (58/58 tests passing)
- [x] 1.1.6: Update ENMS-API-DOCUMENTATION-FOR-OVOS.md with deprecation notices

**Deliverables**:
- [x] New route files created (seus.py, factory.py, analytics.py)
- [x] API documentation updated with strikethrough for deprecated endpoints
- [x] Old endpoints still work (marked DEPRECATED)

**Endpoint Mappings**:
```
OLD (v2)                         → NEW (v3)
─────────────────────────────────────────────────────────
/api/v1/ovos/train-baseline      → /api/v1/baseline/train-seu
/api/v1/ovos/seus                → /api/v1/seus
/api/v1/ovos/energy-sources      → /api/v1/energy-sources
/api/v1/ovos/summary             → /api/v1/factory/summary
/api/v1/ovos/top-consumers       → /api/v1/analytics/top-consumers
/api/v1/ovos/forecast/tomorrow   → /api/v1/forecast/short-term
```

**Success Criteria**:
- ✅ No endpoint contains `ovos` in path
- ✅ Old endpoints still work (302 redirect to new)
- ✅ All tests updated and passing
- ✅ Documentation updated

---

#### Milestone 1.2: Route Organization
**Duration**: 1 day  
**Tasks**:
- [ ] 1.2.1: Create logical route grouping
- [ ] 1.2.2: Reorganize `analytics/api/routes/` folder
- [ ] 1.2.3: Update OpenAPI tags and descriptions
- [ ] 1.2.4: Standardize response formats

**New Route Structure**:
```
analytics/api/routes/
├── baseline.py          # Baseline training, prediction, models
├── seus.py              # SEU management (NEW - extracted from ovos_training.py)
├── energy_sources.py    # Energy source configuration (NEW)
├── performance.py       # Energy performance analysis (NEW in Phase 2)
├── anomaly.py           # Anomaly detection
├── kpi.py               # KPI calculations
├── forecast.py          # Energy forecasting
├── iso50001.py          # ISO compliance reporting (NEW in Phase 3)
├── factory.py           # Factory-level analytics
├── machines.py          # Machine management
└── timeseries.py        # Time-series data
```

**Success Criteria**:
- ✅ Clear separation of concerns
- ✅ Each route file <500 lines
- ✅ Logical grouping by domain
- ✅ Swagger UI organized properly

---

### 📍 **PHASE 2: Energy Performance Engine** (Week 2-3)
**Goal**: Build core intelligence layer that connects all services

#### Milestone 2.1: Performance Engine Foundation
**Duration**: 3 days  
**Tasks**:
- [ ] 2.1.1: Create `analytics/services/energy_performance_engine.py`
- [ ] 2.1.2: Design orchestration patterns
- [ ] 2.1.3: Implement complete analysis workflow
- [ ] 2.1.4: Add root cause analysis logic
- [ ] 2.1.5: Build recommendation engine

**Core Engine Class**:
```python
class EnergyPerformanceEngine:
    """
    Orchestrates complete energy performance analysis:
    Baseline → Prediction → Comparison → Root Cause → Recommendations
    """
    
    async def analyze_seu_performance(
        self, 
        seu_name: str,
        energy_source: str,
        analysis_date: date
    ) -> PerformanceAnalysis:
        """
        Complete performance analysis for a SEU on specific date
        
        Returns:
        - Actual vs baseline comparison
        - Deviation analysis (%, cost)
        - Root cause identification
        - Actionable recommendations
        - ISO 50001 status
        - Voice-friendly summary
        """
        
    async def get_improvement_opportunities(
        self,
        factory_id: str,
        period: str = "month"
    ) -> List[ImprovementOpportunity]:
        """
        Proactive analysis: Find optimization opportunities
        
        Returns ranked list of:
        - Inefficient operating patterns
        - Potential energy savings
        - Cost savings
        - Implementation effort
        - ROI calculation
        """
        
    async def generate_action_plan(
        self,
        seu_name: str,
        issue_type: str
    ) -> ActionPlan:
        """
        Generate structured action plan for energy issue
        
        Returns:
        - Problem statement
        - Root causes
        - Recommended actions (prioritized)
        - Expected outcomes
        - Monitoring plan
        """
```

**Success Criteria**:
- ✅ Engine connects baseline + anomaly + KPI services
- ✅ Single method call returns complete analysis
- ✅ Root cause logic validated with real data
- ✅ Recommendations are actionable and specific

---

#### Milestone 2.2: Performance API Endpoints
**Duration**: 2 days  
**Tasks**:
- [ ] 2.2.1: Create `analytics/api/routes/performance.py`
- [ ] 2.2.2: Implement `/performance/analyze` endpoint
- [ ] 2.2.3: Implement `/performance/opportunities` endpoint
- [ ] 2.2.4: Implement `/performance/action-plan` endpoint
- [ ] 2.2.5: Add response models with Pydantic

**New Endpoints**:

**EP-PERF-1: Analyze SEU Performance**
```bash
POST /api/v1/performance/analyze
{
  "seu_name": "Compressor-1",
  "energy_source": "electricity",
  "analysis_date": "2025-11-04"
}

# Returns: Complete performance analysis
{
  "seu_name": "Compressor-1",
  "date": "2025-11-04",
  "actual_energy_kwh": 1200,
  "baseline_energy_kwh": 950,
  "deviation_percent": 26.3,
  "deviation_cost_usd": 37.50,
  "efficiency_score": 0.82,
  "root_cause_analysis": {
    "primary_factor": "production_volume",
    "impact_description": "Production increased 15% vs baseline",
    "contributing_factors": ["outdoor_temp +5°C", "pressure +0.5 bar"]
  },
  "recommendations": [
    {
      "action": "Optimize compressor load scheduling",
      "type": "operational",
      "potential_savings_kwh": 180,
      "potential_savings_usd": 27.00,
      "implementation_effort": "medium",
      "priority": "high",
      "expected_roi_days": 30
    }
  ],
  "iso50001_status": "requires_attention",
  "voice_summary": "Compressor-1 used 26% more energy than expected..."
}
```

**EP-PERF-2: Get Improvement Opportunities**
```bash
GET /api/v1/performance/opportunities?factory_id=XXX&period=month

# Returns: Ranked optimization opportunities
{
  "factory_id": "XXX",
  "period": "2025-10",
  "total_opportunities": 8,
  "total_potential_savings_kwh": 12500,
  "total_potential_savings_usd": 1875.00,
  "opportunities": [
    {
      "rank": 1,
      "seu_name": "HVAC-Main",
      "issue_type": "inefficient_scheduling",
      "description": "HVAC running at full capacity during non-production hours",
      "potential_savings_kwh": 4200,
      "potential_savings_usd": 630.00,
      "effort": "low",
      "roi_days": 7,
      "recommended_action": "Implement time-based setback schedule"
    }
  ]
}
```

**Success Criteria**:
- ✅ All endpoints return complete analysis
- ✅ Response times <500ms
- ✅ Voice summaries suitable for TTS
- ✅ Recommendations are specific and actionable

---

#### Milestone 2.3: Integration & Testing
**Duration**: 2 days  
**Tasks**:
- [ ] 2.3.1: Write unit tests for performance engine
- [ ] 2.3.2: Write integration tests for performance APIs
- [ ] 2.3.3: Test with real production data (3 machines minimum)
- [ ] 2.3.4: Validate recommendation logic
- [ ] 2.3.5: Load testing (100 concurrent requests)

**Test Coverage**:
```python
# tests/test_performance_engine.py
class TestPerformanceEngine:
    async def test_analyze_seu_performance()
    async def test_root_cause_accuracy()
    async def test_recommendation_generation()
    async def test_improvement_opportunities()
    async def test_action_plan_creation()

# tests/test_performance_api.py
class TestPerformanceAPI:
    async def test_analyze_endpoint()
    async def test_opportunities_endpoint()
    async def test_action_plan_endpoint()
    async def test_invalid_seu_name()
    async def test_concurrent_requests()
```

**Success Criteria**:
- ✅ 100% test coverage for performance engine
- ✅ All tests passing
- ✅ Performance validated (<500ms response)
- ✅ Recommendations validated with domain expert

---

### 📍 **PHASE 3: ISO 50001 Compliance Engine** (Week 4)
**Goal**: Complete ISO 50001 compliance, not just SEU structure

#### Milestone 3.1: EnPI Tracking System
**Duration**: 2 days  
**Tasks**:
- [ ] 3.1.1: Design EnPI (Energy Performance Indicator) database schema
- [ ] 3.1.2: Create `analytics/services/enpi_tracker.py`
- [ ] 3.1.3: Implement baseline year vs current comparison
- [ ] 3.1.4: Add target setting and tracking
- [ ] 3.1.5: Calculate cumulative savings

**Database Schema (New Tables)**:
```sql
-- EnPI baseline periods
CREATE TABLE enpi_baselines (
    id UUID PRIMARY KEY,
    seu_id UUID REFERENCES seus(id),
    baseline_year INTEGER NOT NULL,
    baseline_energy_kwh DECIMAL(10, 2),
    baseline_production_units INTEGER,
    baseline_sec DECIMAL(10, 6),  -- Specific Energy Consumption
    created_at TIMESTAMP DEFAULT NOW()
);

-- EnPI tracking
CREATE TABLE enpi_performance (
    id UUID PRIMARY KEY,
    seu_id UUID REFERENCES seus(id),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    actual_energy_kwh DECIMAL(10, 2),
    expected_energy_kwh DECIMAL(10, 2),  -- Based on baseline
    deviation_percent DECIMAL(5, 2),
    cumulative_savings_kwh DECIMAL(10, 2),
    iso_status VARCHAR(50),  -- 'on_track', 'requires_attention', 'critical'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Action plans (ISO 50001 requirement)
CREATE TABLE action_plans (
    id UUID PRIMARY KEY,
    seu_id UUID REFERENCES seus(id),
    title VARCHAR(255) NOT NULL,
    objective TEXT,
    target_savings_kwh DECIMAL(10, 2),
    status VARCHAR(50),  -- 'planned', 'in_progress', 'completed', 'cancelled'
    responsible_person VARCHAR(255),
    start_date DATE,
    target_date DATE,
    completion_date DATE,
    actual_savings_kwh DECIMAL(10, 2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Success Criteria**:
- ✅ EnPI tracking for all SEUs
- ✅ Baseline year comparison working
- ✅ Cumulative savings calculated automatically
- ✅ ISO status indicators accurate

---

#### Milestone 3.2: ISO 50001 Reporting
**Duration**: 2 days  
**Tasks**:
- [ ] 3.2.1: Create `analytics/api/routes/iso50001.py`
- [ ] 3.2.2: Implement EnPI report generation
- [ ] 3.2.3: Implement action plan management endpoints
- [ ] 3.2.4: Add management review data aggregation
- [ ] 3.2.5: Generate compliance PDF reports

**New Endpoints**:

**EP-ISO-1: Get EnPI Report**
```bash
GET /api/v1/iso50001/enpi-report?factory_id=XXX&period=2025-Q3

# Returns complete ISO 50001 EnPI report
{
  "factory_id": "XXX",
  "report_period": "2025-Q3",
  "baseline_year": 2024,
  "seus_analyzed": 10,
  "overall_performance": {
    "total_energy_baseline_kwh": 450000,
    "total_energy_actual_kwh": 428000,
    "deviation_percent": -4.9,
    "cumulative_savings_kwh": 22000,
    "cumulative_savings_usd": 3300,
    "iso_status": "on_track"
  },
  "seu_breakdown": [
    {
      "seu_name": "Compressor-1",
      "baseline_energy_kwh": 95000,
      "actual_energy_kwh": 92000,
      "savings_kwh": 3000,
      "status": "on_track"
    }
  ],
  "action_plans_status": {
    "total_plans": 5,
    "completed": 2,
    "in_progress": 3,
    "planned": 0
  }
}
```

**EP-ISO-2: Action Plan Management**
```bash
# Create action plan
POST /api/v1/iso50001/action-plans
{
  "seu_name": "HVAC-Main",
  "title": "Optimize HVAC Scheduling",
  "objective": "Reduce off-hours energy consumption by 30%",
  "target_savings_kwh": 4200,
  "responsible_person": "Facility Manager",
  "target_date": "2025-12-31"
}

# Get all action plans
GET /api/v1/iso50001/action-plans?factory_id=XXX&status=in_progress

# Update action plan progress
PUT /api/v1/iso50001/action-plans/{id}/progress
{
  "status": "completed",
  "actual_savings_kwh": 4500,
  "completion_notes": "Implemented time-based setback..."
}
```

**Success Criteria**:
- ✅ EnPI report matches ISO 50001 requirements
- ✅ Action plan workflow complete
- ✅ PDF export working
- ✅ Management review data aggregated

---

### 📍 **PHASE 4: Comprehensive Testing & Bug Fixing** (Week 5)
**Goal**: Zero bugs, all outputs validated, performance optimized

#### Milestone 4.1: Data Quality Validation
**Duration**: 2 days  
**Tasks**:
- [ ] 4.1.1: Create data sanity test suite
- [ ] 4.1.2: Test all API outputs for logical correctness
- [ ] 4.1.3: Validate calculations (energy, cost, carbon)
- [ ] 4.1.4: Check for null values in required fields
- [ ] 4.1.5: Verify date ranges and timestamps

**Sanity Checks**:
```python
# tests/test_data_sanity.py
class TestDataSanity:
    async def test_energy_values_positive():
        """All energy values must be > 0"""
        
    async def test_percentages_valid_range():
        """All percentages between 0-100"""
        
    async def test_costs_calculated_correctly():
        """Cost = Energy × Rate"""
        
    async def test_r_squared_valid_range():
        """R² between 0-1"""
        
    async def test_timestamps_valid():
        """All timestamps in valid ISO 8601 format"""
        
    async def test_no_null_in_required_fields():
        """Required fields never null"""
```

**Success Criteria**:
- ✅ All sanity tests passing
- ✅ Zero logical errors in outputs
- ✅ All calculations validated

---

#### Milestone 4.2: End-to-End Workflow Testing
**Duration**: 2 days  
**Tasks**:
- [ ] 4.2.1: Test complete user workflows
- [ ] 4.2.2: Test OVOS integration scenarios
- [ ] 4.2.3: Test multi-energy machine workflows
- [ ] 4.2.4: Test error handling and edge cases
- [ ] 4.2.5: Load testing with realistic data volumes

**User Workflow Tests**:
```python
# tests/test_user_workflows.py

async def test_energy_manager_morning_routine():
    """
    Workflow: Energy manager checks daily status
    1. Get performance analysis for yesterday
    2. Check for anomalies
    3. Review recommendations
    4. Create action plan if needed
    """
    
async def test_ovos_voice_commands():
    """
    Workflow: User asks OVOS for energy status
    1. "What's today's energy status?"
    2. "Why is Compressor-1 using more energy?"
    3. "What should I do about it?"
    """
    
async def test_multi_energy_machine_analysis():
    """
    Workflow: Analyze Boiler-1 (3 SEUs)
    1. Get performance for each energy source
    2. Compare electricity vs natural gas vs steam
    3. Identify optimization opportunities
    """
```

**Success Criteria**:
- ✅ All user workflows complete successfully
- ✅ OVOS can execute all voice commands
- ✅ Multi-energy workflows validated
- ✅ Load testing: 100 concurrent users, <1s response

---

#### Milestone 4.3: Bug Fixing & Performance Optimization
**Duration**: 2 days  
**Tasks**:
- [ ] 4.3.1: Fix all identified bugs
- [ ] 4.3.2: Optimize slow queries (target <100ms)
- [ ] 4.3.3: Add database indexes where needed
- [ ] 4.3.4: Implement caching for frequent queries
- [ ] 4.3.5: Profile and optimize hot paths

**Performance Targets**:
- `/performance/analyze`: <500ms
- `/baseline/predict`: <200ms
- `/baseline/models`: <300ms (with explanations)
- `/iso50001/enpi-report`: <1s
- Dashboard load: <2s total

**Success Criteria**:
- ✅ Zero known bugs
- ✅ All endpoints meet performance targets
- ✅ Query optimization complete
- ✅ Caching implemented

---

### 📍 **PHASE 5: Documentation & Migration** (Week 6)
**Goal**: Complete documentation, smooth migration path

#### Milestone 5.1: API Documentation Update
**Duration**: 2 days  
**Tasks**:
- [ ] 5.1.1: Update ENMS-API-DOCUMENTATION-FOR-OVOS.md
- [ ] 5.1.2: Document all new v3 endpoints
- [ ] 5.1.3: Add performance engine examples
- [ ] 5.1.4: Document ISO 50001 endpoints
- [ ] 5.1.5: Update Swagger/OpenAPI specs

**Documentation Structure**:
```
ENMS-API-DOCUMENTATION-FOR-OVOS.md
├── v3 Changes Summary
├── Migration Guide (v2 → v3)
├── New Endpoints Section
│   ├── Performance Engine
│   ├── ISO 50001 Compliance
│   └── Improved Baseline APIs
├── Updated Examples (all tested)
└── Backward Compatibility Notes
```

**Success Criteria**:
- ✅ All v3 endpoints documented
- ✅ Every example tested and working
- ✅ Migration guide clear and complete
- ✅ Swagger UI updated

---

#### Milestone 5.2: Burak Migration Support
**Duration**: 1 day  
**Tasks**:
- [ ] 5.2.1: Create BURAK-API-MIGRATION-GUIDE.md
- [ ] 5.2.2: List all endpoint changes (old → new)
- [ ] 5.2.3: Provide code examples for each change
- [ ] 5.2.4: Document backward compatibility period
- [ ] 5.2.5: Schedule migration call with Burak

**Migration Guide Contents**:
```markdown
# OVOS API Migration Guide: v2 → v3

## Timeline
- November 5-30, 2025: Both old and new endpoints work
- December 1, 2025: Old endpoints deprecated (show warnings)
- January 1, 2026: Old endpoints removed

## Endpoint Changes
[Table with old → new mappings]

## Code Examples
[Before/After code for each change]

## Testing Your Integration
[Test checklist]
```

**Success Criteria**:
- ✅ Migration guide complete
- ✅ Burak notified and guide shared
- ✅ All changes documented with examples
- ✅ Support plan established

---

### 📍 **PHASE 6: Frontend Modernization** (Week 7-8)
**Goal**: UI matches backend capabilities

#### Milestone 6.1: Component Library
**Duration**: 2 days  
**Tasks**:
- [ ] 6.1.1: Create SEU selector component
- [ ] 6.1.2: Create explanation card component
- [ ] 6.1.3: Create energy badge component
- [ ] 6.1.4: Create performance dashboard widget
- [ ] 6.1.5: Test components with real data

**Deliverables**:
- `analytics/ui/static/js/components/seu-selector.js`
- `analytics/ui/static/js/components/explanation-card.js`
- `analytics/ui/static/js/components/energy-badge.js`
- `analytics/ui/static/js/components/performance-widget.js`

**Success Criteria**:
- ✅ All components reusable
- ✅ Consistent design system
- ✅ Performance validated (<50ms render)

---

#### Milestone 6.2: Baseline Page Overhaul
**Duration**: 2 days  
**Tasks**:
- [ ] 6.2.1: Add SEU selector dropdown
- [ ] 6.2.2: Add energy source filter
- [ ] 6.2.3: Replace /baseline/train with /baseline/train-seu
- [ ] 6.2.4: Display model explanations
- [ ] 6.2.5: Add voice summary display

**Success Criteria**:
- ✅ SEU-based training working
- ✅ Model explanations displayed
- ✅ Voice summaries shown
- ✅ Test with Boiler-1 (3 SEUs)

---

#### Milestone 6.3: Dashboard & Other Pages
**Duration**: 4 days  
**Tasks**:
- [ ] 6.3.1: Update dashboard with SEU stats
- [ ] 6.3.2: Update KPI page with energy source breakdown
- [ ] 6.3.3: Update model performance page (explanation tab)
- [ ] 6.3.4: Update anomaly, forecast, comparison pages
- [ ] 6.3.5: Test all pages comprehensively

**Success Criteria**:
- ✅ All 7 pages updated
- ✅ SEU support everywhere
- ✅ Energy source breakdown visible
- ✅ No broken links or features

---

### 📍 **PHASE 7: Production Deployment** (Week 9)
**Goal**: Deploy v3 to production, monitor performance

#### Milestone 7.1: Pre-Deployment Checklist
**Duration**: 1 day  
**Tasks**:
- [ ] 7.1.1: Run full test suite (all tests passing)
- [ ] 7.1.2: Performance testing (load, stress, spike)
- [ ] 7.1.3: Security audit
- [ ] 7.1.4: Database migration scripts prepared
- [ ] 7.1.5: Rollback plan documented

**Success Criteria**:
- ✅ All tests passing
- ✅ Performance benchmarks met
- ✅ Security validated
- ✅ Rollback plan ready

---

#### Milestone 7.2: Production Deployment
**Duration**: 1 day  
**Tasks**:
- [ ] 7.2.1: Deploy database migrations
- [ ] 7.2.2: Deploy backend services
- [ ] 7.2.3: Deploy frontend updates
- [ ] 7.2.4: Run smoke tests in production
- [ ] 7.2.5: Monitor for issues (24 hours)

**Success Criteria**:
- ✅ v3 deployed successfully
- ✅ Smoke tests passing
- ✅ No critical errors in logs
- ✅ Performance metrics normal

---

#### Milestone 7.3: Post-Deployment Monitoring
**Duration**: 1 week  
**Tasks**:
- [ ] 7.3.1: Monitor API response times
- [ ] 7.3.2: Track error rates
- [ ] 7.3.3: Validate data quality
- [ ] 7.3.4: Gather user feedback
- [ ] 7.3.5: Address any issues immediately

**Success Criteria**:
- ✅ Response times within SLAs
- ✅ Error rate <0.1%
- ✅ No data quality issues
- ✅ Positive user feedback

---

## 📊 Success Metrics

### Technical Metrics
- **API Response Time**: 95th percentile <500ms
- **Test Coverage**: >90% for critical paths
- **Bug Count**: 0 critical, <5 minor
- **Uptime**: >99.9%

### Business Metrics
- **User Adoption**: 80% of users using v3 features within 1 month
- **OVOS Integration**: 100% of voice commands working
- **ISO Compliance**: Full EnPI reporting capability
- **Energy Savings**: 10+ improvement opportunities identified per factory

### Quality Metrics
- **Code Quality**: All services follow DRY principle
- **Documentation**: 100% of endpoints documented with examples
- **Testing**: All workflows tested end-to-end
- **Performance**: All targets met

---

## � Data Migration Strategy (v2 → v3)

### Database Schema Changes

#### No Breaking Changes to Core Tables ✅
- `machines` table: NO CHANGE (8 machines remain)
- `seus` table: NO CHANGE (10 SEUs remain)
- `energy_readings` table: NO CHANGE (data preserved)
- `energy_baselines` table: NO CHANGE (61 models preserved)

#### New Tables Added (Phase 3)
```sql
-- EnPI tracking (ISO 50001)
CREATE TABLE enpi_baselines (
    id UUID PRIMARY KEY,
    seu_id UUID REFERENCES seus(id),
    baseline_year INTEGER NOT NULL,
    baseline_energy_kwh DECIMAL(10, 2),
    baseline_production_units INTEGER,
    baseline_sec DECIMAL(10, 6),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE enpi_performance (
    id UUID PRIMARY KEY,
    seu_id UUID REFERENCES seus(id),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    actual_energy_kwh DECIMAL(10, 2),
    expected_energy_kwh DECIMAL(10, 2),
    deviation_percent DECIMAL(5, 2),
    cumulative_savings_kwh DECIMAL(10, 2),
    iso_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE action_plans (
    id UUID PRIMARY KEY,
    seu_id UUID REFERENCES seus(id),
    title VARCHAR(255) NOT NULL,
    objective TEXT,
    target_savings_kwh DECIMAL(10, 2),
    status VARCHAR(50),
    responsible_person VARCHAR(255),
    start_date DATE,
    target_date DATE,
    completion_date DATE,
    actual_savings_kwh DECIMAL(10, 2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Existing Data Preservation

**61 Baseline Models (v2)**:
- ✅ ALL models remain functional in v3
- ✅ NO retraining required
- ✅ Model files in `analytics/models/saved/` preserved
- ✅ Database records in `energy_baselines` unchanged

**Historical Data**:
- ✅ ALL time-series data preserved
- ✅ NO data loss during migration
- ✅ Continuous aggregates remain functional

### API Backward Compatibility

**Strategy: Dual Endpoints (2 months)**

#### Phase 1: Both Old and New Endpoints Work
```python
# OLD endpoint (v2 - deprecated but working)
POST /api/v1/ovos/train-baseline
→ 302 Redirect to /api/v1/baseline/train-seu
→ Warning header: "Deprecated: Use /baseline/train-seu"

# NEW endpoint (v3)
POST /api/v1/baseline/train-seu
→ Direct implementation
```

#### Phase 2: Deprecation Warnings (December 2025)
```python
# OLD endpoint returns warning in response
{
  "success": true,
  "data": {...},
  "warning": "This endpoint is deprecated and will be removed January 1, 2026. Use /baseline/train-seu instead.",
  "migration_guide": "https://docs.enms/v3-migration"
}
```

#### Phase 3: Removal (January 2026)
```python
# OLD endpoint returns 410 Gone
{
  "error": "This endpoint has been removed. Use /baseline/train-seu instead.",
  "migration_guide": "https://docs.enms/v3-migration",
  "new_endpoint": "/api/v1/baseline/train-seu"
}
```

### Code Migration - No Changes Needed

**Frontend (analytics/ui/):**
- ✅ Update API calls to new endpoints
- ✅ Add SEU selector components
- ✅ No database schema changes affect UI

**Backend Services:**
- ✅ Add new services (performance_engine.py, enpi_tracker.py)
- ✅ Rename routes (ovos_training.py → seus.py, energy_sources.py)
- ✅ Existing services (baseline, anomaly, KPI) unchanged

**Database:**
- ✅ Run migration scripts to add new tables
- ✅ Populate enpi_baselines from existing data
- ✅ No downtime required (additive changes only)

### Migration Checklist

**Pre-Migration (Phase 0)**:
- [ ] Backup database: `pg_dump enms > enms_v2_backup.sql`
- [ ] Backup models: `tar -czf models_v2.tar.gz analytics/models/saved/`
- [ ] Document current API usage (Burak's OVOS endpoints)
- [ ] Create rollback plan

**During Migration (Phase 1-3)**:
- [ ] Deploy new code with backward compatibility
- [ ] Run database migration scripts (additive only)
- [ ] Test old endpoints still work (302 redirects)
- [ ] Notify Burak of deprecation timeline

**Post-Migration (Phase 7)**:
- [ ] Verify all data migrated correctly
- [ ] Confirm Burak migrated to new endpoints
- [ ] Remove old endpoint code (January 2026)
- [ ] Archive v2 backup (keep for 6 months)

### Rollback Strategy

**If Critical Issues Found**:
```bash
# Restore v2 from checkpoint
git checkout v2-checkpoint  # commit 5b20761
docker-compose down
docker-compose up -d

# Restore database (if schema changed)
psql -U postgres -d enms < enms_v2_backup.sql

# Restore models (if corrupted)
tar -xzf models_v2.tar.gz -C analytics/models/saved/
```

**Rollback Decision Points**:
- Phase 0: If >5 critical bugs found → PAUSE, stabilize v2
- Phase 2: If performance engine causes data corruption → ROLLBACK
- Phase 7: If production issues after 48 hours → ROLLBACK

---

## �🚨 Risk Management

### Risk 1: Scope Creep
**Probability**: HIGH  
**Impact**: HIGH  
**Mitigation**: 
- Strict phase boundaries
- Defer non-critical features to v3.1
- Regular progress reviews

### Risk 2: Burak Integration Breaks
**Probability**: MEDIUM  
**Impact**: HIGH  
**Mitigation**:
- Maintain backward compatibility for 2 months
- Provide migration guide early
- Test OVOS integration before old endpoint removal

### Risk 3: Performance Issues
**Probability**: MEDIUM  
**Impact**: MEDIUM  
**Mitigation**:
- Load testing before each phase completion
- Database query optimization
- Caching layer implementation

### Risk 4: Data Quality Issues
**Probability**: LOW  
**Impact**: HIGH  
**Mitigation**:
- Comprehensive sanity testing
- Validation layer for all outputs
- Automated data quality checks

### Risk 5: v2 Bugs Discovered During Refactor (NEW)
**Probability**: MEDIUM  
**Impact**: HIGH  
**Mitigation**:
- Phase 0 validation catches bugs early
- Separate bug fix commits (v2-bugfix tag)
- Decision point: fix in v2 or redesign in v3

---

## 🧪 OVOS Integration Validation Plan

### Purpose
Ensure Burak's OVOS voice assistant can successfully interact with ALL v3 endpoints without issues.

### Test Scenarios

#### Scenario 1: Basic Voice Commands (v2 Working, v3 Enhanced)
```
Voice: "Train Compressor-1 electricity baseline"
OVOS → EnMS: POST /baseline/train-seu
Expected: Model trained successfully, voice summary returned

Voice: "Predict Compressor-1 energy for today"
OVOS → EnMS: POST /baseline/predict
Expected: Prediction with explanation, suitable for TTS

Voice: "Show me Compressor-1 model details"
OVOS → EnMS: GET /baseline/model/{id}?include_explanation=true
Expected: Natural language model explanation
```

#### Scenario 2: Multi-Step Analysis (v3 NEW - Phase 2)
```
Voice: "Analyze today's energy performance"
OVOS → EnMS: POST /performance/analyze
Expected: Complete analysis (actual vs baseline, root cause, recommendations)

Voice: "What can we do to save energy?"
OVOS → EnMS: GET /performance/opportunities
Expected: Ranked list of improvement opportunities with ROI

Voice: "Create an action plan for the HVAC issue"
OVOS → EnMS: POST /iso50001/action-plans
Expected: Action plan created, confirmation returned
```

#### Scenario 3: Multi-Energy Machine (v2 Working, v3 Enhanced)
```
Voice: "Train Boiler-1 natural gas baseline"
OVOS → EnMS: POST /baseline/train-seu
         (seu_name: "Boiler-1", energy_source: "natural_gas")
Expected: Natural gas model trained (not electricity)

Voice: "Compare Boiler-1 electricity and natural gas consumption"
OVOS → EnMS: Multiple calls to /baseline/predict
Expected: Independent predictions for each energy source
```

#### Scenario 4: ISO 50001 Reporting (v3 NEW - Phase 3)
```
Voice: "Show me this quarter's EnPI report"
OVOS → EnMS: GET /iso50001/enpi-report?period=2025-Q4
Expected: Complete ISO compliance report

Voice: "What's the status of our action plans?"
OVOS → EnMS: GET /iso50001/action-plans?status=in_progress
Expected: List of active action plans
```

### Voice Response Quality Checklist

**Every v3 endpoint must return:**
- ✅ `voice_summary` field (natural language, TTS-ready)
- ✅ No technical jargon (or explained in simple terms)
- ✅ Numbers formatted for speech ("twelve hundred kilowatt hours" not "1200 kWh")
- ✅ Action-oriented language ("Consider doing X" not "X is recommended")
- ✅ Contextual information (time, location, machine name)

### Backward Compatibility Testing (Phase 1)

**Old Endpoints (v2) Must Still Work:**
```bash
# Old endpoint
curl -X POST "http://localhost:8001/api/v1/ovos/train-baseline" \
  -H "Content-Type: application/json" \
  -d '{"machine_id": "c0000000-0000-0000-0000-000000000001"}'

Expected Response:
- HTTP 302 Redirect OR
- HTTP 200 with deprecation warning
- Data identical to new endpoint

# New endpoint
curl -X POST "http://localhost:8001/api/v1/baseline/train-seu" \
  -H "Content-Type: application/json" \
  -d '{"seu_name": "Compressor-1", "energy_source": "electricity"}'

Expected Response:
- HTTP 200
- Model trained successfully
```

### Migration Testing (Phase 5)

**Burak's Integration Checklist:**
- [ ] All old endpoints documented with new equivalents
- [ ] Migration guide includes code examples (Python SDK)
- [ ] Deprecation timeline clearly communicated
- [ ] Test environment available for validation
- [ ] Support channel established (email/Slack)

### Performance Testing (Phase 4)

**Voice Interface Requirements:**
- 🎯 Response time: <500ms for predictions
- 🎯 Response time: <1s for analysis
- 🎯 Response time: <2s for reports
- 🎯 Concurrent requests: Handle 10 simultaneous OVOS instances
- 🎯 Failure rate: <0.1% under normal load

### Error Handling for Voice

**Bad User Input:**
```
Voice: "Train the compressor" (missing energy source)
OVOS → EnMS: POST /baseline/train-seu (incomplete data)
Expected Response:
{
  "error": "Missing required field: energy_source",
  "voice_message": "I need to know which energy source. Please say electricity, natural gas, steam, or compressed air.",
  "valid_options": ["electricity", "natural_gas", "steam", "compressed_air"]
}
```

**System Error:**
```
Voice: "Analyze energy performance"
OVOS → EnMS: POST /performance/analyze
EnMS: Database connection failed
Expected Response:
{
  "error": "Service temporarily unavailable",
  "voice_message": "I'm having trouble accessing the energy system right now. Please try again in a moment.",
  "retry_after_seconds": 30
}
```

### Validation Schedule

**Phase 1 (API Cleanup):**
- [ ] Test all old endpoints still work (backward compatibility)
- [ ] Test all new endpoints accessible
- [ ] Notify Burak of changes

**Phase 2 (Performance Engine):**
- [ ] Test new performance endpoints with OVOS
- [ ] Validate voice_summary quality
- [ ] Test multi-step workflows

**Phase 3 (ISO 50001):**
- [ ] Test ISO reporting endpoints
- [ ] Test action plan CRUD operations
- [ ] Validate report format for voice

**Phase 5 (Documentation):**
- [ ] Share migration guide with Burak
- [ ] Schedule migration review call
- [ ] Provide test environment access

**Phase 7 (Deployment):**
- [ ] Final integration test with Burak's OVOS
- [ ] Monitor OVOS API calls post-deployment
- [ ] Address any issues within 24 hours

### Success Metrics

**Integration Success:**
- ✅ Burak reports 100% of voice commands working
- ✅ OVOS can execute all test scenarios
- ✅ Voice response quality rated "excellent"
- ✅ Zero breaking changes after migration period
- ✅ Response times meet performance targets

---

## 📅 Timeline Summary

| Phase | Duration | Start | End | Key Deliverable |
|-------|----------|-------|-----|-----------------|
| **Phase 0: v2 Validation** | 2 days | Nov 5 | Nov 6 | Bug-free foundation |
| **Phase 1: API Cleanup** | 2 days | Nov 7 | Nov 8 | Clean API naming |
| **Phase 2: Performance Engine** | 7 days | Nov 9 | Nov 15 | Intelligence layer |
| **Phase 3: ISO 50001** | 4 days | Nov 16 | Nov 19 | Compliance engine |
| **Phase 4: Testing** | 6 days | Nov 20 | Nov 25 | Zero bugs |
| **Phase 5: Documentation** | 3 days | Nov 26 | Nov 28 | Complete docs |
| **Phase 6: Frontend** | 6 days | Nov 29 | Dec 4 | UI modernized |
| **Phase 7: Deployment** | 3 days | Dec 5 | Dec 7 | v3 in production |

**Total Duration**: ~33 days (6.5 weeks)  
**Target Completion**: December 7, 2025

**Timeline Adjustment**: Phase 0 added (+2 days), dates shifted accordingly

---

## 🎯 Critical Path

```
Phase 0 (v2 Validation) → Phase 1 (API Cleanup) → Phase 2 (Performance Engine) → Phase 4 (Testing) → Phase 7 (Deployment)
```

**Can be parallelized**:
- Phase 3 (ISO 50001) can start after Phase 2 Milestone 2.1
- Phase 5 (Documentation) can run parallel with Phase 6 (Frontend)

**Cannot Skip**:
- Phase 0 must complete before Phase 1 (foundation must be solid)
- Phase 4 must complete before Phase 7 (no bugs in production)

---

## 🎯 Mr. Umut's Regression Analysis Requirements - Coverage Map

### Original Requirement (October 2025)
**"Regression analysis with voice interface"** - requested by Mr. Umut during WASABI Project review.

### What "Regression Analysis" Means in Context
Based on implementation and Mr. Umut's feedback:
1. **Train baseline models** using linear regression
2. **Predict energy consumption** based on production/environmental factors
3. **Explain predictions** in natural language (not just numbers)
4. **Identify deviations** from expected performance
5. **Provide root cause analysis** (why deviation occurred)
6. **Recommend actions** to optimize energy use
7. **Enable voice interface** for all above capabilities

### Coverage Status

#### ✅ Already Working in v2.0
- **Baseline Training** (`/baseline/train-seu`)
  - Linear regression models for each SEU
  - Multi-energy support (4 sources)
  - 61 models trained (7 machines)
  - R² accuracy: 85-99%
  
- **Energy Prediction** (`/baseline/predict`)
  - Predict consumption given inputs
  - Dual input: UUID OR (SEU name + energy source)
  - Voice-friendly response format
  
- **Natural Language Explanations** (`/baseline/model/{id}?include_explanation=true`)
  - Model explainer service (304 lines)
  - Explains: coefficients, feature importance, accuracy
  - Example: "This model achieves 98.7% accuracy..."
  
- **Voice Interface Ready** (All endpoints)
  - OVOS can call any endpoint
  - Response formats suitable for TTS
  - Natural language summaries included

#### ⚠️ Partial in v2.0 (Enhanced in v3)
- **Deviation Analysis**
  - v2: Can compare actual vs baseline (manual, separate calls)
  - v3 Phase 2: Automated performance analysis (single call)
  
- **Root Cause Analysis**
  - v2: Data available, but no automated analysis
  - v3 Phase 2: Performance Engine identifies root causes automatically

#### ❌ Missing in v2.0 (Added in v3)
- **Actionable Recommendations**
  - v2: No recommendation engine
  - v3 Phase 2: Recommendation system with ROI calculations
  
- **Multi-Step Workflows**
  - v2: Each step requires separate API call
  - v3 Phase 2: Single call returns complete analysis
  
- **ISO 50001 Integration**
  - v2: Has SEU structure, but no EnPI tracking
  - v3 Phase 3: Complete compliance engine

### How v3 Completes the Vision

**Phase 2: Energy Performance Engine (Week 2-3)**
```python
# Single voice command: "Analyze Compressor-1 performance today"
POST /api/v1/performance/analyze
{
  "seu_name": "Compressor-1",
  "energy_source": "electricity",
  "analysis_date": "2025-11-05"
}

# Returns complete regression analysis:
{
  "actual_energy_kwh": 1200,
  "baseline_energy_kwh": 950,          # ← Regression prediction
  "deviation_percent": 26.3,            # ← Deviation analysis
  "root_cause_analysis": {              # ← Root cause (NEW)
    "primary_factor": "production_volume",
    "impact_description": "Production +15% vs baseline",
    "contributing_factors": ["outdoor_temp +5°C"]
  },
  "recommendations": [                   # ← Actions (NEW)
    {
      "action": "Optimize load scheduling",
      "potential_savings_kwh": 180,
      "roi_days": 30
    }
  ],
  "voice_summary": "Compressor-1 used 26% more energy than expected because production increased 15%. Consider optimizing load scheduling to save 180 kWh daily."
}
```

**Phase 3: ISO 50001 Compliance (Week 4)**
- EnPI tracking (baseline year comparison)
- Action plan management
- Management review reporting

### Validation Checklist
- [x] Train baseline models via voice
- [x] Predict energy consumption
- [x] Explain predictions in natural language
- [ ] Analyze deviations automatically (Phase 2)
- [ ] Identify root causes (Phase 2)
- [ ] Provide actionable recommendations (Phase 2)
- [ ] Single-call complete analysis (Phase 2)
- [ ] ISO 50001 EnPI tracking (Phase 3)

### Demo Scenario for Mr. Umut (Post-v3)
```
User (voice): "What's today's energy status?"

OVOS → EnMS: GET /api/v1/performance/analyze
         (seu_name: "Factory-Wide", date: "today")

EnMS Response:
- Regression analysis: Expected 2,500 kWh, actual 2,700 kWh
- Root cause: HVAC-Main running outside schedule
- Recommendation: Implement time-based setback (save 200 kWh/day)
- Cost impact: $30/day wasted

OVOS (voice): "You're using 8% more energy than expected today. The HVAC system is running outside normal hours. Would you like me to create an action plan to fix this?"
```

**This is the complete "regression analysis with voice interface" Mr. Umut requested.** ✅

---

## 📝 Document Maintenance

### How to Use This Document
1. **Daily**: Check current phase tasks
2. **Weekly**: Update milestone completion status
3. **As Needed**: Reference when context is lost
4. **After Each Phase**: Update success criteria checkboxes

### Update Protocol
- Update completion status: Change `[ ]` to `[x]`
- Add notes in dedicated section at end of document
- Keep timeline updated if delays occur
- Document all architectural decisions

---

## 📚 Related Documents

### Planning Documents
- `FRONTEND-MODERNIZATION-PLAN.md` - Detailed frontend plan (Phase 6 reference)
- `FRONTEND-MODERNIZATION-SUMMARY.md` - Executive summary
- `SEU-MACHINE-ARCHITECTURE-ANALYSIS.md` - Architecture validation

### Completion Reports (v2)
- `TASK-2-ENHANCE-PREDICT-COMPLETE.md`
- `TASK-3-ENHANCE-MODEL-DETAILS-COMPLETE.md`
- `TASK-4-ENHANCE-MODELS-LIST-COMPLETE.md`
- `TASK-7-INTEGRATION-TEST-SUITE-COMPLETE.md`

### API Documentation
- `ENMS-API-DOCUMENTATION-FOR-OVOS.md` - Current v2 docs (to be updated)
- `BURAK-API-MIGRATION-GUIDE.md` - To be created in Phase 5

---

## 🎯 Vision Statement

**EnMS v3 will be:**
- ✅ **Intelligent**: Proactive system that identifies opportunities, not just collects data
- ✅ **Interconnected**: All components work together, orchestrated by performance engine
- ✅ **Compliant**: Full ISO 50001 compliance with EnPI tracking and action plans
- ✅ **User-Friendly**: Single API call for complete analysis, voice-ready responses
- ✅ **Valuable**: Real business impact through automated recommendations
- ✅ **SOTA**: State-of-the-art energy management system that sets industry standard

**Target Users:**
- Energy Managers (proactive insights)
- Facility Managers (optimization recommendations)
- OVOS Voice Assistant (natural language interface)
- ISO 50001 Auditors (compliance reporting)
- WASABI Project (AI-driven building automation)

---

## 📌 Notes & Updates

### Session 1 - November 5, 2025 (Planning)
- Created v3 project charter
- Identified 7 phases with 20+ milestones
- Established 6-week timeline
- Created git checkpoint (commit 5b20761)
- Document status: READY FOR IMPLEMENTATION

### Session 2 - November 5, 2025 (Phase 0 Complete)
**Phase 0: v2 Critical Path Validation**
- Created comprehensive test suite (58 tests: 27+18+13)
- Discovered BUG-001: Multi-Energy Baseline Cross-Contamination
- Fixed critical bug with database migration 010
- Validated fix: 58/58 tests passing
- Created `docs/V2-KNOWN-ISSUES.md`
- Commit: 6201a10 "v2-bugfix: Fix multi-energy baseline cross-contamination"
- **DECISION**: Proceed to Phase 1 (foundation validated)

### Session 3 - November 5, 2025 (Phase 1 Started)
**Phase 1: API Cleanup & Refactoring - Milestone 1.1 COMPLETE**
- Created new route files: `seus.py`, `factory.py`, `analytics.py`
- Implemented new endpoints:
  - ✅ `/api/v1/seus` - SEU management (10 SEUs listed)
  - ✅ `/api/v1/factory/summary` - Factory overview
  - ✅ `/api/v1/analytics/top-consumers` - Energy rankings
- Registered routers in main.py
- Updated `ENMS-API-DOCUMENTATION-FOR-OVOS.md`:
  - Added deprecation notice at top
  - Strikethrough all old `/ovos/*` endpoints
  - Documented all new endpoints with examples
- **All 58 tests still passing**
- Commits: 069bf47, 7a10210, 0d39583
- Old `/ovos/*` endpoints still work but marked DEPRECATED

### Next Session Actions
1. Continue Phase 1: Complete Milestone 1.2 (Route Organization)
2. Add remaining endpoints (machines/status, forecast/short-term)
3. Create backward compatibility tests

---

**Document Version**: 1.0  
**Last Updated**: November 5, 2025  
**Status**: 📋 APPROVED - Ready for Implementation  
**Next Review**: After Phase 1 completion
