-- Phase 1 Step 1.1: Archive Backfilled Data
-- Purpose: Move fake hourly backfill data to archive schema, keep only real simulator data
-- Safe: Creates archive before deleting (can restore if needed)
-- Date: October 24, 2025

-- Create archive schema
CREATE SCHEMA IF NOT EXISTS demo_archive;

-- Archive backfilled energy readings (Jan 2024 - Sep 2025, hourly intervals)
CREATE TABLE demo_archive.energy_readings_backfill AS 
SELECT * FROM energy_readings WHERE time < '2025-10-10'::timestamptz;

-- Archive backfilled production data
CREATE TABLE demo_archive.production_data_backfill AS 
SELECT * FROM production_data WHERE time < '2025-10-10'::timestamptz;

-- Archive backfilled environmental data
CREATE TABLE demo_archive.environmental_data_backfill AS 
SELECT * FROM environmental_data WHERE time < '2025-10-10'::timestamptz;

-- Show archive statistics
DO $$
DECLARE
    energy_count INTEGER;
    production_count INTEGER;
    env_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO energy_count FROM demo_archive.energy_readings_backfill;
    SELECT COUNT(*) INTO production_count FROM demo_archive.production_data_backfill;
    SELECT COUNT(*) INTO env_count FROM demo_archive.environmental_data_backfill;
    
    RAISE NOTICE '✓ Archived % energy_readings', energy_count;
    RAISE NOTICE '✓ Archived % production_data', production_count;
    RAISE NOTICE '✓ Archived % environmental_data', env_count;
END $$;

-- Delete backfilled data from main tables
DELETE FROM energy_readings WHERE time < '2025-10-10'::timestamptz;
DELETE FROM production_data WHERE time < '2025-10-10'::timestamptz;
DELETE FROM environmental_data WHERE time < '2025-10-10'::timestamptz;

-- Show remaining data statistics
DO $$
DECLARE
    energy_count INTEGER;
    production_count INTEGER;
    env_count INTEGER;
    oldest_time TIMESTAMPTZ;
    newest_time TIMESTAMPTZ;
    samples_per_sec NUMERIC;
BEGIN
    SELECT COUNT(*), MIN(time), MAX(time) 
    INTO energy_count, oldest_time, newest_time 
    FROM energy_readings;
    
    SELECT ROUND(COUNT(*)::NUMERIC / EXTRACT(EPOCH FROM (MAX(time) - MIN(time))), 2)
    INTO samples_per_sec
    FROM energy_readings;
    
    SELECT COUNT(*) INTO production_count FROM production_data;
    SELECT COUNT(*) INTO env_count FROM environmental_data;
    
    RAISE NOTICE '';
    RAISE NOTICE '=== Remaining Real Simulator Data ===';
    RAISE NOTICE 'Energy readings: %', energy_count;
    RAISE NOTICE 'Production data: %', production_count;
    RAISE NOTICE 'Environmental data: %', env_count;
    RAISE NOTICE 'Date range: % to %', oldest_time, newest_time;
    RAISE NOTICE 'Sample rate: % samples/sec', samples_per_sec;
    RAISE NOTICE '';
END $$;

-- Vacuum to reclaim disk space
VACUUM FULL energy_readings;
VACUUM FULL production_data;
VACUUM FULL environmental_data;

RAISE NOTICE '✓ Phase 1 Step 1.1 complete: Backfilled data archived, real data remains';
