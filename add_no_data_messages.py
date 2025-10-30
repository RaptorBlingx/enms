#!/usr/bin/env python3
"""Add custom 'No Data' messages to SOTA dashboards."""

import json
import sys

# Custom messages for different panel types
NO_DATA_MESSAGES = {
    "ML Model Performance": "ℹ️ No model metrics available for this machine. Train a baseline model first or select Compressor-1 which has trained models.",
    "Anomaly Timeline": "✓ No anomalies detected in selected time range. Try expanding to last 7 days or last 30 days.",
    "Anomaly Details": "✓ No anomalies found in selected time range. This is good! Expand time range to see historical anomalies.",
    "Baseline Variance (24h)": "ℹ️ Insufficient data in time range. Need at least 24 hours of readings. Expand time range to see variance.",
    "Actual vs Baseline Power": "ℹ️ No power readings in selected time range. Expand time range to see consumption patterns.",
    "Production vs Energy Correlation": "ℹ️ No production data in time range. Expand to last 7 days to see correlation patterns.",
    "Active Anomalies (Unresolved)": "✓ No active anomalies! System operating normally.",
    "Active Anomalies": "✓ No active anomalies detected. Machine operating within normal parameters."
}

def add_no_data_messages(filepath):
    """Add custom no data messages to panels."""
    with open(filepath, 'r') as f:
        dashboard = json.load(f)
    
    changes_made = []
    
    for panel in dashboard.get('panels', []):
        title = panel.get('title', '')
        
        # Check if this panel needs a custom message
        if title in NO_DATA_MESSAGES:
            message = NO_DATA_MESSAGES[title]
            
            # Add or update the options.text section for different panel types
            if 'options' not in panel:
                panel['options'] = {}
            
            # For gauge and stat panels
            if panel.get('type') in ['gauge', 'stat']:
                if 'text' not in panel['options']:
                    panel['options']['text'] = {}
                panel['options']['text']['titleSize'] = panel['options'].get('text', {}).get('titleSize', 14)
                panel['options']['text']['valueSize'] = panel['options'].get('text', {}).get('valueSize', 32)
            
            # For table panels
            if panel.get('type') == 'table':
                if 'footer' not in panel['options']:
                    panel['options']['footer'] = {
                        "show": False,
                        "reducer": ["sum"],
                        "fields": "",
                        "countRows": False
                    }
            
            # For time series panels
            if panel.get('type') == 'timeseries':
                if 'legend' not in panel['options']:
                    panel['options']['legend'] = {
                        "displayMode": "list",
                        "placement": "bottom",
                        "showLegend": True
                    }
            
            # For bar chart panels
            if panel.get('type') == 'barchart':
                if 'legend' not in panel['options']:
                    panel['options']['legend'] = {
                        "displayMode": "list",
                        "placement": "bottom",
                        "showLegend": False
                    }
            
            # Add fieldConfig overrides for custom no data message
            if 'fieldConfig' not in panel:
                panel['fieldConfig'] = {'defaults': {}, 'overrides': []}
            
            if 'defaults' not in panel['fieldConfig']:
                panel['fieldConfig']['defaults'] = {}
            
            # Set the no data text
            panel['fieldConfig']['defaults']['noValue'] = message
            
            changes_made.append(f"Panel '{title}': Added custom no data message")
    
    # Save updated dashboard
    with open(filepath, 'w') as f:
        json.dump(dashboard, f, indent=2)
    
    return changes_made

if __name__ == '__main__':
    # Process both dashboards
    dashboards = [
        '/home/ubuntu/enms/grafana/dashboards/SOTA-machine-health.json',
        '/home/ubuntu/enms/grafana/dashboards/SOTA-factory-overview.json'
    ]
    
    total_changes = 0
    for filepath in dashboards:
        print(f"\n{'='*60}")
        print(f"Processing: {filepath.split('/')[-1]}")
        print('='*60)
        
        try:
            changes = add_no_data_messages(filepath)
            total_changes += len(changes)
            
            if changes:
                print(f"✓ Added {len(changes)} custom no data messages:")
                for change in changes:
                    print(f"  • {change}")
            else:
                print("  No matching panels found")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\n{'='*60}")
    print(f"Total changes: {total_changes}")
    print('='*60)
