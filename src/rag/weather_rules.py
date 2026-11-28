# -*- coding: utf-8 -*-
"""
QUY TẮC THÍCH ỨNG THỜI TIẾT (OPEN-METEO + MÃ WMO) DÙNG CHUNG CHO AGENTIC RAG VÀ SPATIAL ITINERARY PLANNER

weather_context = {temp, humidity, precipitation, weather_code, condition_vi}
Phân loại 4 mức:
  1. Quang đãng, mát mẻ   : WMO 0/1/2 và T <= 33, P == 0
  2. Nắng nóng gay gắt    : T > 33, P == 0 (trời không mưa)
  3. Mưa dầm đặc trưng    : WMO 51..67 hoặc 0 < P < 5
  4. Mưa rào / dông sét   : WMO 80..99 hoặc P >= 5
  0. Trung tính (nhiều mây, sương mù...): không điều chỉnh gì.
"""
import math
import re
from typing import Any, Dict, List, Optional

from src.graph.graph_retriever import strip_accents

HOT_TEMP_C = 33.0
HEAVY_RAIN_MM = 5.0

LEVEL_NEUTRAL = 0
LEVEL_CLEAR = 1
LEVEL_HOT = 2
LEVEL_DRIZZLE = 3
LEVEL_STORM = 4

# Chiến lược thích ứng theo từng mức (vi / en)
LEVEL_RULES: Dict[int, Dict[str, Any]] = {
    LEVEL_CLEAR: {
        "key": "clear_mild",
        "label_vi": "Trời quang đãng, mát mẻ",
        "label_en": "Clear and mild",
        "strategy_vi": "Thời tiết thuận lợi, ưu tiên các quần thể di tích ngoài trời và danh thắng.",
        "strategy_en": "Favourable weather: prioritise open-air heritage complexes and scenic spots.",
        "suggest": ["Đại Nội", "Chùa Thiên Mụ", "Đồi Vọng Cảnh", "Lăng Khải Định"],
    },
    LEVEL_HOT: {
        "key": "scorching_heat",
        "label_vi": "Nắng nóng gay gắt",
        "label_en": "Scorching heat",
        "strategy_vi": "Hạn chế di chuyển ngoài trời lúc trưa; ưu tiên di tích râm mát hoặc không gian trưng bày trong nhà, "
                       "kết hợp cà phê ven sông Hương và chè thanh nhiệt.",
        "strategy_en": "Avoid outdoor travel around midday; favour shaded or indoor exhibition venues, riverside cafés and cooling chè desserts.",
        "suggest": ["Cung An Định", "Bảo tàng Cổ vật Cung đình", "Nhà hát Duyệt Thị Đường"],
    },
    LEVEL_DRIZZLE: {
        "key": "persistent_rain",
        "label_vi": "Mưa dầm đặc trưng",
        "label_en": "Persistent drizzle",
        "strategy_vi": "Nhắc mang ô dù; ưu tiên điểm có mái che, hành lang hoặc bảo tàng và các món ẩm thực nóng ấm.",
        "strategy_en": "Bring an umbrella; favour sheltered sites, covered corridors or museums, and warm Huế dishes.",
        "suggest": ["Đại Nội", "Bảo tàng Cổ vật Cung đình", "Bún bò Huế", "Bánh canh", "Bánh khoái"],
    },
    LEVEL_STORM: {
        "key": "heavy_rain_storm",
        "label_vi": "Mưa rào / dông sét",
        "label_en": "Heavy rain / thunderstorm",
        "strategy_vi": "CẢNH BÁO AN TOÀN: tránh các điểm đồi núi, sông nước ngoài trời (Đồi Vọng Cảnh, Đầm Chuồn, Bạch Mã, bến thuyền); "
                       "chuyển sang di tích trong nhà và ẩm thực nóng ấm.",
        "strategy_en": "SAFETY WARNING: avoid open hills and waterfront sites (Vong Canh Hill, Dam Chuon, Bach Ma, boat docks); "
                       "move to indoor heritage venues and warm cuisine.",
        "suggest": ["Bảo tàng Cổ vật Cung đình", "Cung An Định", "Bún bò Huế", "Bánh khoái"],
    },
}

AVOID_IN_STORM = ["Đồi Vọng Cảnh", "Đầm Chuồn", "Bạch Mã", "Bến thuyền"]

_WARM_DISH_TOKENS = ("bun bo", "banh canh", "banh khoai")

_FLIGHT_NEWS_TOKENS = (
    "ve may bay", "chuyen bay", "flight", "san bay", "airport", "tin tuc", "news", "bao so",
)
_FUTURE_TOKENS = (
    "ngay mai", "tomorrow", "hom sau", "tuan sau", "tuan toi", "cuoi tuan", "next week", "weekend",
    "mai co mua", "may ngay toi",
)
_WEATHER_TOKENS = (
    "thoi tiet", "nhiet do", "bao nhieu do", "mua khong", "co mua", "troi mua", "troi nang",
    "weather", "forecast", "temperature", "is it raining", "will it rain",
)
_TRAVEL_RECOMMEND_TOKENS = (
    "tham quan", "di dau", "nen di", "choi gi", "cho nao", "diem nao", "dia diem",
    "di tich", "bao tang", "lich trinh", "tour",
    "an gi", "an uong", "mon gi", "quan an", "nha hang", "ca phe", "cafe", "dac san", "nen an",
    "khach san", "luu tru", "homestay", "resort", "nha nghi", "villa", "hostel",
    "hotel", "lodging", "accommodation", "where to stay",
    "goi y", "tu van", "phu hop", "hop voi",
    "sightseeing", "visit", "where to go", "itinerary", "places to", "things to do",
    "eat", "food", "dish", "restaurant", "recommend", "suggest", "suitable",
)
_TRAVEL_RECOMMEND_RE = re.compile(r"\b(?:" + "|".join(_TRAVEL_RECOMMEND_TOKENS) + r")\b")
_INDOOR_HUE_FALLBACKS = ("Cung An Định", "Chợ Đông Ba", "Cà Phê Muối Nguyễn Huệ")
_FOOD_QUERY_TOKENS = ("an gi", "an uong", "mon gi", "mon", "quan an", "am thuc", "dac san", "food", "eat", "dish", "restaurant")
_FOOD_QUERY_RE = re.compile(r"\b(?:" + "|".join(_FOOD_QUERY_TOKENS) + r")\b")


def _num(raw: Dict[str, Any], key: str, lo: float, hi: float) -> Optional[float]:
    val = raw.get(key)
    if val is None or isinstance(val, bool):
        return None
    try:
        f = float(val)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(f):
        return None
    return max(lo, min(hi, f))


def normalize_weather_context(raw: Any) -> Optional[Dict[str, Any]]:
    """Làm sạch ngữ cảnh thời tiết do client gửi: chỉ giữ số đã ép kiểu/kẹp biên, bỏ mọi chuỗi tự do."""
    if not isinstance(raw, dict):
        return None
    temp = _num(raw, "temp", -30.0, 60.0)
    humidity = _num(raw, "humidity", 0.0, 100.0)
    precip = _num(raw, "precipitation", 0.0, 500.0)
    code_f = _num(raw, "weather_code", 0.0, 99.0)
    code = int(code_f) if code_f is not None else None
    if temp is None and code is None and precip is None:
        return None
    return {
        "temp": temp,
        "humidity": humidity,
        "precipitation": precip if precip is not None else 0.0,
        "weather_code": code,
    }


def classify_weather(raw: Any) -> Optional[Dict[str, Any]]:
    """Trả về {level, key, label_vi, label_en, strategy_*, suggest, context} hoặc None nếu không có dữ liệu."""
    ctx = normalize_weather_context(raw)
    if ctx is None:
        return None
    code, temp, precip = ctx["weather_code"], ctx["temp"], ctx["precipitation"]

    if (code is not None and 80 <= code <= 99) or precip >= HEAVY_RAIN_MM:
        level = LEVEL_STORM
    elif (code is not None and 51 <= code <= 67) or 0 < precip < HEAVY_RAIN_MM:
        level = LEVEL_DRIZZLE
    elif precip == 0 and temp is not None and temp > HOT_TEMP_C and (code is None or code in (0, 1)):
        level = LEVEL_HOT
    elif precip == 0 and code in (0, 1, 2) and (temp is None or temp <= HOT_TEMP_C):
        level = LEVEL_CLEAR
    else:
        level = LEVEL_NEUTRAL

    if level == LEVEL_NEUTRAL:
        return {
            "level": LEVEL_NEUTRAL, "key": "neutral",
            "label_vi": "Thời tiết bình thường", "label_en": "Ordinary weather",
            "strategy_vi": "", "strategy_en": "", "suggest": [], "context": ctx,
        }
    rule = LEVEL_RULES[level]
    return {"level": level, **rule, "suggest": list(rule["suggest"]), "context": ctx}


def wmo_label(code: Optional[int], lang: str = "vi") -> str:
    vi = lang != "en"
    if code is None:
        return "không rõ" if vi else "unknown"
    if code == 0:
        return "trời quang" if vi else "clear sky"
    if code in (1, 2):
        return "ít mây / mây rải rác" if vi else "mainly clear / partly cloudy"
    if code == 3:
        return "nhiều mây" if vi else "overcast"
    if code in (45, 48):
        return "sương mù" if vi else "fog"
    if 51 <= code <= 57:
        return "mưa phùn" if vi else "drizzle"
    if 61 <= code <= 67:
        return "có mưa" if vi else "rain"
    if 80 <= code <= 82:
        return "mưa rào" if vi else "rain showers"
    if 95 <= code <= 99:
        return "dông sét" if vi else "thunderstorm"
    return "thay đổi" if vi else "variable"


def is_flight_or_future_weather(query: str) -> bool:
    """Câu hỏi về vé máy bay, tin tức hoặc dự báo thời tiết ngày khác."""
    q = strip_accents((query or "").lower())
    return any(t in q for t in _FLIGHT_NEWS_TOKENS) or any(t in q for t in _FUTURE_TOKENS)


def is_travel_recommendation_query(query: str) -> bool:
    """Câu hỏi xin gợi ý điểm tham quan, ăn uống hoặc lịch trình (kể cả có nhắc thời tiết)."""
    q = strip_accents((query or "").lower())
    return bool(_TRAVEL_RECOMMEND_RE.search(q))


def is_weather_question(query: str) -> bool:
    """Câu hỏi thuần về thời tiết Huế HIỆN TẠI (loại trừ vé máy bay, tin tức, dự báo và gợi ý đi đâu/ăn gì)."""
    q = strip_accents((query or "").lower())
    if not any(t in q for t in _WEATHER_TOKENS):
        return False
    if is_flight_or_future_weather(q) or is_travel_recommendation_query(q):
        return False
    return True


def get_weather_kg_seeds(raw: Any, query: str) -> List[str]:
    """Danh sách tên địa danh/món ăn ưu tiên truy xuất KG cho câu hỏi gợi ý mở theo thời tiết."""
    info = classify_weather(raw)
    if info is None:
        return []
    seeds = list(info.get("suggest") or LEVEL_RULES[LEVEL_CLEAR]["suggest"])
    if info["level"] in (LEVEL_NEUTRAL, LEVEL_HOT, LEVEL_DRIZZLE, LEVEL_STORM):
        for extra in _INDOOR_HUE_FALLBACKS:
            if extra not in seeds:
                seeds.append(extra)
    q = strip_accents((query or "").lower())
    if _FOOD_QUERY_RE.search(q) and info["level"] in (LEVEL_CLEAR, LEVEL_HOT, LEVEL_NEUTRAL):
        for dish in ("Bún bò Huế", "Cơm hến"):
            if dish not in seeds:
                seeds.append(dish)
    return seeds


def is_warm_dish(name: str) -> bool:
    n = strip_accents((name or "").lower())
    return any(t in n for t in _WARM_DISH_TOKENS)


def _fmt_ctx_line(ctx: Dict[str, Any], lang: str) -> str:
    parts: List[str] = []
    if ctx.get("temp") is not None:
        parts.append(f"{ctx['temp']:.0f}°C")
    if ctx.get("humidity") is not None:
        parts.append(f"{'humidity' if lang == 'en' else 'độ ẩm'} {ctx['humidity']:.0f}%")
    parts.append(f"{'precipitation' if lang == 'en' else 'lượng mưa'} {ctx['precipitation']:.1f} mm")
    parts.append(wmo_label(ctx.get("weather_code"), lang))
    return ", ".join(parts)


def build_weather_prompt_section(raw: Any, lang: str = "vi") -> str:
    """Đoạn bổ sung cho system_prompt; trả về chuỗi rỗng nếu không có dữ liệu thời tiết."""
    info = classify_weather(raw)
    if info is None:
        return ""
    ctx_line = _fmt_ctx_line(info["context"], lang)
    if info["level"] == LEVEL_NEUTRAL:
        if lang == "en":
            return f"\n\n8. REAL-TIME WEATHER (Open-Meteo): {ctx_line}. Mention it only if relevant; never invent other weather figures."
        return f"\n\n8. THỜI TIẾT THỜI GIAN THỰC (Open-Meteo): {ctx_line}. Chỉ nhắc khi liên quan; không bịa số liệu thời tiết khác."
    suggest = ", ".join(info["suggest"])
    if lang == "en":
        extra = f" AVOID: {', '.join(AVOID_IN_STORM)}." if info["level"] == LEVEL_STORM else ""
        return (
            f"\n\n8. REAL-TIME WEATHER ADAPTATION (Open-Meteo, WMO):\n"
            f"   - Current Huế weather: {ctx_line}. Scenario: {info['label_en']}.\n"
            f"   - Strategy: {info['strategy_en']} Preferred suggestions: {suggest}.{extra}\n"
            f"   - Only adapt suggestions and briefly mention this weather when the question involves sightseeing, dining, transport or itinerary planning (skip weather talk for pure history/ticket-price facts). Use ONLY the figures above; do not invent other weather data."
        )
    extra = f" TRÁNH: {', '.join(AVOID_IN_STORM)}." if info["level"] == LEVEL_STORM else ""
    return (
        f"\n\n8. THÍCH ỨNG THỜI TIẾT THỜI GIAN THỰC (Open-Meteo, mã WMO):\n"
        f"   - Thời tiết Huế hiện tại: {ctx_line}. Kịch bản: {info['label_vi']}.\n"
        f"   - Chiến lược: {info['strategy_vi']} Gợi ý ưu tiên: {suggest}.{extra}\n"
        f"   - Chỉ điều chỉnh gợi ý và nhắc ngắn gọn thời tiết này khi câu hỏi liên quan đến tham quan, ăn uống, di chuyển hoặc lập lịch trình (không chèn lan man nếu khách chỉ hỏi lịch sử hay giá vé). CHỈ dùng đúng số liệu ở trên, không bịa số liệu thời tiết khác."
    )


def build_weather_answer(raw: Any, lang: str = "vi") -> Optional[str]:
    """Câu trả lời trực tiếp bằng số liệu thực cho câu hỏi 'thời tiết Huế bây giờ thế nào?'."""
    info = classify_weather(raw)
    if info is None:
        return None
    ctx_line = _fmt_ctx_line(info["context"], lang)
    names = [f"**{n}**" for n in info["suggest"]]
    if lang == "en":
        text = f"Current weather in Huế (live Open-Meteo data): {ctx_line}."
        if info["level"] != LEVEL_NEUTRAL:
            text += f" Scenario: {info['label_en']}. {info['strategy_en']}"
            text += f" Suggestions: {', '.join(names)}."
        return text
    text = f"Dạ, thời tiết Huế hiện tại (dữ liệu thời gian thực Open-Meteo): {ctx_line}."
    if info["level"] != LEVEL_NEUTRAL:
        text += f" Kịch bản: {info['label_vi']}. {info['strategy_vi']}"
        text += f" Em gợi ý: {', '.join(names)}."
    return text
