# 🤝 Task Division: Burak (OVOS) vs. Mohamad (EnMS)

**Quick Reference Guide for "Regression Analysis" Skill Development**

---

## 🔵 BURAK'S RESPONSIBILITIES (OVOS Side)

### Your Domain: Voice User Interface
You handle **everything the user sees/hears** and **translating voice to API calls**.

### Core Tasks

#### 1. **Intent Recognition** (Your Bread & Butter)
**What:** Recognize when user wants to do regression analysis

**Voice Patterns to Catch:**
```
"train baseline for Compressor-1"
"create energy model for HVAC-Main"
"regression analysis for Boiler-1"
"teach the system about Compressor-1 energy"
```

**Output:** Extract entities (seu_name, energy_source, year)

**Files:**
- `locale/en-us/train.baseline.intent`
- `locale/en-us/predict.energy.intent`

---

#### 2. **Multi-Turn Conversations** (Key Requirement!)
**What:** Guide user through training process step-by-step

**Example Flow YOU Build:**
```
User:  "Train Compressor-1"
YOU:   "Which energy source? Electricity, natural gas, or steam?"
User:  "Electricity"
YOU:   "Which year should I use? 2024 or 2025?"
User:  "2025"
YOU:   "Should I auto-select features for best accuracy?"
User:  "Yes"
YOU:   [Call Mohamad's API]
YOU:   "Training complete! 99% accuracy achieved."
```

**Implementation:**
```python
def handle_train_conversation(self):
    # Step 1: Get SEU
    seu = self.ask_for_seu_name()
    
    # Step 2: Get energy source
    energy = self.ask_selection("Energy source?", ["electricity", "natural gas"])
    
    # Step 3: Get year
    year = self.get_response("Which year?")
    
    # Step 4: Call Mohamad's API
    result = self.call_enms_api(seu, energy, year)
    
    # Step 5: Speak result
    self.speak(result["message"])
```

---

#### 3. **API Integration** (HTTP Requests to Mohamad's Backend)
**What:** Make HTTP POST/GET requests to EnMS Analytics

**Your Code:**
```python
import requests

def call_training_api(self, seu_name, energy_source, features, year):
    response = requests.post(
        "http://enms-server:8001/api/v1/ovos/train-baseline",
        json={
            "seu_name": seu_name,
            "energy_source": energy_source,
            "features": features,  # [] for auto-select
            "year": year
        },
        timeout=30  # Training can take 10-20 seconds
    )
    
    return response.json()
```

**APIs Mohamad Provides for You:**
| Endpoint | Purpose | When to Use |
|----------|---------|-------------|
| POST /ovos/train-baseline | Train model | Main training command |
| GET /ovos/energy-sources | List energy types | Discovery/validation |
| GET /ovos/seus | List machines | "List all machines" command |
| GET /features/{energy} | List features | Feature discovery |

---

#### 4. **Error Handling & User Guidance** (Make It Human!)
**What:** When API returns error, guide user to fix it

**Your Responsibility:**
```python
def handle_error(self, error_response):
    error_msg = error_response.get("detail", "")
    
    if "not found" in error_msg.lower():
        self.speak("I couldn't find that machine. Let me list available machines...")
        self.list_seus()
    
    elif "insufficient data" in error_msg.lower():
        self.speak("Not enough data for that year. Try 2025 instead, which has more data.")
    
    elif "invalid features" in error_msg.lower():
        self.speak("Those features aren't available. I'll use automatic selection instead.")
        # Retry with features=[]
    
    else:
        self.speak(f"Something went wrong: {error_msg}")
```

---

#### 5. **Text-to-Speech Polish** (Make It Sound Natural)
**What:** Convert Mohamad's JSON responses into natural speech

**Mohamad Gives You:**
```json
{
  "message": "Compressor-1 electricity baseline trained. R-squared 0.99...",
  "r_squared": 0.99,
  "formula_readable": "Energy equals 370.329 plus 0.000004 times production count..."
}
```

**You Say:**
```
"Great news! I've trained the Compressor-1 electricity baseline 
with 99% accuracy. The model shows that energy consumption 
increases with production count and decreases with higher pressure."
```

**Simplification Tips:**
- R² 0.99 → "99% accuracy" or "highly accurate"
- RMSE 1.21 → Skip (too technical for voice)
- Formula → Summarize key drivers only

---

### Your Deliverables

**Code Files:**
```
ovos-skills/enms-regression-skill/
├── __init__.py                    # Main skill class with handlers
├── requirements.txt               # requests, json
├── locale/en-us/
│   ├── train.baseline.intent      # Voice patterns for training
│   ├── predict.energy.intent      # Voice patterns for prediction
│   ├── list.seus.intent           # Voice patterns for discovery
│   └── *.dialog                   # Response templates
└── settingsmeta.json              # EnMS API endpoint config
```

**Key Functions:**
- `handle_train_baseline()` - Main training intent handler
- `handle_predict_energy()` - Prediction handler
- `handle_list_seus()` - Machine discovery
- `_ask_for_features()` - Multi-turn feature selection
- `_call_enms_api()` - HTTP request wrapper
- `_handle_api_error()` - Error recovery

---

### What You DON'T Need to Worry About

❌ **NOT Your Problem:**
- Database queries
- Machine learning algorithms
- Energy calculations
- Feature validation
- Model training logic
- R² calculation
- Data aggregation

✅ **Your Focus:**
- Voice recognition
- Conversation flow
- API calls
- User experience
- Error messages in natural language
- TTS quality

---

## 🟢 MOHAMAD'S RESPONSIBILITIES (EnMS Backend)

### Your Domain: Data & Machine Learning
You handle **everything Burak's voice commands trigger** on the backend.

### Core Tasks

#### 1. **Endpoint: POST /ovos/train-baseline** ✅ DONE
**Status:** 95% complete, needs minor enhancements

**What It Does:**
1. Looks up SEU by name + energy source
2. Validates features exist
3. Fetches daily aggregated energy data
4. Trains Linear Regression model
5. Calculates R², RMSE, MAE
6. Saves model to database
7. Returns voice-friendly response

**Current Implementation:** `analytics/api/routes/ovos_training.py`

**Enhancement Needed:** Add more detailed error messages for edge cases

---

#### 2. **Endpoint: POST /ovos/predict-energy** ⚠️ NEW (2 hours)
**Status:** Needs implementation

**What Burak Needs:**
```
POST /api/v1/ovos/predict-energy
{
  "seu_name": "Compressor-1",
  "energy_source": "electricity",
  "features": {
    "production_count": 500,
    "outdoor_temp_c": 22.5
  }
}

Response:
{
  "success": true,
  "message": "Compressor-1 will consume 367 kWh",
  "predicted_energy": 367.5,
  "unit": "kWh"
}
```

**Implementation:**
```python
@router.post("/predict-energy")
async def predict_energy_via_ovos(request: OVOSPredictionRequest):
    # Lookup SEU
    seu = await get_seu_by_name_and_energy_source(
        request.seu_name, 
        request.energy_source
    )
    
    # Get trained model
    model = await baseline_service.get_active_model(seu['machine_ids'][0])
    
    if not model:
        raise HTTPException(404, "No trained model found. Train baseline first.")
    
    # Predict
    prediction = model.predict(request.features)
    
    # Voice-friendly message
    message = f"{request.seu_name} will consume {prediction:.0f} {seu['unit']}"
    
    return {
        "success": True,
        "message": message,
        "predicted_energy": round(prediction, 1),
        "unit": seu['unit']
    }
```

---

#### 3. **Endpoint: GET /ovos/explain-baseline/{seu}/{energy}** ⚠️ NEW (1.5 hours)
**Status:** Needs implementation

**What Burak Needs:**
User says: "Explain the Compressor-1 baseline"

**Response:**
```json
{
  "success": true,
  "seu_name": "Compressor-1",
  "explanation": {
    "accuracy_description": "Highly accurate (99%)",
    "key_drivers": [
      {
        "feature": "production_count",
        "impact": "high",
        "description": "Production count is the strongest energy driver"
      },
      {
        "feature": "pressure_bar",
        "impact": "medium",
        "description": "Higher pressure reduces energy consumption"
      }
    ],
    "sample_scenario": "At 500 units and 22°C, expect 367 kWh consumption"
  }
}
```

**Implementation:**
```python
@router.get("/explain-baseline/{seu_name}/{energy_source}")
async def explain_baseline_via_ovos(seu_name: str, energy_source: str):
    # Get trained model
    model = await get_latest_trained_model(seu_name, energy_source)
    
    # Analyze coefficients
    key_drivers = []
    for feature, coef in model.coefficients.items():
        impact = "high" if abs(coef) > threshold else "medium"
        direction = "increases" if coef > 0 else "reduces"
        
        key_drivers.append({
            "feature": feature,
            "impact": impact,
            "description": f"{feature} {direction} energy consumption"
        })
    
    # Sort by importance
    key_drivers.sort(key=lambda x: abs(x["coefficient"]), reverse=True)
    
    return {
        "success": True,
        "explanation": {
            "accuracy_description": _interpret_r2(model.r_squared),
            "key_drivers": key_drivers[:3],  # Top 3
            "sample_scenario": _generate_sample_prediction(model)
        }
    }
```

---

#### 4. **Enhance Error Messages** (1 hour)
**What:** Make error responses more helpful for voice interface

**Current:**
```json
{"detail": "SEU not found: uuid"}
```

**Better for Voice:**
```json
{
  "success": false,
  "error_code": "SEU_NOT_FOUND",
  "message": "I couldn't find a machine named 'Compressor-99'",
  "suggestion": "Try one of these machines: Compressor-1, HVAC-Main, Boiler-1",
  "available_seus": ["Compressor-1", "HVAC-Main", "Boiler-1"]
}
```

**Implementation:**
```python
async def handle_seu_not_found(seu_name, energy_source):
    # Get similar SEUs
    similar = await find_similar_seus(seu_name, energy_source)
    
    return {
        "success": False,
        "error_code": "SEU_NOT_FOUND",
        "message": f"I couldn't find '{seu_name}' using {energy_source}",
        "suggestion": f"Did you mean: {', '.join(similar[:3])}?",
        "available_seus": similar
    }
```

---

#### 5. **WebSocket Progress Updates** (Optional, 4 hours)
**What:** Send real-time training progress for long jobs

**Flow:**
```
Burak calls API → Training starts (takes 10 seconds)
├─ WebSocket: {"status": "fetching_data", "progress": 10}
├─ WebSocket: {"status": "training", "progress": 50}
├─ WebSocket: {"status": "validating", "progress": 80}
└─ WebSocket: {"status": "complete", "r_squared": 0.99, "progress": 100}

Burak speaks: "Still working... model training in progress... almost done... complete!"
```

---

### Your Deliverables

**New Files:**
```python
analytics/api/routes/ovos_training.py  # Enhancement (prediction, explanation)
analytics/models/ovos.py               # Pydantic models for OVOS endpoints
analytics/services/model_explainer.py  # NEW - Model interpretation logic
```

**New Endpoints:**
- POST /api/v1/ovos/predict-energy
- GET /api/v1/ovos/explain-baseline/{seu}/{energy}
- GET /api/v1/ovos/compare-models (optional)

**Enhanced Endpoints:**
- POST /api/v1/ovos/train-baseline (better error messages)

---

### What You DON'T Need to Worry About

❌ **NOT Your Problem:**
- Voice recognition accuracy
- TTS quality
- OVOS intent patterns
- Multi-turn conversation flow
- User experience polish
- Wake word detection

✅ **Your Focus:**
- Database queries
- ML model training
- Feature validation
- Data aggregation
- API response format
- Error handling
- Performance optimization

---

## 🔄 Integration Points (Where You Work Together)

### 1. **API Contract**
**Mohamad defines, Burak consumes**

**Example:**
```
Mohamad: "I created POST /ovos/train-baseline. Request format is..."
Burak:   "Got it, I'll send that JSON when user says 'train baseline'"
```

### 2. **Error Handling**
**Mohamad provides codes, Burak translates to voice**

**Example:**
```json
// Mohamad's response
{
  "success": false,
  "error_code": "INSUFFICIENT_DATA",
  "message": "Only 3 days of data found, need minimum 7 days",
  "suggestion": "Try year 2025 which has 365 days"
}

// Burak's voice output
"Not enough historical data for that year. I need at least 7 days. 
Try 2025 instead, which has a full year of data."
```

### 3. **Response Format**
**Mohamad provides `message` field for TTS**

**Example:**
```json
{
  "success": true,
  "message": "Compressor-1 baseline trained with 99% accuracy",  // ← Burak speaks this
  "r_squared": 0.99,  // ← Burak can use for detailed response
  "formula_readable": "Energy equals 370 plus 0.0004 times production"  // ← Optional detail
}
```

### 4. **Testing**
**Both test independently, then together**

**Mohamad's Tests:**
```bash
curl -X POST http://localhost:8001/api/v1/ovos/train-baseline \
  -d '{"seu_name": "Compressor-1", ...}'
```

**Burak's Tests:**
```python
# In OVOS skill
response = self.call_enms_api("Compressor-1", "electricity", 2025)
assert response["success"] == True
assert "message" in response
```

**Integration Tests:**
```
1. Burak: "I'll say 'train Compressor-1' to OVOS"
2. Mohamad: "I'll watch the API logs"
3. Both: Verify request arrives correctly
4. Both: Verify response is spoken correctly
```

---

## 📊 Example End-to-End Flow

### User Action: "Train baseline for Compressor-1"

#### Step 1: Burak's Code
```python
# Intent recognized
seu_name = "Compressor-1"
energy_source = "electricity"  # Default or ask user
year = 2025  # Default or ask user
features = []  # Auto-select

# Make API call
response = requests.post(
    "http://enms:8001/api/v1/ovos/train-baseline",
    json={
        "seu_name": seu_name,
        "energy_source": energy_source,
        "features": features,
        "year": year
    }
)
```

#### Step 2: Mohamad's Code
```python
# Endpoint receives request
@router.post("/train-baseline")
async def train_baseline_via_ovos(request: OVOSTrainingRequest):
    # Lookup SEU
    seu = await get_seu_by_name_and_energy_source(
        request.seu_name, 
        request.energy_source
    )
    
    # Train model
    result = await baseline_service.train_baseline(
        machine_id=seu['machine_ids'][0],
        start_date=datetime(request.year, 1, 1),
        end_date=datetime(request.year, 12, 31),
        drivers=request.features if request.features else None
    )
    
    # Build voice message
    message = (
        f"{request.seu_name} {request.energy_source} baseline trained. "
        f"R-squared {result['r_squared']:.2f} ({int(result['r_squared']*100)}% accuracy)"
    )
    
    return {
        "success": True,
        "message": message,
        "r_squared": result['r_squared'],
        # ...
    }
```

#### Step 3: Burak's Code
```python
# Receive response
data = response.json()

if data["success"]:
    # Speak voice-friendly message
    self.speak(data["message"])
    
    # Optional: Offer details
    if self.ask_yesno("Would you like technical details?"):
        self.speak(
            f"The model used {data['samples_count']} days of training data "
            f"with {len(data.get('features', []))} features."
        )
else:
    # Handle error
    self.speak(f"Training failed: {data['message']}")
```

---

## ✅ Quick Checklist

### Burak's Checklist
- [ ] Can recognize "train baseline" intent
- [ ] Can extract SEU name from voice
- [ ] Can ask follow-up questions (energy source, year)
- [ ] Can call Mohamad's API correctly
- [ ] Can handle API timeouts (10-20s for training)
- [ ] Can speak response in natural language
- [ ] Can handle errors gracefully
- [ ] Can list available SEUs
- [ ] Multi-turn conversation works

### Mohamad's Checklist
- [ ] /ovos/train-baseline works (✅ done)
- [ ] /ovos/predict-energy implemented
- [ ] /ovos/explain-baseline implemented
- [ ] Error messages are voice-friendly
- [ ] Response includes `message` field for TTS
- [ ] API handles invalid SEU names
- [ ] API handles invalid energy sources
- [ ] API handles insufficient data
- [ ] Documentation updated

---

## 🎯 Success Criteria

**Definition of Done:**
```
User: "Train baseline for Compressor-1"
OVOS: [Conversation to get details]
OVOS: [Calls Mohamad's API]
OVOS: "Compressor-1 baseline trained with 99% accuracy"
User: "Predict energy at 500 units"
OVOS: "Compressor-1 will consume 367 kilowatt-hours"
```

**Must Work:**
- Single-turn training (quick command)
- Multi-turn training (guided conversation)
- Prediction queries
- Error recovery
- All 4 energy sources (electricity, gas, steam, air)

---

## 📞 When to Sync

**Daily 10-min Check:**
- "What did you complete yesterday?"
- "Any blockers?"
- "What are you working on today?"

**When Burak Gets Stuck:**
- "Mohamad, what's the correct API format for...?"
- "Mohamad, I'm getting this error, what does it mean?"
- "Mohamad, can you add a field to the response for...?"

**When Mohamad Gets Stuck:**
- "Burak, how do you want error messages formatted?"
- "Burak, is this response too technical for voice?"
- "Burak, can you test this endpoint and confirm it works?"

---

## 🎤 Remember

**Burak:** You're the **user's friend** - make it conversational and helpful
**Mohamad:** You're the **data wizard** - make it accurate and fast

**Together:** You're building a voice assistant that teaches machines about their own energy consumption! 🚀

---

Good luck! This is very doable in one week! 💪
