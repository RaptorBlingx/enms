-- Phase 1 Step 1.2: Update SEU Baseline Metadata
-- Purpose: Set baseline period to first 14 days of real simulator data
-- Date: October 24, 2025

-- Update all electricity SEUs to use real data period
UPDATE seus SET
    baseline_year = 2025,
    baseline_start_date = '2025-10-10',
    baseline_end_date = '2025-10-21',  -- 11 days training period
    trained_at = NULL,  -- Force retrain
    r_squared = NULL,
    rmse = NULL,
    mae = NULL,
    regression_coefficients = NULL,
    intercept = NULL
WHERE energy_source_id = (SELECT id FROM energy_sources WHERE name = 'electricity');

-- Show updated SEUs
SELECT 
    name,
    baseline_year,
    baseline_start_date,
    baseline_end_date,
    baseline_end_date - baseline_start_date as baseline_days,
    trained_at,
    r_squared
FROM seus
WHERE energy_source_id = (SELECT id FROM energy_sources WHERE name = 'electricity')
ORDER BY name;

-- Verify data exists for training period
DO $$
DECLARE
    seu_record RECORD;
    sample_count INTEGER;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=== Verify Training Data Availability ===';
    
    FOR seu_record IN 
        SELECT s.name, s.machine_ids
        FROM seus s
        WHERE s.energy_source_id = (SELECT id FROM energy_sources WHERE name = 'electricity')
        ORDER BY s.name
    LOOP
        SELECT COUNT(*) INTO sample_count
        FROM energy_readings
        WHERE machine_id = ANY(seu_record.machine_ids)
          AND time BETWEEN '2025-10-10' AND '2025-10-21';
        
        RAISE NOTICE 'SEU: % - % training samples available', 
            RPAD(seu_record.name, 25), 
            sample_count;
    END LOOP;
    
    RAISE NOTICE '';
END $$;

RAISE NOTICE '✓ Phase 1 Step 1.2 complete: SEU baseline periods updated to Oct 7-21';
