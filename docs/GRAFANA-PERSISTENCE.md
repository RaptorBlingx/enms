# Grafana Dashboard Backup & Restore

## 🚨 CRITICAL: How Grafana Persistence Works

### Current Setup:
- **Dashboards are provisioned from**: `./grafana/dashboards/*.json`
- **UI changes are saved to**: Docker volume `enms-grafana-data` (SQLite database)
- **Changes are NOT automatically synced** back to JSON files

### The Problem:
1. You edit a dashboard in Grafana UI ✏️
2. Changes saved to Grafana's database (Docker volume) 💾
3. JSON files in `./grafana/dashboards/` remain unchanged ❌
4. You commit to git → Old dashboards committed ⚠️
5. Someone clones repo → Gets old dashboards 😱
6. You run `docker compose down -v` → Changes lost! 💥

---

## ✅ SOLUTION: Export Before Committing

### Workflow for Making Grafana Changes:

```bash
# 1. Make changes in Grafana UI
#    → Edit panels, queries, layouts, etc.

# 2. Export changes back to JSON files
./scripts/backup-grafana-dashboards.sh

# 3. Review the changes
git diff grafana/dashboards/

# 4. Commit and push
git add grafana/dashboards/*.json
git commit -m "Update Grafana dashboards: [describe changes]"
git push
```

### Automated Backup (Recommended):

Set up a cron job to automatically backup dashboards:

```bash
# Edit crontab
crontab -e

# Add this line to backup every day at 2 AM
0 2 * * * cd /home/ubuntu/enms && ./scripts/backup-grafana-dashboards.sh >> /var/log/grafana-backup.log 2>&1

# Or backup every 6 hours
0 */6 * * * cd /home/ubuntu/enms && ./scripts/backup-grafana-dashboards.sh >> /var/log/grafana-backup.log 2>&1
```

---

## 📦 What Gets Saved Where

### Node-RED (Already Safe ✅):
- **Config**: `./nodered/data/` (volume mounted, persisted to git)
- **Flows**: `./nodered/data/flows.json`
- **Changes automatically saved** to git-tracked files

### Grafana (Needs Manual Export ⚠️):
- **Dashboards**: `./grafana/dashboards/*.json` (provisioned, read-only)
- **UI Changes**: Docker volume `enms-grafana-data` (ephemeral)
- **Must export** using backup script before committing

### What's Safe to Delete:
```bash
# This WILL delete Grafana UI changes:
docker compose down -v

# This is SAFE (keeps volumes):
docker compose down
docker compose restart grafana
```

---

## 🔧 Backup Script Details

### Script Location:
```
./scripts/backup-grafana-dashboards.sh
```

### What It Does:
1. Connects to Grafana API
2. Lists all dashboards
3. Exports each dashboard JSON
4. Saves to `./grafana/dashboards/*.json`
5. Creates timestamped backup in `./grafana/dashboards-backup-YYYYMMDD-HHMMSS/`

### Requirements:
- Grafana must be running (`docker compose up -d grafana`)
- `jq` must be installed (`sudo apt install jq`)
- Grafana credentials in `.env` file

### Environment Variables:
```bash
GRAFANA_URL=http://localhost:3001
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin
```

---

## 🎯 Best Practices

### Before Making Changes:
```bash
# 1. Create a backup of current state
./scripts/backup-grafana-dashboards.sh

# 2. Commit the backup
git add grafana/dashboards/*.json
git commit -m "Backup dashboards before modifications"
```

### After Making Changes:
```bash
# 1. Export updated dashboards
./scripts/backup-grafana-dashboards.sh

# 2. Review what changed
git diff grafana/dashboards/

# 3. Commit the changes
git add grafana/dashboards/*.json
git commit -m "Update dashboards: Added new panel for XYZ"
git push
```

### Regular Backups:
```bash
# Set up automated daily backups
./scripts/setup-grafana-backup-cron.sh
```

---

## 🆘 Recovery Scenarios

### Scenario 1: Lost Changes After `docker compose down -v`
If you ran this and lost Grafana changes:
1. Check git history: `git log --all -- grafana/dashboards/`
2. Restore from backup: `git checkout <commit> -- grafana/dashboards/`
3. Restart Grafana: `docker compose up -d grafana`

### Scenario 2: Someone Cloned Repo and Dashboards Are Old
The person who made changes forgot to run backup script:
1. If original system still running: Run backup script on that system
2. Commit and push the exported JSON files
3. Other people pull the updates

### Scenario 3: Accidentally Overwrote Dashboard
1. Check timestamped backups in `./grafana/dashboards-backup-*/`
2. Copy the desired version back to `./grafana/dashboards/`
3. Restart Grafana to reload

---

## 🔄 Alternative: File-Based Persistence (Advanced)

If you want TRUE bidirectional sync (UI changes → JSON files automatically), you would need to:

1. **Remove read-only mount**:
   ```yaml
   - ./grafana/dashboards:/var/lib/grafana/dashboards  # Remove :ro
   ```

2. **Disable dashboard provisioning**, use file-based storage
3. **Configure Grafana** to save directly to files

⚠️ **Not recommended** because:
- Grafana writes messy JSON (not formatted)
- Difficult to track changes in git
- Can cause permission issues
- Provisioning system is better for version control

---

## 📝 Summary

| Component | Persistence | Git-Tracked | Action Required |
|-----------|------------|-------------|-----------------|
| Node-RED Flows | ✅ Auto | ✅ Yes | None - just `git add` |
| Grafana Dashboards | ⚠️ Manual | ✅ Yes | Run backup script before commit |
| Grafana Settings | ❌ Volume | ❌ No | Not critical (users, datasources) |
| Database | ❌ Volume | ❌ No | Use `pg_dump` for backups |

**Golden Rule**: Always run `./scripts/backup-grafana-dashboards.sh` before `git commit` if you made Grafana changes!
