# EnMS Database Schema

## Overview

This directory contains the complete PostgreSQL + TimescaleDB database schema for the Energy Management System (EnMS).

## Structure

```
database/
├── init/                           # Initialization scripts (executed in order)
│   ├── 01-extensions.sql          # Enable extensions (TimescaleDB, UUID, etc.)
│   ├── 02-schema.sql              # Create all tables and constraints
│   ├── 03-timescaledb-setup.sql   # Configure hypertables and continuous aggregates
│   ├── 04-functions.sql           # KPI calculation functions
│   ├── 05-views.sql               # Common query views
│   └── 06-seed-data.sql           # Initial sample data
├── postgresql.conf                 # Optimized PostgreSQL configuration
├── migrations/                     # Future schema changes (empty)
└── backup/                         # Backup scripts (empty)
```

## Initialization Order

The SQL scripts in `init/` are executed **automatically** in alphabetical order when the PostgreSQL container starts for the first time.

### Execution Sequence:

1. **01-extensions.sql** - Enables required PostgreSQL extensions
2. **02-schema.sql** - Creates all tables, constraints, and triggers
3. **03-timescaledb-setup.sql** - Converts tables to hypertables and sets up continuous aggregates
4. **04-functions.sql** - Creates SQL functions for KPI calculations
5. **05-views.sql** - Creates views for common queries
6. **06-seed-data.sql** - Populates initial factories and machines

## Database Schema

### Core Tables

#### Dimension Tables
- **factories** - Industrial facilities
- **machines** - SEUs (Significant Energy Users)

#### Fact Tables (Hypertables)
- **energy_readings** - Time-series power and energy data
- **production_data** - Time-series production metrics
- **environmental_data** - Time-series environmental conditions

#### State Tables
- **machine_status** - Current state of each machine

#### Analytics Tables
- **energy_baselines** - Trained ML models (EnB)
- **anomalies** - Detected anomalies

#### Configuration Tables
- **energy_tariffs** - Electricity pricing
- **carbon_factors** - CO2 emission factors

#### System Tables
- **audit_log** - System audit trail

### TimescaleDB Features

#### Hypertables (Automatic Partitioning)
- `energy_readings` - Partitioned by time (1-day chunks)
- `production_data` - Partitioned by time (1-day chunks)
- `environmental_data` - Partitioned by time (1-day chunks)

#### Continuous Aggregates
Pre-computed rollups for fast queries:
- **1 minute** - Refreshed every 1 minute
- **15 minutes** - Refreshed every 5 minutes
- **1 hour** - Refreshed every 15 minutes
- **1 day** - Refreshed every 1 hour

#### Data Retention
- Raw data: Kept for **90 days**
- Continuous aggregates: Kept **indefinitely**

#### Compression
- Automatic compression after **7 days**
- Compression ratio: ~90% storage savings

## KPI Functions

### Available Functions

```sql
-- Specific Energy Consumption
SELECT * FROM calculate_sec(machine_id, start_time, end_time);

-- Peak Demand
SELECT * FROM calculate_peak_demand(machine_id, start_time, end_time);

-- Load Factor
SELECT * FROM calculate_load_factor(machine_id, start_time, end_time);

-- Energy Cost
SELECT * FROM calculate_energy_cost(machine_id, start_time, end_time);

-- Carbon Intensity
SELECT * FROM calculate_carbon_intensity(machine_id, start_time, end_time);

-- All KPIs at once
SELECT * FROM calculate_all_kpis(machine_id, start_time, end_time);
```

### Helper Functions

```sql
-- Operating hours breakdown
SELECT * FROM get_machine_operating_hours(machine_id, start_time, end_time);

-- Factory summary
SELECT * FROM get_factory_summary(factory_id, start_time, end_time);
```

## Sample Data

The seed data script creates:

### Factories
1. **Demo Manufacturing Plant** (Silicon Valley, CA)
2. **European Production Facility** (Munich, Germany)

### Machines (SEUs)

#### Demo Manufacturing Plant:
| Machine | Type | Data Interval | MQTT Topic |
|---------|------|---------------|------------|
| Compressor-1 | compressor | 1 second | factory/demo/compressor-1 |
| HVAC-Main | hvac | 10 seconds | factory/demo/hvac-main |
| Conveyor-A | motor | 10 seconds | factory/demo/conveyor-a |
| Hydraulic-Pump-1 | pump | 30 seconds | factory/demo/hydraulic-pump-1 |
| Injection-Molding-1 | injection_molding | 30 seconds | factory/demo/injection-molding-1 |

#### European Production Facility:
| Machine | Type | Data Interval | MQTT Topic |
|---------|------|---------------|------------|
| Compressor-EU-1 | compressor | 1 second | factory/europe/compressor-1 |
| HVAC-EU-North | hvac | 10 seconds | factory/europe/hvac-north |

### Machine IDs (for testing)

```
Demo Plant:
  - Compressor-1:        c0000000-0000-0000-0000-000000000001
  - HVAC-Main:           c0000000-0000-0000-0000-000000000002
  - Conveyor-A:          c0000000-0000-0000-0000-000000000003
  - Hydraulic-Pump-1:    c0000000-0000-0000-0000-000000000004
  - Injection-Molding-1: c0000000-0000-0000-0000-000000000005

European Plant:
  - Compressor-EU-1:     c0000000-0000-0000-0000-000000000006
  - HVAC-EU-North:       c0000000-0000-0000-0000-000000000007
```

## Testing the Database

### Connect to Database

```bash
# Via Docker
docker-compose exec postgres psql -U enms_user -d enms

# Direct connection
psql -h localhost -U enms_user -d enms
```

### Sample Queries

```sql
-- List all factories
SELECT * FROM factories;

-- List all machines
SELECT * FROM v_machines_current_status;

-- Check hypertables
SELECT * FROM timescaledb_information.hypertables;

-- Check continuous aggregates
SELECT * FROM timescaledb_information.continuous_aggregates;

-- Test KPI function
SELECT * FROM calculate_all_kpis(
    'c0000000-0000-0000-0000-000000000001',
    NOW() - INTERVAL '24 hours',
    NOW()
);
```

## Performance Tuning

The `postgresql.conf` file is optimized for:
- 8GB RAM server
- SSD storage
- Mixed read/write workload
- Time-series data patterns

### Key Settings:
- `shared_buffers = 2GB` (25% of RAM)
- `effective_cache_size = 6GB` (75% of RAM)
- `work_mem = 64MB`
- `random_page_cost = 1.1` (optimized for SSD)

Adjust these values based on your server's resources.

## Backup and Recovery

### Backup

```bash
# Full backup
docker-compose exec postgres pg_dump -U enms_user enms > backup.sql

# Or use the backup script (coming soon)
./scripts/backup.sh
```

### Restore

```bash
# Restore from backup
docker-compose exec -T postgres psql -U enms_user enms < backup.sql

# Or use the restore script (coming soon)
./scripts/restore.sh backup.sql
```

## Monitoring

### Check Database Size

```sql
SELECT pg_size_pretty(pg_database_size('enms')) AS database_size;
```

### Check Table Sizes

```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Check Compression Stats

```sql
SELECT * FROM timescaledb_information.compression_settings;
```

### Monitor Query Performance

```sql
-- Top 10 slowest queries
SELECT
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

## Troubleshooting

### Database Won't Start

```bash
# Check logs
docker-compose logs postgres

# Check initialization scripts
docker-compose exec postgres ls -la /docker-entrypoint-initdb.d/
```

### Slow Queries

```bash
# Enable query logging
# Edit postgresql.conf:
log_min_duration_statement = 100  # Log queries > 100ms

# Restart database
docker-compose restart postgres
```

### High Memory Usage

```bash
# Check active connections
docker-compose exec postgres psql -U enms_user -d enms -c "SELECT count(*) FROM pg_stat_activity;"

# Consider reducing max_connections or adjusting work_mem
```

## Next Steps

After database setup:
1. ✅ Database schema is ready
2. ⏳ Build simulator to generate data
3. ⏳ Configure Node-RED to ingest data
4. ⏳ Set up Grafana dashboards
5. ⏳ Develop analytics service

---

**Database Schema Version**: 1.0.0  
**Last Updated**: 2025-10-08  
**Status**: Production Ready ✅
