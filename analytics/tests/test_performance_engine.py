"""
Unit tests for Energy Performance Engine

Tests all core methods:
- analyze_seu_performance()
- _get_improvement_opportunities()
- _generate_action_plan()
- Root cause analysis
- Recommendation generation
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from services.energy_performance_engine import (
    EnergyPerformanceEngine,
    ImprovementType,
    ImplementationEffort,
    Priority,
    ISO50001Status,
    PerformanceAnalysis,
    ImprovementOpportunity,
    ActionPlan
)


@pytest.fixture
def engine():
    """Create EnergyPerformanceEngine instance"""
    return EnergyPerformanceEngine()


@pytest.fixture
def mock_db_pool():
    """Mock asyncpg database pool"""
    pool = MagicMock()
    conn = AsyncMock()
    pool.acquire.return_value.__aenter__.return_value = conn
    return pool, conn


class TestAnalyzeSEUPerformance:
    """Test analyze_seu_performance() method"""
    
    @pytest.mark.asyncio
    async def test_analyze_with_positive_deviation(self, engine, mock_db_pool):
        """Test analysis when actual > baseline (overconsumption)"""
        pool, conn = mock_db_pool
        
        # Mock actual energy reading (500 kWh)
        conn.fetchrow.side_effect = [
            {"total_energy": 500.0, "hours_elapsed": 24.0},  # Actual consumption
            {"avg_energy": 400.0}  # Baseline prediction
        ]
        
        with patch('services.energy_performance_engine.db.pool', pool):
            result = await engine.analyze_seu_performance(
                seu_name="Compressor-1",
                energy_source="energy",
                analysis_date=date(2025, 11, 6)
            )
        
        assert isinstance(result, PerformanceAnalysis)
        assert result.seu_name == "Compressor-1"
        assert result.actual_energy_kwh == 500.0
        assert result.baseline_energy_kwh == 400.0
        assert result.deviation_kwh == 100.0
        assert result.deviation_percent == 25.0
        assert result.iso_status == ISO50001Status.REQUIRES_ATTENTION
        assert result.efficiency_score < 1.0
        assert len(result.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_with_negative_deviation(self, engine, mock_db_pool):
        """Test analysis when actual < baseline (savings)"""
        pool, conn = mock_db_pool
        
        # Mock actual energy reading (300 kWh) vs baseline (400 kWh)
        conn.fetchrow.side_effect = [
            {"total_energy": 300.0, "hours_elapsed": 24.0},
            {"avg_energy": 400.0}
        ]
        
        with patch('services.energy_performance_engine.db.pool', pool):
            result = await engine.analyze_seu_performance(
                seu_name="HVAC-Main",
                energy_source="energy",
                analysis_date=date(2025, 11, 6)
            )
        
        assert result.actual_energy_kwh == 300.0
        assert result.baseline_energy_kwh == 400.0
        assert result.deviation_kwh == -100.0
        assert result.deviation_percent == -25.0
        assert result.iso_status == ISO50001Status.EXCELLENT
        assert result.efficiency_score > 1.0
    
    @pytest.mark.asyncio
    async def test_analyze_incomplete_day_projection(self, engine, mock_db_pool):
        """Test projection for incomplete day (14 hours of data)"""
        pool, conn = mock_db_pool
        
        # Mock partial day data (14 hours, 350 kWh)
        conn.fetchrow.side_effect = [
            {"total_energy": 350.0, "hours_elapsed": 14.0},
            {"avg_energy": 600.0}
        ]
        
        with patch('services.energy_performance_engine.db.pool', pool):
            result = await engine.analyze_seu_performance(
                seu_name="Injection-Molding-1",
                energy_source="energy",
                analysis_date=datetime.utcnow().date()  # Today (incomplete)
            )
        
        # Should project to 24h: (350 / 14) * 24 = 600 kWh
        assert result.actual_energy_kwh == pytest.approx(600.0, rel=0.1)
        assert "projected from" in result.voice_summary.lower()
    
    @pytest.mark.asyncio
    async def test_analyze_no_data_raises_error(self, engine, mock_db_pool):
        """Test error when no data available"""
        pool, conn = mock_db_pool
        
        # Mock no data
        conn.fetchrow.side_effect = [
            None,  # No actual readings
            {"avg_energy": 400.0}
        ]
        
        with patch('services.energy_performance_engine.db.pool', pool):
            with pytest.raises(ValueError, match="No energy data available"):
                await engine.analyze_seu_performance(
                    seu_name="NonExistent-Machine",
                    energy_source="energy",
                    analysis_date=date(2025, 11, 6)
                )


class TestRootCauseAnalysis:
    """Test _analyze_root_cause() method"""
    
    @pytest.mark.asyncio
    async def test_root_cause_normal_variation(self, engine):
        """Test root cause for deviation within ±5%"""
        result = await engine._analyze_root_cause(
            seu_name="Compressor-1",
            energy_source="energy",
            analysis_date=date(2025, 11, 6),
            actual_energy_kwh=400.0,
            baseline_energy_kwh=410.0
        )
        
        assert result.primary_factor == "normal_variation"
        assert result.confidence >= 0.9
        assert "expected range" in result.impact_description.lower()
    
    @pytest.mark.asyncio
    async def test_root_cause_overconsumption(self, engine):
        """Test root cause for significant overconsumption"""
        result = await engine._analyze_root_cause(
            seu_name="Boiler-1",
            energy_source="natural_gas",
            analysis_date=date(2025, 11, 6),
            actual_energy_kwh=500.0,
            baseline_energy_kwh=400.0
        )
        
        assert result.primary_factor == "increased_load"
        assert result.confidence >= 0.5
        assert len(result.contributing_factors) > 0
    
    @pytest.mark.asyncio
    async def test_root_cause_savings(self, engine):
        """Test root cause for energy savings"""
        result = await engine._analyze_root_cause(
            seu_name="HVAC-Main",
            energy_source="energy",
            analysis_date=date(2025, 11, 6),
            actual_energy_kwh=300.0,
            baseline_energy_kwh=400.0
        )
        
        assert result.primary_factor == "reduced_load"
        assert result.confidence >= 0.5
        assert len(result.contributing_factors) > 0


class TestRecommendationGeneration:
    """Test _generate_recommendations() method"""
    
    def test_recommendations_for_high_deviation(self, engine):
        """Test recommendations for >15% overconsumption"""
        recommendations = engine._generate_recommendations(
            deviation_percent=20.0,
            deviation_kwh=100.0,
            seu_name="Compressor-1"
        )
        
        assert len(recommendations) >= 2
        assert any(r.priority == Priority.HIGH for r in recommendations)
        assert all(r.potential_savings_kwh > 0 for r in recommendations)
        assert all(r.potential_savings_usd > 0 for r in recommendations)
    
    def test_recommendations_for_moderate_deviation(self, engine):
        """Test recommendations for 5-15% deviation"""
        recommendations = engine._generate_recommendations(
            deviation_percent=8.0,
            deviation_kwh=40.0,
            seu_name="HVAC-Main"
        )
        
        assert len(recommendations) >= 1
        assert any(r.priority == Priority.MEDIUM for r in recommendations)
    
    def test_no_recommendations_for_normal(self, engine):
        """Test no recommendations for deviation <5%"""
        recommendations = engine._generate_recommendations(
            deviation_percent=2.0,
            deviation_kwh=10.0,
            seu_name="Conveyor-A"
        )
        
        assert len(recommendations) == 0


class TestImprovementOpportunities:
    """Test get_improvement_opportunities() method"""
    
    @pytest.mark.asyncio
    async def test_opportunities_detection(self, engine, mock_db_pool):
        """Test opportunity detection across multiple SEUs"""
        pool, conn = mock_db_pool
        
        # Mock SEUs query
        conn.fetch.return_value = [
            {"id": "uuid1", "name": "Compressor-1"},
            {"id": "uuid2", "name": "HVAC-Main"}
        ]
        
        # Mock opportunity detection queries (idle, scheduling, drift)
        conn.fetchrow.side_effect = [
            # Compressor-1 idle check
            {"idle_percent": 35.0, "avg_idle_power": 5.0},
            # Compressor-1 scheduling check
            {"offhours_percent": 25.0, "offhours_kwh": 200.0},
            # Compressor-1 drift check
            None,
            # HVAC-Main idle check
            None,
            # HVAC-Main scheduling check
            {"offhours_percent": 40.0, "offhours_kwh": 300.0},
            # HVAC-Main drift check
            {"drift_percent": 15.0}
        ]
        
        with patch('services.energy_performance_engine.db.pool', pool):
            opportunities = await engine.get_improvement_opportunities(
                factory_id="factory-uuid",
                period="month"
            )
        
        assert len(opportunities) > 0
        assert all(isinstance(o, ImprovementOpportunity) for o in opportunities)
        assert all(o.rank > 0 for o in opportunities)
        # Ranked by savings (highest first)
        if len(opportunities) > 1:
            assert opportunities[0].potential_savings_kwh >= opportunities[-1].potential_savings_kwh
    
    @pytest.mark.asyncio
    async def test_no_opportunities_found(self, engine, mock_db_pool):
        """Test when no opportunities detected"""
        pool, conn = mock_db_pool
        
        # Mock SEUs query
        conn.fetch.return_value = [
            {"id": "uuid1", "name": "Compressor-1"}
        ]
        
        # Mock all detection queries return None (no issues)
        conn.fetchrow.side_effect = [None, None, None]
        
        with patch('services.energy_performance_engine.db.pool', pool):
            opportunities = await engine.get_improvement_opportunities(
                factory_id="factory-uuid",
                period="week"
            )
        
        assert len(opportunities) == 0


class TestActionPlanGeneration:
    """Test generate_action_plan() method"""
    
    @pytest.mark.asyncio
    async def test_action_plan_excessive_idle(self, engine):
        """Test action plan for excessive idle issue"""
        plan = await engine.generate_action_plan(
            seu_name="HVAC-Main",
            issue_type="excessive_idle"
        )
        
        assert isinstance(plan, ActionPlan)
        assert plan.seu_name == "HVAC-Main"
        assert "idle" in plan.problem_statement.lower()
        assert len(plan.root_causes) >= 3
        assert len(plan.actions) == 3
        assert all(a["priority"] in [1, 2, 3] for a in plan.actions)
        assert plan.expected_outcomes["energy_kwh"] > 0
        assert len(plan.monitoring_plan) > 0
        assert plan.status == "draft"
    
    @pytest.mark.asyncio
    async def test_action_plan_inefficient_scheduling(self, engine):
        """Test action plan for scheduling issue"""
        plan = await engine.generate_action_plan(
            seu_name="Compressor-1",
            issue_type="inefficient_scheduling"
        )
        
        assert "off-hours" in plan.problem_statement.lower() or "scheduling" in plan.problem_statement.lower()
        assert len(plan.actions) == 3
        assert plan.expected_outcomes["cost_usd"] > 0
    
    @pytest.mark.asyncio
    async def test_action_plan_baseline_drift(self, engine):
        """Test action plan for equipment degradation"""
        plan = await engine.generate_action_plan(
            seu_name="Injection-Molding-1",
            issue_type="baseline_drift"
        )
        
        assert "degradation" in plan.problem_statement.lower() or "increase" in plan.problem_statement.lower()
        assert len(plan.root_causes) >= 3
    
    @pytest.mark.asyncio
    async def test_action_plan_invalid_issue_type(self, engine):
        """Test error for invalid issue type"""
        with pytest.raises(ValueError, match="Invalid issue_type"):
            await engine.generate_action_plan(
                seu_name="Compressor-1",
                issue_type="invalid_type"
            )


class TestISO50001Status:
    """Test _determine_iso_status() method"""
    
    def test_iso_excellent_status(self, engine):
        """Test excellent status for negative deviation"""
        status = engine._determine_iso_status(-10.0)
        assert status == ISO50001Status.EXCELLENT
    
    def test_iso_on_target_status(self, engine):
        """Test on-target status for ±5% deviation"""
        assert engine._determine_iso_status(3.0) == ISO50001Status.ON_TARGET
        assert engine._determine_iso_status(-2.0) == ISO50001Status.ON_TARGET
    
    def test_iso_requires_attention(self, engine):
        """Test requires-attention for 5-15% deviation"""
        status = engine._determine_iso_status(10.0)
        assert status == ISO50001Status.REQUIRES_ATTENTION
    
    def test_iso_non_compliant(self, engine):
        """Test non-compliant for >15% deviation"""
        status = engine._determine_iso_status(20.0)
        assert status == ISO50001Status.NON_COMPLIANT


class TestVoiceSummary:
    """Test _create_voice_summary() method"""
    
    def test_voice_summary_overconsumption(self, engine):
        """Test voice summary for overconsumption"""
        summary = engine._create_voice_summary(
            seu_name="Compressor-1",
            actual_energy_kwh=500.0,
            baseline_energy_kwh=400.0,
            deviation_percent=25.0,
            iso_status=ISO50001Status.REQUIRES_ATTENTION,
            is_incomplete_day=False
        )
        
        assert "Compressor-1" in summary
        assert "500" in summary or "25" in summary
        assert "above" in summary.lower() or "more" in summary.lower()
    
    def test_voice_summary_savings(self, engine):
        """Test voice summary for energy savings"""
        summary = engine._create_voice_summary(
            seu_name="HVAC-Main",
            actual_energy_kwh=300.0,
            baseline_energy_kwh=400.0,
            deviation_percent=-25.0,
            iso_status=ISO50001Status.EXCELLENT,
            is_incomplete_day=False
        )
        
        assert "HVAC-Main" in summary
        assert "below" in summary.lower() or "less" in summary.lower() or "saved" in summary.lower()
    
    def test_voice_summary_includes_projection_note(self, engine):
        """Test voice summary mentions projection for incomplete day"""
        summary = engine._create_voice_summary(
            seu_name="Boiler-1",
            actual_energy_kwh=450.0,
            baseline_energy_kwh=500.0,
            deviation_percent=-10.0,
            iso_status=ISO50001Status.ON_TARGET,
            is_incomplete_day=True
        )
        
        assert "projected" in summary.lower() or "incomplete" in summary.lower()
