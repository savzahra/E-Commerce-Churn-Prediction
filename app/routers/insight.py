from fastapi import APIRouter, Query
from typing import Optional

from app.services import insight_service

router = APIRouter(prefix="/api/insight", tags=["insight"])


@router.get("/summary", summary="Summary statistik prediksi")
async def get_summary(
    gender: Optional[str] = Query(None),
    city_tier: Optional[int] = Query(None),
    marital_status: Optional[str] = Query(None),
    tenure_min: Optional[float] = Query(None),
    tenure_max: Optional[float] = Query(None),
):
    return insight_service.get_summary(
        gender=gender,
        city_tier=city_tier,
        marital_status=marital_status,
        tenure_min=tenure_min,
        tenure_max=tenure_max,
    )


@router.get("/charts", summary="Data chart dengan filter")
async def get_charts(
    gender: Optional[str] = Query(None, description="Male / Female"),
    city_tier: Optional[int] = Query(None, description="1 / 2 / 3"),
    marital_status: Optional[str] = Query(None, description="Single / Married / Divorced"),
    tenure_min: Optional[float] = Query(None, description="Minimum tenure (bulan)"),
    tenure_max: Optional[float] = Query(None, description="Maximum tenure (bulan)"),
):
    return insight_service.get_chart_data(
        gender=gender,
        city_tier=city_tier,
        marital_status=marital_status,
        tenure_min=tenure_min,
        tenure_max=tenure_max,
    )


@router.delete("/clear", summary="Reset semua data prediksi")
async def clear_data():
    insight_service.clear_store()
    return {"message": "Data berhasil dihapus"}
