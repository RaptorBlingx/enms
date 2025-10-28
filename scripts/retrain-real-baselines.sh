#!/bin/bash
# Phase 1 Step 1.3: Retrain All SEU Baselines on Real Data
# Purpose: Train baselines using Oct 7-21 real simulator data (not backfilled 2024 data)
# Date: October 24, 2025

set -e

echo ""
echo "=========================================="
echo "🔄 Retraining SEU Baselines on Real Data"
echo "=========================================="
echo ""
echo "Training Period: Oct 10-24, 2025 (14 days)"
echo "Expected Samples: ~800k per SEU (2.26 samples/sec × 14 days)"
echo ""

BASELINE_START="2025-10-10"
BASELINE_END="2025-10-24"
API_URL="http://localhost:8001/api/v1/baseline/seu/train"

# Get all electricity SEUs
echo "📋 Fetching electricity SEUs..."
SEUS=$(docker exec enms-postgres psql -U raptorblingx -d enms -t -c "
  SELECT id FROM seus 
  WHERE energy_source_id = (SELECT id FROM energy_sources WHERE name = 'electricity')
  ORDER BY name
")

if [ -z "$SEUS" ]; then
  echo "❌ No electricity SEUs found!"
  exit 1
fi

SEU_COUNT=$(echo "$SEUS" | wc -l)
echo "✓ Found $SEU_COUNT electricity SEUs"
echo ""

# Train each SEU
TRAINED=0
FAILED=0

for seu_id in $SEUS; do
  seu_id=$(echo $seu_id | xargs)  # Trim whitespace
  
  # Get SEU name
  SEU_NAME=$(docker exec enms-postgres psql -U raptorblingx -d enms -t -c "SELECT name FROM seus WHERE id = '$seu_id';" | xargs)
  
  echo "=========================================="
  echo "Training: $SEU_NAME"
  echo "SEU ID: $seu_id"
  echo "=========================================="
  
  # Call training API
  RESPONSE=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "{
      \"seu_id\": \"$seu_id\",
      \"baseline_year\": 2025,
      \"start_date\": \"$BASELINE_START\",
      \"end_date\": \"$BASELINE_END\",
      \"features\": [\"production_count\", \"outdoor_temp_c\"]
    }")
  
  # Check if successful
  SUCCESS=$(echo "$RESPONSE" | jq -r '.success // false')
  
  if [ "$SUCCESS" = "true" ]; then
    R2=$(echo "$RESPONSE" | jq -r '.r_squared // 0')
    RMSE=$(echo "$RESPONSE" | jq -r '.rmse // 0')
    SAMPLES=$(echo "$RESPONSE" | jq -r '.samples_count // 0')
    
    echo "✅ SUCCESS"
    echo "   R² Score: $R2"
    echo "   RMSE: $RMSE"
    echo "   Samples: $SAMPLES"
    TRAINED=$((TRAINED + 1))
  else
    ERROR=$(echo "$RESPONSE" | jq -r '.error // "Unknown error"')
    echo "❌ FAILED: $ERROR"
    FAILED=$((FAILED + 1))
  fi
  
  echo ""
  sleep 2  # Rate limiting
done

echo "=========================================="
echo "📊 Training Summary"
echo "=========================================="
echo "Total SEUs: $SEU_COUNT"
echo "✅ Trained: $TRAINED"
echo "❌ Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
  echo "🎉 All SEUs trained successfully!"
  echo ""
  echo "Next steps:"
  echo "1. Verify baselines: docker exec enms-postgres psql -U raptorblingx -d enms -c \"SELECT name, r_squared, trained_at FROM seus ORDER BY r_squared DESC;\""
  echo "2. Generate reports: curl -X POST http://localhost:8001/api/v1/reports/generate-monthly -H 'Content-Type: application/json' -d '{\"year\":2025,\"month\":10,\"baseline_year\":2024}'"
  exit 0
else
  echo "⚠️  Some SEUs failed to train. Check API logs for details."
  exit 1
fi
