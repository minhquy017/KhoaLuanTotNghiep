# -*- coding: utf-8 -*-
"""
ROUTER: LẬP LỊCH TRÌNH DU LỊCH (ITINERARY ROUTE)
"""
from fastapi import APIRouter, HTTPException
from src.app.schemas.itinerary_schema import ItineraryRequest, ItineraryResponse
from src.planner.itinerary_planner import get_itinerary_planner

router = APIRouter(prefix="/api/v1", tags=["Lập Lịch trình (Tour Planner)"])
planner = get_itinerary_planner()


@router.post("/itinerary", response_model=ItineraryResponse)
def generate_itinerary(req: ItineraryRequest):
    """
    Tự động Lập Lịch trình Tour du lịch (1 - 3 Ngày) tại Huế:
    - Phân cụm không gian (Bờ Bắc, Bờ Nam, Ngoại ô).
    - Tự động ghép quán ăn gần nhất (< 1.5km) qua cạnh NEAR_BY và SERVES.
    - Trả về cấu trúc JSON từng buổi kèm tọa độ GPS và mảng Polyline để app Hue-S tự render lên bản đồ.
    """
    try:
        plan_data = planner.plan_itinerary(
            num_days=req.num_days,
            preferred_dishes=req.preferred_dishes,
            trip_type=req.trip_type or "Couples"
        )
        md_text = planner.format_itinerary_markdown(plan_data)

        return ItineraryResponse(
            status="success",
            locality="Thành phố Huế",
            num_days=req.num_days,
            trip_type=req.trip_type or "Couples",
            itinerary_data=plan_data,
            formatted_markdown=md_text
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lập lịch trình: {str(e)}")
