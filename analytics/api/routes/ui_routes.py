"""
Analytics UI Routes
===================
FastAPI routes for serving the analytics dashboard UI.

These routes serve Jinja2 templates for:
- Dashboard overview
- Baseline regression training
- Anomaly viewer
- KPI visualization
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/ui", tags=["UI"])

# Configure Jinja2 templates
templates = Jinja2Templates(directory="/app/ui/templates")


@router.get("/", response_class=HTMLResponse, name="ui_dashboard")
async def dashboard(request: Request):
    """
    Analytics Dashboard - Main UI landing page
    
    Shows:
    - Service status overview
    - Recent anomalies
    - Quick action buttons
    - System information
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/baseline", response_class=HTMLResponse, name="ui_baseline")
async def baseline_ui(request: Request):
    """
    Baseline Training UI
    
    Provides interface for:
    - Machine selection
    - Date range selection
    - Driver (feature) selection
    - Model training execution
    - Results visualization (R², coefficients, charts)
    """
    return templates.TemplateResponse("baseline.html", {"request": request})


@router.get("/anomaly", response_class=HTMLResponse, name="ui_anomaly")
async def anomaly_ui(request: Request):
    """
    Anomaly Viewer UI
    
    Features:
    - Anomaly filtering (machine, time, severity, status)
    - Detection trigger
    - Anomaly resolution
    - Severity indicators
    """
    return templates.TemplateResponse("anomaly.html", {"request": request})


@router.get("/kpi", response_class=HTMLResponse, name="ui_kpi")
async def kpi_ui(request: Request):
    """
    KPI Dashboard UI
    
    Displays:
    - All 5 KPIs (SEC, Peak Demand, Load Factor, Cost, Carbon)
    - Interactive charts
    - Time range selection
    - Export functionality
    """
    return templates.TemplateResponse("kpi.html", {"request": request})


@router.get("/forecast", response_class=HTMLResponse, name="ui_forecast")
async def forecast_ui(request: Request):
    """
    Forecast UI
    
    Features:
    - ARIMA & Prophet model training
    - Short/medium/long-term forecasting
    - Confidence interval visualization
    - Optimal load scheduling
    - Model status tracking
    """
    return templates.TemplateResponse("forecast.html", {"request": request})


# Health check for UI service
@router.get("/health", response_class=HTMLResponse)
async def ui_health(request: Request):
    """UI service health check"""
    return HTMLResponse(content="<h1>Analytics UI is healthy</h1>", status_code=200)