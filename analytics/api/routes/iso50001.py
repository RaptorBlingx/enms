"""
ISO 50001 Compliance API

Endpoints for EnPI tracking, baseline management, target monitoring,
and compliance reporting.

Phase 3 Milestone 3.1
"""

import logging
from datetime import date, datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from services.enpi_tracker import EnPITracker

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/iso50001", tags=["ISO 50001 Compliance"])

# Singleton service instance
enpi_tracker = EnPITracker()


# ============================================================================
# Request/Response Models
# ============================================================================

class CreateBaselineRequest(BaseModel):
    """Request to create EnPI baseline"""
    seu_id: str = Field(..., description="SEU UUID")
    baseline_year: int = Field(..., description="Baseline year (e.g., 2024)")
    baseline_start_date: date = Field(..., description="Baseline period start")
    baseline_end_date: date = Field(..., description="Baseline period end")
    created_by: str = Field(default="api_user", description="User creating baseline")


class BaselineResponse(BaseModel):
    """EnPI baseline response"""
    id: str
    seu_id: str
    seu_name: str
    baseline_year: int
    baseline_start_date: date
    baseline_end_date: date
    baseline_energy_kwh: float
    baseline_production_units: int
    baseline_operating_hours: float
    baseline_sec: float
    is_active: bool


class TrackPerformanceRequest(BaseModel):
    """Request to track EnPI performance"""
    seu_id: str = Field(..., description="SEU UUID")
    period_start: date = Field(..., description="Period start date")
    period_end: date = Field(..., description="Period end date")
    period_type: str = Field(default="monthly", description="monthly, quarterly, or annual")


class PerformanceResponse(BaseModel):
    """EnPI performance response"""
    id: str
    seu_id: str
    seu_name: str
    period_start: date
    period_end: date
    period_type: str
    
    actual_energy_kwh: float
    actual_production_units: int
    actual_sec: float
    
    expected_energy_kwh: float
    expected_sec: float
    
    deviation_kwh: float
    deviation_percent: float
    cumulative_savings_kwh: float
    cumulative_savings_usd: float
    
    iso_status: str
    compliance_notes: Optional[str] = None


class CreateTargetRequest(BaseModel):
    """Request to create energy reduction target"""
    target_type: str = Field(..., description="'seu' or 'factory'")
    seu_id: Optional[str] = Field(None, description="SEU UUID (if SEU target)")
    factory_id: Optional[str] = Field(None, description="Factory UUID (if factory target)")
    target_year: int = Field(..., description="Target year")
    target_description: str = Field(..., description="Target description")
    baseline_year: int = Field(..., description="Reference baseline year")
    target_reduction_percent: float = Field(..., description="Target reduction % (e.g., 10)")
    deadline: Optional[date] = Field(None, description="Target deadline")
    created_by: str = Field(default="api_user", description="User creating target")


class TargetResponse(BaseModel):
    """Energy target response"""
    id: str
    target_type: str
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
    status: str
    deadline: Optional[date]


# ============================================================================
# Baseline Management Endpoints
# ============================================================================

@router.post("/baseline", response_model=BaselineResponse)
async def create_baseline(request: CreateBaselineRequest):
    """
    Create EnPI baseline for SEU.
    
    Automatically calculates baseline metrics from historical data:
    - Total energy consumption
    - Total production units
    - Specific Energy Consumption (SEC)
    
    **ISO 50001 Requirement**: Establish baseline for energy performance tracking.
    """
    try:
        baseline = await enpi_tracker.create_baseline(
            seu_id=request.seu_id,
            baseline_year=request.baseline_year,
            baseline_start_date=request.baseline_start_date,
            baseline_end_date=request.baseline_end_date,
            created_by=request.created_by
        )
        
        return {
            "id": baseline.id,
            "seu_id": baseline.seu_id,
            "seu_name": baseline.seu_name,
            "baseline_year": baseline.baseline_year,
            "baseline_start_date": baseline.baseline_start_date,
            "baseline_end_date": baseline.baseline_end_date,
            "baseline_energy_kwh": baseline.baseline_energy_kwh,
            "baseline_production_units": baseline.baseline_production_units,
            "baseline_operating_hours": baseline.baseline_operating_hours,
            "baseline_sec": baseline.baseline_sec,
            "is_active": baseline.is_active
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ISO50001] Error creating baseline: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/baseline/{seu_id}", response_model=BaselineResponse)
async def get_baseline(
    seu_id: str,
    baseline_year: Optional[int] = Query(None, description="Specific baseline year (defaults to most recent)")
):
    """
    Get EnPI baseline for SEU.
    
    Returns the active baseline for the SEU. If baseline_year is not specified,
    returns the most recent active baseline.
    """
    try:
        baseline = await enpi_tracker.get_baseline(seu_id, baseline_year)
        
        if not baseline:
            raise HTTPException(
                status_code=404,
                detail=f"No baseline found for SEU {seu_id}" +
                       (f" year {baseline_year}" if baseline_year else "")
            )
        
        return {
            "id": baseline.id,
            "seu_id": baseline.seu_id,
            "seu_name": baseline.seu_name,
            "baseline_year": baseline.baseline_year,
            "baseline_start_date": baseline.baseline_start_date,
            "baseline_end_date": baseline.baseline_end_date,
            "baseline_energy_kwh": baseline.baseline_energy_kwh,
            "baseline_production_units": baseline.baseline_production_units,
            "baseline_operating_hours": baseline.baseline_operating_hours,
            "baseline_sec": baseline.baseline_sec,
            "is_active": baseline.is_active
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ISO50001] Error getting baseline: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================================
# Performance Tracking Endpoints
# ============================================================================

@router.post("/performance", response_model=PerformanceResponse)
async def track_performance(request: TrackPerformanceRequest):
    """
    Track EnPI performance for period vs baseline.
    
    Calculates:
    - Actual energy consumption and SEC
    - Expected energy consumption (based on baseline SEC × actual production)
    - Deviation from baseline
    - Cumulative savings (year-to-date)
    - ISO 50001 compliance status
    
    **ISO 50001 Requirement**: Monitor energy performance against baseline.
    """
    try:
        performance = await enpi_tracker.track_performance(
            seu_id=request.seu_id,
            period_start=request.period_start,
            period_end=request.period_end,
            period_type=request.period_type
        )
        
        return {
            "id": performance.id,
            "seu_id": performance.seu_id,
            "seu_name": performance.seu_name,
            "period_start": performance.period_start,
            "period_end": performance.period_end,
            "period_type": performance.period_type,
            "actual_energy_kwh": performance.actual_energy_kwh,
            "actual_production_units": performance.actual_production_units,
            "actual_sec": performance.actual_sec,
            "expected_energy_kwh": performance.expected_energy_kwh,
            "expected_sec": performance.expected_sec,
            "deviation_kwh": performance.deviation_kwh,
            "deviation_percent": performance.deviation_percent,
            "cumulative_savings_kwh": performance.cumulative_savings_kwh,
            "cumulative_savings_usd": performance.cumulative_savings_usd,
            "iso_status": performance.iso_status,
            "compliance_notes": performance.compliance_notes
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ISO50001] Error tracking performance: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================================
# Target Management Endpoints
# ============================================================================

@router.post("/target", response_model=TargetResponse)
async def create_target(request: CreateTargetRequest):
    """
    Create energy reduction target.
    
    Targets can be set at:
    - SEU level: Specific to one Significant Energy User
    - Factory level: Aggregated across all SEUs
    
    **ISO 50001 Requirement**: Establish energy reduction objectives and targets.
    """
    try:
        # Validate target type
        if request.target_type not in ["seu", "factory"]:
            raise HTTPException(
                status_code=400,
                detail="target_type must be 'seu' or 'factory'"
            )
        
        if request.target_type == "seu" and not request.seu_id:
            raise HTTPException(
                status_code=400,
                detail="seu_id required for SEU targets"
            )
        
        if request.target_type == "factory" and not request.factory_id:
            raise HTTPException(
                status_code=400,
                detail="factory_id required for factory targets"
            )
        
        target = await enpi_tracker.create_target(
            target_type=request.target_type,
            seu_id=request.seu_id,
            factory_id=request.factory_id,
            target_year=request.target_year,
            target_description=request.target_description,
            baseline_year=request.baseline_year,
            target_reduction_percent=request.target_reduction_percent,
            deadline=request.deadline,
            created_by=request.created_by
        )
        
        return {
            "id": target.id,
            "target_type": target.target_type,
            "target_year": target.target_year,
            "target_description": target.target_description,
            "baseline_year": target.baseline_year,
            "baseline_energy_kwh": target.baseline_energy_kwh,
            "target_reduction_percent": target.target_reduction_percent,
            "target_energy_kwh": target.target_energy_kwh,
            "target_savings_kwh": target.target_savings_kwh,
            "current_energy_kwh": target.current_energy_kwh,
            "current_savings_kwh": target.current_savings_kwh,
            "progress_percent": target.progress_percent,
            "status": target.status,
            "deadline": target.deadline
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ISO50001] Error creating target: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/target/{target_id}/progress", response_model=TargetResponse)
async def update_target_progress(target_id: str):
    """
    Update energy target progress with current year-to-date data.
    
    Calculates:
    - Current YTD energy consumption
    - Current savings vs baseline
    - Progress % towards target
    - Updates status (active, achieved, at_risk)
    
    **Use Case**: Run periodically (weekly/monthly) to track progress towards targets.
    """
    try:
        target = await enpi_tracker.update_target_progress(target_id)
        
        return {
            "id": target.id,
            "target_type": target.target_type,
            "target_year": target.target_year,
            "target_description": target.target_description,
            "baseline_year": target.baseline_year,
            "baseline_energy_kwh": target.baseline_energy_kwh,
            "target_reduction_percent": target.target_reduction_percent,
            "target_energy_kwh": target.target_energy_kwh,
            "target_savings_kwh": target.target_savings_kwh,
            "current_energy_kwh": target.current_energy_kwh,
            "current_savings_kwh": target.current_savings_kwh,
            "progress_percent": target.progress_percent,
            "status": target.status,
            "deadline": target.deadline
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[ISO50001] Error updating target progress: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
