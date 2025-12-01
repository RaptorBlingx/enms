"""
EnMS Analytics - Endpoint Consistency Tests
============================================
Tests to verify consistent data across all API endpoints.
Addresses OVOS bug report regarding inconsistent energy values.

Bug Fix: Phase 4 Session 9
Author: EnMS Team
Date: 2025-11-06
"""

import pytest
from datetime import datetime, timedelta, timezone
import httpx

BASE_URL = "http://analytics:8001/api/v1"


@pytest.mark.asyncio
async def test_timeseries_vs_analytics_consistency():
    """PRIMARY BUG TEST: timeseries vs analytics endpoints must return identical energy totals"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        end = datetime.now(timezone.utc)
        start = end - timedelta(hours=1)
        
        machines_resp = await client.get(f"{BASE_URL}/machines")
        assert machines_resp.status_code == 200
        machines = machines_resp.json()
        machine_id = machines[0]['id']
        
        timeseries_resp = await client.get(
            f"{BASE_URL}/timeseries/energy",
            params={'machine_id': machine_id, 'start_time': start.isoformat(), 'end_time': end.isoformat(), 'interval': '1min'}
        )
        
        if timeseries_resp.status_code == 404:
            pytest.skip("No data")
        
        assert timeseries_resp.status_code == 200
        timeseries_total = sum(p['value'] for p in timeseries_resp.json()['data_points'])
        
        analytics_resp = await client.get(
            f"{BASE_URL}/analytics/top-consumers",
            params={'metric': 'energy', 'start_time': start.isoformat(), 'end_time': end.isoformat(), 'limit': 10}
        )
        assert analytics_resp.status_code == 200
        machine_ranking = next((m for m in analytics_resp.json()['ranking'] if m['machine_id'] == machine_id), None)
        assert machine_ranking is not None
        
        analytics_total = machine_ranking['energy_kwh']
        assert abs(timeseries_total - analytics_total) < 0.01, f"Mismatch: {timeseries_total:.2f} vs {analytics_total:.2f} kWh"


@pytest.mark.asyncio
async def test_multi_machine_vs_single_machine_consistency():
    """Multi-machine endpoint must match individual queries"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        start = datetime.now(timezone.utc) - timedelta(hours=24)
        end = datetime.now(timezone.utc)
        
        machines = (await client.get(f"{BASE_URL}/machines")).json()
        machine_ids = [m['id'] for m in machines[:3]]
        
        multi_resp = await client.get(
            f"{BASE_URL}/timeseries/multi-machine/energy",
            params={'machine_ids': ','.join(machine_ids), 'start_time': start.isoformat(), 'end_time': end.isoformat(), 'interval': '1hour'}
        )
        assert multi_resp.status_code == 200
        multi_data = multi_resp.json()
        
        for machine_id in machine_ids:
            single_resp = await client.get(
                f"{BASE_URL}/timeseries/energy",
                params={'machine_id': machine_id, 'start_time': start.isoformat(), 'end_time': end.isoformat(), 'interval': '1hour'}
            )
            
            if single_resp.status_code == 404:
                continue
                
            single_total = sum(p['value'] for p in single_resp.json()['data_points'])
            multi_machine = next((m for m in multi_data['machines'] if m['machine_id'] == machine_id), None)
            assert multi_machine
            multi_total = sum(p['value'] for p in multi_machine['data_points'])
            assert abs(single_total - multi_total) < 0.01


@pytest.mark.asyncio
async def test_exclusive_end_boundary():
    """End time must be exclusive (bucket < end_time, NOT <=)"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        end = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        start = end - timedelta(hours=1)
        
        machines = (await client.get(f"{BASE_URL}/machines")).json()
        resp = await client.get(
            f"{BASE_URL}/timeseries/energy",
            params={'machine_id': machines[0]['id'], 'start_time': start.isoformat(), 'end_time': end.isoformat(), 'interval': '1min'}
        )
        
        if resp.status_code == 404:
            pytest.skip("No data")
            
        data = resp.json()
        if data['data_points']:
            timestamps = [datetime.fromisoformat(p['timestamp']) for p in data['data_points']]
            assert max(timestamps) < end, "End boundary not exclusive!"


@pytest.mark.asyncio
async def test_ovos_exact_scenario():
    """OVOS bug: all 3 endpoints must return same total for same query"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        end = datetime.now(timezone.utc)
        start = end - timedelta(hours=1)
        
        machines = (await client.get(f"{BASE_URL}/machines")).json()
        machine_id = machines[0]['id']
        
        resp1 = await client.get(
            f"{BASE_URL}/timeseries/energy",
            params={'machine_id': machine_id, 'start_time': start.isoformat(), 'end_time': end.isoformat(), 'interval': '1min'}
        )
        
        if resp1.status_code == 404:
            pytest.skip("No data")
            
        total1 = sum(p['value'] for p in resp1.json()['data_points'])
        
        resp2 = await client.get(
            f"{BASE_URL}/analytics/top-consumers",
            params={'metric': 'energy', 'start_time': start.isoformat(), 'end_time': end.isoformat(), 'limit': 10}
        )
        ranking = next((m for m in resp2.json()['ranking'] if m['machine_id'] == machine_id), None)
        total2 = ranking['energy_kwh'] if ranking else 0
        
        resp3 = await client.get(
            f"{BASE_URL}/timeseries/multi-machine/energy",
            params={'machine_ids': machine_id, 'start_time': start.isoformat(), 'end_time': end.isoformat(), 'interval': '1hour'}
        )
        total3 = sum(p['value'] for p in resp3.json()['machines'][0]['data_points'])
        
        assert abs(total1 - total2) < 0.01, f"Endpoint 1 vs 2: {total1:.2f} vs {total2:.2f} kWh"
        assert abs(total1 - total3) < 0.01, f"Endpoint 1 vs 3: {total1:.2f} vs {total3:.2f} kWh"
