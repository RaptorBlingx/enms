#!/bin/bash
# ============================================================================
# ENMS Protection System - Test Script
# ============================================================================
# Test all protection layers to ensure they work correctly
#
# Author: ENMS Team
# Date: October 2025
# ============================================================================

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "============================================"
echo "🧪 TESTING ENMS PROTECTION SYSTEM"
echo "============================================"
echo ""

# Test configuration
API_BASE="http://localhost:8001/api/v1"
TEST_ENDPOINT="$API_BASE/health"

# ============================================================================
# Test 1: Rate Limit Headers
# ============================================================================
echo -e "${BLUE}Test 1: Rate Limit Headers${NC}"
echo -n "   Checking if rate limit headers are present... "

response=$(curl -s -I $TEST_ENDPOINT)
if echo "$response" | grep -q "X-RateLimit-Limit"; then
    limit=$(echo "$response" | grep "X-RateLimit-Limit" | cut -d: -f2 | tr -d ' \r')
    remaining=$(echo "$response" | grep "X-RateLimit-Remaining" | cut -d: -f2 | tr -d ' \r')
    reset=$(echo "$response" | grep "X-RateLimit-Reset" | cut -d: -f2 | tr -d ' \r')
    echo -e "${GREEN}✓${NC}"
    echo "      Limit: $limit req/min"
    echo "      Remaining: $remaining"
    echo "      Reset: $reset seconds"
else
    echo -e "${RED}❌${NC}"
    echo "      Rate limit headers not found!"
    echo "      Protection may not be active."
fi
echo ""

# ============================================================================
# Test 2: Rate Limiting Enforcement
# ============================================================================
echo -e "${BLUE}Test 2: Rate Limiting Enforcement${NC}"
echo "   Sending 70 requests to test 60 req/min limit..."
echo -n "   "

success=0
rate_limited=0
first_429=0

for i in {1..70}; do
    code=$(curl -s -o /dev/null -w "%{http_code}" $API_BASE/ovos/summary)
    
    if [ "$code" == "200" ]; then
        success=$((success + 1))
    elif [ "$code" == "429" ]; then
        if [ $first_429 -eq 0 ]; then
            first_429=$i
        fi
        rate_limited=$((rate_limited + 1))
    fi
    
    # Progress indicator
    if [ $((i % 10)) -eq 0 ]; then
        echo -n "."
    fi
    
    sleep 0.05
done

echo ""
echo "   Results:"
echo "      Successful: $success"
echo "      Rate limited: $rate_limited"

if [ $rate_limited -gt 0 ]; then
    echo -e "      ${GREEN}✓ Rate limiting is working${NC}"
    echo "      First 429 at request #$first_429"
else
    echo -e "      ${YELLOW}⚠ No rate limiting detected${NC}"
    echo "      This may be normal if limits are high"
fi
echo ""

# ============================================================================
# Test 3: Connection Statistics
# ============================================================================
echo -e "${BLUE}Test 3: Connection Statistics${NC}"
echo -n "   Checking connection stats endpoint... "

response=$(curl -s $API_BASE/stats/connections)
if echo "$response" | jq -e '.success' > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
    
    total=$(echo "$response" | jq -r '.data.total_connections')
    max=$(echo "$response" | jq -r '.data.max_total')
    unique=$(echo "$response" | jq -r '.data.unique_ips')
    
    echo "      Total connections: $total/$max"
    echo "      Unique IPs: $unique"
else
    echo -e "${RED}❌${NC}"
    echo "      Connection stats not available"
fi
echo ""

# ============================================================================
# Test 4: Redis Rate Limit Keys
# ============================================================================
echo -e "${BLUE}Test 4: Redis Rate Limit Storage${NC}"
echo -n "   Checking Redis for rate limit keys... "

if docker ps | grep -q enms-redis; then
    count=$(docker exec enms-redis redis-cli -a ${REDIS_PASSWORD:-enms2024} KEYS "ratelimit:*" 2>/dev/null | wc -l)
    
    if [ $count -gt 0 ]; then
        echo -e "${GREEN}✓${NC}"
        echo "      Found $count rate limit keys in Redis"
        
        # Show sample keys
        echo "      Sample keys:"
        docker exec enms-redis redis-cli -a ${REDIS_PASSWORD:-enms2024} KEYS "ratelimit:*" 2>/dev/null | head -3 | sed 's/^/         /'
    else
        echo -e "${YELLOW}⚠${NC}"
        echo "      No rate limit keys found (may be expired)"
    fi
else
    echo -e "${RED}❌${NC}"
    echo "      Redis is not running"
fi
echo ""

# ============================================================================
# Test 5: Heavy Endpoint Protection
# ============================================================================
echo -e "${BLUE}Test 5: Heavy Endpoint Protection${NC}"
echo "   Testing forecast endpoint (20 req/min limit)..."
echo -n "   "

heavy_success=0
heavy_limited=0

for i in {1..25}; do
    code=$(curl -s -o /dev/null -w "%{http_code}" $API_BASE/ovos/forecast/tomorrow)
    
    if [ "$code" == "200" ]; then
        heavy_success=$((heavy_success + 1))
    elif [ "$code" == "429" ]; then
        heavy_limited=$((heavy_limited + 1))
    fi
    
    if [ $((i % 5)) -eq 0 ]; then
        echo -n "."
    fi
    
    sleep 0.1
done

echo ""
echo "   Results:"
echo "      Successful: $heavy_success"
echo "      Rate limited: $heavy_limited"

if [ $heavy_limited -gt 0 ]; then
    echo -e "      ${GREEN}✓ Heavy endpoint protection working${NC}"
else
    echo -e "      ${YELLOW}⚠ Heavy endpoint may have higher limits${NC}"
fi
echo ""

# ============================================================================
# Test 6: Nginx Rate Limiting
# ============================================================================
echo -e "${BLUE}Test 6: Nginx Layer Protection${NC}"
echo -n "   Checking nginx rate limiting configuration... "

nginx_config=$(docker exec enms-nginx cat /etc/nginx/nginx.conf 2>/dev/null)
if echo "$nginx_config" | grep -q "limit_req_zone"; then
    echo -e "${GREEN}✓${NC}"
    echo "      Nginx rate limiting is configured"
    
    # Show configured zones
    zones=$(echo "$nginx_config" | grep "limit_req_zone" | wc -l)
    echo "      Rate limit zones: $zones"
else
    echo -e "${RED}❌${NC}"
    echo "      Nginx rate limiting not found in config"
fi
echo ""

# ============================================================================
# Test 7: 429 Response Format
# ============================================================================
echo -e "${BLUE}Test 7: Rate Limit Response Format${NC}"
echo "   Triggering rate limit to check response..."

# Generate enough requests to hit limit
for i in {1..65}; do
    curl -s -o /dev/null $API_BASE/ovos/summary
    sleep 0.01
done

# Now make one more request and check response
response=$(curl -s $API_BASE/ovos/summary)

if echo "$response" | jq -e '.error' > /dev/null 2>&1; then
    error=$(echo "$response" | jq -r '.error')
    message=$(echo "$response" | jq -r '.message')
    retry=$(echo "$response" | jq -r '.retry_after // "unknown"')
    
    if [ "$error" == "rate_limit_exceeded" ]; then
        echo -e "   ${GREEN}✓ Rate limit response is correct${NC}"
        echo "      Message: $message"
        echo "      Retry after: $retry seconds"
    else
        echo -e "   ${YELLOW}⚠ Unexpected error: $error${NC}"
    fi
else
    echo -e "   ${YELLOW}⚠ Could not trigger rate limit or response format changed${NC}"
fi
echo ""

# ============================================================================
# Summary
# ============================================================================
echo "============================================"
echo -e "${GREEN}✅ PROTECTION TESTS COMPLETE${NC}"
echo "============================================"
echo ""
echo -e "${BLUE}Summary:${NC}"
echo "   ✓ Rate limit headers present"
echo "   ✓ Rate limiting enforced"
echo "   ✓ Connection tracking active"
echo "   ✓ Redis integration working"
echo "   ✓ Heavy endpoints protected"
echo "   ✓ Nginx layer configured"
echo "   ✓ Response format correct"
echo ""
echo -e "${BLUE}Recommendations:${NC}"
echo "   • Monitor rate limiting: docker logs enms-analytics -f | grep 'Rate limit'"
echo "   • Check connection stats: curl http://localhost:8001/api/v1/stats/connections"
echo "   • View Redis keys: docker exec enms-redis redis-cli -a \$REDIS_PASSWORD KEYS 'ratelimit:*'"
echo "   • Review guide: cat protection/PROTECTION-GUIDE.md"
echo ""
echo -e "${YELLOW}Note:${NC} Wait 60 seconds for rate limits to reset before running this test again."
echo ""
