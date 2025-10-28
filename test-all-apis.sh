#!/bin/bash

# EnMS API Comprehensive Test Script
# Tests all OVOS-documented endpoints systematically
# Date: October 27, 2025

BASE_URL="http://localhost:8001/api/v1"
BOILER_ID="e9fcad45-1f7b-4425-8710-c368a681f15e"
COMPRESSOR_ID="c0000000-0000-0000-0000-000000000001"
COMPRESSOR_EU_ID="c0000000-0000-0000-0000-000000000006"

# Get current timestamp for queries
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
ONE_HOUR_AGO=$(date -u -d "1 hour ago" +"%Y-%m-%dT%H:%M:%SZ")
TWO_HOURS_AGO=$(date -u -d "2 hours ago" +"%Y-%m-%dT%H:%M:%SZ")
ONE_DAY_AGO=$(date -u -d "1 day ago" +"%Y-%m-%dT%H:%M:%SZ")

echo "======================================"
echo "EnMS API Comprehensive Test Suite"
echo "======================================"
echo "Time Range: $TWO_HOURS_AGO to $NOW"
echo ""

# Counter for pass/fail
PASS_COUNT=0
FAIL_COUNT=0

test_endpoint() {
    local test_num=$1
    local test_name=$2
    local url=$3
    local method=${4:-GET}
    local data=$5
    
    echo "----------------------------------------"
    echo "Test $test_num: $test_name"
    echo "URL: $url"
    
    if [ "$method" == "GET" ]; then
        response=$(curl -s "$url")
    else
        response=$(curl -s -X "$method" -H "Content-Type: application/json" -d "$data" "$url")
    fi
    
    # Check if response contains error
    if echo "$response" | jq -e '.detail' >/dev/null 2>&1; then
        echo "❌ FAILED"
        echo "Error: $(echo "$response" | jq -r '.detail')"
        ((FAIL_COUNT++))
    elif echo "$response" | jq -e '.success == false' >/dev/null 2>&1; then
        echo "❌ FAILED"
        echo "Response: $(echo "$response" | jq -c '.')"
        ((FAIL_COUNT++))
    else
        echo "✅ PASSED"
        echo "Response: $(echo "$response" | jq -c '.' | head -c 200)..."
        ((PASS_COUNT++))
    fi
    echo ""
}

echo "=== SYSTEM HEALTH & STATS ==="
test_endpoint 1 "Health Check" "$BASE_URL/health"
test_endpoint 2 "System Statistics" "$BASE_URL/stats/system"

echo ""
echo "=== MACHINES API ==="
test_endpoint 3 "List All Machines" "$BASE_URL/machines"
test_endpoint 4 "Search Machines (boiler)" "$BASE_URL/machines?search=boiler"
test_endpoint 5 "Get Single Machine (Boiler-1)" "$BASE_URL/machines/$BOILER_ID"

echo ""
echo "=== TIME-SERIES DATA ==="
test_endpoint 6 "Energy Time-Series (Boiler-1)" \
    "$BASE_URL/timeseries/energy?machine_id=$BOILER_ID&start_time=$TWO_HOURS_AGO&end_time=$NOW&interval=15min"

test_endpoint 7 "Power Time-Series (Compressor-1)" \
    "$BASE_URL/timeseries/power?machine_id=$COMPRESSOR_ID&start_time=$ONE_HOUR_AGO&end_time=$NOW&interval=5min"

test_endpoint 8 "Latest Reading (Boiler-1)" \
    "$BASE_URL/timeseries/latest/$BOILER_ID"

test_endpoint 9 "Multi-Machine Comparison" \
    "$BASE_URL/timeseries/multi-machine/energy?machine_ids=$COMPRESSOR_ID,$COMPRESSOR_EU_ID&start_time=$TWO_HOURS_AGO&end_time=$NOW&interval=1hour"

echo ""
echo "=== MULTI-ENERGY ENDPOINTS (NEW) ==="
test_endpoint 10 "List Energy Types (Boiler-1)" \
    "$BASE_URL/machines/$BOILER_ID/energy-types?hours=2"

test_endpoint 11 "Natural Gas Readings" \
    "$BASE_URL/machines/$BOILER_ID/energy/natural_gas?limit=5"

test_endpoint 12 "Steam Readings" \
    "$BASE_URL/machines/$BOILER_ID/energy/steam?limit=5"

test_endpoint 13 "Multi-Energy Summary" \
    "$BASE_URL/machines/$BOILER_ID/energy-summary?hours=2"

echo ""
echo "=== ANOMALY DETECTION ==="
test_endpoint 14 "Detect Anomalies" \
    "$BASE_URL/anomaly/detect" \
    "POST" \
    "{\"machine_id\":\"$COMPRESSOR_ID\",\"start\":\"$ONE_DAY_AGO\",\"end\":\"$NOW\",\"threshold\":2.0}"

test_endpoint 15 "Get Recent Anomalies" \
    "$BASE_URL/anomaly/recent?machine_id=$COMPRESSOR_ID&limit=5"

test_endpoint 16 "Get Active Anomalies" \
    "$BASE_URL/anomaly/active?machine_id=$COMPRESSOR_ID"

echo ""
echo "=== BASELINE MODELS ==="
test_endpoint 17 "List Baseline Models" \
    "$BASE_URL/baseline/models?machine_id=$COMPRESSOR_ID"

test_endpoint 18 "Predict Expected Energy" \
    "$BASE_URL/baseline/predict" \
    "POST" \
    "{\"machine_id\":\"$COMPRESSOR_ID\",\"features\":{\"total_production_count\":100.0,\"avg_outdoor_temp_c\":22.0,\"avg_pressure_bar\":7.2}}"

echo ""
echo "=== KPI & FORECASTING ==="
test_endpoint 19 "Get KPIs" \
    "$BASE_URL/kpi/all?machine_id=$COMPRESSOR_ID&start=$ONE_DAY_AGO&end=$NOW"

test_endpoint 20 "Energy Forecast" \
    "$BASE_URL/forecast/demand?machine_id=$COMPRESSOR_ID&forecast_hours=4"

echo ""
echo "=== OVOS VOICE TRAINING ==="
test_endpoint 21 "Train Baseline (Voice Command)" \
    "$BASE_URL/ovos/train-baseline" \
    "POST" \
    "{\"seu_name\":\"Compressor-1\",\"energy_source\":\"electricity\",\"features\":[\"production_count\",\"outdoor_temp_c\"],\"year\":2024}"

echo ""
echo "======================================"
echo "TEST SUMMARY"
echo "======================================"
echo "✅ PASSED: $PASS_COUNT"
echo "❌ FAILED: $FAIL_COUNT"
echo "TOTAL: $((PASS_COUNT + FAIL_COUNT))"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo "🎉 ALL TESTS PASSED!"
    exit 0
else
    echo "⚠️  SOME TESTS FAILED - Review output above"
    exit 1
fi
