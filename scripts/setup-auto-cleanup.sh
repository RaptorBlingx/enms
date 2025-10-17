#!/bin/bash
# Setup Automated Docker Cleanup

echo "🔧 Setting up automated Docker cleanup for EnMS"
echo ""

# Check if cleanup script exists
if [ ! -f "/home/ubuntu/enms/scripts/docker-cleanup.sh" ]; then
    echo "❌ Error: docker-cleanup.sh not found!"
    exit 1
fi

# Make cleanup script executable
chmod +x /home/ubuntu/enms/scripts/docker-cleanup.sh

# Check current crontab
echo "📋 Current crontab:"
crontab -l 2>/dev/null || echo "  (no crontab entries)"
echo ""

# Ask user for schedule
echo "Choose cleanup schedule:"
echo "  1) Daily at 2 AM (recommended for active development)"
echo "  2) Weekly on Sunday at 2 AM (recommended for production)"
echo "  3) Manual only (no auto-cleanup)"
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        CRON_SCHEDULE="0 2 * * *"
        SCHEDULE_NAME="Daily at 2 AM"
        ;;
    2)
        CRON_SCHEDULE="0 2 * * 0"
        SCHEDULE_NAME="Weekly on Sunday at 2 AM"
        ;;
    3)
        echo "✅ Skipping auto-cleanup setup"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

# Add to crontab
CRON_JOB="$CRON_SCHEDULE cd /home/ubuntu/enms && ./scripts/docker-cleanup.sh -y >> /var/log/docker-cleanup.log 2>&1"

# Check if already exists
if crontab -l 2>/dev/null | grep -q "docker-cleanup.sh"; then
    echo "⚠️  Docker cleanup already in crontab!"
    read -p "Replace existing entry? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cancelled"
        exit 1
    fi
    # Remove old entry
    crontab -l 2>/dev/null | grep -v "docker-cleanup.sh" | crontab -
fi

# Add new entry
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo ""
echo "✅ Auto-cleanup configured: $SCHEDULE_NAME"
echo ""
echo "📋 New crontab:"
crontab -l | grep "docker-cleanup.sh"
echo ""
echo "📝 Logs will be written to: /var/log/docker-cleanup.log"
echo ""
echo "To test now:"
echo "  cd /home/ubuntu/enms && ./scripts/docker-cleanup.sh"
echo ""
echo "To view logs:"
echo "  tail -f /var/log/docker-cleanup.log"
echo ""
echo "To disable:"
echo "  crontab -e  # Then remove the docker-cleanup.sh line"
echo ""
echo "✅ Setup complete!"
