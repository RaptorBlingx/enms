# ✅ Anomaly Count Discrepancy - FIXED

**Date**: October 21, 2025  
**Reporter**: User (End-user Testing)  
**Status**: ✅ RESOLVED & PUSHED TO GIT

---

## 🐛 Issue Reported

During end-user testing, discrepancy found between two dashboards:

| Dashboard | Location | Anomaly Count (24h) | Status |
|-----------|----------|---------------------|--------|
| **Portal Dashboard** | `/` (index.html) | 0 | ✅ Correct |
| **Analytics Dashboard** | `/ui/` (dashboard.html) | 20 | ❌ Wrong |

User question: *"What is going on here?"*

---

## 🔍 Root Cause Analysis

### Portal Dashboard (Correct)
- **Endpoint**: `GET /api/v1/health`
- **Field**: `recent_anomalies`
- **Query**: 
  ```sql
  SELECT COUNT(*) 
  FROM anomalies 
  WHERE detected_at > NOW() - INTERVAL '24 hours'
  ```
- **Result**: 0 anomalies ✅

### Analytics Dashboard (Wrong)
- **Endpoint**: `GET /api/v1/anomaly/recent`
- **Parameters**: ❌ **NONE** (relied on default)
- **Default Behavior**: Last **7 days** when no `start_time`/`end_time` provided
- **Result**: 20 anomalies from Oct 16-20 (5+ days ago)

### The Bug
The Analytics Dashboard JavaScript was passing a non-existent parameter:
```javascript
// ❌ WRONG CODE:
params: { hours: 24 }  // This parameter doesn't exist in the API!
```

The API endpoint `/anomaly/recent` doesn't have an `hours` parameter - it uses `start_time` and `end_time` (ISO 8601 timestamps).

---

## 🛠️ Fix Applied

**File**: `analytics/ui/templates/dashboard.html`

**Before**:
```javascript
async function loadRecentAnomalies() {
    try {
        const anomaliesResponse = await axios.get(`${API_BASE}/anomaly/recent`, {
            params: {
                hours: 24  // ❌ This doesn't work!
            }
        });
```

**After**:
```javascript
async function loadRecentAnomalies() {
    try {
        // Calculate 24-hour time window
        const endTime = new Date();
        const startTime = new Date(endTime.getTime() - (24 * 60 * 60 * 1000));
        
        const anomaliesResponse = await axios.get(`${API_BASE}/anomaly/recent`, {
            params: {
                start_time: startTime.toISOString(),  // ✅ Proper ISO timestamp
                end_time: endTime.toISOString(),      // ✅ Proper ISO timestamp
                limit: 100
            }
        });
```

---

## ✅ Verification

### Before Fix
```bash
# Portal Dashboard
curl http://localhost:8001/api/v1/health | jq '.recent_anomalies'
# Result: 0

# Analytics Dashboard (default 7 days)
curl http://localhost:8001/api/v1/anomaly/recent | jq '.total_count'
# Result: 20
```

### After Fix
```bash
# Portal Dashboard (unchanged)
curl http://localhost:8001/api/v1/health | jq '.recent_anomalies'
# Result: 0

# Analytics Dashboard (now with 24h window)
curl "http://localhost:8001/api/v1/anomaly/recent?start_time=2025-10-20T06:40:25Z&end_time=2025-10-21T06:40:25Z" | jq '.total_count'
# Result: 0
```

### Anomaly Timeline
```bash
# Those 20 anomalies were from 5+ days ago:
curl "http://localhost:8001/api/v1/anomaly/recent?limit=5" | jq '{total, oldest: .anomalies[-1].detected_at, newest: .anomalies[0].detected_at}'
```

**Result**:
```json
{
  "total": 5,
  "oldest": "2025-10-16T14:30:00+00:00",  // 5+ days ago
  "newest": "2025-10-20T06:00:00+00:00"   // 24.5 hours ago (outside 24h window)
}
```

---

## 🚀 Deployment Steps

1. **Updated Code**: Modified `dashboard.html`
2. **Rebuilt Container**: 
   ```bash
   docker compose build analytics
   docker compose up -d analytics
   ```
3. **Verified**: Both dashboards now show consistent counts
4. **Committed**: 
   ```bash
   git add analytics/ui/templates/dashboard.html .github/copilot-instructions.md
   git commit -m "fix: correct Analytics Dashboard anomaly count to show 24h instead of 7 days"
   git push origin main
   ```

**Commit**: `14fab15`  
**Pushed to**: GitHub & GitLab (both remotes)

---

## 📋 Additional Work

As part of this session, also created:
- **`.github/copilot-instructions.md`**: AI agent guidance document (190 lines)
  - Architecture overview
  - Development workflows
  - Critical commands
  - Common issues & solutions
  - Project-specific patterns

---

## 🎯 User Action Required

**Refresh the Analytics Dashboard** in your browser:
- **Hard Refresh**: `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (Mac)
- The container has been rebuilt, so new code is active

Both dashboards will now show **0 anomalies (24h)** consistently! ✅

---

## 📊 Impact

- **Bug Severity**: Medium (data accuracy issue, not critical)
- **User Impact**: Could cause confusion about system status
- **Detection**: Caught during end-user testing ✅
- **Fix Time**: ~15 minutes (analysis + fix + deploy)
- **Testing**: Verified via API calls and logs

---

## 🔄 Related Issues

None - this was an isolated frontend parameter mismatch.

---

**Fixed by**: AI Assistant (Claude)  
**Reported by**: User (End-user Testing)  
**Status**: ✅ RESOLVED  
**Pushed**: October 21, 2025 07:30 UTC
