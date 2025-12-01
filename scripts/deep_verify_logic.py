import requests
import sys
import json
from datetime import datetime, timedelta, timezone
import time

# Configuration
BASE_URL = "http://localhost:8001/api/v1"
# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

def log_pass(msg):
    print(f"{GREEN}[PASS]{RESET} {msg}")

def log_fail(msg):
    print(f"{RED}[FAIL]{RESET} {msg}")

def log_warn(msg):
    print(f"{YELLOW}[WARN]{RESET} {msg}")

def log_info(msg):
    print(f"{CYAN}[INFO]{RESET} {msg}")

def get_iso_time(delta_hours=0):
    """Get current UTC time +/- delta hours in ISO format"""
    dt = datetime.now(timezone.utc) + timedelta(hours=delta_hours)
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

def check_almost_equal(val1, val2, tolerance_percent=1.0, label="Values"):
    """Check if two values are within X% of each other"""
    if val1 == 0 and val2 == 0:
        return True
    
    diff = abs(val1 - val2)
    avg = (abs(val1) + abs(val2)) / 2
    
    # Avoid division by zero
    if avg == 0:
        percent_diff = 0
    else:
        percent_diff = (diff / avg) * 100
        
    if percent_diff <= tolerance_percent:
        log_pass(f"{label}: {val1:.2f} ≈ {val2:.2f} (Diff: {percent_diff:.2f}%)")
        return True
    else:
        log_fail(f"{label}: {val1:.2f} != {val2:.2f} (Diff: {percent_diff:.2f}% > {tolerance_percent}%)")
        return False

def test_physics_power_energy():
    """
    Test 1: The Physics Rule
    Energy (kWh) should approx equal Avg Power (kW) * Time (h)
    Using 1-minute interval to account for missing data gaps.
    """
    log_info("--- Test 1: Physics Rule (Energy ≈ Power × Time) ---")
    
    # Get a machine (Compressor-1)
    machine_id = "c0000000-0000-0000-0000-000000000001" # Compressor-1
    
    # Query last 1 hour of data
    end_time = get_iso_time()
    start_time = get_iso_time(-1)
    
    # 1. Get Energy (1min interval)
    resp_energy = requests.get(f"{BASE_URL}/timeseries/energy", params={
        "machine_id": machine_id,
        "start_time": start_time,
        "end_time": end_time,
        "interval": "1min"
    })
    
    # 2. Get Power (1min interval)
    resp_power = requests.get(f"{BASE_URL}/timeseries/power", params={
        "machine_id": machine_id,
        "start_time": start_time,
        "end_time": end_time,
        "interval": "1min"
    })
    
    if resp_energy.status_code != 200 or resp_power.status_code != 200:
        log_fail("Could not fetch timeseries data")
        return

    energy_data = resp_energy.json().get('data_points', [])
    power_data = resp_power.json().get('data_points', [])
    
    if not energy_data or not power_data:
        log_warn("No data points found for last hour")
        return

    # Calculate totals from 1-min data
    total_energy = sum(d['value'] for d in energy_data)
    avg_power = sum(d['value'] for d in power_data) / len(power_data)
    
    # Expected Energy = Avg Power * (Minutes / 60)
    minutes_count = len(energy_data)
    expected_energy = avg_power * (minutes_count / 60.0)
    
    check_almost_equal(total_energy, expected_energy, tolerance_percent=1.0, label=f"Energy vs Power ({minutes_count} min samples)")


def test_sum_of_parts():
    """
    Test 2: Sum of Parts
    Factory Total Energy should equal Sum of Active Machines Energy
    """
    log_info("\n--- Test 2: Sum of Parts (Factory vs Machines) ---")
    
    # 1. Get Factory Summary
    resp_factory = requests.get(f"{BASE_URL}/factory/summary")
    if resp_factory.status_code != 200:
        log_fail("Factory summary failed")
        return
        
    factory_total = resp_factory.json()['energy']['total_kwh_today']
    log_info(f"Factory Summary Total: {factory_total}")
    
    # 2. Get All Machines Status
    resp_machines = requests.get(f"{BASE_URL}/machines")
    machines = resp_machines.json()
    
    sum_machines = 0
    print(f"{'Machine Name':<30} | {'Energy (kWh)':<15}")
    print("-" * 50)
    
    for m in machines:
        # Get status for each machine
        resp_status = requests.get(f"{BASE_URL}/machines/status/{m['name']}")
        if resp_status.status_code == 200:
            val = resp_status.json().get('today_stats', {}).get('energy_kwh', 0)
            print(f"{m['name']:<30} | {val:<15.2f}")
            sum_machines += val
        else:
            print(f"{m['name']:<30} | ERROR")
            
    print("-" * 50)
    print(f"{'TOTAL':<30} | {sum_machines:<15.2f}")
            
    check_almost_equal(factory_total, sum_machines, tolerance_percent=2.0, label="Factory Total vs Sum(Machines)")

def test_single_source_truth():
    """
    Test 3: Single Source of Truth
    Machine Status API (Today) vs Timeseries API (Sum of today)
    """
    log_info("\n--- Test 3: Single Source of Truth (Status vs Timeseries) ---")
    
    machine_name = "Compressor-1"
    machine_id = "c0000000-0000-0000-0000-000000000001"
    
    # 1. Get Status API value
    resp_status = requests.get(f"{BASE_URL}/machines/status/{machine_name}")
    status_val = resp_status.json().get('today_stats', {}).get('energy_kwh', 0)
    
    # 2. Get Timeseries Sum
    # Calculate "Today" start/end
    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%dT%H:%M:%SZ')
    end_of_day = now.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    resp_ts = requests.get(f"{BASE_URL}/timeseries/energy", params={
        "machine_id": machine_id,
        "start_time": start_of_day,
        "end_time": end_of_day,
        "interval": "1hour"
    })
    
    ts_data = resp_ts.json().get('data_points', [])
    ts_sum = sum(d['value'] for d in ts_data)
    
    check_almost_equal(status_val, ts_sum, tolerance_percent=1.0, label=f"{machine_name} Status vs Timeseries")

def test_impossible_values():
    """
    Test 4: Impossible Values
    Load Factor > 1.0, Negative Costs, etc.
    """
    log_info("\n--- Test 4: Impossible Values ---")
    
    machine_id = "c0000000-0000-0000-0000-000000000001"
    
    # Get KPI
    end = get_iso_time()
    start = get_iso_time(-24)
    
    resp_kpi = requests.get(f"{BASE_URL}/kpi/all", params={
        "machine_id": machine_id,
        "start": start,
        "end": end
    })
    
    if resp_kpi.status_code == 200:
        kpis = resp_kpi.json().get('kpis', {})
        
        # Load Factor
        lf = kpis.get('load_factor', {}).get('value', 0)
        if lf > 1.05: # Allow tiny floating point error
            log_fail(f"Load Factor > 1.0: {lf}")
        else:
            log_pass(f"Load Factor valid: {lf}")
            
        # Cost
        cost = kpis.get('energy_cost', {}).get('value', 0)
        if cost < 0:
            log_fail(f"Negative Cost: {cost}")
        else:
            log_pass(f"Cost valid (>=0): {cost}")

if __name__ == "__main__":
    print("Starting Deep Logic Verification...\n")
    try:
        test_physics_power_energy()
        test_sum_of_parts()
        test_single_source_truth()
        test_impossible_values()
    except Exception as e:
        log_fail(f"Script crashed: {e}")
    print("\nVerification Complete.")
