# EnMS Analytics API Documentation for OVOS Integration

**Version:** 1.0.0  
**Base URL:** `http://localhost:8001`  
**API Prefix:** `/api/v1`  
**Date:** October 15, 2025  

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Common Patterns](#common-patterns)
4. [System Endpoints](#system-endpoints)
5. [Machine Management](#machine-management)
6. [Time Series Data](#time-series-data)
7. [KPI Endpoints](#kpi-endpoints)
8. [Baseline Models](#baseline-models)
9. [Anomaly Detection](#anomaly-detection)
10. [Energy Forecasting](#energy-forecasting)
11. [Visualizations](#visualizations)
12. [Model Performance](#model-performance)
13. [Scheduler](#scheduler)
14. [Error Handling](#error-handling)
15. [Examples](#examples)

---

## 🎯 Overview

The EnMS Analytics Service provides REST APIs for:
- Real-time energy monitoring and analytics
- Machine learning-powered baseline regression
- Anomaly detection and alerting
- Energy forecasting (ARIMA & Prophet models)
- KPI calculations (SEC, Peak Demand, Load Factor, Cost, Carbon)
- Multi-machine comparison and benchmarking
- Energy flow visualization (Sankey diagrams, Heatmaps)
- Model performance tracking and drift detection

### Features Available

✅ Baseline Regression  
✅ Anomaly Detection  
✅ KPI Calculation  
✅ Energy Forecasting  
✅ Time Series Analytics  
✅ Sankey Energy Flow  
✅ Anomaly Heatmap  
✅ Machine Comparison  
✅ Model Performance Tracking

---

## 🔐 Authentication

**Current Status:** No authentication required (internal service)

For production OVOS integration, consider implementing:
- API key authentication
- JWT tokens
- Rate limiting per client

---

## 🔄 Common Patterns

### Date/Time Formats

All timestamps use **ISO 8601 format with timezone**:
```
2025-10-15T14:30:00Z        # UTC
2025-10-15T14:30:00+00:00   # UTC with explicit timezone
```

### UUID Format

Machine IDs and other identifiers use **UUID v4**:
```
c0000000-0000-0000-0000-000000000001
```

### Response Structure

**Success Response:**
```json
{
  "machine_id": "uuid",
  "data": [...],
  "metadata": {}
}
```

**Error Response:**
```json
{
  "detail": "Error message"
}
```

or for validation errors:
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["query", "start_time"],
      "msg": "Field required"
    }
  ]
}
```

### Time Intervals

Valid interval values:
- `1min` - 1 minute
- `5min` - 5 minutes
- `15min` - 15 minutes
- `1hour` - 1 hour
- `1day` - 1 day

---

## 🏥 System Endpoints

### GET `/`
**Service Information**

Get basic service information and available endpoints.

**Response:**
```json
{
  "service": "EnMS Analytics Service",
  "version": "1.0.0",
  "status": "healthy",
  "endpoints": {
    "docs": "/docs",
    "ui": "/ui/",
    "api": "/api/v1",
    "health": "/api/v1/health"
  }
}
```

---

### GET `/api/v1/health`
**Health Check**

Comprehensive health check including database, scheduler, and system statistics.

**Request:**
```bash
curl http://localhost:8001/api/v1/health
```

**Response:**
```json
{
  "service": "EnMS Analytics Service",
  "version": "1.0.0",
  "status": "healthy",
  "database": {
    "status": "connected",
    "name": "enms",
    "host": "postgres",
    "pool_size": 1
  },
  "scheduler": {
    "enabled": true,
    "running": true,
    "job_count": 4,
    "jobs": [
      {
        "id": "anomaly_detect",
        "name": "Hourly Anomaly Detection",
        "next_run": "2025-10-15T12:05:00+00:00",
        "trigger": "cron[month='*', day='*', day_of_week='*', hour='*', minute='5']"
      }
    ]
  },
  "features": [
    "baseline_regression",
    "anomaly_detection",
    "kpi_calculation",
    "energy_forecasting",
    "time_series_analytics"
  ],
  "active_machines": 7,
  "baseline_models": 0,
  "recent_anomalies": 0,
  "timestamp": "2025-10-15T11:58:16.429128"
}
```

**Use Case for OVOS:**
- Voice command: "What's the system status?"
- Response: "All systems healthy. 7 machines active, no recent anomalies."

---

## 🏭 Machine Management

### GET `/api/v1/machines`
**List All Machines**

Get a list of all active machines in the system.

**Request:**
```bash
curl http://localhost:8001/api/v1/machines
```

**Response:**
```json
[
  {
    "id": "c0000000-0000-0000-0000-000000000001",
    "factory_id": "11111111-1111-1111-1111-111111111111",
    "name": "Compressor-1",
    "type": "compressor",
    "rated_power_kw": "55.00",
    "is_active": true,
    "factory_name": "Demo Manufacturing Plant",
    "factory_location": "Silicon Valley, CA, USA"
  },
  {
    "id": "c0000000-0000-0000-0000-000000000002",
    "name": "HVAC-Main",
    "type": "hvac",
    "rated_power_kw": "150.00",
    "is_active": true,
    "factory_name": "Demo Manufacturing Plant",
    "factory_location": "Silicon Valley, CA, USA"
  }
]
```

**Use Case for OVOS:**
- Voice: "List all machines"
- Voice: "Show me the compressor machines"
- Response: Filter by type and read machine names

---

### GET `/api/v1/machines/{machine_id}`
**Get Single Machine Details**

Get detailed information about a specific machine.

**Parameters:**
- `machine_id` (path, required): UUID of the machine

**Request:**
```bash
curl http://localhost:8001/api/v1/machines/c0000000-0000-0000-0000-000000000001
```

**Response:**
```json
{
  "id": "c0000000-0000-0000-0000-000000000001",
  "factory_id": "11111111-1111-1111-1111-111111111111",
  "name": "Compressor-1",
  "type": "compressor",
  "rated_power_kw": "55.00",
  "is_active": true,
  "factory_name": "Demo Manufacturing Plant",
  "factory_location": "Silicon Valley, CA, USA"
}
```

**Use Case for OVOS:**
- Voice: "Tell me about Compressor-1"
- Response: "Compressor-1 is a 55 kilowatt compressor located at Demo Manufacturing Plant in Silicon Valley."

---

## 📊 Time Series Data

### GET `/api/v1/timeseries/energy`
**Get Energy Time Series**

Retrieve aggregated energy consumption data over time.

**Parameters:**
- `machine_id` (query, required): UUID of the machine
- `start_time` (query, required): Start timestamp (ISO 8601)
- `end_time` (query, required): End timestamp (ISO 8601)
- `interval` (query, required): Aggregation interval (`1min`, `5min`, `15min`, `1hour`, `1day`)

**Request:**
```bash
curl "http://localhost:8001/api/v1/timeseries/energy?machine_id=c0000000-0000-0000-0000-000000000001&start_time=2025-10-14T00:00:00Z&end_time=2025-10-14T06:00:00Z&interval=1hour"
```

**Response:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "machine_name": "Compressor-1",
  "metric": "energy",
  "interval": "1hour",
  "start_time": "2025-10-14T00:00:00+00:00",
  "end_time": "2025-10-14T06:00:00+00:00",
  "data_points": [
    {
      "timestamp": "2025-10-14T01:00:00+00:00",
      "value": 0.011867,
      "unit": "kWh"
    },
    {
      "timestamp": "2025-10-14T02:00:00+00:00",
      "value": 0.011897,
      "unit": "kWh"
    }
  ],
  "total_points": 2,
  "aggregation": "sum"
}
```

**Use Case for OVOS:**
- Voice: "What's the energy consumption of Compressor-1 today?"
- Voice: "Show hourly energy usage for HVAC-Main yesterday"

---

### GET `/api/v1/timeseries/power`
**Get Power Time Series**

Retrieve power demand data over time.

**Parameters:** Same as `/timeseries/energy`

**Response Structure:** Same format, but values in `kW`

---

### GET `/api/v1/timeseries/sec`
**Get Specific Energy Consumption Time Series**

Retrieve SEC (Specific Energy Consumption) data over time.

**Parameters:** Same as `/timeseries/energy`

**Response Structure:** Same format, but values in `kWh/unit`

---

### GET `/api/v1/timeseries/latest/{machine_id}`
**Get Latest Reading**

Get the most recent sensor reading for a machine.

**Request:**
```bash
curl http://localhost:8001/api/v1/timeseries/latest/c0000000-0000-0000-0000-000000000001
```

**Response:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "machine_name": "Compressor-1",
  "timestamp": "2025-10-15T11:55:00+00:00",
  "power_kw": 45.2,
  "energy_kwh": 0.754,
  "current_a": 82.3,
  "voltage_v": 415.0,
  "power_factor": 0.88,
  "frequency_hz": 50.0,
  "temperature_c": 42.5
}
```

**Use Case for OVOS:**
- Voice: "What's the current power of Compressor-1?"
- Response: "Compressor-1 is currently drawing 45.2 kilowatts."

---

### GET `/api/v1/timeseries/multi-machine/energy`
**Get Multi-Machine Energy Comparison**

Compare energy consumption across multiple machines.

**Parameters:**
- `machine_ids` (query, required): Comma-separated list of machine UUIDs
- `start_time` (query, required): Start timestamp
- `end_time` (query, required): End timestamp
- `interval` (query, required): Aggregation interval

**Request:**
```bash
curl "http://localhost:8001/api/v1/timeseries/multi-machine/energy?machine_ids=c0000000-0000-0000-0000-000000000001,c0000000-0000-0000-0000-000000000002&start_time=2025-10-14T00:00:00Z&end_time=2025-10-14T23:59:59Z&interval=1hour"
```

**Response:**
```json
{
  "start_time": "2025-10-14T00:00:00+00:00",
  "end_time": "2025-10-14T23:59:59+00:00",
  "interval": "1hour",
  "machines": [
    {
      "machine_id": "c0000000-0000-0000-0000-000000000001",
      "machine_name": "Compressor-1",
      "total_energy": 123.45,
      "data_points": [...]
    },
    {
      "machine_id": "c0000000-0000-0000-0000-000000000002",
      "machine_name": "HVAC-Main",
      "total_energy": 567.89,
      "data_points": [...]
    }
  ]
}
```

**Use Case for OVOS:**
- Voice: "Compare energy usage of Compressor-1 and HVAC-Main today"

---

## 📈 KPI Endpoints

### GET `/api/v1/kpi/all`
**Get All KPIs**

Get all 5 KPIs for a machine in a single request.

**Parameters:**
- `machine_id` (query, required): UUID of the machine
- `start` (query, required): Start timestamp (ISO 8601)
- `end` (query, required): End timestamp (ISO 8601)

**Request:**
```bash
curl "http://localhost:8001/api/v1/kpi/all?machine_id=c0000000-0000-0000-0000-000000000001&start=2025-01-01T00:00:00Z&end=2025-01-31T23:59:59Z"
```

**Response:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "machine_name": "Compressor-1",
  "machine_type": "compressor",
  "time_period": {
    "start": "2025-01-01T00:00:00+00:00",
    "end": "2025-01-31T23:59:59+00:00",
    "hours": 743.9997
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
      "unit": "ratio",
      "description": "Average/Peak Power Ratio"
    },
    "energy_cost": {
      "value": 1234.56,
      "cost_per_unit": 0.15,
      "unit": "USD",
      "description": "Total Energy Cost (Time-of-Use Tariff)"
    },
    "carbon_intensity": {
      "value": 567.89,
      "co2_per_unit": 0.45,
      "unit": "kg CO2",
      "description": "Total Carbon Emissions"
    }
  },
  "totals": {
    "total_energy_kwh": 8234.56,
    "avg_power_kw": 39.2,
    "total_production_units": 3360
  }
}
```

**Use Case for OVOS:**
- Voice: "What are the KPIs for Compressor-1 this month?"
- Response: "Compressor-1 this month: Specific Energy Consumption 2.45 kilowatt hours per unit, Peak Demand 52.3 kilowatts, Load Factor 75%, Energy Cost $1,234.56, Carbon Emissions 567.89 kilograms."

---

### GET `/api/v1/kpi/sec`
**Get SEC Only**

Get only the Specific Energy Consumption KPI.

**Parameters:** Same as `/kpi/all`

**Response:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "machine_name": "Compressor-1",
  "time_period": {...},
  "sec": {
    "value": 2.45,
    "unit": "kWh/unit",
    "total_energy": 8234.56,
    "total_production": 3360
  }
}
```

---

### GET `/api/v1/kpi/peak-demand`
**Get Peak Demand Only**

**Parameters:** Same as `/kpi/all`

**Response:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "peak_demand": {
    "value": 52.3,
    "unit": "kW",
    "timestamp": "2025-01-15T14:30:00+00:00",
    "avg_power": 39.2
  }
}
```

**Use Case for OVOS:**
- Voice: "What was the peak demand of Compressor-1 today?"
- Response: "Peak demand was 52.3 kilowatts at 2:30 PM."

---

### GET `/api/v1/kpi/load-factor`
**Get Load Factor Only**

**Parameters:** Same as `/kpi/all`

---

### GET `/api/v1/kpi/energy-cost`
**Get Energy Cost Only**

**Parameters:** Same as `/kpi/all`

---

### GET `/api/v1/kpi/carbon`
**Get Carbon Emissions Only**

**Parameters:** Same as `/kpi/all`

---

## 🤖 Baseline Models

Baseline models use regression to predict expected energy consumption based on operational parameters.

### GET `/api/v1/baseline/models`
**List Baseline Models**

Get all trained baseline models for a machine.

**Parameters:**
- `machine_id` (query, required): UUID of the machine

**Request:**
```bash
curl "http://localhost:8001/api/v1/baseline/models?machine_id=c0000000-0000-0000-0000-000000000001"
```

**Response:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "total_models": 8,
  "models": [
    {
      "id": "4fbf7568-ede7-4eb9-a545-b3ef49a0910a",
      "machine_id": "c0000000-0000-0000-0000-000000000001",
      "model_name": "baseline_v8",
      "model_version": 8,
      "training_samples": 117,
      "r_squared": 0.9672,
      "rmse": 1.604165,
      "mae": 0.629889,
      "is_active": true,
      "created_at": "2025-10-15T11:14:11.977990+00:00"
    }
  ]
}
```

**Use Case for OVOS:**
- Voice: "How accurate is the baseline model for Compressor-1?"
- Response: "The current baseline model has an R-squared of 0.967, indicating 96.7% accuracy."

---

### GET `/api/v1/baseline/model/{model_id}`
**Get Model Details**

Get detailed information about a specific model.

**Response:**
```json
{
  "id": "4fbf7568-ede7-4eb9-a545-b3ef49a0910a",
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "model_name": "baseline_v8",
  "coefficients": {
    "intercept": 12.34,
    "power_kw": 0.856,
    "temperature_c": 0.123
  },
  "feature_importance": {
    "power_kw": 0.72,
    "temperature_c": 0.18,
    "vibration": 0.10
  },
  "statistics": {
    "r_squared": 0.9672,
    "rmse": 1.604165,
    "mae": 0.629889
  }
}
```

---

### POST `/api/v1/baseline/train`
**Train New Baseline Model**

Train a new baseline model for a machine.

**Request Body:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "start_date": "2025-10-01T00:00:00Z",
  "end_date": "2025-10-15T23:59:59Z",
  "drivers": ["power_kw", "temperature_c", "vibration"]
}
```

**Response:**
```json
{
  "success": true,
  "model_id": "new-uuid",
  "model_version": 9,
  "statistics": {
    "r_squared": 0.9712,
    "rmse": 1.523,
    "mae": 0.589,
    "training_samples": 125
  },
  "message": "Baseline model trained successfully"
}
```

---

### POST `/api/v1/baseline/predict`
**Predict Energy Consumption**

Use baseline model to predict expected energy consumption.

**Request Body:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "inputs": {
    "power_kw": 45.5,
    "temperature_c": 42.0,
    "vibration": 0.5
  }
}
```

**Response:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "predicted_energy": 52.3,
  "unit": "kWh",
  "model_version": 8,
  "confidence": 0.95
}
```

**Use Case for OVOS:**
- Voice: "What's the expected energy for Compressor-1 at 45 kilowatts?"
- Response: "Expected energy consumption is 52.3 kilowatt hours."

---

### GET `/api/v1/baseline/deviation`
**Get Deviation from Baseline**

Compare actual vs. predicted energy consumption.

**Parameters:**
- `machine_id` (query, required): UUID
- `start_time` (query, required): Start timestamp
- `end_time` (query, required): End timestamp

**Response:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "time_period": {...},
  "deviations": [
    {
      "timestamp": "2025-10-15T10:00:00+00:00",
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

---

## 🚨 Anomaly Detection

### GET `/api/v1/anomaly/recent`
**Get Recent Anomalies**

Get recently detected anomalies.

**Parameters:**
- `limit` (query, optional): Number of results (default: 10)
- `machine_id` (query, optional): Filter by machine UUID
- `severity` (query, optional): Filter by severity (`low`, `medium`, `high`, `critical`)
- `hours` (query, optional): Time window in hours (default: 24)

**Request:**
```bash
curl "http://localhost:8001/api/v1/anomaly/recent?limit=5&severity=high"
```

**Response:**
```json
{
  "total_count": 3,
  "filters": {
    "machine_id": null,
    "severity": "high",
    "time_window": "24 hours"
  },
  "anomalies": [
    {
      "id": "anomaly-uuid",
      "machine_id": "c0000000-0000-0000-0000-000000000001",
      "machine_name": "Compressor-1",
      "detected_at": "2025-10-15T10:30:00+00:00",
      "severity": "high",
      "anomaly_type": "energy_spike",
      "description": "Energy consumption 45% above baseline",
      "actual_value": 75.5,
      "expected_value": 52.3,
      "deviation": 23.2,
      "deviation_percent": 44.4,
      "status": "unresolved",
      "resolved_at": null
    }
  ]
}
```

**Use Case for OVOS:**
- Voice: "Are there any high severity anomalies?"
- Response: "Yes, Compressor-1 has a high severity energy spike detected at 10:30 AM. Energy consumption is 45% above baseline."

---

### GET `/api/v1/anomaly/active`
**Get Active Anomalies**

Get all unresolved anomalies.

**Request:**
```bash
curl http://localhost:8001/api/v1/anomaly/active
```

**Response:** Same format as `/anomaly/recent`

**Use Case for OVOS:**
- Voice: "What anomalies need attention?"
- Voice: "Show me active alerts"

---

### POST `/api/v1/anomaly/detect`
**Trigger Anomaly Detection**

Manually trigger anomaly detection for a machine.

**Request Body:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "start_time": "2025-10-15T00:00:00Z",
  "end_time": "2025-10-15T23:59:59Z"
}
```

**Response:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "detection_window": {...},
  "anomalies_detected": 2,
  "anomalies": [...]
}
```

---

### PUT `/api/v1/anomaly/{anomaly_id}/resolve`
**Resolve Anomaly**

Mark an anomaly as resolved.

**Request Body:**
```json
{
  "resolution_notes": "Issue identified and fixed - faulty sensor replaced"
}
```

**Response:**
```json
{
  "success": true,
  "anomaly_id": "anomaly-uuid",
  "status": "resolved",
  "resolved_at": "2025-10-15T11:45:00+00:00"
}
```

**Use Case for OVOS:**
- Voice: "Mark the Compressor-1 anomaly as resolved"

---

## 🔮 Energy Forecasting

### GET `/api/v1/forecast/models/{machine_id}`
**Get Forecast Model Status**

Check if forecast models are trained for a machine.

**Request:**
```bash
curl http://localhost:8001/api/v1/forecast/models/c0000000-0000-0000-0000-000000000001
```

**Response:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "arima": {
    "trained": true,
    "path": "/app/models/saved/forecast/arima_c0000000-0000-0000-0000-000000000001.joblib",
    "last_modified": "2025-10-14T10:50:17.428511"
  },
  "prophet": {
    "trained": true,
    "path": "/app/models/saved/forecast/prophet_c0000000-0000-0000-0000-000000000001.joblib",
    "last_modified": "2025-10-15T11:10:34.726634"
  }
}
```

---

### POST `/api/v1/forecast/train/arima`
**Train ARIMA Forecast Model**

Train a new ARIMA forecast model.

**Request Body:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "start_date": "2025-09-01T00:00:00Z",
  "end_date": "2025-10-15T23:59:59Z",
  "model_params": {
    "p": 1,
    "d": 1,
    "q": 1
  }
}
```

**Response:**
```json
{
  "success": true,
  "model_type": "arima",
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "training_samples": 1440,
  "model_path": "/app/models/saved/forecast/arima_...",
  "metrics": {
    "mape": 5.6,
    "rmse": 2.3
  }
}
```

---

### POST `/api/v1/forecast/train/prophet`
**Train Prophet Forecast Model**

Train a new Facebook Prophet forecast model.

**Request Body:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "start_date": "2025-09-01T00:00:00Z",
  "end_date": "2025-10-15T23:59:59Z",
  "seasonality_mode": "multiplicative"
}
```

---

### POST `/api/v1/forecast/predict`
**Generate Energy Forecast**

Predict future energy consumption.

**Request Body:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "model_type": "prophet",
  "forecast_hours": 24
}
```

**Response:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "machine_name": "Compressor-1",
  "model_type": "prophet",
  "forecast_start": "2025-10-15T12:00:00+00:00",
  "forecast_end": "2025-10-16T12:00:00+00:00",
  "predictions": [
    {
      "timestamp": "2025-10-15T13:00:00+00:00",
      "predicted_energy": 52.3,
      "lower_bound": 48.1,
      "upper_bound": 56.5,
      "confidence": 0.95
    },
    {
      "timestamp": "2025-10-15T14:00:00+00:00",
      "predicted_energy": 54.1,
      "lower_bound": 49.8,
      "upper_bound": 58.4,
      "confidence": 0.95
    }
  ],
  "total_predicted_energy": 1256.7
}
```

**Use Case for OVOS:**
- Voice: "What's the energy forecast for Compressor-1 tomorrow?"
- Response: "Tomorrow's forecast for Compressor-1 is 1,256 kilowatt hours, with hourly predictions available."

---

### GET `/api/v1/forecast/demand`
**Get Demand Forecast**

Get demand forecast (power, not energy).

**Parameters:**
- `machine_id` (query, required)
- `hours` (query, required): Forecast horizon in hours

---

### GET `/api/v1/forecast/peak`
**Get Peak Demand Forecast**

Predict when peak demand will occur.

**Parameters:**
- `machine_id` (query, required)
- `date` (query, required): Target date

**Response:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "date": "2025-10-16",
  "predicted_peak": {
    "value": 58.7,
    "unit": "kW",
    "timestamp": "2025-10-16T14:30:00+00:00"
  }
}
```

**Use Case for OVOS:**
- Voice: "When will Compressor-1 peak tomorrow?"
- Response: "Predicted peak is 58.7 kilowatts at 2:30 PM."

---

### POST `/api/v1/forecast/optimal-schedule`
**Get Optimal Schedule**

Calculate optimal machine operation schedule to minimize cost.

**Request Body:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "date": "2025-10-16",
  "constraints": {
    "production_target": 1000,
    "max_runtime_hours": 20
  }
}
```

**Response:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "date": "2025-10-16",
  "schedule": [
    {
      "hour": 0,
      "operate": false,
      "reason": "High tariff period"
    },
    {
      "hour": 1,
      "operate": true,
      "expected_power": 45.2
    }
  ],
  "estimated_cost": 123.45,
  "estimated_energy": 890.5,
  "cost_savings": 45.67
}
```

**Use Case for OVOS:**
- Voice: "What's the optimal schedule for Compressor-1 tomorrow?"

---

## 📊 Visualizations

### GET `/api/v1/sankey/factories`
**List Factories for Sankey**

Get list of available factories.

**Response:**
```json
[
  {
    "id": "11111111-1111-1111-1111-111111111111",
    "name": "Demo Manufacturing Plant",
    "location": "Silicon Valley, CA, USA"
  }
]
```

---

### GET `/api/v1/sankey/data`
**Get Sankey Diagram Data**

Get energy flow data for Sankey visualization.

**Parameters:**
- `factory_id` (query, optional): Filter by factory
- `date` (query, optional): Target date (YYYY-MM-DD)

**Request:**
```bash
curl "http://localhost:8001/api/v1/sankey/data?factory_id=11111111-1111-1111-1111-111111111111&date=2025-10-14"
```

**Response:**
```json
{
  "nodes": [
    {
      "id": "grid",
      "name": "Grid",
      "level": 0
    },
    {
      "id": "factory_11111111-1111-1111-1111-111111111111",
      "name": "Demo Manufacturing Plant",
      "level": 1
    },
    {
      "id": "dept_..._Production Floor",
      "name": "Production Floor",
      "level": 2
    },
    {
      "id": "machine_c0000000-0000-0000-0000-000000000001",
      "name": "Compressor-1",
      "level": 3
    }
  ],
  "links": [
    {
      "source": "grid",
      "target": "factory_11111111-1111-1111-1111-111111111111",
      "value": 13618.77,
      "percentage": 60.19
    },
    {
      "source": "factory_11111111-1111-1111-1111-111111111111",
      "target": "dept_..._Production Floor",
      "value": 6234.56,
      "percentage": 45.8
    }
  ],
  "metadata": {
    "date": "2025-10-14",
    "total_energy": 22627.93,
    "factory_count": 2,
    "machine_count": 7
  }
}
```

**Use Case for OVOS:**
- Voice: "Show me energy flow for the Demo Plant"
- Processing: Generate Sankey visualization from data

---

### GET `/api/v1/heatmap/hourly`
**Get Hourly Heatmap Data**

Get hourly energy consumption data for heatmap visualization.

**Parameters:**
- `machine_id` (query, optional): Filter by machine
- `start_date` (query, required): Start date (YYYY-MM-DD)
- `end_date` (query, required): End date (YYYY-MM-DD)

**Response:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "machine_name": "Compressor-1",
  "start_date": "2025-10-01",
  "end_date": "2025-10-15",
  "data": [
    {
      "date": "2025-10-01",
      "hour": 0,
      "value": 45.2,
      "anomaly": false
    },
    {
      "date": "2025-10-01",
      "hour": 1,
      "value": 48.7,
      "anomaly": false
    }
  ]
}
```

**Use Case for OVOS:**
- Voice: "Show heatmap for Compressor-1 this month"

---

### GET `/api/v1/heatmap/daily`
**Get Daily Heatmap Data**

Get daily aggregated data for heatmap.

**Parameters:** Same as `/heatmap/hourly`

---

### GET `/api/v1/comparison/available`
**Get Available Machines for Comparison**

Get list of machines that can be compared.

**Request:**
```bash
curl http://localhost:8001/api/v1/comparison/available
```

**Response:**
```json
[
  {
    "id": "c0000000-0000-0000-0000-000000000001",
    "name": "Compressor-1",
    "type": "compressor",
    "location": "Demo Plant - Utilities"
  },
  {
    "id": "c0000000-0000-0000-0000-000000000006",
    "name": "Compressor-EU-1",
    "type": "compressor",
    "location": "Europe Plant - Utilities"
  }
]
```

---

### GET `/api/v1/comparison/machines`
**Compare Multiple Machines**

Compare performance metrics across machines.

**Parameters:**
- `machine_ids` (query, required): Comma-separated UUIDs
- `start_date` (query, required): Start date
- `end_date` (query, required): End date
- `metrics` (query, optional): Comma-separated metrics (energy, power, sec, cost)

**Request:**
```bash
curl "http://localhost:8001/api/v1/comparison/machines?machine_ids=c0000000-0000-0000-0000-000000000001,c0000000-0000-0000-0000-000000000006&start_date=2025-10-01&end_date=2025-10-15&metrics=energy,cost"
```

**Response:**
```json
{
  "start_date": "2025-10-01",
  "end_date": "2025-10-15",
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

**Use Case for OVOS:**
- Voice: "Compare Compressor-1 and Compressor-EU-1 energy usage this week"
- Response: "Compressor-1 used 1,234 kilowatt hours costing $185. Compressor-EU-1 used 1,567 kilowatt hours costing $235. Compressor-1 is the better performer."

---

## 🎯 Model Performance

### POST `/api/v1/model-performance/retrain/trigger`
**Trigger Model Retraining**

Manually trigger model retraining for a machine.

**Parameters:**
- `model_type` (query, required): Model type (`baseline`, `anomaly`, `forecast_arima`, `forecast_prophet`)
- `machine_id` (query, required): Machine UUID
- `trigger_type` (query, required): Trigger type (`manual`, `scheduled`, `drift`)
- `reason` (query, optional): Reason for retraining

**Request:**
```bash
curl -X POST "http://localhost:8001/api/v1/model-performance/retrain/trigger?model_type=baseline&machine_id=c0000000-0000-0000-0000-000000000001&trigger_type=manual&reason=Testing"
```

**Response:**
```json
{
  "triggered": true,
  "trigger_type": "manual",
  "reason": "Testing",
  "training_job_id": "ce524bc0-80a8-460e-902c-228cf921da37",
  "estimated_completion": "2025-10-15T12:05:39.049062+00:00"
}
```

**Or if training already in progress:**
```json
{
  "triggered": false,
  "trigger_type": "manual",
  "reason": "Training already in progress",
  "training_job_id": null
}
```

---

### GET `/api/v1/model-performance/metrics/trend`
**Get Model Performance Trend**

Get performance metrics over time for a model.

**Parameters:**
- `model_type` (query, required): Model type
- `machine_id` (query, required): Machine UUID
- `days` (query, optional): Number of days (default: 30)

**Response:**
```json
{
  "model_type": "baseline",
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "machine_name": "Compressor-1",
  "metrics": [
    {
      "evaluation_date": "2025-10-15T10:53:42+00:00",
      "model_version": 1,
      "r_squared": 0.8600,
      "rmse": 14.500000,
      "mae": 9.700000,
      "drift_detected": false,
      "drift_score": 0.1
    }
  ],
  "trend_direction": "improving",
  "degradation_rate": null
}
```

---

### POST `/api/v1/model-performance/drift/check`
**Check for Model Drift**

Check if a model has drifted and needs retraining.

**Request Body:**
```json
{
  "model_type": "baseline",
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "evaluation_start": "2025-10-14T00:00:00Z",
  "evaluation_end": "2025-10-15T00:00:00Z"
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
  },
  "baseline_performance": {
    "r_squared": 0.96,
    "rmse": 1.7
  }
}
```

---

### GET `/api/v1/model-performance/alerts/active`
**Get Active Performance Alerts**

Get alerts for models showing degraded performance.

**Parameters:**
- `machine_id` (query, optional): Filter by machine
- `model_type` (query, optional): Filter by model type

**Response:**
```json
[
  {
    "alert_id": "alert-uuid",
    "model_type": "baseline",
    "machine_id": "c0000000-0000-0000-0000-000000000001",
    "machine_name": "Compressor-1",
    "alert_type": "performance_degradation",
    "severity": "medium",
    "message": "R² dropped below threshold (0.85)",
    "current_value": 0.82,
    "threshold": 0.85,
    "created_at": "2025-10-15T10:00:00+00:00",
    "status": "unresolved"
  }
]
```

---

## ⏰ Scheduler

### GET `/api/v1/scheduler/status`
**Get Scheduler Status**

Get status of all scheduled jobs.

**Response:**
```json
{
  "enabled": true,
  "running": true,
  "job_count": 4,
  "jobs": [
    {
      "id": "baseline_retrain",
      "name": "Weekly Baseline Retraining",
      "next_run": "2025-10-20T02:00:00+00:00",
      "trigger": "cron[month='*', day='*', day_of_week='0', hour='2', minute='0']"
    },
    {
      "id": "anomaly_detect",
      "name": "Hourly Anomaly Detection",
      "next_run": "2025-10-15T12:05:00+00:00",
      "trigger": "cron[month='*', day='*', day_of_week='*', hour='*', minute='5']"
    },
    {
      "id": "kpi_calculate",
      "name": "Daily KPI Calculation",
      "next_run": "2025-10-16T00:30:00+00:00",
      "trigger": "cron[month='*', day='*', day_of_week='*', hour='0', minute='30']"
    },
    {
      "id": "training_cleanup",
      "name": "Training Job Cleanup",
      "next_run": "2025-10-15T12:15:00+00:00",
      "trigger": "cron[month='*', day='*', day_of_week='*', hour='*', minute='15']"
    }
  ]
}
```

---

### POST `/api/v1/scheduler/trigger/{job_id}`
**Manually Trigger Scheduled Job**

Force a scheduled job to run immediately.

**Parameters:**
- `job_id` (path, required): Job ID (`baseline_retrain`, `anomaly_detect`, `kpi_calculate`, `training_cleanup`)

**Response:**
```json
{
  "success": true,
  "job_id": "anomaly_detect",
  "message": "Job triggered successfully"
}
```

---

## ❌ Error Handling

### HTTP Status Codes

- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid parameters or request body
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

### Error Response Format

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

**Simple Error:**
```json
{
  "detail": "Machine not found"
}
```

### Common Error Messages

- `"Machine not found"` - Invalid machine_id
- `"No data available for this period"` - Time range has no data
- `"Model not trained"` - No baseline/forecast model exists
- `"Training already in progress"` - Cannot start duplicate training
- `"Invalid time range"` - start_time must be before end_time

---

## 💡 Examples for OVOS Integration

### Example 1: Voice - "What's the status?"

```python
import requests

response = requests.get("http://localhost:8001/api/v1/health")
data = response.json()

# OVOS Response
if data['status'] == 'healthy':
    speak(f"System is healthy. {data['active_machines']} machines active. "
          f"{data['recent_anomalies']} recent anomalies.")
```

---

### Example 2: Voice - "How much energy did Compressor-1 use today?"

```python
from datetime import datetime

machine_id = "c0000000-0000-0000-0000-000000000001"
today = datetime.now().date()
start = f"{today}T00:00:00Z"
end = f"{today}T23:59:59Z"

response = requests.get(
    f"http://localhost:8001/api/v1/timeseries/energy",
    params={
        "machine_id": machine_id,
        "start_time": start,
        "end_time": end,
        "interval": "1hour"
    }
)
data = response.json()

total_energy = sum(point['value'] for point in data['data_points'])
speak(f"Compressor-1 used {total_energy:.2f} kilowatt hours today.")
```

---

### Example 3: Voice - "Compare energy usage of Compressor-1 and HVAC-Main"

```python
machine_ids = [
    "c0000000-0000-0000-0000-000000000001",  # Compressor-1
    "c0000000-0000-0000-0000-000000000002"   # HVAC-Main
]

response = requests.get(
    "http://localhost:8001/api/v1/comparison/machines",
    params={
        "machine_ids": ",".join(machine_ids),
        "start_date": "2025-10-01",
        "end_date": "2025-10-15",
        "metrics": "energy,cost"
    }
)
data = response.json()

for machine in data['machines']:
    speak(f"{machine['machine_name']} used "
          f"{machine['metrics']['total_energy']:.2f} kilowatt hours, "
          f"costing ${machine['metrics']['total_cost']:.2f}")

best = data['best_performer']
speak(f"The best performer is {best}")
```

---

### Example 4: Voice - "Are there any anomalies?"

```python
response = requests.get(
    "http://localhost:8001/api/v1/anomaly/active"
)
data = response.json()

if data['total_count'] == 0:
    speak("No active anomalies detected.")
else:
    speak(f"There are {data['total_count']} active anomalies.")
    
    for anomaly in data['anomalies']:
        if anomaly['severity'] in ['high', 'critical']:
            speak(f"{anomaly['machine_name']} has a {anomaly['severity']} "
                  f"severity {anomaly['anomaly_type']}. "
                  f"{anomaly['description']}")
```

---

### Example 5: Voice - "What's the energy forecast for tomorrow?"

```python
machine_id = "c0000000-0000-0000-0000-000000000001"

response = requests.post(
    "http://localhost:8001/api/v1/forecast/predict",
    json={
        "machine_id": machine_id,
        "model_type": "prophet",
        "forecast_hours": 24
    }
)
data = response.json()

total = data['total_predicted_energy']
speak(f"Tomorrow's forecast for {data['machine_name']} is "
      f"{total:.2f} kilowatt hours.")
```

---

### Example 6: Voice - "What are the KPIs for Compressor-1 this month?"

```python
from datetime import datetime

machine_id = "c0000000-0000-0000-0000-000000000001"
now = datetime.now()
start = now.replace(day=1, hour=0, minute=0, second=0).isoformat() + "Z"
end = now.isoformat() + "Z"

response = requests.get(
    "http://localhost:8001/api/v1/kpi/all",
    params={
        "machine_id": machine_id,
        "start": start,
        "end": end
    }
)
data = response.json()

kpis = data['kpis']
speak(f"This month's KPIs for {data['machine_name']}: ")
speak(f"Specific Energy Consumption: {kpis['sec']['value']} kilowatt hours per unit")
speak(f"Peak Demand: {kpis['peak_demand']['value']} kilowatts")
speak(f"Load Factor: {kpis['load_factor']['percent']} percent")
speak(f"Energy Cost: ${kpis['energy_cost']['value']}")
speak(f"Carbon Emissions: {kpis['carbon_intensity']['value']} kilograms CO2")
```

---

### Example 7: Voice - "Trigger retraining for Compressor-1 baseline model"

```python
machine_id = "c0000000-0000-0000-0000-000000000001"

response = requests.post(
    "http://localhost:8001/api/v1/model-performance/retrain/trigger",
    params={
        "model_type": "baseline",
        "machine_id": machine_id,
        "trigger_type": "manual",
        "reason": "User requested via voice"
    }
)
data = response.json()

if data['triggered']:
    speak(f"Training started. Job ID: {data['training_job_id']}. "
          f"Estimated completion: {data['estimated_completion']}")
else:
    speak(f"Cannot start training: {data['reason']}")
```

---

## 🔍 Advanced Queries

### Multi-Machine Aggregation

Get total energy for all machines in a factory:

```python
# 1. Get all machines
machines = requests.get("http://localhost:8001/api/v1/machines").json()

# 2. Get energy for each machine
total_energy = 0
for machine in machines:
    response = requests.get(
        "http://localhost:8001/api/v1/timeseries/energy",
        params={
            "machine_id": machine['id'],
            "start_time": "2025-10-15T00:00:00Z",
            "end_time": "2025-10-15T23:59:59Z",
            "interval": "1day"
        }
    )
    data = response.json()
    if data['data_points']:
        total_energy += sum(p['value'] for p in data['data_points'])

speak(f"Total factory energy today: {total_energy:.2f} kilowatt hours")
```

---

### Peak Detection Across Multiple Machines

Find which machine has the highest peak demand:

```python
machines = requests.get("http://localhost:8001/api/v1/machines").json()
peaks = []

for machine in machines:
    response = requests.get(
        "http://localhost:8001/api/v1/kpi/peak-demand",
        params={
            "machine_id": machine['id'],
            "start": "2025-10-15T00:00:00Z",
            "end": "2025-10-15T23:59:59Z"
        }
    )
    data = response.json()
    if data['peak_demand']['value']:
        peaks.append({
            'name': machine['name'],
            'peak': data['peak_demand']['value'],
            'time': data['peak_demand']['timestamp']
        })

highest = max(peaks, key=lambda x: x['peak'])
speak(f"{highest['name']} has the highest peak demand at "
      f"{highest['peak']} kilowatts, occurring at {highest['time']}")
```

---

## 🎨 Response Formatting for Voice

### Best Practices

1. **Round Numbers:** `{value:.2f}` for 2 decimal places
2. **Units:** Always say the unit (kilowatts, kilowatt hours, percent)
3. **Time:** Convert ISO timestamps to natural language
4. **Context:** Include machine name and timeframe

### Example Formatter

```python
def format_energy(kwh):
    """Format energy for voice"""
    if kwh < 1:
        return f"{kwh * 1000:.0f} watt hours"
    elif kwh > 1000:
        return f"{kwh / 1000:.2f} megawatt hours"
    else:
        return f"{kwh:.2f} kilowatt hours"

def format_time(iso_timestamp):
    """Format timestamp for voice"""
    from datetime import datetime
    dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
    return dt.strftime("%I:%M %p on %B %d")

def format_percentage(decimal):
    """Format decimal as percentage"""
    return f"{decimal * 100:.1f} percent"
```

---

## 📚 Additional Resources

### Interactive API Documentation

Visit the auto-generated Swagger UI:
```
http://localhost:8001/docs
```

This provides:
- Complete API reference
- Try-it-out functionality
- Request/response examples
- Schema definitions

### Web UI

For visual exploration:
```
http://localhost:8001/ui/
```

Includes dashboards for:
- Baseline training
- Anomaly detection
- KPI visualization
- Forecasting
- Model performance tracking

---

## 🚀 Quick Start Checklist

- [ ] Verify service is running: `GET /api/v1/health`
- [ ] List available machines: `GET /api/v1/machines`
- [ ] Test time series data: `GET /api/v1/timeseries/energy`
- [ ] Test KPI retrieval: `GET /api/v1/kpi/all`
- [ ] Check for anomalies: `GET /api/v1/anomaly/recent`
- [ ] Get forecast models: `GET /api/v1/forecast/models/{machine_id}`
- [ ] Test visualization data: `GET /api/v1/sankey/data`

---

**Document Version:** 1.0.0  
**Last Updated:** October 15, 2025  
**Status:** ✅ All APIs Tested and Verified
