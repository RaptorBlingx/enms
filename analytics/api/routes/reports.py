"""
Reports API Router
==================
Endpoints for generating and retrieving reports.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Optional
from datetime import datetime
import logging

from services.report_service import ReportService
from reports.monthly_enpi_report import MonthlyEnPIReport
from reports.chart_generator import ReportChartGenerator

logger = logging.getLogger(__name__)

router = APIRouter()
report_service = ReportService()
chart_generator = ReportChartGenerator()


@router.get("/types")
async def get_report_types():
    """
    Get available report types.
    
    Returns:
        List of report type metadata
    """
    return {
        "success": True,
        "data": [
            {
                "type": "monthly_enpi",
                "name": "Monthly Energy Performance Report",
                "description": "Comprehensive monthly report with EnPIs, machine consumption, and anomalies",
                "format": "PDF",
                "parameters": {
                    "year": "Required - Report year (integer)",
                    "month": "Required - Report month 1-12 (integer)",
                    "factory_id": "Optional - Filter by factory ID (integer)"
                }
            }
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/generate")
async def generate_report(
    report_type: str = Query(..., description="Type of report to generate"),
    year: int = Query(..., description="Report year"),
    month: int = Query(..., ge=1, le=12, description="Report month (1-12)"),
    factory_id: Optional[int] = Query(None, description="Optional factory filter")
):
    """
    Generate a report and return PDF.
    
    Args:
        report_type: Type of report (currently only 'monthly_enpi')
        year: Year for the report
        month: Month for the report (1-12)
        factory_id: Optional factory filter
    
    Returns:
        PDF file stream
    """
    try:
        if report_type != "monthly_enpi":
            raise HTTPException(status_code=400, detail=f"Unsupported report type: {report_type}")
        
        logger.info(f"Generating {report_type} report for {year}-{month:02d}, factory={factory_id}")
        
        # Fetch report data
        data = await report_service.generate_monthly_enpi_data(year, month, factory_id)
        
        # Generate charts
        if data.get('machines'):
            machine_chart = chart_generator.generate_machine_consumption_chart(data['machines'])
            data['machine_chart'] = machine_chart
        
        if data.get('daily_data'):
            daily_chart = chart_generator.generate_daily_trend_chart(data['daily_data'])
            data['daily_trend_chart'] = daily_chart
        
        # Generate PDF
        report = MonthlyEnPIReport(data)
        pdf_buffer = report.generate()
        
        # Cleanup
        chart_generator.cleanup()
        
        # Return PDF
        headers = {
            'Content-Disposition': f'attachment; filename="{report.filename}"'
        }
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers=headers
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/preview")
async def preview_report_data(
    report_type: str = Query(..., description="Type of report"),
    year: int = Query(..., description="Report year"),
    month: int = Query(..., ge=1, le=12, description="Report month (1-12)"),
    factory_id: Optional[int] = Query(None, description="Optional factory filter")
):
    """
    Get report data as JSON (preview without generating PDF).
    
    Args:
        report_type: Type of report
        year: Year for the report
        month: Month for the report (1-12)
        factory_id: Optional factory filter
    
    Returns:
        JSON data that would be used in the report
    """
    try:
        if report_type != "monthly_enpi":
            raise HTTPException(status_code=400, detail=f"Unsupported report type: {report_type}")
        
        logger.info(f"Previewing {report_type} data for {year}-{month:02d}, factory={factory_id}")
        
        # Fetch report data
        data = await report_service.generate_monthly_enpi_data(year, month, factory_id)
        
        # Remove chart buffers from response (not JSON serializable)
        data.pop('machine_chart', None)
        data.pop('daily_trend_chart', None)
        
        return {
            "success": True,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error previewing report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to preview report: {str(e)}")
