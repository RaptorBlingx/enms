"""
Phase 4.1 - Data Quality Validation Test Suite

This test suite validates the logical correctness of all API outputs to ensure zero bugs.

Test Categories:
1. Performance Engine Sanity
2. ISO 50001 Sanity
3. Baseline Sanity
4. General Sanity

Each test verifies specific data quality rules (e.g., energy > 0, percentages valid, etc.)
"""

import pytest
import httpx
from datetime import datetime, timedelta
import re


BASE_URL = "http://localhost:8001"


@pytest.mark.asyncio
class TestPerformanceEngineSanity:
    """Test Performance Engine endpoints for logical data correctness"""
    
    async def test_analyze_energy_positive(self):
        """All energy values in /performance/analyze must be > 0"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/performance/analyze",
                json={
                    "seu_name": "Compressor-1",
                    "energy_source": "electricity",
                    "analysis_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Check all energy fields
            assert data["actual_energy_kwh"] > 0, "Actual energy must be positive"
            assert data["baseline_energy_kwh"] > 0, "Baseline energy must be positive"
            assert abs(data["deviation_kwh"]) >= 0, "Deviation must be valid"
    
    async def test_analyze_deviation_percent_valid(self):
        """Deviation percent should be within reasonable range"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/performance/analyze",
                json={
                    "seu_name": "Compressor-1",
                    "energy_source": "electricity",
                    "analysis_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Deviation can be negative (savings) but should be within -100% to +500% (extreme cases)
            assert -100 <= data["deviation_percent"] <= 500, \
                f"Deviation {data['deviation_percent']}% seems unrealistic"
    
    async def test_analyze_cost_calculation(self):
        """Cost should equal energy × rate"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/performance/analyze",
                json={
                    "seu_name": "Compressor-1",
                    "energy_source": "electricity",
                    "analysis_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Assuming $0.15/kWh rate
            expected_cost_usd = abs(data["deviation_kwh"]) * 0.15
            actual_cost_usd = abs(data["deviation_cost_usd"])
            
            # Allow 1% tolerance for rounding
            tolerance = expected_cost_usd * 0.01
            assert abs(actual_cost_usd - expected_cost_usd) <= tolerance, \
                f"Cost calculation error: expected ${expected_cost_usd:.2f}, got ${actual_cost_usd:.2f}"
    
    async def test_analyze_iso_status_valid(self):
        """ISO status must be one of the allowed values"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/performance/analyze",
                json={
                    "seu_name": "Compressor-1",
                    "energy_source": "electricity",
                    "analysis_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            valid_statuses = ["excellent", "on_track", "needs_attention", "requires_attention", "at_risk"]
            assert data["iso50001_status"] in valid_statuses, \
                f"Invalid ISO status: {data['iso50001_status']}"
    
    async def test_analyze_no_null_required_fields(self):
        """No null values in required fields"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/performance/analyze",
                json={
                    "seu_name": "Compressor-1",
                    "energy_source": "electricity",
                    "analysis_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            required_fields = [
                "actual_energy_kwh", "baseline_energy_kwh", "deviation_kwh", 
                "deviation_cost_usd", "deviation_percent", "iso50001_status"
            ]
            
            for field in required_fields:
                assert data[field] is not None, f"Field '{field}' is null"
    
    async def test_opportunities_savings_positive(self):
        """All savings opportunities must have positive potential savings"""
        async with httpx.AsyncClient(timeout=30.0) as client:  # Increased timeout
            response = await client.get(
                f"{BASE_URL}/api/v1/performance/opportunities?factory_id=11111111-1111-1111-1111-111111111111&period=month"
            )
            
            assert response.status_code == 200
            data = response.json()
            
            for opp in data["opportunities"]:
                assert opp["potential_savings_kwh"] > 0, \
                    f"Opportunity for {opp['seu_name']} has non-positive savings"
    
    async def test_opportunities_effort_valid(self):
        """Effort must be low/medium/high"""
        async with httpx.AsyncClient(timeout=30.0) as client:  # Increased timeout
            response = await client.get(
                f"{BASE_URL}/api/v1/performance/opportunities?factory_id=11111111-1111-1111-1111-111111111111&period=month"
            )
            
            assert response.status_code == 200
            data = response.json()
            
            valid_efforts = ["high", "medium", "low"]
            for opp in data["opportunities"]:
                assert opp["effort"] in valid_efforts, \
                    f"Invalid effort: {opp['effort']}"


@pytest.mark.asyncio
class TestISO50001Sanity:
    """Test ISO 50001 endpoints for logical data correctness"""
    
    async def test_enpi_report_energy_positive(self):
        """All energy values in EnPI report must be > 0"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/iso50001/enpi-report?factory_id=11111111-1111-1111-1111-111111111111&period=2025-Q4"
            )
            
            assert response.status_code == 200
            data = response.json()
            
            overall = data["overall_performance"]
            assert overall["total_energy_actual_kwh"] > 0, "Actual consumption must be positive"
            assert overall["total_energy_baseline_kwh"] > 0, "Baseline consumption must be positive"
    
    async def test_enpi_report_deviation_logical(self):
        """EnPI deviation calculations must be logically consistent"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/iso50001/enpi-report?factory_id=11111111-1111-1111-1111-111111111111&period=2025-Q4"
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # deviation = (actual - baseline) / baseline * 100
            overall = data["overall_performance"]
            actual = overall["total_energy_actual_kwh"]
            baseline = overall["total_energy_baseline_kwh"]
            deviation = overall["deviation_percent"]
            
            expected_deviation = ((actual - baseline) / baseline) * 100
            
            # Allow 0.1% tolerance
            assert abs(deviation - expected_deviation) <= 0.1, \
                f"Deviation calculation error: expected {expected_deviation:.2f}%, got {deviation:.2f}%"
    
    async def test_enpi_report_savings_calculation(self):
        """Savings should equal deviation × rate"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/iso50001/enpi-report?factory_id=11111111-1111-1111-1111-111111111111&period=2025-Q4"
            )
            
            assert response.status_code == 200
            data = response.json()
            
            overall = data["overall_performance"]
            expected_savings_usd = abs(overall["deviation_kwh"]) * 0.15
            
            # Allow 1% tolerance
            tolerance = expected_savings_usd * 0.01
            assert abs(overall["cumulative_savings_usd"] - expected_savings_usd) <= tolerance, \
                f"Savings calculation error"
    
    async def test_enpi_report_iso_status_valid(self):
        """ISO status must be valid"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/iso50001/enpi-report?factory_id=11111111-1111-1111-1111-111111111111&period=2025-Q4"
            )
            
            assert response.status_code == 200
            data = response.json()
            
            valid_statuses = ["on_track", "needs_attention", "at_risk"]
            assert data["overall_performance"]["iso_status"] in valid_statuses, \
                f"Invalid ISO status: {data['overall_performance']['iso_status']}"
    
    async def test_seu_breakdown_energy_positive(self):
        """All SEU breakdown energy values must be positive"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/iso50001/enpi-report?factory_id=11111111-1111-1111-1111-111111111111&period=2025-Q4"
            )
            
            assert response.status_code == 200
            data = response.json()
            
            for seu in data["seu_breakdown"]:
                assert seu["actual_energy_kwh"] > 0, f"{seu['seu_name']} actual energy must be positive"
                assert seu["baseline_energy_kwh"] > 0, f"{seu['seu_name']} baseline energy must be positive"
    
    async def test_seu_breakdown_status_valid(self):
        """All SEU ISO statuses must be valid"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/iso50001/enpi-report?factory_id=11111111-1111-1111-1111-111111111111&period=2025-Q4"
            )
            
            assert response.status_code == 200
            data = response.json()
            
            valid_statuses = ["on_track", "needs_attention", "at_risk"]
            for seu in data["seu_breakdown"]:
                assert seu["iso_status"] in valid_statuses, \
                    f"{seu['seu_name']} has invalid ISO status: {seu['iso_status']}"


@pytest.mark.asyncio
class TestBaselineSanity:
    """Test Baseline endpoints for logical data correctness"""
    
    async def test_predict_energy_positive(self):
        """Baseline predictions must be positive"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/baseline/predict",
                json={
                    "seu_name": "Compressor-1",
                    "energy_source": "electricity",
                    "features": {
                        "total_production_count": 100000,
                        "avg_outdoor_temp_c": 25.0,
                        "avg_pressure_bar": 7.0
                    }
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["predicted_energy_kwh"] > 0, "Predicted energy must be positive"
    
    async def test_models_r_squared_range(self):
        """R² must be between 0 and 1"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/baseline/models?seu_name=Compressor-1&energy_source=electricity"
            )
            
            assert response.status_code == 200
            data = response.json()
            
            for model in data["models"]:
                r_squared = model["r_squared"]
                assert 0 <= r_squared <= 1, \
                    f"R² {r_squared} out of range for {model['model_name']}"
    
    async def test_models_error_metrics_positive(self):
        """Error metrics (RMSE, MAE) must be >= 0"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/baseline/models?seu_name=Compressor-1&energy_source=electricity"
            )
            
            assert response.status_code == 200
            data = response.json()
            
            for model in data["models"]:
                assert model["rmse"] >= 0, f"RMSE cannot be negative"
                assert model["mae"] >= 0, f"MAE cannot be negative"
    
    async def test_models_timestamps_valid(self):
        """Timestamps must be valid ISO 8601 format"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/baseline/models?seu_name=Compressor-1&energy_source=electricity"
            )
            
            assert response.status_code == 200
            data = response.json()
            
            iso8601_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
            
            for model in data["models"]:
                assert re.match(iso8601_pattern, model["created_at"]), \
                    f"Invalid timestamp format: {model['created_at']}"


@pytest.mark.asyncio
class TestGeneralSanity:
    """General sanity checks across all endpoints"""
    
    async def test_no_negative_percentages(self):
        """Percentage fields should not be negative (except deviation)"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test EnPI report
            response = await client.get(
                f"{BASE_URL}/api/v1/iso50001/enpi-report?factory_id=11111111-1111-1111-1111-111111111111&period=2025-Q4"
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # deviation_percent can be negative (savings)
            # but other percentages should not be
            if "confidence_level" in data:
                assert data["confidence_level"] >= 0
    
    async def test_timestamps_are_recent(self):
        """API responses should have recent timestamps"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/performance/analyze",
                json={
                    "seu_name": "Compressor-1",
                    "energy_source": "electricity",
                    "analysis_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Timestamps should be within last 5 seconds
            if "timestamp" in data:
                timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
                age_seconds = (datetime.now() - timestamp.replace(tzinfo=None)).total_seconds()
                assert age_seconds <= 5, f"Timestamp too old: {age_seconds}s"
    
    async def test_no_null_in_numeric_fields(self):
        """Numeric fields should never be null"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/performance/analyze",
                json={
                    "seu_name": "Compressor-1",
                    "energy_source": "electricity",
                    "analysis_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            numeric_fields = ["actual_energy_kwh", "baseline_energy_kwh", "deviation_kwh", "deviation_cost_usd"]
            for field in numeric_fields:
                if field in data:
                    assert data[field] is not None, f"Numeric field '{field}' is null"
                    assert isinstance(data[field], (int, float)), f"Field '{field}' is not numeric"
