# Grafana Dashboards Enhancement Plan

**Date:** October 17, 2025  
**Author:** EnMS Development Team  
**Purpose:** Integrate analytics features from the Analytics UI into Grafana dashboards  
**Status:** Phase 1 Complete ✅ | Phase 2-5 Pending

---

## 🎉 What's New - Phase 1 Complete!

### Energy Analysis Dashboard
- **New KPI Stat Panels (4):**
  - SEC (Specific Energy Consumption) with color thresholds
  - Energy Cost in USD (customizable rate)
  - Carbon Emissions in kg CO₂ (customizable factor)
  - Total Energy Consumption
- **New Variables (2):**
  - `$cost_per_kwh` - default 0.15 (editable textbox)
  - `$carbon_factor` - default 0.45 (editable textbox)

### Factory Overview Dashboard
- **New Panels (2):**
  - Top 5 Energy Consumers bar chart (Last 24h)
  - Machine Efficiency Ranking table with:
    - Rank by SEC (best to worst)
    - SEC with color thresholds
    - Load Factor % with color coding
    - Total Energy consumption

### Access the Dashboards
🔗 http://10.33.10.109:8080/grafana/
- Username: `admin` / Password: `admin`

**Git Commits:**
- `5df85f3` - Backup before enhancement
- `ee9acd6` - Added KPI panels and variables
- `a0ba6e7` - Added comparison panels (Phase 1 complete)

---

## 📋 Executive Summary

This document outlines a comprehensive plan to enhance the existing Grafana dashboards by incorporating features from the Analytics service pages. We currently have 3 Grafana dashboards and multiple Analytics UI pages with advanced visualizations. The goal is to bring the best features from Analytics into Grafana for unified monitoring.

---

## 🔍 Current State Analysis

### Existing Grafana Dashboards

#### 1. **Factory Overview** (`enms-factory-overview.json`)
- **Purpose:** Real-time factory-wide monitoring
- **Refresh:** 5 seconds
- **Variables:** None
- **Panels (7):**
  - Active Machines count
  - Current Total Power (stat)
  - Energy Today (stat)
  - Active Alerts count
  - Power Consumption - Last Hour (time series)
  - Machine Status table
  - Energy by Machine (pie chart)

#### 2. **Energy Analysis** (`enms-energy-analysis.json`)
- **Purpose:** Detailed energy analysis and trends
- **Refresh:** 30 seconds
- **Variables:** `$machines` (multi-select, all machines)
- **Panels (7):**
  - Power Consumption Trend - Stacked (time series)
  - Hourly Energy Consumption (bar chart)
  - Peak Demand Analysis (time series)
  - Energy Summary by Machine (table)
  - Load Factor (gauge)
  - Daily Energy - Last 30 Days (bar chart)
  - Power Heatmap - 7 Days (heatmap)

#### 3. **Machine Monitoring** (`enms-machine-monitoring.json`)
- **Purpose:** Individual machine deep-dive
- **Refresh:** 10 seconds
- **Variables:** `$machine_id` (single-select)
- **Panels (9):**
  - Machine Status badge
  - Current Power (stat)
  - Energy Today (stat)
  - Units Produced Today (stat)
  - Power Consumption (time series)
  - Environmental Conditions - Temperature & Humidity (time series)
  - Production Output (time series)
  - Quality - Defect Rate (gauge)
  - Hourly Performance Summary (table)

---

### Analytics Service Features

#### 1. **KPI Dashboard** (`/ui/kpi`)
**Key Features:**
- 6 KPI Summary Cards:
  - SEC (Specific Energy Consumption) - kWh/unit
  - Peak Demand - kW
  - Load Factor - %
  - Energy Cost - USD
  - Carbon Intensity - kg CO₂
  - Total Energy - kWh
- 4 Time-Series Charts:
  - Energy Consumption Trend
  - Power Demand Profile
  - SEC Trend (Efficiency)
  - KPI Overview (Radar chart)
- Detailed KPI breakdown table
- Export CSV functionality
- Configurable time periods (24h, 7d, 30d, custom)

**Data Sources:**
- `/api/v1/kpi/sec` - Specific Energy Consumption
- `/api/v1/kpi/peak-demand` - Peak demand calculation
- `/api/v1/kpi/load-factor` - Load factor metrics
- `/api/v1/kpi/energy-cost` - Cost calculations
- `/api/v1/kpi/carbon` - Carbon emissions
- `/api/v1/timeseries/*` - Time-series data

#### 2. **Sankey Diagram** (`/ui/sankey`)
**Key Features:**
- Energy flow visualization: Grid → Factory → Departments → Machines
- Hierarchical energy distribution
- Interactive node selection
- Flow percentage calculations
- Multi-level drill-down

**Data Sources:**
- `/api/v1/sankey/data` - Energy flow data with hierarchy

#### 3. **Anomaly Heatmap** (`/ui/heatmap`)
**Key Features:**
- Hour-of-day × Machine anomaly frequency
- Day-of-week × Machine anomaly frequency
- Color intensity by anomaly count
- Average severity scoring
- Pattern identification (automatic insights)
- Interactive tooltips

**Data Sources:**
- `/api/v1/heatmap/hourly` - Hourly anomaly distribution
- `/api/v1/heatmap/daily` - Daily anomaly distribution

#### 4. **Machine Comparison** (`/ui/comparison`)
**Key Features:**
- Side-by-side comparison of 2-4 machines
- Energy metrics comparison (total, avg, peak)
- Efficiency metrics (SEC, load factor)
- Production metrics
- Performance ranking
- Winner identification
- Benchmark insights

**Data Sources:**
- `/api/v1/comparison/compare` - Multi-machine comparison data

#### 5. **Model Performance** (`/ui/model-performance`)
**Key Features:**
- ML model performance tracking
- Performance trend over time (R², RMSE, MAE, MAPE)
- Drift detection alerts
- Model version comparison
- Health status indicators
- Metrics evolution charts

**Data Sources:**
- `/api/v1/metrics/trend` - Performance metrics trend
- `/api/v1/metrics/latest` - Latest model metrics

---

## 🎯 Enhancement Recommendations

### Phase 1: Add KPI Panels (High Priority)

#### **Dashboard:** Energy Analysis
**Why:** Already has energy focus, perfect fit for KPIs

**New Panels to Add:**

1. **SEC (Specific Energy Consumption) Stat Panel**
   - Query: Custom SQL calculating `total_energy_kwh / total_production_units`
   - Position: Top row with other stats
   - Color thresholds: Green (< 0.05), Yellow (0.05-0.1), Red (> 0.1)
   - Unit: kWh/unit

2. **Energy Cost Panel**
   - Query: Calculate cost based on energy consumption × rate
   - Position: Top row
   - Unit: USD
   - Color: Green to red gradient

3. **Carbon Emissions Panel**
   - Query: Energy × Carbon intensity factor
   - Position: Top row
   - Unit: kg CO₂
   - Icon/color: Green theme

4. **SEC Trend Chart (Bar)**
   - Query: Daily SEC calculation over selected time range
   - Position: New row below existing charts
   - Visualization: Bar chart
   - Time range: Use dashboard time picker

**Variables to Add:**
- `$cost_per_kwh` - Constant or query-based (default: 0.15)
- `$carbon_factor` - kg CO₂ per kWh (default: 0.45)

**SQL Query Examples:**
```sql
-- SEC Calculation
SELECT 
  SUM(er.total_energy_kwh) / NULLIF(SUM(pd.production_count), 0) as sec
FROM energy_readings_1hour er
LEFT JOIN production_data_1hour pd ON er.bucket = pd.bucket AND er.machine_id = pd.machine_id
WHERE er.bucket >= $__timeFrom() AND er.bucket <= $__timeTo()
  AND er.machine_id IN (${machines:sqlstring})

-- Energy Cost
SELECT 
  SUM(total_energy_kwh) * $cost_per_kwh as cost_usd
FROM energy_readings_1hour
WHERE bucket >= $__timeFrom() AND bucket <= $__timeTo()
  AND machine_id IN (${machines:sqlstring})

-- Carbon Emissions
SELECT 
  SUM(total_energy_kwh) * $carbon_factor as carbon_kg
FROM energy_readings_1hour
WHERE bucket >= $__timeFrom() AND bucket <= $__timeTo()
  AND machine_id IN (${machines:sqlstring})
```

---

### Phase 2: Add Anomaly Heatmap (Medium Priority)

#### **Dashboard:** Create New Dashboard - "Anomaly Analysis"
**Why:** Anomaly data requires dedicated space, doesn't fit well in existing dashboards

**Option A: Use Grafana Native Heatmap (Recommended)**

**Panels:**

1. **Anomaly Heatmap - Hourly**
   - Query: Anomaly count by machine × hour of day
   - Visualization: Heatmap panel
   - Color scheme: Green (low) → Red (high)
   - Time range: Last 30 days

2. **Anomaly Heatmap - Daily**
   - Query: Anomaly count by machine × day of week
   - Visualization: Heatmap panel
   - Color scheme: Green (low) → Red (high)

3. **Total Anomalies Stat**
   - Count of anomalies in time range
   - Position: Top left

4. **Anomalies by Severity**
   - Pie chart: Critical, High, Medium, Low
   - Position: Top right

5. **Recent Anomalies Table**
   - Last 20 anomalies
   - Columns: Time, Machine, Severity, Description, Status

**SQL Query Examples:**
```sql
-- Hourly Heatmap
SELECT 
  time_bucket('1 hour', detected_at) as time,
  m.name as metric,
  COUNT(*) as value
FROM anomalies a
JOIN machines m ON a.machine_id = m.id
WHERE $__timeFilter(detected_at)
GROUP BY time, m.name
ORDER BY time, m.name

-- Daily Pattern (Day of Week)
SELECT 
  EXTRACT(DOW FROM detected_at)::int as hour,
  m.name as machine,
  COUNT(*) as count
FROM anomalies a
JOIN machines m ON a.machine_id = m.id
WHERE detected_at >= NOW() - INTERVAL '30 days'
GROUP BY EXTRACT(DOW FROM detected_at), m.name

-- Anomalies by Severity
SELECT 
  severity,
  COUNT(*) as count
FROM anomalies
WHERE $__timeFilter(detected_at)
GROUP BY severity
```

**Option B: Use Infinity Plugin for API Integration**
- Install Infinity datasource plugin
- Query `/api/v1/heatmap/hourly` directly
- More complex but preserves Analytics service logic

---

### Phase 3: Machine Comparison Panels (Medium Priority)

#### **Dashboard:** Factory Overview
**Why:** Factory-level view benefits from comparison features

**New Panels:**

1. **Top 5 Energy Consumers**
   - Bar chart: Machines ranked by energy consumption
   - Position: New row
   - Time range: Today or last 24h

2. **Efficiency Ranking Table**
   - Columns: Rank, Machine, SEC, Load Factor, Energy
   - Sorted by SEC (best to worst)
   - Color coding: Top 3 green, Bottom 3 red

3. **Energy Distribution by Type**
   - Pie chart: Energy consumption grouped by machine type
   - Position: Replace or supplement existing pie chart

**SQL Query Examples:**
```sql
-- Top Energy Consumers
SELECT 
  m.name as metric,
  SUM(er.total_energy_kwh) as value
FROM energy_readings_1hour er
JOIN machines m ON er.machine_id = m.id
WHERE $__timeFilter(bucket)
GROUP BY m.name
ORDER BY value DESC
LIMIT 5

-- Efficiency Ranking
SELECT 
  ROW_NUMBER() OVER (ORDER BY SUM(er.total_energy_kwh) / NULLIF(SUM(pd.production_count), 0)) as rank,
  m.name as machine,
  SUM(er.total_energy_kwh) / NULLIF(SUM(pd.production_count), 0) as sec,
  AVG(er.avg_power_kw) / NULLIF(MAX(er.max_power_kw), 0) * 100 as load_factor,
  SUM(er.total_energy_kwh) as energy_kwh
FROM energy_readings_1hour er
JOIN machines m ON er.machine_id = m.id
LEFT JOIN production_data_1hour pd ON er.bucket = pd.bucket AND er.machine_id = pd.machine_id
WHERE $__timeFilter(er.bucket)
  AND m.is_active = true
GROUP BY m.name
ORDER BY sec ASC
```

---

### Phase 4: Model Performance Monitoring (Low Priority)

#### **Dashboard:** Create New Dashboard - "ML Model Performance"
**Why:** Specialized ML metrics for data science team

**Panels:**

1. **Model Health Score**
   - Gauge: 0-100% health score
   - Based on latest R² and drift detection

2. **R² Trend Over Time**
   - Time series: R² values by model version
   - Target line at 0.8

3. **RMSE/MAE Trend**
   - Dual-axis time series
   - Track prediction accuracy

4. **Drift Detection Alerts**
   - Stat panel: Count of drift events
   - Color: Red if drift detected

5. **Model Versions Table**
   - Columns: Version, Date, R², RMSE, MAE, Status
   - Latest 10 versions

**SQL Query Examples:**
```sql
-- Latest Model Health
SELECT 
  CASE 
    WHEN r_squared > 0.8 AND NOT drift_detected THEN 100
    WHEN r_squared > 0.6 AND NOT drift_detected THEN 75
    WHEN r_squared > 0.4 THEN 50
    ELSE 25
  END as health_score
FROM model_performance
WHERE machine_id = $machine_id
ORDER BY evaluation_date DESC
LIMIT 1

-- R² Trend
SELECT 
  evaluation_date as time,
  model_version as metric,
  r_squared as value
FROM model_performance
WHERE machine_id = $machine_id
  AND evaluation_date >= $__timeFrom()
ORDER BY evaluation_date
```

**Note:** This requires the `model_performance` table to be queryable by Grafana. Alternative: Use Infinity plugin to query Analytics API.

---

### Phase 5: Sankey Diagram (Optional/Low Priority)

#### **Status:** Not Recommended for Grafana
**Reason:** Sankey diagrams are not natively supported in Grafana. While plugins exist, they are limited.

**Alternatives:**
1. **Keep in Analytics UI** - Best user experience
2. **Use FlowChart plugin** - Limited functionality
3. **Embed Analytics page** - Use Grafana's iframe/HTML panel to embed `/ui/sankey`

**Recommendation:** Keep Sankey in Analytics UI and add a link from Grafana dashboard

---

## 🔧 Variable Enhancements

### Recommended Variables to Add

#### 1. **Factory Overview Dashboard**

Add these variables:
- `$factory_id` - Filter by factory (for multi-factory deployments)
  ```sql
  SELECT id AS __value, name AS __text FROM factories ORDER BY name
  ```

- `$machine_type` - Filter by machine type (compressor, pump, etc.)
  ```sql
  SELECT DISTINCT type FROM machines WHERE is_active = true ORDER BY type
  ```

- `$time_range_quick` - Custom time range selector
  - Options: "Last Hour", "Today", "Last 24h", "This Week", "Last 7 Days"

#### 2. **Energy Analysis Dashboard**

Enhance existing `$machines` variable:
- Already good! Multi-select is perfect.

Add:
- `$cost_per_kwh` - Energy cost rate (default: 0.15)
  - Type: Constant or Custom variable
  - Value: 0.15

- `$carbon_factor` - Carbon emission factor (default: 0.45)
  - Type: Constant
  - Value: 0.45

- `$aggregation_interval` - Aggregation granularity
  - Options: "1 minute", "15 minutes", "1 hour", "1 day"
  - Default: "1 hour"

#### 3. **Machine Monitoring Dashboard**

Current `$machine_id` is good!

Add:
- `$baseline_id` - Select baseline model for comparison
  ```sql
  SELECT id AS __value, 
         CONCAT(model_name, ' (', training_start_date::date, ')') AS __text
  FROM energy_baselines
  WHERE machine_id = '$machine_id' AND is_active = true
  ORDER BY training_start_date DESC
  ```

- `$show_production` - Toggle production metrics (boolean)
  - Type: Custom
  - Options: "Yes", "No"
  - Use in panel visibility rules

---

## 📊 New Dashboard Proposals

### Dashboard 4: **Anomaly Analysis** (NEW)
**Purpose:** Centralized anomaly monitoring and pattern analysis

**Sections:**
1. **Summary (Row 1)**
   - Total Anomalies (stat)
   - Critical Anomalies (stat)
   - Resolution Rate % (gauge)
   - Avg Time to Resolve (stat)

2. **Heatmaps (Row 2-3)**
   - Anomaly Heatmap - Hourly (24×7 machines)
   - Anomaly Heatmap - Daily (7 days×machines)

3. **Details (Row 4)**
   - Recent Anomalies (table)
   - Anomalies by Machine (bar chart)
   - Anomalies by Severity (pie chart)

4. **Trends (Row 5)**
   - Anomaly Count Trend (time series)
   - MTBF - Mean Time Between Failures (time series)

**Variables:**
- `$severity` - Filter by severity (multi-select)
- `$machine` - Filter by machine (multi-select)
- `$status` - Active/Resolved/All

---

### Dashboard 5: **KPI Overview** (NEW)
**Purpose:** Executive-level KPI dashboard with ISO 50001 compliance metrics

**Sections:**
1. **Key Metrics (Row 1)**
   - SEC (stat with trend sparkline)
   - Peak Demand (stat)
   - Load Factor (gauge)
   - Energy Cost (stat)
   - Carbon Emissions (stat)
   - Energy Savings vs Baseline (stat %)

2. **Trends (Row 2-3)**
   - Energy Consumption Trend (time series)
   - SEC Trend (bar chart)
   - Cost Trend (time series)
   - Carbon Trend (time series)

3. **Comparison (Row 4)**
   - KPI Comparison by Machine (table)
   - Efficiency Ranking (bar chart)

4. **Targets (Row 5)**
   - SEC vs Target (gauge with thresholds)
   - Carbon Intensity vs Target (gauge)
   - Cost Budget Tracking (progress bar)

**Variables:**
- `$machines` - Multi-select machines
- `$aggregation` - Daily/Weekly/Monthly
- `$sec_target` - Target SEC value (constant)
- `$cost_budget` - Monthly cost budget (constant)

---

## 🎨 Design & UX Improvements

### Color Scheme Standardization
- **Energy:** Blue spectrum (#4facfe to #00f2fe)
- **Power:** Yellow/Orange (#ff9800 to #f5576c)
- **Efficiency:** Green (#43e97b to #38f9d7)
- **Anomalies/Alerts:** Red (#f44336 to #e91e63)
- **Production:** Purple (#667eea to #764ba2)

### Panel Layout Best Practices
1. **Top Row:** Always use for summary stats (4-6 panels)
2. **Middle Rows:** Charts and time-series
3. **Bottom Row:** Detailed tables
4. **Consistent Heights:** 
   - Stats: 4 units
   - Charts: 8-10 units
   - Tables: 10-12 units

### Thresholds & Alerts
Configure meaningful thresholds:
- **SEC:** Green < 0.05, Yellow 0.05-0.1, Red > 0.1 kWh/unit
- **Load Factor:** Red < 50%, Yellow 50-70%, Green > 70%
- **Power Factor:** Red < 0.8, Yellow 0.8-0.9, Green > 0.9
- **Anomaly Severity:** Info (blue), Warning (yellow), Critical (red)

---

## 🚀 Implementation Priority & Progress

### ✅ Backup Completed
- Backup created: `grafana/dashboards-backup/20251017-111648`
- Git commit: `5df85f3` - "Backup: Grafana dashboards before Phase 1 enhancement (KPI panels)"

### High Priority (Week 1-2) - ✅ PHASE 1 COMPLETE!
✅ **Must Have:**
1. ✅ Add KPI panels to Energy Analysis dashboard (COMPLETED)
   - ✅ SEC stat (panel ID: 100, gridPos x:0 y:0)
   - ✅ Energy cost stat (panel ID: 101, gridPos x:6 y:0)
   - ✅ Carbon emissions stat (panel ID: 102, gridPos x:12 y:0)
   - ✅ Total Energy stat (panel ID: 103, gridPos x:18 y:0)
2. ✅ Add variables for cost and carbon factor (COMPLETED)
   - ✅ $cost_per_kwh (default: 0.15)
   - ✅ $carbon_factor (default: 0.45)
3. ✅ Add efficiency ranking table to Factory Overview (COMPLETED)
   - ✅ Machine Efficiency Ranking table (panel ID: 201, Last 24h)
4. ✅ Add top energy consumers chart (COMPLETED)
   - ✅ Top 5 Energy Consumers bar chart (panel ID: 200, Last 24h)

**Phase 1 Summary:**
- Energy Analysis: 7 → 11 panels (added 4 KPI stats, 2 variables)
- Factory Overview: 9 → 11 panels (added 1 bar chart, 1 table)
- Total enhancements: 6 new panels, 2 new variables
- All queries tested and working with real-time data

### Medium Priority (Week 3-4) - NOT STARTED
⚠️ **Should Have:**
1. ⏳ Create Anomaly Analysis dashboard
2. ⏳ Implement anomaly heatmaps
3. ⏳ Add machine comparison features
4. ⏳ Enhance Factory Overview with machine type filter

**Note:** Phase 1 complete! Review dashboards and gather feedback before proceeding to Phase 2.

### Low Priority (Week 5+)
💡 **Nice to Have:**
1. Create KPI Overview dashboard
2. Create ML Model Performance dashboard
3. Add baseline comparison to Machine Monitoring
4. Implement iframe embedding for Sankey (if needed)

---

## 📝 Implementation Steps

### Step 1: Backup Current Dashboards
```bash
# Always backup before changes!
cd /home/ubuntu/enms
./scripts/backup-grafana-dashboards.sh
git add grafana/dashboards/*.json
git commit -m "Backup before enhancement phase"
```

### Step 2: Add Variables First
1. Open Grafana UI
2. Navigate to dashboard settings → Variables
3. Add new variables as specified above
4. Save dashboard
5. Export and commit to git

### Step 3: Add Panels Incrementally
1. **Test queries first** in Grafana Explore
2. Create one panel at a time
3. Test with real data
4. Adjust formatting and thresholds
5. Save and export after each successful panel

### Step 4: Create New Dashboards
1. Create dashboard in UI
2. Set UID: `enms-anomaly-analysis`, `enms-kpi-overview`, etc.
3. Add panels following the plan
4. Configure variables
5. Save with proper tags: `enms`, `anomaly`, `kpi`, etc.

### Step 5: Documentation
1. Update `GRAFANA-QUICKSTART.md` with new features
2. Create `GRAFANA-KPI-GUIDE.md` for KPI calculations
3. Document query patterns in `grafana/README.md`

---

## 🔍 Testing Checklist

Before considering enhancement complete:

- [ ] All queries return data (no empty panels)
- [ ] Variables work correctly and filter panels
- [ ] Thresholds trigger appropriate colors
- [ ] Time ranges work with dashboard time picker
- [ ] Refresh rates are appropriate (not too fast)
- [ ] Dashboards export cleanly to JSON
- [ ] JSON files are committed to git
- [ ] No console errors in browser
- [ ] Mobile/tablet view is acceptable
- [ ] Performance is acceptable (queries < 2 seconds)
- [ ] Documentation is updated

---

## 💡 Advanced Ideas (Future Consideration)

### 1. **Alert Rules Integration**
Create Grafana alert rules for:
- SEC exceeds target threshold
- Anomaly count spike (> 10 in 1 hour)
- Model drift detected
- Critical machines offline

### 2. **Playlist Creation**
Create auto-rotating dashboard playlist:
1. Factory Overview (30s)
2. Energy Analysis (30s)
3. Anomaly Analysis (20s)
4. KPI Overview (30s)
5. Machine Monitoring - Compressor-1 (20s)

Display on factory monitors!

### 3. **Report Scheduling**
Use Grafana Enterprise or Grafana Image Renderer:
- Daily energy report (PDF)
- Weekly KPI summary
- Monthly anomaly report
- Email to stakeholders

### 4. **External API Integration**
Use Infinity datasource to:
- Fetch weather data for correlation analysis
- Get electricity pricing (real-time)
- Import production schedules
- Connect to other factory systems

### 5. **Custom Panels**
Develop custom Grafana panels:
- Sankey diagram plugin (if community plugin insufficient)
- Machine topology map
- 3D factory floor plan with heat overlay

---

## 📚 References

### Documentation
- [Grafana Heatmap Panel](https://grafana.com/docs/grafana/latest/panels-visualizations/visualizations/heatmap/)
- [Grafana Variables](https://grafana.com/docs/grafana/latest/dashboards/variables/)
- [PostgreSQL/TimescaleDB Data Source](https://grafana.com/docs/grafana/latest/datasources/postgres/)
- [Infinity Data Source Plugin](https://grafana.com/grafana/plugins/yesoreyeram-infinity-datasource/)

### Internal Resources
- Analytics API Documentation: `API-DOCUMENTATION-SUMMARY.md`
- Database Schema: `database/init/*.sql`
- Existing Dashboards: `grafana/dashboards/*.json`
- Analytics Routes: `analytics/api/routes/*.py`

---

## ✅ Conclusion

This plan provides a **comprehensive roadmap** to enhance Grafana dashboards by integrating the best features from the Analytics service. The phased approach allows for:

1. **Quick wins** with KPI additions (Week 1-2)
2. **Meaningful insights** with anomaly analysis (Week 3-4)
3. **Long-term value** with ML monitoring and advanced features (Week 5+)

**Key Benefits:**
- ✅ Unified monitoring in Grafana
- ✅ Reduced need to switch between UIs
- ✅ Executive-ready KPI dashboards
- ✅ Better anomaly pattern visibility
- ✅ Machine comparison for optimization
- ✅ Maintains Analytics UI for specialized features (Sankey, detailed ML)

**Recommendation:** Start with **Phase 1 (KPI panels)** as it provides immediate value and requires minimal effort. Then assess user feedback before proceeding to Phases 2-4.

---

**Next Steps:**
1. Review this plan with stakeholders
2. Prioritize features based on user needs
3. Allocate development time (estimated 3-5 weeks total)
4. Begin implementation starting with Phase 1
5. Iterate based on feedback

**Questions or modifications?** Update this document and commit changes to track evolution of the enhancement plan.
