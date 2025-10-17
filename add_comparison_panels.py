#!/usr/bin/env python3
"""
Add comparison panels to Factory Overview Grafana Dashboard
Phase 1 - Step 3: Add Top Energy Consumers and Efficiency Ranking
"""
import json
from pathlib import Path

def create_top_energy_consumers_panel():
    """Create Top 5 Energy Consumers bar chart"""
    return {
        "datasource": {
            "type": "postgres",
            "uid": "TimescaleDB"
        },
        "fieldConfig": {
            "defaults": {
                "color": {
                    "mode": "palette-classic"
                },
                "custom": {
                    "axisBorderShow": False,
                    "axisCenteredZero": False,
                    "axisColorMode": "text",
                    "axisLabel": "",
                    "axisPlacement": "auto",
                    "barAlignment": 0,
                    "drawStyle": "bars",
                    "fillOpacity": 100,
                    "gradientMode": "none",
                    "hideFrom": {
                        "legend": False,
                        "tooltip": False,
                        "viz": False
                    },
                    "insertNulls": False,
                    "lineInterpolation": "linear",
                    "lineWidth": 1,
                    "pointSize": 5,
                    "scaleDistribution": {
                        "type": "linear"
                    },
                    "showPoints": "never",
                    "spanNulls": False,
                    "stacking": {
                        "group": "A",
                        "mode": "none"
                    },
                    "thresholdsStyle": {
                        "mode": "off"
                    }
                },
                "mappings": [],
                "thresholds": {
                    "mode": "absolute",
                    "steps": [
                        {"color": "green", "value": None}
                    ]
                },
                "unit": "kwatth"
            },
            "overrides": []
        },
        "gridPos": {
            "h": 8,
            "w": 12,
            "x": 0,
            "y": 99  # Will be repositioned
        },
        "id": 200,
        "options": {
            "legend": {
                "calcs": [],
                "displayMode": "list",
                "placement": "bottom",
                "showLegend": False
            },
            "tooltip": {
                "mode": "single",
                "sort": "none"
            }
        },
        "pluginVersion": "10.0.0",
        "targets": [
            {
                "datasource": {
                    "type": "postgres",
                    "uid": "TimescaleDB"
                },
                "editorMode": "code",
                "format": "table",
                "rawQuery": True,
                "rawSql": """SELECT 
  m.name as "Machine",
  SUM(er.total_energy_kwh) as "Energy (kWh)"
FROM energy_readings_1hour er
JOIN machines m ON er.machine_id = m.id
WHERE er.bucket >= NOW() - INTERVAL '24 hours'
  AND m.is_active = true
GROUP BY m.name
ORDER BY "Energy (kWh)" DESC
LIMIT 5;""",
                "refId": "A"
            }
        ],
        "title": "Top 5 Energy Consumers (Last 24h)",
        "type": "barchart",
        "transformations": [
            {
                "id": "organize",
                "options": {
                    "excludeByName": {},
                    "indexByName": {},
                    "renameByName": {}
                }
            }
        ]
    }

def create_efficiency_ranking_table():
    """Create Efficiency Ranking table"""
    return {
        "datasource": {
            "type": "postgres",
            "uid": "TimescaleDB"
        },
        "fieldConfig": {
            "defaults": {
                "color": {
                    "mode": "thresholds"
                },
                "custom": {
                    "align": "auto",
                    "cellOptions": {
                        "type": "auto"
                    },
                    "inspect": False
                },
                "mappings": [],
                "thresholds": {
                    "mode": "absolute",
                    "steps": [
                        {"color": "green", "value": None}
                    ]
                }
            },
            "overrides": [
                {
                    "matcher": {
                        "id": "byName",
                        "options": "Rank"
                    },
                    "properties": [
                        {
                            "id": "custom.width",
                            "value": 70
                        }
                    ]
                },
                {
                    "matcher": {
                        "id": "byName",
                        "options": "SEC"
                    },
                    "properties": [
                        {
                            "id": "unit",
                            "value": "none"
                        },
                        {
                            "id": "decimals",
                            "value": 5
                        },
                        {
                            "id": "custom.cellOptions",
                            "value": {
                                "type": "color-background"
                            }
                        },
                        {
                            "id": "thresholds",
                            "value": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "green", "value": None},
                                    {"color": "yellow", "value": 0.05},
                                    {"color": "red", "value": 0.1}
                                ]
                            }
                        }
                    ]
                },
                {
                    "matcher": {
                        "id": "byName",
                        "options": "Load Factor (%)"
                    },
                    "properties": [
                        {
                            "id": "unit",
                            "value": "percent"
                        },
                        {
                            "id": "decimals",
                            "value": 1
                        },
                        {
                            "id": "custom.cellOptions",
                            "value": {
                                "type": "color-background"
                            }
                        },
                        {
                            "id": "thresholds",
                            "value": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "red", "value": None},
                                    {"color": "yellow", "value": 50},
                                    {"color": "green", "value": 70}
                                ]
                            }
                        }
                    ]
                },
                {
                    "matcher": {
                        "id": "byName",
                        "options": "Energy (kWh)"
                    },
                    "properties": [
                        {
                            "id": "unit",
                            "value": "kwatth"
                        },
                        {
                            "id": "decimals",
                            "value": 1
                        }
                    ]
                }
            ]
        },
        "gridPos": {
            "h": 8,
            "w": 12,
            "x": 12,
            "y": 99  # Will be repositioned
        },
        "id": 201,
        "options": {
            "cellHeight": "sm",
            "footer": {
                "countRows": False,
                "fields": "",
                "reducer": ["sum"],
                "show": False
            },
            "showHeader": True
        },
        "pluginVersion": "10.0.0",
        "targets": [
            {
                "datasource": {
                    "type": "postgres",
                    "uid": "TimescaleDB"
                },
                "editorMode": "code",
                "format": "table",
                "rawQuery": True,
                "rawSql": """SELECT 
  ROW_NUMBER() OVER (
    ORDER BY 
      COALESCE(SUM(er.total_energy_kwh) / NULLIF(SUM(pd.production_count), 0), 999) ASC
  ) as "Rank",
  m.name as "Machine",
  COALESCE(
    SUM(er.total_energy_kwh) / NULLIF(SUM(pd.production_count), 0),
    0
  ) as "SEC",
  COALESCE(
    AVG(er.avg_power_kw) / NULLIF(MAX(er.max_power_kw), 0) * 100,
    0
  ) as "Load Factor (%)",
  SUM(er.total_energy_kwh) as "Energy (kWh)"
FROM energy_readings_1hour er
JOIN machines m ON er.machine_id = m.id
LEFT JOIN production_data_1hour pd 
  ON er.bucket = pd.bucket AND er.machine_id = pd.machine_id
WHERE er.bucket >= NOW() - INTERVAL '24 hours'
  AND m.is_active = true
GROUP BY m.name
ORDER BY "Rank" ASC;""",
                "refId": "A"
            }
        ],
        "title": "Machine Efficiency Ranking (Last 24h)",
        "type": "table"
    }

def main():
    dashboard_path = Path('/home/ubuntu/enms/grafana/dashboards/enms-factory-overview.json')
    
    print("📊 Adding Comparison Panels to Factory Overview Dashboard")
    print("=" * 70)
    
    # Read dashboard
    with open(dashboard_path, 'r') as f:
        dashboard = json.load(f)
    
    print(f"✓ Loaded dashboard: {dashboard['title']}")
    print(f"  Current panels: {len(dashboard['panels'])}")
    
    # Find the maximum y position to append new panels
    max_y = 0
    for panel in dashboard['panels']:
        if 'gridPos' in panel:
            panel_bottom = panel['gridPos']['y'] + panel['gridPos']['h']
            if panel_bottom > max_y:
                max_y = panel_bottom
    
    print(f"✓ Max Y position found: {max_y}")
    
    # Create new panels
    top_consumers = create_top_energy_consumers_panel()
    efficiency_ranking = create_efficiency_ranking_table()
    
    # Position them at the bottom
    top_consumers['gridPos']['y'] = max_y
    efficiency_ranking['gridPos']['y'] = max_y
    
    # Add to dashboard
    dashboard['panels'].append(top_consumers)
    dashboard['panels'].append(efficiency_ranking)
    
    print(f"✓ Added 2 new panels")
    print(f"  Total panels now: {len(dashboard['panels'])}")
    
    # Write back
    with open(dashboard_path, 'w') as f:
        json.dump(dashboard, f, indent=2)
    
    print(f"✓ Saved updated dashboard")
    print()
    print("New panels added:")
    print(f"  1. Top 5 Energy Consumers (Last 24h) - Bar Chart - y:{max_y}")
    print(f"  2. Machine Efficiency Ranking (Last 24h) - Table - y:{max_y}")
    print()
    print("✅ Phase 1, Step 3 Complete!")
    print("   Next: Restart Grafana to see the changes")

if __name__ == '__main__':
    main()
