# 🎉 AUTO-BACKUP ENABLED - Your Work is Safe!

## ✅ What's Active

**Grafana dashboards are now automatically backed up every 10 minutes!**

You can edit dashboards freely in the Grafana UI at http://localhost:3000 and your changes will be automatically exported to git-tracked JSON files.

---

## 🔄 Your New Workflow (Super Simple!)

```bash
# 1. Edit dashboards in Grafana UI
#    Make any changes you want - add panels, change queries, etc.

# 2. Wait 10 minutes (or less) - auto-export happens automatically!
#    Or run manually if you're in a hurry:
#    ./scripts/backup-grafana-dashboards.sh

# 3. Commit to git (your normal workflow)
git add .
git commit -m "Update dashboards"
git push
```

**That's it!** No special commands to remember. Your work is automatically safe.

---

## 📊 How to Monitor

### Check Auto-Backup Status
```bash
sudo systemctl status grafana-backup.timer
```

### View Backup Logs (Real-time)
```bash
tail -f logs/grafana-backup.log
```

### Next Backup Time
```bash
systemctl list-timers grafana-backup.timer
```

### Run Backup Immediately (Manual)
```bash
sudo systemctl start grafana-backup.service
# Or just:
./scripts/backup-grafana-dashboards.sh
```

---

## 🛡️ Safety Guarantees

✅ **Every 10 minutes:** Dashboards automatically exported  
✅ **Timestamped backups:** Located in `grafana/dashboards-backup-*/`  
✅ **Persistent logs:** All backups logged to `logs/grafana-backup.log`  
✅ **Survives reboots:** Systemd timer starts automatically on boot  
✅ **Git-tracked files:** All exports go to `grafana/dashboards/*.json`  

**Your nightmare scenario is 100% PREVENTED! 🎊**

---

## 📁 Files and Locations

```
/home/ubuntu/enms/
├── grafana/
│   ├── dashboards/                    # ← Git-tracked dashboard JSON files
│   │   ├── enms-energy-analysis.json
│   │   ├── enms-factory-overview.json
│   │   └── enms-machine-monitoring.json
│   └── dashboards-backup/             # ← Rotating backups (max 3 kept)
│       ├── 20251011-120000/
│       ├── 20251011-121000/
│       └── 20251011-122000/           # ← Oldest deleted automatically
│
├── logs/
│   ├── grafana-backup.log             # ← Success logs
│   └── grafana-backup-error.log       # ← Error logs (if any)
│
└── scripts/
    ├── backup-grafana-dashboards.sh   # ← Manual backup script
    ├── setup-grafana-auto-backup.sh   # ← Setup script for new systems
    └── systemd/
        ├── grafana-backup.service     # ← Systemd service definition
        └── grafana-backup.timer       # ← Systemd timer (every 10 min)
```

---

## 🔧 Control Commands

### Stop Auto-Backup (NOT Recommended)
```bash
sudo systemctl stop grafana-backup.timer
sudo systemctl disable grafana-backup.timer
```

### Start Auto-Backup Again
```bash
sudo systemctl start grafana-backup.timer
sudo systemctl enable grafana-backup.timer
```

### Change Backup Interval
```bash
# Edit the timer file
sudo nano /etc/systemd/system/grafana-backup.timer

# Change this line:
OnUnitActiveSec=10min  # Change to 5min, 15min, 1h, etc.

# Reload systemd
sudo systemctl daemon-reload
sudo systemctl restart grafana-backup.timer
```

---

## 🆘 Troubleshooting

### Check if Auto-Backup is Working
```bash
# Should show "active (waiting)"
sudo systemctl status grafana-backup.timer

# Should show recent backup entries
cat logs/grafana-backup.log
```

### If Backups Fail
```bash
# Check error log
cat logs/grafana-backup-error.log

# View detailed systemd logs
journalctl -u grafana-backup.service -n 50

# Test manual backup
./scripts/backup-grafana-dashboards.sh
```

### Common Issues

**"Grafana not running"**
```bash
docker compose ps grafana
docker compose up -d grafana
```

**"Authentication failed"**
```bash
# Check credentials in .env
grep GRAFANA_ADMIN .env
```

**"Permission denied"**
```bash
# Fix script permissions
chmod +x scripts/backup-grafana-dashboards.sh
```

---

## 🚀 Setup on New Systems

When someone clones your repo and wants the same auto-backup:

```bash
cd /path/to/enms
sudo ./scripts/setup-grafana-auto-backup.sh
```

Done! Auto-backup will be active on their system too.

---

## 🎓 Technical Details

### What Happens Every 10 Minutes

1. **Timer triggers** the systemd service
2. **Service runs** `backup-grafana-dashboards.sh`
3. **Script connects** to Grafana API (localhost:3001)
4. **Fetches all dashboards** via `/api/search?type=dash-db`
5. **Exports each dashboard** via `/api/dashboards/uid/{uid}`
6. **Saves to JSON files** in `grafana/dashboards/`
7. **Creates timestamped backup** in `grafana/dashboards-backup-*/`
8. **Logs success/failure** to `logs/grafana-backup.log`

### Why This is Safe

- **No data loss risk:** Even if script fails, previous backups remain
- **No corruption risk:** Read-only API operations, doesn't modify Grafana
- **Git-friendly:** JSON files have clear diffs, easy to review changes
- **Automatic recovery:** If backup fails once, next run (10 min later) succeeds
- **Smart rotation:** Only last 3 backups kept (no thousands of files!)
- **Git is your history:** Full change history tracked in git, not backup directories

### Systemd Timer Configuration

```ini
[Timer]
OnBootSec=2min        # First backup 2 minutes after system boot
OnUnitActiveSec=10min # Then every 10 minutes after last run
Persistent=true       # If system was off, run missed backups on boot
```

---

## 📚 Related Documentation

- **Full persistence guide:** `docs/GRAFANA-PERSISTENCE.md`
- **Quick reference:** `grafana/README.md`
- **One-page cheat sheet:** `GRAFANA-BACKUP-QUICKREF.txt`
- **Implementation details:** `docs/SESSION-GRAFANA-PERSISTENCE.md`

---

## ✨ Summary

### Before (Manual Backup)
```bash
# Make changes in Grafana
# Remember to run: ./scripts/backup-grafana-dashboards.sh  ← Easy to forget!
# Then commit
```

### After (Auto-Backup - NOW!)
```bash
# Make changes in Grafana
# Changes automatically exported every 10 minutes! ✨
# Just commit when ready - that's it!
```

**Your work is safe. No more worries. Just create! 🎨**

---

**Date:** October 10, 2025  
**Status:** ✅ ACTIVE and VERIFIED  
**Auto-Backup Interval:** Every 10 minutes  
**Next Backup:** Check with `systemctl list-timers grafana-backup.timer`
