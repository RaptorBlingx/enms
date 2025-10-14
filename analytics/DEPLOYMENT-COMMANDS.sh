#!/bin/bash

# ============================================================================
# Phase 3 - Session 1: Analytics Service Deployment
# ============================================================================
# Quick deployment and testing commands
# ============================================================================

echo "======================================================================"
echo "🚀 Phase 3 - Session 1: Analytics Service Deployment"
echo "======================================================================"
echo ""

# Navigate to EnMS root
cd /enms

# Build the analytics service
echo "📦 Building analytics service..."
docker-compose build analytics

# Start the analytics service
echo "🚀 Starting analytics service..."
docker-compose up -d analytics

# Wait for startup
echo "⏳ Waiting for service to start..."
sleep 5

# Check logs
echo ""
echo "======================================================================"
echo "📋 Service Logs:"
echo "======================================================================"
docker-compose logs --tail=50 analytics

# Test health endpoint
echo ""
echo "======================================================================"
echo "✅ Testing Health Endpoint:"
echo "======================================================================"
curl -s http://localhost:8001/health | python3 -m json.tool

# Check container status
echo ""
echo "======================================================================"
echo "🐳 Container Status:"
echo "======================================================================"
docker-compose ps analytics

echo ""
echo "======================================================================"
echo "✅ Deployment Complete!"
echo "======================================================================"
echo ""
echo "📡 API Docs: http://YOUR_SERVER_IP:8001/docs"
echo "🏥 Health Check: http://YOUR_SERVER_IP:8001/health"
echo ""
echo "To view logs: docker-compose logs -f analytics"
echo "To stop: docker-compose stop analytics"
echo ""
echo "Ready for Session 2! 🎯"
echo "======================================================================"
