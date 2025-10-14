#!/bin/bash

# Test Analytics Baseline Training
# Real parameters from our database

echo "==================================="
echo "Testing Analytics Baseline Training"
echo "==================================="
echo ""
echo "Machine: Compressor-1 (c0000000-0000-0000-0000-000000000001)"
echo "Date Range: 2025-10-10 07:00 to 2025-10-11 11:45"
echo "Drivers: production_count, outdoor_temp_c, pressure_bar"
echo ""
echo "Making API request..."
echo ""

RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "http://localhost:8080/api/analytics/api/v1/baseline/train" \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "c0000000-0000-0000-0000-000000000001",
    "start_date": "2025-10-10T07:00:00Z",
    "end_date": "2025-10-11T11:45:00Z",
    "drivers": ["total_production_count", "avg_outdoor_temp_c", "avg_pressure_bar"]
  }')

HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')

echo "HTTP Status: $HTTP_CODE"
echo ""
echo "Response Body:"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
echo ""

if [ "$HTTP_CODE" != "200" ]; then
    echo "❌ Request failed! Checking logs..."
    echo ""
    docker compose logs analytics --tail 30 2>&1 | grep -A15 "ERROR\|Error\|Traceback\|Exception" | tail -20
fi

echo "==================================="
