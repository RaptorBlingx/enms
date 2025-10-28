#!/usr/bin/env python3
"""
Fix ISO 50001 EnPI Report Dashboard
- Data is monthly (2025-01) not quarterly (2025-Q1)
- Need to aggregate monthly data into quarters
- Fix datasource references
- Fix time field references
- Add monthly breakdown query
"""

import json

dashboard_path = "grafana/dashboards/iso-50001-enpi-report.json"

with open(dashboard_path, 'r') as f:
    dashboard = json.load(f)

def fix_datasource(obj):
    """Recursively fix datasource references"""
    if isinstance(obj, dict):
        if 'datasource' in obj:
            if isinstance(obj['datasource'], str) and obj['datasource'] in ['PostgreSQL', 'TimescaleDB']:
                obj['datasource'] = {
                    "type": "postgres",
                    "uid": "TimescaleDB"
                }
        for value in obj.values():
            fix_datasource(value)
    elif isinstance(obj, list):
        for item in obj:
            fix_datasource(item)

# Fix datasources
fix_datasource(dashboard)

# Update panel queries
for panel in dashboard.get('panels', []):
    if 'targets' in panel:
        for target in panel['targets']:
            if 'rawSql' in target:
                old_sql = target['rawSql']
                
                # Panel 2: Compliance Status - use latest month
                if panel['id'] == 2:
                    target['rawSql'] = """SELECT 
  compliance_status
FROM seu_energy_performance
WHERE seu_id = '$seu_id'
  AND EXTRACT(YEAR FROM period_start) = $year::integer
ORDER BY period_start DESC
LIMIT 1;"""
                
                # Panel 3: Deviation Gauge - use latest month
                elif panel['id'] == 3:
                    target['rawSql'] = """SELECT 
  deviation_percent
FROM seu_energy_performance
WHERE seu_id = '$seu_id'
  AND EXTRACT(YEAR FROM period_start) = $year::integer
ORDER BY period_start DESC
LIMIT 1;"""
                
                # Panel 4: Actual vs Expected - monthly time series
                elif panel['id'] == 4:
                    target['rawSql'] = """SELECT 
  period_start as time,
  actual_consumption as "Actual (kWh)",
  expected_consumption as "Expected (kWh)"
FROM seu_energy_performance
WHERE seu_id = '$seu_id'
  AND EXTRACT(YEAR FROM period_start) = $year::integer
ORDER BY period_start;"""
                
                # Panel 5: Performance Table - monthly breakdown
                elif panel['id'] == 5:
                    target['rawSql'] = """SELECT 
  TO_CHAR(period_start, 'YYYY-MM') as "Month",
  ROUND(actual_consumption::numeric, 2) as "Actual (kWh)",
  ROUND(expected_consumption::numeric, 2) as "Expected (kWh)",
  ROUND(deviation_kwh::numeric, 2) as "Deviation (kWh)",
  ROUND(deviation_percent::numeric, 1) as "Deviation %",
  compliance_status as "Status"
FROM seu_energy_performance
WHERE seu_id = '$seu_id'
  AND EXTRACT(YEAR FROM period_start) = $year::integer
ORDER BY period_start;"""
                
                # Panel 6: EnPI Trend - monthly time series
                elif panel['id'] == 6:
                    target['rawSql'] = """SELECT 
  period_start as time,
  deviation_percent as "Deviation from Baseline (%)"
FROM seu_energy_performance
WHERE seu_id = '$seu_id'
ORDER BY period_start;"""
                
                # Panel 7: Baseline Model Info - keep query but fix datasource
                elif panel['id'] == 7:
                    target['rawSql'] = """SELECT 
  name,
  r_squared,
  rmse,
  regression_coefficients
FROM seus
WHERE id = '$seu_id';"""
                
                # Panel 8: Monthly Deviation Bar Chart - aggregate by quarter
                elif panel['id'] == 8:
                    target['rawSql'] = """SELECT 
  TO_CHAR(period_start, 'Mon') as "Month",
  deviation_percent as "Deviation %"
FROM seu_energy_performance
WHERE seu_id = '$seu_id'
  AND EXTRACT(YEAR FROM period_start) = $year::integer
  AND EXTRACT(QUARTER FROM period_start) = 
    CASE 
      WHEN '$quarter' LIKE '%-Q1' THEN 1
      WHEN '$quarter' LIKE '%-Q2' THEN 2
      WHEN '$quarter' LIKE '%-Q3' THEN 3
      WHEN '$quarter' LIKE '%-Q4' THEN 4
      ELSE EXTRACT(QUARTER FROM CURRENT_DATE)
    END
ORDER BY period_start;"""

# Update templating variables
for var in dashboard.get('templating', {}).get('list', []):
    if var['name'] == 'quarter':
        # Change quarter variable to use generated quarters from months
        var['definition'] = """SELECT DISTINCT 
  EXTRACT(YEAR FROM period_start)::text || '-Q' || EXTRACT(QUARTER FROM period_start)::text as __text
FROM seu_energy_performance
WHERE seu_id = '$seu_id'
ORDER BY 1 DESC;"""
        var['query'] = var['definition']

# Update panel 4 to be time series
for panel in dashboard.get('panels', []):
    if panel['id'] == 4:
        # Ensure it's configured as time series
        panel['type'] = 'timeseries'
        if 'fieldConfig' not in panel:
            panel['fieldConfig'] = {}
        if 'defaults' not in panel['fieldConfig']:
            panel['fieldConfig']['defaults'] = {}
        panel['fieldConfig']['defaults']['unit'] = 'kwatth'

# Update description
dashboard['description'] = "ISO 50001 Energy Performance Indicator (EnPI) dashboard - Monthly performance tracking with quarterly aggregation"

# Save
with open(dashboard_path, 'w') as f:
    json.dump(dashboard, f, indent=2)

print("✅ Fixed ISO 50001 EnPI Report dashboard:")
print("  - Fixed datasource references (TimescaleDB)")
print("  - Changed from quarterly to monthly reporting")
print("  - Fixed all 8 panel queries")
print("  - Panel 2: Latest compliance status")
print("  - Panel 3: Latest deviation gauge")
print("  - Panel 4: Actual vs Expected time series")
print("  - Panel 5: Monthly performance table")
print("  - Panel 6: EnPI trend over time")
print("  - Panel 7: Baseline model info")
print("  - Panel 8: Monthly deviation by quarter")
