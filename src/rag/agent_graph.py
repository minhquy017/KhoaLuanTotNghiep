# -*- coding: utf-8 -*-
"""
LANGGRAPH AGENTIC RAG (ĐIỀU PHỐI ĐA NGUỒN TRI THỨC VỚI LANGGRAPH & QWEN2.5)
Khóa luận Tốt nghiệp ngành Khoa học Dữ liệu và Trí tuệ Nhân tạo (DS&AI K3 - HUET)
Trường Kỹ thuật và Công nghệ - Đại học Huế
Đề tài: Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh dựa trên Đồ thị Tri thức Không gian và LLM
-----------------------------------------------------------------------------------------------------
Kiến trúc State Graph:
  [START]
     │
     ▼
  1. [extract_and_retrieve_kg]  --> Truy xuất Đồ thị Không gian (NetworkX: SERVES, NEAR_BY, LOCATED_IN)
     │
     ▼
  2. [retrieve_vector_reviews]  --> Truy xuất 1.69M reviews (ChromaDB) + Đánh giá Confidence Score
     │
     ▼
  <grade_confidence> (Conditional Edge: Router)
     ├── (Score >= 0.40 & có dữ liệu nội bộ) ────────┐
     │                                                │
     └── (Score < 0.40 hoặc thiếu thông tin) ──┐      │
                                               ▼      │
                                   3. [web_search_fallback] (DuckDuckGo / Wiki)
                                               │      │
                                               ▼      ▼
                                      4. [generate_response] (Ollama Qwen2.5:3b GPU)
                                               │
                                               ▼
                                             [END]
"""

import os
import sys
import unicodedata
from typing import TypedDict, List, Dict, Any, Optional, Literal

# Bắt buộc UTF-8 stdout trên Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
sys.path.append(PROJECT_ROOT)

from langgraph.graph import StateGraph, END, START
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama

from src.graph.graph_retriever import get_graph_retriever, strip_accents
from src.graph.spatial_indexer import haversine_distance
from src.rag.vector_retriever import get_vector_retriever
from src.rag.web_search_tool import get_web_search_tool


# =============================================================================
# 1. ĐỊNH NGHĨA TRẠNG THÁI HỆ THỐNG (STATE DEFINITION)
# =============================================================================
class TourismAgentState(TypedDict):
    query: str
    locality: str
    target_dish: Optional[str]
    target_place: Optional[str]
    matched_places: List[Dict[str, Any]]
    nearby_map: Dict[str, List[Dict[str, Any]]]
    dishes_map: Dict[str, List[Dict[str, Any]]]
    reviews: List[Dict[str, Any]]
    web_results: List[Dict[str, Any]]
    confidence_score: float
    route_taken: str                      # "local_knowledge" | "web_fallback"
    formatted_context: str
    final_answer: str
    graph_trace: List[Dict[str, Any]]     # XAI: chuỗi suy luận minh bạch của đồ thị


# =============================================================================
# 2. KHỞI TẠO CÁC ENGINES (SINGLETONS)
# =============================================================================
graph_retriever = get_graph_retriever()
vector_retriever = get_vector_retriever()
web_search_tool = get_web_search_tool()

# LLM cục bộ chạy trên GPU RTX 3050 (100% miễn phí)
llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0.3,
    num_ctx=4096,
    keep_alive="24h"
)


# =============================================================================
# 3. NODE 1: TRUY XUẤT ĐỒ THỊ TRI THỨC KHÔNG GIAN (KG RETRIEVAL)
# =============================================================================
def node_extract_and_retrieve_kg(state: TourismAgentState) -> Dict[str, Any]:
    query = state["query"]
    trace_steps = state.get("graph_trace", [])
    norm_q = strip_accents(query)

    # 1. Nhận diện địa phương
    locality = "Thành phố Huế" if any(h in norm_q for h in ["hue", "thua thien", "co do"]) else ""
    if "ha noi" in norm_q or "hanoi" in norm_q:
        locality = "Thủ Đô Hà Nội"
    elif "sai gon" in norm_q or "ho chi minh" in norm_q:
        locality = "Thành phố Hồ Chí Minh"
    elif "da nang" in norm_q:
        locality = "Thành phố Đà Nẵng"

    trace_steps.append({
        "step": "locality_detection",
        "icon": "📍",
        "label": "Nhận diện địa phương",
        "detail": locality if locality else "Không xác định rõ → mặc định Huế",
        "status": "found" if locality else "default"
    })

    # 2. Nhận diện món ăn đặc sản trong câu hỏi (hỗ trợ alias phổ biến)
    dish_aliases = {
        "bun bo": "Bún bò Huế",
        "banh beo": "Bánh bèo",
        "banh nam": "Bánh nậm",
        "banh loc": "Bánh bột lọc",
        "banh bot loc": "Bánh bột lọc",
        "com hen": "Cơm hến",
        "bun hen": "Bún hến",
        "che heo quay": "Chè bột lọc bọc heo quay",
        "che bot loc": "Chè bột lọc bọc heo quay",
        "banh khoai": "Bánh khoái",
        "nem lui": "Nem lụi",
        "banh canh": "Bánh canh Nam Phổ",
        "che bap": "Chè bắp",
        "me xung": "Mè xửng",
        "banh ep": "Bánh ép",
        "banh mi bot loc": "Bánh mì bột lọc",
        "banh uot thit nuong": "Bánh ướt thịt nướng",
        "com am phu": "Cơm âm phủ",
        "com bay mau": "Cơm âm phủ"
    }
    target_dish = None
    for alias, formal_name in dish_aliases.items():
        if alias in norm_q:
            target_dish = formal_name
            trace_steps.append({
                "step": "dish_recognition",
                "icon": "🍲",
                "label": "Nhận diện món đặc sản",
                "detail": f"'{alias}' → {formal_name}",
                "edge": "ALIAS_MATCH",
                "status": "found"
            })
            break

    if not target_dish:
        for d_norm, d_node_id in graph_retriever._dish_name_index.items():
            if d_norm in norm_q and len(d_norm) >= 3:
                target_dish = graph_retriever.G.nodes[d_node_id].get("name")
                break

    # 3. Nhận diện địa điểm nổi tiếng (hỗ trợ alias tiếng Việt phổ biến)
    alias_dict = {
        "dai noi": "place_8875",
        "kinh thanh": "place_8875",
        "hoang thanh": "place_8875",
        "chua thien mu": "place_8876",
        "thien mu": "place_8876",
        "song huong": "place_8882",
        "cau trang tien": "place_8882",
        "cho dong ba": "place_8920",
        "dong ba": "place_8920",
        "lang khai dinh": "place_8879",
        "khai dinh": "place_8879",
        "lang tu duc": "place_8880",
        "lang minh mang": "place_8878",
        "lang dong khanh": "place_8881",
        "bach ma": "place_8877",
        "cau ngoi thanh toan": "place_8885",
        "thanh toan": "place_8885",
        "bien lang co": "place_8917",
        "lang co": "place_8917",
        "deo hai van": "place_8895",
        "hai van": "place_8895",
        # Các địa điểm bản địa tinh tuyển mới bổ sung
        "banh ep gia di": "custom_local_17",
        "gia di": "custom_local_17",
        "banh mi o tho": "custom_local_13",
        "o tho": "custom_local_13",
        "com am phu": "custom_local_18",
        "cung an dinh": "custom_local_31",
        "an dinh": "custom_local_31",
        "ho thuy tien": "custom_local_21",
        "chua tu dam": "custom_local_30",
        "tu dam": "custom_local_30",
        "banh canh di huong": "custom_local_25",
        "di huong": "custom_local_25",
        "bun bo mu keo": "custom_local_26",
        "mu keo": "custom_local_26",
        "nem lui ba ty": "custom_local_27",
        "ba ty": "custom_local_27",
        "che mo ton dich": "custom_local_29",
        "mo ton dich": "custom_local_29",
        "dam lap an": "custom_local_32",
        "lap an": "custom_local_32",
        "lang thieu tri": "custom_local_33",
        "thieu tri": "custom_local_33",
        "ca phe mat biec": "custom_local_15",
        "mat biec": "custom_local_15",
        "banh uot huyen anh": "custom_local_08",
        "huyen anh": "custom_local_08",
        "chua dieu de": "custom_local_07",
        "dieu de": "custom_local_07",
        "gac trinh": "custom_local_16",
        "ca phe gac trinh": "custom_local_16",
        "com hen thuy": "custom_local_01",
        "banh beo o le": "custom_local_02"
    }

    matched_places = []
    nearby_map = {}
    dishes_map = {}

    # Bóc tách TẤT CẢ các địa danh xuất hiện trong câu hỏi (theo thứ tự xuất hiện)
    sorted_aliases = sorted(alias_dict.items(), key=lambda x: len(x[0]), reverse=True)
    matched_spans = []
    ordered_place_ids = []

    for alias, pid in sorted_aliases:
        pos = norm_q.find(alias)
        if pos != -1:
            # Kiểm tra tránh trùng lặp span (ví dụ 'chua thien mu' đã chứa 'thien mu')
            overlaps = any(pos < end and pos + len(alias) > start for start, end in matched_spans)
            if not overlaps:
                matched_spans.append((pos, pos + len(alias)))
                ordered_place_ids.append((pos, pid))

    ordered_place_ids.sort(key=lambda x: x[0])
    extracted_place_ids = [pid for _, pid in ordered_place_ids]

    # XAI trace: ghi lại các thực thể địa danh đã bóc tách
    for pid in extracted_place_ids:
        p_info = graph_retriever.G.nodes.get(pid, {})
        trace_steps.append({
            "step": "entity_extraction",
            "icon": "🏯",
            "label": "Bóc tách thực thể KG",
            "detail": f"{p_info.get('name', pid)} (node: {pid})",
            "node_id": pid,
            "edge": "ALIAS_DICT",
            "status": "found"
        })
    target_place_id = extracted_place_ids[0] if extracted_place_ids else None

    # A. Nếu người dùng đề cập TỪ 2 ĐỊA DANH TRỞ LÊN (ví dụ: 'Từ Đại Nội đi Chợ Đông Ba'):
    if len(extracted_place_ids) >= 2:
        for pid in extracted_place_ids:
            p_data = graph_retriever.get_place(pid)
            if p_data and p_data not in matched_places:
                matched_places.append(p_data)
    # B. Nếu có CẢ địa danh xuất phát VÀ món ăn đặc sản: Tìm quán phục vụ món và sắp xếp theo khoảng cách Haversine
    elif target_place_id and target_dish:
        origin_place = graph_retriever.get_place(target_place_id)
        if origin_place:
            matched_places.append(origin_place)
            lat0, lng0 = origin_place.get("latitude"), origin_place.get("longitude")
            serving_places = graph_retriever.find_places_by_dish(target_dish, locality=locality or "Thành phố Huế", limit=15)
            if lat0 and lng0:
                for sp in serving_places:
                    if sp.get("latitude") and sp.get("longitude"):
                        sp["dist_to_origin"] = haversine_distance(lat0, lng0, sp["latitude"], sp["longitude"])
                serving_places.sort(key=lambda x: x.get("dist_to_origin", 999))
            
            # Đưa các quán gần nhất vào matched_places
            for sp in serving_places[:4]:
                if sp not in matched_places:
                    matched_places.append(sp)

            # Lấy thêm các điểm lân cận qua cạnh NEAR_BY
            nearby = graph_retriever.find_nearby_places(target_place_id, max_distance_km=1.5, limit=3)
            nearby_map[target_place_id] = nearby

            # XAI trace: ghi lại quan hệ SERVES + NEAR_BY
            trace_steps.append({
                "step": "edge_traversal",
                "icon": "🔗",
                "label": "Duyệt cạnh SERVES",
                "detail": f"Tìm {len(serving_places)} quán phục vụ '{target_dish}' gần {origin_place.get('name', '')}",
                "edge": "SERVES",
                "count": len(serving_places),
                "status": "found" if serving_places else "empty"
            })
            if nearby:
                trace_steps.append({
                    "step": "edge_traversal",
                    "icon": "📐",
                    "label": "Duyệt cạnh NEAR_BY",
                    "detail": f"{len(nearby)} điểm lân cận trong bán kính 1.5km",
                    "edge": "NEAR_BY",
                    "count": len(nearby),
                    "status": "found"
                })
    elif target_dish:
        # Chỉ có món đặc sản: Tìm các quán uy tín phục vụ món
        serving_places = graph_retriever.find_places_by_dish(target_dish, locality=locality, limit=5)
        matched_places.extend(serving_places)
        if serving_places:
            trace_steps.append({
                "step": "edge_traversal",
                "icon": "🍽️",
                "label": f"Tìm quán phục vụ '{target_dish}' (SERVES)",
                "detail": f"Định vị được {len(serving_places)} quán đặc sản tại {locality or 'Huế'}",
                "edge": "SERVES",
                "count": len(serving_places),
                "status": "found"
            })
    elif target_place_id:
        # Chỉ có địa danh di tích: Lấy điểm gốc và các điểm lân cận
        origin_place = graph_retriever.get_place(target_place_id)
        if origin_place:
            matched_places.append(origin_place)
            nearby = graph_retriever.find_nearby_places(target_place_id, max_distance_km=1.5, limit=4)
            nearby_map[target_place_id] = nearby
            for nb in nearby:
                if nb not in matched_places:
                    matched_places.append(nb)
            if nearby:
                trace_steps.append({
                    "step": "edge_traversal",
                    "icon": "📐",
                    "label": "Duyệt cạnh NEAR_BY",
                    "detail": f"{len(nearby)} điểm lân cận '{origin_place.get('name', '')}'",
                    "edge": "NEAR_BY",
                    "count": len(nearby),
                    "status": "found"
                })

    # C. Nếu chưa có địa điểm nào, tìm kiếm theo từ khóa trong KG
    if not matched_places:
        searched = graph_retriever.search_places(query, locality=locality, limit=4)
        matched_places.extend(searched)
        trace_steps.append({
            "step": "fuzzy_search",
            "icon": "🔎",
            "label": "Tìm kiếm mờ trong KG",
            "detail": f"Fuzzy search '{query}' → {len(searched)} kết quả",
            "count": len(searched),
            "status": "found" if searched else "empty"
        })

    # 4. Nhận diện nhu cầu ăn chay hoặc danh mục đặc thù
    if any(k in norm_q for k in ["chay", "quan chay", "com chay", "an chay", "do chay"]):
        veg_places = graph_retriever.search_places("chay", locality=locality or "Thành phố Huế", limit=3)
        for vp in veg_places:
            if vp not in matched_places:
                matched_places.append(vp)

    # Lấy thêm thông tin món đặc sản và điểm lân cận cho các địa điểm tìm thấy
    for p in matched_places:
        pid = p.get("node_id")
        if pid:
            if pid not in dishes_map:
                dishes = graph_retriever.get_dishes_of_place(pid)
                if dishes:
                    dishes_map[pid] = dishes
            if pid not in nearby_map and len(matched_places) <= 2:
                near = graph_retriever.find_nearby_places(pid, limit=3)
                if near:
                    nearby_map[pid] = near

    # XAI: tổng kết bước KG retrieval
    trace_steps.append({
        "step": "kg_summary",
        "icon": "📊",
        "label": "Tổng kết Đồ thị Tri thức",
        "detail": f"{len(matched_places)} địa điểm, {sum(len(v) for v in nearby_map.values())} lân cận, {sum(len(v) for v in dishes_map.values())} món đặc sản",
        "status": "found" if matched_places else "empty"
    })

    return {
        "locality": locality,
        "target_dish": target_dish,
        "target_place": target_place_id,
        "matched_places": matched_places,
        "nearby_map": nearby_map,
        "dishes_map": dishes_map,
        "graph_trace": trace_steps
    }


# =============================================================================
# 4. NODE 2: TRUY XUẤT VECTOR TỪ CHROMADB (VECTOR RETRIEVAL & CONFIDENCE)
# =============================================================================
def node_retrieve_vector_reviews(state: TourismAgentState) -> Dict[str, Any]:
    query = state["query"]
    trace_steps = state.get("graph_trace", [])
    norm_q = strip_accents(query)
    matched_places = state.get("matched_places", [])

    # Nếu câu hỏi thuần về giờ mở cửa, giá vé, địa chỉ -> không cần inject review tránh loãng ngữ cảnh
    pure_fact_triggers = ["may gio", "mo cua", "dong cua", "gia ve", "bao nhieu tien", "o dau", "dia chi"]
    is_pure_fact = any(f in norm_q for f in pure_fact_triggers) and not any(k in norm_q for k in ["review", "danh gia", "ngon", "kinh nghiem", "khen", "che"])

    if is_pure_fact:
        return {
            "reviews": [],
            "confidence_score": 0.5
        }

    # Lọc theo place_urls nếu đã tìm được địa điểm cụ thể từ KG
    place_urls = [p.get("url") for p in matched_places if p.get("url")]

    reviews, raw_score = vector_retriever.query_reviews(
        query_text=query,
        n_results=3,
        place_urls=place_urls if place_urls else None
    )

    # Nếu câu hỏi dạng hội thoại tự nhiên làm điểm vector thấp, thử tìm theo từ khóa món ăn
    target_dish = state.get("target_dish")
    if (not reviews or raw_score < 0.40) and target_dish:
        dish_query = f"{target_dish} {state.get('locality', 'Huế')}"
        d_reviews, d_score = vector_retriever.query_reviews(
            query_text=dish_query,
            n_results=3,
            place_urls=place_urls if place_urls else None
        )
        if d_score > raw_score:
            reviews = d_reviews
            raw_score = d_score

    # Nếu ChromaDB chưa có vector cho địa điểm bản địa mới nhưng node KG đã có sẵn reviews thực tế:
    if not reviews and matched_places:
        for p in matched_places:
            if p.get("reviews"):
                for r in p["reviews"][:2]:
                    reviews.append({
                        "text": f"[{r.get('title', 'Đánh giá')}] {r.get('comment', '')}",
                        "rating": r.get("rating", 5.0),
                        "trip_type": r.get("trip_type", "Du khách"),
                        "source": p.get("name", "Đặc sản Cố Đô")
                    })
                raw_score = max(raw_score, 0.75)
                break

    # Tính toán Composite Confidence Score
    # Khi Knowledge Graph đã định vị được các địa điểm thực tế, hệ thống có độ tin cậy cơ sở cao (0.60)
    kg_base = 0.60 if matched_places else 0.0
    entity_bonus = 0.15 if len(matched_places) >= 2 else (0.10 if matched_places else 0.0)
    dish_bonus = 0.10 if target_dish else 0.0
    vector_contrib = min(0.15, raw_score * 0.2) if raw_score > 0 else 0.0
    total_confidence = min(0.98, kg_base + entity_bonus + dish_bonus + vector_contrib) if matched_places else min(1.0, raw_score + dish_bonus)

    # XAI trace: ghi lại bước vector retrieval và confidence scoring
    place_names = [p.get("name", "") for p in matched_places[:2] if p.get("name")]
    names_str = f" cho '{', '.join(place_names)}'" if place_names else ""
    trace_steps.append({
        "step": "vector_retrieval",
        "icon": "🧠",
        "label": "Truy xuất Review thực tế (Graph-Guided Vector)",
        "detail": f"{len(reviews)} reviews khớp{names_str} | Điểm tương đồng: {raw_score:.2f}",
        "count": len(reviews),
        "status": "found" if reviews else "empty"
    })
    trace_steps.append({
        "step": "confidence_scoring",
        "icon": "⚡",
        "label": "Tính Composite Confidence",
        "detail": f"KG Base={kg_base:.2f} + Entity={entity_bonus:.2f} + Dish={dish_bonus:.2f} + Vector={vector_contrib:.2f} → {total_confidence:.2f}",
        "score": total_confidence,
        "status": "high" if total_confidence >= 0.6 else "medium" if total_confidence >= 0.4 else "low"
    })

    return {
        "reviews": reviews,
        "confidence_score": round(total_confidence, 4),
        "graph_trace": trace_steps
    }


# =============================================================================
# 5. CONDITIONAL ROUTER: ĐÁNH GIÁ ĐIỂM TIN CẬY (CONFIDENCE ROUTING)
# =============================================================================
def grade_confidence(state: TourismAgentState) -> Literal["node_generate_response", "node_web_search_fallback"]:
    """
    Quyết định nhánh xử lý trong LangGraph:
    - Nếu câu hỏi về thông tin thời gian thực / vận hành (giờ mở cửa, giá vé, thời tiết): Kích hoạt Web Fallback
    - Nếu câu hỏi về món ăn / địa điểm đã có trong Knowledge Graph: Đi thẳng tới LLM
    - Nếu hoàn toàn không có thực thể: Kích hoạt Web Fallback
    """
    confidence = state.get("confidence_score", 0.0)
    has_places = len(state.get("matched_places", [])) > 0
    has_reviews = len(state.get("reviews", [])) > 0
    trace_steps = state.get("graph_trace", [])

    query_lower = state["query"].lower()
    norm_q = strip_accents(query_lower)

    # Các từ khóa hỏi về thông tin thời gian thực / giờ giấc / giá vé mà KG tĩnh không có
    external_triggers = [
        "thoi tiet", "thời tiết", "ve may bay", "vé máy bay", 
        "nhiet do", "nhiệt độ", "bao nhieu do", "mưa khong", "mưa không", "dự báo thời tiết",
        "mo cua", "mở cửa", "dong cua", "đóng cửa", "may gio", "mấy giờ", "khi nao mo",
        "gia ve", "giá vé", "ve vao cong", "vé vào cổng", "phi tham quan", "phí tham quan"
    ]
    is_external_query = any(t in norm_q or t in query_lower for t in external_triggers)

    if is_external_query:
        trace_steps.append({
            "step": "routing_decision",
            "icon": "🌐",
            "label": "Router → Web Search Fallback",
            "detail": "Câu hỏi thời gian thực (giờ mở cửa/giá vé/thời tiết) → chuyển sang DuckDuckGo",
            "decision": "web_fallback",
            "status": "redirect"
        })
        return "node_web_search_fallback"

    # Nếu Knowledge Graph đã định vị được các địa điểm thực tế
    if has_places:
        trace_steps.append({
            "step": "routing_decision",
            "icon": "✅",
            "label": "Router → Tri thức Nội bộ",
            "detail": f"KG đã định vị {len(state.get('matched_places', []))} địa điểm → phản hồi từ CSDL nội bộ",
            "decision": "local_knowledge",
            "status": "confident"
        })
        return "node_generate_response"

    # Nếu Vector Search tìm được review chất lượng cao
    if has_reviews and confidence >= 0.40:
        trace_steps.append({
            "step": "routing_decision",
            "icon": "✅",
            "label": "Router → Tri thức Nội bộ (Review)",
            "detail": f"ChromaDB review đủ tin cậy (confidence={confidence:.2f} ≥ 0.40)",
            "decision": "local_knowledge",
            "status": "confident"
        })
        return "node_generate_response"

    trace_steps.append({
        "step": "routing_decision",
        "icon": "🌐",
        "label": "Router → Web Search Fallback",
        "detail": f"Confidence thấp ({confidence:.2f} < 0.40, KG=0 địa điểm) → chuyển sang DuckDuckGo",
        "decision": "web_fallback",
        "status": "redirect"
    })
    return "node_web_search_fallback"


# =============================================================================
# 6. NODE 3: TÌM KIẾM WEB BỔ SUNG (WEB SEARCH FALLBACK)
# =============================================================================
def node_web_search_fallback(state: TourismAgentState) -> Dict[str, Any]:
    query = state["query"]
    trace_steps = state.get("graph_trace", [])
    web_results = web_search_tool.search(query, max_results=3)

    trace_steps.append({
        "step": "web_search",
        "icon": "🌐",
        "label": "Tìm kiếm Web (DuckDuckGo)",
        "detail": f"{len(web_results)} kết quả từ DuckDuckGo/Wikipedia",
        "count": len(web_results),
        "status": "found" if web_results else "empty"
    })

    return {
        "web_results": web_results,
        "route_taken": "web_fallback",
        "graph_trace": trace_steps
    }


# =============================================================================
# 7. NODE 4: SINH CÂU TRẢ LỜI TỔNG HỢP VỚI QWEN2.5-3B (GENERATION)
# =============================================================================
def node_generate_response(state: TourismAgentState) -> Dict[str, Any]:
    query = state["query"]
    route_taken = state.get("route_taken", "local_knowledge")
    matched_places = state.get("matched_places", [])
    nearby_map = state.get("nearby_map", {})
    dishes_map = state.get("dishes_map", {})
    reviews = state.get("reviews", [])
    web_results = state.get("web_results", [])

    target_dish = state.get("target_dish")

    # Gom ngữ cảnh
    context_blocks = []

    # 1. Ngữ cảnh từ Knowledge Graph
    if matched_places:
        kg_context = graph_retriever.format_graph_context(
            retrieved_places=matched_places,
            nearby_info=nearby_map,
            dishes_info=dishes_map
        )
        context_blocks.append(kg_context)

    # 2. Ngữ cảnh từ ChromaDB Reviews
    if reviews:
        rev_context = vector_retriever.format_reviews_context(reviews)
        if rev_context:
            context_blocks.append(rev_context)

    # 3. Ngữ cảnh từ Web Search nếu có
    if web_results:
        web_context = web_search_tool.format_search_context(web_results)
        if web_context:
            context_blocks.append(web_context)

    full_context = "\n\n".join(context_blocks) if context_blocks else "Không tìm thấy dữ liệu liên quan."

    # Định dạng Prompt chuyên gia du lịch Cố Đô Huế
    norm_q = query.lower()
    nav_keywords = [
        "chỉ đường", "chi duong", "đường đi", "duong di", "đi đến", "di den", 
        "làm sao để đi", "lam sao de di", "cách đi", "cach di", "dẫn đường", "dan duong",
        "hướng dẫn đường", "lộ trình", "lo trinh", "chỉ lối", "chi loi"
    ]
    is_nav = any(k in norm_q for k in nav_keywords) or (
        ("từ " in norm_q or "tu " in norm_q) and any(w in norm_q for w in ["đi ", "đến ", "den ", "tới ", "toi ", "sang ", "qua "])
    ) or any(k in norm_q for k in ["đi tới", "di toi", "đi sang", "di sang", "đi qua", "di qua"])

    dish_rule = ""
    if target_dish:
        dish_rule = f"""
4. YÊU CẦU ĐẶC BIỆT VỀ MÓN ĂN:
   - Du khách đang hỏi về món: "{target_dish}".
   - Bạn CHỈ ĐƯỢC PHÉP giới thiệu các quán ăn phục vụ món {target_dish} từ danh sách ngữ cảnh.
   - Tuyệt đối KHÔNG ĐƯỢC nhắc đến các món ăn hay quán ăn khác (như cơm hến, bánh bèo, chè...) không liên quan đến {target_dish}."""

    system_prompt = f"""Bạn là Hướng dẫn viên & Trợ lý Du lịch Cố đô Huế thông minh, thân thiện, mang phong cách mến khách và nhã nhặn đặc trưng của người dân xứ Huế.

Nguyên tắc trả lời bắt buộc:
1. VĂN PHONG TỰ NHIÊN, LỊCH SỰ, ẤM ÁP:
   - Mở đầu nhẹ nhàng, lịch thiệp ("Dạ thưa bạn...", "Dạ, em xin chia sẻ...", "Chào bạn...").
   - Tuyệt đối KHÔNG dùng các câu cứng nhắc, máy móc như: "Dựa trên dữ liệu Đồ thị Tri thức...", "Hệ thống đã xác định thành công...".
   - Diễn đạt 100% bằng tiếng Việt trong sáng, gần gũi như một người bạn đồng hành bản địa tại Huế.

2. NẾU DU KHÁCH HỎI ĐƯỜNG ĐI / LỘ TRÌNH:
   - Trả lời ngắn gọn (1-2 câu), thông báo tuyến đường đã được định vị và vẽ trực tiếp trên bản đồ bên cạnh.
   - Nhắc tên điểm đến và địa chỉ cụ thể nếu có, gợi ý du khách xem cự ly và bấm nút Google Maps bên dưới để nghe dẫn đường khi di chuyển.

3. VỚI CÂU HỎI VỀ ẨM THỰC / DANH THẮNG:
   - Đi thẳng vào các thắc mắc (địa chỉ, giá cả, thời điểm đẹp nhất trong ngày, món ngon đặc sản).
   - Dùng icon sinh động (🏯, 🍲, 📍, ⏰) và gạch đầu dòng rõ ràng.{dish_rule}"""

    user_prompt = f"""[NGỮ CẢNH HỆ THỐNG]:
{full_context}

[CÂU HỎI CỦA DU KHÁCH]:
{query}

[CÂU TRẢ LỜI CỦA BẠN]:"""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        answer_text = response.content.strip()
    except Exception as e:
        # Fallback thân thiện, tự nhiên khi LLM cục bộ chưa khởi động
        if is_nav and matched_places:
            if len(matched_places) >= 2 and ("từ " in norm_q or "tu " in norm_q):
                origin_name = matched_places[0].get("name", "điểm xuất phát")
                dest_p = matched_places[1]
            else:
                origin_name = "vị trí của bạn"
                dest_p = matched_places[0]
            
            dest_name = dest_p.get("name", "điểm đến")
            dest_addr = dest_p.get("address", "")
            addr_str = f" ({dest_addr})" if dest_addr else ""
            answer_text = (
                f"Dạ, em đã định vị và vẽ tuyến đường nhanh nhất từ {origin_name} đến **{dest_name}**{addr_str} trên bản đồ bên cạnh rồi nhé! "
                f"Bạn có thể xem cự ly, thời gian ước tính và bấm mở Google Maps bên dưới để nghe dẫn đường trực tiếp khi di chuyển."
            )
        elif is_nav:
            answer_text = "Dạ, em đã ghi nhận điểm đến và định vị lộ trình di chuyển tối ưu trên bản đồ bên cạnh cho bạn rồi nhé!"
        elif target_dish and matched_places:
            bullets = []
            for p in matched_places[:4]:
                p_name = p.get('name')
                p_addr = p.get('address') or p.get('street_address') or 'TP. Huế'
                p_desc = p.get('description') or p.get('desc') or ''
                desc_snippet = f" — {p_desc[:80]}..." if p_desc and len(p_desc) > 10 else ""
                bullets.append(f"• **{p_name}** ({p_addr}){desc_snippet}")
            places_bullets = "\n".join(bullets)
            answer_text = (
                f"Dạ, nếu bạn muốn thưởng thức món **{target_dish}** chuẩn vị xứ Huế, em xin gợi ý những quán nổi tiếng được người dân địa phương và du khách đánh giá cao nhất:\n\n"
                f"{places_bullets}\n\n"
                f"Bạn có thể nhấp vào các nút bên dưới để ghim vị trí và mở hồ sơ chi tiết trên bản đồ nhé!"
            )
        elif matched_places:
            places_str = ", ".join([p.get("name", "") for p in matched_places[:3]])
            answer_text = (
                f"Dạ, em xin gửi bạn thông tin về **{places_str}**. "
                f"Bạn có thể xem vị trí chi tiết, các món ăn đặc sắc và đánh giá thực tế của du khách ngay trên bản đồ bên cạnh nhé!"
            )
        elif web_results:
            bullets = []
            for w in web_results[:3]:
                title = w.get("title") or ""
                snippet = w.get("snippet") or ""
                if title:
                    bullets.append(f"• **{title}**: {snippet[:140]}...")
            wb_str = "\n".join(bullets)
            answer_text = (
                f"Dạ, theo kết quả tra cứu tổng hợp về du lịch Cố đô Huế:\n\n{wb_str}\n\n"
                f"Bạn có thể xem chi tiết vị trí và gợi ý trên bản đồ tương tác nhé!"
            )
        else:
            answer_text = "Dạ, em đã tìm thấy các thông tin phù hợp cho câu hỏi của bạn tại Cố đô Huế. Bạn có thể xem chi tiết trên bản đồ tương tác nhé!"

    # XAI trace: ghi lại bước sinh phản hồi cuối cùng
    trace_steps = state.get("graph_trace", [])
    trace_steps.append({
        "step": "llm_generation",
        "icon": "🤖",
        "label": "Sinh phản hồi (Qwen2.5-3B GPU)",
        "detail": f"LLM tổng hợp từ {len(context_blocks)} khối ngữ cảnh → câu trả lời tự nhiên",
        "model": "qwen2.5:3b",
        "status": "done"
    })

    return {
        "formatted_context": full_context,
        "final_answer": answer_text,
        "route_taken": route_taken,
        "graph_trace": trace_steps
    }


# =============================================================================
# 8. XÂY DỰNG & BIÊN DỊCH LANGGRAPH (WORKFLOW BUILDER)
# =============================================================================
def build_tourism_agent_graph():
    workflow = StateGraph(TourismAgentState)

    # Thêm các đỉnh (Nodes)
    workflow.add_node("node_extract_and_retrieve_kg", node_extract_and_retrieve_kg)
    workflow.add_node("node_retrieve_vector_reviews", node_retrieve_vector_reviews)
    workflow.add_node("node_web_search_fallback", node_web_search_fallback)
    workflow.add_node("node_generate_response", node_generate_response)

    # Thiết lập luồng cạnh (Edges)
    workflow.add_edge(START, "node_extract_and_retrieve_kg")
    workflow.add_edge("node_extract_and_retrieve_kg", "node_retrieve_vector_reviews")

    # Cạnh có điều kiện: Router phân luồng
    workflow.add_conditional_edges(
        "node_retrieve_vector_reviews",
        grade_confidence,
        {
            "node_generate_response": "node_generate_response",
            "node_web_search_fallback": "node_web_search_fallback"
        }
    )

    workflow.add_edge("node_web_search_fallback", "node_generate_response")
    workflow.add_edge("node_generate_response", END)

    app = workflow.compile()
    return app


# Singleton Agent
_compiled_agent = None

def get_tourism_agent():
    global _compiled_agent
    if _compiled_agent is None:
        _compiled_agent = build_tourism_agent_graph()
    return _compiled_agent


# =============================================================================
# 9. HÀM THỰC THI CHÍNH (INTERACTIVE TEST)
# =============================================================================
def query_agent(question: str):
    agent = get_tourism_agent()
    initial_state: TourismAgentState = {
        "query": question,
        "locality": "",
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
        "final_answer": "",
        "graph_trace": []
    }

    result = agent.invoke(initial_state)
    return result


if __name__ == "__main__":
    print("=" * 80)
    print("🤖 KHỞI CHẠY LANGGRAPH SPATIAL GRAPHRAG AGENT (QWEN2.5-3B)")
    print("=" * 80)

    # Test Case 1: Câu hỏi trong CSDL du lịch (KG + ChromaDB)
    q1 = "Quán nào ở Huế bán Bún bò ngon và địa chỉ ở đâu?"
    print(f"\n👉 [TEST CASE 1 (Nội bộ)]: {q1}")
    res1 = query_agent(q1)
    print(f"• Luồng điều hướng: {res1['route_taken']} (Confidence: {res1['confidence_score']})")
    print(f"• Số địa điểm KG: {len(res1['matched_places'])} | Số reviews: {len(res1['reviews'])}")
    print(f"\n📝 Câu trả lời:\n{res1['final_answer']}")

    # Test Case 2: Câu hỏi về thông tin bên ngoài (Trigger Web Search Fallback)
    q2 = "Thời tiết Huế hôm nay thế nào, có mưa không?"
    print("\n" + "-" * 80)
    print(f"\n👉 [TEST CASE 2 (Web Fallback)]: {q2}")
    res2 = query_agent(q2)
    print(f"• Luồng điều hướng: {res2['route_taken']} (Confidence: {res2['confidence_score']})")
    print(f"• Số kết quả web: {len(res2['web_results'])}")
    print(f"\n📝 Câu trả lời:\n{res2['final_answer']}")
