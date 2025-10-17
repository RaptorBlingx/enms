#!/bin/bash

# Docker Cleanup Script for EnMS
# Prevents disk usage from growing due to unused Docker resources

echo "🧹 EnMS Docker Cleanup Script"
echo "=============================="
echo ""

# Show current Docker disk usage
echo "📊 Current Docker Disk Usage:"
docker system df
echo ""

# Count resources
echo "📈 Resource Counts:"
dangling_images=$(docker images -f "dangling=true" -q | wc -l)
stopped_containers=$(docker ps -a -f "status=exited" -q | wc -l)
unused_volumes=$(docker volume ls -f "dangling=true" -q | wc -l)

echo "   Dangling images: $dangling_images"
echo "   Stopped containers: $stopped_containers"
echo "   Unused volumes: $unused_volumes"
echo ""

# Confirm cleanup
read -p "❓ Do you want to clean up unused Docker resources? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "🗑️  Cleaning up..."
    echo ""
    
    # Remove dangling images (unused layers from rebuilds)
    if [ $dangling_images -gt 0 ]; then
        echo "🖼️  Removing dangling images..."
        docker image prune -f
        echo ""
    fi
    
    # Remove stopped containers
    if [ $stopped_containers -gt 0 ]; then
        echo "📦 Removing stopped containers..."
        docker container prune -f
        echo ""
    fi
    
    # Remove unused volumes
    if [ $unused_volumes -gt 0 ]; then
        echo "💾 Removing unused volumes..."
        docker volume prune -f
        echo ""
    fi
    
    # Remove build cache (keeps last 24h)
    echo "🏗️  Removing old build cache..."
    docker builder prune -f --filter "until=24h"
    echo ""
    
    # Show results
    echo "✅ Cleanup Complete!"
    echo ""
    echo "📊 New Docker Disk Usage:"
    docker system df
    echo ""
    
    # Calculate space freed
    echo "💾 Disk Space Summary:"
    df -h / | grep -v Filesystem
    
else
    echo "❌ Cleanup cancelled"
fi
