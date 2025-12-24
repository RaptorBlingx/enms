# Handoff Prompt: OVOS Architecture Refactor Implementation

**Date:** December 16, 2025  
**Project:** HumanEnerDIA - WASABI 1st Open Call  
**Task:** Execute OVOS refactor plan phase by phase  

---

## 🎯 CONTEXT FOR NEW AGENT

### Situation Summary

We discovered a **critical architecture misalignment** in the EnMS OVOS integration:

**Current (Wrong):** REST API bridge that bypasses OVOS framework entirely
**Target (Correct):** Proper OVOS skill using messagebus and skill framework
**Why Critical:** WASABI proposal committed to OVOS integration, current implementation doesn't meet this

### What Was Done Before You

1. ✅ Comprehensive review completed (see docs/COMPREHENSIVE-REVIEW-VALIDATION.md)
2. ✅ Architecture gap confirmed via docker ps, code inspection
3. ✅ Refactor plan validated and approved (docs/OPTION-A-OVOS-REFACTOR-PLAN.md)
4. ✅ NLU components verified as production-ready (52KB intent_parser, 95%+ accuracy)
5. ⚠️ Timeline still needs determination (M? of M12 months)

### Key Findings (Verified)

- Container runs `python bridge/ovos_headless_bridge.py` NOT ovos-core ❌
- No OVOS messagebus, skills service, or core services running ❌
- EnmsSkill class exists but @intent_handler decorators commented (lines 1961-1979) ❌
- setup.py and skill.json exist but never used by OVOS ❌
- License is Apache-2.0, should be GPL-3.0 per proposal ❌

---

## 📋 YOUR TASK

**Execute the refactor plan in docs/OPTION-A-OVOS-REFACTOR-PLAN.md systematically:**

### Working Mode

1. **Read First:** Review the full plan before starting
2. **One Phase at a Time:** Complete each phase before moving to next
3. **Validate Each Step:** Test after significant changes
4. **Document Progress:** Update plan's "Progress Tracking" section
5. **Ask Before Critical Changes:** Architecture decisions, file deletions, major refactors

### Work Locations

- **PRIMARY (90%):** `/home/ubuntu/ovos-llm/` - All OVOS refactoring work
- **SECONDARY (10%):** `/home/ubuntu/humanergy/` - Analytics stays as-is, minor portal updates

---

## 🚀 EXECUTION INSTRUCTIONS

### Step 0: Pre-Flight (Before Phase 1)

**DO THIS FIRST:**

1. **Determine Project Timeline** - CRITICAL
   ```bash
   # User needs to answer:
   # - What month are we in? (M? of M12)
   # - When did the 12-month WASABI project start?
   # - Are Romania field trials scheduled?
   # - Any deliverable deadlines approaching?
   ```
   
   **ACTION:** Ask user for timeline info, then decide:
   - If M6-M9 (3-6 months left): Full refactor (Option 1) ✅
   - If M10 (2 months left): Accelerated (Option 2) ⚠️
   - If M11+ (1 month left): Document only (Option 3) ❌

2. **Review Required Documents**
   - [ ] Read: docs/OPTION-A-OVOS-REFACTOR-PLAN.md (full plan)
   - [ ] Read: docs/COMPREHENSIVE-REVIEW-VALIDATION.md (validation proof)
   - [ ] Read: docs/HumanEnerDIA_WASABI_1st Open Call_Proposal.txt (commitments)
   - [ ] Read: .github/copilot-instructions.md (humanergy/ project context)

3. **Create Work Branch**
   ```bash
   cd /home/ubuntu/ovos-llm
   git checkout -b feature/ovos-refactor
   git tag v0.9-pre-ovos-refactor
   ```

4. **Contact WASABI Team** (if user hasn't done this)
   - Request Docker Compose for OVOS reference
   - Explain architecture gap discovered
   - Request technical mentoring/guidance

5. **Environment Check**
   ```bash
   # Verify current state
   docker ps | grep ovos
   docker exec ovos-enms ps aux | grep -E "ovos|python"
   
   # Should show: python bridge/ovos_headless_bridge.py
   # Should NOT show: ovos-core, messagebus, skills service
   ```

---

### Phase 1: Setup OVOS Core (Days 1-3)

**Location:** `/home/ubuntu/ovos-llm/`

**Tasks:**

1. **Update Dockerfile** (enms-ovos-skill/Dockerfile or create new ovos-docker/Dockerfile)
   ```dockerfile
   # Add OVOS core packages
   RUN pip install ovos-core ovos-messagebus ovos-skills-manager ovos-workshop
   
   # Create skills directory
   RUN mkdir -p /opt/ovos/skills
   
   # Copy skill to skills directory (not bridge!)
   COPY enms-ovos-skill/ /opt/ovos/skills/enms-ovos-skill/
   
   # Install skill dependencies
   RUN pip install -r /opt/ovos/skills/enms-ovos-skill/requirements.txt
   ```

2. **Create ovos.conf** (OVOS configuration)
   - Location: `/home/ubuntu/ovos-llm/ovos.conf` or `ovos-docker/ovos.conf`
   - Configure messagebus port (8181)
   - Disable audio if headless
   - Set skills directory

3. **Create supervisord.conf** (multi-service manager)
   - Run ovos-messagebus
   - Run ovos-skills
   - Run bridge (as REST proxy)
   
4. **Update docker-compose.yml**
   - Change CMD from bridge to supervisord or ovos-core
   - Expose port 8181 (messagebus, internal only)
   - Keep port 5000 (REST bridge)

5. **Test Build**
   ```bash
   cd /home/ubuntu/ovos-llm
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   
   # Check logs
   docker logs ovos-enms
   
   # Should see: messagebus started, skills service scanning
   ```

**Success Criteria:**
- [ ] OVOS messagebus running (check logs)
- [ ] Skills service scanning /opt/ovos/skills/
- [ ] No errors in docker logs
- [ ] `curl http://localhost:8181/core/version` works (inside container)

**⚠️ If Stuck:** Ask user to contact WASABI team for Docker Compose reference

---

### Phase 1.2: Configure Messagebus Communication (Days 4-5)

**Location:** `/home/ubuntu/ovos-llm/enms-ovos-skill/bridge/`

**Tasks:**

1. **Refactor ovos_headless_bridge.py**
   - Import: `from ovos_bus_client.client import MessageBusClient`
   - Remove: Direct skill engine instantiation
   - Add: Messagebus client connection
   - Change: Process queries via messagebus, not direct calls

2. **Bridge New Logic**
   ```python
   # Send utterance to OVOS
   self.bus.emit(Message('recognizer_loop:utterance',
                         {'utterances': [text],
                          'session_id': session_id}))
   
   # Listen for response
   self.bus.on('speak', self.handle_speak)
   ```

3. **Test Messagebus Communication**
   ```bash
   # Inside container
   docker exec ovos-enms ovos-cli send "test message"
   
   # Check if skill receives it (logs)
   docker logs ovos-enms | grep EnmsSkill
   ```

**Success Criteria:**
- [ ] Bridge connects to messagebus (no connection errors)
- [ ] Bridge can send `recognizer_loop:utterance` messages
- [ ] Bridge receives `speak` messages
- [ ] End-to-end: REST → Messagebus → Skill → Response

---

### Phase 2: Refactor EnmsSkill (Days 6-9)

**Location:** `/home/ubuntu/ovos-llm/enms-ovos-skill/enms_ovos_skill/__init__.py`

**Tasks:**

1. **Uncomment Intent Handlers** (lines 1961-1979)
   ```python
   # Change from:
   # @intent_handler("energy.query.intent")
   
   # To:
   @intent_handler("energy.query.intent")
   def handle_energy_query(self, message):
       utterance = message.data.get('utterance')
       # Use existing lib/intent_parser.py logic
       result = self.handle_enms_query(utterance)
       self.speak(result['response'])
   ```

2. **Keep Existing NLU** (lib/ directory stays as-is)
   - lib/intent_parser.py - 52KB, production-ready ✅
   - lib/api_client.py - 29KB, full API integration ✅
   - lib/validator.py - 27KB, zero-trust validation ✅
   - **DO NOT REWRITE** - Just wrap in OVOS decorators

3. **Hybrid Approach** (optional)
   ```python
   def initialize(self):
       self.parser = IntentParser()  # Keep our NLU
       self.register_fallback(self.hybrid_handler, priority=10)
   ```

4. **Test Each Intent**
   ```bash
   python scripts/test_skill_chat.py "factory overview"
   python scripts/test_skill_chat.py "power of Compressor-1"
   python scripts/test_skill_chat.py "forecast tomorrow"
   ```

**Success Criteria:**
- [ ] All 20 intent types working via OVOS
- [ ] 95%+ accuracy maintained
- [ ] <100ms response time
- [ ] Existing test suite passes

---

### Phase 3: Package for Distribution (Days 12-14)

**Location:** `/home/ubuntu/ovos-llm/enms-ovos-skill/`

**Tasks:**

1. **Fix License** - CRITICAL
   ```python
   # In setup.py, change:
   license='Apache2.0'  # WRONG
   # To:
   license='GPL-3.0'    # CORRECT (per proposal)
   
   # In skill.json, change:
   "license": "Apache-2.0"  # WRONG
   # To:
   "license": "GPL-3.0"     # CORRECT
   ```

2. **Add LICENSE File**
   - Download GPL-3.0 license text
   - Save as `/home/ubuntu/ovos-llm/enms-ovos-skill/LICENSE`

3. **Create README.md** (user-facing)
   - Installation instructions
   - Voice command examples
   - Configuration guide

4. **Test Installation**
   ```bash
   cd /home/ubuntu/ovos-llm/enms-ovos-skill
   pip install -e .  # Test install
   ovos-skills-manager list  # Should show enms-ovos-skill
   ```

**Success Criteria:**
- [ ] GPL-3.0 license in setup.py, skill.json, LICENSE file
- [ ] README with installation guide
- [ ] Skill installable via pip

---

### Phase 4: Testing (Days 15-17)

**Tasks:**

1. **Full Integration Test**
   ```bash
   # Test via REST API (portal integration)
   curl -X POST http://localhost:5000/query \
     -H "Content-Type: application/json" \
     -d '{"text": "factory overview"}'
   
   # Should return JSON with proper response
   ```

2. **Regression Test Suite**
   ```bash
   cd /home/ubuntu/ovos-llm/enms-ovos-skill
   python scripts/test_skill_chat.py "energy consumption Compressor-1"
   python scripts/test_skill_chat.py "forecast tomorrow"
   python scripts/test_skill_chat.py "top 5 consumers"
   # ... all test cases from tests/
   ```

3. **Performance Benchmark**
   - Measure P50, P90, P99 latency
   - Target: <100ms P50
   - Compare with pre-refactor metrics

**Success Criteria:**
- [ ] All integration tests pass
- [ ] Latency <100ms P50
- [ ] 95%+ accuracy maintained
- [ ] Portal works with new OVOS backend

---

### Phase 5: Documentation & Open Source (Days 18-21)

**Location:** `/home/ubuntu/humanergy/docs/wasabi/`

**Tasks:**

1. **Create WASABI Deliverables Folder**
   ```bash
   mkdir -p /home/ubuntu/humanergy/docs/wasabi
   ```

2. **Write Documents**
   - White paper: OVOS integration for EnMS
   - Case study: HumanEnerDIA implementation
   - Architecture diagram: OVOS-correct flow
   - Field trial report (if Romania trials done)
   - Green eDIH collaboration report

3. **Prepare Open Source**
   - Create GitHub repo plan
   - Prepare OVOS Skill Store submission
   - Write deployment guide

**Success Criteria:**
- [ ] White paper written
- [ ] Case study completed
- [ ] Architecture diagrams updated
- [ ] Ready for GitHub publication

---

## 📊 PROGRESS TRACKING

**Update this after each phase:**

### Phase Status

| Phase | Status | Started | Completed | Notes |
|-------|--------|---------|-----------|-------|
| 0: Pre-Flight | ⏳ | - | - | Timeline determination needed |
| 1.1: OVOS Core | 🔴 | - | - | Not started |
| 1.2: Messagebus | 🔴 | - | - | Not started |
| 2.1: Intent Handlers | 🔴 | - | - | Not started |
| 2.2: NLU Integration | 🔴 | - | - | Not started |
| 3.1: Packaging | 🔴 | - | - | Not started |
| 3.2: Documentation | 🔴 | - | - | Not started |
| 4.1: Testing | 🔴 | - | - | Not started |
| 4.2: Portal Integration | 🔴 | - | - | Not started |
| 5.1: WASABI Docs | 🔴 | - | - | Not started |
| 5.2: Open Source | 🔴 | - | - | Not started |

Legend: 🔴 Not Started | ⏳ In Progress | ✅ Complete | ❌ Blocked

---

## ⚠️ CRITICAL REMINDERS

### Before You Start

1. **ASK USER FOR TIMELINE** - Is this M6, M9, M10, M11 of 12-month project?
   - This determines if we do full refactor or accelerated version
   
2. **READ ALL DOCUMENTS** - Don't skip the plan or validation report

3. **CHECK WASABI CONTACT** - Has user contacted WASABI team yet?

4. **CREATE BRANCH** - `git checkout -b feature/ovos-refactor`

### During Implementation

1. **Work Incrementally** - Commit after each working change
2. **Test Continuously** - Don't wait until end to test
3. **Update Progress** - Mark phases complete as you go
4. **Ask When Stuck** - Don't guess on architecture decisions
5. **Keep humanergy/ Stable** - 90% work is in ovos-llm/

### Key Files to Modify

**Primary Work (ovos-llm/):**
- `/home/ubuntu/ovos-llm/Dockerfile` - Add OVOS packages
- `/home/ubuntu/ovos-llm/docker-compose.yml` - Change CMD
- `/home/ubuntu/ovos-llm/enms-ovos-skill/enms_ovos_skill/__init__.py` - Uncomment decorators
- `/home/ubuntu/ovos-llm/enms-ovos-skill/bridge/ovos_headless_bridge.py` - Add messagebus
- `/home/ubuntu/ovos-llm/enms-ovos-skill/setup.py` - Fix license
- `/home/ubuntu/ovos-llm/enms-ovos-skill/skill.json` - Fix license

**DO NOT MODIFY (keep as-is):**
- `/home/ubuntu/ovos-llm/enms-ovos-skill/enms_ovos_skill/lib/*.py` - NLU is production-ready
- `/home/ubuntu/humanergy/analytics/` - EnMS API is stable
- `/home/ubuntu/humanergy/database/` - Don't touch database

### Success Indicators

**You'll know it's working when:**
- `docker logs ovos-enms` shows "messagebus started"
- `docker logs ovos-enms` shows "EnmsSkill loaded"
- `curl localhost:5000/query` returns proper responses
- All test cases pass
- Latency <100ms

---

## 🆘 WHEN YOU NEED HELP

### If OVOS Won't Start
1. Check Dockerfile: Are ovos-core packages installed?
2. Check logs: `docker logs ovos-enms`
3. Check inside container: `docker exec ovos-enms ps aux | grep ovos`
4. Ask user: Did WASABI provide Docker Compose reference?

### If Skills Won't Load
1. Check: Is skill in `/opt/ovos/skills/enms-ovos-skill/`?
2. Check: Does setup.py have correct entry points?
3. Check logs: `docker logs ovos-enms | grep EnmsSkill`
4. Check: Are @intent_handler decorators uncommented?

### If Messagebus Won't Connect
1. Check: Is messagebus running? (ps aux inside container)
2. Check: Is port 8181 open? (inside container)
3. Check: Is bridge importing ovos-bus-client correctly?
4. Check logs: Connection errors in docker logs

### If Tests Fail
1. Check: Are NLU components still in lib/?
2. Check: Is API client connecting to analytics (port 8001)?
3. Check: Are intent handlers calling existing logic?
4. Compare: Pre-refactor vs post-refactor behavior

---

## 📋 DELIVERABLES CHECKLIST

### For WASABI (End of Refactor)

- [ ] OVOS framework properly integrated
- [ ] Skill installable via ovos-skills-manager
- [ ] GPL-3.0 licensed
- [ ] White paper written
- [ ] Case study completed
- [ ] Architecture diagram (correct)
- [ ] Field trial documentation (if applicable)
- [ ] Green eDIH collaboration report

### For User (End of Refactor)

- [ ] Working OVOS integration (not REST bypass)
- [ ] All 20 intents working
- [ ] 95%+ accuracy maintained
- [ ] Portal integration working
- [ ] Docker deployment updated
- [ ] Open-source ready for publication

---

## 🎯 YOUR FIRST ACTION

**When user starts new chat with you:**

1. Say: "I'll implement the OVOS refactor plan. First, I need timeline information:"
   - What month are we in? (M? of M12)
   - When did the WASABI project start?
   - Are there deliverable deadlines approaching?
   
2. Based on answer, recommend:
   - **M6-M9:** Full refactor (3-4 weeks) ✅
   - **M10:** Accelerated (2 weeks) ⚠️
   - **M11+:** Document only ❌

3. After user confirms, say: "I'll start with Phase 0: Pre-Flight checks"

4. Execute Step 0, then proceed phase by phase

---

## 📚 QUICK REFERENCE

**Key Documents:**
- Plan: docs/OPTION-A-OVOS-REFACTOR-PLAN.md
- Validation: docs/COMPREHENSIVE-REVIEW-VALIDATION.md  
- Proposal: docs/HumanEnerDIA_WASABI_1st Open Call_Proposal.txt

**Key Commands:**
```bash
# Build and run
cd /home/ubuntu/ovos-llm
docker-compose down && docker-compose build --no-cache && docker-compose up -d

# Check OVOS status
docker logs ovos-enms
docker exec ovos-enms ps aux | grep ovos

# Test skill
python scripts/test_skill_chat.py "factory overview"

# Check messagebus
docker exec ovos-enms ovos-cli send "test"
```

**Key Files:**
- Skill: `/home/ubuntu/ovos-llm/enms-ovos-skill/enms_ovos_skill/__init__.py`
- Bridge: `/home/ubuntu/ovos-llm/enms-ovos-skill/bridge/ovos_headless_bridge.py`
- Config: `/home/ubuntu/ovos-llm/docker-compose.yml`

---

**Document Version:** 1.0  
**Last Updated:** December 16, 2025  
**Status:** ✅ Ready for new agent  
**Expected Duration:** 3-4 weeks (depending on timeline)
