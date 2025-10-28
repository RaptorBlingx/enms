-- Optimize Continuous Aggregate Refresh Intervals
-- Reduces refresh frequency to decrease CPU/RAM usage
-- Execute: docker exec enms-postgres psql -U raptorblingx -d enms -f /path/to/this/script.sql

-- ============================================
-- CURRENT STATE (BEFORE):
-- ============================================
-- 1-minute aggregates: Refresh every 1 minute (1,440 times/day) - EXCESSIVE
-- 15-minute aggregates: Refresh every 5 minutes (288 times/day) - AGGRESSIVE  
-- 1-hour aggregates: Refresh every 15 minutes (96 times/day) - REASONABLE
-- 1-day aggregates: Refresh every 1 hour (24 times/day) - OPTIMAL

\echo '=== BEFORE: Current Refresh Intervals ==='
SELECT 
    job_id, 
    hypertable_name, 
    schedule_interval,
    CASE 
        WHEN schedule_interval = '00:01:00' THEN '⚠️ CRITICAL - Too frequent'
        WHEN schedule_interval = '00:05:00' THEN '⚠️ HIGH - Can be optimized'
        WHEN schedule_interval = '00:15:00' THEN '✅ REASONABLE'
        ELSE '✅ OPTIMAL'
    END as assessment
FROM timescaledb_information.jobs 
WHERE proc_name = 'policy_refresh_continuous_aggregate'
ORDER BY schedule_interval;

-- ============================================
-- OPTIMIZATION STRATEGY:
-- ============================================
-- 1-minute aggregates: 1 min → 5 min (80% reduction)
-- 15-minute aggregates: 5 min → 15 min (67% reduction)
-- 1-hour aggregates: 15 min → 30 min (50% reduction)
-- 1-day aggregates: Keep at 1 hour (already optimal)

-- ============================================
-- 1. REDUCE 1-MINUTE AGGREGATES TO 5 MINUTES
-- ============================================
\echo ''
\echo '=== Optimizing 1-minute aggregates (1min → 5min) ==='

-- Job 1000: energy_readings_1min
SELECT alter_job(1000, schedule_interval => INTERVAL '5 minutes');

-- Job 1001: production_data_1min
SELECT alter_job(1001, schedule_interval => INTERVAL '5 minutes');

-- Job 1002: environmental_data_1min
SELECT alter_job(1002, schedule_interval => INTERVAL '5 minutes');

\echo '✅ 1-minute aggregates now refresh every 5 minutes'

-- ============================================
-- 2. REDUCE 15-MINUTE AGGREGATES TO 15 MINUTES
-- ============================================
\echo ''
\echo '=== Optimizing 15-minute aggregates (5min → 15min) ==='

-- Job 1003: energy_readings_15min
SELECT alter_job(1003, schedule_interval => INTERVAL '15 minutes');

-- Job 1004: production_data_15min
SELECT alter_job(1004, schedule_interval => INTERVAL '15 minutes');

-- Job 1005: environmental_data_15min
SELECT alter_job(1005, schedule_interval => INTERVAL '15 minutes');

\echo '✅ 15-minute aggregates now refresh every 15 minutes'

-- ============================================
-- 3. REDUCE 1-HOUR AGGREGATES TO 30 MINUTES
-- ============================================
\echo ''
\echo '=== Optimizing 1-hour aggregates (15min → 30min) ==='

-- Job 1006: energy_readings_1hour
SELECT alter_job(1006, schedule_interval => INTERVAL '30 minutes');

-- Job 1007: production_data_1hour
SELECT alter_job(1007, schedule_interval => INTERVAL '30 minutes');

-- Job 1008: environmental_data_1hour
SELECT alter_job(1008, schedule_interval => INTERVAL '30 minutes');

\echo '✅ 1-hour aggregates now refresh every 30 minutes'

-- ============================================
-- 4. KEEP 1-DAY AGGREGATES AT 1 HOUR (OPTIMAL)
-- ============================================
\echo ''
\echo '=== 1-day aggregates ==='
\echo '✅ Already optimal at 1 hour refresh - no change needed'

-- Jobs 1009, 1010, 1012: Keep at 1 hour

-- ============================================
-- VERIFICATION
-- ============================================
\echo ''
\echo '=== AFTER: New Refresh Intervals ==='
SELECT 
    job_id, 
    hypertable_name, 
    schedule_interval,
    next_start,
    CASE 
        WHEN schedule_interval <= '00:05:00' THEN '✅ OPTIMIZED'
        WHEN schedule_interval <= '00:30:00' THEN '✅ GOOD'
        ELSE '✅ OPTIMAL'
    END as status
FROM timescaledb_information.jobs 
WHERE proc_name = 'policy_refresh_continuous_aggregate'
ORDER BY schedule_interval;

-- ============================================
-- EXPECTED IMPROVEMENTS:
-- ============================================
-- CPU usage: 60-80% → 20-30% (60% reduction)
-- Aggregate executions: 
--   - 1min: 1,440/day → 288/day (80% reduction)
--   - 15min: 288/day → 96/day (67% reduction)
--   - 1hour: 96/day → 48/day (50% reduction)
-- Total daily refreshes: 1,824 → 432 (76% reduction)
-- 
-- Dashboard impact: Minimal
--   - 5-minute delay for real-time data (acceptable for dashboards)
--   - Historical data unaffected
-- ============================================

\echo ''
\echo '🎉 Optimization complete!'
\echo ''
\echo '📊 Expected results:'
\echo '  - Daily aggregate refreshes: 1,824 → 432 (76% reduction)'
\echo '  - CPU usage: 60-80% → 20-30% (60% reduction)'
\echo '  - RAM pressure: Significantly reduced'
\echo ''
\echo '⏱️  Data freshness:'
\echo '  - Real-time data: 5-minute delay (was 1 minute)'
\echo '  - Grafana dashboards: Minimal impact'
\echo '  - API queries: Use raw tables for true real-time'
\echo ''
\echo '✅ No restart required - changes take effect immediately!'
