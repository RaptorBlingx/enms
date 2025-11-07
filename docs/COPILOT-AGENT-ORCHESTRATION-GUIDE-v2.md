# GitHub Copilot Agent Workflow Guide - EnMS Phase 6

**VS Code Insiders Required** | **Created:** November 7, 2025 | **Checkpoint:** v3.0.0-phase5.1-complete

---

## Core Concepts

### 1. **Subagents** (#runSubagent)
Context-isolated autonomous agents for complex multi-step tasks. Operate independently, return final result only.

**Use for:**
- Research and context gathering
- Complex analysis
- TDD workflows
- Context optimization (separate token window)

### 2. **Agent Sessions** (Delegate to Agent)
Background coding agents (GitHub Copilot coding agent, CLI, OpenAI Codex). Work asynchronously while you continue in VS Code.

**Use for:**
- Long-running tasks
- Multi-file refactoring
- Background implementation

### 3. **Chat Modes**
Specialized personas: Agent, Ask, Edit (Plan mode not found in docs - may be experimental/renamed).

---

## Setup Steps

### Enable Agent Sessions View

```
1. Ctrl+Shift+P → "Preferences: Open Settings (UI)"
2. Search: "chat.agentSessionsViewLocation"
3. Set to: "primary" or "secondary"
4. Restart VS Code Insiders
```

**Verify:** Agent Sessions view appears in sidebar with sections:
- LOCAL CHAT AGENT
- GITHUB COPILOT CLOUD AGENT
- GITHUB COPILOT CLI AGENT
- OPENAI CODEX (if enabled)

---

## Workflow Patterns

### Pattern 1: Research with Subagent

**Scenario:** Research v3 API patterns before implementation

```
# Main chat
Analyze analytics/ui/templates/baseline.html and recommend migration strategy to v3 /baseline/train-seu endpoint.

First, research the existing implementation using a subagent #runSubagent. Then provide migration steps.

#codebase
```

**What happens:**
1. Subagent spawns (isolated context)
2. Researches codebase autonomously
3. Returns findings to main chat
4. Main chat provides recommendations

**Benefit:** Subagent uses separate token window, preserving main chat context.

### Pattern 2: Delegate Long Tasks

**Scenario:** Migrate entire baseline page while working on other tasks

```
1. Open Chat View (Ctrl+Alt+I)
2. Type prompt:
   "Migrate analytics/ui/templates/baseline.html to v3 API:
    - Update endpoint: /ovos/train-baseline → /baseline/train-seu
    - Add SEU selector dropdown
    - Add energy source filter
    - Update baseline.js API calls
    
    #file:analytics/ui/templates/baseline.html
    #file:analytics/ui/static/js/baseline.js
    #file:docs/api-documentation/ENMS-API-DOCUMENTATION-FOR-OVOS.md"

3. Click "Delegate to Agent" button (or select from ... menu)
4. Choose "GitHub Copilot coding agent"
5. Monitor progress in Agent Sessions view
```

**What happens:**
1. Coding agent session created in cloud
2. Works in background (async)
3. You continue working in VS Code
4. Check progress in Agent Sessions view
5. Review changes when complete

**Benefit:** Offload complex task, continue other work.

### Pattern 3: TDD Workflow with Subagent

**Scenario:** Test-driven development for component

```
Implement LoadingSpinner component with TDD workflow using a subagent #runSubagent:

1. Write tests first (analytics/ui/static/js/components/__tests__/loading-spinner.test.js)
2. Implement component (analytics/ui/static/js/components/loading-spinner.js)
3. Run tests, iterate until passing
4. Return final implementation

Requirements:
- 3 sizes (sm, md, lg)
- 2 themes (light, dark)
- SVG animation
- Jest tests

#codebase
```

**Benefit:** Subagent handles full TDD cycle autonomously.

---

## Phase 6 Practical Workflow

### Milestone 6.1: Component Library

**Main Chat Strategy:**

```
# Session 1: Research & Plan
Analyze existing UI components in analytics/ui/static/js/ and create implementation plan for:
- LoadingSpinner
- ErrorMessage  
- SEUSelector

Use subagent for analysis #runSubagent, then provide structured plan.

#codebase analytics/ui/
```

**Subagent Tasks:**

```
# Session 2: Implement LoadingSpinner (Subagent)
Implement LoadingSpinner component using subagent #runSubagent:
- File: analytics/ui/static/js/components/loading-spinner.js
- 3 sizes, 2 themes, SVG animation
- Follow patterns from chart-utils.js

#file:analytics/ui/static/js/chart-utils.js
#codebase
```

```
# Session 3: Implement ErrorMessage (Delegate)
[Type prompt, then click "Delegate to Agent"]

Implement ErrorMessage component:
- File: analytics/ui/static/js/components/error-message.js
- 4 severity types (info, warning, error, success)
- Retry button, dismissible
- Match industrial design system

#file:analytics/ui/static/css/style.css
#codebase
```

**Coordination:**
1. Main chat creates plan (5 min)
2. Spawn 2 subagents for LoadingSpinner + SEUSelector (parallel)
3. Delegate ErrorMessage to coding agent
4. Review results in Agent Sessions view
5. Integrate, test, commit

---

### Milestone 6.2: Baseline Page Migration

**Delegate Full Page:**

```
[Delegate to Agent]

Migrate baseline page to v3 API endpoints:

Files to modify:
- analytics/ui/templates/baseline.html
- analytics/ui/static/js/baseline.js
- analytics/ui/static/css/baseline.css (if needed)

Changes:
1. Replace /api/v1/ovos/train-baseline → /api/v1/baseline/train-seu
2. Add SEU selector (use SEUSelector component from milestone 6.1)
3. Add energy source filter dropdown
4. Update request payload: {seu_name, energy_source, ...}
5. Display new response fields: explanation, voice_summary
6. Error handling (404, 400, 500)

Testing:
- Compressor-1 (electricity)
- Boiler-1 (natural_gas)

#file:analytics/ui/templates/baseline.html
#file:analytics/ui/static/js/baseline.js
#file:docs/api-documentation/ENMS-API-DOCUMENTATION-FOR-OVOS.md
#codebase
```

**Monitor in Agent Sessions:**
- View: Agent Sessions → GitHub Copilot coding agent → [session name]
- Watch file changes in real-time
- Cancel if going wrong
- Review diff when complete

---

### Milestone 6.3: Multi-Page Migration

**Parallel Delegation:**

```
# Session 1: Dashboard (Delegate)
[Delegate to Agent - Session 1]
Update analytics/ui/templates/index.html to v3:
- /api/v1/factory/summary
- /api/v1/seus
- Add SEU stats cards
- Add Performance Engine widget

#file:analytics/ui/templates/index.html
#codebase

---

# Session 2: KPI Page (Delegate)  
[Delegate to Agent - Session 2]
Update analytics/ui/templates/kpi.html to v3:
- /api/v1/kpi/energy-breakdown
- Multi-energy stacked chart
- SEU filter dropdown

#file:analytics/ui/templates/kpi.html
#codebase

---

# Session 3: Model Performance (Subagent)
Add model explanation tab using subagent #runSubagent:
- /api/v1/baseline/models?include_explanation=true
- Coefficient importance chart
- Feature correlation heatmap

#file:analytics/ui/templates/model-performance.html
#codebase
```

**Management:**
1. Start 3 agent sessions (parallel)
2. Monitor in Agent Sessions view
3. Review each when complete
4. Test integrated system
5. Commit checkpoint

---

## Prompt Engineering

### Subagent Prompts

**Structure:**
```
[Task description] using subagent #runSubagent:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Requirements:
- [Requirement 1]
- [Requirement 2]

Return: [Expected output]

#file:path/to/file
#codebase
```

**Example:**
```
Research authentication patterns in codebase using subagent #runSubagent:
1. Find all authentication-related files
2. Analyze current implementation
3. Identify security vulnerabilities
4. Recommend improvements

Return: Security audit report with actionable recommendations

#codebase
```

### Delegate Prompts

**Structure:**
```
[Clear objective]

Files to modify:
- [file 1]
- [file 2]

Changes required:
1. [Change 1]
2. [Change 2]

Testing scenarios:
- [Scenario 1]
- [Scenario 2]

#file:path/to/file
#codebase

[Click "Delegate to Agent"]
```

**Example:**
```
Implement OAuth authentication for EnMS:

Files to modify:
- analytics/api/routes/auth.py (create)
- analytics/main.py (add auth middleware)
- analytics/config.py (add OAuth settings)

Changes:
1. Google OAuth 2.0 integration
2. JWT token generation
3. Protected route decorator
4. Login/logout endpoints

Testing:
- Login flow works
- Protected routes require auth
- Logout clears session

#file:analytics/main.py
#file:analytics/config.py
#codebase

[Delegate to Agent]
```

---

## Safety & Monitoring

### Agent Sessions View Actions

**Monitor Progress:**
- Real-time file changes displayed
- Console output visible
- Error messages shown

**Available Actions (right-click session):**
- **Cancel** - Stop agent if going wrong
- **Open in new window** - Dedicated monitoring
- **Open in Chat view** - Switch to interactive
- **Apply changes** - Merge to workspace
- **Discard** - Reject all changes

### Checkpoints Strategy

```bash
# Before delegating major tasks
git add -A
git commit -m "v3: Pre-delegation checkpoint - baseline page"
git tag temp-checkpoint-baseline

# After agent completes
# Review changes in Agent Sessions view
# If good: commit normally
# If bad: rollback

git reset --hard temp-checkpoint-baseline
git tag -d temp-checkpoint-baseline
```

### Review Before Merge

**Checklist:**
1. Open Agent Sessions view
2. Click completed session
3. Review file diffs
4. Check for:
   - Unintended file changes
   - Deleted important code
   - Incorrect patterns
   - Missing error handling
5. Test locally before committing
6. Use "Apply changes" to merge, or "Discard" to reject

---

## Context Management

### Attach Context Efficiently

**For Subagents:**
```
#codebase [specific folder]          # Better than whole workspace
#file:exact/path/to/file.js          # Specific files only
#fetch:URL                            # External documentation
```

**For Delegation:**
```
#file:analytics/ui/templates/baseline.html
#file:analytics/ui/static/js/baseline.js
#file:docs/api-documentation/ENMS-API-DOCUMENTATION-FOR-OVOS.md

# Avoid #codebase alone - too broad for delegation
```

### When to Use What

| Task Type | Method | Reason |
|-----------|--------|--------|
| Research/analysis | Subagent | Isolated context, returns summary |
| Long refactoring | Delegate | Background async, continue working |
| Quick fixes | Main chat (Edit mode) | Direct, immediate |
| Multi-file coordination | Delegate | Handles dependencies |
| TDD workflow | Subagent | Autonomous test-implement cycle |
| Complex planning | Main chat + subagent research | Subagent gathers info, main chat plans |

---

## Troubleshooting

### Subagent Not Working
**Symptom:** No subagent spawned
**Fix:** 
- Ensure VS Code Insiders (not stable)
- Use explicit `#runSubagent` in prompt
- Try natural language: "use a subagent for this"

### Delegate Button Missing
**Symptom:** "Delegate to Agent" button not visible
**Fix:**
- Enable Agent Sessions view (Settings: `chat.agentSessionsViewLocation`)
- Ensure GitHub Copilot coding agent enabled
- Restart VS Code Insiders

### Agent Session Stuck
**Symptom:** Agent running too long, no progress
**Fix:**
- Right-click session → Cancel
- Review prompt for clarity
- Break into smaller tasks
- Try again with more specific instructions

### Context Not Available
**Symptom:** Agent asks for info already in attached files
**Fix:**
- Use explicit `#file:path` instead of `#codebase`
- Push code to GitHub (enables remote indexing)
- Build workspace index: Ctrl+Shift+P → "Build Remote Workspace Index"

---

## Quick Reference

### Commands
```
Ctrl+Alt+I          # Open Chat View
Ctrl+Shift+P        # Command Palette
View: Show Agent Sessions
Build Remote Workspace Index
```

### Prompt Syntax
```
#runSubagent        # Spawn context-isolated subagent
#codebase           # Search workspace
#file:path/to/file  # Attach specific file
#fetch:URL          # External docs
```

### Git Safety
```bash
# Pre-delegation checkpoint
git add -A && git commit -m "temp checkpoint"
git tag temp-$(date +%s)

# Rollback if agent fails
git reset --hard temp-<timestamp>
```

---

## Phase 6 Execution Plan

### Week 1: Milestones 6.1 + 6.2

**Day 1-2: Component Library (6.1)**
1. Main chat: Research existing patterns (subagent)
2. Delegate: LoadingSpinner implementation
3. Delegate: ErrorMessage implementation  
4. Subagent: SEUSelector with API integration
5. Review all in Agent Sessions
6. Integrate, test, commit

**Day 3-4: Baseline Page (6.2)**
1. Delegate full page migration (one agent session)
2. Monitor in Agent Sessions view
3. Test migration with Compressor-1, Boiler-1
4. Review diff, apply changes
5. Commit checkpoint

### Week 2: Milestone 6.3

**Day 5-8: Multi-Page Migration**
1. Delegate 4 sessions in parallel:
   - Dashboard (high priority)
   - KPI page (high priority)
   - Model Performance (medium)
   - Anomaly + Forecast (low - combined session)
2. Monitor all 4 in Agent Sessions view
3. Review each when complete
4. Integration testing
5. Final checkpoint: v3.0.0-phase6-complete

---

**Rollback Tag:** v3.0.0-phase5.1-complete  
**Next:** Open VS Code Insiders → Enable Agent Sessions View → Start Milestone 6.1
