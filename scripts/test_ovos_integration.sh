#!/bin/bash

# OVOS Integration Validation Script
# Purpose: Quick test of all EnMS API endpoints that OVOS uses
# Run this to verify backend is working before testing OVOS

API_BASE="http://10.33.10.109:8001/api/v1"

echo "🧪 OVOS Integration Test - EnMS Backend API Validation"
echo "========================================================"
echo ""

# Test 1: List all machines
echo "📋 Test 1: List all machines"
echo "----------------------------"
curl -s "${API_BASE}/ovos/seus" | jq '{total: .total_count, names: [.seus[].name]}'
echo ""

# Test 2: List energy sources
echo "🔋 Test 2: List energy sources"
echo "-------------------------------"
curl -s "${API_BASE}/ovos/energy-sources" | jq '{total: .total_count, sources: [.energy_sources[] | {name, unit}]}'
echo ""

# Test 3: Filter machines by energy source
echo "🔍 Test 3: Filter machines by natural gas"
echo "------------------------------------------"
curl -s "${API_BASE}/ovos/seus?energy_source=natural_gas" | jq '{total: .total_count, filtered_by: .filtered_by, names: [.seus[].name]}'
echo ""

# Test 4: Get electricity features
echo "⚡ Test 4: Get electricity features"
echo "------------------------------------"
curl -s "${API_BASE}/features/electricity" | jq '{energy_source, total_features, sample_features: [.features[0:5] | .[].feature_name]}'
echo ""

# Test 5: Train baseline - Success case
echo "🎓 Test 5: Train baseline for Compressor-EU-1 (should succeed)"
echo "----------------------------------------------------------------"
curl -s -X POST "${API_BASE}/ovos/train-baseline" \
  -H "Content-Type: application/json" \
  -d '{"seu_name": "Compressor-EU-1", "energy_source": "electricity", "features": [], "year": 2025}' | \
  jq '{success, message, r_squared, samples_count}'
echo ""

# Test 6: Train baseline - Error case
echo "❌ Test 6: Train baseline for invalid machine (should fail gracefully)"
echo "------------------------------------------------------------------------"
curl -s -X POST "${API_BASE}/ovos/train-baseline" \
  -H "Content-Type: application/json" \
  -d '{"seu_name": "InvalidMachine", "energy_source": "electricity", "features": [], "year": 2025}' | \
  jq '{success, message, error_details}'
echo ""

# Test 7: List trained machines
echo "📊 Test 7: List machines with trained baselines"
echo "------------------------------------------------"
curl -s "${API_BASE}/ovos/seus" | jq '{trained: [.seus[] | select(.baseline_year != null) | {name, r_squared, baseline_year}]}'
echo ""

# Test 8: Train natural gas baseline
echo "🔥 Test 8: Train baseline for Boiler-1 Natural Gas Burner"
echo "----------------------------------------------------------"
curl -s -X POST "${API_BASE}/ovos/train-baseline" \
  -H "Content-Type: application/json" \
  -d '{"seu_name": "Boiler-1 Natural Gas Burner", "energy_source": "natural_gas", "features": [], "year": 2025}' | \
  jq '{success, message, r_squared, samples_count}'
echo ""

echo "✅ All tests completed!"
echo ""
echo "📝 What to check:"
echo "  - All tests should return valid JSON"
echo "  - Test 1 should show 10 machines"
echo "  - Test 2 should show 4 energy sources"
echo "  - Test 5 should have success: true"
echo "  - Test 6 should have success: false with helpful message"
echo "  - Test 7 should show machines with R² values"
echo ""
echo "If all tests pass, backend is ready for OVOS integration! 🚀"
