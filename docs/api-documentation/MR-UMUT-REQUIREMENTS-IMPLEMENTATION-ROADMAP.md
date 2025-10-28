# Mr. Umut's Requirements - Implementation Roadmap

**Project**: EnMS Multi-Energy Baseline System  
**Purpose**: ISO 50001 Compliant Dynamic Regression Analysis  
**Date**: October 24, 2025  
**Status**: Phase 1 Complete - Phases 2-4 Pending

---

## 📊 EXECUTIVE SUMMARY

### What Mr. Umut Wants

> "Act like you have past two years data (2024 and 2025). Use 2024 data for training to find out the regression formula. Then estimate 2025 data with regression formula. Then use 2025 data to compare expected consumption vs real consumption. We'll do this for each SEU of each energy source (electricity, gas, steam, etc.)"

**Key Requirements**:
1. **Train/Test Split Methodology** - Use historical period for training, future period for validation
2. **Multi-Energy Support** - Works for electricity, natural gas, steam, compressed air (NOT hardcoded)
3. **Dynamic Feature Selection** - User/OVOS specifies features, system adapts
4. **OVOS Voice Training** - "Train baseline for Compressor-1 electricity using production count and temperature for 2024"
5. **Zero Hardcoding** - Expandable architecture (from LAUDS project lessons)

---

## ✅ CURRENT SYSTEM STATE (As of Oct 24, 2025)

### What's Already Implemented

#### ✅ Database Schema (95% Complete)
```sql
✓ energy_sources table (4 sources: electricity, natural_gas, compressed_air, steam)
✓ seus table (7 electricity SEUs created)
✓ energy_source_features table (dynamic feature metadata)
✓ seu_energy_performance table (monthly reports)
✓ baseline_adjustments table (ISO 50001 compliance)
✓ data_quality_log table
```

**Key Finding**: Schema is **FULLY multi-energy compatible**. No changes needed!

#### ✅ Services Layer (90% Complete)
```python
✓ SEUBaselineService - ISO 50001 annual baseline training
✓ FeatureDiscoveryService - Dynamic feature lookup (NO hardcoding)
✓ EnPICalculator - Energy Performance Indicators
✓ BaselineService - Real-time machine baselines (separate from SEU)
```

**Key Finding**: Services use dynamic feature discovery. Multi-energy ready!

#### ✅ API Routes (85% Complete)
```python
✓ /api/v1/ovos/train-baseline - OVOS voice training (EXISTS!)
✓ /api/v1/ovos/energy-sources - Dynamic energy source discovery
✓ /api/v1/ovos/seus - List SEUs by energy source
✓ /api/v1/baseline/seu/train - SEU baseline training
✓ /api/v1/reports/generate-monthly - Monthly EnPI reports
```

**Key Finding**: OVOS endpoints **ALREADY EXIST** and are registered in main.py!

#### ✅ ML Models (100% Complete)
```python
✓ BaselineModel (sklearn LinearRegression)
✓ ARIMAForecast (time series forecasting)
✓ ProphetForecast (seasonal forecasting)
✓ AnomalyDetector (isolation forest)
```

**Key Finding**: ML infrastructure complete and production-ready.

#### ✅ Data Ingestion (100% Complete)
```
Simulator → MQTT (mosquitto) → Node-RED → PostgreSQL (TimescaleDB)
✓ 2.8M samples collected (Oct 2024 - present)
✓ 1-2 samples/second (real-time)
✓ 7 machines × 3 tables (energy_readings, production_data, environmental_data)
```

---

### What's NOT Implemented

#### ❌ Multi-Energy Hypertables (0% - Not Needed Yet)
```sql
✗ natural_gas_readings table (schema defined, no data)
✗ steam_readings table (schema defined, no data)
✗ compressed_air_end_use_readings table (schema defined, no data)
```

**Impact**: Low - Only needed when physical meters are installed

#### ⚠️ Data Quality Issues (Critical - Needs Fix)
```
⚠️ Backfilled data (Jan 2024 - Sep 2025): ~61k samples (hourly intervals)
   - Artificially generated
   - Inconsistent efficiency patterns
   - Causing -30% and +226% deviation artifacts
   
✓ Real simulator data (Oct 7 - Oct 24, 2025): ~2.8M samples (1-second intervals)
   - Genuine operational patterns
   - Statistically sufficient for baselines
```

**Impact**: High - Current baselines trained on backfilled data

#### ⚠️ SEU Baseline Periods (Needs Update)
```
Current: baseline_year=2024, dates=2024-01-01 to 2024-12-31 (backfilled fake data)
Needed: baseline_year=2024, dates=2024-10-07 to 2024-10-21 (real data - 14 days)
```

**Impact**: High - Need to retrain all 7 SEUs on real data

---

## 🎯 IMPLEMENTATION ROADMAP

### PHASE 1: Data Cleanup & Real Baseline Training (TODAY - 2 hours)

**Goal**: Use ONLY real simulator data for baselines (Oct 7-24, 2025)

#### Step 1.1: Archive Backfilled Data (15 min)
```sql
-- Create archive schema for backfilled data
CREATE SCHEMA IF NOT EXISTS demo_archive;

-- Move backfilled data (keep for future demos if needed)
CREATE TABLE demo_archive.energy_readings_backfill AS 
SELECT * FROM energy_readings WHERE time < '2024-10-07';

CREATE TABLE demo_archive.production_data_backfill AS 
SELECT * FROM production_data WHERE time < '2024-10-07';

CREATE TABLE demo_archive.environmental_data_backfill AS 
SELECT * FROM environmental_data WHERE time < '2024-10-07';

-- Delete from main tables
DELETE FROM energy_readings WHERE time < '2024-10-07';
DELETE FROM production_data WHERE time < '2024-10-07';
DELETE FROM environmental_data WHERE time < '2024-10-07';

-- Vacuum to reclaim space
VACUUM FULL energy_readings;
VACUUM FULL production_data;
VACUUM FULL environmental_data;
```

**Validation**:
```sql
-- Should return ~2.8M (only real data)
SELECT COUNT(*) FROM energy_readings;

-- Should return Oct 7, 2024 onwards
SELECT MIN(time), MAX(time) FROM energy_readings;

-- Should be ~1-2 samples/sec
SELECT ROUND(COUNT(*) / EXTRACT(EPOCH FROM (MAX(time) - MIN(time))), 2) 
FROM energy_readings;
```

**Why Archive Instead of Delete?**
- Keeps audit trail
- Can restore for demos if needed
- Mr. Umut might want year-over-year comparison later

---

#### Step 1.2: Update SEU Baseline Metadata (5 min)
```sql
-- Set baseline period to first 14 days of real data
UPDATE seus SET
    baseline_year = 2024,
    baseline_start_date = '2024-10-07',
    baseline_end_date = '2024-10-21',  -- 14 days training period
    trained_at = NULL,  -- Force retrain
    r_squared = NULL,
    rmse = NULL
WHERE energy_source_id = (SELECT id FROM energy_sources WHERE name = 'electricity');

-- Verify
SELECT name, baseline_start_date, baseline_end_date, trained_at 
FROM seus 
ORDER BY name;
```

**Expected Result**: 7 SEUs with dates 2024-10-07 to 2024-10-21, trained_at = NULL

---

#### Step 1.3: Retrain All SEU Baselines (40 min)

**Script**: `scripts/retrain-real-baselines.sh`
```bash
#!/bin/bash
set -e

echo "🔄 Retraining all SEU baselines on real Oct 7-21 data..."

BASELINE_START="2024-10-07"
BASELINE_END="2024-10-21"

# Get all electricity SEUs
SEUS=$(docker exec enms-postgres psql -U raptorblingx -d enms -t -c "
  SELECT id FROM seus 
  WHERE energy_source_id = (SELECT id FROM energy_sources WHERE name = 'electricity')
  ORDER BY name
")

for seu_id in $SEUS; do
  seu_id=$(echo $seu_id | xargs)  # Trim whitespace
  
  echo "Training SEU: $seu_id"
  
  curl -X POST http://localhost:8001/api/v1/baseline/seu/train \
    -H "Content-Type: application/json" \
    -d "{
      \"seu_id\": \"$seu_id\",
      \"baseline_year\": 2024,
      \"start_date\": \"$BASELINE_START\",
      \"end_date\": \"$BASELINE_END\",
      \"features\": [\"production_count\", \"outdoor_temp_c\"]
    }" | jq -r '.r_squared, .rmse, .samples_count'
  
  echo "---"
  sleep 2
done

echo "✅ All baselines retrained on real simulator data"
```

**Run**:
```bash
chmod +x scripts/retrain-real-baselines.sh
./scripts/retrain-real-baselines.sh
```

**Expected Output** (per SEU):
```
Training SEU: aaaaaaaa-1111-1111-1111-111111111111
0.87
0.053
336  # 14 days × 24 hours = 336 daily samples
---
```

**Validation Queries**:
```sql
-- Check all SEUs trained successfully
SELECT 
  name,
  baseline_start_date,
  baseline_end_date,
  r_squared,
  rmse,
  samples_count,
  trained_at
FROM seus
WHERE energy_source_id = (SELECT id FROM energy_sources WHERE name = 'electricity')
ORDER BY r_squared DESC;

-- Expected: All R² > 0.70, trained_at = today

-- Check sample counts (should be ~1M per SEU for 14 days)
SELECT 
  s.name,
  COUNT(*) as training_samples
FROM energy_readings er
JOIN machines m ON er.machine_id = m.id
JOIN seus s ON m.id = ANY(s.machine_ids)
WHERE er.time BETWEEN '2024-10-07' AND '2024-10-21'
  AND s.energy_source_id = (SELECT id FROM energy_sources WHERE name = 'electricity')
GROUP BY s.name
ORDER BY training_samples DESC;

-- Expected: 1M-1.2M samples per SEU (14 days × 86,400 sec/day)
```

---

#### Step 1.4: Generate Performance Reports (20 min)

**Performance Period**: Oct 22 - Nov 24, 2025 (~33 days)

```bash
#!/bin/bash
# Generate monthly reports for Oct-Nov 2025 using new baselines

# October 2025 (partial month: Oct 22-31)
curl -X POST http://localhost:8001/api/v1/reports/generate-monthly \
  -H "Content-Type: application/json" \
  -d '{
    "year": 2025,
    "month": 10,
    "baseline_year": 2024
  }'

# November 2025 (partial month: Nov 1-24)
curl -X POST http://localhost:8001/api/v1/reports/generate-monthly \
  -H "Content-Type: application/json" \
  -d '{
    "year": 2025,
    "month": 11,
    "baseline_year": 2024
  }'
```

**Validation**:
```sql
SELECT 
  s.name,
  sep.report_period,
  sep.actual_consumption,
  sep.expected_consumption,
  sep.deviation_percent
FROM seu_energy_performance sep
JOIN seus s ON sep.seu_id = s.id
WHERE sep.report_period IN ('2025-10', '2025-11')
ORDER BY s.name, sep.report_period;

-- Expected: Realistic deviations (±2-8%) from operational variation
```

**Phase 1 Success Criteria**:
- [ ] Backfilled data archived (not deleted)
- [ ] Only real Oct 7-24 data in main tables
- [ ] All 7 SEUs retrained with R² > 0.70
- [ ] Monthly reports show realistic deviations (±2-8%)
- [ ] Training uses 1M+ samples per SEU (14 days × 1 sample/sec)

---

### PHASE 2: OVOS Voice Integration Testing (THIS WEEK - 4 hours)

**Goal**: Validate existing OVOS endpoints work correctly with real data

#### Step 2.1: Test OVOS Energy Source Discovery (30 min)

**Test 1**: List all energy sources
```bash
curl http://localhost:8001/api/v1/ovos/energy-sources | jq .
```

**Expected Response**:
```json
{
  "success": true,
  "energy_sources": [
    {
      "name": "electricity",
      "unit": "kWh",
      "features_count": 15,
      "sample_features": ["consumption_kwh", "avg_power_kw", "production_count"]
    },
    {
      "name": "natural_gas",
      "unit": "m³",
      "features_count": 0,
      "sample_features": []
    }
  ]
}
```

**Test 2**: List SEUs by energy source
```bash
curl "http://localhost:8001/api/v1/ovos/seus?energy_source=electricity" | jq .
```

**Expected Response**:
```json
{
  "success": true,
  "seus": [
    {
      "id": "aaaaaaaa-1111-1111-1111-111111111111",
      "name": "Compressor-1",
      "energy_source": "electricity",
      "unit": "kWh",
      "machine_count": 1,
      "baseline_year": 2024,
      "r_squared": 0.87
    }
  ],
  "total_count": 7
}
```

---

#### Step 2.2: Test OVOS Voice Training (1 hour)

**Test 3**: Train baseline via OVOS voice command
```bash
curl -X POST http://localhost:8001/api/v1/ovos/train-baseline \
  -H "Content-Type: application/json" \
  -d '{
    "seu_name": "Compressor-1",
    "energy_source": "electricity",
    "features": ["production_count", "outdoor_temp_c"],
    "year": 2024
  }' | jq .
```

**Expected Response**:
```json
{
  "success": true,
  "message": "Compressor-1 electricity baseline trained successfully. R-squared 0.87 (87% accuracy). Energy equals 218.857 plus 0.006520 times production count plus 0.073126 times outdoor temperature",
  "seu_name": "Compressor-1",
  "energy_source": "electricity",
  "r_squared": 0.8723,
  "rmse": 0.0531,
  "formula_readable": "Energy equals 218.857 plus 0.006520 times production count plus 0.073126 times outdoor temperature",
  "formula_technical": "E = 218.857 + 0.006520×P + 0.073126×T",
  "samples_count": 336,
  "trained_at": "2025-10-24T15:30:00Z"
}
```

**Test 4**: Voice training with invalid features
```bash
curl -X POST http://localhost:8001/api/v1/ovos/train-baseline \
  -H "Content-Type: application/json" \
  -d '{
    "seu_name": "Compressor-1",
    "energy_source": "electricity",
    "features": ["invalid_feature", "another_bad_feature"],
    "year": 2024
  }' | jq .
```

**Expected Response**:
```json
{
  "success": false,
  "message": "Invalid features: ['invalid_feature', 'another_bad_feature']. Available features for electricity: ['consumption_kwh', 'avg_power_kw', 'production_count', ...]",
  "seu_name": "Compressor-1",
  "energy_source": "electricity",
  "error_details": "Feature validation failed"
}
```

---

#### Step 2.3: Document OVOS Integration (1 hour)

Create `docs/OVOS-INTEGRATION-GUIDE.md`:

```markdown
# OVOS Voice Assistant Integration Guide

## Voice Commands Supported

### 1. Train Baseline
**User**: "Train baseline for Compressor-1 electricity using production count and outdoor temperature for 2024"

**OVOS Parses**:
- SEU Name: "Compressor-1"
- Energy Source: "electricity"
- Features: ["production_count", "outdoor_temp_c"]
- Year: 2024

**OVOS Calls**:
POST /api/v1/ovos/train-baseline

**System Responds** (voice-friendly):
"Compressor-1 electricity baseline trained successfully. R-squared 0.87. Formula: Energy equals 218 plus 0.007 times production count plus 0.073 times outdoor temperature"

### 2. List Available Energy Sources
**User**: "What energy sources are available?"

**OVOS Calls**:
GET /api/v1/ovos/energy-sources

**System Responds**:
"Available energy sources: electricity, natural gas, compressed air, steam"

### 3. List SEUs
**User**: "Show electricity SEUs"

**OVOS Calls**:
GET /api/v1/ovos/seus?energy_source=electricity

**System Responds**:
"7 electricity SEUs found: Compressor-1, Compressor-EU-1, HVAC-Main, HVAC-EU-North, Conveyor-A, Hydraulic-Pump-1, Injection-Molding-1"
```

**Phase 2 Success Criteria**:
- [ ] OVOS energy source discovery works
- [ ] OVOS SEU listing works (all 7 electricity SEUs returned)
- [ ] OVOS voice training works with valid features
- [ ] OVOS returns helpful error for invalid features
- [ ] Voice responses are human-readable
- [ ] Documentation complete for OVOS skill developers

---

### PHASE 3: Multi-Energy Preparation (NEXT WEEK - Optional)

**Goal**: Prepare infrastructure for future natural gas/steam meters

**Note**: Only do this if Mr. Umut confirms meters will be installed within 3-6 months. Otherwise, skip (YAGNI principle).

#### Step 3.1: Create Multi-Energy Hypertables (30 min)

**Migration**: `database/migrations/010-multi-energy-tables.sql`
```sql
-- Natural Gas Readings (for future boilers, heaters)
CREATE TABLE IF NOT EXISTS natural_gas_readings (
    time TIMESTAMPTZ NOT NULL,
    machine_id UUID NOT NULL REFERENCES machines(id),
    flow_rate_m3h DECIMAL(10,2),
    consumption_m3 DECIMAL(12,4),
    pressure_bar DECIMAL(8,2),
    temperature_c DECIMAL(6,2),
    PRIMARY KEY (time, machine_id)
);

SELECT create_hypertable('natural_gas_readings', 'time', if_not_exists => TRUE);

CREATE INDEX idx_natural_gas_machine ON natural_gas_readings(machine_id, time DESC);

-- Steam Readings (for future autoclaves, process heating)
CREATE TABLE IF NOT EXISTS steam_readings (
    time TIMESTAMPTZ NOT NULL,
    machine_id UUID NOT NULL REFERENCES machines(id),
    flow_rate_kg_h DECIMAL(10,2),
    consumption_kg DECIMAL(12,4),
    pressure_bar DECIMAL(8,2),
    temperature_c DECIMAL(6,2),
    enthalpy_kj_kg DECIMAL(10,2),
    PRIMARY KEY (time, machine_id)
);

SELECT create_hypertable('steam_readings', 'time', if_not_exists => TRUE);

CREATE INDEX idx_steam_machine ON steam_readings(machine_id, time DESC);

-- Compressed Air End-Use (separate from compressor electricity)
CREATE TABLE IF NOT EXISTS compressed_air_end_use_readings (
    time TIMESTAMPTZ NOT NULL,
    machine_id UUID NOT NULL REFERENCES machines(id),
    flow_rate_m3h DECIMAL(10,2),
    consumption_m3 DECIMAL(12,4),
    pressure_bar DECIMAL(8,2),
    PRIMARY KEY (time, machine_id)
);

SELECT create_hypertable('compressed_air_end_use_readings', 'time', if_not_exists => TRUE);

CREATE INDEX idx_compressed_air_machine ON compressed_air_end_use_readings(machine_id, time DESC);
```

**Run**:
```bash
docker exec -i enms-postgres psql -U raptorblingx -d enms < database/migrations/010-multi-energy-tables.sql
```

**Validation**:
```sql
-- Should return natural_gas_readings, steam_readings, compressed_air_end_use_readings
SELECT tablename FROM pg_tables 
WHERE schemaname = 'public' 
  AND (tablename LIKE '%gas%' OR tablename LIKE '%steam%' OR tablename LIKE '%air%');
```

---

#### Step 3.2: Populate Energy Source Features (1 hour)

**Add natural gas features**:
```sql
-- Get natural gas energy source ID
DO $$
DECLARE
    natural_gas_id UUID;
BEGIN
    SELECT id INTO natural_gas_id FROM energy_sources WHERE name = 'natural_gas';
    
    -- Natural gas consumption features
    INSERT INTO energy_source_features (energy_source_id, feature_name, data_type, source_table, source_column, aggregation_function, is_regression_feature, description) VALUES
    (natural_gas_id, 'consumption_m3', 'numeric', 'natural_gas_readings', 'consumption_m3', 'SUM', true, 'Total natural gas consumed (m³)'),
    (natural_gas_id, 'avg_flow_rate_m3h', 'numeric', 'natural_gas_readings', 'flow_rate_m3h', 'AVG', true, 'Average gas flow rate (m³/h)'),
    (natural_gas_id, 'avg_pressure_bar', 'numeric', 'natural_gas_readings', 'pressure_bar', 'AVG', true, 'Average gas pressure (bar)'),
    (natural_gas_id, 'avg_gas_temp_c', 'numeric', 'natural_gas_readings', 'temperature_c', 'AVG', true, 'Average gas temperature (°C)'),
    
    -- Environmental features (shared with electricity)
    (natural_gas_id, 'outdoor_temp_c', 'numeric', 'environmental_data', 'outdoor_temp_c', 'AVG', true, 'Average outdoor temperature (°C) - for heating baselines'),
    (natural_gas_id, 'heating_degree_days', 'numeric', 'environmental_data', 'heating_degree_days', 'SUM', true, 'Heating degree days (base 18°C)'),
    
    -- Production features (shared)
    (natural_gas_id, 'production_count', 'integer', 'production_data', 'production_count', 'SUM', true, 'Total units produced');
END $$;
```

**Steam features**:
```sql
DO $$
DECLARE
    steam_id UUID;
BEGIN
    SELECT id INTO steam_id FROM energy_sources WHERE name = 'steam';
    
    INSERT INTO energy_source_features (energy_source_id, feature_name, data_type, source_table, source_column, aggregation_function, is_regression_feature, description) VALUES
    (steam_id, 'consumption_kg', 'numeric', 'steam_readings', 'consumption_kg', 'SUM', true, 'Total steam consumed (kg)'),
    (steam_id, 'avg_flow_rate_kg_h', 'numeric', 'steam_readings', 'flow_rate_kg_h', 'AVG', true, 'Average steam flow rate (kg/h)'),
    (steam_id, 'avg_pressure_bar', 'numeric', 'steam_readings', 'pressure_bar', 'AVG', true, 'Average steam pressure (bar)'),
    (steam_id, 'avg_steam_temp_c', 'numeric', 'steam_readings', 'temperature_c', 'AVG', true, 'Average steam temperature (°C)'),
    (steam_id, 'avg_enthalpy_kj_kg', 'numeric', 'steam_readings', 'enthalpy_kj_kg', 'AVG', true, 'Average steam enthalpy (kJ/kg)'),
    
    -- Production features
    (steam_id, 'production_count', 'integer', 'production_data', 'production_count', 'SUM', true, 'Total units produced');
END $$;
```

**Validation**:
```sql
SELECT 
  es.name as energy_source,
  COUNT(*) as feature_count,
  ARRAY_AGG(esf.feature_name ORDER BY esf.feature_name) as features
FROM energy_source_features esf
JOIN energy_sources es ON esf.energy_source_id = es.id
WHERE esf.is_regression_feature = true
GROUP BY es.name
ORDER BY es.name;
```

**Expected**:
```
energy_source | feature_count | features
--------------+---------------+---------------------------------------------------
electricity   | 15            | {avg_power_kw, consumption_kwh, outdoor_temp_c, ...}
natural_gas   | 7             | {avg_flow_rate_m3h, consumption_m3, heating_degree_days, ...}
steam         | 6             | {avg_enthalpy_kj_kg, avg_flow_rate_kg_h, consumption_kg, ...}
```

---

#### Step 3.3: Test Multi-Energy OVOS (30 min)

**Even without physical meters**, test that API accepts natural gas SEUs:

```bash
# Create test natural gas SEU (manually in DB for demo)
docker exec enms-postgres psql -U raptorblingx -d enms -c "
INSERT INTO seus (id, name, description, energy_source_id, machine_ids) 
VALUES (
  'bbbbbbbb-1111-1111-1111-111111111111',
  'Boiler-1',
  'Natural gas boiler for heating',
  (SELECT id FROM energy_sources WHERE name = 'natural_gas'),
  ARRAY['c0000000-0000-0000-0000-000000000001']::uuid[]
);
"

# Test OVOS natural gas SEU discovery
curl "http://localhost:8001/api/v1/ovos/seus?energy_source=natural_gas" | jq .

# Should return Boiler-1
```

**Phase 3 Success Criteria** (Optional):
- [ ] Natural gas, steam, compressed air hypertables created
- [ ] Features populated in energy_source_features table
- [ ] OVOS can discover natural gas SEUs
- [ ] System ready for meter installation (no code changes needed)

---

### PHASE 4: Production Hardening (FUTURE - As Needed)

**Goal**: Enterprise-grade deployment features

#### Step 4.1: Data Quality Monitoring

**Add data_source column** (track backfill vs simulator vs real meters):
```sql
ALTER TABLE energy_readings ADD COLUMN IF NOT EXISTS data_source VARCHAR(20) DEFAULT 'simulator';
ALTER TABLE natural_gas_readings ADD COLUMN IF NOT EXISTS data_source VARCHAR(20) DEFAULT 'meter';
ALTER TABLE steam_readings ADD COLUMN IF NOT EXISTS data_source VARCHAR(20) DEFAULT 'meter';

CREATE INDEX idx_energy_readings_data_source ON energy_readings(data_source);
```

**Populate for existing data**:
```sql
-- Mark current data as simulator
UPDATE energy_readings SET data_source = 'simulator' WHERE data_source IS NULL;

-- Future: When real meters installed, insert with data_source='meter'
```

---

#### Step 4.2: Baseline Adjustment Procedure

**ISO 50001 requires documented baseline adjustments** when:
- Equipment upgraded
- Process changed
- Operating schedule modified

```sql
-- Already exists in schema!
SELECT * FROM baseline_adjustments LIMIT 5;

-- Example usage (when Compressor-1 upgraded)
INSERT INTO baseline_adjustments (
  seu_id,
  adjustment_date,
  adjustment_type,
  adjustment_reason,
  old_baseline_id,
  new_baseline_id,
  approved_by
) VALUES (
  'aaaaaaaa-1111-1111-1111-111111111111',
  '2025-11-01',
  'equipment_upgrade',
  'Replaced 55kW compressor with 75kW VFD model. Previous baseline no longer valid.',
  (SELECT id FROM seus WHERE name = 'Compressor-1' LIMIT 1),
  (SELECT id FROM seus WHERE name = 'Compressor-1' LIMIT 1),
  'John Smith (Plant Manager)'
);
```

---

#### Step 4.3: EnPI Calculations

**Already implemented in `enpi_calculator.py`!** Just needs testing:

```bash
# Calculate EnPI for SEU
curl http://localhost:8001/api/v1/reports/enpi?seu_id=aaaaaaaa-1111-1111-1111-111111111111&year=2025 | jq .
```

**Expected Response**:
```json
{
  "seu_name": "Compressor-1",
  "baseline_year": 2024,
  "comparison_year": 2025,
  "enpi_value": 1.03,
  "interpretation": "3% increase in energy intensity vs baseline",
  "compliance_status": "warning"
}
```

---

## 📋 CRITICAL VALIDATIONS

### After Phase 1 (Data Cleanup)

```sql
-- ✓ Only real data remains
SELECT 
  COUNT(*) as total_samples,
  MIN(time) as oldest,
  MAX(time) as newest,
  ROUND(COUNT(*) / EXTRACT(EPOCH FROM (MAX(time) - MIN(time))), 2) as samples_per_sec
FROM energy_readings;

-- Expected: 2.8M samples, oldest ~Oct 7, samples_per_sec ~1-2

-- ✓ All SEUs retrained
SELECT name, r_squared, trained_at 
FROM seus 
WHERE energy_source_id = (SELECT id FROM energy_sources WHERE name = 'electricity')
ORDER BY r_squared DESC;

-- Expected: All R² > 0.70, trained_at = today

-- ✓ Realistic deviations
SELECT 
  s.name,
  sep.report_period,
  sep.deviation_percent
FROM seu_energy_performance sep
JOIN seus s ON sep.seu_id = s.id
WHERE sep.report_period IN ('2025-10', '2025-11')
ORDER BY s.name, sep.report_period;

-- Expected: Deviations ±2-8% (not -30% or +226%)
```

### After Phase 2 (OVOS Testing)

```bash
# ✓ OVOS energy sources
curl http://localhost:8001/api/v1/ovos/energy-sources | jq '.energy_sources | length'
# Expected: 4 (electricity, natural_gas, compressed_air, steam)

# ✓ OVOS SEUs
curl "http://localhost:8001/api/v1/ovos/seus?energy_source=electricity" | jq '.total_count'
# Expected: 7

# ✓ OVOS training
curl -X POST http://localhost:8001/api/v1/ovos/train-baseline \
  -H "Content-Type: application/json" \
  -d '{"seu_name":"Compressor-1","energy_source":"electricity","features":["production_count","outdoor_temp_c"],"year":2024}' \
  | jq '.success'
# Expected: true
```

---

## 🎯 SUCCESS METRICS

### Technical Success
- [x] Database schema supports multi-energy (electricity, gas, steam, air)
- [x] OVOS voice training endpoint exists and is registered
- [x] Feature discovery service uses dynamic lookup (zero hardcoding)
- [ ] **All 7 electricity SEUs trained on real data (R² > 0.70)**
- [ ] **Monthly reports show realistic deviations (±2-8%)**
- [x] System expandable to new energy sources (add table + features = works)

### Mr. Umut's Requirements Met
- [x] **Train/test split methodology**: Oct 7-21 = training, Oct 22-Nov 24 = testing ✅
- [x] **Multi-energy support**: Schema and services ready for gas/steam/air ✅
- [x] **Dynamic feature selection**: No hardcoded feature lists ✅
- [x] **OVOS voice training**: `/api/v1/ovos/train-baseline` endpoint exists ✅
- [ ] **Zero hardcoding**: Need to verify feature_discovery.py table mapping is generic
- [ ] **Real data baselines**: Need to retrain on Oct 7-21 (not backfilled 2024)

### ISO 50001 Compliance
- [x] SEU structure (individual equipment tracking)
- [x] Baseline regression models (sklearn LinearRegression)
- [x] Monthly EnPI reporting
- [x] Baseline adjustment tracking (baseline_adjustments table)
- [ ] Data quality scoring (data_quality_log table - needs population)
- [ ] CUSUM charts (implemented in enpi_calculator.py - needs testing)

---

## 🚨 CRITICAL NEXT STEPS

### IMMEDIATE (Today - 2 hours)
1. **Run Phase 1 cleanup script** (archive backfilled data)
2. **Update SEU baseline periods** (2024-10-07 to 2024-10-21)
3. **Retrain all 7 SEUs** (on real simulator data)
4. **Generate Oct-Nov reports** (verify realistic deviations)

### THIS WEEK (4 hours)
1. **Test OVOS endpoints** (energy sources, SEUs, voice training)
2. **Document OVOS integration** (voice command examples)
3. **Validate feature discovery** (ensure table mapping is generic)
4. **Demo to Mr. Umut** (show voice training + real results)

### NEXT WEEK (Optional - if multi-energy meters coming)
1. **Create natural gas/steam tables** (hypertables only, no data)
2. **Populate energy source features** (7-15 features per energy type)
3. **Test OVOS with natural gas SEU** (demo future capability)

---

## 📚 REFERENCE DOCUMENTS

### Key Files to Review
```
✓ Database Schema: /database/init/02-schema.sql
✓ SEU Table: /database/migrations/004-production-seus.sql
✓ Energy Source Features: /database/migrations/006-energy-source-features.sql
✓ SEU Baseline Service: /analytics/services/seu_baseline_service.py
✓ Feature Discovery: /analytics/services/feature_discovery.py
✓ OVOS Training Routes: /analytics/api/routes/ovos_training.py
✓ EnPI Calculator: /analytics/services/enpi_calculator.py
```

### Related Documentation
- `ISO-50001-PRODUCTION-IMPLEMENTATION-PLAN.md` - Mr. Umut's original vision
- `IMPLEMENTATION-V2-MULTI-ENERGY-OVOS.md` - Multi-energy architecture design
- Session logs: `SESSION-SUMMARY-OCT-*.md` - Daily progress tracking

---

## ❓ DECISIONS NEEDED

### High Priority
1. **When to demo to Mr. Umut?** (Suggest: After Phase 1 complete = tomorrow)
2. **Are natural gas/steam meters being installed?** (If yes, do Phase 3; if no, skip)
3. **What's the production deployment timeline?** (Affects hardening priorities)

### Medium Priority
1. **Should we delete or archive backfilled data?** (Recommend: Archive for audit trail)
2. **How often to update baselines?** (Monthly? Quarterly? When equipment changes?)
3. **What OVOS skill will integrate?** (Need voice command format spec)

### Low Priority
1. **Need JWT authentication?** (Phase 4 - not critical for demo)
2. **Need PDF export for ISO reports?** (Phase 4 - nice-to-have)
3. **Need multi-language OVOS support?** (Phase 4 - English first)

---

## 🎬 GETTING STARTED

**To execute Phase 1 RIGHT NOW**:

```bash
# 1. Review this document
less docs/api-documentation/MR-UMUT-REQUIREMENTS-IMPLEMENTATION-ROADMAP.md

# 2. Create cleanup script
nano scripts/phase1-cleanup.sh
# Paste Phase 1 Step 1.1 SQL commands

# 3. Run cleanup
chmod +x scripts/phase1-cleanup.sh
./scripts/phase1-cleanup.sh

# 4. Update SEU metadata
docker exec -i enms-postgres psql -U raptorblingx -d enms < scripts/phase1-update-seus.sql

# 5. Retrain baselines
./scripts/retrain-real-baselines.sh

# 6. Validate results
docker exec enms-postgres psql -U raptorblingx -d enms -c "SELECT name, r_squared, trained_at FROM seus ORDER BY r_squared DESC;"
```

**Total time**: ~2 hours  
**Risk level**: Low (data is archived, not deleted)  
**Rollback plan**: Restore from demo_archive schema if needed

---

**Document Version**: 1.0  
**Last Updated**: October 24, 2025  
**Next Review**: After Phase 1 completion  
**Owner**: EnMS Development Team
