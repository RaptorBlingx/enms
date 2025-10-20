# ENMS Monitoring & Alerting Guide

## 📊 How to Monitor Burak's OVOS Requests

### Quick Status Check
```bash
# Check if system is running
docker ps | grep enms

# Check API health
curl http://localhost:8001/api/v1/health

# View recent logs
docker logs enms-analytics --tail 100
```

---

## 🔍 Monitoring Scripts

### 1. System Health Check
**Script:** `monitoring/check-system-health.sh`

**What it checks:**
- ✅ Container status (running/stopped)
- ✅ API health endpoint
- ✅ Database connectivity
- ✅ Request statistics (total, success, errors)
- ✅ Most requested endpoints
- ✅ Recent errors
- ✅ Resource usage (CPU, memory)
- ✅ Disk space

**Usage:**
```bash
# Make executable
chmod +x monitoring/check-system-health.sh

# Run check
./monitoring/check-system-health.sh
```

**Output Example:**
```
📦 Docker Containers Status:
✅ enms-analytics is RUNNING
✅ enms-postgres is RUNNING

🌐 API Health Check:
✅ API is HEALTHY (HTTP 200)

📊 Request Statistics:
Total HTTP Requests: 847
Successful (200): 823
Errors (4xx/5xx): 24
Success Rate: 97.2%

🔥 Top 10 Most Requested Endpoints:
  156 "GET /api/v1/health"
   89 "GET /api/v1/machines"
   67 "GET /api/v1/anomaly/recent"
   45 "GET /api/v1/ovos/summary"
```

---

### 2. Request Rate Monitor
**Script:** `monitoring/monitor-request-rate.sh`

**What it does:**
- Monitors requests over time period
- Calculates requests per minute
- Shows breakdown by endpoint and IP
- Alerts if threshold exceeded

**Usage:**
```bash
# Make executable
chmod +x monitoring/monitor-request-rate.sh

# Monitor for 60 seconds (default)
./monitoring/monitor-request-rate.sh

# Monitor for 5 minutes (300 seconds)
./monitoring/monitor-request-rate.sh 300
```

**Output Example:**
```
📈 ENMS REQUEST RATE MONITOR
Monitoring for 60 seconds...

⏱️  Monitoring Duration: 60s
📊 Total Requests: 145
🚀 Request Rate: 145.0 requests/minute

📍 Endpoint Breakdown:
  /api/v1/health                                       45 requests
  /api/v1/ovos/summary                                 32 requests
  /api/v1/machines                                     28 requests

🌍 Client IPs:
  172.18.0.4            125 requests
  127.0.0.1              20 requests

✅ Request rate is within normal limits
```

---

### 3. Auto-Alert System
**Script:** `monitoring/auto-alert.sh`

**What it monitors:**
- Container health (auto-restart if down)
- API availability
- Database connectivity
- Error rate percentage
- Traffic spikes
- Disk space
- Memory usage

**Alerts on:**
- ❌ CRITICAL: Container down
- ❌ CRITICAL: API not responding
- ❌ CRITICAL: Database down
- ⚠️ WARNING: Error rate > 10%
- ⚠️ WARNING: Traffic > 500 req/min
- ⚠️ WARNING: Disk > 90% full
- ⚠️ WARNING: Memory > 90% used

**Usage:**
```bash
# Make executable
chmod +x monitoring/auto-alert.sh

# Run in background
nohup ./monitoring/auto-alert.sh > /home/ubuntu/enms/logs/monitor.log 2>&1 &

# View alerts
tail -f /home/ubuntu/enms/logs/alerts.log
```

---

## 🚨 Common Issues & Solutions

### Issue 1: Too Many Requests from OVOS
**Symptoms:**
- High CPU usage
- Slow API responses
- Request rate > 500/min

**Check:**
```bash
./monitoring/monitor-request-rate.sh 60
```

**Solutions:**
- Ask Burak to reduce polling frequency
- Implement caching in OVOS
- Add rate limiting to API

### Issue 2: System is Down
**Symptoms:**
- Containers not running
- API returns no response

**Check:**
```bash
docker ps | grep enms
curl http://localhost:8001/api/v1/health
```

**Solutions:**
```bash
# Restart containers
cd /home/ubuntu/enms
docker compose restart

# Check logs for errors
docker logs enms-analytics --tail 100

# If database issue
docker compose restart postgres
```

### Issue 3: High Error Rate
**Symptoms:**
- Many 4xx or 5xx responses
- Errors in logs

**Check:**
```bash
docker logs enms-analytics --tail 200 | grep ERROR
```

**Solutions:**
- Check if Burak is sending invalid data
- Verify database connectivity
- Check disk space: `df -h`

### Issue 4: Database Issues
**Symptoms:**
- "Connection refused" errors
- Timeouts

**Check:**
```bash
docker exec enms-postgres pg_isready -U raptorblingx
```

**Solutions:**
```bash
# Restart database
docker compose restart postgres

# Check database logs
docker logs enms-postgres --tail 100
```

---

## 📈 Manual Monitoring Commands

### View Real-time Logs
```bash
# All logs
docker logs enms-analytics -f

# Only HTTP requests
docker logs enms-analytics -f 2>&1 | grep "HTTP/1.1"

# Only errors
docker logs enms-analytics -f 2>&1 | grep ERROR
```

### Count Requests
```bash
# Total requests in last hour
docker logs enms-analytics --since 1h 2>&1 | grep -c "HTTP/1.1"

# Requests to specific endpoint
docker logs enms-analytics --since 1h 2>&1 | grep -c "/ovos/summary"

# Error count
docker logs enms-analytics --since 1h 2>&1 | grep -c "HTTP/1.1\" [45]"
```

### Check Resource Usage
```bash
# Container stats
docker stats enms-analytics --no-stream

# System resources
top
htop

# Disk space
df -h

# Memory
free -h
```

### Database Queries
```bash
# Connect to database
docker exec -it enms-postgres psql -U raptorblingx -d enms

# Count machines
SELECT COUNT(*) FROM machines;

# Recent readings
SELECT * FROM energy_readings ORDER BY time DESC LIMIT 10;

# Exit
\q
```

---

## 📧 Set Up Email Alerts (Optional)

### Install mail utilities
```bash
sudo apt-get install mailutils
```

### Configure in auto-alert.sh
Edit line 6 to add your email:
```bash
ALERT_EMAIL="your-email@example.com"
```

Uncomment line 91:
```bash
echo -e "$ALERT_MSG" | mail -s "ENMS Alert: $TIMESTAMP" $ALERT_EMAIL
```

---

## 📊 Create Custom Dashboard (Optional)

### Using Grafana
Already installed! Access at: `http://your-server:3000`

**Default credentials:**
- Username: `admin`
- Password: `admin` (change on first login)

**Pre-configured dashboards:**
- ENMS Dashboard (ID: 1)
- Shows real-time metrics
- Request rates
- Error rates
- Resource usage

---

## 🔄 Automated Monitoring with Cron

### Set up hourly health checks
```bash
# Edit crontab
crontab -e

# Add this line (check every hour)
0 * * * * /home/ubuntu/enms/monitoring/check-system-health.sh >> /home/ubuntu/enms/logs/health-check.log 2>&1

# Or check every 15 minutes
*/15 * * * * /home/ubuntu/enms/monitoring/check-system-health.sh >> /home/ubuntu/enms/logs/health-check.log 2>&1
```

### View scheduled checks
```bash
tail -f /home/ubuntu/enms/logs/health-check.log
```

---

## 🎯 Quick Reference

| What to Check | Command |
|---------------|---------|
| System health | `./monitoring/check-system-health.sh` |
| Request rate | `./monitoring/monitor-request-rate.sh 60` |
| Live logs | `docker logs enms-analytics -f` |
| Container status | `docker ps \| grep enms` |
| API health | `curl http://localhost:8001/api/v1/health` |
| Database status | `docker exec enms-postgres pg_isready -U raptorblingx` |
| Recent errors | `docker logs enms-analytics --tail 100 \| grep ERROR` |
| Disk space | `df -h` |
| Memory usage | `free -h` |

---

## 📞 When to Contact Someone

**Contact Burak if:**
- Request rate > 1000/min (too frequent)
- High error rate from his IP
- Strange endpoint access patterns
- Malformed requests

**Investigate yourself if:**
- Container crashes
- Database issues
- Disk full
- High server CPU/memory
- Network issues

---

**Last Updated:** October 20, 2025
