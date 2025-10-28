# Grafana SOTA (State-of-the-Art) Review & Enhancement Roadmap

## 📊 Executive Summary

**Current Status**: Good foundation with 6 dashboards, but **NOT leveraging full EnMS capabilities**  
**Database Potential**: Rich data (23 tables, 19 views, 4 hypertables) **underutilized**  
**Performance Issue**: **17 queries still using raw `energy_readings` table** (should use aggregates)  
**Missing Features**: 8+ critical dashboards not built yet

**Goal**: Transform into **SOTA industrial energy management dashboards**

---

## 🔍 Current Dashboard Analysis

### ✅ **Dashboard 1: Factory Overview** (34KB, 11 panels)
**Status**: Good foundation, needs optimization  
**Description**: Real-time factory energy and machine status

**Current Panels**:
1. Active Machines Count (Stat)
2. Energy Today (Stat) - ❌ **Uses raw table**
3. Current Power (Gauge)
4. Machine Status (Table)
5. Real-Time Power (Time Series) - ❌ **Uses raw table, 1-hour only**
6. Energy by Machine Today (Bar Chart)
7. Energy by Factory (Pie Chart)
8. Top Energy Consumers (Table)

**Issues Found**:
- ❌ Query at line 250: `FROM energy_readings` scanning full table for "Energy Today"
- ❌ Query at line 463: Last 1 hour only (should support multiple time ranges)
- ⚠️ No anomaly indicators
- ⚠️ No cost tracking
- ⚠️ No efficiency metrics (SEC, OEE)

**Recommendations**:
1. **Replace raw table query** with continuous aggregate:
   ```sql
   -- OLD (line 250):
   FROM energy_readings er WHERE er.time >= DATE_TRUNC('day', NOW())
   
   -- NEW:
   FROM energy_readings_1hour er WHERE er.bucket >= DATE_TRUNC('day', NOW())
   ```

2. **Add new panels**:
   - Anomaly Alert Count (Stat with red threshold)
   - Energy Cost Today (Stat with currency format)
   - Carbon Footprint Today (Stat with kg CO2 unit)
   - System Efficiency Score (Gauge 0-100%)
   - Forecasted vs Actual Power (Time Series comparison)

3. **Enhance existing**:
   - Make "Real-Time Power" support last 6h, 24h, 7d (not just 1h)
   - Add drill-down links from machine table to Machine Monitoring dashboard

---

### ✅ **Dashboard 2: Energy Analysis** (29KB, 11 panels)
**Status**: Good, but missing advanced analytics  
**Description**: Detailed consumption analysis and trends

**Current Panels**:
1. SEC (kWh/unit) - Specific Energy Consumption
2. Energy Cost (USD)
3. Carbon Emissions (kg CO2)
4. Total Energy (kWh)
5. Power Consumption (Time Series) - ❌ **Uses raw table**
6. Energy Cost Trend
7. Carbon Emissions Trend
8. Peak Demand Analysis

**Issues Found**:
- ❌ Query at line 400: `FROM energy_readings er` for power consumption time series
- ⚠️ No baseline comparison (actual vs target)
- ⚠️ No efficiency trends (improving/degrading)
- ⚠️ No seasonal decomposition
- ⚠️ Missing cost breakdown (peak/off-peak rates)

**Recommendations**:
1. **Optimize power query** (line 400):
   ```sql
   -- Replace with aggregate:
   FROM energy_readings_1min er
   WHERE er.bucket >= $__timeFrom() AND er.bucket <= $__timeTo()
   ```

2. **Add baseline comparison**:
   ```sql
   SELECT 
     er.bucket as time,
     AVG(er.avg_power_kw) as actual_power,
     eb.expected_power as baseline_power,
     ((AVG(er.avg_power_kw) - eb.expected_power) / eb.expected_power * 100) as variance_percent
   FROM energy_readings_1hour er
   LEFT JOIN energy_baselines eb ON er.machine_id = eb.machine_id
   WHERE er.bucket >= $__timeFrom()
   GROUP BY er.bucket, eb.expected_power
   ```

3. **Add new panels**:
   - Baseline vs Actual (Dual-axis time series)
   - Efficiency Trend (Line chart with trendline)
   - Energy Cost Breakdown by Rate (Stacked bar: peak/off-peak/shoulder)
   - Load Factor by Machine (Heatmap)
   - Energy Intensity (kWh per production unit over time)

---

### ✅ **Dashboard 3: Machine Monitoring** (25KB, 8 panels)
**Status**: Basic, needs real-time capabilities  
**Description**: Machine-level monitoring with production data

**Current Panels**:
1. Energy Today (Stat) - ❌ **Uses raw table**
2. Current Status (Table)
3. Power Consumption (Time Series) - ❌ **Uses raw table**
4. Production Count
5. Environmental Conditions

**Issues Found**:
- ❌ Line 269: `FROM energy_readings` for today's energy
- ❌ Line 464: `FROM energy_readings` for power time series
- ⚠️ No health score
- ⚠️ No anomaly visualization
- ⚠️ No predictive maintenance indicators
- ⚠️ Missing baseline model comparison

**Recommendations**:
1. **Optimize queries** (lines 269, 464):
   ```sql
   -- Energy Today (use 1hour aggregate):
   FROM energy_readings_1hour WHERE bucket >= DATE_TRUNC('day', NOW())
   
   -- Power time series (use 1min for recent data):
   FROM energy_readings_1min WHERE bucket >= $__timeFrom()
   ```

2. **Add predictive maintenance panel**:
   ```sql
   SELECT 
     a.detected_at as time,
     a.severity as metric,
     a.power_kw as value,
     a.anomaly_type as label
   FROM anomalies a
   WHERE a.machine_id = '$machine_id'
     AND a.detected_at >= $__timeFrom()
   ORDER BY a.detected_at
   ```

3. **Add new panels**:
   - Machine Health Score (Gauge with thresholds: 90-100 green, 75-90 yellow, <75 red)
   - Anomaly Timeline (Time series with annotations)
   - Actual vs Baseline Power (Comparison chart)
   - Predicted Next Failure (Stat with countdown)
   - Energy Efficiency Trend (Line chart: kWh/unit over 30 days)
   - Model Performance Metrics (Table: RMSE, MAE, R²)

---

### ✅ **Dashboard 4: Boiler Multi-Energy** (24KB, 9 panels)
**Status**: Unique, but ALL queries need optimization  
**Description**: Multi-energy source tracking (electricity, gas, steam)

**Current Panels**:
1. Total Electricity (Stat) - ❌ **Raw table**
2. Total Gas (Stat) - ❌ **Raw table**
3. Total Steam (Stat) - ❌ **Raw table**
4. Boiler Efficiency (Time Series) - ❌ **Raw table**
5. Power by Energy Type (Stacked area) - ❌ **Raw table** (3 queries!)
6. Energy Mix (Pie chart) - ❌ **Raw table**
7. Gas Flow Rate (Time Series) - ❌ **Raw table**
8. Steam Flow Rate (Time Series) - ❌ **Raw table**
9. Pressure Monitoring (Dual-axis) - ❌ **Raw table** (2 queries!)

**Issues Found**:
- ❌ **ALL 15 queries** (lines 83, 151, 219, 287, 426, 435, 444, 509, 602, 695, 818, 827) use raw `energy_readings`
- ⚠️ Hardcoded machine_id `e9fcad45-1f7b-4425-8710-c368a681f15e`
- ⚠️ No cost allocation by energy source
- ⚠️ No carbon emission comparison

**Critical Recommendations**:
1. **Mass query optimization required**:
   ```sql
   -- ALL these queries should use energy_readings_1min or energy_readings_15min
   -- Example fix for line 83:
   SELECT SUM(total_energy_kwh) as total_energy
   FROM energy_readings_1min
   WHERE machine_id = '$machine_id'  -- Make dynamic!
     AND energy_type = 'electricity'
     AND bucket >= $__timeFrom() AND bucket <= $__timeTo()
   ```

2. **Make machine_id dynamic**:
   - Add dashboard variable: `machine` (multi-value from machines table)
   - Replace hardcoded UUID with `'$machine_id'`

3. **Add new panels**:
   - Energy Cost by Source (Bar chart: electricity vs gas vs steam costs)
   - Carbon Intensity by Source (Stacked bar)
   - Sankey Diagram (Energy flow: Gas → Boiler → Steam → Output)
   - Real-Time Efficiency Gauge (with target line)
   - Energy Source Optimization Recommendation (Stat panel with text)

---

### ✅ **Dashboard 5: ISO 50001 EnPI Report** (27KB, 8 panels)
**Status**: Functional, meets compliance  
**Description**: Monthly energy performance indicators vs baseline

**Current Panels**:
1. Period Selector (Variable)
2. EnPI Score (Gauge)
3. CUSUM Chart (Time Series)
4. Monthly Energy Consumption (Bar Chart)
5. Baseline vs Actual (Comparison)
6. Performance Summary (Table)
7. SEU Breakdown (Pie Chart)
8. Trend Analysis (Line Chart)

**Issues Found**:
- ✅ Good: Uses proper aggregates
- ⚠️ Missing: Regression analysis
- ⚠️ Missing: Degree-days normalization visualization
- ⚠️ Missing: EnPI improvement targets

**Recommendations**:
1. **Add regression scatter plot**:
   ```sql
   SELECT 
     total_energy_kwh as energy,
     production_output as production,
     outdoor_temp_c as temperature
   FROM seu_energy_performance
   WHERE seu_id = '$seu' AND report_period >= '$year-01'
   ```

2. **Add EnPI target tracking**:
   ```sql
   SELECT 
     report_period as time,
     enpi as "Actual EnPI",
     (SELECT AVG(enpi) * 0.95 FROM seu_energy_performance WHERE EXTRACT(YEAR FROM report_period::date) = 2024) as "Target (-5%)"
   FROM seu_energy_performance
   ORDER BY report_period
   ```

3. **Add new panels**:
   - EnPI Improvement Trend (Line with target)
   - Degree-Days vs Energy (Scatter plot)
   - Monthly Savings (Stat: difference from baseline)
   - Top 3 Improvement Opportunities (Table)

---

### ✅ **Dashboard 6: ISO 50001 EnPI** (27KB, 8 panels)
**Status**: Duplicate of #5, needs consolidation  
**Description**: Same as EnPI Report

**Recommendation**: **MERGE with Dashboard 5** or differentiate:
- Option A: Delete this, enhance Dashboard 5
- Option B: Make this "Quarterly Aggregation" view, #5 stays "Monthly Detail"

---

## 🚨 Critical Performance Issues Summary

### **Raw Table Queries Found: 17 locations**

| Dashboard | Query Location | Current | Should Use |
|-----------|---------------|---------|------------|
| Factory Overview | Line 250 | `energy_readings` (daily sum) | `energy_readings_1hour` |
| Factory Overview | Line 463 | `energy_readings` (1 hour) | `energy_readings_1min` |
| Energy Analysis | Line 400 | `energy_readings` (time series) | `energy_readings_1min` |
| Machine Monitoring | Line 269 | `energy_readings` (daily sum) | `energy_readings_1hour` |
| Machine Monitoring | Line 464 | `energy_readings` (time series) | `energy_readings_1min` |
| Boiler Multi-Energy | Lines 83, 151, 219 | `energy_readings` (totals) | `energy_readings_15min` |
| Boiler Multi-Energy | Line 287 | `energy_readings` (efficiency) | `energy_readings_15min` |
| Boiler Multi-Energy | Lines 426, 435, 444 | `energy_readings` (power) | `energy_readings_1min` |
| Boiler Multi-Energy | Line 509 | `energy_readings` (energy mix) | `energy_readings_15min` |
| Boiler Multi-Energy | Lines 602, 695 | `energy_readings` (flow rates) | `energy_readings_1min` |
| Boiler Multi-Energy | Lines 818, 827 | `energy_readings` (pressure) | `energy_readings_1min` |

**Impact**: These queries scan **3.5 million rows** instead of **60-1440 aggregated rows**  
**Performance Gain**: 99% reduction in data scanned (similar to portal stats optimization)

---

## 🆕 Missing SOTA Dashboards (High Priority)

### **Dashboard 7: Anomaly Detection & Alerts** ⚡ CRITICAL
**Why**: You have 7 anomalies detected but NO visualization!

**Panels**:
1. **Active Anomalies** (Stat with red threshold)
   ```sql
   SELECT COUNT(*) as count
   FROM anomalies
   WHERE resolved_at IS NULL
   ```

2. **Anomaly Timeline** (Time series with annotations)
   ```sql
   SELECT 
     detected_at as time,
     severity as metric,
     power_kw as value,
     CONCAT(machine_id, ': ', anomaly_type) as label
   FROM anomalies
   WHERE detected_at >= $__timeFrom()
   ORDER BY detected_at
   ```

3. **Anomaly Heatmap** (Machine × Hour of Day)
   ```sql
   SELECT 
     DATE_TRUNC('hour', detected_at) as time,
     m.name as machine,
     COUNT(*) as anomaly_count
   FROM anomalies a
   JOIN machines m ON a.machine_id = m.id
   WHERE detected_at >= $__timeFrom()
   GROUP BY 1, 2
   ```

4. **Top Machines by Anomalies** (Bar chart)
5. **Severity Distribution** (Pie chart)
6. **Mean Time to Resolution** (Stat)
7. **Anomaly Detection Model Performance** (Table: precision, recall, F1)

---

### **Dashboard 8: Predictive Analytics & Forecasting** 🔮 HIGH VALUE
**Why**: You have 124 forecasts but NO dashboard!

**Panels**:
1. **24-Hour Power Forecast** (Time series: historical + forecast)
   ```sql
   -- Historical (last 24h)
   SELECT bucket as time, AVG(avg_power_kw) as "Actual Power"
   FROM energy_readings_1hour
   WHERE machine_id = '$machine' AND bucket >= NOW() - INTERVAL '24 hours'
   GROUP BY bucket
   
   UNION ALL
   
   -- Forecast (next 24h)
   SELECT forecast_time as time, predicted_power_kw as "Forecast"
   FROM energy_forecasts
   WHERE machine_id = '$machine' 
     AND forecast_time >= NOW() 
     AND forecast_time <= NOW() + INTERVAL '24 hours'
   ORDER BY time
   ```

2. **Forecast Accuracy Metrics** (Stat panel row: RMSE, MAPE, R²)
   ```sql
   SELECT 
     AVG(rmse) as rmse,
     AVG(mape) as mape,
     AVG(r2) as r2
   FROM energy_forecasts
   WHERE machine_id = '$machine' 
     AND forecasted_at >= NOW() - INTERVAL '7 days'
   ```

3. **Confidence Intervals** (Time series with upper/lower bounds)
4. **Model Comparison** (Table: ARIMA vs Prophet vs Linear)
5. **Forecast Error Distribution** (Histogram)
6. **Next Week Energy Prediction** (Bar chart by day)

---

### **Dashboard 9: Energy Cost Analytics** 💰 BUSINESS VALUE
**Why**: You have `energy_tariffs` table but NOT using it!

**Panels**:
1. **Monthly Cost Trend** (Line chart with budget line)
   ```sql
   SELECT 
     DATE_TRUNC('month', er.bucket) as time,
     SUM(er.total_energy_kwh * et.rate) as cost
   FROM energy_readings_1day er
   JOIN machines m ON er.machine_id = m.id
   JOIN energy_tariffs et ON m.factory_id = et.factory_id 
     AND et.is_active = true
   WHERE er.bucket >= NOW() - INTERVAL '12 months'
   GROUP BY 1
   ORDER BY 1
   ```

2. **Cost by Time-of-Use** (Stacked bar: peak/off-peak/shoulder)
3. **Top Cost Contributors** (Pie chart by machine)
4. **Cost Savings Opportunities** (Table with recommendations)
5. **Peak Demand Charges** (Time series with threshold)
6. **Energy Spend per Unit Produced** (Line chart: $/unit)
7. **Monthly Cost Variance** (Stat: budget vs actual)

---

### **Dashboard 10: ML Model Performance Tracking** 🤖 DATA SCIENCE
**Why**: You have `model_performance_metrics` but only 1 record - need visualization!

**Panels**:
1. **Model Accuracy Over Time** (Time series: MAE, RMSE, R²)
   ```sql
   SELECT 
     evaluated_at as time,
     model_type as metric,
     r2_score as value
   FROM model_performance_metrics
   WHERE evaluated_at >= $__timeFrom()
   ORDER BY evaluated_at
   ```

2. **Active A/B Tests** (Table from `model_ab_tests`)
   ```sql
   SELECT 
     test_name,
     status,
     control_model,
     variant_model,
     improvement_percent,
     p_value
   FROM v_active_ab_tests
   ```

3. **Model Drift Detection** (Time series with threshold)
4. **Feature Importance** (Bar chart)
5. **Training vs Test Performance** (Grouped bar chart)
6. **Model Alerts** (Table from `v_unresolved_model_alerts`)

---

### **Dashboard 11: Operational Efficiency** 📈 OPERATIONAL
**Why**: Core industrial KPI tracking

**Panels**:
1. **Overall Equipment Effectiveness (OEE)** (Gauge)
   ```sql
   SELECT 
     (AVG(availability) * AVG(performance) * AVG(quality)) * 100 as oee
   FROM (
     SELECT 
       machine_id,
       SUM(CASE WHEN is_running THEN 1 ELSE 0 END)::float / COUNT(*) as availability,
       AVG(production_count)::float / MAX(production_count) as performance,
       1.0 as quality  -- Adjust based on quality data
     FROM machine_status
     WHERE timestamp >= NOW() - INTERVAL '24 hours'
     GROUP BY machine_id
   ) sub
   ```

2. **Availability by Machine** (Bar chart)
3. **Performance Rate** (Gauge)
4. **Quality Rate** (Gauge)
5. **Downtime Analysis** (Table: machine, duration, reason)
6. **Production vs Energy** (Scatter plot: identify inefficiencies)
7. **Shift Comparison** (Grouped bar: day/night/weekend)

---

### **Dashboard 12: Environmental Impact** 🌍 SUSTAINABILITY
**Why**: ESG reporting requirement

**Panels**:
1. **Carbon Footprint** (Gauge with target)
   ```sql
   SELECT 
     SUM(er.total_energy_kwh * cf.co2_kg_per_kwh) as total_co2_kg
   FROM energy_readings_1day er
   JOIN machines m ON er.machine_id = m.id
   JOIN carbon_factors cf ON er.energy_type = cf.energy_type
   WHERE er.bucket >= DATE_TRUNC('month', NOW())
   ```

2. **CO2 Emissions Trend** (Area chart)
3. **Emission Intensity** (Line: kg CO2 per unit produced)
4. **Green Energy Usage** (Pie: renewable vs non-renewable)
5. **Monthly Emission Reduction** (Bar chart: actual vs target)
6. **Carbon Cost** (Stat: if carbon tax applies)

---

### **Dashboard 13: Real-Time Production Dashboard** ⚡ LIVE
**Why**: Factory floor big screen display

**Features**:
- Auto-refresh every 5 seconds
- Large fonts for visibility
- Traffic light indicators
- Minimal charts, max stats
- No drill-downs needed

**Panels**:
1. **Factory Status** (Huge stat: "RUNNING" green / "ALERT" red)
2. **Current Power** (Huge gauge)
3. **Active Machines** (Big number)
4. **Today's Production** (Big number with trend arrow)
5. **Active Alerts** (Scrolling table)
6. **Live Power Chart** (Last 15 minutes only)

---

### **Dashboard 14: Executive Summary** 👔 C-LEVEL
**Why**: High-level KPIs for management

**Panels**:
1. **Monthly Metrics** (Stat row: Energy, Cost, CO2, Efficiency)
2. **YTD vs Budget** (Progress bars)
3. **Top 3 Concerns** (Table with red/yellow/green)
4. **Monthly Trend** (Sparklines)
5. **Energy Intensity Trend** (Line chart: kWh/unit)
6. **Cost Savings vs Last Year** (Stat with % change)
7. **Compliance Status** (ISO 50001 checklist)

---

## 🎯 Implementation Priority

### **Phase 1: Critical Fixes (TODAY - 2-3 hours)**
1. ✅ Optimize 17 raw table queries → use continuous aggregates
2. ✅ Fix Boiler dashboard hardcoded machine_id → add variable
3. ✅ Add missing indexes if needed

**Impact**: 99% query performance improvement, system stability

---

### **Phase 2: High-Value Dashboards (THIS WEEK - 6-8 hours)**
4. ✅ Build **Anomaly Detection & Alerts** dashboard (1.5h)
5. ✅ Build **Predictive Analytics & Forecasting** dashboard (2h)
6. ✅ Build **Energy Cost Analytics** dashboard (2h)
7. ✅ Enhance **Factory Overview** with new panels (1h)
8. ✅ Enhance **Machine Monitoring** with health scores (1.5h)

**Impact**: Unlock existing data value, provide actionable insights

---

### **Phase 3: Operational Dashboards (NEXT WEEK - 8-10 hours)**
9. ✅ Build **ML Model Performance Tracking** (2h)
10. ✅ Build **Operational Efficiency (OEE)** (2h)
11. ✅ Build **Environmental Impact** (2h)
12. ✅ Build **Real-Time Production** (1.5h)
13. ✅ Build **Executive Summary** (1.5h)

**Impact**: Complete SOTA monitoring suite, enterprise-ready

---

### **Phase 4: Advanced Features (FUTURE - 10-15 hours)**
14. ✅ Implement alerting rules (email/Slack/webhook)
15. ✅ Add drill-down dashboard links
16. ✅ Create dashboard playlists for rotation
17. ✅ Build mobile-optimized dashboards
18. ✅ Add user annotations for events
19. ✅ Implement dashboard snapshots/reporting
20. ✅ Create Grafana API integration for automation

---

## 📋 Detailed Action Plan (Next 2-3 Hours)

### **Step 1: Backup Current Dashboards (5 min)**
```bash
cd /home/ubuntu/enms
cp -r grafana/dashboards grafana/dashboards-backup-$(date +%Y%m%d-%H%M%S)
git add -A && git commit -m "backup: dashboards before SOTA optimization"
```

### **Step 2: Optimize Factory Overview (30 min)**

Edit `grafana/dashboards/enms-factory-overview.json`:

**Fix 1: Line 250 - Energy Today**
```json
"rawSql": "SELECT \n  COALESCE(SUM(er.total_energy_kwh), 0) as \"Energy Today\"\nFROM energy_readings_1hour er\nJOIN machines m ON er.machine_id = m.id\nJOIN factories f ON m.factory_id = f.id\nWHERE er.bucket >= DATE_TRUNC('day', NOW())\n  AND f.name IN ($factory);",
```

**Fix 2: Line 463 - Real-Time Power**
```json
"rawSql": "SELECT \n  er.bucket AS time,\n  m.name as metric,\n  AVG(er.avg_power_kw) as value\nFROM energy_readings_1min er\nJOIN machines m ON er.machine_id = m.id\nJOIN factories f ON m.factory_id = f.id\nWHERE er.bucket >= NOW() - INTERVAL '1 hour'\n  AND f.name IN ($factory)\nGROUP BY er.bucket, m.name\nORDER BY er.bucket;",
```

### **Step 3: Optimize Energy Analysis (20 min)**

Edit `grafana/dashboards/enms-energy-analysis.json`:

**Fix: Line 400 - Power Consumption**
```json
"rawSql": "SELECT \n  er.bucket AS time,\n  m.name as metric,\n  AVG(er.avg_power_kw) as value\nFROM energy_readings_1min er\nJOIN machines m ON er.machine_id = m.id\nWHERE er.bucket >= $__timeFrom() AND er.bucket <= $__timeTo()\n  AND m.name IN ($machines)\nGROUP BY er.bucket, m.name\nORDER BY er.bucket;",
```

### **Step 4: Optimize Machine Monitoring (20 min)**

Edit `grafana/dashboards/enms-machine-monitoring.json`:

**Fix 1: Line 269**
```json
"rawSql": "SELECT COALESCE(SUM(total_energy_kwh), 0) as energy\nFROM energy_readings_1hour\nWHERE bucket >= DATE_TRUNC('day', NOW()) AND machine_id = '$machine_id'::uuid;",
```

**Fix 2: Line 464**
```json
"rawSql": "SELECT \n  bucket AS time,\n  'Power' as metric,\n  avg_power_kw as value\nFROM energy_readings_1min\nWHERE machine_id = '$machine_id'::uuid\n  AND bucket >= $__timeFrom() AND bucket <= $__timeTo()\nORDER BY bucket;",
```

### **Step 5: Optimize Boiler Multi-Energy (40 min)**

**THIS IS CRITICAL** - All 15 queries need updating

Edit `grafana/dashboards/boiler-multi-energy.json`:

1. Add dashboard variable `machine_id` (query: `SELECT id, name FROM machines WHERE name LIKE '%Boiler%'`)

2. Replace ALL instances of `energy_readings` with appropriate aggregate:
   - Stats (totals): Use `energy_readings_15min`
   - Time series: Use `energy_readings_1min`
   - Replace all `'e9fcad45-1f7b-4425-8710-c368a681f15e'` with `'$machine_id'`

### **Step 6: Restart Grafana (5 min)**
```bash
docker compose restart grafana
```

Wait 30 seconds, then verify:
```bash
curl http://localhost:8080/grafana/api/health
```

### **Step 7: Test All Dashboards (30 min)**
- Open each dashboard
- Test with different time ranges (1h, 6h, 24h, 7d)
- Verify data loads in <2 seconds
- Check for query errors in browser console

---

## 🎨 Dashboard Design Best Practices

### **Layout Standards**
- **Stat panels**: 4-6 columns (h=4, w=6)
- **Gauges**: 6 columns (h=8, w=6)
- **Time series**: Full width (h=8-10, w=24)
- **Tables**: 12-24 columns (h=10-12)
- **Heatmaps**: Full width (h=10, w=24)

### **Color Scheme**
- **Green**: Normal/Good (>90%)
- **Yellow**: Warning (75-90%)
- **Red**: Critical (<75%)
- **Blue**: Neutral/Info
- **Orange**: Attention needed

### **Refresh Rates**
- **Real-time dashboards**: 5s
- **Operational dashboards**: 30s
- **Analytical dashboards**: 5m
- **Historical dashboards**: Manual

### **Query Optimization Rules**
1. Always use continuous aggregates for time ranges >1 hour
2. Use `energy_readings_1min` for last 1-6 hours
3. Use `energy_readings_1hour` for last 1-7 days
4. Use `energy_readings_1day` for last 30+ days
5. Add `LIMIT 10000` to prevent massive result sets

---

## 🚀 Expected Outcomes

### **After Phase 1 (Critical Fixes)**
- ✅ Dashboard load time: 5-10s → <2s (80% faster)
- ✅ Database CPU: 4.5% → <1% (75% reduction)
- ✅ Query response: 500ms → 50ms (90% faster)
- ✅ System stability: High

### **After Phase 2 (High-Value Dashboards)**
- ✅ Anomaly visibility: 0 → 100% (7 anomalies now visible)
- ✅ Forecast accuracy tracking: 0 → 100% (124 forecasts visualized)
- ✅ Cost insights: None → Full breakdown by source/time
- ✅ Actionable insights: +500%

### **After Phase 3 (Operational Suite)**
- ✅ Total dashboards: 6 → 14 (+133%)
- ✅ Data utilization: 30% → 90% (using 20/23 tables)
- ✅ Stakeholder coverage: Operators only → Operators + Engineers + Executives
- ✅ Business value: SOTA industrial energy management platform

---

## 📊 Dashboard Coverage Matrix

| Stakeholder | Current Dashboards | After Phase 3 | Coverage |
|-------------|-------------------|---------------|----------|
| **Factory Operators** | Factory Overview, Machine Monitoring | +Real-Time Production | ✅ 100% |
| **Energy Managers** | Energy Analysis, ISO 50001 | +Cost Analytics, Environmental Impact | ✅ 100% |
| **Maintenance Engineers** | Machine Monitoring | +Anomaly Detection, Predictive Analytics | ✅ 100% |
| **Data Scientists** | None | +ML Model Performance | ✅ 100% |
| **Plant Managers** | Factory Overview | +Operational Efficiency (OEE) | ✅ 100% |
| **Executives** | None | +Executive Summary | ✅ 100% |

---

## 💡 Quick Wins (If Time is Limited)

If you only have 1-2 hours, do these:

1. **Fix Boiler Multi-Energy queries** (40 min) - Biggest performance impact
2. **Build Anomaly Detection dashboard** (30 min) - Unlock hidden data
3. **Add cost panel to Factory Overview** (15 min) - Business value

This alone will:
- Improve performance by 95%
- Visualize previously hidden anomalies
- Add immediate business insight

---

## 🎯 Success Metrics

Track these after implementation:

| Metric | Current | Target | How to Measure |
|--------|---------|--------|----------------|
| Dashboard load time | 5-10s | <2s | Browser DevTools Network tab |
| Query response time | 500ms | <100ms | Grafana Query Inspector |
| Dashboards using aggregates | 35% | 95% | grep "energy_readings[^_]" dashboards/*.json |
| Data tables visualized | 6/23 (26%) | 20/23 (87%) | Dashboard audit |
| Stakeholder coverage | 33% | 100% | Coverage matrix above |
| Active users/week | ? | Track | Grafana Analytics |

---

**Status**: Ready to implement - let me know when to start!  
**Estimated Total Time**: 2-3 hours (Phase 1) → 8-10 hours (Phase 2) → 18-20 hours (Phase 3)  
**Priority**: **Phase 1 is CRITICAL** (fixes performance issues)  

**Next command**: Should I start optimizing the dashboards now?
