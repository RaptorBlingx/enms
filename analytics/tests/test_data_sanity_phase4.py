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
            assert data["expected_energy_kwh"] > 0, "Expected energy must be positive"
            assert abs(data["savings_kwh"]) >= 0, "Savings must be valid"
    
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
            expected_savings_usd = abs(data["savings_kwh"]) * 0.15
            actual_savings_usd = abs(data["savings_usd"])
            
            # Allow 1% tolerance for rounding
            tolerance = expected_savings_usd * 0.01
            assert abs(actual_savings_usd - expected_savings_usd) <= tolerance, \
                f"Cost calculation error: expected ${expected_savings_usd:.2f}, got ${actual_savings_usd:.2f}"
    
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
            
            valid_statuses = ["excellent", "on_track", "needs_attention", "at_risk"]
            assert data["iso_status"] in valid_statuses, \
                f"Invalid ISO status: {data['iso_status']}"
    
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
                "actual_energy_kwh", "expected_energy_kwh", "savings_kwh", 
                "savings_usd", "deviation_percent", "iso_status"
            ]
            
            for field in required_fields:
                assert data[field] is not None, f"Field '{field}' is null"
    
    async def test_opportunities_savings_positive(self):
        """All savings opportunities must have positive potential savings"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/performance/opportunities/identify?factory_id=11111111-1111-1111-1111-111111111111"
            )
            
            assert response.status_code == 200
            opportunities = response.json()
            
            for opp in opportunities:
                assert opp["potential_savings_kwh"] > 0, \
                    f"Opportunity {opp['opportunity_id']} has non-positive savings"
    
    async def test_opportunities_priority_valid(self):
        """Priority must be high/medium/low"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/performance/opportunities/identify?factory_id=11111111-1111-1111-1111-111111111111"
            )
            
            assert response.status_code == 200
            opportunities = response.json()
            
            valid_priorities = ["high", "medium", "low"]
            for opp in opportunities:
                assert opp["priority"] in valid_priorities, \
                    f"Invalid priority: {opp['priority']}"


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
            
            assert data["actual_consumption_kwh"] > 0, "Actual consumption must be positive"
            assert data["baseline_consumption_kwh"] > 0, "Baseline consumption must be positive"
    
    async def test_enpi_report_deviation_logical(self):
        """EnPI deviation calculations must be logically consistent"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/iso50001/enpi-report?factory_id=11111111-1111-1111-1111-111111111111&period=2025-Q4"
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # deviation = (actual - baseline) / baseline * 100
            actual = data["actual_consumption_kwh"]
            baseline = data["baseline_consumption_kwh"]
            deviation = data["deviation_percent"]
            
            expected_deviation = ((actual - baseline) / baseline) * 100
            
            # Allow 0.1% tolerance
            assert abs(deviation - expected_deviation) <= 0.1, \
                f"Deviation calculation error: expected {expected_deviation:.2f}%, got {deviation:.2f}%"
    
    async def test_enpi_report_cost_calculation(self):
        """Cost should equal energy × rate"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/iso50001/enpi-report?factory_id=11111111-1111-1111-1111-111111111111&period=2025-Q4"
            )
            
            assert response.status_code == 200
            data = response.json()
            
            expected_cost = data["actual_consumption_kwh"] * 0.15
            
            # Allow 1% tolerance
            tolerance = expected_cost * 0.01
            assert abs(data["total_cost_usd"] - expected_cost) <= tolerance, \
                f"Cost calculation error"
    
    async def test_enpi_report_iso_status_valid(self):
        """ISO status must be valid"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/iso50001/enpi-report?factory_id=11111111-1111-1111-1111-111111111111&period=2025-Q4"
            )
            
            assert response.status_code == 200
            data = response.json()
            
            valid_statuses = ["excellent", "on_track", "needs_attention", "at_risk"]
            assert data["iso_status"] in valid_statuses
    
    async def test_action_plan_roi_calculation(self):
        """Action plan ROI calculations must be correct"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            # First create an action plan
            create_response = await client.post(
                f"{BASE_URL}/api/v1/iso50001/action-plans",
                json={
                    "factory_id": "11111111-1111-1111-1111-111111111111",
                    "title": "Test Action Plan",
                    "description": "Test ROI calculation",
                    "category": "energy_efficiency",
                    "target_kwh_reduction": 1000,
                    "estimated_investment_usd": 500,
                    "target_completion_date": (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")
                }
            )
            
            assert create_response.status_code == 200
            plan_data = create_response.json()
            
            # Verify savings calculation
            expected_savings_usd = 1000 * 0.15  # 1000 kWh × $0.15
            assert abs(plan_data["estimated_annual_savings_usd"] - expected_savings_usd) <= 0.01
            
            # Verify payback period
            expected_payback = (500 / expected_savings_usd) * 12  # months
            assert abs(plan_data["payback_period_months"] - expected_payback) <= 0.01
    
    async def test_action_plan_progress_percent_range(self):
        """Progress percent must be 0-100"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/iso50001/action-plans?factory_id=11111111-1111-1111-1111-111111111111"
            )
            
            assert response.status_code == 200
            plans = response.json()
            
            for plan in plans:
                assert 0 <= plan["progress_percent"] <= 100, \
                    f"Progress {plan['progress_percent']}% out of range"


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
                    "production_units": 100000
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["predicted_energy_kwh"] > 0, "Predicted energy must be positive"
    
    async def test_models_r_squared_range(self):
        """R² must be between 0 and 1"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/baseline/models"
            )
            
            assert response.status_code == 200
            models = response.json()
            
            for model in models:
                r_squared = model["metrics"]["r_squared"]
                assert 0 <= r_squared <= 1, \
                    f"R² {r_squared} out of range for {model['seu_name']}"
    
    async def test_models_error_metrics_positive(self):
        """Error metrics (RMSE, MAE) must be >= 0"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/baseline/models"
            )
            
            assert response.status_code == 200
            models = response.json()
            
            for model in models:
                metrics = model["metrics"]
                assert metrics["rmse"] >= 0, f"RMSE cannot be negative"
                assert metrics["mae"] >= 0, f"MAE cannot be negative"
    
    async def test_models_timestamps_valid(self):
        """Timestamps must be valid ISO 8601 format"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/baseline/models"
            )
            
            assert response.status_code == 200
            models = response.json()
            
            iso8601_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
            
            for model in models:
                assert re.match(iso8601_pattern, model["trained_at"]), \
                    f"Invalid timestamp format: {model['trained_at']}"


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
            
            numeric_fields = ["actual_energy_kwh", "expected_energy_kwh", "savings_kwh", "savings_usd"]
            for field in numeric_fields:
                if field in data:
                    assert data[field] is not None, f"Numeric field '{field}' is null"
                    assert isinstance(data[field], (int, float)), f"Field '{field}' is not numeric"
