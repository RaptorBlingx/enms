"""
EnPI (Energy Performance Indicator) Tracker Service

ISO 50001 Compliance Engine - Tracks energy performance vs baseline year,
calculates cumulative savings, monitors targets, and generates compliance reports.

Phase 3 Milestone 3.1
"""

import logging
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from decimal import Decimal
from database import db

logger = logging.getLogger(__name__)


@dataclass
class EnPIBaseline:
    """EnPI baseline period data"""
    id: str
    seu_id: str
    seu_name: str
    baseline_year: int
    baseline_start_date: date
    baseline_end_date: date
    baseline_energy_kwh: float
    baseline_production_units: int
    baseline_operating_hours: float
    baseline_sec: float  # Specific Energy Consumption (kWh/unit)
    is_active: bool


@dataclass
class EnPIPerformance:
    """EnPI performance tracking data"""
    id: str
    seu_id: str
    seu_name: str
    period_start: date
    period_end: date
    period_type: str  # monthly, quarterly, annual
    
    # Actual performance
    actual_energy_kwh: float
    actual_production_units: int
    actual_sec: float
    
    # Expected performance (based on baseline)
    expected_energy_kwh: float
    expected_sec: float
    
    # Deviation metrics
    deviation_kwh: float
    deviation_percent: float
    cumulative_savings_kwh: float
    cumulative_savings_usd: float
    
    # ISO 50001 status
    iso_status: str  # excellent, on_track, requires_attention, critical
    compliance_notes: Optional[str] = None


@dataclass
class EnergyTarget:
    """Energy reduction target"""
    id: str
    target_type: str  # seu or factory
    target_year: int
    target_description: str
    baseline_year: int
    baseline_energy_kwh: float
    target_reduction_percent: float
    target_energy_kwh: float
    target_savings_kwh: float
    current_energy_kwh: Optional[float]
    current_savings_kwh: Optional[float]
    progress_percent: Optional[float]
    status: str  # active, achieved, missed, cancelled
    deadline: Optional[date]


class EnPITracker:
    """
    EnPI Tracker Service - ISO 50001 Compliance Engine
    
    Responsibilities:
    - Track baseline year energy performance
    - Calculate expected vs actual energy consumption
    - Compute cumulative savings
    - Monitor energy reduction targets
    - Generate ISO 50001 compliance reports
    """
    
    def __init__(self):
        self.electricity_rate = 0.15  # USD per kWh (configurable)
    
    # ========================================================================
    # Baseline Management
    # ========================================================================
    
    async def create_baseline(
        self,
        seu_id: str,
        baseline_year: int,
        baseline_start_date: date,
        baseline_end_date: date,
        created_by: str = "system"
    ) -> EnPIBaseline:
        """
        Create EnPI baseline for SEU from historical data.
        
        Automatically calculates baseline metrics from actual data:
        - Total energy consumption
        - Total production units
        - Operating hours
        - Specific Energy Consumption (SEC)
        
        Args:
            seu_id: SEU UUID
            baseline_year: Baseline year (e.g., 2024)
            baseline_start_date: Start of baseline period
            baseline_end_date: End of baseline period
            created_by: User creating baseline
        
        Returns:
            Created EnPI baseline
        
        Raises:
            ValueError: If insufficient data or invalid dates
        """
        logger.info(f"[EnPI] Creating baseline for SEU {seu_id}, year {baseline_year}")
        
        # Validate dates
        if baseline_end_date <= baseline_start_date:
            raise ValueError("Baseline end date must be after start date")
        
        if baseline_year != baseline_start_date.year:
            raise ValueError("Baseline year must match start date year")
        
        # Get SEU name
        query_seu = "SELECT name FROM seus WHERE id = $1"
        async with db.pool.acquire() as conn:
            seu_record = await conn.fetchrow(query_seu, seu_id)
            if not seu_record:
                raise ValueError(f"SEU {seu_id} not found")
            seu_name = seu_record['name']
        
        # Calculate baseline metrics from historical data (use 1-day aggregates for performance)
        query_metrics = """
            SELECT 
                COALESCE(SUM(er.total_energy_kwh), 0) as total_energy,
                COUNT(DISTINCT er.bucket) * 24 as operating_hours
            FROM energy_readings_1day er
            JOIN machines m ON er.machine_id = m.id
            JOIN seus s ON m.id = ANY(s.machine_ids)
            WHERE s.id = $1
              AND er.bucket >= $2::date
              AND er.bucket <= $3::date
        """
        
        # Get production count separately (from production_data 1-day aggregate if exists)
        query_production = """
            SELECT COALESCE(SUM(pd.production_count), 0) as total_production
            FROM production_data pd
            JOIN machines m ON pd.machine_id = m.id
            JOIN seus s ON m.id = ANY(s.machine_ids)
            WHERE s.id = $1
              AND DATE(pd.time) >= $2
              AND DATE(pd.time) <= $3
        """
        
        async with db.pool.acquire() as conn:
            # Get energy metrics
            metrics = await conn.fetchrow(
                query_metrics,
                seu_id,
                baseline_start_date,
                baseline_end_date
            )
            
            # Get production count
            production = await conn.fetchrow(
                query_production,
                seu_id,
                baseline_start_date,
                baseline_end_date
            )
        
        if not metrics or metrics['total_energy'] == 0:
            raise ValueError(
                f"No energy data found for {seu_name} in baseline period "
                f"{baseline_start_date} to {baseline_end_date}"
            )
        
        baseline_energy = float(metrics['total_energy'])
        baseline_production = int(production['total_production']) if production and production['total_production'] else 0
        baseline_hours = float(metrics['operating_hours'])
        
        # Calculate SEC (Specific Energy Consumption)
        baseline_sec = (baseline_energy / baseline_production) if baseline_production > 0 else 0
        
        # Insert baseline record
        query_insert = """
            INSERT INTO enpi_baselines (
                seu_id, baseline_year, baseline_start_date, baseline_end_date,
                baseline_energy_kwh, baseline_production_units, baseline_operating_hours,
                baseline_sec, is_active, created_by
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, true, $9)
            RETURNING id
        """
        
        async with db.pool.acquire() as conn:
            baseline_id = await conn.fetchval(
                query_insert,
                seu_id, baseline_year, baseline_start_date, baseline_end_date,
                baseline_energy, baseline_production, baseline_hours,
                baseline_sec, created_by
            )
        
        logger.info(
            f"[EnPI] Created baseline {baseline_id} for {seu_name}: "
            f"{baseline_energy:.2f} kWh, {baseline_production} units, SEC={baseline_sec:.4f}"
        )
        
        return EnPIBaseline(
            id=str(baseline_id),
            seu_id=str(seu_id),
            seu_name=seu_name,
            baseline_year=baseline_year,
            baseline_start_date=baseline_start_date,
            baseline_end_date=baseline_end_date,
            baseline_energy_kwh=baseline_energy,
            baseline_production_units=baseline_production,
            baseline_operating_hours=baseline_hours,
            baseline_sec=baseline_sec,
            is_active=True
        )
    
    async def get_baseline(self, seu_id: str, baseline_year: Optional[int] = None) -> Optional[EnPIBaseline]:
        """
        Get active EnPI baseline for SEU.
        
        Args:
            seu_id: SEU UUID
            baseline_year: Specific year (optional, defaults to most recent active)
        
        Returns:
            EnPI baseline or None if not found
        """
        if baseline_year:
            query = """
                SELECT eb.*, s.name as seu_name
                FROM enpi_baselines eb
                JOIN seus s ON eb.seu_id = s.id
                WHERE eb.seu_id = $1 AND eb.baseline_year = $2 AND eb.is_active = true
            """
            params = [seu_id, baseline_year]
        else:
            query = """
                SELECT eb.*, s.name as seu_name
                FROM enpi_baselines eb
                JOIN seus s ON eb.seu_id = s.id
                WHERE eb.seu_id = $1 AND eb.is_active = true
                ORDER BY eb.baseline_year DESC
                LIMIT 1
            """
            params = [seu_id]
        
        async with db.pool.acquire() as conn:
            record = await conn.fetchrow(query, *params)
        
        if not record:
            return None
        
        return EnPIBaseline(
            id=str(record['id']),
            seu_id=str(record['seu_id']),
            seu_name=record['seu_name'],
            baseline_year=record['baseline_year'],
            baseline_start_date=record['baseline_start_date'],
            baseline_end_date=record['baseline_end_date'],
            baseline_energy_kwh=float(record['baseline_energy_kwh']),
            baseline_production_units=int(record['baseline_production_units']) if record['baseline_production_units'] else 0,
            baseline_operating_hours=float(record['baseline_operating_hours']) if record['baseline_operating_hours'] else 0,
            baseline_sec=float(record['baseline_sec']) if record['baseline_sec'] else 0,
            is_active=record['is_active']
        )
    
    # ========================================================================
    # Performance Tracking
    # ========================================================================
    
    async def track_performance(
        self,
        seu_id: str,
        period_start: date,
        period_end: date,
        period_type: str = "monthly"
    ) -> EnPIPerformance:
        """
        Track EnPI performance for period vs baseline.
        
        Calculates:
        - Actual energy consumption and SEC
        - Expected energy consumption (based on baseline SEC × actual production)
        - Deviation from baseline
        - Cumulative savings (year-to-date)
        - ISO 50001 compliance status
        
        Args:
            seu_id: SEU UUID
            period_start: Period start date
            period_end: Period end date
            period_type: monthly, quarterly, or annual
        
        Returns:
            EnPI performance record
        
        Raises:
            ValueError: If no baseline exists or insufficient data
        """
        logger.info(f"[EnPI] Tracking performance for SEU {seu_id}, period {period_start} to {period_end}")
        
        # Get baseline
        baseline = await self.get_baseline(seu_id)
        if not baseline:
            raise ValueError(f"No active baseline found for SEU {seu_id}")
        
        # Get actual performance for period (use 1-day aggregates)
        query_actual = """
            SELECT 
                COALESCE(SUM(er.total_energy_kwh), 0) as total_energy,
                COUNT(DISTINCT er.bucket) * 24 as operating_hours
            FROM energy_readings_1day er
            JOIN machines m ON er.machine_id = m.id
            JOIN seus s ON m.id = ANY(s.machine_ids)
            WHERE s.id = $1
              AND er.bucket >= $2::date
              AND er.bucket <= $3::date
        """
        
        query_production_actual = """
            SELECT COALESCE(SUM(pd.production_count), 0) as total_production
            FROM production_data pd
            JOIN machines m ON pd.machine_id = m.id
            JOIN seus s ON m.id = ANY(s.machine_ids)
            WHERE s.id = $1
              AND DATE(pd.time) >= $2
              AND DATE(pd.time) <= $3
        """
        
        async with db.pool.acquire() as conn:
            actual = await conn.fetchrow(query_actual, seu_id, period_start, period_end)
            production_actual = await conn.fetchrow(query_production_actual, seu_id, period_start, period_end)
        
        if not actual or actual['total_energy'] == 0:
            raise ValueError(f"No energy data found for period {period_start} to {period_end}")
        
        actual_energy = float(actual['total_energy'])
        actual_production = int(production_actual['total_production']) if production_actual and production_actual['total_production'] else 0
        actual_sec = (actual_energy / actual_production) if actual_production > 0 else 0
        
        # Calculate expected energy (based on baseline SEC × actual production)
        expected_energy = baseline.baseline_sec * actual_production if actual_production > 0 else baseline.baseline_energy_kwh
        expected_sec = baseline.baseline_sec
        
        # Calculate deviation
        deviation_kwh = actual_energy - expected_energy
        deviation_percent = (deviation_kwh / expected_energy * 100) if expected_energy > 0 else 0
        
        # Calculate cumulative savings (year-to-date)
        year_start = date(period_end.year, 1, 1)
        cumulative_savings_kwh = await self._calculate_cumulative_savings(
            seu_id, year_start, period_end, baseline
        )
        cumulative_savings_usd = cumulative_savings_kwh * self.electricity_rate
        
        # Determine ISO 50001 status
        iso_status = self._determine_enpi_status(deviation_percent)
        
        # Insert performance record
        query_insert = """
            INSERT INTO enpi_performance (
                seu_id, baseline_id, period_start, period_end, period_type,
                actual_energy_kwh, actual_production_units, actual_operating_hours, actual_sec,
                expected_energy_kwh, expected_sec,
                deviation_kwh, deviation_percent,
                cumulative_savings_kwh, cumulative_savings_usd,
                iso_status
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
            RETURNING id
        """
        
        async with db.pool.acquire() as conn:
            performance_id = await conn.fetchval(
                query_insert,
                seu_id, baseline.id, period_start, period_end, period_type,
                actual_energy, actual_production, float(actual['operating_hours']), actual_sec,
                expected_energy, expected_sec,
                deviation_kwh, deviation_percent,
                cumulative_savings_kwh, cumulative_savings_usd,
                iso_status
            )
        
        logger.info(
            f"[EnPI] Performance tracked: actual={actual_energy:.2f} kWh, "
            f"expected={expected_energy:.2f} kWh, deviation={deviation_percent:.1f}%, "
            f"status={iso_status}"
        )
        
        return EnPIPerformance(
            id=str(performance_id),
            seu_id=str(seu_id),
            seu_name=baseline.seu_name,
            period_start=period_start,
            period_end=period_end,
            period_type=period_type,
            actual_energy_kwh=actual_energy,
            actual_production_units=actual_production,
            actual_sec=actual_sec,
            expected_energy_kwh=expected_energy,
            expected_sec=expected_sec,
            deviation_kwh=deviation_kwh,
            deviation_percent=deviation_percent,
            cumulative_savings_kwh=cumulative_savings_kwh,
            cumulative_savings_usd=cumulative_savings_usd,
            iso_status=iso_status
        )
    
    async def _calculate_cumulative_savings(
        self,
        seu_id: str,
        year_start: date,
        period_end: date,
        baseline: EnPIBaseline
    ) -> float:
        """Calculate year-to-date cumulative savings (use 1-day aggregates)."""
        query_ytd_energy = """
            SELECT COALESCE(SUM(er.total_energy_kwh), 0) as ytd_energy
            FROM energy_readings_1day er
            JOIN machines m ON er.machine_id = m.id
            JOIN seus s ON m.id = ANY(s.machine_ids)
            WHERE s.id = $1
              AND er.bucket >= $2::date
              AND er.bucket <= $3::date
        """
        
        query_ytd_production = """
            SELECT COALESCE(SUM(pd.production_count), 0) as ytd_production
            FROM production_data pd
            JOIN machines m ON pd.machine_id = m.id
            JOIN seus s ON m.id = ANY(s.machine_ids)
            WHERE s.id = $1
              AND DATE(pd.time) >= $2
              AND DATE(pd.time) <= $3
        """
        
        async with db.pool.acquire() as conn:
            ytd_energy_result = await conn.fetchrow(query_ytd_energy, seu_id, year_start, period_end)
            ytd_production_result = await conn.fetchrow(query_ytd_production, seu_id, year_start, period_end)
        
        ytd_energy = float(ytd_energy_result['ytd_energy']) if ytd_energy_result else 0
        ytd_production = int(ytd_production_result['ytd_production']) if ytd_production_result and ytd_production_result['ytd_production'] else 0
        
        # Expected energy = baseline SEC × actual production
        expected_ytd = baseline.baseline_sec * ytd_production if ytd_production > 0 else ytd_energy
        
        # Cumulative savings = expected - actual (negative if overconsumption)
        return expected_ytd - ytd_energy
    
    def _determine_enpi_status(self, deviation_percent: float) -> str:
        """
        Determine ISO 50001 compliance status based on deviation from baseline.
        
        Status definitions:
        - excellent: >5% improvement (below baseline)
        - on_track: ±5% of baseline
        - requires_attention: 5-15% above baseline
        - critical: >15% above baseline
        """
        if deviation_percent < -5:
            return "excellent"
        elif deviation_percent <= 5:
            return "on_track"
        elif deviation_percent <= 15:
            return "requires_attention"
        else:
            return "critical"
    
    # ========================================================================
    # Target Management
    # ========================================================================
    
    async def create_target(
        self,
        target_type: str,
        seu_id: Optional[str],
        factory_id: Optional[str],
        target_year: int,
        target_description: str,
        baseline_year: int,
        target_reduction_percent: float,
        deadline: Optional[date] = None,
        created_by: str = "system"
    ) -> EnergyTarget:
        """
        Create energy reduction target.
        
        Args:
            target_type: 'seu' or 'factory'
            seu_id: SEU UUID (if SEU target)
            factory_id: Factory UUID (if factory target)
            target_year: Target year
            target_description: Description
            baseline_year: Reference baseline year
            target_reduction_percent: Target reduction % (e.g., 10 for 10% reduction)
            deadline: Target deadline
            created_by: User creating target
        
        Returns:
            Created energy target
        """
        logger.info(f"[EnPI] Creating {target_type} target: {target_reduction_percent}% reduction by {target_year}")
        
        # Get baseline energy
        if target_type == "seu":
            baseline = await self.get_baseline(seu_id, baseline_year)
            if not baseline:
                raise ValueError(f"No baseline found for SEU {seu_id}, year {baseline_year}")
            baseline_energy = baseline.baseline_energy_kwh
        else:
            # Factory-wide baseline (sum of all SEUs)
            query = """
                SELECT COALESCE(SUM(baseline_energy_kwh), 0) as total_baseline
                FROM enpi_baselines eb
                JOIN seus s ON eb.seu_id = s.id
                JOIN machines m ON m.id = ANY(s.machine_ids)
                WHERE m.factory_id = $1 AND eb.baseline_year = $2 AND eb.is_active = true
            """
            async with db.pool.acquire() as conn:
                result = await conn.fetchval(query, factory_id, baseline_year)
            baseline_energy = float(result) if result else 0
            
            if baseline_energy == 0:
                raise ValueError(f"No baselines found for factory {factory_id}, year {baseline_year}")
        
        # Calculate target values
        target_savings_kwh = baseline_energy * (target_reduction_percent / 100)
        target_energy_kwh = baseline_energy - target_savings_kwh
        
        # Insert target
        query_insert = """
            INSERT INTO energy_targets (
                target_type, seu_id, factory_id, target_year, target_description,
                baseline_year, baseline_energy_kwh,
                target_reduction_percent, target_energy_kwh, target_savings_kwh,
                status, deadline, created_by
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, 'active', $11, $12)
            RETURNING id
        """
        
        async with db.pool.acquire() as conn:
            target_id = await conn.fetchval(
                query_insert,
                target_type, seu_id, factory_id, target_year, target_description,
                baseline_year, baseline_energy,
                target_reduction_percent, target_energy_kwh, target_savings_kwh,
                deadline, created_by
            )
        
        logger.info(
            f"[EnPI] Created target {target_id}: reduce {target_reduction_percent}% "
            f"({target_savings_kwh:.2f} kWh) from {baseline_energy:.2f} kWh"
        )
        
        return EnergyTarget(
            id=str(target_id),
            target_type=target_type,
            target_year=target_year,
            target_description=target_description,
            baseline_year=baseline_year,
            baseline_energy_kwh=baseline_energy,
            target_reduction_percent=target_reduction_percent,
            target_energy_kwh=target_energy_kwh,
            target_savings_kwh=target_savings_kwh,
            current_energy_kwh=None,
            current_savings_kwh=None,
            progress_percent=None,
            status="active",
            deadline=deadline
        )
    
    async def update_target_progress(self, target_id: str) -> EnergyTarget:
        """
        Update energy target progress with current year-to-date data.
        
        Calculates:
        - Current year-to-date energy consumption
        - Current savings vs baseline
        - Progress % towards target
        - Updates status (active, achieved, at risk)
        """
        # Get target details
        query_target = """
            SELECT * FROM energy_targets WHERE id = $1
        """
        
        async with db.pool.acquire() as conn:
            target = await conn.fetchrow(query_target, target_id)
        
        if not target:
            raise ValueError(f"Target {target_id} not found")
        
        # Calculate current YTD energy
        year_start = date(target['target_year'], 1, 1)
        today = date.today()
        
        if target['target_type'] == 'seu':
            query_ytd = """
                SELECT COALESCE(SUM(total_energy_kwh), 0) as ytd_energy
                FROM energy_readings_1day er
                JOIN machines m ON er.machine_id = m.id
                JOIN seus s ON m.id = ANY(s.machine_ids)
                WHERE s.id = $1
                  AND er.bucket >= $2::date
                  AND er.bucket <= $3::date
            """
            params = [target['seu_id'], year_start, today]
        else:
            query_ytd = """
                SELECT COALESCE(SUM(total_energy_kwh), 0) as ytd_energy
                FROM energy_readings_1day er
                JOIN machines m ON er.machine_id = m.id
                WHERE m.factory_id = $1
                  AND er.bucket >= $2::date
                  AND er.bucket <= $3::date
            """
            params = [target['factory_id'], year_start, today]
        
        async with db.pool.acquire() as conn:
            ytd_energy = float(await conn.fetchval(query_ytd, *params))
        
        # Calculate savings and progress
        baseline_energy = float(target['baseline_energy_kwh'])
        current_savings = baseline_energy - ytd_energy
        target_savings = float(target['target_savings_kwh'])
        
        # Calculate progress (cap at 999.99% to fit NUMERIC(5,2) constraint)
        progress_percent = (current_savings / target_savings * 100) if target_savings > 0 else 0
        progress_percent = min(999.99, max(-999.99, progress_percent))  # Cap to field limits
        
        # Determine status
        if progress_percent >= 100:
            status = "achieved"
        elif progress_percent < 50 and today.month > 6:  # Behind at mid-year
            status = "at_risk"
        else:
            status = "active"
        
        # Update target
        query_update = """
            UPDATE energy_targets
            SET current_energy_kwh = $1,
                current_savings_kwh = $2,
                progress_percent = $3,
                status = $4,
                updated_at = NOW()
            WHERE id = $5
        """
        
        async with db.pool.acquire() as conn:
            await conn.execute(
                query_update,
                ytd_energy, current_savings, progress_percent, status, target_id
            )
        
        logger.info(
            f"[EnPI] Target {target_id} progress: {progress_percent:.1f}% "
            f"({current_savings:.2f}/{target_savings:.2f} kWh), status={status}"
        )
        
        return EnergyTarget(
            id=str(target_id),
            target_type=target['target_type'],
            target_year=target['target_year'],
            target_description=target['target_description'],
            baseline_year=target['baseline_year'],
            baseline_energy_kwh=baseline_energy,
            target_reduction_percent=float(target['target_reduction_percent']),
            target_energy_kwh=float(target['target_energy_kwh']),
            target_savings_kwh=target_savings,
            current_energy_kwh=ytd_energy,
            current_savings_kwh=current_savings,
            progress_percent=progress_percent,
            status=status,
            deadline=target['deadline']
        )
