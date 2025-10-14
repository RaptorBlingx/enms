"""
EnMS Analytics Service - Baseline API Routes
=============================================
REST API endpoints for energy baseline models.

Author: EnMS Team
Phase: 3 - Analytics & ML
"""

from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
import logging

from services.baseline_service import baseline_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class TrainBaselineRequest(BaseModel):
    """Request model for training baseline."""
    machine_id: UUID = Field(..., description="Machine UUID")
    start_date: datetime = Field(..., description="Training data start date (ISO 8601)")
    end_date: datetime = Field(..., description="Training data end date (ISO 8601)")
    drivers: Optional[List[str]] = Field(
        None,
        description="List of driver/feature names (if None, auto-select)",
        example=["total_production_count", "avg_outdoor_temp_c", "avg_pressure_bar"]
    )


class PredictEnergyRequest(BaseModel):
    """Request model for energy prediction."""
    machine_id: UUID = Field(..., description="Machine UUID")
    features: Dict[str, float] = Field(
        ...,
        description="Feature values for prediction",
        example={
            "total_production_count": 500,
            "avg_outdoor_temp_c": 25.5,
            "avg_pressure_bar": 7.2
        }
    )


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/baseline/train", tags=["Baseline"])
async def train_baseline(request: TrainBaselineRequest):
    """
    Train a new energy baseline model for a machine.
    
    **Requirements:**
    - Minimum 1000 data points
    - Target R² > 0.80 for quality baseline
    
    **Process:**
    1. Fetch historical data (energy + production + environmental)
    2. Filter by machine status (exclude maintenance/fault periods)
    3. Train Multiple Linear Regression model
    4. Validate model quality (R², RMSE, MAE)
    5. Save model to disk and database
    6. Deactivate previous models
    
    **Returns:**
    - Model ID and version
    - Performance metrics (R², RMSE, MAE)
    - Model coefficients and intercept
    - Feature names used
    """
    try:
        logger.info(f"[TRAIN-API] Received training request: machine_id={request.machine_id}, start={request.start_date}, end={request.end_date}, drivers={request.drivers}")
        
        result = await baseline_service.train_baseline(
            machine_id=request.machine_id,
            start_date=request.start_date,
            end_date=request.end_date,
            drivers=request.drivers
        )
        
        logger.info(f"[TRAIN-API] Training completed successfully")
        return result
    
    except ValueError as e:
        logger.error(f"[TRAIN-API] ValueError occurred: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[TRAIN-API] Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/baseline/deviation", tags=["Baseline"])
async def get_baseline_deviation(
    machine_id: UUID = Query(..., description="Machine UUID"),
    start: datetime = Query(..., description="Start of analysis period (ISO 8601)"),
    end: datetime = Query(..., description="End of analysis period (ISO 8601)")
):
    """
    Calculate baseline performance deviation for a machine.
    
    **Deviation Calculation:**
    ```
    Deviation (kWh) = Actual Energy - Predicted Energy
    Deviation (%) = (Deviation / Predicted) × 100
    ```
    
    **Severity Levels:**
    - **Normal**: |Deviation| < 5%
    - **Warning**: 5% ≤ |Deviation| < 15%
    - **Critical**: |Deviation| ≥ 15%
    
    **Use Cases:**
    - Detect equipment degradation
    - Identify operational inefficiencies
    - Validate energy optimization measures
    - ISO 50001 compliance reporting
    
    **Returns:**
    - Total actual vs. predicted energy
    - Overall deviation (kWh and %)
    - Severity classification
    - Hourly breakdown of deviations
    """
    try:
        result = await baseline_service.get_baseline_deviation(
            machine_id=machine_id,
            start_time=start,
            end_time=end
        )
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating deviation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/baseline/predict", tags=["Baseline"])
async def predict_energy(request: PredictEnergyRequest):
    """
    Predict energy consumption for given operating conditions.
    
    **Use Cases:**
    - What-if analysis for production planning
    - Energy forecasting for load scheduling
    - Capacity planning
    - Cost estimation
    
    **Example Request:**
    ```json
    {
      "machine_id": "550e8400-e29b-41d4-a716-446655440000",
      "features": {
        "total_production_count": 1000,
        "avg_outdoor_temp_c": 22.0,
        "avg_pressure_bar": 7.5,
        "avg_throughput_units_per_hour": 250
      }
    }
    ```
    
    **Returns:**
    - Predicted energy consumption (kWh)
    - Model version used
    - Input features
    """
    try:
        result = await baseline_service.predict_energy(
            machine_id=request.machine_id,
            features=request.features
        )
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error predicting energy: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/baseline/models", tags=["Baseline"])
async def list_baseline_models(
    machine_id: UUID = Query(..., description="Machine UUID")
):
    """
    List all baseline models for a machine.
    
    **Returns:**
    - List of all models (active and inactive)
    - Model versions, performance metrics
    - Training dates and sample counts
    - Ordered by version (newest first)
    """
    try:
        models = await baseline_service.list_baseline_models(machine_id)
        return {
            'machine_id': str(machine_id),
            'total_models': len(models),
            'models': models
        }
    
    except Exception as e:
        logger.error(f"Error listing models: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/baseline/model/{model_id}", tags=["Baseline"])
async def get_model_details(
    model_id: UUID = Path(..., description="Model UUID")
):
    """
    Get detailed information about a specific baseline model.
    
    **Returns:**
    - Complete model metadata
    - Coefficients for each driver
    - Performance metrics
    - Training information
    """
    try:
        model = await baseline_service.get_model_details(model_id)
        
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        return model
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")