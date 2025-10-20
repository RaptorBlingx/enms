#!/bin/bash

# ENMS Request Rate Monitor
# Detects high traffic from OVOS or other clients
# Usage: ./monitor-request-rate.sh [duration_in_seconds]

DURATION=${1:-60}  # Default 60 seconds
THRESHOLD=100      # Alert if more than 100 requests per minute

echo "============================================"
echo "📈 ENMS REQUEST RATE MONITOR"
echo "============================================"
echo "Monitoring for $DURATION seconds..."
echo "Alert threshold: $THRESHOLD requests/minute"
echo ""

# Get initial log line count
INITIAL_COUNT=$(docker logs enms-analytics --tail 1000 2>&1 | grep -c "HTTP/1.1")
START_TIME=$(date +%s)

sleep $DURATION

# Get final log line count
FINAL_COUNT=$(docker logs enms-analytics --tail 1000 2>&1 | grep -c "HTTP/1.1")
END_TIME=$(date +%s)

# Calculate rate
NEW_REQUESTS=$((FINAL_COUNT - INITIAL_COUNT))
ELAPSED=$((END_TIME - START_TIME))
RATE_PER_MINUTE=$(echo "scale=1; $NEW_REQUESTS * 60 / $ELAPSED" | bc)

echo "⏱️  Monitoring Duration: ${ELAPSED}s"
echo "📊 Total Requests: $NEW_REQUESTS"
echo "🚀 Request Rate: ${RATE_PER_MINUTE} requests/minute"
echo ""

# Breakdown by endpoint
echo "📍 Endpoint Breakdown:"
echo "-------------------------------------------"
docker logs enms-analytics --since ${ELAPSED}s 2>&1 | \
    grep "HTTP/1.1" | \
    grep -o '"GET [^"]*"' | \
    sed 's/"GET //' | sed 's/".*//' | \
    awk -F'?' '{print $1}' | \
    sort | uniq -c | sort -rn | head -10 | \
    while read count endpoint; do
        printf "  %-50s %5d requests\n" "$endpoint" "$count"
    done
echo ""

# Breakdown by IP
echo "🌍 Client IPs:"
echo "-------------------------------------------"
docker logs enms-analytics --since ${ELAPSED}s 2>&1 | \
    grep "HTTP/1.1" | \
    grep -oP '\d+\.\d+\.\d+\.\d+' | \
    sort | uniq -c | sort -rn | head -5 | \
    while read count ip; do
        printf "  %-20s %5d requests\n" "$ip" "$count"
    done
echo ""

# Status codes
echo "📊 HTTP Status Codes:"
echo "-------------------------------------------"
docker logs enms-analytics --since ${ELAPSED}s 2>&1 | \
    grep "HTTP/1.1" | \
    grep -oP 'HTTP/1.1" \d+' | \
    awk '{print $2}' | \
    sort | uniq -c | sort -rn | \
    while read count code; do
        if [ "$code" -ge 200 ] && [ "$code" -lt 300 ]; then
            printf "  \033[0;32m%-10s\033[0m %5d requests\n" "$code" "$count"
        elif [ "$code" -ge 400 ]; then
            printf "  \033[0;31m%-10s\033[0m %5d requests\n" "$code" "$count"
        else
            printf "  %-10s %5d requests\n" "$code" "$count"
        fi
    done
echo ""

# Alert if threshold exceeded
if [ $(echo "$RATE_PER_MINUTE > $THRESHOLD" | bc) -eq 1 ]; then
    echo "⚠️  WARNING: Request rate (${RATE_PER_MINUTE}/min) exceeds threshold ($THRESHOLD/min)"
    echo "   Consider investigating:"
    echo "   - Check if OVOS is running properly"
    echo "   - Look for retry loops or errors"
    echo "   - Check for DDoS or abuse"
else
    echo "✅ Request rate is within normal limits"
fi

echo ""
echo "============================================"
