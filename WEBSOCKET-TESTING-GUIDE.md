# WebSocket Live Testing Guide

**Date:** October 16, 2025  
**Purpose:** Test real-time WebSocket notifications with visual feedback  
**Tester:** Watch your browser while running commands

---

## 🎯 What WebSocket Does in Your Project

### **3 Main Use Cases:**

1. **Real-Time Anomaly Alerts** 
   - When system detects anomaly → Instant toast notification in browser
   - No page refresh needed

2. **Training Progress Updates**
   - When ML model retraining starts → Progress notifications
   - Shows 0% → 20% → 40% → 60% → 80% → 100%

3. **Live Metric Updates**
   - When metrics change → Dashboard updates automatically
   - Real-time energy consumption, efficiency scores

---

## 📋 Pre-Test Setup

### **Step 1: Open the Dashboard Page**

**URL to Open:**
```
http://10.33.10.109:8080/api/analytics/ui/
```

**What You Should See:**
- EnMS Dashboard header
- Machine cards with metrics
- Anomaly table at bottom
- **Bottom-right corner:** Green badge "● Connected" (this is WebSocket status)

**Important:** Keep this browser tab visible while running commands!

---

### **Step 2: Open Browser Console (Optional but Recommended)**

**How:**
- Press `F12` or `Right-click → Inspect`
- Click "Console" tab

**What You'll See:**
```
WebSocket connected to: ws://10.33.10.109:8080/api/analytics/api/v1/ws/dashboard
WebSocket connected to: ws://10.33.10.109:8080/api/analytics/api/v1/ws/anomalies
Dashboard WebSocket initialized
Anomalies WebSocket initialized
```

This confirms WebSocket is working.

---

## 🧪 Test 1: Real-Time Anomaly Alert

### **What This Tests:**
When anomaly is detected → Toast notification appears instantly

### **Command to Run:**
```bash
# First, get a machine ID
MACHINE_ID=$(curl -s http://10.33.10.109:8080/api/analytics/api/v1/machines | jq -r '.[0].id')
echo "Testing with machine: $MACHINE_ID"

# Trigger anomaly detection
curl -X POST "http://10.33.10.109:8080/api/analytics/api/v1/anomaly/detect" \
  -H "Content-Type: application/json" \
  -d "{
    \"machine_id\": \"$MACHINE_ID\",
    \"start\": \"2025-10-01T00:00:00Z\",
    \"end\": \"2025-10-16T23:59:59Z\",
    \"contamination\": 0.1,
    \"use_baseline\": true
  }"
```

### **Expected Output in Terminal:**
```json
{
  "machine_name": "Compressor-1",
  "anomalies_detected": 4,
  "anomalies_saved": 4
}
```

### **Expected Behavior in Browser (Watch carefully!):**

**Within 0.5 seconds:**

1. **Toast Notification Appears (Top-Right Corner):**
   ```
   ╔══════════════════════════════════════╗
   ║  🚨 New Anomaly Detected!           ║
   ║  Compressor-1 - High Temperature    ║
   ║  Severity: high                     ║
   ╚══════════════════════════════════════╝
   ```
   - Background: Orange (for high severity) or Red (for critical)
   - Auto-dismisses after 5 seconds
   - Multiple toasts if multiple anomalies detected

2. **Anomaly Counter Updates:**
   - Top of page: "Recent Anomalies" count increases
   - Example: `5` → `9` (increases by 4)

3. **Anomaly Table Refreshes:**
   - Bottom table reloads
   - New rows appear at top
   - Shows: Timestamp, Machine, Type, Severity

4. **Browser Console Shows:**
   ```
   Received anomaly alert: {type: "anomaly_detected", ...}
   Showing new anomaly toast
   Anomaly table refreshed
   ```

---

## 🧪 Test 2: Training Progress Updates

### **What This Tests:**
When model retraining starts → Progress notifications appear in real-time

### **Command to Run:**
```bash
# Get machine ID
MACHINE_ID=$(curl -s http://10.33.10.109:8080/api/analytics/api/v1/machines | jq -r '.[0].id')
echo "Machine ID: $MACHINE_ID"

# Trigger model retraining
curl -X POST "http://10.33.10.109:8080/api/analytics/api/v1/model-performance/retrain/trigger?model_type=baseline&machine_id=$MACHINE_ID&trigger_type=manual&reason=testing_websocket" | jq
```

### **Expected Output in Terminal:**
```json
{
  "triggered": true,
  "trigger_type": "manual",
  "reason": "testing_websocket",
  "training_job_id": "abc-123-def-456",
  "estimated_completion": "2025-10-16T15:45:00Z"
}
```

### **Expected Behavior in Browser (Watch for ~8-10 seconds):**

**Timeline of Events:**

**At 0 seconds (Immediately):**
```
╔══════════════════════════════════════╗
║  🔄 Training Started                 ║
║  Model: baseline                     ║
║  Machine: Compressor-1               ║
╚══════════════════════════════════════╝
```
- Blue background
- Shows for 3 seconds

**At ~2 seconds:**
```
╔══════════════════════════════════════╗
║  ⏳ Training Progress: 20%           ║
║  Preparing data...                   ║
╚══════════════════════════════════════╝
```

**At ~4 seconds:**
```
╔══════════════════════════════════════╗
║  ⏳ Training Progress: 60%           ║
║  Training model...                   ║
╚══════════════════════════════════════╝
```

**At ~8 seconds:**
```
╔══════════════════════════════════════╗
║  ✅ Training Complete!               ║
║  Accuracy: 95.2%                     ║
║  F1 Score: 0.94                      ║
╚══════════════════════════════════════╝
```
- Green background
- Shows for 5 seconds

**Browser Console Shows:**
```
Training started: baseline
Training progress: 20%
Training progress: 60%
Training completed successfully
Metrics refreshed
```

---

## 🧪 Test 3: Multiple Simultaneous Alerts

### **What This Tests:**
System can handle multiple events at once

### **Command to Run:**
```bash
# Run multiple detections in quick succession
for i in {1..3}; do
  MACHINE_ID=$(curl -s http://10.33.10.109:8080/api/analytics/api/v1/machines | jq -r ".[$((i-1))].id")
  curl -X POST "http://10.33.10.109:8080/api/analytics/api/v1/anomaly/detect" \
    -H "Content-Type: application/json" \
    -d "{
      \"machine_id\": \"$MACHINE_ID\",
      \"start\": \"2025-10-01T00:00:00Z\",
      \"end\": \"2025-10-16T23:59:59Z\",
      \"contamination\": 0.1,
      \"use_baseline\": true
    }" &
done
wait
echo "All detections triggered!"
```

### **Expected Behavior in Browser:**

**Multiple toast notifications stack:**
```
╔════════════════════════════╗
║  🚨 Compressor-1 Anomaly  ║
╚════════════════════════════╝
╔════════════════════════════╗
║  🚨 HVAC-1 Anomaly        ║
╚════════════════════════════╝
╔════════════════════════════╗
║  🚨 Pump-1 Anomaly        ║
╚════════════════════════════╝
```

- Toasts appear one above the other
- Each auto-dismisses after 5 seconds
- Table updates with all new anomalies

---

## 🧪 Test 4: WebSocket Reconnection

### **What This Tests:**
WebSocket automatically reconnects if connection drops

### **Step 1: Break the connection**
```bash
# Restart analytics container (simulates connection loss)
docker compose restart analytics
```

### **Expected Behavior in Browser:**

**Immediately:**
- Bottom-right badge changes: `● Connected` → `● Reconnecting...`
- Badge color: Green → Yellow

**After ~15 seconds:**
- Container finishes restarting
- WebSocket reconnects automatically
- Badge changes: `● Reconnecting...` → `● Connected`
- Badge color: Yellow → Green

**Browser Console Shows:**
```
WebSocket connection closed
Attempting reconnection (attempt 1/10)
Attempting reconnection (attempt 2/10)
WebSocket reconnected successfully
```

---

## 🧪 Test 5: Connection Status Indicator

### **What This Tests:**
Visual feedback of WebSocket health

### **How to Observe:**

**Location:** Bottom-right corner of dashboard

**States:**

1. **Connected (Normal):**
   ```
   ● Connected
   ```
   - Green dot
   - Gray text
   - Both WebSockets active

2. **Connecting (Starting up):**
   ```
   ● Connecting...
   ```
   - Yellow dot
   - Gray text
   - Appears briefly on page load

3. **Reconnecting (Connection lost):**
   ```
   ● Reconnecting...
   ```
   - Yellow dot
   - Orange text
   - Automatically tries to reconnect

4. **Disconnected (Failed):**
   ```
   ● Disconnected
   ```
   - Red dot
   - Red text
   - After 10 failed reconnection attempts

---

## 📊 Quick Test Summary

| Test | Command | Browser Element | What to Watch |
|------|---------|----------------|---------------|
| Anomaly Alert | `curl POST /anomaly/detect` | Top-right corner | Orange/Red toast appears |
| Training Progress | `curl POST /retrain/trigger` | Top-right corner | Blue → multiple toasts → Green |
| Counter Update | `curl POST /anomaly/detect` | Top of page | Number increases |
| Table Refresh | `curl POST /anomaly/detect` | Bottom table | New rows appear |
| Status Indicator | `docker restart analytics` | Bottom-right | Green → Yellow → Green |

---

## 🎬 Complete Testing Session

### **Run this full sequence:**

```bash
#!/bin/bash
echo "=== WebSocket Testing Session ==="
echo "Keep your eyes on the browser!"
echo ""

# Test 1: Anomaly Detection
echo "TEST 1: Triggering anomaly detection..."
echo "👀 WATCH: Top-right corner for orange toast"
MACHINE_ID=$(curl -s http://10.33.10.109:8080/api/analytics/api/v1/machines | jq -r '.[0].id')
curl -s -X POST "http://10.33.10.109:8080/api/analytics/api/v1/anomaly/detect" \
  -H "Content-Type: application/json" \
  -d "{\"machine_id\":\"$MACHINE_ID\",\"start\":\"2025-10-01T00:00:00Z\",\"end\":\"2025-10-16T23:59:59Z\",\"contamination\":0.1,\"use_baseline\":true}" | jq
echo ""
echo "✅ Did you see the orange toast notification?"
read -p "Press Enter to continue..."

# Test 2: Training Progress
echo ""
echo "TEST 2: Triggering model training..."
echo "👀 WATCH: Multiple toasts showing progress (blue → green)"
echo "This takes ~10 seconds..."
curl -s -X POST "http://10.33.10.109:8080/api/analytics/api/v1/model-performance/retrain/trigger?model_type=baseline&machine_id=$MACHINE_ID&trigger_type=manual&reason=test" | jq
echo ""
echo "✅ Did you see: Training Started → Progress 20% → Progress 60% → Training Complete?"
read -p "Press Enter to continue..."

# Test 3: Check WebSocket Logs
echo ""
echo "TEST 3: Checking server logs..."
echo "You should see 'Published anomaly event' and 'Published training' messages"
docker compose logs analytics --tail=20 | grep -E "(Published|WebSocket connected)"
echo ""

echo "=== Testing Complete! ==="
echo ""
echo "Summary of what you should have seen:"
echo "✅ Toast notifications appearing instantly"
echo "✅ Anomaly counter increasing"
echo "✅ Training progress updates"
echo "✅ Connection status indicator (green dot)"
echo ""
echo "If you saw all of these: WebSocket is working perfectly! 🎉"
```

### **Save and run:**
```bash
# Save the script
cat > /tmp/test-websocket.sh << 'EOF'
[paste script above]
EOF

# Make executable and run
chmod +x /tmp/test-websocket.sh
/tmp/test-websocket.sh
```

---

## 🐛 Troubleshooting

### **Problem: No toasts appearing**

**Check 1: Is WebSocket connected?**
```bash
docker compose logs analytics --tail=50 | grep -i websocket
```
Should show: `WebSocket client connected`

**Check 2: Browser console errors?**
Press F12, check for red errors

**Check 3: Is event publishing working?**
```bash
docker compose logs analytics --tail=50 | grep "Published"
```
Should show: `Published anomaly event` or `Published training`

---

### **Problem: Connection status shows "Reconnecting"**

**Fix: Restart analytics container**
```bash
docker compose restart analytics
# Wait 15 seconds, should reconnect
```

---

### **Problem: Old toasts not disappearing**

**Expected:** Toasts auto-dismiss after 5 seconds  
**If stuck:** This is a UI bug, refresh browser

---

## 📝 Testing Checklist

Before marking WebSocket as complete, verify:

- [ ] Dashboard page loads without errors
- [ ] Connection status shows "● Connected" (green)
- [ ] Browser console shows 2 WebSocket connections
- [ ] Anomaly detection triggers orange toast
- [ ] Toast appears within 1 second
- [ ] Anomaly counter updates automatically
- [ ] Training triggers blue → green toast sequence
- [ ] Progress updates show (20%, 60%)
- [ ] Multiple toasts can stack
- [ ] Toasts auto-dismiss after 5 seconds
- [ ] Reconnection works after container restart

---

## 🎯 Key Takeaways

**What WebSocket Gives You:**
1. **Instant feedback** - No waiting for page refresh
2. **Better UX** - Users know system is alive and responding
3. **Proactive alerts** - System pushes critical info to user
4. **Efficient** - No constant polling, saves bandwidth

**Real Factory Impact:**
- Operator sees machine failure alert in <1 second
- Can take action immediately
- Prevents cascading failures
- Reduces downtime

---

**Now go test it live! Keep your browser visible and run the commands.** 🚀
