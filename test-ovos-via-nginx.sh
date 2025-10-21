#!/bin/bash
# Test OVOS endpoints through nginx proxy

BASE_URL="http://10.33.10.109:8080/api/analytics"

echo "🔍 Testing OVOS Endpoints via Nginx Proxy"
echo "=========================================="
echo ""

echo "1. Health Check:"
curl -s -w "\n   HTTP %{http_code}\n" "$BASE_URL/api/v1/health" | jq -r '.status' 2>/dev/null || echo "   Failed"
echo ""

echo "2. OVOS Summary:"
curl -s -w "\n   HTTP %{http_code}\n" "$BASE_URL/api/v1/ovos/summary" | jq -r '.success' 2>/dev/null || echo "   Failed"
echo ""

echo "3. Machine Search (compressor):"
curl -s -w "\n   HTTP %{http_code}\n" "$BASE_URL/api/v1/machines?search=compressor" | jq -r '.total_count' 2>/dev/null || echo "   Failed"
echo ""

echo "4. Recent Anomalies:"
curl -s -w "\n   HTTP %{http_code}\n" "$BASE_URL/api/v1/anomaly/recent?machine_id=c0000000-0000-0000-0000-000000000001" | jq -r '.success' 2>/dev/null || echo "   Failed"
echo ""

echo "5. Top Consumers:"
curl -s -w "\n   HTTP %{http_code}\n" "$BASE_URL/api/v1/ovos/top-consumers?start_time=2025-10-20T00:00:00Z&end_time=2025-10-21T00:00:00Z&limit=5" | jq -r '.success' 2>/dev/null || echo "   Failed"
echo ""

echo "6. Forecast Tomorrow:"
curl -s -w "\n   HTTP %{http_code}\n" "$BASE_URL/api/v1/ovos/forecast/tomorrow" | jq -r '.success' 2>/dev/null || echo "   Failed"
echo ""

echo "✅ All OVOS endpoints tested via nginx!"
