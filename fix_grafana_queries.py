#!/usr/bin/env python3
"""
Fix Grafana dashboard queries to match actual database schema
"""
import json
import re
from pathlib import Path

def fix_query(query):
    """Fix common query issues"""
    if not query:
        return query
    
    # Fix 1: Replace timestamp with time for energy_readings, production_data, environmental_data
    query = re.sub(r'\btimestamp\b(?=.*\bFROM\s+energy_readings\b)', 'time', query, flags=re.IGNORECASE | re.DOTALL)
    query = re.sub(r'\btimestamp\b(?=.*\bFROM\s+production_data\b)', 'time', query, flags=re.IGNORECASE | re.DOTALL)
    query = re.sub(r'\btimestamp\b(?=.*\bFROM\s+environmental_data\b)', 'time', query, flags=re.IGNORECASE | re.DOTALL)
    
    # Fix 2: Replace energy_readings_1hour with energy_readings_1min
    query = query.replace('energy_readings_1hour', 'energy_readings_1min')
    
    # Fix 3: Replace energy_readings_1day with time_bucket on energy_readings
    if 'energy_readings_1day' in query:
        # Replace the FROM clause and bucket reference
        query = query.replace('energy_readings_1day', 'energy_readings')
        query = query.replace('bucket >=', 'time >=')
        query = query.replace('WHERE machine_id', 'WHERE time >= DATE_TRUNC(\'day\', NOW()) AND machine_id')
    
    # Fix 4: Remove timestamp references in machine_status queries
    # machine_status doesn't have timestamp column, it has last_updated
    if 'machine_status' in query and 'timestamp' in query.lower():
        # Remove ORDER BY timestamp DESC from machine_status queries
        query = re.sub(r'ORDER BY\s+timestamp\s+DESC', '', query, flags=re.IGNORECASE)
        # Remove WHERE timestamp clauses from machine_status
        query = re.sub(r'WHERE\s+ms\.timestamp\s+>=.*?;', 'WHERE 1=1;', query, flags=re.IGNORECASE)
        query = re.sub(r'ms\.timestamp', 'ms.last_updated', query, flags=re.IGNORECASE)
    
    # Fix 5: For machine_status single value queries, just query the table directly (no ORDER BY needed)
    if re.search(r'SELECT\s+current_(mode|power_kw)\s+FROM\s+machine_status\s+WHERE\s+machine_id', query, re.IGNORECASE):
        # Remove any ORDER BY and LIMIT since machine_status only has one row per machine
        query = re.sub(r'ORDER BY.*?LIMIT.*?;', ';', query, flags=re.IGNORECASE | re.DOTALL)
        query = re.sub(r'ORDER BY.*?$', '', query, flags=re.IGNORECASE)
    
    return query

def fix_dashboard(filepath):
    """Fix all queries in a dashboard JSON file"""
    print(f"Fixing {filepath.name}...")
    
    with open(filepath, 'r') as f:
        dashboard = json.load(f)
    
    changes_made = 0
    
    # Recursively find all rawSql fields
    def fix_panel(obj):
        nonlocal changes_made
        if isinstance(obj, dict):
            if 'rawSql' in obj:
                old_query = obj['rawSql']
                new_query = fix_query(old_query)
                if old_query != new_query:
                    obj['rawSql'] = new_query
                    changes_made += 1
            for value in obj.values():
                fix_panel(value)
        elif isinstance(obj, list):
            for item in obj:
                fix_panel(item)
    
    fix_panel(dashboard)
    
    if changes_made > 0:
        with open(filepath, 'w') as f:
            json.dump(dashboard, f, indent=2)
        print(f"  ✅ Fixed {changes_made} queries in {filepath.name}")
    else:
        print(f"  ℹ️  No changes needed in {filepath.name}")
    
    return changes_made

def main():
    dashboards_dir = Path('/home/ubuntu/enms/grafana/dashboards')
    total_changes = 0
    
    print("=" * 60)
    print("Fixing Grafana Dashboard Queries")
    print("=" * 60)
    
    for dashboard_file in dashboards_dir.glob('*.json'):
        changes = fix_dashboard(dashboard_file)
        total_changes += changes
    
    print("=" * 60)
    print(f"✅ Total queries fixed: {total_changes}")
    print("=" * 60)

if __name__ == '__main__':
    main()
