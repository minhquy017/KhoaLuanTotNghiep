# -*- coding: utf-8 -*-
"""
SCHEMAS CHO LẬP LỊCH TRÌNH DU LỊCH (ITINERARY SCHEMAS)
"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class ItineraryRequest(BaseModel):
    num_days: int = Field(1, ge=1, le=3, examples=[1], description="Số ngày lưu trú (1 - 3 ngày)")
    trip_type: Optional[str] = Field("Couples", examples=["Couples"], description="Loại hình: Couples, Family, Friends, Solo")
    preferred_dishes: Optional[List[str]] = Field(
        default=["Bún bò Huế", "Cơm hến", "Bánh bèo"],
        examples=[["Bún bò Huế", "Bánh bèo"]],
        description="Danh sách món ăn ưu tiên thưởng thức"
    )


class ItineraryResponse(BaseModel):
    status: str
    locality: str
    num_days: int
    trip_type: str
    itinerary_data: Dict[str, Any]
    formatted_markdown: str
