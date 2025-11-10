# EnMS v3 Frontend - Component Architecture Specification

**Document:** Component Architecture & Design Patterns  
**Version:** 1.0  
**Date:** November 10, 2025  
**Status:** ✅ APPROVED (Milestone 6.0 Complete)  
**Author:** EnMS Frontend Team  
**Purpose:** Define architectural patterns for v3 frontend modernization before implementation

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Component Communication (Task 6.0.1)](#1-component-communication-task-601)
3. [State Persistence (Task 6.0.2)](#2-state-persistence-task-602)
4. [Component Lifecycle (Task 6.0.3)](#3-component-lifecycle-task-603)
5. [API Client Extensions (Task 6.0.4)](#4-api-client-extensions-task-604)
6. [Error Recovery Playbook (Task 6.0.5)](#5-error-recovery-playbook-task-605)
7. [Multi-Energy UX Flows (Task 6.0.6)](#6-multi-energy-ux-flows-task-606)
8. [Progressive Loading (Task 6.0.7)](#7-progressive-loading-task-607)
9. [Data Flow Diagrams](#8-data-flow-diagrams)
10. [Implementation Checklist](#9-implementation-checklist)

---

## Overview

### Architecture Philosophy

EnMS v3 frontend follows these principles:

- **No Frameworks:** Vanilla JavaScript (ES6+) for consistency with v2
- **Component-Based:** Reusable, self-contained UI components
- **Event-Driven:** CustomEvent system for loose coupling
- **Progressive Enhancement:** Add v3 features without breaking v2
- **Mobile-First:** Responsive design from ground up
- **Accessibility:** WCAG 2.1 Level AA compliance

### Technology Stack

- **Language:** JavaScript ES6+ (no transpilation)
- **Charts:** Chart.js 3.x
- **Styling:** Custom CSS with CSS variables
- **State:** localStorage for persistence
- **Communication:** CustomEvent API
- **HTTP:** Fetch API with async/await

---

## 1. Component Communication (Task 6.0.1)

### Event Naming Convention

**Pattern:** `namespace:action`

**Namespaces:**
- `seu:` - SEU selector events
- `energy:` - Energy source filter events
- `chart:` - Chart container events
- `loading:` - Loading state events
- `error:` - Error message events
- `modal:` - Modal dialog events

**Examples:**
```javascript
// SEU selected
seu:selected → { seuName, seuId, energySources, machineType }

// Energy source filter changed
energy:filtered → { sources: ['electricity', 'natural_gas'], seuName }

// Chart export requested
chart:export → { format: 'csv', chartId, data }

// Loading state changed
loading:start → { component: 'dashboard-widget', message: 'Loading opportunities...' }
loading:complete → { component: 'dashboard-widget', duration: 2340 }

// Error occurred
error:show → { type: 'timeout', message, retryable: true, retryFn }
error:dismiss → { errorId }

// Modal actions
modal:open → { modalId, title, content }
modal:close → { modalId }
```

### Event System Implementation

**Base Component Pattern:**

```javascript
/**
 * BaseComponent - Foundation for all UI components
 * Extends EventTarget for built-in event handling
 */
class BaseComponent extends EventTarget {
  constructor(containerId, options = {}) {
    super();
    this.containerId = containerId;
    this.container = document.getElementById(containerId);
    this.options = options;
    this.state = {};
    
    if (!this.container) {
      throw new Error(`Container #${containerId} not found`);
    }
  }

  /**
   * Emit custom event with namespaced name
   * @param {string} eventName - Event name (e.g., 'seu:selected')
   * @param {object} detail - Event payload
   */
  emit(eventName, detail = {}) {
    const event = new CustomEvent(eventName, {
      detail: {
        ...detail,
        timestamp: new Date().toISOString(),
        component: this.constructor.name
      },
      bubbles: true,
      cancelable: true
    });
    
    this.dispatchEvent(event);
    
    // Also dispatch on container for DOM event delegation
    this.container.dispatchEvent(event);
    
    console.debug(`[Event] ${eventName}`, detail);
  }

  /**
   * Subscribe to events (wrapper around addEventListener)
   * @param {string} eventName - Event name
   * @param {function} handler - Event handler
   */
  on(eventName, handler) {
    this.addEventListener(eventName, handler);
  }

  /**
   * Unsubscribe from events
   * @param {string} eventName - Event name
   * @param {function} handler - Event handler
   */
  off(eventName, handler) {
    this.removeEventListener(eventName, handler);
  }

  /**
   * Update component state and re-render
   * @param {object} newState - State updates
   */
  setState(newState) {
    this.state = { ...this.state, ...newState };
    this.render();
  }

  /**
   * Render component (override in subclass)
   */
  render() {
    throw new Error('render() must be implemented by subclass');
  }

  /**
   * Clean up resources
   */
  destroy() {
    // Remove all event listeners
    this.container.innerHTML = '';
    console.debug(`[Component] ${this.constructor.name} destroyed`);
  }
}
```

**Example: SEUSelector Component:**

```javascript
/**
 * SEUSelector - Dropdown for selecting Significant Energy Uses
 * 
 * Events emitted:
 *   - seu:selected { seuName, seuId, energySources, machineType }
 *   - seu:loading { isLoading }
 *   - seu:error { message }
 * 
 * Usage:
 *   const selector = new SEUSelector('seu-selector-container');
 *   selector.on('seu:selected', (e) => {
 *     console.log('Selected:', e.detail.seuName);
 *   });
 */
class SEUSelector extends BaseComponent {
  constructor(containerId, options = {}) {
    super(containerId, options);
    this.seus = [];
    this.selectedSEU = null;
    this.init();
  }

  async init() {
    this.emit('loading:start', { component: 'SEUSelector' });
    
    try {
      // Fetch SEUs from API (cached)
      this.seus = await apiClient.getSEUs();
      this.render();
      
      // Restore previous selection from localStorage
      const savedSelection = StateManager.get('seu_selection');
      if (savedSelection) {
        this.selectSEU(savedSelection.seuName);
      }
      
      this.emit('loading:complete', { component: 'SEUSelector' });
    } catch (error) {
      this.emit('error:show', {
        type: 'network',
        message: 'Failed to load SEUs',
        retryable: true,
        retryFn: () => this.init()
      });
    }
  }

  render() {
    this.container.innerHTML = `
      <div class="seu-selector">
        <label for="seu-dropdown">Select SEU:</label>
        <select id="seu-dropdown" class="form-control">
          <option value="">-- Select a Significant Energy Use --</option>
          ${this.seus.map(seu => `
            <option value="${seu.seu_name}" 
                    data-id="${seu.id}"
                    data-energy-sources='${JSON.stringify(seu.energy_sources)}'>
              ${seu.seu_name} (${seu.machine_type})
            </option>
          `).join('')}
        </select>
        <small class="text-muted">${this.seus.length} SEUs available</small>
      </div>
    `;

    // Attach event listener
    const dropdown = this.container.querySelector('#seu-dropdown');
    dropdown.addEventListener('change', (e) => this.handleSelection(e));
  }

  handleSelection(event) {
    const selectedOption = event.target.selectedOptions[0];
    if (!selectedOption.value) return;

    const seuName = selectedOption.value;
    const seuId = selectedOption.dataset.id;
    const energySources = JSON.parse(selectedOption.dataset.energySources);
    
    this.selectedSEU = { seuName, seuId, energySources };

    // Persist selection
    StateManager.set('seu_selection', this.selectedSEU, 3600); // 1h TTL

    // Emit event
    this.emit('seu:selected', {
      seuName,
      seuId,
      energySources,
      machineType: this.seus.find(s => s.seu_name === seuName)?.machine_type
    });
  }

  selectSEU(seuName) {
    const dropdown = this.container.querySelector('#seu-dropdown');
    if (dropdown) {
      dropdown.value = seuName;
      dropdown.dispatchEvent(new Event('change'));
    }
  }
}
```

**Example: Energy Source Filter Component:**

```javascript
/**
 * EnergySourceFilter - Multi-select filter for energy sources
 * 
 * Events emitted:
 *   - energy:filtered { sources: ['electricity'], seuName }
 * 
 * States:
 *   - Single-energy SEU: Auto-select only source, disable others
 *   - Multi-energy SEU: Enable relevant sources (radio buttons)
 *   - Multi-SEU mode: Enable all sources (checkboxes)
 */
class EnergySourceFilter extends BaseComponent {
  constructor(containerId, options = {}) {
    super(containerId, options);
    this.availableSources = [];
    this.selectedSources = [];
    this.mode = options.mode || 'single'; // 'single' or 'multi'
    this.init();
  }

  init() {
    this.render();

    // Listen for SEU selection
    document.addEventListener('seu:selected', (e) => {
      this.handleSEUSelected(e.detail);
    });
  }

  handleSEUSelected({ seuName, energySources }) {
    this.availableSources = energySources || [];
    this.seuName = seuName;

    // Auto-select if single energy source
    if (energySources.length === 1) {
      this.selectedSources = [energySources[0]];
      this.mode = 'single';
    } else {
      this.selectedSources = [];
      this.mode = 'multi';
    }

    this.render();
    this.emitChange();
  }

  render() {
    const allSources = [
      { value: 'electricity', label: 'Electricity', color: '#3b82f6' },
      { value: 'natural_gas', label: 'Natural Gas', color: '#f59e0b' },
      { value: 'steam', label: 'Steam', color: '#ef4444' },
      { value: 'compressed_air', label: 'Compressed Air', color: '#10b981' }
    ];

    const isSingleEnergy = this.availableSources.length === 1;
    const inputType = this.mode === 'multi' && !isSingleEnergy ? 'checkbox' : 'radio';

    this.container.innerHTML = `
      <div class="energy-filter">
        <label>Energy Source:</label>
        <div class="energy-options">
          ${allSources.map(source => {
            const isAvailable = this.availableSources.includes(source.value);
            const isSelected = this.selectedSources.includes(source.value);
            const isDisabled = !isAvailable || isSingleEnergy;

            return `
              <div class="energy-option ${isDisabled ? 'disabled' : ''}" 
                   style="border-color: ${isAvailable ? source.color : '#ccc'}">
                <input 
                  type="${inputType}" 
                  id="energy-${source.value}" 
                  name="energy-source"
                  value="${source.value}"
                  ${isSelected ? 'checked' : ''}
                  ${isDisabled ? 'disabled' : ''}
                  onchange="window.energyFilter.handleChange(event)">
                <label for="energy-${source.value}">
                  <span class="badge" style="background: ${source.color}"></span>
                  ${source.label}
                  ${!isAvailable ? '<small>(unavailable)</small>' : ''}
                </label>
              </div>
            `;
          }).join('')}
        </div>
        ${isSingleEnergy ? '<small class="text-muted">Single energy source (auto-selected)</small>' : ''}
      </div>
    `;

    // Store reference globally for inline handlers (simplicity)
    window.energyFilter = this;
  }

  handleChange(event) {
    const value = event.target.value;

    if (this.mode === 'multi') {
      // Checkbox mode
      if (event.target.checked) {
        this.selectedSources.push(value);
      } else {
        this.selectedSources = this.selectedSources.filter(s => s !== value);
      }
    } else {
      // Radio mode
      this.selectedSources = [value];
    }

    this.emitChange();
  }

  emitChange() {
    this.emit('energy:filtered', {
      sources: this.selectedSources,
      seuName: this.seuName
    });

    // Persist selection
    StateManager.set('energy_filter', {
      sources: this.selectedSources,
      seuName: this.seuName
    }, 3600);
  }
}
```

---

## 2. State Persistence (Task 6.0.2)

### localStorage Schema

**Keys:** `enms_<feature>_<version>`

**Format:**
```javascript
{
  data: {...},          // Actual data
  timestamp: 1699564800, // Unix timestamp
  ttl: 3600,            // Time-to-live in seconds
  version: 1            // Schema version
}
```

**Storage Keys:**

| Key | Description | TTL | Example Value |
|-----|-------------|-----|---------------|
| `enms_seu_selection_v1` | Selected SEU | 1 hour | `{ seuName: "Compressor-1", seuId: "...", energySources: [...] }` |
| `enms_energy_filter_v1` | Energy source filter | 1 hour | `{ sources: ["electricity"], seuName: "Compressor-1" }` |
| `enms_date_range_v1` | Date range picker | 24 hours | `{ start: "2025-11-10T00:00:00Z", end: "2025-11-10T23:59:59Z" }` |
| `enms_chart_settings_v1` | Chart preferences | 7 days | `{ type: "line", interval: "1hour", showGrid: true }` |
| `enms_api_cache_seus_v1` | Cached SEU list | 5 minutes | `[ { seu_name: "...", ... } ]` |
| `enms_api_cache_metrics_v1` | Cached metrics | 1 minute | `{ energy_kwh: 123, power_kw: 45 }` |

### StateManager Utility

```javascript
/**
 * StateManager - Centralized state persistence with TTL
 */
class StateManager {
  /**
   * Get item from localStorage with TTL validation
   * @param {string} key - Storage key (without enms_ prefix)
   * @param {number} version - Schema version (default: 1)
   * @returns {*} Data or null if expired/not found
   */
  static get(key, version = 1) {
    const storageKey = `enms_${key}_v${version}`;
    const item = localStorage.getItem(storageKey);

    if (!item) return null;

    try {
      const parsed = JSON.parse(item);
      const now = Math.floor(Date.now() / 1000);

      // Check if expired
      if (parsed.timestamp + parsed.ttl < now) {
        console.debug(`[StateManager] Cache expired: ${key}`);
        this.remove(key, version);
        return null;
      }

      console.debug(`[StateManager] Cache hit: ${key}`, parsed.data);
      return parsed.data;
    } catch (error) {
      console.error(`[StateManager] Parse error for ${key}:`, error);
      this.remove(key, version);
      return null;
    }
  }

  /**
   * Set item in localStorage with TTL
   * @param {string} key - Storage key
   * @param {*} data - Data to store
   * @param {number} ttl - Time-to-live in seconds
   * @param {number} version - Schema version (default: 1)
   */
  static set(key, data, ttl = 3600, version = 1) {
    const storageKey = `enms_${key}_v${version}`;
    const item = {
      data,
      timestamp: Math.floor(Date.now() / 1000),
      ttl,
      version
    };

    try {
      localStorage.setItem(storageKey, JSON.stringify(item));
      console.debug(`[StateManager] Cache set: ${key} (TTL: ${ttl}s)`);
    } catch (error) {
      console.error(`[StateManager] Storage error for ${key}:`, error);
      // Handle quota exceeded
      if (error.name === 'QuotaExceededError') {
        this.clearExpired();
        localStorage.setItem(storageKey, JSON.stringify(item));
      }
    }
  }

  /**
   * Remove item from localStorage
   * @param {string} key - Storage key
   * @param {number} version - Schema version (default: 1)
   */
  static remove(key, version = 1) {
    const storageKey = `enms_${key}_v${version}`;
    localStorage.removeItem(storageKey);
    console.debug(`[StateManager] Cache removed: ${key}`);
  }

  /**
   * Clear all expired items
   */
  static clearExpired() {
    const now = Math.floor(Date.now() / 1000);
    let clearedCount = 0;

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (!key.startsWith('enms_')) continue;

      try {
        const item = JSON.parse(localStorage.getItem(key));
        if (item.timestamp + item.ttl < now) {
          localStorage.removeItem(key);
          clearedCount++;
        }
      } catch (error) {
        // Invalid item, remove it
        localStorage.removeItem(key);
        clearedCount++;
      }
    }

    console.debug(`[StateManager] Cleared ${clearedCount} expired items`);
  }

  /**
   * Clear all EnMS storage
   */
  static clearAll() {
    const keys = Object.keys(localStorage).filter(k => k.startsWith('enms_'));
    keys.forEach(k => localStorage.removeItem(k));
    console.debug(`[StateManager] Cleared all storage (${keys.length} items)`);
  }

  /**
   * Invalidate cache by version bump
   * @param {string} key - Storage key
   */
  static invalidate(key) {
    // Remove all versions
    for (let v = 1; v <= 10; v++) {
      this.remove(key, v);
    }
    console.debug(`[StateManager] Invalidated: ${key}`);
  }
}

// Auto-clear expired items on page load
window.addEventListener('load', () => {
  StateManager.clearExpired();
});
```

---

## 3. Component Lifecycle (Task 6.0.3)

### Lifecycle Methods

All components follow this lifecycle:

1. **Constructor** - Initialize properties, validate container
2. **init()** - Async setup (fetch data, restore state)
3. **render()** - Build DOM, attach event listeners
4. **update()** - Re-render on state change
5. **destroy()** - Clean up resources, remove listeners

### Lifecycle Diagram

```
┌─────────────┐
│ Constructor │ → Validate container, set defaults
└──────┬──────┘
       │
       v
┌─────────────┐
│   init()    │ → Fetch data, restore localStorage
└──────┬──────┘
       │
       v
┌─────────────┐
│  render()   │ → Build DOM, attach events
└──────┬──────┘
       │
       v
┌─────────────┐
│   Running   │ ←──┐
└──────┬──────┘    │
       │           │
       v           │
┌─────────────┐    │
│  update()   │ ───┘  (on state change)
└──────┬──────┘
       │
       v
┌─────────────┐
│  destroy()  │ → Remove listeners, clear DOM
└─────────────┘
```

### Memory Management

**Rules:**
1. **Always remove event listeners** in `destroy()`
2. **Clear intervals/timeouts** before destroying
3. **Nullify object references** to prevent memory leaks
4. **Use WeakMap** for private data when possible

**Example:**

```javascript
class ChartContainer extends BaseComponent {
  constructor(containerId, options) {
    super(containerId, options);
    this.chart = null;
    this.resizeHandler = null;
    this.updateInterval = null;
  }

  async init() {
    // ... fetch data ...
    this.render();

    // Auto-refresh every 30s
    this.updateInterval = setInterval(() => this.update(), 30000);

    // Responsive resize
    this.resizeHandler = () => this.handleResize();
    window.addEventListener('resize', this.resizeHandler);
  }

  render() {
    // ... create chart ...
    this.chart = new Chart(ctx, config);
  }

  update() {
    // ... fetch new data ...
    this.chart.data = newData;
    this.chart.update();
  }

  destroy() {
    // 1. Clear intervals
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }

    // 2. Remove event listeners
    if (this.resizeHandler) {
      window.removeEventListener('resize', this.resizeHandler);
      this.resizeHandler = null;
    }

    // 3. Destroy chart instance
    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }

    // 4. Call parent destroy
    super.destroy();
  }

  handleResize() {
    if (this.chart) {
      this.chart.resize();
    }
  }
}
```

---

## 4. API Client Extensions (Task 6.0.4)

### Extended API Client

**File:** `analytics/ui/static/js/api-client.js`

```javascript
/**
 * APIClient - Extended for v3 endpoints
 * Features: Caching, retry logic, request queue
 */
class APIClient {
  constructor(baseURL = '/api/v1') {
    this.baseURL = baseURL;
    this.cache = new Map();
    this.requestQueue = new Map();
  }

  /**
   * Get all SEUs (cached for 5 minutes)
   * @returns {Promise<Array>} SEU list
   */
  async getSEUs() {
    const cacheKey = 'seus_list';
    const cached = this._getCached(cacheKey, 300); // 5min TTL
    if (cached) return cached;

    const data = await this._fetch('/seus');
    this._setCached(cacheKey, data, 300);
    return data;
  }

  /**
   * Train baseline model for SEU
   * @param {string} seuName - SEU name
   * @param {string} energySource - Energy source type
   * @param {number} days - Training window (default: 30)
   * @returns {Promise<Object>} Training result
   */
  async trainBaseline(seuName, energySource, days = 30) {
    return this._fetch('/baseline/train-seu', {
      method: 'POST',
      body: JSON.stringify({ seu_name: seuName, energy_source: energySource, days })
    });
  }

  /**
   * Get performance opportunities (slow endpoint - 35s)
   * @param {number} timeout - Custom timeout (default: 60s)
   * @returns {Promise<Object>} Opportunities list
   */
  async getOpportunities(timeout = 60000) {
    const cacheKey = 'opportunities';
    const cached = this._getCached(cacheKey, 300); // 5min cache
    if (cached) return cached;

    const data = await this._fetch('/performance/opportunities', { timeout });
    this._setCached(cacheKey, data, 300);
    return data;
  }

  /**
   * Get factory summary (cached 1 minute)
   * @returns {Promise<Object>} Factory stats
   */
  async getFactorySummary() {
    const cacheKey = 'factory_summary';
    const cached = this._getCached(cacheKey, 60); // 1min TTL
    if (cached) return cached;

    const data = await this._fetch('/factory/summary');
    this._setCached(cacheKey, data, 60);
    return data;
  }

  /**
   * Get baseline models with explanations
   * @param {string} seuName - Filter by SEU
   * @param {string} energySource - Filter by energy source
   * @param {boolean} includeExplanation - Include ML explanations
   * @returns {Promise<Object>} Models list
   */
  async getBaselineModels(seuName = null, energySource = null, includeExplanation = false) {
    const params = new URLSearchParams();
    if (seuName) params.append('seu_name', seuName);
    if (energySource) params.append('energy_source', energySource);
    if (includeExplanation) params.append('include_explanation', 'true');

    const url = `/baseline/models${params.toString() ? '?' + params : ''}`;
    return this._fetch(url);
  }

  /**
   * Get energy time-series data
   * @param {string} machineId - Machine UUID
   * @param {string} startTime - ISO timestamp
   * @param {string} endTime - ISO timestamp
   * @param {string} interval - Time bucket (1min, 15min, 1hour, 1day)
   * @returns {Promise<Object>} Time-series data
   */
  async getEnergyTimeSeries(machineId, startTime, endTime, interval = '1hour') {
    const params = new URLSearchParams({
      machine_id: machineId,
      start_time: startTime,
      end_time: endTime,
      interval
    });

    return this._fetch(`/timeseries/energy?${params}`);
  }

  /**
   * Internal fetch with retry logic and caching
   * @private
   */
  async _fetch(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      method: options.method || 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    // Retry configuration
    const maxRetries = options.retries || 3;
    const timeout = options.timeout || 10000; // 10s default
    let lastError;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        console.debug(`[API] ${config.method} ${endpoint} (attempt ${attempt}/${maxRetries})`);

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        const response = await fetch(url, {
          ...config,
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new APIError(
            `HTTP ${response.status}`,
            response.status,
            await response.json().catch(() => ({}))
          );
        }

        const data = await response.json();
        console.debug(`[API] Success: ${endpoint}`, data);
        return data;

      } catch (error) {
        lastError = error;

        // Don't retry on client errors (400-499)
        if (error.status >= 400 && error.status < 500) {
          throw error;
        }

        // Don't retry on abort (user cancelled)
        if (error.name === 'AbortError') {
          throw new APIError('Request timeout', 408, { timeout });
        }

        // Exponential backoff
        if (attempt < maxRetries) {
          const delay = Math.pow(2, attempt) * 1000; // 2s, 4s, 8s
          console.warn(`[API] Retry ${attempt}/${maxRetries} after ${delay}ms:`, error.message);
          await this._sleep(delay);
        }
      }
    }

    // All retries exhausted
    throw lastError;
  }

  /**
   * Get cached value
   * @private
   */
  _getCached(key, ttlSeconds) {
    const cached = this.cache.get(key);
    if (!cached) return null;

    const age = (Date.now() - cached.timestamp) / 1000;
    if (age > ttlSeconds) {
      this.cache.delete(key);
      return null;
    }

    console.debug(`[API Cache] Hit: ${key} (age: ${age.toFixed(1)}s)`);
    return cached.data;
  }

  /**
   * Set cached value
   * @private
   */
  _setCached(key, data, ttlSeconds) {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl: ttlSeconds
    });
    console.debug(`[API Cache] Set: ${key} (TTL: ${ttlSeconds}s)`);
  }

  /**
   * Clear cache
   */
  clearCache() {
    this.cache.clear();
    console.debug('[API Cache] Cleared');
  }

  /**
   * Sleep utility
   * @private
   */
  _sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

/**
 * APIError - Standardized error format
 */
class APIError extends Error {
  constructor(message, status, details = {}) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.details = details;
    this.retryable = this._isRetryable(status);
  }

  _isRetryable(status) {
    // Retryable: 5xx errors, network errors, timeouts
    // Not retryable: 4xx client errors
    if (!status) return true; // Network error
    if (status === 408 || status === 429) return true; // Timeout, rate limit
    if (status >= 500) return true; // Server error
    return false; // 4xx client error
  }

  toJSON() {
    return {
      code: this.status,
      message: this.message,
      retryable: this.retryable,
      details: this.details
    };
  }
}

// Global instance
const apiClient = new APIClient();
```

---

## 5. Error Recovery Playbook (Task 6.0.5)

### Error Types & Recovery Strategies

#### 1. Timeout Errors (>30s)

**Scenario:** `/performance/opportunities` takes 35+ seconds

**Strategy:**
- Show "Still working..." message after 3 seconds
- Show cancel button
- Continue request in background
- On completion: Hide message, show result
- On cancel: Abort request, show retry button

**UI Pattern:**

```javascript
async function loadOpportunities() {
  const container = document.getElementById('opportunities-widget');
  const abortController = new AbortController();

  // Show loading after 3s
  const slowTimeout = setTimeout(() => {
    container.innerHTML = `
      <div class="slow-loading">
        <div class="spinner"></div>
        <p>This is taking longer than usual. Still working...</p>
        <button onclick="abortRequest()">Cancel</button>
      </div>
    `;
  }, 3000);

  try {
    const data = await apiClient.getOpportunities(60000); // 60s timeout
    clearTimeout(slowTimeout);
    renderOpportunities(data);
  } catch (error) {
    clearTimeout(slowTimeout);

    if (error.name === 'AbortError') {
      // User cancelled
      container.innerHTML = `
        <div class="error-message warning">
          <p>Request cancelled</p>
          <button onclick="loadOpportunities()">Retry</button>
        </div>
      `;
    } else {
      // Timeout
      container.innerHTML = `
        <div class="error-message error">
          <p>Request timed out (${error.message})</p>
          <button onclick="loadOpportunities()">Retry</button>
        </div>
      `;
    }
  }

  function abortRequest() {
    abortController.abort();
  }
}
```

#### 2. Network Errors (fetch failed)

**Scenario:** User loses internet connection

**Strategy:**
- Auto-retry 3 times with exponential backoff (2s, 4s, 8s)
- Show retry attempt number
- Final failure: Show manual retry button
- Check `navigator.onLine` before retry

**UI Pattern:**

```javascript
async function fetchWithRetry(fetchFn, retries = 3) {
  let lastError;

  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      // Check network status
      if (!navigator.onLine) {
        throw new Error('No internet connection');
      }

      return await fetchFn();
    } catch (error) {
      lastError = error;

      if (attempt < retries) {
        const delay = Math.pow(2, attempt) * 1000;
        showRetryMessage(attempt, retries, delay);
        await sleep(delay);
      }
    }
  }

  // All retries failed
  showFinalError(lastError);
  throw lastError;
}

function showRetryMessage(attempt, maxRetries, delay) {
  const container = document.getElementById('error-container');
  container.innerHTML = `
    <div class="error-message info">
      <i class="icon-wifi-off"></i>
      <p>Connection lost. Retrying (${attempt}/${maxRetries})...</p>
      <small>Next attempt in ${(delay / 1000).toFixed(0)}s</small>
    </div>
  `;
}

function showFinalError(error) {
  const container = document.getElementById('error-container');
  container.innerHTML = `
    <div class="error-message error">
      <i class="icon-alert"></i>
      <p>Connection failed: ${error.message}</p>
      <button onclick="location.reload()">Retry</button>
    </div>
  `;
}
```

#### 3. 404 Errors (Resource Not Found)

**Scenario:** User enters invalid SEU name

**Strategy:**
- Show friendly error message
- Display available options
- Pre-populate SEU selector
- No auto-retry (requires user action)

**UI Pattern:**

```javascript
async function loadSEUData(seuName) {
  try {
    const data = await apiClient.getBaselineModels(seuName);
    renderData(data);
  } catch (error) {
    if (error.status === 404) {
      // Get available SEUs
      const seus = await apiClient.getSEUs();
      
      showError404({
        resource: 'SEU',
        name: seuName,
        available: seus.map(s => s.seu_name),
        suggestion: 'Please select from available SEUs:'
      });

      // Auto-populate selector
      populateSEUSelector(seus);
    } else {
      throw error;
    }
  }
}

function showError404({ resource, name, available, suggestion }) {
  const container = document.getElementById('error-container');
  container.innerHTML = `
    <div class="error-message warning">
      <i class="icon-search"></i>
      <h4>${resource} not found: "${name}"</h4>
      <p>${suggestion}</p>
      <ul class="available-options">
        ${available.map(opt => `
          <li><a href="#" onclick="selectSEU('${opt}')">${opt}</a></li>
        `).join('')}
      </ul>
    </div>
  `;
}
```

#### 4. 500 Errors (Server Error)

**Scenario:** Backend crashes or database issue

**Strategy:**
- Show user-friendly error message
- Log full error to console for debugging
- Show manual retry button (no auto-retry)
- Provide support contact if persistent

**UI Pattern:**

```javascript
async function loadData() {
  try {
    const data = await apiClient.getFactorySummary();
    renderData(data);
  } catch (error) {
    if (error.status >= 500) {
      showError500(error);
    } else {
      throw error;
    }
  }
}

function showError500(error) {
  const container = document.getElementById('error-container');
  
  // Log detailed error for debugging
  console.error('[Server Error]', {
    status: error.status,
    message: error.message,
    details: error.details,
    timestamp: new Date().toISOString()
  });

  container.innerHTML = `
    <div class="error-message error">
      <i class="icon-server"></i>
      <h4>System Error</h4>
      <p>We're experiencing technical difficulties. Please try again.</p>
      <div class="error-actions">
        <button onclick="loadData()" class="btn-primary">Retry</button>
        <button onclick="showErrorDetails()" class="btn-secondary">Details</button>
      </div>
      <small class="text-muted">
        If problem persists, contact support with error code: 
        <code>${error.status}-${Date.now()}</code>
      </small>
    </div>
  `;
}

function showErrorDetails() {
  // Show technical details in expandable section
  const detailsDiv = document.createElement('div');
  detailsDiv.className = 'error-details';
  detailsDiv.innerHTML = `
    <pre>${JSON.stringify(error.details, null, 2)}</pre>
  `;
  document.getElementById('error-container').appendChild(detailsDiv);
}
```

---

## 6. Multi-Energy UX Flows (Task 6.0.6)

### Scenario 1: Single-Energy Machine (Compressor-1)

**Data:**
- Machine: Compressor-1
- Energy sources: `["electricity"]` (1 source)

**UX Flow:**

1. User selects "Compressor-1" from SEU selector
2. Energy source filter auto-populates:
   - ✅ Electricity: **Selected, disabled** (grayed out)
   - ❌ Natural Gas: Disabled
   - ❌ Steam: Disabled
   - ❌ Compressed Air: Disabled
3. Training form **enabled immediately** (no action needed)
4. Help text: "Single energy source (auto-selected)"

**Code Example:**

```javascript
// In EnergySourceFilter component
handleSEUSelected({ seuName, energySources }) {
  if (energySources.length === 1) {
    // Single-energy mode
    this.mode = 'single';
    this.selectedSources = [energySources[0]];
    this.availableSources = [energySources[0]];
    
    // Auto-enable form
    document.getElementById('training-form').disabled = false;
    
    // Show help text
    this.showHelpText('Single energy source (auto-selected)');
  }
  
  this.render();
}
```

**Visual Design:**

```
┌─────────────────────────────────────┐
│ SEU: [Compressor-1 ▼]              │
├─────────────────────────────────────┤
│ Energy Source:                      │
│ [✓] Electricity (auto-selected)     │  ← Blue, checked, disabled
│ [ ] Natural Gas (unavailable)       │  ← Gray, disabled
│ [ ] Steam (unavailable)             │  ← Gray, disabled
│ [ ] Compressed Air (unavailable)    │  ← Gray, disabled
│                                     │
│ ℹ️ Single energy source (auto)      │
└─────────────────────────────────────┘
```

---

### Scenario 2: Multi-Energy Machine (Boiler-1)

**Data:**
- Machine: Boiler-1
- Energy sources: `["electricity", "natural_gas", "steam"]` (3 sources)

**UX Flow:**

1. User selects "Boiler-1" from SEU selector
2. Energy source filter shows **radio buttons** (select ONE):
   - ⭕ Electricity: **Enabled, highlighted**
   - ⭕ Natural Gas: **Enabled, highlighted**
   - ⭕ Steam: **Enabled, highlighted**
   - ❌ Compressed Air: Disabled
3. User **MUST** select one energy source (radio button)
4. Training form **enabled after selection**
5. Help text: "Select energy source to analyze"

**Code Example:**

```javascript
handleSEUSelected({ seuName, energySources }) {
  if (energySources.length > 1) {
    // Multi-energy mode (radio buttons)
    this.mode = 'radio';
    this.selectedSources = []; // None selected initially
    this.availableSources = energySources;
    
    // Disable form until energy source selected
    document.getElementById('training-form').disabled = true;
    
    // Show help text
    this.showHelpText('Select one energy source to analyze');
  }
  
  this.render();
}

handleEnergySelected(energySource) {
  this.selectedSources = [energySource];
  
  // Enable form
  document.getElementById('training-form').disabled = false;
  
  this.emit('energy:filtered', {
    sources: [energySource],
    seuName: this.seuName
  });
}
```

**Visual Design:**

```
┌─────────────────────────────────────┐
│ SEU: [Boiler-1 ▼]                  │
├─────────────────────────────────────┤
│ Energy Source:                      │
│ (•) Electricity                     │  ← Blue border, enabled
│ ( ) Natural Gas                     │  ← Orange border, enabled
│ ( ) Steam                           │  ← Red border, enabled
│ [ ] Compressed Air (unavailable)    │  ← Gray, disabled
│                                     │
│ ℹ️ Select one energy source         │
└─────────────────────────────────────┘
```

---

### Scenario 3: Multi-SEU Comparison (All SEUs)

**Data:**
- Mode: Comparison page
- SEUs: Multiple selection allowed
- Energy sources: All 4 sources

**UX Flow:**

1. User selects **multiple SEUs** (checkboxes)
2. Energy source filter shows **checkboxes** (select many):
   - ☑️ Electricity: **Enabled**
   - ☑️ Natural Gas: **Enabled**
   - ☑️ Steam: **Enabled**
   - ☑️ Compressed Air: **Enabled**
3. User can select **multiple energy sources**
4. Chart shows **combined data** with color-coded legends
5. Help text: "Select SEUs and energy sources to compare"

**Code Example:**

```javascript
// In Comparison page
handleMultiSEUMode() {
  // Enable multi-select on SEU selector
  this.seuSelector.setMode('multi');
  
  // Enable checkboxes on energy filter
  this.energyFilter.setMode('multi');
  
  // Listen for selections
  document.addEventListener('seu:selected', (e) => {
    this.selectedSEUs = e.detail.seuNames; // Array
    this.updateChart();
  });
  
  document.addEventListener('energy:filtered', (e) => {
    this.selectedEnergies = e.detail.sources; // Array
    this.updateChart();
  });
}

updateChart() {
  // Fetch data for each SEU + energy combination
  const datasets = [];
  
  for (const seu of this.selectedSEUs) {
    for (const energy of this.selectedEnergies) {
      const data = await apiClient.getEnergyTimeSeries(seu, energy);
      datasets.push({
        label: `${seu} - ${energy}`,
        data: data,
        borderColor: getEnergyColor(energy),
        backgroundColor: getEnergyColor(energy, 0.2)
      });
    }
  }
  
  this.chart.data.datasets = datasets;
  this.chart.update();
}
```

**Visual Design:**

```
┌─────────────────────────────────────┐
│ SEUs: [☑️ Compressor-1]             │
│       [☑️ Boiler-1]                 │
│       [☑️ HVAC-Main]                │
├─────────────────────────────────────┤
│ Energy Sources:                     │
│ [☑️] Electricity (3 SEUs)           │  ← Blue
│ [☑️] Natural Gas (1 SEU)            │  ← Orange
│ [☑️] Steam (1 SEU)                  │  ← Red
│ [ ] Compressed Air (0 SEUs)         │  ← Gray
│                                     │
│ ℹ️ 5 combinations selected           │
└─────────────────────────────────────┘
```

---

## 7. Progressive Loading (Task 6.0.7)

### Dashboard Widget Loading Pattern

**Problem:** Dashboard loads 3 endpoints:
- `/factory/summary` - 2s response
- `/seus` - 500ms response
- `/performance/opportunities` - **35s response** ⚠️

**Solution:** Load widgets independently, don't block each other

### LoadingOrchestrator Utility

```javascript
/**
 * LoadingOrchestrator - Manage multiple async widget loads
 */
class LoadingOrchestrator {
  constructor() {
    this.widgets = new Map();
  }

  /**
   * Register widget for loading
   * @param {string} widgetId - DOM container ID
   * @param {function} loadFn - Async function to load data
   * @param {object} options - Configuration
   */
  register(widgetId, loadFn, options = {}) {
    this.widgets.set(widgetId, {
      id: widgetId,
      loadFn,
      timeout: options.timeout || 10000,
      priority: options.priority || 'normal', // 'high', 'normal', 'low'
      showSkeletonAfter: options.showSkeletonAfter || 200,
      showSlowWarningAfter: options.showSlowWarningAfter || 3000,
      onSuccess: options.onSuccess || (() => {}),
      onError: options.onError || ((err) => this.showDefaultError(widgetId, err))
    });
  }

  /**
   * Load all widgets (parallel execution)
   */
  async loadAll() {
    const promises = Array.from(this.widgets.values()).map(widget => 
      this.loadWidget(widget)
    );

    await Promise.allSettled(promises);
  }

  /**
   * Load single widget
   * @private
   */
  async loadWidget(widget) {
    const container = document.getElementById(widget.id);
    if (!container) {
      console.error(`[LoadingOrchestrator] Container not found: ${widget.id}`);
      return;
    }

    const startTime = Date.now();
    let skeletonTimeout, slowWarningTimeout;

    try {
      // Show skeleton loader after delay
      skeletonTimeout = setTimeout(() => {
        this.showSkeleton(widget.id);
      }, widget.showSkeletonAfter);

      // Show slow warning after delay
      slowWarningTimeout = setTimeout(() => {
        this.showSlowWarning(widget.id);
      }, widget.showSlowWarningAfter);

      // Load data
      const data = await Promise.race([
        widget.loadFn(),
        this.timeout(widget.timeout)
      ]);

      // Clear timers
      clearTimeout(skeletonTimeout);
      clearTimeout(slowWarningTimeout);

      // Success
      const duration = Date.now() - startTime;
      console.debug(`[LoadingOrchestrator] ${widget.id} loaded in ${duration}ms`);
      
      widget.onSuccess(data, container);

    } catch (error) {
      clearTimeout(skeletonTimeout);
      clearTimeout(slowWarningTimeout);

      console.error(`[LoadingOrchestrator] ${widget.id} failed:`, error);
      widget.onError(error, container);
    }
  }

  /**
   * Show skeleton loader
   * @private
   */
  showSkeleton(widgetId) {
    const container = document.getElementById(widgetId);
    container.innerHTML = `
      <div class="skeleton-loader">
        <div class="skeleton-line"></div>
        <div class="skeleton-line"></div>
        <div class="skeleton-line short"></div>
      </div>
    `;
  }

  /**
   * Show slow loading warning
   * @private
   */
  showSlowWarning(widgetId) {
    const container = document.getElementById(widgetId);
    const skeleton = container.querySelector('.skeleton-loader');
    
    if (skeleton) {
      const warning = document.createElement('div');
      warning.className = 'slow-warning';
      warning.innerHTML = `
        <i class="icon-clock"></i>
        <small>This is taking longer than usual...</small>
      `;
      skeleton.appendChild(warning);
    }
  }

  /**
   * Show default error message
   * @private
   */
  showDefaultError(widgetId, error) {
    const container = document.getElementById(widgetId);
    container.innerHTML = `
      <div class="widget-error">
        <i class="icon-alert-circle"></i>
        <p>${error.message}</p>
        <button onclick="location.reload()">Retry</button>
      </div>
    `;
  }

  /**
   * Timeout helper
   * @private
   */
  timeout(ms) {
    return new Promise((_, reject) => 
      setTimeout(() => reject(new Error(`Timeout after ${ms}ms`)), ms)
    );
  }
}
```

### Dashboard Implementation Example

```javascript
// analytics/ui/static/js/dashboard.js

const orchestrator = new LoadingOrchestrator();

// Register widgets with different priorities
orchestrator.register('factory-summary', 
  () => apiClient.getFactorySummary(),
  {
    priority: 'high',
    timeout: 5000,
    showSkeletonAfter: 200,
    onSuccess: (data, container) => renderFactorySummary(data, container)
  }
);

orchestrator.register('seus-list', 
  () => apiClient.getSEUs(),
  {
    priority: 'high',
    timeout: 2000,
    showSkeletonAfter: 200,
    onSuccess: (data, container) => renderSEUsList(data, container)
  }
);

orchestrator.register('opportunities', 
  () => apiClient.getOpportunities(60000),
  {
    priority: 'low',
    timeout: 60000, // 60s for slow endpoint
    showSkeletonAfter: 500,
    showSlowWarningAfter: 3000,
    onSuccess: (data, container) => renderOpportunities(data, container),
    onError: (error, container) => {
      // Custom error handling for opportunities
      container.innerHTML = `
        <div class="widget-info">
          <p>Opportunities calculation in progress...</p>
          <small>Check back in a few moments</small>
        </div>
      `;
    }
  }
);

// Load all widgets in parallel
window.addEventListener('DOMContentLoaded', () => {
  orchestrator.loadAll();
});
```

---

## 8. Data Flow Diagrams

### Baseline Training Flow

```
┌──────────────┐
│     User     │
└──────┬───────┘
       │
       │ 1. Select SEU
       v
┌──────────────────┐
│  SEUSelector     │
│  Component       │
└──────┬───────────┘
       │
       │ Event: seu:selected
       │ { seuName, energySources }
       v
┌──────────────────────┐
│  EnergySourceFilter  │
│  Component           │
└──────┬───────────────┘
       │
       │ 2a. Single energy: Auto-select
       │ 2b. Multi energy: User selects
       │
       │ Event: energy:filtered
       │ { sources: ['electricity'] }
       v
┌──────────────────┐
│  Baseline Page   │
│  Handler         │
└──────┬───────────┘
       │
       │ 3. POST /baseline/train-seu
       │    { seu_name, energy_source, days }
       v
┌──────────────────┐
│   API Client     │
│   (with retry)   │
└──────┬───────────┘
       │
       │ 4. Response
       │    { success, model_id, explanation, voice_summary }
       v
┌──────────────────┐
│  Render Result   │
│  - Model card    │
│  - Explanation   │
│  - Voice summary │
└──────────────────┘
```

### Dashboard Progressive Loading Flow

```
┌──────────────┐
│ Page Load    │
└──────┬───────┘
       │
       │ DOMContentLoaded
       v
┌─────────────────────┐
│ LoadingOrchestrator │
└──────┬──────────────┘
       │
       ├─────────────┐───────────────┐
       │             │               │
       v             v               v
 ┌──────────┐  ┌─────────┐   ┌─────────────┐
 │ Widget 1 │  │Widget 2 │   │  Widget 3   │
 │ Summary  │  │  SEUs   │   │Opportunities│
 │ (2s)     │  │ (500ms) │   │   (35s)     │
 └────┬─────┘  └────┬────┘   └─────┬───────┘
      │             │              │
      │200ms        │200ms         │500ms
      v             v              v
 ┌─────────┐   ┌─────────┐   ┌──────────┐
 │Skeleton │   │Skeleton │   │ Skeleton │
 └────┬────┘   └────┬────┘   └────┬─────┘
      │             │              │3s
      │2s           │500ms         v
      v             v          ┌──────────┐
 ┌─────────┐   ┌─────────┐   │  "Slow"  │
 │ Render  │   │ Render  │   │ Warning  │
 │ Success │   │ Success │   └────┬─────┘
 └─────────┘   └─────────┘        │35s
                                  v
                             ┌──────────┐
                             │ Render   │
                             │ Success  │
                             └──────────┘
```

### Component Communication Flow

```
┌─────────────┐       seu:selected       ┌──────────────────┐
│ SEUSelector ├───────────────────────────>│ Baseline Page   │
└─────────────┘                           └──────────────────┘
                                                  │
┌──────────────────┐  energy:filtered            │
│ EnergySource     ├─────────────────────────────┤
│ Filter           │                             │
└──────────────────┘                             │
                                                  │
┌──────────────┐       loading:start             │
│ Loading      │<────────────────────────────────┤
│ Spinner      │                                 │
└──────────────┘       loading:complete          │
                  <────────────────────────────────┤
┌──────────────┐                                 │
│ Error        │       error:show                │
│ Message      │<────────────────────────────────┤
└──────────────┘                                 │
                                                  │
┌──────────────┐       chart:export              │
│ Chart        │<────────────────────────────────┘
│ Container    │
└──────────────┘
```

---

## 9. Implementation Checklist

### Pre-Implementation (Milestone 6.0)
- [x] Component communication pattern defined (CustomEvent)
- [x] State persistence schema designed (localStorage + TTL)
- [x] Component lifecycle documented (init → render → update → destroy)
- [x] API client extended (v3 endpoints, caching, retry)
- [x] Error recovery playbook created (4 error types)
- [x] Multi-energy UX flows specified (3 scenarios)
- [x] Progressive loading pattern documented
- [ ] Architecture document reviewed by human ← **YOU ARE HERE**

### Component Library (Milestone 6.1)
- [ ] BaseComponent class created
- [ ] LoadingSpinner component
- [ ] ErrorMessage component
- [ ] SEUSelector component
- [ ] EnergySourceFilter component
- [ ] ChartContainer component
- [ ] StateManager utility
- [ ] LoadingOrchestrator utility
- [ ] components.css stylesheet
- [ ] Demo page created

### Page Modernization (Milestones 6.2-6.3)
- [ ] Baseline page migrated
- [ ] Dashboard page migrated
- [ ] KPI page migrated
- [ ] Model Performance page migrated
- [ ] Anomaly page migrated
- [ ] Forecast page migrated
- [ ] Comparison page migrated

### Testing & QA
- [ ] Unit tests for components
- [ ] Integration tests for pages
- [ ] E2E workflow tests
- [ ] Mobile responsive testing
- [ ] Accessibility audit (WCAG 2.1 AA)
- [ ] Cross-browser testing (Chrome, Firefox, Safari)
- [ ] Performance testing (<2s page load)

### Deployment
- [ ] Exclude demo page from production
- [ ] Update documentation
- [ ] Create user guide
- [ ] Deploy to staging
- [ ] Production deployment

---

## Summary

**Architecture Decisions Made:**

1. ✅ **Component Communication:** CustomEvent system with `namespace:action` pattern
2. ✅ **State Management:** localStorage with TTL, versioning, auto-cleanup
3. ✅ **API Strategy:** Extended client with caching (5min SEUs, 1min metrics), retry logic (3 attempts, exponential backoff)
4. ✅ **Error Handling:** 4 recovery patterns (timeout, network, 404, 500) with specific UX flows
5. ✅ **Multi-Energy UX:** 3 scenarios defined (single-energy auto-select, multi-energy radio, multi-SEU checkboxes)
6. ✅ **Progressive Loading:** LoadingOrchestrator for independent widget loading, skeleton screens, slow warnings

**Next Step:** Review this document with human, then proceed to Milestone 6.1 (Component Library implementation).

**Estimated Review Time:** 30 minutes

---

**Document Status:** ✅ COMPLETE - Ready for review

**Last Updated:** November 10, 2025
