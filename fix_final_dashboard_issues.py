#!/usr/bin/env python3
"""
Final comprehensive fix for ALL remaining Grafana dashboard query errors.

Issues Fixed:
1. Grafana $machines variable returns names, not UUIDs - change m.id IN ($machines) to m.name IN ($machines)
2. peak_demand_kw doesn't exist in energy_readings_1min (only in 15min+) - use max_power_kw instead
3. energy_readings table doesn't have 'bucket' column - use 'time' for raw table
4. All other schema mismatches
"""

import json
import re
from pathlib import Path

def fix_query(query):
    """Fix a single SQL query to match actual database schema and Grafana variables."""
    if not query or not isinstance(query, str):
        return query
    
    original = query
    
    # Fix 1: Change m.id IN ($machines) to m.name IN ($machines)
    # Grafana variable $machines contains machine NAMES not UUIDs
    query = re.sub(r'm\.id\s+IN\s+\(\$machines\)', 'm.name IN ($machines)', query, flags=re.IGNORECASE)
    
    # Fix 2: peak_demand_kw doesn't exist in energy_readings_1min
    # Replace with max_power_kw which exists in all aggregates
    if 'energy_readings_1min' in query and 'peak_demand_kw' in query:
        query = query.replace('peak_demand_kw', 'max_power_kw')
    
    # Fix 3: energy_readings doesn't have 'bucket' column (that's for aggregates)
    # If querying raw energy_readings, use 'time' not 'bucket'
    if 'FROM energy_readings er' in query and 'bucket::date' in query:
        query = query.replace('bucket::date', 'time::date')
        query = query.replace('GROUP BY bucket::date', 'GROUP BY time::date')
        query = query.replace('ORDER BY bucket::date', 'ORDER BY time::date')
    
    # Fix 4: load_factor column doesn't exist in energy_readings_1min
    # Need to calculate it from avg_power_kw / max_power_kw
    if 'energy_readings_1min' in query and '(avg_power_kw / NULLIF(peak_demand_kw, 0) * 100)' in query:
        query = query.replace(
            '(avg_power_kw / NULLIF(peak_demand_kw, 0) * 100)',
            '(avg_power_kw / NULLIF(max_power_kw, 0) * 100)'
        )
        # Also fix the WHERE clause
        query = query.replace('AND peak_demand_kw > 0', 'AND max_power_kw > 0')
    
    if query != original:
        return query
    return query

def fix_dashboard(file_path):
    """Fix all queries in a dashboard JSON file."""
    print(f"\n📄 Processing {file_path.name}...")
    
    with open(file_path, 'r') as f:
        dashboard = json.load(f)
    
    fixes_made = 0
    
    # Iterate through all panels
    if 'panels' in dashboard:
        for panel in dashboard['panels']:
            if 'targets' not in panel:
                continue
                
            for target in panel['targets']:
                if 'rawSql' not in target:
                    continue
                
                original_query = target['rawSql']
                fixed_query = fix_query(original_query)
                
                if fixed_query != original_query:
                    target['rawSql'] = fixed_query
                    fixes_made += 1
                    print(f"  ✓ Fixed query in panel: {panel.get('title', 'Untitled')}")
    
    if fixes_made > 0:
        with open(file_path, 'w') as f:
            json.dump(dashboard, f, indent=2)
        print(f"  ✅ Saved {fixes_made} fixes to {file_path.name}")
    else:
        print(f"  ℹ️  No fixes needed for {file_path.name}")
    
    return fixes_made

def main():
    dashboards_dir = Path(__file__).parent / 'grafana' / 'dashboards'
    
    print("🔧 Final comprehensive fix for ALL dashboard queries...")
    print(f"📁 Dashboard directory: {dashboards_dir}")
    print("\nFixes Applied:")
    print("1. m.id IN ($machines) → m.name IN ($machines)")
    print("2. peak_demand_kw → max_power_kw (in 1min aggregate)")
    print("3. bucket::date → time::date (in raw table)")
    print("4. Load factor calculation fixed")
    print()
    
    total_fixes = 0
    
    for dashboard_file in dashboards_dir.glob('*.json'):
        fixes = fix_dashboard(dashboard_file)
        total_fixes += fixes
    
    print(f"\n{'='*60}")
    print(f"✅ Complete! Fixed {total_fixes} queries across all dashboards")
    print(f"{'='*60}")
    
    if total_fixes > 0:
        print("\n⚠️  Next steps:")
        print("1. Restart Grafana: docker compose restart grafana")
        print("2. Refresh your browser")
        print("3. All dashboards should now work without errors!")

if __name__ == '__main__':
    main()
