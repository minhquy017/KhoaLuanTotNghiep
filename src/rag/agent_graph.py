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
        "me xung": "Mè xửng"
    }
    target_dish = None
    for alias, formal_name in dish_aliases.items():
        if alias in norm_q:
            target_dish = formal_name
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
        "hai van": "place_8895"
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
    elif target_dish:
        # Chỉ có món đặc sản: Tìm các quán uy tín phục vụ món
        serving_places = graph_retriever.find_places_by_dish(target_dish, locality=locality, limit=5)
        matched_places.extend(serving_places)
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

    # C. Nếu chưa có địa điểm nào, tìm kiếm theo từ khóa trong KG
    if not matched_places:
        searched = graph_retriever.search_places(query, locality=locality, limit=4)
        matched_places.extend(searched)

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

    # Tính toán Composite Confidence Score
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
    - Nếu câu hỏi về thông tin thời gian thực / vận hành (giờ mở cửa, giá vé, thời tiết): Kích hoạt Web Fallback
    - Nếu câu hỏi về món ăn / địa điểm đã có trong Knowledge Graph: Đi thẳng tới LLM
    - Nếu hoàn toàn không có thực thể: Kích hoạt Web Fallback
    """
    confidence = state.get("confidence_score", 0.0)
    has_places = len(state.get("matched_places", [])) > 0
    has_reviews = len(state.get("reviews", [])) > 0

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
        return "node_web_search_fallback"

    # Nếu Knowledge Graph đã định vị được các địa điểm thực tế
    if has_places:
        return "node_generate_response"

    # Nếu Vector Search tìm được review chất lượng cao
    if has_reviews and confidence >= 0.40:
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
        if rev_context:
            context_blocks.append(rev_context)

    # 3. Ngữ cảnh từ Web Search nếu có
    if web_results:
        web_context = web_search_tool.format_search_context(web_results)
        if web_context:
            context_blocks.append(web_context)

    full_context = "\n\n".join(context_blocks) if context_blocks else "Không tìm thấy dữ liệu liên quan."

    # Định dạng Prompt chuyên gia du lịch Cố Đô Huế
    # Kiểm tra xem câu hỏi có phải dạng chỉ đường / điều hướng hay không
    norm_q = query.lower()
    nav_keywords = [
        "chỉ đường", "chi duong", "đường đi", "duong di", "đi đến", "di den", 
        "làm sao để đi", "lam sao de di", "cách đi", "cach di", "dẫn đường", "dan duong",
        "hướng dẫn đường", "lộ trình", "lo trinh", "chỉ lối", "chi loi"
    ]
    is_nav = any(k in norm_q for k in nav_keywords) or (
        ("từ " in norm_q or "tu " in norm_q) and any(w in norm_q for w in ["đi ", "đến ", "den ", "tới ", "toi ", "sang ", "qua "])
    ) or any(k in norm_q for k in ["đi tới", "di toi", "đi sang", "di sang", "đi qua", "di qua"])

    # Định dạng Prompt chuyên gia du lịch Cố Đô Huế
    system_prompt = """Bạn là Hướng dẫn viên & Trợ lý Du lịch Cố đô Huế thông minh, thân thiện, mang phong cách mến khách và nhã nhặn đặc trưng của người dân xứ Huế.

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
   - Dùng icon sinh động (🏯, 🍲, 📍, ⏰) và gạch đầu dòng rõ ràng."""

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
        elif matched_places:
            places_str = ", ".join([p.get("name", "") for p in matched_places[:3]])
            answer_text = (
                f"Dạ, em xin gửi bạn thông tin về **{places_str}**. "
                f"Bạn có thể xem vị trí chi tiết, các món ăn đặc sắc và đánh giá thực tế của du khách ngay trên bản đồ bên cạnh nhé!"
            )
        else:
            answer_text = "Dạ, em đã tìm thấy các thông tin phù hợp cho câu hỏi của bạn tại Cố đô Huế. Bạn có thể xem chi tiết trên bản đồ tương tác nhé!"

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
