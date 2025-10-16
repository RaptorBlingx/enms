# EnMS API - Quick Reference for OVOS

**Base URL:** `http://10.33.10.109:8080/api/analytics/api/v1`  
**Docs:** http://10.33.10.109:8080/api/analytics/docs  
**WebSocket:** `ws://10.33.10.109:8080/api/analytics/api/v1/ws/`

---

## 🚀 5-Minute Integration

### **1. Test Connection**
```bash
curl http://10.33.10.109:8080/api/analytics/api/v1/health
```

### **2. Install Python Client**
```bash
pip install requests websocket-client
```

### **3. Copy This Code**
```python
import requests

BASE = "http://10.33.10.109:8080/api/analytics/api/v1"

# Get energy consumption
r = requests.get(f"{BASE}/kpis/overview")
energy = r.json()['total_energy_kwh']
print(f"Energy: {energy} kWh")

# Get machines
r = requests.get(f"{BASE}/machines")
machines = r.json()
print(f"Machines: {[m['name'] for m in machines]}")

# Get recent anomalies
r = requests.get(f"{BASE}/anomaly/recent?limit=5")
anomalies = r.json()['anomalies']
print(f"Anomalies: {len(anomalies)}")
```

---

## 📊 Top 10 Endpoints for OVOS

| # | Endpoint | Method | Use Case |
|---|----------|--------|----------|
| 1 | `/health` | GET | Check if online |
| 2 | `/machines` | GET | List all machines |
| 3 | `/kpis/overview` | GET | Get energy/cost/carbon |
| 4 | `/anomaly/recent` | GET | Get recent alerts |
| 5 | `/timeseries/{id}/current` | GET | Get machine status |
| 6 | `/forecast/{id}` | GET | Energy forecast |
| 7 | `/kpis/machines` | GET | Compare machines |
| 8 | `/anomaly/detect` | POST | Trigger scan |
| 9 | `/model-performance/retrain/trigger` | POST | Retrain ML model |
| 10 | `/scheduler/status` | GET | Get automation status |

---

## 🎤 Voice Command Examples

### **Energy Queries**
```
"What's the energy consumption?"
→ GET /kpis/overview
→ Response: total_energy_kwh

"How much did we spend on energy?"
→ GET /kpis/overview
→ Response: total_cost

"What's the carbon footprint?"
→ GET /kpis/overview
→ Response: carbon_emissions_kg
```

### **Machine Queries**
```
"List all machines"
→ GET /machines
→ Response: [machine names]

"What's the temperature of Compressor-1?"
→ GET /machines (get ID)
→ GET /timeseries/{id}/current
→ Response: temperature

"Is Compressor-1 running?"
→ GET /timeseries/{id}/current
→ Response: status
```

### **Anomaly Queries**
```
"Any problems today?"
→ GET /anomaly/recent?limit=10
→ Response: anomaly list

"Scan for anomalies"
→ POST /anomaly/detect
→ Response: anomalies found

"Show critical alerts"
→ GET /anomaly/recent?severity=critical
→ Response: critical anomalies
```

### **Forecasting**
```
"What's tomorrow's energy forecast?"
→ GET /forecast/{id}?periods=24
→ Response: forecast data
```

---

## 🌐 WebSocket (Real-Time Alerts)

### **Connect to Anomalies Stream**
```python
import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    if data['type'] == 'anomaly_detected':
        anomaly = data['data']
        severity = anomaly['severity']
        machine = anomaly.get('machine_id', 'Unknown')
        
        if severity in ['high', 'critical']:
            # Interrupt and speak
            ovos.speak(f"ALERT! {machine} has a {severity} anomaly!")

ws = websocket.WebSocketApp(
    "ws://10.33.10.109:8080/api/analytics/api/v1/ws/anomalies?client_id=ovos",
    on_message=on_message
)
ws.run_forever()
```

### **Event Types**
- `anomaly_detected` - New anomaly alert
- `training_started` - ML training began
- `training_progress` - Training progress update
- `training_completed` - Training finished
- `metric_updated` - Metric changed
- `connection` - WebSocket connected

---

## 📋 Common Query Patterns

### **Get Current Status**
```python
# Get all machines
machines = requests.get(f"{BASE}/machines").json()

# For each machine, get current status
for machine in machines:
    status = requests.get(
        f"{BASE}/timeseries/{machine['id']}/current"
    ).json()
    print(f"{machine['name']}: {status['energy_kwh']} kWh")
```

### **Get Time Range Data**
```python
# Get energy consumption for date range
kpis = requests.get(
    f"{BASE}/kpis/overview",
    params={
        'start_date': '2025-10-01',
        'end_date': '2025-10-16'
    }
).json()
```

### **Find Specific Machine**
```python
# Find machine by name
machines = requests.get(f"{BASE}/machines").json()
compressor = next(m for m in machines if 'Compressor' in m['name'])
machine_id = compressor['id']

# Get its status
status = requests.get(f"{BASE}/timeseries/{machine_id}/current").json()
```

---

## 🔧 Response Formats

### **Success Response**
```json
{
  "data": [...],
  "metadata": {}
}
```

### **Error Response**
```json
{
  "detail": "Error message"
}
```

### **Common Fields**
- `machine_id` - UUID v4 format
- `timestamp` - ISO 8601: "2025-10-16T10:30:00Z"
- `energy_kwh` - Float (kilowatt hours)
- `temperature` - Float (Celsius)
- `severity` - "normal", "low", "medium", "high", "critical"

---

## ⚡ Quick Tests

```bash
# 1. Health check
curl http://10.33.10.109:8080/api/analytics/api/v1/health

# 2. Get machines
curl http://10.33.10.109:8080/api/analytics/api/v1/machines | jq

# 3. Get KPIs
curl "http://10.33.10.109:8080/api/analytics/api/v1/kpis/overview" | jq

# 4. Get recent anomalies
curl "http://10.33.10.109:8080/api/analytics/api/v1/anomaly/recent?limit=5" | jq

# 5. Test WebSocket (requires wscat)
wscat -c "ws://10.33.10.109:8080/api/analytics/api/v1/ws/anomalies?client_id=test"
```

---

## 🎯 Integration Checklist

### **Phase 1: Basic (2-4 hours)**
- [ ] Test API connection
- [ ] Get machines list working
- [ ] Get energy consumption working
- [ ] Test 3-5 voice commands

### **Phase 2: Complete (1 day)**
- [ ] All query types working
- [ ] Error handling implemented
- [ ] Natural language processing
- [ ] Response formatting for speech

### **Phase 3: Advanced (Optional)**
- [ ] WebSocket integration
- [ ] Proactive alerts
- [ ] Interrupt logic
- [ ] Severity-based handling

---

## 📞 Need Help?

**Documentation:**
- Full API Reference: `api-ovos.md`
- Integration Guide: `OVOS-INTEGRATION-GUIDE.md`
- Swagger UI: http://10.33.10.109:8080/api/analytics/docs

**Test Your Integration:**
```python
# test_enms.py
import requests

BASE = "http://10.33.10.109:8080/api/analytics/api/v1"

tests = [
    ("Health", f"{BASE}/health"),
    ("Machines", f"{BASE}/machines"),
    ("KPIs", f"{BASE}/kpis/overview"),
    ("Anomalies", f"{BASE}/anomaly/recent?limit=1"),
]

print("Testing EnMS API...")
for name, url in tests:
    try:
        r = requests.get(url, timeout=5)
        status = "✓" if r.status_code == 200 else "✗"
        print(f"{status} {name}: {r.status_code}")
    except Exception as e:
        print(f"✗ {name}: {e}")
```

---

**🚀 You're ready to integrate! EnMS is waiting for OVOS to connect.**
