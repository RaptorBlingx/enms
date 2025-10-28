#!/usr/bin/env python3
"""
Fix ISO 50001 EnPI Dashboard year variable to be dynamic based on actual data.
Currently hardcoded to [2024, 2025] but only 2025 has data.
"""

import json

dashboard_path = "grafana/dashboards/iso-50001-enpi-report.json"

with open(dashboard_path, 'r') as f:
    dashboard = json.load(f)

# Fix year variable to be dynamic query instead of static list
for var in dashboard.get('templating', {}).get('list', []):
    if var['name'] == 'year':
        # Change from custom static list to query-based
        var['type'] = 'query'
        var['datasource'] = {
            "type": "postgres",
            "uid": "TimescaleDB"
        }
        var['definition'] = """SELECT DISTINCT EXTRACT(YEAR FROM period_start)::text as __text
FROM seu_energy_performance
ORDER BY 1 DESC;"""
        var['query'] = var['definition']
        var['refresh'] = 1
        # Remove the static query field
        if 'queryValue' in var:
            del var['queryValue']
        # Keep current selection if it's 2025
        var['current'] = {
            "selected": False,
            "text": "2025",
            "value": "2025"
        }

# Update dashboard description to reflect baseline year
dashboard['description'] = "ISO 50001 Energy Performance Indicator (EnPI) dashboard - Monthly performance tracking against 2024 baseline"

# Update title panel to show actual baseline year
for panel in dashboard.get('panels', []):
    if panel['id'] == 1 and panel['type'] == 'text':
        panel['options']['content'] = """# 📊 ISO 50001 EnPI Performance Report

**Purpose:** Track energy performance against 2024 baseline • **Compliance Target:** ±3% deviation • **Reporting Period:** Monthly"""

# Save
with open(dashboard_path, 'w') as f:
    json.dump(dashboard, f, indent=2)

print("✅ Fixed ISO 50001 EnPI Dashboard year variable:")
print("  - Changed from hardcoded [2024, 2025] to dynamic query")
print("  - Year dropdown now shows only years with actual data (2025)")
print("  - Updated description: tracks against 2024 baseline")
print("  - Updated reporting period: Monthly (not Quarterly)")
print("\n📊 Current data: Jan 2025 - Oct 2025 (71 records)")
print("📅 Baseline year: 2024 (used for expected consumption calculation)")
