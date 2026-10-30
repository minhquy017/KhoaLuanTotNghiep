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
from src.rag.visual_retriever import get_visual_retriever
from src.rag.web_search_tool import get_web_search_tool


# =============================================================================
# 1. ĐỊNH NGHĨA TRẠNG THÁI HỆ THỐNG (STATE DEFINITION)
# =============================================================================
class TourismAgentState(TypedDict):
    query: str
    locality: str
    preferences: Optional[Dict[str, Any]]
    image_base64: Optional[str]           # Chuỗi base64 của ảnh du khách gửi
    image_detected: Optional[Dict[str, Any]] # Kết quả nhận diện thị giác từ Qwen2.5-VL
    visual_matches: Optional[List[Dict[str, Any]]] # Danh sách top địa danh từ Visual Image RAG (ChromaDB + CLIP)
    visual_confidence: Optional[float]    # Điểm tương đồng Cosine cao nhất [0.0, 1.0]
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
    nav_route_info: Optional[Dict[str, Any]]


# =============================================================================
# 2. KHỞI TẠO CÁC ENGINES (SINGLETONS)
# =============================================================================
graph_retriever = get_graph_retriever()
vector_retriever = get_vector_retriever()
visual_retriever = get_visual_retriever()
web_search_tool = get_web_search_tool()

# LLM cục bộ chạy trên GPU (Mặc định: Qwen2.5-VL:7B - tag Ollama là qwen2.5vl:7b)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5vl:7b")
llm = ChatOllama(
    model=OLLAMA_MODEL,
    temperature=0.3,
    num_ctx=4096,
    keep_alive="24h"
)


# =============================================================================
# 2.1 HÀM NHẬN DIỆN THỊ GIÁC ĐA PHƯƠNG THỨC (QWEN2.5-VL)
# =============================================================================
def recognize_image_entity(image_base64: str, user_query: str = "") -> Dict[str, Any]:
    """
    Sử dụng Vision Model (Qwen2.5-VL) nhận diện địa danh, di tích lịch sử hoặc món ăn đặc sản Huế trong ảnh.
    Trả về dict: {"name": str, "category": str, "description": str}
    """
    if not image_base64:
        return {}
    
    clean_b64 = image_base64.split(",")[-1] if "," in image_base64 else image_base64
    
    prompt = (
        "Bạn là Chuyên gia Thị giác AI và Cố vấn Di sản Du lịch Cố đô Huế.\n"
        "Hãy quan sát kỹ bức ảnh này và cho biết đây là địa danh, di tích lịch sử, cảnh quan hay món ăn đặc sản nào tại Huế (hoặc Việt Nam).\n"
        "Đặc biệt chú ý nhận diện các điểm du lịch nổi tiếng: Đại Nội Huế, Ngọ Môn, Kỳ Đài, Chùa Thiên Mụ, Lăng Khải Định, Lăng Tự Đức, Lăng Minh Mạng, Cầu Trường Tiền, Chợ Đông Ba, Đồi Vọng Cảnh, Trường Quốc Học, Nhà thờ Phủ Cam, Chùa Từ Hiếu...\n"
        "hoặc các món đặc sản: Bún bò Huế, Cơm hến, Bún hến, Bánh bèo, Bánh nậm, Bánh bột lọc, Chè heo quay, Bánh khoái, Bánh ép, Nem lụi...\n\n"
        "Trả lời đúng theo định dạng 3 dòng sau (không thêm lời dẫn khác):\n"
        "TEN_DOI_TUONG: [Tên chính xác của địa danh hoặc món ăn, ví dụ: Chùa Thiên Mụ hoặc Bún bò Huế]\n"
        "LOAI: [DI_TICH / THANG_CANH / AM_THUC / KHAC]\n"
        "MO_TA: [1 câu ngắn mô tả nét đặc trưng nhận diện trong ảnh]"
    )
    if user_query and len(user_query.strip()) > 3:
        prompt += f"\nNgữ cảnh kèm theo của du khách: {user_query}"
        
    try:
        res = llm.invoke([
            SystemMessage(content="Bạn là chuyên gia thị giác AI phân tích hình ảnh du lịch và ẩm thực Huế."),
            HumanMessage(content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": f"data:image/jpeg;base64,{clean_b64}"}
            ])
        ])
        raw_text = res.content.strip()
        result = {"name": "", "category": "KHAC", "description": ""}
        for line in raw_text.splitlines():
            line = line.strip()
            if line.startswith("TEN_DOI_TUONG:"):
                result["name"] = line.replace("TEN_DOI_TUONG:", "").strip()
            elif line.startswith("LOAI:"):
                result["category"] = line.replace("LOAI:", "").strip()
            elif line.startswith("MO_TA:"):
                result["description"] = line.replace("MO_TA:", "").strip()
        
        # Nếu model không trả đúng định dạng key-value, trích xuất tên chính
        if not result["name"] and len(raw_text) > 0:
            first_line = raw_text.splitlines()[0]
            result["name"] = first_line.replace("**", "").replace("*", "").strip()[:50]
        return result
    except Exception as e:
        print(f"[Vision Recognition Error]: {e}")
        return {}


# =============================================================================
# 3. NODE 1: TRUY XUẤT ĐỒ THỊ TRI THỨC KHÔNG GIAN (KG RETRIEVAL)
# =============================================================================
def node_extract_and_retrieve_kg(state: TourismAgentState) -> Dict[str, Any]:
    query = state.get("query", "")
    trace_steps = state.get("graph_trace", [])
    image_base64 = state.get("image_base64")
    image_detected_info = None
    visual_matches = None
    visual_confidence = 0.0
    vis_matched_place_id = None

    # 0. Từ điển bí danh / tên gọi phổ biến và cụm di tích phụ thuộc (dùng chung cho cả ảnh và văn bản)
    alias_dict = {
        "dai noi": "place_8875",
        "dai noi hue": "place_8875",
        "kinh thanh": "place_8875",
        "kinh thanh hue": "place_8875",
        "hoang thanh": "place_8875",
        "hoang thanh hue": "place_8875",
        "ngo mon": "place_8875",
        "cong ngo mon": "place_8875",
        "ngo mon hue": "place_8875",
        "meridian gate": "place_8875",
        "ky dai": "place_8875",
        "cot co": "place_8875",
        "dien thai hoa": "place_8875",
        "thai hoa": "place_8875",
        "the mieu": "place_8875",
        "hien lam cac": "place_8875",
        "cuu dinh": "place_8875",
        "tu cam thanh": "place_8875",
        "chua thien mu": "place_8876",
        "thien mu": "place_8876",
        "thap phuoc duyen": "place_8876",
        "phuoc duyen": "place_8876",
        "linh mu": "place_8876",
        "chua linh mu": "place_8876",
        "song huong": "place_8882",
        "ben thuyen toa kham": "place_8882",
        "toa kham": "place_8882",
        "cau trang tien": "place_8919",
        "cau truong tien": "place_8919",
        "truong tien": "place_8919",
        "trang tien": "place_8919",
        "cho dong ba": "place_8920",
        "dong ba": "place_8920",
        "lang khai dinh": "place_8879",
        "khai dinh": "place_8879",
        "ung lang": "place_8879",
        "lang tu duc": "place_8880",
        "tu duc": "place_8880",
        "khiem lang": "place_8880",
        "lang minh mang": "place_8878",
        "minh mang": "place_8878",
        "hieu lang": "place_8878",
        "lang dong khanh": "place_8881",
        "dong khanh": "place_8881",
        "tu lang": "place_8881",
        "bach ma": "place_8877",
        "cau ngoi thanh toan": "place_8885",
        "thanh toan": "place_8885",
        # Các bãi biển danh tiếng của Thừa Thiên Huế
        "thuan an": "beach_thuan_an",
        "bien thuan an": "beach_thuan_an",
        "bai bien thuan an": "beach_thuan_an",
        "canh duong": "beach_canh_duong",
        "bien canh duong": "beach_canh_duong",
        "bai bien canh duong": "beach_canh_duong",
        "hai duong": "beach_hai_duong",
        "bien hai duong": "beach_hai_duong",
        "bai bien hai duong": "beach_hai_duong",
        "lang co": "beach_lang_co",
        "bien lang co": "beach_lang_co",
        "vinh lang co": "beach_lang_co",
        "dam lap an": "beach_lang_co",
        "deo hai van": "place_8895",
        "hai van": "place_8895",
        # Các danh thắng nổi tiếng ở bờ Nam và ngoại ô Huế
        "doi vong canh": "custom_attr_02",
        "vong canh": "custom_attr_02",
        "lang gia long": "custom_attr_01",
        "gia long": "custom_attr_01",
        "lang huong thuy xuan": "custom_attr_03",
        "lang huong": "custom_attr_03",
        "thuy xuan": "custom_attr_03",
        "dien hon chen": "custom_attr_04",
        "hon chen": "custom_attr_04",
        "huyen khong son thuong": "custom_attr_05",
        "chua huyen khong": "custom_attr_05",
        "doi thien an": "custom_local_21",
        "thien an": "custom_local_21",
        "cung an dinh": "custom_local_31",
        "an dinh": "custom_local_31",
        "ho thuy tien": "custom_local_21",
        "chua tu dam": "custom_local_30",
        "tu dam": "custom_local_30",
        "con hen": "custom_attr_con_hen",
        "dao con hen": "custom_attr_con_hen",
        "vi da": "custom_attr_con_hen",
        "banh beo ba do": "custom_rest_04",
        "ba do": "custom_rest_04",
        "com hen hoa dong": "custom_rest_02",
        "hoa dong": "custom_rest_02",
        # Các địa điểm bản địa tinh tuyển mới bổ sung
        "banh ep gia di": "custom_local_17",
        "gia di": "custom_local_17",
        "banh mi o tho": "custom_local_13",
        "o tho": "custom_local_13",
        "com am phu": "custom_local_18",
        "banh canh di huong": "custom_local_25",
        "di huong": "custom_local_25",
        "bun bo mu keo": "custom_local_26",
        "mu keo": "custom_local_26",
        "nem lui ba ty": "custom_local_27",
        "ba ty": "custom_local_27",
        "che mo ton dich": "custom_local_29",
        "mo ton dich": "custom_local_29",
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

    # A. Xử lý nhận diện ảnh đa phương thức (Multimodal Image RAG)
    if image_base64:
        trace_steps.append({
            "step": "image_upload_received",
            "icon": "🖼️",
            "label": "Tiếp nhận Ảnh từ Du khách",
            "detail": "Kích hoạt phân hệ Visual Image RAG (ChromaDB + CLIP) & Thị giác Qwen2.5-VL",
            "status": "processing"
        })

        # 1. VISUAL IMAGE RAG: So khớp Cosine đặc trưng thị giác 512D với kho ảnh mẫu địa danh Huế trong ChromaDB
        try:
            vis_matches, vis_conf = visual_retriever.query_by_image(image_base64, n_results=3)
            if vis_matches and vis_conf >= 0.60:
                top_vis = vis_matches[0]
                vis_matched_place_id = top_vis.get("place_id")
                vis_place_name = top_vis.get("place_name")
                vis_sim_pct = top_vis.get("confidence_pct", round(vis_conf * 100, 1))
                visual_confidence = vis_conf
                visual_matches = vis_matches
                
                trace_steps.append({
                    "step": "visual_rag_match",
                    "icon": "🎯",
                    "label": "Visual Image RAG (ChromaDB + CLIP)",
                    "detail": f"Khớp vector ảnh mẫu di sản: **{vis_place_name}** | Cosine Similarity: **{vis_sim_pct}%**",
                    "edge": "VISUAL_SIMILARITY",
                    "status": "found"
                })
        except Exception as e:
            print(f"⚠️ [AgentGraph] Lỗi Visual Retriever: {e}")

        # 2. VISION LLM: Nhận diện thực thể ảnh chi tiết (món ăn, góc chụp, chi tiết kiến trúc)
        img_info = recognize_image_entity(image_base64, query)
        if img_info and img_info.get("name"):
            image_detected_info = img_info
            det_name = img_info["name"]
            det_cat = img_info.get("category", "KHAC")
            det_desc = img_info.get("description", "")
            trace_steps.append({
                "step": "vision_recognition",
                "icon": "📷",
                "label": "Nhận diện Thị giác & Thực thể Ảnh",
                "detail": f"Xác định: **{det_name}** ({det_cat}) — {det_desc}",
                "status": "found"
            })

            # Đối sánh định danh thực thể ảnh trực tiếp với Knowledge Graph
            if not vis_matched_place_id:
                norm_det = strip_accents(det_name)
                for a_k, a_pid in alias_dict.items():
                    if a_k == norm_det or a_k in norm_det or norm_det in a_k:
                        vis_matched_place_id = a_pid
                        break
                if not vis_matched_place_id:
                    found_p = graph_retriever.get_place(det_name)
                    if found_p:
                        vis_matched_place_id = found_p.get("node_id")

        # Xác định đối tượng trọng tâm để sinh câu hỏi ngữ cảnh
        focus_name = None
        focus_cat = "DI_TICH"
        if vis_matched_place_id:
            matched_node = graph_retriever.get_place(vis_matched_place_id)
            if matched_node:
                focus_name = matched_node.get("name")
        if not focus_name:
            if img_info and img_info.get("name"):
                focus_name = img_info["name"]
                focus_cat = img_info.get("category", "KHAC")
            elif visual_matches:
                focus_name = visual_matches[0]["place_name"]

        if focus_name:
            norm_orig = strip_accents(query)
            if not query or len(query.strip()) < 8 or any(q in norm_orig for q in ["day la dau", "day la gi", "mon gi", "cho toi biet", "anh nay", "day o dau", "chup o dau"]):
                if "AM_THUC" in focus_cat:
                    query = f"Giới thiệu món {focus_name} trong ảnh và gợi ý những quán ăn ngon nổi tiếng nhất tại Huế để thưởng thức món này"
                else:
                    query = f"Giới thiệu di tích {focus_name} trong ảnh, nguồn gốc lịch sử, nét đặc sắc kiến trúc và gợi ý các địa điểm lân cận"
            else:
                query = f"Về {focus_name} trong ảnh: {query}"

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

    # 3. Bóc tách TẤT CẢ các địa danh xuất hiện trong câu hỏi (theo thứ tự xuất hiện qua alias_dict)

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
    pid_to_pos = {pid: pos for pos, pid in ordered_place_ids}

    # Nếu có địa danh khớp từ Visual Image RAG, ưu tiên đưa lên đầu extracted_place_ids
    if vis_matched_place_id and vis_matched_place_id not in extracted_place_ids:
        extracted_place_ids.insert(0, vis_matched_place_id)
        pid_to_pos[vis_matched_place_id] = 0

    # Nhận diện câu hỏi tổng quát về bãi biển / tắm biển / hải sản biển
    is_beach_query = any(b in norm_q for b in ["bai bien", "bien", "tam bien", "ngam bien"]) and not any(k in norm_q for k in ["bien hoa", "bien gioi"])
    if is_beach_query and not any(pid in extracted_place_ids for pid in ["beach_thuan_an", "beach_lang_co", "beach_canh_duong", "beach_hai_duong"]):
        for b_id in ["beach_thuan_an", "beach_lang_co", "beach_canh_duong", "beach_hai_duong"]:
            extracted_place_ids.append(b_id)

    # Nhận diện câu hỏi tìm địa điểm lân cận ('quanh X', 'gần X', 'trong bán kính Y km')
    is_nearby_query = any(k in norm_q for k in ["quanh", "xung quanh", "lan can", "ban kinh", "gan day", "gan do", "gan "])
    # Nếu hỏi quanh một địa danh mà có 'song huong' xuất hiện như cảnh quan, loại bỏ 'song huong' khỏi danh sách đích
    if is_nearby_query and "place_8882" in extracted_place_ids and len(extracted_place_ids) >= 2:
        extracted_place_ids = [pid for pid in extracted_place_ids if pid != "place_8882"]

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

    # A. ƯU TIÊN TUYỆT ĐỐI 1: Người dùng đề cập TỪ 2 ĐỊA DANH TRỞ LÊN và có ý định di chuyển (Từ A đi/sang/đến B):
    has_route_intent = any(w in norm_q for w in [
        "từ ", "tu ", "sang ", "đến ", "den ", "tới ", "toi ", "qua ", "đi ", "di ",
        "sau khi ", "xong ", "khoang cach", "bao xa", "may cay", "may km", "duong nao"
    ])
    if len(extracted_place_ids) >= 2 and has_route_intent:
        for pid in extracted_place_ids:
            p_data = graph_retriever.get_place(pid)
            if p_data:
                p_copy = dict(p_data)
                p_copy["query_pos"] = pid_to_pos.get(pid, 999)
                if not any(p.get("node_id") == pid for p in matched_places):
                    matched_places.append(p_copy)
        
        trace_steps.append({
            "step": "edge_traversal",
            "icon": "🛣️",
            "label": "Tuyến hành lang di chuyển A → B",
            "detail": f"Khớp lộ trình: {' → '.join(p.get('name', '') for p in matched_places[:3])}",
            "edge": "MULTI_POINT_ROUTE",
            "count": len(matched_places),
            "status": "found"
        })
    # B. ƯU TIÊN 2: Có CẢ địa danh mốc VÀ món ăn đặc sản (ví dụ: 'ngắm hoàng hôn ở Đồi Vọng Cảnh, trên đường về ghé quán bánh bèo', 'ăn bún bò gần Cầu Tràng Tiền'):
    elif target_place_id and target_dish:
        origin_place = graph_retriever.get_place(target_place_id)
        if origin_place:
            origin_copy = dict(origin_place)
            origin_copy["query_pos"] = pid_to_pos.get(target_place_id, 0)
            lat0, lng0 = origin_copy.get("latitude"), origin_copy.get("longitude")
            serving_places = graph_retriever.find_places_by_dish(target_dish, locality=locality or "Thành phố Huế", limit=20)
            if lat0 and lng0:
                for sp in serving_places:
                    if sp.get("latitude") and sp.get("longitude"):
                        sp["dist_to_origin"] = haversine_distance(lat0, lng0, sp["latitude"], sp["longitude"])
                serving_places.sort(key=lambda x: x.get("dist_to_origin", 999))

            # Đưa origin_place (mốc khởi hành ví dụ Đồi Vọng Cảnh) vào đầu danh sách làm mốc xuất phát
            if not any(p.get("node_id") == target_place_id for p in matched_places):
                matched_places.append(origin_copy)

            # Đưa các quán phục vụ món gần nhất vào matched_places (loại bỏ chính điểm mốc)
            for sp in serving_places[:5]:
                if sp.get("node_id") != target_place_id and not any(p.get("node_id") == sp.get("node_id") for p in matched_places):
                    sp_copy = dict(sp)
                    sp_copy["query_pos"] = 999
                    matched_places.append(sp_copy)

            # XAI trace: ghi lại quan hệ SERVES
            trace_steps.append({
                "step": "edge_traversal",
                "icon": "🍽️",
                "label": "Duyệt cạnh SERVES",
                "detail": f"Tìm thấy {len(matched_places)} quán phục vụ '{target_dish}' gần '{origin_place.get('name', '')}'",
                "edge": "SERVES",
                "count": len(matched_places),
                "status": "found" if matched_places else "empty"
            })
    # C. ƯU TIÊN 3: Nếu là câu hỏi tìm kiếm địa điểm LÂN CẬN chung quanh X (không chỉ định món ăn cụ thể):
    elif is_nearby_query and target_place_id:
        origin_place = graph_retriever.get_place(target_place_id)
        if origin_place:
            # Bóc tách bán kính km nếu người dùng ghi rõ (ví dụ: 'trong bán kính 2km')
            radius_km = 2.0
            import re
            km_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:km|cay|kilomet)', norm_q)
            if km_match:
                try:
                    radius_km = min(10.0, max(0.5, float(km_match.group(1))))
                except Exception:
                    pass

            nearby = graph_retriever.find_nearby_places(target_place_id, max_distance_km=radius_km, limit=6)
            nearby_map[target_place_id] = nearby
            
            # QUAN TRỌNG: Đưa origin_place lên ĐẦU matched_places để làm mốc trung tâm trên bản đồ
            matched_places.append(origin_place)

            for nb in nearby:
                nb_id = nb.get("node_id")
                if nb_id != target_place_id and nb_id != "place_8882" and nb not in matched_places:
                    matched_places.append(nb)

            trace_steps.append({
                "step": "edge_traversal",
                "icon": "📐",
                "label": "Duyệt cạnh NEAR_BY",
                "detail": f"{len(matched_places)} điểm lân cận '{origin_place.get('name', '')}' trong bán kính {radius_km}km",
                "edge": "NEAR_BY",
                "count": len(matched_places),
                "status": "found"
            })
    # C. Nếu người dùng đề cập TỪ 2 ĐỊA DANH TRỞ LÊN (ví dụ: 'Từ Đại Nội đi Chợ Đông Ba' hoặc hỏi về các bãi biển):
    elif len(extracted_place_ids) >= 2:
        for pid in extracted_place_ids:
            p_data = graph_retriever.get_place(pid)
            if p_data and p_data not in matched_places:
                matched_places.append(p_data)
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

    # Nếu có thực thể nhận diện từ ảnh, đảm bảo đưa vào danh sách địa điểm khớp ở vị trí đầu tiên (Index 0)
    if image_detected_info and image_detected_info.get("name"):
        det_name = image_detected_info["name"]
        norm_det = strip_accents(det_name)
        det_pid = alias_dict.get(norm_det)
        det_place = graph_retriever.get_place(det_pid) if det_pid else graph_retriever.get_place(det_name)
        if not det_place:
            vis_places = graph_retriever.search_places(det_name, locality=locality or "Thành phố Huế", limit=3)
            det_place = vis_places[0] if vis_places else None
        if det_place:
            det_id = det_place.get("node_id") or det_place.get("name")
            matched_places = [p for p in matched_places if (p.get("node_id") or p.get("name")) != det_id]
            matched_places.insert(0, det_place)

    # XAI: tổng kết bước KG retrieval
    trace_steps.append({
        "step": "kg_summary",
        "icon": "📊",
        "label": "Tổng kết Đồ thị Tri thức",
        "detail": f"{len(matched_places)} địa điểm, {sum(len(v) for v in nearby_map.values())} lân cận, {sum(len(v) for v in dishes_map.values())} món đặc sản",
        "status": "found" if matched_places else "empty"
    })

    return {
        "query": query,
        "image_detected": image_detected_info,
        "visual_matches": visual_matches,
        "visual_confidence": visual_confidence,
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

    # 0. Nếu là câu hỏi có ảnh đính kèm và đã có thực thể nhận diện hoặc địa điểm trong KG:
    if state.get("image_base64") and (has_places or state.get("visual_matches") or state.get("image_detected")):
        trace_steps.append({
            "step": "routing_decision",
            "icon": "🎯",
            "label": "Router → Tri thức Thị giác & Di sản Nội bộ",
            "detail": "Nhận diện ảnh thành công → đối sánh và phản hồi từ CSDL tri thức Cố đô",
            "decision": "local_knowledge",
            "status": "confident"
        })
        return "node_generate_response"

    # Các từ khóa hỏi về thông tin thời gian thực ngoài phạm vi dữ liệu tĩnh (thời tiết, vé máy bay)
    realtime_triggers = [
        "thoi tiet", "thời tiết", "ve may bay", "vé máy bay", 
        "nhiet do", "nhiệt độ", "bao nhieu do", "mưa khong", "mưa không", "dự báo thời tiết"
    ]
    is_realtime_query = any(t in norm_q or t in query_lower for t in realtime_triggers)
    if is_realtime_query:
        trace_steps.append({
            "step": "routing_decision",
            "icon": "🌐",
            "label": "Router → Web Search Fallback",
            "detail": "Câu hỏi thời tiết / vé máy bay thời gian thực → chuyển sang DuckDuckGo",
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

    # 0. Ngữ cảnh đối sánh thị giác từ Visual Image RAG (ChromaDB & CLIP ViT-B/32)
    visual_matches = state.get("visual_matches") or []
    visual_confidence = state.get("visual_confidence", 0.0)
    if visual_matches and visual_confidence >= 0.60:
        top_v = visual_matches[0]
        vis_context = f"""=== KẾT QUẢ ĐỐI SÁNH THỊ GIÁC VISUAL IMAGE RAG (CHROMADB & CLIP ViT-B/32) ===
- Địa danh khớp chính xác: {top_v['place_name']} ({top_v.get('sub_location', '')})
- Định danh đồ thị (Place ID): {top_v['place_id']}
- Điểm tương đồng Cosine: {top_v.get('confidence_pct', round(visual_confidence * 100, 1))}% (Độ tin cậy cao >= 60%)
- Căn cứ đối sánh: Vector thị giác 512 chiều được so khớp Cosine với kho ảnh mẫu di sản văn hóa Cố đô Huế trong ChromaDB."""
        context_blocks.append(vis_context)

    # Bổ sung thông tin nhận diện đối tượng từ Vision Model nếu có
    if state.get("image_detected"):
        det = state["image_detected"]
        img_context = f"""=== KẾT QUẢ NHẬN DIỆN THỊ GIÁC VISION MODEL ===
- Đối tượng di sản / ẩm thực nhận diện trong ảnh: {det.get('name')} ({det.get('category', 'DI_TICH')})
- Đặc điểm nhận dạng: {det.get('description', '')}"""
        context_blocks.append(img_context)

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
    norm_q_no_accent = strip_accents(norm_q)
    nav_keywords = [
        "chỉ đường", "chi duong", "đường đi", "duong di", "đi đến", "di den", 
        "làm sao để đi", "lam sao de di", "cách đi", "cach di", "dẫn đường", "dan duong",
        "hướng dẫn đường", "huong dan duong", "lộ trình", "lo trinh", "chỉ lối", "chi loi",
        "đi đường nào", "di duong nao", "đi như thế nào", "di nhu the nao", "đi thế nào", "di the nao",
        "khoảng bao xa", "khoang bao xa", "bao xa", "mất bao xa", "mat bao xa",
        "mấy cây số", "may cay so", "mấy km", "may km", "mấy cây", "may cay",
        "cách mấy", "cach may", "lối đi", "loi di", "hướng đi", "huong di",
        "đi ra", "di ra", "đi qua", "di qua", "đi sang", "di sang", "đi tới", "di toi"
    ]
    has_from = any(w in norm_q for w in ["từ ", "tu ", "xuất phát từ", "khoi hanh tu"]) or any(w in norm_q_no_accent for w in ["tu ", "xuat phat tu"])
    has_to = any(w in norm_q for w in ["đi ", "di ", "đến ", "den ", "tới ", "toi ", "sang ", "qua "]) or any(w in norm_q_no_accent for w in ["di ", "den ", "toi ", "sang ", "qua "])
    is_nav = any(k in norm_q for k in nav_keywords) or any(k in norm_q_no_accent for k in nav_keywords) or (has_from and has_to)

    dish_rule = ""
    if target_dish:
        dish_rule = f"""
4. YÊU CẦU ĐẶC BIỆT VỀ MÓN ĂN:
   - Du khách đang hỏi về món: "{target_dish}".
   - Bạn CHỈ ĐƯỢC PHÉP giới thiệu các quán ăn phục vụ món {target_dish} từ danh sách ngữ cảnh.
   - Tuyệt đối KHÔNG ĐƯỢC nhắc đến các món ăn hay quán ăn khác (như cơm hến, bánh bèo, chè...) không liên quan đến {target_dish}."""

    # Tính toán chính xác cự ly đường bộ khi có yêu cầu Chỉ đường (Ground Truth Navigation)
    nav_rule = ""
    nav_route_info = None
    if is_nav and matched_places:
        origin_p = None
        dest_p = None
        has_origin_context = any(w in norm_q for w in [
            "từ ", "tu ", "ở ", "o ", "tại ", "tai ", "sau khi ", "xem xong ", 
            "tham quan xong ", "ngắm ", "ngam ", "tren duong ve", "trên đường về", "gần ", "gan "
        ]) or any(w in norm_q_no_accent for w in ["tu ", "o ", "tai ", "sau khi ", "ngam ", "tren duong ve", "gan "])
        
        if len(matched_places) >= 2 and has_origin_context:
            p0 = matched_places[0]
            p1 = matched_places[1]
            pos0 = p0.get("query_pos", 0)
            pos1 = p1.get("query_pos", 1)

            # Tìm vị trí của từ "từ " hoặc "tu " trong câu hỏi
            tu_idx = norm_q_no_accent.find("tu ")
            if tu_idx != -1:
                d0 = (pos0 - tu_idx) if pos0 >= tu_idx else 9999
                d1 = (pos1 - tu_idx) if pos1 >= tu_idx else 9999
                # Nếu p1 đứng ngay sau "từ " (ví dụ: 'chỉ đường từ Cầu Tràng Tiền đến Quán Bà Đỏ')
                if d1 < d0 and d1 < 25:
                    origin_p = p1
                    dest_p = p0
                else:
                    origin_p = p0
                    dest_p = p1
            else:
                origin_p = p0
                dest_p = p1
        elif matched_places:
            dest_p = matched_places[0]
            user_lat = state.get("user_lat")
            user_lng = state.get("user_lng")
            if user_lat and user_lng:
                origin_p = {"name": "Vị trí của bạn", "latitude": user_lat, "longitude": user_lng}
            else:
                origin_p = {"name": "Trung tâm TP Huế (Cầu Tràng Tiền)", "latitude": 16.4674, "longitude": 107.5905}

        if origin_p and dest_p and origin_p.get("latitude") and dest_p.get("latitude"):
            lat1, lng1 = float(origin_p["latitude"]), float(origin_p["longitude"])
            lat2, lng2 = float(dest_p["latitude"]), float(dest_p["longitude"])
            h_dist = haversine_distance(lat1, lng1, lat2, lng2)

            # 1. Truy vấn nhanh OSRM để lấy cự ly mặt đường thực tế theo mạng lưới giao thông Cố đô
            road_dist = None
            dur_drive = None
            try:
                import urllib.request
                import json
                osrm_url = f"https://router.project-osrm.org/route/v1/driving/{lng1},{lat1};{lng2},{lat2}?overview=false"
                req_osrm = urllib.request.Request(osrm_url, headers={"User-Agent": "HueSpatialRAG/1.0"})
                with urllib.request.urlopen(req_osrm, timeout=1.2) as resp:
                    if resp.status == 200:
                        data_osrm = json.loads(resp.read().decode("utf-8"))
                        if data_osrm.get("code") == "Ok" and data_osrm.get("routes"):
                            r0 = data_osrm["routes"][0]
                            road_dist = round(r0["distance"] / 1000.0, 1)
                            dur_drive = max(2, round(r0["duration"] / 60.0))
            except Exception:
                pass

            # 2. Fallback: Hệ số mạng lưới giao thông đường bộ nội đô Huế uốn lượn qua sông & tường thành (~1.6x)
            if road_dist is None:
                road_dist = max(0.8, round(h_dist * 1.6, 1))
                dur_drive = max(2, round(road_dist * 2.5))

            dur_walk = max(8, round(road_dist * 12))

            nav_route_info = {
                "distance_km": road_dist,
                "duration_min": dur_drive,
                "duration_walk": dur_walk,
                "origin_name": origin_p.get("name"),
                "dest_name": dest_p.get("name"),
                "origin": {
                    "name": origin_p.get("name"),
                    "latitude": float(lat1),
                    "longitude": float(lng1),
                    "address": origin_p.get("street_address", origin_p.get("address", "Thành phố Huế")),
                    "category": origin_p.get("category", "Attraction")
                },
                "destination": {
                    "name": dest_p.get("name"),
                    "latitude": float(lat2),
                    "longitude": float(lng2),
                    "address": dest_p.get("street_address", dest_p.get("address", "Thành phố Huế")),
                    "category": dest_p.get("category", "Attraction")
                }
            }

            nav_rule = f"""
5. DỮ LIỆU ĐỊNH VỊ KHÔNG GIAN BẮT BUỘC (GROUND TRUTH ROUTING):
   - Tuyến đường: Từ **{origin_p.get('name')}** đến **{dest_p.get('name')}**.
   - Khoảng cách đường bộ thực tế: ~{road_dist} km.
   - Thời gian di chuyển: khoảng {dur_drive} phút (xe máy / ô tô) hoặc {dur_walk} phút (đi bộ).
   - NGUYÊN TẮC BẮT BUỘC: Khi trả lời về khoảng cách hay thời gian di chuyển, BẮT BUỘC dùng đúng con số ~{road_dist} km và thời gian trên. TUYỆT ĐỐI KHÔNG tự bịa đặt hay ước lượng con số khác! Hãy nhắc du khách xem lộ trình chi tiết đã được vẽ trên bản đồ bên cạnh và bấm 'Mở Google Maps' để nghe dẫn đường trực tiếp."""

    # Cá nhân hóa theo Hồ sơ Gu Du Lịch của Người dùng
    preferences = state.get("preferences") or {}
    pref_rules = []
    if preferences:
        styles = preferences.get("styles") or []
        if styles:
            style_str = ", ".join(styles)
            pref_rules.append(f"- Phong cách ưa thích: {style_str}. Ưu tiên các điểm đến và trải nghiệm đúng gu này.")
        dietary = preferences.get("dietary") or []
        if "Ăn chay" in dietary:
            pref_rules.append("- Khẩu vị: Du khách ĂN CHAY. Tuyệt đối ưu tiên các quán chay, món chay, danh lam chùa chiền thanh tịnh ở Cố đô.")
        if "Không ăn cay / Ít ớt" in dietary:
            pref_rules.append("- Khẩu vị: Du khách KHÔNG ĂN CAY / ÍT ỚT. Nhắc nhở dặn quán làm ít cay, không bỏ ớt chưng sa tế đậm.")
        if "Ăn cay chuẩn Huế" in dietary:
            pref_rules.append("- Khẩu vị: Du khách thích ĂN CAY ĐẬM ĐÀ, chuẩn phong vị cay xé lưỡi đặc trưng của xứ Huế.")
        if "Dị ứng hải sản" in dietary:
            pref_rules.append("- Dị ứng: Du khách DỊ ỨNG HẢI SẢN. Cảnh báo tránh các món tôm cá, mắm ruốc truyền thống nếu có thể.")
        party = preferences.get("party")
        if party:
            pref_rules.append(f"- Nhóm đồng hành: {party}. Điều chỉnh nhịp độ di chuyển và không gian phù hợp với nhóm này.")
        transport = preferences.get("transport")
        if transport:
            pref_rules.append(f"- Phương tiện di chuyển: {transport}.")

    pref_section = ""
    if pref_rules:
        pref_section = "\n\n6. CÁ NHÂN HÓA THEO GU DU LỊCH CỦA DU KHÁCH:\n" + "\n".join(pref_rules)

    system_prompt = f"""Bạn là Hướng dẫn viên & Trợ lý Du lịch Cố đô Huế thông minh, thân thiện, mang phong cách mến khách và nhã nhặn đặc trưng của người dân xứ Huế.

Nguyên tắc trả lời bắt buộc:
1. VĂN PHONG TỰ NHIÊN, LỊCH SỰ, ĐÚNG MỰC:
   - Xưng hô chuẩn mực: Xưng "em" hoặc "Trợ lý Cố đô", gọi người dùng là "bạn" hoặc "quý khách".
   - Tuyệt đối KHÔNG tự tiện dùng các đại từ xưng hô gia đình kỳ quặc như "chị/mẹ", "cô/bác", "ông/bà".
   - Mở đầu nhẹ nhàng, lịch thiệp ("Dạ chào bạn...", "Dạ, em xin gợi ý với bạn...", "Chào bạn...").
   - Tuyệt đối KHÔNG dùng các câu cứng nhắc, máy móc như: "Dựa trên dữ liệu Đồ thị Tri thức...", "Hệ thống đã xác định thành công...".
   - Diễn đạt 100% bằng tiếng Việt trong sáng, gần gũi như một người bạn đồng hành bản địa tại Huế.

2. NẾU DU KHÁCH HỎI CÁC ĐIỂM QUANH / GẦN MỘT ĐỊA DANH (VÍ DỤ "QUANH CHÙA THIÊN MỤ", "GẦN ĐẠI NỘI"):
   - Tuyệt đối KHÔNG giới thiệu lại chính địa danh mốc đó làm điểm tham quan lân cận (không gợi ý Chùa Thiên Mụ khi người ta đang hỏi quanh Chùa Thiên Mụ).
   - Sông Hương là dòng sông cảnh quan chung, KHÔNG giới thiệu "Perfume River / Sông Hương" như một điểm đến có "Giá: Bình dân" độc lập. Thay vào đó, hãy gợi ý các điểm ngắm sông cụ thể xung quanh như: Nhà vườn Bến Xuân, Bến thuyền chùa Thiên Mụ, Đồi Hà Khê, Văn Miếu Huế, các quán cafe/nhà hàng ngắm cảnh bờ sông trong ngữ cảnh.

3. VỀ BÃI BIỂN VÀ HẢI SẢN TẠI THỪA THIÊN HUẾ:
   - Thừa Thiên Huế có các bãi biển đẹp nổi tiếng gồm: Bãi biển Thuận An (cách TP Huế ~15km, nổi tiếng tắm biển và hải sản tươi rói), Vịnh & Bãi biển Lăng Cô / Đầm Lập An (dưới chân đèo Hải Vân, vịnh biển đẹp bậc nhất thế giới, nức tiếng hải sản tôm hùm, hàu đầm), Bãi biển Cảnh Dương (cắm trại, bãi cát thoai thoải), Bãi biển Hải Dương (bờ kè bãi đá sống ảo cực đẹp).
   - Sông Hương là SÔNG NƯỚC NGỌT CHẢY TRONG LÒNG THÀNH PHỐ HUẾ, TUYỆT ĐỐI KHÔNG CÓ BÃI BIỂN NÀO BÊN BỜ SÔNG HƯƠNG. Cấm tuyệt đối không được bịa đặt hay nói "bãi biển bên bờ sông Hương".
   - Khi du khách hỏi về tắm biển hoặc ăn hải sản ở Huế, hãy giới thiệu các bãi biển Thuận An, Lăng Cô, Cảnh Dương, Hải Dương và các món hải sản tươi sống đặc trưng.

4. NẾU DU KHÁCH HỎI ĐƯỜNG ĐI / LỘ TRÌNH:
   - Trả lời ngắn gọn (1-2 câu), nêu rõ khoảng cách đường bộ và thời gian di chuyển chính xác từ mục DỮ LIỆU ĐỊNH VỊ KHÔNG GIAN BẮT BUỘC.
   - Thông báo tuyến đường đã được định vị và vẽ trực tiếp trên bản đồ bên cạnh, gợi ý du khách xem cự ly và bấm nút Google Maps bên dưới để nghe dẫn đường khi di chuyển.

5. ĐỊNH DẠNG TÊN ĐỊA DANH BẰNG CHỮ IN ĐẬM:
   - Khi nhắc đến tên các địa điểm, quán ăn, danh lam thắng cảnh, hãy IN ĐẬM tên địa danh bằng cú pháp **Tên Địa Danh** (ví dụ: **Bãi biển Thuận An**, **Nhà vườn Bến Xuân**, **Quán Bún bò Mụ Rơi**...) để hệ thống tự động ghim vị trí lên bản đồ cho du khách.{dish_rule}{nav_rule}{pref_section}"""

    image_base64 = state.get("image_base64")
    if image_base64:
        system_prompt += """\n
6. PHÂN TÍCH VÀ BÌNH LUẬN HÌNH ẢNH THỰC TẾ:
   - Du khách đã tải lên một bức ảnh thực tế. Hãy trực tiếp quan sát và xác nhận hình ảnh đối tượng du khách đã chụp (tên di tích / danh thắng / món ăn đặc sản).
   - Đưa ra những nhận xét tinh tế, sinh động về góc chụp, kiến trúc, màu sắc hoặc hương vị/cách thưởng thức món ăn trong ảnh.
   - Kết hợp mượt mà với DỮ LIỆU ĐỒ THỊ TRI THỨC (tọa độ GPS, lịch sử văn hóa, giá vé/giờ mở cửa hoặc quán ăn lân cận) để cung cấp câu trả lời trọn vẹn nhất.
   - Nhắc đến các địa danh/quán ăn bằng chữ IN ĐẬM **Tên Địa Danh** để hệ thống tự động ghim vị trí lên bản đồ cho du khách.
"""

    user_prompt = f"""[NGỮ CẢNH HỆ THỐNG]:
{full_context}

[CÂU HỎI CỦA DU KHÁCH]:
{query}

[CÂU TRẢ LỜI CỦA BẠN]:"""

    try:
        if image_base64:
            clean_b64 = image_base64.split(",")[-1] if "," in image_base64 else image_base64
            human_msg = HumanMessage(content=[
                {"type": "text", "text": user_prompt},
                {"type": "image_url", "image_url": f"data:image/jpeg;base64,{clean_b64}"}
            ])
        else:
            human_msg = HumanMessage(content=user_prompt)

        response = llm.invoke([
            SystemMessage(content=system_prompt),
            human_msg
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
        elif image_base64 and visual_matches and visual_confidence >= 0.70:
            top_v = visual_matches[0]
            matched_p = matched_places[0] if matched_places else {}
            desc = matched_p.get("description") or matched_p.get("desc") or top_v.get("caption", "")
            addr = matched_p.get("address") or matched_p.get("street_address") or "Thành phố Huế"
            sim_pct = top_v.get("confidence_pct", round(visual_confidence * 100, 1))

            nearby_names = []
            for p_sub in matched_places[1:4]:
                if p_sub.get("name"):
                    nearby_names.append(f"**{p_sub.get('name')}**")
            nearby_text = f"\n\n📍 **Gợi ý điểm đến lân cận thuận đường:** {', '.join(nearby_names)}." if nearby_names else ""

            answer_text = (
                f"Dạ chào bạn! Qua phân tích đặc trưng thị giác (Visual Image RAG với độ tương đồng Cosine **{sim_pct}%**), "
                f"em xác nhận bức ảnh của bạn được chụp tại **{top_v['place_name']}** Cố đô Huế!\n\n"
                f"🏛️ **Thông tin di sản:** {desc}\n"
                f"📍 **Địa chỉ:** {addr}{nearby_text}\n\n"
                f"Em đã ghim vị trí chính xác lên bản đồ di sản bên cạnh để bạn dễ dàng định vị và lên kế hoạch tham quan nhé!"
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
        elif image_base64 and matched_places:
            places_str = ", ".join([f"**{p.get('name', '')}**" for p in matched_places[:3]])
            answer_text = (
                f"Dạ, qua hình ảnh bạn gửi, em nhận diện và đối chiếu với dữ liệu di sản Cố đô Huế: {places_str}. "
                f"Em đã định vị các địa điểm này trên bản đồ tương tác để bạn tiện theo dõi và khám phá nhé!"
            )
        elif image_base64:
            answer_text = (
                "Dạ, em đã tiếp nhận hình ảnh của bạn và đối chiếu với bản đồ di sản Cố đô Huế. "
                "Bạn có thể xem các điểm tham quan và quán ăn lân cận ngay trên bản đồ tương tác nhé!"
            )
        else:
            answer_text = "Dạ, em đã tìm thấy các thông tin phù hợp cho câu hỏi của bạn tại Cố đô Huế. Bạn có thể xem chi tiết trên bản đồ tương tác nhé!"

    # XAI trace: ghi lại bước sinh phản hồi cuối cùng
    trace_steps = state.get("graph_trace", [])
    if pref_rules:
        trace_steps.append({
            "step": "user_personalization",
            "icon": "✨",
            "label": "Cá nhân hóa Gu du lịch",
            "detail": f"Đã áp dụng {len(pref_rules)} tiêu chí khẩu vị & phong cách du khách",
            "status": "applied"
        })
    trace_steps.append({
        "step": "llm_generation",
        "icon": "🤖",
        "label": f"Sinh phản hồi ({OLLAMA_MODEL.upper()} GPU)",
        "detail": f"LLM tổng hợp từ {len(context_blocks)} khối ngữ cảnh → câu trả lời tự nhiên",
        "model": OLLAMA_MODEL,
        "status": "done"
    })

    return {
        "formatted_context": full_context,
        "final_answer": answer_text,
        "route_taken": route_taken,
        "graph_trace": trace_steps,
        "nav_route_info": nav_route_info
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
    print(f"🤖 KHỞI CHẠY LANGGRAPH SPATIAL GRAPHRAG AGENT ({OLLAMA_MODEL.upper()})")
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
