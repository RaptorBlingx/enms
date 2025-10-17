# Quick Test Guide - WebSocket & Enhanced Statistics

## 🧪 Verification Steps (5 Minutes)

### 1. Backend Health ✅
```bash
curl http://10.33.10.109:8001/api/v1/health
# Expected: {"status":"healthy","database":"connected","redis":"connected"}
```

### 2. Enhanced Statistics ✅
```bash
curl http://10.33.10.109:8001/api/v1/stats/system | jq .
# Expected: 16 metrics including peak_power, efficiency, estimated_cost, carbon_footprint
```

### 3. Frontend Testing ✅

**Open Landing Page:**
```
http://10.33.10.109:8080/
```

**Browser Console Checks (F12):**
- Look for: `✅ WebSocket connected - Real-time updates active!`
- Look for: `📊 Received WebSocket stats update` (every 5 seconds)
- Status: Green pulsing dot next to "System Status"

**Visual Verification:**
- Row 1: Total Readings (1.2M), Total Energy (28.1K kWh), Data Rate (142 pts/min), Uptime (6 days)
- Row 2: Peak Power (132 kW), Efficiency (40.9%), Cost ($3.4K), Carbon (14.1K kg)
- Sub-metrics visible: "Avg: 54 kW", "$632.58/day", "2,636 kg/day"

**Animation Test:**
- Refresh page (Ctrl+R)
- Watch numbers count up from 0 to actual value
- Numbers should pulse/scale during counting
- Takes ~2.5 seconds to complete

**Live Update Test:**
- Keep page open for 10 seconds
- Watch for subtle glow effect when numbers update
- Console should log "📊 Received WebSocket stats update"

---

## 🔍 Current Statistics (Oct 16, 2025)

```
System Metrics:
  • Total Readings: 1,170,610 (+140/min)
  • Total Energy: 28,147 kWh (+220 kWh/hr)
  • Data Rate: 142 points/minute
  • Uptime: 6 days (32.3%)

Power & Efficiency:
  • Peak Power: 132 kW (Max in 24h)
  • Average Power: 54 kW
  • Efficiency: 40.9% (Load factor)

Financial:
  • Total Cost: $3,377.64
  • Daily Cost: $632.58/day
  • Rate: $0.12/kWh

Environmental:
  • Carbon Footprint: 14,073.5 kg CO₂ (14.1 metric tons)
  • Daily Emissions: 2,635.76 kg/day
  • Factor: 0.5 kg CO₂/kWh

System Health:
  • Total Anomalies: 103
  • Active Machines: 7 (today)
```

---

## 🐛 Troubleshooting

### WebSocket Not Connecting

**Check Backend:**
```bash
docker logs enms-analytics --tail 50 | grep -i websocket
```

**Manual WebSocket Test:**
```bash
# Install websocat if needed: apt install websocat
websocat ws://10.33.10.109:8001/ws
# Should receive JSON updates every 5 seconds
```

**Browser Console Errors:**
- "WebSocket error" → Check if analytics container is running
- "Max reconnection attempts" → Restart analytics: `docker restart enms-analytics`
- Status indicator yellow → WebSocket down, using polling fallback (OK)

### Statistics Not Showing

**Check API:**
```bash
curl http://10.33.10.109:8001/api/v1/stats/system
# Should return JSON with 16 fields
```

**Check Frontend:**
- Open browser console (F12)
- Look for JavaScript errors
- Verify DOM elements exist: `document.getElementById('peak-power')`

### Numbers Not Animating

**Check JavaScript:**
- Console should NOT show errors
- Try: `document.getElementById('total-readings')` (should exist)
- Force reload: Ctrl+Shift+R (clear cache)

**Check CSS:**
```javascript
// In browser console
document.querySelector('.enms-stat-number').classList.add('counting');
// Should see pulse/scale animation
```

---

## 📊 Expected Browser Console Output

```
🚀 EnMS Portal Loading...
📡 Connecting to WebSocket...
✅ WebSocket connected - Real-time updates active!
📊 Loading system data...
✓ System status loaded
✓ System statistics loaded
📊 Received WebSocket stats update
📊 Received WebSocket stats update
📊 Received WebSocket stats update
...
```

---

## 🔄 Quick Restart Commands

**Restart Analytics Only:**
```bash
docker restart enms-analytics
sleep 15
curl http://10.33.10.109:8001/api/v1/health
```

**Rebuild Analytics:**
```bash
cd /home/ubuntu/enms
docker compose up -d --build analytics
sleep 15
docker logs enms-analytics --tail 20
```

**Restart Portal:**
```bash
docker restart enms-portal
```

**Full System Restart:**
```bash
docker compose restart
sleep 30
docker ps | grep enms
```

---

## ✅ Success Criteria

All these should be TRUE:

- [ ] Analytics container is healthy: `docker ps | grep analytics | grep healthy`
- [ ] API returns 16 metrics: `curl http://10.33.10.109:8001/api/v1/stats/system | jq 'keys | length'` → 17 (16 stats + timestamp)
- [ ] WebSocket connects: Browser console shows "✅ WebSocket connected"
- [ ] Numbers animate: Refresh page, watch 0→value counting
- [ ] Live updates work: Console logs "📊 Received WebSocket stats update" every 5s
- [ ] All 8 statistics display: 4 in row 1, 4 in row 2
- [ ] Sub-metrics show: "Avg: 54 kW", "$632.58/day", "2,636 kg/day"
- [ ] Status indicators: Green pulsing dot visible

---

## 📝 Test Results Template

```
Date: _______________
Tester: _______________

Backend Tests:
[ ] Health endpoint responds
[ ] Statistics endpoint returns 16 metrics
[ ] WebSocket endpoint accepts connections

Frontend Tests:
[ ] Landing page loads without errors
[ ] WebSocket connects (console message)
[ ] All 8 statistics display
[ ] Numbers animate from 0→value
[ ] Live updates every 5 seconds
[ ] Sub-metrics visible
[ ] Status indicator green/pulsing

Performance:
[ ] Page loads in < 2 seconds
[ ] Animations smooth (60fps)
[ ] WebSocket latency < 100ms
[ ] No memory leaks (keep open 5 min)

Notes:
_________________________________
_________________________________
_________________________________

Status: [ ] PASS  [ ] FAIL
```

---

## 🎯 Quick Demo Script (30 seconds)

1. Open http://10.33.10.109:8080/
2. Point out "System Statistics" card
3. Refresh page (Ctrl+R)
4. **Watch numbers count up** ← WOW factor!
5. Point out business metrics:
   - "We're consuming $633/day in electricity"
   - "That's 2.6 metric tons of CO₂ daily"
   - "Our power efficiency is 41%, room for improvement"
6. Open console (F12)
7. Show: "✅ WebSocket connected"
8. Wait 5 seconds, show: "📊 Received WebSocket stats update"
9. Point out: "Updates every 5 seconds automatically"

**Done! 🎉**

---

## 🔗 Related Documents

- Full Implementation Guide: `WEBSOCKET-ENHANCEMENT-COMPLETE.md`
- Design System: `portal/public/css/enms-design-system.css`
- Backend Code: `analytics/main.py`
- Frontend Code: `portal/public/index.html`

---

**Last Updated:** October 16, 2025  
**Status:** ✅ All tests passing
