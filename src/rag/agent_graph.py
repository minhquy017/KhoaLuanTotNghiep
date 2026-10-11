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
    num_ctx=4096
)


# =============================================================================
# 3. NODE 1: TRUY XUẤT ĐỒ THỊ TRI THỨC KHÔNG GIAN (KG RETRIEVAL)
# =============================================================================
def node_extract_and_retrieve_kg(state: TourismAgentState) -> Dict[str, Any]:
    query = state["query"]
    norm_q = strip_accents(query)

    # 1. Nhận diện địa phương
    locality = "Thành phố Huế" if any(h in norm_q for h in ["hue", "thua thien", "co do"]) else ""
    if "ha noi" in norm_q or "hanoi" in norm_q:
        locality = "Thủ Đô Hà Nội"
    elif "sai gon" in norm_q or "ho chi minh" in norm_q:
        locality = "Thành phố Hồ Chí Minh"
    elif "da nang" in norm_q:
        locality = "Thành phố Đà Nẵng"

    # 2. Nhận diện món ăn đặc sản trong câu hỏi
    target_dish = None
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
        "lang tu duc": "place_8880",
        "lang minh mang": "place_8878",
        "lang dong khanh": "place_8881",
        "bach ma": "place_8877",
        "cau ngoi thanh toan": "place_8885",
        "thanh toan": "place_8885",
        "bien lang co": "place_8917",
        "lang co": "place_8917",
        "deo hai van": "place_8895",
        "hai van": "place_8895"
    }

    matched_places = []
    nearby_map = {}
    dishes_map = {}
    target_place_id = None

    for alias, pid in alias_dict.items():
        if alias in norm_q:
            target_place_id = pid
            break

    # A. Nếu tìm quán ăn theo món đặc sản (SERVES edge)
    if target_dish:
        serving_places = graph_retriever.find_places_by_dish(target_dish, locality=locality, limit=4)
        matched_places.extend(serving_places)

    # B. Nếu tìm địa điểm lân cận địa danh xác định (NEAR_BY edge)
    if target_place_id:
        origin_place = graph_retriever.get_place(target_place_id)
        if origin_place and origin_place not in matched_places:
            matched_places.append(origin_place)
        
        # Lấy các điểm lân cận
        nearby = graph_retriever.find_nearby_places(target_place_id, max_distance_km=1.5, limit=4)
        nearby_map[target_place_id] = nearby

    # C. Nếu chưa có địa điểm nào, tìm kiếm theo từ khóa trong KG
    if not matched_places:
        searched = graph_retriever.search_places(query, locality=locality, limit=3)
        matched_places.extend(searched)

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

    return {
        "locality": locality,
        "target_dish": target_dish,
        "target_place": target_place_id,
        "matched_places": matched_places,
        "nearby_map": nearby_map,
        "dishes_map": dishes_map
    }


# =============================================================================
# 4. NODE 2: TRUY XUẤT VECTOR TỪ CHROMADB (VECTOR RETRIEVAL & CONFIDENCE)
# =============================================================================
def node_retrieve_vector_reviews(state: TourismAgentState) -> Dict[str, Any]:
    query = state["query"]
    matched_places = state.get("matched_places", [])

    # Lọc theo place_urls nếu đã tìm được địa điểm cụ thể từ KG
    place_urls = [p.get("url") for p in matched_places if p.get("url")]

    reviews, raw_score = vector_retriever.query_reviews(
        query_text=query,
        n_results=4,
        place_urls=place_urls if place_urls else None
    )

    # Tính toán Composite Confidence Score
    # Điểm tin cậy được củng cố bởi cả sự tồn tại của thực thể trong KG và điểm tương đồng vector
    entity_bonus = 0.15 if matched_places else 0.0
    dish_bonus = 0.10 if state.get("target_dish") else 0.0
    
    total_confidence = min(1.0, raw_score + entity_bonus + dish_bonus)

    return {
        "reviews": reviews,
        "confidence_score": round(total_confidence, 4)
    }


# =============================================================================
# 5. CONDITIONAL ROUTER: ĐÁNH GIÁ ĐIỂM TIN CẬY (CONFIDENCE ROUTING)
# =============================================================================
def grade_confidence(state: TourismAgentState) -> Literal["node_generate_response", "node_web_search_fallback"]:
    """
    Quyết định nhánh xử lý trong LangGraph:
    - Nếu câu hỏi về thông tin thời gian thực ngoài CSDL (thời tiết, giá vé máy bay, tin tức): Kích hoạt Web Fallback
    - Nếu Đồ thị Tri thức đã tìm thấy địa điểm/món ăn HOẶC Vector Store có độ tương đồng tốt (>= 0.35): Đi thẳng tới LLM
    - Nếu hoàn toàn không có thực thể và điểm vector thấp: Kích hoạt Web Fallback
    """
    confidence = state.get("confidence_score", 0.0)
    has_places = len(state.get("matched_places", [])) > 0
    has_reviews = len(state.get("reviews", [])) > 0

    # Các từ khóa đặc trưng của thông tin ngoại vi real-time
    query_lower = state["query"].lower()
    external_triggers = [
        "thoi tiet", "thời tiết", "ve may bay", "vé máy bay", 
        "nhiet do", "nhiệt độ", "bao nhieu do", "mưa khong", "mưa không", "dự báo thời tiết"
    ]
    is_external_query = any(t in query_lower for t in external_triggers)

    if is_external_query:
        return "node_web_search_fallback"

    # Nếu Knowledge Graph đã định vị được các địa điểm thực tế
    if has_places:
        return "node_generate_response"

    # Nếu Vector Search tìm được review chất lượng cao
    if has_reviews and confidence >= 0.38:
        return "node_generate_response"

    return "node_web_search_fallback"


# =============================================================================
# 6. NODE 3: TÌM KIẾM WEB BỔ SUNG (WEB SEARCH FALLBACK)
# =============================================================================
def node_web_search_fallback(state: TourismAgentState) -> Dict[str, Any]:
    query = state["query"]
    web_results = web_search_tool.search(query, max_results=3)

    return {
        "web_results": web_results,
        "route_taken": "web_fallback"
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
        context_blocks.append(rev_context)

    # 3. Ngữ cảnh từ Web Search nếu có
    if web_results:
        web_context = web_search_tool.format_search_context(web_results)
        context_blocks.append(web_context)

    full_context = "\n\n".join(context_blocks) if context_blocks else "Không tìm thấy dữ liệu liên quan."

    # Định dạng Prompt học thuật, súc tích cho Qwen2.5
    system_prompt = """Bạn là trợ lý AI chuyên gia tư vấn du lịch Việt Nam thông minh, chuẩn xác và am hiểu sâu sắc văn hóa, ẩm thực Cố đô Huế.
Nhiệm vụ: Dựa vào thông tin được cung cấp trong [NGỮ CẢNH HỆ THỐNG] để trả lời câu hỏi của du khách.

Nguyên tắc bắt buộc:
1. TRUNG THỰC & CHUẨN XÁC: Chỉ dùng thông tin có trong ngữ cảnh. Không suy đoán hay tự bịa số liệu.
2. NÊU RÕ BẰNG CHỨNG:
   - Nếu có thông tin từ Đồ thị Tri thức: Nêu rõ tên quán, địa chỉ, rating, món đặc sản, khoảng cách lân cận.
   - Nếu có trải nghiệm du khách: Trích dẫn nhận xét thực tế (ví dụ: "Theo đánh giá của du khách...").
   - Nếu sử dụng thông tin Internet: Nêu rõ "Dựa trên dữ liệu cập nhật từ nguồn mở...".
3. TRÌNH BÀY ĐẸP: Dùng gạch đầu dòng, icon trực quan (🍲, 📍, ⭐), ngôn phong lịch sự, ấm áp."""

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
        answer_text = f"Đã xảy ra lỗi khi tạo câu trả lời với LLM: {str(e)}"

    return {
        "formatted_context": full_context,
        "final_answer": answer_text,
        "route_taken": route_taken
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
        "final_answer": ""
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
