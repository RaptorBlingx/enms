"""
Integration tests for Performance API endpoints

Tests all 4 endpoints:
- POST /performance/analyze
- GET /performance/opportunities
- POST /performance/action-plan
- GET /performance/health
"""

import pytest
import asyncio
from httpx import AsyncClient
from datetime import date, datetime, timedelta
from main import app


@pytest.fixture
async def client():
    """Create async HTTP client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def valid_seu_name():
    """Return a valid SEU name from test data"""
    return "Compressor-1"


@pytest.fixture
def valid_factory_id():
    """Return a valid factory UUID from test data"""
    return "11111111-1111-1111-1111-111111111111"


class TestAnalyzeEndpoint:
    """Test POST /api/v1/performance/analyze"""
    
    @pytest.mark.asyncio
    async def test_analyze_success(self, client, valid_seu_name):
        """Test successful performance analysis"""
        response = await client.post(
            "/api/v1/performance/analyze",
            params={
                "seu_name": valid_seu_name,
                "energy_source": "energy",
                "analysis_date": "2025-11-05"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "seu_name" in data
        assert "energy_source" in data
        assert "actual_energy_kwh" in data
        assert "baseline_energy_kwh" in data
        assert "deviation_kwh" in data
        assert "deviation_percent" in data
        assert "efficiency_score" in data
        assert "iso_status" in data
        assert "root_cause_analysis" in data
        assert "recommendations" in data
        assert "voice_summary" in data
        
        # Validate data types
        assert isinstance(data["actual_energy_kwh"], (int, float))
        assert isinstance(data["baseline_energy_kwh"], (int, float))
        assert isinstance(data["recommendations"], list)
        assert isinstance(data["voice_summary"], str)
        
        # Validate logical values
        assert data["actual_energy_kwh"] >= 0
        assert data["baseline_energy_kwh"] >= 0
        assert 0.0 <= data["efficiency_score"] <= 2.0
        assert data["iso_status"] in ["excellent", "on_target", "requires_attention", "non_compliant"]
    
    @pytest.mark.asyncio
    async def test_analyze_invalid_seu(self, client):
        """Test error for non-existent SEU"""
        response = await client.post(
            "/api/v1/performance/analyze",
            params={
                "seu_name": "NonExistent-Machine",
                "energy_source": "energy",
                "analysis_date": "2025-11-05"
            }
        )
        
        assert response.status_code in [404, 500]
        assert "detail" in response.json()
    
    @pytest.mark.asyncio
    async def test_analyze_invalid_energy_source(self, client, valid_seu_name):
        """Test error for invalid energy source"""
        response = await client.post(
            "/api/v1/performance/analyze",
            params={
                "seu_name": valid_seu_name,
                "energy_source": "invalid_source",
                "analysis_date": "2025-11-05"
            }
        )
        
        assert response.status_code == 400
        assert "detail" in response.json()
    
    @pytest.mark.asyncio
    async def test_analyze_future_date(self, client, valid_seu_name):
        """Test error for future date"""
        future_date = (datetime.utcnow() + timedelta(days=30)).date().isoformat()
        response = await client.post(
            "/api/v1/performance/analyze",
            params={
                "seu_name": valid_seu_name,
                "energy_source": "energy",
                "analysis_date": future_date
            }
        )
        
        assert response.status_code == 400
        assert "future" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_analyze_response_time(self, client, valid_seu_name):
        """Test response time <500ms requirement"""
        import time
        
        start = time.time()
        response = await client.post(
            "/api/v1/performance/analyze",
            params={
                "seu_name": valid_seu_name,
                "energy_source": "energy",
                "analysis_date": "2025-11-05"
            }
        )
        duration = (time.time() - start) * 1000  # Convert to ms
        
        assert response.status_code == 200
        assert duration < 500, f"Response took {duration:.0f}ms, expected <500ms"


class TestOpportunitiesEndpoint:
    """Test GET /api/v1/performance/opportunities"""
    
    @pytest.mark.asyncio
    async def test_opportunities_success(self, client, valid_factory_id):
        """Test successful opportunity detection"""
        response = await client.get(
            "/api/v1/performance/opportunities",
            params={
                "factory_id": valid_factory_id,
                "period": "month"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "factory_id" in data
        assert "period" in data
        assert "total_opportunities" in data
        assert "total_potential_savings_kwh" in data
        assert "total_potential_savings_usd" in data
        assert "opportunities" in data
        assert "timestamp" in data
        
        # Validate data types
        assert isinstance(data["total_opportunities"], int)
        assert isinstance(data["opportunities"], list)
        
        # If opportunities found, validate structure
        if len(data["opportunities"]) > 0:
            opp = data["opportunities"][0]
            assert "rank" in opp
            assert "seu_name" in opp
            assert "issue_type" in opp
            assert "description" in opp
            assert "potential_savings_kwh" in opp
            assert "potential_savings_usd" in opp
            assert "effort" in opp
            assert "roi_days" in opp
            assert "recommended_action" in opp
            
            # Validate ranking (highest savings first)
            assert opp["rank"] == 1
            if len(data["opportunities"]) > 1:
                assert data["opportunities"][0]["potential_savings_kwh"] >= \
                       data["opportunities"][-1]["potential_savings_kwh"]
    
    @pytest.mark.asyncio
    async def test_opportunities_all_periods(self, client, valid_factory_id):
        """Test all valid period options"""
        for period in ["week", "month", "quarter"]:
            response = await client.get(
                "/api/v1/performance/opportunities",
                params={
                    "factory_id": valid_factory_id,
                    "period": period
                }
            )
            
            assert response.status_code == 200
            assert response.json()["period"] == period
    
    @pytest.mark.asyncio
    async def test_opportunities_invalid_period(self, client, valid_factory_id):
        """Test error for invalid period"""
        response = await client.get(
            "/api/v1/performance/opportunities",
            params={
                "factory_id": valid_factory_id,
                "period": "invalid_period"
            }
        )
        
        assert response.status_code == 400
        assert "Invalid period" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_opportunities_response_time(self, client, valid_factory_id):
        """Test response time <500ms requirement"""
        import time
        
        start = time.time()
        response = await client.get(
            "/api/v1/performance/opportunities",
            params={
                "factory_id": valid_factory_id,
                "period": "month"
            }
        )
        duration = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert duration < 500, f"Response took {duration:.0f}ms, expected <500ms"


class TestActionPlanEndpoint:
    """Test POST /api/v1/performance/action-plan"""
    
    @pytest.mark.asyncio
    async def test_action_plan_excessive_idle(self, client, valid_seu_name):
        """Test action plan for excessive idle issue"""
        response = await client.post(
            "/api/v1/performance/action-plan",
            params={
                "seu_name": valid_seu_name,
                "issue_type": "excessive_idle"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "id" in data
        assert "seu_name" in data
        assert "problem_statement" in data
        assert "root_causes" in data
        assert "actions" in data
        assert "expected_outcomes" in data
        assert "monitoring_plan" in data
        assert "target_date" in data
        assert "status" in data
        
        # Validate data types
        assert isinstance(data["root_causes"], list)
        assert isinstance(data["actions"], list)
        assert isinstance(data["monitoring_plan"], list)
        assert data["status"] == "draft"
        
        # Validate actions structure
        assert len(data["actions"]) > 0
        action = data["actions"][0]
        assert "priority" in action
        assert "action" in action
        assert "responsible" in action
        assert "timeline_days" in action
        
        # Validate expected outcomes
        outcomes = data["expected_outcomes"]
        assert "energy_kwh" in outcomes
        assert "cost_usd" in outcomes
        assert "carbon_kg" in outcomes
        assert all(v > 0 for v in outcomes.values())
    
    @pytest.mark.asyncio
    async def test_action_plan_all_issue_types(self, client, valid_seu_name):
        """Test all valid issue types"""
        issue_types = [
            "excessive_idle",
            "inefficient_scheduling",
            "baseline_drift",
            "suboptimal_setpoints"
        ]
        
        for issue_type in issue_types:
            response = await client.post(
                "/api/v1/performance/action-plan",
                params={
                    "seu_name": valid_seu_name,
                    "issue_type": issue_type
                }
            )
            
            assert response.status_code == 200, f"Failed for issue_type: {issue_type}"
            data = response.json()
            assert issue_type in data["id"]  # Plan ID includes issue type
    
    @pytest.mark.asyncio
    async def test_action_plan_invalid_issue_type(self, client, valid_seu_name):
        """Test error for invalid issue type"""
        response = await client.post(
            "/api/v1/performance/action-plan",
            params={
                "seu_name": valid_seu_name,
                "issue_type": "invalid_issue"
            }
        )
        
        assert response.status_code == 400
        assert "Invalid issue_type" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_action_plan_response_time(self, client, valid_seu_name):
        """Test response time <500ms requirement"""
        import time
        
        start = time.time()
        response = await client.post(
            "/api/v1/performance/action-plan",
            params={
                "seu_name": valid_seu_name,
                "issue_type": "excessive_idle"
            }
        )
        duration = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert duration < 500, f"Response took {duration:.0f}ms, expected <500ms"


class TestHealthEndpoint:
    """Test GET /api/v1/performance/health"""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test performance engine health check"""
        response = await client.get("/api/v1/performance/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "engine_version" in data
        assert "capabilities" in data
        assert data["status"] == "healthy"


class TestConcurrentRequests:
    """Test concurrent request handling"""
    
    @pytest.mark.asyncio
    async def test_concurrent_analyze_requests(self, client, valid_seu_name):
        """Test 10 concurrent /analyze requests"""
        tasks = [
            client.post(
                "/api/v1/performance/analyze",
                params={
                    "seu_name": valid_seu_name,
                    "energy_source": "energy",
                    "analysis_date": "2025-11-05"
                }
            )
            for _ in range(10)
        ]
        
        responses = await asyncio.gather(*tasks)
        
        # All requests should succeed
        assert all(r.status_code == 200 for r in responses)
        
        # All should return valid data
        for response in responses:
            data = response.json()
            assert data["seu_name"] == valid_seu_name
            assert "actual_energy_kwh" in data
    
    @pytest.mark.asyncio
    async def test_concurrent_opportunities_requests(self, client, valid_factory_id):
        """Test 10 concurrent /opportunities requests"""
        tasks = [
            client.get(
                "/api/v1/performance/opportunities",
                params={
                    "factory_id": valid_factory_id,
                    "period": "month"
                }
            )
            for _ in range(10)
        ]
        
        responses = await asyncio.gather(*tasks)
        
        assert all(r.status_code == 200 for r in responses)
        
        # All should return same opportunities (deterministic)
        first_count = responses[0].json()["total_opportunities"]
        assert all(r.json()["total_opportunities"] == first_count for r in responses)
    
    @pytest.mark.asyncio
    async def test_concurrent_mixed_requests(self, client, valid_seu_name, valid_factory_id):
        """Test 100 concurrent requests across all endpoints"""
        import time
        
        tasks = []
        
        # 40 analyze requests
        for _ in range(40):
            tasks.append(
                client.post(
                    "/api/v1/performance/analyze",
                    params={
                        "seu_name": valid_seu_name,
                        "energy_source": "energy",
                        "analysis_date": "2025-11-05"
                    }
                )
            )
        
        # 30 opportunities requests
        for _ in range(30):
            tasks.append(
                client.get(
                    "/api/v1/performance/opportunities",
                    params={
                        "factory_id": valid_factory_id,
                        "period": "month"
                    }
                )
            )
        
        # 30 action plan requests
        for _ in range(30):
            tasks.append(
                client.post(
                    "/api/v1/performance/action-plan",
                    params={
                        "seu_name": valid_seu_name,
                        "issue_type": "excessive_idle"
                    }
                )
            )
        
        start = time.time()
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.time() - start
        
        # Count successes
        successful = sum(1 for r in responses if not isinstance(r, Exception) and r.status_code == 200)
        
        # Should have high success rate (>90%)
        success_rate = (successful / len(tasks)) * 100
        assert success_rate > 90, f"Success rate: {success_rate:.1f}%, expected >90%"
        
        print(f"\n✅ Load Test Results:")
        print(f"   Total requests: {len(tasks)}")
        print(f"   Successful: {successful}")
        print(f"   Success rate: {success_rate:.1f}%")
        print(f"   Total duration: {duration:.2f}s")
        print(f"   Avg response time: {(duration/len(tasks)*1000):.0f}ms")


class TestErrorHandling:
    """Test error handling across endpoints"""
    
    @pytest.mark.asyncio
    async def test_missing_required_params(self, client):
        """Test error for missing required parameters"""
        # Missing seu_name
        response = await client.post(
            "/api/v1/performance/analyze",
            params={
                "energy_source": "energy",
                "analysis_date": "2025-11-05"
            }
        )
        assert response.status_code == 422  # Validation error
        
        # Missing factory_id
        response = await client.get(
            "/api/v1/performance/opportunities",
            params={"period": "month"}
        )
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_invalid_date_format(self, client, valid_seu_name):
        """Test error for invalid date format"""
        response = await client.post(
            "/api/v1/performance/analyze",
            params={
                "seu_name": valid_seu_name,
                "energy_source": "energy",
                "analysis_date": "invalid-date"
            }
        )
        
        assert response.status_code == 422
