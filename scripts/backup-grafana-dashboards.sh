#!/bin/bash
################################################################################
# EnMS Project - Grafana Dashboard Backup Script
# 
# Purpose: Export all Grafana dashboards from the running container to JSON files
#          so they can be committed to git
#
# Usage: ./scripts/backup-grafana-dashboards.sh
#
# This script:
# 1. Connects to Grafana API
# 2. Lists all dashboards
# 3. Exports each dashboard to ./grafana/dashboards/*.json
# 4. Preserves the original file structure
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load Grafana credentials from .env
if [ -f .env ]; then
    GRAFANA_ADMIN_USER=$(grep "^GRAFANA_ADMIN_USER=" .env | cut -d '=' -f2)
    GRAFANA_ADMIN_PASSWORD=$(grep "^GRAFANA_ADMIN_PASSWORD=" .env | cut -d '=' -f2)
fi

# Configuration
GRAFANA_URL="${GRAFANA_URL:-http://localhost:3001}"
GRAFANA_USER="${GRAFANA_ADMIN_USER:-admin}"
GRAFANA_PASSWORD="${GRAFANA_ADMIN_PASSWORD:-admin}"
DASHBOARD_DIR="./grafana/dashboards"
BACKUP_BASE_DIR="./grafana/dashboards-backup"
BACKUP_RETENTION=3  # Keep only last 3 backups

echo "======================================================================"
echo "EnMS - Grafana Dashboard Backup"
echo "======================================================================"

# Check if Grafana is running
if ! curl -sf "${GRAFANA_URL}/api/health" > /dev/null; then
    echo -e "${RED}❌ Error: Grafana is not running at ${GRAFANA_URL}${NC}"
    echo "Please start Grafana with: docker compose up -d grafana"
    exit 1
fi

echo -e "${GREEN}✅ Grafana is running${NC}"

# Check if dashboards have changed (compare with git)
CHANGES_DETECTED=false
if git diff --quiet grafana/dashboards/*.json 2>/dev/null; then
    echo "📊 No changes detected in dashboards (compared to git)"
else
    CHANGES_DETECTED=true
    echo "📊 Changes detected - proceeding with backup"
fi

# Create timestamped backup directory
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="${BACKUP_BASE_DIR}/${TIMESTAMP}"
mkdir -p "${BACKUP_DIR}"

# Rotate old backups (keep only last N backups)
if [ -d "${BACKUP_BASE_DIR}" ]; then
    BACKUP_COUNT=$(find "${BACKUP_BASE_DIR}" -maxdepth 1 -type d | wc -l)
    if [ $BACKUP_COUNT -gt $((BACKUP_RETENTION + 1)) ]; then
        echo "�️  Rotating old backups (keeping last ${BACKUP_RETENTION})..."
        find "${BACKUP_BASE_DIR}" -maxdepth 1 -type d | \
            sort | head -n -${BACKUP_RETENTION} | \
            tail -n +2 | xargs rm -rf
    fi
fi

echo "📁 Backup location: ${BACKUP_DIR}"

# Get all dashboards
echo "📋 Fetching dashboard list..."
DASHBOARDS=$(curl -s -u "${GRAFANA_USER}:${GRAFANA_PASSWORD}" \
    "${GRAFANA_URL}/api/search?type=dash-db" | \
    jq -r '.[] | "\(.uid)|\(.title)|\(.uri)"')

if [ -z "$DASHBOARDS" ]; then
    echo -e "${YELLOW}⚠️  No dashboards found${NC}"
    exit 0
fi

DASHBOARD_COUNT=$(echo "$DASHBOARDS" | wc -l)
echo "Found ${DASHBOARD_COUNT} dashboard(s)"
echo "----------------------------------------------------------------------"

# Export each dashboard
EXPORTED=0
FAILED=0

while IFS='|' read -r DASH_UID TITLE URI; do
    echo "📤 Exporting: ${TITLE} (${DASH_UID})"
    
    # Fetch dashboard JSON using UID
    DASHBOARD_JSON=$(curl -s -u "${GRAFANA_USER}:${GRAFANA_PASSWORD}" \
        "${GRAFANA_URL}/api/dashboards/uid/${DASH_UID}")
    
    # Check if fetch was successful
    if echo "$DASHBOARD_JSON" | jq -e '.dashboard' > /dev/null 2>&1; then
        # Extract dashboard object and remove metadata
        echo "$DASHBOARD_JSON" | jq '.dashboard' > "${DASHBOARD_DIR}/${DASH_UID}.json"
        
        # Also save to backup with timestamp
        echo "$DASHBOARD_JSON" | jq '.dashboard' > "${BACKUP_DIR}/${DASH_UID}.json"
        
        echo -e "${GREEN}   ✅ Saved to: ${DASHBOARD_DIR}/${DASH_UID}.json${NC}"
        ((EXPORTED++)) || true
    else
        echo -e "${RED}   ❌ Failed to export ${TITLE}${NC}"
        ((FAILED++)) || true
    fi
done <<< "$DASHBOARDS"

echo "======================================================================"
echo "Backup Complete!"
echo "======================================================================"
echo -e "${GREEN}✅ Exported: ${EXPORTED}${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}❌ Failed: ${FAILED}${NC}"
fi
echo ""
echo "📁 Dashboards saved to: ${DASHBOARD_DIR}"
echo "💾 Backup created at: ${BACKUP_DIR}"
echo ""
echo "Next steps:"
echo "  1. Review the exported JSON files"
echo "  2. git add grafana/dashboards/*.json"
echo "  3. git commit -m 'Update Grafana dashboards'"
echo "  4. git push"
echo "======================================================================"
