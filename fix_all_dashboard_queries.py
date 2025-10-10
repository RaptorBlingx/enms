#!/usr/bin/env python3
"""
Comprehensive fix for all Grafana dashboard queries to match actual database schema.
Fixes ALL timestamp references to 'time' in queries.
"""

import json
import re
from pathlib import Path

def fix_query(query):
    """Fix a single SQL query to match the actual database schema."""
    if not query or not isinstance(query, str):
        return query
    
    original = query
    
    # Fix 1: Replace 'timestamp' with 'time' in WHERE clauses for all hypertables
    # Match patterns like: WHERE timestamp >= ..., AND timestamp ..., $__timeFilter(timestamp)
    query = re.sub(r'\btimestamp\b(?=\s*>=|\s*<=|\s*<|\s*>|\s*=|\s*\))', 'time', query)
    
    # Fix 2: Replace $__timeFilter(timestamp) with $__timeFilter(time)
    query = query.replace('$__timeFilter(timestamp)', '$__timeFilter(time)')
    
    # Fix 3: Replace ORDER BY timestamp with ORDER BY time
    query = query.replace('ORDER BY timestamp', 'ORDER BY time')
    
    # Fix 4: Fix continuous aggregate references in energy_readings queries
    query = query.replace('energy_readings_1hour', 'energy_readings_1min')
    query = query.replace('energy_readings_1day', 'energy_readings')  # Use raw table for daily
    
    # Fix 5: Remove timestamp from machine_status LATERAL subquery
    # machine_status is a status table, not a time-series table
    if 'machine_status' in query and 'SELECT current_mode, current_power_kw, timestamp' in query:
        query = query.replace('SELECT current_mode, current_power_kw, timestamp', 
                             'SELECT current_mode, current_power_kw, last_updated')
    
    # Fix 6: Fix production_data and environmental_data table references
    # These tables also use 'time' column, not 'timestamp'
    # But be careful not to replace 'timestamp' in other contexts like data types or function names
    
    # Fix 7: Fix time_bucket joins with production_data
    if 'time_bucket' in query and 'pd.timestamp' in query:
        query = query.replace('pd.timestamp', 'pd.time')
    
    # Fix 8: Check for any remaining issues with production_data and environmental_data
    # Look for patterns where these tables are referenced with timestamp column
    for table in ['production_data', 'environmental_data']:
        if table in query:
            # Replace timestamp references specific to these tables
            pattern = f'FROM {table}[\\s\\w]*WHERE[^;]+timestamp'
            if re.search(pattern, query, re.IGNORECASE):
                # More targeted replacement for these specific tables
                query = re.sub(
                    f'(FROM\\s+{table}.*?WHERE.*?)timestamp',
                    r'\1time',
                    query,
                    flags=re.IGNORECASE | re.DOTALL
                )
    
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
    
    print("🔧 Fixing all Grafana dashboard queries...")
    print(f"📁 Dashboard directory: {dashboards_dir}")
    
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
        print("2. Refresh your browser on http://10.33.10.109:8080/grafana/")
        print("3. Test the dashboards to verify all panels load correctly")

if __name__ == '__main__':
    main()
