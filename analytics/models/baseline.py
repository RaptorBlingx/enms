"""
EnMS Analytics Service - Energy Baseline Model
===============================================
Multiple Linear Regression for ISO 50001-compliant energy baseline (EnB).

Author: EnMS Team
Phase: 3 - Analytics & ML
"""

from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import joblib
import json
import logging
from pathlib import Path

from config import settings

logger = logging.getLogger(__name__)


class BaselineModel:
    """
    Energy Baseline (EnB) model using Multiple Linear Regression.
    
    Formula:
        Energy = β₀ + β₁(Production) + β₂(Temp) + β₃(Hours) + β₄(Material) + ε
    
    Features (Drivers):
        - Production count (units/hour)
        - Outdoor temperature (°C)
        - Operating hours (hours)
        - Pressure (bar)
        - Custom metadata fields
    """
    
    def __init__(self, machine_id: str, model_version: int = 1):
        """
        Initialize baseline model.
        
        Args:
            machine_id: Machine UUID
            model_version: Model version number
        """
        self.machine_id = machine_id
        self.model_version = model_version
        self.model = LinearRegression()
        self.feature_names: List[str] = []
        self.coefficients: Dict[str, float] = {}
        self.intercept: float = 0.0
        self.r_squared: float = 0.0
        self.rmse: float = 0.0
        self.mae: float = 0.0
        self.training_samples: int = 0
        self.training_start_date: Optional[datetime] = None
        self.training_end_date: Optional[datetime] = None
        self.is_trained: bool = False
    
    def prepare_data(
        self,
        data: List[Dict[str, Any]],
        target_column: str = 'total_energy_kwh',
        feature_columns: Optional[List[str]] = None
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Prepare training data from raw database records.
        
        Args:
            data: List of combined data records (energy + production + environmental)
            target_column: Target variable column name
            feature_columns: List of feature column names (if None, auto-select)
            
        Returns:
            Tuple of (X, y, feature_names)
        """
        # Convert to DataFrame
        df = pd.DataFrame(data)
        logger.info(f"[MODEL-PREP] DataFrame created with {len(df)} rows and {len(df.columns)} columns")
        logger.info(f"[MODEL-PREP] Column names: {list(df.columns)}")
        logger.info(f"[MODEL-PREP] First row sample: {df.iloc[0].to_dict() if len(df) > 0 else 'No data'}")
        
        # Auto-select features if not provided
        if feature_columns is None:
            feature_columns = [
                'total_production_count',
                'avg_outdoor_temp_c',
                'avg_pressure_bar',
                'avg_throughput_units_per_hour',
                'avg_machine_temp_c',
                'avg_load_factor'
            ]
        
        # Filter to columns that exist in the data
        available_features = [col for col in feature_columns if col in df.columns]
        
        logger.info(f"Available columns in data: {list(df.columns)}")
        logger.info(f"Requested features: {feature_columns}")
        logger.info(f"Features found in data: {available_features}")
        
        if len(available_features) == 0:
            raise ValueError(f"No valid features found in data. Available columns: {list(df.columns)}, Requested: {feature_columns}")
        
        # Remove rows with missing values
        df = df[[target_column] + available_features].dropna()
        
        if len(df) < settings.BASELINE_MIN_SAMPLES:
            raise ValueError(
                f"Insufficient samples after cleaning: {len(df)} "
                f"(minimum: {settings.BASELINE_MIN_SAMPLES})"
            )
        
        # Extract features (X) and target (y)
        X = df[available_features].values
        y = df[target_column].values
        
        logger.info(
            f"Prepared data: {len(df)} samples, "
            f"{len(available_features)} features: {available_features}"
        )
        
        return X, y, available_features
    
    def train(
        self,
        data: List[Dict[str, Any]],
        target_column: str = 'total_energy_kwh',
        feature_columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Train the baseline model.
        
        Args:
            data: Training data records
            target_column: Target variable column name
            feature_columns: Feature column names (if None, auto-select)
            
        Returns:
            Training results dictionary
        """
        logger.info(f"Training baseline model for machine: {self.machine_id}")
        
        # Prepare data
        try:
            logger.info(f"Received {len(data)} data records for training")
            logger.info(f"Target column: {target_column}, Feature columns: {feature_columns}")
            X, y, feature_names = self.prepare_data(data, target_column, feature_columns)
            self.feature_names = feature_names
            self.training_samples = int(len(X))
            logger.info(f"Data preparation successful: {self.training_samples} samples, {len(feature_names)} features")
        except Exception as e:
            logger.error(f"Error preparing data: {e}", exc_info=True)
            raise
        
        # Extract training dates
        df = pd.DataFrame(data)
        self.training_start_date = pd.to_datetime(df['time'].min())
        self.training_end_date = pd.to_datetime(df['time'].max())
        
        # Train model
        self.model.fit(X, y)
        
        # Make predictions on training data
        y_pred = self.model.predict(X)
        
        # Calculate metrics (convert numpy types to Python natives)
        self.r_squared = float(r2_score(y, y_pred))
        self.rmse = float(np.sqrt(mean_squared_error(y, y_pred)))
        self.mae = float(mean_absolute_error(y, y_pred))
        
        # Store coefficients
        self.intercept = float(self.model.intercept_)
        self.coefficients = {
            name: float(coef) 
            for name, coef in zip(feature_names, self.model.coef_)
        }
        
        self.is_trained = True
        
        # Validate model quality
        if self.r_squared < settings.BASELINE_MIN_R2:
            logger.warning(
                f"Model R² ({self.r_squared:.4f}) below minimum "
                f"({settings.BASELINE_MIN_R2})"
            )
        
        results = {
            'r_squared': self.r_squared,
            'rmse': self.rmse,
            'mae': self.mae,
            'training_samples': self.training_samples,
            'coefficients': self.coefficients,
            'intercept': self.intercept,
            'feature_names': feature_names,
            'training_start_date': self.training_start_date.isoformat(),
            'training_end_date': self.training_end_date.isoformat()
        }
        
        logger.info(
            f"✓ Model trained: R²={self.r_squared:.4f}, "
            f"RMSE={self.rmse:.4f}, MAE={self.mae:.4f}"
        )
        
        return results
    
    def predict(self, features: Dict[str, float]) -> float:
        """
        Predict energy consumption for given features.
        
        Args:
            features: Dictionary of feature values
            
        Returns:
            Predicted energy (kWh)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        # Create feature array in correct order
        X = np.array([[features.get(name, 0.0) for name in self.feature_names]])
        
        # Predict
        prediction = self.model.predict(X)[0]
        
        return float(prediction)
    
    def predict_batch(self, data: List[Dict[str, Any]]) -> np.ndarray:
        """
        Predict energy for multiple data points.
        
        Args:
            data: List of data records with features
            
        Returns:
            Array of predictions
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        # Convert to DataFrame and extract features
        df = pd.DataFrame(data)
        X = df[self.feature_names].fillna(0).values
        
        # Predict
        predictions = self.model.predict(X)
        
        return predictions
    
    def calculate_deviation(
        self,
        actual_energy: float,
        predicted_energy: float
    ) -> Tuple[float, float]:
        """
        Calculate baseline deviation.
        
        Args:
            actual_energy: Actual energy consumption (kWh)
            predicted_energy: Predicted energy consumption (kWh)
            
        Returns:
            Tuple of (deviation_kwh, deviation_percent)
        """
        deviation_kwh = float(actual_energy) - float(predicted_energy)
        
        if predicted_energy > 0:
            deviation_percent = (deviation_kwh / float(predicted_energy)) * 100
        else:
            deviation_percent = 0.0
        
        return deviation_kwh, deviation_percent
    
    def save(self, filepath: Optional[Path] = None) -> Path:
        """
        Save model to disk.
        
        Args:
            filepath: Optional custom filepath
            
        Returns:
            Path where model was saved
        """
        if filepath is None:
            filepath = Path(settings.MODEL_STORAGE_PATH) / \
                      f"baseline_{self.machine_id}_v{self.model_version}.joblib"
        
        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Save model state
        model_state = {
            'machine_id': self.machine_id,
            'model_version': self.model_version,
            'sklearn_model': self.model,
            'feature_names': self.feature_names,
            'coefficients': self.coefficients,
            'intercept': self.intercept,
            'r_squared': self.r_squared,
            'rmse': self.rmse,
            'mae': self.mae,
            'training_samples': self.training_samples,
            'training_start_date': self.training_start_date.isoformat() if self.training_start_date else None,
            'training_end_date': self.training_end_date.isoformat() if self.training_end_date else None
        }
        
        joblib.dump(model_state, filepath)
        logger.info(f"✓ Model saved to: {filepath}")
        
        return filepath
    
    @classmethod
    def load(cls, filepath: Path) -> 'BaselineModel':
        """
        Load model from disk.
        
        Args:
            filepath: Path to saved model
            
        Returns:
            Loaded BaselineModel instance
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        # Load model state
        model_state = joblib.load(filepath)
        
        # Create instance
        instance = cls(
            machine_id=model_state['machine_id'],
            model_version=model_state['model_version']
        )
        
        # Restore state
        instance.model = model_state['sklearn_model']
        instance.feature_names = model_state['feature_names']
        instance.coefficients = model_state['coefficients']
        instance.intercept = model_state['intercept']
        instance.r_squared = model_state['r_squared']
        instance.rmse = model_state['rmse']
        instance.mae = model_state['mae']
        instance.training_samples = model_state['training_samples']
        instance.training_start_date = pd.to_datetime(model_state['training_start_date']) if model_state['training_start_date'] else None
        instance.training_end_date = pd.to_datetime(model_state['training_end_date']) if model_state['training_end_date'] else None
        instance.is_trained = True
        
        logger.info(f"✓ Model loaded from: {filepath}")
        
        return instance
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary for database storage.
        
        Returns:
            Model metadata dictionary
        """
        return {
            'machine_id': self.machine_id,
            'model_name': f'baseline_v{self.model_version}',
            'model_type': 'linear_regression',
            'model_version': self.model_version,
            'training_start_date': self.training_start_date,
            'training_end_date': self.training_end_date,
            'training_samples': self.training_samples,
            'coefficients': json.dumps(self.coefficients),  # Convert to JSON string
            'intercept': self.intercept,
            'feature_names': self.feature_names,
            'r_squared': self.r_squared,
            'rmse': self.rmse,
            'mae': self.mae,
            'is_active': True,
            'trained_by': 'analytics-service'
        }