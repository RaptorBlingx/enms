# Phase 4 Session 5: Real-Time Updates - Implementation Plan

**Session:** Phase 4 - Session 5  
**Feature:** Real-Time Updates & WebSocket Integration  
**Status:** Ready to Implement  
**Date:** October 15, 2025  
**Prerequisites:** Session 4 Complete (Model Performance Tracking)

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current System State](#current-system-state)
3. [Architecture Design](#architecture-design)
4. [Technology Stack](#technology-stack)
5. [Implementation Steps](#implementation-steps)
6. [Database Changes](#database-changes)
7. [Testing Strategy](#testing-strategy)
8. [Rollback Plan](#rollback-plan)
9. [Success Criteria](#success-criteria)
10. [OVOS Integration](#ovos-integration)

---

## Executive Summary

### Objectives

Transform the current polling-based UI into a real-time, event-driven system that pushes updates to clients instantly without manual refresh.

### Key Features

- ✅ **WebSocket Connections** - Bidirectional real-time communication
- ✅ **Live Dashboard Updates** - Instant metric updates without polling
- ✅ **Push Notifications** - Real-time anomaly alerts to connected clients
- ✅ **Live Training Progress** - Real-time model training status updates
- ✅ **Event-Driven Architecture** - Redis pub/sub for system-wide events
- ✅ **Auto-Updating Charts** - Charts update automatically on new data

### Benefits

- **Reduced Latency** - Sub-second updates vs 5-30 second polling delays
- **Reduced Server Load** - Eliminate constant polling requests
- **Better UX** - Instant feedback and live updates
- **Scalability** - Event-driven architecture scales horizontally
- **Flexibility** - Easy to add new real-time features

---

## Current System State

### ✅ What's Working (Session 4)

```yaml
Service: EnMS Analytics Service v1.0.0
Framework: FastAPI 0.104.1 (WebSocket support built-in ✅)
Database: PostgreSQL + TimescaleDB + asyncpg
Cache: Redis 7 (container running, not configured for pub/sub)
Scheduler: APScheduler (4 automated jobs)
UI: Vanilla JavaScript (REST polling with setInterval)

Active Features:
  - Baseline Model Training ✅
  - Anomaly Detection ✅
  - KPI Calculation ✅
  - Forecasting ✅
  - Model Performance Tracking ✅
  - Visualization (Sankey, Heatmap, Comparison) ✅
  - 7 Active Machines ✅
  - 45+ API Endpoints ✅
```

### ⚠️ Current Limitations

```yaml
Communication: REST only (no WebSocket)
Updates: Manual refresh or polling (setInterval 5-30s)
Notifications: None (users must check manually)
Events: No event-driven architecture
Real-time: No push updates
Server Load: High (constant polling from all clients)
```

### 📊 Current UI Polling Behavior

```javascript
// dashboard.html - Lines ~200-230
function startAutoRefresh() {
    // Refresh every 30 seconds
    setInterval(() => {
        loadDashboardStats();
        loadRecentAnomalies();
    }, 30000);
}

// model_performance.html - Similar pattern
setInterval(() => {
    loadTrainingJobs();
}, 5000);  // Poll every 5 seconds
```

**Problem:** Every client polls every 5-30 seconds = High server load + Delayed updates

---

## Architecture Design

### 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT BROWSER                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ Dashboard  │  │  Anomaly   │  │   Model    │            │
│  │    UI      │  │     UI     │  │ Performance│            │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘            │
│        │               │               │                     │
│        └───────────────┴───────────────┘                     │
│                        │                                     │
│                   WebSocket                                  │
│                  Connection(s)                               │
└────────────────────────┼────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              FASTAPI ANALYTICS SERVICE (Port 8001)           │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              WebSocket Manager                        │  │
│  │  - Connection lifecycle management                    │  │
│  │  - Client registration/unregistration                 │  │
│  │  - Message broadcasting                               │  │
│  │  - Reconnection handling                              │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 │                                            │
│  ┌──────────────┴───────────────────────────────────────┐  │
│  │              WebSocket Routes                         │  │
│  │  /ws/dashboard    - Real-time dashboard metrics       │  │
│  │  /ws/anomalies    - Live anomaly alerts              │  │
│  │  /ws/training     - Training progress updates         │  │
│  │  /ws/events       - General system events             │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 │                                            │
│  ┌──────────────┴───────────────────────────────────────┐  │
│  │          Event Publisher (Redis Pub/Sub)              │  │
│  │  - Publishes events to Redis channels                 │  │
│  │  - Topics: anomaly.detected, metric.updated, etc.     │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Event Subscriber (Redis Pub/Sub)             │  │
│  │  - Subscribes to Redis channels                       │  │
│  │  - Forwards events to WebSocket clients               │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    REDIS (Port 6379)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                 Pub/Sub Channels                      │  │
│  │  - anomaly.detected    (Anomaly alerts)              │  │
│  │  - metric.updated      (Metric changes)              │  │
│  │  - training.started    (Training begins)             │  │
│  │  - training.progress   (Training updates)            │  │
│  │  - training.completed  (Training finished)           │  │
│  │  - system.alert        (System notifications)        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 🔄 Event Flow Examples

#### Example 1: Anomaly Detection Event

```
1. Scheduler runs anomaly detection job
2. New anomaly detected in database
3. API endpoint publishes event to Redis:
   Channel: "anomaly.detected"
   Payload: {machine_id, severity, value, timestamp}
4. Redis broadcasts to all subscribers
5. WebSocket subscriber receives event
6. WebSocket Manager broadcasts to all connected clients
7. Browser receives WebSocket message
8. UI shows toast notification + updates anomaly list
```

#### Example 2: Training Progress Update

```
1. User starts model training (or scheduled job)
2. Training job publishes periodic progress events:
   Channel: "training.progress"
   Payload: {job_id, status, progress_pct, eta}
3. Redis broadcasts to all subscribers
4. WebSocket Manager sends to relevant clients
5. Browser updates progress bar in real-time
6. Training completion event auto-refreshes results
```

### 🌐 WebSocket Connection Management

```python
# Pseudo-code for connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    async def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)
    
    async def broadcast(self, message: dict, channel: str):
        # Send to all connected clients subscribed to channel
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except:
                await self.disconnect(client_id)
```

---

## Technology Stack

### 🛠️ Backend Dependencies

```python
# requirements.txt - ADDITIONS NEEDED

# WebSocket Support (already available in FastAPI 0.104.1)
# No additional WebSocket library needed

# Redis Async Client for Pub/Sub
redis==5.0.1              # NEW - Redis client
aioredis==2.0.1           # NEW - Async Redis (alternative)

# WebSocket utilities
websockets==12.0          # NEW - WebSocket protocol support

# Background task improvements
asyncio-mqtt==0.16.1      # Optional - If we want MQTT→WebSocket bridge
```

### 📦 Frontend Dependencies (CDN)

```html
<!-- No additional libraries needed - Native WebSocket API -->
<script>
  // Built-in browser WebSocket API
  const ws = new WebSocket('ws://localhost:8001/ws/dashboard');
</script>
```

### 🐳 Docker Configuration Updates

```yaml
# docker-compose.yml - Redis service (already exists)
redis:
  image: redis:7-alpine
  command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
  ports:
    - "6380:6379"
  # Add environment for pub/sub configuration
  environment:
    - REDIS_NOTIFY_KEYSPACE_EVENTS=Ex  # Enable keyspace notifications
```

### ⚙️ Configuration Changes

```python
# analytics/config.py - ADD THESE SETTINGS

class Settings(BaseSettings):
    # ... existing settings ...
    
    # ============================================================================
    # WebSocket Configuration (NEW)
    # ============================================================================
    WEBSOCKET_ENABLED: bool = True
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30  # seconds
    WEBSOCKET_MAX_CONNECTIONS: int = 100
    WEBSOCKET_MESSAGE_QUEUE_SIZE: int = 1000
    
    # ============================================================================
    # Redis Pub/Sub Configuration (NEW)
    # ============================================================================
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "raptorblingx"
    REDIS_DB: int = 0
    REDIS_PUBSUB_ENABLED: bool = True
    
    # Pub/Sub Channel Names
    CHANNEL_ANOMALY_DETECTED: str = "anomaly.detected"
    CHANNEL_METRIC_UPDATED: str = "metric.updated"
    CHANNEL_TRAINING_STARTED: str = "training.started"
    CHANNEL_TRAINING_PROGRESS: str = "training.progress"
    CHANNEL_TRAINING_COMPLETED: str = "training.completed"
    CHANNEL_SYSTEM_ALERT: str = "system.alert"
```

---

## Implementation Steps

### 📝 Phase 1: Backend Infrastructure (Steps 1-3)

#### **Step 1: Install Dependencies** ✅ **COMPLETED**

```bash
# Add to analytics/requirements.txt
echo "redis==5.0.1" >> analytics/requirements.txt
echo "websockets==12.0" >> analytics/requirements.txt

# Rebuild analytics container
docker compose build analytics
docker compose up -d analytics
```

**Status:** ✅ Dependencies installed and verified:
- redis==5.0.1 ✅
- websockets==12.0 ✅

#### **Step 2: Update Configuration** ✅ **COMPLETED**

**File:** `analytics/config.py`

```python
# Add WebSocket and Redis settings (see Configuration Changes section above)
```

**Status:** ✅ Configuration updated and verified:
- WebSocket settings added ✅
- Redis Pub/Sub settings added ✅
- 6 channel names configured ✅
- Container rebuilt and restarted ✅

#### **Step 3: Create Redis Connection Manager** ✅ **COMPLETED**

**New File:** `analytics/services/redis_manager.py`

**Status:** ✅ Redis Manager created and tested:
- File created with full implementation ✅
- Connection test successful ✅
- Pub/Sub methods implemented ✅
- Global redis_manager instance ready ✅

```python
"""
Redis Connection Manager for Pub/Sub
"""
import redis.asyncio as redis
from typing import Optional, Callable, Dict
import logging
import asyncio
from config import settings

logger = logging.getLogger(__name__)


class RedisManager:
    """Manages Redis connection and pub/sub operations."""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self.subscribers: Dict[str, list] = {}
        self._listener_task: Optional[asyncio.Task] = None
    
    async def connect(self):
        """Establish Redis connection."""
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("✓ Redis connected successfully")
            
            # Initialize pub/sub
            self.pubsub = self.redis_client.pubsub()
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Close Redis connection."""
        if self._listener_task:
            self._listener_task.cancel()
        
        if self.pubsub:
            await self.pubsub.close()
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Redis disconnected")
    
    async def publish(self, channel: str, message: dict):
        """
        Publish message to Redis channel.
        
        Args:
            channel: Channel name
            message: Message dict (will be JSON serialized)
        """
        try:
            import json
            message_str = json.dumps(message)
            await self.redis_client.publish(channel, message_str)
            logger.debug(f"Published to {channel}: {message}")
        except Exception as e:
            logger.error(f"Failed to publish to {channel}: {e}")
    
    async def subscribe(self, channel: str, callback: Callable):
        """
        Subscribe to Redis channel with callback.
        
        Args:
            channel: Channel name
            callback: Async function to call with message
        """
        try:
            await self.pubsub.subscribe(channel)
            
            if channel not in self.subscribers:
                self.subscribers[channel] = []
            self.subscribers[channel].append(callback)
            
            logger.info(f"Subscribed to channel: {channel}")
            
            # Start listener if not already running
            if not self._listener_task:
                self._listener_task = asyncio.create_task(self._listen())
        
        except Exception as e:
            logger.error(f"Failed to subscribe to {channel}: {e}")
    
    async def _listen(self):
        """Listen for messages on subscribed channels."""
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    channel = message["channel"]
                    data = message["data"]
                    
                    # Parse JSON
                    import json
                    try:
                        parsed_data = json.loads(data)
                    except:
                        parsed_data = data
                    
                    # Call all callbacks for this channel
                    if channel in self.subscribers:
                        for callback in self.subscribers[channel]:
                            try:
                                await callback(channel, parsed_data)
                            except Exception as e:
                                logger.error(f"Callback error for {channel}: {e}")
        
        except asyncio.CancelledError:
            logger.info("Redis listener cancelled")
        except Exception as e:
            logger.error(f"Redis listener error: {e}")


# Global instance
redis_manager = RedisManager()
```

---

### 📝 Phase 2: WebSocket Infrastructure (Steps 4-5)

#### **Step 4: Create WebSocket Connection Manager** ✅ **COMPLETED**

**New File:** `analytics/services/websocket_manager.py`

**Status:** ✅ WebSocket Manager created and tested:
- File created with full implementation ✅
- Connection manager imported successfully ✅
- 4 connection types initialized (dashboard, anomalies, training, events) ✅
- Global connection_manager instance ready ✅

```python
"""
WebSocket Connection Manager
"""
from fastapi import WebSocket
from typing import Dict, Set
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting."""
    
    def __init__(self):
        # Store connections by type
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {
            "dashboard": {},
            "anomalies": {},
            "training": {},
            "events": {}
        }
    
    async def connect(self, websocket: WebSocket, client_id: str, connection_type: str):
        """
        Accept and register new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            client_id: Unique client identifier
            connection_type: Type of connection (dashboard, anomalies, training, events)
        """
        await websocket.accept()
        
        if connection_type not in self.active_connections:
            self.active_connections[connection_type] = {}
        
        self.active_connections[connection_type][client_id] = websocket
        
        logger.info(f"Client {client_id} connected to {connection_type}")
        logger.info(f"Total connections: {self.get_connection_count()}")
        
        # Send welcome message
        await self.send_personal_message(
            {
                "type": "connection",
                "status": "connected",
                "client_id": client_id,
                "connection_type": connection_type,
                "timestamp": datetime.utcnow().isoformat()
            },
            websocket
        )
    
    def disconnect(self, client_id: str, connection_type: str):
        """
        Remove WebSocket connection.
        
        Args:
            client_id: Client identifier
            connection_type: Type of connection
        """
        if connection_type in self.active_connections:
            if client_id in self.active_connections[connection_type]:
                del self.active_connections[connection_type][client_id]
                logger.info(f"Client {client_id} disconnected from {connection_type}")
                logger.info(f"Total connections: {self.get_connection_count()}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific client."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
    
    async def broadcast(self, message: dict, connection_type: str = None):
        """
        Broadcast message to all clients or specific connection type.
        
        Args:
            message: Message to broadcast
            connection_type: If specified, only broadcast to this type
        """
        if connection_type:
            # Broadcast to specific type
            await self._broadcast_to_type(message, connection_type)
        else:
            # Broadcast to all
            for conn_type in self.active_connections:
                await self._broadcast_to_type(message, conn_type)
    
    async def _broadcast_to_type(self, message: dict, connection_type: str):
        """Broadcast to all connections of a specific type."""
        if connection_type not in self.active_connections:
            return
        
        disconnected = []
        
        for client_id, websocket in self.active_connections[connection_type].items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to {client_id}: {e}")
                disconnected.append(client_id)
        
        # Remove disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id, connection_type)
    
    def get_connection_count(self) -> int:
        """Get total number of active connections."""
        total = 0
        for conn_type in self.active_connections:
            total += len(self.active_connections[conn_type])
        return total
    
    def get_connections_by_type(self) -> dict:
        """Get connection count by type."""
        return {
            conn_type: len(connections)
            for conn_type, connections in self.active_connections.items()
        }


# Global instance
connection_manager = ConnectionManager()
```

#### **Step 5: Create WebSocket Routes** ✅ **COMPLETED**

**New File:** `analytics/api/websocket_routes.py`

**Status:** ✅ WebSocket routes created and registered:
- File created with 4 WebSocket endpoints ✅
- Routes imported in main.py ✅
- Router registered with API prefix ✅
- Endpoints available:
  - `/api/v1/ws/dashboard` ✅
  - `/api/v1/ws/anomalies` ✅
  - `/api/v1/ws/training` ✅
  - `/api/v1/ws/events` ✅

```python
"""
WebSocket API Routes
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import logging
import uuid
from datetime import datetime

from services.websocket_manager import connection_manager
from services.redis_manager import redis_manager
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/dashboard")
async def websocket_dashboard(websocket: WebSocket, client_id: Optional[str] = Query(None)):
    """
    WebSocket endpoint for real-time dashboard updates.
    
    Streams:
    - Active machine count updates
    - Baseline model count updates
    - Recent anomaly count updates
    - Scheduler status updates
    """
    if not client_id:
        client_id = str(uuid.uuid4())
    
    await connection_manager.connect(websocket, client_id, "dashboard")
    
    try:
        while True:
            # Keep connection alive and receive client messages
            data = await websocket.receive_text()
            
            # Echo back or handle client messages
            if data == "ping":
                await connection_manager.send_personal_message(
                    {"type": "pong", "timestamp": datetime.utcnow().isoformat()},
                    websocket
                )
    
    except WebSocketDisconnect:
        connection_manager.disconnect(client_id, "dashboard")
        logger.info(f"Dashboard client {client_id} disconnected")
    
    except Exception as e:
        logger.error(f"Dashboard WebSocket error: {e}")
        connection_manager.disconnect(client_id, "dashboard")


@router.websocket("/anomalies")
async def websocket_anomalies(websocket: WebSocket, client_id: Optional[str] = Query(None)):
    """
    WebSocket endpoint for real-time anomaly alerts.
    
    Streams:
    - New anomaly detections
    - Anomaly severity changes
    - Anomaly acknowledgments
    """
    if not client_id:
        client_id = str(uuid.uuid4())
    
    await connection_manager.connect(websocket, client_id, "anomalies")
    
    try:
        while True:
            data = await websocket.receive_text()
            
            if data == "ping":
                await connection_manager.send_personal_message(
                    {"type": "pong", "timestamp": datetime.utcnow().isoformat()},
                    websocket
                )
    
    except WebSocketDisconnect:
        connection_manager.disconnect(client_id, "anomalies")
        logger.info(f"Anomalies client {client_id} disconnected")
    
    except Exception as e:
        logger.error(f"Anomalies WebSocket error: {e}")
        connection_manager.disconnect(client_id, "anomalies")


@router.websocket("/training")
async def websocket_training(websocket: WebSocket, client_id: Optional[str] = Query(None)):
    """
    WebSocket endpoint for real-time training progress.
    
    Streams:
    - Training job started events
    - Training progress updates
    - Training completion events
    - Training error notifications
    """
    if not client_id:
        client_id = str(uuid.uuid4())
    
    await connection_manager.connect(websocket, client_id, "training")
    
    try:
        while True:
            data = await websocket.receive_text()
            
            if data == "ping":
                await connection_manager.send_personal_message(
                    {"type": "pong", "timestamp": datetime.utcnow().isoformat()},
                    websocket
                )
    
    except WebSocketDisconnect:
        connection_manager.disconnect(client_id, "training")
        logger.info(f"Training client {client_id} disconnected")
    
    except Exception as e:
        logger.error(f"Training WebSocket error: {e}")
        connection_manager.disconnect(client_id, "training")


@router.websocket("/events")
async def websocket_events(websocket: WebSocket, client_id: Optional[str] = Query(None)):
    """
    WebSocket endpoint for general system events.
    
    Streams:
    - System alerts
    - Service status changes
    - Configuration updates
    - General notifications
    """
    if not client_id:
        client_id = str(uuid.uuid4())
    
    await connection_manager.connect(websocket, client_id, "events")
    
    try:
        while True:
            data = await websocket.receive_text()
            
            if data == "ping":
                await connection_manager.send_personal_message(
                    {"type": "pong", "timestamp": datetime.utcnow().isoformat()},
                    websocket
                )
    
    except WebSocketDisconnect:
        connection_manager.disconnect(client_id, "events")
        logger.info(f"Events client {client_id} disconnected")
    
    except Exception as e:
        logger.error(f"Events WebSocket error: {e}")
        connection_manager.disconnect(client_id, "events")
```

---

### 📝 Phase 3: Event Publisher Integration (Steps 6-7)

#### **Step 6: Create Event Publisher Helper** ✅ **COMPLETED**

**New File:** `analytics/services/event_publisher.py`

**Status:** ✅ Event Publisher created:
- File created with 6 event types ✅
- Anomaly detected events ✅
- Metric updated events ✅
- Training lifecycle events (started, progress, completed) ✅
- System alert events ✅
- Global event_publisher instance ready ✅

```python
"""
Event Publisher - Publishes events to Redis channels
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
```

#### **Step 7: Create Event Subscriber** ✅ **COMPLETED**

**New File:** `analytics/services/event_subscriber.py`

**Status:** ✅ Event Subscriber created:
- File created with 6 event handlers ✅
- Subscribes to all Redis channels ✅
- Forwards events to appropriate WebSocket clients ✅
- Handles anomaly, metric, training, and system events ✅
- Global event_subscriber instance ready ✅

```python
"""
Event Subscriber - Subscribes to Redis channels and forwards to WebSocket clients
"""
import logging
from typing import Dict, Any

from services.redis_manager import redis_manager
from services.websocket_manager import connection_manager
from config import settings

logger = logging.getLogger(__name__)


class EventSubscriber:
    """Subscribes to Redis events and forwards to WebSocket clients."""
    
    async def start(self):
        """Start subscribing to all channels."""
        logger.info("Starting event subscriber...")
        
        # Subscribe to all channels
        await redis_manager.subscribe(
            settings.CHANNEL_ANOMALY_DETECTED,
            self._handle_anomaly_detected
        )
        
        await redis_manager.subscribe(
            settings.CHANNEL_METRIC_UPDATED,
            self._handle_metric_updated
        )
        
        await redis_manager.subscribe(
            settings.CHANNEL_TRAINING_STARTED,
            self._handle_training_started
        )
        
        await redis_manager.subscribe(
            settings.CHANNEL_TRAINING_PROGRESS,
            self._handle_training_progress
        )
        
        await redis_manager.subscribe(
            settings.CHANNEL_TRAINING_COMPLETED,
            self._handle_training_completed
        )
        
        await redis_manager.subscribe(
            settings.CHANNEL_SYSTEM_ALERT,
            self._handle_system_alert
        )
        
        logger.info("✓ Event subscriber started")
    
    async def _handle_anomaly_detected(self, channel: str, data: Dict[str, Any]):
        """Handle anomaly detected event."""
        logger.info(f"Anomaly detected: {data.get('machine_id')} - {data.get('severity')}")
        
        # Broadcast to dashboard clients
        await connection_manager.broadcast(
            {
                "type": "anomaly_detected",
                "data": data
            },
            connection_type="dashboard"
        )
        
        # Broadcast to anomaly page clients
        await connection_manager.broadcast(
            {
                "type": "anomaly_detected",
                "data": data
            },
            connection_type="anomalies"
        )
    
    async def _handle_metric_updated(self, channel: str, data: Dict[str, Any]):
        """Handle metric updated event."""
        logger.debug(f"Metric updated: {data.get('machine_id')} - {data.get('metric')}")
        
        # Broadcast to dashboard clients
        await connection_manager.broadcast(
            {
                "type": "metric_updated",
                "data": data
            },
            connection_type="dashboard"
        )
    
    async def _handle_training_started(self, channel: str, data: Dict[str, Any]):
        """Handle training started event."""
        logger.info(f"Training started: Job {data.get('job_id')}")
        
        # Broadcast to training page clients
        await connection_manager.broadcast(
            {
                "type": "training_started",
                "data": data
            },
            connection_type="training"
        )
    
    async def _handle_training_progress(self, channel: str, data: Dict[str, Any]):
        """Handle training progress event."""
        logger.debug(f"Training progress: Job {data.get('job_id')} - {data.get('progress_pct')}%")
        
        # Broadcast to training page clients
        await connection_manager.broadcast(
            {
                "type": "training_progress",
                "data": data
            },
            connection_type="training"
        )
    
    async def _handle_training_completed(self, channel: str, data: Dict[str, Any]):
        """Handle training completed event."""
        logger.info(f"Training completed: Job {data.get('job_id')} - {data.get('status')}")
        
        # Broadcast to training page clients
        await connection_manager.broadcast(
            {
                "type": "training_completed",
                "data": data
            },
            connection_type="training"
        )
        
        # Also update dashboard
        await connection_manager.broadcast(
            {
                "type": "model_updated",
                "data": data
            },
            connection_type="dashboard"
        )
    
    async def _handle_system_alert(self, channel: str, data: Dict[str, Any]):
        """Handle system alert event."""
        logger.warning(f"System alert: {data.get('alert_type')} - {data.get('severity')}")
        
        # Broadcast to all event clients
        await connection_manager.broadcast(
            {
                "type": "system_alert",
                "data": data
            },
            connection_type="events"
        )


# Global instance
event_subscriber = EventSubscriber()
```

---

### 📝 Phase 4: Main Application Integration (Step 8)

#### **Step 8: Update main.py** ✅ **COMPLETED**

**File:** `analytics/main.py`

**Status:** ✅ Main application integration complete:
- Redis manager integrated into lifespan ✅
- Event subscriber started on application startup ✅
- Graceful shutdown for Redis connection ✅
- All 6 channels subscribed successfully ✅
- Test event published and received ✅

```python
# Add to imports at top
from services.redis_manager import redis_manager
from services.event_subscriber import event_subscriber
from api import websocket_routes  # NEW import

# Update lifespan function
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan (startup and shutdown)."""
    # Startup
    logger.info("=" * 70)
    logger.info(f"🚀 Starting {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}")
    logger.info("=" * 70)
    
    try:
        # Connect to database
        logger.info("Connecting to database...")
        await db.connect()
        
        is_healthy = await db.health_check()
        if not is_healthy:
            raise Exception("Database health check failed")
        logger.info("✓ Database connected and healthy")
        
        # Connect to Redis (NEW)
        if settings.REDIS_PUBSUB_ENABLED:
            logger.info("Connecting to Redis...")
            await redis_manager.connect()
            logger.info("✓ Redis connected")
            
            # Start event subscriber (NEW)
            logger.info("Starting event subscriber...")
            await event_subscriber.start()
            logger.info("✓ Event subscriber started")
        
        # Clean up stuck training jobs
        logger.info("Cleaning up stuck training jobs...")
        stuck_count = await cleanup_stuck_training_jobs()
        if stuck_count > 0:
            logger.info(f"✓ Cleaned up {stuck_count} stuck training job(s)")
        else:
            logger.info("✓ No stuck training jobs found")
        
        # Start scheduler
        if settings.SCHEDULER_ENABLED:
            from scheduler.jobs import scheduler
            scheduler.start()
            logger.info("✓ Scheduler started")
            logger.info(f"  Scheduled jobs: {len(scheduler.get_jobs())}")
        
        logger.info("=" * 70)
        logger.info("✓ Service started successfully")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"Failed to start service: {e}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    
    if settings.SCHEDULER_ENABLED:
        from scheduler.jobs import scheduler
        scheduler.shutdown()
        logger.info("✓ Scheduler stopped")
    
    # Disconnect Redis (NEW)
    if settings.REDIS_PUBSUB_ENABLED:
        await redis_manager.disconnect()
        logger.info("✓ Redis disconnected")
    
    await db.disconnect()
    logger.info("✓ Database disconnected")
    logger.info("Shutdown complete")

# Add WebSocket router AFTER creating app
app.include_router(baseline_routes.router)
app.include_router(anomaly_routes.router)
app.include_router(kpi_routes.router)
app.include_router(forecast_routes.router)
app.include_router(timeseries_routes.router)
app.include_router(sankey_routes.router)
app.include_router(heatmap_routes.router)
app.include_router(comparison_routes.router)
app.include_router(model_performance_routes.router)
app.include_router(websocket_routes.router)  # NEW - WebSocket routes
```

---

### ✅ Phase 5: Integrate Event Publishing (Step 9) - COMPLETE

#### **Step 9: Add Event Publishing to Existing Routes** ✅

**Example 1: Anomaly Detection Route**

**File:** `analytics/api/anomaly_routes.py`

```python
# Add import
from services.event_publisher import event_publisher

# Update detect_anomalies endpoint
@router.post("/detect/{machine_id}")
async def detect_anomalies(
    machine_id: str,
    background_tasks: BackgroundTasks
):
    """Detect anomalies for a specific machine."""
    try:
        # ... existing anomaly detection logic ...
        
        # After storing anomalies in database, publish events
        if new_anomalies:
            for anomaly in new_anomalies:
                # Publish event (non-blocking)
                background_tasks.add_task(
                    event_publisher.publish_anomaly_detected,
                    machine_id=anomaly["machine_id"],
                    metric=anomaly["metric"],
                    value=anomaly["value"],
                    anomaly_score=anomaly["anomaly_score"],
                    severity=anomaly["severity"],
                    timestamp=anomaly["timestamp"]
                )
        
        # ... return response ...
```

**Example 2: Model Training Route**

**File:** `analytics/api/model_performance_routes.py`

```python
# Add import
from services.event_publisher import event_publisher

# Update train_model endpoint
@router.post("/train/{machine_id}/{model_type}")
async def train_model(
    machine_id: str,
    model_type: str,
    background_tasks: BackgroundTasks
):
    """Train a model for a specific machine."""
    try:
        # ... create training job ...
        
        job_id = result["job_id"]
        
        # Publish training started event
        background_tasks.add_task(
            event_publisher.publish_training_started,
            job_id=job_id,
            machine_id=machine_id,
            model_type=model_type
        )
        
        # ... start training in background ...
        
        # Publish progress updates during training
        # (implement in training logic)
        
        return {"success": True, "job_id": job_id}
```

**✅ Completion Status (October 15, 2025):**

**Files Modified:**
1. ✅ `analytics/api/routes/model_performance.py` - Added training event publishing
   - Training started event when user triggers training
   - Progress events at 20% and 60% during training
   - Completion events with metrics on success
   - Failure events with error messages

2. ✅ `analytics/services/anomaly_service.py` - Added anomaly event publishing
   - Publishes anomaly_detected event when anomalies are saved
   - Includes all anomaly details (severity, type, metrics, deviations)
   - Error handling for event publishing failures

**Verification:**
- ✅ Container rebuilt successfully
- ✅ Service started with all 6 Redis channels subscribed
- ✅ Event publishing integrated into model training workflow
- ✅ Event publishing integrated into anomaly detection workflow

**Next Steps:**
- Proceed to Phase 6: Frontend WebSocket Integration

---

### 📝 Phase 6: Frontend WebSocket Integration (Steps 10-11)

#### **Step 10: Create WebSocket Client Utility**

**New File:** `analytics/ui/static/js/websocket-client.js`

```javascript
/**
 * WebSocket Client Utility
 * Handles WebSocket connections with auto-reconnect
 */

class WebSocketClient {
    constructor(endpoint, onMessage, onConnect, onDisconnect) {
        this.endpoint = endpoint;
        this.onMessage = onMessage;
        this.onConnect = onConnect || (() => {});
        this.onDisconnect = onDisconnect || (() => {});
        
        this.ws = null;
        this.clientId = this.generateClientId();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 1000; // Start with 1 second
        this.isConnected = false;
        this.shouldReconnect = true;
        
        this.connect();
    }
    
    generateClientId() {
        return `client-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }
    
    getWebSocketUrl() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.hostname;
        const port = '8001'; // Analytics service port
        return `${protocol}//${host}:${port}${this.endpoint}?client_id=${this.clientId}`;
    }
    
    connect() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            console.log('WebSocket already connected');
            return;
        }
        
        const url = this.getWebSocketUrl();
        console.log(`Connecting to WebSocket: ${url}`);
        
        try {
            this.ws = new WebSocket(url);
            
            this.ws.onopen = () => {
                console.log(`WebSocket connected: ${this.endpoint}`);
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.reconnectDelay = 1000;
                this.onConnect();
                
                // Start heartbeat
                this.startHeartbeat();
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    console.log('WebSocket message received:', data);
                    
                    // Handle pong responses
                    if (data.type === 'pong') {
                        return;
                    }
                    
                    // Call message handler
                    this.onMessage(data);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
            this.ws.onclose = () => {
                console.log(`WebSocket disconnected: ${this.endpoint}`);
                this.isConnected = false;
                this.stopHeartbeat();
                this.onDisconnect();
                
                // Attempt to reconnect
                if (this.shouldReconnect) {
                    this.reconnect();
                }
            };
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            if (this.shouldReconnect) {
                this.reconnect();
            }
        }
    }
    
    reconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnect attempts reached');
            return;
        }
        
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1);
        
        console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        
        setTimeout(() => {
            this.connect();
        }, delay);
    }
    
    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.error('WebSocket not connected');
        }
    }
    
    sendText(text) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(text);
        } else {
            console.error('WebSocket not connected');
        }
    }
    
    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.sendText('ping');
            }
        }, 30000); // Ping every 30 seconds
    }
    
    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }
    
    disconnect() {
        this.shouldReconnect = false;
        this.stopHeartbeat();
        
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}
```

#### **Step 11: Update Dashboard UI**

**File:** `analytics/ui/templates/dashboard.html`

```html
<!-- Add after existing script tags -->
<script src="/api/analytics/static/js/websocket-client.js"></script>
<script>
// WebSocket connection for real-time updates
let dashboardWS = null;

function initWebSocket() {
    dashboardWS = new WebSocketClient(
        '/api/v1/ws/dashboard',
        handleWebSocketMessage,
        () => {
            console.log('Dashboard WebSocket connected');
            updateConnectionStatus(true);
        },
        () => {
            console.log('Dashboard WebSocket disconnected');
            updateConnectionStatus(false);
        }
    );
}

function handleWebSocketMessage(data) {
    console.log('Dashboard message:', data);
    
    switch (data.type) {
        case 'anomaly_detected':
            handleAnomalyAlert(data.data);
            break;
        case 'metric_updated':
            handleMetricUpdate(data.data);
            break;
        case 'model_updated':
            loadDashboardStats(); // Refresh stats
            break;
        default:
            console.log('Unknown message type:', data.type);
    }
}

function handleAnomalyAlert(anomaly) {
    // Show toast notification
    showToast(
        'Anomaly Detected',
        `${anomaly.machine_id}: ${anomaly.metric} - ${anomaly.severity}`,
        'warning'
    );
    
    // Refresh anomaly list
    loadRecentAnomalies();
}

function handleMetricUpdate(metric) {
    // Update specific metric in UI
    // Could update specific cards without full refresh
    console.log('Metric updated:', metric);
}

function updateConnectionStatus(connected) {
    // Update UI to show connection status
    const indicator = document.getElementById('ws-status-indicator');
    if (indicator) {
        if (connected) {
            indicator.classList.remove('disconnected');
            indicator.classList.add('connected');
            indicator.title = 'Real-time updates active';
        } else {
            indicator.classList.remove('connected');
            indicator.classList.add('disconnected');
            indicator.title = 'Reconnecting...';
        }
    }
}

function showToast(title, message, type = 'info') {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'warning' ? 'warning' : 'primary'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <strong>${title}</strong><br>${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    // Add to toast container
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.appendChild(toast);
    
    // Initialize Bootstrap toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove after hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Initialize WebSocket on page load
document.addEventListener('DOMContentLoaded', function() {
    // ... existing initialization ...
    
    // Initialize WebSocket
    initWebSocket();
    
    // REMOVE or comment out polling intervals
    // setInterval(() => {
    //     loadDashboardStats();
    //     loadRecentAnomalies();
    // }, 30000);
});

// Clean up WebSocket on page unload
window.addEventListener('beforeunload', function() {
    if (dashboardWS) {
        dashboardWS.disconnect();
    }
});
</script>

<!-- Add connection status indicator to header -->
<div class="row mb-4">
    <div class="col-12 d-flex align-items-center">
        <h1 class="display-6 me-3">Analytics Dashboard</h1>
        <span id="ws-status-indicator" class="badge disconnected" title="Connecting...">
            <i class="bi bi-circle-fill"></i> Live
        </span>
    </div>
</div>

<!-- Add CSS for status indicator -->
<style>
.badge.connected {
    background-color: #28a745 !important;
}
.badge.disconnected {
    background-color: #6c757d !important;
}
.badge i {
    font-size: 0.5rem;
}
</style>
```

---

## Database Changes

### No Schema Changes Required ✅

The existing database schema already supports all real-time features:

- `energy_consumption_hourly` - Metrics data
- `anomalies` - Anomaly records
- `model_training_history` - Training job tracking
- `baseline_models`, `anomaly_models` - Model storage

### Optional: Event Log Table (Phase 2)

```sql
-- Optional: Track all system events for debugging
CREATE TABLE IF NOT EXISTS system_events (
    event_id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    event_channel VARCHAR(100) NOT NULL,
    event_data JSONB NOT NULL,
    published_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_system_events_type ON system_events(event_type);
CREATE INDEX idx_system_events_published ON system_events(published_at DESC);

-- Convert to hypertable for time-series storage
SELECT create_hypertable('system_events', 'published_at', if_not_exists => TRUE);
```

---

## Testing Strategy

### 🧪 Unit Tests

```bash
# Test WebSocket connection manager
pytest analytics/tests/test_websocket_manager.py

# Test Redis pub/sub
pytest analytics/tests/test_redis_manager.py

# Test event publishing
pytest analytics/tests/test_event_publisher.py
```

### 🔌 Integration Tests

```bash
# Test WebSocket endpoints
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
    -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: test" \
    http://localhost:8001/api/v1/ws/dashboard

# Test Redis pub/sub manually
docker exec -it enms-redis redis-cli -a raptorblingx
PUBLISH anomaly.detected '{"machine_id":"M01","severity":"high"}'
```

### 🌐 Browser Testing

```javascript
// Open browser console and test WebSocket
const ws = new WebSocket('ws://localhost:8001/api/v1/ws/dashboard?client_id=test123');

ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log('Message:', JSON.parse(e.data));
ws.onerror = (e) => console.error('Error:', e);
ws.onclose = () => console.log('Disconnected');

// Send ping
ws.send('ping');
```

### 📊 Load Testing

```bash
# Install wscat for WebSocket testing
npm install -g wscat

# Test multiple connections
for i in {1..10}; do
    wscat -c "ws://localhost:8001/api/v1/ws/dashboard?client_id=load-test-$i" &
done

# Monitor connection count
curl http://localhost:8001/api/v1/health
```

### ✅ Manual Testing Checklist

- [ ] WebSocket connects successfully
- [ ] Dashboard receives real-time updates
- [ ] Anomaly alerts appear as toasts
- [ ] Training progress updates in real-time
- [ ] Connection status indicator works
- [ ] Reconnection works after disconnect
- [ ] Multiple tabs/clients work correctly
- [ ] No memory leaks after extended use
- [ ] Mobile browser compatibility

---

## Rollback Plan

### 🚨 If Issues Occur

1. **Disable WebSocket in Config**
   ```python
   # analytics/config.py
   WEBSOCKET_ENABLED: bool = False
   REDIS_PUBSUB_ENABLED: bool = False
   ```

2. **Restore Polling in UI**
   ```javascript
   // Comment out WebSocket initialization
   // initWebSocket();
   
   // Restore polling
   setInterval(() => {
       loadDashboardStats();
       loadRecentAnomalies();
   }, 30000);
   ```

3. **Restart Service**
   ```bash
   docker-compose restart analytics
   ```

### 📁 Backup Files

```bash
# Backup before starting
cp analytics/main.py analytics/main.py.backup
cp analytics/requirements.txt analytics/requirements.txt.backup
cp analytics/ui/templates/dashboard.html analytics/ui/templates/dashboard.html.backup
```

---

## Success Criteria

### ✅ Feature Checklist

- [ ] WebSocket connections established successfully
- [ ] Real-time dashboard updates working
- [ ] Anomaly alerts pushed to clients instantly
- [ ] Training progress updates in real-time
- [ ] Event-driven architecture operational
- [ ] Redis pub/sub functioning correctly
- [ ] Auto-reconnection working
- [ ] Multiple clients supported
- [ ] No polling intervals remaining
- [ ] Connection status indicator visible
- [ ] Toast notifications working
- [ ] Browser console shows no errors
- [ ] Performance improved (reduced server load)
- [ ] Latency < 1 second for updates

### 📈 Performance Metrics

**Before (Polling):**
- Update latency: 5-30 seconds
- Server requests: ~120-360 requests/hour per client
- Server load: High (constant polling)

**After (WebSocket):**
- Update latency: < 1 second
- Server requests: 2 requests/session (connect + disconnect)
- Server load: Low (event-driven)

### 🎯 Acceptance Criteria

1. **Dashboard loads and connects via WebSocket**
2. **Anomalies appear as toast notifications within 1 second of detection**
3. **Training progress bar updates smoothly without refresh**
4. **Connection status indicator shows correct state**
5. **Multiple browser tabs can connect simultaneously**
6. **Reconnection works after network interruption**
7. **No JavaScript errors in browser console**
8. **REST API endpoints still work for initial data load**

---

## OVOS Integration

### 🎤 Voice Commands (Updated)

```python
# Existing commands still work, plus new real-time features:

"Show me real-time dashboard"
"Are there any new anomalies?"
"What's the training progress?"
"Show me system alerts"
"Connect to live updates"
```

### 📡 API Endpoints (Still Available)

All existing REST endpoints remain functional for OVOS:
- `/api/v1/baseline/*` - Baseline models
- `/api/v1/anomaly/*` - Anomaly detection
- `/api/v1/kpi/*` - KPI calculations
- `/api/v1/model-performance/*` - Training status

### 🔔 Push Notifications to OVOS (Future)

```python
# Potential integration: Publish OVOS-specific events
await redis_manager.publish("ovos.notification", {
    "type": "anomaly_alert",
    "message": "Critical anomaly detected on Machine M03",
    "severity": "critical",
    "timestamp": datetime.utcnow().isoformat()
})
```

---

## Implementation Timeline

### 📅 Estimated Duration: 4-6 Hours

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Phase 1** | 30 min | Install dependencies, update config, create Redis manager |
| **Phase 2** | 1 hour | Create WebSocket manager and routes |
| **Phase 3** | 1 hour | Create event publisher/subscriber |
| **Phase 4** | 30 min | Integrate into main.py |
| **Phase 5** | 30 min | Add event publishing to existing routes |
| **Phase 6** | 1.5 hours | Create frontend WebSocket client and update UIs |
| **Testing** | 1 hour | Integration testing and verification |

**Total:** ~6 hours for complete implementation

---

## Next Steps After Session 5

### Phase 4 - Session 6: Advanced Analytics (Planned)

- Machine learning model optimization
- Advanced forecasting algorithms
- Predictive maintenance models
- Energy consumption predictions
- Efficiency recommendations

### Phase 5: Security & Authentication (Planned)

- JWT authentication
- Role-based access control
- API key management
- Audit logging
- Rate limiting

---

## Quick Reference Commands

### Start Implementation

```bash
# 1. Update dependencies
cd /home/ubuntu/enms/analytics
# Edit requirements.txt to add redis==5.0.1 and websockets==12.0

# 2. Rebuild container
cd /home/ubuntu/enms
docker-compose build analytics
docker-compose up -d analytics

# 3. Check logs
docker-compose logs -f analytics

# 4. Test WebSocket
# Open browser to http://localhost:8080/api/analytics/ui/
```

### Verify Installation

```bash
# Check Redis connection
docker exec -it enms-analytics python3 -c "import redis; print('Redis imported successfully')"

# Check WebSocket support
docker exec -it enms-analytics python3 -c "import websockets; print('WebSocket imported successfully')"

# Test Redis pub/sub
docker exec -it enms-redis redis-cli -a raptorblingx PUBLISH test "Hello WebSocket"
```

### Debugging

```bash
# Check WebSocket connections
docker exec -it enms-analytics python3 -c "
from services.websocket_manager import connection_manager
print(connection_manager.get_connections_by_type())
"

# Monitor Redis pub/sub
docker exec -it enms-redis redis-cli -a raptorblingx
PSUBSCRIBE '*'

# Check analytics logs
docker-compose logs -f analytics | grep -i websocket
```

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-15 | EnMS Team | Initial session plan created |

---

## Conclusion

This session transforms the EnMS Analytics Service from a polling-based system to a modern, event-driven architecture with real-time updates. The implementation maintains backward compatibility while adding powerful new capabilities for instant feedback and live monitoring.

**Ready to implement?** Follow the steps in order, test thoroughly, and verify each phase before moving to the next.

**Questions?** Refer to the [Architecture Design](#architecture-design) section for detailed explanations of how components interact.

---

*End of Phase 4 Session 5 Implementation Plan*
