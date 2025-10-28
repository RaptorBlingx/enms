#!/bin/bash
# Phase 1: Complete Data Cleanup and Baseline Retraining
# Orchestrates all Phase 1 steps in sequence
# Date: October 24, 2025

set -e

echo ""
echo "========================================================================="
echo "🚀 Phase 1: Data Cleanup & Real Baseline Training"
echo "========================================================================="
echo ""
echo "This script will:"
echo "  1. Archive backfilled data (Jan 2024 - Sep 2025)"
echo "  2. Update SEU baseline periods (Oct 7-21, 2024)"
echo "  3. Retrain all 7 electricity SEUs on real data"
echo "  4. Validate training results"
echo ""
echo "Estimated time: ~40 minutes"
echo "Risk level: Low (data is archived, not deleted)"
echo ""

# Confirm before proceeding
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "========================================================================="
echo "Step 1/4: Archive Backfilled Data"
echo "========================================================================="
echo ""

docker exec -i enms-postgres psql -U raptorblingx -d enms < scripts/phase1-cleanup-backfill.sql

if [ $? -ne 0 ]; then
    echo "❌ Step 1 failed! Check logs above."
    exit 1
fi

echo ""
echo "✅ Step 1 complete: Backfilled data archived"
echo ""

sleep 2

echo "========================================================================="
echo "Step 2/4: Update SEU Baseline Metadata"
echo "========================================================================="
echo ""

docker exec -i enms-postgres psql -U raptorblingx -d enms < scripts/phase1-update-seus.sql

if [ $? -ne 0 ]; then
    echo "❌ Step 2 failed! Check logs above."
    exit 1
fi

echo ""
echo "✅ Step 2 complete: SEU baseline periods updated"
echo ""

sleep 2

echo "========================================================================="
echo "Step 3/4: Retrain All SEU Baselines"
echo "========================================================================="
echo ""

bash scripts/retrain-real-baselines.sh

if [ $? -ne 0 ]; then
    echo "❌ Step 3 failed! Check logs above."
    exit 1
fi

echo ""
echo "✅ Step 3 complete: All SEUs retrained"
echo ""

sleep 2

echo "========================================================================="
echo "Step 4/4: Validate Training Results"
echo "========================================================================="
echo ""

echo "📊 SEU Baseline Quality:"
echo ""
docker exec enms-postgres psql -U raptorblingx -d enms -c "
SELECT 
  name,
  r_squared,
  rmse,
  TO_CHAR(trained_at, 'YYYY-MM-DD HH24:MI') as trained_at
FROM seus
WHERE energy_source_id = (SELECT id FROM energy_sources WHERE name = 'electricity')
ORDER BY r_squared DESC;
"

echo ""
echo "📈 Training Data Statistics:"
echo ""
docker exec enms-postgres psql -U raptorblingx -d enms -c "
SELECT 
  s.name,
  COUNT(*) as training_samples,
  MIN(er.time) as first_sample,
  MAX(er.time) as last_sample
FROM energy_readings er
JOIN machines m ON er.machine_id = m.id
JOIN seus s ON m.id = ANY(s.machine_ids)
WHERE er.time BETWEEN '2024-10-07' AND '2024-10-21'
  AND s.energy_source_id = (SELECT id FROM energy_sources WHERE name = 'electricity')
GROUP BY s.name
ORDER BY training_samples DESC;
"

echo ""
echo "========================================================================="
echo "🎉 Phase 1 Complete!"
echo "========================================================================="
echo ""
echo "Summary:"
echo "  ✅ Backfilled data archived to demo_archive schema"
echo "  ✅ Only real simulator data remains (Oct 7-24, 2025)"
echo "  ✅ All 7 SEUs trained on 14 days of real data"
echo "  ✅ Baselines ready for performance comparison"
echo ""
echo "Next Steps:"
echo "  1. Generate performance reports: bash scripts/phase1-generate-reports.sh"
echo "  2. Test OVOS endpoints: bash scripts/phase2-test-ovos.sh"
echo "  3. Demo to Mr. Umut: Show voice training + real results"
echo ""
echo "Rollback (if needed):"
echo "  - Restore backfilled data: psql < scripts/restore-from-archive.sql"
echo ""
