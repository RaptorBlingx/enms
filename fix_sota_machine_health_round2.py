#!/usr/bin/env python3
"""Fix remaining issues in SOTA Machine Health dashboard."""

import json

def fix_dashboard(filepath):
    """Fix remaining query issues."""
    with open(filepath, 'r') as f:
        dashboard = json.load(f)
    
    changes_made = []
    
    for panel in dashboard.get('panels', []):
        if 'targets' not in panel:
            continue
            
        for target in panel['targets']:
            if 'rawSql' not in target:
                continue
                
            sql = target['rawSql']
            original_sql = sql
            
            # Fix 1: Remove "description" column from anomalies table (doesn't exist)
            # Replace with anomaly_type and metric_name which provide context
            if 'description as "Description"' in sql:
                sql = sql.replace(
                    '  CASE WHEN is_resolved = false THEN \'Active\' ELSE \'Resolved\' END as "Status",\n  description as "Description"',
                    '  CASE WHEN is_resolved = false THEN \'Active\' ELSE \'Resolved\' END as "Status",\n  detection_method as "Detection Method"'
                )
                changes_made.append(f"Panel {panel.get('id')} ({panel.get('title')}): Removed non-existent 'description' column, added 'detection_method'")
            
            # Fix 2: Fix INTERVAL issue in Actual vs Baseline Power
            # The problem is $__timeFrom() returns a timestamp, not an interval
            # Need to use date arithmetic instead
            if 'Baseline (MA-24h)' in sql and '$__timeFrom() - INTERVAL' in sql:
                sql = """SELECT 
  er.bucket as time,
  'Actual' as metric,
  AVG(er.avg_power_kw) as value
FROM energy_readings_1hour er
WHERE er.machine_id = '$machine_id'::uuid
  AND er.bucket >= $__timeFrom() AND er.bucket <= $__timeTo()
GROUP BY er.bucket

UNION ALL

SELECT 
  er.bucket as time,
  'Baseline (MA-24h)' as metric,
  AVG(er.avg_power_kw) OVER (ORDER BY er.bucket ROWS BETWEEN 24 PRECEDING AND CURRENT ROW) as value
FROM energy_readings_1hour er
WHERE er.machine_id = '$machine_id'::uuid
  AND er.bucket >= ($__timeFrom()::timestamptz - INTERVAL '24 hours')
  AND er.bucket <= $__timeTo()

ORDER BY time;"""
                changes_made.append(f"Panel {panel.get('id')} ({panel.get('title')}): Fixed interval syntax - cast $__timeFrom() to timestamptz before subtracting")
            
            # Update if changes were made
            if sql != original_sql:
                target['rawSql'] = sql
    
    # Save fixed dashboard
    with open(filepath, 'w') as f:
        json.dump(dashboard, f, indent=2)
    
    return changes_made

if __name__ == '__main__':
    filepath = '/home/ubuntu/enms/grafana/dashboards/SOTA-machine-health.json'
    changes = fix_dashboard(filepath)
    
    print(f"Fixed {len(changes)} issues:")
    for change in changes:
        print(f"  - {change}")
    
    print(f"\nDashboard saved to: {filepath}")
    print("\nNote: 'No data' in ML Model Performance is EXPECTED for machines without")
    print("      trained models. Only Compressor-1 has model metrics currently.")
    print("      The panel will show data when you select Compressor-1 in the dropdown.")
