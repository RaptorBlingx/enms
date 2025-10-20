#!/bin/bash

# ENMS System Health & Request Monitoring Script
# Usage: ./check-system-health.sh

echo "============================================"
echo "🔍 ENMS SYSTEM HEALTH CHECK"
echo "============================================"
echo "Date: $(date)"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Check if containers are running
echo "📦 Docker Containers Status:"
echo "-------------------------------------------"
docker ps --filter "name=enms" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | head -10
echo ""

# 2. Check container health
echo "🏥 Container Health:"
echo "-------------------------------------------"
for container in enms-analytics enms-postgres enms-timescaledb; do
    if docker ps | grep -q $container; then
        echo -e "${GREEN}✅ $container is RUNNING${NC}"
    else
        echo -e "${RED}❌ $container is DOWN${NC}"
    fi
done
echo ""

# 3. Check API health endpoint
echo "🌐 API Health Check:"
echo "-------------------------------------------"
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8001/api/v1/health 2>/dev/null)
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ API is HEALTHY (HTTP $HTTP_CODE)${NC}"
    echo "$HEALTH_RESPONSE" | head -n -1 | jq -r '.status, .active_machines, .recent_anomalies' 2>/dev/null
else
    echo -e "${RED}❌ API is DOWN or UNHEALTHY (HTTP $HTTP_CODE)${NC}"
fi
echo ""

# 4. Count recent HTTP requests (last 1000 lines)
echo "📊 Request Statistics (Last 1000 log lines):"
echo "-------------------------------------------"
TOTAL_REQUESTS=$(docker logs enms-analytics --tail 1000 2>&1 | grep -c "HTTP/1.1")
SUCCESS_REQUESTS=$(docker logs enms-analytics --tail 1000 2>&1 | grep -c "200 OK")
ERROR_REQUESTS=$(docker logs enms-analytics --tail 1000 2>&1 | grep -c "HTTP/1.1 [45]")

echo "Total HTTP Requests: $TOTAL_REQUESTS"
echo "Successful (200): $SUCCESS_REQUESTS"
echo "Errors (4xx/5xx): $ERROR_REQUESTS"

if [ $TOTAL_REQUESTS -gt 0 ]; then
    SUCCESS_RATE=$(echo "scale=1; $SUCCESS_REQUESTS * 100 / $TOTAL_REQUESTS" | bc)
    echo "Success Rate: ${SUCCESS_RATE}%"
fi
echo ""

# 5. Most requested endpoints
echo "🔥 Top 10 Most Requested Endpoints:"
echo "-------------------------------------------"
docker logs enms-analytics --tail 1000 2>&1 | \
    grep "HTTP/1.1" | \
    grep -o '"GET [^"]*"' | \
    sort | uniq -c | sort -rn | head -10
echo ""

# 6. Recent errors
echo "⚠️  Recent Errors (Last 20):"
echo "-------------------------------------------"
docker logs enms-analytics --tail 500 2>&1 | \
    grep -E "ERROR|CRITICAL|Exception|error" | \
    tail -20 | \
    sed 's/^/  /'
echo ""

# 7. Database connection
echo "🗄️  Database Status:"
echo "-------------------------------------------"
DB_STATUS=$(docker exec enms-postgres pg_isready -U raptorblingx 2>&1)
if echo "$DB_STATUS" | grep -q "accepting connections"; then
    echo -e "${GREEN}✅ PostgreSQL is ACCEPTING CONNECTIONS${NC}"
else
    echo -e "${RED}❌ PostgreSQL is NOT RESPONDING${NC}"
fi
echo ""

# 8. Resource usage
echo "💻 Resource Usage:"
echo "-------------------------------------------"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep enms
echo ""

# 9. Disk space
echo "💾 Disk Space:"
echo "-------------------------------------------"
df -h | grep -E "Filesystem|/$"
echo ""

# 10. Request timeline (last 5 minutes)
echo "⏰ Request Timeline (Last 5 minutes):"
echo "-------------------------------------------"
FIVE_MIN_AGO=$(date -d '5 minutes ago' '+%Y-%m-%d %H:%M' 2>/dev/null || date -v-5M '+%Y-%m-%d %H:%M')
docker logs enms-analytics --since 5m 2>&1 | \
    grep "HTTP/1.1" | \
    tail -20 | \
    sed 's/^/  /'
echo ""

echo "============================================"
echo "✅ Health check complete!"
echo "============================================"
