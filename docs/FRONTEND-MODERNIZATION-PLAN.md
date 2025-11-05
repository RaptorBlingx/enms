# Frontend Modernization Plan - EnMS UI Enhancement

**Date**: November 4, 2025  
**Status**: 🔴 CRITICAL - Frontend significantly behind API capabilities  
**Scope**: Complete frontend overhaul to match enhanced API endpoints  

---

## 🎯 Executive Summary

**Problem**: Frontend UI built on OLD API patterns (machine_id only, no SEU support, no natural language explanations)

**Impact**: 
- ❌ Users cannot access 50% of new API features from UI
- ❌ Voice-friendly explanations invisible to dashboard users
- ❌ Multi-energy machines (Boiler-1: 3 SEUs) show as single entity
- ❌ No way to select SEU or energy source in UI
- ❌ Model explanations not displayed (Task 3, 4, 5 work wasted!)

**Solution**: Systematic frontend modernization across 7 pages + API documentation update

---

## 📊 Current State Analysis

### API Endpoint Status (Backend)

| Endpoint | UUID Support | SEU Name Support | Explanations | Frontend Status |
|----------|-------------|------------------|--------------|-----------------|
| POST /baseline/predict | ✅ | ✅ NEW | ✅ Voice msgs | ❌ UUID only |
| GET /baseline/models | ✅ | ✅ NEW | ✅ Batch explain | ❌ UUID only |
| GET /baseline/model/{id} | ✅ | N/A | ✅ Detailed | ❌ No explain |
| POST /ovos/train-baseline | N/A | ✅ Only | N/A | ❌ Not in UI |
| POST /baseline/train | ✅ | ❌ | ❌ | ✅ In UI (old) |

### Frontend Pages Inventory

#### 1. **baseline.html** (856 lines) - 🔴 CRITICAL UPDATE NEEDED
**Current State**:
- Uses `/baseline/train` with `machine_id` only (line 637-678)
- No SEU dropdown
- No energy source selection
- No model explanation display
- Loads models with `GET /baseline/models?machine_id={uuid}` (line 595)

**Missing Features**:
- ❌ SEU name input (should use `/ovos/train-baseline`)
- ❌ Energy source dropdown (electricity, natural_gas, steam, compressed_air)
- ❌ Model explanation display (Task 3 output)
- ❌ Voice-friendly message display
- ❌ Batch explanation toggle for model list

**Required Changes**:
1. Add SEU dropdown (populate from `/api/v1/ovos/seus`)
2. Add energy source dropdown
3. Replace `/baseline/train` with `/ovos/train-baseline`
4. Add "Show Explanations" toggle for model list
5. Add explanation card UI (accuracy, key drivers, formula, voice summary)
6. Update model table to show explanation preview

**Priority**: 🔴 CRITICAL (most visible gap for users)

---

#### 2. **anomaly.html** (600+ lines) - 🟡 MODERATE UPDATE
**Current State**:
- Uses `machine_id` filter only (line 381-416)
- No SEU-level filtering
- Displays anomalies by machine

**Missing Features**:
- ❌ SEU-level anomaly filtering
- ❌ Energy source filter
- ❌ Multi-energy anomaly comparison

**Required Changes**:
1. Add optional SEU filter dropdown
2. Add energy source filter
3. Update anomaly display to show SEU name when available
4. Consider: "Group by SEU" vs "Group by Machine" toggle

**Priority**: 🟡 MODERATE (anomalies currently machine-scoped)

---

#### 3. **dashboard.html** (600+ lines) - 🟠 HIGH UPDATE
**Current State**:
- Shows system stats (line 321, 425, 539)
- Machine-centric view
- No SEU breakdown

**Missing Features**:
- ❌ SEU count display
- ❌ Energy source breakdown pie chart
- ❌ Multi-energy consumption trends
- ❌ SEU-specific quick stats

**Required Changes**:
1. Add SEU count to system stats card
2. Create "Energy Sources" pie chart (4 sources)
3. Add "Top Energy-Consuming SEUs" table (not machines)
4. Update quick stats to show total SEUs monitored
5. Add filter: "View by Machine" vs "View by SEU"

**Priority**: 🟠 HIGH (dashboard sets first impression)

---

#### 4. **model_performance.html** (1000+ lines) - 🟡 MODERATE UPDATE
**Current State**:
- Uses `machine_id` extensively (line 565-945)
- Shows model performance metrics
- No explanation display

**Missing Features**:
- ❌ Model explanation tab
- ❌ Key drivers chart
- ❌ Natural language accuracy description
- ❌ SEU-level performance comparison

**Required Changes**:
1. Add "Explanation" tab (alongside Performance, Alerts)
2. Display explanation fields from EP13a:
   - Accuracy explanation
   - Key drivers table
   - Formula explanation
   - Impact summary (positive/negative)
   - Voice summary
3. Add SEU dropdown for multi-energy machines
4. Create "Feature Importance" bar chart

**Priority**: 🟡 MODERATE (power users benefit most)

---

#### 5. **comparison.html** (600+ lines) - 🟢 LOW UPDATE
**Current State**:
- Multi-machine comparison with `machine_ids` (line 518-526)
- Energy consumption charts

**Missing Features**:
- ❌ SEU-level comparison
- ❌ Energy source filter
- ❌ Cross-energy-source comparison

**Required Changes**:
1. Add "Compare by Machine" vs "Compare by SEU" toggle
2. Add energy source filter (show only electricity SEUs, etc.)
3. Update chart to show SEU names when in SEU mode
4. Add "Energy Source Mix" stacked bar chart

**Priority**: 🟢 LOW (advanced feature, fewer users)

---

#### 6. **forecast.html** (500+ lines) - 🟡 MODERATE UPDATE
**Current State**:
- Uses `machine_id` for forecasts (line 264, 320, 456)
- Energy demand prediction

**Missing Features**:
- ❌ SEU-level forecasting
- ❌ Multi-energy forecast comparison
- ❌ Energy source selection

**Required Changes**:
1. Add SEU dropdown (for multi-energy machines)
2. Add energy source selector
3. Update forecast API calls to use SEU when available
4. Display forecast by energy source (separate charts)

**Priority**: 🟡 MODERATE (forecasting is machine-level OK, but SEU adds value)

---

#### 7. **kpi.html** (400+ lines) - 🟠 HIGH UPDATE
**Current State**:
- Machine-level KPI calculations
- No energy source breakdown

**Missing Features**:
- ❌ SEU-specific KPIs
- ❌ Energy source cost breakdown
- ❌ Multi-energy carbon footprint

**Required Changes**:
1. Add "View by Machine" vs "View by SEU" toggle
2. Add energy source breakdown table
3. Show KPIs per energy source:
   - Electricity: kWh, cost ($0.15/kWh), carbon (0.45 kg CO₂/kWh)
   - Natural gas: m³, cost ($0.50/m³), carbon (2.03 kg CO₂/m³)
   - Steam: kg, cost ($0.08/kg), carbon (0.35 kg CO₂/kg)
   - Compressed air: Nm³, cost ($0.03/Nm³), carbon (0.12 kg CO₂/Nm³)
4. Create energy source comparison chart

**Priority**: 🟠 HIGH (KPIs drive business decisions)

---

## 🏗️ Architecture Gaps

### Missing UI Components

#### 1. SEU Selector Component (NEW)
**Purpose**: Unified dropdown for SEU selection across all pages

**Features**:
- Fetches SEUs from `/api/v1/ovos/seus`
- Groups by machine name
- Shows energy source badge
- Supports search/filter

**Usage**:
```html
<div class="seu-selector">
  <label>Select SEU</label>
  <select id="seu-select" class="form-select">
    <option value="">-- All SEUs --</option>
    <optgroup label="Compressor-1">
      <option value="seu_uuid_1" data-energy="electricity">
        Compressor-1 (Electricity)
      </option>
    </optgroup>
    <optgroup label="Boiler-1">
      <option value="seu_uuid_2" data-energy="electricity">
        Boiler-1 (Electricity)
      </option>
      <option value="seu_uuid_3" data-energy="natural_gas">
        Boiler-1 (Natural Gas)
      </option>
      <option value="seu_uuid_4" data-energy="steam">
        Boiler-1 (Steam)
      </option>
    </optgroup>
  </select>
</div>
```

**Implementation**:
- Create `static/js/components/seu-selector.js`
- Cache SEU list (updates hourly)
- Emit events on selection change

---

#### 2. Model Explanation Card Component (NEW)
**Purpose**: Display natural language model explanations (Task 3, 5 output)

**Features**:
- Accuracy interpretation with color coding
- Key drivers table (ranked by impact)
- Formula explanation (collapsible)
- Impact summary (positive vs negative)
- Voice summary (TTS-ready)

**Design**:
```html
<div class="explanation-card">
  <div class="explanation-header">
    <h5>Model Explanation</h5>
    <span class="accuracy-badge excellent">98.7% Accuracy</span>
  </div>
  
  <div class="explanation-body">
    <p class="accuracy-text">
      This model has excellent accuracy with an R-squared of 0.9868...
    </p>
    
    <h6>Key Energy Drivers (Ranked)</h6>
    <table class="drivers-table">
      <tr>
        <td>1. Equipment Load Factor</td>
        <td class="decreases">-362.61 kWh/unit</td>
        <td><span class="impact-badge high">High Impact</span></td>
      </tr>
      <!-- More drivers -->
    </table>
    
    <details class="formula-details">
      <summary>Formula Explanation</summary>
      <p>Energy = 366.41 + (0.000004 × production) - (0.569 × pressure)...</p>
    </details>
    
    <div class="voice-summary">
      <strong>Voice Summary:</strong>
      <p>"The baseline model for Compressor-1 has 98.7% accuracy..."</p>
    </div>
  </div>
</div>
```

**Implementation**:
- Create `static/js/components/explanation-card.js`
- Add CSS in `static/css/components.css`
- Reusable across baseline.html, model_performance.html

---

#### 3. Energy Source Badge Component (NEW)
**Purpose**: Visual indicator for energy source type

**Design**:
```html
<span class="energy-badge electricity">⚡ Electricity</span>
<span class="energy-badge natural-gas">🔥 Natural Gas</span>
<span class="energy-badge steam">♨️ Steam</span>
<span class="energy-badge compressed-air">💨 Compressed Air</span>
```

**CSS**:
```css
.energy-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}
.energy-badge.electricity { background: #3498db; color: white; }
.energy-badge.natural-gas { background: #e74c3c; color: white; }
.energy-badge.steam { background: #9b59b6; color: white; }
.energy-badge.compressed-air { background: #1abc9c; color: white; }
```

---

### API Integration Gaps

#### Missing API Calls in Frontend

| API Endpoint | Purpose | Used By | Status |
|--------------|---------|---------|--------|
| GET /api/v1/ovos/seus | List all SEUs | All pages | ❌ Not called |
| GET /api/v1/ovos/energy-sources | List energy sources | Dropdowns | ❌ Not called |
| POST /api/v1/ovos/train-baseline | Train with SEU name | baseline.html | ❌ Not called |
| GET /api/v1/baseline/models?seu_name=X | List models by SEU | baseline.html | ❌ Not called |
| GET /api/v1/baseline/models?include_explanation=true | Batch explanations | baseline.html | ❌ Not called |
| GET /api/v1/baseline/model/{id}?include_explanation=true | Single explanation | model_performance.html | ❌ Not called |
| POST /api/v1/baseline/predict (SEU name) | Predict with SEU | baseline.html | ❌ Not called |

---

## 🚀 Implementation Roadmap

### Phase 1: Core Infrastructure (Priority 🔴)

**Goal**: Create reusable components and API integration layer

**Tasks**:
1. ✅ Create `/analytics/ui/static/js/api-client.js` - Centralized API wrapper
2. ✅ Create `/analytics/ui/static/js/components/seu-selector.js` - SEU dropdown
3. ✅ Create `/analytics/ui/static/js/components/energy-badge.js` - Energy badges
4. ✅ Create `/analytics/ui/static/js/components/explanation-card.js` - Explanation display
5. ✅ Create `/analytics/ui/static/css/components.css` - Component styles

**Deliverables**:
- Reusable JavaScript modules
- Component library documentation
- API client with error handling

**Time Estimate**: 4-6 hours

---

### Phase 2: Baseline Page Overhaul (Priority 🔴)

**Goal**: Full SEU support + model explanations

**Tasks**:
1. ✅ Add SEU selector to training form
2. ✅ Add energy source dropdown
3. ✅ Replace `/baseline/train` with `/ovos/train-baseline`
4. ✅ Add "Show Explanations" toggle to model list
5. ✅ Display explanation card when toggled
6. ✅ Update model table with explanation preview
7. ✅ Add voice summary display
8. ✅ Test with real data (Compressor-1, Boiler-1)

**Deliverables**:
- Updated `baseline.html` with SEU support
- Model explanation display
- Training with SEU name working

**Time Estimate**: 6-8 hours

---

### Phase 3: Dashboard Enhancement (Priority 🟠)

**Goal**: SEU-aware statistics and multi-energy metrics

**Tasks**:
1. ✅ Add SEU count to system stats
2. ✅ Create energy source breakdown chart (pie/donut)
3. ✅ Add "Top SEUs by Consumption" table
4. ✅ Add "View by Machine" vs "View by SEU" toggle
5. ✅ Update real-time metrics to show SEU data
6. ✅ Add energy source filter

**Deliverables**:
- SEU-aware dashboard
- Multi-energy visualization
- Real-time SEU monitoring

**Time Estimate**: 5-7 hours

---

### Phase 4: KPI Page Enhancement (Priority 🟠)

**Goal**: Energy source breakdown and SEU-specific KPIs

**Tasks**:
1. ✅ Add "View by Machine" vs "View by SEU" toggle
2. ✅ Create energy source breakdown table
3. ✅ Show KPIs per energy source (cost, carbon, units)
4. ✅ Add energy source comparison chart
5. ✅ Calculate total cost by energy source
6. ✅ Display carbon footprint by source

**Deliverables**:
- SEU-level KPIs
- Energy source cost analysis
- Carbon footprint breakdown

**Time Estimate**: 4-6 hours

---

### Phase 5: Model Performance Page (Priority 🟡)

**Goal**: Add explanation tab and feature importance

**Tasks**:
1. ✅ Add "Explanation" tab to page
2. ✅ Display full explanation card (from EP13a)
3. ✅ Create "Feature Importance" bar chart
4. ✅ Add SEU dropdown for multi-energy machines
5. ✅ Show key drivers ranked by impact
6. ✅ Display formula explanation

**Deliverables**:
- Explanation tab functional
- Feature importance visualization
- SEU-level performance view

**Time Estimate**: 5-7 hours

---

### Phase 6: Secondary Pages (Priority 🟡-🟢)

**Goal**: Update remaining pages with SEU support

**Tasks**:
1. **anomaly.html** - Add SEU filter, energy source filter
2. **forecast.html** - Add SEU dropdown, energy source selector
3. **comparison.html** - Add SEU comparison mode, energy filter

**Deliverables**:
- All pages SEU-aware
- Consistent UX across application

**Time Estimate**: 6-8 hours (2-3 hours per page)

---

### Phase 7: Testing & Documentation (Priority 🟢)

**Goal**: Comprehensive testing and user guide

**Tasks**:
1. ✅ Test all pages with real data
2. ✅ Test multi-energy machines (Boiler-1: 3 SEUs)
3. ✅ Test single-energy machines (Compressor-1: 1 SEU)
4. ✅ Create user guide for SEU features
5. ✅ Create admin guide for energy source management
6. ✅ Update API documentation with frontend examples

**Deliverables**:
- Test report (all scenarios passed)
- User documentation
- Admin guide

**Time Estimate**: 4-6 hours

---

## 📋 Detailed Task Breakdown

### Task 1: Create Reusable SEU Selector Component

**File**: `/analytics/ui/static/js/components/seu-selector.js`

**Implementation**:
```javascript
class SEUSelector {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    this.options = {
      allowAll: true, // Show "All SEUs" option
      energyFilter: null, // Filter by energy source
      onChange: () => {}, // Callback on selection
      ...options
    };
    this.seus = [];
    this.machines = [];
    this.init();
  }
  
  async init() {
    await this.loadSEUs();
    await this.loadMachines();
    this.render();
  }
  
  async loadSEUs() {
    const response = await axios.get('/api/v1/ovos/seus');
    this.seus = response.data;
  }
  
  async loadMachines() {
    const response = await axios.get('/api/v1/machines');
    this.machines = response.data;
  }
  
  render() {
    // Group SEUs by machine
    const grouped = this.groupByMachine();
    
    let html = '<select class="form-select seu-select">';
    if (this.options.allowAll) {
      html += '<option value="">-- All SEUs --</option>';
    }
    
    for (const [machineName, seuList] of Object.entries(grouped)) {
      html += `<optgroup label="${machineName}">`;
      for (const seu of seuList) {
        if (this.options.energyFilter && seu.energy_source !== this.options.energyFilter) {
          continue;
        }
        html += `<option value="${seu.id}" data-machine="${seu.machine_id}" data-energy="${seu.energy_source}">
          ${seu.name} (${this.formatEnergySource(seu.energy_source)})
        </option>`;
      }
      html += '</optgroup>';
    }
    
    html += '</select>';
    this.container.innerHTML = html;
    
    // Add event listener
    this.container.querySelector('select').addEventListener('change', (e) => {
      const seuId = e.target.value;
      const seu = this.seus.find(s => s.id === seuId);
      this.options.onChange(seu);
    });
  }
  
  groupByMachine() {
    const grouped = {};
    for (const seu of this.seus) {
      const machine = this.machines.find(m => m.id === seu.machine_id);
      const machineName = machine ? machine.name : 'Unknown Machine';
      if (!grouped[machineName]) grouped[machineName] = [];
      grouped[machineName].push(seu);
    }
    return grouped;
  }
  
  formatEnergySource(source) {
    const map = {
      'electricity': '⚡ Electricity',
      'natural_gas': '🔥 Natural Gas',
      'steam': '♨️ Steam',
      'compressed_air': '💨 Compressed Air'
    };
    return map[source] || source;
  }
}
```

**Usage in baseline.html**:
```html
<div id="seu-selector-container"></div>

<script>
  const seuSelector = new SEUSelector('seu-selector-container', {
    onChange: (seu) => {
      console.log('Selected SEU:', seu);
      // Load models for this SEU
      loadModels(seu.name, seu.energy_source);
    }
  });
</script>
```

---

### Task 2: Create Model Explanation Card Component

**File**: `/analytics/ui/static/js/components/explanation-card.js`

**Implementation**:
```javascript
class ExplanationCard {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
  }
  
  render(explanation) {
    if (!explanation) {
      this.container.innerHTML = '<p class="text-muted">No explanation available</p>';
      return;
    }
    
    const r2 = explanation.r_squared || 0;
    const accuracyClass = this.getAccuracyClass(r2);
    const accuracyBadge = this.getAccuracyBadge(r2);
    
    const html = `
      <div class="explanation-card">
        <div class="explanation-header">
          <h5>Model Explanation</h5>
          ${accuracyBadge}
        </div>
        
        <div class="explanation-body">
          <div class="accuracy-section">
            <h6>Accuracy</h6>
            <p class="accuracy-text ${accuracyClass}">
              ${explanation.accuracy_explanation}
            </p>
          </div>
          
          <div class="drivers-section">
            <h6>Key Energy Drivers (Ranked by Impact)</h6>
            ${this.renderDriversTable(explanation.key_drivers)}
          </div>
          
          <details class="formula-details">
            <summary>📐 Formula Explanation</summary>
            <div class="formula-content">
              <p>${explanation.formula_explanation}</p>
            </div>
          </details>
          
          <div class="impact-summary">
            <h6>Impact Summary</h6>
            ${this.renderImpactSummary(explanation.impact_summary)}
          </div>
          
          <div class="voice-summary">
            <h6>🎙️ Voice Summary (TTS-Ready)</h6>
            <p class="voice-text">"${explanation.voice_summary}"</p>
            <button class="btn btn-sm btn-outline-primary" onclick="speakText('${explanation.voice_summary}')">
              🔊 Speak
            </button>
          </div>
        </div>
      </div>
    `;
    
    this.container.innerHTML = html;
  }
  
  getAccuracyClass(r2) {
    if (r2 >= 0.95) return 'accuracy-excellent';
    if (r2 >= 0.85) return 'accuracy-very-good';
    if (r2 >= 0.70) return 'accuracy-good';
    if (r2 >= 0.50) return 'accuracy-moderate';
    return 'accuracy-poor';
  }
  
  getAccuracyBadge(r2) {
    const percent = (r2 * 100).toFixed(1);
    let badgeClass = 'badge-success';
    let label = 'Excellent';
    
    if (r2 < 0.50) { badgeClass = 'badge-danger'; label = 'Poor'; }
    else if (r2 < 0.70) { badgeClass = 'badge-warning'; label = 'Moderate'; }
    else if (r2 < 0.85) { badgeClass = 'badge-info'; label = 'Good'; }
    else if (r2 < 0.95) { badgeClass = 'badge-primary'; label = 'Very Good'; }
    
    return `<span class="badge ${badgeClass}">${percent}% ${label}</span>`;
  }
  
  renderDriversTable(drivers) {
    if (!drivers || drivers.length === 0) return '<p class="text-muted">No drivers available</p>';
    
    let html = '<table class="table drivers-table">';
    html += '<thead><tr><th>Rank</th><th>Driver</th><th>Impact</th><th>Direction</th></tr></thead><tbody>';
    
    for (const driver of drivers) {
      const directionBadge = driver.direction === 'increases' 
        ? '<span class="badge badge-danger-light">↑ Increases</span>'
        : '<span class="badge badge-success-light">↓ Decreases</span>';
      
      html += `
        <tr>
          <td><span class="rank-badge">#${driver.rank}</span></td>
          <td><strong>${driver.human_name}</strong></td>
          <td>${driver.coefficient.toFixed(3)}</td>
          <td>${directionBadge}</td>
        </tr>
      `;
    }
    
    html += '</tbody></table>';
    return html;
  }
  
  renderImpactSummary(summary) {
    if (!summary) return '<p class="text-muted">No impact summary available</p>';
    
    let html = '<div class="impact-grid">';
    
    // Positive impacts
    html += '<div class="impact-col positive">';
    html += '<h7>📈 Increases Energy</h7>';
    if (summary.positive_impacts && summary.positive_impacts.length > 0) {
      html += '<ul>';
      for (const impact of summary.positive_impacts) {
        html += `<li>${impact.feature}: ${impact.impact}</li>`;
      }
      html += '</ul>';
    } else {
      html += '<p class="text-muted">None</p>';
    }
    html += '</div>';
    
    // Negative impacts
    html += '<div class="impact-col negative">';
    html += '<h7>📉 Decreases Energy</h7>';
    if (summary.negative_impacts && summary.negative_impacts.length > 0) {
      html += '<ul>';
      for (const impact of summary.negative_impacts) {
        html += `<li>${impact.feature}: ${impact.impact}</li>`;
      }
      html += '</ul>';
    } else {
      html += '<p class="text-muted">None</p>';
    }
    html += '</div>';
    
    html += '</div>';
    return html;
  }
}
```

---

## 🧪 Testing Strategy

### Test Scenarios

#### Scenario 1: Single-Energy Machine (Compressor-1)
1. Select Compressor-1 from SEU dropdown
2. Verify only 1 SEU shown (electricity)
3. Train baseline with SEU name
4. View model explanation
5. Verify voice summary displayed

#### Scenario 2: Multi-Energy Machine (Boiler-1)
1. Select Boiler-1 from machine dropdown
2. Verify 3 SEUs shown (electricity, natural_gas, steam)
3. Select each SEU independently
4. Train baselines for each energy source
5. Compare models across energy sources

#### Scenario 3: Model Explanation Display
1. Load model with `include_explanation=true`
2. Verify all explanation fields rendered:
   - Accuracy explanation
   - Key drivers table
   - Formula explanation
   - Impact summary
   - Voice summary
3. Click "Speak" button, verify TTS works

#### Scenario 4: Batch Explanation Toggle
1. Load model list with toggle OFF
2. Verify no explanations shown
3. Toggle ON
4. Verify all models show explanation preview
5. Verify performance acceptable (<3s for 46 models)

---

## 📈 Success Metrics

### Functional Completeness
- [ ] All 7 pages updated with SEU support
- [ ] All new API endpoints utilized in UI
- [ ] Model explanations displayed properly
- [ ] Energy source badges visible
- [ ] SEU selector working on all pages

### Performance Targets
- [ ] Explanation card renders <50ms
- [ ] SEU selector populates <200ms
- [ ] Batch explanations load <3s (50 models)
- [ ] No UI blocking during API calls

### User Experience
- [ ] Consistent UX across all pages
- [ ] Clear visual hierarchy
- [ ] Helpful error messages
- [ ] Responsive design (mobile/tablet)
- [ ] Accessibility (WCAG 2.1 AA)

---

## 🚨 Critical Risks

### Risk 1: Scope Creep
**Mitigation**: Stick to phased approach, defer nice-to-haves

### Risk 2: API Breaking Changes
**Mitigation**: Keep old UUID endpoints working (backward compatibility)

### Risk 3: Performance Degradation
**Mitigation**: Cache SEU list, lazy-load explanations, paginate results

### Risk 4: Incomplete Documentation
**Mitigation**: Update API docs FIRST before starting frontend work

---

## 📝 Next Steps (Immediate Actions)

1. ✅ **Update API Documentation** - Ensure MD file has all enhanced endpoints documented
2. ✅ **Create Component Library** - Build reusable components (Phase 1)
3. ✅ **Baseline Page Overhaul** - Priority #1 (Phase 2)
4. ✅ **Dashboard Enhancement** - Priority #2 (Phase 3)
5. ✅ **Testing & Validation** - Test each phase before moving to next

---

**Document Status**: 📋 PLANNING COMPLETE - Ready for implementation  
**Next Review**: After Phase 1 completion  
**Owner**: AI Development Team  
**Stakeholder**: Mr. Umut, Burak (OVOS integration)
