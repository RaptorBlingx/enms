# EnMS v3 Frontend Modernization - Project Plan

**Project Name:** EnMS Frontend v3.0  
**Start Date:** November 10, 2025  
**Backend Status:** ✅ v3 API Complete (Phase 0-5 done)  
**Current Phase:** Phase 6 - Frontend Modernization  
**Target Completion:** November 20, 2025 (8 working days)

---

## 🎯 Executive Summary

### Context
EnMS backend has been fully modernized to v3 with:
- ✅ Clean RESTful API (no `/ovos/*` paths)
- ✅ SEU-based architecture (ISO 50001 compliant)
- ✅ Performance Engine with root cause analysis
- ✅ Multi-energy support (electricity, natural_gas, steam, compressed_air)
- ✅ 32/32 end-to-end tests passing

**Problem:** Frontend UI is 6 months behind - still uses v2 patterns and missing v3 features.

### Vision
Transform frontend from v2 data display to v3 intelligent energy management interface:
- **Current:** Machine-centric, single energy source, static charts
- **Target:** SEU-centric, multi-energy, Performance Engine integration, actionable insights

### Success Criteria
1. **100% v3 API coverage** - All pages use new endpoints
2. **SEU interface** - Dropdown selectors on every page
3. **Multi-energy support** - Charts show all 4 energy sources
4. **Performance Engine UI** - Opportunities, action plans, savings widgets
5. **Zero regressions** - All existing features work better
6. **Mobile responsive** - Works on tablet/phone
7. **Component library** - Reusable, consistent design

---

## 📊 Current State Assessment

### Existing Pages (7 total)

| Page | File | Status | v2 Endpoint Used | Missing v3 Features |
|------|------|--------|------------------|---------------------|
| Dashboard | `index.html` | 🟡 Partial | `/ovos/summary` | SEU stats, Performance widgets |
| Baseline Training | `baseline.html` | 🔴 v2 Only | `/ovos/train-baseline` | SEU selector, multi-energy, explanations |
| KPI Dashboard | `kpi.html` | 🟡 Partial | Mixed v2/v3 | Energy source breakdown |
| Model Performance | `model-performance.html` | 🟡 Partial | `/baseline/models` | Explanation tab, coefficient charts |
| Anomaly Detection | `anomaly.html` | 🟡 Partial | `/anomaly/*` | SEU filtering |
| Forecasting | `forecast.html` | 🟡 Partial | `/forecast/*` | SEU-based predictions |
| Comparison | `comparison.html` | 🟡 Partial | Mixed | Multi-SEU comparison |

### Technology Stack
- **Frontend:** Vanilla JavaScript (ES6+), no frameworks
- **Charts:** Chart.js 3.x
- **Styling:** Custom CSS with industrial design system
- **Architecture:** MVC pattern (simple)
  - Templates: `analytics/ui/templates/*.html`
  - Scripts: `analytics/ui/static/js/*.js`
  - Styles: `analytics/ui/static/css/*.css`

### Key Files Inventory
```
analytics/ui/
├── templates/
│   ├── index.html              # Dashboard (4,200 lines)
│   ├── baseline.html           # Baseline training (890 lines)
│   ├── kpi.html               # KPI dashboard (1,200 lines)
│   ├── model-performance.html # ML model metrics (980 lines)
│   ├── anomaly.html           # Anomaly detection (1,100 lines)
│   ├── forecast.html          # Energy forecasting (850 lines)
│   └── comparison.html        # Multi-machine comparison (920 lines)
├── static/
│   ├── js/
│   │   ├── chart-utils.js     # Chart helpers (780 lines)
│   │   ├── api-client.js      # API wrapper (450 lines)
│   │   ├── utils.js           # Common utilities (320 lines)
│   │   └── [page-specific].js # Per-page logic
│   └── css/
│       ├── style.css          # Main styles (2,400 lines)
│       └── components.css     # Component styles (TBD - Phase 6.1)
```

---

## 🏗️ Architecture Decisions

### Design Principles
1. **No frameworks** - Stick with vanilla JS (consistent with v2)
2. **Progressive enhancement** - Add v3 features without breaking v2 compatibility during transition
3. **Component-based** - Build reusable UI components
4. **API-first** - All data from v3 REST endpoints
5. **Mobile-first CSS** - Responsive breakpoints (768px, 1024px, 1440px)
6. **Accessibility** - ARIA labels, keyboard navigation
7. **Performance** - <100ms page load, lazy loading for charts

### Component Library Strategy
Create 5 core components (Milestone 6.1):
- **LoadingSpinner** - Replace all loading divs
- **ErrorMessage** - Standardize error displays
- **SEUSelector** - Reusable dropdown with search
- **EnergySourceFilter** - Multi-select for 4 energy types
- **ChartContainer** - Responsive wrapper for Chart.js

### API Migration Strategy
- **Phase 1:** Add new v3 calls alongside v2 (dual mode)
- **Phase 2:** Switch default to v3, keep v2 as fallback
- **Phase 3:** Remove v2 calls completely
- **Validation:** Test each page with Compressor-1 (single energy) + Boiler-1 (multi-energy)

---

## 🎨 Design System

### Color Palette (Industrial Theme)
```css
/* Primary Colors */
--primary-blue: #1e3a8a;      /* Headers, primary actions */
--primary-dark: #0f172a;      /* Navigation, text */

/* Status Colors */
--success-green: #10b981;     /* Success states, positive trends */
--warning-orange: #f59e0b;    /* Warnings, moderate issues */
--danger-red: #ef4444;        /* Errors, critical alerts */
--info-blue: #3b82f6;         /* Info messages, neutral states */

/* Neutral Grays */
--gray-50: #f9fafb;           /* Backgrounds */
--gray-100: #f3f4f6;          /* Cards, containers */
--gray-200: #e5e7eb;          /* Borders */
--gray-500: #6b7280;          /* Secondary text */
--gray-800: #1f2937;          /* Primary text */

/* Energy Source Colors (NEW) */
--electricity-color: #3b82f6;    /* Blue */
--natural-gas-color: #f59e0b;    /* Orange */
--steam-color: #ef4444;          /* Red */
--compressed-air-color: #10b981; /* Green */
```

### Typography
```css
/* Font Family */
font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Scale */
--text-xs: 0.75rem;   /* 12px - labels */
--text-sm: 0.875rem;  /* 14px - secondary text */
--text-base: 1rem;    /* 16px - body */
--text-lg: 1.125rem;  /* 18px - headings */
--text-xl: 1.25rem;   /* 20px - page titles */
--text-2xl: 1.5rem;   /* 24px - dashboard titles */
```

### Spacing Scale (4px base)
```css
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
```

### Responsive Breakpoints
```css
/* Mobile-first approach */
@media (min-width: 768px)  { /* Tablet */ }
@media (min-width: 1024px) { /* Desktop */ }
@media (min-width: 1440px) { /* Large desktop */ }
```

---

## 📋 Phase 6 Milestones

### Milestone 6.0: Component Architecture Design (0.5 days - 4 hours)
**Goal:** Define component communication, state management, and architectural patterns before coding  
**Status:** ✅ COMPLETE (November 10, 2025)  
**Git Commit:** 00c7e29

**Deliverables:**
- [x] `docs/frontend/COMPONENT-ARCHITECTURE.md` (architecture specification - 1,350 lines)
- [x] Event naming conventions (e.g., `seu:selected`, `energy:filtered`)
- [x] State management approach (localStorage for persistence, EventTarget for communication)
- [x] Data flow diagrams (ASCII art showing component interactions)
- [x] Extended API client with v3 endpoints
- [x] Error recovery playbook (timeout, network, 404, 500 strategies)
- [x] Multi-energy UX flows (single-energy vs multi-energy SEUs)

**Tasks:**
- [x] 6.0.1: Define component communication (CustomEvent system)
  - Event naming: `namespace:action` pattern
  - Event payload structure
  - Bubbling vs direct dispatch
  - Example: `seu:selected` → `{ seuName, energySources }`
- [x] 6.0.2: Design state persistence (localStorage schema)
  - Keys: `enms_seu_selection`, `enms_energy_filters`, `enms_date_range`
  - TTL for cached data (5 min for `/seus`, 1 min for metrics)
  - Versioning strategy (invalidate on schema change)
- [x] 6.0.3: Document lifecycle (init, render, update, destroy)
  - Component base class or mixin pattern
  - Cleanup on destroy (event listeners, timers)
  - Lazy initialization pattern
- [x] 6.0.4: Extend API client for v3 endpoints
  - Add methods: `getSEUs()`, `trainBaseline()`, `getOpportunities()`
  - Response caching for frequently called endpoints
  - Request queue for slow endpoints (>5s)
  - Automatic retry logic (3 attempts, exponential backoff)
  - Standardized error format: `{ code, message, retryable }`
- [x] 6.0.5: Create error recovery playbook
  - **Timeout errors** (>30s): "Still working..." message, cancel button
  - **Network errors**: Auto-retry 3 times with 5s delay
  - **404 errors**: Show available options, no auto-retry
  - **500 errors**: Manual retry button, log to console
- [x] 6.0.6: Define multi-energy UX flows
  - **Single-energy machine** (Compressor-1): Auto-select energy source (disabled filter)
  - **Multi-energy machine** (Boiler-1): Radio buttons for ONE energy source selection
  - **Multi-SEU comparison**: Checkboxes for multiple energy sources
  - Visual indicators: Grayed out (unavailable), blue highlight (available)
- [x] 6.0.7: Progressive loading orchestration
  - Dashboard widgets load independently (don't block each other)
  - Skeleton screens for slow endpoints (>3s)
  - Failed widgets show inline errors (other widgets still work)
  - Example pattern: `LoadingOrchestrator` utility

**Example Component Communication Pattern:**
```javascript
// SEUSelector fires event when selection changes
class SEUSelector extends EventTarget {
  selectSEU(seuName, energySources) {
    this.dispatchEvent(new CustomEvent('seu:selected', {
      detail: { seuName, energySources },
      bubbles: true
    }));
  }
}

// Baseline page listens for selection
seuSelector.addEventListener('seu:selected', (e) => {
  const { seuName, energySources } = e.detail;
  energyFilter.update(energySources); // Update dependent component
  loadBaselineData(seuName); // Fetch data
});
```

**Example API Client Extensions:**
```javascript
// analytics/ui/static/js/api-client.js additions
class APIClient {
  constructor() {
    this._cache = new Map();
    this._requestQueue = [];
  }

  async getSEUs(cache = true) {
    const cacheKey = 'seus_list';
    if (cache) {
      const cached = this._cache.get(cacheKey);
      if (cached && Date.now() - cached.timestamp < 300000) { // 5min TTL
        return cached.data;
      }
    }
    const data = await this.get('/api/v1/seus');
    this._cache.set(cacheKey, { data, timestamp: Date.now() });
    return data;
  }

  async trainBaseline(seuName, energySource, days = 30) {
    return this.post('/api/v1/baseline/train-seu', {
      seu_name: seuName,
      energy_source: energySource,
      days
    });
  }

  async getOpportunities(timeout = 60000) {
    // Slow endpoint - special handling
    return this.get('/api/v1/performance/opportunities', { timeout });
  }

  async get(url, options = {}) {
    const { timeout = 10000, retries = 3 } = options;
    for (let i = 0; i < retries; i++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);
        const response = await fetch(url, { signal: controller.signal });
        clearTimeout(timeoutId);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
      } catch (error) {
        if (i === retries - 1) throw this._formatError(error);
        await this._sleep(Math.pow(2, i) * 1000); // Exponential backoff
      }
    }
  }

  _formatError(error) {
    if (error.name === 'AbortError') {
      return { code: 'TIMEOUT', message: 'Request timed out', retryable: true };
    }
    if (!navigator.onLine) {
      return { code: 'NETWORK', message: 'No internet connection', retryable: true };
    }
    if (error.message.includes('404')) {
      return { code: 'NOT_FOUND', message: 'Resource not found', retryable: false };
    }
    return { code: 'SERVER_ERROR', message: error.message, retryable: true };
  }

  _sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

**Example Multi-Energy UX:**
```javascript
// Baseline page: Handle SEU selection
async function handleSEUSelected(seuName) {
  const seus = await apiClient.getSEUs();
  const selectedSEU = seus.find(s => s.seu_name === seuName);
  
  if (selectedSEU.energy_sources.length === 1) {
    // Single-energy machine: Auto-select, disable filter
    energyFilter.setOptions(selectedSEU.energy_sources, { disabled: true });
    energyFilter.select(selectedSEU.energy_sources[0]);
    enableTrainingForm();
  } else {
    // Multi-energy machine: User must select ONE
    energyFilter.setOptions(selectedSEU.energy_sources, { 
      mode: 'radio', // Only one selection allowed
      disabled: false 
    });
    disableTrainingForm(); // Wait for energy source selection
  }
}
```

**Example Progressive Loading:**
```javascript
// Dashboard: Load widgets independently
const widgets = [
  { id: 'factory-summary', endpoint: '/api/v1/factory/summary', timeout: 5000 },
  { id: 'seus', endpoint: '/api/v1/seus', timeout: 2000 },
  { id: 'opportunities', endpoint: '/api/v1/performance/opportunities', timeout: 60000 }
];

widgets.forEach(async (widget) => {
  const container = document.getElementById(widget.id);
  try {
    loadingSpinner.show(container); // Show skeleton
    const data = await apiClient.get(widget.endpoint, { timeout: widget.timeout });
    renderWidget(widget.id, data);
  } catch (error) {
    errorMessage.show(container, {
      type: error.code === 'TIMEOUT' ? 'warning' : 'error',
      message: error.message,
      retryable: error.retryable,
      onRetry: () => loadWidget(widget)
    });
  } finally {
    loadingSpinner.hide(container);
  }
});
```

**Success Criteria:**
- ✅ Component communication pattern documented (CustomEvent system)
- ✅ State persistence schema defined (localStorage keys, TTL)
- ✅ API client extended with v3 endpoints (caching, retry logic)
- ✅ Error recovery strategies defined (4 error types)
- ✅ Multi-energy UX flows specified (3 scenarios)
- ✅ Progressive loading pattern documented
- ✅ Architecture doc complete (<5 pages)

**Testing:**
- ✅ Review architecture doc with human (30 min discussion)
- ✅ Validate event naming conventions (no conflicts)
- ✅ Test API client caching (verify TTL works)
- ✅ Mock multi-energy SEU selection (verify radio buttons)

**Completion Notes:**
- Document created: `docs/frontend/COMPONENT-ARCHITECTURE.md` (1,350 lines)
- All 7 tasks completed with working code examples
- 4 data flow diagrams (baseline, dashboard, communication flows)
- Ready to proceed to Milestone 6.1 (Component Library)
- Git checkpoint: commit `00c7e29` (November 10, 2025)

---

### Milestone 6.1: Component Library (2 days)
**Goal:** Build reusable UI components following DRY principle  
**Status:** ✅ COMPLETE (November 10, 2025)  
**Git Commit:** (pending - see below)

**Deliverables:**
- [x] `analytics/ui/static/js/components/base-component.js` (311 lines - foundation class)
- [x] `analytics/ui/static/js/components/loading-spinner.js` (104 lines)
- [x] `analytics/ui/static/js/components/error-message.js` (173 lines)
- [x] `analytics/ui/static/js/components/seu-selector.js` (220 lines)
- [x] `analytics/ui/static/js/components/energy-source-filter.js` (227 lines)
- [x] `analytics/ui/static/js/components/chart-container.js` (470 lines)
- [x] `analytics/ui/static/js/utils/state-manager.js` (214 lines - localStorage wrapper)
- [x] `analytics/ui/static/js/utils/loading-orchestrator.js` (340 lines - progressive loading)
- [x] `analytics/ui/static/js/api-client.js` (520 lines - v3 endpoints)
- [x] `analytics/ui/static/css/components.css` (650 lines - unified styles)
- [x] `analytics/ui/templates/components-demo.html` (demo page with all components)

**Tasks:**
- [x] 6.1.1: Create BaseComponent utility class
  - EventTarget extension for component lifecycle
  - State management with `setState()` triggering re-render
  - Automatic cleanup tracking (listeners, timers, intervals)
  - `emit()`, `on()`, `off()` helpers
  - `showLoading()`, `hideLoading()`, `showError()` shortcuts
  - JSDoc documentation (all methods)
- [x] 6.1.2: Create LoadingSpinner component
  - 3 sizes (sm, md, lg) with CSS variables
  - 2 modes (inline, overlay with backdrop)
  - 2 colors (primary blue, white for overlays)
  - Fade-out animation on hide
  - Message support: `show(message)`, `updateMessage()`
- [x] 6.1.3: Create ErrorMessage component
  - 4 types (error, warning, info, success)
  - Retry button for retryable errors
  - Dismissible with close button
  - Auto-hide for success messages (5s default)
  - Shortcuts: `showError()`, `showWarning()`, `showInfo()`, `showSuccess()`
- [x] 6.1.4: Create SEUSelector component
  - Single-select (dropdown) and multi-select (checkboxes) modes
  - Fetches from `/api/v1/seus` with 5min cache
  - Fires `seu:selected` event with `{ seuName, seuId, energySources, machineType }`
  - Restores previous selection from localStorage
  - `selectSEU()`, `getSelected()`, `clearSelection()` API
- [x] 6.1.5: Create EnergySourceFilter component
  - 4 energy sources with icons and colors (electricity, natural_gas, steam, compressed_air)
  - Auto-select for single-energy SEUs (disabled, grayed out)
  - Radio buttons for multi-energy SEUs (select ONE)
  - Checkboxes for comparison mode (select many)
  - Listens for `seu:selected` event, auto-configures
  - Fires `energy:filtered` event with `{ sources, seuName }`
  - Visual indicators: colored border, badges (unavailable, auto-selected)
- [x] 6.1.6: Create ChartContainer component
  - Responsive Chart.js wrapper with debounced resize
  - Loading and error state UI
  - Export to PNG (canvas.toDataURL) and CSV (data to CSV converter)
  - Fullscreen mode with `requestFullscreen()`
  - `renderChart()`, `updateData()`, `showNoData()` methods
  - ResizeObserver for dynamic sizing
- [x] 6.1.7: Create StateManager utility
  - localStorage wrapper with TTL expiration
  - `get(key, version)`, `set(key, data, ttl, version)`
  - Auto-cleanup on page load (`clearExpired()`)
  - Storage quota handling (graceful degradation)
  - `getStats()` returns usage metrics
- [x] 6.1.8: Create LoadingOrchestrator utility
  - Progressive loading coordinator with priority queue
  - Task dependencies (wait for task X before starting Y)
  - Timeout per task (default 30s)
  - Concurrent execution (max 3 parallel tasks)
  - `addTask()`, `executeAll()`, `getStats()` API
  - `onProgress`, `onTaskStart`, `onTaskComplete`, `onTaskError` callbacks
- [x] 6.1.9: Extend APIClient with v3 endpoints
  - `getSEUs()`, `getSEU(id)`, `getEnergyData()`
  - `trainBaseline()`, `getBaseline()`, `getOpportunities()`
  - `getKPIs()`, `getAnomalies()`, `getForecast()`, `getModelPerformance()`
  - Retry logic (3 attempts, exponential backoff: 2s, 4s, 8s)
  - Response caching with TTL (5min for SEUs, 1min for metrics)
  - AbortController for timeout (30s default)
  - Standardized error format: `{ code, message, retryable }`
- [x] 6.1.10: Create components.css stylesheet
  - CSS variables for design system (colors, spacing, typography)
  - All component styles (loading, error, seu, energy, chart)
  - Responsive breakpoints (768px, 480px)
  - Accessibility (focus-visible, reduced-motion, skip-to-content)
  - Utility classes (text-muted, form-control)
- [x] 6.1.11: Create component demo page
  - Interactive showcase HTML with all components
  - Event logging for `seu:selected`, `energy:filtered`, `chart:*` events
  - Demo controls (buttons to test all states)
  - Chart.js integration test (line, bar, error, no-data)
  - LoadingOrchestrator example (progressive widget loading)
  - API client test scenarios (success, cache, retry, timeout)

**Success Criteria:**
- ✅ All 6 components extend BaseComponent
- ✅ Consistent event naming (`namespace:action`)
- ✅ All components use StateManager for persistence
- ✅ Mobile responsive tested (<768px breakpoint)
- ✅ JSDoc comments for all public methods
- ✅ Demo page includes all components

**Testing (PENDING - Task 6.1.12):**
```bash
# Open demo page
open http://localhost:8001/ui/components-demo

# Test checklist:
1. LoadingSpinner: All 3 sizes, inline + overlay modes
2. ErrorMessage: All 4 types, retry button, auto-hide
3. SEUSelector: Dropdown loads, selection fires event, localStorage
4. EnergySourceFilter: Auto-select (single), radio (multi), checkboxes (comparison)
5. ChartContainer: Render chart, export PNG/CSV, fullscreen
6. LoadingOrchestrator: Progressive loading, progress bar updates
7. Mobile: All components responsive at 768px, 480px breakpoints
```

---

### Milestone 6.2: Baseline Page Overhaul (2 days)
**Goal:** Modernize baseline training page to use v3 API with SEU interface

**Current Problems:**
- Uses deprecated `/ovos/train-baseline` endpoint
- Machine selector instead of SEU selector
- No energy source filter
- No model explanations displayed
- No voice summary for OVOS

**Target State:**
- Uses `/api/v1/baseline/train-seu` endpoint
- SEU selector (replaces machine dropdown)
- Energy source filter (4 options)
- Model explanation card with coefficient importance
- Voice summary display for TTS
- Multi-energy training workflow

**Deliverables:**
- [ ] Updated `analytics/ui/templates/baseline.html`
- [ ] Updated `analytics/ui/static/js/baseline.js`
- [ ] Updated `analytics/ui/static/css/baseline.css` (if needed)

**Tasks:**
- [ ] 6.2.1: Update HTML structure
  - Replace machine selector with SEUSelector component
  - Add EnergySourceFilter component
  - Add model explanation card section
  - Add voice summary section
  - Update form validation
- [ ] 6.2.2: Update JavaScript logic
  - Change API endpoint to `/baseline/train-seu`
  - Update request payload: `{seu_name, energy_source, ...}`
  - Parse new response fields: `explanation`, `voice_summary`
  - Display coefficient importance chart
  - Handle multi-energy machines (e.g., Boiler-1)
- [ ] 6.2.3: Update error handling
  - 404 SEU not found → show ErrorMessage with available SEUs
  - 400 Invalid energy source → show valid options
  - 500 Server error → retry button
  - Training in progress → show LoadingSpinner
- [ ] 6.2.4: Add model explanation visualization
  - Horizontal bar chart for coefficient importance
  - Tooltip with detailed explanations
  - Color gradient (positive/negative impact)
  - Natural language summary
- [ ] 6.2.5: Add voice summary display
  - Speech bubble design
  - TTS-friendly text format
  - Copy-to-clipboard button
  - OVOS integration hints
- [ ] 6.2.6: Responsive design updates
  - Mobile: stacked layout
  - Tablet: 2-column grid
  - Desktop: 3-column grid with sidebar

**API Integration:**
```javascript
// OLD (v2 - deprecated)
POST /api/v1/ovos/train-baseline
{
  "machine_id": "c0000000-0000-0000-0000-000000000001"
}

// NEW (v3)
POST /api/v1/baseline/train-seu
{
  "seu_name": "Compressor-1",
  "energy_source": "electricity",
  "days": 30
}

Response:
{
  "success": true,
  "seu_name": "Compressor-1",
  "energy_source": "electricity",
  "model_version": "v1.2.3",
  "r_squared": 0.94,
  "explanation": {
    "summary": "Strong model with 94% accuracy...",
    "coefficients": [...]
  },
  "voice_summary": "Baseline model trained successfully for Compressor-1 electricity..."
}
```

**Success Criteria:**
- ✅ SEU selector populated from `/api/v1/seus`
- ✅ Energy source filter works
- ✅ Training succeeds for Compressor-1 (single energy)
- ✅ Training succeeds for Boiler-1 (multi-energy)
- ✅ Model explanation displays correctly
- ✅ Voice summary shows in speech bubble
- ✅ Error messages user-friendly
- ✅ Mobile responsive
- ✅ No console errors

**Testing Scenarios:**
```bash
# Test 1: Single energy machine
SEU: Compressor-1
Energy: electricity
Expected: Training success, model explanation shown

# Test 2: Multi-energy machine
SEU: Boiler-1
Energy: natural_gas
Expected: Training success, gas-specific model

# Test 3: Invalid SEU
SEU: InvalidMachine-999
Expected: 404 error with available SEUs list

# Test 4: Missing energy source
SEU: Boiler-1
Energy: (none selected)
Expected: 400 error with valid options
```

---

### Milestone 6.3: Dashboard & Remaining Pages (4 days)
**Goal:** Migrate all 6 remaining pages to v3 API

**Strategy:** Prioritize by business impact
- **High Priority (Day 1-2):** Dashboard, KPI (most used)
- **Medium Priority (Day 3):** Model Performance, Anomaly
- **Low Priority (Day 4):** Forecast, Comparison

---

#### 6.3.1: Dashboard Page (Day 1 - High Priority)

**Current State:**
- Uses `/ovos/summary` endpoint
- Machine-centric view
- Single energy source
- No Performance Engine widgets

**Target State:**
- Uses `/api/v1/factory/summary`, `/api/v1/seus`, `/api/v1/performance/opportunities`
- SEU statistics cards
- Multi-energy breakdown
- Performance Engine widget (top 3 opportunities)
- ISO 50001 compliance widget

**Deliverables:**
- [ ] Updated `analytics/ui/templates/index.html`
- [ ] Updated `analytics/ui/static/js/dashboard.js`

**Tasks:**
- [ ] 6.3.1.1: Add SEU statistics section
  - Total SEUs card (10 total)
  - Trained models per SEU
  - Energy sources per SEU
  - Status indicators (active/inactive)
  - Quick links to SEU details
- [ ] 6.3.1.2: Add Performance Engine widget (NEW)
  - Top 3 improvement opportunities
  - Estimated savings (kWh, USD)
  - Priority badges (high/medium/low)
  - Quick action buttons ("Create Action Plan")
  - Real-time updates via WebSocket
- [ ] 6.3.1.3: Add multi-energy breakdown chart
  - Stacked bar chart (4 energy sources)
  - Color-coded by energy type
  - Percentage breakdown
  - Cost allocation
- [ ] 6.3.1.4: Update factory summary API call
  - Endpoint: `/api/v1/factory/summary`
  - Display total energy, cost, carbon across all sources
  - Today vs yesterday comparison
- [ ] 6.3.1.5: Add ISO 50001 compliance widget
  - EnPI trend chart
  - Active action plans count
  - Compliance score (if available)
- [ ] 6.3.1.6: Responsive grid layout
  - Mobile: 1 column (stack all widgets)
  - Tablet: 2 columns
  - Desktop: 3 columns
  - Large desktop: 4 columns

**API Endpoints Used:**
- `GET /api/v1/factory/summary` - Factory-level stats
- `GET /api/v1/seus` - SEU list
- `GET /api/v1/performance/opportunities` - Top opportunities (⚠️ 35s response - set 60s timeout)
- `GET /api/v1/iso50001/enpi-report` - EnPI data

**Success Criteria:**
- ✅ All widgets load data correctly
- ✅ Performance widget shows top 3 opportunities
- ✅ Multi-energy chart displays all 4 sources
- ✅ SEU stats accurate (10 SEUs total)
- ✅ Responsive on mobile/tablet/desktop
- ✅ Page load <2 seconds
- ✅ No API errors

---

#### 6.3.2: KPI Page (Day 2 - High Priority)

**Current State:**
- Mixed v2/v3 endpoints
- Single energy source charts
- No SEU filtering

**Target State:**
- 100% v3 endpoints
- Multi-energy stacked charts
- SEU filter dropdown
- Energy source breakdown
- Export to CSV/PDF

**Deliverables:**
- [ ] Updated `analytics/ui/templates/kpi.html`
- [ ] Updated `analytics/ui/static/js/kpi.js`

**Tasks:**
- [ ] 6.3.2.1: Add SEU filter
  - Use SEUSelector component
  - Multi-select support
  - "All SEUs" option
  - Filter persistence (localStorage)
- [ ] 6.3.2.2: Add energy source breakdown chart
  - Stacked bar chart (4 energy sources)
  - Per-SEU breakdown
  - Time-series (hourly, daily, weekly)
  - Color-coded by energy type
- [ ] 6.3.2.3: Update KPI calculation display
  - Energy intensity (kWh/unit)
  - Cost per unit ($/ unit)
  - Carbon intensity (kg CO₂/unit)
  - Specific energy consumption (SEC)
- [ ] 6.3.2.4: Add export functionality
  - CSV download (all KPIs)
  - PDF report generation
  - Email report option (future)
- [ ] 6.3.2.5: Add date range picker
  - Presets (Today, Last 7 days, Last 30 days, Custom)
  - Update charts on date change
  - Validate date ranges

**API Endpoint:**
- `GET /api/v1/kpi/energy-breakdown?seu_name={name}&start_date={date}&end_date={date}`

**Success Criteria:**
- ✅ SEU filter works (single + multi-select)
- ✅ Energy breakdown shows all 4 sources
- ✅ KPI calculations accurate
- ✅ Export to CSV works
- ✅ Date range filter works
- ✅ Charts responsive

---

#### 6.3.3: Model Performance Page (Day 3 - Medium Priority)

**Current State:**
- Uses v3 `/baseline/models` endpoint
- Missing explanation tab
- No coefficient visualization

**Target State:**
- Add "Explanation" tab
- Coefficient importance chart
- Feature correlation heatmap
- Model comparison view

**Deliverables:**
- [ ] Updated `analytics/ui/templates/model-performance.html`
- [ ] Updated `analytics/ui/static/js/model-performance.js`

**Tasks:**
- [ ] 6.3.3.1: Add tabbed interface
  - Tab 1: "Metrics" (existing)
  - Tab 2: "Explanation" (NEW)
  - Tab 3: "Comparison" (NEW)
  - Tab persistence
- [ ] 6.3.3.2: Create Explanation tab
  - Natural language summary
  - Coefficient importance chart (horizontal bars)
  - Feature correlation heatmap
  - Training data insights
- [ ] 6.3.3.3: Create Comparison tab
  - Side-by-side model comparison
  - Version diff highlighting
  - Performance trend over time
  - Regression detection
- [ ] 6.3.3.4: Add coefficient importance visualization
  - Horizontal bar chart
  - Tooltip with explanations
  - Color gradient (positive/negative)
  - Sort by importance
- [ ] 6.3.3.5: Add SEU filter
  - Filter models by SEU
  - Filter by energy source
  - "Show Active Only" toggle

**API Integration:**
```javascript
// Use include_explanation parameter
GET /api/v1/baseline/models?seu_name=Compressor-1&energy_source=electricity&include_explanation=true

Response:
{
  "models": [{
    "model_version": "v1.2.3",
    "r_squared": 0.94,
    "explanation": {
      "summary": "Strong model...",
      "coefficients": [
        {
          "feature": "total_production_count",
          "coefficient": 0.0082,
          "importance": 0.65,
          "interpretation": "Production count is the strongest predictor..."
        }
      ]
    }
  }]
}
```

**Success Criteria:**
- ✅ Explanation tab displays correctly
- ✅ Coefficient chart renders
- ✅ Comparison view works
- ✅ SEU filter functional
- ✅ Explanations match API response

---

#### 6.3.4: Anomaly Page (Day 3 - Medium Priority)

**Current State:**
- Uses v3 `/anomaly/*` endpoints
- No SEU filtering
- Mixed severity display

**Target State:**
- SEU filter dropdown
- Severity badges (color-coded)
- Real-time updates via WebSocket
- Anomaly details modal

**Deliverables:**
- [ ] Updated `analytics/ui/templates/anomaly.html`
- [ ] Updated `analytics/ui/static/js/anomaly.js`

**Tasks:**
- [ ] 6.3.4.1: Add SEU filter
  - Filter anomalies by SEU
  - "All SEUs" option
  - Active anomalies only toggle
- [ ] 6.3.4.2: Add severity badges
  - Color-coded (critical=red, warning=orange, normal=blue)
  - Icon per severity
  - Count per severity
- [ ] 6.3.4.3: Add anomaly details modal
  - Click anomaly to expand
  - Show full details
  - Chart with anomaly highlighted
  - Related anomalies
- [ ] 6.3.4.4: Add real-time updates
  - WebSocket connection
  - New anomaly notifications
  - Toast messages
  - Sound alert (optional)
- [ ] 6.3.4.5: Add date range filter
  - Presets (Today, Last 7 days, Custom)
  - Filter by detection time

**API Endpoints:**
- `GET /api/v1/anomaly/recent?machine_id={id}&severity={level}`
- `GET /api/v1/anomaly/active`
- WebSocket: `ws://localhost:8001/ws` (for real-time updates)

**Success Criteria:**
- ✅ SEU filter works
- ✅ Severity badges color-coded
- ✅ Modal shows details
- ✅ Real-time updates working
- ✅ No duplicate notifications

---

#### 6.3.5: Forecast Page (Day 4 - Low Priority)

**Current State:**
- Uses v3 `/forecast/*` endpoints
- Machine-centric
- No SEU filtering

**Target State:**
- SEU-based forecasting
- Multi-energy forecasts
- Confidence intervals
- Export to CSV

**Deliverables:**
- [ ] Updated `analytics/ui/templates/forecast.html`
- [ ] Updated `analytics/ui/static/js/forecast.js`

**Tasks:**
- [ ] 6.3.5.1: Add SEU selector
  - Replace machine dropdown
  - Load from `/api/v1/seus`
- [ ] 6.3.5.2: Add energy source filter
  - Multi-select for 4 energy types
  - Combined forecast option
- [ ] 6.3.5.3: Update forecast visualization
  - Line chart with confidence intervals
  - Actual vs forecast comparison
  - Multi-energy overlay (different colors)
- [ ] 6.3.5.4: Add forecast horizon selector
  - Short-term (24 hours)
  - Medium-term (7 days)
  - Long-term (30 days)
- [ ] 6.3.5.5: Add export functionality
  - CSV download
  - Chart image export

**API Endpoint:**
- `GET /api/v1/forecast/short-term?seu_name={name}&energy_source={source}`

**Success Criteria:**
- ✅ SEU selector works
- ✅ Energy source filter functional
- ✅ Forecast chart accurate
- ✅ Confidence intervals display
- ✅ Export works

---

#### 6.3.6: Comparison Page (Day 4 - Low Priority)

**Current State:**
- Mixed v2/v3 endpoints
- Machine comparison only
- Single energy source

**Target State:**
- SEU comparison
- Multi-energy comparison
- Side-by-side charts
- Benchmark against average

**Deliverables:**
- [ ] Updated `analytics/ui/templates/comparison.html`
- [ ] Updated `analytics/ui/static/js/comparison.js`

**Tasks:**
- [ ] 6.3.6.1: Update SEU selector
  - Multi-select (up to 5 SEUs)
  - "Compare to Factory Average" checkbox
- [ ] 6.3.6.2: Add energy source filter
  - Select which energy sources to compare
  - "All Sources" option
- [ ] 6.3.6.3: Update comparison charts
  - Side-by-side bar charts
  - Normalized comparison (per unit production)
  - Trend comparison (line charts)
- [ ] 6.3.6.4: Add benchmark overlay
  - Factory average line
  - Industry benchmark (if available)
  - Best performer highlight
- [ ] 6.3.6.5: Add comparison metrics table
  - Energy consumption
  - Cost
  - Carbon footprint
  - Efficiency ranking

**API Endpoint:**
- `GET /api/v1/timeseries/multi-machine/energy` (supports SEUs via machine_ids)

**Success Criteria:**
- ✅ Multi-SEU comparison works
- ✅ Energy source filter functional
- ✅ Benchmark overlay displays
- ✅ Metrics table accurate
- ✅ Charts render correctly

---

## 🧪 Testing Strategy

### Test Pyramid

```
         /\
        /  \
       / E2E \           5% - End-to-end workflows
      /------\
     /        \
    /Integration\        25% - API integration tests
   /------------\
  /              \
 /  Unit Tests    \      70% - Component unit tests
/------------------\
```

### Testing Levels

#### Level 1: Component Unit Tests (Milestone 6.1)
**Location:** `analytics/ui/static/js/components/__tests__/`

**Tools:** Jest (or similar) for JavaScript unit testing

**Coverage:**
- [ ] LoadingSpinner
  - Renders all 3 sizes correctly
  - Theme switching works
  - Animation starts/stops
- [ ] ErrorMessage
  - All 4 severity types display
  - Retry button fires event
  - Auto-hide works (5s)
  - Dismissible via close button
- [ ] SEUSelector
  - Loads SEUs from API
  - Search/filter works
  - Selection emits event
  - Multi-select toggles
- [ ] EnergySourceFilter
  - All 4 checkboxes work
  - Select All/Clear All buttons
  - Disabled state
  - Change event emitted
- [ ] ChartContainer
  - Renders Chart.js instance
  - Loading state shows
  - Error state shows
  - Export buttons work

**Run Command:**
```bash
npm test components
```

#### Level 2: Page Integration Tests (Milestones 6.2-6.3)
**Location:** `analytics/ui/tests/integration/`

**Tools:** Playwright or Selenium for browser automation

**Coverage:**
- [ ] Baseline Page
  - SEU selector populates from API
  - Energy source filter works
  - Training submits to correct endpoint
  - Model explanation displays
  - Voice summary shows
  - Error handling (404, 400, 500)
- [ ] Dashboard
  - All widgets load data
  - Performance widget shows opportunities
  - Multi-energy chart renders
  - SEU stats accurate
- [ ] KPI Page
  - SEU filter works
  - Energy breakdown chart renders
  - Export to CSV works
  - Date range filter updates data
- [ ] Model Performance Page
  - Explanation tab displays
  - Coefficient chart renders
  - Comparison view works
- [ ] Anomaly Page
  - SEU filter works
  - Severity badges display
  - Modal opens on click
  - Real-time updates work
- [ ] Forecast Page
  - SEU selector works
  - Forecast chart renders
  - Energy source filter works
- [ ] Comparison Page
  - Multi-SEU selection works
  - Comparison charts render
  - Benchmark overlay works

**Run Command:**
```bash
npm run test:integration
```

#### Level 3: End-to-End Workflows (Phase 6 Complete)
**Location:** `analytics/ui/tests/e2e/`

**Scenarios:**
1. **New User Onboarding**
   - Navigate to Dashboard
   - Explore SEU statistics
   - Click on SEU → view details
   - Train baseline model
   - View model explanation

2. **Daily Monitoring Workflow**
   - Check Dashboard for alerts
   - Review Performance opportunities
   - Investigate anomalies
   - Create action plan
   - Export KPI report

3. **Multi-Energy Machine Management**
   - Select Boiler-1 (3 energy sources)
   - Train electricity baseline
   - Train natural_gas baseline
   - Compare energy source costs
   - Identify optimization opportunities

4. **Mobile Access**
   - Open Dashboard on mobile
   - Navigate to Anomaly page
   - View anomaly details
   - Acknowledge alert

**Run Command:**
```bash
npm run test:e2e
```

### Testing Checklist (Before Milestone Completion)

**Milestone 6.1 Completion:**
- [ ] All component unit tests passing
- [ ] Demo page renders without errors
- [ ] Components work on mobile (< 768px)
- [ ] No console errors
- [ ] Accessibility (ARIA labels, keyboard nav)

**Milestone 6.2 Completion:**
- [ ] Baseline page integration tests passing
- [ ] Training succeeds for Compressor-1 (single energy)
- [ ] Training succeeds for Boiler-1 (multi-energy)
- [ ] Error handling works (404, 400, 500)
- [ ] Model explanation displays correctly
- [ ] Voice summary shows
- [ ] Mobile responsive

**Milestone 6.3 Completion:**
- [ ] All 6 page integration tests passing
- [ ] Dashboard widgets load correctly
- [ ] KPI export works
- [ ] Model Performance explanation tab works
- [ ] Anomaly real-time updates work
- [ ] Forecast chart renders
- [ ] Comparison multi-SEU works
- [ ] Mobile responsive (all pages)

**Phase 6 Final Validation:**
- [ ] All E2E workflows passing
- [ ] Performance: Page load <2s
- [ ] Performance: API calls <1s (except /performance/opportunities)
- [ ] No console errors (any page)
- [ ] No API errors (any page)
- [ ] Mobile responsive (all pages)
- [ ] Cross-browser (Chrome, Firefox, Safari)
- [ ] Accessibility (WCAG 2.1 Level AA)

---

## 🚀 Deployment Plan

### Pre-Deployment Checklist
- [ ] All tests passing (unit + integration + E2E)
- [ ] Code review completed
- [ ] Performance benchmarks met
- [ ] Accessibility audit passed
- [ ] Cross-browser testing done
- [ ] Mobile testing done
- [ ] Security review (XSS, CSRF)
- [ ] Documentation updated

### Deployment Steps

**Step 1: Backup Current UI**
```bash
# Backup current templates and static files
cd analytics/ui
tar -czf backup-ui-$(date +%Y%m%d).tar.gz templates/ static/
```

**Step 2: Deploy to Staging**
```bash
# Exclude demo page from deployment
rsync -av --exclude='components-demo.html' \
  analytics/ui/templates/ \
  enms-analytics:/app/ui/templates/

# Copy static files
docker cp analytics/ui/static/. enms-analytics:/app/ui/static/

# Restart analytics service
docker-compose restart analytics
```

**Step 2.5: Demo Page Access Strategy**
- **Development:** Demo page accessible at `/ui/components-demo`
- **Production:** Add to `.dockerignore` or exclude via rsync
- **Documentation:** Note in README: "Component demos available in development mode only"

```bash
# Option 1: Use .dockerignore (if using Docker COPY)
echo "analytics/ui/templates/components-demo.html" >> .dockerignore

# Option 2: Use rsync exclude (if copying manually)
# Already shown in Step 2 above
```

**Step 3: Smoke Test**
- [ ] Dashboard loads
- [ ] Baseline training works
- [ ] KPI page renders
- [ ] No 500 errors

**Step 4: Deploy to Production**
```bash
# Same as staging, but on production server
ssh production-server
cd /path/to/enms
docker-compose down analytics
docker-compose up -d analytics
```

**Step 5: Post-Deployment Monitoring**
- [ ] Check error logs: `docker-compose logs -f analytics`
- [ ] Monitor API response times
- [ ] Check user analytics (page views, errors)
- [ ] Verify WebSocket connections

### Rollback Plan

**If critical issues found:**
```bash
# Restore from backup
cd analytics/ui
tar -xzf backup-ui-YYYYMMDD.tar.gz
docker-compose restart analytics
```

**Rollback triggers:**
- Page load errors (500s)
- API integration failures
- Mobile rendering broken
- Performance degradation (>5s page load)
- Security vulnerability discovered

---

## 📊 Success Metrics

### Technical Metrics
| Metric | Baseline (v2) | Target (v3) | Measurement |
|--------|---------------|-------------|-------------|
| Page Load Time | 3.2s | <2s | Lighthouse |
| API Call Time | 0.8s | <0.5s | Browser DevTools |
| Component Reusability | 0% | 80%+ | Code analysis |
| Mobile Responsive | 60% | 100% | Manual testing |
| Console Errors | 12/page | 0/page | Browser console |
| Test Coverage | 0% | 70%+ | Jest coverage |
| Accessibility Score | 65 | 90+ | WAVE, axe |

### User Experience Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to Train Baseline | <30s | User testing |
| SEU Discovery Time | <10s | User testing |
| Energy Source Selection | <5s | User testing |
| Dashboard Comprehension | 90%+ understand widgets | User survey |
| Mobile Usability | 85%+ satisfaction | User survey |

### Business Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| OVOS Integration Success | 100% commands work | Burak feedback |
| User Adoption | 80% use v3 features within 1 month | Analytics |
| Feature Utilization | 60% use Performance Engine | Analytics |
| Bug Reports | <5 critical bugs | Issue tracker |
| Support Tickets | <10 UI-related tickets | Support system |

---

## 🛡️ Risk Management

### Risk Matrix

| Risk | Probability | Impact | Mitigation | Owner |
|------|-------------|--------|------------|-------|
| API endpoint changes mid-development | Low | High | Lock API version, use changelog | Backend team |
| Component library not reusable | Medium | Medium | Review after 6.1, refactor if needed | Frontend dev |
| Performance degradation | Medium | High | Benchmark after each milestone | Frontend dev |
| Mobile rendering issues | High | Medium | Test on real devices early (Day 3) | Frontend dev |
| Scope creep (new features) | High | Medium | Strict adherence to milestones, defer to Phase 7 | Project manager |
| Backend API bugs discovered | Medium | High | Report immediately, create workarounds | Both teams |
| Time overrun (>8 days) | Medium | Medium | Daily progress tracking, cut low-priority features | Project manager |
| Browser compatibility issues | Low | Medium | Test Chrome/Firefox/Safari in parallel | Frontend dev |

### Contingency Plans

**If Milestone 6.1 takes >2 days:**
- Reduce components to 3 (LoadingSpinner, ErrorMessage, SEUSelector only)
- Defer EnergySourceFilter, ChartContainer to 6.2/6.3

**If API integration fails:**
- Use mock data for development
- Continue UI work in parallel
- Integrate API when stable

**If performance targets not met:**
- Implement lazy loading for charts
- Add pagination for data tables
- Cache API responses (localStorage)
- Defer real-time updates to Phase 7

**If mobile testing reveals major issues:**
- Focus on desktop first (80% users)
- Create mobile-specific stylesheets
- Extend timeline by 2 days for mobile fixes

---

## 📚 Documentation

### Developer Documentation (create during Phase 6)
- [ ] `docs/frontend/COMPONENT-LIBRARY.md` - Component API reference
- [ ] `docs/frontend/STYLE-GUIDE.md` - CSS conventions, design system
- [ ] `docs/frontend/API-INTEGRATION.md` - How to call v3 endpoints
- [ ] `docs/frontend/TESTING-GUIDE.md` - How to run tests, write new tests
- [ ] `docs/frontend/DEPLOYMENT.md` - Deployment procedures

### User Documentation (create during Phase 6)
- [ ] `docs/user/WHATS-NEW-V3.md` - User-facing changelog
- [ ] `docs/user/SEU-GUIDE.md` - Understanding SEUs vs Machines
- [ ] `docs/user/MULTI-ENERGY-GUIDE.md` - Working with multi-energy machines
- [ ] `docs/user/PERFORMANCE-ENGINE.md` - Using Performance Engine features

### API Documentation Updates
- [ ] Update `ENMS-API-DOCUMENTATION-FOR-OVOS.md` with UI integration examples
- [ ] Add screenshots of UI consuming each endpoint
- [ ] Document WebSocket usage for real-time updates

---

## 🎯 Phase 6 Schedule

### Week 1 (Nov 10-14)
| Day | Milestone | Deliverables | Hours |
|-----|-----------|--------------|-------|
| Sun | **6.0 Architecture** | **Component patterns, API client, error recovery, multi-energy UX** | **4h** |
| Mon | 6.1 Start | LoadingSpinner, ErrorMessage | 8h |
| Tue | 6.1 Complete | SEUSelector, EnergySourceFilter, ChartContainer, Demo page | 8h |
| Wed | 6.2 Start | Baseline page HTML/JS updates | 8h |
| Thu | 6.2 Complete | Model explanation, voice summary, testing | 8h |
| Fri | 6.3.1 | Dashboard page updates | 8h |

### Week 2 (Nov 17-20)
| Day | Milestone | Deliverables | Hours |
|-----|-----------|--------------|-------|
| Mon | 6.3.2 | KPI page updates | 8h |
| Tue | 6.3.3-6.3.4 | Model Performance + Anomaly pages | 8h |
| Wed | 6.3.5-6.3.6 | Forecast + Comparison pages | 8h |
| Thu | Testing & Deployment | E2E tests, staging deployment | 8h |

**Total: 10.5 working days, 84 hours (was 80h - added 4h for Milestone 6.0)**

---

## 🎓 Self-Reflection Protocol

### Before Starting Phase 6

**AI Agent: Execute this self-reflection before implementing ANY code:**

```
<self_reflection>

STEP 1: Define Excellence Rubric (5-7 categories)
Create internal rubric for world-class frontend modernization:

1. Code Quality (20%)
   - Component reusability (DRY principle)
   - Clean, readable code
   - Proper error handling
   - JSDoc documentation

2. User Experience (25%)
   - Intuitive SEU selection
   - Clear energy source filtering
   - Fast page loads (<2s)
   - Mobile responsive
   - Accessibility (ARIA labels, keyboard nav)

3. API Integration (20%)
   - Correct v3 endpoints used
   - Proper error handling (404, 400, 500)
   - Efficient data fetching
   - Response validation

4. Visual Design (15%)
   - Consistent with design system
   - Industrial theme maintained
   - Multi-energy color coding
   - Responsive breakpoints

5. Testing Coverage (10%)
   - Unit tests for components
   - Integration tests for pages
   - E2E workflows
   - Edge cases covered

6. Performance (5%)
   - Page load <2s
   - API calls <1s
   - Smooth animations
   - No console errors

7. Documentation (5%)
   - JSDoc for components
   - Code comments where needed
   - User guide updates
   - Deployment docs

STEP 2: Analyze Each Milestone Against Rubric
For each milestone (6.1, 6.2, 6.3):
- Does it score 90%+ on ALL rubric categories?
- If not, what's missing?
- How can I improve before implementation?

STEP 3: Iterate Until Confident
Do NOT start coding until:
- Rubric scores 90%+ across all categories
- Implementation plan is crystal clear
- Edge cases identified and handled
- Testing strategy defined

STEP 4: Validate After Each Milestone
After completing each milestone:
- Re-score against rubric
- If any category <90%, refactor immediately
- Do NOT proceed to next milestone until current scores 90%+

</self_reflection>
```

### During Implementation

**Daily Reflection Questions:**
1. Am I following the design system strictly?
2. Are my components truly reusable?
3. Have I tested on mobile (<768px)?
4. Are error messages user-friendly?
5. Is my code self-documenting?
6. Have I created unit tests?
7. Does this work for multi-energy machines?

### After Each Milestone

**Checkpoint Questions:**
1. Does this score 90%+ on my rubric?
2. Would I be proud to demo this?
3. Can another developer understand my code?
4. Have I tested all edge cases?
5. Is performance acceptable?
6. Are users going to love this?
7. What would I improve if I had one more day?

---

## 📝 Session Notes Template

**Use this template after each work session:**

```markdown
### Session [N] - [Date]
**Milestone:** [6.1 / 6.2 / 6.3.X]
**Time Spent:** [Hours]

**Completed:**
- [ ] Task 1
- [ ] Task 2

**In Progress:**
- [ ] Task 3 (50% done)

**Blockers:**
- [Issue description] - [Resolution plan]

**Decisions Made:**
- [Decision 1] - [Rationale]

**Next Session:**
- Start: [Task name]
- Goal: [Milestone completion / partial completion]

**Rubric Self-Score:**
- Code Quality: [%]
- User Experience: [%]
- API Integration: [%]
- Visual Design: [%]
- Testing: [%]
- Performance: [%]
- Documentation: [%]
**Overall:** [Average %]

**Reflection:**
[What went well, what to improve, lessons learned]
```

---

## 🎯 Final Deliverables Checklist

**Upon Phase 6 Completion:**

### Code Deliverables
- [ ] 5 reusable components (6.1)
- [ ] 1 demo page for components
- [ ] 7 modernized UI pages (6.2-6.3)
- [ ] Updated CSS with component styles
- [ ] Updated JavaScript with v3 API calls

### Testing Deliverables
- [ ] Component unit tests (Jest)
- [ ] Page integration tests (Playwright/Selenium)
- [ ] E2E workflow tests
- [ ] Test coverage report (>70%)
- [ ] Accessibility audit report

### Documentation Deliverables
- [ ] Component API reference
- [ ] Style guide
- [ ] API integration guide
- [ ] Testing guide
- [ ] Deployment guide
- [ ] User-facing changelog

### Deployment Deliverables
- [ ] Staging deployment successful
- [ ] Production deployment plan
- [ ] Rollback procedure documented
- [ ] Backup of v2 UI created
- [ ] Smoke test checklist

### Metrics Deliverables
- [ ] Performance benchmark results
- [ ] Accessibility score (WAVE/axe)
- [ ] Test coverage report
- [ ] User testing feedback summary
- [ ] Bug tracker snapshot (0 critical bugs)

---

## 🚀 Getting Started

**For AI Agent Implementing This Plan:**

1. **Read thoroughly:**
   - This document (ENMS-v3-frontend.md)
   - ENMS-v3.md (backend context)
   - ENMS-API-DOCUMENTATION-FOR-OVOS.md (API reference)

2. **Execute self-reflection:**
   - Create your rubric (5-7 categories)
   - Analyze Milestone 6.1 against rubric
   - Iterate until confident (90%+ all categories)

3. **Start Milestone 6.1:**
   - Create component files
   - Write unit tests
   - Build demo page
   - Test on mobile
   - Score against rubric
   - Refactor if needed

4. **Document progress:**
   - Use session notes template
   - Update this plan (mark tasks complete)
   - Commit frequently
   - Push to GitHub

5. **Move to next milestone:**
   - Only when current scores 90%+
   - Repeat process for 6.2, 6.3

6. **Final validation:**
   - Run all tests
   - Deploy to staging
   - Smoke test
   - Get approval
   - Deploy to production

---

**Document Status:** ✅ Ready for Implementation  
**Last Updated:** November 10, 2025  
**Next Review:** After Milestone 6.1 completion  
**Owner:** AI Agent + Human Oversight
