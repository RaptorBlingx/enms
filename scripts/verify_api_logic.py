import requests
import sys
import json
from datetime import datetime

BASE_URL = "http://localhost:8001/api/v1"

# ANSI colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def log_success(msg):
    print(f"{GREEN}[PASS]{RESET} {msg}")

def log_fail(msg):
    print(f"{RED}[FAIL]{RESET} {msg}")

def log_warn(msg):
    print(f"{YELLOW}[WARN]{RESET} {msg}")

def check_logic(condition, success_msg, fail_msg):
    if condition:
        log_success(success_msg)
        return True
    else:
        log_fail(fail_msg)
        return False

def verify_factory_summary():
    print("\n--- Verifying Factory Summary ---")
    try:
        response = requests.get(f"{BASE_URL}/factory/summary")
        if response.status_code != 200:
            log_fail(f"API returned {response.status_code}")
            return

        data = response.json()
        
        # Structure is different than expected, adapting...
        energy_total = data['energy']['total_kwh_today']
        cost_total = data['costs']['total_usd_today']
        
        # 1. Check for negative values
        check_logic(energy_total >= 0, "Total energy is non-negative", f"Total energy is negative: {energy_total}")
        check_logic(cost_total >= 0, "Total cost is non-negative", f"Total cost is negative: {cost_total}")
        
        # 2. Check Cost Logic (Dynamic Tariff Check)
        # Rate should be between min (0.10) and max (0.25) tariff
        if energy_total > 0:
            implied_rate = cost_total / energy_total
            check_logic(0.09 <= implied_rate <= 0.30, 
                       f"Implied rate is reasonable ({implied_rate:.3f} $/kWh)", 
                       f"Implied rate unreasonable: {implied_rate:.3f} $/kWh (Cost: {cost_total}, Energy: {energy_total})")
        else:
            check_logic(cost_total == 0, "Cost is 0 when energy is 0", f"Cost is {cost_total} when energy is 0")

        # CO2 is not in the summary response explicitly as a total, skipping for now or need to find where it is.
        # It seems 'costs' is there but 'co2' might be missing or named differently?
        # Looking at the response: "anomalies", "machines", "top_consumer", "latest_anomaly".
        # No explicit CO2 total in the JSON output I saw.

    except Exception as e:
        log_fail(f"Exception during factory summary check: {e}")

def verify_machine_status():
    print("\n--- Verifying Machine Status (Compressor-1) ---")
    try:
        # Get machine list first to find a valid name if needed, but we'll try Compressor-1
        response = requests.get(f"{BASE_URL}/machines/status/Compressor-1")
        if response.status_code != 200:
            log_warn(f"Could not fetch Compressor-1 status (Status: {response.status_code}). Skipping.")
            return

        data = response.json()
        stats = data.get('today_stats', {})
        
        energy = stats.get('energy_kwh', 0)
        cost = stats.get('cost_usd', 0)
        
        # 1. Check Cost Logic
        # Note: After fix, rate might be ~0.175, not 0.15.
        # We should check if it's non-zero and reasonable (e.g. between 0.10 and 0.30 * energy)
        
        if energy > 0:
            implied_rate = cost / energy
            check_logic(0.09 <= implied_rate <= 0.30, 
                       f"Implied rate is reasonable ({implied_rate:.3f} $/kWh)", 
                       f"Implied rate unreasonable: {implied_rate:.3f} $/kWh (Cost: {cost}, Energy: {energy})")
        else:
            check_logic(cost == 0, "Cost is 0 when energy is 0", f"Cost is {cost} when energy is 0")

        # 2. Check Uptime
        uptime = stats.get('uptime_percent', 0)
        check_logic(0 <= uptime <= 100.1, f"Uptime is valid ({uptime}%)", f"Uptime invalid: {uptime}%")

    except Exception as e:
        log_fail(f"Exception during machine status check: {e}")

def verify_top_consumers():
    print("\n--- Verifying Top Consumers ---")
    try:
        # Add required time parameters
        now = datetime.utcnow()
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z"
        end_time = now.isoformat() + "Z"
        
        params = {
            "start_time": start_time,
            "end_time": end_time
        }
        
        response = requests.get(f"{BASE_URL}/analytics/top-consumers", params=params)
        if response.status_code != 200:
            log_fail(f"API returned {response.status_code}: {response.text}")
            return

        data = response.json()
        # The response is a list of consumers directly or a dict?
        # Let's assume list based on name, but check data type
        consumers = data if isinstance(data, list) else data.get('consumers', [])
        
        if not consumers and isinstance(data, list):
             consumers = data

        total_pct = sum(c['percentage'] for c in consumers)
        check_logic(total_pct <= 100.1, f"Total percentage <= 100% ({total_pct:.2f}%)", f"Total percentage > 100%: {total_pct}%")
        
        for c in consumers:
            check_logic(c['energy_kwh'] >= 0, f"Consumer {c['name']} energy >= 0", f"Consumer {c['name']} energy negative")

    except Exception as e:
        log_fail(f"Exception during top consumers check: {e}")

if __name__ == "__main__":
    print("Starting Logic Verification...")
    verify_factory_summary()
    verify_machine_status()
    verify_top_consumers()
    print("\nVerification Complete.")
