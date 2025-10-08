#!/bin/bash

# ============================================================================
# EnMS - Energy Management System
# Zero-Touch Setup Script
# ============================================================================
# This script performs a complete installation of the EnMS platform
# 
# Usage: ./setup.sh
# ============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"
ENV_EXAMPLE="${SCRIPT_DIR}/.env.example"

# ============================================================================
# Helper Functions
# ============================================================================

print_header() {
    echo -e "${BLUE}"
    echo "============================================================================"
    echo "$1"
    echo "============================================================================"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# ============================================================================
# Check Prerequisites
# ============================================================================

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    local all_good=true
    
    # Check Docker
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | awk '{print $3}' | sed 's/,//')
        print_success "Docker found: $DOCKER_VERSION"
    else
        print_error "Docker not found. Please install Docker 20.10+"
        all_good=false
    fi
    
    # Check Docker Compose
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
        if docker compose version &> /dev/null; then
            COMPOSE_VERSION=$(docker compose version | awk '{print $4}')
        else
            COMPOSE_VERSION=$(docker-compose --version | awk '{print $4}' | sed 's/,//')
        fi
        print_success "Docker Compose found: $COMPOSE_VERSION"
    else
        print_error "Docker Compose not found. Please install Docker Compose 2.0+"
        all_good=false
    fi
    
    # Check if Docker daemon is running
    if docker info &> /dev/null; then
        print_success "Docker daemon is running"
    else
        print_error "Docker daemon is not running. Please start Docker."
        all_good=false
    fi
    
    # Check available disk space (require at least 10GB)
    AVAILABLE_SPACE=$(df -BG "$SCRIPT_DIR" | tail -1 | awk '{print $4}' | sed 's/G//')
    if [ "$AVAILABLE_SPACE" -lt 10 ]; then
        print_warning "Low disk space: ${AVAILABLE_SPACE}GB available (10GB recommended)"
    else
        print_success "Sufficient disk space: ${AVAILABLE_SPACE}GB available"
    fi
    
    if [ "$all_good" = false ]; then
        print_error "Prerequisites check failed. Please fix the issues above and try again."
        exit 1
    fi
    
    echo ""
}

# ============================================================================
# Generate Environment File
# ============================================================================

generate_env_file() {
    print_header "Setting Up Environment Configuration"
    
    if [ -f "$ENV_FILE" ]; then
        print_warning ".env file already exists"
        read -p "Do you want to regenerate it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Keeping existing .env file"
            return
        fi
    fi
    
    if [ ! -f "$ENV_EXAMPLE" ]; then
        print_error ".env.example not found!"
        exit 1
    fi
    
    print_info "Creating .env file from template..."
    cp "$ENV_EXAMPLE" "$ENV_FILE"
    
    # Generate secure passwords
    print_info "Generating secure passwords..."
    
    POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    GRAFANA_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    MQTT_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    JWT_SECRET=$(openssl rand -hex 32)
    API_KEY=$(openssl rand -hex 32)
    
    # Replace placeholders in .env file
    sed -i "s|POSTGRES_PASSWORD=<CHANGE_ME>|POSTGRES_PASSWORD=${POSTGRES_PASSWORD}|g" "$ENV_FILE"
    sed -i "s|GRAFANA_ADMIN_PASSWORD=<CHANGE_ME>|GRAFANA_ADMIN_PASSWORD=${GRAFANA_PASSWORD}|g" "$ENV_FILE"
    sed -i "s|REDIS_PASSWORD=<CHANGE_ME>|REDIS_PASSWORD=${REDIS_PASSWORD}|g" "$ENV_FILE"
    sed -i "s|MQTT_PASSWORD=<CHANGE_ME>|MQTT_PASSWORD=${MQTT_PASSWORD}|g" "$ENV_FILE"
    sed -i "s|JWT_SECRET=<CHANGE_ME>|JWT_SECRET=${JWT_SECRET}|g" "$ENV_FILE"
    sed -i "s|API_KEY=<CHANGE_ME>|API_KEY=${API_KEY}|g" "$ENV_FILE"
    
    print_success "Environment file created successfully"
    print_warning "IMPORTANT: Save these credentials in a secure location!"
    echo ""
    echo "  Grafana Admin Password: $GRAFANA_PASSWORD"
    echo "  PostgreSQL Password: $POSTGRES_PASSWORD"
    echo ""
    
    # Prompt user to review
    read -p "Press Enter to continue..."
    echo ""
}

# ============================================================================
# Create Directory Structure
# ============================================================================

create_directories() {
    print_header "Creating Directory Structure"
    
    local dirs=(
        "nginx/conf.d"
        "nginx/ssl"
        "portal/public/css"
        "portal/public/js"
        "grafana/provisioning/datasources"
        "grafana/provisioning/dashboards"
        "grafana/dashboards"
        "nodered/flows"
        "database/init"
        "database/migrations"
        "database/backup"
        "simulator/machines"
        "simulator/patterns"
        "analytics/models"
        "analytics/ui/static/css"
        "analytics/ui/static/js"
        "analytics/ui/templates"
        "query-service/api/routes"
        "mqtt/config"
        "redis"
        "scripts"
        "docs"
        "logs"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "${SCRIPT_DIR}/${dir}"
        print_success "Created: $dir"
    done
    
    echo ""
}

# ============================================================================
# Pull Docker Images
# ============================================================================

pull_images() {
    print_header "Pulling Docker Images"
    
    print_info "This may take several minutes depending on your internet connection..."
    
    if docker-compose pull; then
        print_success "All images pulled successfully"
    else
        print_error "Failed to pull images"
        exit 1
    fi
    
    echo ""
}

# ============================================================================
# Build Custom Images
# ============================================================================

build_images() {
    print_header "Building Custom Docker Images"
    
    print_info "Building application images..."
    
    if docker-compose build; then
        print_success "All images built successfully"
    else
        print_error "Failed to build images"
        exit 1
    fi
    
    echo ""
}

# ============================================================================
# Initialize Database
# ============================================================================

initialize_database() {
    print_header "Initializing Database"
    
    print_info "Starting PostgreSQL container..."
    docker-compose up -d postgres
    
    print_info "Waiting for PostgreSQL to be ready..."
    sleep 10
    
    # Wait for PostgreSQL to be healthy
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose exec -T postgres pg_isready -U enms_user -d enms &> /dev/null; then
            print_success "PostgreSQL is ready"
            break
        fi
        
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "PostgreSQL failed to start"
        exit 1
    fi
    
    echo ""
    print_info "Database initialization will be handled by init scripts"
    echo ""
}

# ============================================================================
# Start All Services
# ============================================================================

start_services() {
    print_header "Starting All Services"
    
    print_info "Starting EnMS platform..."
    
    if docker-compose up -d; then
        print_success "All services started successfully"
    else
        print_error "Failed to start services"
        exit 1
    fi
    
    echo ""
}

# ============================================================================
# Health Checks
# ============================================================================

run_health_checks() {
    print_header "Running Health Checks"
    
    print_info "Waiting for services to be healthy (this may take a minute)..."
    sleep 15
    
    local services=(
        "nginx:80:/health"
        "grafana:3000:/api/health"
        "nodered:1880:/"
        "simulator:8003:/health"
        "analytics:8001:/health"
        "query-service:8002:/health"
    )
    
    for service in "${services[@]}"; do
        IFS=':' read -r name port path <<< "$service"
        
        if curl -f -s "http://localhost:${port}${path}" > /dev/null 2>&1; then
            print_success "${name} is healthy"
        else
            print_warning "${name} is not responding yet (may need more time)"
        fi
    done
    
    echo ""
}

# ============================================================================
# Display Access Information
# ============================================================================

display_access_info() {
    print_header "Installation Complete! 🎉"
    
    # Get Grafana password from .env
    GRAFANA_PASS=$(grep "GRAFANA_ADMIN_PASSWORD=" "$ENV_FILE" | cut -d '=' -f2)
    
    echo -e "${GREEN}"
    echo "EnMS is now running!"
    echo ""
    echo "Access URLs:"
    echo "============================================================================"
    echo -e "${NC}"
    echo "  🌐 Unified Portal:     http://localhost"
    echo "  📊 Grafana:            http://localhost:3000"
    echo "      Username: admin"
    echo "      Password: $GRAFANA_PASS"
    echo ""
    echo "  🔄 Node-RED:           http://localhost:1880"
    echo "  🤖 Simulator API:      http://localhost:8003/docs"
    echo "  📈 Analytics API:      http://localhost:8001/docs"
    echo "  🔍 Query API:          http://localhost:8002/docs"
    echo ""
    echo -e "${BLUE}"
    echo "Documentation:          ./docs/"
    echo "Logs:                   docker-compose logs -f"
    echo "Stop:                   docker-compose down"
    echo "Restart:                docker-compose restart"
    echo -e "${NC}"
    echo ""
    
    print_warning "IMPORTANT: Save the Grafana password above!"
    echo ""
}

# ============================================================================
# Main Installation Flow
# ============================================================================

main() {
    clear
    
    echo -e "${BLUE}"
    cat << "EOF"
    ███████╗███╗   ██╗███╗   ███╗███████╗
    ██╔════╝████╗  ██║████╗ ████║██╔════╝
    █████╗  ██╔██╗ ██║██╔████╔██║███████╗
    ██╔══╝  ██║╚██╗██║██║╚██╔╝██║╚════██║
    ███████╗██║ ╚████║██║ ╚═╝ ██║███████║
    ╚══════╝╚═╝  ╚═══╝╚═╝     ╚═╝╚══════╝
    
    Energy Management System - Setup
    Version 1.0.0
EOF
    echo -e "${NC}"
    echo ""
    
    # Run installation steps
    check_prerequisites
    generate_env_file
    create_directories
    pull_images
    build_images
    initialize_database
    start_services
    run_health_checks
    display_access_info
    
    print_success "Setup completed successfully!"
    echo ""
}

# ============================================================================
# Execute Main
# ============================================================================

main "$@"
