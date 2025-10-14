"""
EnMS Analytics Service - Baseline Service
==========================================
Business logic for energy baseline training and predictions.

Author: EnMS Team
Phase: 3 - Analytics & ML
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from uuid import UUID
import logging

from models.baseline import BaselineModel
from database import (
    db,
    get_machine_by_id,
    get_machine_data_combined,
    save_baseline_model,
    get_active_baseline_model,
    deactivate_baseline_models
)
from config import settings

logger = logging.getLogger(__name__)


class BaselineService:
    """Service for managing energy baseline models."""
    
    @staticmethod
    async def train_baseline(
        machine_id: UUID,
        start_date: datetime,
        end_date: datetime,
        drivers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Train energy baseline model for a machine.
        
        Args:
            machine_id: Machine UUID
            start_date: Training data start date
            end_date: Training data end date
            drivers: Optional list of driver/feature names
            
        Returns:
            Training results with model metadata
        """
        logger.info(
            f"[TRAIN-SVC] Training baseline for machine {machine_id}: "
            f"{start_date.date()} to {end_date.date()}, drivers={drivers}"
        )
        
        # Validate machine exists
        logger.info(f"[TRAIN-SVC] Step 1: Validating machine exists")
        machine = await get_machine_by_id(machine_id)
        if not machine:
            logger.error(f"[TRAIN-SVC] Machine not found: {machine_id}")
            raise ValueError(f"Machine not found: {machine_id}")
        logger.info(f"[TRAIN-SVC] Machine found: {machine.get('name', 'Unknown')}")
        
        # Fetch training data (with machine status filtering)
        logger.info(f"[TRAIN-SVC] Step 2: Fetching training data")
        data = await get_machine_data_combined(
            machine_id=machine_id,
            start_time=start_date,
            end_time=end_date,
            include_machine_status=True  # Filter out maintenance/fault periods
        )
        
        logger.info(f"[TRAIN-SVC] Retrieved {len(data) if data else 0} data records")
        
        if not data:
            logger.error(f"[TRAIN-SVC] No data available for training")
            raise ValueError("No data available for training")
        
        if len(data) < settings.BASELINE_MIN_SAMPLES:
            error_msg = (
                f"Insufficient samples: {len(data)} "
                f"(minimum: {settings.BASELINE_MIN_SAMPLES}). "
                f"Collect at least {settings.BASELINE_MIN_SAMPLES - len(data)} more data points."
            )
            logger.error(f"[TRAIN-SVC] {error_msg}")
            raise ValueError(error_msg)
        
        # Get next model version
        logger.info(f"[TRAIN-SVC] Step 3: Getting next model version")
        existing_model = await get_active_baseline_model(machine_id)
        next_version = existing_model['model_version'] + 1 if existing_model else 1
        logger.info(f"[TRAIN-SVC] Next version will be: {next_version}")
        
        # Create and train model
        logger.info(f"[TRAIN-SVC] Step 4: Creating model instance")
        model = BaselineModel(
            machine_id=str(machine_id),
            model_version=next_version
        )
        
        logger.info(f"[TRAIN-SVC] Step 5: Starting model training")
        logger.info(f"[TRAIN-SVC] Training with {len(data)} records, target='total_energy_kwh', drivers={drivers}")
        
        try:
            training_results = model.train(
                data=data,
                target_column='total_energy_kwh',
                feature_columns=drivers
            )
            logger.info(f"[TRAIN-SVC] Training completed successfully")
        except Exception as e:
            logger.error(f"[TRAIN-SVC] Training failed in model.train(): {str(e)}", exc_info=True)
            raise
        
        # Validate R² threshold
        if model.r_squared < settings.BASELINE_MIN_R2:
            logger.warning(
                f"Model R² ({model.r_squared:.4f}) below threshold "
                f"({settings.BASELINE_MIN_R2}). Model may not be accurate."
            )
        
        # Save model to disk
        model_path = model.save()
        
        # Deactivate old models
        await deactivate_baseline_models(machine_id)
        
        # Save model metadata to database
        model_data = model.to_dict()
        model_id = await save_baseline_model(model_data)
        
        logger.info(
            f"✓ Baseline model trained and saved: {model_id} "
            f"(R²={model.r_squared:.4f})"
        )
        
        # Return comprehensive results
        return {
            'model_id': str(model_id),
            'machine_id': str(machine_id),
            'machine_name': machine['name'],
            'model_version': model.model_version,
            'r_squared': model.r_squared,
            'rmse': model.rmse,
            'mae': model.mae,
            'training_samples': model.training_samples,
            'coefficients': model.coefficients,
            'intercept': model.intercept,
            'feature_names': model.feature_names,
            'training_start_date': model.training_start_date.isoformat(),
            'training_end_date': model.training_end_date.isoformat(),
            'trained_at': datetime.utcnow().isoformat(),
            'model_path': str(model_path),
            'meets_quality_threshold': model.r_squared >= settings.BASELINE_MIN_R2
        }
    
    @staticmethod
    async def get_baseline_deviation(
        machine_id: UUID,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """
        Calculate baseline deviation for a machine over a time period.
        
        Args:
            machine_id: Machine UUID
            start_time: Start of analysis period
            end_time: End of analysis period
            
        Returns:
            Deviation analysis results
        """
        logger.info(
            f"Calculating baseline deviation for machine {machine_id}: "
            f"{start_time} to {end_time}"
        )
        
        # Get machine info
        machine = await get_machine_by_id(machine_id)
        if not machine:
            raise ValueError(f"Machine not found: {machine_id}")
        
        # Get active baseline model
        model_record = await get_active_baseline_model(machine_id)
        if not model_record:
            raise ValueError(
                f"No active baseline model found for machine {machine_id}. "
                "Train a model first."
            )
        
        # Load model from disk
        model_path = settings.MODEL_STORAGE_PATH + \
                     f"/baseline_{machine_id}_v{model_record['model_version']}.joblib"
        model = BaselineModel.load(model_path)
        
        # Fetch actual data
        data = await get_machine_data_combined(
            machine_id=machine_id,
            start_time=start_time,
            end_time=end_time,
            include_machine_status=True
        )
        
        if not data:
            raise ValueError("No data available for deviation analysis")
        
        # Make predictions
        predictions = model.predict_batch(data)
        
        # Calculate deviations
        hourly_deviations = []
        total_actual = 0.0
        total_predicted = 0.0
        
        for i, record in enumerate(data):
            actual = float(record['total_energy_kwh'])
            predicted = predictions[i]
            deviation_kwh, deviation_percent = model.calculate_deviation(
                actual, predicted
            )
            
            total_actual += actual
            total_predicted += predicted
            
            hourly_deviations.append({
                'time': record['time'].isoformat(),
                'actual_kwh': round(actual, 2),
                'predicted_kwh': round(predicted, 2),
                'deviation_kwh': round(deviation_kwh, 2),
                'deviation_percent': round(deviation_percent, 2)
            })
        
        # Calculate overall deviation
        overall_deviation_kwh = total_actual - total_predicted
        overall_deviation_percent = (overall_deviation_kwh / total_predicted * 100) if total_predicted > 0 else 0
        
        # Determine severity
        abs_deviation_percent = abs(overall_deviation_percent)
        if abs_deviation_percent > 15:
            severity = 'critical'
        elif abs_deviation_percent > 5:
            severity = 'warning'
        else:
            severity = 'normal'
        
        return {
            'machine_id': str(machine_id),
            'machine_name': machine['name'],
            'time_period': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat()
            },
            'baseline_model_version': model_record['model_version'],
            'total_actual_kwh': round(total_actual, 2),
            'total_predicted_kwh': round(total_predicted, 2),
            'deviation_kwh': round(overall_deviation_kwh, 2),
            'deviation_percent': round(overall_deviation_percent, 2),
            'deviation_severity': severity,
            'hourly_deviations': hourly_deviations
        }
    
    @staticmethod
    async def predict_energy(
        machine_id: UUID,
        features: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Predict energy consumption for given operating conditions.
        
        Args:
            machine_id: Machine UUID
            features: Dictionary of feature values (drivers)
            
        Returns:
            Prediction result
        """
        # Get active baseline model
        model_record = await get_active_baseline_model(machine_id)
        if not model_record:
            raise ValueError(
                f"No active baseline model found for machine {machine_id}"
            )
        
        # Load model
        model_path = settings.MODEL_STORAGE_PATH + \
                     f"/baseline_{machine_id}_v{model_record['model_version']}.joblib"
        model = BaselineModel.load(model_path)
        
        # Make prediction
        predicted_energy = model.predict(features)
        
        return {
            'machine_id': str(machine_id),
            'model_version': model_record['model_version'],
            'features': features,
            'predicted_energy_kwh': round(predicted_energy, 2)
        }
    
    @staticmethod
    async def list_baseline_models(machine_id: UUID) -> List[Dict[str, Any]]:
        """
        List all baseline models for a machine.
        
        Args:
            machine_id: Machine UUID
            
        Returns:
            List of model records
        """
        query = """
            SELECT 
                id, machine_id, model_name, model_version,
                training_samples, r_squared, rmse, mae,
                is_active, created_at
            FROM energy_baselines
            WHERE machine_id = $1
            ORDER BY model_version DESC
        """
        
        async with db.pool.acquire() as conn:
            rows = await conn.fetch(query, machine_id)
            return [dict(row) for row in rows]
    
    @staticmethod
    async def get_model_details(model_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific baseline model.
        
        Args:
            model_id: Model UUID
            
        Returns:
            Model details or None
        """
        query = """
            SELECT 
                eb.id, eb.machine_id, eb.model_name, eb.model_type, eb.model_version,
                eb.training_start_date, eb.training_end_date, eb.training_samples,
                eb.coefficients, eb.intercept, eb.feature_names,
                eb.r_squared, eb.rmse, eb.mae, eb.is_active, eb.created_at,
                m.name as machine_name, m.type as machine_type
            FROM energy_baselines eb
            JOIN machines m ON eb.machine_id = m.id
            WHERE eb.id = $1
        """
        
        async with db.pool.acquire() as conn:
            row = await conn.fetchrow(query, model_id)
            return dict(row) if row else None


# Global service instance
baseline_service = BaselineService()