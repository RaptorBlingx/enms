# EnMS Implementation V2 - Multi-Energy & OVOS Voice Integration
**Date**: October 24, 2025  
**Status**: Planning Phase  
**Priority**: Critical - Aligns with Mr. Umut's Original Vision

---

## 🎯 Executive Summary

### What We Built (V1) vs What Mr. Umut Actually Wants (V2)

| Aspect | ❌ V1 (Current) | ✅ V2 (Target) |
|--------|-----------------|----------------|
| **Architecture** | 7 machines = 7 SEUs (electricity only) | 7 machines × N energies = dynamic SEUs |
| **Feature Selection** | Partially hardcoded by machine type | User/OVOS specifies ANY features |
| **Energy Sources** | Only `energy_readings` table | Expandable: electricity, gas, steam, air |
| **Data Usage** | Trained on backfilled fake data (2024) | Train on real simulator data (Oct 2024+) |
| **OVOS Integration** | ❌ Missing voice training endpoint | ✅ "Train baseline for X using Y features" |
| **Expandability** | Requires code changes for new energy | Add row to table, zero code changes |

---

## 📊 Critical Data Reality Check

### Current Data Inventory (The Truth)

1. **Backfilled 2024 Data** (Created by AI, NOT REAL):
   - Period: Jan 1 - Dec 31, 2024
   - Frequency: 24 hourly samples/day
   - Purpose: Historical baseline for training
   - **Status**: ⚠️ Artificial data with intentional patterns

2. **Backfilled Jan-Sep 2025 Data** (Created by AI, NOT REAL):
   - Period: Jan 1 - Sep 30, 2025
   - Frequency: 24 hourly samples/day
   - Purpose: Performance period for comparison
   - **Status**: ⚠️ Artificial data with 2-4% efficiency improvement baked in

3. **Real Simulator Data** (ONLY REAL DATA):
   - Period: ~Oct 7-24, 2025 (estimated, needs verification)
   - Frequency: **1-second resolution** (141 samples/minute)
   - Volume: 2.5-2.8 million records in <3 weeks
   - **Status**: ✅ True operational data from simulator

### The Problem with V1 Analysis

All current EnPI reports, baselines, and deviations are based on:
- **Training**: Fake 2024 hourly data
- **Comparison**: Fake 2025 hourly data
- **Result**: The -30% compressor and +226% HVAC deviations are **artifacts of inconsistent backfill scripts**, not real insights!

**V2 Solution**: Use only real simulator data (Oct 7-24) for all analysis.

---

## 🏗️ V2 Architecture - Mr. Umut's Multi-Energy Vision

### 1. Multi-Energy SEU Structure

**NOT**: One machine = One SEU

**BUT**: One machine × N energy sources = N SEUs

#### Example: Compressor-1 Multi-Energy Expansion

```
Compressor-1 Machine
│
├─ SEU: Compressor-1-Electricity
│  ├─ Energy Source: electricity
│  ├─ Data Table: energy_readings
│  ├─ Features: production_count, outdoor_temp_c, motor_load
│  ├─ Baseline Formula: kWh = f(production, temp)
│  └─ Status: ✅ EXISTS (Current V1)
│
├─ SEU: Compressor-1-Compressed-Air-Production [FUTURE]
│  ├─ Energy Source: compressed_air
│  ├─ Data Table: compressed_air_readings
│  ├─ Features: electricity_kwh, pressure_bar, ambient_temp
│  ├─ Baseline Formula: Nm³ = f(electricity, pressure)
│  └─ Status: 🔴 FUTURE (V2 enables this)
│
└─ SEU: Compressor-1-Cooling-Water [FUTURE]
   ├─ Energy Source: cooling_water
   ├─ Data Table: water_readings
   ├─ Features: flow_rate, inlet_temp, ambient_temp
   ├─ Baseline Formula: m³ = f(cooling_load, ambient)
   └─ Status: 🔴 FUTURE (V2 enables this)
```

#### Example: Boiler Multi-Energy (Future Facility Expansion)

```
Boiler-1 Machine [WHEN INSTALLED]
│
├─ SEU: Boiler-1-Natural-Gas
│  ├─ Energy Source: natural_gas
│  ├─ Data Table: natural_gas_readings
│  ├─ Features: outdoor_temp_c, heating_degree_days, wind_speed
│  ├─ Baseline Formula: m³ = f(outdoor_temp, HDD, wind)
│  └─ Status: 🔴 FUTURE (V2 schema ready)
│
└─ SEU: Boiler-1-Electricity (for controls/pumps)
   ├─ Energy Source: electricity
   ├─ Data Table: energy_readings
   ├─ Features: operating_hours, outdoor_temp_c
   ├─ Baseline Formula: kWh = f(hours, temp)
   └─ Status: 🔴 FUTURE (V2 enables this)
```

**Key Insight**: Different energy sources have **different physics** → different regression variables.

---

### 2. Dynamic Feature Selection (ZERO Hardcoding)

#### ❌ V1 Approach (Partially Hardcoded)

```python
# OLD - Still has implicit assumptions
def train_seu_baseline(seu_id, features):
    # Feature discovery is dynamic ✅
    # But table selection is still partially hardcoded
    data = await get_daily_aggregates(seu_id, features)
    # Always queries: energy_readings + production_data + environmental_data
```

**Problem**: When natural gas is added, code must be modified to query `natural_gas_readings`.

#### ✅ V2 Approach (Fully Dynamic)

```python
# NEW - Completely data-driven
async def train_seu_baseline(seu_id: UUID, features: List[str]):
    # 1. Get SEU metadata
    seu = await db.fetchrow("SELECT * FROM seus WHERE id = $1", seu_id)
    
    # 2. Get energy source metadata
    energy_source = await db.fetchrow(
        "SELECT * FROM energy_sources WHERE id = $1", 
        seu['energy_source_id']
    )
    
    # 3. Dynamically determine source table
    table_name = get_energy_table(energy_source['name'])
    # electricity → energy_readings
    # natural_gas → natural_gas_readings
    # steam → steam_readings
    
    # 4. Build query dynamically from energy_source_features table
    query = await feature_discovery.build_query(
        energy_source_id=seu['energy_source_id'],
        features=features,
        source_table=table_name
    )
    
    # 5. Train regression (generic, works for any energy type)
    return await train_regression(query_results)
```

**Key**: No `if energy_source == 'electricity'` logic anywhere!

---

### 3. OVOS Voice Training Integration ⭐

Mr. Umut's primary use case: **Voice-controlled baseline training**.

#### Voice Command Examples

**Example 1: Electricity (Current)**
```
User Voice Command:
"Train baseline for electricity Compressor-1 using production count and outdoor temperature for year 2024"

OVOS Parsing:
├─ Energy Source: "electricity"
├─ SEU Name: "Compressor-1"
├─ Features: ["production_count", "outdoor_temperature"]
└─ Year: 2024

API Call:
POST /api/v1/voice/train-baseline
{
  "energy_source": "electricity",
  "seu_name": "Compressor-1",
  "features": ["production_count", "outdoor_temp_c"],
  "year": 2024
}

Voice Response:
"Compressor-1 electricity baseline trained successfully. 
R-squared 0.87. 
Formula: Energy equals 212 plus 0.007 times production count plus 0.073 times outdoor temperature."
```

**Example 2: Natural Gas (Future)**
```
User Voice Command:
"Train baseline for natural gas Boiler-1 using outdoor temperature and heating degree days for year 2024"

OVOS Parsing:
├─ Energy Source: "natural_gas"
├─ SEU Name: "Boiler-1"
├─ Features: ["outdoor_temperature", "heating_degree_days"]
└─ Year: 2024

API Call:
POST /api/v1/voice/train-baseline
{
  "energy_source": "natural_gas",
  "seu_name": "Boiler-1",
  "features": ["outdoor_temp_c", "heating_degree_days"],
  "year": 2024
}

Voice Response:
"Boiler-1 natural gas baseline trained. 
R-squared 0.92. 
Formula: Gas consumption equals 120 plus 3.2 times outdoor temperature plus 0.8 times heating degree days."
```

**Example 3: Multi-Variable Query (Future)**
```
User Voice Command:
"Train baseline for compressed air Compressor-1 using electricity, pressure, and ambient temperature for 2024"

OVOS Parsing:
├─ Energy Source: "compressed_air"
├─ SEU Name: "Compressor-1"
├─ Features: ["electricity_kwh", "pressure_bar", "ambient_temp_c"]
└─ Year: 2024

API Call:
POST /api/v1/voice/train-baseline
{
  "energy_source": "compressed_air",
  "seu_name": "Compressor-1",
  "features": ["electricity_kwh", "pressure_bar", "ambient_temp_c"],
  "year": 2024
}

Voice Response:
"Compressor-1 compressed air baseline trained. 
R-squared 0.94. 
Formula: Air production equals 45 plus 0.12 times electricity plus 2.3 times pressure plus 0.5 times ambient temperature."
```

---

### 4. Database Schema V2 (Future-Proof Expandability)

#### Energy Sources Table (Already Exists ✅)

```sql
-- Existing table
CREATE TABLE energy_sources (
    id UUID PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,  -- 'electricity', 'natural_gas', etc.
    unit VARCHAR(20) NOT NULL,         -- 'kWh', 'm³', 'kg', 'Nm³'
    cost_per_unit DECIMAL(10,4),
    carbon_intensity DECIMAL(10,6),    -- kg CO2 per unit
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Current data
INSERT INTO energy_sources VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'electricity', 'kWh', 0.12, 0.45),
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'natural_gas', 'm³', 0.50, 2.02),
('cccccccc-cccc-cccc-cccc-cccccccccccc', 'steam', 'kg', 0.08, 0.15),
('dddddddd-dddd-dddd-dddd-dddddddddddd', 'compressed_air', 'Nm³', 0.03, 0.12);
```

#### Multi-Energy Readings Tables (V2 Addition)

**Electricity** (Already Exists ✅)
```sql
CREATE TABLE energy_readings (
    time TIMESTAMPTZ NOT NULL,
    machine_id UUID NOT NULL REFERENCES machines(id),
    energy_kwh DECIMAL(12,4),
    power_kw DECIMAL(10,3),
    voltage_v DECIMAL(8,2),
    current_a DECIMAL(10,3),
    power_factor DECIMAL(5,4),
    PRIMARY KEY (time, machine_id)
);

SELECT create_hypertable('energy_readings', 'time');
```

**Natural Gas** (NEW - V2)
```sql
CREATE TABLE natural_gas_readings (
    time TIMESTAMPTZ NOT NULL,
    machine_id UUID NOT NULL REFERENCES machines(id),
    flow_rate_m3h DECIMAL(10,2),      -- Instantaneous flow
    consumption_m3 DECIMAL(12,4),     -- Cumulative for interval
    pressure_bar DECIMAL(8,2),        -- Line pressure
    temperature_c DECIMAL(6,2),       -- Gas temperature
    PRIMARY KEY (time, machine_id)
);

SELECT create_hypertable('natural_gas_readings', 'time');
CREATE INDEX ON natural_gas_readings (machine_id, time DESC);
```

**Steam** (NEW - V2)
```sql
CREATE TABLE steam_readings (
    time TIMESTAMPTZ NOT NULL,
    machine_id UUID NOT NULL REFERENCES machines(id),
    flow_rate_kg_h DECIMAL(10,2),     -- Mass flow rate
    consumption_kg DECIMAL(12,4),     -- Cumulative for interval
    pressure_bar DECIMAL(8,2),        -- Steam pressure
    temperature_c DECIMAL(6,2),       -- Steam temperature
    enthalpy_kj_kg DECIMAL(10,3),     -- Specific enthalpy
    PRIMARY KEY (time, machine_id)
);

SELECT create_hypertable('steam_readings', 'time');
CREATE INDEX ON steam_readings (machine_id, time DESC);
```

**Compressed Air (End Use)** (NEW - V2)
```sql
CREATE TABLE compressed_air_end_use_readings (
    time TIMESTAMPTZ NOT NULL,
    machine_id UUID NOT NULL REFERENCES machines(id),
    flow_rate_m3h DECIMAL(10,2),      -- Volumetric flow
    consumption_m3 DECIMAL(12,4),     -- Normalized volume (Nm³)
    pressure_bar DECIMAL(8,2),        -- Delivery pressure
    dewpoint_c DECIMAL(6,2),          -- Air quality indicator
    PRIMARY KEY (time, machine_id)
);

SELECT create_hypertable('compressed_air_end_use_readings', 'time');
CREATE INDEX ON compressed_air_end_use_readings (machine_id, time DESC);
```

#### SEUs Table (Already Multi-Energy Ready ✅)

```sql
-- Existing table structure (already correct!)
CREATE TABLE seus (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    energy_source_id UUID NOT NULL REFERENCES energy_sources(id),  -- ✅ Links to any energy
    machine_ids UUID[] NOT NULL,
    baseline_year INT,
    baseline_start_date DATE,
    baseline_end_date DATE,
    regression_coefficients JSONB,
    intercept DECIMAL(15,6),
    feature_columns TEXT[],
    r_squared DECIMAL(8,6),
    rmse DECIMAL(12,4),
    mae DECIMAL(12,4),
    trained_at TIMESTAMPTZ,
    trained_by VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Key**: One machine can have multiple SEUs (one per energy source).

---

## 🚀 V2 Implementation Plan

### Phase 1: Data Foundation (Immediate - Today)

#### 1.1 Verify Real Simulator Data Range
```sql
-- Find exact range of real simulator data
SELECT 
  MIN(time) as first_real_data,
  MAX(time) as last_real_data,
  COUNT(*) as total_samples,
  COUNT(DISTINCT machine_id) as machines,
  COUNT(*) / NULLIF(EXTRACT(EPOCH FROM (MAX(time) - MIN(time))), 0) as avg_samples_per_second
FROM energy_readings
WHERE time >= '2024-10-01';

-- Expected result: Oct 7-24, ~2.5M samples, ~141/min = 2.35/sec
```

#### 1.2 Flag or Separate Backfilled Data
**Option A**: Add flag to distinguish real vs simulated
```sql
-- Add column to mark data source
ALTER TABLE energy_readings ADD COLUMN IF NOT EXISTS data_source VARCHAR(20) DEFAULT 'simulator';
ALTER TABLE production_data ADD COLUMN IF NOT EXISTS data_source VARCHAR(20) DEFAULT 'simulator';
ALTER TABLE environmental_data ADD COLUMN IF NOT EXISTS data_source VARCHAR(20) DEFAULT 'simulator';

-- Mark backfilled data
UPDATE energy_readings SET data_source = 'backfill' WHERE time < '2024-10-07';
UPDATE production_data SET data_source = 'backfill' WHERE time < '2024-10-07';
UPDATE environmental_data SET data_source = 'backfill' WHERE time < '2024-10-07';

-- Create indexes
CREATE INDEX ON energy_readings (data_source);
CREATE INDEX ON production_data (data_source);
CREATE INDEX ON environmental_data (data_source);
```

**Option B**: Keep as-is, filter in queries
```python
# Always filter in application code
REAL_DATA_START = datetime(2024, 10, 7)

async def get_real_data_only(table, start, end):
    return await db.fetch(f"""
        SELECT * FROM {table}
        WHERE time >= $1 AND time <= $2
          AND time >= '{REAL_DATA_START}'  -- Force real data only
    """, start, end)
```

**Recommendation**: Option A (explicit flag) for clarity.

#### 1.3 Retrain All Baselines on Real Data
```python
# Use Oct 7-21 as baseline (14 days of real data)
# Oct 22-24 as performance comparison (3 days)

BASELINE_START = "2024-10-07"
BASELINE_END = "2024-10-21"

for seu in all_seus:
    await train_baseline(
        seu_id=seu.id,
        baseline_year=2024,
        start_date=BASELINE_START,
        end_date=BASELINE_END,
        features=seu.default_features
    )
```

---

### Phase 2: OVOS Voice Integration (This Week)

#### 2.1 Create Voice Training Endpoint

**New File**: `analytics/api/routes/ovos_training.py`

```python
"""
EnMS Analytics Service - OVOS Voice Training Endpoint
=====================================================
Voice-controlled baseline training for Mr. Umut's OVOS integration.

Voice Command Examples:
- "Train baseline for electricity Compressor-1 using production and temp for 2024"
- "Train baseline for natural gas Boiler-1 using outdoor temp and degree days for 2024"
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import date
from uuid import UUID

router = APIRouter()

@router.post("/voice/train-baseline", tags=["OVOS Integration"])
async def voice_train_baseline(
    energy_source: str,        # "electricity", "natural_gas", "steam", etc.
    seu_name: str,             # "Compressor-1", "HVAC-Main", etc.
    features: List[str],       # ["production_count", "outdoor_temp_c"]
    year: int,                 # 2024
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """
    OVOS voice command endpoint for baseline training.
    
    Example Voice Command:
    "Train baseline for electricity Compressor-1 using production count and outdoor temperature for year 2024"
    
    OVOS Parses Into:
    {
        "energy_source": "electricity",
        "seu_name": "Compressor-1",
        "features": ["production_count", "outdoor_temp_c"],
        "year": 2024
    }
    
    Returns:
        Voice-friendly response with formula in natural language
    """
    
    # 1. Find energy source
    energy_source_record = await db.fetchrow(
        "SELECT id, name, unit FROM energy_sources WHERE LOWER(name) = LOWER($1)",
        energy_source
    )
    
    if not energy_source_record:
        available = await db.fetch("SELECT name FROM energy_sources")
        available_names = [r['name'] for r in available]
        raise HTTPException(
            status_code=404,
            detail=f"Energy source '{energy_source}' not found. Available: {available_names}"
        )
    
    # 2. Find SEU by name + energy source
    seu = await db.fetchrow("""
        SELECT s.* 
        FROM seus s
        WHERE LOWER(s.name) = LOWER($1)
          AND s.energy_source_id = $2
    """, seu_name, energy_source_record['id'])
    
    if not seu:
        raise HTTPException(
            status_code=404,
            detail=f"SEU '{seu_name}' not found for energy source '{energy_source}'"
        )
    
    # 3. Validate features exist for this energy source
    is_valid, valid_features, invalid_features = await feature_discovery.validate_features(
        energy_source_id=energy_source_record['id'],
        requested_features=features
    )
    
    if not is_valid:
        available = await feature_discovery.get_available_features(energy_source_record['id'])
        available_names = [f.feature_name for f in available]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid features: {invalid_features}. Available for {energy_source}: {available_names}"
        )
    
    # 4. Train baseline (using existing service)
    training_result = await seu_baseline_service.train_baseline(
        TrainBaselineRequest(
            seu_id=seu['id'],
            baseline_year=year,
            start_date=start_date or date(year, 1, 1),
            end_date=end_date or date(year, 12, 31),
            features=features
        )
    )
    
    # 5. Format response for voice output
    voice_response = format_voice_friendly(
        seu_name=seu_name,
        energy_source=energy_source,
        energy_unit=energy_source_record['unit'],
        result=training_result
    )
    
    return {
        "success": True,
        "seu_id": str(seu['id']),
        "seu_name": seu_name,
        "energy_source": energy_source,
        "energy_unit": energy_source_record['unit'],
        "voice_response": voice_response,
        "formula_text": training_result.formula,
        "coefficients": training_result.coefficients,
        "intercept": training_result.intercept,
        "r_squared": training_result.r_squared,
        "rmse": training_result.rmse,
        "samples_count": training_result.samples_count,
        "training_period": training_result.training_period
    }


def format_voice_friendly(seu_name: str, energy_source: str, energy_unit: str, result) -> str:
    """
    Convert training result to natural language for OVOS voice output.
    
    Example Output:
    "Compressor-1 electricity baseline trained successfully. 
    R-squared 0.87. 
    Formula: Energy equals 212 plus 0.007 times production count plus 0.073 times outdoor temperature."
    """
    
    # Format R-squared as percentage
    r2_percent = round(result.r_squared * 100, 1)
    
    # Humanize formula
    formula_parts = [f"{result.intercept:.2f}"]
    
    for feature, coef in result.coefficients.items():
        # Clean feature name for speech
        feature_clean = feature.replace('_', ' ').replace('avg ', '')
        
        if coef >= 0:
            formula_parts.append(f"plus {abs(coef):.3f} times {feature_clean}")
        else:
            formula_parts.append(f"minus {abs(coef):.3f} times {feature_clean}")
    
    formula_speech = " ".join(formula_parts)
    
    # Build complete voice response
    response = (
        f"{seu_name} {energy_source} baseline trained successfully. "
        f"Model explains {r2_percent} percent of variance. "
        f"Formula: {energy_unit} equals {formula_speech}."
    )
    
    return response


@router.get("/voice/available-features", tags=["OVOS Integration"])
async def voice_get_available_features(energy_source: str):
    """
    Get available features for an energy source (for OVOS to suggest).
    
    Voice Command: "What features are available for electricity?"
    
    Returns: List of feature names with descriptions
    """
    
    # Find energy source
    energy_source_record = await db.fetchrow(
        "SELECT id, name FROM energy_sources WHERE LOWER(name) = LOWER($1)",
        energy_source
    )
    
    if not energy_source_record:
        available = await db.fetch("SELECT name FROM energy_sources")
        available_names = [r['name'] for r in available]
        raise HTTPException(
            status_code=404,
            detail=f"Energy source '{energy_source}' not found. Available: {available_names}"
        )
    
    # Get features
    features = await feature_discovery.get_available_features(
        energy_source_id=energy_source_record['id'],
        regression_only=True
    )
    
    # Format for voice
    feature_list = [
        {
            "name": f.feature_name,
            "description": f.description or f.feature_name.replace('_', ' '),
            "data_type": f.data_type,
            "source": f.source_table
        }
        for f in features
    ]
    
    voice_response = (
        f"Available features for {energy_source}: "
        f"{', '.join([f['name'].replace('_', ' ') for f in feature_list])}"
    )
    
    return {
        "success": True,
        "energy_source": energy_source,
        "features": feature_list,
        "voice_response": voice_response
    }


@router.get("/voice/available-energy-sources", tags=["OVOS Integration"])
async def voice_get_energy_sources():
    """
    Get list of available energy sources for OVOS.
    
    Voice Command: "What energy sources can I train baselines for?"
    """
    
    sources = await db.fetch("SELECT name, unit FROM energy_sources ORDER BY name")
    
    source_list = [{"name": s['name'], "unit": s['unit']} for s in sources]
    
    voice_response = (
        f"Available energy sources: "
        f"{', '.join([s['name'] for s in source_list])}"
    )
    
    return {
        "success": True,
        "energy_sources": source_list,
        "voice_response": voice_response
    }
```

**Register in main.py**:
```python
from api.routes import ovos_training

app.include_router(ovos_training.router, prefix="/api/v1", tags=["OVOS"])
```

---

### Phase 3: Generic Multi-Energy Data Fetching (Next Week)

#### 3.1 Energy Table Mapping Service

**New File**: `analytics/services/energy_table_mapper.py`

```python
"""
EnMS Analytics Service - Energy Table Mapper
============================================
Maps energy sources to their respective database tables.
Enables expansion to natural gas, steam, compressed air with zero code changes.
"""

from typing import Dict, Optional
from uuid import UUID

# Static mapping (can be moved to database if needed)
ENERGY_TABLE_MAP = {
    'electricity': 'energy_readings',
    'natural_gas': 'natural_gas_readings',
    'steam': 'steam_readings',
    'compressed_air': 'compressed_air_end_use_readings',
    'water': 'water_readings',
    'fuel_oil': 'fuel_oil_readings'
}

# Column mappings for each energy type
ENERGY_COLUMN_MAP = {
    'electricity': {
        'consumption': 'energy_kwh',
        'rate': 'power_kw',
        'quality': 'power_factor'
    },
    'natural_gas': {
        'consumption': 'consumption_m3',
        'rate': 'flow_rate_m3h',
        'quality': 'pressure_bar'
    },
    'steam': {
        'consumption': 'consumption_kg',
        'rate': 'flow_rate_kg_h',
        'quality': 'enthalpy_kj_kg'
    },
    'compressed_air': {
        'consumption': 'consumption_m3',
        'rate': 'flow_rate_m3h',
        'quality': 'pressure_bar'
    }
}


async def get_energy_table_name(energy_source_id: UUID) -> str:
    """
    Get database table name for an energy source.
    
    Args:
        energy_source_id: UUID of energy source
        
    Returns:
        Table name (e.g., 'energy_readings', 'natural_gas_readings')
    """
    query = "SELECT name FROM energy_sources WHERE id = $1"
    
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(query, energy_source_id)
    
    if not row:
        raise ValueError(f"Energy source not found: {energy_source_id}")
    
    source_name = row['name']
    
    # Map to table name
    table_name = ENERGY_TABLE_MAP.get(source_name)
    
    if not table_name:
        # Fallback: assume table is named {source_name}_readings
        table_name = f"{source_name}_readings"
    
    return table_name


async def get_energy_columns(energy_source_id: UUID) -> Dict[str, str]:
    """
    Get column mapping for an energy source.
    
    Returns:
        Dict with keys: consumption, rate, quality
    """
    query = "SELECT name FROM energy_sources WHERE id = $1"
    
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(query, energy_source_id)
    
    if not row:
        raise ValueError(f"Energy source not found: {energy_source_id}")
    
    source_name = row['name']
    
    return ENERGY_COLUMN_MAP.get(source_name, {
        'consumption': 'consumption',
        'rate': 'rate',
        'quality': 'quality'
    })
```

#### 3.2 Update Feature Discovery to Use Generic Tables

**Modify**: `analytics/services/feature_discovery.py`

```python
# Add at top
from services.energy_table_mapper import get_energy_table_name, get_energy_columns

async def build_daily_aggregation_query(
    self,
    energy_source_id: UUID,
    machine_ids: List[UUID],
    requested_features: List[str],
    start_date: str,
    end_date: str
) -> str:
    """
    Build dynamic SQL query to aggregate features by day.
    NOW WORKS FOR ANY ENERGY SOURCE (electricity, gas, steam, etc.)
    """
    
    # Get primary energy table dynamically
    primary_table = await get_energy_table_name(energy_source_id)
    primary_columns = await get_energy_columns(energy_source_id)
    
    logger.info(
        f"[FEATURE-DISCOVERY] Building query for energy source {energy_source_id}: "
        f"table={primary_table}, consumption_col={primary_columns['consumption']}"
    )
    
    # Get ALL features for the energy source
    all_features_query = """
        SELECT feature_name, source_table, source_column, aggregation_function
        FROM energy_source_features
        WHERE energy_source_id = $1
          AND source_table = $2
        LIMIT 1
    """
    async with db.pool.acquire() as conn:
        primary_feature = await conn.fetchrow(
            all_features_query, 
            energy_source_id,
            primary_table  # Use dynamic table name
        )
    
    if not primary_feature:
        raise ValueError(
            f"No primary energy table features found for energy_source_id={energy_source_id}, "
            f"table={primary_table}"
        )
    
    # Rest of the query building logic remains the same
    # Just uses primary_table and primary_columns['consumption'] instead of hardcoded values
    
    primary_alias = self._get_table_alias(primary_table)
    primary_consumption_feature = primary_feature['feature_name']
    
    # Continue with existing CTE building logic...
    # (rest of function unchanged)
```

---

### Phase 4: Create Future Energy Tables (Next Week)

#### 4.1 Migration Script

**New File**: `database/migrations/007-multi-energy-tables.sql`

```sql
-- =====================================================
-- EnMS V2: Multi-Energy Tables Migration
-- =====================================================
-- Adds support for natural gas, steam, and compressed air
-- Tables created but empty - ready for future meters

-- Natural Gas Readings (for boilers, heaters, furnaces)
-- =====================================================
CREATE TABLE IF NOT EXISTS natural_gas_readings (
    time TIMESTAMPTZ NOT NULL,
    machine_id UUID NOT NULL REFERENCES machines(id),
    flow_rate_m3h DECIMAL(10,2),      -- Instantaneous flow (m³/hour)
    consumption_m3 DECIMAL(12,4),     -- Interval consumption (m³)
    pressure_bar DECIMAL(8,2),        -- Line pressure (bar)
    temperature_c DECIMAL(6,2),       -- Gas temperature (°C)
    calorific_value_mj_m3 DECIMAL(8,3) DEFAULT 38.5,  -- Heating value
    PRIMARY KEY (time, machine_id)
);

SELECT create_hypertable('natural_gas_readings', 'time', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_natural_gas_machine_time ON natural_gas_readings (machine_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_natural_gas_day ON natural_gas_readings (time_bucket('1 day', time), machine_id);

COMMENT ON TABLE natural_gas_readings IS 'Natural gas consumption readings for boilers, heaters, and gas-powered equipment';
COMMENT ON COLUMN natural_gas_readings.calorific_value_mj_m3 IS 'Gross calorific value for energy content calculation';


-- Steam Readings (for steam-heated processes)
-- =====================================================
CREATE TABLE IF NOT EXISTS steam_readings (
    time TIMESTAMPTZ NOT NULL,
    machine_id UUID NOT NULL REFERENCES machines(id),
    flow_rate_kg_h DECIMAL(10,2),     -- Mass flow rate (kg/hour)
    consumption_kg DECIMAL(12,4),     -- Interval consumption (kg)
    pressure_bar DECIMAL(8,2),        -- Steam pressure (bar)
    temperature_c DECIMAL(6,2),       -- Steam temperature (°C)
    enthalpy_kj_kg DECIMAL(10,3),     -- Specific enthalpy (kJ/kg)
    quality_percent DECIMAL(5,2),     -- Steam quality/dryness (%)
    PRIMARY KEY (time, machine_id)
);

SELECT create_hypertable('steam_readings', 'time', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_steam_machine_time ON steam_readings (machine_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_steam_day ON steam_readings (time_bucket('1 day', time), machine_id);

COMMENT ON TABLE steam_readings IS 'Steam consumption for heating, drying, and process applications';
COMMENT ON COLUMN steam_readings.enthalpy_kj_kg IS 'Specific enthalpy for thermal energy calculation';


-- Compressed Air End Use Readings
-- =====================================================
CREATE TABLE IF NOT EXISTS compressed_air_end_use_readings (
    time TIMESTAMPTZ NOT NULL,
    machine_id UUID NOT NULL REFERENCES machines(id),
    flow_rate_m3h DECIMAL(10,2),      -- Volumetric flow (m³/hour actual)
    consumption_m3 DECIMAL(12,4),     -- Normalized volume (Nm³ at STP)
    pressure_bar DECIMAL(8,2),        -- Delivery pressure (bar gauge)
    dewpoint_c DECIMAL(6,2),          -- Dewpoint (air quality indicator)
    PRIMARY KEY (time, machine_id)
);

SELECT create_hypertable('compressed_air_end_use_readings', 'time', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_compressed_air_machine_time ON compressed_air_end_use_readings (machine_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_compressed_air_day ON compressed_air_end_use_readings (time_bucket('1 day', time), machine_id);

COMMENT ON TABLE compressed_air_end_use_readings IS 'Compressed air consumption at end-use points (pneumatic tools, actuators, etc.)';
COMMENT ON COLUMN compressed_air_end_use_readings.consumption_m3 IS 'Normalized to standard conditions (0°C, 1.013 bar)';


-- Update energy_sources table with new entries
-- =====================================================
INSERT INTO energy_sources (id, name, unit, cost_per_unit, carbon_intensity, created_at)
VALUES 
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'natural_gas', 'm³', 0.50, 2.02, NOW()),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', 'steam', 'kg', 0.08, 0.15, NOW()),
    ('dddddddd-dddd-dddd-dddd-dddddddddddd', 'compressed_air', 'Nm³', 0.03, 0.12, NOW())
ON CONFLICT (name) DO NOTHING;


-- Add features for natural gas
-- =====================================================
INSERT INTO energy_source_features (energy_source_id, feature_name, data_type, source_table, source_column, aggregation_function, description, is_regression_feature)
VALUES 
    -- Natural gas features
    ((SELECT id FROM energy_sources WHERE name='natural_gas'), 'consumption_m3', 'numeric', 'natural_gas_readings', 'consumption_m3', 'SUM', 'Total natural gas consumption (m³)', false),
    ((SELECT id FROM energy_sources WHERE name='natural_gas'), 'avg_flow_rate_m3h', 'numeric', 'natural_gas_readings', 'flow_rate_m3h', 'AVG', 'Average gas flow rate', true),
    ((SELECT id FROM energy_sources WHERE name='natural_gas'), 'avg_pressure_bar', 'numeric', 'natural_gas_readings', 'pressure_bar', 'AVG', 'Average line pressure', true),
    ((SELECT id FROM energy_sources WHERE name='natural_gas'), 'outdoor_temp_c', 'numeric', 'environmental_data', 'outdoor_temp_c', 'AVG', 'Average outdoor temperature', true),
    ((SELECT id FROM energy_sources WHERE name='natural_gas'), 'heating_degree_days', 'numeric', 'environmental_data', 'outdoor_temp_c', 'CUSTOM', 'Heating degree days (18°C base)', true),
    
    -- Steam features
    ((SELECT id FROM energy_sources WHERE name='steam'), 'consumption_kg', 'numeric', 'steam_readings', 'consumption_kg', 'SUM', 'Total steam consumption (kg)', false),
    ((SELECT id FROM energy_sources WHERE name='steam'), 'avg_flow_rate_kg_h', 'numeric', 'steam_readings', 'flow_rate_kg_h', 'AVG', 'Average steam flow rate', true),
    ((SELECT id FROM energy_sources WHERE name='steam'), 'avg_pressure_bar', 'numeric', 'steam_readings', 'pressure_bar', 'AVG', 'Average steam pressure', true),
    ((SELECT id FROM energy_sources WHERE name='steam'), 'avg_enthalpy_kj_kg', 'numeric', 'steam_readings', 'enthalpy_kj_kg', 'AVG', 'Average specific enthalpy', true),
    
    -- Compressed air features
    ((SELECT id FROM energy_sources WHERE name='compressed_air'), 'consumption_m3', 'numeric', 'compressed_air_end_use_readings', 'consumption_m3', 'SUM', 'Total compressed air consumption (Nm³)', false),
    ((SELECT id FROM energy_sources WHERE name='compressed_air'), 'avg_flow_rate_m3h', 'numeric', 'compressed_air_end_use_readings', 'flow_rate_m3h', 'AVG', 'Average air flow rate', true),
    ((SELECT id FROM energy_sources WHERE name='compressed_air'), 'avg_pressure_bar', 'numeric', 'compressed_air_end_use_readings', 'pressure_bar', 'AVG', 'Average delivery pressure', true)
ON CONFLICT DO NOTHING;


-- Grant permissions
-- =====================================================
GRANT SELECT, INSERT, UPDATE ON natural_gas_readings TO raptorblingx;
GRANT SELECT, INSERT, UPDATE ON steam_readings TO raptorblingx;
GRANT SELECT, INSERT, UPDATE ON compressed_air_end_use_readings TO raptorblingx;
```

---

## 📋 V2 Checklist & Status

### Phase 1: Data Foundation ⏳
- [ ] Verify exact date range of real simulator data (Oct 7-24?)
- [ ] Add `data_source` column to flag backfilled vs real data
- [ ] Retrain all SEU baselines using only real Oct 7-21 data
- [ ] Generate reports comparing Oct 22-24 vs baseline
- [ ] Document actual baseline period in database

### Phase 2: OVOS Voice Integration 🔴
- [ ] Create `/api/v1/voice/train-baseline` endpoint
- [ ] Create `/api/v1/voice/available-features` endpoint
- [ ] Create `/api/v1/voice/available-energy-sources` endpoint
- [ ] Implement `format_voice_friendly()` function
- [ ] Add OVOS router to main.py
- [ ] Test voice commands with sample data
- [ ] Document voice command syntax

### Phase 3: Generic Multi-Energy 🔴
- [ ] Create `energy_table_mapper.py` service
- [ ] Update `feature_discovery.py` to use generic table lookups
- [ ] Update `seu_baseline_service.py` to use generic queries
- [ ] Remove any remaining hardcoded `energy_readings` references
- [ ] Add unit tests for multi-energy scenarios

### Phase 4: Future Energy Tables 🔴
- [ ] Create migration `007-multi-energy-tables.sql`
- [ ] Run migration to create natural_gas_readings table
- [ ] Run migration to create steam_readings table
- [ ] Run migration to create compressed_air_end_use_readings table
- [ ] Insert new energy sources into energy_sources table
- [ ] Add features to energy_source_features table
- [ ] Test schema with sample data

### Phase 5: Documentation & Testing 🔴
- [ ] Update API documentation with OVOS endpoints
- [ ] Create multi-energy usage examples
- [ ] Add voice command examples to OVOS docs
- [ ] Create test suite for multi-energy scenarios
- [ ] Update Project Knowledge Base
- [ ] Create demo script for Mr. Umut

---

## 🎯 Success Metrics for V2

### Technical Metrics
- ✅ Zero hardcoded `if energy_source == 'electricity'` statements
- ✅ Can add new energy source by inserting 1 row in `energy_sources` table
- ✅ OVOS voice training works with <95% accuracy on natural language
- ✅ All baselines trained on real simulator data (Oct 7-21)
- ✅ Feature discovery dynamically queries any energy table

### Business Metrics (Mr. Umut's Requirements)
- ✅ Voice command: "Train baseline for electricity Compressor-1..." → Returns formula
- ✅ Adding natural gas boiler requires:
  - 1 row in `energy_sources`
  - 1 row in `seus`
  - 0 code changes
- ✅ EnPI reports show realistic deviations (±5-10% from real operational changes)
- ✅ System is "future-proof" for 5+ years of facility expansion

---

## 📞 Next Steps & Questions

### Immediate Actions Required
1. **Verify simulator data range**: Run SQL query to confirm Oct 7-24 date range
2. **Decision on backfilled data**: Keep with flag? Delete? Archive?
3. **Priority**: OVOS voice endpoint vs data foundation first?

### Questions for Mr. Umut
1. When is the OVOS voice integration demo scheduled?
2. Are there plans to install natural gas, steam, or compressed air meters in next 6-12 months?
3. Should we keep backfilled 2024 data for testing/demos, or delete for clean slate?
4. What's the minimum acceptable R² for baselines in production? (currently 0.65-0.99)

---

## 📚 References

- **Current Implementation (V1)**: `docs/ISO-50001-PRODUCTION-IMPLEMENTATION-PLAN.md`
- **LAUDS Project**: Original multi-energy vision from Mr. Umut
- **ISO 50001**: Energy management system standard
- **ISO 50006**: Energy baseline and EnPI methodology
- **OVOS**: Open Voice Operating System for voice assistant integration

---

**Document Status**: Planning Phase - Awaiting approval to proceed  
**Last Updated**: October 24, 2025  
**Author**: EnMS Development Team  
**Approver**: Mr. Umut (Pending)
