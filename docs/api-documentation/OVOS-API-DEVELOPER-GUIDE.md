# OVOS API Integration Guide - Quick Reference

**Base URL:** `http://localhost:8001`  
**API Version:** v1  
**Date:** October 17, 2025  
**Status:** Production Ready ✅

---

## 📋 Quick Navigation

1. [Essential Endpoints](#essential-endpoints)
2. [Machine Data](#machine-data)
3. [Energy & Power Queries](#energy--power-queries)
4. [KPIs & Analytics](#kpis--analytics)
5. [Anomalies & Alerts](#anomalies--alerts)
6. [Forecasting](#forecasting)
7. [Comparisons](#comparisons)
8. [Error Handling](#error-handling)
9. [Integration Examples](#integration-examples)

---

## 🎯 Essential Endpoints

### Health Check
```bash
GET /api/v1/health
```
**Response:**
```json
{
  "status": "healthy",
  "active_machines": 7,
  "recent_anomalies": 0,
  "database": {"status": "connected"},
  "scheduler": {"running": true}
}
```

### List All Machines
```bash
GET /api/v1/machines
```
**Response:**
```json
[
  {
    "id": "c0000000-0000-0000-0000-000000000001",
    "name": "Compressor-1",
    "type": "compressor",
    "rated_power_kw": "55.00",
    "factory_name": "Demo Manufacturing Plant"
  }
]
```

---

## 🏭 Machine Data

### Get Single Machine
```bash
GET /api/v1/machines/{machine_id}

# Example
curl http://localhost:8001/api/v1/machines/c0000000-0000-0000-0000-000000000001
```

### Get Latest Reading
```bash
GET /api/v1/timeseries/latest/{machine_id}

# Example
curl http://localhost:8001/api/v1/timeseries/latest/c0000000-0000-0000-0000-000000000001
```
**Response:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "machine_name": "Compressor-1",
  "timestamp": "2025-10-17T11:55:00+00:00",
  "power_kw": 45.2,
  "energy_kwh": 0.754,
  "current_a": 82.3,
  "voltage_v": 415.0,
  "temperature_c": 42.5
}
```

---

## ⚡ Energy & Power Queries

### Get Energy Time Series
```bash
GET /api/v1/timeseries/energy?machine_id={uuid}&start_time={iso8601}&end_time={iso8601}&interval={interval}

# Example - Today's hourly energy
curl "http://localhost:8001/api/v1/timeseries/energy?machine_id=c0000000-0000-0000-0000-000000000001&start_time=2025-10-17T00:00:00Z&end_time=2025-10-17T23:59:59Z&interval=1hour"
```

**Parameters:**
- `machine_id` (required): UUID
- `start_time` (required): ISO 8601 format (e.g., `2025-10-17T00:00:00Z`)
- `end_time` (required): ISO 8601 format
- `interval` (required): `1min` | `5min` | `15min` | `1hour` | `1day`

**Response:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "machine_name": "Compressor-1",
  "interval": "1hour",
  "data_points": [
    {
      "timestamp": "2025-10-17T01:00:00+00:00",
      "value": 52.34,
      "unit": "kWh"
    }
  ],
  "total_points": 24
}
```

### Get Power Time Series
```bash
GET /api/v1/timeseries/power?machine_id={uuid}&start_time={iso8601}&end_time={iso8601}&interval={interval}

# Same parameters as energy, but returns power (kW)
```

### Multi-Machine Energy Comparison
```bash
GET /api/v1/timeseries/multi-machine/energy?machine_ids={uuid1,uuid2}&start_time={iso8601}&end_time={iso8601}&interval={interval}

# Example - Compare 2 machines
curl "http://localhost:8001/api/v1/timeseries/multi-machine/energy?machine_ids=c0000000-0000-0000-0000-000000000001,c0000000-0000-0000-0000-000000000002&start_time=2025-10-17T00:00:00Z&end_time=2025-10-17T23:59:59Z&interval=1hour"
```

---

## 📊 KPIs & Analytics

### Get All KPIs (Single Request)
```bash
GET /api/v1/kpi/all?machine_id={uuid}&start={iso8601}&end={iso8601}

# Example - This month's KPIs
curl "http://localhost:8001/api/v1/kpi/all?machine_id=c0000000-0000-0000-0000-000000000001&start=2025-10-01T00:00:00Z&end=2025-10-17T23:59:59Z"
```

**Response:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "machine_name": "Compressor-1",
  "time_period": {
    "start": "2025-10-01T00:00:00+00:00",
    "end": "2025-10-17T23:59:59+00:00"
  },
  "kpis": {
    "sec": {
      "value": 2.45,
      "unit": "kWh/unit",
      "description": "Specific Energy Consumption"
    },
    "peak_demand": {
      "value": 52.3,
      "unit": "kW",
      "description": "Maximum Power Demand"
    },
    "load_factor": {
      "value": 0.75,
      "percent": 75.0,
      "description": "Average/Peak Power Ratio"
    },
    "energy_cost": {
      "value": 1234.56,
      "unit": "USD",
      "cost_per_unit": 0.15
    },
    "carbon_intensity": {
      "value": 567.89,
      "unit": "kg CO2",
      "co2_per_unit": 0.45
    }
  },
  "totals": {
    "total_energy_kwh": 8234.56,
    "avg_power_kw": 39.2
  }
}
```

### Individual KPI Endpoints
```bash
GET /api/v1/kpi/sec              # Specific Energy Consumption only
GET /api/v1/kpi/peak-demand      # Peak Demand only
GET /api/v1/kpi/load-factor      # Load Factor only
GET /api/v1/kpi/energy-cost      # Energy Cost only
GET /api/v1/kpi/carbon           # Carbon Emissions only

# All use same parameters as /kpi/all
```

---

## 🚨 Anomalies & Alerts

### Get Recent Anomalies
```bash
GET /api/v1/anomaly/recent?limit={number}&severity={level}&hours={hours}

# Example - Last 5 high severity anomalies
curl "http://localhost:8001/api/v1/anomaly/recent?limit=5&severity=high&hours=24"
```

**Parameters:**
- `limit` (optional): Number of results (default: 10)
- `machine_id` (optional): Filter by machine
- `severity` (optional): `low` | `medium` | `high` | `critical`
- `hours` (optional): Time window in hours (default: 24)

**Response:**
```json
{
  "total_count": 3,
  "anomalies": [
    {
      "id": "anomaly-uuid",
      "machine_id": "c0000000-0000-0000-0000-000000000001",
      "machine_name": "Compressor-1",
      "detected_at": "2025-10-17T10:30:00+00:00",
      "severity": "high",
      "anomaly_type": "energy_spike",
      "description": "Energy consumption 45% above baseline",
      "actual_value": 75.5,
      "expected_value": 52.3,
      "deviation_percent": 44.4,
      "status": "unresolved"
    }
  ]
}
```

### Get Active Anomalies
```bash
GET /api/v1/anomaly/active

# Returns only unresolved anomalies
curl http://localhost:8001/api/v1/anomaly/active
```

### Trigger Anomaly Detection
```bash
POST /api/v1/anomaly/detect
Content-Type: application/json

{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "start_time": "2025-10-17T00:00:00Z",
  "end_time": "2025-10-17T23:59:59Z"
}
```

### Resolve Anomaly
```bash
PUT /api/v1/anomaly/{anomaly_id}/resolve
Content-Type: application/json

{
  "resolution_notes": "Issue fixed - sensor calibrated"
}
```

---

## 🔮 Forecasting

### Check Forecast Models
```bash
GET /api/v1/forecast/models/{machine_id}

# Example
curl http://localhost:8001/api/v1/forecast/models/c0000000-0000-0000-0000-000000000001
```

**Response:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "arima": {
    "trained": true,
    "last_modified": "2025-10-17T10:50:17+00:00"
  },
  "prophet": {
    "trained": true,
    "last_modified": "2025-10-17T11:10:34+00:00"
  }
}
```

### Generate Energy Forecast
```bash
POST /api/v1/forecast/predict
Content-Type: application/json

{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "model_type": "prophet",
  "forecast_hours": 24
}
```

**Request Body:**
- `machine_id` (required): UUID
- `model_type` (required): `arima` | `prophet`
- `forecast_hours` (required): Number of hours to forecast

**Response:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "machine_name": "Compressor-1",
  "model_type": "prophet",
  "forecast_start": "2025-10-17T12:00:00+00:00",
  "forecast_end": "2025-10-18T12:00:00+00:00",
  "predictions": [
    {
      "timestamp": "2025-10-17T13:00:00+00:00",
      "predicted_energy": 52.3,
      "lower_bound": 48.1,
      "upper_bound": 56.5,
      "confidence": 0.95
    }
  ],
  "total_predicted_energy": 1256.7
}
```

### Get Peak Demand Forecast
```bash
GET /api/v1/forecast/peak?machine_id={uuid}&date={YYYY-MM-DD}

# Example - Tomorrow's peak
curl "http://localhost:8001/api/v1/forecast/peak?machine_id=c0000000-0000-0000-0000-000000000001&date=2025-10-18"
```

**Response:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "date": "2025-10-18",
  "predicted_peak": {
    "value": 58.7,
    "unit": "kW",
    "timestamp": "2025-10-18T14:30:00+00:00"
  }
}
```

### Train Forecast Models
```bash
# Train ARIMA
POST /api/v1/forecast/train/arima
Content-Type: application/json

{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "start_date": "2025-09-01T00:00:00Z",
  "end_date": "2025-10-17T23:59:59Z"
}

# Train Prophet
POST /api/v1/forecast/train/prophet
Content-Type: application/json

{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "start_date": "2025-09-01T00:00:00Z",
  "end_date": "2025-10-17T23:59:59Z",
  "seasonality_mode": "multiplicative"
}
```

---

## 🔄 Comparisons

### List Available Machines for Comparison
```bash
GET /api/v1/comparison/available

curl http://localhost:8001/api/v1/comparison/available
```

### Compare Multiple Machines
```bash
GET /api/v1/comparison/machines?machine_ids={uuid1,uuid2,uuid3}&start_date={YYYY-MM-DD}&end_date={YYYY-MM-DD}&metrics={metric1,metric2}

# Example - Compare 2 compressors
curl "http://localhost:8001/api/v1/comparison/machines?machine_ids=c0000000-0000-0000-0000-000000000001,c0000000-0000-0000-0000-000000000006&start_date=2025-10-01&end_date=2025-10-17&metrics=energy,cost"
```

**Parameters:**
- `machine_ids` (required): Comma-separated UUIDs
- `start_date` (required): YYYY-MM-DD format
- `end_date` (required): YYYY-MM-DD format
- `metrics` (optional): Comma-separated: `energy`, `power`, `sec`, `cost` (default: all)

**Response:**
```json
{
  "start_date": "2025-10-01",
  "end_date": "2025-10-17",
  "machines": [
    {
      "machine_id": "c0000000-0000-0000-0000-000000000001",
      "machine_name": "Compressor-1",
      "metrics": {
        "total_energy": 1234.56,
        "total_cost": 185.18,
        "avg_power": 38.5
      },
      "rank": 1
    },
    {
      "machine_id": "c0000000-0000-0000-0000-000000000006",
      "machine_name": "Compressor-EU-1",
      "metrics": {
        "total_energy": 1567.89,
        "total_cost": 235.18,
        "avg_power": 48.9
      },
      "rank": 2
    }
  ],
  "best_performer": "c0000000-0000-0000-0000-000000000001",
  "worst_performer": "c0000000-0000-0000-0000-000000000006"
}
```

---

## 📈 Visualizations

### Sankey Energy Flow
```bash
GET /api/v1/sankey/data?factory_id={uuid}&date={YYYY-MM-DD}

# Example - Today's energy flow
curl "http://localhost:8001/api/v1/sankey/data?date=2025-10-17"
```

**Response:**
```json
{
  "nodes": [
    {"id": "grid", "name": "Grid", "level": 0},
    {"id": "factory_...", "name": "Demo Plant", "level": 1},
    {"id": "machine_...", "name": "Compressor-1", "level": 3}
  ],
  "links": [
    {
      "source": "grid",
      "target": "factory_...",
      "value": 13618.77,
      "percentage": 60.19
    }
  ],
  "metadata": {
    "date": "2025-10-17",
    "total_energy": 22627.93,
    "machine_count": 7
  }
}
```

### Energy Heatmap
```bash
GET /api/v1/heatmap/hourly?machine_id={uuid}&start_date={YYYY-MM-DD}&end_date={YYYY-MM-DD}

# Example - This month's hourly heatmap
curl "http://localhost:8001/api/v1/heatmap/hourly?machine_id=c0000000-0000-0000-0000-000000000001&start_date=2025-10-01&end_date=2025-10-17"
```

---

## 🎯 Baseline Models

### List Baseline Models
```bash
GET /api/v1/baseline/models?machine_id={uuid}

curl "http://localhost:8001/api/v1/baseline/models?machine_id=c0000000-0000-0000-0000-000000000001"
```

**Response:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "total_models": 8,
  "models": [
    {
      "id": "model-uuid",
      "model_version": 8,
      "training_samples": 117,
      "r_squared": 0.9672,
      "rmse": 1.604165,
      "is_active": true,
      "created_at": "2025-10-17T11:14:11+00:00"
    }
  ]
}
```

### Get Deviation from Baseline
```bash
GET /api/v1/baseline/deviation?machine_id={uuid}&start_time={iso8601}&end_time={iso8601}

# Example
curl "http://localhost:8001/api/v1/baseline/deviation?machine_id=c0000000-0000-0000-0000-000000000001&start_time=2025-10-17T00:00:00Z&end_time=2025-10-17T12:00:00Z"
```

**Response:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "deviations": [
    {
      "timestamp": "2025-10-17T10:00:00+00:00",
      "actual": 54.2,
      "predicted": 52.3,
      "deviation": 1.9,
      "deviation_percent": 3.6,
      "is_anomaly": false
    }
  ],
  "statistics": {
    "avg_deviation": 1.2,
    "max_deviation": 5.6,
    "anomaly_count": 2
  }
}
```

### Train New Baseline Model
```bash
POST /api/v1/baseline/train
Content-Type: application/json

{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "start_date": "2025-10-01T00:00:00Z",
  "end_date": "2025-10-17T23:59:59Z",
  "drivers": ["power_kw", "temperature_c"]
}
```

### Predict Energy with Baseline
```bash
POST /api/v1/baseline/predict
Content-Type: application/json

{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "inputs": {
    "power_kw": 45.5,
    "temperature_c": 42.0
  }
}
```

---

## 🤖 Model Performance

### Trigger Model Retraining
```bash
POST /api/v1/model-performance/retrain/trigger?model_type={type}&machine_id={uuid}&trigger_type=manual&reason={text}

# Example
curl -X POST "http://localhost:8001/api/v1/model-performance/retrain/trigger?model_type=baseline&machine_id=c0000000-0000-0000-0000-000000000001&trigger_type=manual&reason=User%20requested"
```

**Parameters:**
- `model_type`: `baseline` | `anomaly` | `forecast_arima` | `forecast_prophet`
- `machine_id`: UUID
- `trigger_type`: `manual` | `scheduled` | `drift`
- `reason` (optional): Text explanation

**Response:**
```json
{
  "triggered": true,
  "trigger_type": "manual",
  "training_job_id": "job-uuid",
  "estimated_completion": "2025-10-17T12:05:39+00:00"
}
```

### Check Model Performance Trend
```bash
GET /api/v1/model-performance/metrics/trend?model_type={type}&machine_id={uuid}&days={number}

# Example - Last 30 days
curl "http://localhost:8001/api/v1/model-performance/metrics/trend?model_type=baseline&machine_id=c0000000-0000-0000-0000-000000000001&days=30"
```

### Check for Model Drift
```bash
POST /api/v1/model-performance/drift/check
Content-Type: application/json

{
  "model_type": "baseline",
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "evaluation_start": "2025-10-16T00:00:00Z",
  "evaluation_end": "2025-10-17T00:00:00Z"
}
```

**Response:**
```json
{
  "drift_detected": false,
  "drift_score": 0.15,
  "drift_type": "no_drift",
  "recommendation": "Model performance is stable",
  "threshold": 0.25,
  "current_performance": {
    "r_squared": 0.95,
    "rmse": 1.8
  }
}
```

---

## ⏰ Scheduler

### Get Scheduler Status
```bash
GET /api/v1/scheduler/status

curl http://localhost:8001/api/v1/scheduler/status
```

**Response:**
```json
{
  "enabled": true,
  "running": true,
  "job_count": 4,
  "jobs": [
    {
      "id": "anomaly_detect",
      "name": "Hourly Anomaly Detection",
      "next_run": "2025-10-17T12:05:00+00:00"
    },
    {
      "id": "baseline_retrain",
      "name": "Weekly Baseline Retraining",
      "next_run": "2025-10-20T02:00:00+00:00"
    }
  ]
}
```

### Trigger Scheduled Job Manually
```bash
POST /api/v1/scheduler/trigger/{job_id}

# Example - Trigger anomaly detection now
curl -X POST http://localhost:8001/api/v1/scheduler/trigger/anomaly_detect
```

**Available Job IDs:**
- `anomaly_detect` - Hourly anomaly detection
- `baseline_retrain` - Weekly baseline retraining
- `kpi_calculate` - Daily KPI calculation
- `training_cleanup` - Training job cleanup

---

## ❌ Error Handling

### HTTP Status Codes
- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid parameters
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

### Error Response Format

**Simple Error:**
```json
{
  "detail": "Machine not found"
}
```

**Validation Error:**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["query", "machine_id"],
      "msg": "Field required",
      "input": null
    }
  ]
}
```

### Common Errors
- `"Machine not found"` - Invalid machine_id
- `"No data available for this period"` - Time range has no data
- `"Model not trained"` - Forecast/baseline model doesn't exist
- `"Training already in progress"` - Cannot start duplicate training
- `"Invalid time range"` - start_time must be before end_time

---

## 🔧 Integration Examples

### Python Example
```python
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8001"

# 1. Check system health
response = requests.get(f"{BASE_URL}/api/v1/health")
health = response.json()
print(f"Status: {health['status']}, Machines: {health['active_machines']}")

# 2. Get all machines
response = requests.get(f"{BASE_URL}/api/v1/machines")
machines = response.json()
compressor = next(m for m in machines if m['name'] == 'Compressor-1')

# 3. Get today's energy
today = datetime.now().date()
response = requests.get(
    f"{BASE_URL}/api/v1/timeseries/energy",
    params={
        "machine_id": compressor['id'],
        "start_time": f"{today}T00:00:00Z",
        "end_time": f"{today}T23:59:59Z",
        "interval": "1hour"
    }
)
energy_data = response.json()
total_energy = sum(point['value'] for point in energy_data['data_points'])
print(f"Total energy today: {total_energy:.2f} kWh")

# 4. Check for anomalies
response = requests.get(
    f"{BASE_URL}/api/v1/anomaly/active"
)
anomalies = response.json()
if anomalies['total_count'] > 0:
    for anomaly in anomalies['anomalies']:
        if anomaly['severity'] in ['high', 'critical']:
            print(f"ALERT: {anomaly['machine_name']} - {anomaly['description']}")

# 5. Get KPIs
response = requests.get(
    f"{BASE_URL}/api/v1/kpi/all",
    params={
        "machine_id": compressor['id'],
        "start": f"{today.replace(day=1).isoformat()}T00:00:00Z",
        "end": f"{today.isoformat()}T23:59:59Z"
    }
)
kpis = response.json()
print(f"SEC: {kpis['kpis']['sec']['value']} kWh/unit")
print(f"Cost: ${kpis['kpis']['energy_cost']['value']:.2f}")

# 6. Get forecast
response = requests.post(
    f"{BASE_URL}/api/v1/forecast/predict",
    json={
        "machine_id": compressor['id'],
        "model_type": "prophet",
        "forecast_hours": 24
    }
)
forecast = response.json()
print(f"Tomorrow's forecast: {forecast['total_predicted_energy']:.2f} kWh")
```

### JavaScript Example
```javascript
const BASE_URL = 'http://localhost:8001';

// 1. Get machine list
async function getMachines() {
  const response = await fetch(`${BASE_URL}/api/v1/machines`);
  return await response.json();
}

// 2. Get latest reading
async function getLatestReading(machineId) {
  const response = await fetch(
    `${BASE_URL}/api/v1/timeseries/latest/${machineId}`
  );
  return await response.json();
}

// 3. Get energy for date range
async function getEnergy(machineId, startTime, endTime, interval) {
  const params = new URLSearchParams({
    machine_id: machineId,
    start_time: startTime,
    end_time: endTime,
    interval: interval
  });
  
  const response = await fetch(
    `${BASE_URL}/api/v1/timeseries/energy?${params}`
  );
  return await response.json();
}

// 4. Check for anomalies
async function checkAnomalies(severity = 'high') {
  const params = new URLSearchParams({
    limit: 10,
    severity: severity,
    hours: 24
  });
  
  const response = await fetch(
    `${BASE_URL}/api/v1/anomaly/recent?${params}`
  );
  return await response.json();
}

// 5. Get forecast
async function getForecast(machineId, hours = 24) {
  const response = await fetch(
    `${BASE_URL}/api/v1/forecast/predict`,
    {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        machine_id: machineId,
        model_type: 'prophet',
        forecast_hours: hours
      })
    }
  );
  return await response.json();
}

// Usage
(async () => {
  const machines = await getMachines();
  const compressor = machines.find(m => m.name === 'Compressor-1');
  
  const latest = await getLatestReading(compressor.id);
  console.log(`Current power: ${latest.power_kw} kW`);
  
  const anomalies = await checkAnomalies('high');
  console.log(`Active anomalies: ${anomalies.total_count}`);
})();
```

### cURL Examples for Testing
```bash
# Health check
curl http://localhost:8001/api/v1/health

# Get all machines
curl http://localhost:8001/api/v1/machines

# Get latest reading
curl http://localhost:8001/api/v1/timeseries/latest/c0000000-0000-0000-0000-000000000001

# Get today's hourly energy
curl "http://localhost:8001/api/v1/timeseries/energy?machine_id=c0000000-0000-0000-0000-000000000001&start_time=2025-10-17T00:00:00Z&end_time=2025-10-17T23:59:59Z&interval=1hour"

# Get all KPIs for this month
curl "http://localhost:8001/api/v1/kpi/all?machine_id=c0000000-0000-0000-0000-000000000001&start=2025-10-01T00:00:00Z&end=2025-10-17T23:59:59Z"

# Check active anomalies
curl http://localhost:8001/api/v1/anomaly/active

# Get 24-hour forecast
curl -X POST "http://localhost:8001/api/v1/forecast/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "c0000000-0000-0000-0000-000000000001",
    "model_type": "prophet",
    "forecast_hours": 24
  }'

# Compare 2 machines
curl "http://localhost:8001/api/v1/comparison/machines?machine_ids=c0000000-0000-0000-0000-000000000001,c0000000-0000-0000-0000-000000000002&start_date=2025-10-01&end_date=2025-10-17&metrics=energy,cost"
```

---

## 🎤 OVOS Voice Integration Examples

### Example 1: "What's the system status?"
```python
response = requests.get(f"{BASE_URL}/api/v1/health")
data = response.json()

if data['status'] == 'healthy':
    speak(f"All systems healthy. {data['active_machines']} machines active.")
    if data['recent_anomalies'] > 0:
        speak(f"There are {data['recent_anomalies']} recent anomalies.")
```

### Example 2: "How much power is Compressor-1 using?"
```python
machine_id = "c0000000-0000-0000-0000-000000000001"
response = requests.get(f"{BASE_URL}/api/v1/timeseries/latest/{machine_id}")
data = response.json()

speak(f"{data['machine_name']} is currently drawing {data['power_kw']:.1f} kilowatts.")
```

### Example 3: "What's the energy usage today?"
```python
machine_id = "c0000000-0000-0000-0000-000000000001"
today = datetime.now().date()

response = requests.get(
    f"{BASE_URL}/api/v1/timeseries/energy",
    params={
        "machine_id": machine_id,
        "start_time": f"{today}T00:00:00Z",
        "end_time": f"{today}T23:59:59Z",
        "interval": "1day"
    }
)
data = response.json()
total = sum(p['value'] for p in data['data_points'])

speak(f"{data['machine_name']} has used {total:.2f} kilowatt hours today.")
```

### Example 4: "Are there any alerts?"
```python
response = requests.get(f"{BASE_URL}/api/v1/anomaly/active")
data = response.json()

if data['total_count'] == 0:
    speak("No active alerts.")
else:
    speak(f"There are {data['total_count']} active alerts.")
    for anomaly in data['anomalies'][:3]:  # Top 3
        if anomaly['severity'] in ['high', 'critical']:
            speak(f"{anomaly['machine_name']}: {anomaly['description']}")
```

### Example 5: "What's tomorrow's energy forecast?"
```python
machine_id = "c0000000-0000-0000-0000-000000000001"

response = requests.post(
    f"{BASE_URL}/api/v1/forecast/predict",
    json={
        "machine_id": machine_id,
        "model_type": "prophet",
        "forecast_hours": 24
    }
)
data = response.json()

speak(f"Tomorrow's forecast for {data['machine_name']} is "
      f"{data['total_predicted_energy']:.0f} kilowatt hours.")
```

### Example 6: "Compare energy usage of Compressor-1 and HVAC-Main"
```python
machine_ids = [
    "c0000000-0000-0000-0000-000000000001",
    "c0000000-0000-0000-0000-000000000002"
]

response = requests.get(
    f"{BASE_URL}/api/v1/comparison/machines",
    params={
        "machine_ids": ",".join(machine_ids),
        "start_date": "2025-10-01",
        "end_date": "2025-10-17",
        "metrics": "energy,cost"
    }
)
data = response.json()

for machine in data['machines']:
    speak(f"{machine['machine_name']}: "
          f"{machine['metrics']['total_energy']:.0f} kilowatt hours, "
          f"costing ${machine['metrics']['total_cost']:.2f}")

best = next(m for m in data['machines'] 
            if m['machine_id'] == data['best_performer'])
speak(f"{best['machine_name']} is the better performer.")
```

---

## 📚 Additional Resources

### Interactive API Documentation
Access the auto-generated Swagger UI:
```
http://localhost:8001/docs
```

### Web Dashboard
Visual interface for testing:
```
http://localhost:8001/ui/
```

### Machine IDs Reference
Common machine IDs in the system:
```
Compressor-1:     c0000000-0000-0000-0000-000000000001
HVAC-Main:        c0000000-0000-0000-0000-000000000002
CNC-Mill-1:       c0000000-0000-0000-0000-000000000003
Injection-Mold-1: c0000000-0000-0000-0000-000000000004
Chiller-1:        c0000000-0000-0000-0000-000000000005
Compressor-EU-1:  c0000000-0000-0000-0000-000000000006
HVAC-EU-Main:     c0000000-0000-0000-0000-000000000007
```

---

## 🚀 Quick Start Checklist

- [ ] Verify service: `curl http://localhost:8001/api/v1/health`
- [ ] Get machines: `curl http://localhost:8001/api/v1/machines`
- [ ] Test energy query with a valid machine_id
- [ ] Test anomaly detection
- [ ] Test forecast (if models are trained)
- [ ] Test KPI retrieval
- [ ] Review Swagger docs: `http://localhost:8001/docs`

---

## 📞 Support

**Service Port:** 8001  
**Documentation:** http://localhost:8001/docs  
**Web UI:** http://localhost:8001/ui/  
**Status:** ✅ Production Ready

**Note:** All timestamps use ISO 8601 format with timezone (UTC). All machine IDs are UUID v4 format.

---

**Last Updated:** October 17, 2025  
**API Version:** 1.0.0  
**Document Version:** 1.0
