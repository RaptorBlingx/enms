# 🎯 MQTT FIX - Visual Step-by-Step Guide

## 🔴 **THE PROBLEM**

Your Node-RED is trying to connect to a server called **literally** `$(MQTT_HOST)` instead of `89.252.166.188`!

```
Current (WRONG):           What Node-RED Sees:
broker: "$(MQTT_HOST)"  →  Connect to "$(MQTT_HOST)" ❌
port: "$(MQTT_PORT)"    →  Port "$(MQTT_PORT)" ❌

Should Be:                 What Node-RED Needs:
broker: "89.252.166.188" → Connect to 89.252.166.188 ✅
port: "2010"             → Port 2010 ✅
```

---

## 🔧 **THE FIX - Step by Step**

### **Step 1: Open Node-RED**
```
http://<your-server-ip>:1881
```

### **Step 2: Edit MQTT Broker**

1. **Find the MQTT node** (pink/purple node that says "Subscribe: factory/#")
2. **Double-click it**
3. You'll see this:
   ```
   Topic: factory/demo/compressor-1/energy
   QoS: 1
   Server: [mqtt_broker_config] 🖊️ (pencil icon)
   ```
4. **Click the pencil icon** 🖊️ next to the server dropdown

### **Step 3: Update Broker Settings**

You'll see a form with these fields. **Change them to:**

```
┌─────────────────────────────────────────┐
│ Name: EnMS MQTT Broker                  │
├─────────────────────────────────────────┤
│ Server: 89.252.166.188                  │ ← Change from $(MQTT_HOST)
│ Port: 2010                              │ ← Change from $(MQTT_PORT)
│ Protocol: MQTT V3.1.1                   │ ← Select from dropdown
│ Client ID:  [leave empty]              │
│ Keep Alive: 60                          │
│ ☑ Clean Session                        │
│ ☐ Use TLS                              │
│ ☐ Use Legacy MQTT 3.1 support         │
└─────────────────────────────────────────┘
```

### **Step 4: Add Security Credentials**

1. **Click the "Security" tab** at the top
2. Fill in:

```
┌─────────────────────────────────────────┐
│ Username: raptorblingx                  │
│ Password: raptorblingx                  │
└─────────────────────────────────────────┘
```

### **Step 5: Save**
1. Click **"Update"** button (top right)
2. You'll be back at the node properties
3. Click **"Done"** button

### **Step 6: Fix PostgreSQL Config**

1. **Find any purple "postgresql" node**
2. **Double-click it**
3. **Click the pencil icon** 🖊️ next to the config dropdown
4. **Change these values:**

```
┌─────────────────────────────────────────┐
│ Host: postgres                          │ ← Change from $(POSTGRES_HOST)
│ Port: 5432                              │ ← Change from $(POSTGRES_PORT)
│ Database: enms                          │ ← Change from $(POSTGRES_DB)
│ SSL: false                              │
│ Max Connections: 10                     │
└─────────────────────────────────────────┘
```

5. **Click the "User" tab**
6. **Fill in:**

```
┌─────────────────────────────────────────┐
│ User: raptorblingx                      │ ← Change from $(POSTGRES_USER)
│ Password: raptorblingx                  │ ← Change from $(POSTGRES_PASSWORD)
└─────────────────────────────────────────┘
```

7. Click **"Update"**
8. Click **"Done"**

### **Step 7: Deploy!**

1. **Click the big red "Deploy" button** (top right)
2. **Watch the MQTT node status change:**
   - Before: 🟡 "connecting..."
   - After: 🟢 "connected"

---

## ✅ **Verification**

### **1. Check MQTT Node Status**
```
Look under the "Subscribe: factory/#" node
Should say: 🟢 connected
```

### **2. Open Debug Panel**
```
Click the bug icon (🐛) on the right sidebar
You should see messages flowing:
"10/10/2025, 10:30:15msg.payload : Object
{ time: "2025-10-10T10:30:15.123", power_kw: 45.2, ... }"
```

### **3. Check Statistics**
```
Wait 30 seconds for the "Every 30s" inject to trigger
Debug panel should show:
{
  energy: 50,
  production: 50,
  environmental: 50,
  status: 7,
  errors: 0,
  lastUpdate: "2025-10-10T10:30:45Z"
}
```

### **4. Verify Database**
```bash
# Check if data is being inserted
docker compose exec postgres psql -U raptorblingx -d enms \
  -c "SELECT COUNT(*) FROM energy_readings;"

# Should show increasing numbers each time you run it
```

---

## 🎉 **Success Checklist**

- [ ] MQTT node shows 🟢 "connected" (not yellow "connecting")
- [ ] Debug panel shows messages every 1-5 seconds
- [ ] No red "error" nodes
- [ ] Statistics counter shows increasing numbers
- [ ] PostgreSQL nodes show "connected"
- [ ] Database query shows data rows

---

## 🆘 **Still Not Working?**

### **Check 1: MQTT Node Still Yellow?**
```bash
# Test MQTT from command line
docker compose exec nodered mosquitto_sub \
  -h 89.252.166.188 -p 2010 \
  -u raptorblingx -P raptorblingx \
  -t 'factory/#' -C 3

# If this works but Node-RED doesn't:
# - Make sure you clicked "Update" then "Deploy"
# - Check Node-RED logs: docker compose logs nodered --tail=50
```

### **Check 2: PostgreSQL Not Connecting?**
```bash
# Test PostgreSQL connection
docker compose exec nodered nc -zv postgres 5432

# Should show: postgres (postgres:5432) open
```

### **Check 3: No Messages in Debug?**
```bash
# Make sure simulator is running
docker compose ps simulator

# Check simulator is publishing
docker compose logs simulator --tail=20 | grep "Published"
```

---

## 📊 **Before vs After**

### **Before (Not Working):**
```
MQTT: 🟡 connecting...
Broker trying to connect to: "$(MQTT_HOST):$(MQTT_PORT)"
PostgreSQL: ❌ Error: cannot connect
Host trying to connect to: "$(POSTGRES_HOST)"
```

### **After (Working):**
```
MQTT: 🟢 connected
Broker connected to: 89.252.166.188:2010
PostgreSQL: ✅ Connected
Host connected to: postgres:5432
Data flowing: ✅ Every 1-5 seconds
Database: ✅ Rows increasing
```

---

**Fix these configuration values and your entire data pipeline will start working!** 🚀
