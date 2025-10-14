-- ============================================================================
-- TimescaleDB Continuous Aggregates - CORRECTED VERSION
-- ============================================================================
-- Issue: Original design attempted to create continuous aggregates FROM
--        other continuous aggregates, which TimescaleDB does NOT support.
--
-- Solution: All continuous aggregates now query directly from hypertables.
-- ============================================================================
-- Author: System Architect (Claude Sonnet 4.5)
-- Date: October 11, 2025
-- Migration: Run this AFTER dropping failed aggregates
-- ============================================================================

\echo ''
\echo '=========================================='
\echo 'FIXING CONTINUOUS AGGREGATES'
\echo '=========================================='
\echo ''

-- ============================================================================
-- STEP 1: Drop failed aggregates (if they exist)
-- ============================================================================

\echo 'Dropping failed continuous aggregates...'

DROP MATERIALIZED VIEW IF EXISTS energy_readings_1day CASCADE;
DROP MATERIALIZED VIEW IF EXISTS production_data_1day CASCADE;
DROP MATERIALIZED VIEW IF EXISTS environmental_data_1day CASCADE;

DROP MATERIALIZED VIEW IF EXISTS energy_readings_1hour CASCADE;
DROP MATERIALIZED VIEW IF EXISTS production_data_1hour CASCADE;
DROP MATERIALIZED VIEW IF EXISTS environmental_data_1hour CASCADE;

DROP MATERIALIZED VIEW IF EXISTS energy_readings_15min CASCADE;
DROP MATERIALIZED VIEW IF EXISTS production_data_15min CASCADE;
DROP MATERIALIZED VIEW IF EXISTS environmental_data_15min CASCADE;

\echo '✓ Old aggregates dropped'

-- ============================================================================
-- STEP 2: Create 15-minute aggregates FROM hypertables
-- ============================================================================

\echo 'Creating 15-minute continuous aggregates FROM hypertables...'

CREATE MATERIALIZED VIEW energy_readings_15min
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('15 minutes', time) AS bucket,
    machine_id,
    
    -- Power statistics
    AVG(power_kw) AS avg_power_kw,
    MIN(power_kw) AS min_power_kw,
    MAX(power_kw) AS max_power_kw,
    MAX(power_kw) AS peak_demand_kw,
    
    -- Energy (sum of 1-second readings * time interval)
    SUM(power_kw) / 3600 AS total_energy_kwh,  -- Convert kW*sec to kWh
    
    -- Electrical parameters
    AVG(voltage_v) AS avg_voltage_v,
    AVG(current_a) AS avg_current_a,
    AVG(power_factor) AS avg_power_factor,
    AVG(frequency_hz) AS avg_frequency_hz,
    
    -- Load factor
    CASE 
        WHEN MAX(power_kw) > 0 THEN AVG(power_kw) / MAX(power_kw)
        ELSE 0
    END AS load_factor,
    
    COUNT(*) AS total_readings
    
FROM energy_readings
GROUP BY bucket, machine_id
WITH NO DATA;

\echo '✓ energy_readings_15min created'

CREATE MATERIALIZED VIEW production_data_15min
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('15 minutes', time) AS bucket,
    machine_id,
    
    SUM(production_count) AS total_production_count,
    SUM(production_count_good) AS total_production_good,
    SUM(production_count_bad) AS total_production_bad,
    
    AVG(throughput_units_per_hour) AS avg_throughput,
    AVG(speed_percent) AS avg_speed_percent,
    
    SUM(downtime_seconds) AS total_downtime_seconds,
    
    COUNT(*) AS total_readings
    
FROM production_data
GROUP BY bucket, machine_id
WITH NO DATA;

\echo '✓ production_data_15min created'

CREATE MATERIALIZED VIEW environmental_data_15min
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('15 minutes', time) AS bucket,
    machine_id,
    
    AVG(outdoor_temp_c) AS avg_outdoor_temp_c,
    AVG(indoor_temp_c) AS avg_indoor_temp_c,
    AVG(machine_temp_c) AS avg_machine_temp_c,
    
    AVG(outdoor_humidity_percent) AS avg_outdoor_humidity,
    AVG(indoor_humidity_percent) AS avg_indoor_humidity,
    
    AVG(pressure_bar) AS avg_pressure_bar,
    MIN(pressure_bar) AS min_pressure_bar,
    MAX(pressure_bar) AS max_pressure_bar,
    
    AVG(flow_rate_m3h) AS avg_flow_rate_m3h,
    AVG(vibration_mm_s) AS avg_vibration_mm_s,
    
    COUNT(*) AS total_readings
    
FROM environmental_data
GROUP BY bucket, machine_id
WITH NO DATA;

\echo '✓ environmental_data_15min created'

-- ============================================================================
-- STEP 3: Create 1-hour aggregates FROM hypertables
-- ============================================================================

\echo 'Creating 1-hour continuous aggregates FROM hypertables...'

CREATE MATERIALIZED VIEW energy_readings_1hour
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', time) AS bucket,
    machine_id,
    
    AVG(power_kw) AS avg_power_kw,
    MIN(power_kw) AS min_power_kw,
    MAX(power_kw) AS max_power_kw,
    MAX(power_kw) AS peak_demand_kw,
    
    SUM(power_kw) / 3600 AS total_energy_kwh,
    
    AVG(voltage_v) AS avg_voltage_v,
    AVG(current_a) AS avg_current_a,
    AVG(power_factor) AS avg_power_factor,
    
    CASE 
        WHEN MAX(power_kw) > 0 THEN AVG(power_kw) / MAX(power_kw)
        ELSE 0
    END AS avg_load_factor,
    
    COUNT(*) AS total_readings
    
FROM energy_readings
GROUP BY bucket, machine_id
WITH NO DATA;

\echo '✓ energy_readings_1hour created'

CREATE MATERIALIZED VIEW production_data_1hour
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', time) AS bucket,
    machine_id,
    
    SUM(production_count) AS total_production_count,
    SUM(production_count_good) AS total_production_good,
    SUM(production_count_bad) AS total_production_bad,
    
    CASE 
        WHEN SUM(production_count) > 0 THEN 
            (SUM(production_count_good)::DECIMAL / SUM(production_count)) * 100
        ELSE 0
    END AS quality_percent,
    
    AVG(throughput_units_per_hour) AS avg_throughput,
    AVG(speed_percent) AS avg_speed_percent,
    
    SUM(downtime_seconds) AS total_downtime_seconds,
    
    CASE 
        WHEN (3600 - SUM(downtime_seconds)) > 0 THEN
            ((3600 - SUM(downtime_seconds))::DECIMAL / 3600) * 100
        ELSE 0
    END AS availability_percent,
    
    COUNT(*) AS total_readings
    
FROM production_data
GROUP BY bucket, machine_id
WITH NO DATA;

\echo '✓ production_data_1hour created'

CREATE MATERIALIZED VIEW environmental_data_1hour
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', time) AS bucket,
    machine_id,
    
    AVG(outdoor_temp_c) AS avg_outdoor_temp_c,
    AVG(indoor_temp_c) AS avg_indoor_temp_c,
    AVG(machine_temp_c) AS avg_machine_temp_c,
    
    AVG(outdoor_humidity_percent) AS avg_outdoor_humidity,
    AVG(indoor_humidity_percent) AS avg_indoor_humidity,
    
    AVG(pressure_bar) AS avg_pressure_bar,
    AVG(flow_rate_m3h) AS avg_flow_rate_m3h,
    AVG(vibration_mm_s) AS avg_vibration_mm_s,
    
    COUNT(*) AS total_readings
    
FROM environmental_data
GROUP BY bucket, machine_id
WITH NO DATA;

\echo '✓ environmental_data_1hour created'

-- ============================================================================
-- STEP 4: Create 1-day aggregates FROM hypertables
-- ============================================================================

\echo 'Creating 1-day continuous aggregates FROM hypertables...'

CREATE MATERIALIZED VIEW energy_readings_1day
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 day', time) AS bucket,
    machine_id,
    
    AVG(power_kw) AS avg_power_kw,
    MIN(power_kw) AS min_power_kw,
    MAX(power_kw) AS max_power_kw,
    MAX(power_kw) AS peak_demand_kw,
    
    SUM(power_kw) / 3600 AS total_energy_kwh,
    
    AVG(voltage_v) AS avg_voltage_v,
    AVG(power_factor) AS avg_power_factor,
    
    CASE 
        WHEN MAX(power_kw) > 0 THEN AVG(power_kw) / MAX(power_kw)
        ELSE 0
    END AS avg_load_factor,
    
    COUNT(*) AS total_readings
    
FROM energy_readings
GROUP BY bucket, machine_id
WITH NO DATA;

\echo '✓ energy_readings_1day created'

CREATE MATERIALIZED VIEW production_data_1day
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 day', time) AS bucket,
    machine_id,
    
    SUM(production_count) AS total_production_count,
    SUM(production_count_good) AS total_production_good,
    SUM(production_count_bad) AS total_production_bad,
    
    CASE 
        WHEN SUM(production_count) > 0 THEN 
            (SUM(production_count_good)::DECIMAL / SUM(production_count)) * 100
        ELSE 0
    END AS quality_percent,
    
    AVG(throughput_units_per_hour) AS avg_throughput,
    
    SUM(downtime_seconds) AS total_downtime_seconds,
    
    CASE 
        WHEN (86400 - SUM(downtime_seconds)) > 0 THEN
            ((86400 - SUM(downtime_seconds))::DECIMAL / 86400) * 100
        ELSE 0
    END AS availability_percent,
    
    COUNT(*) AS total_readings
    
FROM production_data
GROUP BY bucket, machine_id
WITH NO DATA;

\echo '✓ production_data_1day created'

-- ============================================================================
-- STEP 5: Set up refresh policies
-- ============================================================================

\echo 'Setting up refresh policies...'

-- 1-minute aggregates: refresh every 1 minute (keep existing)
-- Already created during initial setup

-- 15-minute aggregates: refresh every 5 minutes
SELECT add_continuous_aggregate_policy('energy_readings_15min',
    start_offset => INTERVAL '6 hours',
    end_offset => INTERVAL '15 minutes',
    schedule_interval => INTERVAL '5 minutes');

SELECT add_continuous_aggregate_policy('production_data_15min',
    start_offset => INTERVAL '6 hours',
    end_offset => INTERVAL '15 minutes',
    schedule_interval => INTERVAL '5 minutes');

SELECT add_continuous_aggregate_policy('environmental_data_15min',
    start_offset => INTERVAL '6 hours',
    end_offset => INTERVAL '15 minutes',
    schedule_interval => INTERVAL '5 minutes');

\echo '✓ 15-minute refresh policies set'

-- 1-hour aggregates: refresh every 15 minutes
SELECT add_continuous_aggregate_policy('energy_readings_1hour',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '15 minutes');

SELECT add_continuous_aggregate_policy('production_data_1hour',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '15 minutes');

SELECT add_continuous_aggregate_policy('environmental_data_1hour',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '15 minutes');

\echo '✓ 1-hour refresh policies set'

-- 1-day aggregates: refresh every hour
SELECT add_continuous_aggregate_policy('energy_readings_1day',
    start_offset => INTERVAL '7 days',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 hour');

SELECT add_continuous_aggregate_policy('production_data_1day',
    start_offset => INTERVAL '7 days',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 hour');

\echo '✓ 1-day refresh policies set'

-- ============================================================================
-- STEP 6: Initial materialization
-- ============================================================================

\echo 'Materializing aggregates (this may take a while)...'

-- Materialize with all available historical data
CALL refresh_continuous_aggregate('energy_readings_15min', NULL, NULL);
CALL refresh_continuous_aggregate('production_data_15min', NULL, NULL);
CALL refresh_continuous_aggregate('environmental_data_15min', NULL, NULL);

CALL refresh_continuous_aggregate('energy_readings_1hour', NULL, NULL);
CALL refresh_continuous_aggregate('production_data_1hour', NULL, NULL);
CALL refresh_continuous_aggregate('environmental_data_1hour', NULL, NULL);

CALL refresh_continuous_aggregate('energy_readings_1day', NULL, NULL);
CALL refresh_continuous_aggregate('production_data_1day', NULL, NULL);

\echo '✓ All aggregates materialized'

\echo ''
\echo '=========================================='
\echo 'CONTINUOUS AGGREGATES FIXED!'
\echo '=========================================='
\echo ''
\echo 'All aggregates now query directly from hypertables.'
\echo 'Hierarchy: hypertable → 15min, hypertable → 1hour, hypertable → 1day'
\echo ''
\echo 'Refresh policies:'
\echo '  - 15 minutes: every 5 minutes'
\echo '  - 1 hour: every 15 minutes'
\echo '  - 1 day: every 1 hour'
\echo ''
