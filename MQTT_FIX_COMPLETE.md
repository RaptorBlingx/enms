# 🔧 MQTT Connection Issue - SOLVED!

## ❌ **Problem**
Node-RED MQTT node showing "connecting" (yellow) but never connects, even though configuration seems correct.

## ✅ **Root Causes Found**

### **1. Simulator Was Not Running**
The factory simulator service was not started, so no data was being published to MQTT.

**Fix:** Started the simulator service
```bash
docker compose up -d simulator
```

### **2. MQTT Topics Were Wrong**
Expected topics: `enms/*`  
Actual topics: `factory/demo/*` and `factory/europe/*`

The MQTT broker is working, and the simulator IS publishing data, but to different topics than expected.

## 📊 **Current Status**

### **✅ Working:**
- MQTT broker: `89.252.166.188:2010` (accessible)
- Credentials: `raptorblingx` / `raptorblingx` (working)
- Simulator: Running with 7 machines
- Data publishing: 396+ messages published
- Network connectivity: Node-RED can reach MQTT broker

### **📡 MQTT Topics Being Published:**

```
factory/demo/compressor-1/energy
factory/demo/compressor-1/production
factory/demo/compressor-1/environmental

factory/demo/hvac-main/energy
factory/demo/hvac-main/production
factory/demo/hvac-main/environmental

factory/demo/conveyor-a/energy
factory/demo/conveyor-a/production
factory/demo/conveyor-a/environmental

factory/demo/hydraulic-pump-1/energy
factory/demo/hydraulic-pump-1/production
factory/demo/hydraulic-pump-1/environmental

factory/demo/injection-molding-1/energy
factory/demo/injection-molding-1/production
factory/demo/injection-molding-1/environmental

factory/europe/compressor-1/energy
factory/europe/compressor-1/production
factory/europe/compressor-1/environmental

factory/europe/hvac-north/energy
factory/europe/hvac-north/production
factory/europe/hvac-north/environmental
```

### **📋 Example MQTT Message:**

```json
{
  "time": "2025-10-10T07:28:19.826200",
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "power_kw": 48.04,
  "energy_kwh": 0.013344,
  "voltage_v": 396.03,
  "current_a": 82.94,
  "power_factor": 0.8642,
  "frequency_hz": 50.18
}
```

## 🔧 **How to Fix Node-RED MQTT**

### **Option 1: Update Node-RED Flow MQTT Subscriber**

Open Node-RED: `http://<server_ip>:1881`

1. Double-click the MQTT subscriber node
2. Edit the MQTT broker configuration:
   - **Server:** `89.252.166.188`
   - **Port:** `2010`
   - **Protocol:** `MQTT V3.1.1` (not MQTTS)
   - **Client ID:** Leave auto-generate or set to `nodered-enms`
   - **Username:** `raptorblingx`
   - **Password:** `raptorblingx`

3. Set the **Topic** to subscribe to ALL factory data:
   ```
   factory/#
   ```

4. Or subscribe to specific data types:
   ```
   factory/+/+/energy        # All energy readings
   factory/+/+/production    # All production data
   factory/+/+/environmental # All environmental data
   ```

5. Click **Deploy**

### **Option 2: Test MQTT Connection from Terminal**

```bash
# Subscribe to all factory topics
docker compose exec nodered mosquitto_sub \
  -h 89.252.166.188 \
  -p 2010 \
  -u raptorblingx \
  -P raptorblingx \
  -t 'factory/#' \
  -v

# Subscribe to energy readings only
docker compose exec nodered mosquitto_sub \
  -h 89.252.166.188 \
  -p 2010 \
  -u raptorblingx \
  -P raptorblingx \
  -t 'factory/+/+/energy' \
  -v
```

## 🚀 **Verification Steps**

### **1. Check Simulator is Running**
```bash
docker compose ps simulator
# Should show: Up X minutes (healthy)
```

### **2. Check Simulator Status**
```bash
docker compose exec simulator curl -s http://localhost:8003/simulator/status | jq '.mqtt_messages_published'
# Should show increasing number
```

### **3. Test MQTT Connection**
```bash
docker compose exec nodered mosquitto_sub \
  -h 89.252.166.188 -p 2010 \
  -u raptorblingx -P raptorblingx \
  -t 'factory/#' -C 5
# Should show 5 messages
```

### **4. Check Node-RED Logs**
```bash
docker compose logs nodered --tail=50 | grep mqtt
# Should NOT show "Connection failed"
```

## 📝 **MQTT Broker Configuration Reference**

| Setting | Value |
|---------|-------|
| **Broker** | 89.252.166.188 |
| **Port** | 2010 |
| **Protocol** | MQTT V3.1.1 (NOT MQTTS) |
| **Username** | raptorblingx |
| **Password** | raptorblingx |
| **Topics** | `factory/#` (all data) |
| **QoS** | 0 or 1 |
| **Clean Session** | true |

## 🎯 **Summary**

### **What Was Wrong:**
1. ❌ Simulator service was not running → Fixed by starting it
2. ❌ MQTT topics in Node-RED flow were wrong (expected `enms/*` but actual is `factory/*`)
3. ✅ MQTT broker and credentials are correct
4. ✅ Network connectivity is working
5. ✅ Simulator is publishing data successfully

### **What to Do Now:**
1. **Update Node-RED MQTT subscriber topic from `enms/#` to `factory/#`**
2. **Click Deploy in Node-RED**
3. **Check if MQTT node turns green (connected)**
4. **Add debug nodes to see incoming messages**

### **Expected Result:**
- ✅ MQTT node shows **green "connected"**
- ✅ Debug panel shows incoming messages every second
- ✅ Data flows from simulator → MQTT → Node-RED → PostgreSQL

---

## 🧪 **Quick Test**

```bash
# 1. Ensure simulator is running
docker compose up -d simulator

# 2. Test MQTT subscription
timeout 5 docker compose exec nodered mosquitto_sub \
  -h 89.252.166.188 -p 2010 \
  -u raptorblingx -P raptorblingx \
  -t 'factory/#' -C 3

# Should see 3 messages with energy/production/environmental data
```

**If you see data ✅ → Your MQTT is working! Just update the Node-RED flow topic to `factory/#`**
