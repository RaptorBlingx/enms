# EnMS Project Charter & Knowledge Base
**Last Updated**: 2025-10-08
**Version**: 1.0.0
**Status**: Phase 1 - Foundation Setup

---

## 🎯 PROJECT OVERVIEW

### Mission
Build a production-ready, open-source Energy Management System (EnMS) for industrial facilities as part of the WASABI Project (https://wasabiproject.eu/).

### Key Objectives
1. ISO 50001-compliant energy monitoring and analytics
2. Real-time data ingestion from factory equipment
3. ML-powered insights (baselines, forecasting, anomaly detection)
4. Voice interface ready (OVOS integration)
5. Zero-touch deployment via Docker
6. Modular, API-first architecture
7. Open-source release with comprehensive documentation

### Success Criteria
- Handles 5+ machines with variable data frequencies (1s, 10s, 30s intervals)
- Calculates core KPIs: SEC, Peak Demand, Load Factor, Energy Cost, Carbon Intensity
- Provides regression analysis UI with driver selection
- Exposes REST APIs for external integration (OVOS, third-party systems)
- Single-command deployment: `./setup.sh`
- Production-grade error handling and logging

---

## 🏗️ SYSTEM ARCHITECTURE

### Service Topology
```
Nginx (API Gateway & Reverse Proxy)
  ├── Unified Portal (HTML/CSS/JS)
  ├── Grafana (Dashboards)
  ├── Node-RED (Data Ingestion)
  ├── Analytics Service (FastAPI - Python)
  ├── Query Service (FastAPI - Python)
  └── Simulator Service (FastAPI - Python)

Data Layer:
  ├── PostgreSQL + TimescaleDB (Time-series storage)
  ├── Redis (Cache & Pub/Sub)
  └── MQTT Broker (Mosquitto - Message bus)
```

### Key Design Decisions

1. **TimescaleDB over InfluxDB**: 
   - Rationale: SQL familiarity, ACID compliance, joins for analytics
   - Trade-off: Slightly lower write throughput (acceptable for factory scenarios)

2. **Separate Analytics & Query Services**:
   - Analytics: Heavy ML computations, scheduled jobs
   - Query: Fast API responses, NLP parsing for voice
   - Allows independent scaling

3. **Node-RED for ETL**:
   - Visual programming for factory operators
   - Easy debugging of data flows
   - Built-in MQTT support

4. **FastAPI over Flask**:
   - Async support for high concurrency
   - Auto-generated OpenAPI docs
   - Pydantic validation

5. **Nginx as Gateway**:
   - Single entry point (security)
   - SSL termination
   - Rate limiting
   - Load balancing ready

---

## 🗂️ PROJECT STRUCTURE
```
/enms/                                   # Root directory on Ubuntu server
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env.example
├── .gitignore
├── README.md
├── setup.sh                            # One-command installer
├── docs/                               # Full documentation
├── nginx/                              # API Gateway
├── portal/                             # Unified Web Portal
├── grafana/                            # Dashboards & provisioning
├── nodered/                            # ETL flows
├── database/                           # PostgreSQL + TimescaleDB
├── simulator/                          # Factory data generator
├── analytics/                          # ML service (FastAPI)
├── query-service/                      # API service (FastAPI)
├── mqtt/                               # Mosquitto broker
├── redis/                              # Cache & pub/sub
└── scripts/                            # Utility scripts
```

---

## 📊 DATA MODEL

### Core Entities

**factories**
- id (UUID, PK)
- name (VARCHAR)
- location (VARCHAR)
- created_at (TIMESTAMPTZ)

**machines** (SEUs)
- id (UUID, PK)
- factory_id (UUID, FK)
- name (VARCHAR)
- type (ENUM: compressor, hvac, motor, pump, injection_molding)
- rated_power_kw (DECIMAL)
- created_at (TIMESTAMPTZ)

**energy_readings** (Hypertable - partitioned by time)
- time (TIMESTAMPTZ, PK)
- machine_id (UUID, PK)
- power_kw (DECIMAL)
- energy_kwh (DECIMAL)
- voltage_v (DECIMAL)
- current_a (DECIMAL)
- power_factor (DECIMAL)
- frequency_hz (DECIMAL)

**production_data** (Hypertable)
- time (TIMESTAMPTZ, PK)
- machine_id (UUID, PK)
- production_count (INTEGER)
- throughput_units_per_hour (DECIMAL)
- operating_mode (VARCHAR)
- recipe_id (VARCHAR)

**environmental_data** (Hypertable)
- time (TIMESTAMPTZ, PK)
- machine_id (UUID, PK)
- outdoor_temp_c (DECIMAL)
- indoor_temp_c (DECIMAL)
- humidity_percent (DECIMAL)
- pressure_bar (DECIMAL)

**machine_status** (Current state)
- machine_id (UUID, PK)
- is_running (BOOLEAN)
- last_updated (TIMESTAMPTZ)
- operating_hours_total (DECIMAL)
- alert_level (ENUM: normal, warning, critical)

### Continuous Aggregates (TimescaleDB)
- energy_readings_1min
- energy_readings_15min
- energy_readings_1hour
- energy_readings_1day

---

## 🤖 FACTORY SIMULATOR SPECIFICATION

### 5 Machine Types (Variable Frequencies)

1. **Compressor** (1-second intervals)
   - Power: 15-75 kW
   - Pressure: 6-8 bar
   - Flow rate: 100-500 m³/h
   - Anomaly: Gradual pressure loss (leak simulation)

2. **HVAC System** (10-second intervals)
   - Power: 20-150 kW
   - Supply temp: 7-12°C
   - Return temp: 12-18°C
   - COP: 2.5-4.0
   - Driver: Outdoor temperature

3. **Conveyor Motor** (10-second intervals)
   - Power: 5-30 kW
   - Speed: 0-100% (VFD)
   - Production count linked
   - Load factor varies

4. **Hydraulic Pump** (30-second intervals)
   - Power: 10-50 kW
   - Pressure: 150-200 bar
   - Cycle-based operation
   - Batch-linked

5. **Injection Molding Machine** (30-second intervals)
   - Power: 25-200 kW
   - Cycle phases: heating → injection → cooling
   - Material-dependent energy
   - Cycle time: 60-180 seconds

### Realistic Patterns
- **Daily**: 3 shifts (06:00-14:00, 14:00-22:00, 22:00-06:00)
- **Weekly**: Reduced production on weekends
- **Seasonal**: Summer HVAC load higher
- **Random**: ±5% noise, occasional anomalies (10% probability/day)

### Simulator Control API
```
POST   /simulator/start
POST   /simulator/stop
GET    /simulator/status
PUT    /simulator/config
POST   /simulator/inject-anomaly
```

---

## 📈 KEY PERFORMANCE INDICATORS (KPIs)

### Calculations (SQL Functions)

1. **Specific Energy Consumption (SEC)**
```sql
   SEC = SUM(energy_kwh) / SUM(production_count)
   Unit: kWh/unit
```

2. **Peak Demand**
```sql
   Peak = MAX(power_kw) over 15-minute rolling window
   Unit: kW
```

3. **Load Factor**
```sql
   Load_Factor = AVG(power_kw) / MAX(power_kw)
   Unitless: 0-1
```

4. **Energy Cost**
```sql
   Cost = SUM(energy_kwh * tariff_rate)
   Unit: USD
   Tariff: Time-of-use (peak/off-peak)
```

5. **Carbon Intensity**
```sql
   CO2 = SUM(energy_kwh) * emission_factor
   Unit: kg CO2
   Factor: 0.45 kg CO2/kWh (grid average)
```

---

## 🧠 MACHINE LEARNING MODELS

### 1. Energy Baseline (EnB) - Multiple Linear Regression

**Purpose**: ISO 50001 compliance - establish normalized baseline

**Formula**:
```
Energy = β₀ + β₁(Production) + β₂(Temp) + β₃(Hours) + β₄(Material) + ε
```

**Drivers (Independent Variables)**:
- Production count (units/hour)
- Outdoor temperature (°C)
- Operating hours (hours)
- Material moisture content (%)
- Pressure (bar)

**Training**:
- Historical data: Last 90 days
- Minimum samples: 1000 observations
- Validation: R² > 0.80, p-values < 0.05
- Retraining: Weekly (scheduled job)

**Output**:
- Baseline Performance Deviation = Actual - Predicted
- Positive deviation = inefficiency/fault

### 2. Anomaly Detection - Isolation Forest

**Purpose**: Real-time fault detection

**Features**:
- Power deviation from baseline
- Pressure anomalies
- Temperature spikes
- Efficiency drops

**Thresholds**:
- Warning: 2σ deviation
- Critical: 3σ deviation

### 3. Forecasting - Prophet + ARIMA

**Purpose**: Demand prediction for load scheduling

**Horizons**:
- Short-term (next hour): ARIMA
- Medium-term (next day): Prophet
- Long-term (next week): Prophet with regressors

**Use Case**: Avoid peak demand charges by shifting loads

---

## 🔌 OVOS INTEGRATION ARCHITECTURE

### Integration Point: Query Service

**Voice Command Flow**:
```
User Voice → OVOS (STT) → NLP Parser → Query Service API → Response → OVOS (TTS)
```

**Sample NLP Mappings**:
- "energy consumption compressor last hour" → `/api/v1/energy/machine/compressor-1?duration=1h`
- "machines using more than 50 kilowatts" → `/api/v1/energy/machines?min_power=50`
- "temperature effect on HVAC" → `/api/v1/analytics/correlation?machine=hvac-1&driver=temperature`

**Query Service Responsibilities**:
- Parse natural language intents
- Map to SQL/API queries
- Format responses for TTS
- Cache common queries (Redis)
- Log all voice interactions

**API Contract** (for OVOS developer):
```
POST /api/v1/voice/query
Request:
{
  "intent": "energy_consumption",
  "entities": {
    "machine": "compressor-1",
    "timeframe": "last_hour"
  }
}

Response:
{
  "text": "Compressor 1 consumed 45.3 kilowatt-hours in the last hour",
  "data": {
    "value": 45.3,
    "unit": "kWh",
    "timeframe": "2025-10-08T14:00-15:00"
  }
}
```

---

## 🔐 SECURITY & PRODUCTION READINESS

### Authentication & Authorization
- JWT tokens for API access
- API keys for service-to-service
- Role-based access control (RBAC)
- Rate limiting: 100 requests/minute per IP

### Data Protection
- Input validation (Pydantic models)
- SQL injection prevention (parameterized queries)
- XSS protection (Content Security Policy)
- HTTPS enforcement (Nginx SSL)

### Monitoring & Logging
- Health check endpoints: `/health`
- Structured logging (JSON format)
- Error tracking
- Performance metrics (response times)

### Backup & Recovery
- Automated daily database backups
- Retention: 30 days
- Restore script: `./scripts/restore.sh`

---

## 🚀 DEPLOYMENT STRATEGY

### Zero-Touch Installation
```bash
git clone https://github.com/wasabi/enms.git
cd enms
cp .env.example .env
# Edit .env with your settings
./setup.sh
```

### Setup Script Actions
1. Check dependencies (Docker, Docker Compose)
2. Pull/build all images
3. Initialize database schema
4. Seed sample data (optional)
5. Start all services
6. Run health checks
7. Display access URLs

### Environment Variables
```
# Database
POSTGRES_USER=enms_user
POSTGRES_PASSWORD=<generated>
POSTGRES_DB=enms
TIMESCALEDB_TELEMETRY=off

# MQTT
MQTT_HOST=mqtt
MQTT_PORT=1883

# Services
GRAFANA_PORT=3000
NODERED_PORT=1880
ANALYTICS_PORT=8001
QUERY_PORT=8002
SIMULATOR_PORT=8003

# Security
JWT_SECRET=<generated>
API_KEY=<generated>
```

---

## 📋 IMPLEMENTATION PHASES

### ✅ Phase 1: Foundation (Week 1-2)
**Status**: READY TO START

**Deliverables**:
- Project structure created in `/enms/`
- Docker Compose with all services
- PostgreSQL + TimescaleDB schema
- Nginx API gateway configured
- Basic health checks

**Tasks**:
1. Create folder structure
2. Write docker-compose.yml
3. Create Dockerfiles for each service
4. Design database schema
5. Initialize TimescaleDB (hypertables, continuous aggregates)
6. Configure Nginx reverse proxy
7. Create .env.example
8. Write setup.sh script

---

### Phase 2: Data Pipeline (Week 3)
**Status**: PENDING

**Deliverables**:
- Factory simulator (5 machines, variable frequencies)
- MQTT broker operational
- Node-RED flows (ingestion → validation → storage)
- Data flowing end-to-end

---

### Phase 3: Visualization (Week 4)
**Status**: PENDING

**Deliverables**:
- 5 Grafana dashboards provisioned
- Variables configured (machine selection)
- Real-time updates working

---

### Phase 4: Analytics Service (Week 5-6)
**Status**: PENDING

**Deliverables**:
- FastAPI service with ML models
- Baseline regression implemented
- Anomaly detection working
- Forecast API endpoints
- Custom analytics UI (driver selection)

---

### Phase 5: Unified Portal (Week 7)
**Status**: PENDING

**Deliverables**:
- Central navigation hub
- Service cards with status
- Embedded iframes (Grafana, Node-RED)
- System health dashboard

---

### Phase 6: OVOS Integration (Week 8)
**Status**: PENDING

**Deliverables**:
- Query Service API
- NLP parser for voice commands
- Redis caching
- API documentation for OVOS developer

---

### Phase 7: Production Hardening (Week 9)
**Status**: PENDING

**Deliverables**:
- Security implemented (JWT, rate limiting)
- Performance optimization
- Monitoring setup
- Load testing completed

---

### Phase 8: Open Source Release (Week 10)
**Status**: PENDING

**Deliverables**:
- GitHub repository published
- Documentation complete
- Demo video
- Release announcement

---

## 🛠️ DEVELOPMENT WORKFLOW

### Roles
- **Claude 4.5 (This Project)**: Architect, planner, problem solver
- **GitHub Copilot (Sonnet 4 in VS Code)**: Code implementer, assistant
- **Developer**: Decision maker, integrator, tester

### Session Management
When approaching chat limits:
1. Request checkpoint summary
2. Copy to Knowledge Base
3. Start new chat in project
4. Reference Knowledge Base for context

### Git Workflow
```bash
# Feature branch strategy
git checkout -b feature/simulator-service
# Make changes
git add .
git commit -m "feat: implement compressor machine simulator"
git push origin feature/simulator-service
# Merge to main after testing
```

---

## 📚 REFERENCE LINKS

- WASABI Project: https://wasabiproject.eu/
- ISO 50001: https://www.iso.org/iso-50001-energy-management.html
- TimescaleDB Docs: https://docs.timescale.com/
- FastAPI: https://fastapi.tiangolo.com/
- Node-RED: https://nodered.org/docs/
- Grafana: https://grafana.com/docs/
- OVOS: https://openvoiceos.org/

---

## 🎯 CURRENT STATUS

**Active Phase**: Phase 1 - Foundation Setup  
**Next Action**: Create project structure and Docker Compose  
**Blockers**: None  
**Last Updated**: 2025-10-08

---

END OF KNOWLEDGE BASE v1.0.0
```