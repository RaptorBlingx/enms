#!/bin/bash

# ENMS Automatic Alert System
# Runs continuously and alerts on issues
# Usage: ./auto-alert.sh

ALERT_EMAIL="your-email@example.com"  # Configure your email
CHECK_INTERVAL=300  # Check every 5 minutes (300 seconds)

echo "🔔 ENMS Auto-Alert System Started"
echo "Checking every $CHECK_INTERVAL seconds..."
echo ""

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    ALERT=0
    ALERT_MSG=""

    # Check 1: Container running
    if ! docker ps | grep -q enms-analytics; then
        ALERT=1
        ALERT_MSG+="❌ CRITICAL: enms-analytics container is DOWN\n"
    fi

    # Check 2: API responding
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/v1/health 2>/dev/null)
    if [ "$HTTP_CODE" != "200" ]; then
        ALERT=1
        ALERT_MSG+="❌ CRITICAL: API not responding (HTTP $HTTP_CODE)\n"
    fi

    # Check 3: Database connection
    if ! docker exec enms-postgres pg_isready -U raptorblingx 2>&1 | grep -q "accepting connections"; then
        ALERT=1
        ALERT_MSG+="❌ CRITICAL: Database not responding\n"
    fi

    # Check 4: High error rate
    TOTAL=$(docker logs enms-analytics --since 5m 2>&1 | grep -c "HTTP/1.1")
    ERRORS=$(docker logs enms-analytics --since 5m 2>&1 | grep -c "HTTP/1.1\" [45]")
    
    if [ $TOTAL -gt 50 ] && [ $ERRORS -gt 0 ]; then
        ERROR_RATE=$(echo "scale=1; $ERRORS * 100 / $TOTAL" | bc)
        if [ $(echo "$ERROR_RATE > 10" | bc) -eq 1 ]; then
            ALERT=1
            ALERT_MSG+="⚠️  WARNING: High error rate (${ERROR_RATE}% in last 5 min)\n"
        fi
    fi

    # Check 5: Excessive traffic
    REQUESTS=$(docker logs enms-analytics --since 1m 2>&1 | grep -c "HTTP/1.1")
    if [ $REQUESTS -gt 500 ]; then
        ALERT=1
        ALERT_MSG+="⚠️  WARNING: Very high traffic ($REQUESTS requests/minute)\n"
    fi

    # Check 6: Disk space
    DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $DISK_USAGE -gt 90 ]; then
        ALERT=1
        ALERT_MSG+="⚠️  WARNING: Disk usage critical (${DISK_USAGE}%)\n"
    fi

    # Check 7: Memory usage (container)
    MEM_USAGE=$(docker stats --no-stream --format "{{.MemPerc}}" enms-analytics 2>/dev/null | sed 's/%//')
    if [ ! -z "$MEM_USAGE" ]; then
        MEM_NUM=$(echo "$MEM_USAGE" | cut -d'.' -f1)
        if [ $MEM_NUM -gt 90 ]; then
            ALERT=1
            ALERT_MSG+="⚠️  WARNING: High memory usage (${MEM_USAGE}%)\n"
        fi
    fi

    # Send alert if needed
    if [ $ALERT -eq 1 ]; then
        echo "=================================================="
        echo "🚨 ALERT at $TIMESTAMP"
        echo "=================================================="
        echo -e "$ALERT_MSG"
        echo "=================================================="
        
        # Log to file
        echo "[$TIMESTAMP] ALERT" >> /home/ubuntu/enms/logs/alerts.log
        echo -e "$ALERT_MSG" >> /home/ubuntu/enms/logs/alerts.log
        
        # Optional: Send email (requires mailutils configured)
        # echo -e "$ALERT_MSG" | mail -s "ENMS Alert: $TIMESTAMP" $ALERT_EMAIL
        
    else
        echo "[$TIMESTAMP] ✅ All systems normal"
    fi

    sleep $CHECK_INTERVAL
done
