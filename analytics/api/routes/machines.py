"""
EnMS Analytics - Machines API Routes
=====================================
API endpoints for machine information.
"""

from fastapi import APIRouter, Query
from typing import List, Dict, Any, Optional
from uuid import UUID

from database import get_machines, get_machine_by_id

router = APIRouter()


@router.get("/machines", tags=["Machines"])
async def list_machines(
    is_active: Optional[bool] = Query(None, description="Filter by active status")
) -> List[Dict[str, Any]]:
    """
    Get list of all machines.
    
    **Parameters:**
    - `is_active`: Filter by active status (optional)
    
    **Returns:**
    - List of machine objects with basic information
    
    **Example:**
    ```
    GET /api/v1/machines
    GET /api/v1/machines?is_active=true
    ```
    """
    machines = await get_machines(is_active=is_active)
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
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine
