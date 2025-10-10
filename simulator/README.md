# 🏭 EnMS Factory Simulator

Production-ready factory data simulator for the Energy Management System (EnMS). Generates realistic time-series data for 5 different machine types with variable data frequencies.

## 🎯 Overview

The simulator generates realistic industrial data including:
- **Energy readings** (power, voltage, current, power factor)
- **Production data** (output counts, throughput, quality)
- **Environmental data** (temperature, pressure, humidity, vibration)
- **Machine status** (running state, operating mode, alerts)

## 🔧 Machine Types

### 1. **Compressor** (1-second intervals)
- Air pressure control (6-8 bar)
- Load/unload cycles
- Flow rate simulation
- Power: 15-75 kW

### 2. **HVAC System** (10-second intervals)
- Temperature-dependent operation
- Multi-stage compressors
- COP (Coefficient of Performance) calculation
- Power: 20-150 kW

### 3. **Motor/Conveyor** (10-second intervals)
- VFD (Variable Frequency Drive) control
- Speed ramping
- Production count linked
- Power: 5-30 kW

### 4. **Hydraulic Pump** (30-second intervals)
- Cycle-based operation (build, hold, release)
- Pressure control (150-200 bar)
- Batch-linked production
- Power: 10-50 kW

### 5. **Injection Molding** (30-second intervals)
- Complex cycle phases (heating → injection → cooling → ejection)
- Material-dependent parameters
- Quality tracking
- Power: 25-200 kW

## 🚀 Quick Start

### Running with Docker

```bash
# Start the simulator service
docker-compose up -d simulator

# View logs
docker-compose logs -f simulator

# Check status
curl http://localhost:8003/health
```

### Running Standalone

```bash
cd /enms/simulator

# Install dependencies
pip install -r requirements.txt

# Start the service
python main.py

# Or with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

## 📡 API Endpoints

### Control Endpoints

#### Start Simulator
```bash
POST /simulator/start
```

**Request Body (Optional):**
```json
{
    "machine_ids": ["c0000000-0000-0000-0000-000000000001"]
}
```

**Response:**
```json
{
    "message": "Simulator started successfully",
    "success": true,
    "data": {
        "running_machines": 5,
        "total_machines": 5
    }
}
```

#### Stop Simulator
```bash
POST /simulator/stop
```

#### Get Status
```bash
GET /simulator/status
```

**Response:**
```json
{
    "status": "running",
    "uptime_seconds": 3600.5,
    "factories_count": 1,
    "machines_count": 5,
    "running_machines": 5,
    "total_readings_generated": 180000,
    "mqtt_connected": true,
    "mqtt_messages_published": 180000,
    "configuration": {
        "enable_anomalies": true,
        "anomaly_probability": 0.1
    }
}
```

### Machine Endpoints

#### List All Machines
```bash
GET /simulator/machines
```

#### Get Machine Status
```bash
GET /simulator/machines/{machine_id}
```

### Anomaly Testing

#### Inject Anomaly
```bash
POST /simulator/machines/{machine_id}/anomaly
```

**Request Body:**
```json
{
    "machine_id": "c0000000-0000-0000-0000-000000000001",
    "anomaly_type": "leak",
    "duration_seconds": 300,
    "severity": 1.5
}
```

**Anomaly Types:**
- **Compressor**: `leak`, `efficiency_loss`, `bearing_fault`
- **HVAC**: `refrigerant_leak`, `dirty_coils`, `compressor_fault`
- **Motor**: `bearing_wear`, `belt_slip`, `overload`
- **Pump**: `seal_leak`, `pump_wear`, `valve_fault`
- **Injection Molding**: `heater_fault`, `cooling_insufficient`, `hydraulic_leak`

#### Clear Anomaly
```bash
DELETE /simulator/machines/{machine_id}/anomaly
```

### Configuration

#### Update Configuration
```bash
PUT /simulator/config
```

**Request Body:**
```json
{
    "enable_anomalies": true,
    "anomaly_probability": 0.15,
    "weekend_production_factor": 0.3
}
```

## 📊 Data Output

### MQTT Topics

Data is published to MQTT in real-time:

```
factory/{factory_id}/{machine_name}/energy
factory/{factory_id}/{machine_name}/production
factory/{factory_id}/{machine_name}/environmental
factory/{factory_id}/{machine_name}/status
```

**Example:**
```
factory/demo/compressor-1/energy
factory/demo/compressor-1/production
factory/demo/hvac-main/energy
```

### Message Format

**Energy Reading:**
```json
{
    "time": "2025-10-09T12:00:00Z",
    "machine_id": "c0000000-0000-0000-0000-000000000001",
    "power_kw": 45.3,
    "energy_kwh": 0.0126,
    "voltage_v": 402.5,
    "current_a": 65.2,
    "power_factor": 0.89,
    "frequency_hz": 50.1
}
```

## 🎨 Realistic Features

### Shift Patterns
- **Shift 1**: 06:00-14:00 (100% production)
- **Shift 2**: 14:00-22:00 (100% production)
- **Shift 3**: 22:00-06:00 (50% production)
- **Weekends**: 30% production

### Seasonal Variations
- **Summer** (Jun-Aug): +15°C outdoor temperature
- **Winter** (Dec-Feb): -10°C outdoor temperature
- **Spring/Fall**: Interpolated

### Noise & Variation
- ±3-5% random noise on all readings
- Realistic electrical parameter calculations
- Temperature-dependent behaviors

## ⚙️ Configuration

Environment variables in `.env`:

```bash
# Simulator Settings
SIMULATOR_AUTO_START=true
SIMULATOR_ENABLE_ANOMALIES=true
ANOMALY_PROBABILITY=0.10

# Machine Intervals
COMPRESSOR_INTERVAL=1
HVAC_INTERVAL=10
MOTOR_INTERVAL=10
PUMP_INTERVAL=30
INJECTION_MOLDING_INTERVAL=30

# Shift Schedule
SHIFT_1_START=6
SHIFT_1_END=14
SHIFT_2_START=14
SHIFT_2_END=22

# Production
WEEKEND_PRODUCTION_FACTOR=0.3
```

## 📈 Data Volumes

Expected message rates:

| Machine Type | Interval | Messages/sec | Messages/hour |
|--------------|----------|--------------|---------------|
| Compressor | 1s | 3.0 | 10,800 |
| HVAC | 10s | 0.3 | 1,080 |
| Motor | 10s | 0.3 | 1,080 |
| Pump | 30s | 0.1 | 360 |
| Injection Molding | 30s | 0.1 | 360 |
| **Total (5 machines)** | - | **3.8** | **13,680** |

## 🧪 Testing

### Test Simulator Locally

```bash
# 1. Start dependencies
docker-compose up -d postgres mqtt redis

# 2. Run simulator
python main.py

# 3. Test endpoints
curl http://localhost:8003/health
curl http://localhost:8003/simulator/status

# 4. Start simulation
curl -X POST http://localhost:8003/simulator/start

# 5. Check MQTT messages
mosquitto_sub -h 89.252.166.188 -p 2010 -u raptorblingx -P raptorblingx -t 'factory/#' -v
```

### Test Anomaly Injection

```bash
# Inject a leak on compressor
curl -X POST http://localhost:8003/simulator/machines/c0000000-0000-0000-0000-000000000001/anomaly \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "c0000000-0000-0000-0000-000000000001",
    "anomaly_type": "leak",
    "duration_seconds": 300,
    "severity": 1.5
  }'

# Clear anomaly
curl -X DELETE http://localhost:8003/simulator/machines/c0000000-0000-0000-0000-000000000001/anomaly
```

## 📚 API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8003/docs
- **ReDoc**: http://localhost:8003/redoc

## 🐛 Troubleshooting

### Simulator won't start
- Check database connection
- Verify MQTT broker is accessible
- Check logs: `docker-compose logs simulator`

### No MQTT messages
- Verify MQTT broker connection
- Check `mqtt_connected` in status endpoint
- Test MQTT broker: `mosquitto_pub -h 89.252.166.188 -p 2010 -u raptorblingx -P raptorblingx -t test -m "hello"`

### Database connection errors
- Ensure PostgreSQL is running
- Verify credentials in `.env`
- Check network connectivity

## 📝 License

Part of the WASABI Project - MIT License

## 🤝 Contributing

See main EnMS project documentation for contribution guidelines.