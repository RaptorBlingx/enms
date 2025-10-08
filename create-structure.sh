#!/bin/bash

# ============================================================================
# EnMS - Create Project Structure
# ============================================================================
# This script creates the complete folder structure for the EnMS project
# Run this on your Ubuntu server to set up the directory hierarchy
#
# Usage: ./create-structure.sh
# ============================================================================

set -e

echo "Creating EnMS project structure..."

# Main directories
mkdir -p nginx/{conf.d,ssl}
mkdir -p portal/public/{css,js,images}
mkdir -p grafana/{provisioning/{datasources,dashboards},dashboards}
mkdir -p nodered/{flows,nodes}
mkdir -p database/{init,migrations,backup}
mkdir -p simulator/{api/routes,core,machines,patterns,mqtt}
mkdir -p analytics/{api/{routes,middleware},models,database,services,scheduler,ui/{static/{css,js},templates},tests}
mkdir -p query-service/{api/{routes,schema},services,cache}
mkdir -p mqtt/config
mkdir -p redis
mkdir -p scripts
mkdir -p docs/{architecture,installation,user-guide,developer}
mkdir -p logs

# Create .gitkeep files to preserve empty directories in git
find . -type d -empty -exec touch {}/.gitkeep \;

echo "✓ Folder structure created successfully!"
echo ""
echo "Directory tree:"
tree -L 2 -d

echo ""
echo "Next steps:"
echo "1. Copy the generated files to this directory"
echo "2. Start implementing each service"
echo "3. Follow the phase plan in the Knowledge Base"
