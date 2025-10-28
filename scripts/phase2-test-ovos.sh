#!/bin/bash
# Phase 2: Test OVOS Voice Integration Endpoints
# Validates that OVOS endpoints work correctly with real data
# Date: October 24, 2025

set -e

BASE_URL="http://localhost:8001/api/v1/ovos"

echo ""
echo "========================================================================="
echo "🧪 Phase 2: OVOS Voice Integration Testing"
echo "========================================================================="
echo ""

# Test 1: Energy Source Discovery
echo "========================================================================="
echo "Test 1: Energy Source Discovery"
echo "========================================================================="
echo ""
echo "Request: GET $BASE_URL/energy-sources"
echo ""

RESPONSE=$(curl -s "$BASE_URL/energy-sources")
echo "$RESPONSE" | jq .

SUCCESS=$(echo "$RESPONSE" | jq -r '.success')
ENERGY_COUNT=$(echo "$RESPONSE" | jq -r '.energy_sources | length')

if [ "$SUCCESS" = "true" ] && [ "$ENERGY_COUNT" -ge 1 ]; then
    echo ""
    echo "✅ Test 1 PASSED: Found $ENERGY_COUNT energy sources"
else
    echo ""
    echo "❌ Test 1 FAILED: Energy source discovery failed"
    exit 1
fi

sleep 2

# Test 2: SEU Discovery
echo ""
echo "========================================================================="
echo "Test 2: SEU Discovery (Electricity)"
echo "========================================================================="
echo ""
echo "Request: GET $BASE_URL/seus?energy_source=electricity"
echo ""

RESPONSE=$(curl -s "$BASE_URL/seus?energy_source=electricity")
echo "$RESPONSE" | jq .

SUCCESS=$(echo "$RESPONSE" | jq -r '.success')
SEU_COUNT=$(echo "$RESPONSE" | jq -r '.total_count')

if [ "$SUCCESS" = "true" ] && [ "$SEU_COUNT" -eq 7 ]; then
    echo ""
    echo "✅ Test 2 PASSED: Found $SEU_COUNT electricity SEUs"
else
    echo ""
    echo "❌ Test 2 FAILED: Expected 7 electricity SEUs, got $SEU_COUNT"
    exit 1
fi

sleep 2

# Test 3: Voice Training (Valid Request)
echo ""
echo "========================================================================="
echo "Test 3: Voice Training (Valid Features)"
echo "========================================================================="
echo ""
echo "Simulated voice command: 'Train baseline for Compressor-1 electricity"
echo "using production count and outdoor temperature for 2024'"
echo ""
echo "Request: POST $BASE_URL/train-baseline"
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/train-baseline" \
  -H "Content-Type: application/json" \
  -d '{
    "seu_name": "Compressor-1",
    "energy_source": "electricity",
    "features": ["production_count", "outdoor_temp_c"],
    "year": 2024
  }')

echo "$RESPONSE" | jq .

SUCCESS=$(echo "$RESPONSE" | jq -r '.success')
R2=$(echo "$RESPONSE" | jq -r '.r_squared // 0')
MESSAGE=$(echo "$RESPONSE" | jq -r '.message')

if [ "$SUCCESS" = "true" ]; then
    echo ""
    echo "✅ Test 3 PASSED: Training successful"
    echo "   R² Score: $R2"
    echo "   Voice Response: $MESSAGE"
else
    echo ""
    echo "❌ Test 3 FAILED: Training failed"
    echo "   Error: $MESSAGE"
    exit 1
fi

sleep 2

# Test 4: Voice Training (Invalid Features)
echo ""
echo "========================================================================="
echo "Test 4: Voice Training (Invalid Features - Error Handling)"
echo "========================================================================="
echo ""
echo "Request: POST $BASE_URL/train-baseline (with invalid features)"
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/train-baseline" \
  -H "Content-Type: application/json" \
  -d '{
    "seu_name": "Compressor-1",
    "energy_source": "electricity",
    "features": ["invalid_feature", "another_bad_feature"],
    "year": 2024
  }')

echo "$RESPONSE" | jq .

SUCCESS=$(echo "$RESPONSE" | jq -r '.success')
ERROR_DETAILS=$(echo "$RESPONSE" | jq -r '.error_details // "No error details"')

if [ "$SUCCESS" = "false" ]; then
    echo ""
    echo "✅ Test 4 PASSED: Invalid features rejected correctly"
    echo "   Error message provided: $ERROR_DETAILS"
else
    echo ""
    echo "❌ Test 4 FAILED: Should have rejected invalid features"
    exit 1
fi

sleep 2

# Test 5: Voice Training (Non-existent SEU)
echo ""
echo "========================================================================="
echo "Test 5: Voice Training (Non-existent SEU)"
echo "========================================================================="
echo ""
echo "Request: POST $BASE_URL/train-baseline (with invalid SEU name)"
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/train-baseline" \
  -H "Content-Type: application/json" \
  -d '{
    "seu_name": "NonExistentSEU-999",
    "energy_source": "electricity",
    "features": ["production_count", "outdoor_temp_c"],
    "year": 2024
  }')

echo "$RESPONSE" | jq .

SUCCESS=$(echo "$RESPONSE" | jq -r '.success')
MESSAGE=$(echo "$RESPONSE" | jq -r '.message')

if [ "$SUCCESS" = "false" ] && [[ "$MESSAGE" == *"not found"* ]]; then
    echo ""
    echo "✅ Test 5 PASSED: Non-existent SEU rejected correctly"
else
    echo ""
    echo "❌ Test 5 FAILED: Should have rejected non-existent SEU"
    exit 1
fi

sleep 2

# Summary
echo ""
echo "========================================================================="
echo "📊 Phase 2 Testing Summary"
echo "========================================================================="
echo ""
echo "✅ Test 1: Energy source discovery - PASSED"
echo "✅ Test 2: SEU discovery - PASSED (7 electricity SEUs)"
echo "✅ Test 3: Voice training (valid) - PASSED"
echo "✅ Test 4: Error handling (invalid features) - PASSED"
echo "✅ Test 5: Error handling (invalid SEU) - PASSED"
echo ""
echo "🎉 All OVOS endpoint tests passed!"
echo ""
echo "Next Steps:"
echo "  1. Review OVOS integration guide: cat docs/OVOS-INTEGRATION-GUIDE.md"
echo "  2. Demo voice commands to Mr. Umut"
echo "  3. (Optional) Proceed to Phase 3: Multi-energy preparation"
echo ""
