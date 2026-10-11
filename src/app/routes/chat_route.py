# -*- coding: utf-8 -*-
"""
ROUTER: TRỢ LÝ HỎI ĐÁP DU LỊCH (CHAT ROUTE)
"""
from fastapi import APIRouter, HTTPException
from src.app.schemas.chat_schema import ChatRequest, ChatResponse
from src.rag.agent_graph import get_tourism_agent

router = APIRouter(prefix="/api/v1", tags=["Trợ lý Hỏi đáp (Chatbot)"])
agent = get_tourism_agent()


@router.post("/chat", response_model=ChatResponse)
def chat_assistant(req: ChatRequest):
    """
    Hỏi đáp du lịch thông minh:
    - Bóc tách thực thể và tra cứu Đồ thị Không gian (Spatial KG).
    - Đọc review thực tế từ Kho Vector ChromaDB.
    - Router phân luồng: Tự tin nội bộ (Local) hoặc Web Search Fallback.
    - Trả về câu trả lời tự nhiên + tọa độ GPS các địa điểm liên quan để vẽ lên bản đồ (Hue-S / Web).
    """
    try:
        initial_state = {
            "query": req.query,
            "locality": req.locality or "Thành phố Huế",
            "target_dish": None,
            "target_place": None,
            "matched_places": [],
            "nearby_map": {},
            "dishes_map": {},
            "reviews": [],
            "web_results": [],
            "confidence_score": 0.0,
            "route_taken": "local_knowledge",
            "formatted_context": "",
            "final_answer": ""
        }
        res = agent.invoke(initial_state)

        # Chuẩn hóa danh sách địa điểm trả về
        clean_places = []
        for p in res.get("matched_places", [])[:5]:
            clean_places.append({
                "node_id": p.get("node_id"),
                "name": p.get("name"),
                "category": p.get("category"),
                "latitude": p.get("latitude"),
                "longitude": p.get("longitude"),
                "rating": p.get("rating_value", 4.5),
                "address": p.get("street_address", "")
            })

        return ChatResponse(
            status="success",
            query=req.query,
            answer=res.get("final_answer", ""),
            route_taken=res.get("route_taken", "local_knowledge"),
            confidence_score=res.get("confidence_score", 0.88),
            matched_places=clean_places
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý câu hỏi: {str(e)}")
