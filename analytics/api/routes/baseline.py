"""
EnMS Analytics Service - Baseline API Routes
=============================================
REST API endpoints for energy baseline models.

Author: EnMS Team
Phase: 3 - Analytics & ML
"""

from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
import logging

from services.baseline_service import baseline_service
from services.model_explainer import model_explainer
from database import db

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Helper Functions
# ============================================================================

async def get_seu_by_name_and_energy_source(
    seu_name: str, 
    energy_source: str
) -> Optional[Dict[str, Any]]:
    """
    Lookup SEU by name and energy source.
    Reused from ovos_training.py for consistency.
    """
    query = """
        SELECT 
            s.id, s.name, s.description, s.energy_source_id, s.machine_ids,
            es.name as energy_source_name, es.unit as energy_unit
        FROM seus s
        JOIN energy_sources es ON s.energy_source_id = es.id
        WHERE LOWER(s.name) = LOWER($1)
          AND LOWER(es.name) = LOWER($2)
          AND s.is_active = true
        LIMIT 1
    """
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(query, seu_name, energy_source)
        return dict(row) if row else None


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
    """
    Request model for energy prediction.
    
    ENHANCEMENT (Nov 4, 2025): Supports BOTH UUID and SEU name inputs
    - Dashboard usage: Provide machine_id (UUID)
    - OVOS/Voice usage: Provide seu_name + energy_source
    """
    # Option 1: UUID-based (existing dashboard usage)
    machine_id: Optional[UUID] = Field(
        default=None, 
        description="Machine UUID (for dashboard/programmatic access)"
    )
    
    # Option 2: SEU name-based (NEW - OVOS/voice usage)
    seu_name: Optional[str] = Field(
        default=None,
        description="SEU name for voice-friendly access (e.g., 'Compressor-1')"
    )
    energy_source: Optional[str] = Field(
        default=None,
        description="Energy source name (e.g., 'electricity', 'natural_gas', 'steam', 'compressed_air')"
    )
    
    # Common parameters
    features: Dict[str, float] = Field(
        ...,
        description="Feature values for prediction",
        example={
            "total_production_count": 500,
            "avg_outdoor_temp_c": 25.5,
            "avg_pressure_bar": 7.2
        }
    )
    
    # NEW: Voice-friendly response flag
    include_message: bool = Field(
        False,
        description="Include voice-friendly message in response (for OVOS/TTS)"
    )
    
    @model_validator(mode='after')
    def check_identifier(self):
        """Ensure either machine_id OR (seu_name + energy_source) is provided."""
        machine_id = self.machine_id
        seu_name = self.seu_name
        energy_source = self.energy_source
        
        # Check if we have either UUID or SEU name combo
        has_uuid = machine_id is not None
        has_seu = seu_name is not None and energy_source is not None
        
        if not has_uuid and not has_seu:
            raise ValueError(
                "Must provide either 'machine_id' OR both 'seu_name' and 'energy_source'"
            )
        
        if seu_name is not None and energy_source is None:
            raise ValueError(
                "When using 'seu_name', 'energy_source' is also required"
            )
        
        if energy_source is not None and seu_name is None:
            raise ValueError(
                "When using 'energy_source', 'seu_name' is also required"
            )
        
        return self
    
    class Config:
        schema_extra = {
            "examples": [
                {
                    "name": "UUID-based (Dashboard)",
                    "value": {
                        "machine_id": "c0000000-0000-0000-0000-000000000001",
                        "features": {
                            "total_production_count": 500,
                            "avg_outdoor_temp_c": 22.5,
                            "avg_pressure_bar": 7.0
                        }
                    }
                },
                {
                    "name": "SEU name-based (OVOS/Voice)",
                    "value": {
                        "seu_name": "Compressor-1",
                        "energy_source": "electricity",
                        "features": {
                            "total_production_count": 500,
                            "avg_outdoor_temp_c": 22.5,
                            "avg_pressure_bar": 7.0
                        },
                        "include_message": True
                    }
                }
            ]
        }


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
    
    **ENHANCED (Nov 4, 2025):** Now supports BOTH UUID and SEU name inputs!
    
    **Input Methods:**
    
    **Method 1: UUID-based (Dashboard/Programmatic)**
    ```json
    {
      "machine_id": "c0000000-0000-0000-0000-000000000001",
      "features": {
        "total_production_count": 1000,
        "avg_outdoor_temp_c": 22.0,
        "avg_pressure_bar": 7.5
      }
    }
    ```
    
    **Method 2: SEU name-based (OVOS/Voice Assistant)** ⭐ NEW
    ```json
    {
      "seu_name": "Compressor-1",
      "energy_source": "electricity",
      "features": {
        "total_production_count": 1000,
        "avg_outdoor_temp_c": 22.0,
        "avg_pressure_bar": 7.5
      },
      "include_message": true
    }
    ```
    
    **Use Cases:**
    - What-if analysis for production planning
    - Energy forecasting for load scheduling
    - Voice queries: "What's the expected energy for Compressor-1 at 500 units?"
    - Capacity planning and cost estimation
    
    **Returns:**
    - Predicted energy consumption (kWh or other unit)
    - Model version used
    - Input features
    - Optional: Voice-friendly message (when include_message=true)
    """
    try:
        # Step 1: Resolve machine_id (from UUID or SEU name)
        machine_id = request.machine_id
        seu_name_for_message = None
        energy_unit = "kWh"  # default
        seu = None  # Initialize to None (used later for energy_source_id)
        
        if machine_id is None:
            # SEU name-based lookup
            logger.info(f"[PREDICT] SEU name-based lookup: {request.seu_name} ({request.energy_source})")
            
            seu = await get_seu_by_name_and_energy_source(
                request.seu_name,
                request.energy_source
            )
            
            if not seu:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "SEU_NOT_FOUND",
                        "message": f"Could not find SEU '{request.seu_name}' with energy source '{request.energy_source}'",
                        "suggestion": "Check SEU name spelling or use GET /api/v1/ovos/seus to list available SEUs"
                    }
                )
            
            # Get first machine ID from SEU
            if not seu['machine_ids'] or len(seu['machine_ids']) == 0:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "NO_MACHINES",
                        "message": f"SEU '{request.seu_name}' has no associated machines"
                    }
                )
            
            machine_id = seu['machine_ids'][0]
            seu_name_for_message = seu['name']
            energy_unit = seu.get('energy_unit', 'kWh')
            
            logger.info(f"[PREDICT] Resolved SEU '{request.seu_name}' to machine_id: {machine_id}")
        else:
            logger.info(f"[PREDICT] UUID-based lookup: {machine_id}")
        
        # Step 2: Make prediction using baseline service
        # Pass energy_source_id if SEU-based lookup was used
        energy_source_id_for_predict = seu.get('energy_source_id') if seu else None
        
        result = await baseline_service.predict_energy(
            machine_id=machine_id,
            features=request.features,
            energy_source_id=energy_source_id_for_predict  # NEW: Support multi-energy
        )
        
        # Step 3: Add voice-friendly message if requested
        if request.include_message:
            predicted_value = result.get('predicted_energy_kwh', 0)
            
            # Build natural language message
            if seu_name_for_message:
                message = (
                    f"{seu_name_for_message} is predicted to consume "
                    f"{predicted_value:.1f} {energy_unit} under these conditions"
                )
            else:
                message = f"Predicted energy consumption: {predicted_value:.1f} {energy_unit}"
            
            result['message'] = message
            result['energy_unit'] = energy_unit
        
        logger.info(f"[PREDICT] Prediction successful: {result.get('predicted_energy_kwh', 0):.2f} {energy_unit}")
        return result
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"[PREDICT] ValueError: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[PREDICT] Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/baseline/models", tags=["Baseline"])
async def list_baseline_models(
    machine_id: Optional[UUID] = Query(None, description="Machine UUID (Option 1)"),
    seu_name: Optional[str] = Query(None, description="SEU name (Option 2 - for OVOS)"),
    energy_source: Optional[str] = Query(None, description="Energy source (required with seu_name)"),
    include_explanation: bool = Query(False, description="Include natural language explanations")
):
    """
    List all baseline models for a machine.
    
    **ENHANCED (November 2025):** Now accepts BOTH UUID and SEU name!
    
    **Parameters:**
    - **Option 1 - Dashboard usage (UUID):**
      - `machine_id`: Machine UUID
    - **Option 2 - Voice usage (SEU name) - NEW:**
      - `seu_name`: SEU name (e.g., "Compressor-1")
      - `energy_source`: "electricity", "natural_gas", "steam", "compressed_air"
    - `include_explanation`: Add natural language explanations to each model (default: false)
    
    **Returns:**
    - List of all models (active and inactive)
    - Model versions, performance metrics
    - Training dates and sample counts
    - Optional: Natural language explanations
    - Ordered by version (newest first)
    
    **OVOS Use Cases:**
    - "List baseline models for Compressor-1"
    - "Show me all models with explanations"
    - "What models exist for electricity?"
    """
    try:
        # Validation: Must provide exactly one input method
        if machine_id is None and (seu_name is None or energy_source is None):
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "MISSING_IDENTIFIER",
                    "message": "Must provide either 'machine_id' OR ('seu_name' + 'energy_source')",
                    "examples": {
                        "option_1": "?machine_id=c0000000-0000-0000-0000-000000000001",
                        "option_2": "?seu_name=Compressor-1&energy_source=electricity"
                    }
                }
            )
        
        if machine_id is not None and seu_name is not None:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "CONFLICTING_IDENTIFIERS",
                    "message": "Cannot provide both 'machine_id' and 'seu_name'. Choose one method.",
                }
            )
        
        # Resolve machine_id from SEU name if needed
        resolved_machine_id = machine_id
        seu_display_name = None
        
        if machine_id is None:
            # Look up SEU
            seu = await get_seu_by_name_and_energy_source(seu_name, energy_source)
            if not seu:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "SEU_NOT_FOUND",
                        "message": f"Could not find SEU '{seu_name}' with energy source '{energy_source}'.",
                        "suggestion": "Use GET /api/v1/ovos/seus to list all available SEUs."
                    }
                )
            
            # Get first machine ID from the SEU
            machine_ids = seu.get('machine_ids', [])
            if not machine_ids:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "NO_MACHINE_FOR_SEU",
                        "message": f"SEU '{seu_name}' has no associated machines.",
                    }
                )
            
            resolved_machine_id = machine_ids[0]
            seu_display_name = seu.get('seu_name') or seu_name
            energy_source_id_for_list = seu.get('energy_source_id')  # Get energy_source_id
        
        # Get models (filtered by energy source if SEU-based)
        models = await baseline_service.list_baseline_models(
            resolved_machine_id,
            energy_source_id=energy_source_id_for_list if seu_display_name else None
        )
        
        # Add explanations if requested
        if include_explanation:
            for model in models:
                # Get full model details (includes coefficients)
                full_model = await baseline_service.get_model_details(model['id'])
                if full_model:
                    explanation = model_explainer.explain_model(full_model)
                    model['explanation'] = explanation
        
        response = {
            'machine_id': str(resolved_machine_id),
            'total_models': len(models),
            'models': models
        }
        
        # Add SEU info if accessed via SEU name
        if seu_display_name:
            response['seu_name'] = seu_display_name
            response['energy_source'] = energy_source
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing models: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/baseline/model/{model_id}", tags=["Baseline"])
async def get_model_details(
    model_id: UUID = Path(..., description="Model UUID"),
    include_explanation: bool = Query(
        False, 
        description="Include natural language explanation of model (for OVOS/voice)"
    )
):
    """
    Get detailed information about a specific baseline model.
    
    **ENHANCED (November 2025):** Adds optional natural language explanations for voice interfaces.
    
    **Parameters:**
    - `model_id`: Model UUID (required, in path)
    - `include_explanation`: Add voice-friendly explanations (optional, default: false)
    
    **Returns:**
    - Complete model metadata
    - Coefficients for each driver
    - Performance metrics
    - Training information
    - Natural language explanations (if requested)
    
    **OVOS Use Cases:**
    - "Explain the Compressor-1 baseline model"
    - "What are the key energy drivers?"
    - "How accurate is the model?"
    """
    try:
        model = await baseline_service.get_model_details(model_id)
        
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Add natural language explanation if requested
        if include_explanation:
            explanation = model_explainer.explain_model(model)
            model['explanation'] = explanation
        
        return model
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")