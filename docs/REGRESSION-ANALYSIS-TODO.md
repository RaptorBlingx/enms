# 🚀 Regression Analysis Implementation TODO

**Project:** OVOS Voice-Controlled Energy Baseline Training  
**Manager:** Mr. Umut  
**Backend Developer:** Mohamad  
**OVOS Developer:** Burak  
**Started:** November 3, 2025  
**Updated:** November 4, 2025  
**Target Completion:** November 8, 2025 (5 days)  
**Strategy:** ✅ **ENHANCEMENT APPROACH** (Enhance existing endpoints, not create duplicates)

---

## 🎯 Project Overview

Implement **state-of-the-art (SOTA)** regression analysis endpoints for OVOS voice assistant integration. Users will train energy baseline models, get predictions, and understand model behavior through voice commands.

**ARCHITECTURAL DECISION (Nov 4, 2025):**
- ❌ NOT creating new `/ovos/predict-energy` and `/ovos/explain-baseline` endpoints
- ✅ ENHANCING existing `/baseline/predict` and `/baseline/model/{id}` to accept SEU names
- ✅ Supporting BOTH UUID (dashboards) and SEU name (OVOS) inputs
- ✅ Backward compatible with existing dashboard usage

**Success Criteria:**
- ✅ Train baseline models via voice with 95%+ accuracy (R² ≥ 0.95)
- ✅ Make energy predictions from voice queries
- ✅ Explain model behavior in natural language for TTS
- ✅ Support all 4 energy sources (electricity, natural gas, steam, compressed air)
- ✅ Zero hardcoding - fully dynamic feature discovery
- ✅ Voice-friendly error messages with suggestions

---

## 📋 Phase 1: Backend Endpoint Implementation (Mohamad)

### ✅ Task 1.1: Verify Existing Training Endpoint (30 min) - **DONE**
**Status:** Already implemented at `POST /api/v1/ovos/train-baseline`

**What Exists:**
- ✅ `/api/v1/ovos/train-baseline` endpoint working (98.66% R² achieved)
- ✅ `/api/v1/ovos/energy-sources` endpoint working (4 energy sources)
- ✅ `/api/v1/ovos/seus` endpoint working (10 SEUs listed)
- ✅ `/api/v1/features/{energy_source}` endpoint working (dynamic features)

**Verified Features:**
- Dynamic feature discovery from database
- Multi-energy support (electricity, natural_gas, steam, compressed_air)
- Voice-friendly response messages
- Automatic feature selection when features=[]
- Daily aggregation for baseline training
- Model persistence to database

**Files:**
- `analytics/api/routes/ovos_training.py` (main endpoint)
- `analytics/services/seu_baseline_service.py` (business logic)
- `analytics/services/baseline_service.py` (ML training)

**Action:** ✅ Tested and documented in BURAK-READY-ENDPOINTS.md

---

### 🔄 Task 1.2: Enhance Training Endpoint Error Messages (1 hour) - **IN PROGRESS**

**Current State:** Basic error messages like "SEU not found"

**Enhancement Goal:** Voice-friendly errors with suggestions

**Changes Needed:**

#### File: `analytics/api/routes/ovos_training.py`

**Add Helper Function:**
```python
async def _build_voice_friendly_error(
    error_type: str,
    seu_name: str = None,
    energy_source: str = None
) -> dict:
    """Build voice-friendly error responses for OVOS TTS"""
    
    if error_type == "SEU_NOT_FOUND":
        # Get similar SEUs
        async with db.pool.acquire() as conn:
            similar_seus = await conn.fetch("""
                SELECT DISTINCT seu_name 
                FROM seu_mappings 
                WHERE energy_source = $1
                ORDER BY seu_name
                LIMIT 5
            """, energy_source)
        
        suggestions = [row['seu_name'] for row in similar_seus]
        
        return {
            "success": False,
            "error_code": "SEU_NOT_FOUND",
            "message": f"I couldn't find a machine named '{seu_name}' using {energy_source.replace('_', ' ')}.",
            "suggestion": f"Try one of these: {', '.join(suggestions[:3])}",
            "available_seus": suggestions
        }
    
    elif error_type == "INSUFFICIENT_DATA":
        return {
            "success": False,
            "error_code": "INSUFFICIENT_DATA",
            "message": "Not enough historical data for that period. I need at least 7 days of data.",
            "suggestion": "Try year 2025, which has a full year of data available.",
            "minimum_days_required": 7
        }
    
    elif error_type == "INVALID_FEATURES":
        # Get valid features
        async with db.pool.acquire() as conn:
            features = await conn.fetch("""
                SELECT feature_name 
                FROM energy_features 
                WHERE energy_source = $1
                ORDER BY feature_name
            """, energy_source)
        
        valid_features = [row['feature_name'] for row in features]
        
        return {
            "success": False,
            "error_code": "INVALID_FEATURES",
            "message": "Some features you specified aren't available for this energy source.",
            "suggestion": "Use automatic feature selection by providing an empty list, or choose from available features.",
            "available_features": valid_features
        }
    
    elif error_type == "NO_BASELINE_MODEL":
        return {
            "success": False,
            "error_code": "NO_BASELINE_MODEL",
            "message": f"No baseline model found for {seu_name}. You need to train a baseline first.",
            "suggestion": f"Say 'train baseline for {seu_name}' to create a model.",
            "required_action": "train_baseline"
        }
    
    else:
        return {
            "success": False,
            "error_code": "UNKNOWN_ERROR",
            "message": "Something unexpected happened. Please try again or contact support."
        }
```

**Update Exception Handling in `train_baseline_via_ovos()`:**
```python
@router.post("/train-baseline")
async def train_baseline_via_ovos(request: OVOSTrainingRequest):
    try:
        # ... existing code ...
        
        # Replace basic error handling with voice-friendly errors
        if not seu:
            return await _build_voice_friendly_error(
                "SEU_NOT_FOUND",
                seu_name=request.seu_name,
                energy_source=request.energy_source
            )
        
        # Check data availability
        if daily_data_count < 7:
            return await _build_voice_friendly_error(
                "INSUFFICIENT_DATA",
                seu_name=request.seu_name,
                energy_source=request.energy_source
            )
        
        # ... rest of implementation ...
        
    except ValueError as e:
        if "invalid features" in str(e).lower():
            return await _build_voice_friendly_error(
                "INVALID_FEATURES",
                seu_name=request.seu_name,
                energy_source=request.energy_source
            )
        raise
    
    except Exception as e:
        logger.error(f"Training error: {e}")
        return {
            "success": False,
            "error_code": "TRAINING_FAILED",
            "message": f"Training failed: {str(e)}",
            "suggestion": "Check if the machine has enough data and try again."
        }
```

**Testing Commands:**
```bash
# Test SEU not found
curl -X POST "http://localhost:8001/api/v1/ovos/train-baseline" \
  -H "Content-Type: application/json" \
  -d '{"seu_name": "NonExistent-Machine", "energy_source": "electricity", "features": [], "year": 2025}'

# Test insufficient data
curl -X POST "http://localhost:8001/api/v1/ovos/train-baseline" \
  -H "Content-Type: application/json" \
  -d '{"seu_name": "Compressor-1", "energy_source": "electricity", "features": [], "year": 2020}'

# Test invalid features
curl -X POST "http://localhost:8001/api/v1/ovos/train-baseline" \
  -H "Content-Type: application/json" \
  -d '{"seu_name": "Compressor-1", "energy_source": "electricity", "features": ["invalid_feature"], "year": 2025}'
```

**Expected Results:**
- ✅ Voice-friendly error messages
- ✅ Suggestions for fixing errors
- ✅ Available options listed
- ✅ Error codes for programmatic handling

**Completion Criteria:**
- [ ] Helper function implemented
- [ ] Exception handling updated
- [ ] All error scenarios tested
- [ ] Documentation updated in ENMS-API-DOCUMENTATION-FOR-OVOS.md

**Estimated Time:** 1 hour

---

### ⚠️ Task 1.3: Enhance Prediction Endpoint (2 hours) - **TODO** ⭐ ENHANCEMENT STRATEGY

**Endpoint:** `POST /api/v1/baseline/predict` (EXISTING - TO BE ENHANCED)

**Purpose:** Enhance existing prediction endpoint to accept BOTH machine_id (UUID) OR seu_name+energy_source for OVOS voice queries

**Strategy Change:** Instead of creating new `/ovos/predict-energy`, we enhance the existing `/baseline/predict` endpoint to support dual input methods.

**User Voice Commands:**
- "What's the expected energy for Compressor-1 at 500 units production?"
- "Predict energy consumption at 22 degrees"
- "How much energy will the HVAC use with current conditions?"

**Request Schema:**
```python
class OVOSPredictionRequest(BaseModel):
    seu_name: str = Field(..., description="SEU name (e.g., 'Compressor-1')")
    energy_source: str = Field(..., description="Energy source (electricity, natural_gas, steam, compressed_air)")
    features: Dict[str, float] = Field(..., description="Operating conditions for prediction")
    
    class Config:
        schema_extra = {
            "example": {
                "seu_name": "Compressor-1",
                "energy_source": "electricity",
                "features": {
                    "total_production_count": 500,
                    "avg_outdoor_temp_c": 22.5,
                    "avg_pressure_bar": 7.0
                }
            }
        }
```

**Implementation Steps:**

#### Step 1: Create Pydantic Models (`analytics/models/ovos.py`)
```python
from pydantic import BaseModel, Field
from typing import Dict

class OVOSPredictionRequest(BaseModel):
    seu_name: str
    energy_source: str
    features: Dict[str, float]

class OVOSPredictionResponse(BaseModel):
    success: bool
    message: str
    predicted_energy: float
    unit: str
    confidence_score: float
    model_version: str
    features_used: Dict[str, float]
```

#### Step 2: Add Endpoint (`analytics/api/routes/ovos_training.py`)
```python
@router.post("/predict-energy", response_model=OVOSPredictionResponse)
async def predict_energy_via_ovos(request: OVOSPredictionRequest):
    """
    Predict energy consumption for SEU based on operating conditions.
    Designed for OVOS voice assistant integration.
    """
    try:
        logger.info(f"OVOS prediction request for {request.seu_name} ({request.energy_source})")
        
        # 1. Lookup SEU by name + energy source
        async with db.pool.acquire() as conn:
            seu = await conn.fetchrow("""
                SELECT 
                    sm.seu_id,
                    sm.seu_name,
                    sm.machine_ids,
                    es.unit,
                    es.conversion_factor
                FROM seu_mappings sm
                JOIN energy_sources es ON sm.energy_source = es.source_name
                WHERE sm.seu_name = $1 
                AND sm.energy_source = $2
            """, request.seu_name, request.energy_source)
        
        if not seu:
            return await _build_voice_friendly_error(
                "SEU_NOT_FOUND",
                seu_name=request.seu_name,
                energy_source=request.energy_source
            )
        
        # 2. Get active baseline model for primary machine
        primary_machine_id = seu['machine_ids'][0]
        
        async with db.pool.acquire() as conn:
            model_record = await conn.fetchrow("""
                SELECT 
                    model_id,
                    model_version,
                    coefficients,
                    intercept,
                    r_squared,
                    feature_names
                FROM energy_baselines
                WHERE machine_id = $1
                AND is_active = true
                ORDER BY trained_at DESC
                LIMIT 1
            """, primary_machine_id)
        
        if not model_record:
            return await _build_voice_friendly_error(
                "NO_BASELINE_MODEL",
                seu_name=request.seu_name,
                energy_source=request.energy_source
            )
        
        # 3. Validate features match model
        model_features = model_record['feature_names']
        missing_features = set(model_features) - set(request.features.keys())
        
        if missing_features:
            return {
                "success": False,
                "error_code": "MISSING_FEATURES",
                "message": f"Missing required features: {', '.join(missing_features)}",
                "suggestion": "Provide all features used during training.",
                "required_features": model_features
            }
        
        # 4. Make prediction (manual calculation)
        coefficients = model_record['coefficients']
        intercept = model_record['intercept']
        
        prediction = intercept
        for feature_name in model_features:
            prediction += coefficients[feature_name] * request.features[feature_name]
        
        # 5. Calculate confidence based on R²
        r_squared = model_record['r_squared']
        confidence_score = min(r_squared * 100, 99.9)  # Convert to percentage
        
        # 6. Build voice-friendly message
        unit_name = seu['unit']
        confidence_desc = "high" if r_squared > 0.9 else "moderate" if r_squared > 0.7 else "low"
        
        message = (
            f"{request.seu_name} will consume approximately "
            f"{prediction:.1f} {unit_name} under those conditions. "
            f"Confidence: {confidence_desc} ({confidence_score:.1f}%)"
        )
        
        return {
            "success": True,
            "message": message,
            "predicted_energy": round(prediction, 2),
            "unit": unit_name,
            "confidence_score": round(confidence_score, 1),
            "model_version": model_record['model_version'],
            "features_used": request.features
        }
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return {
            "success": False,
            "error_code": "PREDICTION_FAILED",
            "message": f"Prediction failed: {str(e)}",
            "suggestion": "Check if all features are provided correctly."
        }
```

**Testing Commands:**
```bash
# Test successful prediction
curl -X POST "http://localhost:8001/api/v1/ovos/predict-energy" \
  -H "Content-Type: application/json" \
  -d '{
    "seu_name": "Compressor-1",
    "energy_source": "electricity",
    "features": {
      "total_production_count": 500,
      "avg_outdoor_temp_c": 22.5,
      "avg_pressure_bar": 7.0
    }
  }'

# Test missing features
curl -X POST "http://localhost:8001/api/v1/ovos/predict-energy" \
  -H "Content-Type: application/json" \
  -d '{
    "seu_name": "Compressor-1",
    "energy_source": "electricity",
    "features": {
      "total_production_count": 500
    }
  }'

# Test no model exists
curl -X POST "http://localhost:8001/api/v1/ovos/predict-energy" \
  -H "Content-Type: application/json" \
  -d '{
    "seu_name": "Untrained-Machine",
    "energy_source": "electricity",
    "features": {}
  }'
```

**Expected Results:**
- ✅ Accurate predictions using trained model
- ✅ Voice-friendly messages for TTS
- ✅ Confidence scores based on R²
- ✅ Proper error handling for missing models/features

**Completion Criteria:**
- [ ] Pydantic models created
- [ ] Endpoint implemented
- [ ] All test cases pass
- [ ] Documentation added to ENMS-API-DOCUMENTATION-FOR-OVOS.md

**Estimated Time:** 2 hours

---

### ⚠️ Task 1.4: Enhance Model Explanation Endpoint (1.5 hours) - **TODO** ⭐ ENHANCEMENT STRATEGY

**Endpoint:** `GET /api/v1/baseline/model/{id}` (EXISTING - TO BE ENHANCED)

**Purpose:** Add optional `include_explanation` query parameter to existing model detail endpoint for natural language explanations

**Strategy Change:** Instead of creating new `/ovos/explain-baseline/{seu}/{energy}`, we enhance existing `/baseline/model/{id}` endpoint.

**User Voice Commands:**
- "Explain the Compressor-1 baseline model"
- "How does the energy model work for HVAC-Main?"
- "What factors affect energy consumption?"

**Response Schema:**
```python
class ModelExplanation(BaseModel):
    success: bool
    seu_name: str
    energy_source: str
    accuracy_description: str  # "Highly accurate (99%)"
    key_drivers: List[Dict[str, Any]]  # Top 3 influential features
    sample_scenario: str  # Example prediction
    formula_simplified: str  # "Energy increases with production and decreases with pressure"
    training_info: Dict[str, Any]  # When trained, sample count
```

**Implementation Steps:**

#### Step 1: Create Model Explainer Service (`analytics/services/model_explainer.py`)
```python
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class ModelExplainerService:
    """Service for explaining ML models in natural language for OVOS TTS"""
    
    def __init__(self):
        pass
    
    def interpret_r_squared(self, r_squared: float) -> str:
        """Convert R² to voice-friendly accuracy description"""
        if r_squared >= 0.95:
            return f"Highly accurate ({r_squared*100:.1f}%)"
        elif r_squared >= 0.85:
            return f"Very accurate ({r_squared*100:.1f}%)"
        elif r_squared >= 0.70:
            return f"Moderately accurate ({r_squared*100:.1f}%)"
        else:
            return f"Limited accuracy ({r_squared*100:.1f}%). Consider retraining."
    
    def analyze_feature_importance(
        self, 
        coefficients: Dict[str, float],
        feature_names: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Analyze which features have the most impact on energy consumption.
        Returns top 3 drivers with natural language descriptions.
        """
        # Calculate absolute importance
        importance = []
        for feature in feature_names:
            coef = coefficients.get(feature, 0)
            importance.append({
                "feature": feature,
                "coefficient": coef,
                "abs_importance": abs(coef)
            })
        
        # Sort by absolute importance
        importance.sort(key=lambda x: x['abs_importance'], reverse=True)
        
        # Build natural language descriptions for top 3
        key_drivers = []
        for i, item in enumerate(importance[:3]):
            feature = item['feature']
            coef = item['coefficient']
            
            # Determine impact level
            if i == 0:
                impact = "high"
            elif i == 1:
                impact = "medium"
            else:
                impact = "low"
            
            # Determine direction
            direction = "increases" if coef > 0 else "reduces"
            
            # Humanize feature name
            feature_readable = self._humanize_feature_name(feature)
            
            # Build description
            description = f"{feature_readable} {direction} energy consumption significantly"
            
            key_drivers.append({
                "feature": feature,
                "feature_readable": feature_readable,
                "impact": impact,
                "direction": direction,
                "description": description,
                "coefficient": round(coef, 6)
            })
        
        return key_drivers
    
    def _humanize_feature_name(self, feature: str) -> str:
        """Convert database field names to natural language"""
        replacements = {
            "total_production_count": "Production volume",
            "avg_outdoor_temp_c": "Outdoor temperature",
            "avg_pressure_bar": "Operating pressure",
            "avg_humidity_percent": "Humidity level",
            "total_shift_hours": "Operating hours",
            "avg_indoor_temp_c": "Indoor temperature",
            "total_gas_flow_m3": "Gas flow rate",
            "avg_steam_pressure_bar": "Steam pressure",
            "avg_steam_temp_c": "Steam temperature"
        }
        return replacements.get(feature, feature.replace('_', ' ').title())
    
    def generate_sample_scenario(
        self,
        coefficients: Dict[str, float],
        intercept: float,
        feature_names: List[str],
        unit: str
    ) -> Dict[str, Any]:
        """Generate a realistic example prediction"""
        # Use typical values for features
        typical_values = {
            "total_production_count": 500,
            "avg_outdoor_temp_c": 22,
            "avg_pressure_bar": 7.0,
            "avg_humidity_percent": 60,
            "total_shift_hours": 8,
            "avg_indoor_temp_c": 20,
            "total_gas_flow_m3": 100,
            "avg_steam_pressure_bar": 10,
            "avg_steam_temp_c": 150
        }
        
        # Calculate prediction
        prediction = intercept
        scenario_features = {}
        
        for feature in feature_names:
            value = typical_values.get(feature, 1.0)
            prediction += coefficients[feature] * value
            scenario_features[feature] = value
        
        # Build natural language description
        readable_conditions = []
        for feature, value in scenario_features.items():
            readable_name = self._humanize_feature_name(feature)
            readable_conditions.append(f"{readable_name}: {value}")
        
        scenario_text = (
            f"For example, with {', '.join(readable_conditions[:3])}, "
            f"expect approximately {prediction:.1f} {unit} consumption"
        )
        
        return {
            "scenario_text": scenario_text,
            "predicted_energy": round(prediction, 1),
            "unit": unit,
            "conditions": scenario_features
        }
    
    def build_simplified_formula(
        self,
        key_drivers: List[Dict[str, Any]]
    ) -> str:
        """Build simplified formula in natural language"""
        if not key_drivers:
            return "Not enough information to explain the model"
        
        positive_drivers = [d for d in key_drivers if d['direction'] == 'increases']
        negative_drivers = [d for d in key_drivers if d['direction'] == 'reduces']
        
        parts = []
        if positive_drivers:
            features = ', '.join([d['feature_readable'] for d in positive_drivers])
            parts.append(f"increases with {features}")
        
        if negative_drivers:
            features = ', '.join([d['feature_readable'] for d in negative_drivers])
            parts.append(f"decreases with {features}")
        
        return f"Energy consumption {' and '.join(parts)}"


# Singleton instance
model_explainer_service = ModelExplainerService()
```

#### Step 2: Add Endpoint (`analytics/api/routes/ovos_training.py`)
```python
from ..services.model_explainer import model_explainer_service

@router.get("/explain-baseline/{seu_name}/{energy_source}")
async def explain_baseline_via_ovos(
    seu_name: str,
    energy_source: str
):
    """
    Explain how baseline model works in natural language.
    Designed for OVOS voice assistant TTS output.
    """
    try:
        logger.info(f"OVOS explanation request for {seu_name} ({energy_source})")
        
        # 1. Lookup SEU and get active model
        async with db.pool.acquire() as conn:
            seu = await conn.fetchrow("""
                SELECT 
                    sm.seu_id,
                    sm.seu_name,
                    sm.machine_ids,
                    es.unit
                FROM seu_mappings sm
                JOIN energy_sources es ON sm.energy_source = es.source_name
                WHERE sm.seu_name = $1 
                AND sm.energy_source = $2
            """, seu_name, energy_source)
        
        if not seu:
            return await _build_voice_friendly_error(
                "SEU_NOT_FOUND",
                seu_name=seu_name,
                energy_source=energy_source
            )
        
        # 2. Get active baseline model
        primary_machine_id = seu['machine_ids'][0]
        
        async with db.pool.acquire() as conn:
            model = await conn.fetchrow("""
                SELECT 
                    model_id,
                    model_version,
                    coefficients,
                    intercept,
                    r_squared,
                    rmse,
                    feature_names,
                    training_samples,
                    trained_at
                FROM energy_baselines
                WHERE machine_id = $1
                AND is_active = true
                ORDER BY trained_at DESC
                LIMIT 1
            """, primary_machine_id)
        
        if not model:
            return await _build_voice_friendly_error(
                "NO_BASELINE_MODEL",
                seu_name=seu_name,
                energy_source=energy_source
            )
        
        # 3. Use explainer service to build natural language explanation
        accuracy_desc = model_explainer_service.interpret_r_squared(
            model['r_squared']
        )
        
        key_drivers = model_explainer_service.analyze_feature_importance(
            coefficients=model['coefficients'],
            feature_names=model['feature_names']
        )
        
        sample_scenario = model_explainer_service.generate_sample_scenario(
            coefficients=model['coefficients'],
            intercept=model['intercept'],
            feature_names=model['feature_names'],
            unit=seu['unit']
        )
        
        formula_simplified = model_explainer_service.build_simplified_formula(
            key_drivers
        )
        
        # 4. Build voice-friendly summary message
        top_driver = key_drivers[0]['feature_readable'] if key_drivers else "unknown factors"
        
        message = (
            f"The {seu_name} {energy_source.replace('_', ' ')} baseline model is {accuracy_desc.lower()}. "
            f"{formula_simplified}. "
            f"The strongest factor is {top_driver}."
        )
        
        return {
            "success": True,
            "message": message,
            "seu_name": seu_name,
            "energy_source": energy_source,
            "explanation": {
                "accuracy_description": accuracy_desc,
                "key_drivers": key_drivers,
                "sample_scenario": sample_scenario['scenario_text'],
                "formula_simplified": formula_simplified,
                "training_info": {
                    "trained_at": model['trained_at'].isoformat(),
                    "samples_count": model['training_samples'],
                    "model_version": model['model_version']
                }
            }
        }
    
    except Exception as e:
        logger.error(f"Explanation error: {e}")
        return {
            "success": False,
            "error_code": "EXPLANATION_FAILED",
            "message": f"Could not explain model: {str(e)}"
        }
```

**Testing Commands:**
```bash
# Test successful explanation
curl "http://localhost:8001/api/v1/ovos/explain-baseline/Compressor-1/electricity"

# Test different energy source
curl "http://localhost:8001/api/v1/ovos/explain-baseline/Boiler-1/natural_gas"

# Test SEU not found
curl "http://localhost:8001/api/v1/ovos/explain-baseline/NonExistent/electricity"

# Test no model trained
curl "http://localhost:8001/api/v1/ovos/explain-baseline/Untrained-Machine/electricity"
```

**Expected Results:**
- ✅ Natural language explanation of model
- ✅ Top 3 influential features identified
- ✅ Sample scenario with realistic values
- ✅ Simplified formula in plain English

**Completion Criteria:**
- [ ] Model explainer service created
- [ ] Endpoint implemented
- [ ] All test cases pass
- [ ] Documentation added to ENMS-API-DOCUMENTATION-FOR-OVOS.md

**Estimated Time:** 1.5 hours

---

### ⚠️ Task 1.5: Implement Model Comparison Endpoint (OPTIONAL - 2 hours) - **TODO**

**Endpoint:** `GET /api/v1/ovos/compare-models/{seu_name}/{energy_source}`

**Purpose:** Compare different model versions to show improvement over time

**User Voice Commands:**
- "How has the Compressor-1 model improved?"
- "Compare current and previous baselines"
- "Show me model performance history"

**Response Schema:**
```python
class ModelComparison(BaseModel):
    success: bool
    seu_name: str
    current_model: Dict[str, Any]
    previous_models: List[Dict[str, Any]]
    improvement_summary: str
```

**Implementation:** (Lower priority - implement if time permits)

**Estimated Time:** 2 hours

---

## 📖 Phase 2: Documentation Updates (Mohamad)

### Task 2.1: Create Regression Analysis Section in API Docs (30 min per endpoint)

**File:** `/home/ubuntu/enms/docs/api-documentation/ENMS-API-DOCUMENTATION-FOR-OVOS.md`

**New Section Structure:**
```markdown
## 🧮 Regression Analysis & ML Baselines

This section contains all machine learning and regression analysis endpoints for energy baseline training, prediction, and model explanation.

### Overview
Voice-controlled energy baseline training allows users to:
- Train regression models to predict normal energy consumption
- Get predictions based on operating conditions
- Understand which factors affect energy usage
- Compare model performance over time

**SOTA Approach:**
- Linear Regression with automatic feature selection
- R² accuracy typically 95-99%
- Dynamic feature discovery from database
- Multi-energy support (electricity, gas, steam, compressed air)
- Zero hardcoding - fully data-driven

---

### EP16: POST /ovos/train-baseline - Train Energy Baseline Model ✅
[Full documentation with curl examples, parameters, responses]

### EP17: POST /ovos/predict-energy - Predict Energy Consumption
[Full documentation with curl examples, parameters, responses]

### EP18: GET /ovos/explain-baseline/{seu}/{energy} - Explain Model Behavior
[Full documentation with curl examples, parameters, responses]

### EP19: GET /ovos/compare-models/{seu}/{energy} - Compare Model Versions (OPTIONAL)
[Full documentation with curl examples, parameters, responses]

---

### Quick Reference: Regression Analysis Workflow

**Step 1: Train Baseline**
```bash
curl -X POST "http://localhost:8001/api/v1/ovos/train-baseline" \
  -H "Content-Type: application/json" \
  -d '{"seu_name": "Compressor-1", "energy_source": "electricity", "features": [], "year": 2025}'
```

**Step 2: Make Predictions**
```bash
curl -X POST "http://localhost:8001/api/v1/ovos/predict-energy" \
  -H "Content-Type: application/json" \
  -d '{"seu_name": "Compressor-1", "energy_source": "electricity", "features": {"total_production_count": 500}}'
```

**Step 3: Explain Model**
```bash
curl "http://localhost:8001/api/v1/ovos/explain-baseline/Compressor-1/electricity"
```
```

**Completion Criteria:**
- [ ] Section added to ENMS-API-DOCUMENTATION-FOR-OVOS.md
- [ ] All endpoints documented with real examples
- [ ] Use cases clearly explained
- [ ] Quick reference guide included

**Estimated Time:** 30 minutes per endpoint (2 hours total)

---

## 🧪 Phase 3: Testing & Validation (Mohamad)

### Task 3.1: Create Comprehensive Test Suite (2 hours)

**File:** `analytics/tests/test_ovos_regression_endpoints.py`

**Test Coverage:**
- ✅ Training endpoint (existing tests in `test_ovos_endpoints.py`)
- ⚠️ Prediction endpoint (new tests needed)
- ⚠️ Explanation endpoint (new tests needed)
- ⚠️ Error handling for all endpoints
- ⚠️ Multi-energy support
- ⚠️ Edge cases (missing data, invalid features, etc.)

**Example Test Structure:**
```python
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_predict_energy_success():
    """Test successful energy prediction"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/ovos/predict-energy", json={
            "seu_name": "Compressor-1",
            "energy_source": "electricity",
            "features": {
                "total_production_count": 500,
                "avg_outdoor_temp_c": 22.5,
                "avg_pressure_bar": 7.0
            }
        })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "predicted_energy" in data
    assert data["predicted_energy"] > 0
    assert data["unit"] == "kWh"

@pytest.mark.asyncio
async def test_predict_energy_no_model():
    """Test prediction when no baseline model exists"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/ovos/predict-energy", json={
            "seu_name": "Untrained-Machine",
            "energy_source": "electricity",
            "features": {}
        })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["error_code"] == "NO_BASELINE_MODEL"
    assert "train a baseline first" in data["message"].lower()

# ... more tests ...
```

**Completion Criteria:**
- [ ] Test file created
- [ ] 15+ test cases covering all scenarios
- [ ] All tests pass
- [ ] Coverage report generated

**Estimated Time:** 2 hours

---

### Task 3.2: Manual Testing with Real Data (1 hour)

**Testing Checklist:**
- [ ] Train baseline for Compressor-1 (electricity)
- [ ] Train baseline for Boiler-1 (natural gas)
- [ ] Make predictions with various feature values
- [ ] Explain models in natural language
- [ ] Test all error scenarios
- [ ] Verify voice-friendly messages
- [ ] Test with different energy sources
- [ ] Verify R² accuracy > 95%

**Completion Criteria:**
- [ ] All manual tests pass
- [ ] Screenshots/logs captured
- [ ] Performance metrics recorded (response times)

**Estimated Time:** 1 hour

---

## 📊 Phase 4: Burak Integration Support (Both)

### Task 4.1: Coordination Meeting (30 min)

**Agenda:**
- Demo new endpoints to Burak
- Review API documentation
- Answer questions about request/response formats
- Discuss error handling strategy
- Plan OVOS intent structure

**Completion Criteria:**
- [ ] Meeting held
- [ ] Burak understands all endpoints
- [ ] Questions answered
- [ ] Integration plan agreed upon

**Estimated Time:** 30 minutes

---

### Task 4.2: Integration Testing (1 hour)

**Test Scenarios:**
- Burak calls endpoints from OVOS skill
- Verify voice commands trigger correct API calls
- Test error recovery in OVOS
- Verify TTS output sounds natural

**Completion Criteria:**
- [ ] OVOS successfully calls all endpoints
- [ ] Voice commands work end-to-end
- [ ] Error messages are voice-friendly
- [ ] No integration issues

**Estimated Time:** 1 hour

---

## 📈 Success Metrics

**Technical Metrics:**
- ✅ All endpoints return < 500ms response time
- ✅ Training achieves R² ≥ 0.95 (95% accuracy)
- ✅ Prediction accuracy within ±5% of actual consumption
- ✅ Zero hardcoded values (fully dynamic)
- ✅ Support all 4 energy sources
- ✅ 100% test coverage for new endpoints

**User Experience Metrics:**
- ✅ Voice commands work on first try
- ✅ Error messages guide users to fix issues
- ✅ Model explanations are understandable
- ✅ Response messages are natural for TTS

---

## 📅 Timeline

| Day | Tasks | Duration |
|-----|-------|----------|
| **Day 1 (Nov 3)** | Task 1.2: Enhance error messages | 1h |
| **Day 1 (Nov 3)** | Task 1.3: Implement prediction endpoint | 2h |
| **Day 2 (Nov 4)** | Task 1.4: Implement explanation endpoint | 1.5h |
| **Day 2 (Nov 4)** | Task 2.1: Documentation updates | 2h |
| **Day 3 (Nov 5)** | Task 3.1: Test suite creation | 2h |
| **Day 3 (Nov 5)** | Task 3.2: Manual testing | 1h |
| **Day 4 (Nov 6)** | Task 4.1: Burak coordination meeting | 0.5h |
| **Day 4 (Nov 6)** | Task 4.2: Integration testing | 1h |
| **Day 5 (Nov 7)** | Buffer for fixes and polish | 2h |

**Total Estimated Time:** ~13 hours (spread over 5 days)

---

## 🚀 Getting Started

**Next Action:** Start with Task 1.2 (Enhance error messages)

**Command to Begin:**
```bash
cd /home/ubuntu/enms
git checkout -b feature/regression-analysis-ovos
```

**Let's go! 🚀**
