"""
EnMS Analytics API - OVOS Training Routes
==========================================
Voice-controlled baseline training for OVOS (Open Voice OS) integration.

Mr. Umut's Requirement:
"I'll be asking to implement regression analysis by just saying the energy source, 
SEU and possible relevant drivers name, and I'll be expecting to see the results (talking about OVOS)"

Example Voice Command:
"Train baseline for Compressor-1 electricity using production count and outdoor temperature for 2024"

Expected System Response:
"Compressor-1 electricity baseline trained. R-squared 0.99. 
Formula: Energy equals 0.061 plus 0.000043 times production count minus 0.000004 times outdoor temperature."

Author: EnMS Team
Phase: 3 - OVOS Integration
Date: October 23, 2025
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
from uuid import UUID
import logging

from services.seu_baseline_service import SEUBaselineService
from services.feature_discovery import feature_discovery
from database import db
from models.seu import TrainBaselineRequest
from typing import Dict, Any

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_seu_by_name_and_energy_source(
    seu_name: str, 
    energy_source: str
) -> Optional[Dict[str, Any]]:
    """Lookup SEU by name and energy source."""
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


class OVOSTrainingRequest(BaseModel):
    """
    OVOS-friendly baseline training request.
    
    Designed for natural language input from voice assistant.
    """
    seu_name: str = Field(..., description="SEU name (e.g., 'Compressor-1', 'HVAC-Main')")
    energy_source: str = Field(..., description="Energy source name (e.g., 'electricity', 'natural_gas', 'steam')")
    features: List[str] = Field(..., description="List of feature names to use in baseline (e.g., ['production_count', 'outdoor_temp_c'])")
    year: int = Field(..., description="Baseline year (e.g., 2024)", ge=2000, le=2100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "seu_name": "Compressor-1",
                "energy_source": "electricity",
                "features": ["production_count", "outdoor_temp_c"],
                "year": 2024
            }
        }


class OVOSTrainingResponse(BaseModel):
    """
    OVOS-friendly baseline training response.
    
    Formatted for voice output and human readability.
    """
    success: bool
    message: str = Field(..., description="Voice-friendly message summarizing results")
    seu_name: str
    energy_source: str
    r_squared: Optional[float] = Field(None, description="R-squared value (0-1, higher is better)")
    rmse: Optional[float] = Field(None, description="Root mean squared error")
    formula_readable: Optional[str] = Field(None, description="Human-readable formula for voice output")
    formula_technical: Optional[str] = Field(None, description="Mathematical formula notation")
    samples_count: Optional[int] = Field(None, description="Number of days used for training")
    trained_at: Optional[datetime] = None
    error_details: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Compressor-1 electricity baseline trained successfully with R-squared 0.99",
                "seu_name": "Compressor-1",
                "energy_source": "electricity",
                "r_squared": 0.99,
                "rmse": 0.05,
                "formula_readable": "Energy equals 0.061 plus 0.000043 times production count minus 0.000004 times outdoor temperature",
                "formula_technical": "E = 0.061 + 0.000043×P - 0.000004×T",
                "samples_count": 365,
                "trained_at": "2025-10-23T15:30:00Z"
            }
        }


@router.post("/train-baseline", response_model=OVOSTrainingResponse)
async def train_baseline_via_ovos(request: OVOSTrainingRequest):
    """
    Train baseline for SEU via OVOS voice command.
    
    This endpoint is designed for natural language input from voice assistants.
    It accepts SEU name + energy source + features, looks up the SEU dynamically,
    validates features exist, trains the baseline, and returns a voice-friendly response.
    
    **ZERO HARDCODING:** Works for ANY energy source (electricity, natural gas, steam, etc.)
    as long as the energy source and features are defined in the database.
    
    Args:
        request: OVOS training request with SEU name, energy source, features, year
    
    Returns:
        Voice-friendly response with training results
        
    Raises:
        HTTPException 404: SEU not found
        HTTPException 400: Invalid features or insufficient data
        HTTPException 500: Training failed
    """
    try:
        logger.info(
            f"[OVOS-TRAIN] Voice request: SEU='{request.seu_name}', "
            f"Energy='{request.energy_source}', Features={request.features}, Year={request.year}"
        )
        
                # Step 1: Lookup SEU by name and energy source
        seu = await get_seu_by_name_and_energy_source(
            request.seu_name, 
            request.energy_source
        )
        
        if not seu:
            return OVOSTrainingResponse(
                success=False,
                message=f"SEU '{request.seu_name}' with energy source '{request.energy_source}' not found",
                seu_name=request.seu_name,
                energy_source=request.energy_source
            )
        
        # Convert UUID to proper type
        seu_id = UUID(str(seu['id']))
        
        logger.info(f"[OVOS-TRAIN] Found SEU: {seu['id']} - {seu['name']}")
        
        # Convert energy_source_id to UUID
        energy_source_id = UUID(str(seu['energy_source_id']))
        
        # Step 2: Validate features exist for this energy source
        is_valid, valid_features, invalid_features = await feature_discovery.validate_features(
            energy_source_id=energy_source_id,
            requested_features=request.features
        )
        
        if not is_valid:
            # Get available features to help user
            available = await feature_discovery.get_available_features(
                energy_source_id=energy_source_id,
                regression_only=True
            )
            available_names = [f.feature_name for f in available]
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid features: {invalid_features}. "
                       f"Available features for {request.energy_source}: {available_names}"
            )
        
        logger.info(f"[OVOS-TRAIN] Features validated: {valid_features}")
        
        # Step 3: Build training request
        training_request = TrainBaselineRequest(
            seu_id=seu_id,
            baseline_year=request.year,
            start_date=date(request.year, 1, 1),
            end_date=date(request.year, 12, 31),
            features=request.features
        )
        
        # Step 4: Train baseline using dynamic service
        baseline_service = SEUBaselineService()
        training_response = await baseline_service.train_baseline(training_request)
        
        logger.info(
            f"[OVOS-TRAIN] Training complete: R²={training_response.r_squared}, "
            f"Samples={training_response.samples_count}"
        )
        
        # Step 5: Format response for voice output
        formula_readable = _build_voice_formula(
            intercept=training_response.intercept,
            coefficients=training_response.coefficients
        )
        
        formula_technical = _build_technical_formula(
            intercept=training_response.intercept,
            coefficients=training_response.coefficients
        )
        
        # Build voice-friendly message
        r2_percent = round(training_response.r_squared * 100)
        message = (
            f"{request.seu_name} {request.energy_source} baseline trained successfully. "
            f"R-squared {training_response.r_squared:.2f} ({r2_percent}% accuracy). "
            f"{formula_readable}"
        )
        
        return OVOSTrainingResponse(
            success=True,
            message=message,
            seu_name=request.seu_name,
            energy_source=request.energy_source,
            r_squared=training_response.r_squared,
            rmse=training_response.rmse,
            formula_readable=formula_readable,
            formula_technical=formula_technical,
            samples_count=training_response.samples_count,
            trained_at=training_response.trained_at
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except Exception as e:
        logger.error(f"[OVOS-TRAIN] Training failed: {e}", exc_info=True)
        
        return OVOSTrainingResponse(
            success=False,
            message=f"Training failed for {request.seu_name} {request.energy_source}: {str(e)}",
            seu_name=request.seu_name,
            energy_source=request.energy_source,
            error_details=str(e)
        )


@router.get("/energy-sources")
async def get_energy_sources_summary():
    """
    Get summary of all energy sources and their available features.
    
    Useful for OVOS to discover what energy sources and features are available
    in the system dynamically.
    
    Returns:
        List of energy sources with feature counts and sample features
        
    Example Response:
        [
            {
                "name": "electricity",
                "unit": "kWh",
                "features_count": 20,
                "sample_features": ["consumption_kwh", "production_count", "outdoor_temp_c"]
            },
            {
                "name": "natural_gas",
                "unit": "m3",
                "features_count": 9,
                "sample_features": ["consumption_m3", "outdoor_temp_c", "heating_degree_days"]
            }
        ]
    """
    try:
        summary = await feature_discovery.get_energy_source_summary()
        return {
            "success": True,
            "energy_sources": summary,
            "total_count": len(summary)
        }
    except Exception as e:
        logger.error(f"[OVOS] Failed to get energy sources: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve energy sources: {str(e)}"
        )


@router.get("/seus")
async def get_seus_by_energy_source(energy_source: Optional[str] = None):
    """
    Get list of SEUs, optionally filtered by energy source.
    
    Useful for OVOS to discover available SEUs before training.
    
    Args:
        energy_source: Optional filter by energy source name (e.g., 'electricity', 'natural_gas')
    
    Returns:
        List of SEUs with their names and energy sources
    """
    try:
        query = """
            SELECT 
                s.id,
                s.name,
                es.name as energy_source,
                es.unit,
                array_length(s.machine_ids, 1) as machine_count,
                s.baseline_year,
                s.r_squared
            FROM seus s
            JOIN energy_sources es ON s.energy_source_id = es.id
            WHERE s.is_active = true
        """
        
        params = []
        if energy_source:
            query += " AND es.name = $1"
            params.append(energy_source)
        
        query += " ORDER BY s.name"
        
        async with db.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            
            seus = [
                {
                    "id": str(row['id']),
                    "name": row['name'],
                    "energy_source": row['energy_source'],
                    "unit": row['unit'],
                    "machine_count": row['machine_count'],
                    "baseline_year": row['baseline_year'],
                    "r_squared": float(row['r_squared']) if row['r_squared'] else None
                }
                for row in rows
            ]
            
            return {
                "success": True,
                "seus": seus,
                "total_count": len(seus),
                "filtered_by": energy_source
            }
    
    except Exception as e:
        logger.error(f"[OVOS] Failed to get SEUs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve SEUs: {str(e)}"
        )


# ============================================================================
# Helper Functions
# ============================================================================

async def _lookup_seu_by_name_and_energy_source(
    seu_name: str, 
    energy_source_name: str
) -> Optional[dict]:
    """
    Lookup SEU by name and energy source.
    
    Supports fuzzy matching (case-insensitive, strips whitespace).
    """
    query = """
        SELECT 
            s.id,
            s.name,
            s.energy_source_id,
            es.name as energy_source_name,
            s.machine_ids
        FROM seus s
        JOIN energy_sources es ON s.energy_source_id = es.id
        WHERE LOWER(TRIM(s.name)) = LOWER(TRIM($1))
          AND LOWER(TRIM(es.name)) = LOWER(TRIM($2))
          AND s.is_active = true
    """
    
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(query, seu_name, energy_source_name)
        return dict(row) if row else None


def _build_voice_formula(intercept: float, coefficients: dict) -> str:
    """
    Build human-readable formula for voice output.
    
    Example:
        "Energy equals 0.061 plus 0.000043 times production count minus 0.000004 times outdoor temperature"
    """
    parts = [f"Energy equals {intercept:.3f}"]
    
    for feature_name, coef in coefficients.items():
        # Convert feature name to readable text
        readable_name = feature_name.replace('_', ' ')
        
        if coef >= 0:
            parts.append(f"plus {abs(coef):.6f} times {readable_name}")
        else:
            parts.append(f"minus {abs(coef):.6f} times {readable_name}")
    
    return ' '.join(parts)


def _build_technical_formula(intercept: float, coefficients: dict) -> str:
    """
    Build mathematical formula notation.
    
    Example:
        "E = 0.061 + 0.000043×P - 0.000004×T"
    """
    parts = [f"E = {intercept:.3f}"]
    
    for i, (feature_name, coef) in enumerate(coefficients.items()):
        # Use first letter of feature as variable
        var = feature_name[0].upper()
        
        if coef >= 0:
            parts.append(f"+ {coef:.6f}×{var}")
        else:
            parts.append(f"- {abs(coef):.6f}×{var}")
    
    return ' '.join(parts)
