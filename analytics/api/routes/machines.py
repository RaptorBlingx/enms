"""
EnMS Analytics - Machines API Routes
=====================================
API endpoints for machine information.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime

from database import get_machines, get_machine_by_id, db

router = APIRouter()


@router.get("/machines", tags=["Machines"])
async def list_machines(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by machine name (case-insensitive partial match)")
) -> List[Dict[str, Any]]:
    """
    Get list of all machines with optional search.
    
    **Parameters:**
    - `is_active`: Filter by active status (optional)
    - `search`: Search by machine name - case-insensitive partial match (optional)
    
    **Returns:**
    - List of machine objects with basic information
    
    **OVOS Integration:**
    - Use `search` parameter to resolve machine names to UUIDs
    - Enables voice queries like "Tell me about Compressor-1"
    
    **Example:**
    ```
    GET /api/v1/machines
    GET /api/v1/machines?is_active=true
    GET /api/v1/machines?search=compressor
    GET /api/v1/machines?search=Compressor-1
    GET /api/v1/machines?search=hvac&is_active=true
    ```
    """
    machines = await get_machines(is_active=is_active)
    
    # Apply search filter if provided
    if search:
        search_lower = search.lower()
        machines = [
            machine for machine in machines
            if search_lower in machine.get("name", "").lower()
        ]
    
    return machines


@router.get("/machines/{machine_id}", tags=["Machines"])
async def get_machine(
    machine_id: UUID
) -> Dict[str, Any]:
    """
    Get detailed information about a specific machine.
    
    **Parameters:**
    - `machine_id`: Machine UUID
    
    **Returns:**
    - Machine object with full details
    
    **Example:**
    ```
    GET /api/v1/machines/c0000000-0000-0000-0000-000000000001
    ```
    """
    machine = await get_machine_by_id(machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine


@router.get("/machines/{machine_id}/status-history", tags=["Machines"])
async def get_machine_status_history(
    machine_id: UUID,
    start_time: datetime = Query(..., description="Start time (ISO 8601)"),
    end_time: datetime = Query(..., description="End time (ISO 8601)"),
    interval: str = Query("1hour", description="Aggregation interval (5min, 15min, 1hour)")
) -> Dict[str, Any]:
    """
    Get machine status history with running/stopped timeline.
    
    **NEW FEATURE** - Track when machines were online/offline.
    
    **Status Classification:**
    - `running`: power_kw > 5 kW
    - `idle`: 0.5 kW < power_kw ≤ 5 kW  
    - `stopped`: power_kw ≤ 0.5 kW
    
    **Parameters:**
    - `machine_id`: Machine UUID
    - `start_time`: Start of history period (ISO 8601)
    - `end_time`: End of history period (ISO 8601)
    - `interval`: Time bucket size (5min, 15min, 1hour, default: 1hour)
    
    **Returns:**
    - Timeline of machine status with duration percentages
    - Total running/idle/stopped times
    - Status transitions count
    
    **Use Cases:**
    - "When was Compressor-1 offline yesterday?"
    - "Show me machine uptime for last week"
    - "What's the operating pattern for HVAC-Main?"
    
    **Example:**
    ```
    GET /api/v1/machines/{id}/status-history?start_time=2025-10-19T00:00:00Z&end_time=2025-10-20T00:00:00Z&interval=1hour
    ```
    """
    # Verify machine exists
    machine = await get_machine_by_id(machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Map interval names to PostgreSQL interval syntax
    interval_map = {
        "5min": "5 minutes",
        "15min": "15 minutes",
        "1hour": "1 hour",
        "1day": "1 day"
    }
    
    if interval not in interval_map:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid interval. Must be one of: {', '.join(interval_map.keys())}"
        )
    
    pg_interval = interval_map[interval]
    
    # Query to calculate status history with time buckets
    # Note: interval must be hardcoded for time_bucket function
    query = f"""
        WITH time_buckets AS (
            SELECT
                time_bucket('{pg_interval}'::interval, time) as bucket,
                AVG(power_kw) as avg_power_kw,
                MAX(power_kw) as max_power_kw,
                MIN(power_kw) as min_power_kw,
                COUNT(*) as reading_count
            FROM energy_readings
            WHERE machine_id = $1
                AND time >= $2
                AND time < $3
            GROUP BY bucket
            ORDER BY bucket
        ),
        status_classified AS (
            SELECT
                bucket,
                avg_power_kw,
                max_power_kw,
                min_power_kw,
                reading_count,
                CASE
                    WHEN avg_power_kw > 5 THEN 'running'
                    WHEN avg_power_kw > 0.5 THEN 'idle'
                    ELSE 'stopped'
                END as status
            FROM time_buckets
        )
        SELECT
            bucket,
            avg_power_kw,
            max_power_kw,
            min_power_kw,
            status,
            reading_count
        FROM status_classified
        ORDER BY bucket;
    """
    
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(query, machine_id, start_time, end_time)
    
    if not rows:
        return {
            "machine_id": str(machine_id),
            "machine_name": machine["name"],
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "interval": interval,
            "message": "No data available for this time period",
            "timeline": [],
            "summary": {
                "total_periods": 0,
                "running_periods": 0,
                "idle_periods": 0,
                "stopped_periods": 0,
                "running_percent": 0.0,
                "idle_percent": 0.0,
                "stopped_percent": 0.0,
                "transitions": 0
            }
        }
    
    # Build timeline
    timeline = []
    prev_status = None
    transitions = 0
    status_counts = {"running": 0, "idle": 0, "stopped": 0}
    
    for row in rows:
        status = row["status"]
        status_counts[status] += 1
        
        if prev_status and prev_status != status:
            transitions += 1
        
        timeline.append({
            "timestamp": row["bucket"].isoformat(),
            "status": status,
            "avg_power_kw": float(row["avg_power_kw"]),
            "max_power_kw": float(row["max_power_kw"]),
            "min_power_kw": float(row["min_power_kw"]),
            "reading_count": row["reading_count"]
        })
        
        prev_status = status
    
    total_periods = len(rows)
    
    return {
        "machine_id": str(machine_id),
        "machine_name": machine["name"],
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "interval": interval,
        "timeline": timeline,
        "summary": {
            "total_periods": total_periods,
            "running_periods": status_counts["running"],
            "idle_periods": status_counts["idle"],
            "stopped_periods": status_counts["stopped"],
            "running_percent": round((status_counts["running"] / total_periods) * 100, 2) if total_periods > 0 else 0.0,
            "idle_percent": round((status_counts["idle"] / total_periods) * 100, 2) if total_periods > 0 else 0.0,
            "stopped_percent": round((status_counts["stopped"] / total_periods) * 100, 2) if total_periods > 0 else 0.0,
            "transitions": transitions,
            "uptime_percent": round(((status_counts["running"] + status_counts["idle"]) / total_periods) * 100, 2) if total_periods > 0 else 0.0
        }
    }
