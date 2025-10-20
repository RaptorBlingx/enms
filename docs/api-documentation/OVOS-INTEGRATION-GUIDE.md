# EnMS → OVOS Integration Guide

**Date:** October 16, 2025  
**EnMS Version:** Phase 4 Complete (with WebSocket)  
**Status:** ✅ Ready for OVOS Integration  

---

## 🎯 Quick Answer: YES, Your EnMS is Ready!

Your EnMS provides everything OVOS needs:

✅ **REST API** - 40+ endpoints for queries  
✅ **WebSocket** - Real-time event streaming  
✅ **OpenAPI/Swagger** - Auto-generated documentation  
✅ **No Authentication** - Simple integration (add auth later if needed)  
✅ **JSON Responses** - Easy to parse  
✅ **CORS Enabled** - Cross-origin requests allowed  

---

## 📦 What to Provide to Your Colleague

### **1. Base URL**
```
http://10.33.10.109:8080/api/analytics
```

### **2. API Documentation**
```
Swagger UI:  http://10.33.10.109:8080/api/analytics/docs
OpenAPI JSON: http://10.33.10.109:8080/api/analytics/openapi.json
```

### **3. WebSocket Endpoints**
```
Dashboard:  ws://10.33.10.109:8080/api/analytics/api/v1/ws/dashboard
Anomalies:  ws://10.33.10.109:8080/api/analytics/api/v1/ws/anomalies
Training:   ws://10.33.10.109:8080/api/analytics/api/v1/ws/training
Events:     ws://10.33.10.109:8080/api/analytics/api/v1/ws/events
```

### **4. Integration Documents**
Send your colleague these files:
- ✅ `api-ovos.md` (already exists in your project)
- ✅ This guide (OVOS-INTEGRATION-GUIDE.md)
- ✅ Example code (see below)

---

## 🔌 Integration Types

### **Type 1: REST API Only (Basic)**
**Use Case:** Voice queries and commands  
**Complexity:** Simple  
**Latency:** Request → Response (~100-500ms)

**OVOS asks questions, EnMS responds:**
```
User: "Hey OVOS, what's the energy consumption?"
OVOS → GET /api/v1/kpis/overview
EnMS → Response with energy data
OVOS: "Total energy is 3,911 kilowatt hours"
```

---

### **Type 2: REST API + WebSocket (Advanced)** ⭐ **RECOMMENDED**
**Use Case:** Proactive alerts + queries  
**Complexity:** Medium  
**Latency:** Events pushed instantly (<500ms)

**EnMS pushes critical alerts to OVOS:**
```
Anomaly detected → EnMS → WebSocket → OVOS
OVOS (interrupts): "ALERT! Compressor-1 temperature is critical!"

User can also ask questions:
User: "Hey OVOS, show me the machines"
OVOS → GET /api/v1/machines → Response
```

---

## 📚 REST API Quick Reference

### **Core Endpoints Your Colleague Needs**

#### **1. System Status**
```http
GET /api/v1/health
```
**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-10-16T10:30:00Z"
}
```
**OVOS Use:** Check if EnMS is online

---

#### **2. Get All Machines**
```http
GET /api/v1/machines
```
**Response:**
```json
[
  {
    "id": "c0000000-0000-0000-0000-000000000001",
    "name": "Compressor-1",
    "type": "compressor",
    "location": "Production Floor A",
    "status": "active"
  }
]
```
**OVOS Use:** "List all machines", "Show me compressors"

---

#### **3. Get KPIs (Energy, Cost, etc.)**
```http
GET /api/v1/kpis/overview?start_date=2025-10-01&end_date=2025-10-16
```
**Response:**
```json
{
  "total_energy_kwh": 3911.45,
  "peak_demand_kw": 285.3,
  "average_sec": 2.84,
  "total_cost": 1564.58,
  "load_factor": 0.73,
  "carbon_emissions_kg": 1955.73
}
```
**OVOS Use:** "What's the energy consumption?", "How much did we spend on energy?"

---

#### **4. Get Recent Anomalies**
```http
GET /api/v1/anomaly/recent?limit=10
```
**Response:**
```json
{
  "anomalies": [
    {
      "id": "uuid",
      "machine_id": "c0000000-0000-0000-0000-000000000001",
      "machine_name": "Compressor-1",
      "detected_at": "2025-10-16T08:30:00Z",
      "anomaly_type": "temperature",
      "severity": "high",
      "metric_value": 95.2,
      "expected_value": 70.0
    }
  ]
}
```
**OVOS Use:** "Any anomalies today?", "Show me critical alerts"

---

#### **5. Get Machine Current Status**
```http
GET /api/v1/timeseries/{machine_id}/current
```
**Response:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "timestamp": "2025-10-16T10:30:00Z",
  "energy_kwh": 45.2,
  "temperature": 72.5,
  "pressure": 120.0,
  "current": 38.5,
  "status": "running"
}
```
**OVOS Use:** "What's the temperature of Compressor-1?"

---

#### **6. Trigger Anomaly Detection**
```http
POST /api/v1/anomaly/detect
Content-Type: application/json

{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "start": "2025-10-01T00:00:00Z",
  "end": "2025-10-16T23:59:59Z",
  "contamination": 0.1,
  "use_baseline": true
}
```
**OVOS Use:** "Scan for anomalies", "Check machine health"

---

#### **7. Get Energy Forecast**
```http
GET /api/v1/forecast/{machine_id}?periods=24&model=prophet
```
**Response:**
```json
{
  "machine_id": "c0000000-0000-0000-0000-000000000001",
  "forecast": [
    {
      "timestamp": "2025-10-17T00:00:00Z",
      "predicted_energy": 42.3,
      "lower_bound": 38.1,
      "upper_bound": 46.5
    }
  ]
}
```
**OVOS Use:** "What's tomorrow's energy forecast?"

---

## 🌐 WebSocket Integration (Real-Time Alerts)

### **Why WebSocket for OVOS?**

**Without WebSocket:**
```
OVOS polls every 30s: "Any alerts?"
EnMS: "No"
[30s later]
OVOS: "Any alerts?"
EnMS: "No"
[Alert happens]
[30s delay...]
OVOS: "Any alerts?"
EnMS: "Yes! Critical!"
```
❌ **30+ second delay**

**With WebSocket:**
```
OVOS ←──────→ EnMS (persistent connection)
[Alert happens]
EnMS → OVOS (instant)
OVOS (interrupts): "ALERT! Critical temperature!"
```
✅ **<1 second notification**

---

### **WebSocket Endpoints**

#### **1. Anomalies Stream (Recommended for OVOS)**
```
ws://10.33.10.109:8080/api/analytics/api/v1/ws/anomalies?client_id=ovos-assistant
```

**Events Received:**
```json
{
  "type": "anomaly_detected",
  "data": {
    "machine_id": "c0000000-0000-0000-0000-000000000001",
    "machine_name": "Compressor-1",
    "metric": "temperature",
    "value": 95.2,
    "anomaly_score": 0.85,
    "severity": "high",
    "timestamp": "2025-10-16T10:30:00Z"
  }
}
```

**OVOS Speaks:**
```
"ALERT! Compressor-1 has a high temperature anomaly.
 Current: 95.2 degrees. Expected: 70 degrees."
```

---

#### **2. Dashboard Stream (Optional)**
```
ws://10.33.10.109:8080/api/analytics/api/v1/ws/dashboard?client_id=ovos-assistant
```

**Events Received:**
```json
{
  "type": "metric_updated",
  "data": {
    "machine_id": "uuid",
    "metric": "energy_kwh",
    "value": 45.2,
    "timestamp": "2025-10-16T10:30:00Z"
  }
}
```

---

#### **3. Training Stream (Optional)**
```
ws://10.33.10.109:8080/api/analytics/api/v1/ws/training?client_id=ovos-assistant
```

**Events Received:**
```json
{
  "type": "training_completed",
  "data": {
    "job_id": "uuid",
    "model_type": "baseline",
    "machine_id": "uuid",
    "status": "completed",
    "metrics": {
      "r2_score": 0.952,
      "mae": 2.34
    }
  }
}
```

**OVOS Speaks:**
```
"Model training completed for Compressor-1.
 Accuracy: 95.2%"
```

---

## 💻 Example Code for OVOS Integration

### **Python Example: REST API**

```python
import requests

class EnMSClient:
    def __init__(self, base_url="http://10.33.10.109:8080/api/analytics"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
    
    def get_energy_consumption(self, start_date=None, end_date=None):
        """Get total energy consumption"""
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        response = requests.get(f"{self.api_url}/kpis/overview", params=params)
        data = response.json()
        return data['total_energy_kwh']
    
    def get_machines(self):
        """Get all machines"""
        response = requests.get(f"{self.api_url}/machines")
        return response.json()
    
    def get_recent_anomalies(self, limit=5):
        """Get recent anomalies"""
        response = requests.get(f"{self.api_url}/anomaly/recent", params={'limit': limit})
        return response.json()['anomalies']
    
    def get_machine_status(self, machine_id):
        """Get current machine status"""
        response = requests.get(f"{self.api_url}/timeseries/{machine_id}/current")
        return response.json()

# Usage in OVOS Skill
client = EnMSClient()

# "Hey OVOS, what's the energy consumption?"
energy = client.get_energy_consumption()
speak(f"Total energy consumption is {energy:.1f} kilowatt hours")

# "Hey OVOS, list machines"
machines = client.get_machines()
machine_names = [m['name'] for m in machines]
speak(f"I found {len(machines)} machines: {', '.join(machine_names)}")

# "Hey OVOS, any anomalies?"
anomalies = client.get_recent_anomalies(limit=3)
if anomalies:
    speak(f"There are {len(anomalies)} recent anomalies")
    for anom in anomalies[:3]:
        speak(f"{anom['machine_name']} has a {anom['severity']} {anom['anomaly_type']} anomaly")
else:
    speak("No anomalies detected")
```

---

### **Python Example: WebSocket (Real-Time Alerts)**

```python
import websocket
import json
import threading

class EnMSWebSocketClient:
    def __init__(self, endpoint="ws://10.33.10.109:8080/api/analytics/api/v1/ws/anomalies"):
        self.endpoint = f"{endpoint}?client_id=ovos-assistant"
        self.ws = None
        self.on_anomaly_callback = None
    
    def on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            
            if data['type'] == 'anomaly_detected':
                anomaly = data['data']
                self.handle_anomaly(anomaly)
            
            elif data['type'] == 'training_completed':
                training = data['data']
                self.handle_training_complete(training)
                
        except Exception as e:
            print(f"Error handling message: {e}")
    
    def handle_anomaly(self, anomaly):
        """Handle anomaly alert"""
        machine = anomaly.get('machine_id', 'Unknown')
        severity = anomaly.get('severity', 'normal')
        metric = anomaly.get('metric', 'unknown')
        
        if severity in ['high', 'critical']:
            # Interrupt OVOS and speak alert
            message = f"ALERT! {machine} has a {severity} {metric} anomaly!"
            
            if self.on_anomaly_callback:
                self.on_anomaly_callback(message, severity, anomaly)
            else:
                print(message)
    
    def handle_training_complete(self, training):
        """Handle training completion"""
        status = training.get('status')
        model_type = training.get('model_type')
        
        if status == 'completed':
            metrics = training.get('metrics', {})
            r2 = metrics.get('r2_score', 0)
            message = f"Model training completed. Accuracy: {r2*100:.1f}%"
            print(message)
    
    def on_error(self, ws, error):
        print(f"WebSocket error: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket connection closed")
    
    def on_open(self, ws):
        print("WebSocket connection established")
    
    def connect(self, on_anomaly=None):
        """Connect to WebSocket"""
        self.on_anomaly_callback = on_anomaly
        
        self.ws = websocket.WebSocketApp(
            self.endpoint,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )
        
        # Run in background thread
        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()
    
    def disconnect(self):
        """Disconnect from WebSocket"""
        if self.ws:
            self.ws.close()

# Usage in OVOS Skill
def handle_anomaly_alert(message, severity, anomaly_data):
    """Called when anomaly is detected"""
    # Interrupt current activity and speak
    if severity == 'critical':
        ovos.interrupt()
        ovos.speak_urgent(message)
    elif severity == 'high':
        ovos.speak(message)
    else:
        ovos.notify(message)

# Start WebSocket listener when OVOS skill loads
ws_client = EnMSWebSocketClient()
ws_client.connect(on_anomaly=handle_anomaly_alert)

# WebSocket runs in background, alerts arrive automatically!
```

---

## 🎤 Example OVOS Voice Commands

### **Queries (REST API)**

| User Says | OVOS Action | EnMS Endpoint |
|-----------|-------------|---------------|
| "What's the energy consumption?" | GET /api/v1/kpis/overview | Returns total kWh |
| "List all machines" | GET /api/v1/machines | Returns machine list |
| "Any anomalies today?" | GET /api/v1/anomaly/recent | Returns recent anomalies |
| "What's the temperature of Compressor-1?" | GET /api/v1/timeseries/{id}/current | Returns current metrics |
| "Show me the energy cost" | GET /api/v1/kpis/overview | Returns cost data |
| "Forecast tomorrow's energy" | GET /api/v1/forecast/{id} | Returns forecast |
| "Compare all machines" | GET /api/v1/kpis/machines | Returns comparison |
| "Scan for problems" | POST /api/v1/anomaly/detect | Triggers detection |

### **Proactive Alerts (WebSocket)**

| Event | OVOS Speaks |
|-------|-------------|
| Critical anomaly | "ALERT! Compressor-1 temperature is critical! 95 degrees!" |
| High anomaly | "Warning: HVAC-1 power consumption is high" |
| Training complete | "Model training completed. Accuracy 95%." |
| System alert | "System maintenance required" |

---

## 🔧 What's Missing (Optional Enhancements)

### **Currently NOT Implemented (but easy to add):**

#### **1. Natural Language Query Endpoint**
```http
POST /api/v1/query/natural
{
  "query": "what's the energy consumption for compressor 1 today?"
}
```
**Status:** Not implemented  
**Difficulty:** Medium  
**Need it?** Your colleague can parse queries in OVOS and call appropriate endpoints

---

#### **2. Voice-Optimized Responses**
```http
GET /api/v1/kpis/overview?format=voice
```
**Response:**
```json
{
  "text": "Total energy is 3,911 kilowatt hours. Cost is $1,564.",
  "ssml": "<speak>Total energy is <say-as interpret-as='unit'>3911 kilowatt hours</say-as></speak>"
}
```
**Status:** Not implemented  
**Difficulty:** Easy  
**Need it?** OVOS can format responses itself

---

#### **3. Authentication**
**Status:** No authentication required  
**Difficulty:** Medium  
**Need it?** Only if EnMS is public-facing

To add:
```python
# In OVOS client
headers = {"Authorization": "Bearer YOUR_API_KEY"}
requests.get(url, headers=headers)
```

---

#### **4. Rate Limiting**
**Status:** Not implemented  
**Need it?** Only if OVOS makes many rapid requests

---

#### **5. Custom WebSocket Filters**
```
ws://...ws/anomalies?client_id=ovos&severity=high,critical&machine_id=xxx
```
**Status:** Not implemented (receives all events)  
**Difficulty:** Easy  
**Need it?** OVOS can filter events client-side

---

## ✅ Integration Checklist

### **For Your Colleague:**

**Setup (5 minutes):**
- [ ] Test API connection: `curl http://10.33.10.109:8080/api/analytics/api/v1/health`
- [ ] Browse API docs: http://10.33.10.109:8080/api/analytics/docs
- [ ] Test a query: GET /api/v1/machines
- [ ] Copy example code from this guide

**REST API Integration:**
- [ ] Implement EnMSClient class
- [ ] Map voice intents to API endpoints
- [ ] Test with voice commands
- [ ] Handle error responses

**WebSocket Integration (Optional):**
- [ ] Implement WebSocket client
- [ ] Connect to /ws/anomalies endpoint
- [ ] Test event reception
- [ ] Implement interrupt/speak logic
- [ ] Test with live anomaly

**Testing:**
- [ ] Test each voice command
- [ ] Verify responses are natural
- [ ] Test error handling
- [ ] Load test if needed

---

## 📦 Files to Send Your Colleague

```bash
# 1. Create a package for your colleague
mkdir -p enms-ovos-integration
cd enms-ovos-integration

# 2. Copy documentation
cp /home/ubuntu/enms/api-ovos.md ./API-REFERENCE.md
cp /home/ubuntu/enms/OVOS-INTEGRATION-GUIDE.md ./

# 3. Create example code file (see above examples)
cat > enms_client.py << 'EOF'
# [Include the Python examples from above]
EOF

# 4. Create README
cat > README.md << 'EOF'
# EnMS Integration for OVOS

## Quick Start
1. Install: pip install requests websocket-client
2. Test API: python test_api.py
3. Integrate: Use enms_client.py in your OVOS skill

## Base URL
http://10.33.10.109:8080/api/analytics

## Documentation
- API-REFERENCE.md - Complete API documentation
- OVOS-INTEGRATION-GUIDE.md - Integration guide
- enms_client.py - Python client examples

## Support
Contact: [Your contact info]
EOF

# 5. Create test script
cat > test_api.py << 'EOF'
import requests

BASE_URL = "http://10.33.10.109:8080/api/analytics/api/v1"

print("Testing EnMS API...")

# Test 1: Health check
response = requests.get(f"{BASE_URL}/health")
print(f"✓ Health check: {response.json()}")

# Test 2: Get machines
response = requests.get(f"{BASE_URL}/machines")
machines = response.json()
print(f"✓ Found {len(machines)} machines")

# Test 3: Get KPIs
response = requests.get(f"{BASE_URL}/kpis/overview")
kpis = response.json()
print(f"✓ Energy: {kpis['total_energy_kwh']} kWh")

print("\n✅ All tests passed! EnMS API is ready.")
EOF

# 6. Zip everything
cd ..
tar -czf enms-ovos-integration.tar.gz enms-ovos-integration/
echo "Package created: enms-ovos-integration.tar.gz"
```

---

## 🎉 Summary

### **Your EnMS Status: ✅ READY!**

**What You Have:**
- ✅ 40+ REST API endpoints
- ✅ 4 WebSocket endpoints for real-time events
- ✅ OpenAPI/Swagger documentation
- ✅ CORS enabled
- ✅ JSON responses
- ✅ No authentication (simple integration)

**What Your Colleague Needs:**
1. **Base URL:** http://10.33.10.109:8080/api/analytics
2. **Docs:** http://10.33.10.109:8080/api/analytics/docs
3. **Example code** (in this guide)
4. **WebSocket URLs** (for real-time alerts)

**Integration Time:**
- REST API only: **2-4 hours**
- REST + WebSocket: **1 day**

**Next Steps:**
1. ✅ Send this guide to your colleague
2. ✅ They implement REST API calls for voice queries
3. ✅ (Optional) They implement WebSocket for proactive alerts
4. ✅ Test with voice commands
5. ✅ Deploy!

---

**Your EnMS is production-ready for OVOS integration!** 🚀

**No changes needed on your side** - everything is already exposed and working!
