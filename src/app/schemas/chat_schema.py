# -*- coding: utf-8 -*-
"""
SCHEMAS CHO TRỢ LÝ HỎI ĐÁP (CHAT SCHEMAS)
"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(..., examples=["Tôi vừa tham quan Đại Nội xong, muốn ăn bún bò gần đây thì đi quán nào?"])
    locality: Optional[str] = Field("Thành phố Huế", examples=["Thành phố Huế"])


class PlaceItem(BaseModel):
    node_id: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rating: Optional[float] = 4.5
    address: Optional[str] = ""


class ChatResponse(BaseModel):
    status: str
    query: str
    answer: str
    route_taken: str
    confidence_score: float
    matched_places: List[Dict[str, Any]]
