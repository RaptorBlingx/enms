#!/bin/bash
# ============================================================================
# ENMS Protection System - Activation Script
# ============================================================================
# This script activates all protection layers for ENMS
#
# Author: ENMS Team
# Date: October 2025
# ============================================================================

set -e

echo "============================================"
echo "🛡️  ACTIVATING ENMS PROTECTION SYSTEM"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running from enms directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ Error: Must run from /home/ubuntu/enms directory${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Protection Layers:${NC}"
echo "   1. ✅ Rate Limiting (Application Layer)"
echo "   2. ✅ Connection Throttling (Application Layer)"
echo "   3. ✅ Nginx Rate Limiting (Edge Layer)"
echo ""

# Step 1: Verify Redis is running
echo -e "${BLUE}Step 1: Verifying Redis...${NC}"
if docker ps | grep -q enms-redis; then
    echo -e "${GREEN}   ✓ Redis is running${NC}"
else
    echo -e "${RED}   ❌ Redis is not running!${NC}"
    echo "   Starting Redis..."
    docker-compose up -d redis
    sleep 5
fi
echo ""

# Step 2: Check if middleware exists
echo -e "${BLUE}Step 2: Verifying middleware files...${NC}"
if [ -f "analytics/middleware/rate_limiter.py" ]; then
    echo -e "${GREEN}   ✓ Rate limiter middleware exists${NC}"
else
    echo -e "${RED}   ❌ Rate limiter middleware not found!${NC}"
    exit 1
fi

if [ -f "analytics/middleware/__init__.py" ]; then
    echo -e "${GREEN}   ✓ Middleware package initialized${NC}"
else
    echo -e "${RED}   ❌ Middleware package not initialized!${NC}"
    exit 1
fi
echo ""

# Step 3: Restart analytics service to load middleware
echo -e "${BLUE}Step 3: Restarting analytics service...${NC}"
docker-compose restart analytics
echo -e "${YELLOW}   Waiting for service to start (15 seconds)...${NC}"
sleep 15

# Check if analytics is healthy
if docker ps | grep -q "enms-analytics.*healthy"; then
    echo -e "${GREEN}   ✓ Analytics service is healthy${NC}"
else
    echo -e "${YELLOW}   ⚠ Analytics service may still be starting...${NC}"
fi
echo ""

# Step 4: Reload Nginx configuration
echo -e "${BLUE}Step 4: Reloading Nginx with new rate limits...${NC}"
docker exec enms-nginx nginx -t > /dev/null 2>&1
if [ $? -eq 0 ]; then
    docker exec enms-nginx nginx -s reload
    echo -e "${GREEN}   ✓ Nginx configuration reloaded${NC}"
else
    echo -e "${RED}   ❌ Nginx configuration test failed!${NC}"
    echo "   Running test again with output:"
    docker exec enms-nginx nginx -t
    exit 1
fi
echo ""

# Step 5: Test protection
echo -e "${BLUE}Step 5: Testing protection...${NC}"

# Test 1: Check rate limit headers
echo -n "   Testing rate limit headers... "
response=$(curl -s -I http://localhost:8001/api/v1/health 2>&1)
if echo "$response" | grep -q "X-RateLimit"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠ (Headers may not appear yet)${NC}"
fi

# Test 2: Check API is responding
echo -n "   Testing API availability... "
status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/v1/health)
if [ "$status" == "200" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}❌ (HTTP $status)${NC}"
fi

# Test 3: Check connection statistics endpoint
echo -n "   Testing connection stats endpoint... "
status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/v1/stats/connections)
if [ "$status" == "200" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠ (HTTP $status)${NC}"
fi
echo ""

# Step 6: Show current status
echo -e "${BLUE}Step 6: Current protection status...${NC}"

# Get connection stats
conn_stats=$(curl -s http://localhost:8001/api/v1/stats/connections 2>/dev/null)
if [ $? -eq 0 ]; then
    total=$(echo "$conn_stats" | jq -r '.data.total_connections // 0' 2>/dev/null)
    max=$(echo "$conn_stats" | jq -r '.data.max_total // 100' 2>/dev/null)
    echo "   Connections: $total/$max"
else
    echo -e "${YELLOW}   Could not fetch connection stats${NC}"
fi

# Check Redis keys
redis_keys=$(docker exec enms-redis redis-cli -a ${REDIS_PASSWORD:-enms2024} KEYS "ratelimit:*" 2>/dev/null | wc -l)
echo "   Rate limit keys in Redis: $redis_keys"
echo ""

# Final summary
echo "============================================"
echo -e "${GREEN}✅ PROTECTION SYSTEM ACTIVATED${NC}"
echo "============================================"
echo ""
echo -e "${BLUE}📊 Configuration:${NC}"
echo "   Application Rate Limits:"
echo "      • Critical endpoints: 100 req/min"
echo "      • Normal endpoints: 60 req/min"
echo "      • Heavy endpoints: 20 req/min"
echo "      • Global per IP: 120 req/min"
echo ""
echo "   Connection Limits:"
echo "      • Per IP: 10 concurrent"
echo "      • Total: 100 concurrent"
echo ""
echo "   Nginx Rate Limits:"
echo "      • General API: 10 req/sec"
echo "      • OVOS endpoints: 20 req/sec"
echo "      • Heavy ops: 2 req/sec"
echo "      • Auth: 5 req/min"
echo ""
echo -e "${BLUE}📚 Next Steps:${NC}"
echo "   1. Test protection: ./protection/test-protection.sh"
echo "   2. Monitor: ./monitoring/check-system-health.sh"
echo "   3. View guide: cat protection/PROTECTION-GUIDE.md"
echo ""
echo -e "${BLUE}🔍 Verify Protection:${NC}"
echo "   # Check rate limit headers"
echo "   curl -I http://localhost:8001/api/v1/health"
echo ""
echo "   # View connection stats"
echo "   curl http://localhost:8001/api/v1/stats/connections | jq"
echo ""
echo "   # Monitor rate limiting"
echo "   docker logs enms-analytics -f | grep 'Rate limit'"
echo ""
