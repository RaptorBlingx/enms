# 🚀 EnMS API Quick Reference for OVOS

**Quick access guide for Burak's OVOS integration**

---

## 📍 Base URL

```
Production: http://your-server/api/analytics/api/v1
Local: http://localhost:8001/api/v1
```

---

## 🔥 Most Used Endpoints

### 1. Get Current Status
```bash
# System health
curl http://localhost:8001/api/v1/health

# Current statistics
curl http://localhost:8001/api/v1/stats/system
```

### 2. List Machines
```bash
curl http://localhost:8001/api/v1/machines
```

### 3. Latest Reading
```bash
curl http://localhost:8001/api/v1/timeseries/latest/{MACHINE_ID}
```

### 4. Active Alerts
```bash
curl http://localhost:8001/api/v1/anomaly/active
```

### 5. Energy Data (Last 24h)
```bash
curl -G http://localhost:8001/api/v1/timeseries/energy \
  --data-urlencode "machine_id={MACHINE_ID}" \
  --data-urlencode "start_time=2025-01-20T00:00:00Z" \
  --data-urlencode "end_time=2025-01-20T23:59:59Z" \
  --data-urlencode "interval=1hour"
```

---

## 🎙️ Voice Query Mapping

| User Says | API to Call | Parse This Field |
|-----------|-------------|------------------|
| "How much energy?" | `/stats/system` | `energy_per_hour` |
| "Current power?" | `/timeseries/latest/{id}` | `power_kw` |
| "Is machine running?" | `/machines/{id}` | `current_status` |
| "Any alerts?" | `/anomaly/active` | `total_count` |
| "Show energy today" | `/timeseries/energy?...` | `data_points[]` |
| "Predict tomorrow" | `/forecast?horizon_hours=24` | `predictions[]` |

---

## 🧪 Test Script

Run comprehensive API tests:

```bash
python test_enms_api.py
```

---

## 📚 Full Documentation

See: `ENMS-API-DOCUMENTATION-FOR-OVOS.md`

---

## 🆘 Quick Troubleshooting

### Connection Refused
```bash
# Check if EnMS is running
docker ps | grep analytics

# Check logs
docker logs enms-analytics
```

### Invalid Date Format
Always use ISO 8601: `2025-01-20T10:30:00Z`

### 404 Not Found
Check machine ID exists:
```bash
curl http://localhost:8001/api/v1/machines
```

---

## 📞 Contact

- **Mohamad**: Backend/API provider
- **Burak**: OVOS integration
- **Documentation**: ENMS-API-DOCUMENTATION-FOR-OVOS.md

---

**Last Updated:** January 20, 2025
