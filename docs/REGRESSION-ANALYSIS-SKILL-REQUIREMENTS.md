 # 🎯 Regression Analysis Skill - Requirements & Implementation Guide

**Date:** November 3, 2025  
**For:** Burak (OVOS Developer) & Mohamad (EnMS Backend)  
**Manager:** Mr. Umut  
**Context:** Developing "regression analysis" skill for OVOS voice assistant

---

## 📋 Executive Summary

**What Mr. Umut Wants:**
> "I want you to develop 'regression analysis' skill this week. It is a complex skill as it has to take couple of consecutive actions."

**Translation:** Mr. Umut wants an **OVOS voice skill** that allows users to:
1. **Train energy baseline models** using voice commands (regression analysis = baseline training)
2. **Query predictions** from trained models
3. **Get insights** from regression results in natural language
4. **Perform multi-step workflows** via conversation (not single-shot commands)

**Status:** ✅ **Backend 95% Ready** | ⚠️ **OVOS Integration Needed**

---

## 🎙️ What is "Regression Analysis" in EnMS Context?

### Definition
**Regression Analysis** in energy management = **Energy Baseline Training**

- **Input:** Historical energy data + operational drivers (production, temperature, pressure, etc.)
- **Algorithm:** Multiple Linear Regression (sklearn)
- **Output:** Mathematical formula predicting energy consumption based on drivers
- **Purpose:** Identify energy drivers, detect anomalies, forecast future consumption

### ISO 50001 Context
This is the **EnPI (Energy Performance Indicator)** baseline requirement for ISO 50001 compliance:
```
Energy = β₀ + β₁(Production) + β₂(Temperature) + β₃(Pressure) + ε
```

### Real-World Example
**Voice Command:**
> "Train baseline for Compressor-1 electricity using production count and outdoor temperature for 2025"

**System Response:**
> "Compressor-1 electricity baseline trained successfully. R-squared 0.99 (99% accuracy). Energy equals 370.329 plus 0.000004 times production count minus 0.404959 times pressure bar."

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER                                     │
│              "Train baseline for Compressor-1..."                │
└────────────────────────────┬────────────────────────────────────┘
                             │ Voice Input
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OVOS (Burak's Side)                         │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  1. STT (Speech-to-Text)                                │     │
│  │  2. Intent Recognition (Padatious/Adapt)                │     │
│  │  3. Entity Extraction (SEU name, energy source, etc.)   │     │
│  │  4. API Request Formation                               │     │
│  │  5. HTTP POST to EnMS Analytics                         │     │
│  │  6. Response Processing                                 │     │
│  │  7. TTS (Text-to-Speech) Output                         │     │
│  └────────────────────────────────────────────────────────┘     │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP REST API
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                 EnMS Analytics API (Mohamad's Side)              │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Endpoint: POST /api/v1/ovos/train-baseline            │     │
│  │  ┌──────────────────────────────────────────────┐      │     │
│  │  │ 1. Validate SEU name + energy source         │      │     │
│  │  │ 2. Validate features exist in database       │      │     │
│  │  │ 3. Fetch daily aggregated energy data        │      │     │
│  │  │ 4. Train Linear Regression model             │      │     │
│  │  │ 5. Calculate R², RMSE, MAE metrics           │      │     │
│  │  │ 6. Save model to database                    │      │     │
│  │  │ 7. Return voice-friendly response            │      │     │
│  │  └──────────────────────────────────────────────┘      │     │
│  └────────────────────────────────────────────────────────┘     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   TimescaleDB (PostgreSQL)                       │
│  - energy_readings (hypertable)                                  │
│  - seus (Significant Energy Uses)                                │
│  - energy_sources (electricity, natural_gas, steam)              │
│  - features (dynamic feature registry)                           │
│  - energy_baselines (trained models)                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 What Exists Already (Backend - Mohamad)

### ✅ Completed Endpoints

#### 1. **POST /api/v1/ovos/train-baseline** ⭐ PRODUCTION READY
**File:** `analytics/api/routes/ovos_training.py`

**Request:**
```json
{
  "seu_name": "Compressor-1",
  "energy_source": "electricity",
  "features": ["production_count", "outdoor_temp_c"],
  "year": 2025
}
```

**Response:**
```json
{
  "success": true,
  "message": "Compressor-1 electricity baseline trained. R-squared 0.99...",
  "seu_name": "Compressor-1",
  "energy_source": "electricity",
  "r_squared": 0.99,
  "rmse": 1.21,
  "formula_readable": "Energy equals 370.329 plus 0.000004 times...",
  "samples_count": 6957,
  "trained_at": "2025-10-27T12:34:56Z"
}
```

**Features:**
- ✅ Voice-friendly natural language responses
- ✅ Dynamic feature discovery (no hardcoding)
- ✅ Multi-energy support (electricity, gas, steam, compressed air)
- ✅ Auto-feature selection (97-99% accuracy)
- ✅ Comprehensive error handling with helpful messages

#### 2. **GET /api/v1/ovos/energy-sources**
List all available energy sources dynamically.

**Response:**
```json
{
  "success": true,
  "energy_sources": [
    {
      "name": "electricity",
      "unit": "kWh",
      "features_count": 22,
      "sample_features": ["consumption_kwh", "production_count", "outdoor_temp_c"]
    },
    {
      "name": "natural_gas",
      "unit": "m³",
      "features_count": 10,
      "sample_features": ["consumption_m3", "heating_degree_days"]
    }
  ]
}
```

#### 3. **GET /api/v1/ovos/seus**
List available SEUs (machines) filtered by energy source.

**Response:**
```json
{
  "success": true,
  "seus": [
    {
      "id": "uuid",
      "name": "Compressor-1",
      "energy_source": "electricity",
      "machine_count": 1,
      "r_squared": 0.99
    }
  ]
}
```

#### 4. **GET /api/v1/features/{energy_source}**
Get available features for specific energy source.

**Example:** `/api/v1/features/electricity`

**Response:**
```json
{
  "energy_source": "electricity",
  "features": [
    {
      "feature_name": "consumption_kwh",
      "description": "Total electrical energy consumed",
      "unit": "kWh"
    },
    {
      "feature_name": "production_count",
      "description": "Total production units",
      "unit": "units"
    }
  ]
}
```

---

## 🎯 What's Already Working (with Examples)

### Test Scenario 1: Basic Training
```bash
curl -X POST http://localhost:8001/api/v1/ovos/train-baseline \
  -H "Content-Type: application/json" \
  -d '{
    "seu_name": "Compressor-1",
    "energy_source": "electricity",
    "features": ["production_count", "outdoor_temp_c"],
    "year": 2025
  }'
```

**Result:** ✅ R² = 0.47 (47% accuracy with 2 features)

### Test Scenario 2: Auto-Feature Selection (Best Accuracy)
```bash
curl -X POST http://localhost:8001/api/v1/ovos/train-baseline \
  -H "Content-Type: application/json" \
  -d '{
    "seu_name": "Compressor-1",
    "energy_source": "electricity",
    "features": [],
    "year": 2025
  }'
```

**Result:** ✅ R² = 0.99 (99% accuracy with auto-selected 6 features)

### Test Scenario 3: Multi-Energy (Natural Gas)
```bash
curl -X POST http://localhost:8001/api/v1/ovos/train-baseline \
  -H "Content-Type: application/json" \
  -d '{
    "seu_name": "Boiler-1",
    "energy_source": "natural_gas",
    "features": ["heating_degree_days", "production_count"],
    "year": 2025
  }'
```

**Result:** ✅ R² = 0.87 (87% accuracy - gas consumption strongly correlates with HDD)

---

## 🚀 What Needs to Be Done

### 🔵 Burak's Tasks (OVOS Side)

#### Task 1: Create OVOS Skill Structure (30 min)
```
ovos-skills/
└── enms-regression-skill/
    ├── __init__.py           # Main skill class
    ├── locale/
    │   └── en-us/
    │       ├── train.baseline.intent
    │       ├── predict.energy.intent
    │       ├── list.seus.intent
    │       └── baseline.dialog
    ├── requirements.txt      # requests, json
    └── settingsmeta.json     # EnMS API endpoint config
```

#### Task 2: Define Intents (Padatious/Adapt) (45 min)

**File:** `locale/en-us/train.baseline.intent`
```
train baseline for {seu_name} {energy_source}
train {seu_name} {energy_source} baseline
create baseline for {seu_name} using {energy_source}
regression analysis for {seu_name} {energy_source}
train energy model for {seu_name}
```

**File:** `locale/en-us/predict.energy.intent`
```
predict energy for {seu_name}
what's the expected energy for {seu_name}
forecast {seu_name} energy consumption
```

**File:** `locale/en-us/list.seus.intent`
```
list all machines
show available SEUs
what machines can I train
```

#### Task 3: Implement Intent Handlers (2-3 hours)

**File:** `__init__.py`
```python
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler
import requests
import json

class EnMSRegressionSkill(OVOSSkill):
    def __init__(self):
        super().__init__()
        self.api_base = "http://your-enms-server:8001/api/v1"
    
    @intent_handler("train.baseline.intent")
    def handle_train_baseline(self, message):
        """
        Handle: "Train baseline for Compressor-1 electricity"
        """
        # Extract entities
        seu_name = message.data.get("seu_name")
        energy_source = message.data.get("energy_source", "electricity")
        
        # Multi-turn conversation: Ask for year
        year = self.ask_yesno(
            f"Which year should I use for training {seu_name}?",
            {"2025": 2025, "2024": 2024, "2023": 2023}
        )
        
        # Multi-turn conversation: Ask for features
        use_auto = self.ask_yesno(
            "Should I auto-select the best features for maximum accuracy?",
            {"yes": True, "no": False}
        )
        
        features = [] if use_auto else self._ask_for_features(energy_source)
        
        # Call EnMS API
        response = requests.post(
            f"{self.api_base}/ovos/train-baseline",
            json={
                "seu_name": seu_name,
                "energy_source": energy_source,
                "features": features,
                "year": year
            }
        )
        
        data = response.json()
        
        if data["success"]:
            # Speak voice-friendly message
            self.speak(data["message"])
            
            # Provide additional details if requested
            if self.ask_yesno("Would you like technical details?"):
                self.speak(
                    f"The model achieved R-squared {data['r_squared']:.2f}, "
                    f"using {data['samples_count']} days of training data."
                )
        else:
            self.speak(f"Training failed: {data['message']}")
    
    def _ask_for_features(self, energy_source):
        """Ask user which features to include (multi-turn)."""
        # Get available features
        response = requests.get(
            f"{self.api_base}/features/{energy_source}"
        )
        features_list = [f["feature_name"] for f in response.json()["features"]]
        
        # Present options
        self.speak(
            f"Available features for {energy_source}: "
            f"{', '.join(features_list[:5])}. "
            f"Which features should I use? Say 'all' or specify."
        )
        
        # Get user selection (simplified - real implementation needs NLU)
        selection = self.get_response()
        
        if "all" in selection.lower():
            return []  # Auto-select
        else:
            # Parse feature names from response
            return self._parse_features(selection, features_list)
    
    @intent_handler("list.seus.intent")
    def handle_list_seus(self, message):
        """Handle: "List all machines" """
        response = requests.get(f"{self.api_base}/ovos/seus")
        seus = response.json()["seus"]
        
        seu_names = [seu["name"] for seu in seus[:5]]
        self.speak(
            f"I found {len(seus)} machines. Here are the first five: "
            f"{', '.join(seu_names)}"
        )

def create_skill():
    return EnMSRegressionSkill()
```

#### Task 4: Multi-Turn Conversation Flow (1-2 hours)

**Conversation Example:**
```
User:  "Train baseline for Compressor-1"
OVOS:  "Which energy source? Electricity, natural gas, or steam?"
User:  "Electricity"
OVOS:  "Which year? 2024 or 2025?"
User:  "2025"
OVOS:  "Should I auto-select features for maximum accuracy, or do you want to specify?"
User:  "Auto-select"
OVOS:  [Calls API]
OVOS:  "Compressor-1 electricity baseline trained. R-squared 0.99. 99% accuracy."
User:  "Give me details"
OVOS:  "The model used 365 days of training data with 6 features including 
        production count, pressure, temperature, and load factor."
```

**Implementation Pattern:**
```python
def handle_train_baseline_conversation(self, message):
    """Multi-step conversation for training."""
    # Step 1: Get SEU name
    seu_name = message.data.get("seu_name")
    if not seu_name:
        seu_name = self.get_response("Which machine would you like to train?")
    
    # Step 2: Get energy source
    energy_source = self.ask_selection(
        "Which energy source?",
        ["electricity", "natural gas", "steam"]
    )
    
    # Step 3: Get year
    year = int(self.get_response("Which year? Say a year between 2020 and 2025."))
    
    # Step 4: Feature selection
    use_auto = self.ask_yesno("Should I automatically select the best features?")
    
    # Step 5: Execute training
    # ... (call API as shown above)
```

#### Task 5: Error Handling & User Guidance (1 hour)

**Handle Common Errors:**
```python
def handle_api_error(self, error_response):
    """Provide helpful guidance for API errors."""
    error = error_response.get("detail", "Unknown error")
    
    if "SEU" in error and "not found" in error:
        self.speak(
            "I couldn't find that machine. "
            "Would you like me to list available machines?"
        )
        if self.ask_yesno("List machines?"):
            self.handle_list_seus(None)
    
    elif "Invalid features" in error:
        self.speak(
            "Those features aren't available for this energy source. "
            "Let me use automatic feature selection instead."
        )
        # Retry with features=[]
    
    elif "Insufficient data" in error:
        self.speak(
            "There isn't enough historical data for that year. "
            "Try a different year with more data."
        )
    
    else:
        self.speak(f"An error occurred: {error}")
```

#### Task 6: Testing Checklist (1 hour)

- [ ] Test intent recognition with variations
- [ ] Test multi-turn conversation flow
- [ ] Test error handling (invalid SEU, invalid features)
- [ ] Test with all 4 energy sources (electricity, gas, steam, air)
- [ ] Test TTS output quality (formula readability)
- [ ] Test with/without auto-feature selection
- [ ] Test API timeout handling
- [ ] Test concurrent requests (multiple users)

---

### 🟢 Mohamad's Tasks (Backend Side)

#### Task 1: Add Prediction Endpoint for OVOS (2 hours)

**New Endpoint Needed:** `POST /api/v1/ovos/predict-energy`

**Purpose:** Let OVOS query predictions after training

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
  "message": "Compressor-1 is predicted to consume 367.5 kWh under these conditions",
  "seu_name": "Compressor-1",
  "predicted_energy": 367.5,
  "unit": "kWh",
  "confidence": 0.99,
  "features_used": ["production_count", "outdoor_temp_c", "pressure_bar"]
}
```

**Implementation:**
```python
@router.post("/predict-energy", response_model=OVOSPredictionResponse)
async def predict_energy_via_ovos(request: OVOSPredictionRequest):
    """Predict energy for given operating conditions (OVOS-friendly)."""
    # Similar to /baseline/predict but with SEU name lookup
    seu = await get_seu_by_name_and_energy_source(
        request.seu_name, 
        request.energy_source
    )
    
    # Get latest trained model
    model = await baseline_service.get_active_model(seu['machine_ids'][0])
    
    # Predict
    prediction = model.predict(request.features)
    
    # Build voice-friendly message
    message = (
        f"{request.seu_name} is predicted to consume "
        f"{prediction:.1f} {seu['unit']} under these conditions"
    )
    
    return OVOSPredictionResponse(
        success=True,
        message=message,
        predicted_energy=prediction,
        # ...
    )
```

#### Task 2: Add Regression Results Explanation Endpoint (1.5 hours)

**New Endpoint:** `GET /api/v1/ovos/explain-baseline/{seu_name}/{energy_source}`

**Purpose:** Provide human-readable insights about trained models

**Response:**
```json
{
  "success": true,
  "seu_name": "Compressor-1",
  "energy_source": "electricity",
  "explanation": {
    "accuracy_percent": 99,
    "interpretation": "The model is highly accurate and can reliably predict energy consumption",
    "key_drivers": [
      {
        "feature": "production_count",
        "impact": "high",
        "description": "Production count has the strongest influence on energy consumption"
      },
      {
        "feature": "outdoor_temp_c",
        "impact": "medium",
        "description": "Temperature affects energy by 2% per degree"
      }
    ],
    "sample_prediction": "At 500 units production and 22°C, expect 367 kWh consumption"
  }
}
```

#### Task 3: Add Forecasting Integration (3-4 hours)

**Challenge:** Integrate **regression baseline** with **time-series forecasting**

**New Workflow:**
1. User trains baseline (regression) → Get energy drivers relationship
2. User requests forecast → Use Prophet/ARIMA for time-series + baseline for constraints
3. Combined prediction more accurate

**Example:**
```python
# Forecast next 24 hours using both models
baseline_prediction = baseline_model.predict(future_features)
timeseries_forecast = prophet_model.predict(24)

# Combine predictions (weighted average or ensemble)
final_forecast = 0.6 * timeseries_forecast + 0.4 * baseline_prediction
```

#### Task 4: Add Model Comparison Endpoint (2 hours)

**New Endpoint:** `POST /api/v1/ovos/compare-models`

**Purpose:** Compare multiple feature combinations

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
      "interpretation": "Moderate fit - temperature improves prediction significantly"
    },
    {
      "features": ["production_count", "outdoor_temp_c", "pressure_bar"],
      "r_squared": 0.85,
      "interpretation": "Good fit - pressure is a strong additional driver"
    }
  ],
  "recommendation": "Use 3 features for best accuracy"
}
```

#### Task 5: WebSocket for Real-Time Training Progress (Optional, 4 hours)

**Enhancement:** Long training jobs send progress updates via WebSocket

```python
# In training function
async def train_with_progress(seu_id, ...):
    await websocket.send({"status": "fetching_data", "progress": 10})
    data = await fetch_data(...)
    
    await websocket.send({"status": "training", "progress": 50})
    model.fit(X, y)
    
    await websocket.send({"status": "complete", "progress": 100, "r_squared": 0.99})
```

---

## 📊 Complete Use Cases & Examples

### Use Case 1: Basic Training (Single-Turn)
**Voice:** "Train baseline for Compressor-1 electricity for 2025"

**OVOS Actions:**
1. Extract: seu_name="Compressor-1", energy_source="electricity", year=2025
2. POST to `/ovos/train-baseline` with features=[]
3. Speak response: "Compressor-1 baseline trained, 99% accuracy"

### Use Case 2: Training with Feature Selection (Multi-Turn)
**Voice:** "Train Compressor-1 electricity baseline"
**OVOS:** "Which year?"
**Voice:** "2025"
**OVOS:** "Auto-select features or specify?"
**Voice:** "Use production count and temperature"
**OVOS:** [Calls API with features=["production_count", "outdoor_temp_c"]]
**OVOS:** "Baseline trained, 47% accuracy with 2 features"

### Use Case 3: Prediction After Training
**Voice:** "Predict energy for Compressor-1 at 500 units production"
**OVOS:** [Calls /ovos/predict-energy]
**OVOS:** "Compressor-1 will consume approximately 367 kWh at those conditions"

### Use Case 4: Model Explanation
**Voice:** "Explain the Compressor-1 baseline"
**OVOS:** [Calls /ovos/explain-baseline]
**OVOS:** "The model is 99% accurate. Production count has the strongest influence on energy consumption, followed by pressure and temperature."

### Use Case 5: Comparison Analysis
**Voice:** "Compare different features for Compressor-1"
**OVOS:** [Calls /ovos/compare-models with different feature sets]
**OVOS:** "Using production alone gives 16% accuracy. Adding temperature improves it to 47%. Adding pressure reaches 85% accuracy. I recommend using all three features."

### Use Case 6: Forecasting Integration
**Voice:** "Forecast Compressor-1 energy for tomorrow"
**OVOS:** [Combines regression baseline + time-series forecast]
**OVOS:** "Based on predicted production of 12,000 units and temperature of 20°C, Compressor-1 will consume approximately 8,800 kWh tomorrow."

---

## 🔄 Multi-Step Workflow Example

**Scenario:** User wants to optimize energy consumption

```
1. User:  "Help me optimize Compressor-1 energy"
2. OVOS:  "I'll start by training a baseline. Which year's data should I use?"
3. User:  "2025"
4. OVOS:  [Trains baseline] "Baseline trained with 99% accuracy"
5. OVOS:  "Now predicting next week's consumption based on production schedule..."
6. OVOS:  [Calls forecast API] "Expected consumption: 9,500 kWh next week"
7. OVOS:  "I found 3 high-consumption periods. Would you like recommendations?"
8. User:  "Yes"
9. OVOS:  "Peak energy usage Tuesday 2-4pm. Consider shifting 30% production to Wednesday morning for 15% cost savings."
```

**APIs Called in Sequence:**
1. POST /ovos/train-baseline
2. POST /forecast/predict (horizon=long)
3. POST /forecast/optimal-schedule
4. GET /anomaly/recent (check for inefficiencies)

---

## 🧪 Testing Strategy

### Backend Testing (Mohamad)
```bash
# Test 1: Basic training
curl -X POST http://localhost:8001/api/v1/ovos/train-baseline \
  -H "Content-Type: application/json" \
  -d '{"seu_name": "Compressor-1", "energy_source": "electricity", "features": [], "year": 2025}'

# Test 2: Invalid SEU
curl -X POST http://localhost:8001/api/v1/ovos/train-baseline \
  -H "Content-Type: application/json" \
  -d '{"seu_name": "InvalidSEU", "energy_source": "electricity", "features": [], "year": 2025}'

# Test 3: Multi-energy
curl -X POST http://localhost:8001/api/v1/ovos/train-baseline \
  -H "Content-Type: application/json" \
  -d '{"seu_name": "Boiler-1", "energy_source": "natural_gas", "features": ["heating_degree_days"], "year": 2025}'
```

### OVOS Testing (Burak)
```python
# Test intent recognition
test_utterances = [
    "train baseline for Compressor-1 electricity",
    "create energy model for HVAC-Main",
    "regression analysis for Boiler-1 natural gas",
    "predict energy for Compressor-1",
    "list all machines"
]

for utterance in test_utterances:
    intent = skill.intent_recognizer.calc_intent(utterance)
    assert intent.confidence > 0.8
```

### Integration Testing (Both)
1. **End-to-End Test:** Voice → OVOS → EnMS → Database → Response → TTS
2. **Error Recovery Test:** Test invalid inputs at each step
3. **Performance Test:** Measure response time (<5s target)
4. **Multi-Turn Test:** Test conversation flows with interruptions

---

## 📝 What We Already Have vs. What's Missing

### ✅ Already Implemented (95% Backend Ready)

| Feature | Status | Location |
|---------|--------|----------|
| Baseline training API | ✅ Done | `analytics/api/routes/ovos_training.py` |
| Multi-energy support | ✅ Done | Dynamic from database |
| Feature discovery | ✅ Done | `services/feature_discovery.py` |
| Voice-friendly responses | ✅ Done | `message` field in responses |
| SEU lookup by name | ✅ Done | `get_seu_by_name_and_energy_source()` |
| Error handling | ✅ Done | HTTPException with helpful messages |
| Auto-feature selection | ✅ Done | Smart hybrid approach (97-99% accuracy) |
| Energy source listing | ✅ Done | GET /ovos/energy-sources |
| SEU listing | ✅ Done | GET /ovos/seus |
| Feature validation | ✅ Done | `feature_discovery.validate_features()` |

### ⚠️ Missing / Needs Work

| Feature | Priority | Estimated Time |
|---------|----------|----------------|
| OVOS skill implementation | 🔴 High | 6-8 hours |
| Prediction endpoint for OVOS | 🟡 Medium | 2 hours |
| Baseline explanation endpoint | 🟡 Medium | 1.5 hours |
| Model comparison endpoint | 🟢 Low | 2 hours |
| Forecasting integration | 🟡 Medium | 3-4 hours |
| Multi-turn conversation logic | 🔴 High | 2-3 hours |
| WebSocket progress updates | 🟢 Optional | 4 hours |

---

## 📅 Proposed Timeline

### Week 1 (This Week)

**Day 1-2 (Burak):** OVOS Skill Foundation
- Create skill structure
- Define intents
- Implement basic handlers
- Test intent recognition

**Day 1-2 (Mohamad):** Additional Endpoints
- Add prediction endpoint
- Add explanation endpoint
- Write tests

**Day 3-4 (Both):** Integration
- Connect OVOS to EnMS API
- Test end-to-end flows
- Handle errors gracefully

**Day 5 (Both):** Advanced Features
- Multi-turn conversations
- Model comparison
- Polish TTS output

---

## 🎓 Key Concepts Burak Needs to Understand

### 1. **Regression Analysis = Energy Baseline**
- Not generic statistical analysis
- Specific to energy management context
- Predicts energy from operational parameters

### 2. **Multi-Energy Sources**
- EnMS tracks 4 energy types (not just electricity)
- Each has different features and units
- OVOS must handle all dynamically

### 3. **Features = Energy Drivers**
- Production count, temperature, pressure, etc.
- User can specify or auto-select
- More features ≠ better (risk of overfitting)

### 4. **R-Squared (R²) = Accuracy Metric**
- 0-1 scale (0% to 100%)
- >0.85 = good, >0.95 = excellent
- Explain to users in percentage terms

### 5. **Multi-Turn Conversations**
- Training is complex, needs multiple inputs
- Guide user through steps
- Provide helpful defaults

---

## 🚨 Common Pitfalls to Avoid

### Burak's Side (OVOS)
1. ❌ **Don't hardcode machine names** → Use dynamic SEU discovery
2. ❌ **Don't assume electricity only** → Support all 4 energy sources
3. ❌ **Don't skip error handling** → API will return helpful error messages, use them
4. ❌ **Don't make single-turn only** → Multi-step workflows are key requirement
5. ❌ **Don't forget to validate year** → Must have data for that year

### Mohamad's Side (EnMS)
1. ❌ **Don't break existing /baseline/train** → OVOS endpoint is separate
2. ❌ **Don't assume features exist** → Always validate with feature_discovery
3. ❌ **Don't return technical jargon** → Keep responses voice-friendly
4. ❌ **Don't forget units** → Include units in responses (kWh, m³, kg)
5. ❌ **Don't skip logging** → Log all OVOS requests for debugging

---

## 📚 Documentation References

**For Burak:**
- OVOS API Documentation: `/docs/api-documentation/ENMS-API-DOCUMENTATION-FOR-OVOS.md`
- Endpoint details: Section "EP16: OVOS Voice Training"
- Test examples: Analytics service tests

**For Mohamad:**
- Current implementation: `analytics/api/routes/ovos_training.py`
- Service layer: `analytics/services/seu_baseline_service.py`
- Feature discovery: `analytics/services/feature_discovery.py`

---

## 🎤 Example Voice Interactions (Final Product)

### Example 1: Quick Training
```
User:  "Train Compressor-1"
OVOS:  "Training Compressor-1 electricity baseline for 2025 with auto-selected features"
       [3 seconds]
OVOS:  "Done! 99% accuracy using production count, pressure, temperature, and load factor"
```

### Example 2: Detailed Training
```
User:  "I want to train an energy baseline"
OVOS:  "Which machine?"
User:  "Compressor-1"
OVOS:  "Which energy source?"
User:  "Electricity"
OVOS:  "Which year?"
User:  "2025"
OVOS:  "Should I automatically select the best features?"
User:  "No, use production count and temperature"
OVOS:  "Training with 2 features..."
       [3 seconds]
OVOS:  "Baseline complete. 47% accuracy. Would you like me to try with more features?"
User:  "Yes"
OVOS:  "Re-training with auto-selection..."
       [3 seconds]
OVOS:  "Much better! 99% accuracy with 6 features"
```

### Example 3: Prediction
```
User:  "Predict Compressor-1 energy at 500 units production"
OVOS:  "What temperature?"
User:  "22 degrees"
OVOS:  "What pressure?"
User:  "7 bar"
OVOS:  "Compressor-1 will consume approximately 367 kilowatt-hours under those conditions"
```

---

## ✅ Success Criteria

**Definition of Done:**
- [ ] OVOS recognizes regression training intents
- [ ] User can train baseline via voice (single-turn or multi-turn)
- [ ] User can query predictions via voice
- [ ] System handles errors gracefully with helpful guidance
- [ ] Works for all 4 energy sources dynamically
- [ ] Response time <5 seconds for training
- [ ] TTS output is natural and understandable
- [ ] Multi-turn conversations work smoothly
- [ ] Demo video showing full workflow

---

## 🤝 Coordination Points

**Daily Sync (15 min):**
- Burak: "Intent recognition working for X, need help with Y"
- Mohamad: "Added endpoint Z, test with curl command..."
- Blockers discussed
- Next 24h plan

**Mid-Week Review (30 min):**
- Demo current progress
- Identify integration issues
- Adjust timeline if needed

**End-of-Week Demo:**
- Full workflow demonstration
- Test with Mr. Umut's use cases
- Document learnings

---

## 📞 Contact & Support

**Burak:** OVOS skill development, intent recognition, TTS/STT
**Mohamad:** Backend API, database queries, ML models
**Mr. Umut:** Requirements clarification, use case validation

**Slack Channel:** #enms-ovos-integration  
**Git Branches:**
- Burak: `feature/ovos-regression-skill`
- Mohamad: `feature/ovos-endpoints-enhancement`

---

## 🎯 Bottom Line

**Mr. Umut wants:** A voice-controlled system where users can train energy regression models, query predictions, and get insights **through natural conversation** (not single commands).

**What's ready:** Backend APIs 95% complete, tested, production-quality

**What's needed:** OVOS skill implementation with multi-turn conversation logic

**Timeline:** Realistic 5-day completion if both work together

**Key Success Factor:** Good communication between Burak (OVOS) and Mohamad (EnMS) to handle edge cases and integration issues

---

**Good luck! You've got this! 🚀**
