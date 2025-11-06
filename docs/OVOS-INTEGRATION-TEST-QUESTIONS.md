# 🧪 OVOS Integration Test Questions & Expected Responses

**Purpose:** Validate OVOS integration with EnMS backend API  
**Created:** November 6, 2025  
**API Base URL:** `http://10.33.10.109:8001/api/v1`  
**Status:** ✅ All curl commands tested and verified

---

## 📋 How to Use This Document

For each test question:
1. **User Question**: What the user would ask OVOS
2. **Expected OVOS Response**: What OVOS should speak back
3. **Backend API Call**: Exact curl command to verify
4. **Backend Response**: JSON response from our API
5. **Validation**: How to compare OVOS output with backend data

**Important**: If OVOS response doesn't match the backend response, the issue is in OVOS integration, NOT in EnMS backend!

---

## 🎯 Category 1: Machine Discovery

### Test 1.1: List All Machines

**User Question:**
> "What machines do you have?" / "List all machines" / "Show me available equipment"

**Expected OVOS Response:**
> "I found 10 machines in the system: Boiler-1 Electrical System, Boiler-1 Natural Gas Burner, Boiler-1 Steam Production, Compressor-1, Compressor-EU-1, Conveyor-A, HVAC-EU-North, HVAC-Main, Hydraulic-Pump-1, and Injection-Molding-1."

**Backend API Call:**
```bash
curl -s http://10.33.10.109:8001/api/v1/ovos/seus | jq '{total_count, machine_names: [.seus[].name]}'
```

**Backend Response:**
```json
{
  "total_count": 10,
  "machine_names": [
    "Boiler-1 Electrical System",
    "Boiler-1 Natural Gas Burner",
    "Boiler-1 Steam Production",
    "Compressor-1",
    "Compressor-EU-1",
    "Conveyor-A",
    "HVAC-EU-North",
    "HVAC-Main",
    "Hydraulic-Pump-1",
    "Injection-Molding-1"
  ]
}
```

**Validation Checklist:**
- ✅ OVOS mentions "10 machines"
- ✅ OVOS lists all 10 machine names
- ✅ Machine names match exactly (case-sensitive)

---

### Test 1.2: List Machines by Energy Source

**User Question:**
> "What machines use natural gas?" / "Show me natural gas equipment"

**Expected OVOS Response:**
> "I found 1 machine using natural gas: Boiler-1 Natural Gas Burner."

**Backend API Call:**
```bash
curl -s "http://10.33.10.109:8001/api/v1/ovos/seus?energy_source=natural_gas" | jq '{total_count, filtered_by, machine_names: [.seus[].name]}'
```

**Backend Response:**
```json
{
  "total_count": 1,
  "filtered_by": "natural_gas",
  "machine_names": [
    "Boiler-1 Natural Gas Burner"
  ]
}
```

**Validation Checklist:**
- ✅ OVOS mentions "1 machine"
- ✅ OVOS says "Boiler-1 Natural Gas Burner"
- ✅ OVOS confirms energy source is "natural gas"

---

### Test 1.3: List Machines Using Electricity

**User Question:**
> "What electrical equipment do you have?" / "Show me machines using electricity"

**Expected OVOS Response:**
> "I found 8 machines using electricity: Boiler-1 Electrical System, Compressor-1, Compressor-EU-1, Conveyor-A, HVAC-EU-North, HVAC-Main, Hydraulic-Pump-1, and Injection-Molding-1."

**Backend API Call:**
```bash
curl -s "http://10.33.10.109:8001/api/v1/ovos/seus?energy_source=electricity" | jq '{total_count, filtered_by, machine_names: [.seus[].name]}'
```

**Backend Response:**
```json
{
  "total_count": 8,
  "filtered_by": "electricity",
  "machine_names": [
    "Boiler-1 Electrical System",
    "Compressor-1",
    "Compressor-EU-1",
    "Conveyor-A",
    "HVAC-EU-North",
    "HVAC-Main",
    "Hydraulic-Pump-1",
    "Injection-Molding-1"
  ]
}
```

**Validation Checklist:**
- ✅ OVOS mentions "8 machines"
- ✅ OVOS lists all 8 electrical machines
- ✅ No non-electrical machines included

---

## 🔋 Category 2: Energy Source Information

### Test 2.1: List All Energy Sources

**User Question:**
> "What energy sources do you monitor?" / "What types of energy can you track?"

**Expected OVOS Response:**
> "I monitor 4 energy sources: compressed air measured in normal cubic meters, electricity measured in kilowatt-hours, natural gas measured in cubic meters, and steam measured in kilograms."

**Backend API Call:**
```bash
curl -s http://10.33.10.109:8001/api/v1/ovos/energy-sources | jq '{total_count, energy_sources: [.energy_sources[] | {name, unit, description}]}'
```

**Backend Response:**
```json
{
  "total_count": 4,
  "energy_sources": [
    {
      "name": "compressed_air",
      "unit": "Nm³",
      "description": "Compressed air for pneumatic systems"
    },
    {
      "name": "electricity",
      "unit": "kWh",
      "description": "Electrical power from grid"
    },
    {
      "name": "natural_gas",
      "unit": "m³",
      "description": "Natural gas for heating/boilers"
    },
    {
      "name": "steam",
      "unit": "kg",
      "description": "Process steam"
    }
  ]
}
```

**Validation Checklist:**
- ✅ OVOS mentions "4 energy sources"
- ✅ OVOS mentions all 4: compressed air, electricity, natural gas, steam
- ✅ OVOS mentions units correctly (Nm³, kWh, m³, kg)

---

### Test 2.2: Get Features for Electricity

**User Question:**
> "What factors affect electricity consumption?" / "What features are available for electricity?"

**Expected OVOS Response:**
> "I track 22 features for electricity, including average current, load factor, power factor, outdoor temperature, production count, and 17 others."

**Backend API Call:**
```bash
curl -s http://10.33.10.109:8001/api/v1/features/electricity | jq '{energy_source, total_features, sample_features: [.features[0:6] | .[].feature_name]}'
```

**Backend Response:**
```json
{
  "energy_source": "electricity",
  "total_features": 22,
  "sample_features": [
    "avg_current_a",
    "avg_cycle_time_sec",
    "avg_load_factor",
    "avg_power_factor",
    "avg_power_kw",
    "avg_throughput"
  ]
}
```

**Validation Checklist:**
- ✅ OVOS mentions "22 features"
- ✅ OVOS confirms energy source is "electricity"
- ✅ OVOS can list some example features

---

### Test 2.3: Get Features for Natural Gas

**User Question:**
> "What factors affect natural gas consumption?" / "What features can I use for natural gas?"

**Expected OVOS Response:**
> "I track 10 features for natural gas, including average flow rate, outdoor temperature, pressure, production count, and 6 others."

**Backend API Call:**
```bash
curl -s http://10.33.10.109:8001/api/v1/features/natural_gas | jq '{energy_source, total_features, sample_features: [.features[0:5] | .[].feature_name]}'
```

**Backend Response:**
```json
{
  "energy_source": "natural_gas",
  "total_features": 10,
  "sample_features": [
    "avg_calorific_value",
    "avg_flow_rate_m3h",
    "avg_gas_temp_c",
    "avg_pressure_bar",
    "consumption_m3"
  ]
}
```

**Validation Checklist:**
- ✅ OVOS mentions "10 features"
- ✅ OVOS confirms energy source is "natural_gas"
- ✅ OVOS can list example features

---

## 🎓 Category 3: Baseline Training (Main Feature)

### Test 3.1: Train Baseline - Success Case (High Accuracy)

**User Question:**
> "Train a baseline for Compressor-EU-1" / "Run regression analysis on Compressor-EU-1"

**Expected OVOS Response:**
> "Compressor-EU-1 electricity baseline trained successfully. R-squared 0.99, which means 99% accuracy. The model used 7,191 days of data. Energy equals 598.692 plus 0.000006 times total production count minus 1.095568 times average pressure bar plus 0.021066 times average machine temperature celsius minus 591.369831 times average load factor."

**Backend API Call:**
```bash
curl -s -X POST http://10.33.10.109:8001/api/v1/ovos/train-baseline \
  -H "Content-Type: application/json" \
  -d '{"seu_name": "Compressor-EU-1", "energy_source": "electricity", "features": [], "year": 2025}' | jq .
```

**Backend Response:**
```json
{
  "success": true,
  "message": "Compressor-EU-1 electricity baseline trained successfully. R-squared 0.99 (99% accuracy). Energy equals 598.692 plus 0.000006 times total production count minus 1.095568 times avg pressure bar plus 0.021066 times avg machine temp c minus 591.369831 times avg load factor",
  "seu_name": "Compressor-EU-1",
  "energy_source": "electricity",
  "r_squared": 0.9862887014423478,
  "rmse": 2.416720735948801,
  "formula_readable": "Energy equals 598.692 plus 0.000006 times total production count minus 1.095568 times avg pressure bar plus 0.021066 times avg machine temp c minus 591.369831 times avg load factor",
  "formula_technical": "E = 598.692 + 0.000006×T - 1.095568×A + 0.021066×A - 591.369831×A",
  "samples_count": 7191,
  "trained_at": "2025-11-06T06:42:20.008808",
  "error_details": null
}
```

**Validation Checklist:**
- ✅ OVOS confirms success
- ✅ OVOS mentions "Compressor-EU-1"
- ✅ OVOS mentions R² value (~0.99 or 99%)
- ✅ OVOS mentions sample count (7,191)
- ✅ OVOS speaks the formula OR the message field
- ✅ `success` field is `true`

---

### Test 3.2: Train Baseline - Natural Gas

**User Question:**
> "Train baseline for Boiler-1 Natural Gas Burner" / "Analyze natural gas for Boiler-1"

**Expected OVOS Response:**
> "Boiler-1 Natural Gas Burner natural_gas baseline trained successfully. R-squared 0.98, which means 98% accuracy. The model used 164 days of data. Energy equals negative 22.243 plus 0.187169 times total production count plus 64.270406 times average load factor."

**Backend API Call:**
```bash
curl -s -X POST http://10.33.10.109:8001/api/v1/ovos/train-baseline \
  -H "Content-Type: application/json" \
  -d '{"seu_name": "Boiler-1 Natural Gas Burner", "energy_source": "natural_gas", "features": [], "year": 2025}' | jq .
```

**Backend Response:**
```json
{
  "success": true,
  "message": "Boiler-1 Natural Gas Burner natural_gas baseline trained successfully. R-squared 0.98 (98% accuracy). Energy equals -22.243 plus 0.187169 times total production count plus 64.270406 times avg load factor",
  "seu_name": "Boiler-1 Natural Gas Burner",
  "energy_source": "natural_gas",
  "r_squared": 0.9818574572404973,
  "rmse": 3.10789379148825,
  "formula_readable": "Energy equals -22.243 plus 0.187169 times total production count plus 64.270406 times avg load factor",
  "formula_technical": "E = -22.243 + 0.187169×T + 64.270406×A",
  "samples_count": 164,
  "trained_at": "2025-11-06T06:44:28.967519",
  "error_details": null
}
```

**Validation Checklist:**
- ✅ OVOS confirms success
- ✅ OVOS mentions "Boiler-1 Natural Gas Burner"
- ✅ OVOS mentions energy source "natural_gas"
- ✅ OVOS mentions R² value (~0.98 or 98%)
- ✅ OVOS mentions sample count (164)

---

### Test 3.3: Train Baseline - Low Accuracy Case

**User Question:**
> "Train baseline for HVAC-Main"

**Expected OVOS Response:**
> "HVAC-Main electricity baseline trained successfully. R-squared 0.06, which means 6% accuracy. The model used 6,552 days of data. Energy equals 0.010 minus 0.000115 times average machine temperature celsius plus 0.000000 times average load factor. Note: This accuracy is quite low, you may want to check if the machine has consistent operating patterns."

**Backend API Call:**
```bash
curl -s -X POST http://10.33.10.109:8001/api/v1/ovos/train-baseline \
  -H "Content-Type: application/json" \
  -d '{"seu_name": "HVAC-Main", "energy_source": "electricity", "features": [], "year": 2025}' | jq .
```

**Backend Response:**
```json
{
  "success": true,
  "message": "HVAC-Main electricity baseline trained successfully. R-squared 0.06 (6% accuracy). Energy equals 0.010 minus 0.000115 times avg machine temp c plus 0.000000 times avg load factor",
  "seu_name": "HVAC-Main",
  "energy_source": "electricity",
  "r_squared": 0.056972351924586495,
  "rmse": 0.004280642454229357,
  "formula_readable": "Energy equals 0.010 minus 0.000115 times avg machine temp c plus 0.000000 times avg load factor",
  "formula_technical": "E = 0.010 - 0.000115×A + 0.000000×A",
  "samples_count": 6552,
  "trained_at": "2025-11-06T06:44:19.286674",
  "error_details": null
}
```

**Validation Checklist:**
- ✅ OVOS confirms success (even though accuracy is low)
- ✅ OVOS mentions "HVAC-Main"
- ✅ OVOS mentions R² value (~0.06 or 6%)
- ✅ OVOS should warn user about low accuracy
- ✅ `success` field is still `true`

---

### Test 3.4: Train Baseline - Error Case (Invalid Machine)

**User Question:**
> "Train baseline for XYZ-Machine" / "Run analysis on SuperCompressor"

**Expected OVOS Response:**
> "I couldn't find a machine named XYZ-Machine using electricity. Would you like me to list available machines? Try one of these: Boiler-1 Electrical System, Compressor-1, Compressor-EU-1."

**Backend API Call:**
```bash
curl -s -X POST http://10.33.10.109:8001/api/v1/ovos/train-baseline \
  -H "Content-Type: application/json" \
  -d '{"seu_name": "NonExistentMachine", "energy_source": "electricity", "features": [], "year": 2025}' | jq .
```

**Backend Response:**
```json
{
  "success": false,
  "message": "I couldn't find a machine named 'NonExistentMachine' using electricity. Try one of these: Boiler-1 Electrical System, Compressor-1, Compressor-EU-1.",
  "seu_name": "NonExistentMachine",
  "energy_source": "electricity",
  "r_squared": null,
  "rmse": null,
  "formula_readable": null,
  "formula_technical": null,
  "samples_count": null,
  "trained_at": null,
  "error_details": "SEU_NOT_FOUND: Available SEUs: Boiler-1 Electrical System, Compressor-1, Compressor-EU-1, Conveyor-A, HVAC-EU-North"
}
```

**Validation Checklist:**
- ✅ OVOS indicates error/failure
- ✅ OVOS says machine was not found
- ✅ OVOS suggests alternative machines
- ✅ `success` field is `false`
- ✅ OVOS does NOT say "training successful"

---

## 🔍 Category 4: Model Information

### Test 4.1: Check Training Status

**User Question:**
> "Which machines have trained baselines?" / "Show me trained models"

**Expected OVOS Response:**
> "I found 6 machines with trained baselines: Compressor-1 (47% accuracy, trained in 2025), Compressor-EU-1 (100% accuracy, trained in 2025), Conveyor-A (100% accuracy, trained in 2025), HVAC-EU-North (100% accuracy, trained in 2025), HVAC-Main (100% accuracy, trained in 2025), and Hydraulic-Pump-1 (100% accuracy, trained in 2025)."

**Backend API Call:**
```bash
curl -s http://10.33.10.109:8001/api/v1/ovos/seus | jq '{trained_machines: [.seus[] | select(.baseline_year != null) | {name, r_squared, baseline_year}]}'
```

**Backend Response:**
```json
{
  "trained_machines": [
    {
      "name": "Compressor-1",
      "r_squared": 0.4661,
      "baseline_year": 2025
    },
    {
      "name": "Compressor-EU-1",
      "r_squared": 0.9975,
      "baseline_year": 2025
    },
    {
      "name": "Conveyor-A",
      "r_squared": 0.9998,
      "baseline_year": 2025
    },
    {
      "name": "HVAC-EU-North",
      "r_squared": 1.0,
      "baseline_year": 2025
    },
    {
      "name": "HVAC-Main",
      "r_squared": 1.0,
      "baseline_year": 2025
    },
    {
      "name": "Hydraulic-Pump-1",
      "r_squared": 0.9995,
      "baseline_year": 2025
    }
  ]
}
```

**Validation Checklist:**
- ✅ OVOS counts trained machines correctly (6)
- ✅ OVOS lists machine names
- ✅ OVOS mentions R² values (as percentages)
- ✅ OVOS mentions baseline year (2025)

---

### Test 4.2: Check Specific Machine Status

**User Question:**
> "Does Compressor-EU-1 have a baseline?" / "What's the accuracy of Compressor-EU-1?"

**Expected OVOS Response:**
> "Yes, Compressor-EU-1 has a trained baseline from 2025 with 100% accuracy (R-squared 0.9975)."

**Backend API Call:**
```bash
curl -s http://10.33.10.109:8001/api/v1/ovos/seus | jq '.seus[] | select(.name=="Compressor-EU-1") | {name, baseline_year, r_squared}'
```

**Backend Response:**
```json
{
  "name": "Compressor-EU-1",
  "baseline_year": 2025,
  "r_squared": 0.9975
}
```

**Validation Checklist:**
- ✅ OVOS confirms baseline exists
- ✅ OVOS mentions year (2025)
- ✅ OVOS mentions R² or accuracy (~100% or 0.9975)

---

## 🧮 Category 5: Complex Multi-Turn Conversations

### Test 5.1: Guided Training Workflow

**User Turns:**
1. User: "I want to train a baseline"
2. OVOS: "Which machine would you like to train?"
3. User: "Compressor-1"
4. OVOS: "Which energy source? Available options are: electricity, natural gas, steam, compressed air."
5. User: "Electricity"
6. OVOS: "Should I automatically select features for maximum accuracy?"
7. User: "Yes"
8. OVOS: [Calls training API]
9. OVOS: "Compressor-1 electricity baseline trained successfully with 47% accuracy using 7,191 days of data."

**Backend API Calls (in sequence):**

1. List available machines:
```bash
curl -s http://10.33.10.109:8001/api/v1/ovos/seus | jq '[.seus[].name]'
```

2. List energy sources:
```bash
curl -s http://10.33.10.109:8001/api/v1/ovos/energy-sources | jq '[.energy_sources[].name]'
```

3. Train baseline:
```bash
curl -s -X POST http://10.33.10.109:8001/api/v1/ovos/train-baseline \
  -H "Content-Type: application/json" \
  -d '{"seu_name": "Compressor-1", "energy_source": "electricity", "features": [], "year": 2025}' | jq .
```

**Validation Checklist:**
- ✅ OVOS asks for machine name
- ✅ OVOS asks for energy source
- ✅ OVOS asks about feature selection
- ✅ OVOS makes correct API call with user's choices
- ✅ OVOS speaks final result

---

### Test 5.2: Error Recovery Workflow

**User Turns:**
1. User: "Train baseline for SuperMachine"
2. OVOS: "I couldn't find SuperMachine. Let me list available machines..."
3. OVOS: "Available machines are: Compressor-1, Compressor-EU-1, HVAC-Main... Which one would you like?"
4. User: "Compressor-1"
5. OVOS: [Trains Compressor-1]

**Backend API Calls:**

1. Attempt invalid training:
```bash
curl -s -X POST http://10.33.10.109:8001/api/v1/ovos/train-baseline \
  -H "Content-Type: application/json" \
  -d '{"seu_name": "SuperMachine", "energy_source": "electricity", "features": [], "year": 2025}' | jq .
```

2. List valid machines:
```bash
curl -s http://10.33.10.109:8001/api/v1/ovos/seus | jq '[.seus[].name]'
```

3. Train correct machine:
```bash
curl -s -X POST http://10.33.10.109:8001/api/v1/ovos/train-baseline \
  -H "Content-Type: application/json" \
  -d '{"seu_name": "Compressor-1", "energy_source": "electricity", "features": [], "year": 2025}' | jq .
```

**Validation Checklist:**
- ✅ OVOS detects error from API (`success: false`)
- ✅ OVOS lists alternative machines
- ✅ OVOS retries with valid machine name

---

## 📊 Category 6: Information Queries

### Test 6.1: What Can OVOS Do?

**User Question:**
> "What can you do?" / "How can you help me?" / "What features do you have?"

**Expected OVOS Response:**
> "I can help you with energy management tasks like: listing available machines and energy sources, training energy baselines using regression analysis, checking model accuracy and status, and explaining energy consumption patterns. What would you like to do?"

**Backend API Call:**
```bash
# No direct API call - this is OVOS skill description
# But OVOS should be aware of all available endpoints
curl -s http://10.33.10.109:8001/api/v1/ovos/energy-sources | jq '{total_sources: .total_count}'
curl -s http://10.33.10.109:8001/api/v1/ovos/seus | jq '{total_machines: .total_count}'
```

**Validation Checklist:**
- ✅ OVOS mentions key capabilities
- ✅ OVOS mentions "baseline" or "regression"
- ✅ OVOS offers to help

---

## 🎯 Quick Validation Script

Run this script to get all expected responses in one go:

```bash
#!/bin/bash
echo "=== Test 1: List all machines ==="
curl -s http://10.33.10.109:8001/api/v1/ovos/seus | jq '{total: .total_count, names: [.seus[].name]}'

echo -e "\n=== Test 2: List energy sources ==="
curl -s http://10.33.10.109:8001/api/v1/ovos/energy-sources | jq '{total: .total_count, sources: [.energy_sources[] | {name, unit}]}'

echo -e "\n=== Test 3: Train Compressor-EU-1 ==="
curl -s -X POST http://10.33.10.109:8001/api/v1/ovos/train-baseline \
  -H "Content-Type: application/json" \
  -d '{"seu_name": "Compressor-EU-1", "energy_source": "electricity", "features": [], "year": 2025}' | jq '{success, message, r_squared, samples_count}'

echo -e "\n=== Test 4: Invalid machine ==="
curl -s -X POST http://10.33.10.109:8001/api/v1/ovos/train-baseline \
  -H "Content-Type: application/json" \
  -d '{"seu_name": "InvalidMachine", "energy_source": "electricity", "features": [], "year": 2025}' | jq '{success, message}'

echo -e "\n=== Test 5: Trained machines ==="
curl -s http://10.33.10.109:8001/api/v1/ovos/seus | jq '{trained: [.seus[] | select(.baseline_year != null) | {name, r_squared}]}'
```

Save as `test_ovos_integration.sh` and run:
```bash
chmod +x test_ovos_integration.sh
./test_ovos_integration.sh
```

---

## ✅ Pass/Fail Criteria

### For Each Test Question:

**PASS** if:
- ✅ OVOS response contains key information from backend
- ✅ Numbers match (counts, R², etc.)
- ✅ Machine names are exact
- ✅ Error handling works (invalid input → helpful error)

**FAIL** if:
- ❌ OVOS returns different numbers than backend
- ❌ OVOS says "success" when `success: false`
- ❌ OVOS can't handle errors gracefully
- ❌ OVOS times out (training takes 3-10 seconds max)

---

## 🚨 Critical Notes for Burak

### 1. **Message Field is TTS-Ready**
The `message` field in API responses is designed for direct speech output. Just speak it!

```python
response = call_api("/ovos/train-baseline", ...)
self.speak(response["message"])  # ← Perfect!
```

### 2. **Timeout Settings**
Training can take up to 10 seconds. Set timeout:
```python
response = requests.post(url, json=data, timeout=30)
```

### 3. **Energy Source Format**
- User says: "natural gas"
- API expects: "natural_gas" (with underscore)

```python
energy_source = user_input.replace(" ", "_").lower()
```

### 4. **Case Sensitivity**
Machine names are case-sensitive:
- ✅ "Compressor-EU-1"
- ❌ "compressor-eu-1"

### 5. **Empty Features Array**
Always use `features: []` for auto-selection (best accuracy):
```json
{
  "seu_name": "Compressor-1",
  "energy_source": "electricity",
  "features": [],  // ← Auto-select for best results
  "year": 2025
}
```

---

## 📞 When to Escalate to Mohamad

**Contact Mohamad if:**
- ❌ API returns 500 error
- ❌ Training takes > 30 seconds
- ❌ Response format doesn't match this document
- ❌ `success: true` but no data returned

**Don't contact Mohamad for:**
- ✅ OVOS intent recognition issues
- ✅ TTS pronunciation problems
- ✅ Your Python code structure
- ✅ How to use OVOS framework

---

## 📝 Test Execution Checklist

Before saying "OVOS integration is complete":

- [ ] Test all 15 sample questions
- [ ] Run validation script
- [ ] Test multi-turn conversations (5.1, 5.2)
- [ ] Test error handling (3.4, 5.2)
- [ ] Compare OVOS output with expected responses
- [ ] Verify timeouts work (30 seconds for training)
- [ ] Test with valid AND invalid inputs
- [ ] Document any API issues found

---

## 🎓 Summary

**Total Test Cases:** 15 questions + 2 multi-turn scenarios = 17 tests  
**API Endpoints Covered:** 5 endpoints  
**Expected Test Duration:** 10-15 minutes  
**Pass Criteria:** All validations ✅

**Remember:** If OVOS output doesn't match backend response, it's an OVOS integration bug, NOT an EnMS backend bug!

Good luck with testing! 🚀
