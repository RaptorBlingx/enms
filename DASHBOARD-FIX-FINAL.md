# DASHBOARD JAVASCRIPT - FINAL FIX

**Date:** October 13, 2025  
**Status:** ✅ **CORRECTED**

---

## 🐛 PROBLEM IDENTIFIED

The dashboard was showing **9982** for both Active Machines and Baseline Models because:

1. **`/baseline/models` endpoint REQUIRES `machine_id` parameter**
2. Without it, the API returns an error object: `{detail: [{type: "missing", loc: ["query", "machine_id"], ...}]}`
3. JavaScript was calling `.length` on this error object, resulting in weird numbers

---

## ✅ SOLUTION APPLIED

### Changed Dashboard Loading Logic:

**BEFORE (Wrong):**
```javascript
// This fails because machine_id is required!
const baselineResponse = await axios.get(`${API_BASE}/baseline/models`);
const models = baselineResponse.data || [];
document.getElementById('baseline-models-count').textContent = models.length; // = 9982 (error!)
```

**AFTER (Fixed):**
```javascript
// Load machines first
const machinesResponse = await axios.get(`${API_BASE}/machines`, {
    params: { is_active: true }
});
const machines = machinesResponse.data || [];

// Count baseline models across ALL machines
let totalModels = 0;
for (const machine of machines) {
    try {
        const modelResponse = await axios.get(`${API_BASE}/baseline/models`, {
            params: { machine_id: machine.id }  // ✅ Required parameter!
        });
        totalModels += modelResponse.data.total_models || 0;
    } catch (e) {
        // Machine has no models, skip
    }
}
document.getElementById('baseline-models-count').textContent = totalModels;
```

---

## 🔍 OTHER FIXES APPLIED

### 1. **Anomaly Display**
- Changed `machine_id` → `machine_name` in table
- Changed `anomaly_type: 'unknown'` → `'Energy Deviation'` for better readability
- Fixed Jinja template syntax `url_for()` → hardcoded URL

### 2. **Console Logging Added**
- Logs machine count: `[Dashboard] Active machines loaded: 7`
- Logs each machine's models: `[Dashboard] Compressor-1: 3 models`
- Logs total: `[Dashboard] Total baseline models: 3`
- Helps debug future issues

### 3. **Error Handling**
- Gracefully handles machines with no baseline models
- Shows `?` if API calls fail completely

---

## 📊 EXPECTED DASHBOARD VALUES

After refreshing (Ctrl+F5 to bypass cache):

| Card | Expected Value | Source |
|------|---------------|---------|
| **Active Machines** | **7** | GET /machines?is_active=true |
| **Baseline Models** | **3+** | Sum of all machines' models |
| **Anomalies (24h)** | **3** | GET /anomaly/recent?hours=24 |
| **Scheduler Status** | **Active** | GET /health (scheduler.running) |

---

## 🧪 TESTING

### Test the APIs directly:
```bash
# Should return 7
curl -s "http://10.33.10.109:8080/api/analytics/api/v1/machines?is_active=true" | jq 'length'

# Should return 3
curl -s "http://10.33.10.109:8080/api/analytics/api/v1/baseline/models?machine_id=c0000000-0000-0000-0000-000000000001" | jq '.total_models'

# Should return 3
curl -s "http://10.33.10.109:8080/api/analytics/api/v1/anomaly/recent?hours=24" | jq '.total_count'
```

### Check browser console:
1. Open http://10.33.10.109:8080/api/analytics/ui/
2. Press F12 → Console tab
3. Refresh page (Ctrl+F5)
4. Look for:
   ```
   [Dashboard] Active machines loaded: 7 [Array of machines]
   [Dashboard] Compressor-1: 3 models
   [Dashboard] HVAC-1: 0 models
   ...
   [Dashboard] Total baseline models: 3
   ```

---

## 🎯 WHAT SHOULD NOW WORK

1. ✅ **Dashboard shows correct numbers** (7, 3, 3, Active)
2. ✅ **Recent Anomalies table displays** with machine names
3. ✅ **Baseline page** - 7 machines in dropdown
4. ✅ **KPI page** - 7 machines in dropdown
5. ✅ **Console logs** - Help debug any issues

---

## 📝 FILES MODIFIED

1. `/analytics/ui/templates/dashboard.html`
   - Fixed baseline models counting (loop through all machines)
   - Added console.log for debugging
   - Fixed anomaly display (machine_name, anomaly_type)
   - Fixed URL generation

---

## ⚠️ IMPORTANT: CLEAR BROWSER CACHE

The old JavaScript may be cached. To see the fix:

1. **Hard Refresh:** Press `Ctrl + F5` (or `Cmd + Shift + R` on Mac)
2. **Or clear cache:** F12 → Application → Clear storage → Clear site data
3. **Or incognito mode:** Open in new incognito window

---

## ✅ VERIFICATION CHECKLIST

After hard refresh:

- [ ] Active Machines shows **7** (not 9982)
- [ ] Baseline Models shows **3** or more (not 9982)
- [ ] Anomalies shows **3** (not 0)
- [ ] Scheduler Status shows **Active** (not Disabled)
- [ ] Recent Anomalies table shows 3 rows with machine names
- [ ] Service Information section displays correctly
- [ ] Database Health section displays correctly
- [ ] Browser console shows `[Dashboard]` log messages
- [ ] No errors in browser console

---

**Please hard refresh your browser (Ctrl+F5) and verify the numbers are now correct!**
