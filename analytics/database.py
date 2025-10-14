"""
EnMS Analytics Service - Database Module
=========================================
Manages asyncpg connection pool and database operations.

Author: EnMS Team
Phase: 3 - Analytics & ML
"""

import asyncpg
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
from uuid import UUID

from config import settings

logger = logging.getLogger(__name__)


class Database:
    """Database connection pool manager."""
    
    def __init__(self):
        """Initialize database manager."""
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Create database connection pool."""
        try:
            self.pool = await asyncpg.create_pool(
                host=settings.DATABASE_HOST,
                port=settings.DATABASE_PORT,
                database=settings.DATABASE_NAME,
                user=settings.DATABASE_USER,
                password=settings.DATABASE_PASSWORD,
                min_size=settings.DATABASE_MIN_POOL_SIZE,
                max_size=settings.DATABASE_MAX_POOL_SIZE,
                command_timeout=60
            )
            logger.info(
                f"✓ Database pool created: "
                f"{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
            )
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}", exc_info=True)
            raise
    
    async def disconnect(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Database pool closed")
    
    async def health_check(self) -> bool:
        """Check database connectivity."""
        if not self.pool:
            return False
        try:
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database instance
db = Database()


# ============================================================================
# Helper Functions for Data Retrieval
# ============================================================================

async def get_machines(
    factory_id: Optional[UUID] = None,
    is_active: bool = True
) -> List[Dict[str, Any]]:
    """
    Get list of machines.
    
    Args:
        factory_id: Optional factory filter
        is_active: Filter by active status
        
    Returns:
        List of machine records
    """
    query = """
        SELECT 
            m.id, 
            m.factory_id, 
            m.name, 
            m.type, 
            m.rated_power_kw,
            m.is_active,
            f.name as factory_name,
            f.location as factory_location
        FROM machines m
        JOIN factories f ON m.factory_id = f.id
        WHERE m.is_active = $1
    """
    
    params = [is_active]
    
    if factory_id:
        query += " AND m.factory_id = $2"
        params.append(factory_id)
    
    query += " ORDER BY m.name"
    
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]


async def get_machine_by_id(machine_id: UUID) -> Optional[Dict[str, Any]]:
    """
    Get machine by ID.
    
    Args:
        machine_id: Machine UUID
        
    Returns:
        Machine record or None
    """
    query = """
        SELECT 
            m.id, 
            m.factory_id, 
            m.name, 
            m.type, 
            m.rated_power_kw,
            m.is_active,
            f.name as factory_name,
            f.location as factory_location
        FROM machines m
        JOIN factories f ON m.factory_id = f.id
        WHERE m.id = $1
    """
    
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(query, machine_id)
        return dict(row) if row else None


async def get_energy_readings(
    machine_id: UUID,
    start_time: datetime,
    end_time: datetime,
    include_machine_status: bool = True
) -> List[Dict[str, Any]]:
    """
    Get energy readings for a machine within time range.
    Uses 1-hour continuous aggregate for efficiency.
    
    Args:
        machine_id: Machine UUID
        start_time: Start of time range
        end_time: End of time range
        include_machine_status: Whether to filter by machine status
        
    Returns:
        List of energy reading records
    """
    # Base query using continuous aggregate (using 1min for now, TODO: create 1hour aggregate)
    query = """
        SELECT 
            er.bucket as time,
            er.machine_id,
            er.avg_power_kw,
            er.total_energy_kwh,
            er.max_power_kw as peak_demand_kw,
            er.min_power_kw,
            er.max_power_kw,
            er.avg_load_factor
        FROM energy_readings_1hour er
    """
    
    # Add machine status filter if requested
    if include_machine_status:
        query += """
            JOIN machine_status ms ON er.machine_id = ms.machine_id
        """
    
    query += """
        WHERE er.machine_id = $1
          AND er.bucket >= $2
          AND er.bucket <= $3
    """
    
    # Filter by machine status
    if include_machine_status:
        query += """
          AND ms.is_running = TRUE
          AND ms.current_mode NOT IN ('maintenance', 'fault', 'offline')
        """
    
    query += " ORDER BY er.bucket"
    
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(query, machine_id, start_time, end_time)
        return [dict(row) for row in rows]


async def get_production_data(
    machine_id: UUID,
    start_time: datetime,
    end_time: datetime
) -> List[Dict[str, Any]]:
    """
    Get production data for a machine within time range.
    Uses 1-hour continuous aggregate.
    
    Args:
        machine_id: Machine UUID
        start_time: Start of time range
        end_time: End of time range
        
    Returns:
        List of production data records
    """
    query = """
        SELECT 
            pd.bucket as time,
            pd.machine_id,
            pd.total_production_count,
            pd.avg_throughput as avg_throughput_units_per_hour,
            pd.avg_throughput as max_throughput_units_per_hour
        FROM production_data_1hour pd
        WHERE pd.machine_id = $1
          AND pd.bucket >= $2
          AND pd.bucket <= $3
        ORDER BY pd.bucket
    """
    
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(query, machine_id, start_time, end_time)
        return [dict(row) for row in rows]


async def get_environmental_data(
    machine_id: UUID,
    start_time: datetime,
    end_time: datetime
) -> List[Dict[str, Any]]:
    """
    Get environmental data for a machine within time range.
    Uses 1-hour continuous aggregate.
    
    Args:
        machine_id: Machine UUID
        start_time: Start of time range
        end_time: End of time range
        
    Returns:
        List of environmental data records
    """
    query = """
        SELECT 
            ed.bucket as time,
            ed.machine_id,
            ed.avg_outdoor_temp_c,
            ed.avg_indoor_temp_c,
            ed.avg_machine_temp_c,
            ed.avg_outdoor_humidity_percent,
            ed.avg_indoor_humidity_percent,
            ed.avg_pressure_bar
        FROM environmental_data_1hour ed
        WHERE ed.machine_id = $1
          AND ed.bucket >= $2
          AND ed.bucket <= $3
        ORDER BY ed.bucket
    """
    
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(query, machine_id, start_time, end_time)
        return [dict(row) for row in rows]


async def get_machine_data_combined(
    machine_id: UUID,
    start_time: datetime,
    end_time: datetime,
    include_machine_status: bool = True
) -> List[Dict[str, Any]]:
    """
    Get combined data (energy + production + environmental) for ML training.
    
    Args:
        machine_id: Machine UUID
        start_time: Start of time range
        end_time: End of time range
        include_machine_status: Whether to filter by machine status
        
    Returns:
        List of combined data records
    """
    query = """
        SELECT 
            er.bucket as time,
            er.machine_id,
            er.avg_power_kw,
            er.total_energy_kwh,
            er.max_power_kw as peak_demand_kw,
            er.avg_load_factor,
            pd.total_production_count,
            pd.avg_throughput as avg_throughput_units_per_hour,
            ed.avg_outdoor_temp_c,
            ed.avg_indoor_temp_c,
            ed.avg_machine_temp_c,
            ed.avg_pressure_bar
        FROM energy_readings_1hour er
        LEFT JOIN production_data_1hour pd 
            ON er.machine_id = pd.machine_id 
            AND er.bucket = pd.bucket
        LEFT JOIN environmental_data_1hour ed 
            ON er.machine_id = ed.machine_id 
            AND er.bucket = ed.bucket
    """
    
    # Add machine status filter if requested
    if include_machine_status:
        query += """
            JOIN machine_status ms ON er.machine_id = ms.machine_id
        """
    
    query += """
        WHERE er.machine_id = $1
          AND er.bucket >= $2
          AND er.bucket <= $3
    """
    
    # Filter by machine status
    if include_machine_status:
        query += """
          AND ms.is_running = TRUE
          AND ms.current_mode NOT IN ('maintenance', 'fault', 'offline')
        """
    
    query += " ORDER BY er.bucket"
    
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(query, machine_id, start_time, end_time)
        return [dict(row) for row in rows]


async def save_baseline_model(model_data: Dict[str, Any]) -> UUID:
    """
    Save baseline model to database.
    
    Args:
        model_data: Model metadata and parameters
        
    Returns:
        Model ID (UUID)
    """
    query = """
        INSERT INTO energy_baselines (
            machine_id, model_name, model_type, model_version,
            training_start_date, training_end_date, training_samples,
            coefficients, intercept, feature_names,
            r_squared, rmse, mae, is_active, trained_by
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15
        )
        RETURNING id
    """
    
    async with db.pool.acquire() as conn:
        model_id = await conn.fetchval(
            query,
            model_data['machine_id'],
            model_data['model_name'],
            model_data.get('model_type', 'linear_regression'),
            model_data['model_version'],
            model_data['training_start_date'],
            model_data['training_end_date'],
            model_data['training_samples'],
            model_data['coefficients'],  # JSONB
            model_data.get('intercept'),
            model_data['feature_names'],  # Array
            model_data.get('r_squared'),
            model_data.get('rmse'),
            model_data.get('mae'),
            model_data.get('is_active', True),
            model_data.get('trained_by', 'analytics-service')
        )
    
    logger.info(f"✓ Baseline model saved: {model_id}")
    return model_id


async def save_anomaly(anomaly_data: Dict[str, Any]) -> UUID:
    """
    Save detected anomaly to database.
    
    Args:
        anomaly_data: Anomaly details
        
    Returns:
        Anomaly ID (UUID)
    """
    query = """
        INSERT INTO anomalies (
            machine_id, detected_at, anomaly_type, severity,
            metric_name, metric_value, expected_value,
            deviation_percent, deviation_std_dev,
            detection_method, confidence_score
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11
        )
        RETURNING id
    """
    
    async with db.pool.acquire() as conn:
        anomaly_id = await conn.fetchval(
            query,
            anomaly_data['machine_id'],
            anomaly_data['detected_at'],
            anomaly_data['anomaly_type'],
            anomaly_data['severity'],
            anomaly_data.get('metric_name'),
            anomaly_data.get('metric_value'),
            anomaly_data.get('expected_value'),
            anomaly_data.get('deviation_percent'),
            anomaly_data.get('deviation_std_dev'),
            anomaly_data.get('detection_method', 'isolation_forest'),
            anomaly_data.get('confidence_score')
        )
    
    logger.info(f"✓ Anomaly saved: {anomaly_id} ({anomaly_data['anomaly_type']})")
    return anomaly_id


async def get_active_baseline_model(machine_id: UUID) -> Optional[Dict[str, Any]]:
    """
    Get active baseline model for a machine.
    
    Args:
        machine_id: Machine UUID
        
    Returns:
        Model record or None
    """
    query = """
        SELECT 
            id, machine_id, model_name, model_type, model_version,
            training_start_date, training_end_date, training_samples,
            coefficients, intercept, feature_names,
            r_squared, rmse, mae, created_at
        FROM energy_baselines
        WHERE machine_id = $1 AND is_active = TRUE
        ORDER BY model_version DESC
        LIMIT 1
    """
    
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(query, machine_id)
        return dict(row) if row else None


async def deactivate_baseline_models(machine_id: UUID):
    """
    Deactivate all baseline models for a machine.
    Used before saving a new model.
    
    Args:
        machine_id: Machine UUID
    """
    query = """
        UPDATE energy_baselines
        SET is_active = FALSE
        WHERE machine_id = $1 AND is_active = TRUE
    """
    
    async with db.pool.acquire() as conn:
        await conn.execute(query, machine_id)
    
    logger.info(f"Deactivated old baseline models for machine: {machine_id}")