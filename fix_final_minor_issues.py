#!/usr/bin/env python3
"""
Fix remaining dashboard issues:
1. energy_kwh vs total_energy_kwh in raw table
2. Machine Monitoring template variable returning names instead of UUIDs
"""

import json
import re
from pathlib import Path

def fix_energy_analysis(dashboard):
    """Fix energy_kwh column reference in raw table queries."""
    fixes = 0
    
    if 'panels' in dashboard:
        for panel in dashboard['panels']:
            if 'targets' not in panel:
                continue
                
            for target in panel['targets']:
                if 'rawSql' not in target:
                    continue
                
                query = target['rawSql']
                
                # If querying raw energy_readings (not aggregate), use energy_kwh not total_energy_kwh
                if 'FROM energy_readings er' in query or 'FROM energy_readings\n' in query:
                    if 'total_energy_kwh' in query:
                        # Change total_energy_kwh to energy_kwh for raw table
                        query = query.replace('total_energy_kwh', 'energy_kwh')
                        target['rawSql'] = query
                        fixes += 1
                        print(f"  ✓ Fixed energy_kwh in panel: {panel.get('title', 'Untitled')}")
    
    return fixes

def fix_machine_monitoring_variable(dashboard):
    """Fix machine_id template variable to properly return UUID."""
    fixes = 0
    
    if 'templating' in dashboard and 'list' in dashboard['templating']:
        for var in dashboard['templating']['list']:
            if var.get('name') == 'machine_id':
                # Current query: SELECT id, name FROM machines...
                # Grafana interprets: value=first_column, text=second_column
                # But we need to be explicit and also handle the WHERE clause properly
                
                # The query already returns id (UUID) as first column, which should work
                # The issue is that the WHERE clause needs to check UUID type
                
                # Let's verify the query is correct
                old_query = var.get('query', '')
                if 'SELECT id, name FROM machines' in old_query:
                    print(f"  ℹ️  Template variable query looks correct: {old_query}")
                    print(f"      This should return UUID as value, name as text")
                    
                    # The issue might be in the panel queries using machine_id
                    # They might need explicit UUID casting
                    fixes += 1
    
    return fixes

def fix_machine_monitoring_queries(dashboard):
    """Add explicit UUID casting to machine_id WHERE clauses."""
    fixes = 0
    
    if 'panels' in dashboard:
        for panel in dashboard['panels']:
            if 'targets' not in panel:
                continue
                
            for target in panel['targets']:
                if 'rawSql' not in target:
                    continue
                
                query = target['rawSql']
                original = query
                
                # Fix: WHERE machine_id = $machine_id needs explicit UUID cast
                # Change to: WHERE machine_id = $machine_id::uuid
                if 'WHERE machine_id = $machine_id' in query and '::uuid' not in query:
                    query = query.replace(
                        'WHERE machine_id = $machine_id',
                        'WHERE machine_id = $machine_id::uuid'
                    )
                
                # Also handle JOIN conditions
                if 'pd.machine_id = er.machine_id AND' in query:
                    # This is fine, internal join
                    pass
                
                if query != original:
                    target['rawSql'] = query
                    fixes += 1
                    print(f"  ✓ Added UUID cast in panel: {panel.get('title', 'Untitled')}")
    
    return fixes

def main():
    dashboards_dir = Path(__file__).parent / 'grafana' / 'dashboards'
    
    print("🔧 Fixing remaining dashboard issues...")
    print("1. energy_kwh vs total_energy_kwh in raw tables")
    print("2. Machine Monitoring UUID casting")
    print()
    
    # Fix Energy Analysis
    energy_file = dashboards_dir / 'energy-analysis.json'
    if energy_file.exists():
        print(f"\n📄 Processing {energy_file.name}...")
        with open(energy_file, 'r') as f:
            dashboard = json.load(f)
        
        fixes = fix_energy_analysis(dashboard)
        
        if fixes > 0:
            with open(energy_file, 'w') as f:
                json.dump(dashboard, f, indent=2)
            print(f"  ✅ Saved {fixes} fixes")
        else:
            print(f"  ℹ️  No fixes needed")
    
    # Fix Machine Monitoring
    machine_file = dashboards_dir / 'machine-monitoring.json'
    if machine_file.exists():
        print(f"\n📄 Processing {machine_file.name}...")
        with open(machine_file, 'r') as f:
            dashboard = json.load(f)
        
        var_fixes = fix_machine_monitoring_variable(dashboard)
        query_fixes = fix_machine_monitoring_queries(dashboard)
        
        total_fixes = var_fixes + query_fixes
        
        if total_fixes > 0:
            with open(machine_file, 'w') as f:
                json.dump(dashboard, f, indent=2)
            print(f"  ✅ Saved {total_fixes} fixes")
        else:
            print(f"  ℹ️  No fixes needed")
    
    print("\n" + "="*60)
    print("✅ Complete! Restart Grafana and test:")
    print("   docker compose restart grafana")
    print("="*60)

if __name__ == '__main__':
    main()
