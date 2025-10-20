"""
Integration tests for OVOS endpoints
Tests all Priority 1-3 OVOS features for reliability and error handling
"""

import pytest
import httpx
from datetime import datetime, timedelta
import uuid


BASE_URL = "http://localhost:8001/api/v1"


class TestMachineSearch:
    """Task 1: Machine search by name"""
    
    @pytest.mark.asyncio
    async def test_search_existing_machine(self):
        """Test searching for existing machine"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/ovos/machine/search?name=Compressor")
            assert response.status_code == 200
            data = response.json()
            assert "machine_id" in data
            assert "machine_name" in data
            assert "Compressor" in data["machine_name"]
    
    @pytest.mark.asyncio
    async def test_search_nonexistent_machine(self):
        """Test searching for non-existent machine returns 404"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/ovos/machine/search?name=NonExistentMachine999")
            assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_search_case_insensitive(self):
        """Test case-insensitive search"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/ovos/machine/search?name=compressor")
            assert response.status_code == 200
            data = response.json()
            assert "Compressor" in data["machine_name"]
    
    @pytest.mark.asyncio
    async def test_search_missing_name_parameter(self):
        """Test missing name parameter returns 422"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/ovos/machine/search")
            assert response.status_code == 422


class TestAnomalyRecent:
    """Task 2: Enhanced anomaly/recent with date range"""
    
    @pytest.mark.asyncio
    async def test_recent_anomalies_default(self, client: AsyncClient):
        """Test recent anomalies without date filters"""
        response = await client.get(f"{BASE_URL}/anomaly/recent")
        assert response.status_code == 200
        data = response.json()
        assert "anomalies" in data
        assert "count" in data
    
    @pytest.mark.asyncio
    async def test_recent_anomalies_with_date_range(self, client: AsyncClient):
        """Test anomalies with specific date range"""
        start = "2025-10-19T00:00:00Z"
        end = "2025-10-20T00:00:00Z"
        response = await client.get(
            f"{BASE_URL}/anomaly/recent?start_date={start}&end_date={end}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "anomalies" in data
        # Verify all anomalies are within range
        for anomaly in data["anomalies"]:
            timestamp = datetime.fromisoformat(anomaly["timestamp"].replace("Z", "+00:00"))
            assert start <= anomaly["timestamp"] <= end
    
    @pytest.mark.asyncio
    async def test_recent_anomalies_with_limit(self, client: AsyncClient):
        """Test limit parameter"""
        response = await client.get(f"{BASE_URL}/anomaly/recent?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["anomalies"]) <= 5
    
    @pytest.mark.asyncio
    async def test_recent_anomalies_invalid_date(self, client: AsyncClient):
        """Test invalid date format returns 422"""
        response = await client.get(
            f"{BASE_URL}/anomaly/recent?start_date=invalid-date"
        )
        assert response.status_code == 422


class TestOVOSSummary:
    """Task 3: OVOS summary endpoint"""
    
    @pytest.mark.asyncio
    async def test_ovos_summary(self, client: AsyncClient):
        """Test factory-wide summary"""
        response = await client.get(f"{BASE_URL}/ovos/summary")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "total_machines" in data
        assert "active_machines" in data
        assert "total_energy_kwh" in data
        assert "total_cost_usd" in data
        assert "alerts" in data
        assert "voice_summary" in data
        
        # Check data types
        assert isinstance(data["total_machines"], int)
        assert isinstance(data["total_energy_kwh"], (int, float))
        assert isinstance(data["voice_summary"], str)


class TestTopConsumers:
    """Task 4: Top consumers ranking"""
    
    @pytest.mark.asyncio
    async def test_top_consumers_energy(self, client: AsyncClient):
        """Test top energy consumers"""
        response = await client.get(f"{BASE_URL}/ovos/top-consumers?metric=energy")
        assert response.status_code == 200
        data = response.json()
        
        assert "metric" in data
        assert data["metric"] == "energy"
        assert "consumers" in data
        assert len(data["consumers"]) > 0
        
        # Verify sorted descending
        values = [c["value"] for c in data["consumers"]]
        assert values == sorted(values, reverse=True)
    
    @pytest.mark.asyncio
    async def test_top_consumers_cost(self, client: AsyncClient):
        """Test top cost consumers"""
        response = await client.get(f"{BASE_URL}/ovos/top-consumers?metric=cost")
        assert response.status_code == 200
        data = response.json()
        assert data["metric"] == "cost"
    
    @pytest.mark.asyncio
    async def test_top_consumers_power(self, client: AsyncClient):
        """Test top power consumers"""
        response = await client.get(f"{BASE_URL}/ovos/top-consumers?metric=power")
        assert response.status_code == 200
        data = response.json()
        assert data["metric"] == "power"
    
    @pytest.mark.asyncio
    async def test_top_consumers_carbon(self, client: AsyncClient):
        """Test top carbon emitters"""
        response = await client.get(f"{BASE_URL}/ovos/top-consumers?metric=carbon")
        assert response.status_code == 200
        data = response.json()
        assert data["metric"] == "carbon"
    
    @pytest.mark.asyncio
    async def test_top_consumers_with_limit(self, client: AsyncClient):
        """Test limit parameter"""
        response = await client.get(f"{BASE_URL}/ovos/top-consumers?metric=energy&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data["consumers"]) <= 3
    
    @pytest.mark.asyncio
    async def test_top_consumers_invalid_metric(self, client: AsyncClient):
        """Test invalid metric returns 422"""
        response = await client.get(f"{BASE_URL}/ovos/top-consumers?metric=invalid")
        assert response.status_code == 422


class TestMachineStatus:
    """Task 5: OVOS machine status by name"""
    
    @pytest.mark.asyncio
    async def test_machine_status_existing(self, client: AsyncClient):
        """Test status for existing machine"""
        response = await client.get(f"{BASE_URL}/ovos/machine/status?name=Compressor-1")
        assert response.status_code == 200
        data = response.json()
        
        assert "machine_name" in data
        assert "status" in data
        assert "current_power_kw" in data
        assert "energy_today_kwh" in data
        assert "voice_response" in data
    
    @pytest.mark.asyncio
    async def test_machine_status_nonexistent(self, client: AsyncClient):
        """Test status for non-existent machine returns 404"""
        response = await client.get(f"{BASE_URL}/ovos/machine/status?name=NonExistent999")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_machine_status_missing_name(self, client: AsyncClient):
        """Test missing name parameter returns 422"""
        response = await client.get(f"{BASE_URL}/ovos/machine/status")
        assert response.status_code == 422


class TestFactoryKPI:
    """Task 6: Factory-wide KPI aggregation"""
    
    @pytest.mark.asyncio
    async def test_single_factory_kpi(self, client: AsyncClient):
        """Test single factory KPI aggregation"""
        # Use Demo Plant factory ID
        factory_id = "f0000000-0000-0000-0000-000000000001"
        response = await client.get(f"{BASE_URL}/kpi/factory/{factory_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert "factory_id" in data
        assert "factory_name" in data
        assert "total_energy_kwh" in data
        assert "total_cost_usd" in data
        assert "machines_count" in data
        assert "total_production_units" in data
    
    @pytest.mark.asyncio
    async def test_all_factories_kpi(self, client: AsyncClient):
        """Test all factories KPI aggregation"""
        response = await client.get(f"{BASE_URL}/kpi/factories")
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
    
    @pytest.mark.asyncio
    async def test_nonexistent_factory(self, client: AsyncClient):
        """Test non-existent factory returns 404"""
        fake_id = "f9999999-9999-9999-9999-999999999999"
        response = await client.get(f"{BASE_URL}/kpi/factory/{fake_id}")
        assert response.status_code == 404


class TestTimeOfUsePricing:
    """Task 7: Time-of-use pricing tiers"""
    
    @pytest.mark.asyncio
    async def test_standard_tariff(self, client: AsyncClient):
        """Test standard flat rate tariff"""
        machine_id = "c0000000-0000-0000-0000-000000000001"
        start = "2025-10-19T00:00:00Z"
        end = "2025-10-20T00:00:00Z"
        
        response = await client.get(
            f"{BASE_URL}/kpi/energy-cost?machine_id={machine_id}"
            f"&start_time={start}&end_time={end}&tariff=standard"
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["tariff_type"] == "standard"
        assert "total_energy_kwh" in data
        assert "total_cost_usd" in data
        assert "rate_per_kwh" in data
    
    @pytest.mark.asyncio
    async def test_time_of_use_tariff(self, client: AsyncClient):
        """Test time-of-use tariff with peak/off-peak rates"""
        machine_id = "c0000000-0000-0000-0000-000000000001"
        start = "2025-10-19T00:00:00Z"
        end = "2025-10-20T00:00:00Z"
        
        response = await client.get(
            f"{BASE_URL}/kpi/energy-cost?machine_id={machine_id}"
            f"&start_time={start}&end_time={end}&tariff=time_of_use"
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
    
    @pytest.mark.asyncio
    async def test_demand_charge_tariff(self, client: AsyncClient):
        """Test demand charge tariff"""
        machine_id = "c0000000-0000-0000-0000-000000000001"
        start = "2025-10-19T00:00:00Z"
        end = "2025-10-20T00:00:00Z"
        
        response = await client.get(
            f"{BASE_URL}/kpi/energy-cost?machine_id={machine_id}"
            f"&start_time={start}&end_time={end}&tariff=demand_charge"
            f"&demand_charge=20.0"
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["tariff_type"] == "demand_charge"
        assert "energy_charge_usd" in data
        assert "demand_charge_usd" in data
        assert "peak_demand_kw" in data
        assert "total_cost_usd" in data
    
    @pytest.mark.asyncio
    async def test_invalid_tariff_type(self, client: AsyncClient):
        """Test invalid tariff type returns 422"""
        machine_id = "c0000000-0000-0000-0000-000000000001"
        start = "2025-10-19T00:00:00Z"
        end = "2025-10-20T00:00:00Z"
        
        response = await client.get(
            f"{BASE_URL}/kpi/energy-cost?machine_id={machine_id}"
            f"&start_time={start}&end_time={end}&tariff=invalid"
        )
        assert response.status_code == 422


class TestForecastEndpoint:
    """Task 10: Simplified forecast endpoint"""
    
    @pytest.mark.asyncio
    async def test_factory_wide_forecast(self, client: AsyncClient):
        """Test factory-wide forecast"""
        response = await client.get(f"{BASE_URL}/ovos/forecast/tomorrow")
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
    
    @pytest.mark.asyncio
    async def test_single_machine_forecast(self, client: AsyncClient):
        """Test single machine forecast"""
        machine_id = "c0000000-0000-0000-0000-000000000001"
        response = await client.get(
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
    
    @pytest.mark.asyncio
    async def test_forecast_invalid_machine_id(self, client: AsyncClient):
        """Test forecast with invalid machine ID returns 404"""
        fake_id = "c9999999-9999-9999-9999-999999999999"
        response = await client.get(
            f"{BASE_URL}/ovos/forecast/tomorrow?machine_id={fake_id}"
        )
        assert response.status_code == 404


class TestEdgeCases:
    """Test error handling and edge cases"""
    
    @pytest.mark.asyncio
    async def test_invalid_uuid_format(self, client: AsyncClient):
        """Test endpoints with invalid UUID format"""
        response = await client.get(f"{BASE_URL}/kpi/factory/not-a-uuid")
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_future_date_range(self, client: AsyncClient):
        """Test endpoints with future dates"""
        start = "2026-01-01T00:00:00Z"
        end = "2026-01-02T00:00:00Z"
        response = await client.get(
            f"{BASE_URL}/anomaly/recent?start_date={start}&end_date={end}"
        )
        assert response.status_code == 200
        # Should return empty results, not error
        data = response.json()
        assert data["count"] == 0
    
    @pytest.mark.asyncio
    async def test_invalid_date_range(self, client: AsyncClient):
        """Test start date after end date"""
        start = "2025-10-20T00:00:00Z"
        end = "2025-10-19T00:00:00Z"
        response = await client.get(
            f"{BASE_URL}/anomaly/recent?start_date={start}&end_date={end}"
        )
        # Should handle gracefully (either 422 or empty results)
        assert response.status_code in [200, 422]


# Pytest fixtures
@pytest.fixture
def client():
    """Create async HTTP client"""
    return AsyncClient(base_url="http://localhost:8001", timeout=30.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
