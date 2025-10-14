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

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from datetime import datetime
import logging
import sys

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

# Register API routes with prefix
app.include_router(baseline_router, prefix=settings.API_PREFIX)
app.include_router(anomaly_router, prefix=settings.API_PREFIX)
app.include_router(kpi_router, prefix=settings.API_PREFIX)
app.include_router(machines_router, prefix=settings.API_PREFIX)
app.include_router(forecast_router, prefix=settings.API_PREFIX)


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
            query = "SELECT COUNT(*) FROM baseline_models"
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
        "active_machines": active_machines,
        "baseline_models": baseline_models,
        "recent_anomalies": recent_anomalies,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return health_data


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