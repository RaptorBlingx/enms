# ISO 50001 EnPI Implementation Guide

**Last Updated:** October 22, 2025  
**Status:** Requirements Defined - Implementation Pending

---

## Executive Summary

EnMS currently has **real-time ML prediction** for monitoring. Mr. Umut requires **annual baseline regression for ISO 50001 compliance reporting**. Both systems coexist with different purposes.

---

## Two Parallel Systems

### System 1: Real-Time Monitoring (EXISTS ✅)
- **Purpose:** Anomaly detection, live dashboards
- **Frequency:** Predictions every 1 minute
- **Scope:** Last 7 days rolling window
- **Training:** Auto-retrain weekly via scheduler
- **Audience:** Operators, maintenance teams
- **Status:** Working (R²=0.97, 15,000x query optimization)

### System 2: ISO 50001 EnPI Reporting (REQUIRED ⚠️)
- **Purpose:** Annual energy performance vs baseline
- **Frequency:** Quarterly/annual reports
- **Scope:** Full year comparison (e.g., 2024 baseline vs 2025 actual)
- **Training:** Manual trigger, once per baseline year
- **Audience:** Management, ISO auditors
- **Status:** NOT IMPLEMENTED

---

## ISO 50001 Workflow

```
┌─────────────────────────────────────────────┐
│ Year 2024: Establish Baseline              │
│ - Train regression on full year data       │
│ - Formula: Power = β0 + β1*prod + β2*temp  │
│ - Store coefficients in seus table         │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Year 2025: Compare Performance             │
│ - Apply 2024 formula to 2025 conditions    │
│ - Expected = Formula(2025_production, temp)│
│ - Actual = 2025 real consumption           │
│ - Deviation % = (Actual - Expected) / Expected │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Generate Report (Quarterly/Annual)         │
│ - Q1, Q2, Q3, Q4 deviation breakdown       │
│ - EnPI trend chart                         │
│ - Compliance: Green (±3%), Red (>5%)       │
└─────────────────────────────────────────────┘
```

---

## Database Schema Changes

### New Tables

```sql
-- Energy sources (electricity, gas, compressed air, steam)
CREATE TABLE energy_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) UNIQUE NOT NULL,
    unit VARCHAR(20) NOT NULL,
    cost_per_unit DECIMAL(10,4),
    carbon_factor DECIMAL(10,6),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- SEUs (Significant Energy Users) - ISO 50001 requirement
CREATE TABLE seus (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    energy_source_id UUID REFERENCES energy_sources(id) NOT NULL,
    machine_ids UUID[] NOT NULL,
    baseline_year INTEGER,
    baseline_start_date DATE,
    baseline_end_date DATE,
    regression_coefficients JSONB,
    feature_columns TEXT[],
    r_squared DECIMAL(6,4),
    rmse DECIMAL(15,4),
    trained_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- EnPI performance tracking
CREATE TABLE seu_energy_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    seu_id UUID REFERENCES seus(id) NOT NULL,
    report_period VARCHAR(20) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    baseline_year INTEGER NOT NULL,
    actual_consumption DECIMAL(15,4) NOT NULL,
    expected_consumption DECIMAL(15,4) NOT NULL,
    deviation_kwh DECIMAL(15,4),
    deviation_percent DECIMAL(6,2),
    compliance_status VARCHAR(20),
    notes TEXT,
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(seu_id, report_period)
);

CREATE INDEX idx_seu_performance_period ON seu_energy_performance(seu_id, period_start, period_end);
CREATE INDEX idx_seu_energy_source ON seus(energy_source_id);
```

### Seed Data

```sql
INSERT INTO energy_sources (name, unit, cost_per_unit, carbon_factor) VALUES
    ('electricity', 'kWh', 0.15, 0.45),
    ('natural_gas', 'm³', 0.50, 2.03),
    ('compressed_air', 'Nm³', 0.03, 0.12),
    ('steam', 'kg', 0.08, 0.35);

-- Example SEU: Compressor Group
INSERT INTO seus (name, energy_source_id, machine_ids, description) VALUES
    ('Compressor Group', 
     (SELECT id FROM energy_sources WHERE name='electricity'),
     ARRAY[
         'c0000000-0000-0000-0000-000000000001'::uuid,
         'c0000000-0000-0000-0000-000000000006'::uuid
     ],
     'All industrial compressors');
```

---

## API Endpoints (New)

### Baseline Training

```http
POST /api/v1/baseline/seu/train
Content-Type: application/json

{
    "seu_id": "uuid",
    "baseline_year": 2024,
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "features": ["production_count", "avg_temp_c", "operating_hours"]
}

Response 200:
{
    "success": true,
    "seu_id": "uuid",
    "r_squared": 0.94,
    "rmse": 2.34,
    "coefficients": {
        "intercept": 45.2,
        "production_count": 0.00003,
        "avg_temp_c": 0.5,
        "operating_hours": 1.2
    },
    "formula": "Power = 45.2 + 0.00003*production + 0.5*temp + 1.2*hours"
}
```

### Generate Performance Report

```http
POST /api/v1/reports/seu-performance
Content-Type: application/json

{
    "seu_id": "uuid",
    "report_year": 2025,
    "baseline_year": 2024,
    "period": "Q1"  // or "annual"
}

Response 200:
{
    "success": true,
    "report": {
        "seu_name": "Compressor Group",
        "period": "2025-Q1",
        "actual_consumption": 12450.5,
        "expected_consumption": 11800.0,
        "deviation_kwh": 650.5,
        "deviation_percent": 5.51,
        "compliance_status": "warning",
        "breakdown": {
            "jan": {"actual": 4100, "expected": 3900, "deviation": 5.13},
            "feb": {"actual": 4050, "expected": 3950, "deviation": 2.53},
            "mar": {"actual": 4300, "expected": 3950, "deviation": 8.86}
        }
    }
}
```

### Get EnPI Trend

```http
GET /api/v1/analytics/enpi?seu_id={uuid}&start_year=2023&end_year=2025

Response 200:
{
    "success": true,
    "data": [
        {"year": 2023, "quarter": "Q1", "enpi": 100, "deviation_percent": 0},
        {"year": 2023, "quarter": "Q2", "enpi": 102, "deviation_percent": 2.0},
        {"year": 2024, "quarter": "Q1", "enpi": 100, "deviation_percent": 0},
        {"year": 2025, "quarter": "Q1", "enpi": 105, "deviation_percent": 5.5}
    ]
}
```

### List SEUs

```http
GET /api/v1/seus?energy_source=electricity&is_active=true

Response 200:
{
    "success": true,
    "data": [
        {
            "id": "uuid",
            "name": "Compressor Group",
            "energy_source": "electricity",
            "machine_count": 2,
            "baseline_year": 2024,
            "has_baseline": true,
            "last_report": "2025-Q3"
        }
    ]
}
```

---

## Analytics Service Changes

### New File Structure

```
analytics/
├── services/
│   ├── baseline_service.py          # Existing (real-time)
│   ├── seu_baseline_service.py      # NEW - ISO 50001 baselines
│   └── enpi_calculator.py           # NEW - Performance reports
├── api/routes/
│   ├── baseline.py                  # Existing
│   └── seu.py                       # NEW - SEU management & EnPI
└── models/
    └── seu.py                       # NEW - Pydantic models
```

### seu_baseline_service.py (Pseudo-code)

```python
class SEUBaselineService:
    async def train_baseline(self, seu_id, year, start_date, end_date, features):
        # 1. Get all machines in SEU
        machines = await get_seu_machines(seu_id)
        
        # 2. Aggregate energy data for full year
        query = """
            SELECT 
                time_bucket('1 day', time) as day,
                SUM(energy_kwh) as total_energy,
                AVG(production_count) as avg_production,
                AVG(machine_temp_c) as avg_temp
            FROM energy_readings er
            JOIN production_data pd USING (time, machine_id)
            WHERE machine_id = ANY($1)
              AND time BETWEEN $2 AND $3
            GROUP BY day
            ORDER BY day
        """
        
        # 3. Train linear regression (sklearn)
        X = df[features]
        y = df['total_energy']
        model = LinearRegression().fit(X, y)
        
        # 4. Store coefficients
        await store_baseline(seu_id, year, model.coef_, model.intercept_)
        
        return {"r_squared": model.score(X, y), "coefficients": model.coef_}
    
    async def calculate_expected(self, seu_id, period_start, period_end):
        # 1. Load baseline formula
        baseline = await get_seu_baseline(seu_id)
        
        # 2. Get actual conditions for comparison period
        conditions = await get_period_conditions(seu_id, period_start, period_end)
        
        # 3. Apply formula: expected = β0 + β1*x1 + β2*x2 + ...
        expected = baseline['intercept']
        for i, coef in enumerate(baseline['coefficients']):
            expected += coef * conditions[baseline['features'][i]]
        
        return expected
```

---

## Grafana Dashboard: ISO 50001 EnPI Report

**File:** `grafana/dashboards/iso-50001-enpi-report.json`

### Panel Layout

```
┌─────────────────────────────────────────────────────────┐
│ Row 1: SEU Selection                                    │
├─────────────────────────────────────────────────────────┤
│ [Dropdown: Select SEU] [Dropdown: Energy Source]       │
└─────────────────────────────────────────────────────────┘

┌──────────────────────┬──────────────────────────────────┐
│ Baseline vs Actual   │  Compliance Status               │
│ (Bar Chart)          │  (Stat Panel)                    │
│                      │  ✅ Within Target ±3%            │
│  2024: 100,000 kWh  │  Current: +5.5%                  │
│  2025: 105,500 kWh  │  ⚠️ Warning                      │
└──────────────────────┴──────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Quarterly Deviation Analysis (Table)                    │
├──────────┬─────────┬──────────┬──────────┬─────────────┤
│ Quarter  │ Actual  │ Expected │ Deviation│ Status      │
├──────────┼─────────┼──────────┼──────────┼─────────────┤
│ 2025-Q1  │ 26,250  │ 25,000   │ +5.0%    │ ⚠️ Warning │
│ 2025-Q2  │ 26,800  │ 25,500   │ +5.1%    │ ⚠️ Warning │
│ 2025-Q3  │ 27,100  │ 25,200   │ +7.5%    │ 🔴 Critical│
│ 2025-Q4  │ 25,350  │ 24,300   │ +4.3%    │ ⚠️ Warning │
└──────────┴─────────┴──────────┴──────────┴─────────────┘

┌─────────────────────────────────────────────────────────┐
│ EnPI Trend (Line Chart - 3 years)                       │
│                                                          │
│  110 ┤                                    ╭──●          │
│  105 ┤                          ╭──●──●──╯             │
│  100 ┤ ●──●──●──●──●──●──●──●──╯                      │
│   95 ┤                                                   │
│      └─────────────────────────────────────────         │
│       2023-Q1      2024-Q1      2025-Q1                 │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Regression Formula (Text Panel)                         │
│                                                          │
│  Expected Power (kW) = 45.2 + 0.00003×Production       │
│                             + 0.5×Temperature           │
│                             + 1.2×Operating Hours       │
│                                                          │
│  Model Performance: R² = 0.94, RMSE = 2.34 kW          │
│  Baseline Period: 2024-01-01 to 2024-12-31             │
└─────────────────────────────────────────────────────────┘
```

### Key Queries

**Quarterly Deviation Table:**
```sql
SELECT 
    report_period,
    actual_consumption,
    expected_consumption,
    deviation_percent,
    compliance_status
FROM seu_energy_performance
WHERE seu_id = '$seu_id'
  AND period_start >= date_trunc('year', NOW())
ORDER BY period_start;
```

**EnPI Trend (3 years):**
```sql
WITH baseline AS (
    SELECT AVG(actual_consumption) as baseline_avg
    FROM seu_energy_performance
    WHERE seu_id = '$seu_id' AND baseline_year = baseline_year
)
SELECT 
    report_period,
    (actual_consumption / baseline_avg * 100) as enpi_index
FROM seu_energy_performance, baseline
WHERE seu_id = '$seu_id'
  AND period_start >= NOW() - INTERVAL '3 years'
ORDER BY period_start;
```

---

## Variables

```json
{
  "templating": {
    "list": [
      {
        "name": "seu_id",
        "label": "SEU",
        "type": "query",
        "query": "SELECT id as __value, name as __text FROM seus WHERE is_active=true",
        "current": {"value": "", "text": "All SEUs"}
      },
      {
        "name": "energy_source",
        "label": "Energy Source",
        "type": "query",
        "query": "SELECT name FROM energy_sources",
        "current": {"value": "electricity", "text": "Electricity"}
      },
      {
        "name": "baseline_year",
        "label": "Baseline Year",
        "type": "custom",
        "options": "2023,2024,2025",
        "current": {"value": "2024", "text": "2024"}
      }
    ]
  }
}
```

---

## Implementation Checklist

### Phase 1: Database (2 hours)
- [ ] Create migration script `database/migrations/003-iso50001-schema.sql`
- [ ] Add `energy_sources`, `seus`, `seu_energy_performance` tables
- [ ] Seed initial energy sources
- [ ] Test: Create sample SEU with 2 machines

### Phase 2: Analytics API (4 hours)
- [ ] Create `analytics/models/seu.py` (Pydantic models)
- [ ] Create `analytics/services/seu_baseline_service.py`
- [ ] Create `analytics/services/enpi_calculator.py`
- [ ] Create `analytics/api/routes/seu.py`
- [ ] Add routes: `/seu/train`, `/reports/seu-performance`, `/analytics/enpi`
- [ ] Test: Train baseline on 2024 data, calculate 2025 deviation

### Phase 3: Grafana Dashboard (3 hours)
- [ ] Create `grafana/dashboards/iso-50001-enpi-report.json`
- [ ] Add 6 panels: SEU selector, baseline vs actual, compliance, table, trend, formula
- [ ] Configure variables: `$seu_id`, `$energy_source`, `$baseline_year`
- [ ] Test: View dashboard with sample SEU, verify queries work

### Phase 4: Integration (2 hours)
- [ ] Add SEU management UI (optional: simple HTML form or API-only)
- [ ] Test end-to-end: Create SEU → Train baseline → Generate Q1 report → View dashboard
- [ ] Documentation: Update README with ISO 50001 workflow

### Phase 5: Testing (2 hours)
- [ ] Test with 365 days of 2024 data (check simulator has enough history)
- [ ] Verify regression R² > 0.85 for all SEUs
- [ ] Test quarterly vs annual reports
- [ ] Verify compliance status colors (green/yellow/red)

---

## Key Differences: Real-Time vs ISO 50001

| Aspect | Real-Time Monitoring | ISO 50001 Baseline |
|--------|---------------------|-------------------|
| **Table** | `energy_baselines` | `seus` |
| **Scope** | Per machine, last 90 days | Per SEU, full year |
| **Training** | Auto weekly (scheduler) | Manual, once per baseline year |
| **Prediction** | Next minute | Full comparison year |
| **Storage** | Materialized view (7 days) | `seu_energy_performance` (permanent) |
| **API** | `/baseline/train`, `/baseline/predict` | `/seu/train`, `/reports/seu-performance` |
| **Dashboard** | "Machine Monitoring" | "ISO 50001 EnPI Report" |
| **Audience** | Operators | Auditors, Management |

---

## Compliance Thresholds

```python
def get_compliance_status(deviation_percent: float) -> str:
    abs_dev = abs(deviation_percent)
    if abs_dev <= 3.0:
        return "compliant"      # Green ✅
    elif abs_dev <= 5.0:
        return "warning"        # Yellow ⚠️
    else:
        return "critical"       # Red 🔴
```

---

## Data Requirements

### Minimum Data for Baseline
- **365 days** of continuous data (allow 10% gaps max)
- **Features required:** production_count, temperature, operating hours
- **Target variable:** energy_kwh (aggregated daily)

### Feature Selection Strategy
```python
# Start with core features
base_features = ['production_count', 'avg_temp_c']

# Add if available
optional_features = [
    'operating_hours',      # Calculate from status changes
    'shift_id',             # If simulator has shift data
    'product_type',         # If multiple products tracked
    'outdoor_humidity'      # For HVAC SEUs
]

# Exclude time-based (causes overfitting)
exclude = ['hour', 'day_of_week', 'month']
```

---

## Testing Scenarios

### Scenario 1: Perfect Baseline
- Train on 2024 data (365 days, R²=0.95)
- 2025 consumption exactly matches expected
- **Expected:** Deviation = 0%, Status = Compliant ✅

### Scenario 2: Efficiency Improvement
- Train on 2024 baseline
- 2025 actual = 95% of expected (process optimization)
- **Expected:** Deviation = -5%, Status = Compliant (savings!) ✅

### Scenario 3: Performance Degradation
- Train on 2024 baseline
- 2025 actual = 110% of expected (equipment wear)
- **Expected:** Deviation = +10%, Status = Critical 🔴

### Scenario 4: Quarterly Tracking
- Q1: +2% (compliant)
- Q2: +4% (warning)
- Q3: +8% (critical) ← Trigger maintenance action
- Q4: +3% (back to compliant after repairs)

---

## SQL Helper Functions

```sql
-- Calculate SEU energy for period
CREATE OR REPLACE FUNCTION get_seu_energy(
    p_seu_id UUID,
    p_start_date TIMESTAMPTZ,
    p_end_date TIMESTAMPTZ
) RETURNS DECIMAL AS $$
    SELECT SUM(energy_kwh)
    FROM energy_readings er
    WHERE machine_id = ANY(
        SELECT unnest(machine_ids) FROM seus WHERE id = p_seu_id
    )
    AND time BETWEEN p_start_date AND p_end_date;
$$ LANGUAGE SQL;

-- Get deviation status
CREATE OR REPLACE FUNCTION get_deviation_status(
    p_deviation_percent DECIMAL
) RETURNS TEXT AS $$
    SELECT CASE
        WHEN abs(p_deviation_percent) <= 3.0 THEN 'compliant'
        WHEN abs(p_deviation_percent) <= 5.0 THEN 'warning'
        ELSE 'critical'
    END;
$$ LANGUAGE SQL;
```

---

## Migration Path (No Breaking Changes)

### Existing System (Keep Running)
- `energy_baselines` table → Real-time predictions
- Materialized view `energy_predictions_realtime` → 1-min refresh
- Scheduler: Weekly retraining → Keep for anomaly detection
- Dashboard: "Machine Monitoring" → Rename to "Real-Time Monitoring"

### New System (Add Parallel)
- `seus`, `seu_energy_performance` → ISO 50001 compliance
- No materialized view needed (reports generated on demand)
- Manual training via API
- Dashboard: "ISO 50001 EnPI Report" → New

### Zero Downtime Deployment
1. Run migration script (adds new tables, doesn't touch existing)
2. Deploy analytics service with new routes (old routes unchanged)
3. Add new Grafana dashboard (doesn't replace existing)
4. Test new system with one SEU
5. Roll out to all SEUs

---

## Success Metrics

- [ ] Train baseline on 365 days in <30 seconds
- [ ] Regression R² > 0.85 for all SEUs
- [ ] Generate quarterly report in <5 seconds
- [ ] Dashboard loads in <2 seconds
- [ ] Auditor can view 3-year EnPI trend with 2 clicks
- [ ] Energy manager can explain ±5% deviation with stored notes

---

## Future Enhancements (Post-MVP)

1. **Multi-year baselines:** Compare 2025 to best of 2023/2024
2. **Weather normalization:** Adjust baseline for abnormal weather years
3. **Production mix adjustment:** Account for product type changes
4. **Auto-alerts:** Email when deviation >5% for 2 consecutive quarters
5. **Export to PDF:** Generate ISO 50001 compliance report for auditors
6. **Baseline versioning:** Track formula changes over time
7. **What-if scenarios:** "If production increases 20%, expected energy?"

---

## References

- ISO 50001:2018 Energy Management Systems standard
- EnPI = Energy Performance Indicator (Clause 6.3)
- SEU = Significant Energy Use (Clause 6.3)
- Baseline period: Minimum 12 months continuous data
- Review frequency: Minimum annually, recommended quarterly

---

**End of Document**
