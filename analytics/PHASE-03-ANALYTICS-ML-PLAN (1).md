# PHASE 3: Analytics & ML Service - Implementation Plan

**Document Version:** 1.0  
**Created:** October 10, 2025  
**Phase Status:** READY TO START  
**Prerequisites:** Phase 1 (Foundation) ✅ & Phase 2 (Grafana Visualization) ✅ COMPLETE  
**Estimated Duration:** 6-8 hours (split across 2-3 sessions)

---

## 📋 EXECUTIVE SUMMARY

Phase 3 focuses on building the **Analytics Service** - the ML-powered brain of the EnMS system. This FastAPI-based Python service will provide:

1. **Energy Baseline (EnB)** - ISO 50001-compliant regression analysis
2. **Anomaly Detection** - Real-time fault detection using Isolation Forest
3. **Energy Forecasting** - Demand prediction with ARIMA + Prophet
4. **KPI Calculations** - SEC, Peak Demand, Load Factor, Energy Cost, Carbon Intensity
5. **Custom Analytics UI** - Interactive regression analysis with driver selection
6. **Scheduled Jobs** - Automated model training and retraining

This service will operate on **port 8001** and integrate seamlessly with the existing TimescaleDB database and Nginx gateway.

---

## 🎯 PHASE 3 OBJECTIVES (FROM ORIGINAL PLAN)

### Deliverables (as specified in Project Knowledge Base)
- ✅ FastAPI service with ML models
- ✅ Baseline regression implemented
- ✅ Anomaly detection working
- ✅ Forecast API endpoints
- ✅ Custom analytics UI (driver selection)
- ✅ KPI calculation endpoints
- ✅ Scheduled model training jobs
- ✅ Integration with existing database schema
- ✅ OpenAPI documentation
- ✅ Docker deployment ready

### Success Criteria
- Analytics service starts and connects to database
- All API endpoints functional and documented
- Energy Baseline model achieves R² > 0.80
- Anomaly detection identifies test anomalies correctly
- Forecasting provides 24-hour predictions
- KPI calculations match SQL function results
- UI allows driver selection and displays regression results
- Scheduled jobs run without manual intervention
- Service accessible via Nginx at `/api/analytics/`

---

## 🏗️ ARCHITECTURE OVERVIEW

### Service Specifications

**Technology Stack:**
- **Framework:** FastAPI (Python 3.12)
- **ML Libraries:** scikit-learn, Prophet, statsmodels
- **Database Client:** asyncpg (async PostgreSQL)
- **Scheduler:** APScheduler
- **UI:** Jinja2 templates + vanilla JavaScript
- **Container:** Docker with Python 3.12-slim base

**Port & Routing:**
- **Internal Port:** 8001
- **External Access:** `http://server-ip:8080/api/analytics/`
- **API Docs:** `http://server-ip:8080/api/analytics/docs`
- **UI:** `http://server-ip:8080/api/analytics/ui/`

**Integration Points:**
- **Database:** PostgreSQL/TimescaleDB (postgres:5432)
- **Tables Used:** `energy_readings_1hour`, `production_data_1hour`, `environmental_data_1hour`, `energy_baselines`, `anomalies`, `machines`
- **Functions Used:** `calculate_sec()`, `calculate_peak_demand()`, `calculate_load_factor()`, `calculate_energy_cost()`, `calculate_carbon_intensity()`
- **Gateway:** Nginx reverse proxy
- **Monitoring:** Health check endpoint at `/health`

---

## 📦 PROJECT STRUCTURE

```
/enms/analytics/
├── Dockerfile                      # Python 3.12 container
├── requirements.txt                # Python dependencies
├── main.py                         # FastAPI application entry point
├── config.py                       # Configuration & environment variables
├── database.py                     # Database connection pool
│
├── api/                           # API Routes
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── baseline.py            # Energy baseline endpoints
│   │   ├── anomaly.py             # Anomaly detection endpoints
│   │   ├── forecast.py            # Forecasting endpoints
│   │   ├── kpi.py                 # KPI calculation endpoints
│   │   └── health.py              # Health check
│   └── middleware/
│       ├── __init__.py
│       ├── auth.py                # JWT authentication (Phase 7)
│       └── error_handlers.py      # Global error handling
│
├── models/                        # ML Models
│   ├── __init__.py
│   ├── baseline.py                # Energy Baseline (Linear Regression)
│   ├── anomaly_detector.py        # Isolation Forest
│   ├── forecaster.py              # ARIMA + Prophet
│   └── model_storage.py           # Save/load trained models
│
├── services/                      # Business Logic
│   ├── __init__.py
│   ├── baseline_service.py        # Baseline training & prediction
│   ├── anomaly_service.py         # Anomaly detection logic
│   ├── forecast_service.py        # Forecasting logic
│   └── kpi_service.py             # KPI calculations
│
├── scheduler/                     # Scheduled Jobs
│   ├── __init__.py
│   ├── jobs.py                    # Job definitions
│   └── scheduler.py               # APScheduler configuration
│
├── ui/                            # Analytics UI
│   ├── static/
│   │   ├── css/
│   │   │   └── analytics.css      # Custom styles
│   │   └── js/
│   │       └── analytics.js       # Interactive UI logic
│   └── templates/
│       ├── base.html              # Base template
│       ├── dashboard.html         # Analytics dashboard
│       ├── baseline.html          # Baseline regression UI
│       ├── anomaly.html           # Anomaly viewer
│       └── forecast.html          # Forecast viewer
│
└── tests/                         # Unit tests
    ├── __init__.py
    ├── test_baseline.py
    ├── test_anomaly.py
    ├── test_forecast.py
    └── test_kpi.py
```

---

## 🤖 ML MODELS SPECIFICATION (FROM KNOWLEDGE BASE)

### 1. Energy Baseline (EnB) - Multiple Linear Regression

**Purpose:** ISO 50001 compliance - establish normalized baseline for energy consumption

**Algorithm:** Multiple Linear Regression (sklearn.linear_model.LinearRegression)

**Formula:**
```
Energy = β₀ + β₁(Production) + β₂(Temp) + β₃(Hours) + β₄(Material) + ε
```

**Drivers (Independent Variables):**
- Production count (units/hour)
- Outdoor temperature (°C)
- Operating hours (hours)
- Material moisture content (%) - stored in production_data.metadata
- Pressure (bar)

**Training Requirements:**
- **Data Source:** Historical data from last 90 days
- **Minimum Samples:** 1000 observations per machine
- **Validation Criteria:** 
  - R² > 0.80
  - All p-values < 0.05
- **Retraining Schedule:** Weekly (automated via APScheduler)

**Database Storage:**
- Table: `energy_baselines`
- Fields: `coefficients` (JSONB), `intercept`, `feature_names`, `r_squared`, `rmse`, `mae`
- Versioning: `model_version` field for tracking

**Output:**
- Baseline Performance Deviation = Actual Energy - Predicted Energy
- Positive deviation indicates inefficiency or fault

**API Endpoints:**
```
POST   /api/v1/baseline/train          # Train model for machine
GET    /api/v1/baseline/deviation      # Get current deviation
GET    /api/v1/baseline/predict        # Predict energy for given conditions
GET    /api/v1/baseline/models         # List all baseline models
GET    /api/v1/baseline/model/{id}     # Get specific model details
```

---

### 2. Anomaly Detection - Isolation Forest

**Purpose:** Real-time fault detection and alert generation

**Algorithm:** Isolation Forest (sklearn.ensemble.IsolationForest)

**Detection Targets:**
- Power deviation from baseline (kW)
- Pressure anomalies (bar)
- Temperature spikes (°C)
- Efficiency drops (%)
- Unusual consumption patterns

**Thresholds:**
- **Warning Level:** 2σ deviation from baseline
- **Critical Level:** 3σ deviation from baseline

**Implementation:**
- **Contamination Rate:** 0.1 (10% of data expected to be anomalous)
- **Features Used:** 
  - Power deviation (actual - predicted)
  - Temperature differential
  - Pressure variation
  - Operating mode changes
  - Time-based features (hour of day, day of week)

**Database Storage:**
- Table: `anomalies`
- Fields: `anomaly_type`, `severity`, `metric_name`, `metric_value`, `expected_value`, `deviation_percent`, `confidence_score`

**API Endpoints:**
```
POST   /api/v1/anomaly/detect          # Detect anomalies for machine
GET    /api/v1/anomaly/recent          # Get recent anomalies
GET    /api/v1/anomaly/active          # Get unresolved anomalies
PUT    /api/v1/anomaly/{id}/resolve    # Mark anomaly as resolved
```

---

### 3. Forecasting - ARIMA + Prophet

**Purpose:** Demand prediction for load scheduling and cost optimization

**Algorithms:**
- **Short-term (next hour):** ARIMA (statsmodels)
- **Medium-term (next day):** Prophet (Facebook Prophet)
- **Long-term (next week):** Prophet with regressors

**Use Case:** 
Avoid peak demand charges by shifting loads to off-peak hours

**Forecasting Horizons:**
- **1 Hour:** 15-minute intervals (4 predictions)
- **24 Hours:** Hourly intervals (24 predictions)
- **7 Days:** Daily intervals (7 predictions)

**Regressors for Prophet:**
- Production schedule
- Temperature forecast
- Day of week
- Time of day
- Holiday calendar

**API Endpoints:**
```
GET    /api/v1/forecast/demand         # Get energy forecast
GET    /api/v1/forecast/peak           # Predict next peak demand time
GET    /api/v1/forecast/optimal-schedule  # Suggest load shifting
```

---

## 📊 KPI CALCULATIONS (FROM KNOWLEDGE BASE)

### 1. Specific Energy Consumption (SEC)

**Formula:**
```
SEC = SUM(energy_kwh) / SUM(production_count)
```

**Unit:** kWh/unit

**Database Function:** `calculate_sec(machine_id, start_time, end_time)`

**API Endpoint:**
```
GET /api/v1/kpi/sec?machine_id={uuid}&start={iso8601}&end={iso8601}
```

---

### 2. Peak Demand

**Formula:**
```
Peak = MAX(power_kw) over 15-minute rolling window
```

**Unit:** kW

**Database Function:** `calculate_peak_demand(machine_id, start_time, end_time)`

**API Endpoint:**
```
GET /api/v1/kpi/peak-demand?machine_id={uuid}&start={iso8601}&end={iso8601}
```

---

### 3. Load Factor

**Formula:**
```
Load_Factor = AVG(power_kw) / MAX(power_kw)
```

**Unit:** Unitless (0-1 or 0-100%)

**Database Function:** `calculate_load_factor(machine_id, start_time, end_time)`

**API Endpoint:**
```
GET /api/v1/kpi/load-factor?machine_id={uuid}&start={iso8601}&end={iso8601}
```

---

### 4. Energy Cost

**Formula:**
```
Cost = SUM(energy_kwh * tariff_rate)
```

**Unit:** USD (or local currency)

**Tariff Structure:** Time-of-use (peak/off-peak)
- Peak hours (08:00-20:00): $0.20/kWh
- Off-peak hours (20:00-08:00): $0.10/kWh

**Database Function:** `calculate_energy_cost(machine_id, start_time, end_time)`

**API Endpoint:**
```
GET /api/v1/kpi/energy-cost?machine_id={uuid}&start={iso8601}&end={iso8601}
```

---

### 5. Carbon Intensity

**Formula:**
```
CO2 = SUM(energy_kwh) * emission_factor
```

**Unit:** kg CO₂

**Emission Factor:** 0.45 kg CO₂/kWh (grid average)

**Database Function:** `calculate_carbon_intensity(machine_id, start_time, end_time)`

**API Endpoint:**
```
GET /api/v1/kpi/carbon?machine_id={uuid}&start={iso8601}&end={iso8601}
```

---

### 6. All KPIs (Convenience Endpoint)

**Database Function:** `calculate_all_kpis(machine_id, start_time, end_time)`

**API Endpoint:**
```
GET /api/v1/kpi/all?machine_id={uuid}&start={iso8601}&end={iso8601}
```

**Response includes:** SEC, Peak Demand, Load Factor, Energy Cost, Carbon Intensity in single call

---

## 🎨 CUSTOM ANALYTICS UI SPECIFICATION

### UI Requirements (FROM SUCCESS CRITERIA)

**Purpose:** Provide interactive regression analysis with driver selection

**Features Required:**
1. **Machine Selection Dropdown**
   - Multi-select capability
   - Filter by factory, type, or status

2. **Driver Selection Checkboxes**
   - Production count
   - Outdoor temperature
   - Operating hours
   - Material properties
   - Pressure
   - Custom metadata fields

3. **Time Range Selector**
   - Preset ranges (Last 7 days, Last 30 days, Last 90 days)
   - Custom date range picker

4. **Regression Results Display**
   - R² score
   - Coefficients table (driver → coefficient → p-value)
   - Intercept value
   - RMSE and MAE
   - Training sample count

5. **Visualization**
   - Actual vs. Predicted energy scatter plot
   - Residuals plot
   - Driver contribution bar chart

6. **Actions**
   - Train new model button
   - Export results to CSV
   - Download model coefficients

### UI Routes

```
GET    /api/analytics/ui/               # Landing page
GET    /api/analytics/ui/baseline       # Baseline regression UI
GET    /api/analytics/ui/anomaly        # Anomaly viewer
GET    /api/analytics/ui/forecast       # Forecast viewer
```

### Technology Stack

- **Backend:** Jinja2 templates (served by FastAPI)
- **Frontend:** Vanilla JavaScript (no React/Vue - keep it simple)
- **Charts:** Chart.js or Plotly.js
- **Styling:** Custom CSS (consistent with portal design)

---

## 🔄 SCHEDULED JOBS SPECIFICATION

### Job Scheduler: APScheduler

**Jobs to Implement:**

### 1. Weekly Baseline Retraining

**Schedule:** Every Sunday at 02:00 AM

**Function:** Retrain all active energy baseline models

**Logic:**
1. Fetch all active machines
2. For each machine:
   - Fetch last 90 days of data
   - Check if >= 1000 samples
   - Train new baseline model
   - Validate R² > 0.80
   - If valid, save to database with incremented version
   - Deactivate old model
3. Log results

**Configuration:**
```python
@scheduler.scheduled_job('cron', day_of_week='sun', hour=2)
async def retrain_baselines():
    # Implementation
```

---

### 2. Hourly Anomaly Detection

**Schedule:** Every hour at :05 minutes (e.g., 10:05, 11:05, 12:05)

**Function:** Run anomaly detection on all machines for last hour

**Logic:**
1. Fetch all active machines
2. For each machine:
   - Fetch last hour energy readings
   - Calculate expected values from baseline
   - Detect anomalies (Isolation Forest)
   - Insert anomalies into database
   - Log results

**Configuration:**
```python
@scheduler.scheduled_job('cron', minute=5)
async def detect_anomalies():
    # Implementation
```

---

### 3. Daily KPI Calculations

**Schedule:** Every day at 00:30 AM

**Function:** Pre-calculate KPIs for previous day for all machines

**Logic:**
1. Fetch all active machines
2. For each machine:
   - Calculate all KPIs for previous day (00:00 - 23:59)
   - Store results in cache or database
3. Log results

**Configuration:**
```python
@scheduler.scheduled_job('cron', hour=0, minute=30)
async def calculate_daily_kpis():
    # Implementation
```

---

## 🔌 API ENDPOINTS - COMPLETE SPECIFICATION

### Base URL: `/api/v1/`

---

### Baseline Endpoints

#### POST `/baseline/train`

Train a new energy baseline model for a machine.

**Request Body:**
```json
{
  "machine_id": "uuid",
  "start_date": "2025-10-01T00:00:00Z",
  "end_date": "2025-10-10T23:59:59Z",
  "drivers": ["production_count", "outdoor_temp_c", "operating_hours"]
}
```

**Response:**
```json
{
  "model_id": "uuid",
  "machine_id": "uuid",
  "model_version": 5,
  "r_squared": 0.87,
  "rmse": 4.23,
  "mae": 3.15,
  "training_samples": 1523,
  "coefficients": {
    "production_count": 0.023,
    "outdoor_temp_c": -0.45,
    "operating_hours": 12.34
  },
  "intercept": 25.67,
  "trained_at": "2025-10-10T14:30:00Z"
}
```

---

#### GET `/baseline/deviation`

Get baseline deviation for a machine over a time period.

**Query Parameters:**
- `machine_id` (required): UUID
- `start` (required): ISO 8601 datetime
- `end` (required): ISO 8601 datetime

**Response:**
```json
{
  "machine_id": "uuid",
  "machine_name": "Compressor 1",
  "time_period": {
    "start": "2025-10-10T00:00:00Z",
    "end": "2025-10-10T23:59:59Z"
  },
  "baseline_model_version": 5,
  "total_actual_kwh": 456.78,
  "total_predicted_kwh": 432.15,
  "deviation_kwh": 24.63,
  "deviation_percent": 5.7,
  "deviation_severity": "warning",
  "hourly_deviations": [
    {
      "hour": "2025-10-10T00:00:00Z",
      "actual_kwh": 18.5,
      "predicted_kwh": 17.2,
      "deviation_kwh": 1.3
    }
  ]
}
```

---

### Anomaly Endpoints

#### POST `/anomaly/detect`

Detect anomalies for a machine over a time period.

**Request Body:**
```json
{
  "machine_id": "uuid",
  "start": "2025-10-10T00:00:00Z",
  "end": "2025-10-10T23:59:59Z",
  "contamination": 0.1
}
```

**Response:**
```json
{
  "machine_id": "uuid",
  "anomalies_detected": 3,
  "anomalies": [
    {
      "id": "uuid",
      "detected_at": "2025-10-10T14:35:00Z",
      "anomaly_type": "power_spike",
      "severity": "critical",
      "metric_name": "power_kw",
      "metric_value": 85.3,
      "expected_value": 45.2,
      "deviation_percent": 88.7,
      "confidence_score": 0.95
    }
  ]
}
```

---

#### GET `/anomaly/recent`

Get recent anomalies (last 24 hours).

**Query Parameters:**
- `machine_id` (optional): Filter by machine
- `severity` (optional): Filter by severity (warning, critical)
- `limit` (optional): Max results (default: 50)

**Response:**
```json
{
  "total_count": 12,
  "anomalies": [
    {
      "id": "uuid",
      "machine_id": "uuid",
      "machine_name": "HVAC Main",
      "detected_at": "2025-10-10T14:35:00Z",
      "anomaly_type": "temperature_spike",
      "severity": "warning",
      "is_resolved": false
    }
  ]
}
```

---

### Forecast Endpoints

#### GET `/forecast/demand`

Get energy demand forecast for a machine.

**Query Parameters:**
- `machine_id` (required): UUID
- `horizon` (required): "1h", "24h", or "7d"

**Response:**
```json
{
  "machine_id": "uuid",
  "machine_name": "Injection Molding 1",
  "forecast_generated_at": "2025-10-10T15:00:00Z",
  "horizon": "24h",
  "predictions": [
    {
      "timestamp": "2025-10-10T16:00:00Z",
      "predicted_power_kw": 67.5,
      "confidence_interval_lower": 62.3,
      "confidence_interval_upper": 72.7
    }
  ],
  "peak_demand_predicted": {
    "timestamp": "2025-10-10T19:00:00Z",
    "power_kw": 85.2
  }
}
```

---

### KPI Endpoints

#### GET `/kpi/sec`

Calculate Specific Energy Consumption.

**Query Parameters:**
- `machine_id` (required): UUID
- `start` (required): ISO 8601 datetime
- `end` (required): ISO 8601 datetime

**Response:**
```json
{
  "machine_id": "uuid",
  "machine_name": "Compressor 1",
  "sec_kwh_per_unit": 0.045,
  "total_energy_kwh": 456.78,
  "total_production_units": 10150,
  "time_period_hours": 24.0
}
```

---

#### GET `/kpi/all`

Calculate all KPIs in a single request.

**Query Parameters:**
- `machine_id` (required): UUID
- `start` (required): ISO 8601 datetime
- `end` (required): ISO 8601 datetime

**Response:**
```json
{
  "machine_id": "uuid",
  "machine_name": "Compressor 1",
  "time_period": {
    "start": "2025-10-10T00:00:00Z",
    "end": "2025-10-10T23:59:59Z",
    "hours": 24.0
  },
  "kpis": {
    "sec": {
      "value": 0.045,
      "unit": "kWh/unit"
    },
    "peak_demand": {
      "value": 78.5,
      "unit": "kW",
      "timestamp": "2025-10-10T14:35:00Z"
    },
    "load_factor": {
      "value": 0.67,
      "percent": 67.0
    },
    "energy_cost": {
      "value": 68.52,
      "unit": "USD"
    },
    "carbon_intensity": {
      "value": 205.55,
      "unit": "kg CO2"
    }
  }
}
```

---

### Health Endpoint

#### GET `/health`

Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "service": "analytics",
  "version": "1.0.0",
  "timestamp": "2025-10-10T15:30:00Z",
  "database": "connected",
  "scheduler": "running",
  "models_loaded": 7
}
```

---

## 🐳 DOCKER CONFIGURATION

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories for model storage
RUN mkdir -p /app/models/saved

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8001/health')" || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

---

### requirements.txt

```
# FastAPI & Server
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
asyncpg==0.29.0
psycopg2-binary==2.9.9

# ML & Data Science
scikit-learn==1.3.2
prophet==1.1.5
statsmodels==0.14.0
pandas==2.1.3
numpy==1.26.2

# Scheduler
apscheduler==3.10.4

# UI Templates
jinja2==3.1.2

# Utilities
python-jose[cryptography]==3.3.0  # For JWT (Phase 7)
python-multipart==0.0.6
httpx==0.25.2
```

---

### docker-compose.yml Addition

```yaml
  analytics:
    build: ./analytics
    container_name: enms-analytics
    restart: unless-stopped
    ports:
      - "8001:8001"
    environment:
      - SERVICE_NAME=Analytics Service
      - SERVICE_VERSION=1.0.0
      - API_PORT=8001
      - DATABASE_HOST=postgres
      - DATABASE_PORT=5432
      - DATABASE_NAME=enms
      - DATABASE_USER=${POSTGRES_USER}
      - DATABASE_PASSWORD=${POSTGRES_PASSWORD}
      - LOG_LEVEL=INFO
      - MODEL_STORAGE_PATH=/app/models/saved
      - BASELINE_MIN_SAMPLES=1000
      - BASELINE_MIN_R2=0.80
      - ANOMALY_CONTAMINATION=0.1
      - SCHEDULER_ENABLED=true
    depends_on:
      - postgres
    networks:
      - enms-network
    volumes:
      - ./analytics/models/saved:/app/models/saved
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

---

### Nginx Configuration Addition

Add to `/enms/nginx/conf.d/default.conf`:

```nginx
# Analytics Service
location /api/analytics/ {
    proxy_pass http://analytics:8001/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Increase timeout for ML operations
    proxy_read_timeout 300s;
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
}
```

---

## 📝 IMPLEMENTATION TASKS - DETAILED BREAKDOWN

### Session 1: Core Infrastructure (2-3 hours)

#### Task 1.1: Project Setup (30 min)
- [ ] Create `/enms/analytics/` directory structure
- [ ] Create `Dockerfile`
- [ ] Create `requirements.txt`
- [ ] Create `config.py` with environment variables
- [ ] Create `database.py` with async connection pool
- [ ] Create `main.py` with FastAPI app initialization

**Validation:**
- Directory structure matches plan
- Docker image builds successfully
- Config loads environment variables correctly

---

#### Task 1.2: Database Integration (30 min)
- [ ] Implement async database connection pool
- [ ] Create database helper functions:
  - `get_machine_data(machine_id, start, end)`
  - `get_energy_readings(machine_id, start, end)`
  - `get_production_data(machine_id, start, end)`
  - `get_environmental_data(machine_id, start, end)`
  - `save_baseline_model(model_data)`
  - `save_anomaly(anomaly_data)`
- [ ] Test database connectivity

**Validation:**
- Connection pool connects to PostgreSQL
- Helper functions return data correctly
- Error handling works for failed connections

---

#### Task 1.3: Health Check & Basic Routes (30 min)
- [ ] Implement `/health` endpoint
- [ ] Set up API versioning (`/api/v1/`)
- [ ] Configure CORS middleware
- [ ] Set up logging
- [ ] Create error handlers

**Validation:**
- Health check returns status
- OpenAPI docs accessible at `/docs`
- Logs appear in console/file

---

#### Task 1.4: Docker Integration (30 min)
- [ ] Build Docker image
- [ ] Add analytics service to docker-compose.yml
- [ ] Update Nginx configuration
- [ ] Start service with `docker-compose up -d analytics`
- [ ] Test service accessible via Nginx

**Validation:**
- Service starts without errors
- Accessible at `http://server-ip:8080/api/analytics/`
- Health check returns "healthy"

---

### Session 2: ML Models & KPIs (2-3 hours)

#### Task 2.1: Energy Baseline Implementation (60 min)
- [ ] Create `models/baseline.py`:
  - `BaselineModel` class
  - `train()` method (sklearn LinearRegression)
  - `predict()` method
  - `evaluate()` method (R², RMSE, MAE)
  - `save()` and `load()` methods
- [ ] Create `services/baseline_service.py`:
  - `train_baseline()` - orchestrates training
  - `get_deviation()` - calculates actual vs predicted
  - `get_model()` - retrieves saved model
- [ ] Create `api/routes/baseline.py`:
  - POST `/baseline/train`
  - GET `/baseline/deviation`
  - GET `/baseline/predict`

**Validation:**
- Train model with test data
- R² > 0.80 for good data
- Predictions return reasonable values
- Models save/load correctly

---

#### Task 2.2: Anomaly Detection Implementation (45 min)
- [ ] Create `models/anomaly_detector.py`:
  - `AnomalyDetector` class
  - `fit()` method (Isolation Forest)
  - `detect()` method
  - Severity calculation (2σ warning, 3σ critical)
- [ ] Create `services/anomaly_service.py`:
  - `detect_anomalies()` - run detection
  - `save_anomaly()` - insert to database
  - `get_recent_anomalies()` - query database
- [ ] Create `api/routes/anomaly.py`:
  - POST `/anomaly/detect`
  - GET `/anomaly/recent`
  - GET `/anomaly/active`

**Validation:**
- Inject test anomaly via simulator
- Detection identifies anomaly
- Severity calculated correctly
- Anomaly saved to database

---

#### Task 2.3: Forecasting Implementation (45 min)
- [ ] Create `models/forecaster.py`:
  - `Forecaster` class
  - `forecast_arima()` - short-term (1 hour)
  - `forecast_prophet()` - medium/long-term (24h, 7d)
  - Confidence intervals
- [ ] Create `services/forecast_service.py`:
  - `generate_forecast()` - orchestrates forecasting
  - `predict_peak()` - identify peak demand time
- [ ] Create `api/routes/forecast.py`:
  - GET `/forecast/demand`
  - GET `/forecast/peak`

**Validation:**
- Generate 24-hour forecast
- Predictions within reasonable range
- Confidence intervals calculated
- Peak demand identified correctly

---

#### Task 2.4: KPI Calculations (30 min)
- [ ] Create `services/kpi_service.py`:
  - `calculate_sec()` - calls database function
  - `calculate_peak_demand()`
  - `calculate_load_factor()`
  - `calculate_energy_cost()`
  - `calculate_carbon_intensity()`
  - `calculate_all_kpis()` - convenience method
- [ ] Create `api/routes/kpi.py`:
  - GET `/kpi/sec`
  - GET `/kpi/peak-demand`
  - GET `/kpi/load-factor`
  - GET `/kpi/energy-cost`
  - GET `/kpi/carbon`
  - GET `/kpi/all`

**Validation:**
- KPI calculations match database function results
- All KPIs return for test machine
- Response format matches specification

---

### Session 3: UI & Scheduler (2 hours)

#### Task 3.1: Analytics UI (60 min)
- [ ] Create UI templates:
  - `templates/base.html` - base layout
  - `templates/dashboard.html` - analytics dashboard
  - `templates/baseline.html` - regression analysis UI
- [ ] Create static files:
  - `static/css/analytics.css` - custom styles
  - `static/js/analytics.js` - UI logic
- [ ] Implement UI routes:
  - GET `/ui/` - dashboard
  - GET `/ui/baseline` - baseline regression UI
- [ ] Create interactive features:
  - Machine selection dropdown
  - Driver selection checkboxes
  - Time range picker
  - Train model button
  - Results display (R², coefficients, charts)

**Validation:**
- UI loads without errors
- Machine dropdown populates from database
- Driver selection works
- Training triggers API call
- Results display correctly

---

#### Task 3.2: Scheduled Jobs (45 min)
- [ ] Create `scheduler/scheduler.py`:
  - APScheduler configuration
  - Job registration
- [ ] Create `scheduler/jobs.py`:
  - `retrain_baselines()` - weekly job
  - `detect_anomalies()` - hourly job
  - `calculate_daily_kpis()` - daily job
- [ ] Integrate scheduler with FastAPI startup
- [ ] Add job status endpoint: GET `/scheduler/status`

**Validation:**
- Scheduler starts with service
- Jobs registered correctly
- Manual job trigger works
- Jobs log results

---

#### Task 3.3: Testing & Documentation (15 min)
- [ ] Write unit tests for models
- [ ] Test all API endpoints with Swagger UI
- [ ] Update README with analytics service info
- [ ] Create ANALYTICS-SERVICE.md documentation
- [ ] Update .env.example with analytics variables

**Validation:**
- All tests pass
- API docs complete and accurate
- Documentation clear and comprehensive

---

## ✅ ACCEPTANCE CRITERIA

Phase 3 is considered COMPLETE when:

### Functional Requirements
- [ ] Analytics service starts and stays healthy
- [ ] All API endpoints functional (tested via Swagger UI)
- [ ] Energy Baseline model trains with R² > 0.80
- [ ] Anomaly detection identifies injected test anomalies
- [ ] Forecasting provides 24-hour predictions
- [ ] All KPIs calculate correctly and match database function results
- [ ] Analytics UI loads and allows driver selection
- [ ] Regression results display with charts
- [ ] Scheduled jobs run automatically (weekly, hourly, daily)

### Integration Requirements
- [ ] Service accessible via Nginx at `/api/analytics/`
- [ ] Database queries use asyncpg and connection pool
- [ ] Models save/load from persistent volume
- [ ] Logs structured and informative
- [ ] Health check endpoint returns accurate status

### Code Quality Requirements
- [ ] All Python files have type hints
- [ ] All functions have Google-style docstrings
- [ ] Error handling for all database operations
- [ ] Proper async/await usage
- [ ] No hardcoded values (use config)

### Documentation Requirements
- [ ] API documented in OpenAPI/Swagger
- [ ] README updated with Phase 3 info
- [ ] ANALYTICS-SERVICE.md created
- [ ] Code comments for complex logic
- [ ] Environment variables documented in .env.example

---

## 🔍 TESTING STRATEGY

### Unit Tests

**Test Files:**
- `tests/test_baseline.py`
- `tests/test_anomaly.py`
- `tests/test_forecast.py`
- `tests/test_kpi.py`

**Test Coverage:**
- Model training and prediction
- Anomaly detection logic
- Forecasting algorithms
- KPI calculation accuracy
- Database helper functions
- API endpoint responses

**Run Tests:**
```bash
docker-compose exec analytics pytest
docker-compose exec analytics pytest --cov=. --cov-report=html
```

---

### Integration Tests

**Manual Test Checklist:**

1. **Baseline Training:**
   - [ ] Train model for compressor-1
   - [ ] Verify R² > 0.80
   - [ ] Check model saved to database
   - [ ] Verify model_version incremented

2. **Anomaly Detection:**
   - [ ] Inject anomaly via simulator
   - [ ] Run detection endpoint
   - [ ] Verify anomaly detected and saved
   - [ ] Check severity calculation correct

3. **Forecasting:**
   - [ ] Request 24-hour forecast
   - [ ] Verify predictions returned
   - [ ] Check confidence intervals
   - [ ] Validate peak demand identification

4. **KPI Calculations:**
   - [ ] Calculate all KPIs for test machine
   - [ ] Compare with database function results
   - [ ] Verify units correct
   - [ ] Check time period accuracy

5. **UI Testing:**
   - [ ] Load analytics dashboard
   - [ ] Select machine and drivers
   - [ ] Train model via UI
   - [ ] Verify results display
   - [ ] Check charts render

6. **Scheduler Testing:**
   - [ ] Verify scheduler starts
   - [ ] Check jobs registered
   - [ ] Manually trigger job
   - [ ] Verify job execution logs

---

### Performance Tests

**Load Testing:**
- Simulate 10 concurrent API requests
- Measure response times
- Check database connection pool handling
- Monitor memory usage during ML operations

**Benchmarks:**
- Baseline training: < 30 seconds for 1000 samples
- Anomaly detection: < 5 seconds for 1 hour of data
- Forecasting: < 10 seconds for 24-hour prediction
- KPI calculation: < 2 seconds per endpoint

---

## 🚨 POTENTIAL ISSUES & MITIGATION

### Issue 1: Insufficient Training Data

**Problem:** New machines may not have 1000+ samples for baseline training

**Mitigation:**
- Check sample count before training
- Return informative error if insufficient
- Suggest minimum collection period (e.g., "Collect 3 more days of data")
- Allow training with warning if >= 500 samples

---

### Issue 2: Long-Running ML Operations

**Problem:** Model training may timeout HTTP requests

**Mitigation:**
- Increase Nginx timeout to 300 seconds
- Implement async task queue (optional for Phase 7)
- Return job ID immediately, poll for results
- Add progress indicator in UI

---

### Issue 3: Model Versioning Conflicts

**Problem:** Multiple concurrent training sessions could conflict

**Mitigation:**
- Use database transaction locks
- Implement model versioning correctly
- Check for existing training job before starting new one
- Add status field to energy_baselines table

---

### Issue 4: Scheduler Not Running

**Problem:** APScheduler may not start if database unavailable

**Mitigation:**
- Retry scheduler startup with exponential backoff
- Log scheduler status on startup
- Add scheduler health check to `/health` endpoint
- Separate scheduler from API if needed

---

### Issue 5: Memory Usage for Prophet

**Problem:** Prophet models can consume significant memory

**Mitigation:**
- Limit forecast horizon (max 7 days)
- Use ARIMA for short-term forecasts
- Consider model caching
- Monitor container memory usage

---

## 📈 SUCCESS METRICS

### Phase 3 KPIs

**Deployment:**
- Time to deploy: < 30 minutes
- First successful API call: < 5 minutes after start
- Zero critical errors in logs

**Model Performance:**
- Baseline R² > 0.80 for 80% of machines
- Anomaly detection precision > 0.75
- Forecast MAPE < 15%

**System Performance:**
- API response time < 5 seconds (95th percentile)
- Health check success rate > 99%
- Scheduled jobs complete successfully > 95%

**User Experience:**
- UI loads in < 3 seconds
- Interactive features respond in < 1 second
- Charts render correctly in all major browsers

---

## 🔄 HANDOVER TO PHASE 4

### What's Ready for Phase 4 (Unified Portal):

**APIs Ready:**
- Analytics service fully operational
- All endpoints documented
- Health checks implemented

**Integration Points:**
- Service accessible via Nginx
- Database schema supports analytics
- Model storage volume configured

### What Phase 4 Needs:

**Portal Integration:**
- Embed analytics UI in unified portal
- Add analytics service card to portal landing page
- Link to `/api/analytics/ui/` from portal

**Navigation:**
- Add analytics to portal menu
- Include service status indicator
- Show active anomaly count on portal dashboard

---

## 📚 REFERENCES & RESOURCES

### Knowledge Base Documents Referenced:
- Project Knowledge Base.txt - Main requirements
- SESSION-07-HANDOVER.md - Phase 2 completion status
- 02-schema.sql - Database schema (energy_baselines, anomalies tables)
- 04-functions.sql - KPI calculation functions
- README.md - Overall project architecture

### External Documentation:
- FastAPI: https://fastapi.tiangolo.com/
- scikit-learn: https://scikit-learn.org/
- Prophet: https://facebook.github.io/prophet/
- APScheduler: https://apscheduler.readthedocs.io/
- TimescaleDB: https://docs.timescale.com/

### ISO Standards:
- ISO 50001:2018 - Energy Management Systems
- ISO 50006:2014 - Energy Baselines (EnB)

---

## 📞 CRITICAL NOTES FOR NEXT SESSION

1. **NO GUESSING**: This plan is based 100% on Knowledge Base facts - all ML models, KPIs, and APIs are from the original specification

2. **Database Schema Ready**: The `energy_baselines` and `anomalies` tables already exist from Phase 1 - use them as designed

3. **TimescaleDB Functions**: All KPI calculation functions already exist - call them, don't reimplement

4. **Port 8001**: Analytics service MUST run on port 8001 as specified in original architecture

5. **Python 3.12**: Use Python 3.12 as specified in project requirements

6. **FastAPI**: Use FastAPI (not Flask) as per original design decision

7. **Async Database**: Use asyncpg for database operations - connection pool already designed

8. **Scheduled Jobs**: APScheduler is the chosen scheduler - already in architecture

9. **UI Framework**: Use Jinja2 + vanilla JS - no React/Vue (keep it simple)

10. **Model Storage**: Models save to `/app/models/saved` volume - configure docker-compose.yml accordingly

---

## 🎯 READY TO START!

This comprehensive plan provides:
- ✅ Complete architecture from Knowledge Base
- ✅ All ML models specified with algorithms
- ✅ All API endpoints with request/response formats
- ✅ All KPI formulas from original requirements
- ✅ Complete project structure
- ✅ Detailed implementation tasks (6-8 hours)
- ✅ Acceptance criteria
- ✅ Testing strategy
- ✅ Risk mitigation

**Next Steps:**
1. Add this document to Knowledge Base
2. Start Phase 3 implementation in next session
3. Follow tasks in order (Session 1 → Session 2 → Session 3)
4. Validate against acceptance criteria
5. Deploy and test
6. Update project status and handover documentation

**Phase 3 Target Completion:** 2-3 sessions (6-8 hours total development time)

---

**Document Status:** ✅ COMPLETE - READY FOR KNOWLEDGE BASE  
**Generated By:** Claude (EnMS System Architect)  
**Date:** October 10, 2025  
**Based On:** Original Project Knowledge Base (100% factual, 0% assumptions)  
**Next Phase:** Phase 4 - Unified Portal

---

*This plan will guide the next Claude instance (or developer) through Phase 3 implementation with complete clarity and no ambiguity. All specifications are grounded in the actual project requirements from the Knowledge Base.*
