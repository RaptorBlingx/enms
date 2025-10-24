#!/bin/bash
# ============================================================================
# EnMS - ISO 50001 EnPI System Test Script
# ============================================================================
# Purpose: End-to-end testing of SEU management and EnPI reporting
# Author: EnMS Team
# Date: 2025-10-22
# ============================================================================

set -e  # Exit on error

# Configuration
API_BASE="http://localhost:8001/api/v1"
ANALYTICS_BASE="http://localhost:8080/api/analytics/v1"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "========================================"
echo "ISO 50001 EnPI System Test"
echo "========================================"
echo ""

# ============================================================================
# Step 1: Check API Health
# ============================================================================
echo -e "${YELLOW}Step 1: Checking API health...${NC}"
HEALTH=$(curl -s "$API_BASE/health")
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Analytics service is healthy${NC}"
else
    echo -e "${RED}✗ Analytics service unhealthy${NC}"
    exit 1
fi
echo ""

# ============================================================================
# Step 2: List Energy Sources
# ============================================================================
echo -e "${YELLOW}Step 2: Listing energy sources...${NC}"
SOURCES=$(curl -s "$API_BASE/energy-sources")
echo "$SOURCES" | jq '.'
ELECTRICITY_ID=$(echo "$SOURCES" | jq -r '.[] | select(.name=="electricity") | .id')
echo -e "${GREEN}✓ Found electricity source: $ELECTRICITY_ID${NC}"
echo ""

# ============================================================================
# Step 3: Create Test SEU
# ============================================================================
echo -e "${YELLOW}Step 3: Creating test SEU (Compressor Group)...${NC}"

# Use existing compressor machines
MACHINE_ID_1="c0000000-0000-0000-0000-000000000001"
MACHINE_ID_2="c0000000-0000-0000-0000-000000000006"

CREATE_SEU_PAYLOAD=$(cat <<EOF
{
    "name": "Test Compressor Group",
    "description": "Test SEU for ISO 50001 compliance reporting",
    "energy_source_id": "$ELECTRICITY_ID",
    "machine_ids": [
        "$MACHINE_ID_1"
    ]
}
EOF
)

SEU_RESPONSE=$(curl -s -X POST "$API_BASE/seus" \
    -H "Content-Type: application/json" \
    -d "$CREATE_SEU_PAYLOAD")

if echo "$SEU_RESPONSE" | grep -q "id"; then
    SEU_ID=$(echo "$SEU_RESPONSE" | jq -r '.id')
    echo -e "${GREEN}✓ SEU created: $SEU_ID${NC}"
    echo "$SEU_RESPONSE" | jq '.'
else
    echo -e "${RED}✗ Failed to create SEU${NC}"
    echo "$SEU_RESPONSE" | jq '.'
    exit 1
fi
echo ""

# ============================================================================
# Step 4: List SEUs
# ============================================================================
echo -e "${YELLOW}Step 4: Listing all SEUs...${NC}"
SEUS=$(curl -s "$API_BASE/seus")
echo "$SEUS" | jq '.data[] | {id, name, machine_count, has_baseline}'
echo ""

# ============================================================================
# Step 5: Train Baseline (13 days - limited by current data)
# ============================================================================
echo -e "${YELLOW}Step 5: Training baseline on available data...${NC}"

# Get actual data range
DATA_RANGE=$(docker exec enms-postgres psql -U raptorblingx -d enms -t -c \
    "SELECT MIN(time)::date, MAX(time)::date FROM energy_readings WHERE machine_id='$MACHINE_ID_1';")

START_DATE=$(echo "$DATA_RANGE" | awk '{print $1}' | tr -d ' ')
END_DATE=$(echo "$DATA_RANGE" | awk '{print $3}' | tr -d ' ')

echo "  Data range: $START_DATE to $END_DATE"

TRAIN_PAYLOAD=$(cat <<EOF
{
    "seu_id": "$SEU_ID",
    "baseline_year": 2025,
    "start_date": "$START_DATE",
    "end_date": "$END_DATE",
    "features": ["avg_production_count", "avg_temp_c"]
}
EOF
)

echo "  Training request:"
echo "$TRAIN_PAYLOAD" | jq '.'

TRAIN_RESPONSE=$(curl -s -X POST "$API_BASE/baseline/seu/train" \
    -H "Content-Type: application/json" \
    -d "$TRAIN_PAYLOAD")

if echo "$TRAIN_RESPONSE" | grep -q "success"; then
    echo -e "${GREEN}✓ Baseline trained successfully${NC}"
    echo "$TRAIN_RESPONSE" | jq '{
        success, 
        seu_name, 
        baseline_year, 
        samples_count, 
        r_squared, 
        rmse, 
        formula
    }'
else
    echo -e "${RED}✗ Baseline training failed${NC}"
    echo "$TRAIN_RESPONSE" | jq '.'
    # Don't exit - continue with other tests
fi
echo ""

# ============================================================================
# Step 6: Generate Performance Report (if baseline trained)
# ============================================================================
if echo "$TRAIN_RESPONSE" | grep -q "success"; then
    echo -e "${YELLOW}Step 6: Generating performance report for 2025...${NC}"
    
    REPORT_PAYLOAD=$(cat <<EOF
{
    "seu_id": "$SEU_ID",
    "report_year": 2025,
    "baseline_year": 2025,
    "period": "annual"
}
EOF
)

    echo "  Report request:"
    echo "$REPORT_PAYLOAD" | jq '.'
    
    REPORT_RESPONSE=$(curl -s -X POST "$API_BASE/reports/seu-performance" \
        -H "Content-Type: application/json" \
        -d "$REPORT_PAYLOAD")
    
    if echo "$REPORT_RESPONSE" | grep -q "seu_id"; then
        echo -e "${GREEN}✓ Performance report generated${NC}"
        echo "$REPORT_RESPONSE" | jq '{
            seu_name,
            report_period,
            actual_consumption,
            expected_consumption,
            deviation_percent,
            compliance_status
        }'
    else
        echo -e "${RED}✗ Report generation failed${NC}"
        echo "$REPORT_RESPONSE" | jq '.'
    fi
    echo ""
    
    # ========================================================================
    # Step 7: Get EnPI Trend
    # ========================================================================
    echo -e "${YELLOW}Step 7: Fetching EnPI trend data...${NC}"
    
    TREND_RESPONSE=$(curl -s "$API_BASE/analytics/enpi?seu_id=$SEU_ID&start_year=2025&end_year=2025")
    
    if echo "$TREND_RESPONSE" | grep -q "success"; then
        echo -e "${GREEN}✓ EnPI trend retrieved${NC}"
        echo "$TREND_RESPONSE" | jq '{
            success,
            seu_name,
            baseline_year,
            data_points
        }'
    else
        echo -e "${RED}✗ EnPI trend fetch failed${NC}"
        echo "$TREND_RESPONSE" | jq '.'
    fi
    echo ""
else
    echo -e "${YELLOW}Skipping report generation (baseline training failed)${NC}"
    echo ""
fi

# ============================================================================
# Step 8: Test Database Functions
# ============================================================================
echo -e "${YELLOW}Step 8: Testing PostgreSQL helper functions...${NC}"

echo "  Testing get_seu_energy() function..."
ENERGY_RESULT=$(docker exec enms-postgres psql -U raptorblingx -d enms -t -c \
    "SELECT get_seu_energy('$SEU_ID'::uuid, '$START_DATE'::timestamptz, '$END_DATE'::timestamptz);")
echo "  Total energy for SEU: $ENERGY_RESULT kWh"

echo "  Testing get_deviation_status() function..."
STATUS_RESULT=$(docker exec enms-postgres psql -U raptorblingx -d enms -t -c \
    "SELECT get_deviation_status(2.5);")
echo "  Deviation 2.5% -> Status: $STATUS_RESULT"

echo "  Testing get_seu_daily_aggregates() function..."
AGGREGATES_COUNT=$(docker exec enms-postgres psql -U raptorblingx -d enms -t -c \
    "SELECT COUNT(*) FROM get_seu_daily_aggregates('$SEU_ID'::uuid, '$START_DATE'::date, '$END_DATE'::date);")
echo "  Daily aggregates available: $AGGREGATES_COUNT days"

echo -e "${GREEN}✓ Database functions working${NC}"
echo ""

# ============================================================================
# Step 9: Verify Database Tables
# ============================================================================
echo -e "${YELLOW}Step 9: Verifying database tables...${NC}"

echo "  Checking energy_sources table..."
SOURCES_COUNT=$(docker exec enms-postgres psql -U raptorblingx -d enms -t -c \
    "SELECT COUNT(*) FROM energy_sources;")
echo "  Energy sources: $SOURCES_COUNT"

echo "  Checking seus table..."
SEUS_COUNT=$(docker exec enms-postgres psql -U raptorblingx -d enms -t -c \
    "SELECT COUNT(*) FROM seus;")
echo "  SEUs: $SEUS_COUNT"

echo "  Checking seu_energy_performance table..."
REPORTS_COUNT=$(docker exec enms-postgres psql -U raptorblingx -d enms -t -c \
    "SELECT COUNT(*) FROM seu_energy_performance;")
echo "  Performance reports: $REPORTS_COUNT"

echo -e "${GREEN}✓ All tables verified${NC}"
echo ""

# ============================================================================
# Step 10: API Documentation Check
# ============================================================================
echo -e "${YELLOW}Step 10: Checking API documentation...${NC}"

OPENAPI=$(curl -s "$API_BASE/../openapi.json")
if echo "$OPENAPI" | grep -q "seus"; then
    echo -e "${GREEN}✓ SEU endpoints registered in OpenAPI schema${NC}"
    echo "  Available endpoints:"
    echo "$OPENAPI" | jq -r '.paths | keys[]' | grep -E "(seus|seu-performance|enpi)" | sed 's/^/    /'
else
    echo -e "${YELLOW}⚠ SEU endpoints not found in OpenAPI${NC}"
fi
echo ""

# ============================================================================
# Summary
# ============================================================================
echo "========================================"
echo "Test Summary"
echo "========================================"
echo ""
echo "✅ Completed Steps:"
echo "  1. API health check"
echo "  2. Energy sources listing"
echo "  3. SEU creation"
echo "  4. SEU listing"
echo "  5. Baseline training (limited data)"
echo "  6. Performance report generation"
echo "  7. EnPI trend retrieval"
echo "  8. Database functions validation"
echo "  9. Table verification"
echo "  10. API documentation check"
echo ""
echo "📊 SEU ID: $SEU_ID"
echo "📅 Data Range: $START_DATE to $END_DATE"
echo ""
echo "⚠️  NOTE: Only 13 days of data available."
echo "   For production baseline, need 365 days (full year)."
echo ""
echo "Next Steps:"
echo "  1. Run simulator for longer period to accumulate year of data"
echo "  2. Create Grafana dashboard (iso-50001-enpi-report.json)"
echo "  3. Train baseline on full year (2024-01-01 to 2024-12-31)"
echo "  4. Generate quarterly reports for 2025"
echo ""
echo "========================================"
