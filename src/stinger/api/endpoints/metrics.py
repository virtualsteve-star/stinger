"""
Metrics endpoint for API monitoring.
"""

from fastapi import APIRouter, Query
from fastapi.responses import PlainTextResponse, JSONResponse

from stinger.api import metrics

router = APIRouter()


@router.get("/metrics")
async def get_metrics(format: str = Query("json", enum=["json", "prometheus"])):
    """
    Get current metrics for monitoring.
    
    Formats:
    - json: Detailed metrics in JSON format
    - prometheus: Prometheus text format for scraping
    """
    if format == "prometheus":
        return PlainTextResponse(
            content=metrics.export_metrics("prometheus"),
            media_type="text/plain; version=0.0.4"
        )
    else:
        return JSONResponse(
            content=metrics.get_metrics().get_metrics_summary()
        )