# EnMS Factory Requirements for Romanian Manufacturing SME

**Document Version:** 1.1  
**Date:** December 1, 2025  
**Project:** WASABI - Energy Management System with Chatbot & OVOS Voice Integration  
**EnMS Version:** v3.0.0  
**Contact:** [Your Contact Information]

---

## Executive Summary

This document outlines the technical requirements for a Romanian manufacturing SME (factory) to successfully install and implement the EnMS (Energy Management System) with integrated chatbot and OVOS voice assistant. 

**Key Capabilities:**
- **ISO 50001 Compliance**: Full Energy Performance Indicator (EnPI) tracking, SEU management, baseline regression
- **Multi-Energy Support**: Electricity (kWh), Natural Gas (m³), Steam (kg), Compressed Air (Nm³)
- **ML-Powered Analytics**: Baseline models (85-99% R² accuracy), anomaly detection (Isolation Forest), demand forecasting (Prophet + ARIMA)
- **Voice Interface**: OVOS integration for natural language energy queries
- **Text Chatbot**: Rasa-powered conversational assistant (Turkish/English)
- **Real-Time Monitoring**: TimescaleDB with continuous aggregates, sub-100ms query response

---

## 1. MINIMUM REQUIREMENTS (Must Have)

### 1.1 Energy Metering Infrastructure

| Requirement | Specification | Purpose |
|-------------|---------------|---------|
| **Digital Energy Meters** | Modbus RTU/TCP or MQTT-capable | Real-time power (kW) and energy (kWh) readings |
| **Meter Coverage** | All Significant Energy Users (SEUs) | Compressors, HVAC, motors, pumps, production equipment |
| **Data Granularity** | Minimum 1-minute intervals (1-second for compressors recommended) | Baseline training and anomaly detection require high-frequency data |
| **Parameters** | Power (kW), Energy (kWh) | Core metrics for KPI calculation |

**Multi-Energy Support (Built-in):**
The system natively supports 4 energy types. Factories using multiple energy sources get enhanced analysis:

| Energy Type | Unit | Example Machines | Sensors Required |
|-------------|------|------------------|------------------|
| **Electricity** | kWh | All electric equipment | Power meter |
| **Natural Gas** | m³ | Boilers, furnaces, ovens | Gas flow meter |
| **Steam** | kg | Heat exchangers, autoclaves | Steam flow meter |
| **Compressed Air** | Nm³ | Pneumatic equipment | Air flow meter |

**Supported Meter Protocols:**
- Modbus RTU (RS-485)
- Modbus TCP/IP
- MQTT (preferred - native integration via Node-RED)
- OPC-UA (via gateway)

**Meter Examples:**
- Schneider Electric PM5xxx series
- Siemens SENTRON PAC series
- Janitza UMG series
- Any IEC 62056 compliant meter with Modbus output

### 1.2 Network Infrastructure

| Requirement | Specification | Purpose |
|-------------|---------------|---------|
| **Internet Connection** | Stable broadband (min 10 Mbps) | Cloud connectivity, remote access, software updates |
| **Internal Network** | Ethernet (wired preferred) | Low-latency sensor data transmission |
| **Wi-Fi** | 2.4/5 GHz coverage in factory floor | OVOS voice device connectivity |
| **Firewall Ports** | Outbound HTTPS (443), MQTT (1883/8883) | Secure data transmission |

### 1.3 Server Infrastructure

**Option A: On-Premise Server (Recommended for Data Privacy)**

| Component | Minimum Specification | Recommended |
|-----------|----------------------|-------------|
| **CPU** | 4 cores | 8 cores |
| **RAM** | 8 GB | 16 GB |
| **Storage** | 100 GB SSD | 500 GB SSD |
| **OS** | Ubuntu 22.04 LTS or Debian 12 | Ubuntu 22.04 LTS |
| **Docker** | Version 20.10+ with Compose v2 | Latest stable |

**Storage Calculation:**
- ~5 machines × 1 reading/second × 86,400 seconds/day = ~432,000 readings/day
- With TimescaleDB compression (90% reduction): ~50 MB/day raw → ~5 MB/day compressed
- 1 year retention: ~2 GB (compressed)
- Recommendation: 100 GB provides ample room for logs, models, and growth

**Option B: Cloud Hosting (Alternative)**
- AWS EC2 t3.medium or equivalent (4 vCPU, 8 GB RAM)
- Azure VM Standard_B2s
- Google Cloud e2-medium
- DigitalOcean Droplet (8 GB)

**Note:** All data remains under factory control. Cloud option requires VPN or secure tunnel to factory network for meter access.

### 1.4 MQTT Broker

| Requirement | Specification |
|-------------|---------------|
| **Broker** | Eclipse Mosquitto 2.x (recommended) or any MQTT 3.1.1/5.0 broker |
| **Location** | On-premise server or cloud |
| **Topics** | `factory/{factory_id}/{machine_id}/{data_type}` format |
| **Authentication** | Username/password (TLS recommended for production) |

---

## 2. SENSOR REQUIREMENTS BY MACHINE TYPE

The EnMS simulator currently models 6 machine types. Real factory implementation should aim to match these data requirements:

### 2.1 Compressors (Air Compressors)

**Data Frequency:** 1 second (high-frequency for load/unload cycle detection)

| Sensor | Unit | Required | Protocol | Notes |
|--------|------|----------|----------|-------|
| Power meter | kW, kWh | ✅ Yes | Modbus/MQTT | 3-phase recommended |
| Pressure sensor | bar | ✅ Yes | 4-20mA/Modbus | Setpoint: 6-8 bar typical |
| Flow meter | m³/h | ⭐ Recommended | Pulse/Modbus | For SEC calculation |
| Vibration sensor | mm/s | Optional | Modbus | Predictive maintenance |
| Oil/Machine temperature | °C | Optional | 4-20mA/Modbus | Fault detection |

**ML Features Used:**
- `avg_pressure_bar`, `avg_flow_rate_m3h`, `total_production_count`, `outdoor_temp_c`

### 2.2 HVAC Systems

**Data Frequency:** 10 seconds

| Sensor | Unit | Required | Protocol | Notes |
|--------|------|----------|----------|-------|
| Power meter | kW, kWh | ✅ Yes | Modbus/MQTT | Main chiller/AHU power |
| Indoor temperature | °C | ✅ Yes | 4-20mA/Modbus | Zone temperatures |
| Outdoor temperature | °C | ✅ Yes | 4-20mA/Modbus | Critical for baseline normalization |
| Supply air temperature | °C | ⭐ Recommended | 4-20mA/Modbus | For COP calculation |
| Return air temperature | °C | ⭐ Recommended | 4-20mA/Modbus | For COP calculation |
| Chilled water supply/return | °C | Optional | 4-20mA/Modbus | Advanced analytics |
| Humidity (indoor/outdoor) | % | Optional | 4-20mA/Modbus | Comfort correlation |

**ML Features Used:**
- `avg_outdoor_temp_c`, `avg_indoor_temp_c`, `avg_cop`, `avg_supply_air_temp_c`

### 2.3 Motors/Conveyors

**Data Frequency:** 10 seconds

| Sensor | Unit | Required | Protocol | Notes |
|--------|------|----------|----------|-------|
| Power meter | kW, kWh | ✅ Yes | Modbus/MQTT | VFD may provide this |
| Production count | units | ✅ Yes | PLC/Counter | Linked to conveyor output |
| Speed sensor | % or RPM | ⭐ Recommended | VFD/Modbus | VFD speed reference |
| Motor temperature | °C | Optional | 4-20mA/Modbus | Overload protection |

**ML Features Used:**
- `total_production_count`, `avg_speed_percent`, `avg_outdoor_temp_c`

### 2.4 Hydraulic Pumps

**Data Frequency:** 30 seconds

| Sensor | Unit | Required | Protocol | Notes |
|--------|------|----------|----------|-------|
| Power meter | kW, kWh | ✅ Yes | Modbus/MQTT | Motor power |
| Pressure sensor | bar | ✅ Yes | 4-20mA/Modbus | System pressure |
| Flow rate | m³/h or L/min | ⭐ Recommended | Pulse/Modbus | Efficiency calculation |
| Oil temperature | °C | Optional | 4-20mA/Modbus | Viscosity affects efficiency |

**ML Features Used:**
- `avg_pressure_bar`, `avg_flow_rate_m3h`, `total_production_count`

### 2.5 Injection Molding Machines

**Data Frequency:** 30 seconds (or per cycle)

| Sensor | Unit | Required | Protocol | Notes |
|--------|------|----------|----------|-------|
| Power meter | kW, kWh | ✅ Yes | Modbus/MQTT | Total machine power |
| Cycle count | units | ✅ Yes | PLC/Counter | Parts produced per cycle |
| Good/Bad count | units | ⭐ Recommended | PLC | Quality tracking |
| Mold temperature | °C | Optional | 4-20mA/Modbus | Process correlation |
| Barrel temperature | °C | Optional | 4-20mA/Modbus | Material-specific |
| Cycle time | seconds | Optional | PLC | Efficiency metric |

**ML Features Used:**
- `total_production_count`, `total_production_count_good`, `avg_machine_temp_c`

### 2.6 Boilers (Multi-Energy Example)

**Data Frequency:** 30 seconds

| Sensor | Unit | Required | Protocol | Notes |
|--------|------|----------|----------|-------|
| Electrical power meter | kW, kWh | ✅ Yes | Modbus/MQTT | Fans, pumps, controls |
| Gas flow meter | m³/h | ✅ Yes (if gas) | Pulse/Modbus | Natural gas consumption |
| Steam flow meter | kg/h | ⭐ Recommended | Modbus | Steam production |
| Stack temperature | °C | Optional | 4-20mA | Combustion efficiency |
| Water inlet/outlet temp | °C | Optional | 4-20mA | Heat balance |

**Note:** Boilers create 3 SEUs in the system (electricity + natural_gas + steam)

---

## 3. PRODUCTION DATA REQUIREMENTS

### 3.1 Minimum Production Data

| Data Point | Description | Source | Interval |
|------------|-------------|--------|----------|
| **Production Count** | Units produced | PLC/Counter | Per unit or hourly |
| **Good Units** | Quality-passed units | PLC/Counter | Per unit or hourly |
| **Bad Units** | Rejected/scrap units | PLC/Counter | Per unit or hourly |
| **Operating Mode** | Running/Idle/Maintenance | PLC status | Real-time |

### 3.2 Optional Production Data

| Data Point | Description | Purpose |
|------------|-------------|---------|
| Batch/Recipe ID | Product type identifier | Product-specific energy analysis |
| Operator ID | Shift assignment | Shift-based comparisons |
| Downtime Reason | Categorized stop causes | Availability analysis |
| Throughput | Units per hour | SEC (Specific Energy Consumption) calculation |

---

## 4. DIGITAL MANUFACTURING SYSTEMS (Integration Points)

### 4.1 Required Integration

| System | Integration Method | Data Exchanged |
|--------|-------------------|----------------|
| **Energy Meters** | Modbus/MQTT | Power, energy readings |
| **PLC/SCADA** (if exists) | OPC-UA, Modbus TCP | Production counts, machine status |

### 4.2 Good-to-Have Integrations

| System | Integration Method | Benefit |
|--------|-------------------|---------|
| **MES (Manufacturing Execution System)** | REST API, OPC-UA | Automated production data sync |
| **ERP System** | REST API, database link | Order-based energy tracking |
| **BMS (Building Management System)** | BACnet, Modbus | HVAC optimization, comfort vs. energy |
| **Weather Station** | HTTP API, Modbus | Temperature normalization for baselines |
| **Quality System** | Database/API | Energy per quality unit correlation |

---

## 5. GOOD-TO-HAVE REQUIREMENTS

### 5.1 Enhanced Electrical Monitoring

| Sensor | Purpose | Benefit |
|--------|---------|---------|
| **Power Factor** | Monitor electrical efficiency | Reduce reactive power penalties |
| **THD (Total Harmonic Distortion)** | Power quality monitoring | Prevent equipment damage |
| **Three-Phase Currents (L1, L2, L3)** | Load balancing | Identify phase imbalances |
| **Voltage Monitoring** | Power quality | Detect voltage sags/swells |
| **Frequency** | Grid stability | Monitor grid health |

### 5.2 Environmental Sensors

| Sensor | Location | Purpose |
|--------|----------|---------|
| **Outdoor Weather Station** | Building exterior | Temperature normalization for ISO 50001 |
| **Indoor Climate Sensors** | Production areas | Comfort vs. energy optimization |
| **Humidity Sensors** | Critical areas | Process correlation |

### 5.3 Sub-Metering

| Level | Description | Benefit |
|-------|-------------|---------|
| **Main Meter** | Factory total | Overall consumption tracking |
| **Department Meters** | Production, offices, utilities | Departmental accountability |
| **Machine Meters** | Individual SEUs | Precise machine-level analytics |
| **Lighting Meters** | Lighting circuits | Identify lighting savings opportunities |

---

## 6. VOICE ASSISTANT (OVOS) REQUIREMENTS

### 6.1 Hardware

| Component | Specification | Notes |
|-----------|---------------|-------|
| **OVOS Device** | Raspberry Pi 4 (4GB+) or Mark II | Pi 4 recommended for performance |
| **Microphone** | USB array microphone | ReSpeaker 2-Mic or 4-Mic recommended |
| **Speaker** | 3.5mm or USB speaker | Any powered speaker works |
| **Network** | Wi-Fi or Ethernet to EnMS server | Must reach EnMS API |

### 6.2 Network Access

| Requirement | Specification |
|-------------|---------------|
| **EnMS API Access** | HTTP to EnMS server port 8001 (analytics) |
| **STT Service** | Local Vosk (offline) or cloud Whisper API |
| **TTS Service** | Local Piper (offline) or cloud service |

### 6.3 Supported Voice Commands (Examples)

The OVOS skill supports natural language energy queries:

**Energy Queries:**
- "What's the energy consumption of Compressor-1 in the last hour?"
- "Show me machines using more than 50 kilowatts"
- "What was yesterday's total energy consumption?"

**Baseline & Prediction:**
- "Train baseline for Compressor-1"
- "What's the expected energy for HVAC-Main?"
- "How accurate is the Compressor-1 model?"

**Anomaly & Alerts:**
- "Are there any anomalies detected?"
- "Show me warnings for the hydraulic pump"

**Analysis:**
- "How is temperature affecting HVAC efficiency today?"
- "What are the main energy drivers for Compressor-1?"
- "Compare energy usage this week vs last week"

### 6.4 OVOS Integration Status

| Component | Status | Notes |
|-----------|--------|-------|
| Backend APIs | ✅ Ready | 40+ endpoints available |
| Voice-friendly responses | ✅ Ready | Natural language TTS responses |
| Multi-turn conversations | ⚠️ In Development | Guided training workflows |
| OVOS Skill | ⚠️ In Development | Burak's responsibility |

---

## 7. CHATBOT REQUIREMENTS

### 7.1 Infrastructure (Included in Docker Stack)

| Component | Technology | Port |
|-----------|------------|------|
| **Rasa NLU/Core** | Rasa 3.x | 5005 |
| **Chat Backend** | Express.js | 5006 |
| **Chat Widget** | React/TypeScript | Embedded in portal |

### 7.2 Chatbot Capabilities

**Current Languages:**
- Turkish (primary)
- English (secondary)

**Supported Intents (Rasa-based):**
- Greetings and small talk
- Energy consumption queries
- Machine status inquiries
- Anomaly and alert questions
- Basic analytics requests

### 7.3 User Access

| Requirement | Specification |
|-------------|---------------|
| **Web Browser** | Modern browser (Chrome, Firefox, Edge, Safari) |
| **Network** | Access to factory network or VPN |
| **Mobile** | Responsive design for tablets/phones |
| **Widget** | Floating chat button on portal pages |

### 7.4 Deployment Notes

- Rasa server requires 2-3 GB RAM
- Pre-trained model included (`chatbot/models/`)
- Custom training requires Rasa CLI on host or separate container
- Widget auto-loads on all portal pages via `chatbot-widget.js`

---

## 8. INSTALLATION PHASE REQUIREMENTS

### 8.1 Pre-Installation (Factory Responsibility) - 2 Weeks Before

| Task | Description | Owner | Verification |
|------|-------------|-------|--------------|
| **Identify SEUs** | List all Significant Energy Users with rated power | Factory + Energy Manager | Machine list with kW ratings |
| **Install energy meters** | Digital meters on all SEUs (Modbus/MQTT) | Factory Electrician | Meter commissioning reports |
| **Verify meter network** | Meters accessible via Modbus TCP or MQTT | Factory IT | ping/telnet test to meter IPs |
| **Prepare server** | Physical or VM with Ubuntu 22.04 | Factory IT | SSH access confirmed |
| **Configure network** | Server on same network as meters, internet access | Factory IT | Network diagram |
| **Open firewall ports** | Outbound: 443 (HTTPS), 1883 (MQTT optional) | Factory IT | Port test results |
| **Provide credentials** | SSH access, network credentials | Factory IT | Secure handoff |
| **Factory floor map** | Layout showing machine locations | Factory | PDF or CAD file |

### 8.2 Installation Phase (Joint Responsibility) - Day 1-2

| Task | Duration | Team | Details |
|------|----------|------|---------|
| **Server setup** | 1 hour | Factory IT + WASABI | Docker, Docker Compose installation |
| **Deploy EnMS stack** | 2 hours | WASABI | `docker-compose up -d` (11 containers) |
| **Configure MQTT** | 1 hour | WASABI | Connect to factory broker or deploy Mosquitto |
| **Node-RED flows** | 4-8 hours | WASABI + Factory | Create flows for each meter type |
| **Machine registration** | 2 hours | WASABI | Add machines to database with metadata |
| **Verify data flow** | 2 hours | WASABI + Factory | Confirm readings in Grafana |
| **Dashboard configuration** | 2 hours | WASABI | Configure Grafana variables, alerts |
| **Initial training** | 2 hours | WASABI + Factory | Basic portal navigation, Grafana usage |

### 8.3 Post-Installation Validation (Week 1)

| Task | Owner | Success Criteria |
|------|-------|------------------|
| **Data gap check** | Factory + WASABI | <1% missing readings over 24 hours |
| **Value sanity check** | WASABI | Power values within rated ranges |
| **Grafana dashboard review** | Factory | All machines visible, no "No data" panels |
| **Node-RED flow stability** | WASABI | No flow crashes in 24 hours |
| **User access test** | Factory | All designated users can log in |

---

## 9. IMPLEMENTATION PHASE REQUIREMENTS

### 9.1 Baseline Training Phase (30-90 days)

**Why 30-90 Days?**
The ML baseline models require sufficient data to capture:
- Weekly production patterns (weekday vs weekend)
- Shift variations (3 shifts standard)
- Temperature correlation (seasonal if possible)
- Normal operational variance

| Requirement | Description | Impact on Model |
|-------------|-------------|-----------------|
| **Minimum Data** | 30 days continuous | R² = 70-85% (acceptable) |
| **Recommended Data** | 90 days continuous | R² = 85-99% (optimal) |
| **Normal Operations** | Factory operates as usual | Captures real patterns |
| **Production Records** | Daily/shift counts available | SEC calculation possible |
| **Temperature Data** | Outdoor temp accessible | HVAC normalization works |

**Auto-Training Schedule:**
- Models auto-retrain weekly (Sunday 2 AM)
- Configurable via `SCHEDULER_ENABLED=true` in `.env`

### 9.2 Training Requirements (User Education)

| Training | Audience | Duration | Topics |
|----------|----------|----------|--------|
| **Executive Overview** | Management | 1 hour | KPIs, ISO 50001, business value |
| **Dashboard Usage** | Operators, Supervisors | 4 hours | Grafana navigation, alerts, machine drilldown |
| **Energy Analysis** | Energy Manager | 4 hours | Baseline interpretation, anomaly investigation |
| **Chatbot/Voice** | All users | 1 hour | Voice commands, chatbot queries |
| **API Integration** | IT team | 4 hours | REST API, MQTT topics, Node-RED customization |
| **Administration** | IT team | 4 hours | Docker, backups, troubleshooting, logs |

### 9.3 Ongoing Maintenance

| Task | Frequency | Owner | Details |
|------|-----------|-------|---------|
| **Data integrity check** | Weekly | Factory | Review data gaps in Grafana |
| **Database backup** | Daily (automated) | System | Cron job runs at 3 AM |
| **Grafana backup** | Every 10 min (automated) | System | Dashboards exported to git |
| **Docker image updates** | Monthly | Factory IT + WASABI | Security patches |
| **ML model retraining** | Weekly (automated) | System | APScheduler job |
| **Anomaly review** | Daily | Factory Energy Manager | Review critical alerts |
| **Performance report** | Quarterly | Factory + WASABI | ISO 50001 EnPI review |

---

## 10. DATA PRIVACY & SECURITY

### 10.1 Data Ownership

- All collected data remains property of the factory
- Data is stored locally on factory server (Option A) or in dedicated cloud instance
- No data shared with third parties without explicit consent

### 10.2 Security Measures (System Provides)

| Measure | Implementation |
|---------|----------------|
| **API Authentication** | JWT tokens |
| **Database Encryption** | PostgreSQL SSL/TLS |
| **MQTT Security** | Username/password + TLS |
| **Rate Limiting** | 100 requests/minute per IP |
| **Audit Logging** | All API calls logged |

### 10.3 Factory Responsibility

- Maintain network security (firewall, VPN)
- Control physical access to server
- Manage user credentials
- Regular security updates on host OS

---

## 11. WHAT THE FACTORY WILL RECEIVE

### 11.1 Deployed System Components (Docker Stack)

| Container | Purpose | Technology |
|-----------|---------|------------|
| `enms-nginx` | API Gateway & Web Portal | Nginx 1.25 |
| `enms-postgres` | Time-series database | TimescaleDB (PostgreSQL 16) |
| `enms-redis` | Caching & real-time events | Redis 7 |
| `enms-nodered` | Data ingestion (ETL) | Node-RED |
| `enms-grafana` | Dashboards & visualization | Grafana 10.2 |
| `enms-analytics` | ML models & KPIs | FastAPI (Python) |
| `enms-query-service` | Voice/NLP API | FastAPI (Python) |
| `enms-simulator` | Data generator (dev only) | FastAPI (Python) |
| `enms-rasa` | Chatbot NLU engine | Rasa 3.x |
| `enms-chatbot` | Chat backend | Express.js |

### 11.2 Pre-Built Grafana Dashboards

| Dashboard | Purpose |
|-----------|---------|
| **Energy Overview** | Factory-wide energy consumption, trends, costs |
| **Machine Monitoring** | Individual SEU status, real-time power |
| **Production Analysis** | SEC, OEE correlation, shift comparisons |
| **HVAC Performance** | COP tracking, temperature vs. power |
| **ISO 50001 EnPI** | Baseline deviation, compliance status |
| **Anomaly Dashboard** | Active alerts, historical anomalies |
| **Comparison** | Machine vs machine, period vs period |

### 11.3 ML Capabilities (Out of the Box)

| Capability | Algorithm | Purpose |
|------------|-----------|---------|
| **Energy Baseline** | Multiple Linear Regression | ISO 50001 EnB, deviation detection |
| **Anomaly Detection** | Isolation Forest | Real-time fault detection |
| **Demand Forecast** | Prophet + ARIMA | Short/medium-term prediction |
| **KPI Calculation** | SQL Functions | SEC, Load Factor, Peak Demand |
| **Model Explainer** | Feature importance | "What drives energy consumption?" |

### 11.4 API Endpoints (40+ Available)

**Categories:**
- Machine management (`/api/v1/machines/*`)
- Energy data (`/api/v1/energy/*`)
- Baseline models (`/api/v1/baseline/*`)
- Anomaly detection (`/api/v1/anomaly/*`)
- Forecasting (`/api/v1/forecast/*`)
- KPIs (`/api/v1/kpi/*`)
- SEU management (`/api/v1/seus/*`)
- Performance engine (`/api/v1/performance/*`)

**Documentation:** Swagger UI at `http://{server}:8001/docs`

---

## 12. SUMMARY CHECKLIST

### Minimum Requirements ✅

- [ ] Digital energy meters on all significant machines (SEUs)
- [ ] Stable internet connection (10+ Mbps)
- [ ] Internal network connectivity (Ethernet preferred)
- [ ] Server: 4 cores, 8GB RAM, 100GB SSD, Ubuntu 22.04
- [ ] MQTT broker (Mosquitto) or existing industrial MQTT
- [ ] Production count data available (PLC, counters, or manual)
- [ ] Factory floor contact for installation support
- [ ] IT contact for network/server configuration

### Good-to-Have ✅

- [ ] Three-phase electrical parameters (voltage, current per phase)
- [ ] Power factor monitoring
- [ ] Outdoor temperature sensor or weather API access
- [ ] MES/ERP integration for automated production data
- [ ] Sub-metering by department or process
- [ ] Vibration sensors on rotating equipment
- [ ] Pressure sensors on compressed air systems
- [ ] BMS integration for HVAC data

### Voice/Chatbot Integration ✅

- [ ] Raspberry Pi 4 or OVOS Mark II device
- [ ] USB microphone (ReSpeaker)
- [ ] Speaker for voice responses
- [ ] Wi-Fi coverage in desired voice assistant location

---

## 13. CONTACT & SUPPORT

**For Technical Questions:**
- [Technical Contact Email]
- [Technical Contact Phone]

**For Project Coordination:**
- [Project Manager Email]
- [Project Manager Phone]

**Documentation:**
- Full API documentation: `http://{server}/api/docs`
- User guides: `http://{server}/portal/help`
- WASABI Project: https://wasabiproject.eu/

---

## APPENDIX A: EnMS Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    NGINX (API Gateway)                       │
│                      Port 8080                               │
└────┬────────────────────────────────────────────────────┬───┘
     │                                                     │
     ▼                                                     ▼
┌─────────────────────┐                        ┌──────────────────┐
│   Web Interface     │                        │  OVOS Voice      │
│   Grafana           │                        │  Chatbot         │
│   Node-RED          │                        └──────────────────┘
└─────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     Core Services                            │
├──────────────┬─────────────────┬─────────────────────────────┤
│  Node-RED    │    Analytics    │    Query Service            │
│  (ETL)       │    (ML/KPIs)    │    (NLP/Voice)              │
└──────┬───────┴────────┬────────┴────────┬────────────────────┘
       │                │                 │
       └────────────────┴─────────────────┘
                        │
              ┌─────────┴─────────┐
              │   TimescaleDB     │
              │   PostgreSQL      │
              └───────────────────┘
       ┌──────────────┬──────────────┐
       │     MQTT     │    Redis     │
       │   Broker     │   Cache      │
       └──────────────┴──────────────┘
```

---

## APPENDIX B: Sample MQTT Message Format

### Energy Reading
```json
{
  "time": "2025-12-01T10:30:00Z",
  "machine_id": "compressor-1",
  "power_kw": 45.5,
  "energy_kwh": 0.126,
  "voltage_v": 398.5,
  "current_a": 82.3,
  "power_factor": 0.92,
  "frequency_hz": 50.01
}
```

### Production Data
```json
{
  "time": "2025-12-01T10:30:00Z",
  "machine_id": "injection-mold-1",
  "production_count": 125,
  "production_count_good": 123,
  "production_count_bad": 2,
  "operating_mode": "running",
  "speed_percent": 85.5
}
```

### Environmental Data
```json
{
  "time": "2025-12-01T10:30:00Z",
  "machine_id": "hvac-main",
  "outdoor_temp_c": 5.2,
  "indoor_temp_c": 22.1,
  "outdoor_humidity_percent": 65.0,
  "indoor_humidity_percent": 48.5
}
```

---

## APPENDIX C: Supported Machine Types

| Type | Data Interval | Key Sensors |
|------|---------------|-------------|
| Compressor | 1 second | Power, pressure, flow, temperature |
| HVAC | 10 seconds | Power, temperatures (indoor, outdoor, supply, return), humidity |
| Motor/Conveyor | 10 seconds | Power, speed, temperature |
| Hydraulic Pump | 30 seconds | Power, pressure, flow, oil temperature |
| Injection Molding | 30 seconds | Power, cycle count, temperatures |
| Boiler | 30 seconds | Power/fuel, steam flow, temperatures |
| Other | Configurable | Power (minimum) |

---

**End of Document**

*This document is part of the WASABI Project EnMS implementation package.*
