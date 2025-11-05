# EnMS v3 Development - Starter Prompt

**📋 Instructions: Copy everything below this line and paste into new agent chat**

---

# EnMS v3 Development - Phase 0 Start

## 📦 Context

I am implementing **EnMS v3**, a complete architectural transformation of our Energy Management System. The full roadmap is in the attached **`ENMS-v3.md`** document (6.5-week, 8-phase plan including Phase 0).

### Project Background
- **Project**: WASABI - AI-driven building automation with OVOS voice integration
- **Current Version**: v2.0 (checkpoint: git commit `5b20761`)
- **Purpose**: Industrial energy management, ISO 50001 compliance
- **Stack**: FastAPI (Python), TimescaleDB, Docker, Redis, Node-RED
- **Integration**: Burak's OVOS voice assistant consumes our APIs

## 🚨 Current State

### What's Working (v2.0)
- ✅ 8 machines monitored
- ✅ 10 SEUs (Significant Energy Uses)
- ✅ 61 baseline models trained (linear regression, 85-99% R²)
- ✅ Multi-energy support (4 sources: electricity, natural_gas, steam, compressed_air)
- ✅ 27 integration tests passing
- ✅ Real-time WebSocket updates
- ✅ Grafana dashboards
- ✅ OVOS voice integration working

### Known Issues (v2.0)
1. **Misleading API naming**: `/ovos/*` endpoints suggest exclusivity
2. **Disconnected services**: Baseline, anomaly, KPI don't communicate
3. **No intelligence layer**: Data collection without insights
4. **Partial ISO 50001**: Have SEUs, missing EnPI tracking
5. **Frontend 6 months behind backend**: UI doesn't use new features
6. **UNKNOWN BUG STATUS**: We assume v2 works 100%, but need validation ⚠️

### Critical Assumption Risk
**We're building v3 on the assumption that v2 backend is bug-free.** This is potentially dangerous. Discovering bugs mid-refactor causes:
- Confusion about root causes (v2 bug or v3 regression?)
- Wasted refactoring effort
- Unpredictable timeline

**Solution**: Phase 0 validates v2 foundation BEFORE v3 work begins.

## 🎯 Immediate Task: Phase 0

**Your mission is to execute Phase 0: v2 Critical Path Validation** (2 days)

This is a NEW phase not in the original plan, added specifically to de-risk the v3 transformation.

### Phase 0 Objectives

**Milestone 0.1: Comprehensive Data Quality Audit (1 day)**
1. Run all 27 existing integration tests with REAL production data
2. Create `tests/test_data_sanity.py` with 15+ sanity checks:
   - ❌ NO negative energy predictions (my main concern!)
   - ❌ NO invalid percentages (>100% or <0%)
   - ❌ NO null values in required fields
   - ✅ All timestamps valid ISO 8601
   - ✅ Cost calculations correct (Energy × Rate)
   - ✅ R² values between 0-1
3. Test multi-energy machines (especially Boiler-1: 3 SEUs)
4. Validate baseline prediction logic against recent actual data
5. Identify test coverage gaps

**Milestone 0.2: Critical Bug Fixing (1 day)**
1. Triage bugs: Critical (fix NOW) vs Minor (defer to Phase 4)
2. Fix critical bugs immediately (tag commits: `v2-bugfix:`)
3. Add regression tests for each bug
4. Document minor bugs in `docs/V2-KNOWN-ISSUES.md`
5. Re-run full test suite to verify fixes
6. Update v2 checkpoint if major fixes made

### Critical Questions to Answer

**Before proceeding to Phase 1, I need to know:**
1. ✅ Are there negative energy predictions? (My #1 concern!)
2. ✅ Do multi-energy machines work correctly? (Boiler-1 test)
3. ✅ Are baseline predictions logical given inputs?
4. ✅ Do all 27 integration tests pass with REAL data (not mocks)?
5. ✅ What's NOT tested that should be?
6. ✅ What's the actual bug count? (estimate: 0-3 critical, 5-10 minor)

### Success Criteria for Phase 0

- [ ] All data sanity tests passing (15+ new tests)
- [ ] Critical bugs documented and fixed (0 remaining)
- [ ] Minor bugs documented in V2-KNOWN-ISSUES.md (defer to Phase 4)
- [ ] Multi-energy machines validated (Boiler-1 working correctly)
- [ ] Test coverage gaps identified and documented
- [ ] ENMS-v3.md updated with Phase 0 results
- [ ] **Confidence in v2 foundation: HIGH** ⭐

### Decision Point After Phase 0

**If 0 critical bugs found:**
→ ✅ Proceed directly to Phase 1 (API Cleanup)  
→ Foundation confirmed solid

**If 1-3 critical bugs found and fixed:**
→ ⚠️ Proceed to Phase 1 with increased caution  
→ Add extra validation in Phase 4

**If 5+ critical bugs found:**
→ 🛑 PAUSE v3 planning  
→ Conduct deeper v2 audit  
→ Discuss extended stabilization strategy

## 📚 Your First Actions

### Step 1: Read ENMS-v3.md Completely
- Understand all 8 phases (Phase 0-7)
- Review success criteria for each milestone
- Note the v3 vision (why we're doing this)
- Understand data migration strategy
- Review OVOS integration validation plan

### Step 2: Create Internal TODO List
**Based on your review of ENMS-v3.md Phase 0, create a TODO list for yourself to stay on track:**

Example structure:
```
Phase 0 - v2 Critical Path Validation
├─ Milestone 0.1: Data Quality Audit
│  ├─ [ ] Run existing 27 integration tests
│  ├─ [ ] Create test_data_sanity.py
│  ├─ [ ] Test for negative energy predictions
│  ├─ [ ] Test multi-energy machines (Boiler-1)
│  ├─ [ ] Validate baseline prediction logic
│  └─ [ ] Document test coverage gaps
└─ Milestone 0.2: Bug Fixing
   ├─ [ ] Triage discovered bugs
   ├─ [ ] Fix critical bugs
   ├─ [ ] Add regression tests
   ├─ [ ] Create V2-KNOWN-ISSUES.md
   └─ [ ] Re-run full test suite
```

**Update this TODO list as you work. It helps you (and me) track progress.**

### Step 3: Analyze Current Test Suite
Review `analytics/tests/test_ovos_regression_endpoints.py` and tell me:

1. **What's being tested?** (specific test cases)
2. **What's NOT being tested?** (gaps)
3. **Are tests using real data or mocks?**
4. **Coverage assessment**: What percentage of critical paths are tested?
5. **Proposed sanity test suite**: What tests should we add in Phase 0?

### Step 4: Execute Phase 0 (After Analysis)
Only after you understand the current state, begin implementing:
1. Data sanity test suite
2. Run tests and identify bugs
3. Fix critical bugs
4. Document results in ENMS-v3.md

## 📋 Important Instructions

### DO
- ✅ **Update ENMS-v3.md directly** (mark tasks `[x]` as you complete them)
- ✅ **Add session notes** at end of ENMS-v3.md in "Notes & Updates" section
- ✅ **Update API docs** if you fix any endpoints: `docs/api-documentation/ENMS-API-DOCUMENTATION-FOR-OVOS.md`
- ✅ **Commit frequently** with descriptive messages (`v2-bugfix:` or `v3: [Phase 0]`)
- ✅ **Use your TODO list** to stay organized
- ✅ **Ask questions** if you find something unexpected

### DO NOT
- ❌ **Create separate completion documents** (no `PHASE-0-COMPLETE.md`)
- ❌ **Skip testing** (all tests must pass before marking milestone complete)
- ❌ **Ignore bugs** (fix critical NOW, document minor for Phase 4)
- ❌ **Break backward compatibility** (not yet, that's Phase 1)
- ❌ **Rush through Phase 0** (solid foundation is critical for v3 success)

## 🎯 Expected Outcome

By end of Phase 0, I should have:
1. **Complete bug inventory** (critical vs minor, documented)
2. **Comprehensive test suite** (27+ integration tests, 15+ sanity tests)
3. **Validation report** (data quality, prediction logic, multi-energy support)
4. **Confidence level** (HIGH/MEDIUM/LOW for proceeding to v3)
5. **Updated ENMS-v3.md** (Phase 0 tasks marked complete, results documented)
6. **Decision** (proceed to Phase 1 or extend v2 stabilization)

## 📊 Project Vision (Remember Why)

We're building EnMS v3 to transform from:
- ❌ Disconnected data collection → ✅ Intelligent energy management
- ❌ Manual multi-step analysis → ✅ Automated complete insights
- ❌ Surface-level ISO compliance → ✅ Complete EnPI tracking
- ❌ Confusing API naming → ✅ Clear, intuitive endpoints
- ❌ No proactive recommendations → ✅ AI-driven optimization

**Mr. Umut's "regression analysis with voice interface" requirement will be FULLY delivered in v3.**

## 🚀 Ready to Begin?

**Your first response should include:**
1. Confirmation you've read ENMS-v3.md
2. Your internal TODO list for Phase 0
3. Analysis of current test suite (`test_ovos_regression_endpoints.py`)
4. Proposed data sanity test cases
5. Estimated bug discovery likelihood (your gut feeling)
6. Recommendation: Proceed as planned or adjust strategy

**Let's ensure v2 is rock-solid before building v3 on top!** 🎯

---

**Attachments Required:**
1. `docs/ENMS-v3.md` (complete roadmap)
2. `C:/Users/Swemo/AppData/Roaming/Code/User/prompts/v3.instructions.md` (development instructions)

**Current Date**: November 5, 2025  
**Project Phase**: Pre-v3 (Phase 0 starting)  
**Your Role**: Lead developer implementing EnMS v3 transformation
