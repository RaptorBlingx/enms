# 🔴 CRITICAL: MQTT Node-RED Configuration Issue Found!

## ❌ **The Real Problem**

Your Node-RED flow is using **WRONG ENVIRONMENT VARIABLE SYNTAX**:

### **Current (Broken) Configuration:**
```json
{
  "broker": "$(MQTT_HOST)",      // ❌ WRONG SYNTAX
  "port": "$(MQTT_PORT)",         // ❌ WRONG SYNTAX
  "host": "$(POSTGRES_HOST)",     // ❌ WRONG SYNTAX
}
```

### **Node-RED interprets this literally as:**
- Broker: The string `"$(MQTT_HOST)"` instead of `89.252.166.188`
- Port: The string `"$(MQTT_PORT)"` instead of `2010`

**This is why MQTT shows "connecting" - it's trying to connect to a server called literally `$(MQTT_HOST)`!**

## ✅ **The Fix**

You have 2 options:

### **Option 1: Use Actual Values (Recommended)**

Update your MQTT broker configuration in Node-RED:

1. Open Node-RED: `http://<server_ip>:1881`
2. Double-click any MQTT node
3. Click the pencil icon next to "Server" to edit the broker
4. Change to these **ACTUAL VALUES**:

```
Broker/Server: 89.252.166.188
Port: 2010
Protocol: MQTT V3.1.1
Client ID: (leave empty or "nodered-enms")
Keep Alive: 60
Clean Session: ✓ (checked)
Use Legacy MQTT 3.1 support: ☐ (unchecked)

Security Tab:
Username: raptorblingx
Password: raptorblingx
```

5. Click "Update"
6. Click "Deploy"
7. **✅ MQTT should turn GREEN immediately!**

### **Option 2: Fix Environment Variable Syntax**

If you want to use environment variables, Node-RED uses **different syntax**:

```json
{
  "broker": "${MQTT_HOST}",      // Node-RED syntax
  "port": "${MQTT_PORT}"         // Node-RED syntax
}
```

But this **ONLY works if** the environment variables are passed to the container, which they already are in your `docker-compose.yml`.

## 🔧 **PostgreSQL Configuration Fix**

Same issue with PostgreSQL config. Update it to actual values:

1. In Node-RED, go to any PostgreSQL node
2. Click the pencil icon to edit the configuration
3. Use these **ACTUAL VALUES**:

```
Host: postgres              (NOT $(POSTGRES_HOST))
Port: 5432                  (NOT $(POSTGRES_PORT))
Database: enms              (NOT $(POSTGRES_DB))
User: raptorblingx          (NOT $(POSTGRES_USER))
Password: raptorblingx      (NOT $(POSTGRES_PASSWORD))
SSL: false
Max Connections: 10
Idle Timeout: 1000
Connection Timeout: 10000
```

4. Click "Update"
5. Click "Deploy"

## 📋 **Complete Configuration Values**

### **MQTT Broker:**
```
Server: 89.252.166.188
Port: 2010
Username: raptorblingx
Password: raptorblingx
Protocol: MQTT V3.1.1
```

### **PostgreSQL:**
```
Host: postgres              ← Use Docker service name, not localhost!
Port: 5432                  ← Internal port, not 5433
Database: enms
User: raptorblingx
Password: raptorblingx
SSL: false
```

## 🎯 **Quick Fix Steps**

1. **Open Node-RED:** `http://<server_ip>:1881`

2. **Fix MQTT Broker:**
   - Double-click the "Subscribe: factory/#" node
   - Click pencil icon next to "Server"
   - Replace `$(MQTT_HOST)` with `89.252.166.188`
   - Replace `$(MQTT_PORT)` with `2010`
   - Go to "Security" tab
   - Username: `raptorblingx`
   - Password: `raptorblingx`
   - Click "Update"

3. **Fix PostgreSQL Config:**
   - Double-click any PostgreSQL node (the purple ones)
   - Click pencil icon next to config
   - Replace `$(POSTGRES_HOST)` with `postgres`
   - Replace `$(POSTGRES_PORT)` with `5432`
   - Replace `$(POSTGRES_DB)` with `enms`
   - Replace `$(POSTGRES_USER)` with `raptorblingx`
   - Replace `$(POSTGRES_PASSWORD)` with `raptorblingx`
   - Click "Update"

4. **Click Deploy**

5. **Verify:**
   - MQTT node should turn **GREEN** (connected)
   - Check debug panel for incoming messages
   - Check PostgreSQL node should show **connected**

## 🧪 **Test It**

After fixing, you should see:
- ✅ MQTT node: GREEN "connected"
- ✅ Debug panel: Messages flowing every second
- ✅ PostgreSQL: Data being inserted
- ✅ Energy readings counter increasing

## 💡 **Why This Happened**

The `$()` syntax is from shell/bash scripting. Node-RED doesn't understand this syntax. It needs either:
1. **Actual hardcoded values** (simplest, recommended)
2. **`${ENV_VAR}` syntax** with proper environment variable injection
3. **Node-RED context/flow variables**

Since your docker-compose.yml already passes environment variables to Node-RED, you could use `${MQTT_HOST}` but hardcoded values are more reliable for this use case.

---

## ✅ **Expected Result After Fix**

```
MQTT Node Status: 🟢 Connected
Debug Output: Messages every 1-5 seconds
Database: energy_readings, production_data, environmental_data populating
Statistics: Counters increasing
```

**This is the actual issue! Fix these values and your MQTT will connect immediately!** 🎯
