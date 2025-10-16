# 🛠️ Anomaly Creator - Developer Tool

**Purpose:** Easily create test anomalies for UI development and testing.

## 📍 Access

**URL:** http://10.33.10.109:8080/api/analytics/ui/anomaly-creator

## ✨ Features

### 1. **Helpful Tooltips**
Every field has an **ℹ️ info icon**:
- Hover over any icon to see field explanation
- Understand what each field does
- Learn acceptable values

### 2. **Quick-Fill Buttons**

**Time Buttons:**
- `Now` - Current time
- `1 hour ago` - Test recent anomalies
- `1 day ago` - Test 24-hour view
- `1 week ago` - Test 7-day view

**Metric Buttons:**
- `Temperature` - Pre-fills: 85.5°C actual, 75.0°C expected
- `Pressure` - Pre-fills: 125 PSI actual, 100 PSI expected
- `Vibration` - Pre-fills: 45 Hz actual, 30 Hz expected
- `Current` - Pre-fills: 15.5A actual, 12.0A expected

### 3. **Auto-Calculations**
- Deviation % calculated automatically when you fill actual + expected values
- WebSocket event published automatically (for real-time dashboard updates)

### 4. **Field Descriptions**

| Field | Description | Values |
|-------|-------------|--------|
| **Machine** | Which machine this anomaly belongs to | Dropdown from database |
| **Detection Time** | When anomaly was detected | Any datetime |
| **Anomaly Type** | Type of anomaly | `spike`, `drop`, `drift`, `unknown` |
| **Severity** | How serious | `critical`, `high`, `medium`, `low`, `normal` |
| **Metric Name** | Which sensor/measurement | `temperature`, `pressure`, `vibration`, etc. |
| **Actual Value** | What was measured | Any number |
| **Expected Value** | What should have been | Any number |
| **Deviation %** | How far from normal | Auto-calculated or manual |
| **Confidence Score** | ML confidence (0-1) | Default: 0.85 (85%) |
| **Is Resolved** | Already fixed? | Checkbox |

## 🎯 Common Use Cases

### Test Real-Time Dashboard Notifications

1. Open dashboard in one tab: `http://10.33.10.109:8080/api/analytics/ui/`
2. Open creator in another: `http://10.33.10.109:8080/api/analytics/ui/anomaly-creator`
3. Create anomaly with "Now" time
4. See **orange toast notification** appear on dashboard! 🟠

### Test Anomaly Filtering

1. Create 5 anomalies with different severities:
   - 2 × `critical`
   - 2 × `medium`
   - 1 × `low`
2. Open anomaly page: `http://10.33.10.109:8080/api/analytics/ui/anomaly`
3. Test filter dropdowns

### Test Historical Data

1. Create anomalies at different times:
   - 1 hour ago
   - 1 day ago
   - 1 week ago
2. Test time-based filtering

### Test WebSocket Integration

1. Open WebSocket test page: `http://10.33.10.109:8080/api/analytics/ui/websocket-test`
2. Create anomaly (severity = `critical`)
3. Watch **real-time event** appear in log! ⚡

## 📊 Example Scenarios

### Scenario 1: Temperature Spike
```
Machine: Compressor-1
Time: Now
Type: spike
Severity: critical
Metric: temperature
Actual: 95.5°C
Expected: 75.0°C
Deviation: 27.33%
Confidence: 0.92
```

### Scenario 2: Pressure Drop
```
Machine: Pump-2
Time: 2 hours ago
Type: drop
Severity: high
Metric: pressure
Actual: 65 PSI
Expected: 100 PSI
Deviation: 35%
Confidence: 0.88
```

### Scenario 3: Gradual Drift
```
Machine: Conveyor-3
Time: 1 day ago
Type: drift
Severity: medium
Metric: vibration
Actual: 42 Hz
Expected: 30 Hz
Deviation: 40%
Confidence: 0.75
```

## 🔄 Workflow

```
1. Select Machine
   ↓
2. Set Time (or use quick buttons)
   ↓
3. Choose Type & Severity
   ↓
4. Fill Metric Details (or use quick buttons)
   ↓
5. Click "Create Anomaly"
   ↓
6. See success message
   ↓
7. Check dashboard for WebSocket notification
   ↓
8. Verify in anomaly page
```

## 🔗 Quick Links

- **Creator Page:** http://10.33.10.109:8080/api/analytics/ui/anomaly-creator
- **Anomaly Viewer:** http://10.33.10.109:8080/api/analytics/ui/anomaly
- **Dashboard:** http://10.33.10.109:8080/api/analytics/ui/
- **WebSocket Test:** http://10.33.10.109:8080/api/analytics/ui/websocket-test
- **API Docs:** http://10.33.10.109:8080/api/analytics/docs

## 🎨 Visual Features

- **Gradient purple background** - Easy to identify as dev tool
- **Red "DEVELOPMENT TOOL" badge** - Clear warning this is for testing
- **Color-coded severity** - 🔴 Critical, 🟠 High, 🟡 Medium, 🟢 Low, ⚪ Normal
- **Success/Error boxes** - Green for success, red for errors
- **Responsive design** - Works on mobile, tablet, desktop

## ⚠️ Important Notes

1. **Development Only** - This tool is for testing, not production use
2. **WebSocket Events** - Unresolved anomalies trigger WebSocket notifications
3. **Machine Must Exist** - Select from dropdown (machines must be in database)
4. **Valid Severities** - Must use: `critical`, `high`, `medium`, `low`, `normal`
5. **Valid Types** - Must use: `spike`, `drop`, `drift`, `unknown`

## 🐛 Troubleshooting

**Problem:** Machine dropdown is empty
- **Solution:** Ensure machines exist in database

**Problem:** "Machine not found" error
- **Solution:** Refresh page, select valid machine from dropdown

**Problem:** No WebSocket notification
- **Solution:** Check "Is Resolved" is unchecked, dashboard is open, WebSocket connected

**Problem:** 422 validation error
- **Solution:** Check all required fields filled, valid severity/type values

## 🚀 Next Steps After Creating Anomalies

1. ✅ View them in anomaly page
2. ✅ See real-time notifications on dashboard
3. ✅ Test filtering by severity/machine
4. ✅ Test resolve functionality
5. ✅ Test API endpoints with Swagger UI
6. ✅ Test OVOS integration queries

---

**Created:** October 16, 2025  
**Status:** ✅ Production Ready  
**Version:** 1.0
