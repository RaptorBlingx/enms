"""
EnMS Analytics Service - KPI API Routes
========================================
REST API endpoints for Key Performance Indicator calculations.

Author: EnMS Team
Phase: 3 - Analytics & ML
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from uuid import UUID
import logging

from services.kpi_service import kpi_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/kpi/sec", tags=["KPI"])
async def get_sec(
    machine_id: UUID = Query(..., description="Machine UUID"),
    start: datetime = Query(..., description="Start of calculation period (ISO 8601)"),
    end: datetime = Query(..., description="End of calculation period (ISO 8601)")
):
    """
    Calculate Specific Energy Consumption (SEC).
    
    **Formula:**
    ```
    SEC = Total Energy (kWh) / Total Production (units)
    ```
    
    **Unit:** kWh/unit
    
    **Use Cases:**
    - ISO 50001 compliance reporting
    - Energy efficiency benchmarking
    - Production cost analysis
    - Process optimization tracking
    
    **Returns:**
    - SEC value (kWh/unit)
    - Total energy consumed (kWh)
    - Total production (units)
    - Time period (hours)
    """
    try:
        result = await kpi_service.calculate_sec(
            machine_id=machine_id,
            start_time=start,
            end_time=end
        )
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating SEC: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/kpi/peak-demand", tags=["KPI"])
async def get_peak_demand(
    machine_id: UUID = Query(..., description="Machine UUID"),
    start: datetime = Query(..., description="Start of calculation period (ISO 8601)"),
    end: datetime = Query(..., description="End of calculation period (ISO 8601)")
):
    """
    Calculate Peak Demand.
    
    **Formula:**
    ```
    Peak Demand = MAX(power_kw) over 15-minute rolling window
    ```
    
    **Unit:** kW
    
    **Use Cases:**
    - Demand charge optimization
    - Capacity planning
    - Load shedding strategies
    - Utility billing verification
    
    **Returns:**
    - Peak demand value (kW)
    - Timestamp of peak occurrence
    - Average power (kW)
    """
    try:
        result = await kpi_service.calculate_peak_demand(
            machine_id=machine_id,
            start_time=start,
            end_time=end
        )
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating peak demand: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/kpi/load-factor", tags=["KPI"])
async def get_load_factor(
    machine_id: UUID = Query(..., description="Machine UUID"),
    start: datetime = Query(..., description="Start of calculation period (ISO 8601)"),
    end: datetime = Query(..., description="End of calculation period (ISO 8601)")
):
    """
    Calculate Load Factor.
    
    **Formula:**
    ```
    Load Factor = AVG(power_kw) / MAX(power_kw)
    ```
    
    **Unit:** Ratio (0-1) or Percentage (0-100%)
    
    **Interpretation:**
    - **High (>0.7)**: Efficient, consistent operation
    - **Medium (0.4-0.7)**: Typical intermittent operation
    - **Low (<0.4)**: Inefficient, frequent cycling
    
    **Use Cases:**
    - Equipment utilization analysis
    - Operational efficiency assessment
    - Maintenance planning
    - Right-sizing equipment
    
    **Returns:**
    - Load factor (ratio)
    - Load factor (percentage)
    - Average power (kW)
    - Peak power (kW)
    """
    try:
        result = await kpi_service.calculate_load_factor(
            machine_id=machine_id,
            start_time=start,
            end_time=end
        )
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating load factor: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/kpi/energy-cost", tags=["KPI"])
async def get_energy_cost(
    machine_id: UUID = Query(..., description="Machine UUID"),
    start: datetime = Query(..., description="Start of calculation period (ISO 8601)"),
    end: datetime = Query(..., description="End of calculation period (ISO 8601)")
):
    """
    Calculate Energy Cost with Time-of-Use (TOU) tariff.
    
    **Formula:**
    ```
    Cost = SUM(energy_kwh × tariff_rate)
    ```
    
    **Tariff Structure:**
    - **Peak hours** (08:00-20:00): $0.20/kWh
    - **Off-peak hours** (20:00-08:00): $0.10/kWh
    
    **Unit:** USD (or local currency)
    
    **Use Cases:**
    - Cost allocation by machine
    - Load shifting opportunity analysis
    - Budget forecasting
    - Energy procurement decisions
    
    **Returns:**
    - Total energy cost (USD)
    - Cost per production unit (USD/unit)
    - Peak hour cost breakdown
    - Off-peak hour cost breakdown
    """
    try:
        result = await kpi_service.calculate_energy_cost(
            machine_id=machine_id,
            start_time=start,
            end_time=end
        )
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating energy cost: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/kpi/carbon", tags=["KPI"])
async def get_carbon_intensity(
    machine_id: UUID = Query(..., description="Machine UUID"),
    start: datetime = Query(..., description="Start of calculation period (ISO 8601)"),
    end: datetime = Query(..., description="End of calculation period (ISO 8601)")
):
    """
    Calculate Carbon Intensity (CO₂ emissions).
    
    **Formula:**
    ```
    CO₂ = SUM(energy_kwh) × emission_factor
    ```
    
    **Emission Factor:** 0.45 kg CO₂/kWh (grid average)
    
    **Unit:** kg CO₂
    
    **Use Cases:**
    - Carbon footprint reporting
    - Sustainability metrics
    - Scope 2 emissions (GHG Protocol)
    - ESG reporting
    - Carbon credit calculations
    
    **Returns:**
    - Total CO₂ emissions (kg)
    - CO₂ per production unit (kg/unit)
    - Total energy consumed (kWh)
    """
    try:
        result = await kpi_service.calculate_carbon_intensity(
            machine_id=machine_id,
            start_time=start,
            end_time=end
        )
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating carbon intensity: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/kpi/all", tags=["KPI"])
async def get_all_kpis(
    machine_id: UUID = Query(..., description="Machine UUID"),
    start: datetime = Query(..., description="Start of calculation period (ISO 8601)"),
    end: datetime = Query(..., description="End of calculation period (ISO 8601)")
):
    """
    Calculate all KPIs in a single optimized query.
    
    **Includes:**
    1. **SEC** - Specific Energy Consumption (kWh/unit)
    2. **Peak Demand** - Maximum power draw (kW)
    3. **Load Factor** - Utilization ratio (0-1)
    4. **Energy Cost** - Total cost with TOU tariff (USD)
    5. **Carbon Intensity** - CO₂ emissions (kg)
    
    **Performance:**
    - Single database call for efficiency
    - Optimized for dashboard displays
    - Includes summary totals
    
    **Use Cases:**
    - Executive dashboards
    - Comprehensive reports
    - ISO 50001 compliance packages
    - Multi-KPI analysis
    
    **Returns:**
    - All 5 KPIs with values and units
    - Time period summary
    - Production totals
    - Energy totals
    """
    try:
        result = await kpi_service.calculate_all_kpis(
            machine_id=machine_id,
            start_time=start,
            end_time=end
        )
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating KPIs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")