# ✅ Mohamad's TODO: Complete OVOS Integration

**Date:** November 3, 2025  
**Goal:** Finish backend endpoints for Burak's OVOS skill  
**Timeline:** This week

---

## 📚 Documentation Complete ✅

- ✅ **BURAK-READY-ENDPOINTS.md** (26KB) - All tested working endpoints
- ✅ **BURAK-SUMMARY.md** (4KB) - Quick reference
- ✅ **BURAK-MOHAMAD-TASK-DIVISION.md** (18KB) - Clear task split
- ✅ **REGRESSION-ANALYSIS-SKILL-REQUIREMENTS.md** (34KB) - Full requirements

**Total:** 82KB of comprehensive documentation

---

## 🔧 Backend Tasks (Your Side)

### Priority 1: OVOS-Friendly Prediction Endpoint ⭐
**Estimated Time:** 2 hours  
**Status:** ⚠️ TODO

**Create:** `POST /api/v1/ovos/predict-energy`

**Request:**
```json
{
  "seu_name": "Compressor-1",
  "energy_source": "electricity",
  "features": {
    "production_count": 500,
    "outdoor_temp_c": 22.5,
    "pressure_bar": 7.0
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Compressor-1 will consume 367 kWh under these conditions",
  "seu_name": "Compressor-1",
  "predicted_energy": 367.5,
  "unit": "kWh",
  "confidence": 0.99,
  "features_used": ["production_count", "outdoor_temp_c", "pressure_bar"]
}
```

**Implementation:**
- File: `analytics/api/routes/ovos_training.py`
- Add new route: `@router.post("/predict-energy")`
- Lookup SEU by name (reuse existing function)
- Get latest trained model
- Call `baseline_service.predict_energy()`
- Format voice-friendly response

**Test:**
```bash
curl -X POST http://localhost:8001/api/v1/ovos/predict-energy \
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
```

---

### Priority 2: Model Explanation Endpoint
**Estimated Time:** 1.5 hours  
**Status:** ⚠️ TODO

**Create:** `GET /api/v1/ovos/explain-baseline/{seu_name}/{energy_source}`

**Response:**
```json
{
  "success": true,
  "seu_name": "Compressor-1",
  "energy_source": "electricity",
  "explanation": {
    "accuracy_percent": 99,
    "accuracy_description": "Highly accurate model",
    "key_drivers": [
      {
        "feature": "production_count",
        "impact": "high",
        "coefficient": 0.000004,
        "description": "Production count strongly increases energy consumption"
      },
      {
        "feature": "pressure_bar",
        "impact": "medium",
        "coefficient": -0.545,
        "description": "Higher pressure reduces energy consumption"
      }
    ],
    "sample_prediction": "At 500 units production and 22°C, expect 367 kWh consumption",
    "training_date": "2025-11-03",
    "samples_used": 7126
  }
}
```

**Implementation:**
- File: `analytics/api/routes/ovos_training.py`
- Add route: `@router.get("/explain-baseline/{seu_name}/{energy_source}")`
- Get latest trained model
- Analyze coefficients (sort by absolute value)
- Generate human-readable descriptions
- Create sample prediction scenario

---

### Priority 3: Enhanced Error Messages
**Estimated Time:** 1 hour  
**Status:** ⚠️ TODO

**Update:** All error responses to include:
- `error_code` - Machine-readable code
- `message` - Voice-friendly message
- `suggestion` - What user should do
- `available_options` - List of valid options (if applicable)

**Example:**
```json
{
  "success": false,
  "error_code": "SEU_NOT_FOUND",
  "message": "I couldn't find a machine named 'InvalidSEU'",
  "suggestion": "Try one of these machines: Compressor-1, HVAC-Main, Boiler-1",
  "available_options": ["Compressor-1", "HVAC-Main", "Boiler-1"],
  "hint": "Machine names are case-sensitive"
}
```

**Update in:**
- `analytics/api/routes/ovos_training.py`
- All error handling blocks

---

### Optional: Model Comparison Endpoint
**Estimated Time:** 2 hours  
**Status:** 🟢 Optional (Nice to Have)

**Create:** `POST /api/v1/ovos/compare-models`

**Request:**
```json
{
  "seu_name": "Compressor-1",
  "energy_source": "electricity",
  "year": 2025,
  "feature_sets": [
    ["production_count"],
    ["production_count", "outdoor_temp_c"],
    ["production_count", "outdoor_temp_c", "pressure_bar"]
  ]
}
```

**Response:**
```json
{
  "comparisons": [
    {
      "features": ["production_count"],
      "r_squared": 0.16,
      "interpretation": "Poor fit - production alone doesn't predict energy well"
    },
    {
      "features": ["production_count", "outdoor_temp_c"],
      "r_squared": 0.47,
      "interpretation": "Moderate fit - temperature improves prediction"
    },
    {
      "features": ["production_count", "outdoor_temp_c", "pressure_bar"],
      "r_squared": 0.85,
      "interpretation": "Good fit - pressure is a strong driver"
    }
  ],
  "recommendation": {
    "best_feature_set": ["production_count", "outdoor_temp_c", "pressure_bar"],
    "r_squared": 0.85,
    "reason": "Highest accuracy with reasonable number of features"
  }
}
```

---

## 📋 Testing Checklist

After implementing each endpoint:

### Test 1: Basic Functionality
```bash
# Test prediction endpoint
curl -X POST http://localhost:8001/api/v1/ovos/predict-energy \
  -H "Content-Type: application/json" \
  -d '{
    "seu_name": "Compressor-1",
    "energy_source": "electricity",
    "features": {
      "total_production_count": 500,
      "avg_outdoor_temp_c": 22.5
    }
  }'

# Expected: Success with predicted energy value
```

### Test 2: Error Handling
```bash
# Test with invalid SEU
curl -X POST http://localhost:8001/api/v1/ovos/predict-energy \
  -H "Content-Type: application/json" \
  -d '{
    "seu_name": "InvalidMachine",
    "energy_source": "electricity",
    "features": {}
  }'

# Expected: Helpful error message with suggestions
```

### Test 3: Multi-Energy Support
```bash
# Test with natural gas
curl -X POST http://localhost:8001/api/v1/ovos/predict-energy \
  -H "Content-Type: application/json" \
  -d '{
    "seu_name": "Boiler-1 Natural Gas Burner",
    "energy_source": "natural_gas",
    "features": {
      "heating_degree_days": 15,
      "production_count": 1000
    }
  }'

# Expected: Success with m³ unit
```

### Test 4: Explanation Endpoint
```bash
# Test model explanation
curl http://localhost:8001/api/v1/ovos/explain-baseline/Compressor-1/electricity

# Expected: Voice-friendly explanation with key drivers
```

---

## 📝 Code Templates

### Template 1: Prediction Endpoint

```python
# File: analytics/api/routes/ovos_training.py

class OVOSPredictionRequest(BaseModel):
    seu_name: str
    energy_source: str
    features: Dict[str, float]

class OVOSPredictionResponse(BaseModel):
    success: bool
    message: str
    seu_name: str
    predicted_energy: float
    unit: str
    confidence: Optional[float] = None

@router.post("/predict-energy", response_model=OVOSPredictionResponse)
async def predict_energy_via_ovos(request: OVOSPredictionRequest):
    """
    Predict energy consumption for SEU (OVOS-friendly).
    """
    try:
        # Lookup SEU
        seu = await get_seu_by_name_and_energy_source(
            request.seu_name,
            request.energy_source
        )
        
        if not seu:
            return OVOSPredictionResponse(
                success=False,
                message=f"SEU '{request.seu_name}' not found",
                seu_name=request.seu_name,
                predicted_energy=0,
                unit=""
            )
        
        # Get machine_id
        machine_id = UUID(str(seu['machine_ids'][0]))
        
        # Predict using baseline service
        result = await baseline_service.predict_energy(
            machine_id=machine_id,
            features=request.features
        )
        
        # Build voice message
        message = (
            f"{request.seu_name} will consume "
            f"{result['predicted_energy_kwh']:.0f} {seu['unit']} "
            f"under these conditions"
        )
        
        return OVOSPredictionResponse(
            success=True,
            message=message,
            seu_name=request.seu_name,
            predicted_energy=result['predicted_energy_kwh'],
            unit=seu['unit'],
            confidence=result.get('confidence', 0.95)
        )
        
    except Exception as e:
        logger.error(f"[OVOS-PREDICT] Error: {e}", exc_info=True)
        return OVOSPredictionResponse(
            success=False,
            message=f"Prediction failed: {str(e)}",
            seu_name=request.seu_name,
            predicted_energy=0,
            unit=""
        )
```

### Template 2: Explanation Endpoint

```python
@router.get("/explain-baseline/{seu_name}/{energy_source}")
async def explain_baseline_via_ovos(seu_name: str, energy_source: str):
    """
    Explain trained baseline model in voice-friendly format.
    """
    try:
        # Lookup SEU
        seu = await get_seu_by_name_and_energy_source(seu_name, energy_source)
        
        if not seu:
            raise HTTPException(404, f"SEU '{seu_name}' not found")
        
        # Get latest trained model
        machine_id = seu['machine_ids'][0]
        models = await baseline_service.list_baseline_models(machine_id)
        
        if not models or len(models) == 0:
            raise HTTPException(404, "No trained model found. Train baseline first.")
        
        active_model = next((m for m in models if m.get('is_active')), models[0])
        
        # Analyze coefficients
        coefficients = json.loads(active_model['coefficients'])
        key_drivers = []
        
        for feature, coef in sorted(coefficients.items(), key=lambda x: abs(x[1]), reverse=True)[:3]:
            impact = "high" if abs(coef) > 0.5 else "medium" if abs(coef) > 0.1 else "low"
            direction = "increases" if coef > 0 else "reduces"
            
            key_drivers.append({
                "feature": feature,
                "impact": impact,
                "coefficient": coef,
                "description": f"{feature.replace('_', ' ')} {direction} energy consumption"
            })
        
        # Generate sample prediction
        sample_features = {feature: 500 if 'count' in feature else 22 for feature in coefficients.keys()}
        sample_pred = await baseline_service.predict_energy(machine_id, sample_features)
        
        return {
            "success": True,
            "seu_name": seu_name,
            "energy_source": energy_source,
            "explanation": {
                "accuracy_percent": int(active_model['r_squared'] * 100),
                "accuracy_description": _interpret_r2(active_model['r_squared']),
                "key_drivers": key_drivers,
                "sample_prediction": f"At typical conditions, expect {sample_pred['predicted_energy_kwh']:.0f} {seu['unit']}",
                "training_date": active_model['created_at'].split('T')[0],
                "samples_used": active_model['training_samples']
            }
        }
        
    except Exception as e:
        logger.error(f"[OVOS-EXPLAIN] Error: {e}", exc_info=True)
        raise HTTPException(500, str(e))

def _interpret_r2(r2: float) -> str:
    """Convert R² to voice-friendly description."""
    if r2 >= 0.95:
        return "Highly accurate model"
    elif r2 >= 0.85:
        return "Good accuracy model"
    elif r2 >= 0.70:
        return "Moderate accuracy model"
    else:
        return "Limited accuracy model"
```

---

## 📤 Delivery Checklist

Before notifying Burak:

- [ ] All endpoints implemented
- [ ] All endpoints tested with curl
- [ ] Error handling complete
- [ ] Voice-friendly messages verified
- [ ] Multi-energy support tested
- [ ] Update `BURAK-READY-ENDPOINTS.md` with new endpoints
- [ ] Add test examples to documentation
- [ ] Commit and push changes
- [ ] Notify Burak on Slack

---

## 🎯 Timeline

**Day 1 (Monday):**
- Morning: Implement prediction endpoint (2h)
- Afternoon: Test thoroughly (1h)

**Day 2 (Tuesday):**
- Morning: Implement explanation endpoint (1.5h)
- Afternoon: Enhance error messages (1h)

**Day 3 (Wednesday):**
- Morning: Integration testing with Burak (2h)
- Afternoon: Bug fixes and polish (2h)

**Day 4-5 (Thu-Fri):**
- Optional: Model comparison endpoint
- Documentation updates
- Final testing

---

## 🤝 Coordination with Burak

**Daily Standup (10 min):**
- "I finished prediction endpoint, test with this curl command..."
- "Working on explanation endpoint, expect by EOD..."
- "Found bug in X, investigating..."

**When Complete:**
1. Test endpoint yourself
2. Add to `BURAK-READY-ENDPOINTS.md` with examples
3. Ping Burak: "New endpoint ready: /ovos/predict-energy, see updated doc"
4. Answer any questions about usage

---

## 📞 Current Status

**As of November 3, 2025:**

✅ **Working:**
- Training endpoint (99% accuracy)
- SEU discovery
- Energy source listing
- Feature discovery
- Baseline prediction (machine_id)
- Forecasting

⚠️ **In Progress:**
- OVOS-friendly prediction (TODO)
- Model explanation (TODO)
- Enhanced errors (TODO)

🟢 **Optional:**
- Model comparison
- WebSocket progress

---

**Let's build this! 🚀**
