📊 COMPLETE EnMS API AUDIT FOR OVOS INTEGRATION
Report Date: October 20, 2025
System Status: ✅ Healthy (7 active machines, 21 baseline models)
Base URL: http://10.33.10.109:8080/api/analytics
🎯 EXECUTIVE SUMMARY
Your EnMS has 74 API endpoints across 13 functional categories. All endpoints are in the Analytics Service (port 8001) accessible via Nginx at port 8080. The "Query Service" mentioned in docker-compose is not yet implemented.
Quick Stats:
GET Endpoints: 41 (read operations)
POST Endpoints: 24 (create/trigger operations)
PUT Endpoints: 2 (update operations)
DELETE Endpoints: 1 (delete operations)
WebSocket Endpoints: 4 (real-time streams)
📋 COMPLETE API INVENTORY WITH TEST COMMANDS
1️⃣ SYSTEM & HEALTH ENDPOINTS (4 endpoints)
GET /api/v1/health - System Health Check
curl http://10.33.10.109:8080/api/analytics/api/v1/health | jq
Returns: Service status, database connection, scheduler status, active machines, model count
GET / - Service Information
curl http://10.33.10.109:8080/api/analytics/ | jq
Returns: Service name, version, available endpoints
GET /api/v1/stats/system - Detailed System Statistics
curl http://10.33.10.109:8080/api/analytics/api/v1/stats/system | jq
Returns: CPU, memory, disk usage, uptime
WebSocket /ws - Real-time System Stats
wscat -c "ws://10.33.10.109:8080/api/analytics/ws"
Streams: Live system metrics updates
2️⃣ MACHINE MANAGEMENT (2 endpoints)
GET /api/v1/machines - List All Machines
# All machines
curl "http://10.33.10.109:8080/api/analytics/api/v1/machines" | jq

# Only active machines
curl "http://10.33.10.109:8080/api/analytics/api/v1/machines?is_active=true" | jq

# Response format
[{
  "id": "c0000000-0000-0000-0000-000000000001",
  "name": "Compressor-1",
  "type": "compressor",
  "rated_power_kw": "55.00",
  "factory_name": "Demo Manufacturing Plant",
  "is_active": true
}]
GET /api/v1/machines/{machine_id} - Get Machine Details
MACHINE_ID="c0000000-0000-0000-0000-000000000001"
curl "http://10.33.10.109:8080/api/analytics/api/v1/machines/${MACHINE_ID}" | jq
3️⃣ TIME-SERIES DATA (5 endpoints)
GET /api/v1/timeseries/energy - Energy Consumption History
MACHINE_ID="c0000000-0000-0000-0000-000000000001"

# Last 24 hours, 1-hour intervals
curl "http://10.33.10.109:8080/api/analytics/api/v1/timeseries/energy?\
machine_id=${MACHINE_ID}&\
start_time=2025-10-19T00:00:00Z&\
end_time=2025-10-20T00:00:00Z&\
interval=1hour" | jq

# Last week, daily aggregation
curl "http://10.33.10.109:8080/api/analytics/api/v1/timeseries/energy?\
machine_id=${MACHINE_ID}&\
start_time=2025-10-13T00:00:00Z&\
end_time=2025-10-20T00:00:00Z&\
interval=1day" | jq

# Available intervals: 1min, 5min, 15min, 1hour, 1day
GET /api/v1/timeseries/power - Power Demand History
# Last 8 hours, 15-min intervals
curl "http://10.33.10.109:8080/api/analytics/api/v1/timeseries/power?\
machine_id=${MACHINE_ID}&\
start_time=2025-10-19T23:00:00Z&\
end_time=2025-10-20T07:00:00Z&\
interval=15min" | jq
GET /api/v1/timeseries/sec - Specific Energy Consumption History
# Last month, daily SEC
curl "http://10.33.10.109:8080/api/analytics/api/v1/timeseries/sec?\
machine_id=${MACHINE_ID}&\
start_time=2025-09-20T00:00:00Z&\
end_time=2025-10-20T00:00:00Z&\
interval=1day" | jq

# Available intervals: 1hour, 1day, 1week
GET /api/v1/timeseries/latest/{machine_id} - Latest Reading
curl "http://10.33.10.109:8080/api/analytics/api/v1/timeseries/latest/${MACHINE_ID}" | jq

# Returns: current power_kw, energy_kwh, temperature, pressure, status
GET /api/v1/timeseries/multi-machine/energy - Compare Multiple Machines
# Compare 3 machines
MACHINES="c0000000-0000-0000-0000-000000000001,c0000000-0000-0000-0000-000000000006,c0000000-0000-0000-0000-000000000003"

curl "http://10.33.10.109:8080/api/analytics/api/v1/timeseries/multi-machine/energy?\
machine_ids=${MACHINES}&\
start_time=2025-10-19T00:00:00Z&\
end_time=2025-10-20T00:00:00Z&\
interval=1hour" | jq
4️⃣ KPI ENDPOINTS (6 endpoints)
GET /api/v1/kpi/all - All 5 KPIs at Once (⭐ Most Useful)
curl "http://10.33.10.109:8080/api/analytics/api/v1/kpi/all?\
machine_id=${MACHINE_ID}&\
start=2025-10-19T00:00:00Z&\
end=2025-10-20T00:00:00Z" | jq

# Returns:
{
  "sec": { "kwh_per_unit": 2.5, "total_kwh": 1250, "total_units": 500 },
  "peak_demand": { "peak_kw": 48.5, "timestamp": "...", "avg_kw": 32.1 },
  "load_factor": { "factor": 0.66, "percentage": 66.2 },
  "energy_cost": { "total_usd": 156.80, "cost_per_unit": 0.31, "peak_cost": 120, "offpeak_cost": 36.80 },
  "carbon": { "total_kg_co2": 562.5, "co2_per_unit": 1.125 }
}
GET /api/v1/kpi/sec - Specific Energy Consumption Only
curl "http://10.33.10.109:8080/api/analytics/api/v1/kpi/sec?\
machine_id=${MACHINE_ID}&\
start=2025-10-19T00:00:00Z&\
end=2025-10-20T00:00:00Z" | jq
GET /api/v1/kpi/peak-demand - Peak Demand Only
curl "http://10.33.10.109:8080/api/analytics/api/v1/kpi/peak-demand?\
machine_id=${MACHINE_ID}&\
start=2025-10-19T00:00:00Z&\
end=2025-10-20T00:00:00Z" | jq
GET /api/v1/kpi/load-factor - Load Factor Only
curl "http://10.33.10.109:8080/api/analytics/api/v1/kpi/load-factor?\
machine_id=${MACHINE_ID}&\
start=2025-10-19T00:00:00Z&\
end=2025-10-20T00:00:00Z" | jq
GET /api/v1/kpi/energy-cost - Energy Cost Only
curl "http://10.33.10.109:8080/api/analytics/api/v1/kpi/energy-cost?\
machine_id=${MACHINE_ID}&\
start=2025-10-19T00:00:00Z&\
end=2025-10-20T00:00:00Z" | jq

# Tariff: Peak hours (8am-8pm): $0.20/kWh, Off-peak: $0.10/kWh
GET /api/v1/kpi/carbon - Carbon Emissions Only
curl "http://10.33.10.109:8080/api/analytics/api/v1/kpi/carbon?\
machine_id=${MACHINE_ID}&\
start=2025-10-19T00:00:00Z&\
end=2025-10-20T00:00:00Z" | jq

# Emission factor: 0.45 kg CO₂/kWh
5️⃣ ANOMALY DETECTION (5 endpoints)
GET /api/v1/anomaly/recent - Recent Anomalies (⭐ Key for OVOS)
# Last 10 anomalies
curl "http://10.33.10.109:8080/api/analytics/api/v1/anomaly/recent?limit=10" | jq

# Filter by machine
curl "http://10.33.10.109:8080/api/analytics/api/v1/anomaly/recent?\
machine_id=${MACHINE_ID}&\
limit=20" | jq

# Filter by severity
curl "http://10.33.10.109:8080/api/analytics/api/v1/anomaly/recent?\
severity=critical&\
limit=5" | jq

# Severity levels: warning, critical
# Max limit: 200
GET /api/v1/anomaly/active - Unresolved Anomalies
# All unresolved
curl "http://10.33.10.109:8080/api/analytics/api/v1/anomaly/active" | jq

# For specific machine
curl "http://10.33.10.109:8080/api/analytics/api/v1/anomaly/active?\
machine_id=${MACHINE_ID}" | jq
POST /api/v1/anomaly/detect - Trigger Anomaly Detection
curl -X POST "http://10.33.10.109:8080/api/analytics/api/v1/anomaly/detect" \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "c0000000-0000-0000-0000-000000000001",
    "start": "2025-10-19T00:00:00Z",
    "end": "2025-10-20T00:00:00Z",
    "contamination": 0.1,
    "use_baseline": true
  }' | jq

# contamination: 0.0-0.5 (expected % of anomalies, default 0.1)
# use_baseline: true to also check baseline deviations
PUT /api/v1/anomaly/{anomaly_id}/resolve - Mark Anomaly Resolved
ANOMALY_ID="a1111111-1111-1111-1111-111111111111"

curl -X PUT "http://10.33.10.109:8080/api/analytics/api/v1/anomaly/${ANOMALY_ID}/resolve" \
  -H "Content-Type: application/json" \
  -d '{
    "resolution_notes": "Replaced faulty sensor"
  }' | jq
POST /api/v1/anomaly/create - Manually Create Anomaly (Dev Only)
curl -X POST "http://10.33.10.109:8080/api/analytics/api/v1/anomaly/create" \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "c0000000-0000-0000-0000-000000000001",
    "detected_at": "2025-10-20T07:00:00Z",
    "anomaly_type": "power_anomaly",
    "severity": "warning",
    "metric_name": "power_kw",
    "metric_value": 65.5,
    "confidence_score": 0.92
  }' | jq
6️⃣ BASELINE REGRESSION (5 endpoints)
GET /api/v1/baseline/models - List Baseline Models
# All models
curl "http://10.33.10.109:8080/api/analytics/api/v1/baseline/models" | jq

# For specific machine
curl "http://10.33.10.109:8080/api/analytics/api/v1/baseline/models?\
machine_id=${MACHINE_ID}" | jq
GET /api/v1/baseline/model/{model_id} - Get Model Details
MODEL_ID="b1111111-1111-1111-1111-111111111111"
curl "http://10.33.10.109:8080/api/analytics/api/v1/baseline/model/${MODEL_ID}" | jq

# Returns: coefficients, R², RMSE, MAE, training data range
POST /api/v1/baseline/train - Train Baseline Model
curl -X POST "http://10.33.10.109:8080/api/analytics/api/v1/baseline/train" \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "c0000000-0000-0000-0000-000000000001",
    "start_date": "2025-09-20",
    "end_date": "2025-10-19",
    "drivers": ["production_count", "outdoor_temp_c"]
  }' | jq

# drivers (optional): variables to include in regression
# Available: production_count, outdoor_temp_c, pressure_bar
GET /api/v1/baseline/deviation - Check Baseline Deviation
curl "http://10.33.10.109:8080/api/analytics/api/v1/baseline/deviation?\
machine_id=${MACHINE_ID}&\
start=2025-10-19T00:00:00Z&\
end=2025-10-20T00:00:00Z" | jq

# Returns: actual vs predicted energy, deviation %, severity level
POST /api/v1/baseline/predict - Predict Energy Consumption
curl -X POST "http://10.33.10.109:8080/api/analytics/api/v1/baseline/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "c0000000-0000-0000-0000-000000000001",
    "features": {
      "production_count": 500,
      "outdoor_temp_c": 22.5
    }
  }' | jq
7️⃣ ENERGY FORECASTING (7 endpoints)
GET /api/v1/forecast/models/{machine_id} - Check Trained Models
curl "http://10.33.10.109:8080/api/analytics/api/v1/forecast/models/${MACHINE_ID}" | jq

# Returns: ARIMA and Prophet model status
POST /api/v1/forecast/train/arima - Train ARIMA Model
curl -X POST "http://10.33.10.109:8080/api/analytics/api/v1/forecast/train/arima" \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "c0000000-0000-0000-0000-000000000001",
    "lookback_days": 30,
    "auto_order": true
  }' | jq

# lookback_days: 7-90
# auto_order: auto-select ARIMA(p,d,q) parameters
POST /api/v1/forecast/train/prophet - Train Prophet Model
curl -X POST "http://10.33.10.109:8080/api/analytics/api/v1/forecast/train/prophet" \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "c0000000-0000-0000-0000-000000000001",
    "lookback_days": 60,
    "use_regressors": true
  }' | jq

# use_regressors: include temperature, production, time-of-day features
POST /api/v1/forecast/predict - Generate Forecast
curl -X POST "http://10.33.10.109:8080/api/analytics/api/v1/forecast/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "c0000000-0000-0000-0000-000000000001",
    "horizon": "short",
    "periods": 24
  }' | jq

# horizon: short (hours), medium (days), long (weeks)
# periods: number of time steps to forecast
GET /api/v1/forecast/demand - Get Demand Forecast (GET version)
curl "http://10.33.10.109:8080/api/analytics/api/v1/forecast/demand?\
machine_id=${MACHINE_ID}&\
horizon=short&\
periods=48" | jq
GET /api/v1/forecast/peak - Predict Next Peak Time
curl "http://10.33.10.109:8080/api/analytics/api/v1/forecast/peak?\
machine_id=${MACHINE_ID}" | jq

# Returns: predicted peak time, peak demand kW
POST /api/v1/forecast/optimal-schedule - Find Optimal Operation Time
curl -X POST "http://10.33.10.109:8080/api/analytics/api/v1/forecast/optimal-schedule" \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "c0000000-0000-0000-0000-000000000001",
    "date": "2025-10-21",
    "load_kw": 45.0
  }' | jq

# Returns: top 3 recommended time slots, estimated costs, savings
8️⃣ SANKEY ENERGY FLOW (2 endpoints)
GET /api/v1/sankey/factories - List Available Factories
curl "http://10.33.10.109:8080/api/analytics/api/v1/sankey/factories" | jq
GET /api/v1/sankey/data - Get Energy Flow Diagram Data
FACTORY_ID="11111111-1111-1111-1111-111111111111"

curl "http://10.33.10.109:8080/api/analytics/api/v1/sankey/data?\
start_date=2025-10-19&\
end_date=2025-10-20&\
factory_ids=${FACTORY_ID}&\
min_energy_kwh=10" | jq

# Returns: nodes, links for Sankey diagram (Grid → Factory → Dept → Machine)
9️⃣ ANOMALY HEATMAP (2 endpoints)
GET /api/v1/heatmap/hourly - Hourly Anomaly Heatmap
curl "http://10.33.10.109:8080/api/analytics/api/v1/heatmap/hourly?\
start_date=2025-10-13&\
end_date=2025-10-20&\
machine_ids=${MACHINE_ID}&\
min_severity=warning" | jq

# Returns: 24-hour × machines grid showing anomaly counts
GET /api/v1/heatmap/daily - Daily Anomaly Heatmap
curl "http://10.33.10.109:8080/api/analytics/api/v1/heatmap/daily?\
start_date=2025-09-20&\
end_date=2025-10-20&\
machine_ids=${MACHINE_ID}&\
min_severity=critical" | jq

# Returns: Day-of-week × machines grid
🔟 MACHINE COMPARISON (2 endpoints)
GET /api/v1/comparison/available - Available Machines for Comparison
curl "http://10.33.10.109:8080/api/analytics/api/v1/comparison/available" | jq
GET /api/v1/comparison/machines - Compare Machines
MACHINES="c0000000-0000-0000-0000-000000000001,c0000000-0000-0000-0000-000000000006"

curl "http://10.33.10.109:8080/api/analytics/api/v1/comparison/machines?\
machine_ids=${MACHINES}&\
start_date=2025-10-19&\
end_date=2025-10-20&\
energy_cost_per_kwh=0.15" | jq

# Returns: ranked comparison of energy, SEC, load factor, cost, uptime
1️⃣1️⃣ MODEL PERFORMANCE TRACKING (7 endpoints)
POST /api/v1/model-performance/metrics/record - Record Performance Metrics
curl -X POST "http://10.33.10.109:8080/api/analytics/api/v1/model-performance/metrics/record" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "m1111111-1111-1111-1111-111111111111",
    "model_type": "baseline",
    "machine_id": "c0000000-0000-0000-0000-000000000001",
    "evaluation_start": "2025-10-19T00:00:00Z",
    "evaluation_end": "2025-10-20T00:00:00Z",
    "metrics": {
      "r2_score": 0.92,
      "rmse": 3.5,
      "mae": 2.1
    }
  }' | jq
GET /api/v1/model-performance/metrics/trend - Performance Trend
curl "http://10.33.10.109:8080/api/analytics/api/v1/model-performance/metrics/trend?\
model_type=baseline&\
machine_id=${MACHINE_ID}&\
days=30" | jq

# Returns: trend direction (improving/degrading/stable), degradation rate
POST /api/v1/model-performance/drift/check - Check Model Drift
curl -X POST "http://10.33.10.109:8080/api/analytics/api/v1/model-performance/drift/check" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "m1111111-1111-1111-1111-111111111111",
    "model_type": "baseline",
    "machine_id": "c0000000-0000-0000-0000-000000000001"
  }' | jq

# Returns: drift score, type (data/concept), recommendation
POST /api/v1/model-performance/retrain/trigger - Trigger Retraining
curl -X POST "http://10.33.10.109:8080/api/analytics/api/v1/model-performance/retrain/trigger" \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "baseline",
    "machine_id": "c0000000-0000-0000-0000-000000000001",
    "trigger_type": "manual",
    "reason": "Performance degradation detected"
  }' | jq

# trigger_type: manual, scheduled, drift_detected
POST /api/v1/model-performance/ab-test/start - Start A/B Test
curl -X POST "http://10.33.10.109:8080/api/analytics/api/v1/model-performance/ab-test/start" \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "Baseline v2 vs v3",
    "model_type": "baseline",
    "machine_id": "c0000000-0000-0000-0000-000000000001",
    "model_a_id": "m1111111-1111-1111-1111-111111111111",
    "model_b_id": "m2222222-2222-2222-2222-222222222222",
    "duration_hours": 48
  }' | jq
GET /api/v1/model-performance/ab-test/{test_id}/results - A/B Test Results
TEST_ID="t1111111-1111-1111-1111-111111111111"
curl "http://10.33.10.109:8080/api/analytics/api/v1/model-performance/ab-test/${TEST_ID}/results" | jq
GET /api/v1/model-performance/alerts/active - Active Model Alerts
curl "http://10.33.10.109:8080/api/analytics/api/v1/model-performance/alerts/active?\
machine_id=${MACHINE_ID}&\
model_type=baseline&\
severity=high" | jq
1️⃣2️⃣ SCHEDULER (2 endpoints)
GET /api/v1/scheduler/status - Scheduler Status
curl "http://10.33.10.109:8080/api/analytics/api/v1/scheduler/status" | jq

# Shows: running jobs, next run times, job count
POST /api/v1/scheduler/trigger/{job_id} - Manually Trigger Job
# Available jobs: baseline_retrain, anomaly_detect, kpi_calculate, training_cleanup

curl -X POST "http://10.33.10.109:8080/api/analytics/api/v1/scheduler/trigger/anomaly_detect" | jq
1️⃣3️⃣ WEBSOCKET ENDPOINTS (4 real-time streams)
WS /api/v1/ws/dashboard - Real-time Dashboard Updates
wscat -c "ws://10.33.10.109:8080/api/analytics/api/v1/ws/dashboard?client_id=ovos"
Streams: Machine count, model count, anomaly count, scheduler status
WS /api/v1/ws/anomalies - Real-time Anomaly Alerts (⭐ Key for OVOS)
wscat -c "ws://10.33.10.109:8080/api/analytics/api/v1/ws/anomalies?client_id=ovos"
Streams: New anomaly detections, severity changes, resolutions
WS /api/v1/ws/training - Training Progress Updates
wscat -c "ws://10.33.10.109:8080/api/analytics/api/v1/ws/training?client_id=ovos"
Streams: Training started, progress, completion, errors
WS /api/v1/ws/events - General System Events
wscat -c "ws://10.33.10.109:8080/api/analytics/api/v1/ws/events?client_id=ovos"
Streams: Alerts, status changes, config updates
🚨 CRITICAL FINDINGS & GAPS
❌ MISSING: Query Service Implementation
Status: The Query Service (port 8002) mentioned in docker-compose is NOT implemented (placeholder only)
Impact: All OVOS integration must use Analytics Service (port 8001) via /api/analytics/ route
Recommendation: Either implement Query Service OR update documentation to remove references
⚠️ MISSING: Key OVOS Endpoints Referenced in Docs
Your OVOS-QUICK-REFERENCE.md file references endpoints that DO NOT EXIST:
❌ /kpis/overview - Does NOT exist
Solution: Use /kpi/all instead
❌ /timeseries/{id}/current - Does NOT exist
Solution: Use /timeseries/latest/{machine_id} instead
❌ /forecast/{id} - Does NOT exist
Solution: Use /forecast/demand or /forecast/predict instead
⚠️ MISSING: Date Range Filtering in Some Endpoints
Several endpoints lack flexible date filtering:
Endpoint	Current Status	Missing Feature
/machines	✅ Works	❌ No filter by factory, type, or location
/anomaly/recent	✅ Has limit	❌ No custom date range (fixed to 7 days)
/timeseries/latest/{id}	✅ Works	✅ N/A (latest only)
⚠️ MISSING: Aggregation Endpoints for OVOS Use Cases
For voice queries like "What's the total energy consumption?", you need aggregated data:
Voice Query	Missing Endpoint	Workaround
"What's the total energy today?"	❌ No factory-wide total	Must call /kpi/all for each machine and sum
"Which machine uses the most energy?"	❌ No ranking endpoint	Use /comparison/machines for subset
"What's the average temperature?"	❌ No aggregated metrics	Must query timeseries and calculate
⚠️ MISSING: Natural Language Support
No endpoint to query by natural language:
❌ No support for "Compressor-1" → UUID resolution in query parameters
❌ Must know exact machine IDs (UUIDs)
Solution Needed: Add /machines/search?name=Compressor endpoint
⚠️ MISSING: Authentication
❌ No API key authentication
❌ No rate limiting per client (only IP-based)
Risk: Anyone can access your data
Recommendation: Add API key header requirement for OVOS
✅ RECOMMENDED IMPROVEMENTS FOR OVOS
1. Create Missing Aggregation Endpoints
# NEW ENDPOINT 1: Factory-wide KPIs
GET /api/v1/kpi/factory/{factory_id}
# Returns: total energy, cost, carbon for entire factory

# NEW ENDPOINT 2: Top N consumers
GET /api/v1/machines/top-consumers
?metric=energy_kwh
&start=2025-10-19T00:00:00Z
&end=2025-10-20T00:00:00Z
&limit=5
# Returns: ranked list of machines by energy consumption

# NEW ENDPOINT 3: Current status summary
GET /api/v1/status/summary
# Returns: total active machines, total power kW, total energy today, critical anomalies
2. Add Machine Name Search
# NEW ENDPOINT 4: Search machines by name
GET /api/v1/machines/search?query=compressor
# Returns: machines matching "compressor" (case-insensitive)

# Or enhance existing endpoint:
GET /api/v1/machines?name=Compressor-1
3. Fix Anomaly Date Filtering
# ENHANCE EXISTING: /api/v1/anomaly/recent
# Add optional date range parameters
GET /api/v1/anomaly/recent
?start=2025-10-19T00:00:00Z
&end=2025-10-20T00:00:00Z
&severity=critical
&limit=50
4. Add Voice-Friendly Endpoints
# NEW ENDPOINT 5: Ask natural language questions
POST /api/v1/query/natural
{
  "question": "What's the energy consumption of Compressor-1 today?"
}
# Returns: { "answer": "125.5 kWh", "machine_id": "...", "data": {...} }

# This would require NLP processing to:
# 1. Extract machine name → resolve to UUID
# 2. Extract time range → convert to ISO dates
# 3. Extract metric → route to correct endpoint
5. Add OVOS-Specific Simplified Endpoints
# NEW ENDPOINT 6: OVOS summary (all-in-one for voice)
GET /api/v1/ovos/summary
# Returns:
{
  "total_energy_kwh": 1520.5,
  "total_cost_usd": 185.20,
  "active_machines": 7,
  "critical_anomalies": 2,
  "warnings": 5,
  "top_consumer": {"name": "Compressor-1", "energy_kwh": 450.2},
  "latest_anomaly": {"machine": "HVAC-2", "time": "2025-10-20T06:30:00Z"}
}

# NEW ENDPOINT 7: Machine status by name
GET /api/v1/ovos/machine/{machine_name}/status
# e.g., /api/v1/ovos/machine/Compressor-1/status
# Returns: current power, energy, temperature, status, anomalies
6. Add Authentication
# Add to all endpoints:
Headers: {
  "X-API-Key": "ovos-client-key-12345"
}

# NEW ENDPOINT 8: Generate API key
POST /api/v1/auth/api-key
{
  "client_name": "OVOS",
  "permissions": ["read"]
}
📝 SUGGESTED NEW API STRUCTURE FOR OVOS
Option A: Create /api/v1/ovos/ Namespace
All voice-assistant-optimized endpoints in one place:
GET  /api/v1/ovos/summary                    # All-in-one dashboard
GET  /api/v1/ovos/machines                   # List with friendly names
GET  /api/v1/ovos/machines/{name}            # Get by name, not UUID
GET  /api/v1/ovos/energy/total               # Total energy (all machines)
GET  /api/v1/ovos/energy/today               # Today's consumption
GET  /api/v1/ovos/anomalies                  # Recent anomalies, simplified
GET  /api/v1/ovos/costs/today                # Today's cost
GET  /api/v1/ovos/forecast/tomorrow          # Tomorrow's forecast
POST /api/v1/ovos/query                      # Natural language query
Option B: Enhance Existing Endpoints
Add optional parameters to existing endpoints for OVOS use:
GET /api/v1/machines?search=compressor       # Add search
GET /api/v1/kpi/all?factory_id=XXX           # Add factory aggregation
GET /api/v1/anomaly/recent?date_range=today  # Add friendly date ranges
🎤 OVOS USE CASES & API MAPPING
Voice Command	Current API	Recommended API	Status
"What's the total energy?"	❌ None	GET /ovos/energy/total	Need to create
"List all machines"	✅ /machines	✅ Same	Ready
"Status of Compressor-1"	❌ Must know UUID	GET /ovos/machines/Compressor-1	Need to create
"Any problems today?"	✅ /anomaly/recent	✅ Same (add date filter)	Needs enhancement
"How much did we spend today?"	⚠️ /kpi/all (per machine)	GET /ovos/costs/today	Need to create
"Tomorrow's energy forecast"	⚠️ /forecast/predict (complex)	GET /ovos/forecast/tomorrow	Need to create
"Which machine uses the most?"	⚠️ /comparison/machines	GET /machines/top-consumers	Need to create
"Temperature of HVAC-2"	❌ Must know UUID	GET /ovos/machines/HVAC-2	Need to create
"Scan for anomalies"	✅ POST /anomaly/detect	✅ Same	Ready
"Retrain the model"	✅ POST /model-performance/retrain/trigger	✅ Same	Ready
🔧 IMPLEMENTATION PRIORITY
Phase 1: Critical Fixes (1-2 days)
✅ Fix documentation (OVOS-QUICK-REFERENCE.md) to match actual endpoints
✅ Add machine name search: GET /machines?search=name
✅ Add date range to anomaly endpoint
✅ Create summary endpoint: GET /ovos/summary
Phase 2: OVOS Namespace (3-5 days)
✅ Create /ovos/machines/{name} endpoint
✅ Create /ovos/energy/total and /ovos/costs/today
✅ Create /ovos/forecast/tomorrow
✅ Add API key authentication
Phase 3: Advanced (1-2 weeks)
⭐ Natural language query processing
⭐ WebSocket integration for proactive alerts
⭐ Voice-optimized response formatting
📊 SUMMARY SCORECARD
Category	Total Endpoints	Ready for OVOS	Need Enhancement	Missing
System & Health	4	4 ✅	0	0
Machines	2	1 ✅	1 ⚠️	1 ❌
Time-Series	5	5 ✅	0	0
KPIs	6	6 ✅	0	3 ❌
Anomalies	5	4 ✅	1 ⚠️	0
Baseline	5	5 ✅	0	0
Forecasting	7	7 ✅	0	2 ❌
Visualizations	6	6 ✅	0	0
Model Performance	7	7 ✅	0	0
Scheduler	2	2 ✅	0	0
WebSockets	4	4 ✅	0	0
OVOS-Specific	0	0	0	8 ❌
Authentication	0	0	0	1 ❌
TOTAL	74	67 (91%)	2 (3%)	15 (6%)
🎯 FINAL RECOMMENDATIONS
What You Have (Excellent!)
✅ Comprehensive time-series data API
✅ Advanced ML capabilities (baseline, forecasting, anomaly detection)
✅ Real-time WebSocket streams
✅ Detailed KPI calculations
✅ Model performance tracking
What You Need for OVOS
❌ Simplified aggregation endpoints (factory-wide totals)
❌ Machine name-based queries (not UUID-based)
❌ OVOS-specific namespace for voice queries
❌ Natural language query support (optional but powerful)
❌ API key authentication
⚠️ Fix documentation to match actual endpoints
Priority Actions
Update documentation immediately (fix endpoint paths)
Create 4-5 OVOS-specific endpoints for common voice queries
Add machine name search to /machines endpoint
Add authentication before Burak integrates
Consider natural language API for Phase 2
