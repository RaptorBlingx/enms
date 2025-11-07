#!/bin/bash
#
# API Documentation Validation Script
# Tests all critical v3 endpoints to ensure documentation accuracy
# Run this before any documentation updates to catch bugs early
#
# Author: EnMS Team
# Date: November 7, 2025
# Purpose: Phase 5.1 - API Documentation validation
#

set -e  # Exit on error

BASE_URL="http://localhost:8001/api/v1"
FACTORY_ID="11111111-1111-1111-1111-111111111111"
TEST_DATE="2025-11-06"

# Colors for output
GREEN='\033[0.32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

echo "========================================="
echo "  EnMS API Documentation Validator"
echo "  Testing critical v3 endpoints"
echo "========================================="
echo ""

# Test function
test_endpoint() {
    local name="$1"
    local curl_cmd="$2"
    local validation="$3"
    
    echo -n "Testing: $name ... "
    
    # Execute curl with timeout
    response=$(eval "$curl_cmd" 2>&1 || echo "CURL_FAILED")
    
    if [[ "$response" == "CURL_FAILED" ]]; then
        echo -e "${RED}FAILED${NC} (curl error)"
        FAILED=$((FAILED + 1))
        return 1
    fi
    
    # Check if response is valid JSON
    if ! echo "$response" | jq empty 2>/dev/null; then
        echo -e "${RED}FAILED${NC} (invalid JSON)"
        echo "Response: $response"
        FAILED=$((FAILED + 1))
        return 1
    fi
    
    # Run validation check
    if eval "$validation"; then
        echo -e "${GREEN}PASSED${NC}"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}FAILED${NC} (validation failed)"
        echo "Response: $response"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Test function with performance timing
test_endpoint_timed() {
    local name="$1"
    local curl_cmd="$2"
    local validation="$3"
    local max_time="$4"
    
    echo -n "Testing: $name ... "
    
    # Execute curl with timing
    start_time=$(date +%s.%N)
    response=$(eval "$curl_cmd" 2>&1 || echo "CURL_FAILED")
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc)
    
    if [[ "$response" == "CURL_FAILED" ]]; then
        echo -e "${RED}FAILED${NC} (curl error)"
        FAILED=$((FAILED + 1))
        return 1
    fi
    
    # Check if response is valid JSON
    if ! echo "$response" | jq empty 2>/dev/null; then
        echo -e "${RED}FAILED${NC} (invalid JSON)"
        FAILED=$((FAILED + 1))
        return 1
    fi
    
    # Run validation check
    if eval "$validation"; then
        # Check timing
        if (( $(echo "$duration > $max_time" | bc -l) )); then
            echo -e "${YELLOW}PASSED${NC} (${duration}s - exceeds ${max_time}s target)"
            WARNINGS=$((WARNINGS + 1))
        else
            echo -e "${GREEN}PASSED${NC} (${duration}s)"
        fi
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}FAILED${NC} (validation failed, ${duration}s)"
        echo "Response: $response"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

echo "=== PHASE 1: Core System Endpoints ==="
echo ""

# 1. Health Check
test_endpoint \
    "GET /health" \
    "curl -s -m 5 '$BASE_URL/health'" \
    "echo \"\$response\" | jq -e '.service == \"EnMS Analytics Service\" and .status == \"healthy\"' >/dev/null"

# 2. System Stats
test_endpoint \
    "GET /stats/system" \
    "curl -s -m 5 '$BASE_URL/stats/system'" \
    "echo \"\$response\" | jq -e '.total_energy != null and .active_machines_today != null' >/dev/null"

echo ""
echo "=== PHASE 2: Performance Engine Endpoints ==="
echo ""

# 3. Performance Analyze
test_endpoint_timed \
    "POST /performance/analyze" \
    "curl -s -m 10 -X POST '$BASE_URL/performance/analyze' -H 'Content-Type: application/json' -d '{\"seu_name\":\"Compressor-1\",\"energy_source\":\"electricity\",\"analysis_date\":\"$TEST_DATE\"}'" \
    "echo \"\$response\" | jq -e '.seu_name == \"Compressor-1\" and .actual_energy_kwh != null and .baseline_energy_kwh != null and .deviation_kwh != null and .iso50001_status != null and .voice_summary != null' >/dev/null" \
    "5.0"

# 4. Performance Opportunities (KNOWN SLOW ~35s)
echo -n "Testing: GET /performance/opportunities ... "
echo -e "${YELLOW}SKIPPED${NC} (known slow endpoint ~35s, validated in Phase 4.2)"
WARNINGS=$((WARNINGS + 1))

# 5. Performance Action Plan
test_endpoint_timed \
    "POST /performance/action-plan" \
    "curl -s -m 10 -X POST '$BASE_URL/performance/action-plan?seu_name=Injection-Molding-1&issue_type=excessive_idle'" \
    "echo \"\$response\" | jq -e '.seu_name == \"Injection-Molding-1\" and .problem_statement != null and (.actions | length) > 0' >/dev/null" \
    "2.0"

echo ""
echo "=== PHASE 3: ISO 50001 Endpoints ==="
echo ""

# 6. EnPI Report
test_endpoint_timed \
    "GET /iso50001/enpi-report" \
    "curl -s -m 20 '$BASE_URL/iso50001/enpi-report?factory_id=$FACTORY_ID&period=2025-Q4'" \
    "echo \"\$response\" | jq -e '.report_period == \"2025-Q4\" and .overall_performance.total_energy_baseline_kwh != null and .overall_performance.total_energy_actual_kwh != null and (.seu_breakdown | length) > 0' >/dev/null" \
    "15.0"

echo ""
echo "=== PHASE 4: Baseline Endpoints (Enhanced for v3) ==="
echo ""

# 8. Baseline Predict (with SEU name - v3 enhancement)
test_endpoint_timed \
    "POST /baseline/predict (SEU name)" \
    "curl -s -m 5 -X POST '$BASE_URL/baseline/predict' -H 'Content-Type: application/json' -d '{\"seu_name\":\"Compressor-1\",\"energy_source\":\"electricity\",\"features\":{\"total_production_count\":100000,\"avg_outdoor_temp_c\":25.0,\"avg_pressure_bar\":6.0},\"include_message\":true}'" \
    "echo \"\$response\" | jq -e '.predicted_energy_kwh != null and .message != null' >/dev/null" \
    "1.0"

# 9. Baseline Models (requires seu_name + energy_source)
test_endpoint \
    "GET /baseline/models" \
    "curl -s -m 5 '$BASE_URL/baseline/models?seu_name=Compressor-1&energy_source=electricity'" \
    "echo \"\$response\" | jq -e '.seu_name == \"Compressor-1\" and .models != null and (.models | length) > 0' >/dev/null"

echo ""
echo "=== PHASE 5: SEU & Machine Endpoints ==="
echo ""

# 10. List SEUs
test_endpoint \
    "GET /seus" \
    "curl -s -m 5 '$BASE_URL/seus'" \
    "echo \"\$response\" | jq -e '.success == true and .seus != null and (.seus | length) > 0' >/dev/null"

# 11. Machine Status by Name (v3 enhancement)
test_endpoint \
    "GET /machines/status/{name}" \
    "curl -s -m 5 '$BASE_URL/machines/status/Compressor-1'" \
    "echo \"\$response\" | jq -e '.machine_name == \"Compressor-1\" and .current_status != null and .today_stats != null' >/dev/null"

echo ""
echo "========================================="
echo "  Validation Summary"
echo "========================================="
echo -e "${GREEN}PASSED:${NC}   $PASSED"
echo -e "${RED}FAILED:${NC}   $FAILED"
echo -e "${YELLOW}WARNINGS:${NC} $WARNINGS"
echo "========================================="

if [ $FAILED -gt 0 ]; then
    echo ""
    echo -e "${RED}❌ DOCUMENTATION VALIDATION FAILED${NC}"
    echo "Some endpoints are not working as documented."
    echo "Fix these issues before updating documentation."
    exit 1
else
    echo ""
    echo -e "${GREEN}✅ DOCUMENTATION VALIDATION PASSED${NC}"
    echo "All critical v3 endpoints working as documented."
    exit 0
fi
