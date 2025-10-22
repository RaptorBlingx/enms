#!/bin/bash
# Refresh materialized view every 2 minutes
docker exec enms-postgres psql -U raptorblingx -d enms -c "REFRESH MATERIALIZED VIEW CONCURRENTLY energy_predictions_realtime;" && echo "✅ $(date): Predictions refreshed"
