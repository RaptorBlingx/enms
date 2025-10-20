# 🔧 Anomaly Endpoint Fix for Burak

**Date:** October 20, 2025  
**Issue:** Old documentation had incorrect severity values

---

## ❌ OLD (BROKEN) Command

```bash
curl "http://localhost:8001/api/v1/anomaly/recent?limit=5&severity=high"
```

**Problem:** `severity=high` doesn't exist in the system!

---

## ✅ CORRECTED Commands

### Valid Severity Values

The system uses these severity levels:
- `normal` - Low concern anomalies
- `warning` - Medium concern anomalies  
- `critical` - High concern anomalies (requires immediate attention)

### Working Examples

```bash
# Get last 5 CRITICAL anomalies (what you probably wanted)
curl "http://localhost:8001/api/v1/anomaly/recent?limit=5&severity=critical"

# Get last 5 WARNING anomalies
curl "http://localhost:8001/api/v1/anomaly/recent?limit=5&severity=warning"

# Get ALL anomalies (no severity filter) from last 7 days
curl "http://localhost:8001/api/v1/anomaly/recent?limit=50"

# Get critical anomalies from specific date range
curl "http://localhost:8001/api/v1/anomaly/recent?severity=critical&start_time=2025-10-15T00:00:00&end_time=2025-10-20T23:59:59"

# Get anomalies for specific machine
curl "http://localhost:8001/api/v1/anomaly/recent?machine_id=c0000000-0000-0000-0000-000000000001&limit=10"
```

---

## 🆕 NEW Features (Just Added!)

The endpoint now supports **flexible date ranges**:

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 50 | Max results (1-200) |
| `machine_id` | UUID | none | Filter by machine |
| `severity` | string | none | `normal`, `warning`, or `critical` |
| `start_time` | datetime | 7 days ago | Start of range (ISO 8601) |
| `end_time` | datetime | now | End of range (ISO 8601) |

### Date Range Examples

```bash
# Last 7 days (default behavior)
curl "http://localhost:8001/api/v1/anomaly/recent"

# Specific date range
curl "http://localhost:8001/api/v1/anomaly/recent?start_time=2025-10-15T00:00:00&end_time=2025-10-17T23:59:59"

# Just today
curl "http://localhost:8001/api/v1/anomaly/recent?start_time=2025-10-20T00:00:00&end_time=2025-10-20T23:59:59"

# Last week's critical alerts
curl "http://localhost:8001/api/v1/anomaly/recent?severity=critical&start_time=2025-10-13T00:00:00&end_time=2025-10-20T23:59:59"
```

---

## 📊 Response Format

```json
{
  "total_count": 5,
  "filters": {
    "machine_id": null,
    "severity": "critical",
    "start_time": "2025-10-13T00:00:00",
    "end_time": "2025-10-20T23:59:59",
    "time_window": "Custom range: 2025-10-13T00:00:00 to 2025-10-20T23:59:59"
  },
  "anomalies": [
    {
      "id": "985dacb4-b38b-4310-bf06-32bceb1e1260",
      "machine_id": "c0000000-0000-0000-0000-000000000001",
      "machine_name": "Compressor-1",
      "machine_type": "compressor",
      "detected_at": "2025-10-20T06:00:00+00:00",
      "anomaly_type": "unknown",
      "severity": "critical",
      "confidence_score": 0.0656,
      "is_resolved": false
    }
  ]
}
```

---

## 🧪 Quick Tests

```bash
# Test 1: Get all severity types that exist
curl -s "http://localhost:8001/api/v1/anomaly/recent?limit=100" | jq '[.anomalies[].severity] | unique'
# Expected: ["critical", "normal", "warning"]

# Test 2: Get count of critical anomalies
curl -s "http://localhost:8001/api/v1/anomaly/recent?severity=critical" | jq '.total_count'

# Test 3: Get warnings with pretty output
curl -s "http://localhost:8001/api/v1/anomaly/recent?severity=warning&limit=3" | jq '.anomalies[] | {machine: .machine_name, time: .detected_at, severity: .severity}'
```

---

## 🎯 For OVOS Integration

### Mapping Voice Commands to API Calls

**Voice:** "Are there any critical alerts?"
```python
response = requests.get(
    "http://localhost:8001/api/v1/anomaly/recent",
    params={"severity": "critical", "limit": 10}
)
```

**Voice:** "Show me warnings from last week"
```python
from datetime import datetime, timedelta
end = datetime.now()
start = end - timedelta(days=7)

response = requests.get(
    "http://localhost:8001/api/v1/anomaly/recent",
    params={
        "severity": "warning",
        "start_time": start.isoformat(),
        "end_time": end.isoformat()
    }
)
```

**Voice:** "What anomalies does Compressor-1 have?"
```python
response = requests.get(
    "http://localhost:8001/api/v1/anomaly/recent",
    params={
        "machine_id": "c0000000-0000-0000-0000-000000000001",
        "limit": 20
    }
)
```

---

## 📝 Summary of Changes

1. ❌ **Removed:** `severity=high`, `severity=low`, `severity=medium`
2. ✅ **Use instead:** `severity=critical`, `severity=warning`, `severity=normal`
3. 🆕 **Added:** Flexible date range with `start_time` and `end_time`
4. 🆕 **Default:** Last 7 days if no dates specified
5. 📄 **Updated:** `/home/ubuntu/enms/docs/api-documentation/api-ovos.md`

---

**Updated Documentation Location:**
- `/home/ubuntu/enms/docs/api-documentation/api-ovos.md` (lines 749-799)
- `/home/ubuntu/enms/docs/api-documentation/ENMS-API-DOCUMENTATION-FOR-OVOS.md` (section 7)

**Questions?** The endpoint is live and tested! 🚀
