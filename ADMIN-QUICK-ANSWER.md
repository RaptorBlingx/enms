# Quick Answer for Admin

**Question:** "Did you configure btrfs storage driver on purpose?"

---

## Short Answer

**No, it was not configured on purpose.**

Docker automatically selected the btrfs storage driver when it detected this VM's filesystem is btrfs (inherited from your physical server). This is different from your other VMs which likely use ext4/xfs, where Docker automatically selects overlay2.

---

## What Happened

1. **Your physical server uses btrfs** ✓ (confirmed)
2. **This VM inherited btrfs filesystem** (at VM creation time)
3. **Docker installed on this VM** detected btrfs
4. **Docker automatically chose btrfs storage driver** (no manual config)
5. **BTRFS driver created 101 subvolumes** that didn't clean up properly
6. **Result: 29GB of wasted space**

---

## What We Fixed

**Before:**
- Storage Driver: `btrfs` (automatic, no config file)
- Docker Usage: 34GB
- Orphaned data: 29GB in 101 subvolumes
- Directory: `/var/lib/docker/btrfs/`

**After:**
- Storage Driver: `overlay2` (now explicitly configured)
- Docker Usage: 7GB (27GB freed!)
- Orphaned data: Cleaned up
- Directory: `/var/lib/docker/overlay2/`
- Config: `/etc/docker/daemon.json` created

---

## Why Other VMs Don't Have This

**Other VMs:**
```
Filesystem: ext4/xfs → Docker auto-selects: overlay2
Directory: /var/lib/docker/overlay2/
No btrfs directory
```

**This VM (before fix):**
```
Filesystem: btrfs → Docker auto-selected: btrfs
Directory: /var/lib/docker/btrfs/
101 orphaned subvolumes
```

**This VM (after fix):**
```
Filesystem: btrfs (can't change) → Docker now uses: overlay2 (forced)
Directory: /var/lib/docker/overlay2/
Standard config, matches other VMs
```

---

## Volume Driver vs Storage Driver

**Volume Driver** (docker volume ls shows "local"):
- ✅ This was always correct
- ✅ All VMs use "local" volume driver
- ✅ This is standard

**Storage Driver** (docker info shows):
- ❌ Was: `btrfs` (automatic, problematic)
- ✅ Now: `overlay2` (configured, standard)
- ✅ Now matches your other VMs

**The 101 btrfs subvolumes were from the storage driver, not the volume driver.**

---

## Conclusion

**It was automatic, not manual.** Docker selected btrfs storage driver because this VM's filesystem is btrfs. We have now explicitly configured Docker to use overlay2 (standard), which resolves the disk usage issue and matches your other Docker instances.

**Configuration file created:** `/etc/docker/daemon.json`

```json
{
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

**Result:**
- ✅ 27GB Docker space freed
- ✅ Standard configuration (like other VMs)
- ✅ Better performance and cleanup
- ✅ No more btrfs subvolume accumulation

---

**Status:** Issue resolved, VM now standard ✅
