# -*- coding: utf-8 -*-
"""
SESSION MEMORY: TRÍ NHỚ NGỮ CẢNH PHIÊN CHAT ĐA LƯỢT (MULTI-TURN CONTEXT)
-----------------------------------------------------------------------------------------------------
Module thuần (không phụ thuộc LLM / KG / ChromaDB) để kiểm thử đơn vị dễ dàng:
1. sanitize_session_context: Kiểm tra session_context do client gửi lên. Anchor phải tồn tại trong KG,
   nhãn & loại địa điểm luôn lấy lại từ KG (không tin chuỗi client -> chống chèn prompt).
2. resolve_anaphora: Giải quyết đồng tham chiếu ("ở đó", "từ đó đi...", "quán này", "món đó") và câu
   tỉnh lược ("Giá vé bao nhiêu?") bằng cách VIẾT LẠI câu hỏi với tên địa danh mốc. Nhờ vậy toàn bộ
   pipeline phía sau (bóc tách alias, chỉ đường A -> B, heuristic ở chat_route) dùng chung một câu hỏi
   đã giải nghĩa. Chạy 0ms, không gọi LLM.
3. build_session_context: Cập nhật địa danh mốc (anchor) + miền chủ đề sau mỗi lượt.
4. sanitize_history / format_history_for_prompt: Cắt gọn lịch sử hội thoại đưa vào prompt Node 4.
"""
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Iterable, List, Optional

MAX_HISTORY_MESSAGES = 4          # 2 lượt hỏi - đáp gần nhất
MAX_USER_CHARS = 300
MAX_ASSISTANT_CHARS = 200
MAX_LABEL_CHARS = 80
MAX_ELLIPSIS_WORDS = 8

TOPIC_LABELS = {
    "heritage": "Di tích & Lịch sử",
    "culinary": "Ẩm thực xứ Huế",
    "leisure": "Biển & Thiên nhiên",
    "lodging": "Lưu trú",
    "route_navigation": "Di chuyển & Lộ trình",
}

# -----------------------------------------------------------------------------
# Mẫu đại từ chỉ định tiếng Việt
# -----------------------------------------------------------------------------
# Có dấu: [giới từ] [danh từ nơi chốn] <đại từ>. Hợp lệ khi có danh từ ("quán này", "chỗ đó") hoặc
# giới từ + "đó/đấy" ("ở đó", "từ đó", "gần đó"). Cố ý KHÔNG bắt "đây" ("gần đây", "ở đây", "từ đây"
# = vị trí GPS hiện tại của du khách) và không đụng tới "Đỏ" (Bánh bèo Bà Đỏ) vì so khớp có dấu.
_PREP_ACC = r"xung quanh|quanh|từ|ở|tại|gần|đến|tới|sang|qua|về|ra"
_NOUN_ACC = r"địa điểm|điểm|chỗ|nơi|quán ăn|quán|nhà hàng|chùa|lăng|đền|di tích|khu"
_PLACE_ACC_RE = re.compile(
    rf"(?<!\w)(?:(?P<prep>{_PREP_ACC})\s+)?(?:(?P<noun>{_NOUN_ACC})\s+)?(?P<pro>đó|đấy|ấy|này)(?!\w)"
)
_DISH_ACC_RE = re.compile(r"(?<!\w)món(?:\s+ăn)?\s+(?:đó|đấy|ấy|này)(?!\w)")

# Không dấu: chỉ giữ các cụm có độ chính xác cao ("tu do" chỉ khi theo sau là động từ di chuyển
# để tránh "tự do"; danh từ chỉ đi với "nay/ay" vì "quan do" dễ là "quán đồ...").
_PREP_RAW = r"xung quanh|quanh|tu|o|tai|gan"
_NOUN_RAW = r"dia diem|quan an|quan|nha hang|di tich|cho|khu"
_PLACE_RAW_RE = re.compile(
    rf"(?<!\w)(?:(?P<prep>{_PREP_RAW})\s+)?(?:(?P<noun>{_NOUN_RAW})\s+)?(?P<pro>do|ay|nay)(?!\w)"
)
_DISH_RAW_RE = re.compile(r"(?<!\w)mon(?:\s+an)?\s+(?:nay|ay)(?!\w)")
_RAW_MOVE_AFTER_TU = re.compile(r"\s+(?:di|den|toi|sang|qua|ra|ve)(?!\w)")

# "từ đó đến nay", "từ đó trở đi"... mang nghĩa thời gian, không phải địa điểm
_TEMPORAL_AFTER_TU = re.compile(r"\s*(?:đến nay|tới nay|đến giờ|tới giờ|trở đi|về sau)(?!\w)")

# Danh từ chỉ loại: "quán đó" chỉ trỏ vào quán ăn, "chùa đó" chỉ trỏ vào di tích
_FOOD_NOUNS = {"quán ăn", "quán", "nhà hàng", "quan an", "quan", "nha hang"}
_SITE_NOUNS = {"chùa", "lăng", "đền", "di tích", "di tich"}

# Từ khóa cự ly: "Đại Nội cách chỗ đó bao xa" -> vẫn giải nghĩa dù trước đại từ đã có tên địa danh
_DISTANCE_HINTS = ("bao xa", "cach", "khoang cach", "may km", "may cay", "duong di", "chi duong", "lo trinh")

# Alias địa danh trùng từ thông dụng ("thanh toán", "an định"...) -> không dùng để suy luận
# "câu đã nêu địa danh mới trước đại từ", tránh bỏ sót đại từ cần giải nghĩa.
AMBIGUOUS_ALIASES = {
    "thanh toan", "an dinh", "gia di", "hoa dong", "vi da", "o tho", "di huong", "thien an",
    "huyen anh", "tu lang", "ba ty", "ba do", "mat biec", "dieu de", "toa kham",
}

# Câu tỉnh lược: hỏi thuộc tính mà không nêu đối tượng ("Giá vé bao nhiêu?", "Mở cửa mấy giờ?")
_ELLIPSIS_ATTRS = (
    "gia ve", "ve vao", "mo cua", "dong cua", "may gio", "gio mo", "dia chi", "lich su",
    "kien truc", "y nghia", "di bang gi", "gui xe", "dau xe", "trang phuc", "mac gi",
    "bao lau", "nen den", "luc nao", "thoi diem", "dep khong", "ngon khong", "xay dung",
    "nam nao", "ai xay", "bao nhieu tien", "co dat", "thuc don", "menu", "so dien thoai",
)
# Câu tỉnh lược nhưng mang ý định tìm kiếm mới / phạm vi rộng -> không gắn mốc cũ
_ELLIPSIS_BLOCKERS = (
    "hue", "co do", "thanh pho", "viet nam", "mien trung", "da nang", "ha noi", "sai gon",
    "gan day", "quanh day", "o day", "tu day", "lich trinh", "tour", "khach san", "homestay",
    "quan", "nha hang", "cafe", "ca phe", "bien", "cho ", "mon ", "dac san",
)


# -----------------------------------------------------------------------------
# Tiện ích văn bản
# -----------------------------------------------------------------------------
def fold_text(text: str) -> str:
    """Bỏ dấu tiếng Việt + chữ thường, GIỮ NGUYÊN độ dài để ánh xạ vị trí ký tự."""
    text = unicodedata.normalize("NFC", text or "").replace("đ", "d").replace("Đ", "D")
    return "".join(unicodedata.normalize("NFD", ch)[0] for ch in text).lower()


def has_vietnamese_diacritics(text: str) -> bool:
    text = text or ""
    if "đ" in text or "Đ" in text:
        return True
    return any(unicodedata.category(ch) == "Mn" for ch in unicodedata.normalize("NFD", text))


def _contains_word(folded: str, phrase: str) -> bool:
    return bool(re.search(rf"(?<!\w){re.escape(phrase.strip())}(?!\w)", folded))


def short_place_label(name: str) -> str:
    """'Đại Nội Huế (Hoàng Thành & Ngọ Môn)' -> 'Đại Nội Huế' (nhãn gọn để chèn vào câu hỏi)."""
    label = re.sub(r"\s*\([^)]*\)", "", str(name or ""))
    label = re.sub(r"[\[\]{}<>`*_#\r\n]+", " ", label)
    label = re.sub(r"\s+", " ", label).strip(" -·,;:")
    return label[:MAX_LABEL_CHARS].strip()


def place_kind(place: Optional[Dict[str, Any]]) -> Optional[str]:
    """food | lodging | site"""
    if not place:
        return None
    kind = f"{place.get('node_type', '')} {place.get('category', '')}".lower()
    if any(k in kind for k in ("restaurant", "cafe", "quán", "ẩm thực")):
        return "food"
    if "hotel" in kind:
        return "lodging"
    return "site"


def _infer_topic(place: Optional[Dict[str, Any]], place_id: Optional[str], dish: Optional[str], is_navigation: bool) -> Optional[str]:
    if is_navigation:
        return "route_navigation"
    if dish:
        return "culinary"
    kind = place_kind(place)
    if kind == "food":
        return "culinary"
    if kind == "lodging":
        return "lodging"
    if kind == "site":
        name = fold_text(place.get("name", ""))
        if str(place_id or "").startswith("beach_") or any(k in name for k in ("bien", "deo", "bach ma", "dam lap an")):
            return "leisure"
        return "heritage"
    return None


# -----------------------------------------------------------------------------
# 1. Chuẩn hóa session_context từ client
# -----------------------------------------------------------------------------
def sanitize_session_context(
    raw: Any,
    place_lookup: Callable[[str], Optional[Dict[str, Any]]],
    dish_validator: Optional[Callable[[str], Optional[str]]] = None,
) -> Optional[Dict[str, Any]]:
    """
    place_lookup(place_id): tra cứu theo ID CHÍNH XÁC (không fuzzy), trả về node KG hoặc None.
    dish_validator(name): trả về tên món chuẩn trong KG hoặc None.
    """
    if not isinstance(raw, dict):
        return None

    ctx: Dict[str, Any] = {}
    pid = str(raw.get("anchor_place_id") or "").strip()[:64]
    if pid:
        place = place_lookup(pid)
        label = short_place_label(place.get("name")) if place else ""
        if label:
            ctx["anchor_place_id"] = pid
            ctx["anchor_place_label"] = label
            ctx["anchor_place_kind"] = place_kind(place)

    dish = raw.get("anchor_dish")
    if isinstance(dish, str) and dish.strip():
        clean_dish = dish_validator(dish.strip()) if dish_validator else short_place_label(dish)
        if clean_dish:
            ctx["anchor_dish"] = clean_dish

    topic = raw.get("topic_domain")
    if topic in TOPIC_LABELS:
        ctx["topic_domain"] = topic
        ctx["topic_name"] = TOPIC_LABELS[topic]

    try:
        ctx["turn_count"] = max(0, min(int(raw.get("turn_count") or 0), 10000))
    except (TypeError, ValueError):
        ctx["turn_count"] = 0

    return ctx if (ctx.get("anchor_place_id") or ctx.get("anchor_dish") or ctx["turn_count"]) else None


# -----------------------------------------------------------------------------
# 2. Giải quyết đồng tham chiếu (Anaphora Resolution)
# -----------------------------------------------------------------------------
@dataclass
class AnaphoraResolution:
    query: str
    original_query: str
    place_id: Optional[str] = None
    place_label: Optional[str] = None
    dish: Optional[str] = None
    replacements: List[Dict[str, str]] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return bool(self.replacements)

    def to_state(self) -> Optional[Dict[str, Any]]:
        if not self.changed:
            return None
        return {"place_id": self.place_id, "label": self.place_label, "dish": self.dish}

    def trace_step(self) -> Optional[Dict[str, Any]]:
        if not self.changed:
            return None
        parts = []
        for r in self.replacements:
            if r["kind"] == "ellipsis":
                parts.append(f"Câu hỏi tỉnh lược → hiểu là về **{r['target']}**")
            else:
                parts.append(f"'{r['phrase']}' → **{r['target']}**")
        return {
            "step": "context_carryover",
            "icon": "🔗",
            "label": "Kế thừa ngữ cảnh hội thoại",
            "detail": "; ".join(parts),
            "node_id": self.place_id,
            "edge": "SESSION_ANCHOR",
            "status": "found",
        }


def _noun_fits_anchor(noun: Optional[str], kind: Optional[str]) -> bool:
    if not noun or not kind:
        return True
    if noun in _FOOD_NOUNS:
        return kind == "food"
    if noun in _SITE_NOUNS:
        return kind == "site"
    return True


def resolve_anaphora(
    query: str,
    session_context: Optional[Dict[str, Any]],
    has_image: bool = False,
    place_aliases: Optional[Iterable[str]] = None,
    dish_keywords: Optional[Iterable[str]] = None,
) -> AnaphoraResolution:
    """
    Viết lại đại từ chỉ định bằng địa danh / món ăn mốc của phiên chat:
    - "Từ đó đi Đại Nội bao xa?"  -> "Từ Chùa Thiên Mụ đi Đại Nội bao xa?"
    - "Quán này mở cửa mấy giờ?"  -> "Bún Bò Mụ Kéo mở cửa mấy giờ?"
    - "Món đó ăn ở đâu ngon?"     -> "Món Bún bò Huế ăn ở đâu ngon?"
    - "Giá vé bao nhiêu?"         -> "Về Chùa Thiên Mụ: Giá vé bao nhiêu?"
    Không giải nghĩa khi có ảnh đính kèm ("chỗ này" lúc đó là địa điểm trong ảnh).
    place_aliases / dish_keywords: alias KHÔNG DẤU của địa danh / món ăn, dùng để phát hiện câu
    đã nêu đối tượng mới (khi đó đại từ trỏ vào đối tượng mới, không phải mốc cũ).
    """
    original = unicodedata.normalize("NFC", query or "")
    result = AnaphoraResolution(query=original, original_query=original)
    ctx = session_context or {}
    place_id = ctx.get("anchor_place_id")
    place_label = ctx.get("anchor_place_label")
    anchor_kind = ctx.get("anchor_place_kind")
    dish = ctx.get("anchor_dish")
    if not (place_id and place_label):
        place_id = place_label = None
    if has_image or not original.strip() or not (place_label or dish):
        return result

    accented = has_vietnamese_diacritics(original)
    all_aliases = [a for a in (place_aliases or []) if a]
    safe_aliases = [a for a in all_aliases if len(a) >= 4 and a not in AMBIGUOUS_ALIASES]
    text = original

    # a) Món ăn: "món đó/này" -> "món <anchor_dish>"
    if dish:
        dish_re = _DISH_ACC_RE if accented else _DISH_RAW_RE
        match_text = text.lower() if accented else fold_text(text)
        spans = [(m.start(), m.end()) for m in dish_re.finditer(match_text)]
        for start, end in reversed(spans):
            phrase = text[start:end]
            head = "Món" if phrase[:1].isupper() else "món"
            text = f"{text[:start]}{head} {dish}{text[end:]}"
            result.replacements.append({"phrase": phrase, "target": dish, "kind": "dish"})
        if spans:
            result.dish = dish

    # b) Địa điểm: "ở đó", "từ đó đi...", "quán này", "chỗ đó"...
    if place_label:
        place_re = _PLACE_ACC_RE if accented else _PLACE_RAW_RE
        match_text = text.lower() if accented else fold_text(text)
        asks_distance = any(h in fold_text(text) for h in _DISTANCE_HINTS)
        edits = []
        for m in place_re.finditer(match_text):
            prep, noun, pro = m.group("prep"), m.group("noun"), m.group("pro")
            if accented:
                valid = bool(noun) or (bool(prep) and pro in ("đó", "đấy"))
                if valid and prep == "từ" and not noun and _TEMPORAL_AFTER_TU.match(match_text, m.end()):
                    valid = False
            elif noun:
                valid = pro in ("nay", "ay")
            elif prep == "tu":
                valid = pro == "do" and bool(_RAW_MOVE_AFTER_TU.match(match_text, m.end()))
            else:
                valid = bool(prep) and pro == "do"
            if not valid or not _noun_fits_anchor(noun, anchor_kind):
                continue

            # Câu đã nêu địa danh mới trước đại từ ("Lăng Khải Định có gì, gần đó ăn gì?") -> đại từ
            # trỏ vào địa danh mới. Ngoại lệ: "từ đó ..." (điểm xuất phát) và câu hỏi cự ly.
            is_origin = prep in ("từ", "tu")
            before = fold_text(text[:m.start()])
            if not is_origin and not asks_distance and any(_contains_word(before, a) for a in safe_aliases):
                continue

            edits.append((m.start("noun") if noun else m.start("pro"), m.end(), m.start()))

        for repl_start, end, phrase_start in reversed(edits):
            phrase = text[phrase_start:end]
            text = f"{text[:repl_start]}{place_label}{text[end:]}"
            result.replacements.append({"phrase": phrase, "target": place_label, "kind": "place"})
        if edits:
            result.place_id, result.place_label = place_id, place_label

    # c) Câu tỉnh lược ngắn chỉ hỏi thuộc tính, không nêu đối tượng nào -> gắn mốc địa danh
    if place_label and not result.replacements:
        folded = fold_text(text)
        words = re.findall(r"\w+", folded)
        mentions_entity = any(_contains_word(folded, a) for a in all_aliases) or any(
            _contains_word(folded, d) for d in (dish_keywords or []) if d
        )
        if (
            0 < len(words) <= MAX_ELLIPSIS_WORDS
            and not mentions_entity
            and any(_contains_word(folded, a) for a in _ELLIPSIS_ATTRS)
            and not any(_contains_word(folded, b) for b in _ELLIPSIS_BLOCKERS)
        ):
            text = f"Về {place_label}: {text.strip()}"
            result.place_id, result.place_label = place_id, place_label
            result.replacements.append({"phrase": original.strip(), "target": place_label, "kind": "ellipsis"})

    order = original.lower()
    result.replacements.sort(key=lambda r: order.find(r["phrase"].lower()))
    result.query = text
    return result


# -----------------------------------------------------------------------------
# 3. Cập nhật session_context sau mỗi lượt
# -----------------------------------------------------------------------------
def build_session_context(
    previous: Optional[Dict[str, Any]],
    *,
    session_id: Optional[str] = None,
    anchor_place_id: Optional[str] = None,
    anchor_place: Optional[Dict[str, Any]] = None,
    dish: Optional[str] = None,
    reset_place: bool = False,
    is_navigation: bool = False,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    anchor_place_id/anchor_place: địa danh mốc của lượt này, đã chọn theo ưu tiên
    (điểm đến chỉ đường > địa danh trong ảnh > địa danh được nhắc tới).
    reset_place=True: lượt này chuyển sang hỏi món chung chung (nhiều quán) -> bỏ mốc địa danh cũ
    để "quán đó" ở lượt sau không trỏ nhầm vào quán/di tích của chủ đề trước.
    Không có mốc mới và không reset -> giữ mốc cũ.
    """
    prev = dict(previous or {})
    ctx: Dict[str, Any] = {
        "anchor_place_id": prev.get("anchor_place_id"),
        "anchor_place_label": prev.get("anchor_place_label"),
        "anchor_place_kind": prev.get("anchor_place_kind"),
        "anchor_dish": prev.get("anchor_dish"),
        "topic_domain": prev.get("topic_domain"),
    }

    label = short_place_label(anchor_place.get("name")) if (anchor_place_id and anchor_place) else ""
    if label:
        ctx.update(anchor_place_id=anchor_place_id, anchor_place_label=label, anchor_place_kind=place_kind(anchor_place))
    elif reset_place:
        ctx.update(anchor_place_id=None, anchor_place_label=None, anchor_place_kind=None)
    if dish:
        ctx["anchor_dish"] = dish

    topic = _infer_topic(anchor_place if label else None, anchor_place_id, dish, is_navigation)
    if topic:
        ctx["topic_domain"] = topic
    ctx["topic_name"] = TOPIC_LABELS.get(ctx.get("topic_domain") or "")

    try:
        ctx["turn_count"] = int(prev.get("turn_count") or 0) + 1
    except (TypeError, ValueError):
        ctx["turn_count"] = 1
    if session_id:
        ctx["session_id"] = str(session_id)[:80]
    ctx["updated_at"] = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {k: v for k, v in ctx.items() if v is not None}


# -----------------------------------------------------------------------------
# 4. Lịch sử hội thoại cho prompt
# -----------------------------------------------------------------------------
def _clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def sanitize_history(raw: Any, max_messages: int = MAX_HISTORY_MESSAGES) -> List[Dict[str, str]]:
    if not isinstance(raw, list):
        return []
    clean: List[Dict[str, str]] = []
    for item in raw[-(max_messages * 3):]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        text = item.get("text") if item.get("text") is not None else item.get("content")
        if role not in ("user", "assistant") or not isinstance(text, str):
            continue
        # Bỏ markdown & ngoặc vuông để lịch sử không giả dạng các khối [NGỮ CẢNH HỆ THỐNG] của prompt
        text = re.sub(r"[*_#`>]+", "", text).replace("[", "(").replace("]", ")")
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            continue
        limit = MAX_USER_CHARS if role == "user" else MAX_ASSISTANT_CHARS
        clean.append({"role": role, "text": _clip(text, limit)})
    return clean[-max_messages:]


def format_history_for_prompt(history: Any, max_messages: int = MAX_HISTORY_MESSAGES) -> str:
    items = sanitize_history(history, max_messages)
    return "\n".join(f"- {'Du khách' if it['role'] == 'user' else 'Trợ lý'}: {it['text']}" for it in items)
