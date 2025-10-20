# OVOS Endpoint Integration Tests

Comprehensive test suite for all OVOS API endpoints (Tasks 1-10).

## Setup

1. Install test dependencies:
```bash
pip install -r tests/requirements-test.txt
```

2. Ensure analytics service is running:
```bash
docker compose up -d analytics
```

## Running Tests

### Run all tests:
```bash
pytest tests/test_ovos_endpoints.py -v
```

### Run specific test class:
```bash
# Test Task 1: Machine search
pytest tests/test_ovos_endpoints.py::TestMachineSearch -v

# Test Task 6: Factory KPI
pytest tests/test_ovos_endpoints.py::TestFactoryKPI -v

# Test Task 10: Forecast
pytest tests/test_ovos_endpoints.py::TestForecastEndpoint -v
```

### Run with coverage:
```bash
pytest tests/test_ovos_endpoints.py --cov=api/routes --cov-report=html
```

### Run async tests:
```bash
pytest tests/test_ovos_endpoints.py -v --asyncio-mode=auto
```

## Test Coverage

### ✅ Priority 1 - OVOS Critical Features (5 tests)
- **Task 1:** Machine search by name (4 test cases)
- **Task 2:** Enhanced anomaly/recent with date range (5 test cases)
- **Task 3:** OVOS summary endpoint (1 test case)
- **Task 4:** Top consumers ranking (6 test cases)
- **Task 5:** OVOS machine status by name (3 test cases)

### ✅ Priority 2 - Production Features (3 tests)
- **Task 6:** Factory-wide KPI aggregation (3 test cases)
- **Task 7:** Time-of-use pricing tiers (4 test cases)

### ✅ Priority 3 - Nice-to-have Features (1 test)
- **Task 10:** Simplified forecast endpoint (3 test cases)

### 🧪 Edge Cases & Error Handling (3 tests)
- Invalid UUID formats
- Future date ranges
- Invalid date ranges (start > end)

## Test Structure

Each test class corresponds to a task:
- `TestMachineSearch` → Task 1
- `TestAnomalyRecent` → Task 2
- `TestOVOSSummary` → Task 3
- `TestTopConsumers` → Task 4
- `TestMachineStatus` → Task 5
- `TestFactoryKPI` → Task 6
- `TestTimeOfUsePricing` → Task 7
- `TestForecastEndpoint` → Task 10
- `TestEdgeCases` → Error handling

## Example Output

```
tests/test_ovos_endpoints.py::TestMachineSearch::test_search_existing_machine PASSED
tests/test_ovos_endpoints.py::TestMachineSearch::test_search_nonexistent_machine PASSED
tests/test_ovos_endpoints.py::TestMachineSearch::test_search_case_insensitive PASSED
tests/test_ovos_endpoints.py::TestTopConsumers::test_top_consumers_energy PASSED
tests/test_ovos_endpoints.py::TestForecastEndpoint::test_factory_wide_forecast PASSED
tests/test_ovos_endpoints.py::TestForecastEndpoint::test_single_machine_forecast PASSED

========================= 32 tests passed in 12.45s =========================
```

## What's Tested

### Positive Test Cases:
- ✅ Valid requests return 200 status
- ✅ Response contains expected fields
- ✅ Data types are correct
- ✅ Business logic (sorting, calculations, rankings)
- ✅ Date range filtering
- ✅ Optional parameters work correctly

### Negative Test Cases:
- ✅ Non-existent resources return 404
- ✅ Missing required parameters return 422
- ✅ Invalid formats return 422
- ✅ Invalid values return appropriate errors

### Edge Cases:
- ✅ Future dates handled gracefully
- ✅ Invalid UUIDs rejected
- ✅ Empty results handled correctly

## CI/CD Integration

Add to your CI pipeline:
```yaml
- name: Run integration tests
  run: |
    docker compose up -d analytics
    pip install -r analytics/tests/requirements-test.txt
    pytest analytics/tests/test_ovos_endpoints.py -v --junitxml=test-results.xml
```

## Notes

- Tests use real database connection (ensure test data exists)
- Tests are async using httpx AsyncClient
- Timeout set to 30 seconds per request
- Tests assume analytics service is running on localhost:8001
