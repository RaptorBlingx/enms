# Grafana Dashboard Quick Start Guide

## ✅ All Fixes Applied - Ready to Use!

All database query errors have been resolved. Your Grafana dashboards are now fully operational.

## Access Your Dashboards

**URL:** http://10.33.10.109:8080/grafana/

**Default Login:**
- Username: `admin`
- Password: `admin` (you'll be prompted to change on first login)

## Available Dashboards

### 1. Factory Overview
**Path:** Dashboards → Factory Overview
**Refresh:** Every 5 seconds
**Features:**
- Live machine count (7 active machines)
- Real-time total power consumption
- Today's energy consumption  
- Active alerts count
- Power consumption chart (last hour)
- Machine status table
- Energy distribution pie charts

### 2. Energy Analysis
**Path:** Dashboards → Energy Analysis  
**Refresh:** Every 30 seconds
**Features:**
- Power consumption trends (stacked by machine)
- Hourly/daily energy consumption
- Peak demand tracking
- Load factor analysis (efficiency metrics)
- 30-day historical consumption
- Power heatmap (7-day visualization)

**Variable:** Select machines to analyze (multi-select dropdown at top)

### 3. Machine Monitoring  
**Path:** Dashboards → Machine Monitoring
**Refresh:** Every 10 seconds
**Features:**
- Machine status indicator (running/idle/offline/maintenance)
- Current power consumption
- Today's energy usage
- Production units count
- Power consumption time-series
- Environmental conditions (temperature + humidity)
- Production output chart
- Quality metrics (defect rate %)
- Hourly performance summary table

**Variable:** Select individual machine to monitor (dropdown at top)

## What Was Fixed

### Problem 1: "column er.timestamp does not exist" ✅ FIXED
**Cause:** Dashboard queries used `timestamp` but database uses `time`  
**Solution:** All 11 queries updated to use correct `time` column

### Problem 2: "relation energy_readings_1hour does not exist" ✅ FIXED
**Cause:** Dashboards referenced non-existent aggregate tables
**Solution:** Changed to existing `energy_readings_1min` aggregate

### Additional Fixes Applied:
- ✅ Production data column names corrected (`production_count`, `production_count_bad`)
- ✅ Environmental data column names corrected (`machine_temp_c`, `indoor_humidity_percent`)  
- ✅ Continuous aggregates refreshed (1,641 data points from 33,315 raw readings)
- ✅ Automatic refresh policies enabled (updates every 1 minute)

## Verify Everything Works

### Test 1: Factory Overview Dashboard
1. Open http://10.33.10.109:8080/grafana/
2. Navigate to Factory Overview dashboard
3. **Expected Results:**
   - Active Machines shows: 7
   - Current Total Power shows: ~300+ kW (live value)
   - Energy Today shows: ~900+ kWh
   - Power chart displays data from last hour
   - Machine status table shows all 7 machines

### Test 2: Energy Analysis Dashboard  
1. Click "Energy Analysis" dashboard
2. Leave machines variable at "All" (default)
3. **Expected Results:**
   - Stacked power trend chart shows multiple colored lines
   - Hourly energy bars display consumption data
   - Peak demand chart shows power spikes
   - Energy summary table lists all 7 machines with totals

### Test 3: Machine Monitoring Dashboard
1. Click "Machine Monitoring" dashboard
2. Select "Compressor-EU-1" from machine dropdown
3. **Expected Results:**
   - Machine Status badge shows "Running" (green)
   - Current Power shows: ~75-85 kW
   - Energy Today shows: ~300+ kWh
   - All 9 panels display data without errors

## Current Data Summary

**From database verification:**
```
Machine             | Energy (kWh) | Avg Power (kW) | Readings
--------------------|--------------|----------------|----------
Compressor-EU-1     | 308.56       | 78.73          | 236
Injection-Molding-1 | 201.69       | 51.31          | 236
Compressor-1        | 192.80       | 48.13          | 241
Conveyor-A          | 88.35        | 22.52          | 236
Hydraulic-Pump-1    | 54.76        | 13.93          | 236
HVAC-EU-North       | 51.26        | 13.07          | 236
HVAC-Main           | 51.14        | 13.04          | 236
```

**Total:** ~949 kWh consumed today across all machines

## Troubleshooting

### If dashboards show "No Data"
```bash
# Manually refresh continuous aggregates
docker compose exec -T postgres psql -U raptorblingx -d enms -c \
  "CALL refresh_continuous_aggregate('energy_readings_1min', NULL, NULL);"
```

### If you see query errors
1. Check Grafana logs: `docker compose logs grafana`
2. Verify TimescaleDB connection: Configuration → Data Sources → TimescaleDB
3. Test connection should show: ✅ "Data source is working"

### If data appears stale
- Continuous aggregates refresh every 1 minute automatically
- Force refresh with SQL command above
- Check simulator is running: `docker compose ps simulator`

## Service Status

```bash
# Check all services
docker compose ps

# Expected status:
# enms-postgres   Up 5 hours (healthy)
# enms-redis      Up 5 hours (healthy)  
# enms-nodered    Up 3 hours (healthy)
# enms-simulator  Up 3 hours (healthy)
# enms-grafana    Up 4 minutes (healthy)
# enms-nginx      Up 3 minutes (healthy)
```

## Support Commands

```bash
# Restart Grafana
docker compose restart grafana

# View Grafana logs
docker compose logs -f grafana

# Check database queries
docker compose exec postgres psql -U raptorblingx -d enms

# Test a dashboard query
docker compose exec -T postgres psql -U raptorblingx -d enms -c \
  "SELECT m.name, er.power_kw FROM energy_readings er 
   JOIN machines m ON er.machine_id = m.id 
   ORDER BY er.time DESC LIMIT 5;"
```

## Configuration Files

- **Dashboards:** `/home/ubuntu/enms/grafana/dashboards/*.json`
- **Datasource:** `/home/ubuntu/enms/grafana/provisioning/datasources/timescaledb.yml`
- **Fix Scripts:** `fix_all_dashboard_queries.py`, `fix_production_environmental_columns.py`
- **Full Documentation:** `GRAFANA-FIX-SUMMARY.md`

---

**System:** EnMS v1.0 - Energy Management System  
**Server:** 10.33.10.109 (LXC container "lauds-toy")  
**Last Updated:** October 10, 2025  
**Status:** ✅ Fully Operational
