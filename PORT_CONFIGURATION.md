# EnMS Port Configuration Summary

## Problem Solved
Your Ubuntu server already had Node-RED and PostgreSQL running for another project on the default ports (1880 and 5432). This caused port conflicts when starting the EnMS Docker containers.

## Solution Implemented
We've configured EnMS to use different ports via environment variables in `.env` file, making all ports configurable and avoiding conflicts.

## Port Mappings

### Before (Conflicting Ports)
- PostgreSQL: `5432` ❌ (conflict)
- Node-RED: `1880` ❌ (conflict)  
- Redis: `6379`

### After (New Ports - No Conflicts)
- **PostgreSQL**: `5433` → 5432 (container internal) ✅
- **Node-RED**: `1881` → 1880 (container internal) ✅
- **Redis**: `6380` → 6379 (container internal) ✅
- Grafana: `3000` → 3000
- Analytics: `8001` → 8001
- Query Service: `8002` → 8002
- Simulator: `8003` → 8003

## Access URLs

### External Access (from your host machine or browser)
```bash
# Node-RED UI
http://<server_ip>:1881

# PostgreSQL (from host)
psql -h <server_ip> -p 5433 -U raptorblingx -d enms

# Redis (from host)
redis-cli -h <server_ip> -p 6380 -a raptorblingx

# Grafana
http://<server_ip>:3000

# Analytics API
http://<server_ip>:8001

# Query Service API
http://<server_ip>:8002

# Simulator API
http://<server_ip>:8003
```

### Internal Access (between Docker containers)
Containers use the internal Docker network and standard ports:
```
postgres:5432
redis:6379
nodered:1880 (accessed via service name, not localhost)
```

## Environment Variables in .env

```bash
# External ports (configurable)
POSTGRES_EXTERNAL_PORT=5433
NODERED_PORT=1881
REDIS_EXTERNAL_PORT=6380
GRAFANA_PORT=3000
ANALYTICS_PORT=8001
QUERY_PORT=8002
SIMULATOR_PORT=8003
```

## Docker Compose Configuration

The ports in `docker-compose.yml` now use environment variables:

```yaml
postgres:
  ports:
    - "${POSTGRES_EXTERNAL_PORT:-5433}:5432"

nodered:
  ports:
    - "${NODERED_PORT:-1881}:1880"

redis:
  ports:
    - "${REDIS_EXTERNAL_PORT:-6380}:6379"
```

The format `${VAR:-default}` means: use the value from .env, or use the default if not set.

## Node-RED Flow Configuration

### Issue Fixed
The `enms-data-pipeline.json` flow wasn't loading because Node-RED was looking for `flows.json` by default.

### Solution
Updated the Dockerfile to copy the flow file with the correct name:
```dockerfile
COPY flows/enms-data-pipeline.json /data/flows.json
```

Now when you access `http://<server_ip>:1881`, you'll see the EnMS data pipeline flow loaded and ready to use.

## Testing the Setup

```bash
# Check running services
docker compose ps

# Test Node-RED
curl http://localhost:1881/

# Test PostgreSQL
docker compose exec postgres psql -U raptorblingx -d enms -c "SELECT version();"

# Check all logs
docker compose logs --tail=50

# Check specific service
docker compose logs nodered --tail=20
```

## Important Notes

1. **Port Conflicts Resolved**: EnMS now runs on ports 5433, 1881, 6380 instead of the default 5432, 1880, 6379
2. **Both Projects Can Run**: Your original project and EnMS can now run simultaneously on the same server
3. **Configurable**: You can change any port by editing the `.env` file
4. **Internal Communication**: Docker containers still use standard internal ports and service names

## Next Steps

1. Access Node-RED at `http://<server_ip>:1881`
2. Configure MQTT connection in the flow nodes
3. Configure PostgreSQL connection in the flow nodes
4. Deploy the flow to start data ingestion from MQTT → PostgreSQL
