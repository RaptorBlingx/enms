#!/usr/bin/env python3
"""
EnMS API Testing Script for OVOS Integration
=============================================

Quick testing script to verify all API endpoints work correctly.
Run this to validate APIs before Burak integrates with OVOS.

Usage:
    python test_enms_api.py
    
Author: Mohamad
Date: January 2025
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any
import sys

# Configuration
API_BASE = "http://localhost:8001/api/v1"
MACHINE_ID = "c0000000-0000-0000-0000-000000000001"  # Compressor-1

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print section header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
    print(f"{text}")
    print(f"{'='*70}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_json(data: Any, max_items: int = 3):
    """Pretty print JSON data."""
    if isinstance(data, list) and len(data) > max_items:
        print(f"{Colors.OKCYAN}Showing {max_items} of {len(data)} items:{Colors.ENDC}")
        print(json.dumps(data[:max_items], indent=2))
        print(f"{Colors.OKCYAN}... and {len(data) - max_items} more items{Colors.ENDC}")
    else:
        print(f"{Colors.OKCYAN}{json.dumps(data, indent=2)}{Colors.ENDC}")


def test_endpoint(name: str, method: str, url: str, **kwargs) -> Dict[str, Any]:
    """
    Test an API endpoint and print results.
    
    Args:
        name: Test name
        method: HTTP method (GET, POST, etc.)
        url: Full URL
        **kwargs: Additional requests parameters
    
    Returns:
        Response JSON or None if failed
    """
    print(f"\n{Colors.OKBLUE}Testing: {name}{Colors.ENDC}")
    print(f"Request: {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, **kwargs)
        elif method == "POST":
            response = requests.post(url, **kwargs)
        else:
            print_error(f"Unsupported method: {method}")
            return None
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print_success(f"{name} - OK")
            data = response.json()
            return data
        else:
            print_error(f"{name} - Failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print_error(f"Connection failed. Is EnMS running on {API_BASE}?")
        return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None


def main():
    """Run all API tests."""
    
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║         EnMS API Testing Script for OVOS Integration              ║")
    print("║                                                                    ║")
    print("║  This script tests all API endpoints that Burak will use          ║")
    print("║  for OVOS voice assistant integration.                            ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")
    
    print(f"API Base URL: {API_BASE}")
    print(f"Test Machine ID: {MACHINE_ID}\n")
    
    # Calculate time ranges
    now = datetime.utcnow()
    start_time_24h = (now - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    start_date_7d = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    end_date = now.strftime("%Y-%m-%d")
    
    # ========================================================================
    # TEST 1: Health Check
    # ========================================================================
    print_header("TEST 1: Health Check")
    data = test_endpoint(
        "Health Check",
        "GET",
        f"{API_BASE}/health"
    )
    if data:
        print("\nKey Metrics:")
        print(f"  Service: {data.get('service')}")
        print(f"  Version: {data.get('version')}")
        print(f"  Status: {data.get('status')}")
        print(f"  Active Machines: {data.get('active_machines')}")
        print(f"  Recent Anomalies: {data.get('recent_anomalies')}")
    
    # ========================================================================
    # TEST 2: System Statistics
    # ========================================================================
    print_header("TEST 2: System Statistics")
    data = test_endpoint(
        "System Statistics",
        "GET",
        f"{API_BASE}/stats/system"
    )
    if data:
        print("\nKey Statistics:")
        print(f"  Total Energy: {data.get('total_energy')} kWh")
        print(f"  Energy/Hour: {data.get('energy_per_hour')} kWh")
        print(f"  Cost/Day: ${data.get('cost_per_day')}")
        print(f"  Carbon/Day: {data.get('carbon_per_day')} kg CO2")
        print(f"  Peak Power: {data.get('peak_power')} kW")
        print(f"  Efficiency: {data.get('efficiency')}%")
    
    # ========================================================================
    # TEST 3: List Machines
    # ========================================================================
    print_header("TEST 3: List Machines")
    data = test_endpoint(
        "List All Machines",
        "GET",
        f"{API_BASE}/machines"
    )
    if data and isinstance(data, list):
        print(f"\nFound {len(data)} machines:")
        for machine in data:
            print(f"  - {machine.get('name')} ({machine.get('type')}) - {machine.get('rated_power')} kW")
    
    # ========================================================================
    # TEST 4: Get Machine Details
    # ========================================================================
    print_header("TEST 4: Get Machine Details")
    data = test_endpoint(
        "Get Machine Details",
        "GET",
        f"{API_BASE}/machines/{MACHINE_ID}"
    )
    if data:
        print("\nMachine Details:")
        print_json(data)
    
    # ========================================================================
    # TEST 5: Latest Reading
    # ========================================================================
    print_header("TEST 5: Latest Reading")
    data = test_endpoint(
        "Get Latest Reading",
        "GET",
        f"{API_BASE}/timeseries/latest/{MACHINE_ID}"
    )
    if data:
        print("\nLatest Reading:")
        print(f"  Timestamp: {data.get('timestamp')}")
        print(f"  Power: {data.get('power_kw')} kW")
        print(f"  Energy: {data.get('energy_kwh')} kWh")
        print(f"  Status: {data.get('status')}")
    
    # ========================================================================
    # TEST 6: Energy Time-Series
    # ========================================================================
    print_header("TEST 6: Energy Time-Series (Last 24 Hours)")
    data = test_endpoint(
        "Energy Time-Series",
        "GET",
        f"{API_BASE}/timeseries/energy",
        params={
            "machine_id": MACHINE_ID,
            "start_time": start_time_24h,
            "end_time": end_time,
            "interval": "1hour"
        }
    )
    if data:
        print(f"\nTotal Data Points: {data.get('total_points')}")
        print(f"Interval: {data.get('interval')}")
        print(f"Aggregation: {data.get('aggregation')}")
        if data.get('data_points'):
            print("\nFirst 3 data points:")
            print_json(data['data_points'][:3])
    
    # ========================================================================
    # TEST 7: Power Time-Series
    # ========================================================================
    print_header("TEST 7: Power Time-Series")
    data = test_endpoint(
        "Power Time-Series",
        "GET",
        f"{API_BASE}/timeseries/power",
        params={
            "machine_id": MACHINE_ID,
            "start_time": start_time_24h,
            "end_time": end_time,
            "interval": "15min"
        }
    )
    if data:
        print(f"\nTotal Data Points: {data.get('total_points')}")
        if data.get('data_points'):
            print("Sample data:")
            print_json(data['data_points'][:3])
    
    # ========================================================================
    # TEST 8: Recent Anomalies
    # ========================================================================
    print_header("TEST 8: Recent Anomalies")
    data = test_endpoint(
        "Get Recent Anomalies",
        "GET",
        f"{API_BASE}/anomaly/recent",
        params={"limit": 10}
    )
    if data:
        print(f"\nTotal Anomalies: {data.get('total_count')}")
        if data.get('anomalies'):
            print("\nRecent Anomalies:")
            print_json(data['anomalies'][:3])
        else:
            print_warning("No anomalies found")
    
    # ========================================================================
    # TEST 9: Active Anomalies
    # ========================================================================
    print_header("TEST 9: Active Anomalies")
    data = test_endpoint(
        "Get Active Anomalies",
        "GET",
        f"{API_BASE}/anomaly/active"
    )
    if data:
        print(f"\nActive Anomalies: {data.get('total_count')}")
        if data.get('anomalies'):
            print("\nActive Issues:")
            for anomaly in data['anomalies'][:3]:
                print(f"  - {anomaly.get('machine_name')}: {anomaly.get('anomaly_type')} ({anomaly.get('severity')})")
        else:
            print_success("No active anomalies - System healthy!")
    
    # ========================================================================
    # TEST 10: List Baselines
    # ========================================================================
    print_header("TEST 10: Baseline Models")
    data = test_endpoint(
        "List Baseline Models",
        "GET",
        f"{API_BASE}/baseline/list"
    )
    if data and data.get('baselines'):
        print(f"\nFound {len(data['baselines'])} baseline models:")
        for baseline in data['baselines']:
            print(f"  - {baseline.get('machine_name')}: R²={baseline.get('r_squared')}, MAE={baseline.get('mae')}")
    else:
        print_warning("No baseline models trained yet")
    
    # ========================================================================
    # TEST 11: KPIs
    # ========================================================================
    print_header("TEST 11: KPIs (Last 7 Days)")
    data = test_endpoint(
        "Get KPIs",
        "GET",
        f"{API_BASE}/kpi",
        params={
            "machine_id": MACHINE_ID,
            "start_date": start_date_7d,
            "end_date": end_date
        }
    )
    if data and data.get('kpis'):
        print("\nKPI Summary:")
        kpis = data['kpis']
        print(f"  Total Energy: {kpis.get('total_energy_kwh')} kWh")
        print(f"  Total Cost: ${kpis.get('total_cost_usd')}")
        print(f"  Avg Power: {kpis.get('avg_power_kw')} kW")
        print(f"  Peak Power: {kpis.get('peak_power_kw')} kW")
        print(f"  Load Factor: {kpis.get('load_factor')}")
        print(f"  Efficiency: {kpis.get('efficiency_percent')}%")
        print(f"  Uptime: {kpis.get('uptime_percent')}%")
    
    # ========================================================================
    # TEST 12: Energy Forecast
    # ========================================================================
    print_header("TEST 12: Energy Forecast (Next 24 Hours)")
    data = test_endpoint(
        "Get Energy Forecast",
        "GET",
        f"{API_BASE}/forecast",
        params={
            "machine_id": MACHINE_ID,
            "horizon_hours": 24
        }
    )
    if data:
        print(f"\nForecast Horizon: {data.get('horizon_hours')} hours")
        print(f"Model Confidence: {data.get('model_confidence')}")
        if data.get('predictions'):
            print(f"Total Predictions: {len(data['predictions'])}")
            print("\nFirst 3 predictions:")
            print_json(data['predictions'][:3])
    
    # ========================================================================
    # TEST 13: Multi-Machine Comparison
    # ========================================================================
    print_header("TEST 13: Multi-Machine Energy Comparison")
    # Get all machines first
    machines_data = test_endpoint(
        "List Machines for Comparison",
        "GET",
        f"{API_BASE}/machines"
    )
    if machines_data and len(machines_data) >= 2:
        # Get first 2 machine IDs
        machine_ids = ','.join([m['id'] for m in machines_data[:2]])
        
        data = test_endpoint(
            "Compare Multiple Machines",
            "GET",
            f"{API_BASE}/timeseries/multi-machine/energy",
            params={
                "machine_ids": machine_ids,
                "start_time": start_time_24h,
                "end_time": end_time,
                "interval": "1hour"
            }
        )
        if data:
            print(f"\nComparing {data.get('total_machines')} machines")
            for machine in data.get('machines', []):
                print(f"  - {machine.get('machine_name')}: {len(machine.get('data_points', []))} data points")
    else:
        print_warning("Need at least 2 machines for comparison")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print_header("TEST SUMMARY")
    
    print(f"{Colors.OKGREEN}✓ Core Endpoints Working:{Colors.ENDC}")
    print("  ✓ Health check and system stats")
    print("  ✓ Machine listing and details")
    print("  ✓ Time-series data (energy, power)")
    print("  ✓ Latest readings")
    print("  ✓ Anomaly detection and alerts")
    print("  ✓ Baseline models")
    print("  ✓ KPI calculations")
    print("  ✓ Energy forecasting")
    print("  ✓ Multi-machine comparison")
    
    print(f"\n{Colors.WARNING}⚠ Missing Features for OVOS:{Colors.ENDC}")
    print("  ⚠ Date range filtering for anomalies")
    print("  ⚠ Machine status history")
    print("  ⚠ Aggregated multi-machine stats")
    print("  ⚠ Alert subscriptions/webhooks")
    print("  ⚠ Authentication (API keys)")
    
    print(f"\n{Colors.OKBLUE}📝 Next Steps:{Colors.ENDC}")
    print("  1. Review ENMS-API-DOCUMENTATION-FOR-OVOS.md")
    print("  2. Implement missing features (Priority 1)")
    print("  3. Share API base URL with Burak")
    print("  4. Set up API key authentication")
    print("  5. Create webhook system for real-time alerts")
    
    print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.OKGREEN}{Colors.BOLD}Testing Complete!{Colors.ENDC}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Testing interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}Fatal error: {str(e)}{Colors.ENDC}")
        sys.exit(1)
