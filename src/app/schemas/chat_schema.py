# -*- coding: utf-8 -*-
"""
SCHEMAS CHO TRỢ LÝ HỎI ĐÁP (CHAT SCHEMAS)
"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: Optional[str] = Field("", examples=["Tôi vừa tham quan Đại Nội xong, muốn ăn bún bò gần đây thì đi quán nào?"])
    locality: Optional[str] = Field("Thành phố Huế", examples=["Thành phố Huế"])
    user_lat: Optional[float] = Field(None, examples=[16.4674])
    user_lng: Optional[float] = Field(None, examples=[107.5905])
    preferences: Optional[Dict[str, Any]] = Field(None, description="Hồ sơ gu du lịch cá nhân hóa của du khách")
    image_base64: Optional[str] = Field(None, description="Dữ liệu ảnh dạng chuỗi Base64 (hỗ trợ JPG/PNG) để AI nhận diện thị giác")
    # --- Trí nhớ phiên chat đa lượt ---
    session_id: Optional[str] = Field(None, max_length=80, examples=["session_1741165890"])
    history: Optional[List[Dict[str, Any]]] = Field(
        None,
        max_length=12,
        description="Các tin nhắn gần nhất [{role: 'user'|'assistant', text}] (server chỉ dùng 2 lượt cuối, đã cắt gọn)"
    )
    session_context: Optional[Dict[str, Any]] = Field(
        None,
        description="Mốc ngữ cảnh do server trả về ở lượt trước (anchor_place_id, anchor_dish, topic_domain, turn_count)"
    )


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
    navigation: Optional[Dict[str, Any]] = None
    graph_trace: Optional[List[Dict[str, Any]]] = None  # XAI: chuỗi suy luận minh bạch
    session_context: Optional[Dict[str, Any]] = None    # Mốc ngữ cảnh mới, client gửi lại ở lượt sau
