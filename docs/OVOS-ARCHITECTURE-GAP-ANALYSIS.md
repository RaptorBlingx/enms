# OVOS Skill Architecture - Gap Analysis

**Date:** December 17, 2025  
**Status:** 🔴 **MASSIVE GAPS IDENTIFIED**

---

## 📊 Current State vs Required State

### Current Intent Files (3 files)
```
enms_ovos_skill/intent/
├── machine.status.intent
├── energy.query.intent
└── factory.overview.intent
```

### Current Entity Files (2 files)
```
enms_ovos_skill/entities/
├── machine.entity
└── energy_source.entity
```

### Current IntentType Enum (20 types)
```python
ENERGY_QUERY = "energy_query"
POWER_QUERY = "power_query"
MACHINE_STATUS = "machine_status"
FACTORY_OVERVIEW = "factory_overview"
COMPARISON = "comparison"
RANKING = "ranking"
ANOMALY_DETECTION = "anomaly_detection"
COST_ANALYSIS = "cost_analysis"
FORECAST = "forecast"
BASELINE = "baseline"
BASELINE_MODELS = "baseline_models"
BASELINE_EXPLANATION = "baseline_explanation"
SEUS = "seus"
KPI = "kpi"
PERFORMANCE = "performance"
PRODUCTION = "production"
REPORT = "report"
HELP = "help"
UNKNOWN = "unknown"
```

### API Endpoints (60+ documented)

From `ENMS-API-DOCUMENTATION-FOR-OVOS.md`:

1. **System (2 endpoints)**
   - GET /api/v1/health
   - GET /api/v1/stats/system

2. **Machines (5 endpoints)**
   - GET /api/v1/machines
   - GET /api/v1/machines/{id}
   - GET /api/v1/machines/status/{name}
   - GET /api/v1/machines/{id}/energy-types
   - GET /api/v1/machines/{id}/status-history

3. **Time-Series Data (5 endpoints)**
   - GET /api/v1/timeseries/energy
   - GET /api/v1/timeseries/power
   - GET /api/v1/timeseries/latest/{machine_id}
   - GET /api/v1/timeseries/multi-machine/energy
   - GET /api/v1/stats/aggregated

4. **Anomaly Detection (4 endpoints)**
   - POST /api/v1/anomaly/detect
   - GET /api/v1/anomaly/recent
   - GET /api/v1/anomaly/active
   - GET /api/v1/anomaly/search

5. **Baseline Models (4 endpoints)**
   - GET /api/v1/baseline/models
   - POST /api/v1/baseline/predict
   - GET /api/v1/baseline/model/{id}
   - POST /api/v1/baseline/train-seu

6. **KPIs (4 endpoints)**
   - GET /api/v1/kpi/all
   - GET /api/v1/kpi/factory/{id}
   - GET /api/v1/kpi/factories
   - GET /api/v1/kpi/energy-cost

7. **Forecasting (3 endpoints)**
   - GET /api/v1/forecast/demand
   - GET /api/v1/forecast/short-term
   - GET /api/v1/ovos/forecast/tomorrow

8. **Performance (4 endpoints)**
   - POST /api/v1/performance/analyze
   - GET /api/v1/performance/health
   - GET /api/v1/performance/opportunities
   - POST /api/v1/performance/action-plan

9. **SEUs (1 endpoint)**
   - GET /api/v1/seus

10. **Factory Summary (2 endpoints)**
    - GET /api/v1/factory/summary
    - GET /api/v1/analytics/top-consumers

11. **Production (1 endpoint)**
    - GET /api/v1/production/{machine_id}

12. **Multi-Energy (2 endpoints)**
    - GET /api/v1/machines/{id}/energy/{type}
    - GET /api/v1/machines/{id}/energy-summary

13. **ISO 50001 Compliance (4 endpoints)**
    - GET /api/v1/iso50001/enpi-report
    - POST /api/v1/iso50001/action-plans
    - GET /api/v1/iso50001/action-plans
    - PUT /api/v1/iso50001/action-plans/{id}/progress

14. **Reports (3 endpoints)**
    - GET /api/v1/reports/types
    - POST /api/v1/reports/generate
    - GET /api/v1/reports/preview

15. **OVOS-specific (3 endpoints - DEPRECATED)**
    - GET /api/v1/ovos/summary
    - GET /api/v1/ovos/top-consumers
    - GET /api/v1/ovos/machines/{name}/status

---

## 🔴 The Problem

### Mismatch Analysis

| Component | Expected | Actual | Gap |
|-----------|----------|--------|-----|
| **Intent files** | 20 (one per IntentType) | 3 | **17 missing** |
| **Entity files** | 10+ | 2 | **8+ missing** |
| **API coverage** | 60+ endpoints | ~15 used | **45+ unused** |
| **Heuristic patterns** | 20 intent types | ~10 patterns | **10+ incomplete** |

---

## 🤔 Two Possible Architectures

### Option A: Full Adapt Intent Files (Traditional OVOS)

**What it means:**
- Create 20 `.intent` files (one per IntentType)
- Create 10+ `.entity` files (machines, metrics, time, energy sources, etc.)
- Use Adapt parser for pattern matching
- Minimal heuristic routing
- LLM as fallback only

**Pros:**
- ✅ Standard OVOS architecture
- ✅ Easy to maintain/debug
- ✅ Community-recognized pattern
- ✅ Fast (Adapt is <10ms)

**Cons:**
- ❌ **TONS of files to create** (30+ files)
- ❌ Need to maintain pattern lists
- ❌ Less flexible for complex queries
- ❌ Harder to handle natural variations

**Example Intent File Structure:**
```
enms_ovos_skill/intent/
├── anomaly.detection.intent
├── anomaly.active.intent
├── baseline.models.intent
├── baseline.predict.intent
├── baseline.train.intent
├── comparison.machines.intent
├── cost.analysis.intent
├── energy.query.intent
├── factory.overview.intent
├── forecast.demand.intent
├── forecast.tomorrow.intent
├── kpi.all.intent
├── kpi.machine.intent
├── machine.status.intent
├── performance.analyze.intent
├── performance.opportunities.intent
├── power.query.intent
├── production.metrics.intent
├── ranking.top.intent
├── report.generate.intent
└── seus.list.intent
```

**Example Entity Files:**
```
enms_ovos_skill/entities/
├── machine.entity
├── energy_source.entity
├── metric.entity           # NEW: energy, power, cost, efficiency
├── time_range.entity        # NEW: today, yesterday, last week
├── aggregation.entity       # NEW: sum, avg, max, min
├── ranking_metric.entity    # NEW: efficiency, cost, alerts
├── severity.entity          # NEW: critical, warning, info
├── report_type.entity       # NEW: monthly, quarterly, ISO
├── kpi_type.entity          # NEW: SEC, load_factor, carbon
└── comparison_operator.entity # NEW: vs, compared to, versus
```

---

### Option B: Hybrid Approach (Current Implementation)

**What it means:**
- Minimal `.intent` files (3 basic ones)
- Minimal `.entity` files (2 core ones)
- **Heavy heuristic routing** (regex patterns)
- Adapt for simple cases
- **LLM for complex queries**

**Pros:**
- ✅ Fewer files to maintain
- ✅ More flexible (handles variations)
- ✅ LLM can understand context
- ✅ Faster to develop initially

**Cons:**
- ❌ **Complex heuristic code** (1000+ lines)
- ❌ **Harder to debug** (logic in Python, not files)
- ❌ **LLM is slow** (300-500ms)
- ❌ **Not standard OVOS pattern**
- ❌ **Currently has timeouts** (our issue!)

**Current Code Structure:**
```python
# lib/heuristic_router.py (800+ lines)
PATTERNS = {
    'production': [regex1, regex2, ...],
    'anomaly_detection': [regex1, regex2, ...],
    'baseline_models': [regex1, regex2, ...],
    # ... 20+ intent types
}

# lib/intent_parser.py (1000+ lines)  
class HybridParser:
    def parse(self, utterance):
        # Try heuristic first
        # Fall back to Adapt
        # Fall back to LLM
```

---

## 💭 My Recommendation

### **Option C: Hybrid++** (Best of Both Worlds)

**Combine the best aspects:**

1. **Core intents via Adapt files** (10-12 files for common queries)
   - machine.status.intent
   - energy.query.intent
   - factory.overview.intent
   - anomaly.recent.intent
   - forecast.tomorrow.intent
   - kpi.machine.intent
   - baseline.predict.intent
   - seus.list.intent
   - top.consumers.intent
   - production.metrics.intent

2. **Heuristic for variations** (handles "show me X" vs "what's X" vs "X?")

3. **LLM for complex/ambiguous** (only when needed)

4. **Proper entity files** (8-10 files)
   - machine.entity
   - energy_source.entity
   - metric.entity
   - time_range.entity
   - severity.entity
   - kpi_type.entity
   - report_type.entity
   - comparison_operator.entity

### Why This Works

- ✅ **Fast path**: Adapt catches 60-70% of queries (<10ms)
- ✅ **Flexible**: Heuristic handles variations
- ✅ **Accurate**: LLM for complex cases
- ✅ **Maintainable**: Intent files for common patterns
- ✅ **Debuggable**: Clear routing logic

---

## 🛠️ Implementation Plan

### Phase 1: Fix Timeouts (URGENT - 2-4 hours)

**Don't add files yet!** Fix the current timeout issues first:
1. Add debug logging to handlers
2. Find where 30+ second delay occurs
3. Fix blocking operations
4. Verify queries work

### Phase 2: Add Core Intent Files (4-6 hours)

Create 10 essential `.intent` files:

**anomaly.recent.intent:**
```
show me (recent|latest) anomalies
any anomalies (today|yesterday)
list (active|critical) (anomalies|alerts)
what (anomalies|issues) do we have
check for anomalies
```

**kpi.machine.intent:**
```
show me kpis for {machine}
what are {machine} kpis
{machine} performance metrics
kpi report for {machine}
```

**forecast.tomorrow.intent:**
```
forecast for tomorrow
what's tomorrow's (energy|demand)
predict tomorrow's consumption
energy forecast next day
```

**baseline.predict.intent:**
```
what's the expected energy for {machine}
predicted (energy|consumption) for {machine}
baseline prediction {machine}
how much should {machine} consume
```

### Phase 3: Add Entity Files (2-3 hours)

**metric.entity:**
```
energy
power
cost
efficiency
consumption
demand
```

**time_range.entity:**
```
today
yesterday
last week
last month
this week
this month
last 24 hours
last 7 days
```

**severity.entity:**
```
critical
warning
info
high
medium
low
```

**kpi_type.entity:**
```
SEC
specific energy consumption
load factor
peak demand
energy cost
carbon intensity
```

### Phase 4: Update Heuristic Router (2-3 hours)

Simplify patterns - let Adapt do the heavy lifting:

```python
# Only handle edge cases in heuristic:
- Natural variations ("gimme", "show", "tell me")
- Abbreviations ("comp 1" → "Compressor-1")
- Typos/partial matches
- Context-dependent queries
```

### Phase 5: Comprehensive Testing (6-8 hours)

Test all 60+ API endpoints:
1. Create test dataset (100+ queries)
2. Measure intent accuracy
3. Measure response latency
4. Fix failures
5. Document coverage

---

## 📊 Coverage Gap Summary

### Currently Covered (15%)
- ✅ Machine status queries
- ✅ Energy/power queries
- ✅ Factory overview
- (Works but slow/buggy)

### Partially Covered (30%)
- ⚠️ Anomaly detection (timeout issues)
- ⚠️ KPI queries (timeout issues)
- ⚠️ Forecasting (wrong routing)
- ⚠️ Baseline predictions (exists but untested)

### Not Covered (55%)
- ❌ SEU management
- ❌ Performance analysis
- ❌ Production metrics
- ❌ Multi-energy queries
- ❌ ISO 50001 compliance
- ❌ Report generation
- ❌ Cost analysis
- ❌ Comparison queries
- ❌ Action plans
- ❌ Opportunities identification
- ❌ Multi-machine aggregation

---

## 🎯 Decision Time

**Question for you:** Which approach do you prefer?

### Option A: Full Adapt (20+ intent files, traditional)
- More files, but standard OVOS pattern
- Estimated: 2-3 days of work

### Option B: Keep Hybrid (current approach)
- Fix timeouts, improve heuristics
- Estimated: 1-2 days of work

### Option C: Hybrid++ (my recommendation)
- 10 core intent files + smart heuristics
- Estimated: 1.5-2 days of work

**My vote: Option C** - Best balance of maintainability and flexibility.

---

## 🚦 Next Steps (Your Choice)

1. **Fix timeouts first** (everyone agrees on this - 2-4 hours)
2. **Then decide architecture:**
   - A: Create all 20 intent files
   - B: Improve heuristics only
   - C: Create 10 core + improve heuristics

**What do you think?**
