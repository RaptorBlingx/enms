# Grafana Dashboard Management

## 📋 Overview

This directory contains **provisioned Grafana dashboards** that are loaded automatically when Grafana starts. These JSON files are the source of truth for your dashboard configurations.

## ⚠️ IMPORTANT: Dashboard Persistence

### The Problem

When you edit dashboards in the Grafana UI:
- Changes are saved to Grafana's internal database (Docker volume)
- Changes are **NOT automatically saved** to these JSON files
- Without manual export, changes will be lost when containers are recreated

### The Solution

**Before committing to git, always run:**

```bash
./scripts/backup-grafana-dashboards.sh
```

This script:
1. Connects to the running Grafana API
2. Exports all dashboards to `./grafana/dashboards/*.json`
3. Creates a timestamped backup in `./grafana/dashboards-backup-YYYYMMDD-HHMMSS/`

### Workflow

```bash
# 1. Make changes in Grafana UI
#    http://localhost:3000

# 2. Export dashboards
./scripts/backup-grafana-dashboards.sh

# 3. Review changes
git diff grafana/dashboards/

# 4. Commit to git
git add grafana/dashboards/*.json
git commit -m "Update dashboards: add new panel to Energy Analysis"
git push
```

## 📁 Directory Structure

```
grafana/
├── dashboards/                  # Source of truth - loaded on startup
│   ├── enms-energy-analysis.json
│   ├── enms-factory-overview.json
│   └── enms-machine-monitoring.json
├── dashboards-backup/           # Rotating backups (max 3 kept, gitignored)
│   ├── 20251011-120000/
│   ├── 20251011-121000/
│   └── 20251011-122000/
├── provisioning/
│   ├── dashboards/
│   │   └── dashboards.yaml      # Dashboard provisioning config
│   └── datasources/
│       └── timescaledb.yaml     # TimescaleDB datasource config
└── README.md                    # This file
```

## 🔄 Dashboard Provisioning

Dashboards are provisioned automatically using `dashboards.yaml`:

```yaml
allowUiUpdates: true    # Allow editing in UI
disableDeletion: false  # Allow deletion
updateIntervalSeconds: 10  # Reload from files every 10s
```

**What this means:**
- ✅ You can edit dashboards in the UI
- ✅ Changes take effect immediately
- ⚠️ But changes only persist in Docker volume, not in git
- ✅ Running the backup script saves to git-tracked JSON files

## 🎨 Creating New Dashboards

### Method 1: Create in UI (Recommended for Complex Dashboards)

```bash
# 1. Create dashboard in Grafana UI
# 2. Save with a UID like 'enms-new-dashboard'
# 3. Export to JSON files
./scripts/backup-grafana-dashboards.sh
# 4. Commit to git
git add grafana/dashboards/enms-new-dashboard.json
git commit -m "Add new dashboard: System Overview"
```

### Method 2: Create JSON Directly (For Simple Dashboards)

```bash
# 1. Copy an existing dashboard
cp grafana/dashboards/enms-energy-analysis.json grafana/dashboards/enms-custom.json

# 2. Edit JSON (change title, uid, panels)
nano grafana/dashboards/enms-custom.json

# 3. Restart Grafana to load
docker compose restart grafana

# 4. Commit to git
git add grafana/dashboards/enms-custom.json
git commit -m "Add custom dashboard"
```

## 🔐 Dashboard UIDs

Each dashboard must have a unique `uid` field:

- `enms-energy-analysis` - Energy consumption analysis
- `enms-factory-overview` - Factory-wide overview
- `enms-machine-monitoring` - Individual machine monitoring

**When creating new dashboards, use the pattern:** `enms-<descriptive-name>`

## 🚨 Recovery Scenarios

### Lost Changes (Forgot to Export)

**Don't worry!** Auto-backup runs every 10 minutes, so you have:

1. **Recent backup:** Check `grafana/dashboards-backup/` for last 3 exports
2. **Git history:** Check previous commits with `git log grafana/dashboards/`
3. **Docker volume:** If still exists, restart and export

```bash
# Check recent backups (last 3 kept automatically)
ls -lt grafana/dashboards-backup/

# Restore from specific backup
cp grafana/dashboards-backup/20251011-120000/*.json grafana/dashboards/
```

**If volume was deleted (`docker compose down -v`):**
- No problem! Auto-backup has your last 3 exports
- Git has full history of all changes

### Accidental Dashboard Deletion in UI

```bash
# Restart Grafana to reload from JSON files
docker compose restart grafana
```

## 🤖 Automation

### ✨ Automatic Exports (Pre-Configured!)

**Automatic backup is already set up!** Dashboards are exported every 10 minutes using systemd timers.

**Status and Control:**

```bash
# Check if auto-backup is running
sudo systemctl status grafana-backup.timer

# View backup logs
tail -f logs/grafana-backup.log

# Run backup manually (optional)
sudo systemctl start grafana-backup.service

# Disable auto-backup (not recommended)
sudo systemctl stop grafana-backup.timer
sudo systemctl disable grafana-backup.timer
```

**Setup on New Systems:**

```bash
# Install and enable auto-backup
sudo ./scripts/setup-grafana-auto-backup.sh
```

### Pre-Commit Hook

Create `.git/hooks/pre-commit` to remind you:

```bash
#!/bin/bash
echo "⚠️  REMINDER: Have you exported Grafana dashboards?"
echo "   Run: ./scripts/backup-grafana-dashboards.sh"
echo ""
read -p "Continue with commit? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi
```

## 📚 Further Reading

- [Grafana Dashboard Provisioning Docs](https://grafana.com/docs/grafana/latest/administration/provisioning/#dashboards)
- [Dashboard JSON Model](https://grafana.com/docs/grafana/latest/dashboards/json-model/)
- [Complete Persistence Guide](../docs/GRAFANA-PERSISTENCE.md)

## 🆘 Troubleshooting

### Dashboard Changes Not Appearing

```bash
# Check if Grafana is running
docker compose ps grafana

# Check Grafana logs
docker compose logs grafana --tail=50

# Verify provisioning configuration
cat grafana/provisioning/dashboards/dashboards.yaml
```

### Backup Script Fails

```bash
# Check Grafana is accessible
curl -f http://localhost:3001/api/health

# Test API authentication
curl -u "username:password" http://localhost:3001/api/search

# Check .env credentials
grep GRAFANA_ADMIN .env
```

### Dashboards Load as "Provisioned" (Read-Only)

Check `dashboards.yaml`:
- `allowUiUpdates: true` should be set
- Restart Grafana after changing this

---

**Remember:** When in doubt, export! The backup script is safe to run multiple times.
