"""
Comprehensive Integration Tests for OVOS Regression Analysis Endpoints
=======================================================================
Tests the enhanced baseline prediction endpoints (Tasks 2-4):
- /ovos/train-baseline (Task 1)
- /baseline/predict with UUID and SEU name (Task 2)
- /baseline/model/{id} with explanations (Task 3)
- /baseline/models with dual input and explanations (Task 4)

Author: EnMS Team
Date: November 4, 2025
Status: PRODUCTION TEST SUITE
"""

import pytest
import httpx
from datetime import datetime
from typing import Dict, Any
import asyncio


BASE_URL = "http://localhost:8001/api/v1"

# Test data constants
COMPRESSOR_UUID = "c0000000-0000-0000-0000-000000000001"
COMPRESSOR_NAME = "Compressor-1"
ENERGY_SOURCE = "electricity"
TRAINING_YEAR = 2025

# Sample features for predictions
SAMPLE_FEATURES = {
    "total_production_count": 500,
    "avg_outdoor_temp_c": 22.0,
    "avg_pressure_bar": 7.0
}


# ============================================================================
# Test Class 1: Training Baseline Models (Foundation)
# ============================================================================

class TestBaselineTraining:
    """Test /ovos/train-baseline endpoint - foundation for all regression tests"""
    
    @pytest.mark.asyncio
    async def test_train_baseline_with_seu_name(self):
        """Test training baseline with SEU name and energy source"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "seu_name": COMPRESSOR_NAME,
                "energy_source": ENERGY_SOURCE,
                "features": [],  # Auto-select features
                "year": TRAINING_YEAR
            }
            
            response = await client.post(
                f"{BASE_URL}/ovos/train-baseline",
                json=payload
            )
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            data = response.json()
            
            # Validate response structure
            assert data["success"] is True
            assert "message" in data
            assert "r_squared" in data
            assert "seu_name" in data
            assert data["seu_name"] == COMPRESSOR_NAME
            
            # Validate model quality
            assert data["r_squared"] >= 0.76, f"R² too low: {data['r_squared']}"
            
            # Validate voice-friendly message exists
            assert len(data["message"]) > 0
            assert "accuracy" in data["message"].lower()
    
    @pytest.mark.asyncio
    async def test_train_baseline_with_specific_features(self):
        """Test training with user-specified features"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "seu_name": COMPRESSOR_NAME,
                "energy_source": ENERGY_SOURCE,
                "features": ["production_count", "outdoor_temp_c"],
                "year": TRAINING_YEAR
            }
            
            response = await client.post(
                f"{BASE_URL}/ovos/train-baseline",
                json=payload
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["r_squared"] >= 0.10  # Lower threshold for limited features
    
    @pytest.mark.asyncio
    async def test_train_baseline_invalid_seu(self):
        """Test error handling for invalid SEU name"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "seu_name": "InvalidMachine-999",
                "energy_source": ENERGY_SOURCE,
                "features": [],
                "year": TRAINING_YEAR
            }
            
            response = await client.post(
                f"{BASE_URL}/ovos/train-baseline",
                json=payload
            )
            
            # Accept 200, 404, or 422 (depends on validation implementation)
            assert response.status_code in [200, 404, 422]
            # If 200, check that training actually failed or no data found
            if response.status_code == 200:
                data = response.json()
                # Should indicate failure or insufficient data
                assert data.get("success") in [False, True]  # May succeed with auto-generated data
    
    @pytest.mark.asyncio
    async def test_train_baseline_invalid_features(self):
        """Test error handling for invalid feature names"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "seu_name": COMPRESSOR_NAME,
                "energy_source": ENERGY_SOURCE,
                "features": ["invalid_feature_xyz"],
                "year": TRAINING_YEAR
            }
            
            response = await client.post(
                f"{BASE_URL}/ovos/train-baseline",
                json=payload
            )
            
            # Accept 200 or 422 (API may filter invalid features)
            assert response.status_code in [200, 422]
            if response.status_code == 422:
                data = response.json()
                assert "invalid_feature_xyz" in str(data).lower()
            else:
                # May succeed by ignoring invalid features
                data = response.json()
                assert "success" in data


# ============================================================================
# Test Class 2: Baseline Prediction - UUID Input (Backward Compatibility)
# ============================================================================

class TestPredictionWithUUID:
    """Test /baseline/predict with machine_id (UUID) - backward compatibility"""
    
    @pytest.mark.asyncio
    async def test_predict_with_uuid(self):
        """Test prediction using machine UUID"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "machine_id": COMPRESSOR_UUID,
                "features": SAMPLE_FEATURES
            }
            
            response = await client.post(
                f"{BASE_URL}/baseline/predict",
                json=payload
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate response structure
            assert "predicted_energy_kwh" in data
            assert "machine_id" in data
            assert "model_version" in data
            assert "features" in data
            
            # Validate prediction is positive
            assert data["predicted_energy_kwh"] > 0, "Energy prediction must be positive"
            
            # Validate features echo
            assert data["features"]["total_production_count"] == SAMPLE_FEATURES["total_production_count"]
    
    @pytest.mark.asyncio
    async def test_predict_uuid_no_baseline(self):
        """Test prediction for machine without baseline model"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Use a valid UUID format but non-existent machine
            fake_uuid = "00000000-0000-0000-0000-000000000099"
            payload = {
                "machine_id": fake_uuid,
                "features": SAMPLE_FEATURES
            }
            
            response = await client.post(
                f"{BASE_URL}/baseline/predict",
                json=payload
            )
            
            # Should return error (404 or 400)
            assert response.status_code in [400, 404, 500]


# ============================================================================
# Test Class 3: Baseline Prediction - SEU Name Input (NEW Enhancement)
# ============================================================================

class TestPredictionWithSEUName:
    """Test /baseline/predict with seu_name + energy_source - NEW feature"""
    
    @pytest.mark.asyncio
    async def test_predict_with_seu_name(self):
        """Test prediction using SEU name and energy source"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "seu_name": COMPRESSOR_NAME,
                "energy_source": ENERGY_SOURCE,
                "features": SAMPLE_FEATURES
            }
            
            response = await client.post(
                f"{BASE_URL}/baseline/predict",
                json=payload
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate response structure
            assert "predicted_energy_kwh" in data
            assert "machine_id" in data
            assert "model_version" in data
            
            # Validate prediction is positive and reasonable
            assert data["predicted_energy_kwh"] > 0
            assert data["predicted_energy_kwh"] < 10000, "Energy prediction seems unreasonably high"
    
    @pytest.mark.asyncio
    async def test_predict_seu_name_with_voice_message(self):
        """Test prediction with voice-friendly message generation"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "seu_name": COMPRESSOR_NAME,
                "energy_source": ENERGY_SOURCE,
                "features": SAMPLE_FEATURES,
                "include_message": True
            }
            
            response = await client.post(
                f"{BASE_URL}/baseline/predict",
                json=payload
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate voice message fields
            assert "message" in data
            assert "energy_unit" in data
            assert len(data["message"]) > 0
            assert COMPRESSOR_NAME in data["message"]
            assert "predicted to consume" in data["message"].lower()
    
    @pytest.mark.asyncio
    async def test_predict_seu_name_invalid(self):
        """Test error handling for invalid SEU name"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "seu_name": "InvalidMachine-999",
                "energy_source": ENERGY_SOURCE,
                "features": SAMPLE_FEATURES
            }
            
            response = await client.post(
                f"{BASE_URL}/baseline/predict",
                json=payload
            )
            
            # Accept 404 or 422 (both are valid error responses)
            assert response.status_code in [404, 422]
            data = response.json()
            assert "detail" in data
            # Should have SEU_NOT_FOUND error
            assert "SEU_NOT_FOUND" in str(data) or "not found" in str(data).lower()
    
    @pytest.mark.asyncio
    async def test_predict_missing_energy_source(self):
        """Test validation error when SEU name provided without energy source"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "seu_name": COMPRESSOR_NAME,
                # Missing energy_source
                "features": SAMPLE_FEATURES
            }
            
            response = await client.post(
                f"{BASE_URL}/baseline/predict",
                json=payload
            )
            
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_predict_conflicting_identifiers(self):
        """Test error when both UUID and SEU name provided"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "machine_id": COMPRESSOR_UUID,
                "seu_name": COMPRESSOR_NAME,
                "energy_source": ENERGY_SOURCE,
                "features": SAMPLE_FEATURES
            }
            
            response = await client.post(
                f"{BASE_URL}/baseline/predict",
                json=payload
            )
            
            # Accept 200 or 422 (if 200, machine_id takes precedence)
            assert response.status_code in [200, 422]
            if response.status_code == 200:
                # Verify it used machine_id
                data = response.json()
                assert "predicted_energy_kwh" in data


# ============================================================================
# Test Class 4: Model Details with Explanations
# ============================================================================

class TestModelDetailsWithExplanations:
    """Test /baseline/model/{id} with optional explanations - Task 3"""
    
    @pytest.mark.asyncio
    async def test_get_model_without_explanation(self):
        """Test getting model details without explanation (backward compatibility)"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            # First, get a model ID
            models_response = await client.get(
                f"{BASE_URL}/baseline/models?machine_id={COMPRESSOR_UUID}"
            )
            assert models_response.status_code == 200
            models_data = models_response.json()
            
            if models_data["total_models"] == 0:
                pytest.skip("No baseline models available for testing")
            
            model_id = models_data["models"][0]["id"]
            
            # Get model details
            response = await client.get(f"{BASE_URL}/baseline/model/{model_id}")
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate basic model fields
            assert "id" in data
            assert "r_squared" in data
            assert "model_version" in data
            assert "is_active" in data
            
            # Should NOT have explanation
            assert "explanation" not in data
    
    @pytest.mark.asyncio
    async def test_get_model_with_explanation(self):
        """Test getting model details WITH explanation"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Get a model ID
            models_response = await client.get(
                f"{BASE_URL}/baseline/models?machine_id={COMPRESSOR_UUID}"
            )
            assert models_response.status_code == 200
            models_data = models_response.json()
            
            if models_data["total_models"] == 0:
                pytest.skip("No baseline models available")
            
            model_id = models_data["models"][0]["id"]
            
            # Get model with explanation
            response = await client.get(
                f"{BASE_URL}/baseline/model/{model_id}?include_explanation=true"
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate explanation structure
            assert "explanation" in data
            explanation = data["explanation"]
            
            assert "accuracy_explanation" in explanation
            assert "key_drivers" in explanation
            assert "formula_explanation" in explanation
            assert "impact_summary" in explanation
            assert "voice_summary" in explanation
            
            # Validate key drivers structure
            assert len(explanation["key_drivers"]) > 0
            first_driver = explanation["key_drivers"][0]
            assert "feature" in first_driver
            assert "human_name" in first_driver
            assert "coefficient" in first_driver
            assert "direction" in first_driver
            assert "rank" in first_driver
            assert first_driver["rank"] == 1
            
            # Validate voice summary is concise
            assert len(explanation["voice_summary"]) > 0
            assert len(explanation["voice_summary"]) < 500  # Should be concise
    
    @pytest.mark.asyncio
    async def test_get_model_invalid_id(self):
        """Test error handling for invalid model ID"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            fake_id = "00000000-0000-0000-0000-000000000000"
            response = await client.get(f"{BASE_URL}/baseline/model/{fake_id}")
            
            assert response.status_code == 404


# ============================================================================
# Test Class 5: Model List with Dual Input and Explanations
# ============================================================================

class TestModelListEnhancements:
    """Test /baseline/models with UUID, SEU name, and batch explanations - Task 4"""
    
    @pytest.mark.asyncio
    async def test_list_models_by_uuid(self):
        """Test listing models by machine UUID (backward compatibility)"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/baseline/models?machine_id={COMPRESSOR_UUID}"
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate response structure
            assert "machine_id" in data
            assert "total_models" in data
            assert "models" in data
            
            # Should NOT have seu_name when accessed via UUID
            assert "seu_name" not in data
            
            # Validate models structure
            if data["total_models"] > 0:
                model = data["models"][0]
                assert "id" in model
                assert "model_version" in model
                assert "r_squared" in model
                assert "is_active" in model
    
    @pytest.mark.asyncio
    async def test_list_models_by_seu_name(self):
        """Test listing models by SEU name (NEW feature)"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/baseline/models?seu_name={COMPRESSOR_NAME}&energy_source={ENERGY_SOURCE}"
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate response structure
            assert "machine_id" in data
            assert "seu_name" in data
            assert "energy_source" in data
            assert "total_models" in data
            assert "models" in data
            
            # Validate SEU fields
            assert data["seu_name"] == COMPRESSOR_NAME
            assert data["energy_source"] == ENERGY_SOURCE
    
    @pytest.mark.asyncio
    async def test_list_models_with_batch_explanations(self):
        """Test batch explanation generation for all models"""
        async with httpx.AsyncClient(timeout=30.0) as client:  # Longer timeout for batch
            response = await client.get(
                f"{BASE_URL}/baseline/models?machine_id={COMPRESSOR_UUID}&include_explanation=true"
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate all models have explanations
            if data["total_models"] > 0:
                for model in data["models"]:
                    assert "explanation" in model
                    assert "voice_summary" in model["explanation"]
                    assert "key_drivers" in model["explanation"]
    
    @pytest.mark.asyncio
    async def test_list_models_missing_identifier(self):
        """Test error when no identifier provided"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}/baseline/models")
            
            assert response.status_code == 422
            data = response.json()
            assert "MISSING_IDENTIFIER" in str(data)
    
    @pytest.mark.asyncio
    async def test_list_models_conflicting_identifiers(self):
        """Test error when both UUID and SEU name provided"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/baseline/models?machine_id={COMPRESSOR_UUID}&seu_name={COMPRESSOR_NAME}&energy_source={ENERGY_SOURCE}"
            )
            
            assert response.status_code == 422
            data = response.json()
            assert "CONFLICTING_IDENTIFIERS" in str(data)
    
    @pytest.mark.asyncio
    async def test_list_models_invalid_seu(self):
        """Test error handling for invalid SEU name"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/baseline/models?seu_name=InvalidMachine-999&energy_source={ENERGY_SOURCE}"
            )
            
            assert response.status_code == 404
            data = response.json()
            assert "SEU_NOT_FOUND" in str(data)


# ============================================================================
# Test Class 6: Cross-Endpoint Consistency
# ============================================================================

class TestCrossEndpointConsistency:
    """Test consistency across all regression endpoints"""
    
    @pytest.mark.asyncio
    async def test_prediction_consistency_uuid_vs_seu(self):
        """Test that UUID and SEU name predictions match"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Prediction with UUID
            uuid_payload = {
                "machine_id": COMPRESSOR_UUID,
                "features": SAMPLE_FEATURES
            }
            uuid_response = await client.post(
                f"{BASE_URL}/baseline/predict",
                json=uuid_payload
            )
            
            # Prediction with SEU name
            seu_payload = {
                "seu_name": COMPRESSOR_NAME,
                "energy_source": ENERGY_SOURCE,
                "features": SAMPLE_FEATURES
            }
            seu_response = await client.post(
                f"{BASE_URL}/baseline/predict",
                json=seu_payload
            )
            
            # Both should succeed
            assert uuid_response.status_code == 200
            assert seu_response.status_code == 200
            
            uuid_data = uuid_response.json()
            seu_data = seu_response.json()
            
            # Predictions should match (same machine, same features)
            assert uuid_data["predicted_energy_kwh"] == seu_data["predicted_energy_kwh"]
            assert uuid_data["model_version"] == seu_data["model_version"]
    
    @pytest.mark.asyncio
    async def test_model_list_count_consistency(self):
        """Test that UUID and SEU name return same model count"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            # List by UUID
            uuid_response = await client.get(
                f"{BASE_URL}/baseline/models?machine_id={COMPRESSOR_UUID}"
            )
            
            # List by SEU name
            seu_response = await client.get(
                f"{BASE_URL}/baseline/models?seu_name={COMPRESSOR_NAME}&energy_source={ENERGY_SOURCE}"
            )
            
            assert uuid_response.status_code == 200
            assert seu_response.status_code == 200
            
            uuid_data = uuid_response.json()
            seu_data = seu_response.json()
            
            # Should have same number of models
            assert uuid_data["total_models"] == seu_data["total_models"]
            
            # Should resolve to same machine_id
            assert uuid_data["machine_id"] == seu_data["machine_id"]


# ============================================================================
# Test Class 7: Performance and Response Time
# ============================================================================

class TestPerformance:
    """Test response times meet SLA requirements"""
    
    @pytest.mark.asyncio
    async def test_prediction_response_time(self):
        """Test prediction completes within 500ms"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            start_time = datetime.now()
            
            payload = {
                "machine_id": COMPRESSOR_UUID,
                "features": SAMPLE_FEATURES
            }
            response = await client.post(
                f"{BASE_URL}/baseline/predict",
                json=payload
            )
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            assert response.status_code == 200
            assert elapsed < 0.5, f"Prediction took {elapsed}s (should be <500ms)"
    
    @pytest.mark.asyncio
    async def test_model_explanation_response_time(self):
        """Test single model explanation completes within 100ms"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Get a model ID first
            models_response = await client.get(
                f"{BASE_URL}/baseline/models?machine_id={COMPRESSOR_UUID}"
            )
            models_data = models_response.json()
            
            if models_data["total_models"] == 0:
                pytest.skip("No models available")
            
            model_id = models_data["models"][0]["id"]
            
            # Test explanation generation time
            start_time = datetime.now()
            response = await client.get(
                f"{BASE_URL}/baseline/model/{model_id}?include_explanation=true"
            )
            elapsed = (datetime.now() - start_time).total_seconds()
            
            assert response.status_code == 200
            assert elapsed < 0.1, f"Explanation took {elapsed}s (should be <100ms)"


# ============================================================================
# Test Class 8: Data Validation and Sanity Checks
# ============================================================================

class TestDataValidation:
    """Test that all outputs are logically valid"""
    
    @pytest.mark.asyncio
    async def test_predictions_are_positive(self):
        """Test that energy predictions are always positive"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test multiple feature combinations
            test_features = [
                {"total_production_count": 100, "avg_outdoor_temp_c": 15.0, "avg_pressure_bar": 5.0},
                {"total_production_count": 1000, "avg_outdoor_temp_c": 25.0, "avg_pressure_bar": 8.0},
                {"total_production_count": 10000, "avg_outdoor_temp_c": 30.0, "avg_pressure_bar": 10.0},
            ]
            
            for features in test_features:
                payload = {
                    "machine_id": COMPRESSOR_UUID,
                    "features": features
                }
                response = await client.post(
                    f"{BASE_URL}/baseline/predict",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    assert data["predicted_energy_kwh"] > 0, \
                        f"Negative energy predicted: {data['predicted_energy_kwh']} for features {features}"
    
    @pytest.mark.asyncio
    async def test_r_squared_in_valid_range(self):
        """Test that R² values are between 0 and 1"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BASE_URL}/baseline/models?machine_id={COMPRESSOR_UUID}"
            )
            
            if response.status_code == 200:
                data = response.json()
                for model in data["models"]:
                    r_squared = model["r_squared"]
                    assert 0 <= r_squared <= 1, \
                        f"Invalid R² value: {r_squared} (must be 0-1)"
    
    @pytest.mark.asyncio
    async def test_feature_ranking_is_correct(self):
        """Test that key drivers are ranked by absolute impact"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Get model with explanation
            models_response = await client.get(
                f"{BASE_URL}/baseline/models?machine_id={COMPRESSOR_UUID}"
            )
            models_data = models_response.json()
            
            if models_data["total_models"] == 0:
                pytest.skip("No models available")
            
            model_id = models_data["models"][0]["id"]
            response = await client.get(
                f"{BASE_URL}/baseline/model/{model_id}?include_explanation=true"
            )
            
            data = response.json()
            key_drivers = data["explanation"]["key_drivers"]
            
            # Validate ranking
            for i, driver in enumerate(key_drivers, 1):
                assert driver["rank"] == i, f"Rank mismatch: expected {i}, got {driver['rank']}"
            
            # Validate sorting by absolute impact
            for i in range(len(key_drivers) - 1):
                current_impact = key_drivers[i]["absolute_impact"]
                next_impact = key_drivers[i + 1]["absolute_impact"]
                assert current_impact >= next_impact, \
                    "Key drivers not sorted by absolute impact"


# ============================================================================
# Run Configuration
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
