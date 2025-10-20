"""
EnMS Analytics Service - Main Application
==========================================
FastAPI application with ML-powered analytics for energy management.

Phase 3 Session 3: Added UI and Scheduler
- Analytics Dashboard UI
- APScheduler for automated jobs
- Job status tracking

Author: EnMS Team
Phase: 3 - Analytics & ML (Session 3)
"""

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from datetime import datetime
import logging
import sys
import asyncio
import json

from config import settings
from database import db

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


# ============================================================================
# Utility Functions
# ============================================================================

async def cleanup_stuck_training_jobs() -> int:
    """
    Clean up training jobs that are stuck in pending/running state.
    
    Jobs are considered stuck if they've been in pending/running state
    for more than 30 minutes (configurable).
    
    Returns:
        Number of jobs cleaned up
    """
    try:
        pool = db.pool
        async with pool.acquire() as conn:
            # Mark stuck jobs as failed
            result = await conn.execute("""
                UPDATE model_training_history
                SET training_status = 'failed',
                    training_end = NOW(),
                    error_message = 'Job timed out - exceeded 30 minute limit'
                WHERE training_status IN ('pending', 'running')
                AND training_start < NOW() - INTERVAL '30 minutes'
            """)
            
            # Extract count from result string like "UPDATE 5"
            count = int(result.split()[-1]) if result and result.split() else 0
            return count
            
    except Exception as e:
        logger.error(f"Error cleaning up stuck jobs: {e}", exc_info=True)
        return 0


# ============================================================================
# Lifespan Management
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan (startup and shutdown).
    """
    # Startup
    logger.info("=" * 70)
    logger.info(f"🚀 Starting {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}")
    logger.info("=" * 70)
    
    try:
        # Connect to database
        logger.info("Connecting to database...")
        await db.connect()
        
        # Test database connectivity
        is_healthy = await db.health_check()
        if not is_healthy:
            raise Exception("Database health check failed")
        logger.info("✓ Database connected and healthy")
        
        # Connect to Redis and start event subscriber (Phase 4 Session 5)
        if settings.REDIS_PUBSUB_ENABLED:
            logger.info("Connecting to Redis...")
            from services.redis_manager import redis_manager
            await redis_manager.connect()
            logger.info("✓ Redis connected")
            
            logger.info("Starting event subscriber...")
            from services.event_subscriber import event_subscriber
            await event_subscriber.start()
            logger.info("✓ Event subscriber started")
        else:
            logger.info("⚠ Redis Pub/Sub is disabled in configuration")
        
        # Clean up stuck training jobs
        logger.info("Cleaning up stuck training jobs...")
        try:
            stuck_count = await cleanup_stuck_training_jobs()
            if stuck_count > 0:
                logger.info(f"✓ Cleaned up {stuck_count} stuck training job(s)")
            else:
                logger.info("✓ No stuck training jobs found")
        except Exception as e:
            logger.warning(f"Failed to cleanup stuck jobs: {e}")
        
        # Initialize scheduler
        if settings.SCHEDULER_ENABLED:
            logger.info("Starting scheduler...")
            from scheduler.scheduler import scheduler
            scheduler.start()
            logger.info("✓ Scheduler started")
        else:
            logger.info("⚠ Scheduler is disabled in configuration")
        
        logger.info("=" * 70)
        logger.info(f"✓ {settings.SERVICE_NAME} started successfully!")
        logger.info(f"📡 API available at: http://0.0.0.0:{settings.API_PORT}")
        logger.info(f"📊 API docs at: http://0.0.0.0:{settings.API_PORT}/docs")
        logger.info(f"📈 UI at: http://0.0.0.0:{settings.API_PORT}/ui/")
        logger.info(f"🗄️  Database: {settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"Failed to start {settings.SERVICE_NAME}: {e}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.SERVICE_NAME}...")
    try:
        # Stop scheduler
        if settings.SCHEDULER_ENABLED:
            from scheduler.scheduler import scheduler
            scheduler.stop()
            logger.info("✓ Scheduler stopped")
        
        # Disconnect Redis (Phase 4 Session 5)
        if settings.REDIS_PUBSUB_ENABLED:
            from services.redis_manager import redis_manager
            await redis_manager.disconnect()
            logger.info("✓ Redis disconnected")
        
        # Disconnect from database
        await db.disconnect()
        logger.info("✓ Database disconnected")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    
    logger.info(f"{settings.SERVICE_NAME} shut down successfully")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title=settings.SERVICE_NAME,
    description="ML-powered analytics service for industrial energy management",
    version=settings.SERVICE_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# ============================================================================
# Middleware
# ============================================================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = datetime.utcnow()
    
    # Log request
    logger.debug(f"→ {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    duration = (datetime.utcnow() - start_time).total_seconds()
    logger.debug(
        f"← {request.method} {request.url.path} "
        f"[{response.status_code}] ({duration:.3f}s)"
    )
    
    return response


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "detail": str(exc) if settings.LOG_LEVEL == "DEBUG" else None
        }
    )


# ============================================================================
# Static Files & UI Routes
# ============================================================================

# Mount static files for UI
try:
    app.mount("/ui/static", StaticFiles(directory="/app/ui/static"), name="static")
    logger.info("✓ Static files mounted at /ui/static")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

# Import and register UI routes
try:
    from api.routes.ui_routes import router as ui_router
    app.include_router(ui_router)
    logger.info("✓ UI routes registered")
except Exception as e:
    logger.warning(f"Could not register UI routes: {e}")


# ============================================================================
# API Routes
# ============================================================================

# Import API routers
from api.routes.baseline import router as baseline_router
from api.routes.anomaly import router as anomaly_router
from api.routes.kpi import router as kpi_router
from api.routes.machines import router as machines_router
from api.routes.forecast import router as forecast_router
from api.routes.timeseries import router as timeseries_router
from api.routes.sankey import router as sankey_router
from api.routes.heatmap import router as heatmap_router
from api.routes.comparison import router as comparison_router
from api.routes.model_performance import router as model_performance_router
from api.routes.stats import router as stats_router
from api.routes.production import router as production_router
from api.routes.compare import router as compare_router
from api.routes.ovos import router as ovos_router  # OVOS Integration
from api.websocket_routes import router as websocket_router  # Phase 4 Session 5

# Register API routes with prefix
app.include_router(baseline_router, prefix=settings.API_PREFIX)
app.include_router(anomaly_router, prefix=settings.API_PREFIX)
app.include_router(kpi_router, prefix=settings.API_PREFIX)
app.include_router(machines_router, prefix=settings.API_PREFIX)
app.include_router(forecast_router, prefix=settings.API_PREFIX)
app.include_router(timeseries_router, prefix=settings.API_PREFIX)
app.include_router(sankey_router, prefix=settings.API_PREFIX)
app.include_router(heatmap_router, prefix=settings.API_PREFIX)
app.include_router(comparison_router, prefix=settings.API_PREFIX)
app.include_router(model_performance_router, prefix=settings.API_PREFIX, tags=["Model Performance"])
app.include_router(stats_router, prefix=settings.API_PREFIX)
app.include_router(production_router, prefix=settings.API_PREFIX)
app.include_router(compare_router, prefix=settings.API_PREFIX)
app.include_router(ovos_router, prefix=settings.API_PREFIX)  # OVOS Integration
app.include_router(websocket_router, prefix=settings.API_PREFIX)  # Phase 4 Session 5: WebSocket Routes


# ============================================================================
# Root Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - service information"""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "status": "healthy",
        "endpoints": {
            "docs": "/docs",
            "ui": "/ui/",
            "api": settings.API_PREFIX,
            "health": f"{settings.API_PREFIX}/health"
        }
    }


@app.get(f"{settings.API_PREFIX}/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns service status, database connectivity, scheduler status, and key statistics.
    """
    # Check database
    db_healthy = await db.health_check()
    db_status = "connected" if db_healthy else "disconnected"
    
    # Check scheduler
    scheduler_info = {"enabled": settings.SCHEDULER_ENABLED, "running": False}
    if settings.SCHEDULER_ENABLED:
        try:
            from scheduler.scheduler import scheduler
            scheduler_info = scheduler.get_status()
        except Exception as e:
            logger.error(f"Error getting scheduler status: {e}")
    
    # Get statistics for portal dashboard
    active_machines = 0
    baseline_models = 0
    recent_anomalies = 0
    
    try:
        async with db.pool.acquire() as conn:
            # Count active machines (machines with data in last 24 hours)
            query = """
                SELECT COUNT(DISTINCT machine_id) 
                FROM energy_readings 
                WHERE time > NOW() - INTERVAL '24 hours'
            """
            active_machines = await conn.fetchval(query)
            
            # Count baseline models
            query = "SELECT COUNT(*) FROM energy_baselines"
            baseline_models = await conn.fetchval(query)
            
            # Count recent anomalies (last 24 hours)
            query = """
                SELECT COUNT(*) 
                FROM anomalies 
                WHERE detected_at > NOW() - INTERVAL '24 hours'
            """
            recent_anomalies = await conn.fetchval(query)
        
    except Exception as e:
        logger.error(f"Error fetching health statistics: {e}")
    
    health_data = {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "status": "healthy" if db_healthy else "degraded",
        "database": {
            "status": db_status,
            "name": settings.DATABASE_NAME,
            "host": settings.DATABASE_HOST,
            "pool_size": db.pool.get_size() if db.pool else 0
        },
        "scheduler": scheduler_info,
        "features": [
            "baseline_regression",
            "anomaly_detection",
            "kpi_calculation",
            "energy_forecasting",
            "time_series_analytics",
            "sankey_energy_flow",
            "anomaly_heatmap",
            "machine_comparison",
            "model_performance_tracking"  # ✅ Phase 4 Session 4
        ],
        "active_machines": active_machines,
        "baseline_models": baseline_models,
        "recent_anomalies": recent_anomalies,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return health_data


@app.get(f"{settings.API_PREFIX}/stats/system")
async def system_statistics():
    """
    Get detailed system statistics for the portal dashboard.
    
    Returns comprehensive real-time operational metrics:
    - Total energy readings and consumption
    - Data ingestion rates
    - Cost and carbon footprint
    - Peak power and efficiency
    - System uptime and health
    """
    try:
        async with db.pool.acquire() as conn:
            # Total energy readings
            total_readings = await conn.fetchval(
                "SELECT COUNT(*) FROM energy_readings"
            )
            
            # Total energy consumption (kWh)
            total_energy = await conn.fetchval(
                """
                SELECT COALESCE(SUM(energy_kwh), 0)::INTEGER 
                FROM energy_readings
                """
            )
            
            # Data rate: count readings in last minute
            data_rate = await conn.fetchval(
                """
                SELECT COUNT(*) 
                FROM energy_readings 
                WHERE time > NOW() - INTERVAL '1 minute'
                """
            )
            
            # Readings per minute (average from last hour)
            readings_per_minute = await conn.fetchval(
                """
                SELECT COALESCE(COUNT(*) / 60, 0)::INTEGER
                FROM energy_readings 
                WHERE time > NOW() - INTERVAL '1 hour'
                """
            )
            
            # Energy per hour (average from last 24 hours)
            energy_per_hour = await conn.fetchval(
                """
                SELECT COALESCE(SUM(energy_kwh) / 24, 0)::INTEGER
                FROM energy_readings 
                WHERE time > NOW() - INTERVAL '24 hours'
                """
            )
            
            # Peak power in last 24 hours (kW)
            peak_power = await conn.fetchval(
                """
                SELECT COALESCE(MAX(power_kw), 0)::INTEGER
                FROM energy_readings 
                WHERE time > NOW() - INTERVAL '24 hours'
                """
            )
            
            # Average power (kW)
            avg_power = await conn.fetchval(
                """
                SELECT COALESCE(AVG(power_kw), 0)::INTEGER
                FROM energy_readings 
                WHERE time > NOW() - INTERVAL '24 hours'
                """
            )
            
            # Estimated cost (assuming $0.12 per kWh)
            estimated_cost = round(total_energy * 0.12, 2) if total_energy else 0
            
            # Cost per day (last 24h)
            cost_per_day = await conn.fetchval(
                """
                SELECT COALESCE(SUM(energy_kwh) * 0.12, 0)::NUMERIC(10,2)
                FROM energy_readings 
                WHERE time > NOW() - INTERVAL '24 hours'
                """
            )
            
            # Carbon footprint (kg CO2) - assuming 0.5 kg CO2 per kWh
            carbon_footprint = round(total_energy * 0.5, 2) if total_energy else 0
            
            # Carbon per day
            carbon_per_day = await conn.fetchval(
                """
                SELECT COALESCE(SUM(energy_kwh) * 0.5, 0)::NUMERIC(10,2)
                FROM energy_readings 
                WHERE time > NOW() - INTERVAL '24 hours'
                """
            )
            
            # Total anomalies detected
            total_anomalies = await conn.fetchval(
                "SELECT COUNT(*) FROM anomalies"
            )
            
            # Active machines today
            active_machines_today = await conn.fetchval(
                """
                SELECT COUNT(DISTINCT machine_id) 
                FROM energy_readings 
                WHERE time > NOW() - INTERVAL '24 hours'
                """
            )
            
            # Calculate uptime (days since first reading)
            first_reading_date = await conn.fetchval(
                "SELECT MIN(time) FROM energy_readings"
            )
            
            uptime_days = 0
            uptime_percent = 99.7
            
            if first_reading_date:
                from datetime import timezone
                now_utc = datetime.now(timezone.utc)
                if first_reading_date.tzinfo is None:
                    first_reading_date = first_reading_date.replace(tzinfo=timezone.utc)
                delta = now_utc - first_reading_date
                uptime_days = delta.days
                
                # Calculate uptime percentage
                expected_readings = 7 * 60 * 60 * 24 * uptime_days
                if expected_readings > 0:
                    uptime_percent = min(99.9, (total_readings / expected_readings) * 100)
            
            # Power efficiency (current vs peak)
            efficiency = round((avg_power / peak_power * 100), 1) if peak_power > 0 else 0
            
            return {
                # Core metrics
                "total_readings": total_readings or 0,
                "total_energy": total_energy or 0,
                "data_rate": data_rate or 0,
                "uptime_days": uptime_days,
                "uptime_percent": round(uptime_percent, 1),
                
                # Rates
                "readings_per_minute": readings_per_minute or 0,
                "energy_per_hour": energy_per_hour or 0,
                
                # Power metrics
                "peak_power": peak_power or 0,
                "avg_power": avg_power or 0,
                "efficiency": efficiency,
                
                # Cost and carbon
                "estimated_cost": float(estimated_cost),
                "cost_per_day": float(cost_per_day) if cost_per_day else 0,
                "carbon_footprint": float(carbon_footprint),
                "carbon_per_day": float(carbon_per_day) if carbon_per_day else 0,
                
                # System health
                "total_anomalies": total_anomalies or 0,
                "active_machines_today": active_machines_today or 0,
                
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error fetching system statistics: {e}")
        return {
            "total_readings": 0,
            "total_energy": 0,
            "data_rate": 0,
            "uptime_days": 0,
            "uptime_percent": 0,
            "readings_per_minute": 0,
            "energy_per_hour": 0,
            "peak_power": 0,
            "avg_power": 0,
            "efficiency": 0,
            "estimated_cost": 0,
            "cost_per_day": 0,
            "carbon_footprint": 0,
            "carbon_per_day": 0,
            "total_anomalies": 0,
            "active_machines_today": 0,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@app.get(f"{settings.API_PREFIX}/scheduler/status")
async def scheduler_status():
    """
    Get detailed scheduler status and job information.
    
    Returns:
        - Scheduler running status
        - List of registered jobs
        - Next run times for each job
    """
    if not settings.SCHEDULER_ENABLED:
        return {
            "enabled": False,
            "message": "Scheduler is disabled in configuration"
        }
    
    try:
        from scheduler.scheduler import scheduler
        return scheduler.get_status()
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        return {
            "enabled": True,
            "error": str(e)
        }


@app.post(f"{settings.API_PREFIX}/scheduler/trigger/{{job_id}}")
async def trigger_job(job_id: str):
    """
    Manually trigger a scheduled job to run immediately.
    
    Args:
        job_id: One of 'baseline_retrain', 'anomaly_detect', 'kpi_calculate'
    
    Returns:
        Success status and message
    """
    if not settings.SCHEDULER_ENABLED:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Scheduler is disabled"
            }
        )
    
    valid_jobs = ['baseline_retrain', 'anomaly_detect', 'kpi_calculate']
    if job_id not in valid_jobs:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": f"Invalid job_id. Must be one of: {valid_jobs}"
            }
        )
    
    try:
        from scheduler.scheduler import scheduler
        success = scheduler.trigger_job(job_id)
        
        if success:
            return {
                "success": True,
                "message": f"Job '{job_id}' triggered successfully"
            }
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": f"Job '{job_id}' not found"
                }
            )
    except Exception as e:
        logger.error(f"Error triggering job {job_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": str(e)
            }
        )


# ============================================================================
# WebSocket Endpoint for Real-Time Updates
# ============================================================================

# Store active WebSocket connections
active_connections: list[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time system statistics updates.
    
    Pushes live updates every 5 seconds to all connected clients.
    Sends anomaly alerts immediately when detected.
    """
    await websocket.accept()
    active_connections.append(websocket)
    
    logger.info(f"🔌 WebSocket client connected. Total connections: {len(active_connections)}")
    
    try:
        while True:
            # Fetch latest statistics
            stats = await system_statistics()
            
            # Send stats update
            await websocket.send_json({
                "type": "stats_update",
                "stats": stats,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Wait 5 seconds before next update
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"🔌 WebSocket client disconnected. Total connections: {len(active_connections)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)


async def broadcast_anomaly(anomaly_data: dict):
    """
    Broadcast anomaly detection to all connected WebSocket clients.
    
    Called by the anomaly detection scheduler job.
    """
    if not active_connections:
        return
    
    message = {
        "type": "anomaly_detected",
        "anomaly": anomaly_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Send to all connected clients
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except Exception as e:
            logger.error(f"Error broadcasting to client: {e}")
            disconnected.append(connection)
    
    # Clean up disconnected clients
    for connection in disconnected:
        active_connections.remove(connection)


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.API_PORT,
        reload=settings.LOG_LEVEL == "DEBUG"
    )