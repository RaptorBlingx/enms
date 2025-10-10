#!/usr/bin/env python3
"""
Fix production_data and environmental_data column references in Grafana dashboards.
Maps dashboard column names to actual database schema.
"""

import json
import re
from pathlib import Path

def fix_production_columns(query):
    """Fix production_data column references."""
    if 'production_data' not in query:
        return query
    
    # Map: units_produced -> production_count
    query = query.replace('units_produced', 'production_count')
    
    # Map: defect_count -> production_count_bad
    query = query.replace('defect_count', 'production_count_bad')
    
    return query

def fix_environmental_columns(query):
    """Fix environmental_data column references."""
    if 'environmental_data' not in query:
        return query
    
    # Map: temperature_c -> machine_temp_c (most relevant for machine monitoring)
    query = query.replace('temperature_c', 'machine_temp_c')
    
    # Map: humidity_percent -> indoor_humidity_percent
    query = query.replace('humidity_percent', 'indoor_humidity_percent')
    
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
                fixed_query = original_query
                
                # Apply fixes
                fixed_query = fix_production_columns(fixed_query)
                fixed_query = fix_environmental_columns(fixed_query)
                
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
    
    print("🔧 Fixing production_data and environmental_data column names...")
    print(f"📁 Dashboard directory: {dashboards_dir}")
    
    total_fixes = 0
    
    for dashboard_file in dashboards_dir.glob('*.json'):
        fixes = fix_dashboard(dashboard_file)
        total_fixes += fixes
    
    print(f"\n{'='*60}")
    print(f"✅ Complete! Fixed {total_fixes} column references")
    print(f"{'='*60}")
    
    if total_fixes > 0:
        print("\n⚠️  Next steps:")
        print("1. Restart Grafana: docker compose restart grafana")
        print("2. Refresh your browser")
        print("3. Test the Machine Monitoring dashboard with production/environmental data")

if __name__ == '__main__':
    main()
