# 🔄 OVOS API Migration Guide: v2 → v3

**For:** Burak (OVOS Integration Developer)  
**Created:** November 7, 2025  
**Migration Deadline:** May 1, 2026 (6 months)  
**Status:** ⚠️ **ACTION REQUIRED** - Old endpoints deprecated

---

## 📋 Executive Summary

**What Changed:**
- ✅ `/ovos/*` endpoints renamed to clean RESTful paths
- ✅ Old endpoints still work (with deprecation warnings)
- ✅ **Zero breaking changes** - seamless migration path
- ⚠️ **6-month window** - old endpoints removed in v4.0 (May 2026)

**Why the Change:**
- `/ovos/*` naming confused users (OVOS is the client, not a feature)
- New names are clearer and RESTful
- Better API organization for long-term maintenance

**Action Required:**
Update OVOS integration to use new endpoint names before May 1, 2026.

---

## 🗺️ Endpoint Migration Map

### Quick Reference Table

| ~~Old Endpoint (DEPRECATED)~~ | **New Endpoint (USE THIS)** | Status |
|--------------|--------------|--------|
| ~~`/api/v1/ovos/train-baseline`~~ | **`/api/v1/baseline/train-seu`** | 🟡 6 months to migrate |
| ~~`/api/v1/ovos/seus`~~ | **`/api/v1/seus`** | 🟡 6 months to migrate |
| ~~`/api/v1/ovos/energy-sources`~~ | **`/api/v1/energy-sources`** | ✅ Already migrated |
| ~~`/api/v1/ovos/summary`~~ | **`/api/v1/factory/summary`** | 🟡 6 months to migrate |
| ~~`/api/v1/ovos/top-consumers`~~ | **`/api/v1/analytics/top-consumers`** | 🟡 6 months to migrate |
| ~~`/api/v1/ovos/machines/{name}/status`~~ | **`/api/v1/machines/status/{name}`** | 🟡 6 months to migrate |
| ~~`/api/v1/ovos/forecast/tomorrow`~~ | **`/api/v1/forecast/short-term`** | 🟡 6 months to migrate |

---

## 🔧 Code Migration Examples

### 1. Train Baseline Endpoint

**Before (v2 - DEPRECATED):**
```python
# Old code - will be removed in v4.0
response = requests.post(
    "http://localhost:8001/api/v1/ovos/train-baseline",
    json={
        "seu_name": "Compressor-1",
        "energy_source": "electricity",
        "features": ["production_count", "outdoor_temp_c"],
        "year": 2025
    }
)
```

**After (v3 - NEW):**
```python
# New code - use this
response = requests.post(
    "http://localhost:8001/api/v1/baseline/train-seu",
    json={
        "seu_name": "Compressor-1",
        "energy_source": "electricity",
        "features": ["production_count", "outdoor_temp_c"],
        "year": 2025
    }
)
```

**Notes:**
- ✅ Request body is **identical**
- ✅ Response format is **identical**
- ✅ Only URL changed

---

### 2. List SEUs Endpoint

**Before (v2 - DEPRECATED):**
```python
# Old code
response = requests.get("http://localhost:8001/api/v1/ovos/seus")
seus = response.json()
```

**After (v3 - NEW):**
```python
# New code
response = requests.get("http://localhost:8001/api/v1/seus")
seus = response.json()
```

**Notes:**
- ✅ Response format is **identical**
- ✅ All query parameters work the same

---

### 3. Factory Summary Endpoint

**Before (v2 - DEPRECATED):**
```python
# Old code
response = requests.post(
    "http://localhost:8001/api/v1/ovos/summary",
    json={
        "start_date": "2025-11-01",
        "end_date": "2025-11-07",
        "machines": ["Compressor-1", "HVAC-Main"]
    }
)
```

**After (v3 - NEW):**
```python
# New code
response = requests.post(
    "http://localhost:8001/api/v1/factory/summary",
    json={
        "start_date": "2025-11-01",
        "end_date": "2025-11-07",
        "machines": ["Compressor-1", "HVAC-Main"]
    }
)
```

---

### 4. Top Energy Consumers

**Before (v2 - DEPRECATED):**
```python
# Old code
response = requests.get(
    "http://localhost:8001/api/v1/ovos/top-consumers",
    params={"period": "week", "limit": 5}
)
```

**After (v3 - NEW):**
```python
# New code
response = requests.get(
    "http://localhost:8001/api/v1/analytics/top-consumers",
    params={"period": "week", "limit": 5}
)
```

---

### 5. Machine Status by Name

**Before (v2 - DEPRECATED):**
```python
# Old code
response = requests.get(
    "http://localhost:8001/api/v1/ovos/machines/Compressor-1/status"
)
```

**After (v3 - NEW):**
```python
# New code
response = requests.get(
    "http://localhost:8001/api/v1/machines/status/Compressor-1"
)
```

---

### 6. Energy Forecast

**Before (v2 - DEPRECATED):**
```python
# Old code
response = requests.get(
    "http://localhost:8001/api/v1/ovos/forecast/tomorrow",
    params={"machine_id": "c0000000-0000-0000-0000-000000000001"}
)
```

**After (v3 - NEW):**
```python
# New code
response = requests.get(
    "http://localhost:8001/api/v1/forecast/short-term",
    params={"machine_id": "c0000000-0000-0000-0000-000000000001"}
)
```

---

## 🧪 Testing Your Migration

### Step 1: Check for Deprecation Warnings

Old endpoints return deprecation warnings in **two places**:

**1. HTTP Headers:**
```http
X-Deprecated: true; use=/api/v1/seus
X-Deprecation-Message: This endpoint is deprecated and will be removed in v4.0
```

**2. Response Body:**
```json
{
  "success": true,
  "data": [...],
  "deprecation_warning": {
    "message": "This endpoint is deprecated. Please use /api/v1/seus instead.",
    "deprecated_endpoint": "/api/v1/ovos/seus",
    "new_endpoint": "/api/v1/seus",
    "removal_date": "2026-05-01",
    "documentation": "See BURAK-API-MIGRATION-GUIDE.md for migration details"
  }
}
```

### Step 2: Update One Endpoint at a Time

**Recommended Migration Order:**
1. ✅ `/seus` (simplest - just URL change)
2. ✅ `/machines/status/{name}` (simple)
3. ✅ `/analytics/top-consumers` (simple)
4. ✅ `/factory/summary` (simple)
5. ✅ `/forecast/short-term` (simple)
6. ✅ `/baseline/train-seu` (most critical - do last after testing others)

### Step 3: Validation Checklist

For each endpoint migration, verify:

- [ ] Request body format unchanged
- [ ] Response structure unchanged
- [ ] All query parameters work
- [ ] Error handling unchanged
- [ ] Voice responses still work
- [ ] No deprecation warnings in logs

### Step 4: Run Full Test Suite

```bash
# Example test script
python test_ovos_integration.py --check-deprecations

# Should output:
# ✅ All endpoints migrated
# ✅ Zero deprecation warnings
# ✅ 100% backward compatibility
```

---

## 📊 Migration Timeline

### Phase 1: Now - December 31, 2025 (2 months)
**Goal:** Update OVOS code to use new endpoints

**Tasks:**
- [ ] Update all 6 endpoint URLs in OVOS code
- [ ] Test each endpoint individually
- [ ] Deploy to OVOS development environment
- [ ] Validate voice commands still work
- [ ] Check logs for deprecation warnings

**Support:** Contact Mohamad for any issues

---

### Phase 2: January 1 - April 30, 2026 (4 months)
**Goal:** Production deployment and monitoring

**Tasks:**
- [ ] Deploy updated OVOS to production
- [ ] Monitor for any issues
- [ ] Remove old endpoint URLs from code
- [ ] Update OVOS documentation
- [ ] Final validation

---

### Phase 3: May 1, 2026 (Deadline)
**Event:** Old `/ovos/*` endpoints **REMOVED** in EnMS v4.0

**What happens:**
- ❌ Old endpoints return HTTP 404 Not Found
- ✅ New endpoints continue working
- ⚠️ Any unmigrated code will break

---

## 🆘 Troubleshooting

### Issue 1: Getting 404 on New Endpoint

**Symptoms:**
```python
response = requests.get("http://localhost:8001/api/v1/seus")
# Returns: 404 Not Found
```

**Solution:**
Check EnMS version - new endpoints only work in v3.0+
```bash
curl http://localhost:8001/api/v1/health
# Check "version" field in response
```

---

### Issue 2: Different Response Format

**Symptoms:**
Response looks different from old endpoint

**Solution:**
Response formats are **identical** between old and new. If different, you may be:
- Using wrong HTTP method (GET vs POST)
- Missing required parameters
- Calling a different endpoint

Double-check the migration table above.

---

### Issue 3: Deprecation Warnings in Logs

**Symptoms:**
Seeing warnings like:
```
[WARNING] Deprecated endpoint /api/v1/ovos/seus called
```

**Solution:**
This means you're still using old endpoints. Update to new endpoints to remove warnings.

---

### Issue 4: Voice Commands Not Working

**Symptoms:**
Voice commands fail after migration

**Solution:**
1. Check endpoint URL is correct
2. Verify request body format unchanged
3. Test with curl first:
```bash
curl -X POST "http://localhost:8001/api/v1/baseline/train-seu" \
  -H "Content-Type: application/json" \
  -d '{
    "seu_name": "Compressor-1",
    "energy_source": "electricity",
    "features": ["production_count"],
    "year": 2025
  }'
```

---

## 📞 Support & Contact

**Need Help?**
- **Technical Issues:** Contact Mohamad (GitHub: @raptorblingx)
- **Documentation:** See `ENMS-API-DOCUMENTATION-FOR-OVOS.md` (single source of truth)
- **API Testing:** Use Swagger UI at `http://localhost:8001/docs`

**Migration Support Available:**
- November 2025 - April 2026
- Response time: < 24 hours for migration issues
- Test environment available for validation

---

## ✅ Migration Checklist

Use this checklist to track your progress:

### Code Updates
- [ ] Updated `/ovos/train-baseline` → `/baseline/train-seu`
- [ ] Updated `/ovos/seus` → `/seus`
- [ ] Updated `/ovos/energy-sources` → `/energy-sources`
- [ ] Updated `/ovos/summary` → `/factory/summary`
- [ ] Updated `/ovos/top-consumers` → `/analytics/top-consumers`
- [ ] Updated `/ovos/machines/{name}/status` → `/machines/status/{name}`
- [ ] Updated `/ovos/forecast/tomorrow` → `/forecast/short-term`

### Testing
- [ ] All endpoints tested individually
- [ ] Voice commands validated
- [ ] No deprecation warnings in logs
- [ ] Error handling still works
- [ ] Response formats verified identical

### Deployment
- [ ] Changes deployed to development
- [ ] Development testing complete
- [ ] Changes deployed to production
- [ ] Production monitoring active
- [ ] Old code removed

### Documentation
- [ ] OVOS code documentation updated
- [ ] Team notified of changes
- [ ] Training materials updated (if applicable)

---

## 🎯 Quick Win Strategy

**Fastest Migration Path (1-2 hours):**

1. **Find and Replace in Code:**
   ```bash
   # In your OVOS codebase
   find . -type f -name "*.py" -exec sed -i 's|/ovos/train-baseline|/baseline/train-seu|g' {} +
   find . -type f -name "*.py" -exec sed -i 's|/ovos/seus|/seus|g' {} +
   find . -type f -name "*.py" -exec sed -i 's|/ovos/summary|/factory/summary|g' {} +
   find . -type f -name "*.py" -exec sed -i 's|/ovos/top-consumers|/analytics/top-consumers|g' {} +
   find . -type f -name "*.py" -exec sed -i 's|/ovos/machines/|/machines/status/|g' {} +
   find . -type f -name "*.py" -exec sed -i 's|/ovos/forecast/tomorrow|/forecast/short-term|g' {} +
   ```

2. **Test Each Changed File:**
   ```bash
   python test_ovos_integration.py
   ```

3. **Deploy and Monitor:**
   ```bash
   # No downtime - both endpoints work!
   deploy_ovos_update.sh
   ```

**Done!** ✅

---

**Document Version:** 1.0  
**Last Updated:** November 7, 2025  
**Next Review:** December 1, 2025  
**Migration Deadline:** May 1, 2026
