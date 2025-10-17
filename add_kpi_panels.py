#!/usr/bin/env python3
"""
Add KPI stat panels to Energy Analysis Grafana Dashboard
Phase 1 - Step 2: Add SEC, Energy Cost, and Carbon Emissions panels
"""
import json
from pathlib import Path

def create_sec_panel():
    """Create SEC (Specific Energy Consumption) stat panel"""
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
                "mappings": [],
                "thresholds": {
                    "mode": "absolute",
                    "steps": [
                        {"color": "green", "value": None},
                        {"color": "yellow", "value": 0.05},
                        {"color": "red", "value": 0.1}
                    ]
                },
                "unit": "none",
                "decimals": 5
            },
            "overrides": []
        },
        "gridPos": {
            "h": 4,
            "w": 6,
            "x": 0,
            "y": 0
        },
        "id": 100,  # New unique ID
        "options": {
            "colorMode": "value",
            "graphMode": "area",
            "justifyMode": "auto",
            "orientation": "auto",
            "reduceOptions": {
                "calcs": ["lastNotNull"],
                "fields": "",
                "values": False
            },
            "textMode": "auto",
            "text": {}
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
  COALESCE(
    SUM(er.total_energy_kwh) / NULLIF(SUM(pd.production_count), 0),
    0
  ) as "SEC (kWh/unit)"
FROM energy_readings_1hour er
LEFT JOIN production_data_1hour pd 
  ON er.bucket = pd.bucket AND er.machine_id = pd.machine_id
WHERE er.bucket >= $__timeFrom() 
  AND er.bucket <= $__timeTo()
  AND er.machine_id::text IN (${machines:singlequote})""",
                "refId": "A"
            }
        ],
        "title": "SEC (Specific Energy Consumption)",
        "type": "stat"
    }

def create_energy_cost_panel():
    """Create Energy Cost stat panel"""
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
                "mappings": [],
                "thresholds": {
                    "mode": "absolute",
                    "steps": [
                        {"color": "green", "value": None},
                        {"color": "yellow", "value": 100},
                        {"color": "orange", "value": 500},
                        {"color": "red", "value": 1000}
                    ]
                },
                "unit": "currencyUSD",
                "decimals": 2
            },
            "overrides": []
        },
        "gridPos": {
            "h": 4,
            "w": 6,
            "x": 6,
            "y": 0
        },
        "id": 101,
        "options": {
            "colorMode": "value",
            "graphMode": "area",
            "justifyMode": "auto",
            "orientation": "auto",
            "reduceOptions": {
                "calcs": ["lastNotNull"],
                "fields": "",
                "values": False
            },
            "textMode": "auto"
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
  COALESCE(SUM(total_energy_kwh) * $cost_per_kwh, 0) as "Energy Cost (USD)"
FROM energy_readings_1hour
WHERE bucket >= $__timeFrom() 
  AND bucket <= $__timeTo()
  AND machine_id::text IN (${machines:singlequote})""",
                "refId": "A"
            }
        ],
        "title": "Energy Cost",
        "type": "stat"
    }

def create_carbon_panel():
    """Create Carbon Emissions stat panel"""
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
                "mappings": [],
                "thresholds": {
                    "mode": "absolute",
                    "steps": [
                        {"color": "green", "value": None},
                        {"color": "yellow", "value": 500},
                        {"color": "orange", "value": 1000},
                        {"color": "red", "value": 2000}
                    ]
                },
                "unit": "kg",
                "decimals": 1
            },
            "overrides": []
        },
        "gridPos": {
            "h": 4,
            "w": 6,
            "x": 12,
            "y": 0
        },
        "id": 102,
        "options": {
            "colorMode": "value",
            "graphMode": "area",
            "justifyMode": "auto",
            "orientation": "auto",
            "reduceOptions": {
                "calcs": ["lastNotNull"],
                "fields": "",
                "values": False
            },
            "textMode": "auto"
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
  COALESCE(SUM(total_energy_kwh) * $carbon_factor, 0) as "Carbon Emissions (kg CO2)"
FROM energy_readings_1hour
WHERE bucket >= $__timeFrom() 
  AND bucket <= $__timeTo()
  AND machine_id::text IN (${machines:singlequote})""",
                "refId": "A"
            }
        ],
        "title": "Carbon Emissions (CO₂)",
        "type": "stat"
    }

def create_total_energy_panel():
    """Create Total Energy stat panel"""
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
                "mappings": [],
                "thresholds": {
                    "mode": "absolute",
                    "steps": [
                        {"color": "blue", "value": None}
                    ]
                },
                "unit": "kwatth",
                "decimals": 1
            },
            "overrides": []
        },
        "gridPos": {
            "h": 4,
            "w": 6,
            "x": 18,
            "y": 0
        },
        "id": 103,
        "options": {
            "colorMode": "value",
            "graphMode": "area",
            "justifyMode": "auto",
            "orientation": "auto",
            "reduceOptions": {
                "calcs": ["lastNotNull"],
                "fields": "",
                "values": False
            },
            "textMode": "auto"
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
  COALESCE(SUM(total_energy_kwh), 0) as "Total Energy (kWh)"
FROM energy_readings_1hour
WHERE bucket >= $__timeFrom() 
  AND bucket <= $__timeTo()
  AND machine_id::text IN (${machines:singlequote})""",
                "refId": "A"
            }
        ],
        "title": "Total Energy Consumption",
        "type": "stat"
    }

def shift_panels_down(panels, y_offset=4):
    """Shift all existing panels down by y_offset"""
    for panel in panels:
        if 'gridPos' in panel:
            panel['gridPos']['y'] += y_offset
    return panels

def main():
    dashboard_path = Path('/home/ubuntu/enms/grafana/dashboards/enms-energy-analysis.json')
    
    print("📊 Adding KPI Stat Panels to Energy Analysis Dashboard")
    print("=" * 70)
    
    # Read dashboard
    with open(dashboard_path, 'r') as f:
        dashboard = json.load(f)
    
    print(f"✓ Loaded dashboard: {dashboard['title']}")
    print(f"  Current panels: {len(dashboard['panels'])}")
    
    # Shift existing panels down
    dashboard['panels'] = shift_panels_down(dashboard['panels'], y_offset=4)
    print(f"✓ Shifted existing panels down by 4 units")
    
    # Create new KPI panels
    new_panels = [
        create_sec_panel(),
        create_energy_cost_panel(),
        create_carbon_panel(),
        create_total_energy_panel()
    ]
    
    # Insert new panels at the beginning
    dashboard['panels'] = new_panels + dashboard['panels']
    print(f"✓ Added 4 new KPI stat panels at the top")
    print(f"  Total panels now: {len(dashboard['panels'])}")
    
    # Write back
    with open(dashboard_path, 'w') as f:
        json.dump(dashboard, f, indent=2)
    
    print(f"✓ Saved updated dashboard")
    print()
    print("New panels added:")
    print("  1. SEC (Specific Energy Consumption) - x:0, y:0")
    print("  2. Energy Cost - x:6, y:0")
    print("  3. Carbon Emissions (CO₂) - x:12, y:0")
    print("  4. Total Energy Consumption - x:18, y:0")
    print()
    print("✅ Phase 1, Step 2 Complete!")
    print("   Next: Restart Grafana to see the changes")

if __name__ == '__main__':
    main()
