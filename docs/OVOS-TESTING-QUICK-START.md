# 🎯 OVOS Integration Testing - Quick Start for Burak

**Created:** November 6, 2025  
**Purpose:** Test questions to validate OVOS integration with EnMS backend  
**Status:** ✅ All backend APIs tested and verified working

---

## 📁 Files for Burak

1. **`OVOS-INTEGRATION-TEST-QUESTIONS.md`** - Complete test guide with 17 test scenarios
2. **`test_ovos_integration.sh`** - Automated backend validation script
3. **`BURAK-READY-ENDPOINTS.md`** - Original API reference documentation

---

## 🚀 Quick Start (3 Steps)

### Step 1: Verify Backend is Working (2 minutes)

Run this command on the server:
```bash
/home/ubuntu/enms/scripts/test_ovos_integration.sh
```

**Expected Output:**
- ✅ All 8 tests pass
- ✅ Test 1 shows 10 machines
- ✅ Test 5 has `success: true`
- ✅ Test 6 has `success: false` with helpful error

If this passes, backend is ready! 🎉

---

### Step 2: Test OVOS with Sample Questions (10 minutes)

Use questions from `OVOS-INTEGRATION-TEST-QUESTIONS.md`:

#### Easy Tests (Start Here):
1. "What machines do you have?" → Should list 10 machines
2. "List energy sources" → Should list 4 energy sources
3. "Train baseline for Compressor-EU-1" → Should train successfully with 99% accuracy

#### Error Handling Tests:
4. "Train baseline for XYZ-Machine" → Should say "machine not found" and suggest alternatives

#### Complex Tests:
5. Multi-turn conversation (guided training)
6. Error recovery workflow

---

### Step 3: Compare Outputs (5 minutes)

For each question:

1. **Ask OVOS the question**
2. **Run the corresponding curl command** (from the test doc)
3. **Compare OVOS response with backend JSON**

**Example:**

```bash
# User asks: "What machines do you have?"

# Run backend test:
curl -s http://10.33.10.109:8001/api/v1/ovos/seus | jq '{total_count, names: [.seus[].name]}'

# Backend says: 10 machines, lists names
# OVOS should say: 10 machines, lists same names
# ✅ PASS if they match
# ❌ FAIL if different
```

---

## 📊 Test Coverage

| Category | Tests | Time |
|----------|-------|------|
| Machine Discovery | 3 tests | 2 min |
| Energy Sources | 3 tests | 2 min |
| Baseline Training | 4 tests | 5 min |
| Model Information | 2 tests | 2 min |
| Multi-Turn | 2 tests | 4 min |
| **Total** | **17 tests** | **15 min** |

---

## ✅ Pass Criteria

OVOS integration is **COMPLETE** when:

- ✅ All 17 test questions work
- ✅ OVOS responses match backend JSON data
- ✅ Error handling works (invalid input → helpful error)
- ✅ Multi-turn conversations work
- ✅ Training completes in < 30 seconds
- ✅ Numbers match (counts, R², percentages)

---

## 🚨 Critical Points

### 1. The `message` Field is Your Friend
```python
response = api.post("/ovos/train-baseline", ...)
self.speak(response["message"])  # ← Just speak this!
```

### 2. Timeout Must Be 30 Seconds
Training takes 3-10 seconds:
```python
response = requests.post(url, json=data, timeout=30)
```

### 3. Energy Source Format
- User says: "natural gas"
- API expects: `"natural_gas"` (underscore!)

### 4. Empty Features = Best Accuracy
Always use `features: []` for auto-selection:
```json
{
  "seu_name": "Compressor-1",
  "features": [],  // ← Auto-select
  "year": 2025
}
```

### 5. Check the `success` Field
```python
if response["success"]:
    self.speak(response["message"])  # Success message
else:
    self.speak(response["message"])  # Error message (also helpful!)
```

---

## 🐛 Troubleshooting

### "OVOS says different numbers than backend"
- ❌ **This is an OVOS bug** (not backend)
- Check: Are you parsing JSON correctly?
- Check: Are you using the `message` field?

### "Training times out"
- ✅ **This might be backend** (if > 30 seconds)
- Contact Mohamad if training takes > 30 seconds
- Normal time: 3-10 seconds

### "Machine not found"
- Check: Machine name is case-sensitive
- ✅ "Compressor-EU-1" 
- ❌ "compressor-eu-1"

### "Energy source invalid"
- Check: Use underscores, not spaces
- ✅ "natural_gas"
- ❌ "natural gas"

---

## 📞 Who to Contact

### Contact Mohamad (Backend Issues):
- ❌ API returns 500 error
- ❌ Training takes > 30 seconds
- ❌ Response format doesn't match documentation
- ❌ Backend validation script fails

### Don't Contact Mohamad (OVOS Issues):
- ✅ Intent recognition problems
- ✅ TTS pronunciation issues
- ✅ Python code structure
- ✅ OVOS framework questions

---

## 📝 Testing Checklist for Burak

Before saying "Integration complete":

- [ ] Run backend validation script → All pass
- [ ] Test 5 easy questions → All work
- [ ] Test error handling (invalid machine) → Graceful error
- [ ] Test multi-turn conversation → Workflow works
- [ ] Compare 5+ OVOS responses with backend → Match
- [ ] Test timeout handling → Doesn't crash
- [ ] Document any issues found → Report to team

---

## 🎓 Example Test Session

```bash
# 1. Verify backend
./test_ovos_integration.sh
# ✅ All tests pass

# 2. Ask OVOS: "What machines do you have?"
# OVOS should say: "I found 10 machines: Boiler-1 Electrical System..."

# 3. Verify with backend:
curl -s http://10.33.10.109:8001/api/v1/ovos/seus | jq .total_count
# Backend says: 10

# ✅ MATCH! Test passes!

# 4. Ask OVOS: "Train baseline for Compressor-EU-1"
# OVOS should say: "...trained successfully...99% accuracy...7,191 days..."

# 5. Verify with backend:
curl -s -X POST http://10.33.10.109:8001/api/v1/ovos/train-baseline \
  -H "Content-Type: application/json" \
  -d '{"seu_name": "Compressor-EU-1", "energy_source": "electricity", "features": [], "year": 2025}' | jq .
# Backend says: success: true, r_squared: 0.99, samples_count: 7191

# ✅ MATCH! Test passes!
```

---

## 🎉 Final Notes

**Backend Status:** ✅ Tested and working perfectly  
**Total APIs Available:** 5 endpoints, all verified  
**Test Questions Ready:** 17 scenarios with expected responses  
**Validation Script:** Automated, ready to run  

**Everything you need is in:**
- `docs/OVOS-INTEGRATION-TEST-QUESTIONS.md` ← Main guide
- `scripts/test_ovos_integration.sh` ← Quick validation

Good luck, Burak! The backend is ready for you! 🚀
