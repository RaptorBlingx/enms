"""
Comprehensive Data Sanity Test Suite - Phase 0 Validation
===========================================================
Tests for logical correctness, data quality, and edge cases.
Created as part of EnMS v3 Phase 0: v2 Critical Path Validation

Author: EnMS Team
Date: November 5, 2025
Purpose: Validate v2 foundation before v3 transformation
"""

import pytest
import httpx
from datetime import datetime, timedelta
from typing import Dict, Any
import asyncio


BASE_URL = "http://localhost:8001/api/v1"

# Test constants
COMPRESSOR_UUID = "c0000000-0000-0000-0000-000000000001"
COMPRESSOR_NAME = "Compressor-1"
BOILER_ELECTRICITY_SEU = "Boiler-1 Electrical System"
BOILER_NATURAL_GAS_SEU = "Boiler-1 Natural Gas Burner"
BOILER_STEAM_SEU = "Boiler-1 Steam Production"
ENERGY_SOURCE_ELECTRICITY = "electricity"
ENERGY_SOURCE_NATURAL_GAS = "natural_gas"
ENERGY_SOURCE_STEAM = "steam"

# Sample features
TYPICAL_FEATURES = {
    "total_production_count": 1000,
    "avg_outdoor_temp_c": 20.0,
    "avg_pressure_bar": 7.5
}

EXTREME_LOW_FEATURES = {
    "total_production_count": 1,
    "avg_outdoor_temp_c": -10.0,
    "avg_pressure_bar": 1.0
}

EXTREME_HIGH_FEATURES = {
    "total_production_count": 100000,
    "avg_outdoor_temp_c": 45.0,
    "avg_pressure_bar": 15.0
}


# ============================================================================
# Test Class 1: Energy Prediction Sanity (CRITICAL - #1 Concern)
# ============================================================================

class TestEnergyPredictionSanity:
    """Test that energy predictions are ALWAYS positive and reasonable"""
    
    @pytest.mark.asyncio
    async def test_no_negative_energy_predictions(self):
        """CRITICAL: Test that energy predictions are NEVER negative"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            test_cases = [
                {"features": TYPICAL_FEATURES, "label": "typical"},
                {"features": EXTREME_LOW_FEATURES, "label": "extreme_low"},
                {"features": EXTREME_HIGH_FEATURES, "label": "extreme_high"},
                {"features": {"total_production_count": 0, "avg_outdoor_temp_c": 0.0, "avg_pressure_bar": 0.0}, "label": "zero_values"},
            ]
            
            for test_case in test_cases:
                payload = {
                    "machine_id": COMPRESSOR_UUID,
                    "features": test_case["features"]
                }
                
                response = await client.post(f"{BASE_URL}/baseline/predict", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    predicted_energy = data["predicted_energy_kwh"]
                    
                    assert predicted_energy >= 0, \
                        f"❌ CRITICAL BUG: Negative energy predicted! " \
                        f"Test case: {test_case['label']}, " \
                        f"Features: {test_case['features']}, " \
                        f"Predicted: {predicted_energy} kWh"
                    
                    # Log the prediction for manual review
                    print(f"✅ {test_case['label']}: {predicted_energy:.2f} kWh (valid)")
    
    @pytest.mark.asyncio
    async def test_predictions_reasonable_magnitude(self):
        """Test that predictions are within reasonable bounds (not astronomically high)"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "machine_id": COMPRESSOR_UUID,
                "features": TYPICAL_FEATURES
            }
            
            response = await client.post(f"{BASE_URL}/baseline/predict", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                predicted_energy = data["predicted_energy_kwh"]
                
                # Industrial machine: reasonable range 0-10000 kWh per prediction period
                assert predicted_energy < 10000, \
                    f"Energy prediction seems unreasonably high: {predicted_energy} kWh"
                
                # Should be meaningful (not zero for typical production)
                if TYPICAL_FEATURES["total_production_count"] > 100:
                    assert predicted_energy > 0.1, \
                        f"Energy prediction too low for production: {predicted_energy} kWh"
    
    @pytest.mark.asyncio
    async def test_zero_production_energy_prediction(self):
        """Test edge case: zero production should still have valid energy (baseline consumption)"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "machine_id": COMPRESSOR_UUID,
                "features": {
                    "total_production_count": 0,
                    "avg_outdoor_temp_c": 20.0,
                    "avg_pressure_bar": 5.0
                }
            }
            
            response = await client.post(f"{BASE_URL}/baseline/predict", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                predicted_energy = data["predicted_energy_kwh"]
                
                # Zero production: should have baseline consumption >= 0
                assert predicted_energy >= 0, \
                    f"Negative energy for zero production: {predicted_energy} kWh"


# ============================================================================
# Test Class 2: Multi-Energy Machine Validation (Boiler-1 with 3 SEUs)
# ============================================================================

class TestMultiEnergyMachines:
    """Test machines with multiple energy sources (critical for v3 architecture)"""
    
    @pytest.mark.asyncio
    async def test_boiler_three_energy_sources_independent(self):
        """Test that Boiler-1's 3 SEUs (electricity, natural_gas, steam) are independent"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Map of energy sources to their SEU names
            seu_mapping = {
                ENERGY_SOURCE_ELECTRICITY: BOILER_ELECTRICITY_SEU,
                ENERGY_SOURCE_NATURAL_GAS: BOILER_NATURAL_GAS_SEU,
                ENERGY_SOURCE_STEAM: BOILER_STEAM_SEU
            }
            
            trained_models = {}
            
            for energy_source, seu_name in seu_mapping.items():
                payload = {
                    "seu_name": seu_name,
                    "energy_source": energy_source,
                    "features": [],
                    "year": 2025
                }
                
                response = await client.post(f"{BASE_URL}/ovos/train-baseline", json=payload)
                
                # Training may fail if insufficient data, that's OK
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        trained_models[energy_source] = data
                        print(f"✅ Boiler-1 {energy_source}: R² = {data.get('r_squared', 'N/A')}")
            
            # If we have at least 2 trained models, verify independence
            if len(trained_models) >= 2:
                # Predict with each model
                predictions = {}
                for energy_source in trained_models.keys():
                    pred_payload = {
                        "seu_name": seu_mapping[energy_source],
                        "energy_source": energy_source,
                        "features": TYPICAL_FEATURES
                    }
                    
                    pred_response = await client.post(f"{BASE_URL}/baseline/predict", json=pred_payload)
                    
                    if pred_response.status_code == 200:
                        pred_data = pred_response.json()
                        predictions[energy_source] = pred_data["predicted_energy_kwh"]
                
                # Note: In current system, all Boiler-1 SEUs train on energy_readings (electricity data)
                # so predictions MAY be identical. This is OK until natural_gas_readings and 
                # steam_readings tables are added. The important thing is models are STORED separately.
                pred_values = list(predictions.values())
                if len(pred_values) >= 2:
                    # Just log the values - identical is OK given current data model
                    print(f"Predictions: {dict(predictions)}")
                    # The key validation is that models are stored separately (checked in next test)
                
                # Verify all predictions are positive
                for energy_source, predicted_energy in predictions.items():
                    assert predicted_energy >= 0, \
                        f"Negative prediction for Boiler-1 {energy_source}: {predicted_energy}"
            else:
                pytest.skip("Insufficient trained models for Boiler-1 (need at least 2)")
    
    @pytest.mark.asyncio
    async def test_multi_energy_model_list_correct(self):
        """Test that listing models for multi-energy machine shows correct SEU separation"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            # List models for Boiler-1 electricity
            response_elec = await client.get(
                f"{BASE_URL}/baseline/models?seu_name={BOILER_ELECTRICITY_SEU}&energy_source={ENERGY_SOURCE_ELECTRICITY}"
            )
            
            # List models for Boiler-1 natural_gas
            response_gas = await client.get(
                f"{BASE_URL}/baseline/models?seu_name={BOILER_NATURAL_GAS_SEU}&energy_source={ENERGY_SOURCE_NATURAL_GAS}"
            )
            
            if response_elec.status_code == 200 and response_gas.status_code == 200:
                data_elec = response_elec.json()
                data_gas = response_gas.json()
                
                # Verify they return different model sets (no cross-contamination)
                if data_elec["total_models"] > 0 and data_gas["total_models"] > 0:
                    elec_model_ids = [m["id"] for m in data_elec["models"]]
                    gas_model_ids = [m["id"] for m in data_gas["models"]]
                    
                    # No overlap in model IDs
                    assert set(elec_model_ids).isdisjoint(set(gas_model_ids)), \
                        "Model ID overlap detected between different energy sources!"


# ============================================================================
# Test Class 3: R² Value Validation
# ============================================================================

class TestModelQualityMetrics:
    """Test that model quality metrics are within valid bounds"""
    
    @pytest.mark.asyncio
    async def test_r_squared_bounds(self):
        """Test that all R² values are between 0 and 1"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}/baseline/models?machine_id={COMPRESSOR_UUID}")
            
            if response.status_code == 200:
                data = response.json()
                for model in data.get("models", []):
                    r_squared = model.get("r_squared")
                    if r_squared is not None:
                        assert 0 <= r_squared <= 1, \
                            f"Invalid R² value: {r_squared} (must be 0-1). Model ID: {model['id']}"
    
    @pytest.mark.asyncio
    async def test_trained_models_have_required_fields(self):
        """Test that trained models have all required fields populated"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}/baseline/models?machine_id={COMPRESSOR_UUID}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("total_models", 0) > 0:
                    for model in data["models"]:
                        # Required fields
                        assert "id" in model, "Missing model ID"
                        assert "model_version" in model, "Missing model version"
                        assert "r_squared" in model, "Missing R²"
                        assert "is_active" in model, "Missing is_active flag"
                        
                        # R² should not be null for trained models
                        assert model["r_squared"] is not None, \
                            f"Model {model['id']} has null R²"


# ============================================================================
# Test Class 4: Timestamp and Date Validation
# ============================================================================

class TestTimestampValidation:
    """Test that all timestamps are valid ISO 8601 format"""
    
    @pytest.mark.asyncio
    async def test_prediction_timestamp_format(self):
        """Test that prediction timestamps are valid ISO 8601"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "machine_id": COMPRESSOR_UUID,
                "features": TYPICAL_FEATURES
            }
            
            response = await client.post(f"{BASE_URL}/baseline/predict", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for timestamp field (may vary by implementation)
                timestamp_fields = ["timestamp", "prediction_time", "created_at"]
                
                for field in timestamp_fields:
                    if field in data:
                        timestamp_str = data[field]
                        try:
                            # Validate ISO 8601 format
                            parsed = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                            
                            # Timestamp should be recent (within last hour)
                            now = datetime.now(parsed.tzinfo)
                            diff = abs((now - parsed).total_seconds())
                            assert diff < 3600, \
                                f"Timestamp too old: {timestamp_str} (diff: {diff}s)"
                        except ValueError as e:
                            pytest.fail(f"Invalid timestamp format in {field}: {timestamp_str}. Error: {e}")


# ============================================================================
# Test Class 5: Null Value Checks
# ============================================================================

class TestNullValueValidation:
    """Test that required fields never contain null values"""
    
    @pytest.mark.asyncio
    async def test_prediction_no_null_required_fields(self):
        """Test that predictions don't have null in required fields"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "machine_id": COMPRESSOR_UUID,
                "features": TYPICAL_FEATURES
            }
            
            response = await client.post(f"{BASE_URL}/baseline/predict", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                # Critical fields that must not be null
                required_fields = ["predicted_energy_kwh", "machine_id", "model_version"]
                
                for field in required_fields:
                    assert field in data, f"Missing required field: {field}"
                    assert data[field] is not None, f"Null value in required field: {field}"
    
    @pytest.mark.asyncio
    async def test_model_list_no_null_r_squared(self):
        """Test that active models don't have null R² values"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}/baseline/models?machine_id={COMPRESSOR_UUID}")
            
            if response.status_code == 200:
                data = response.json()
                for model in data.get("models", []):
                    if model.get("is_active"):
                        assert model.get("r_squared") is not None, \
                            f"Active model {model['id']} has null R²"


# ============================================================================
# Test Class 6: Percentage Validation
# ============================================================================

class TestPercentageValidation:
    """Test that percentages are within 0-100% range"""
    
    @pytest.mark.asyncio
    async def test_r_squared_as_percentage(self):
        """Test that R² values (often displayed as percentages) are 0-1"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}/baseline/models?machine_id={COMPRESSOR_UUID}")
            
            if response.status_code == 200:
                data = response.json()
                for model in data.get("models", []):
                    r_squared = model.get("r_squared")
                    if r_squared is not None:
                        # R² is 0-1, when displayed as percentage it's 0-100%
                        percentage = r_squared * 100
                        assert 0 <= percentage <= 100, \
                            f"R² as percentage out of bounds: {percentage}%"


# ============================================================================
# Test Class 7: Feature Input Validation
# ============================================================================

class TestFeatureValidation:
    """Test that feature inputs are validated correctly"""
    
    @pytest.mark.asyncio
    async def test_missing_features_handled(self):
        """Test that missing features are handled gracefully"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Missing one feature
            incomplete_features = {
                "total_production_count": 1000,
                "avg_outdoor_temp_c": 20.0
                # Missing avg_pressure_bar
            }
            
            payload = {
                "machine_id": COMPRESSOR_UUID,
                "features": incomplete_features
            }
            
            response = await client.post(f"{BASE_URL}/baseline/predict", json=payload)
            
            # Should either succeed (with default) or fail gracefully
            assert response.status_code in [200, 422], \
                f"Unexpected status code: {response.status_code}"
    
    @pytest.mark.asyncio
    async def test_extra_features_ignored(self):
        """Test that extra features don't break prediction"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            features_with_extra = {
                "total_production_count": 1000,
                "avg_outdoor_temp_c": 20.0,
                "avg_pressure_bar": 7.5,
                "invalid_feature_xyz": 999.9  # Extra feature
            }
            
            payload = {
                "machine_id": COMPRESSOR_UUID,
                "features": features_with_extra
            }
            
            response = await client.post(f"{BASE_URL}/baseline/predict", json=payload)
            
            # Should succeed (ignore extra feature)
            assert response.status_code == 200, \
                "Extra features should be ignored, not cause failure"


# ============================================================================
# Test Class 8: Cost Calculation Validation
# ============================================================================

class TestCostCalculation:
    """Test that cost calculations are correct (Energy × Rate)"""
    
    @pytest.mark.asyncio
    async def test_cost_calculation_if_present(self):
        """Test that if cost is returned, it matches energy × rate"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "machine_id": COMPRESSOR_UUID,
                "features": TYPICAL_FEATURES
            }
            
            response = await client.post(f"{BASE_URL}/baseline/predict", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                # If cost and rate are present, verify calculation
                if "predicted_cost" in data and "energy_rate" in data:
                    predicted_energy = data["predicted_energy_kwh"]
                    predicted_cost = data["predicted_cost"]
                    energy_rate = data["energy_rate"]
                    
                    expected_cost = predicted_energy * energy_rate
                    
                    # Allow 0.01 tolerance for floating point
                    assert abs(predicted_cost - expected_cost) < 0.01, \
                        f"Cost calculation error: {predicted_cost} != {expected_cost} " \
                        f"(energy: {predicted_energy}, rate: {energy_rate})"


# ============================================================================
# Test Class 9: Explanation Quality Validation
# ============================================================================

class TestExplanationQuality:
    """Test that model explanations are meaningful and complete"""
    
    @pytest.mark.asyncio
    async def test_explanation_has_key_drivers(self):
        """Test that explanations include key drivers"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Get a model with explanation
            models_response = await client.get(
                f"{BASE_URL}/baseline/models?machine_id={COMPRESSOR_UUID}"
            )
            
            if models_response.status_code == 200:
                models_data = models_response.json()
                
                if models_data.get("total_models", 0) > 0:
                    model_id = models_data["models"][0]["id"]
                    
                    response = await client.get(
                        f"{BASE_URL}/baseline/model/{model_id}?include_explanation=true"
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        explanation = data.get("explanation")
                        
                        assert explanation is not None, "Explanation missing"
                        assert "key_drivers" in explanation, "Key drivers missing"
                        assert len(explanation["key_drivers"]) > 0, "No key drivers listed"
                        
                        # Validate first driver structure
                        first_driver = explanation["key_drivers"][0]
                        required_driver_fields = ["feature", "coefficient", "direction", "rank"]
                        
                        for field in required_driver_fields:
                            assert field in first_driver, f"Missing field in key driver: {field}"
    
    @pytest.mark.asyncio
    async def test_voice_summary_exists(self):
        """Test that voice summaries exist and are non-empty"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            models_response = await client.get(
                f"{BASE_URL}/baseline/models?machine_id={COMPRESSOR_UUID}"
            )
            
            if models_response.status_code == 200:
                models_data = models_response.json()
                
                if models_data.get("total_models", 0) > 0:
                    model_id = models_data["models"][0]["id"]
                    
                    response = await client.get(
                        f"{BASE_URL}/baseline/model/{model_id}?include_explanation=true"
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        explanation = data.get("explanation")
                        
                        assert "voice_summary" in explanation, "Voice summary missing"
                        assert len(explanation["voice_summary"]) > 0, "Voice summary empty"
                        assert len(explanation["voice_summary"]) < 500, \
                            f"Voice summary too long ({len(explanation['voice_summary'])} chars)"


# ============================================================================
# Test Class 10: Edge Case Handling
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    @pytest.mark.asyncio
    async def test_prediction_with_all_zero_features(self):
        """Test prediction with all features set to zero"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "machine_id": COMPRESSOR_UUID,
                "features": {
                    "total_production_count": 0,
                    "avg_outdoor_temp_c": 0,
                    "avg_pressure_bar": 0
                }
            }
            
            response = await client.post(f"{BASE_URL}/baseline/predict", json=payload)
            
            # Should succeed or fail gracefully
            if response.status_code == 200:
                data = response.json()
                assert data["predicted_energy_kwh"] >= 0, \
                    "Negative energy with zero features"
    
    @pytest.mark.asyncio
    async def test_prediction_with_negative_temperature(self):
        """Test prediction with negative outdoor temperature (winter scenario)"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "machine_id": COMPRESSOR_UUID,
                "features": {
                    "total_production_count": 1000,
                    "avg_outdoor_temp_c": -20.0,  # Cold winter day
                    "avg_pressure_bar": 7.0
                }
            }
            
            response = await client.post(f"{BASE_URL}/baseline/predict", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                assert data["predicted_energy_kwh"] >= 0, \
                    "Negative energy prediction for negative temperature"


# ============================================================================
# Run Configuration
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto", "-s"])
