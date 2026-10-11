# -*- coding: utf-8 -*-
"""
ROUTER: TRUY VẤN ĐỒ THỊ TRI THỨC KHÔNG GIAN (SPATIAL KG ROUTE)
"""
from typing import Optional
from fastapi import APIRouter, Query
from src.graph.graph_retriever import get_graph_retriever

router = APIRouter(prefix="/api/v1/kg", tags=["Đồ thị Tri thức (Spatial KG)"])
retriever = get_graph_retriever()


@router.get("/places/nearby")
def get_nearby_places(
    place_id: str = Query(..., examples=["place_8875"], description="ID của địa điểm xuất phát"),
    category: Optional[str] = Query(None, examples=["Restaurant"], description="Lọc danh mục: Restaurant, Hotel, Attraction"),
    max_distance_km: float = Query(1.5, examples=[1.2], description="Bán kính tìm kiếm (km)"),
    limit: int = Query(5, examples=[5])
):
    """Tra cứu các địa điểm lân cận qua cạnh NEAR_BY trong Đồ thị."""
    results = retriever.find_nearby_places(
        place_id_or_name=place_id,
        category=category,
        max_distance_km=max_distance_km,
        limit=limit
    )
    return {
        "origin_place_id": place_id,
        "max_distance_km": max_distance_km,
        "count": len(results),
        "nearby_places": results
    }


@router.get("/dishes/search")
def search_places_by_dish(
    dish_name: str = Query(..., examples=["Bún bò Huế"], description="Tên món ăn đặc sản"),
    limit: int = Query(5, examples=[5])
):
    """Tra cứu các quán ăn phục vụ món đặc sản qua cạnh SERVES."""
    results = retriever.find_places_by_dish(dish_name=dish_name, locality="Thành phố Huế", limit=limit)
    return {
        "dish_name": dish_name,
        "count": len(results),
        "places": results
    }
