"""
Integration tests for OVOS endpoints - Simplified sync version
Tests all Priority 1-3 OVOS features for reliability and error handling
"""

import httpx
from datetime import datetime, timedelta


BASE_URL = "http://localhost:8001/api/v1"


class TestMachineSearch:
    """Task 1: Machine search by name"""
    
    def test_search_existing_machine(self):
        """Test searching for existing machine"""
        response = httpx.get(f"{BASE_URL}/machines?search=Compressor")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "id" in data[0]
        assert "name" in data[0]
        assert "Compressor" in data[0]["name"]
    
    def test_search_nonexistent_machine(self):
        """Test searching for non-existent machine returns empty array"""
        response = httpx.get(f"{BASE_URL}/machines?search=NonExistentMachine999")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_search_case_insensitive(self):
        """Test case-insensitive search"""
        response = httpx.get(f"{BASE_URL}/machines?search=compressor")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "Compressor" in data[0]["name"]
    
    def test_search_without_parameter(self):
        """Test search without parameter returns all machines"""
        response = httpx.get(f"{BASE_URL}/machines")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0


class TestAnomalyRecent:
    """Task 2: Enhanced anomaly/recent with date range"""
    
    def test_recent_anomalies_default(self):
        """Test recent anomalies without date filters"""
        response = httpx.get(f"{BASE_URL}/anomaly/recent")
        assert response.status_code == 200
        data = response.json()
        assert "anomalies" in data
        assert "total_count" in data
    
    def test_recent_anomalies_with_date_range(self):
        """Test anomalies with specific date range"""
        start = "2025-10-19T00:00:00Z"
        end = "2025-10-20T00:00:00Z"
        response = httpx.get(
            f"{BASE_URL}/anomaly/recent?start_date={start}&end_date={end}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "anomalies" in data
    
    def test_recent_anomalies_with_limit(self):
        """Test limit parameter"""
        response = httpx.get(f"{BASE_URL}/anomaly/recent?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["anomalies"]) <= 5


class TestOVOSSummary:
    """Task 3: OVOS summary endpoint"""
    
    def test_ovos_summary(self):
        """Test factory-wide summary"""
        response = httpx.get(f"{BASE_URL}/ovos/summary")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields based on actual API response
        assert "machines" in data
        assert "energy" in data
        assert "costs" in data
        assert "anomalies" in data
        assert "status" in data
        assert "timestamp" in data
        
        # Check nested structures
        machines = data["machines"]
        assert "total" in machines
        assert "active" in machines
        
        # Check data types
        assert isinstance(machines["total"], int)
        assert isinstance(data["energy"], dict)
        assert isinstance(data["timestamp"], str)


class TestTopConsumers:
    """Task 4: Top consumers ranking"""
    
    def test_top_consumers_energy(self):
        """Test top energy consumers"""
        start = "2025-10-19T00:00:00Z"
        end = "2025-10-20T00:00:00Z"
        response = httpx.get(
            f"{BASE_URL}/ovos/top-consumers?metric=energy&start_time={start}&end_time={end}"
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "metric" in data
        assert data["metric"] == "energy"
        assert "ranking" in data
        assert len(data["ranking"]) > 0
        
        # Verify sorted descending by rank
        ranks = [c["rank"] for c in data["ranking"]]
        assert ranks == list(range(1, len(ranks) + 1))
    
    def test_top_consumers_cost(self):
        """Test top cost consumers"""
        start = "2025-10-19T00:00:00Z"
        end = "2025-10-20T00:00:00Z"
        response = httpx.get(
            f"{BASE_URL}/ovos/top-consumers?metric=cost&start_time={start}&end_time={end}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["metric"] == "cost"
    
    def test_top_consumers_power(self):
        """Test top power consumers"""
        start = "2025-10-19T00:00:00Z"
        end = "2025-10-20T00:00:00Z"
        response = httpx.get(
            f"{BASE_URL}/ovos/top-consumers?metric=power&start_time={start}&end_time={end}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["metric"] == "power"
    
    def test_top_consumers_carbon(self):
        """Test top carbon emitters"""
        start = "2025-10-19T00:00:00Z"
        end = "2025-10-20T00:00:00Z"
        response = httpx.get(
            f"{BASE_URL}/ovos/top-consumers?metric=carbon&start_time={start}&end_time={end}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["metric"] == "carbon"
    
    def test_top_consumers_with_limit(self):
        """Test limit parameter"""
        start = "2025-10-19T00:00:00Z"
        end = "2025-10-20T00:00:00Z"
        response = httpx.get(
            f"{BASE_URL}/ovos/top-consumers?metric=energy&limit=3&start_time={start}&end_time={end}"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["ranking"]) <= 3
    
    def test_top_consumers_invalid_metric(self):
        """Test invalid metric returns 422"""
        start = "2025-10-19T00:00:00Z"
        end = "2025-10-20T00:00:00Z"
        response = httpx.get(
            f"{BASE_URL}/ovos/top-consumers?metric=invalid&start_time={start}&end_time={end}"
        )
        assert response.status_code == 422


class TestMachineStatus:
    """Task 5: OVOS machine status by name"""
    
    def test_machine_status_existing(self):
        """Test status for existing machine"""
        response = httpx.get(f"{BASE_URL}/ovos/machines/Compressor-1/status")
        assert response.status_code == 200
        data = response.json()
        
        assert "machine_name" in data
        assert "machine_id" in data
        assert "current_status" in data
        assert "today_stats" in data
        assert "recent_anomalies" in data
    
    def test_machine_status_nonexistent(self):
        """Test status for non-existent machine returns 404"""
        response = httpx.get(f"{BASE_URL}/ovos/machines/NonExistent999/status")
        assert response.status_code == 404
    
    def test_machine_status_partial_match(self):
        """Test status with partial name match"""
        response = httpx.get(f"{BASE_URL}/ovos/machines/compressor/status")
        assert response.status_code == 200
        data = response.json()
        assert "Compressor" in data["machine_name"]


class TestFactoryKPI:
    """Task 6: Factory-wide KPI aggregation"""
    
    def test_single_factory_kpi(self):
        """Test single factory KPI aggregation"""
        # Use Demo Plant factory ID
        factory_id = "f0000000-0000-0000-0000-000000000001"
        start = "2025-10-19T00:00:00Z"
        end = "2025-10-20T00:00:00Z"
        response = httpx.get(f"{BASE_URL}/kpi/factory/{factory_id}?start={start}&end={end}")
        assert response.status_code == 200
        data = response.json()
        
        assert "factory_id" in data
        assert "factory_name" in data
        assert "total_energy_kwh" in data
        assert "total_cost_usd" in data
        assert "machines_count" in data
        assert "total_production_units" in data
    
    def test_all_factories_kpi(self):
        """Test all factories KPI aggregation"""
        start = "2025-10-19T00:00:00Z"
        end = "2025-10-20T00:00:00Z"
        response = httpx.get(f"{BASE_URL}/kpi/factories?start={start}&end={end}")
        assert response.status_code == 200
        data = response.json()
        
        assert "enterprise_totals" in data
        assert "factories" in data
        assert "rankings" in data
        
        # Verify enterprise totals
        totals = data["enterprise_totals"]
        assert "total_energy_kwh" in totals
        assert "total_cost_usd" in totals
        assert "total_factories" in totals
        
        # Verify rankings
        rankings = data["rankings"]
        assert len(rankings) > 0
        assert "factory_name" in rankings[0]
        assert "energy_kwh" in rankings[0]
        assert "percentage" in rankings[0]
    
    def test_nonexistent_factory(self):
        """Test non-existent factory returns 404"""
        fake_id = "f9999999-9999-9999-9999-999999999999"
        start = "2025-10-19T00:00:00Z"
        end = "2025-10-20T00:00:00Z"
        response = httpx.get(f"{BASE_URL}/kpi/factory/{fake_id}?start={start}&end={end}")
        assert response.status_code == 404


class TestTimeOfUsePricing:
    """Task 7: Time-of-use pricing tiers"""
    
    def test_standard_tariff(self):
        """Test standard flat rate tariff"""
        machine_id = "c0000000-0000-0000-0000-000000000001"
        start = "2025-10-19T00:00:00Z"
        end = "2025-10-20T00:00:00Z"
        
        response = httpx.get(
            f"{BASE_URL}/kpi/energy-cost?machine_id={machine_id}"
            f"&start={start}&end={end}&tariff=standard"
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["tariff_type"] == "standard"
        assert "total_energy_kwh" in data
        assert "total_cost_usd" in data
        assert "rate_per_kwh" in data
    
    def test_time_of_use_tariff(self):
        """Test time-of-use tariff with peak/off-peak rates"""
        machine_id = "c0000000-0000-0000-0000-000000000001"
        start = "2025-10-19T00:00:00Z"
        end = "2025-10-20T00:00:00Z"
        
        response = httpx.get(
            f"{BASE_URL}/kpi/energy-cost?machine_id={machine_id}"
            f"&start={start}&end={end}&tariff=time_of_use"
            f"&peak_rate=0.25&offpeak_rate=0.08"
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["tariff_type"] == "time_of_use"
        assert "peak_energy_kwh" in data
        assert "offpeak_energy_kwh" in data
        assert "peak_cost_usd" in data
        assert "offpeak_cost_usd" in data
        assert "savings_vs_standard" in data
    
    def test_demand_charge_tariff(self):
        """Test demand charge tariff"""
        machine_id = "c0000000-0000-0000-0000-000000000001"
        start = "2025-10-19T00:00:00Z"
        end = "2025-10-20T00:00:00Z"
        
        response = httpx.get(
            f"{BASE_URL}/kpi/energy-cost?machine_id={machine_id}"
            f"&start={start}&end={end}&tariff=demand_charge"
            f"&demand_charge=20.0"
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["tariff_type"] == "demand_charge"
        assert "energy_charge_usd" in data
        assert "demand_charge_usd" in data
        assert "peak_demand_kw" in data
        assert "total_cost_usd" in data
    
    def test_invalid_tariff_type(self):
        """Test invalid tariff type returns 422"""
        machine_id = "c0000000-0000-0000-0000-000000000001"
        start = "2025-10-19T00:00:00Z"
        end = "2025-10-20T00:00:00Z"
        
        response = httpx.get(
            f"{BASE_URL}/kpi/energy-cost?machine_id={machine_id}"
            f"&start={start}&end={end}&tariff=invalid"
        )
        assert response.status_code == 422


class TestForecastEndpoint:
    """Task 10: Simplified forecast endpoint"""
    
    def test_factory_wide_forecast(self):
        """Test factory-wide forecast"""
        response = httpx.get(f"{BASE_URL}/ovos/forecast/tomorrow")
        assert response.status_code == 200
        data = response.json()
        
        assert data["forecast_type"] == "factory_wide"
        assert "forecast_date" in data
        assert "total_predicted_energy_kwh" in data
        assert "total_predicted_cost_usd" in data
        assert "predicted_peak_demand_kw" in data
        assert "average_confidence" in data
        assert "by_machine" in data
        
        # Check confidence is within valid range
        assert 0.5 <= data["average_confidence"] <= 0.95
        
        # Verify tomorrow's date
        tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
        assert data["forecast_date"] == tomorrow
    
    def test_single_machine_forecast(self):
        """Test single machine forecast"""
        machine_id = "c0000000-0000-0000-0000-000000000001"
        response = httpx.get(
            f"{BASE_URL}/ovos/forecast/tomorrow?machine_id={machine_id}"
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["forecast_type"] == "single_machine"
        assert "machine_name" in data
        assert "predicted_energy_kwh" in data
        assert "predicted_cost_usd" in data
        assert "predicted_avg_power_kw" in data
        assert "predicted_peak_power_kw" in data
        assert "confidence" in data
        assert "method" in data
        
        # Check confidence is within valid range
        assert 0.5 <= data["confidence"] <= 0.95
        assert data["method"] == "7-day moving average"
    
    def test_forecast_invalid_machine_id(self):
        """Test forecast with invalid machine ID returns 404"""
        fake_id = "c9999999-9999-9999-9999-999999999999"
        response = httpx.get(
            f"{BASE_URL}/ovos/forecast/tomorrow?machine_id={fake_id}"
        )
        assert response.status_code == 404


class TestEdgeCases:
    """Test error handling and edge cases"""
    
    def test_invalid_uuid_format(self):
        """Test endpoints with invalid UUID format"""
        response = httpx.get(f"{BASE_URL}/kpi/factory/not-a-uuid")
        assert response.status_code == 422
    
    def test_future_date_range(self):
        """Test endpoints with future dates"""
        start = "2026-01-01T00:00:00Z"
        end = "2026-01-02T00:00:00Z"
        response = httpx.get(
            f"{BASE_URL}/anomaly/recent?start_date={start}&end_date={end}"
        )
        assert response.status_code == 200
        # Should return empty results, not error
        data = response.json()
        assert data["total_count"] == 0
    
    def test_invalid_date_range(self):
        """Test start date after end date"""
        start = "2025-10-20T00:00:00Z"
        end = "2025-10-19T00:00:00Z"
        response = httpx.get(
            f"{BASE_URL}/anomaly/recent?start_date={start}&end_date={end}"
        )
        # Should handle gracefully (either 422 or empty results)
        assert response.status_code in [200, 422]
