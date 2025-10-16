# Phase 4 Session 5: Real-Time Updates - Testing Guide

**Date:** October 15, 2025  
**Status:** Ready for Testing  
**Backend:** ✅ Complete | **Frontend:** ✅ Complete

---

## 🧪 Testing Checklist

### 1. WebSocket Connection Test

**Steps:**
1. Open browser to: `http://10.33.10.109:8080/api/analytics/ui/`
2. Open browser DevTools (F12) → Console tab
3. Look for WebSocket connection messages:
   ```
   [WebSocket] Client utility loaded ✓
   [Dashboard] Initializing dashboard...
   [WebSocket] Connecting to ws://10.33.10.109:8080/api/v1/ws/dashboard?client_id=...
   [WebSocket] Connecting to ws://10.33.10.109:8080/api/v1/ws/anomalies?client_id=...
   [WebSocket] ✓ Connected to /api/v1/ws/dashboard
   [Dashboard] Dashboard WebSocket connected
   [WebSocket] ✓ Connected to /api/v1/ws/anomalies
   [Dashboard] Anomalies WebSocket connected
   ```

4. Check connection status indicator:
   - Bottom-right corner should show green badge with "Live"
   - Toast notification: "✓ Real-time updates active"

**Expected Result:** ✅ Both WebSocket connections established successfully

---

### 2. Real-Time Anomaly Detection Test

**Trigger Method 1: Via Scheduler (Wait for next hourly run)**
- Next scheduled run: Check logs for "Hourly Anomaly Detection"
- Runs at: **:05 minutes of every hour** (e.g., 14:05, 15:05)

**Trigger Method 2: Manual API Call**

```bash
# Get list of machines first
curl -X GET http://10.33.10.109:8080/api/v1/machines | jq '.[0].id'

# Detect anomalies for a specific machine (replace MACHINE_ID)
curl -X POST "http://10.33.10.109:8080/api/v1/anomaly/detect/{MACHINE_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "start_time": "2025-10-14T00:00:00Z",
    "end_time": "2025-10-15T23:59:59Z",
    "contamination": 0.1,
    "use_baseline": true
  }'
```

**Expected Behavior:**
1. If anomalies detected:
   - Toast notification appears (yellow/red based on severity)
   - Shows: Machine name, anomaly type, severity
   - Anomaly counter increments with animation
   - Recent anomalies table updates automatically
2. Check browser console:
   ```
   [Dashboard] Received anomaly: {event_type: "anomaly_detected", ...}
   [Dashboard] New anomaly detected: {...}
   ```

---

### 3. Real-Time Training Progress Test

**Steps:**

1. **Navigate to Model Performance page:**
   ```
   http://10.33.10.109:8080/api/analytics/ui/model-performance
   ```

2. **Trigger training** (if that page has WebSocket, otherwise test via API):
   ```bash
   # Get a machine ID
   MACHINE_ID=$(curl -s http://10.33.10.109:8080/api/v1/machines | jq -r '.[0].id')
   
   # Trigger baseline training
   curl -X POST "http://10.33.10.109:8080/api/v1/baseline/train/${MACHINE_ID}" \
     -H "Content-Type: application/json"
   ```

3. **Watch Dashboard for training events:**
   - Training started toast notification
   - Training completed toast (after ~8 seconds) with performance metrics
   
4. **Check console logs:**
   ```
   [Dashboard] Received message: {event_type: "training_started", ...}
   [Dashboard] Received message: {event_type: "training_completed", ...}
   [Dashboard] Training completed: {job_id: ..., status: "completed", metrics: {...}}
   ```

**Expected Result:** ✅ Training events appear in real-time without refreshing

---

### 4. WebSocket Reconnection Test

**Steps:**
1. Open dashboard with DevTools console open
2. Restart analytics container:
   ```bash
   docker compose restart analytics
   ```
3. Watch console for reconnection attempts:
   ```
   [WebSocket] Connection closed: /api/v1/ws/dashboard (Code: 1006)
   [WebSocket] Reconnecting in Xs (Attempt 1/10)
   [WebSocket] Attempting reconnection 1...
   [WebSocket] Connecting to ws://...
   [WebSocket] ✓ Connected to /api/v1/ws/dashboard
   ```
4. Check status indicator:
   - Should show "Reconnecting..." (yellow) during reconnection
   - Should return to "Live" (green) when connected

**Expected Result:** ✅ Auto-reconnects successfully with exponential backoff

---

### 5. Multiple Browser Tabs Test

**Steps:**
1. Open dashboard in 3 different browser tabs/windows
2. Trigger an anomaly detection or training in one tab (or via API)
3. Verify all 3 tabs receive the event simultaneously
4. Check that toast notifications appear in all tabs
5. Verify anomaly counter updates in all tabs

**Expected Result:** ✅ All connected clients receive events in real-time

---

### 6. Connection Status Indicator Test

**Test States:**

| State | Badge Color | Text | When |
|-------|-------------|------|------|
| Connected | Green | "Live" | Normal operation |
| Connecting | Yellow | "Connecting..." | Initial connection |
| Reconnecting | Yellow | "Reconnecting..." | After disconnect |
| Disconnected | Red | "Offline" | Max reconnect attempts or manual disconnect |

**Steps:**
1. Initial load → "Connecting..." then "Live"
2. Restart container → "Reconnecting..." then "Live"
3. Stop container → "Reconnecting..." → Eventually "Offline" (after 10 attempts)

---

### 7. Toast Notification Types Test

**Toast Types to Verify:**

1. **Success (Green)**
   - Real-time updates active (on connection)
   - Training completed successfully

2. **Warning (Yellow)**
   - Anomaly detected (severity: warning)

3. **Danger (Red)**
   - Anomaly detected (severity: critical)
   - Training failed

4. **Info (Blue)**
   - Model updated
   - General system events

**Check:**
- Toast appears top-right corner
- Auto-dismisses after duration (3-8 seconds)
- Close button works
- Multiple toasts stack vertically

---

## 📊 Backend Event Publishing Verification

### Check Redis Pub/Sub Activity

```bash
# Monitor all Redis pub/sub activity
docker exec -it enms-redis redis-cli
> MONITOR

# Or subscribe to specific channels
> SUBSCRIBE anomaly.detected
> SUBSCRIBE training.started
> SUBSCRIBE training.progress
> SUBSCRIBE training.completed
```

### Check Analytics Service Logs

```bash
# Watch logs for event publishing
docker compose logs analytics -f | grep -E "Publishing|Event|WebSocket"

# Should see:
# - "Published anomaly event for anomaly {id}"
# - "WebSocket connected: {endpoint}"
# - Event subscriber messages
```

---

## 🐛 Troubleshooting Guide

### Problem: WebSocket Won't Connect

**Symptoms:**
- Status indicator stuck on "Connecting..."
- Console error: "WebSocket connection failed"

**Solutions:**
1. Check analytics service is running:
   ```bash
   docker compose ps analytics
   ```

2. Check WebSocket routes are registered:
   ```bash
   curl http://10.33.10.109:8080/api/v1/health
   ```

3. Check browser console for CORS issues

4. Verify port 8001 is accessible from browser

### Problem: No Toast Notifications

**Symptoms:**
- WebSocket connected but no toasts appear
- Console shows messages but no UI updates

**Solutions:**
1. Check toast container exists in HTML:
   ```javascript
   document.querySelector('.toast-container')
   ```

2. Check Bootstrap is loaded (required for toasts):
   ```javascript
   typeof bootstrap !== 'undefined'
   ```

3. Check browser console for JavaScript errors

### Problem: Events Not Publishing

**Symptoms:**
- Anomalies detected but no WebSocket message
- Training runs but no events

**Solutions:**
1. Check Redis is running:
   ```bash
   docker compose ps redis
   ```

2. Check event subscriber is active:
   ```bash
   docker compose logs analytics | grep "Event subscriber"
   # Should see: "✓ Event subscriber started"
   ```

3. Check for event publishing errors:
   ```bash
   docker compose logs analytics | grep -i "failed to publish"
   ```

### Problem: High CPU Usage

**Cause:** Too many WebSocket messages or reconnection loops

**Solutions:**
1. Check reconnection attempts in console
2. Verify heartbeat interval is reasonable (30s)
3. Check for message loops in event handlers

---

## ✅ Success Criteria

All tests must pass:

- [ ] WebSocket connections establish successfully
- [ ] Connection status indicator updates correctly
- [ ] Real-time anomaly alerts appear without refresh
- [ ] Training progress events appear in real-time
- [ ] Toast notifications display correctly
- [ ] Auto-reconnection works after disconnect
- [ ] Multiple browser tabs receive events simultaneously
- [ ] No console errors or warnings
- [ ] Backend event publishing logs show activity
- [ ] Redis pub/sub channels receive messages

---

## 📈 Performance Metrics

**Expected Performance:**

| Metric | Target | Measured |
|--------|--------|----------|
| WebSocket Connection Time | < 1s | ___ ms |
| Event Delivery Latency | < 200ms | ___ ms |
| Reconnection Time | < 5s | ___ s |
| Toast Display Time | 3-8s | ___ s |
| Memory per Connection | < 1MB | ___ KB |
| CPU Impact | < 5% | ___ % |

---

## 📝 Test Results Log

**Test Date:** _______________  
**Tester:** _______________

| Test # | Test Name | Result | Notes |
|--------|-----------|--------|-------|
| 1 | WebSocket Connection | ⬜ Pass / ⬜ Fail | |
| 2 | Real-Time Anomaly Detection | ⬜ Pass / ⬜ Fail | |
| 3 | Training Progress Events | ⬜ Pass / ⬜ Fail | |
| 4 | Auto-Reconnection | ⬜ Pass / ⬜ Fail | |
| 5 | Multiple Browser Tabs | ⬜ Pass / ⬜ Fail | |
| 6 | Connection Status Indicator | ⬜ Pass / ⬜ Fail | |
| 7 | Toast Notifications | ⬜ Pass / ⬜ Fail | |

---

## 🚀 Next Steps After Testing

1. **If All Tests Pass:**
   - Mark Phase 4 Session 5 as complete
   - Update documentation
   - Consider additional event types (metric updates, system alerts)
   - Plan Phase 5 features

2. **If Tests Fail:**
   - Document specific failures
   - Check troubleshooting guide
   - Review backend/frontend integration
   - Check for missing dependencies or configuration

---

**Testing Guide Version:** 1.0  
**Last Updated:** October 15, 2025
