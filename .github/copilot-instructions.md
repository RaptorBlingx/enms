# EnMS (Energy Management System) - AI Agent Instructions

## Project Overview
EnMS is a production-ready, dockerized energy management system for industrial facilities. Built with microservices architecture using FastAPI (Python), TimescaleDB, Node-RED, Grafana, and Nginx as API gateway. Part of WASABI Project for ISO 50001 compliance and OVOS voice integration.

## Architecture & Service Communication

### Core Services (all Docker containers)
- **nginx** (port 8080): API gateway routing `/api/{service}/*` → internal services
- **analytics** (port 8001): ML/KPI service (FastAPI) - baseline models, anomaly detection, forecasting
- **query-service** (port 8002): Query API for OVOS/NLP (FastAPI)
- **simulator** (port 8003): Factory data generator (FastAPI) - 5 machine types with variable intervals (1s, 10s, 30s)
- **postgres** (TimescaleDB): Hypertables for energy_readings, production_data, environmental_data
- **nodered** (port 1880): ETL pipeline - MQTT → PostgreSQL
- **grafana** (port 3000): Pre-provisioned dashboards with auto-backup to git every 10 min
- **redis**: Caching, pub/sub for real-time WebSocket events

**Critical**: External MQTT broker at `172.18.0.1:1883` (host broker, NOT containerized). Simulator publishes to `factory/{factory_id}/{machine_id}/{data_type}` topics.

### Database Patterns
- **Hypertables**: `energy_readings`, `production_data`, `environmental_data` (partitioned by time)
- **Continuous Aggregates**: `*_1min`, `*_15min`, `*_1hour`, `*_1day` (must use when querying aggregated data)
- **KPI Functions**: PostgreSQL functions in `database/init/04-functions.sql` - call via `SELECT calculate_all_kpis(...)`
- **Init Order**: Scripts in `database/init/` run alphabetically (01-extensions → 06-seed-data)

## Development Workflows

### Running Services
```bash
# Start all services
docker-compose up -d

# View logs (CRITICAL for debugging)
docker-compose logs -f analytics

# Restart single service
docker-compose restart analytics

# Database access
docker exec -it enms-postgres psql -U $POSTGRES_USER -d enms
```

### Testing Strategy
- **Integration tests**: `analytics/tests/test_ovos_endpoints.py` (async httpx client)
- **Run tests**: `docker-compose exec analytics pytest tests/ -v`
- **API testing**: Swagger UI at `http://localhost:8001/docs` (analytics), `http://localhost:8003/docs` (simulator)
- **Data verification**: Check `SELECT COUNT(*), MAX(time) FROM energy_readings` should show recent timestamps

### Critical Commands (Not in README)
```bash
# Backup Grafana dashboards to git (runs auto every 10 min via cron)
./scripts/backup-grafana-dashboards.sh

# Clean Docker disk usage (btrfs/overlay2 storage driver)
./scripts/docker-cleanup.sh

# Test MQTT flow
docker exec enms-nodered mosquitto_sub -h 172.18.0.1 -p 1883 -u $MQTT_USERNAME -P $MQTT_PASSWORD -t 'factory/#' -C 5

# Check TimescaleDB aggregates
SELECT * FROM timescaledb_information.continuous_aggregates;
```

## Code Conventions & Patterns

### FastAPI Service Structure (analytics, query-service, simulator)
```
service/
├── main.py              # FastAPI app with lifespan context manager
├── config.py            # Pydantic Settings from env vars
├── database.py          # asyncpg pool singleton
├── api/routes/*.py      # APIRouter instances
├── services/*_service.py # Business logic classes (singletons)
└── models/*.py          # Pydantic models
```

**Key Patterns**:
- Use `@asynccontextmanager` for lifespan in `main.py` (startup/shutdown)
- Database pool: `from database import db` → `async with db.pool.acquire() as conn`
- Routes: `router = APIRouter()` → registered in `main.py` with `app.include_router(router, prefix="/api/v1")`
- Services: Singleton pattern with `__new__()` - import once, reuse instance

### Real-Time Updates (Phase 4 Session 5)
- **WebSocket**: `/ws` endpoint in analytics broadcasts to all clients
- **Redis Pub/Sub**: `services/redis_manager.py` publishes events → `event_subscriber.py` consumes
- **Event types**: `anomaly.detected`, `baseline.trained`, `kpi.calculated`
- **Disable**: Set `REDIS_PUBSUB_ENABLED=false` in `.env` if needed

### ML Model Lifecycle
1. Train: `POST /api/v1/baseline/train` → saves to `analytics/models/saved/{machine_id}.pkl` AND `energy_baselines` table
2. Predict: Models auto-load from DB, fallback to filesystem
3. Scheduler: APScheduler jobs in `analytics/scheduler/scheduler.py` (cron: `0 2 * * 0` for weekly retrain)
4. Status: Track in `model_training_history` table (pending→running→completed/failed)

### Grafana Dashboard Persistence
- **AUTO-SAVED**: Dashboards export to `grafana/dashboards/*.json` every 10 min via cron
- **Provisioning**: `grafana/provisioning/dashboards/dashboard.yml` auto-loads on startup
- **Variables**: All dashboards use `machine` variable for multi-machine support
- **Commit workflow**: Edit in UI → wait for backup → `git add grafana/dashboards/*.json` → commit

## Common Issues & Solutions

### "Connection refused" to postgres/redis/mqtt
- Check service health: `docker ps` - STATUS should be "healthy"
- Wait for `condition: service_healthy` in docker-compose dependencies
- Logs: `docker-compose logs postgres | grep -i error`

### No data in Grafana/API
1. Check simulator running: `curl localhost:8003/simulator/status`
2. Check MQTT flow: `docker-compose logs nodered | grep INSERT`
3. Verify DB: `SELECT COUNT(*) FROM energy_readings WHERE time > NOW() - INTERVAL '5 minutes'`

### "Function does not exist" errors
- Run: `docker exec enms-postgres psql -U $POSTGRES_USER -d enms -f /docker-entrypoint-initdb.d/04-functions.sql`
- Init scripts only run on **first** container start (empty volume)

### Analytics API 500 errors
- Check pool size: `logger.info(f"Pool: {db.pool.get_size()}/{db.pool.get_max_size()}")` in code
- Increase: `POSTGRES_MAX_CONNECTIONS` in `.env`
- Restart analytics: `docker-compose restart analytics`

## Environment Variables (.env)
**Critical ones not in .env.example**:
- `MQTT_HOST=172.18.0.1` (host broker, NOT "mqtt" container)
- `REDIS_PUBSUB_ENABLED=true` (disable if WebSocket not needed)
- `SCHEDULER_ENABLED=true` (for auto ML retraining)
- `GRAFANA_ROOT_URL=http://{SERVER_IP}:8080/grafana` (nginx subpath)

## Project-Specific Idioms

### Time-Series Queries
```sql
-- ❌ WRONG: Direct query on hypertable (slow for aggregates)
SELECT AVG(power_kw) FROM energy_readings WHERE time > NOW() - INTERVAL '1 day';

-- ✅ RIGHT: Use continuous aggregate
SELECT AVG(avg_power_kw) FROM energy_readings_1hour WHERE bucket >= NOW() - INTERVAL '1 day';
```

### API Response Format (standardized)
```python
return {
    "success": True,
    "data": result,
    "timestamp": datetime.utcnow().isoformat()
}
```

### Anomaly Detection Flow
Simulator → MQTT → Node-RED → DB → Analytics API `/anomaly/detect` → Insert to `anomalies` table → Redis publish → WebSocket broadcast

## OVOS Integration (Voice Assistant)
- **Query Service**: `/api/v1/ovos/*` endpoints map voice intents
- **Intent Examples**: "energy consumption compressor last hour" → `/machines/search?query=compressor` + `/machines/{id}/energy?duration=1h`
- **Testing**: `analytics/tests/test_ovos_endpoints.py` (comprehensive async tests)

## Git Workflow
- **Main branch**: Production-ready code, direct commits OK (single developer)
- **Large features**: Use `docs/*.md` session notes, merge when complete
- **Commit messages**: `feat:`, `fix:`, `docs:`, `chore:` prefixes
- **Auto-committed**: Grafana dashboards (via cron), Node-RED flows (auto-save to `nodered/data/flows.json`)

## Files to Always Check Before Changes
- `docker-compose.yml`: Service dependencies and health checks
- `database/init/*.sql`: Schema changes require container rebuild
- `nginx/conf.d/*.conf`: Routing rules for new services
- `.env`: Service ports and passwords (NEVER commit)

## Performance Tuning
- **TimescaleDB chunks**: 24-hour intervals (set in `03-timescaledb-setup.sql`)
- **Connection pooling**: asyncpg min=5, max=20 (see `database.py`)
- **Redis caching**: Use `redis_manager.get()/set()` with 300s TTL for expensive queries
- **Node-RED**: Batch inserts (100 records) instead of single inserts

## Security Notes
- **JWT tokens**: Not implemented yet (Priority for production)
- **Rate limiting**: Nginx `limit_req_zone` (10 req/s) + FastAPI middleware fallback
- **SQL injection**: All queries use parameterized statements (`$1, $2`)
- **CORS**: Configured in `main.py` middleware (restrict origins in production)

## Testing Checklist for New Features
1. ✅ Unit tests in `tests/` with async fixtures
2. ✅ API docs in Swagger UI (`/docs`) with examples
3. ✅ Database migration script in `database/migrations/` if schema change
4. ✅ Session summary document (`docs/*-COMPLETE.md`) with test commands
5. ✅ Update this file if new architectural pattern introduced

---
**Last Updated**: Generated automatically - keep in sync with `Project-Knowledge-Base.md`
