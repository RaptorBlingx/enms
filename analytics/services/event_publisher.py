"""
Event Publisher
===============
Publishes various system events to Redis channels for real-time distribution.

Phase 4 Session 5: Real-Time Updates
Author: EnMS Team
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from services.redis_manager import redis_manager
from config import settings

logger = logging.getLogger(__name__)


class EventPublisher:
    """Publishes various system events to Redis channels."""
    
    @staticmethod
    async def publish_anomaly_detected(
        machine_id: str,
        metric: str,
        value: float,
        anomaly_score: float,
        severity: str,
        timestamp: datetime
    ):
        """Publish anomaly detected event."""
        message = {
            "event_type": "anomaly_detected",
            "machine_id": machine_id,
            "metric": metric,
            "value": value,
            "anomaly_score": anomaly_score,
            "severity": severity,
            "timestamp": timestamp.isoformat(),
            "published_at": datetime.utcnow().isoformat()
        }
        
        await redis_manager.publish(settings.CHANNEL_ANOMALY_DETECTED, message)
        logger.info(f"Published anomaly event: {machine_id} - {metric}")
    
    @staticmethod
    async def publish_metric_updated(
        machine_id: str,
        metric: str,
        value: float,
        timestamp: datetime
    ):
        """Publish metric updated event."""
        message = {
            "event_type": "metric_updated",
            "machine_id": machine_id,
            "metric": metric,
            "value": value,
            "timestamp": timestamp.isoformat(),
            "published_at": datetime.utcnow().isoformat()
        }
        
        await redis_manager.publish(settings.CHANNEL_METRIC_UPDATED, message)
        logger.debug(f"Published metric update: {machine_id} - {metric}")
    
    @staticmethod
    async def publish_training_started(
        job_id: int,
        machine_id: str,
        model_type: str
    ):
        """Publish training started event."""
        message = {
            "event_type": "training_started",
            "job_id": job_id,
            "machine_id": machine_id,
            "model_type": model_type,
            "published_at": datetime.utcnow().isoformat()
        }
        
        await redis_manager.publish(settings.CHANNEL_TRAINING_STARTED, message)
        logger.info(f"Published training started: Job {job_id}")
    
    @staticmethod
    async def publish_training_progress(
        job_id: int,
        progress_pct: int,
        status: str,
        message: Optional[str] = None
    ):
        """Publish training progress event."""
        event_message = {
            "event_type": "training_progress",
            "job_id": job_id,
            "progress_pct": progress_pct,
            "status": status,
            "message": message,
            "published_at": datetime.utcnow().isoformat()
        }
        
        await redis_manager.publish(settings.CHANNEL_TRAINING_PROGRESS, event_message)
        logger.debug(f"Published training progress: Job {job_id} - {progress_pct}%")
    
    @staticmethod
    async def publish_training_completed(
        job_id: int,
        status: str,
        metrics: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ):
        """Publish training completed event."""
        message = {
            "event_type": "training_completed",
            "job_id": job_id,
            "status": status,
            "metrics": metrics,
            "error_message": error_message,
            "published_at": datetime.utcnow().isoformat()
        }
        
        await redis_manager.publish(settings.CHANNEL_TRAINING_COMPLETED, message)
        logger.info(f"Published training completed: Job {job_id} - {status}")
    
    @staticmethod
    async def publish_system_alert(
        alert_type: str,
        severity: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Publish system alert event."""
        event_message = {
            "event_type": "system_alert",
            "alert_type": alert_type,
            "severity": severity,
            "message": message,
            "details": details,
            "published_at": datetime.utcnow().isoformat()
        }
        
        await redis_manager.publish(settings.CHANNEL_SYSTEM_ALERT, event_message)
        logger.warning(f"Published system alert: {alert_type} - {severity}")


# Global instance
event_publisher = EventPublisher()
