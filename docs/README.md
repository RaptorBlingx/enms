# 📚 EnMS Documentation

This directory contains all documentation for the Energy Management System (EnMS).

---

## 📁 Directory Structure

```
docs/
├── README.md (this file)
└── api-documentation/
    ├── ENMS-API-DOCUMENTATION-FOR-OVOS.md
    ├── ENMS-API-REVIEW-SUMMARY.md
    ├── API-QUICK-REFERENCE.md
    ├── api-ovos.md
    ├── API-DOCUMENTATION-SUMMARY.md
    ├── API-BASE-PATH-FIX.md
    └── API-PATH-FIX-FINAL.md
```

---

## 📖 Main Documentation Files

### For OVOS Integration (Start Here!)

1. **[ENMS-API-DOCUMENTATION-FOR-OVOS.md](api-documentation/ENMS-API-DOCUMENTATION-FOR-OVOS.md)** (23KB) ⭐
   - **Complete API reference for OVOS integration**
   - All endpoints documented with curl examples
   - Voice query → API mappings
   - Testing commands
   - Recommendations for missing features
   - **READ THIS FIRST if you're Burak (OVOS developer)**

2. **[ENMS-API-REVIEW-SUMMARY.md](api-documentation/ENMS-API-REVIEW-SUMMARY.md)** (13KB) ⭐
   - **Executive summary for Mohamad (Backend)**
   - API maturity score: 85%
   - What's working, what's missing
   - Implementation roadmap
   - Priority rankings with time estimates
   - **READ THIS FIRST if you're the backend developer**

3. **[API-QUICK-REFERENCE.md](api-documentation/API-QUICK-REFERENCE.md)** (2.2KB) ⭐
   - **Quick lookup guide**
   - Most commonly used endpoints
   - Voice query examples
   - Troubleshooting tips
   - **Perfect for quick reference during development**

### Historical Documentation

4. **[api-ovos.md](api-documentation/api-ovos.md)**
   - Original OVOS integration notes

5. **[API-DOCUMENTATION-SUMMARY.md](api-documentation/API-DOCUMENTATION-SUMMARY.md)**
   - General API documentation summary

6. **[API-BASE-PATH-FIX.md](api-documentation/API-BASE-PATH-FIX.md)**
   - Documentation about API path fixes

7. **[API-PATH-FIX-FINAL.md](api-documentation/API-PATH-FIX-FINAL.md)**
   - Final API path configuration

---

## 🎯 Quick Start Guide

### For Burak (OVOS Integration)

1. **Read the main documentation:**
   ```bash
   cat docs/api-documentation/ENMS-API-DOCUMENTATION-FOR-OVOS.md
   ```

2. **Use the quick reference during development:**
   ```bash
   cat docs/api-documentation/API-QUICK-REFERENCE.md
   ```

3. **Test the APIs:**
   ```bash
   python test_enms_api.py
   ```

### For Mohamad (Backend Developer)

1. **Read the review summary:**
   ```bash
   cat docs/api-documentation/ENMS-API-REVIEW-SUMMARY.md
   ```

2. **Understand what needs to be built:**
   - Priority 1: Anomaly search with date ranges (1 hour)
   - Priority 2: Machine status history (2 hours)
   - Priority 3: Aggregated statistics (2 hours)

3. **Test current APIs:**
   ```bash
   python test_enms_api.py
   ```

### For Team Leader

1. **Executive Summary:** Read `ENMS-API-REVIEW-SUMMARY.md`
2. **Key Findings:**
   - APIs are 85% ready for OVOS
   - Need 5 hours of work for 95% readiness
   - Authentication can come later (not blocking)

---

## 📊 API Maturity Status

```
Overall: 85% Ready for OVOS Integration

✅ System Monitoring:    100% Complete
✅ Machine Management:   100% Complete
✅ Time-Series Data:     100% Complete
⚠️  Anomaly Detection:    80% Complete (missing date range filter)
✅ Baseline/ML:          100% Complete
✅ KPI Analytics:        100% Complete
✅ Forecasting:          100% Complete
❌ Authentication:         0% Complete (security concern)
⚠️  Real-time Alerts:     30% Complete (polling only, no webhooks)
```

---

## 🔗 Related Files

- **Testing Script:** `/test_enms_api.py` (in root directory)
- **API Routes:** `/analytics/api/routes/*.py`
- **Main Application:** `/analytics/main.py`

---

## 🆘 Quick Help

### Common Questions

**Q: How do I test if APIs are working?**
```bash
python test_enms_api.py
```

**Q: Where's the complete API reference?**
```bash
cat docs/api-documentation/ENMS-API-DOCUMENTATION-FOR-OVOS.md
```

**Q: What's missing for OVOS?**
- Anomaly search with date ranges
- Machine status history
- Aggregated statistics
- See: `ENMS-API-REVIEW-SUMMARY.md`

**Q: How do I access the APIs?**
```bash
# Local development
curl http://localhost:8001/api/v1/health

# Production (via Nginx)
curl http://your-server/api/analytics/api/v1/health
```

---

## 📝 Documentation Standards

All API documentation should include:
- ✅ Endpoint URL and HTTP method
- ✅ Request parameters with types
- ✅ Response format with examples
- ✅ Use cases and voice query mappings
- ✅ Error handling
- ✅ Testing commands (curl examples)

---

## 🔄 Updates

| Date | File | Change |
|------|------|--------|
| 2025-01-20 | All | Created comprehensive OVOS API documentation |
| 2025-01-20 | README.md | Created documentation index |

---

## 📞 Contacts

- **Backend (Mohamad):** API development and maintenance
- **OVOS Integration (Burak):** Voice assistant integration
- **Team Leader:** Requirements and timeline

---

**Last Updated:** January 20, 2025
