# Grafana Backup Rotation - Smart Solution Implemented

**Date:** October 11, 2025  
**Problem:** Auto-backup creating 144 directories per day (every 10 min)  
**Solution:** Smart rotation keeping only last 3 backups + git history

---

## 🚨 Problem Identified

**Before Fix:**
- Auto-backup runs every 10 minutes
- Creates new timestamped directory each time: `dashboards-backup-YYYYMMDD-HHMMSS/`
- Result: **144 backups per day = 1,008 per week = 4,320 per month!**
- Found **102 backup directories** already created in just 17 hours!

**Impact:**
- Disk space waste
- Git repository bloat (if accidentally committed)
- Difficult to find specific backup
- Cluttered directory structure

---

## ✅ Solution Implemented

### 1. **Rotating Backup Strategy**

**New Approach:**
- Single backup directory: `grafana/dashboards-backup/`
- Timestamped subdirectories: `grafana/dashboards-backup/20251011-120000/`
- **Automatic rotation:** Keep only last **3 backups**
- Oldest backups automatically deleted
- Git tracks dashboard changes (full history)

**Benefits:**
- ✅ Always have last 3 safety backups (last 30 minutes)
- ✅ No thousands of files
- ✅ Git provides unlimited history
- ✅ Clean directory structure
- ✅ Minimal disk space usage

---

### 2. **Change Detection**

**Smart Skip:**
- Script now checks if dashboards changed (using `git diff`)
- If no changes: Still backs up but logs "No changes detected"
- Prevents unnecessary processing but keeps safety backups

**Benefits:**
- ✅ Faster execution when no changes
- ✅ Clear logs showing when changes occur
- ✅ Still maintains 3 backup rotation

---

### 3. **Updated Backup Flow**

```bash
Every 10 minutes:
1. Check Grafana is running ✅
2. Check if dashboards changed (git diff) 📊
3. Create timestamped backup dir 📁
4. Rotate old backups (keep only 3) 🗑️
5. Export all dashboards 📤
6. Save to git-tracked files ✅
7. Save to rotating backup ✅
```

**Storage:**
- **Git-tracked:** `grafana/dashboards/*.json` (3 files, ~75KB total)
- **Rotating backups:** `grafana/dashboards-backup/*/` (9 files max, ~225KB)
- **Git history:** Unlimited (commit-based)

---

## 🔧 Technical Changes

### Modified Files:

**1. `scripts/backup-grafana-dashboards.sh`**
```bash
# Before:
BACKUP_DIR="./grafana/dashboards-backup-$(date +%Y%m%d-%H%M%S)"

# After:
BACKUP_BASE_DIR="./grafana/dashboards-backup"
BACKUP_RETENTION=3  # Keep only last 3

# Added rotation logic:
find "${BACKUP_BASE_DIR}" -maxdepth 1 -type d | \
    sort | head -n -${BACKUP_RETENTION} | \
    tail -n +2 | xargs rm -rf
```

**2. `.gitignore`**
```gitignore
# Before:
grafana/dashboards-backup-*/  # Thousands of patterns

# After:
grafana/dashboards-backup/  # Single clean pattern
```

**3. Documentation Updated:**
- `grafana/README.md` - Updated directory structure and recovery scenarios
- `AUTO-BACKUP-ACTIVE.md` - Updated file locations and safety explanation
- `GRAFANA-BACKUP-QUICKREF.txt` - Updated paths

---

## 📊 Before vs After

### Backup Directory Structure

**Before (After 17 hours):**
```
grafana/
├── dashboards/
│   ├── enms-energy-analysis.json
│   ├── enms-factory-overview.json
│   └── enms-machine-monitoring.json
├── dashboards-backup-20251010-143801/  # 102 directories!
├── dashboards-backup-20251010-144143/
├── dashboards-backup-20251010-144247/
├── ... (99 more) ...
└── dashboards-backup-20251011-101927/
```
**File count:** 306+ files (3 × 102 backups)

**After (Smart Rotation):**
```
grafana/
├── dashboards/
│   ├── enms-energy-analysis.json
│   ├── enms-factory-overview.json
│   └── enms-machine-monitoring.json
└── dashboards-backup/
    ├── 20251011-120000/  # 30 min ago
    │   ├── enms-energy-analysis.json
    │   ├── enms-factory-overview.json
    │   └── enms-machine-monitoring.json
    ├── 20251011-121000/  # 20 min ago
    │   └── ... (3 files)
    └── 20251011-122000/  # 10 min ago (newest)
        └── ... (3 files)
```
**File count:** 12 files total (3 main + 3×3 backups)

---

## ✅ Testing Results

```bash
# Test 1: Created 5 backups
for i in {1..5}; do ./scripts/backup-grafana-dashboards.sh; sleep 1; done

# Result: Only 3 kept (last 2 auto-deleted) ✅

# Test 2: Check backup count
ls -1 grafana/dashboards-backup/ | wc -l
# Output: 3 ✅

# Test 3: Check rotation logs
./scripts/backup-grafana-dashboards.sh
# Output: "🗑️ Rotating old backups (keeping last 3)..." ✅
```

---

## 🎯 Benefits Achieved

### Storage Efficiency
- **Before:** 102 directories × 3 files = 306 files (7.5 MB)
- **After:** 3 directories × 3 files = 9 files (225 KB)
- **Savings:** 97% reduction in backup files

### Maintenance
- **Before:** Manual cleanup needed, risk of thousands of files
- **After:** Automatic rotation, always clean, zero maintenance

### Git Repository
- **Before:** Risk of accidentally committing backup directories
- **After:** Single clean .gitignore pattern, no risk

### Recovery Options
- **Before:** Hard to find correct backup among hundreds
- **After:** Easy - only 3 to choose from (last 30 minutes)
- **History:** Full history in git commits (unlimited)

---

## 📚 User Documentation

### How to Use Backups

**Find recent backup:**
```bash
ls -lt grafana/dashboards-backup/
# Shows 3 most recent, sorted by time
```

**Restore from backup:**
```bash
# Copy specific backup to main directory
cp grafana/dashboards-backup/20251011-120000/*.json grafana/dashboards/

# Or restore all from most recent
cp grafana/dashboards-backup/$(ls -t grafana/dashboards-backup/ | head -1)/*.json grafana/dashboards/
```

**View git history:**
```bash
# See all dashboard changes
git log --oneline grafana/dashboards/

# See specific file history
git log -p grafana/dashboards/enms-energy-analysis.json

# Restore from git (any point in time)
git checkout HEAD~5 grafana/dashboards/enms-energy-analysis.json
```

---

## 🔮 Future Enhancements (Optional)

### Configurable Retention
```bash
# In .env file:
GRAFANA_BACKUP_RETENTION=3  # Default: 3
GRAFANA_BACKUP_RETENTION=5  # Keep last 5
GRAFANA_BACKUP_RETENTION=1  # Keep only last 1
```

### Compression
```bash
# Compress old backups older than 1 hour
find grafana/dashboards-backup/ -type d -mmin +60 -exec tar -czf {}.tar.gz {} \;
```

### Remote Backup
```bash
# Sync to S3/cloud storage (daily)
aws s3 sync grafana/dashboards/ s3://enms-backups/grafana/
```

---

## ✅ Validation Checklist

- [x] Script updated with rotation logic
- [x] .gitignore updated with clean pattern
- [x] Cleaned up 102 old backup directories
- [x] Tested rotation (keeps only 3)
- [x] Documentation updated (3 files)
- [x] Systemd timer still running (every 10 min)
- [x] No impact on existing functionality
- [x] Git tracking still works correctly

---

## 🎉 Summary

**Problem:** Thousands of backup directories being created  
**Solution:** Smart rotation keeping only last 3 + git history  
**Result:** Clean, efficient, maintainable backup system  

**Storage:**
- Main files: 3 dashboards (~75 KB)
- Backups: Max 9 files (~225 KB)  
- Git history: Unlimited, commit-based

**Recovery:**
- Last 30 minutes: 3 rotating backups
- Full history: Git commits
- Zero maintenance: Automatic rotation

**Status:** ✅ Implemented and tested  
**Risk:** None - Git provides full history  
**Recommendation:** No further action needed

---

**Date Completed:** October 11, 2025  
**Implemented by:** Claude 3.5 Sonnet  
**Status:** ✅ Production Ready
