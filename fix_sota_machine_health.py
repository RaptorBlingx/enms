#!/usr/bin/env python3
"""Fix SOTA Machine Health dashboard queries."""

import json
import sys

def fix_dashboard(filepath):
    """Fix all query issues in SOTA Machine Health dashboard."""
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
            
            # Fix 1: resolved_at IS NULL → is_resolved = false
            if 'resolved_at IS NULL' in sql:
                sql = sql.replace('resolved_at IS NULL', 'is_resolved = false')
                changes_made.append(f"Panel {panel.get('id')}: Fixed resolved_at IS NULL")
            
            # Fix 2: eb.expected_power → 50 (fixed baseline value since table doesn't have this column)
            # Remove baseline join entirely for health score and variance
            if 'eb.expected_power' in sql:
                # For health score panel - simplify to use standard deviation
                if 'Health Score' in sql:
                    sql = """SELECT 
  ROUND(
    CASE 
      WHEN COUNT(*) FILTER (WHERE a.is_resolved = false) = 0 THEN 95
      WHEN COUNT(*) FILTER (WHERE a.is_resolved = false) <= 2 THEN 85
      WHEN COUNT(*) FILTER (WHERE a.is_resolved = false) <= 5 THEN 70
      ELSE 50
    END
  ) as "Health Score"
FROM anomalies a
WHERE a.machine_id = '$machine_id'::uuid;
"""
                # For baseline variance panel - use coefficient of variation
                elif 'Baseline Variance' in sql:
                    sql = """SELECT 
  COALESCE(
    ROUND(
      (STDDEV(avg_power_kw) / NULLIF(AVG(avg_power_kw), 0) * 100)::numeric,
      2
    ),
    0
  ) as "Baseline Variance"
FROM energy_readings_1hour
WHERE machine_id = '$machine_id'::uuid
  AND bucket >= NOW() - INTERVAL '24 hours';"""
                # For actual vs baseline chart - use moving average as baseline
                elif 'Actual vs Baseline' in panel.get('title', '') or "'Baseline' as metric" in sql:
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
  AND er.bucket >= $__timeFrom() - INTERVAL '24 hours' AND er.bucket <= $__timeTo()

ORDER BY time;"""
                
                changes_made.append(f"Panel {panel.get('id')} ({panel.get('title')}): Removed eb.expected_power")
            
            # Fix 3: r2_score → r_squared, add evaluated_at → evaluation_date
            if 'r2_score' in sql:
                sql = sql.replace('r2_score', 'r_squared')
                changes_made.append(f"Panel {panel.get('id')}: Fixed r2_score → r_squared")
            
            if 'evaluated_at' in sql:
                sql = sql.replace('evaluated_at', 'evaluation_date')
                changes_made.append(f"Panel {panel.get('id')}: Fixed evaluated_at → evaluation_date")
            
            # Fix 4: power_kw → metric_value in anomalies table
            if 'power_kw' in sql and 'anomalies' in sql:
                sql = sql.replace('ROUND(power_kw::numeric, 2)', 'ROUND(metric_value::numeric, 2)')
                sql = sql.replace('power_kw', 'metric_value')
                changes_made.append(f"Panel {panel.get('id')}: Fixed power_kw → metric_value")
            
            # Only update if changes were made
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
