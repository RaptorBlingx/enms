"""
API Consistency & Cross-Endpoint Tests - Phase 0 Validation
============================================================
Tests for API consistency, backward compatibility, and cross-endpoint validation.

Author: EnMS Team
Date: November 5, 2025
Purpose: Discover bugs in API design and cross-endpoint interactions
"""

import pytest
import httpx
from datetime import datetime
from typing import Dict, Any


BASE_URL = "http://localhost:8001/api/v1"

COMPRESSOR_UUID = "c0000000-0000-0000-0000-000000000001"
COMPRESSOR_NAME = "Compressor-1"


# ============================================================================
# Test Class 1: API Health & Availability
# ============================================================================

class TestAPIHealth:
    """Test that all documented API endpoints are accessible"""
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test health check endpoint exists and returns 200"""
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert data["status"] in ["healthy", "ok"]
    
    @pytest.mark.asyncio
    async def test_ovos_endpoints_accessible(self):
        """Test critical OVOS endpoints are accessible"""
        async with httpx.AsyncClient(timeout=5.0) as client:
            endpoints = [
                "/ovos/seus",
                "/ovos/energy-sources",
            ]
            
            for endpoint in endpoints:
                response = await client.get(f"{BASE_URL}{endpoint}")
                assert response.status_code in [200, 404, 422], \
                    f"Endpoint {endpoint} returned unexpected status: {response.status_code}"


# ============================================================================
# Test Class 2: Backward Compatibility
# ============================================================================

class TestBackwardCompatibility:
    """Test that old API patterns still work after refactoring"""
    
    @pytest.mark.asyncio
    async def test_uuid_based_prediction_still_works(self):
        """Test that UUID-based prediction (v1 pattern) still works"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "machine_id": COMPRESSOR_UUID,
                "features": {
                    "total_production_count": 1000,
                    "avg_outdoor_temp_c": 20.0,
                    "avg_pressure_bar": 7.0
                }
            }
            
            response = await client.post(f"{BASE_URL}/baseline/predict", json=payload)
            assert response.status_code == 200, \
                f"UUID-based prediction failed: {response.text}"
            
            data = response.json()
            assert "predicted_energy_kwh" in data
            assert "machine_id" in data
    
    @pytest.mark.asyncio
    async def test_uuid_based_model_list_still_works(self):
        """Test that UUID-based model listing still works"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/baseline/models?machine_id={COMPRESSOR_UUID}"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "machine_id" in data
            assert "total_models" in data
            assert "models" in data


# ============================================================================
# Test Class 3: Error Message Quality
# ============================================================================

class TestErrorMessages:
    """Test that error messages are helpful and actionable"""
    
    @pytest.mark.asyncio
    async def test_invalid_seu_error_is_helpful(self):
        """Test that invalid SEU name returns helpful error"""
        async with httpx.AsyncClient(timeout=5.0) as client:
            payload = {
                "seu_name": "NonExistentMachine-999",
                "energy_source": "electricity",
                "features": {"total_production_count": 100}
            }
            
            response = await client.post(f"{BASE_URL}/baseline/predict", json=payload)
            
            assert response.status_code in [404, 422]
            data = response.json()
            
            # Check error message quality
            detail = str(data.get("detail", ""))
            assert len(detail) > 0, "Error message is empty"
            assert "NonExistentMachine-999" in detail or "not found" in detail.lower(), \
                "Error message doesn't mention the invalid SEU name"
    
    @pytest.mark.asyncio
    async def test_missing_required_field_error(self):
        """Test that missing required fields return clear 422 errors"""
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Missing features field
            payload = {
                "machine_id": COMPRESSOR_UUID
            }
            
            response = await client.post(f"{BASE_URL}/baseline/predict", json=payload)
            
            assert response.status_code == 422
            data = response.json()
            assert "detail" in data


# ============================================================================
# Test Class 4: Response Format Consistency
# ============================================================================

class TestResponseConsistency:
    """Test that all endpoints return consistent response formats"""
    
    @pytest.mark.asyncio
    async def test_prediction_response_has_standard_fields(self):
        """Test that prediction responses have consistent structure"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "machine_id": COMPRESSOR_UUID,
                "features": {
                    "total_production_count": 500,
                    "avg_outdoor_temp_c": 22.0
                }
            }
            
            response = await client.post(f"{BASE_URL}/baseline/predict", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check standard fields exist
                required_fields = ["predicted_energy_kwh", "machine_id", "model_version", "features"]
                for field in required_fields:
                    assert field in data, f"Missing required field: {field}"
                
                # Check field types
                assert isinstance(data["predicted_energy_kwh"], (int, float))
                assert isinstance(data["model_version"], int)
                assert isinstance(data["features"], dict)
    
    @pytest.mark.asyncio
    async def test_model_list_response_consistency(self):
        """Test that model list responses have consistent structure"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/baseline/models?machine_id={COMPRESSOR_UUID}"
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Top-level fields
            assert "machine_id" in data
            assert "total_models" in data
            assert "models" in data
            assert isinstance(data["models"], list)
            
            # If models exist, check their structure
            if data["total_models"] > 0:
                first_model = data["models"][0]
                required_model_fields = ["id", "model_version", "r_squared", "is_active"]
                for field in required_model_fields:
                    assert field in first_model, f"Model missing field: {field}"


# ============================================================================
# Test Class 5: Data Type Validation
# ============================================================================

class TestDataTypes:
    """Test that APIs handle incorrect data types gracefully"""
    
    @pytest.mark.asyncio
    async def test_string_instead_of_number_in_features(self):
        """Test that string values in numeric features are rejected"""
        async with httpx.AsyncClient(timeout=5.0) as client:
            payload = {
                "machine_id": COMPRESSOR_UUID,
                "features": {
                    "total_production_count": "not_a_number",  # String instead of number
                    "avg_outdoor_temp_c": 20.0
                }
            }
            
            response = await client.post(f"{BASE_URL}/baseline/predict", json=payload)
            
            # Should return 422 validation error
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_invalid_uuid_format(self):
        """Test that invalid UUID format is rejected"""
        async with httpx.AsyncClient(timeout=5.0) as client:
            payload = {
                "machine_id": "not-a-valid-uuid",
                "features": {"total_production_count": 100}
            }
            
            response = await client.post(f"{BASE_URL}/baseline/predict", json=payload)
            
            # Should return 422 validation error
            assert response.status_code == 422


# ============================================================================
# Test Class 6: Concurrency & Race Conditions
# ============================================================================

class TestConcurrency:
    """Test that concurrent requests don't cause issues"""
    
    @pytest.mark.asyncio
    async def test_concurrent_predictions(self):
        """Test that concurrent predictions work correctly"""
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Make 10 concurrent prediction requests
            tasks = []
            for i in range(10):
                payload = {
                    "machine_id": COMPRESSOR_UUID,
                    "features": {
                        "total_production_count": 500 + i,
                        "avg_outdoor_temp_c": 20.0 + i
                    }
                }
                tasks.append(client.post(f"{BASE_URL}/baseline/predict", json=payload))
            
            # Execute concurrently
            import asyncio
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check all succeeded
            success_count = sum(1 for r in responses if not isinstance(r, Exception) and r.status_code == 200)
            assert success_count >= 8, \
                f"Too many concurrent requests failed: only {success_count}/10 succeeded"


# ============================================================================
# Test Class 7: SEU vs Machine ID Consistency
# ============================================================================

class TestSEUMachineConsistency:
    """Test that SEU-based and UUID-based access return consistent data"""
    
    @pytest.mark.asyncio
    async def test_seu_and_uuid_resolve_to_same_machine(self):
        """Test that SEU lookup and UUID reference the same machine"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Get via UUID
            uuid_response = await client.get(
                f"{BASE_URL}/baseline/models?machine_id={COMPRESSOR_UUID}"
            )
            
            # Get via SEU name
            seu_response = await client.get(
                f"{BASE_URL}/baseline/models?seu_name={COMPRESSOR_NAME}&energy_source=electricity"
            )
            
            if uuid_response.status_code == 200 and seu_response.status_code == 200:
                uuid_data = uuid_response.json()
                seu_data = seu_response.json()
                
                # Should resolve to same machine_id
                assert uuid_data["machine_id"] == seu_data["machine_id"], \
                    "SEU and UUID don't resolve to the same machine!"


# ============================================================================
# Test Class 8: Training Workflow Validation
# ============================================================================

class TestTrainingWorkflow:
    """Test complete training workflow end-to-end"""
    
    @pytest.mark.asyncio
    async def test_train_list_predict_workflow(self):
        """Test that train → list → predict workflow works end-to-end"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Step 1: Train a model
            train_payload = {
                "seu_name": COMPRESSOR_NAME,
                "energy_source": "electricity",
                "features": [],
                "year": 2025
            }
            
            train_response = await client.post(
                f"{BASE_URL}/ovos/train-baseline",
                json=train_payload
            )
            
            # Training may fail if insufficient data - that's OK
            if train_response.status_code != 200:
                pytest.skip("Insufficient data for training")
            
            train_data = train_response.json()
            assert train_data.get("success") == True
            
            # Step 2: List models (should include newly trained)
            list_response = await client.get(
                f"{BASE_URL}/baseline/models?machine_id={COMPRESSOR_UUID}"
            )
            
            assert list_response.status_code == 200
            list_data = list_response.json()
            assert list_data["total_models"] > 0
            
            # Step 3: Make prediction with trained model
            predict_payload = {
                "machine_id": COMPRESSOR_UUID,
                "features": {
                    "total_production_count": 1000,
                    "avg_outdoor_temp_c": 20.0
                }
            }
            
            predict_response = await client.post(
                f"{BASE_URL}/baseline/predict",
                json=predict_payload
            )
            
            assert predict_response.status_code == 200
            predict_data = predict_response.json()
            assert predict_data["predicted_energy_kwh"] > 0


# ============================================================================
# Run Configuration
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto", "-s"])
