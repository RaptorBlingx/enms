#!/bin/bash
# ============================================================================
# EnMS - Grafana Dashboard Auto-Backup Setup
# ============================================================================
# This script sets up automatic Grafana dashboard backups every 10 minutes
# using systemd timers.
#
# Usage:
#   sudo ./scripts/setup-grafana-auto-backup.sh
#
# What it does:
#   1. Creates log directory
#   2. Installs systemd service and timer
#   3. Enables and starts automatic backups
#   4. Shows status
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SYSTEMD_USER_DIR="/etc/systemd/system"
SERVICE_NAME="grafana-backup"

echo "======================================================================"
echo -e "${BLUE}EnMS - Grafana Dashboard Auto-Backup Setup${NC}"
echo "======================================================================"
echo ""

# ============================================================================
# Check Prerequisites
# ============================================================================

echo "🔍 Checking prerequisites..."

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ This script must be run as root (use sudo)${NC}"
   exit 1
fi

# Check if backup script exists
if [[ ! -f "$SCRIPT_DIR/backup-grafana-dashboards.sh" ]]; then
    echo -e "${RED}❌ Backup script not found: $SCRIPT_DIR/backup-grafana-dashboards.sh${NC}"
    exit 1
fi

# Make sure backup script is executable
chmod +x "$SCRIPT_DIR/backup-grafana-dashboards.sh"

echo -e "${GREEN}✅ Prerequisites OK${NC}"
echo ""

# ============================================================================
# Create Log Directory
# ============================================================================

echo "📁 Creating log directory..."

LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"
chown ubuntu:ubuntu "$LOG_DIR"

echo -e "${GREEN}✅ Log directory created: $LOG_DIR${NC}"
echo ""

# ============================================================================
# Install Systemd Service
# ============================================================================

echo "📝 Installing systemd service..."

# Copy service file
cp "$SCRIPT_DIR/systemd/${SERVICE_NAME}.service" "$SYSTEMD_USER_DIR/"
chmod 644 "$SYSTEMD_USER_DIR/${SERVICE_NAME}.service"

# Copy timer file
cp "$SCRIPT_DIR/systemd/${SERVICE_NAME}.timer" "$SYSTEMD_USER_DIR/"
chmod 644 "$SYSTEMD_USER_DIR/${SERVICE_NAME}.timer"

echo -e "${GREEN}✅ Service files installed${NC}"
echo ""

# ============================================================================
# Reload Systemd
# ============================================================================

echo "🔄 Reloading systemd..."

systemctl daemon-reload

echo -e "${GREEN}✅ Systemd reloaded${NC}"
echo ""

# ============================================================================
# Enable and Start Timer
# ============================================================================

echo "⚡ Enabling and starting auto-backup timer..."

# Enable timer (start on boot)
systemctl enable ${SERVICE_NAME}.timer

# Start timer now
systemctl start ${SERVICE_NAME}.timer

echo -e "${GREEN}✅ Auto-backup timer started${NC}"
echo ""

# ============================================================================
# Test Initial Backup
# ============================================================================

echo "🧪 Running initial test backup..."
echo ""

# Run backup once manually to test
systemctl start ${SERVICE_NAME}.service

# Wait a moment for it to complete
sleep 2

# Check if it succeeded
if systemctl is-failed ${SERVICE_NAME}.service >/dev/null 2>&1; then
    echo -e "${RED}❌ Initial backup failed. Check logs:${NC}"
    echo -e "   journalctl -u ${SERVICE_NAME}.service -n 20"
    exit 1
else
    echo -e "${GREEN}✅ Initial backup successful${NC}"
fi

echo ""

# ============================================================================
# Show Status
# ============================================================================

echo "======================================================================"
echo -e "${GREEN}✅ Auto-Backup Setup Complete!${NC}"
echo "======================================================================"
echo ""
echo "📊 Status:"
echo "----------------------------------------------------------------------"
systemctl status ${SERVICE_NAME}.timer --no-pager | head -10
echo ""

echo "⏰ Timer Schedule:"
echo "----------------------------------------------------------------------"
systemctl list-timers ${SERVICE_NAME}.timer --no-pager
echo ""

echo "📝 Recent Backups:"
echo "----------------------------------------------------------------------"
if [[ -f "$LOG_DIR/grafana-backup.log" ]]; then
    tail -5 "$LOG_DIR/grafana-backup.log"
else
    echo "No backups yet. First backup will run in 2 minutes."
fi
echo ""

echo "======================================================================"
echo -e "${BLUE}ℹ️  Information${NC}"
echo "======================================================================"
echo ""
echo "Grafana dashboards will be automatically exported every 10 minutes."
echo ""
echo "📁 Backup files: $PROJECT_ROOT/grafana/dashboards/*.json"
echo "📋 Logs:         $LOG_DIR/grafana-backup.log"
echo "⚠️  Errors:      $LOG_DIR/grafana-backup-error.log"
echo ""
echo "Useful commands:"
echo "  • Status:      sudo systemctl status ${SERVICE_NAME}.timer"
echo "  • Stop:        sudo systemctl stop ${SERVICE_NAME}.timer"
echo "  • Start:       sudo systemctl start ${SERVICE_NAME}.timer"
echo "  • Disable:     sudo systemctl disable ${SERVICE_NAME}.timer"
echo "  • View logs:   journalctl -u ${SERVICE_NAME}.service -f"
echo "  • Run now:     sudo systemctl start ${SERVICE_NAME}.service"
echo ""
echo "======================================================================"
echo -e "${GREEN}🎉 Your Grafana changes are now automatically backed up!${NC}"
echo "======================================================================"
echo ""
echo "Just edit dashboards in Grafana UI, and they'll be exported to JSON"
echo "files automatically. Then git commit and push as usual!"
echo ""
