# ISO 50001 EnPI Implementation - MASTER ROADMAP

**Document Purpose:** Source of truth, guideline, todo list  
**Created:** October 22, 2025  
**Status:** ACTIVE ROADMAP  
**For:** Mr. Umut's Requirements

---

## 🎯 MR. UMUT'S REQUIREMENTS (FINAL VERSION)

### Core Understanding

> **Direct Quote from Mr. Umut:**
> - "you are not expected to implement continuous regression"
> - "act like you have past two years data (2024 and 2025)"
> - "you'll use 2024 data for training to find out the regression formula"
> - "then you'll estimate 2025 data with regression formula"
> - "then you'll use 2025 data to compare expected consumption and real consumption"
> - "we'll do this for each SEU of each energy sources (ie. electricity, gas etc.)"

### Translation to Technical Requirements

1. **NO continuous retraining** - One-time baseline training on 2024 data
2. **2024 = Baseline Year** - Full calendar year for training regression
3. **2025 = Performance Year** - Compare actual vs predicted using 2024 formula
4. **Per-SEU Analysis** - Each SEU gets own baseline formula
5. **Per-Energy-Source** - Separate baselines for electricity, gas, compressed air, steam
6. **Output** - Deviation % = (Actual - Expected) / Expected × 100

---

## 📊 CURRENT SYSTEM STATE (As of Oct 22, 2025 19:15 UTC)

### Database Status

**✅ Data Available:**
- 2024 Data: 61,488 hourly records (full year, 7 machines)
- 2025 Data: 2,477,506 records (Jan 1 - Oct 22, live + backfilled Q1-Q3)
- Machines: 7 active (2 compressors, 2 HVACs, 1 motor, 1 pump, 1 injection molding)

**✅ Schema Complete:**
- `energy_sources`: 4 rows (electricity, natural_gas, compressed_air, steam)
- `seus`: 3 rows (Compressed Air Production, Material Handling, Production Equipment)
- `seu_energy_performance`: 9 rows (Q1-Q3 2025 reports for 3 SEUs)

**⚠️ PROBLEM IDENTIFIED:**
Current system has **3 SEUs ALL using electricity**, but Mr. Umut wants:
- SEUs **per energy source** (electricity SEUs, gas SEUs, compressed air SEUs, steam SEUs)
- Current approach groups machines into SEUs regardless of energy source
- **NEEDS REDESIGN** to match Mr. Umut's intent

### Code Status

**✅ Working Components:**
- `/analytics/services/seu_baseline_service.py` - Annual baseline training (LinearRegression)
- `/analytics/api/routes/reports.py` - SEU performance report generation
- `/scripts/backfill-realistic-historical-data.py` - 2024 data generation (matches live simulator)
- `/scripts/backfill-2025-performance-period.py` - 2025 Q1-Q3 data with efficiency improvement

**❌ Wrong Implementation:**
- Dashboard `/grafana/dashboards/iso-50001-enpi-report.json` - Built for wrong SEU structure
- API expects SEU grouping, not energy-source-based analysis
- Continuous aggregate functions assume hourly data, not daily aggregates

---

## 🔍 GAP ANALYSIS: Current vs Mr. Umut's Expectation

| Aspect | Current Implementation | Mr. Umut's Requirement | Action Needed |
|--------|------------------------|------------------------|---------------|
| **SEU Structure** | 3 SEUs mixing machines by function | SEUs **per energy source** | ❌ REDESIGN |
| **Baseline Scope** | Per SEU (multi-machine aggregate) | Per SEU of **each energy source** | ❌ REDESIGN |
| **Energy Sources** | All 3 SEUs use electricity | Separate electricity, gas, compressed air, steam | ❌ ADD GAS/AIR/STEAM TRACKING |
| **Training Frequency** | One-time (correct) | One-time (matches) | ✅ CORRECT |
| **Comparison Period** | Quarterly (Q1, Q2, Q3) | Any period in 2025 | ✅ FLEXIBLE (correct) |
| **Data Granularity** | Daily aggregates | Daily aggregates | ✅ CORRECT |
| **Formula Storage** | `seus.regression_coefficients` | Per-SEU formula | ✅ CORRECT |
| **Dashboard** | 3 SEUs (wrong grouping) | Per energy source view | ❌ REBUILD |

**CRITICAL INSIGHT:**  
Mr. Umut wants to see:
- **Electricity-based SEUs**: Compressors, HVAC, Motors consuming electricity
- **Gas-based SEUs**: Boilers, heating systems (not yet tracked!)
- **Compressed Air SEUs**: Pneumatic tools, actuators (derived from compressors)
- **Steam SEUs**: Process equipment using steam (not yet tracked!)

But our current data **ONLY tracks electricity**! No gas meters, no compressed air flow meters, no steam flow meters.

---

## 🚨 FUNDAMENTAL QUESTIONS TO RESOLVE

### Q1: Do we have non-electricity energy sources?

**Current Simulator:**
- Generates: `energy_readings` (power_kw, energy_kwh - **assumes electricity**)
- Does NOT generate: gas consumption (m³), compressed air usage (Nm³), steam consumption (kg)

**Options:**
1. **Assume electricity-only for now** (simplest, matches current data)
2. **Add fake gas/air/steam meters** to simulator for demonstration
3. **Derive compressed air from compressor output** (flow_rate_m3h already tracked in environmental_data)

**RECOMMENDATION:** Option 3 - Use existing `environmental_data.flow_rate_m3h` from compressors as "compressed air" SEU.

### Q2: What is a "SEU of an energy source"?

**Interpretation A (Current Implementation):**
- SEU = Group of machines with shared energy characteristics
- Energy source = Type of energy they consume (all electricity)
- Example: "Compressed Air Production SEU" = 2 compressors consuming electricity

**Interpretation B (Mr. Umut's Intent):**
- SEU = Significant energy user
- "SEU of electricity" = Any equipment consuming electricity (compressors, motors, HVAC)
- "SEU of compressed air" = Any equipment consuming compressed air (pneumatic tools - not tracked!)
- Baseline formula predicts energy consumption OF THAT ENERGY TYPE

**RECOMMENDATION:** Interpretation B - Separate baselines for:
- Electricity consumption by compressors
- Electricity consumption by HVAC
- Electricity consumption by motors/pumps
- Compressed air production (output of compressors)

### Q3: Should each machine be its own SEU?

**Current:** 3 SEUs grouping multiple machines  
**Alternative:** 7 SEUs (one per machine)  

**Pros of Per-Machine:**
- Matches "SEU of energy source" better
- Simpler baseline (single machine behavior)
- No aggregation complexity

**Cons:**
- More baselines to manage (7 vs 3)
- Less representative of facility-level view

**RECOMMENDATION:** **Per-Machine SEUs** - Aligns with "each SEU of each energy source"

---

## ✅ CORRECT IMPLEMENTATION PLAN

### Phase 1: Clarify Scope with Mr. Umut (Before Coding!)

**Questions to Ask:**

1. **Energy Sources:**
   - Do you want to track electricity only, or also gas/compressed air/steam?
   - If only electricity, should we rename to "Electricity Consumption Monitoring" instead of "Energy Sources"?

2. **SEU Definition:**
   - Should each machine be its own SEU? Or keep grouping by function (compressors, HVAC, etc.)?
   - Example: "Compressor-1 Electricity SEU" vs "Compressed Air Production SEU"?

3. **Compressed Air:**
   - Compressors consume electricity but produce compressed air. Should we track:
     - Energy input (electricity to compressors) - YES
     - Energy output (compressed air delivered) - MAYBE?

4. **Baseline Variables:**
   - 2024 baseline should use: `production_count`, `temperature`, what else?
   - Should each machine type have different features (HVAC uses temp only, motors use production only)?

### Phase 2: Database Schema Adjustment

**Option A: Per-Machine SEUs (Recommended)**

```sql
-- Delete existing wrong SEUs
DELETE FROM seu_energy_performance;
DELETE FROM seus;

-- Create per-machine SEUs (all electricity for now)
INSERT INTO seus (id, name, description, energy_source_id, machine_ids) VALUES
    ('11111111-1111-1111-1111-000000000001', 
     'Compressor-1 (Electricity)', 
     'Electricity consumption baseline for Compressor-1',
     (SELECT id FROM energy_sources WHERE name='electricity'),
     ARRAY['c0000000-0000-0000-0000-000000000001'::uuid]),
    
    ('11111111-1111-1111-1111-000000000002',
     'Compressor-EU-1 (Electricity)',
     'Electricity consumption baseline for Compressor-EU-1',
     (SELECT id FROM energy_sources WHERE name='electricity'),
     ARRAY['c0000000-0000-0000-0000-000000000006'::uuid]),
    
    ('11111111-1111-1111-1111-000000000003',
     'HVAC-Main (Electricity)',
     'Electricity consumption baseline for HVAC-Main',
     (SELECT id FROM energy_sources WHERE name='electricity'),
     ARRAY['c0000000-0000-0000-0000-000000000002'::uuid]),
    
    ('11111111-1111-1111-1111-000000000004',
     'HVAC-EU-North (Electricity)',
     'Electricity consumption baseline for HVAC-EU-North',
     (SELECT id FROM energy_sources WHERE name='electricity'),
     ARRAY['c0000000-0000-0000-0000-000000000007'::uuid]),
    
    ('11111111-1111-1111-1111-000000000005',
     'Conveyor-A (Electricity)',
     'Electricity consumption baseline for Conveyor-A motor',
     (SELECT id FROM energy_sources WHERE name='electricity'),
     ARRAY['c0000000-0000-0000-0000-000000000003'::uuid]),
    
    ('11111111-1111-1111-1111-000000000006',
     'Hydraulic-Pump-1 (Electricity)',
     'Electricity consumption baseline for Hydraulic-Pump-1',
     (SELECT id FROM energy_sources WHERE name='electricity'),
     ARRAY['c0000000-0000-0000-0000-000000000004'::uuid]),
    
    ('11111111-1111-1111-1111-000000000007',
     'Injection-Molding-1 (Electricity)',
     'Electricity consumption baseline for Injection-Molding-1',
     (SELECT id FROM energy_sources WHERE name='electricity'),
     ARRAY['c0000000-0000-0000-0000-000000000005'::uuid]);
```

**Option B: Keep Grouping + Add Per-Energy-Source View**

(More complex, requires aggregation views)

### Phase 3: PostgreSQL Function Update

**Current Function:**
`get_seu_daily_aggregates(seu_id, start_date, end_date)`

**Returns:** Daily aggregates for all machines in SEU

**Change Needed:**
- **IF** using per-machine SEUs → Function works as-is (1 machine = simple)
- **IF** keeping grouped SEUs → Need to ensure aggregation is by energy source

**Recommendation:** Keep function as-is IF using per-machine approach.

### Phase 4: Baseline Training Strategy

**Per Machine Type:**

| Machine Type | Features for Regression | Rationale |
|--------------|-------------------------|-----------|
| **Compressors** | `avg_production_count` (flow), `avg_temp_c` | Production drives demand, temp affects efficiency |
| **HVACs** | `avg_temp_c` **ONLY** | No production, purely temperature-driven |
| **Motors/Conveyors** | `avg_production_count` | Speed/load varies with production |
| **Pumps** | `avg_production_count`, `avg_temp_c` | Cycle-based production, temp affects viscosity |
| **Injection Molding** | `avg_production_count`, `avg_temp_c` | Heating cycles, ambient temp affects cooling |

**Training API Call (Example for Compressor-1):**

```bash
curl -X POST http://localhost:8001/api/v1/baseline/seu/train \
  -H "Content-Type: application/json" \
  -d '{
    "seu_id": "11111111-1111-1111-1111-000000000001",
    "baseline_year": 2024,
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "features": ["avg_production_count", "avg_temp_c"]
  }'
```

**Expected Output:**
- R² > 0.85 (target quality)
- Positive coefficients for production (more production → more energy)
- Negative or positive for temp (depends on machine type)
- Intercept near zero or positive (base load)

### Phase 5: 2025 Performance Comparison

**Per Quarter:**

```bash
# Q1 2025 for Compressor-1
curl -X POST http://localhost:8001/api/v1/reports/seu-performance \
  -H "Content-Type: application/json" \
  -d '{
    "seu_id": "11111111-1111-1111-1111-000000000001",
    "report_year": 2025,
    "baseline_year": 2024,
    "period": "Q1"
  }'
```

**Expected Response:**
```json
{
  "seu_name": "Compressor-1 (Electricity)",
  "energy_source": "electricity",
  "report_period": "2025-Q1",
  "actual_consumption_kwh": 8234.56,
  "expected_consumption_kwh": 8456.78,
  "deviation_kwh": -222.22,
  "deviation_percent": -2.63,
  "compliance_status": "compliant",
  "baseline_formula": "Energy = 0.45 + 0.0123×production + 0.0045×temp",
  "baseline_r_squared": 0.92
}
```

### Phase 6: Grafana Dashboard Redesign

**New Structure:**

**Panel 1: Energy Source Selector**
- Variable: `$energy_source` (electricity, gas, compressed_air, steam)
- Filters SEU list

**Panel 2: SEU Selector**
- Variable: `$seu_id` (filtered by energy_source)
- Options: All machines consuming selected energy source

**Panel 3: Comparison Period**
- Variables: `$year` (2024, 2025), `$quarter` (Q1, Q2, Q3, Q4)

**Panel 4: Deviation Gauge**
- Query: `SELECT deviation_percent FROM seu_energy_performance WHERE seu_id=$seu_id AND report_period=$year-$quarter`
- Thresholds: Green (±3%), Yellow (±5%), Red (>5%)

**Panel 5: Actual vs Expected Chart**
- Monthly breakdown within quarter
- Two bars per month: Actual (blue), Expected (orange)

**Panel 6: All SEUs Summary Table**
- All SEUs for selected energy source
- Columns: SEU Name, Q1 Dev%, Q2 Dev%, Q3 Dev%, Status

---

## 📝 IMPLEMENTATION CHECKLIST

### ☐ Step 1: Clarification Meeting with Mr. Umut

**Questions to Confirm:**
- [ ] Are we tracking electricity only? (Yes/No)
- [ ] Should we track compressed air production separately? (Yes/No)
- [ ] One SEU per machine, or keep grouping? (Per-machine / Grouped)
- [ ] Acceptable deviation range? (±3%, ±5%, ±10%?)
- [ ] Report frequency? (Quarterly / Monthly / Custom)

**Decision Log:**
- Date: ___________
- Electricity only: [ ] Yes [ ] No
- Per-machine SEUs: [ ] Yes [ ] No
- Compressed air tracking: [ ] Yes [ ] No
- Other decisions: _______________________________

### ☐ Step 2: Database Reset (IF NEEDED)

**If Mr. Umut confirms per-machine approach:**

```bash
# Run SQL script to recreate SEUs
psql -h localhost -p 5433 -U raptorblingx -d enms -f scripts/reset-seus-per-machine.sql
```

**Script creates:**
- 7 electricity SEUs (one per machine)
- Optionally: Compressed air SEUs (if confirmed)
- Deletes old performance reports

### ☐ Step 3: Train 2024 Baselines

**For Each Machine:**

```bash
# Compressor-1
curl -X POST localhost:8001/api/v1/baseline/seu/train \
  -H "Content-Type: application/json" \
  -d '{"seu_id": "11111111-1111-1111-1111-000000000001", "baseline_year": 2024, "start_date": "2024-01-01", "end_date": "2024-12-31", "features": ["avg_production_count", "avg_temp_c"]}'

# HVAC-Main (temperature only!)
curl -X POST localhost:8001/api/v1/baseline/seu/train \
  -H "Content-Type: application/json" \
  -d '{"seu_id": "11111111-1111-1111-1111-000000000003", "baseline_year": 2024, "start_date": "2024-01-01", "end_date": "2024-12-31", "features": ["avg_temp_c"]}'

# ... (repeat for all 7 machines)
```

**Success Criteria:**
- [ ] All baselines trained (R² > 0.85)
- [ ] Formulas stored in `seus` table
- [ ] No negative intercepts (unless explainable)

### ☐ Step 4: Generate 2025 Performance Reports

**For Each Quarter:**

```bash
# Q1 2025 - All SEUs
for seu_id in 11111111-1111-1111-1111-000000000001 11111111-1111-1111-1111-000000000002 ...; do
  curl -X POST localhost:8001/api/v1/reports/seu-performance \
    -H "Content-Type: application/json" \
    -d "{\"seu_id\": \"$seu_id\", \"report_year\": 2025, \"baseline_year\": 2024, \"period\": \"Q1\"}"
done

# Repeat for Q2, Q3
```

**Success Criteria:**
- [ ] 21 reports generated (7 SEUs × 3 quarters)
- [ ] Deviation % within expected range (±2% to ±10%)
- [ ] Status correctly assigned (compliant/warning/critical)

### ☐ Step 5: Update Grafana Dashboard

**Changes Needed:**
- [ ] Add `$energy_source` variable (filtered list)
- [ ] Update `$seu_id` query to filter by energy_source
- [ ] Change panel titles to show energy source + machine name
- [ ] Add "All SEUs Summary" panel (table view)
- [ ] Update queries to use correct SEU IDs

**File:** `/home/ubuntu/enms/grafana/dashboards/iso-50001-enpi-report.json`

### ☐ Step 6: Create Demo Summary Document

**File:** `docs/ISO-50001-DEMO-FINAL-SUMMARY.md`

**Sections:**
1. Executive Summary
2. System Overview (per-machine SEUs, electricity-only)
3. Baseline Training Results (7 machines, R² scores)
4. 2025 Performance Results (Q1-Q3, deviation %)
5. Compliance Status (how many SEUs meet ±X% target)
6. Dashboard Usage Guide
7. API Documentation (how to generate new reports)
8. Next Steps (adding gas/air/steam if needed)

### ☐ Step 7: Presentation to Mr. Umut

**Materials:**
- [ ] Demo Summary Document (printed PDF)
- [ ] Grafana Dashboard (live demo)
- [ ] API Examples (Postman collection or curl commands)
- [ ] Sample Reports (Q1-Q3 2025 for 2-3 machines)

**Key Points to Emphasize:**
- ✅ One-time 2024 baseline training (no continuous retraining)
- ✅ 2025 comparison using 2024 formula
- ✅ Per-SEU, per-energy-source analysis
- ✅ Quarterly reporting (or custom periods)
- ⚠️ Currently electricity-only (can extend to gas/air/steam)

---

## 🎯 SUCCESS CRITERIA

### Technical Success:
- [ ] 7 SEUs created (one per machine, all electricity)
- [ ] 7 baseline models trained (R² > 0.85, realistic coefficients)
- [ ] 21 performance reports generated (7 SEUs × 3 quarters 2025)
- [ ] Grafana dashboard displays correct data
- [ ] API returns consistent results

### Business Success (Mr. Umut's Acceptance):
- [ ] Understands 2024 = baseline year, 2025 = comparison year
- [ ] Can see deviation % for each machine per quarter
- [ ] Knows how to interpret "compliant" vs "warning" vs "critical"
- [ ] Satisfied with electricity-only scope (or requests expansion)
- [ ] Approves next steps (production deployment, add other energy sources)

---

## 📊 DATA VERIFICATION QUERIES

### Check 2024 Baseline Data:
```sql
SELECT 
    COUNT(*) as total_records,
    MIN(time) as earliest,
    MAX(time) as latest,
    COUNT(DISTINCT machine_id) as machines
FROM energy_readings
WHERE time >= '2024-01-01' AND time < '2025-01-01';
-- Expected: 61,488 records, 2024-01-01 to 2024-12-31, 7 machines
```

### Check 2025 Performance Data:
```sql
SELECT 
    COUNT(*) as total_records,
    MIN(time) as earliest,
    MAX(time) as latest
FROM energy_readings
WHERE time >= '2025-01-01' AND time < '2025-10-01';
-- Expected: ~1.9M records (Q1-Q3 backfilled + Oct 10-22 live)
```

### Check SEU Baselines:
```sql
SELECT 
    s.name,
    s.baseline_year,
    s.r_squared,
    s.feature_columns,
    s.intercept,
    s.regression_coefficients
FROM seus s
WHERE s.baseline_year = 2024
ORDER BY s.name;
-- Expected: 7 rows (or 3 if keeping current structure)
```

### Check Performance Reports:
```sql
SELECT 
    s.name as seu_name,
    sp.report_period,
    sp.deviation_percent,
    sp.compliance_status
FROM seu_energy_performance sp
JOIN seus s ON sp.seu_id = s.id
WHERE sp.baseline_year = 2024
  AND sp.report_period LIKE '2025-%'
ORDER BY s.name, sp.report_period;
-- Expected: 21 rows (7 SEUs × 3 quarters) or 9 rows (3 SEUs × 3 quarters)
```

---

## 🚨 RISK MITIGATION

### Risk 1: Mr. Umut expects gas/air/steam tracking

**Likelihood:** Medium  
**Impact:** High (requires major rework)

**Mitigation:**
- Ask clarifying questions upfront (Phase 1)
- If confirmed, add fake meters to simulator for demonstration purposes
- Estimate 2-3 days additional work for gas/air/steam

### Risk 2: Per-machine SEUs produce unstable baselines

**Likelihood:** Low  
**Impact:** Medium (need to revert to grouped SEUs)

**Mitigation:**
- Test baseline training on 2-3 machines first
- If R² < 0.70, consider grouping similar machines
- Keep grouped approach as fallback

### Risk 3: 2025 data has systematic bias vs 2024

**Likelihood:** Medium (already observed in previous attempts!)  
**Impact:** High (unrealistic deviations like +274% or -27%)

**Mitigation:**
- Verify backfill scripts use identical parameters for 2024 and 2025
- Check `rated_power`, `base_power`, shift schedules match exactly
- Run comparison query: `SELECT AVG(power_kw) FROM energy_readings WHERE time BETWEEN '2024-01-01' AND '2024-12-31'` vs `'2025-01-01' AND '2025-03-31'`

---

## 📚 REFERENCE MATERIALS

### Key Files:
- `/analytics/services/seu_baseline_service.py` - Baseline training logic
- `/analytics/api/routes/reports.py` - Performance report generation
- `/database/init/003-iso50001-schema.sql` - SEU schema definition
- `/grafana/dashboards/iso-50001-enpi-report.json` - Current dashboard (needs update)
- `/scripts/backfill-realistic-historical-data.py` - 2024 data generation
- `/scripts/backfill-2025-performance-period.py` - 2025 data generation

### SQL Functions:
- `get_seu_daily_aggregates(seu_id, start_date, end_date)` - Returns daily aggregates for baseline training
- `get_seu_energy(seu_id, start_date, end_date)` - Returns total energy consumption for period
- `calculate_deviation(actual, expected)` - Returns deviation % and compliance status

### API Endpoints:
- `POST /api/v1/baseline/seu/train` - Train annual baseline
- `POST /api/v1/reports/seu-performance` - Generate performance report
- `GET /api/v1/seus` - List all SEUs
- `GET /api/v1/energy-sources` - List energy sources

---

## 💡 LESSONS LEARNED (From Previous Attempts)

### Mistake 1: Synthetic data with wrong production values
- **Problem:** Used `production_count = random(10, 1000)` instead of realistic hourly rates
- **Result:** Baseline formulas predicted nonsense (negative intercepts, wrong coefficients)
- **Fix:** Replicated exact simulator logic in backfill scripts

### Mistake 2: Mismatched power calculations between 2024 and 2025
- **Problem:** 2024 used `rated_power = [12, 9, 7, ...]`, 2025 used `[15, 10, 20, ...]`
- **Result:** 2025 showed +30% to +80% power increase (unrealistic)
- **Fix:** Aligned `rated_power` values across both scripts

### Mistake 3: Wrong SEU grouping
- **Problem:** Created "functional" SEUs (Compressed Air, Material Handling) mixing different machines
- **Result:** Doesn't match Mr. Umut's "per energy source" requirement
- **Fix:** This roadmap recommends per-machine SEUs

### Mistake 4: Dashboard datasource mismatch
- **Problem:** Dashboard referenced "postgres" datasource, but Grafana has "TimescaleDB"
- **Result:** "Datasource not found" error
- **Fix:** Updated all 18 datasource UIDs in JSON

---

## ✅ NEXT IMMEDIATE ACTIONS

1. **STOP** all coding until clarification from Mr. Umut
2. **PREPARE** clarification questions (see Phase 1)
3. **DOCUMENT** current system state (this roadmap)
4. **WAIT** for confirmation on:
   - Per-machine vs grouped SEUs
   - Electricity-only vs multi-energy-source
   - Compressed air tracking
5. **THEN** proceed with Phase 2-7 based on decisions

---

**END OF ROADMAP**

*This document is the single source of truth for ISO 50001 EnPI implementation.*  
*All decisions, changes, and progress must be documented here.*  
*Do not start coding without confirming Phase 1 decisions.*

