# ENMS Protection System
**Comprehensive guide to protecting ENMS from overload and abuse**

Date: October 2025
Status: Production Ready

---

## 🛡️ Protection Layers

### Layer 1: Rate Limiting (Application Level)
**What it does:** Limits requests per minute per IP and endpoint
**Where:** FastAPI middleware in analytics service
**Status:** ✅ Ready to deploy

### Layer 2: Connection Throttling
**What it does:** Limits concurrent connections to prevent exhaustion
**Where:** FastAPI middleware in analytics service  
**Status:** ✅ Ready to deploy

### Layer 3: Nginx Rate Limiting (Edge Level)
**What it does:** Blocks excessive requests before they reach the application
**Where:** Nginx reverse proxy
**Status:** ✅ Ready to deploy

---

## 📊 Rate Limit Configuration

### Application Level Limits (Per Minute)

| Endpoint Category | Limit | Examples |
|------------------|-------|----------|
| **Critical** | 100 req/min | `/health`, authentication |
| **Normal** | 60 req/min | `/ovos/summary`, `/machines`, `/anomaly/recent` |
| **Heavy** | 20 req/min | `/forecast`, `/baseline/train`, ML operations |
| **Default** | 30 req/min | Uncategorized endpoints |
| **Global per IP** | 120 req/min | Total across all endpoints |

### Connection Limits

- **Per IP:** 10 concurrent connections
- **Total:** 100 concurrent connections
- **Prevents:** Connection exhaustion attacks

### Nginx Limits (Edge Protection)

- **Burst:** 20 requests allowed in burst
- **Rate:** 10 req/second sustained
- **Connection limit:** 20 per IP

---

## 🚀 Quick Start

### 1. Enable Protection (Already Done!)

The protection system is **already implemented** and ready to use. To activate:

```bash
# Restart analytics service to load new middleware
docker-compose restart analytics

# Check that it's working
curl http://localhost:8001/api/v1/health
# Look for X-RateLimit-* headers in response
```

### 2. Test Rate Limiting

```bash
# Test endpoint rate limit (try 70 times - should fail after 60)
for i in {1..70}; do
  curl -s http://localhost:8001/api/v1/ovos/summary | jq '.error'
  sleep 0.1
done

# You should see "rate_limit_exceeded" after 60 requests
```

### 3. Monitor Rate Limits

```bash
# Check rate limit headers
curl -I http://localhost:8001/api/v1/ovos/summary

# Look for:
# X-RateLimit-Limit: 60
# X-RateLimit-Remaining: 59
# X-RateLimit-Reset: 60
```

---

## 🔧 Configuration

### Adjust Rate Limits

Edit `/home/ubuntu/enms/analytics/middleware/rate_limiter.py`:

```python
# Change limits (line ~44)
self.limits = {
    "critical": 100,   # Increase if needed
    "normal": 60,      # Standard OVOS queries
    "heavy": 20,       # ML operations
    "default": 30
}

# Change global limit (line ~59)
self.global_limit = 120  # Total per IP per minute
```

### Whitelist IPs

Add trusted IPs that bypass rate limiting:

```python
# In rate_limiter.py (line ~62)
self.whitelist = [
    "127.0.0.1",
    "localhost",
    "::1",
    "10.33.10.109",  # Add your trusted IPs
]
```

### Disable Protection (Emergency)

```python
# In rate_limiter.py (line ~70)
self.enabled = False  # Temporarily disable
```

---

## 📈 Monitoring Protected System

### 1. Check Current Limits

```bash
# See rate limit status in response headers
curl -v http://localhost:8001/api/v1/ovos/summary 2>&1 | grep RateLimit

# Output:
# < X-RateLimit-Limit: 60
# < X-RateLimit-Remaining: 58
# < X-RateLimit-Reset: 60
```

### 2. Monitor Rate Limit Events

```bash
# Watch for rate limiting in logs
docker logs enms-analytics -f | grep "Rate limit exceeded"

# Watch for connection throttling
docker logs enms-analytics -f | grep "Connection throttled"
```

### 3. Redis Monitoring

```bash
# Check rate limit keys in Redis
docker exec -it enms-redis redis-cli -a ${REDIS_PASSWORD}

# List all rate limit keys
KEYS ratelimit:*

# Check specific IP's usage
GET ratelimit:global:192.168.1.100

# Check endpoint-specific usage
GET ratelimit:normal:192.168.1.100:*
```

### 4. Connection Statistics

The system tracks connection stats. Access via new endpoint (after update):

```bash
curl http://localhost:8001/api/v1/stats/connections
```

---

## 🚨 Common Scenarios

### Scenario 1: Burak's OVOS Making Too Many Requests

**Problem:** OVOS queries too frequently, hitting rate limits

**Detection:**
```bash
docker logs enms-analytics | grep "Rate limit exceeded" | tail -20
```

**Solutions:**

1. **Whitelist Burak's IP:**
   ```python
   self.whitelist = [
       "127.0.0.1",
       "192.168.x.x",  # Burak's OVOS server IP
   ]
   ```

2. **Increase OVOS endpoint limits:**
   ```python
   self.limits = {
       "normal": 120,  # Increase from 60 to 120
   }
   ```

3. **Ask Burak to implement caching** in OVOS

### Scenario 2: System Under DDoS Attack

**Problem:** Massive requests from multiple IPs

**Detection:**
```bash
# Check request rate
./monitoring/monitor-request-rate.sh 60

# If > 500 req/min, likely attack
```

**Solutions:**

1. **Nginx already blocks most attacks** (10 req/sec limit)

2. **Check if attacks getting through:**
   ```bash
   docker logs enms-nginx | grep "limiting requests"
   ```

3. **Temporarily tighten limits:**
   ```python
   self.global_limit = 30  # Reduce from 120
   self.limits["normal"] = 20  # Reduce from 60
   ```

4. **Block specific IPs in nginx:**
   ```nginx
   # Add to /home/ubuntu/enms/nginx/conf.d/analytics.conf
   deny 1.2.3.4;  # Attacker IP
   ```

### Scenario 3: Legitimate Spike (Factory Event)

**Problem:** Legitimate high traffic (e.g., shift change, emergency)

**Detection:**
```bash
# Check if errors are legitimate
curl http://localhost:8001/api/v1/ovos/summary

# Response: {"error": "rate_limit_exceeded", "retry_after": 60}
```

**Solutions:**

1. **Temporarily disable rate limiting:**
   ```bash
   # SSH to server
   cd /home/ubuntu/enms/analytics/middleware
   
   # Edit rate_limiter.py
   # Change: self.enabled = False
   
   # Restart
   docker-compose restart analytics
   ```

2. **Or increase limits temporarily:**
   ```python
   self.global_limit = 300
   self.limits["normal"] = 150
   ```

3. **Re-enable after spike:**
   Remember to revert changes and restart!

### Scenario 4: System Crashing Under Load

**Problem:** Analytics service keeps crashing

**Detection:**
```bash
docker ps | grep enms-analytics
# If constantly restarting...

docker logs enms-analytics --tail 100
# Look for: OOM, connection errors, timeout errors
```

**Solutions:**

1. **Check connection throttling is working:**
   ```bash
   docker logs enms-analytics | grep "Connection throttled"
   ```

2. **Reduce connection limits:**
   ```python
   # In ConnectionThrottle (line ~210)
   max_connections_per_ip=5,   # Reduce from 10
   max_total_connections=50    # Reduce from 100
   ```

3. **Increase Docker memory:**
   ```yaml
   # In docker-compose.yml
   analytics:
     deploy:
       resources:
         limits:
           memory: 2G  # Increase from 1G
   ```

4. **Scale horizontally:**
   ```bash
   docker-compose up -d --scale analytics=2
   ```

---

## 🔍 Testing Protection

### Test 1: Rate Limit Test

```bash
#!/bin/bash
# Test rate limiting

echo "Testing rate limit (60 req/min for normal endpoints)..."

success=0
failed=0

for i in {1..70}; do
  response=$(curl -s -w "%{http_code}" http://localhost:8001/api/v1/ovos/summary)
  code="${response: -3}"
  
  if [ "$code" == "200" ]; then
    success=$((success + 1))
  elif [ "$code" == "429" ]; then
    failed=$((failed + 1))
    echo "Rate limited at request #$i"
  fi
  
  sleep 0.1
done

echo "Success: $success, Rate Limited: $failed"
echo "Expected: ~60 success, ~10 rate limited"
```

### Test 2: Connection Limit Test

```bash
#!/bin/bash
# Test connection throttling

echo "Testing connection limits (10 per IP)..."

# Start 15 concurrent connections
for i in {1..15}; do
  curl -s http://localhost:8001/api/v1/ovos/summary &
done

wait

# Check logs for throttling
docker logs enms-analytics 2>&1 | grep "Connection throttled" | tail -5
```

### Test 3: Load Test with Apache Bench

```bash
# Install apache bench
sudo apt-get install -y apache2-utils

# Test with 100 concurrent connections, 1000 requests
ab -n 1000 -c 100 http://localhost:8001/api/v1/health

# Expected:
# - Most requests succeed
# - Some get 429 (rate limited)
# - Some get 503 (connection throttled)
# - System stays stable
```

---

## 📝 Response Codes

| Code | Meaning | Cause | Action |
|------|---------|-------|--------|
| **200** | Success | Request processed | Continue |
| **429** | Too Many Requests | Rate limit exceeded | Wait 60 seconds |
| **503** | Service Unavailable | Connection limit reached | Retry in 30 seconds |
| **500** | Internal Error | Application crash | Check logs |

### Rate Limited Response Example

```json
{
  "success": false,
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please try again in 60 seconds.",
  "category": "normal",
  "limit": 60,
  "retry_after": 60
}
```

### Connection Throttled Response Example

```json
{
  "success": false,
  "error": "too_many_connections",
  "message": "Server is at capacity. Please try again later.",
  "retry_after": 30
}
```

---

## 🎯 Best Practices

### For Burak (OVOS Integration)

1. **Implement caching** - Don't query same data repeatedly
2. **Respect Retry-After** headers
3. **Handle 429 errors** gracefully
4. **Use summary endpoints** instead of detailed queries when possible
5. **Batch requests** instead of making many individual calls

### For System Administrators

1. **Monitor rate limit events** daily
2. **Whitelist known IPs** (Burak's OVOS, internal systems)
3. **Adjust limits** based on actual usage patterns
4. **Keep monitoring logs** for attack patterns
5. **Test protection** after any changes

### For Production

1. **Never disable protection** in production
2. **Use nginx limits** as first line of defense
3. **Application limits** as second layer
4. **Always log rate limit events**
5. **Alert on sustained high rates** (via monitoring)

---

## 📚 Additional Resources

### Related Files
- **Middleware:** `/home/ubuntu/enms/analytics/middleware/rate_limiter.py`
- **Main app:** `/home/ubuntu/enms/analytics/main.py`
- **Nginx config:** `/home/ubuntu/enms/nginx/conf.d/analytics.conf`
- **Monitoring:** `/home/ubuntu/enms/monitoring/`

### Useful Commands

```bash
# Restart with new protection
docker-compose restart analytics

# Check if protection is active
curl -I http://localhost:8001/api/v1/health | grep RateLimit

# Monitor rate limiting
docker logs enms-analytics -f | grep -E "Rate limit|Connection throttled"

# Check Redis keys
docker exec -it enms-redis redis-cli -a $REDIS_PASSWORD KEYS "ratelimit:*"

# Clear all rate limits (emergency)
docker exec -it enms-redis redis-cli -a $REDIS_PASSWORD FLUSHDB
```

---

## ⚡ Quick Reference

| Action | Command |
|--------|---------|
| Enable protection | Already enabled! Just restart |
| Test rate limit | `for i in {1..70}; do curl localhost:8001/api/v1/health; done` |
| Check headers | `curl -I localhost:8001/api/v1/health` |
| View events | `docker logs enms-analytics \| grep "Rate limit"` |
| Clear limits | `docker exec enms-redis redis-cli -a $REDIS_PASSWORD FLUSHDB` |
| Whitelist IP | Edit `rate_limiter.py` -> add to `self.whitelist` |
| Adjust limits | Edit `rate_limiter.py` -> modify `self.limits` |
| Disable (emergency) | Set `self.enabled = False` in `rate_limiter.py` |

---

## 🆘 Emergency Procedures

### If System is Down

1. **Check if rate limiting caused it:**
   ```bash
   docker logs enms-analytics --tail 100 | grep -E "error|Error|ERROR"
   ```

2. **Temporarily disable protection:**
   ```bash
   # Quick disable (requires code edit + restart)
   # OR use bypass:
   curl -H "X-Internal-Request: true" http://localhost:8001/api/v1/health
   ```

3. **Clear all rate limits:**
   ```bash
   docker exec -it enms-redis redis-cli -a $REDIS_PASSWORD FLUSHDB
   ```

### If Attack is Ongoing

1. **Block at nginx level** (faster):
   ```nginx
   # Add to nginx config
   deny 1.2.3.4;
   ```

2. **Tighten all limits** immediately:
   ```python
   self.global_limit = 20
   self.limits = {"critical": 50, "normal": 10, "heavy": 5, "default": 10}
   ```

3. **Enable fail2ban** (if available) to auto-block

---

**Created:** October 2025  
**Version:** 1.0  
**Status:** Production Ready ✅
