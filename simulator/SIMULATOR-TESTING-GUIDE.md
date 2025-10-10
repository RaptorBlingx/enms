# 🧪 EnMS Simulator - Testing Guide

Quick guide to test and validate the Factory Simulator service.

## ✅ Pre-Flight Checklist

### 1. Verify File Structure
```bash
cd /enms/simulator

# Check all files exist
ls -la
# Should see:
# - main.py ✓
# - config.py ✓
# - models.py ✓
# - mqtt_publisher.py ✓
# - simulator_manager.py ✓
# - requirements.txt ✓
# - Dockerfile ✓
# - README.md ✓
# - api/
#   - __init__.py ✓
#   - routes.py ✓
# - machines/
#   - __init__.py ✓
#   - base_machine.py ✓
#   - compressor.py ✓
#   - hvac.py ✓
#   - motor.py ✓
#   - pump.py ✓
#   - injection_molding.py ✓
```

### 2. Environment Configuration
```bash
cd /enms

# Copy and edit .env
cp .env.example .env
nano .env

# Verify these critical settings:
# MQTT_HOST=89.252.166.188
# MQTT_PORT=2010
# MQTT_USERNAME=raptorblingx
# MQTT_PASSWORD=raptorblingx
# POSTGRES_USER=raptorblingx
# POSTGRES_PASSWORD=raptorblingx
```

## 🚀 Step-by-Step Testing

### Step 1: Start Dependencies

```bash
cd /enms

# Start database and MQTT
docker-compose up -d postgres mqtt redis

# Wait 10 seconds for services to be ready
sleep 10

# Verify they're running
docker-compose ps
```

**Expected Output:**
```
NAME                STATUS
enms-postgres       Up 10 seconds (healthy)
enms-mqtt           Up 10 seconds (healthy)
enms-redis          Up 10 seconds (healthy)
```

### Step 2: Build Simulator

```bash
# Build simulator image
docker-compose build simulator

# Check for errors in build output
```

**Expected:** Build completes without errors

### Step 3: Start Simulator

```bash
# Start simulator
docker-compose up -d simulator

# Watch startup logs
docker-compose logs -f simulator
```

**Expected Output:**
```
======================================================================
Starting EnMS Factory Simulator v1.0.0
======================================================================
INFO - Initializing simulator manager...
INFO - Connected to database
INFO - Connected to MQTT broker successfully
INFO - Loaded machine: Compressor-1 (compressor)
INFO - Loaded machine: HVAC-Main (hvac)
INFO - Loaded machine: Conveyor-A (motor)
INFO - Loaded machine: Hydraulic-Pump-1 (pump)
INFO - Loaded machine: Injection-Molding-1 (injection_molding)
INFO - ✓ Simulator manager initialized
INFO - Auto-starting simulator...
INFO - Started machine: Compressor-1
INFO - Started machine: HVAC-Main
INFO - Started machine: Conveyor-A
INFO - Started machine: Hydraulic-Pump-1
INFO - Started machine: Injection-Molding-1
INFO - ✓ Simulator auto-started
======================================================================
🚀 EnMS Factory Simulator is ready!
📡 API available at: http://0.0.0.0:8003
📊 API docs at: http://0.0.0.0:8003/docs
🔌 MQTT broker: 89.252.166.188:2010
======================================================================
```

Press `Ctrl+C` to stop following logs.

### Step 4: Health Check

```bash
# Test health endpoint
curl http://localhost:8003/health

# Pretty print with jq (if installed)
curl -s http://localhost:8003/health | jq
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "EnMS Factory Simulator",
  "version": "1.0.0",
  "timestamp": "2025-10-09T12:00:00.000000",
  "mqtt_connected": true,
  "database_connected": true
}
```

### Step 5: Check Status

```bash
curl -s http://localhost:8003/simulator/status | jq
```

**Expected Response:**
```json
{
  "status": "running",
  "uptime_seconds": 30.5,
  "factories_count": 1,
  "machines_count": 5,
  "running_machines": 5,
  "total_readings_generated": 150,
  "mqtt_connected": true,
  "mqtt_messages_published": 150,
  "configuration": {
    "enable_anomalies": true,
    "anomaly_probability": 0.1,
    "mqtt_broker": "89.252.166.188:2010"
  }
}
```

### Step 6: List Machines

```bash
curl -s http://localhost:8003/simulator/machines | jq
```

**Expected:** List of 5 machines with their status

### Step 7: Verify MQTT Data Flow

```bash
# Install mosquitto clients if needed
# sudo apt-get install mosquitto-clients

# Subscribe to all factory topics
mosquitto_sub \
  -h 89.252.166.188 \
  -p 2010 \
  -u raptorblingx \
  -P raptorblingx \
  -t 'factory/#' \
  -v

# You should see messages flowing:
# factory/demo/compressor-1/energy {"time":"2025-10-09T12:00:00Z","power_kw":45.3,...}
# factory/demo/compressor-1/production {"time":"2025-10-09T12:00:00Z",...}
# factory/demo/hvac-main/energy {"time":"2025-10-09T12:00:10Z",...}
```

Press `Ctrl+C` to stop.

### Step 8: Test Control Endpoints

#### Stop Simulator
```bash
curl -X POST http://localhost:8003/simulator/stop -s | jq
```

**Expected:**
```json
{
  "message": "Simulator stopped successfully",
  "success": true,
  "data": {
    "running_machines": 0,
    "total_machines": 5
  }
}
```

#### Start Simulator
```bash
curl -X POST http://localhost:8003/simulator/start -s | jq
```

**Expected:**
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

### Step 9: Test Anomaly Injection

```bash
# Inject a leak on compressor
curl -X POST http://localhost:8003/simulator/machines/c0000000-0000-0000-0000-000000000001/anomaly \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "c0000000-0000-0000-0000-000000000001",
    "anomaly_type": "leak",
    "duration_seconds": 120,
    "severity": 1.5
  }' -s | jq
```

**Expected:**
```json
{
  "message": "Anomaly 'leak' injected successfully",
  "success": true,
  "data": {
    "machine_id": "c0000000-0000-0000-0000-000000000001",
    "anomaly_type": "leak",
    "duration_seconds": 120,
    "severity": 1.5
  }
}
```

Check machine status:
```bash
curl -s http://localhost:8003/simulator/machines/c0000000-0000-0000-0000-000000000001 | jq
```

**Expected:** `anomaly_active: true`

### Step 10: Test Configuration Update

```bash
curl -X PUT http://localhost:8003/simulator/config \
  -H "Content-Type: application/json" \
  -d '{
    "enable_anomalies": true,
    "anomaly_probability": 0.15
  }' -s | jq
```

**Expected:**
```json
{
  "message": "Configuration updated successfully",
  "success": true,
  "data": {
    "enable_anomalies": true,
    "anomaly_probability": 0.15
  }
}
```

## 📊 Verify Data in Database

```bash
# Connect to database
docker-compose exec postgres psql -U raptorblingx -d enms

# Check energy readings
SELECT COUNT(*) FROM energy_readings;

# Should see increasing count as simulator runs

# Check recent data
SELECT 
    machine_id, 
    time, 
    power_kw, 
    energy_kwh 
FROM energy_readings 
ORDER BY time DESC 
LIMIT 10;

# Exit
\q
```

## 🌐 Interactive API Testing

Open browser to:
```
http://localhost:8003/docs
```

You'll see Swagger UI with all endpoints. Try:
1. Click on any endpoint
2. Click "Try it out"
3. Modify parameters
4. Click "Execute"
5. See response

## ✅ Success Criteria

Your simulator is working correctly if:

- ✅ Health endpoint returns "healthy"
- ✅ Status shows "running" with all machines started
- ✅ MQTT messages are being published (use mosquitto_sub)
- ✅ Database has energy_readings rows
- ✅ Anomaly injection works
- ✅ Start/stop controls work
- ✅ All 5 machine types are generating data
- ✅ Different data frequencies are respected (1s, 10s, 30s)

## 🐛 Common Issues

### Issue: "Connection refused" to MQTT
**Solution:** 
- Check MQTT broker is running: `docker-compose ps mqtt`
- Verify credentials in .env
- Test connection: `mosquitto_pub -h 89.252.166.188 -p 2010 -u raptorblingx -P raptorblingx -t test -m "test"`

### Issue: "Database connection failed"
**Solution:**
- Check PostgreSQL is running: `docker-compose ps postgres`
- Wait for database to be fully ready (30 seconds after start)
- Check logs: `docker-compose logs postgres`

### Issue: No data in database
**Solution:**
- Verify Node-RED is running (Phase 1 Part 4 - not yet implemented)
- For now, simulator publishes to MQTT only
- Database ingestion requires Node-RED flow

### Issue: "Simulator won't start"
**Solution:**
- Check all dependencies installed: `docker-compose exec simulator pip list`
- Check logs: `docker-compose logs simulator`
- Verify .env file exists and has correct values

## 📈 Performance Metrics

Monitor simulator performance:

```bash
# Check resource usage
docker stats enms-simulator

# Expected:
# CPU: 5-15%
# Memory: 200-500 MB
# Network: ~10 KB/s
```

## 🎉 Next Steps

After successful testing:

1. ✅ **Simulator is complete!**
2. ⏳ **Next: Create Nginx configuration** (Phase 1 Part 4)
3. ⏳ **Next: Create Node-RED data pipeline** (Phase 1 Part 4)
4. ⏳ **Next: End-to-end testing** (Phase 1 Part 5)

## 📞 Troubleshooting Tips

If you encounter issues:

1. **Check logs:** `docker-compose logs simulator`
2. **Restart service:** `docker-compose restart simulator`
3. **Rebuild image:** `docker-compose build --no-cache simulator`
4. **Check network:** `docker-compose exec simulator ping postgres`
5. **Verify .env:** `docker-compose exec simulator env | grep MQTT`

---

**🎯 Goal:** All checks pass = Simulator Phase complete = Ready for Phase 1 Part 4!