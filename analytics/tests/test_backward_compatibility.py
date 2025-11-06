"""
EnMS Analytics - Backward Compatibility Tests
==============================================
Ensure old /ovos/* endpoints still work during transition period.

Phase 1 Milestone 1.3 - Backward Compatibility
Created: November 6, 2025
"""

import pytest
import httpx
from datetime import datetime
from uuid import UUID


BASE_URL = "http://localhost:8001/api/v1"


@pytest.mark.asyncio
class TestOldEndpointsStillWork:
    """Verify old /ovos/* endpoints still return correct data."""
    
    async def test_ovos_seus_endpoint_still_works(self):
        """Old /ovos/seus should still return SEU list."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BASE_URL}/ovos/seus")
            assert response.status_code == 200
            data = response.json()
            assert "total_count" in data or "total_seus" in data  # Accept both field names
            assert isinstance(data["seus"], list)
            assert len(data["seus"]) > 0
    
    async def test_ovos_train_baseline_still_works(self):
        """Old /ovos/train-baseline should still train models."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "seu_name": "Compressor-1",
                "energy_source": "electricity",
                "features": [],
                "year": 2025
            }
            response = await client.post(f"{BASE_URL}/ovos/train-baseline", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "r_squared" in data
            assert data["r_squared"] > 0.8  # Good accuracy
    
    async def test_ovos_summary_still_works(self):
        """Old /ovos/summary should still return factory overview."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BASE_URL}/ovos/summary")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "energy" in data
            assert "machines" in data
    
    async def test_ovos_top_consumers_still_works(self):
        """Old /ovos/top-consumers should still return rankings."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{BASE_URL}/ovos/top-consumers?"
                f"metric=energy&limit=5&"
                f"start_time=2025-11-05T00:00:00Z&end_time=2025-11-06T23:59:59Z"
            )
            assert response.status_code == 200
            data = response.json()
            assert "ranking" in data or "top_consumers" in data  # Accept either field name
            rankings = data.get("ranking") or data.get("top_consumers")
            assert isinstance(rankings, list)
    
    async def test_ovos_forecast_tomorrow_still_works(self):
        """Old /ovos/forecast/tomorrow should still return forecast."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BASE_URL}/ovos/forecast/tomorrow")
            assert response.status_code == 200
            data = response.json()
            assert "forecast_type" in data
            assert "total_predicted_energy_kwh" in data or "predicted_energy_kwh" in data
    
    async def test_ovos_machines_status_still_works(self):
        """Old /ovos/machines/{name}/status should still work."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BASE_URL}/ovos/machines/Compressor-1/status")
            assert response.status_code == 200
            data = response.json()
            assert "machine_name" in data
            assert "current_status" in data
            assert "today_stats" in data


@pytest.mark.asyncio
class TestNewEndpointsWorkToo:
    """Verify new endpoints return same/better data."""
    
    async def test_new_seus_endpoint_works(self):
        """New /seus should return same data as old /ovos/seus."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BASE_URL}/seus")
            assert response.status_code == 200
            data = response.json()
            assert "total_count" in data or "total_seus" in data  # Accept both field names
            assert isinstance(data["seus"], list)
    
    async def test_new_factory_summary_works(self):
        """New /factory/summary should return same data as old /ovos/summary."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BASE_URL}/factory/summary")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "energy" in data
    
    async def test_new_analytics_top_consumers_works(self):
        """New /analytics/top-consumers should work like old endpoint."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{BASE_URL}/analytics/top-consumers?"
                f"metric=energy&limit=5&"
                f"start_time=2025-11-05T00:00:00Z&end_time=2025-11-06T23:59:59Z"
            )
            assert response.status_code == 200
            data = response.json()
            assert "ranking" in data or "top_consumers" in data  # Accept either field name
    
    async def test_new_baseline_train_seu_works(self):
        """New /baseline/train-seu should work like old /ovos/train-baseline."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "seu_name": "Compressor-1",
                "energy_source": "electricity",
                "features": [],
                "year": 2025
            }
            response = await client.post(f"{BASE_URL}/baseline/train-seu", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "r_squared" in data
    
    async def test_new_forecast_short_term_works(self):
        """New /forecast/short-term should work like old /ovos/forecast/tomorrow."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BASE_URL}/forecast/short-term")
            assert response.status_code == 200
            data = response.json()
            assert "forecast_type" in data
            assert "total_predicted_energy_kwh" in data or "predicted_energy_kwh" in data
    
    async def test_new_machines_status_works(self):
        """New /machines/status/{name} should work like old endpoint."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{BASE_URL}/machines/status/Compressor-1")
            assert response.status_code == 200
            data = response.json()
            assert "machine_name" in data
            assert "current_status" in data


@pytest.mark.asyncio
class TestDataConsistency:
    """Ensure old and new endpoints return consistent data."""
    
    async def test_seus_list_consistency(self):
        """Old and new SEU endpoints should return same count."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            old_response = await client.get(f"{BASE_URL}/ovos/seus")
            new_response = await client.get(f"{BASE_URL}/seus")
            
            assert old_response.status_code == 200
            assert new_response.status_code == 200
            
            old_data = old_response.json()
            new_data = new_response.json()
            
            # Should return same number of SEUs (accept either field name)
            old_count = old_data.get("total_seus") or old_data.get("total_count")
            new_count = new_data.get("total_seus") or new_data.get("total_count")
            assert old_count == new_count
    
    async def test_factory_summary_consistency(self):
        """Old and new factory summary should return same data."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            old_response = await client.get(f"{BASE_URL}/ovos/summary")
            new_response = await client.get(f"{BASE_URL}/factory/summary")
            
            assert old_response.status_code == 200
            assert new_response.status_code == 200
            
            old_data = old_response.json()
            new_data = new_response.json()
            
            # Should have same status
            assert old_data["status"] == new_data["status"]
    
    async def test_top_consumers_consistency(self):
        """Old and new top consumers should return same rankings."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            time_params = "start_time=2025-11-05T00:00:00Z&end_time=2025-11-06T23:59:59Z"
            old_response = await client.get(f"{BASE_URL}/ovos/top-consumers?metric=energy&limit=5&{time_params}")
            new_response = await client.get(f"{BASE_URL}/analytics/top-consumers?metric=energy&limit=5&{time_params}")
            
            assert old_response.status_code == 200
            assert new_response.status_code == 200
            
            old_data = old_response.json()
            new_data = new_response.json()
            
            # Get rankings (accept either field name)
            old_ranking = old_data.get("ranking") or old_data.get("top_consumers")
            new_ranking = new_data.get("ranking") or new_data.get("top_consumers")
            
            # Should have same number of consumers
            assert len(old_ranking) == len(new_ranking)
            
            # Top consumer should be same
            if len(old_ranking) > 0:
                old_top = old_ranking[0].get("machine_name") or old_ranking[0].get("machine_id")
                new_top = new_ranking[0].get("machine_name") or new_ranking[0].get("machine_id")
                assert old_top == new_top


@pytest.mark.asyncio
class TestMigrationPath:
    """Test that migration from old to new endpoints is smooth."""
    
    async def test_can_switch_from_old_to_new_seus(self):
        """Client can switch from /ovos/seus to /seus without code changes."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Old way
            old_response = await client.get(f"{BASE_URL}/ovos/seus")
            old_seus = old_response.json()["seus"]
            
            # New way
            new_response = await client.get(f"{BASE_URL}/seus")
            new_seus = new_response.json()["seus"]
            
            # Core fields should be present in both (allow new fields in new endpoint)
            core_fields = {'id', 'name', 'energy_source', 'unit', 'machine_count', 'baseline_year', 'r_squared'}
            assert core_fields.issubset(old_seus[0].keys())
            assert core_fields.issubset(new_seus[0].keys())
    
    async def test_can_switch_from_old_to_new_training(self):
        """Training API is backward compatible."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "seu_name": "Compressor-1",
                "energy_source": "electricity",
                "features": [],
                "year": 2025
            }
            
            # Old way
            old_response = await client.post(f"{BASE_URL}/ovos/train-baseline", json=payload)
            old_data = old_response.json()
            
            # New way
            new_response = await client.post(f"{BASE_URL}/baseline/train-seu", json=payload)
            new_data = new_response.json()
            
            # Same response structure
            assert old_data.keys() == new_data.keys()
            assert old_data["success"] == new_data["success"]


@pytest.mark.asyncio
class TestErrorHandling:
    """Ensure error responses are consistent between old and new."""
    
    async def test_old_endpoint_invalid_seu_error(self):
        """Old endpoint should return error message for invalid SEU."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "seu_name": "InvalidMachine-999",
                "energy_source": "electricity",
                "features": [],
                "year": 2025
            }
            response = await client.post(f"{BASE_URL}/ovos/train-baseline", json=payload)
            # EnMS returns 200 with success: false (not HTTP error codes)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert "message" in data or "error" in data
    
    async def test_new_endpoint_invalid_seu_error(self):
        """New endpoint should return same error format."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "seu_name": "InvalidMachine-999",
                "energy_source": "electricity",
                "features": [],
                "year": 2025
            }
            response = await client.post(f"{BASE_URL}/baseline/train-seu", json=payload)
            # Should return same format as old endpoint
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert "message" in data or "error" in data


# Test Summary
# ============
# - TestOldEndpointsStillWork: 6 tests (verify old /ovos/* work)
# - TestNewEndpointsWorkToo: 6 tests (verify new endpoints work)
# - TestDataConsistency: 3 tests (old and new return same data)
# - TestMigrationPath: 2 tests (smooth transition)
# - TestErrorHandling: 2 tests (consistent error handling)
# Total: 19 new backward compatibility tests
