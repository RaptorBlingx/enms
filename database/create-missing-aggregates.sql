-- Create Missing Continuous Aggregates
-- This script manually creates the 15-minute, 1-hour, and 1-day aggregates
-- that were supposed to be created during database initialization

\echo 'Creating missing continuous aggregates...'

-- ============================================================================
-- 15-MINUTE AGGREGATES
-- ============================================================================

\echo 'Creating 15-minute aggregates...'

CREATE MATERIALIZED VIEW IF NOT EXISTS energy_readings_15min
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('15 minutes', bucket) AS bucket,
    machine_id,
    
    AVG(avg_power_kw) AS avg_power_kw,
    MIN(min_power_kw) AS min_power_kw,
    MAX(max_power_kw) AS max_power_kw,
    MAX(max_power_kw) AS peak_demand_kw,
    
    SUM(total_energy_kwh) AS total_energy_kwh,
    
    AVG(avg_voltage_v) AS avg_voltage_v,
    AVG(avg_current_a) AS avg_current_a,
    AVG(avg_power_factor) AS avg_power_factor,
    
    CASE 
        WHEN MAX(max_power_kw) > 0 THEN AVG(avg_power_kw) / MAX(max_power_kw)
        ELSE 0
    END AS load_factor,
    
    SUM(reading_count) AS total_readings
    
FROM energy_readings_1min
GROUP BY bucket, machine_id
WITH NO DATA;

\echo '✓ energy_readings_15min created'

CREATE MATERIALIZED VIEW IF NOT EXISTS production_data_15min
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('15 minutes', bucket) AS bucket,
    machine_id,
    
    SUM(total_production_count) AS total_production_count,
    SUM(total_production_good) AS total_production_good,
    SUM(total_production_bad) AS total_production_bad,
    
    AVG(avg_throughput) AS avg_throughput,
    AVG(avg_speed_percent) AS avg_speed_percent,
    
    SUM(total_downtime_seconds) AS total_downtime_seconds,
    
    SUM(reading_count) AS total_readings
    
FROM production_data_1min
GROUP BY bucket, machine_id
WITH NO DATA;

\echo '✓ production_data_15min created'

-- ============================================================================
-- 1-HOUR AGGREGATES
-- ============================================================================

\echo 'Creating 1-hour aggregates...'

CREATE MATERIALIZED VIEW IF NOT EXISTS energy_readings_1hour
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', bucket) AS bucket,
    machine_id,
    
    AVG(avg_power_kw) AS avg_power_kw,
    MIN(min_power_kw) AS min_power_kw,
    MAX(max_power_kw) AS max_power_kw,
    MAX(peak_demand_kw) AS peak_demand_kw,
    
    SUM(total_energy_kwh) AS total_energy_kwh,
    
    AVG(avg_voltage_v) AS avg_voltage_v,
    AVG(avg_current_a) AS avg_current_a,
    AVG(avg_power_factor) AS avg_power_factor,
    
    AVG(load_factor) AS avg_load_factor,
    
    SUM(total_readings) AS total_readings
    
FROM energy_readings_15min
GROUP BY bucket, machine_id
WITH NO DATA;

\echo '✓ energy_readings_1hour created'

CREATE MATERIALIZED VIEW IF NOT EXISTS production_data_1hour
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', bucket) AS bucket,
    machine_id,
    
    SUM(total_production_count) AS total_production_count,
    SUM(total_production_good) AS total_production_good,
    SUM(total_production_bad) AS total_production_bad,
    
    CASE 
        WHEN SUM(total_production_count) > 0 THEN 
            (SUM(total_production_good)::DECIMAL / SUM(total_production_count)) * 100
        ELSE 0
    END AS quality_percent,
    
    AVG(avg_throughput) AS avg_throughput_units_per_hour,
    AVG(avg_speed_percent) AS avg_speed_percent,
    
    SUM(total_downtime_seconds) AS total_downtime_seconds,
    
    CASE 
        WHEN (3600 - SUM(total_downtime_seconds)) > 0 THEN
            ((3600 - SUM(total_downtime_seconds))::DECIMAL / 3600) * 100
        ELSE 0
    END AS availability_percent,
    
    SUM(total_readings) AS total_readings
    
FROM production_data_15min
GROUP BY bucket, machine_id
WITH NO DATA;

\echo '✓ production_data_1hour created'

-- Also create environmental_data hourly (not in original but should exist)
CREATE MATERIALIZED VIEW IF NOT EXISTS environmental_data_1hour
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', bucket) AS bucket,
    machine_id,
    
    AVG(avg_outdoor_temp_c) AS avg_outdoor_temp_c,
    AVG(avg_indoor_temp_c) AS avg_indoor_temp_c,
    AVG(avg_machine_temp_c) AS avg_machine_temp_c,
    AVG(avg_outdoor_humidity) AS avg_outdoor_humidity,
    AVG(avg_indoor_humidity) AS avg_indoor_humidity,
    AVG(avg_pressure_bar) AS avg_pressure_bar,
    MIN(min_pressure_bar) AS min_pressure_bar,
    MAX(max_pressure_bar) AS max_pressure_bar,
    AVG(avg_flow_rate_m3h) AS avg_flow_rate_m3h,
    AVG(avg_supply_air_temp_c) AS avg_supply_air_temp_c,
    AVG(avg_return_air_temp_c) AS avg_return_air_temp_c,
    AVG(avg_cop) AS avg_cop,
    AVG(avg_vibration_mm_s) AS avg_vibration_mm_s,
    MAX(max_vibration_mm_s) AS max_vibration_mm_s,
    SUM(reading_count) AS total_readings
    
FROM environmental_data_1min
GROUP BY bucket, machine_id
WITH NO DATA;

\echo '✓ environmental_data_1hour created'

-- ============================================================================
-- REFRESH POLICIES
-- ============================================================================

\echo 'Setting up refresh policies...'

SELECT add_continuous_aggregate_policy('energy_readings_15min',
    start_offset => INTERVAL '6 hours',
    end_offset => INTERVAL '15 minutes',
    schedule_interval => INTERVAL '5 minutes');

SELECT add_continuous_aggregate_policy('production_data_15min',
    start_offset => INTERVAL '6 hours',
    end_offset => INTERVAL '15 minutes',
    schedule_interval => INTERVAL '5 minutes');

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

\echo '✓ Refresh policies set'

-- Refresh all aggregates now
\echo 'Refreshing aggregates with existing data...'

CALL refresh_continuous_aggregate('energy_readings_15min', NULL, NULL);
CALL refresh_continuous_aggregate('production_data_15min', NULL, NULL);
CALL refresh_continuous_aggregate('energy_readings_1hour', NULL, NULL);
CALL refresh_continuous_aggregate('production_data_1hour', NULL, NULL);
CALL refresh_continuous_aggregate('environmental_data_1hour', NULL, NULL);

\echo '✓ All aggregates refreshed'
\echo 'Done!'
