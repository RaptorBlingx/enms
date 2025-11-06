# ✅ OVOS Integration Test Checklist

**Tester:** Burak  
**Date:** _____________  
**OVOS Version:** _____________  
**Backend API:** http://10.33.10.109:8001/api/v1  
**Status:** [ ] Not Started [ ] In Progress [ ] Complete

---

## Pre-Testing: Backend Validation

- [ ] Run `/home/ubuntu/enms/scripts/test_ovos_integration.sh`
- [ ] All 8 backend tests pass
- [ ] Test 1 shows 10 machines
- [ ] Test 5 shows `success: true`
- [ ] Test 6 shows `success: false` with helpful error

**Notes:**
```
_________________________________________________________________________
_________________________________________________________________________
```

---

## Test Category 1: Machine Discovery (5 min)

### Test 1.1: List All Machines
- [ ] **Asked OVOS:** "What machines do you have?"
- [ ] **OVOS Response:** Says "10 machines"
- [ ] **Backend Check:** `curl -s http://10.33.10.109:8001/api/v1/ovos/seus | jq .total_count`
- [ ] **Backend Response:** `10`
- [ ] **MATCH:** ✅ Yes / ❌ No

**OVOS said:**
```
_________________________________________________________________________
```

**Backend said:**
```
_________________________________________________________________________
```

---

### Test 1.2: List Natural Gas Machines
- [ ] **Asked OVOS:** "What machines use natural gas?"
- [ ] **OVOS Response:** Says "1 machine" and "Boiler-1 Natural Gas Burner"
- [ ] **Backend Check:** `curl -s "http://10.33.10.109:8001/api/v1/ovos/seus?energy_source=natural_gas" | jq .`
- [ ] **MATCH:** ✅ Yes / ❌ No

---

### Test 1.3: List Electrical Machines
- [ ] **Asked OVOS:** "Show me machines using electricity"
- [ ] **OVOS Response:** Says "8 machines"
- [ ] **Backend Check:** `curl -s "http://10.33.10.109:8001/api/v1/ovos/seus?energy_source=electricity" | jq .total_count`
- [ ] **MATCH:** ✅ Yes / ❌ No

---

## Test Category 2: Energy Source Information (3 min)

### Test 2.1: List Energy Sources
- [ ] **Asked OVOS:** "What energy sources do you monitor?"
- [ ] **OVOS Response:** Mentions "4 energy sources"
- [ ] **Backend Check:** `curl -s http://10.33.10.109:8001/api/v1/ovos/energy-sources | jq .total_count`
- [ ] **Backend Response:** `4`
- [ ] **MATCH:** ✅ Yes / ❌ No

---

### Test 2.2: Electricity Features
- [ ] **Asked OVOS:** "What factors affect electricity consumption?"
- [ ] **OVOS Response:** Mentions "22 features"
- [ ] **Backend Check:** `curl -s http://10.33.10.109:8001/api/v1/features/electricity | jq .total_features`
- [ ] **Backend Response:** `22`
- [ ] **MATCH:** ✅ Yes / ❌ No

---

## Test Category 3: Baseline Training (10 min)

### Test 3.1: Train Baseline - Success (High Accuracy)
- [ ] **Asked OVOS:** "Train baseline for Compressor-EU-1"
- [ ] **OVOS Response:** Says "success" or "trained successfully"
- [ ] **OVOS Response:** Mentions R² or accuracy (~99%)
- [ ] **OVOS Response:** Mentions sample count (~7,191)
- [ ] **Training Time:** _______ seconds (should be < 30)
- [ ] **Backend Check:**
```bash
curl -s -X POST http://10.33.10.109:8001/api/v1/ovos/train-baseline \
  -H "Content-Type: application/json" \
  -d '{"seu_name": "Compressor-EU-1", "energy_source": "electricity", "features": [], "year": 2025}' | jq '{success, r_squared, samples_count}'
```
- [ ] **Backend Response:** `success: true`
- [ ] **Backend Response:** `r_squared: ~0.99`
- [ ] **MATCH:** ✅ Yes / ❌ No

**OVOS said:**
```
_________________________________________________________________________
_________________________________________________________________________
```

**Backend JSON:**
```json
_________________________________________________________________________
_________________________________________________________________________
```

---

### Test 3.2: Train Baseline - Natural Gas
- [ ] **Asked OVOS:** "Train baseline for Boiler-1 Natural Gas Burner"
- [ ] **OVOS Response:** Says "success"
- [ ] **OVOS Response:** Mentions "natural_gas" or "natural gas"
- [ ] **OVOS Response:** Mentions R² (~98%)
- [ ] **Training Time:** _______ seconds
- [ ] **Backend Check:** (Use curl with natural_gas)
- [ ] **MATCH:** ✅ Yes / ❌ No

---

### Test 3.3: Train Baseline - Low Accuracy
- [ ] **Asked OVOS:** "Train baseline for HVAC-Main"
- [ ] **OVOS Response:** Says "success" (even though accuracy is low)
- [ ] **OVOS Response:** Mentions low R² (~6%)
- [ ] **OVOS Response:** Warns about low accuracy (optional but nice)
- [ ] **Backend Check:** (Use curl with HVAC-Main)
- [ ] **MATCH:** ✅ Yes / ❌ No

---

### Test 3.4: Train Baseline - Error Case
- [ ] **Asked OVOS:** "Train baseline for XYZ-Machine"
- [ ] **OVOS Response:** Says "not found" or "couldn't find"
- [ ] **OVOS Response:** Suggests alternative machines
- [ ] **OVOS Response:** Does NOT say "success"
- [ ] **Backend Check:**
```bash
curl -s -X POST http://10.33.10.109:8001/api/v1/ovos/train-baseline \
  -H "Content-Type: application/json" \
  -d '{"seu_name": "XYZ-Machine", "energy_source": "electricity", "features": [], "year": 2025}' | jq .
```
- [ ] **Backend Response:** `success: false`
- [ ] **MATCH:** ✅ Yes / ❌ No

---

## Test Category 4: Model Information (3 min)

### Test 4.1: List Trained Machines
- [ ] **Asked OVOS:** "Which machines have trained baselines?"
- [ ] **OVOS Response:** Lists 6+ machines with trained models
- [ ] **Backend Check:** `curl -s http://10.33.10.109:8001/api/v1/ovos/seus | jq '[.seus[] | select(.baseline_year != null)]'`
- [ ] **MATCH:** ✅ Yes / ❌ No

---

### Test 4.2: Check Specific Machine Status
- [ ] **Asked OVOS:** "Does Compressor-EU-1 have a baseline?"
- [ ] **OVOS Response:** Says "yes" or confirms it exists
- [ ] **OVOS Response:** Mentions accuracy or year
- [ ] **Backend Check:** `curl -s http://10.33.10.109:8001/api/v1/ovos/seus | jq '.seus[] | select(.name=="Compressor-EU-1")'`
- [ ] **MATCH:** ✅ Yes / ❌ No

---

## Test Category 5: Multi-Turn Conversations (10 min)

### Test 5.1: Guided Training Workflow
- [ ] **User:** "I want to train a baseline"
- [ ] **OVOS:** Asks "Which machine?"
- [ ] **User:** "Compressor-1"
- [ ] **OVOS:** Asks "Which energy source?"
- [ ] **User:** "Electricity"
- [ ] **OVOS:** Asks about feature selection
- [ ] **User:** "Yes" (auto-select)
- [ ] **OVOS:** Trains model and speaks result
- [ ] **Workflow completed successfully:** ✅ Yes / ❌ No

**Notes:**
```
_________________________________________________________________________
_________________________________________________________________________
```

---

### Test 5.2: Error Recovery Workflow
- [ ] **User:** "Train baseline for InvalidMachine"
- [ ] **OVOS:** Says machine not found
- [ ] **OVOS:** Lists available machines
- [ ] **OVOS:** Asks user to pick one
- [ ] **User:** Picks "Compressor-1"
- [ ] **OVOS:** Trains Compressor-1 successfully
- [ ] **Error recovery worked:** ✅ Yes / ❌ No

**Notes:**
```
_________________________________________________________________________
_________________________________________________________________________
```

---

## Performance & Reliability (5 min)

### Timeout Handling
- [ ] Training completes in < 30 seconds
- [ ] OVOS doesn't crash if API is slow
- [ ] OVOS handles network errors gracefully

### Edge Cases
- [ ] Case-sensitive machine names handled correctly
- [ ] "natural gas" vs "natural_gas" conversion works
- [ ] Empty responses don't crash OVOS
- [ ] Long machine names don't break TTS

---

## Final Validation

### All Test Results
- **Total Tests:** 17
- **Passed:** _____ / 17
- **Failed:** _____ / 17
- **Pass Rate:** _____ %

### Critical Tests (Must Pass)
- [ ] List machines (1.1)
- [ ] Train baseline success (3.1)
- [ ] Train baseline error (3.4)
- [ ] Multi-turn conversation (5.1)

### Integration Status
- [ ] **READY FOR PRODUCTION** - All tests pass
- [ ] **NEEDS WORK** - Some tests fail (see notes below)
- [ ] **BLOCKED** - Backend issues found (contact Mohamad)

---

## Issues Found

### Issue 1
**Category:** _____________  
**Test:** _____________  
**Description:**
```
_________________________________________________________________________
_________________________________________________________________________
```
**Root Cause:** [ ] OVOS Bug [ ] Backend Bug [ ] Unclear

---

### Issue 2
**Category:** _____________  
**Test:** _____________  
**Description:**
```
_________________________________________________________________________
_________________________________________________________________________
```
**Root Cause:** [ ] OVOS Bug [ ] Backend Bug [ ] Unclear

---

### Issue 3
**Category:** _____________  
**Test:** _____________  
**Description:**
```
_________________________________________________________________________
_________________________________________________________________________
```
**Root Cause:** [ ] OVOS Bug [ ] Backend Bug [ ] Unclear

---

## Sign-Off

**Tested By:** Burak  
**Date:** _____________  
**Time Spent:** _____ minutes  
**Status:** [ ] PASS [ ] FAIL  

**Mohamad Review:**  
**Reviewed By:** _____________  
**Date:** _____________  
**Comments:**
```
_________________________________________________________________________
_________________________________________________________________________
```

---

## Quick Reference Commands

```bash
# Verify backend
/home/ubuntu/enms/scripts/test_ovos_integration.sh

# List all machines
curl -s http://10.33.10.109:8001/api/v1/ovos/seus | jq .

# List energy sources
curl -s http://10.33.10.109:8001/api/v1/ovos/energy-sources | jq .

# Train baseline
curl -s -X POST http://10.33.10.109:8001/api/v1/ovos/train-baseline \
  -H "Content-Type: application/json" \
  -d '{"seu_name": "Compressor-EU-1", "energy_source": "electricity", "features": [], "year": 2025}' | jq .

# Filter by energy source
curl -s "http://10.33.10.109:8001/api/v1/ovos/seus?energy_source=electricity" | jq .

# Get features
curl -s http://10.33.10.109:8001/api/v1/features/electricity | jq .
```
