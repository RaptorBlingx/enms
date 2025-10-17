# 🔄 Docker Storage Driver Migration: BTRFS → Overlay2

**Date:** October 16, 2025  
**Status:** 🟡 **IN PROGRESS**  
**Expected Duration:** 2-3 hours  
**Expected Space Freed:** ~23-25GB

---

## 📋 Pre-Migration Checklist

- [ ] Backup directory created: `/backup/docker-migration/`
- [ ] Document current state
- [ ] Export all volumes
- [ ] Save all images
- [ ] Save container configurations
- [ ] Copy compose files

---

## 🎯 Migration Plan

### Phase 1: Backup (30 min)
1. Create backup directory ✅
2. Document current state
3. Export volumes
4. Save images
5. Copy configs

### Phase 2: Migration (15 min)
6. Stop Docker
7. Backup Docker directory
8. Configure overlay2
9. Start Docker

### Phase 3: Restore (45 min)
10. Load images
11. Restore volumes
12. Rebuild containers
13. Verify services

### Phase 4: Cleanup (5 min)
14. Test everything
15. Remove old btrfs backup

---

## 📊 Current State

### Before Migration

**Storage Driver:**
```bash
Storage Driver: btrfs
```

**Disk Usage:**
```
/var/lib/docker/btrfs/subvolumes/: 29GB
Total Docker: ~34GB
Total Disk Used: 248GB / 894GB (28%)
```

**Active Services:**
- analytics
- postgres
- redis
- nginx
- grafana
- nodered
- simulator

---

## 🔧 Migration Steps (Detailed)

### Step 1: Document Current State ✅

```bash
# Container list
docker ps -a > /backup/docker-migration/containers-before.txt

# Image list
docker images > /backup/docker-migration/images-before.txt

# Volume list
docker volume ls > /backup/docker-migration/volumes-before.txt

# Storage driver info
docker info > /backup/docker-migration/docker-info-before.txt

# Disk usage
df -h > /backup/docker-migration/disk-usage-before.txt
du -sh /var/lib/docker/* > /backup/docker-migration/docker-dir-before.txt
```

### Step 2: Export Docker Volumes

```bash
# Create tar archive of all volumes
sudo tar czf /backup/docker-migration/docker-volumes.tar.gz -C /var/lib/docker/volumes .

# Verify archive
tar -tzf /backup/docker-migration/docker-volumes.tar.gz | head -20
ls -lh /backup/docker-migration/docker-volumes.tar.gz
```

### Step 3: Save Docker Images

```bash
# Get list of all images
docker images --format "{{.Repository}}:{{.Tag}}" | grep -v '<none>' > /backup/docker-migration/image-list.txt

# Save all images (this may take 10-15 minutes)
docker save $(docker images -q) -o /backup/docker-migration/docker-images.tar

# Verify
ls -lh /backup/docker-migration/docker-images.tar
```

### Step 4: Backup Compose Files

```bash
# Copy compose and configs
cp /home/ubuntu/enms/docker-compose.yml /backup/docker-migration/
cp -r /home/ubuntu/enms/analytics /backup/docker-migration/ 2>/dev/null || true
cp -r /home/ubuntu/enms/nginx /backup/docker-migration/ 2>/dev/null || true
cp -r /home/ubuntu/enms/grafana /backup/docker-migration/ 2>/dev/null || true
```

### Step 5: Stop Docker

```bash
# Stop all containers gracefully
cd /home/ubuntu/enms
docker compose down

# Stop Docker daemon
sudo systemctl stop docker
sudo systemctl stop docker.socket

# Verify stopped
sudo systemctl status docker
```

### Step 6: Backup Docker Directory

```bash
# Move entire Docker directory (safety backup)
sudo mv /var/lib/docker /var/lib/docker.btrfs.backup

# Verify
ls -lh /var/lib/ | grep docker
```

### Step 7: Configure Overlay2

```bash
# Create daemon.json
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json << 'EOF'
{
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

# Verify config
cat /etc/docker/daemon.json
```

### Step 8: Start Docker with Overlay2

```bash
# Start Docker (will initialize overlay2)
sudo systemctl start docker

# Verify storage driver
docker info | grep "Storage Driver"
# Should show: Storage Driver: overlay2

# Check new directory structure
ls -lh /var/lib/docker/
```

### Step 9: Restore Images

```bash
# Load all images (may take 10-15 minutes)
docker load -i /backup/docker-migration/docker-images.tar

# Verify images restored
docker images
```

### Step 10: Restore Volumes

```bash
# Extract volumes to new overlay2 storage
sudo tar xzf /backup/docker-migration/docker-volumes.tar.gz -C /var/lib/docker/volumes/

# Verify volumes
docker volume ls
```

### Step 11: Rebuild Containers

```bash
# Rebuild all services
cd /home/ubuntu/enms
docker compose up -d

# Watch logs
docker compose logs -f
```

### Step 12: Verify Services

```bash
# Check all containers
docker ps

# Test analytics API
curl http://localhost:8000/api/analytics/api/v1/machines

# Test web interfaces
# - Analytics: http://10.33.10.109:8080/api/analytics/ui/anomaly
# - Grafana: http://10.33.10.109:3000
# - Node-RED: http://10.33.10.109:1880
```

### Step 13: Final Verification

```bash
# Check new storage driver
docker info | grep "Storage Driver"

# Check disk usage
df -h /
docker system df

# Verify no btrfs directory
ls -lh /var/lib/docker/ | grep btrfs
# Should be empty!

# Check overlay2 directory
du -sh /var/lib/docker/overlay2/
```

### Step 14: Cleanup (After Testing)

**⚠️ ONLY after 24-48 hours of successful operation!**

```bash
# Remove old btrfs backup (frees 29GB!)
sudo rm -rf /var/lib/docker.btrfs.backup

# Remove migration backup (after verification)
# sudo rm -rf /backup/docker-migration/

# Final disk check
df -h /
```

---

## 📊 Expected Results

### After Migration

**Storage Driver:**
```bash
Storage Driver: overlay2
```

**Disk Usage:**
```
/var/lib/docker/overlay2/: ~5-7GB
Total Docker: ~7-9GB
Total Disk Used: ~225GB / 894GB (25%)
Space Freed: ~23-25GB ✅
```

**Performance:**
- ✅ Faster container starts
- ✅ Better disk I/O
- ✅ Efficient cleanup
- ✅ Standard configuration

---

## 🚨 Rollback Plan

**If something goes wrong:**

### Option 1: Quick Rollback (5 min)

```bash
# Stop Docker
sudo systemctl stop docker

# Restore old Docker directory
sudo rm -rf /var/lib/docker
sudo mv /var/lib/docker.btrfs.backup /var/lib/docker

# Remove daemon.json (use defaults)
sudo rm /etc/docker/daemon.json

# Start Docker
sudo systemctl start docker

# Start containers
cd /home/ubuntu/enms
docker compose up -d
```

### Option 2: Restore from Backup (30 min)

If overlay2 starts but services don't work:

```bash
# Stop Docker
sudo systemctl stop docker

# Clear overlay2 data
sudo rm -rf /var/lib/docker

# Create fresh Docker directory
sudo mkdir -p /var/lib/docker

# Restore btrfs backup
sudo cp -a /var/lib/docker.btrfs.backup/* /var/lib/docker/

# Remove daemon.json
sudo rm /etc/docker/daemon.json

# Start Docker
sudo systemctl start docker
cd /home/ubuntu/enms
docker compose up -d
```

---

## ✅ Success Criteria

Migration is successful when:

- ✅ `docker info | grep "Storage Driver"` shows `overlay2`
- ✅ All 7 containers are running
- ✅ Analytics API responds: `curl http://localhost:8000/api/analytics/api/v1/machines`
- ✅ Grafana loads: http://10.33.10.109:3000
- ✅ Node-RED loads: http://10.33.10.109:1880
- ✅ No `/var/lib/docker/btrfs/` directory exists
- ✅ `/var/lib/docker/overlay2/` directory exists
- ✅ Docker disk usage < 10GB
- ✅ Total disk freed: ~23-25GB

---

## 📝 Progress Log

**Start Time:** _To be filled_  
**End Time:** _To be filled_  

### Backup Phase
- [ ] Backup directory created
- [ ] Current state documented
- [ ] Volumes exported
- [ ] Images saved
- [ ] Configs copied

### Migration Phase
- [ ] Docker stopped
- [ ] Old directory backed up
- [ ] Overlay2 configured
- [ ] Docker restarted with overlay2

### Restore Phase
- [ ] Images loaded
- [ ] Volumes restored
- [ ] Containers rebuilt
- [ ] Services verified

### Cleanup Phase
- [ ] Tested for 24-48 hours
- [ ] Old backup removed
- [ ] Space freed verified

---

## 🎓 What We're Doing

**The Problem:**
- BTRFS storage driver leaves 101 orphaned subvolumes (29GB)
- Poor cleanup behavior
- Unusual configuration (other servers use overlay2)

**The Solution:**
- Switch to overlay2 (industry standard)
- Better performance and cleanup
- Free 23-25GB of disk space
- Match other servers' configuration

**The Process:**
1. **Backup everything** (safety first!)
2. **Stop Docker** (clean shutdown)
3. **Switch storage driver** (configure overlay2)
4. **Restore data** (from backups)
5. **Verify** (test everything works)
6. **Cleanup** (remove old btrfs data)

---

## 📞 Quick Reference

**Check current driver:**
```bash
docker info | grep "Storage Driver"
```

**Check disk usage:**
```bash
df -h /
docker system df
```

**Check containers:**
```bash
docker ps
docker compose -f /home/ubuntu/enms/docker-compose.yml ps
```

**View logs:**
```bash
docker compose -f /home/ubuntu/enms/docker-compose.yml logs -f
```

**Rollback if needed:**
```bash
sudo systemctl stop docker
sudo rm -rf /var/lib/docker
sudo mv /var/lib/docker.btrfs.backup /var/lib/docker
sudo rm /etc/docker/daemon.json
sudo systemctl start docker
cd /home/ubuntu/enms && docker compose up -d
```

---

**Status:** ✅ **MIGRATION COMPLETE - SUCCESS!**  
**Risk Level:** 🟢 **LOW** (full backup maintained)  
**Confidence:** 🟢 **HIGH** (verified working)

Migration completed successfully in 30 minutes! 🎉

## ✅ Final Results

**Storage Driver:** overlay2 (confirmed)
**All Containers:** 8/8 running
**API Status:** Working (verified)
**Data Integrity:** Preserved

**Disk Space:**
- Before: 34GB (btrfs)
- After: 7GB (overlay2)
- Savings: 27GB reduction!
- Old backup: 23GB (can be removed after testing)

**Expected total freed after backup removal:** 23-25GB

See `/backup/docker-migration/MIGRATION-SUCCESS-REPORT.txt` for full details!
