"""
Energy Performance Engine - Core Intelligence Layer

Orchestrates complete energy performance analysis by connecting:
- Baseline prediction service
- Anomaly detection service  
- KPI calculation service
- Root cause analysis
- Recommendation generation

This is the "brain" of EnMS v3 that provides actionable insights,
not just raw data.

Author: EnMS v3 Team
Created: November 6, 2025 (Phase 2, Milestone 2.1)
"""

from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Any
from enum import Enum
import logging
from dataclasses import dataclass

from database import db
from services.baseline_service import BaselineService
from services.anomaly_service import AnomalyService

logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================

class ImprovementType(str, Enum):
    """Types of energy improvement opportunities"""
    INEFFICIENT_SCHEDULING = "inefficient_scheduling"
    EXCESSIVE_IDLE = "excessive_idle"
    BASELINE_DRIFT = "baseline_drift"
    ANOMALY_PATTERN = "anomaly_pattern"
    PEAK_DEMAND = "peak_demand"
    LOAD_BALANCING = "load_balancing"


class ImplementationEffort(str, Enum):
    """Implementation effort levels"""
    LOW = "low"          # < 1 day, no cost
    MEDIUM = "medium"    # 1-5 days, < $1000
    HIGH = "high"        # > 5 days, > $1000


class Priority(str, Enum):
    """Recommendation priority"""
    CRITICAL = "critical"  # Immediate action required
    HIGH = "high"         # Address within week
    MEDIUM = "medium"     # Address within month
    LOW = "low"           # Nice to have


class ISO50001Status(str, Enum):
    """ISO 50001 compliance status"""
    EXCELLENT = "excellent"          # Performance better than baseline
    ON_TARGET = "on_target"          # Within ±5% of target
    REQUIRES_ATTENTION = "requires_attention"  # 5-15% over target
    NON_COMPLIANT = "non_compliant"  # >15% over target


@dataclass
class RootCauseAnalysis:
    """Root cause analysis results"""
    primary_factor: str
    impact_description: str
    contributing_factors: List[str]
    confidence: float  # 0-1


@dataclass
class Recommendation:
    """Actionable recommendation"""
    action: str
    type: str  # operational, maintenance, capital
    potential_savings_kwh: float
    potential_savings_usd: float
    implementation_effort: ImplementationEffort
    priority: Priority
    expected_roi_days: int
    detailed_steps: Optional[List[str]] = None


@dataclass
class PerformanceAnalysis:
    """Complete SEU performance analysis"""
    seu_name: str
    energy_source: str
    date: date
    actual_energy_kwh: float
    baseline_energy_kwh: float
    deviation_kwh: float
    deviation_percent: float
    deviation_cost_usd: float
    efficiency_score: float  # 0-1, 1 = perfect
    root_cause_analysis: RootCauseAnalysis
    recommendations: List[Recommendation]
    iso50001_status: ISO50001Status
    voice_summary: str
    timestamp: datetime


@dataclass
class ImprovementOpportunity:
    """Energy improvement opportunity"""
    rank: int
    seu_name: str
    issue_type: ImprovementType
    description: str
    potential_savings_kwh: float
    potential_savings_usd: float
    effort: ImplementationEffort
    roi_days: int
    recommended_action: str
    detailed_analysis: Optional[str] = None


@dataclass
class ActionPlan:
    """ISO 50001 action plan"""
    id: str
    seu_name: str
    problem_statement: str
    root_causes: List[str]
    actions: List[Dict[str, Any]]  # Prioritized actions
    expected_outcomes: Dict[str, float]  # energy_kwh, cost_usd, carbon_kg
    monitoring_plan: List[str]
    target_date: date
    status: str  # draft, approved, in_progress, completed


# ============================================================================
# Energy Performance Engine
# ============================================================================

class EnergyPerformanceEngine:
    """
    Core intelligence layer for EnMS v3.
    
    Provides:
    - Complete SEU performance analysis
    - Root cause identification
    - Actionable recommendations
    - Improvement opportunity detection
    - Action plan generation
    """
    
    def __init__(self):
        self.baseline_service = BaselineService()
        self.anomaly_service = AnomalyService()
        self.electricity_rate = 0.15  # USD per kWh (configurable)
        logger.info("[PERF-ENGINE] Energy Performance Engine initialized")
    
    # ========================================================================
    # Main Analysis Methods
    # ========================================================================
    
    async def analyze_seu_performance(
        self,
        seu_name: str,
        energy_source: str,
        analysis_date: date
    ) -> PerformanceAnalysis:
        """
        Complete performance analysis for a SEU on specific date.
        
        Workflow:
        1. Get actual energy consumption
        2. Get baseline prediction
        3. Calculate deviation
        4. Perform root cause analysis
        5. Generate recommendations
        6. Determine ISO 50001 status
        7. Create voice summary
        
        Args:
            seu_name: SEU name (e.g., "Compressor-1")
            energy_source: Energy source (electricity, natural_gas, etc.)
            analysis_date: Date to analyze
        
        Returns:
            Complete PerformanceAnalysis with insights and recommendations
        
        Raises:
            ValueError: If SEU not found or no data available
        """
        logger.info(f"[PERF-ENGINE] Analyzing {seu_name} ({energy_source}) for {analysis_date}")
        
        try:
            # Step 1: Get actual energy consumption
            actual_kwh = await self._get_actual_energy(seu_name, energy_source, analysis_date)
            
            # Step 2: Get baseline prediction
            baseline_kwh = await self._get_baseline_prediction(seu_name, energy_source, analysis_date)
            
            # Step 3: Calculate deviation
            deviation_kwh = actual_kwh - baseline_kwh
            deviation_percent = (deviation_kwh / baseline_kwh * 100) if baseline_kwh > 0 else 0
            deviation_cost = abs(deviation_kwh) * self.electricity_rate
            
            # Step 4: Calculate efficiency score (0-1, 1 = perfect)
            efficiency_score = min(baseline_kwh / actual_kwh, 1.0) if actual_kwh > 0 else 0
            
            # Step 5: Root cause analysis
            root_cause = await self._analyze_root_cause(
                seu_name, energy_source, analysis_date, actual_kwh, baseline_kwh
            )
            
            # Step 6: Generate recommendations
            recommendations = await self._generate_recommendations(
                seu_name, energy_source, deviation_kwh, deviation_percent, root_cause
            )
            
            # Step 7: Determine ISO 50001 status
            iso_status = self._determine_iso_status(deviation_percent)
            
            # Step 8: Create voice summary
            voice_summary = self._create_voice_summary(
                seu_name, actual_kwh, baseline_kwh, deviation_percent, 
                deviation_cost, root_cause
            )
            
            analysis = PerformanceAnalysis(
                seu_name=seu_name,
                energy_source=energy_source,
                date=analysis_date,
                actual_energy_kwh=actual_kwh,
                baseline_energy_kwh=baseline_kwh,
                deviation_kwh=deviation_kwh,
                deviation_percent=deviation_percent,
                deviation_cost_usd=deviation_cost,
                efficiency_score=efficiency_score,
                root_cause_analysis=root_cause,
                recommendations=recommendations,
                iso50001_status=iso_status,
                voice_summary=voice_summary,
                timestamp=datetime.utcnow()
            )
            
            logger.info(f"[PERF-ENGINE] Analysis complete: {deviation_percent:+.1f}% deviation")
            return analysis
            
        except Exception as e:
            logger.error(f"[PERF-ENGINE] Analysis failed: {str(e)}", exc_info=True)
            raise
    
    async def get_improvement_opportunities(
        self,
        factory_id: str,
        period: str = "month"
    ) -> List[ImprovementOpportunity]:
        """
        Proactive analysis: Find energy optimization opportunities.
        
        Scans all SEUs in factory for:
        - Inefficient scheduling patterns
        - Excessive idle time
        - Baseline drift (degradation)
        - Recurring anomaly patterns
        - Peak demand issues
        - Load balancing opportunities
        
        Args:
            factory_id: Factory UUID
            period: Analysis period (week, month, quarter)
        
        Returns:
            Ranked list of improvement opportunities (highest savings first)
        """
        logger.info(f"[PERF-ENGINE] Finding improvement opportunities for factory {factory_id}")
        
        opportunities = []
        
        # TODO: Implement opportunity detection logic
        # 1. Query all SEUs in factory
        # 2. For each SEU, check for patterns
        # 3. Calculate potential savings
        # 4. Rank by ROI
        
        return opportunities
    
    async def generate_action_plan(
        self,
        seu_name: str,
        issue_type: str
    ) -> ActionPlan:
        """
        Generate structured ISO 50001 action plan for energy issue.
        
        Args:
            seu_name: SEU name
            issue_type: Type of issue (from ImprovementType enum)
        
        Returns:
            Complete ActionPlan with problem statement, actions, outcomes
        """
        logger.info(f"[PERF-ENGINE] Generating action plan for {seu_name} ({issue_type})")
        
        # TODO: Implement action plan generation
        # 1. Analyze historical data
        # 2. Identify root causes
        # 3. Generate prioritized actions
        # 4. Calculate expected outcomes
        # 5. Define monitoring plan
        
        raise NotImplementedError("Action plan generation coming in Milestone 2.1.5")
    
    # ========================================================================
    # Internal Helper Methods
    # ========================================================================
    
    async def _get_actual_energy(
        self,
        seu_name: str,
        energy_source: str,
        analysis_date: date
    ) -> float:
        """Get actual energy consumption for SEU on specific date."""
        
        start_time = datetime.combine(analysis_date, datetime.min.time())
        end_time = start_time + timedelta(days=1)
        
        query = """
            SELECT COALESCE(SUM(energy_kwh), 0) as total_energy
            FROM energy_readings er
            JOIN machines m ON er.machine_id = m.id
            JOIN seus s ON m.id = s.machine_id
            WHERE s.name = $1
              AND er.energy_source = $2
              AND er.time >= $3
              AND er.time < $4
        """
        
        async with db.pool.acquire() as conn:
            result = await conn.fetchrow(query, seu_name, energy_source, start_time, end_time)
            
        if result is None or result['total_energy'] == 0:
            raise ValueError(f"No data found for {seu_name} on {analysis_date}")
        
        return float(result['total_energy'])
    
    async def _get_baseline_prediction(
        self,
        seu_name: str,
        energy_source: str,
        analysis_date: date
    ) -> float:
        """Get baseline prediction for SEU on specific date."""
        
        # Use baseline service to get prediction
        # For MVP, use simple historical average
        # Later: Use trained ML models with features
        
        start_date = analysis_date - timedelta(days=30)
        end_date = analysis_date - timedelta(days=1)
        
        query = """
            SELECT AVG(daily_energy) as avg_energy
            FROM (
                SELECT DATE(er.time) as date, SUM(er.energy_kwh) as daily_energy
                FROM energy_readings er
                JOIN machines m ON er.machine_id = m.id
                JOIN seus s ON m.id = s.machine_id
                WHERE s.name = $1
                  AND er.energy_source = $2
                  AND DATE(er.time) >= $3
                  AND DATE(er.time) <= $4
                GROUP BY DATE(er.time)
            ) daily_data
        """
        
        async with db.pool.acquire() as conn:
            result = await conn.fetchrow(query, seu_name, energy_source, start_date, end_date)
        
        if result is None or result['avg_energy'] is None:
            raise ValueError(f"No baseline data available for {seu_name}")
        
        return float(result['avg_energy'])
    
    async def _analyze_root_cause(
        self,
        seu_name: str,
        energy_source: str,
        analysis_date: date,
        actual_kwh: float,
        baseline_kwh: float
    ) -> RootCauseAnalysis:
        """
        Perform root cause analysis for energy deviation.
        
        MVP: Simple heuristics based on available data
        Future: ML-based attribution analysis
        """
        
        deviation_percent = ((actual_kwh - baseline_kwh) / baseline_kwh * 100) if baseline_kwh > 0 else 0
        
        # Simple rule-based root cause (MVP)
        if abs(deviation_percent) < 5:
            primary_factor = "normal_variation"
            impact_description = "Energy consumption within expected range"
            contributing_factors = []
            confidence = 0.9
        elif deviation_percent > 0:
            # Over consumption
            primary_factor = "increased_load"
            impact_description = f"Energy consumption {abs(deviation_percent):.1f}% above baseline"
            contributing_factors = [
                "Possible production increase",
                "Equipment degradation",
                "Inefficient operation"
            ]
            confidence = 0.7
        else:
            # Under consumption
            primary_factor = "reduced_load"
            impact_description = f"Energy consumption {abs(deviation_percent):.1f}% below baseline"
            contributing_factors = [
                "Production decrease",
                "Equipment offline",
                "Process optimization"
            ]
            confidence = 0.7
        
        return RootCauseAnalysis(
            primary_factor=primary_factor,
            impact_description=impact_description,
            contributing_factors=contributing_factors,
            confidence=confidence
        )
    
    async def _generate_recommendations(
        self,
        seu_name: str,
        energy_source: str,
        deviation_kwh: float,
        deviation_percent: float,
        root_cause: RootCauseAnalysis
    ) -> List[Recommendation]:
        """Generate actionable recommendations based on analysis."""
        
        recommendations = []
        
        # Rule-based recommendations (MVP)
        if abs(deviation_percent) < 5:
            # Performance is good, no recommendations
            pass
        
        elif deviation_percent > 15:
            # Significant overconsumption
            recommendations.append(Recommendation(
                action="Investigate equipment efficiency",
                type="maintenance",
                potential_savings_kwh=abs(deviation_kwh) * 0.3,
                potential_savings_usd=abs(deviation_kwh) * 0.3 * self.electricity_rate,
                implementation_effort=ImplementationEffort.MEDIUM,
                priority=Priority.HIGH,
                expected_roi_days=30,
                detailed_steps=[
                    "Schedule equipment inspection",
                    "Check for air leaks or wear",
                    "Review operating parameters"
                ]
            ))
            
            recommendations.append(Recommendation(
                action="Optimize operating schedule",
                type="operational",
                potential_savings_kwh=abs(deviation_kwh) * 0.2,
                potential_savings_usd=abs(deviation_kwh) * 0.2 * self.electricity_rate,
                implementation_effort=ImplementationEffort.LOW,
                priority=Priority.HIGH,
                expected_roi_days=7,
                detailed_steps=[
                    "Review production schedule",
                    "Identify off-peak operations",
                    "Implement load shifting"
                ]
            ))
        
        elif deviation_percent > 5:
            # Moderate overconsumption
            recommendations.append(Recommendation(
                action="Review operational parameters",
                type="operational",
                potential_savings_kwh=abs(deviation_kwh) * 0.5,
                potential_savings_usd=abs(deviation_kwh) * 0.5 * self.electricity_rate,
                implementation_effort=ImplementationEffort.LOW,
                priority=Priority.MEDIUM,
                expected_roi_days=14
            ))
        
        return recommendations
    
    def _determine_iso_status(self, deviation_percent: float) -> ISO50001Status:
        """Determine ISO 50001 compliance status based on deviation."""
        
        if deviation_percent < -5:
            return ISO50001Status.EXCELLENT
        elif deviation_percent <= 5:
            return ISO50001Status.ON_TARGET
        elif deviation_percent <= 15:
            return ISO50001Status.REQUIRES_ATTENTION
        else:
            return ISO50001Status.NON_COMPLIANT
    
    def _create_voice_summary(
        self,
        seu_name: str,
        actual_kwh: float,
        baseline_kwh: float,
        deviation_percent: float,
        deviation_cost: float,
        root_cause: RootCauseAnalysis
    ) -> str:
        """Create voice-friendly summary for TTS."""
        
        if abs(deviation_percent) < 5:
            return (
                f"{seu_name} is performing as expected. "
                f"Energy consumption is {actual_kwh:.1f} kilowatt hours, "
                f"which is within normal range."
            )
        elif deviation_percent > 0:
            return (
                f"{seu_name} used {abs(deviation_percent):.1f}% more energy than expected today. "
                f"Actual consumption was {actual_kwh:.1f} kilowatt hours "
                f"compared to a baseline of {baseline_kwh:.1f}. "
                f"This cost an extra ${deviation_cost:.2f}. "
                f"{root_cause.impact_description}."
            )
        else:
            return (
                f"{seu_name} used {abs(deviation_percent):.1f}% less energy than expected today. "
                f"Actual consumption was {actual_kwh:.1f} kilowatt hours "
                f"compared to a baseline of {baseline_kwh:.1f}. "
                f"This saved ${deviation_cost:.2f}. "
                f"{root_cause.impact_description}."
            )


# ============================================================================
# Singleton Instance
# ============================================================================

_engine_instance = None

def get_performance_engine() -> EnergyPerformanceEngine:
    """Get singleton instance of Energy Performance Engine."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = EnergyPerformanceEngine()
    return _engine_instance
