#!/usr/bin/env python3
"""
Final fixes for ISO 50001 EnPI Dashboard:
1. SEU dropdown should only show SEUs with performance data
2. Fix Panel 8 (Monthly Deviation Breakdown) - no monthly_breakdown column exists
3. Update panel 5 title from "Quarterly" to "Monthly"
"""

import json

dashboard_path = "grafana/dashboards/iso-50001-enpi-report.json"

with open(dashboard_path, 'r') as f:
    dashboard = json.load(f)

# Fix templating variable to only show SEUs with performance data
for var in dashboard.get('templating', {}).get('list', []):
    if var['name'] == 'seu_id':
        var['definition'] = """SELECT DISTINCT s.id as __value, s.name as __text 
FROM seus s
INNER JOIN seu_energy_performance sep ON s.id = sep.seu_id
WHERE s.is_active = true 
ORDER BY s.name;"""
        var['query'] = var['definition']

# Fix panels
for panel in dashboard.get('panels', []):
    
    # Panel 5: Change title from "Quarterly" to "Monthly"
    if panel['id'] == 5:
        panel['title'] = "Monthly Performance Breakdown"
    
    # Panel 8: Fix Monthly Deviation Breakdown query (remove monthly_breakdown reference)
    if panel['id'] == 8:
        for target in panel.get('targets', []):
            if 'rawSql' in target:
                # The query should just show months within the selected quarter
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
                target['format'] = 'table'

# Save
with open(dashboard_path, 'w') as f:
    json.dump(dashboard, f, indent=2)

print("✅ Fixed ISO 50001 EnPI Dashboard:")
print("  - SEU dropdown now only shows SEUs with performance data (7 SEUs)")
print("  - Panel 5: Changed title to 'Monthly Performance Breakdown'")
print("  - Panel 8: Fixed query - removed non-existent monthly_breakdown column")
print("  - Panel 8: Now directly queries monthly data filtered by quarter")
print("\n⚠️  Note: Boiler-1 SEUs have no performance data yet - they won't appear in dropdown")
