# GitHub Copilot Agent Orchestration Guide for EnMS Phase 6 Frontend

**Created:** November 7, 2025  
**For:** EnMS v3 Phase 6 - Frontend Modernization  
**VS Code Version:** VS Code Insiders (required for Plan mode)  
**Checkpoint:** v3.0.0-phase5.1-complete (commit df7ce17)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [New Copilot Features in VS Code Insiders](#new-copilot-features)
4. [Agent Orchestration Strategy](#agent-orchestration-strategy)
5. [Phase 6 Frontend Work Breakdown](#phase-6-frontend-work-breakdown)
6. [Prompt Engineering Best Practices](#prompt-engineering-best-practices)
7. [Context Attachment Strategy](#context-attachment-strategy)
8. [Multi-Agent Workflow Examples](#multi-agent-workflow-examples)
9. [Safety & Rollback Plan](#safety--rollback-plan)
10. [Troubleshooting](#troubleshooting)

---

## Overview

### What We're Building (Phase 6)

**Objective:** Modernize EnMS frontend UI to match v3 backend capabilities

**Current State:**
- 7 UI pages using v2 API endpoints
- No SEU selector interface
- Missing Performance Engine integration
- No ISO 50001 reporting UI

**Target State:**
- All pages use v3 endpoints
- SEU-based interface (dropdown selectors)
- Performance Engine dashboard integration
- ISO 50001 compliance reporting UI
- Reusable component library
- Modern industrial design system

**Duration:** 6 days (Milestones 6.1, 6.2, 6.3)

---

## Prerequisites

### Required Tools

✅ **VS Code Insiders** (November 2025 or later)
- Download: https://code.visualstudio.com/insiders/
- Required for **Plan mode** (agent orchestration)

✅ **GitHub Copilot Subscription**
- Plan mode requires Copilot Pro or Enterprise
- Agent mode available on all plans

✅ **Git Repository Connected**
- For remote workspace indexing
- Push code to GitHub for best results

### Recommended Settings

```json
// .vscode/settings.json (add to workspace)
{
  "github.copilot.enable": {
    "*": true,
    "yaml": true,
    "markdown": true,
    "javascript": true,
    "html": true,
    "css": true
  },
  "github.copilot.advanced": {
    "debug.overrideEngine": "gpt-4",
    "agent.enabled": true
  },
  "files.autoSave": "off" // Important: review changes before auto-save
}
```

---

## New Copilot Features in VS Code Insiders

### 1. **Plan Mode** (🆕 Preview - VS Code Insiders Only)

**What It Does:**
- Multi-step planning before execution
- Creates detailed implementation plan
- Shows estimated file changes
- Allows review before applying changes

**When to Use:**
- Complex multi-file refactoring (perfect for Phase 6!)
- Uncertain about approach
- Want to see full plan before changes

**How to Use:**
```
1. Open Chat View (Ctrl+Alt+I)
2. Select "Plan" from chat mode dropdown
3. Type prompt: "Migrate baseline.html to use v3 /baseline/train-seu endpoint with SEU selector"
4. Review generated plan (steps, files affected)
5. Approve plan → switches to Agent mode for execution
```

**Example Plan Output:**
```
📋 PLAN: Migrate Baseline Page to v3 API

Steps:
1. Update analytics/ui/templates/baseline.html
   - Add SEU selector dropdown
   - Add energy source filter
   - Replace machine_id with seu_name

2. Update analytics/ui/static/js/baseline.js
   - Change API endpoint: /ovos/train-baseline → /baseline/train-seu
   - Update request payload schema
   - Add SEU dropdown event handlers

3. Update analytics/ui/static/css/baseline.css
   - Add styles for new selectors
   - Maintain industrial design system

Files affected: 3
Estimated changes: ~150 lines

Approve to proceed? [Yes] [No] [Modify Plan]
```

### 2. **Agent Mode** (Autonomous Multi-File Editing)

**What It Does:**
- Autonomously determines what needs to be done
- Makes changes across multiple files
- Runs terminal commands (npm install, etc.)
- Iterates until task complete

**When to Use:**
- Well-defined tasks
- Trusted to make changes
- Want speed over detailed review

**How to Use:**
```
1. Open Chat View (Ctrl+Alt+I)
2. Select "Agent" from chat mode dropdown
3. Type prompt with clear objective
4. Agent works autonomously
5. Review diffs in editor (accept/reject)
```

**Key Features:**
- **Agentic search:** Automatically searches codebase for relevant context
- **Tool invocation:** Can run commands, create files, install packages
- **Multi-turn:** Asks clarifying questions if needed
- **Context retention:** Remembers conversation history

### 3. **Ask Mode** (Conversational Q&A)

**What It Does:**
- Answers questions without code changes
- Provides explanations and guidance
- Single search pass (no follow-ups)

**When to Use:**
- Understanding existing code
- Design decisions
- Architecture questions

### 4. **Edit Mode** (Targeted Code Editing)

**What It Does:**
- Applies specific edits to selected code
- Shows inline diff
- Fast for small changes

**When to Use:**
- Quick fixes
- Refactoring single function
- Code cleanup

---

## Agent Orchestration Strategy

### Swarm Architecture for Phase 6

**Concept:** Use multiple chat sessions as specialized "agents" for different aspects of frontend work.

```
┌─────────────────────────────────────────────────┐
│         ORCHESTRATOR (You + Plan Mode)          │
│   Creates high-level plan, coordinates agents   │
└────────────┬────────────────────────────────────┘
             │
    ┌────────┴────────┬────────────┬──────────────┐
    ▼                 ▼            ▼              ▼
┌─────────┐    ┌──────────┐  ┌─────────┐   ┌──────────┐
│ Agent 1 │    │ Agent 2  │  │ Agent 3 │   │ Agent 4  │
│Component│    │Endpoint  │  │Styling  │   │Testing   │
│Library  │    │Migration │  │System   │   │Validation│
└─────────┘    └──────────┘  └─────────┘   └──────────┘
```

### How to Implement Swarm

**Step 1: Create Multiple Chat Sessions**

VS Code allows multiple concurrent chat sessions. Use them as specialized agents:

```
Chat Session 1 (Plan Mode): "Master Orchestrator"
- Prompt: "Create plan for Phase 6 Milestone 6.1: Component Library"
- Attaches: ENMS-v3.md, design-system requirements
- Output: Detailed plan with steps

Chat Session 2 (Agent Mode): "Component Builder"
- Prompt: "Implement LoadingSpinner component from plan step 1"
- Attaches: Component spec from Chat 1
- Output: Working component code

Chat Session 3 (Agent Mode): "API Migrator"
- Prompt: "Update baseline.html to use v3 /baseline/train-seu endpoint"
- Attaches: ENMS-API-DOCUMENTATION-FOR-OVOS.md
- Output: Migrated endpoint calls

Chat Session 4 (Agent Mode): "Style Enforcer"
- Prompt: "Apply industrial design system to new components"
- Attaches: design-system.css
- Output: Styled components
```

**Step 2: Coordinate Between Sessions**

1. **Plan Mode** (Session 1): Creates master plan
2. **Agent Mode** (Sessions 2-4): Execute plan steps in parallel
3. **You:** Review changes, merge work, commit checkpoints

**Step 3: Use Context Passing**

```
Session 1 Plan Output:
"Component spec: LoadingSpinner with props (size, color, message)"

Session 2 Prompt:
"Implement this component spec: [paste spec from Session 1]"
```

---

## Phase 6 Frontend Work Breakdown

### Milestone 6.1: Component Library (2 days)

**Recommended Agent Strategy: 1 Plan + 3 Agents**

#### **Orchestrator Chat (Plan Mode)**

**Prompt Template:**
```
# Context
Attach: docs/ENMS-v3.md (Phase 6, Milestone 6.1 section)
Attach: analytics/ui/static/css/style.css (existing styles)

# Task
Create implementation plan for EnMS v3 Component Library with these requirements:

1. Reusable components:
   - LoadingSpinner (size variants, color themes)
   - ErrorMessage (error types, retry actions)
   - SEUSelector (dropdown with search, multi-energy support)
   - EnergySourceFilter (checkbox group)
   - ChartContainer (responsive wrapper for Chart.js)

2. Design system:
   - Industrial color palette (grays, blues, warning colors)
   - Consistent spacing scale (4px base)
   - Typography system (Roboto fonts)
   - Component sizing scale (sm, md, lg, xl)

3. File structure:
   analytics/ui/static/js/components/
   - loading-spinner.js
   - error-message.js
   - seu-selector.js
   - energy-source-filter.js
   - chart-container.js

4. Testing:
   - Each component has demo page
   - Responsive behavior validated
   - Accessibility (ARIA labels)

Generate detailed implementation plan with:
- Step-by-step tasks
- File changes per step
- Dependencies between components
- Estimated time per task

#codebase
```

**Expected Output:** 10-15 step plan with file-level details

#### **Agent 1: Component Implementation**

**Prompt Template:**
```
# Context
Attach: Plan from Orchestrator Chat (steps 1-5)
Attach: analytics/ui/static/js/chart-utils.js (for reference patterns)

# Task
Implement LoadingSpinner, ErrorMessage, and SEUSelector components following the plan.

Requirements:
- Vanilla JavaScript (no frameworks)
- ES6+ syntax (classes, arrow functions)
- Follow existing code patterns in chart-utils.js
- Include JSDoc comments
- Export as modules

Start with LoadingSpinner (step 1 in plan).

#codebase
```

#### **Agent 2: Styling**

**Prompt Template:**
```
# Context
Attach: analytics/ui/static/css/style.css (existing styles)
Attach: Component files from Agent 1

# Task
Create component-specific CSS following industrial design system:

Color Palette:
- Primary: #1e3a8a (dark blue)
- Success: #10b981 (green)
- Warning: #f59e0b (orange)
- Danger: #ef4444 (red)
- Neutral: #6b7280 (gray)

Spacing Scale: 4px base (0.25rem units)
Typography: Roboto 400/500/700

Create analytics/ui/static/css/components.css with:
- .loading-spinner (3 size variants)
- .error-message (4 severity types)
- .seu-selector (dropdown styles)
- Responsive breakpoints: 768px, 1024px, 1440px

#codebase
```

#### **Agent 3: Integration & Testing**

**Prompt Template:**
```
# Context
Attach: Component files from Agent 1
Attach: CSS from Agent 2
Attach: analytics/ui/templates/baseline.html (target page)

# Task
Integrate new components into baseline.html:

1. Replace old loading div with LoadingSpinner component
2. Replace old error handling with ErrorMessage component
3. Add SEUSelector component for machine selection
4. Test responsive behavior
5. Create demo page: analytics/ui/templates/components-demo.html

Validation checklist:
- ✅ Components render correctly
- ✅ Event handlers working
- ✅ Mobile responsive
- ✅ No console errors

#codebase
```

---

### Milestone 6.2: Baseline Page Overhaul (2 days)

**Recommended Agent Strategy: 1 Plan + 2 Agents**

#### **Orchestrator Chat (Plan Mode)**

**Prompt Template:**
```
# Context
Attach: docs/ENMS-v3.md (Milestone 6.2 requirements)
Attach: docs/api-documentation/ENMS-API-DOCUMENTATION-FOR-OVOS.md (v3 endpoints)
Attach: analytics/ui/templates/baseline.html (current page)

# Task
Create migration plan for baseline.html to v3 API:

Changes Required:
1. API endpoint migration:
   OLD: POST /api/v1/ovos/train-baseline
   NEW: POST /api/v1/baseline/train-seu
   
2. Request payload update:
   OLD: {"machine_id": "uuid"}
   NEW: {"seu_name": "Compressor-1", "energy_source": "electricity"}

3. UI enhancements:
   - SEU selector dropdown (use SEUSelector component)
   - Energy source filter (use EnergySourceFilter component)
   - Model explanation display (new field in v3 response)
   - Voice summary display (for OVOS integration)

4. Error handling:
   - Handle 404 (SEU not found)
   - Handle 400 (invalid energy source)
   - Show user-friendly messages

Generate detailed plan with:
- Frontend changes (HTML, JS, CSS)
- API migration steps
- Testing scenarios (Compressor-1, Boiler-1 with 3 SEUs)

#codebase
```

#### **Agent 1: HTML & API Migration**

**Prompt Template:**
```
# Context
Attach: Plan from Orchestrator
Attach: docs/api-documentation/ENMS-API-DOCUMENTATION-FOR-OVOS.md
Attach: analytics/ui/templates/baseline.html
Attach: analytics/ui/static/js/baseline.js

# Task
Update baseline page to use v3 /baseline/train-seu endpoint:

1. Update baseline.html:
   - Add SEU selector (replace machine selector)
   - Add energy source filter (electricity, natural_gas, steam, compressed_air)
   - Add model explanation section
   - Add voice summary section

2. Update baseline.js:
   - Change API endpoint to /baseline/train-seu
   - Update request payload: {seu_name, energy_source, ...}
   - Parse new response fields: explanation, voice_summary
   - Display model details (R² score, coefficients with explanations)

3. Error handling:
   - 404 SEU not found → show ErrorMessage with available SEUs
   - 400 Invalid energy source → show valid options
   - 500 Server error → retry button

Test with: Compressor-1 (electricity), Boiler-1 (natural_gas)

#codebase
```

#### **Agent 2: Styling & UX**

**Prompt Template:**
```
# Context
Attach: Updated baseline.html from Agent 1
Attach: analytics/ui/static/css/components.css

# Task
Enhance baseline page UX:

1. Model explanation card:
   - Clear visual hierarchy
   - Icons for each coefficient explanation
   - Color-coded importance (high/medium/low)

2. Voice summary section:
   - Speech bubble design
   - TTS-friendly text display
   - Copy-to-clipboard button

3. Responsive design:
   - Mobile: stacked layout
   - Tablet: 2-column grid
   - Desktop: 3-column grid with sidebar

4. Loading states:
   - Show LoadingSpinner during API call
   - Skeleton loaders for model details
   - Smooth transitions

#codebase
```

---

### Milestone 6.3: Dashboard & Other Pages (4 days)

**Recommended Agent Strategy: 1 Plan + 4 Agents (parallel)**

#### **Orchestrator Chat (Plan Mode)**

**Prompt Template:**
```
# Context
Attach: docs/ENMS-v3.md (Milestone 6.3 requirements)
Attach: docs/api-documentation/ENMS-API-DOCUMENTATION-FOR-OVOS.md

# Task
Create parallel migration plan for 7 UI pages:

Pages to update:
1. Dashboard (index.html) - Add SEU stats, Performance Engine widgets
2. KPI (kpi.html) - Energy source breakdown charts
3. Model Performance (model-performance.html) - Add explanation tab
4. Anomaly (anomaly.html) - Filter by SEU
5. Forecast (forecast.html) - SEU-based predictions
6. Comparison (comparison.html) - Multi-SEU comparison
7. New: Performance Analysis (performance.html) - Phase 2 feature

For each page, specify:
- API endpoint updates (v2 → v3)
- New UI components needed
- Data visualization changes
- Testing scenarios

Organize by priority:
- High: Dashboard, KPI (business-critical)
- Medium: Model Performance, Anomaly
- Low: Forecast, Comparison
- New: Performance Analysis (Phase 2.2 integration)

#codebase
```

#### **Agent 1: Dashboard Page**

**Prompt Template:**
```
# Context
Attach: Plan from Orchestrator (Dashboard section)
Attach: analytics/ui/templates/index.html
Attach: docs/api-documentation/ENMS-API-DOCUMENTATION-FOR-OVOS.md

# Task
Update dashboard.html with v3 features:

1. SEU statistics cards:
   - Total SEUs: 10
   - Trained models per SEU
   - Energy sources per SEU
   - Status indicators (active/inactive)

2. Performance Engine integration (NEW):
   - Top 3 improvement opportunities
   - Estimated savings (kWh, cost)
   - Quick action buttons

3. API endpoints:
   - /api/v1/seus (SEU list)
   - /api/v1/factory/summary (factory stats)
   - /api/v1/performance/opportunities (top opportunities)

4. Responsive grid:
   - 1 column (mobile)
   - 2 columns (tablet)
   - 3 columns (desktop)

#codebase
```

#### **Agent 2: KPI Page**

**Prompt Template:**
```
# Context
Attach: Plan from Orchestrator (KPI section)
Attach: analytics/ui/templates/kpi.html

# Task
Update KPI page with energy source breakdown:

1. Multi-energy chart:
   - Stacked bar chart (4 energy sources)
   - Per-SEU breakdown
   - Color-coded by energy type

2. API endpoint:
   - /api/v1/kpi/energy-breakdown?seu_name=X&start_date=Y&end_date=Z

3. Filters:
   - SEU selector (multi-select)
   - Date range picker
   - Energy source checkboxes

4. Export functionality:
   - CSV download with all metrics
   - PDF report generation

#codebase
```

#### **Agent 3: Model Performance Page**

**Prompt Template:**
```
# Context
Attach: Plan from Orchestrator (Model Performance section)
Attach: analytics/ui/templates/model-performance.html

# Task
Add model explanation tab to model-performance.html:

1. New tab: "Explanation"
   - Natural language description
   - Coefficient importance chart
   - Feature correlation heatmap

2. API endpoint:
   - /api/v1/baseline/models?include_explanation=true

3. Visualization:
   - Horizontal bar chart (coefficient importance)
   - Tooltip with detailed explanations
   - Color gradient (positive/negative impact)

4. Comparison view:
   - Side-by-side model explanations
   - Diff highlighting (coefficient changes)

#codebase
```

#### **Agent 4: Testing & Validation**

**Prompt Template:**
```
# Context
Attach: All updated pages from Agents 1-3
Attach: analytics/tests/test_ui.py (if exists)

# Task
Create comprehensive UI test suite:

1. Automated tests (Selenium/Playwright):
   - Page loads without errors
   - API calls succeed
   - Charts render correctly
   - Responsive breakpoints work

2. Manual test checklist:
   - SEU selector works on all pages
   - Energy source filtering accurate
   - Charts display correct data
   - Error messages user-friendly
   - Loading states smooth

3. Cross-browser testing:
   - Chrome/Edge (Chromium)
   - Firefox
   - Safari

4. Create test report:
   docs/PHASE-6-UI-TEST-REPORT.md

#codebase
```

---

## Prompt Engineering Best Practices

### Context Attachment Strategy

**Always Attach These Files:**

```
For ANY Phase 6 work:
- docs/ENMS-v3.md (master plan, Phase 6 section)
- docs/api-documentation/ENMS-API-DOCUMENTATION-FOR-OVOS.md (v3 API reference)

For Component Work:
- analytics/ui/static/css/style.css (existing design system)
- analytics/ui/static/js/chart-utils.js (code patterns)

For API Migration:
- ENMS-API-DOCUMENTATION-FOR-OVOS.md (endpoint specs)
- docs/api-documentation/BURAK-API-MIGRATION-GUIDE.md (migration examples)

For Page Updates:
- Target HTML file (analytics/ui/templates/*.html)
- Target JS file (analytics/ui/static/js/*.js)
- API documentation for endpoints used
```

### Effective Prompt Structure

```
# Context (what agent needs to know)
Attach: [file1], [file2]
Current state: [brief description]

# Task (what to do)
Specific objective: [clear, actionable goal]

# Requirements (constraints & acceptance criteria)
- Requirement 1
- Requirement 2
- Requirement 3

# Success Criteria (how to validate)
- ✅ Criterion 1
- ✅ Criterion 2

# Tools/Context Hints
#codebase (for workspace search)
#file:path/to/specific/file (for targeted context)
#terminalSelection (if relevant command output)
```

### Example: Bad vs Good Prompts

❌ **Bad Prompt:**
```
Update the baseline page to v3
```

✅ **Good Prompt:**
```
# Context
Attach: docs/ENMS-v3.md (Milestone 6.2)
Attach: docs/api-documentation/ENMS-API-DOCUMENTATION-FOR-OVOS.md
Attach: analytics/ui/templates/baseline.html

# Task
Migrate baseline.html from v2 /ovos/train-baseline to v3 /baseline/train-seu endpoint

# Requirements
- Replace machine_id dropdown with SEU selector
- Add energy_source filter (4 options: electricity, natural_gas, steam, compressed_air)
- Update API call in baseline.js to use new endpoint
- Handle new response fields: explanation, voice_summary
- Show error message if SEU not found (404)

# Success Criteria
- ✅ SEU selector populated from /api/v1/seus endpoint
- ✅ Energy source filter working
- ✅ Training succeeds for Compressor-1 electricity
- ✅ Model explanation displayed
- ✅ No console errors

# Testing
Test with:
1. Compressor-1, electricity (single SEU)
2. Boiler-1, natural_gas (multi-energy machine)

#codebase
```

### Using Chat Tools & Context Items

**Available Tools:**

```
#codebase - Search entire workspace (use frequently!)
#file:path/to/file - Reference specific file
#selection - Current editor selection
#terminalSelection - Selected terminal output
#fetch:URL - Fetch web content (API docs, examples)
#githubRepo:owner/repo - Search GitHub repos
```

**Example with Multiple Tools:**
```
# Context
#codebase analytics/ui/templates/baseline.html
#file:docs/api-documentation/ENMS-API-DOCUMENTATION-FOR-OVOS.md
#fetch:https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API

# Task
Migrate baseline page API calls to v3 /baseline/train-seu endpoint using modern fetch API with error handling

#codebase
```

---

## Multi-Agent Workflow Examples

### Example 1: Component Library Creation

**Scenario:** Build LoadingSpinner, ErrorMessage, SEUSelector components in parallel

**Orchestrator Chat (Plan Mode):**
```
Create implementation plan for 3 reusable components:
1. LoadingSpinner (size variants, colors)
2. ErrorMessage (severity levels, retry actions)
3. SEUSelector (dropdown with search)

Attach: docs/ENMS-v3.md (Milestone 6.1)
#codebase
```

**Agent 1 (LoadingSpinner):**
```
Implement LoadingSpinner component from plan step 1:
- 3 sizes (sm, md, lg)
- 2 color themes (light, dark)
- Animated SVG spinner
- File: analytics/ui/static/js/components/loading-spinner.js

Attach: [plan output from Orchestrator]
#codebase
```

**Agent 2 (ErrorMessage):**
```
Implement ErrorMessage component from plan step 2:
- 4 severity types (info, warning, error, success)
- Retry button support
- Dismissible
- File: analytics/ui/static/js/components/error-message.js

Attach: [plan output from Orchestrator]
#codebase
```

**Agent 3 (SEUSelector):**
```
Implement SEUSelector component from plan step 3:
- Searchable dropdown
- Multi-energy machine support (show energy sources)
- Load data from /api/v1/seus endpoint
- File: analytics/ui/static/js/components/seu-selector.js

Attach: [plan output from Orchestrator]
Attach: docs/api-documentation/ENMS-API-DOCUMENTATION-FOR-OVOS.md
#codebase
```

**Coordination Steps:**
1. Orchestrator creates plan (5 min)
2. Start Agents 1, 2, 3 in parallel (15 min each)
3. Review all changes together (10 min)
4. Run integration test (Agent 4)
5. Commit checkpoint: "feat: Add component library (LoadingSpinner, ErrorMessage, SEUSelector)"

---

### Example 2: Multi-Page API Migration

**Scenario:** Update 7 pages to v3 endpoints in parallel

**Orchestrator Chat (Plan Mode):**
```
Create parallel migration plan for 7 UI pages to v3 API:
1. Dashboard (index.html)
2. KPI (kpi.html)
3. Model Performance (model-performance.html)
4. Anomaly (anomaly.html)
5. Forecast (forecast.html)
6. Comparison (comparison.html)
7. Performance Analysis (performance.html - NEW)

For each page:
- v2 → v3 endpoint mapping
- UI changes required
- Testing scenarios

Attach: docs/ENMS-v3.md (Milestone 6.3)
Attach: docs/api-documentation/ENMS-API-DOCUMENTATION-FOR-OVOS.md
#codebase
```

**Agent 1 (Dashboard):**
```
Update dashboard (index.html) to v3:
- API: /api/v1/factory/summary
- Add SEU stats cards
- Add Performance Engine widget (top opportunities)

Attach: [Dashboard section from plan]
Attach: analytics/ui/templates/index.html
#codebase
```

**Agent 2 (KPI):**
```
Update KPI page (kpi.html) to v3:
- API: /api/v1/kpi/energy-breakdown
- Add energy source breakdown chart
- Add SEU filter dropdown

Attach: [KPI section from plan]
Attach: analytics/ui/templates/kpi.html
#codebase
```

**Agent 3 (Model Performance):**
```
Update model-performance.html to v3:
- API: /api/v1/baseline/models?include_explanation=true
- Add "Explanation" tab
- Display coefficient importance chart

Attach: [Model Performance section from plan]
Attach: analytics/ui/templates/model-performance.html
#codebase
```

**Agent 4 (Remaining Pages):**
```
Update anomaly, forecast, comparison pages to v3:
- Update endpoint paths (/ovos/* → new paths)
- Add SEU selectors
- Maintain existing functionality

Attach: [Remaining pages section from plan]
Attach: analytics/ui/templates/anomaly.html
Attach: analytics/ui/templates/forecast.html
Attach: analytics/ui/templates/comparison.html
#codebase
```

**Coordination:**
1. Orchestrator plan (10 min)
2. Agents 1-4 work in parallel (30 min each)
3. Review all diffs together (20 min)
4. Test each page manually (10 min each = 70 min)
5. Commit checkpoint: "feat: Migrate all UI pages to v3 API"

---

## Safety & Rollback Plan

### Before Starting Phase 6

✅ **Current Checkpoint:** `v3.0.0-phase5.1-complete` (commit df7ce17)

### During Phase 6 Work

**Create Sub-Checkpoints:**

```bash
# After each milestone
git add analytics/ui/
git commit -m "v3: Phase 6.1 complete - Component library"
git tag v3.0.0-phase6.1-complete

git add analytics/ui/
git commit -m "v3: Phase 6.2 complete - Baseline page overhaul"
git tag v3.0.0-phase6.2-complete
```

### If Agents "Ruin" Code

**Rollback Strategy:**

```bash
# Option 1: Rollback to last checkpoint
git reset --hard v3.0.0-phase5.1-complete

# Option 2: Rollback specific files
git checkout v3.0.0-phase5.1-complete -- analytics/ui/templates/baseline.html
git checkout v3.0.0-phase5.1-complete -- analytics/ui/static/js/baseline.js

# Option 3: Undo last commit (if not pushed)
git reset --soft HEAD~1  # Keep changes in staging
git reset --hard HEAD~1  # Discard changes completely
```

### Review Changes Before Committing

**Use Git Diff:**
```bash
# See all changes
git diff

# See changes in specific file
git diff analytics/ui/templates/baseline.html

# See staged changes
git diff --staged
```

**Use VS Code Source Control:**
- Open Source Control panel (Ctrl+Shift+G)
- Review each file individually
- Discard unwanted changes
- Stage only validated changes

### Testing Before Commit

**Checklist:**
```
✅ Page loads without errors
✅ API calls succeed (check browser console)
✅ UI components render correctly
✅ No JavaScript errors in console
✅ Responsive design works (test mobile, tablet, desktop)
✅ Error handling works (test invalid inputs)
✅ Backend tests still passing (docker-compose exec analytics pytest)
```

---

## Troubleshooting

### Issue 1: Agent Makes Wrong Changes

**Symptoms:**
- Changes unrelated files
- Breaks existing functionality
- Doesn't follow instructions

**Solutions:**
1. **More Specific Context:**
   - Attach exact files to change
   - Use `#file:path` instead of `#codebase`
   - Add explicit "DO NOT MODIFY" instructions

2. **Switch to Edit Mode:**
   - Select specific code block
   - Use Edit mode instead of Agent mode
   - More controlled changes

3. **Break Down Task:**
   - Smaller, more focused prompts
   - One file at a time
   - Iterative approach

---

### Issue 2: Agent Can't Find Context

**Symptoms:**
- Asks for clarification repeatedly
- Makes incorrect assumptions
- Doesn't reference attached files

**Solutions:**
1. **Build Workspace Index:**
   ```
   Ctrl+Shift+P → "Build Remote Workspace Index"
   ```
   - Requires GitHub repo connection
   - Makes `#codebase` searches faster

2. **Explicit File References:**
   - Don't rely on `#codebase` alone
   - Attach specific files: `#file:analytics/ui/templates/baseline.html`
   - Paste relevant code snippets in prompt

3. **Push Code to GitHub:**
   ```bash
   git push origin main
   ```
   - Enables remote indexing
   - Better workspace search

---

### Issue 3: Plan Mode Not Available

**Symptoms:**
- "Plan" not in chat mode dropdown

**Solutions:**
1. **Use VS Code Insiders:**
   - Plan mode only in Insiders (November 2025+)
   - Download: https://code.visualstudio.com/insiders/

2. **Update VS Code Insiders:**
   ```
   Help → Check for Updates
   ```

3. **Fallback to Agent Mode:**
   - Use Agent mode with detailed prompts
   - Request step-by-step execution
   - Manual coordination between agents

---

### Issue 4: Changes Not Applied

**Symptoms:**
- Agent says "changes applied" but files unchanged

**Solutions:**
1. **Check Review UI:**
   - Look for diff editor overlay
   - Accept/reject changes manually
   - Check notifications panel

2. **Reload Window:**
   ```
   Ctrl+Shift+P → "Reload Window"
   ```

3. **Check File Permissions:**
   - Files not read-only
   - Workspace folder writable

---

### Issue 5: Too Many Changes at Once

**Symptoms:**
- Overwhelming diff review
- Can't track what changed

**Solutions:**
1. **Smaller Tasks:**
   - One component per agent session
   - One page per agent session
   - Incremental changes

2. **Use Git Staging:**
   - Review changes file-by-file
   - Stage approved changes
   - Discard questionable changes

3. **Commit Frequently:**
   - After each logical unit
   - Easier rollback
   - Clear history

---

## Quick Reference Commands

### Chat Shortcuts

```
Ctrl+Alt+I        - Open Chat View
Ctrl+I            - Open Inline Chat
Ctrl+Shift+I      - Open Quick Chat
Ctrl+Shift+P      - Command Palette
```

### Context Items

```
#codebase         - Search workspace
#file:path        - Reference file
#selection        - Current selection
#terminalSelection - Terminal output
#fetch:URL        - Fetch web content
```

### Git Checkpoints

```bash
# Create checkpoint
git add -A
git commit -m "v3: Phase 6.X - [description]"
git tag v3.0.0-phase6.X-complete

# Rollback
git reset --hard <commit-hash>
git checkout <tag> -- <file>
```

---

## Next Steps

1. **Open VS Code Insiders** with EnMS workspace
2. **Verify checkpoint:** `git status` should be clean, `git log -1` shows df7ce17
3. **Attach context files** to first Plan mode chat:
   - docs/ENMS-v3.md
   - docs/api-documentation/ENMS-API-DOCUMENTATION-FOR-OVOS.md
4. **Start with Milestone 6.1** (Component Library)
5. **Use orchestration strategy** from this guide
6. **Commit frequently** with sub-checkpoints

---

**Document Status:** ✅ Ready for Use  
**Rollback Tag:** `v3.0.0-phase5.1-complete`  
**Next Milestone:** Phase 6.1 - Component Library (2 days)

Good luck with the swarm! 🚀
