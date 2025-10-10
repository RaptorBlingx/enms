# Node-RED Flow Persistence Guide

## ✅ **Problem Solved**

Previously, any changes you made in the Node-RED UI were lost when the container was rebuilt or restarted. Now, all changes are automatically saved to the repository!

## 📁 **How It Works**

### **Before (Flows copied during build)**
```dockerfile
# Flows were copied during Docker build
COPY flows/enms-data-pipeline.json /data/flows.json
```
❌ Changes in Node-RED UI → Lost on container restart

### **After (Flows mounted as volume)**
```yaml
volumes:
  - ./nodered/flows.json:/data/flows.json
  - ./nodered/flows_cred.json:/data/flows_cred.json
```
✅ Changes in Node-RED UI → Automatically saved to repository

## 🔄 **Workflow**

### **Making Changes**
1. Open Node-RED at `http://<server_ip>:1881`
2. Add/edit/delete nodes, flows, or configurations
3. Click **Deploy** button
4. Changes are **automatically saved** to `/home/ubuntu/enms/nodered/flows.json`

### **Version Control**
```bash
# Check what changed
cd /home/ubuntu/enms
git status
git diff nodered/flows.json

# Commit your changes
git add nodered/flows.json
git commit -m "Added MQTT to PostgreSQL data pipeline"
git push origin main
```

### **Cloning on Another Machine**
```bash
# Clone the repository
git clone https://github.com/raptorblingx/enms.git
cd enms

# Start the containers
docker compose up -d

# All your flows are already there! 🎉
# Open http://<new-server-ip>:1881
```

## 📂 **File Structure**

```
nodered/
├── flows.json              ← Your flows (TRACKED by Git)
├── flows_cred.json         ← Credentials (NOT tracked - security)
├── package.json            ← Node-RED dependencies
├── Dockerfile              ← Container build instructions
└── .gitignore             ← Excludes sensitive files
```

## 🔒 **Security**

### **flows_cred.json is NOT committed**
This file contains encrypted passwords and tokens. It's excluded in `.gitignore`:

```gitignore
# Node-RED credentials file (contains passwords and sensitive data)
# DO NOT commit this file to Git
flows_cred.json
```

### **What this means:**
- ✅ `flows.json` → Safe to commit (no passwords)
- ❌ `flows_cred.json` → Never commit (contains secrets)
- 🔐 On new machines, you'll need to re-enter credentials in Node-RED nodes

## 🧪 **Testing It Works**

### **Test 1: Make a change**
```bash
# 1. Open Node-RED at http://<server_ip>:1881
# 2. Add a new comment node or debug node
# 3. Click Deploy
# 4. Check the file changed:
cd /home/ubuntu/enms
git diff nodered/flows.json
```

### **Test 2: Restart container**
```bash
# Restart Node-RED
docker compose restart nodered

# Open http://<server_ip>:1881
# Your changes are still there! ✅
```

### **Test 3: Rebuild container**
```bash
# Completely rebuild
docker compose down
docker compose build nodered
docker compose up -d

# Open http://<server_ip>:1881
# Your changes are STILL there! ✅
```

## 🚀 **Best Practices**

### **1. Commit Regularly**
```bash
# After making significant changes in Node-RED
git add nodered/flows.json
git commit -m "Added new data transformation flow"
git push
```

### **2. Use Meaningful Commit Messages**
```bash
git commit -m "Added MQTT subscriber for factory sensors"
git commit -m "Fixed PostgreSQL connection string"
git commit -m "Added data validation and error handling"
```

### **3. Create Branches for Major Changes**
```bash
# Create a feature branch
git checkout -b feature/add-analytics-pipeline

# Make changes in Node-RED
# Test thoroughly
# Commit when working

git add nodered/flows.json
git commit -m "Implemented analytics data pipeline"
git push origin feature/add-analytics-pipeline

# Create pull request for review
```

### **4. Document Your Flows**
- Use **comment nodes** in Node-RED to document complex logic
- Add descriptions to flows (double-click the flow tab)
- Keep the `flows.json` file readable (it's already prettified)

## 🔧 **Troubleshooting**

### **Q: I made changes but they're not saved**
A: Make sure you clicked the **Deploy** button in Node-RED UI

### **Q: My credentials are gone after cloning**
A: This is normal! Re-enter credentials in Node-RED nodes (MQTT, PostgreSQL, etc.)

### **Q: Can I rename flows.json?**
A: Not recommended. Node-RED expects this default name. If needed, update:
```yaml
environment:
  - FLOWS=my-custom-name.json
```

### **Q: How do I backup my credentials?**
A: Copy `flows_cred.json` to a secure location (NOT Git):
```bash
# Backup
cp nodered/flows_cred.json ~/secure-backup/

# Restore on new machine
cp ~/secure-backup/flows_cred.json nodered/
docker compose restart nodered
```

## 📋 **Summary**

| Action | Result |
|--------|--------|
| Edit flows in Node-RED UI | ✅ Saved to `flows.json` automatically |
| Deploy changes | ✅ Written to host filesystem |
| Restart container | ✅ Changes persist |
| Rebuild container | ✅ Changes persist |
| Commit to Git | ✅ Share with team |
| Clone on new machine | ✅ Flows automatically loaded |
| Credentials | ⚠️ Must be re-entered (security) |

---

## 🎯 **You Asked For:**
> "I want when I add more nodes, codes, new flows, or whatever, or even delete something. all those changes would be saved. so, I push the docker to the repo, and someone clone the repo, all the new changes must be right there"

**✅ DONE!** Now every change you make in Node-RED is automatically saved and version controlled! 🚀
