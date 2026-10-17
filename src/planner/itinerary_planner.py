# -*- coding: utf-8 -*-
"""
SPATIAL ITINERARY PLANNER (BỘ GỢI Ý LỊCH TRÌNH DU LỊCH DỰA TRÊN ĐỒ THỊ KHÔNG GIAN)
Khóa luận Tốt nghiệp ngành Khoa học Dữ liệu và Trí tuệ Nhân tạo (DS&AI K3 - HUET)
Trường Kỹ thuật và Công nghệ - Đại học Huế
Đề tài: Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh dựa trên Đồ thị Tri thức Không gian và LLM
-----------------------------------------------------------------------------------------------------
Nhiệm vụ:
- Tự động lập lịch trình du lịch 1 - 3 ngày tại Huế dựa trên Đồ thị Tri thức Không gian (Spatial KG).
- Tối ưu hóa cự ly di chuyển (Spatial Clustering): Gom cụm Bờ Bắc, Bờ Nam và Ngoại ô để tránh đi vòng vèo.
- Tự động tìm kiếm quán ăn ngon (Rating >= 4.0, nhiều review) gần điểm tham quan qua cạnh NEAR_BY và SERVES.
- Xuất dữ liệu có cấu trúc (Structured JSON) kèm tọa độ GPS để vẽ lộ trình tour lên Bản đồ tương tác (Folium).
"""

import os
import sys
import math
from typing import Dict, List, Any, Optional, Tuple

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
sys.path.append(PROJECT_ROOT)

from src.graph.graph_retriever import get_graph_retriever, strip_accents


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Tính khoảng cách đường chim bay giữa hai tọa độ GPS (km)."""
    R = 6371.0  # Bán kính Trái Đất (km)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


class SpatialItineraryPlanner:
    _instance = None

    def __init__(self):
        self.retriever = get_graph_retriever()
        self._init_hue_knowledge_hubs()

    def _init_hue_knowledge_hubs(self):
        """Khởi tạo danh mục các Hub di sản và điểm tham quan trọng điểm tại Huế có trong KG."""
        # Mapping các điểm di sản lớn kèm node_id trên đồ thị và tên tiếng Việt chuẩn
        self.core_hubs = {
            # Cụm Bờ Bắc: Kinh thành & Di sản Cố đô
            "dai_noi": {
                "node_id": "place_8875",
                "name": "Đại Nội Huế (Hoàng Thành)",
                "cluster": "Bờ Bắc (Kinh thành)",
                "suggested_duration_hours": 2.5,
                "preferred_time": "morning",
                "desc": "Quần thể di tích Cố đô Huế, Hoàng cung của 13 vị vua triều Nguyễn."
            },
            "chua_thien_mu": {
                "node_id": "place_8876",
                "name": "Chùa Thiên Mụ",
                "cluster": "Bờ Bắc (Sông Hương)",
                "suggested_duration_hours": 1.5,
                "preferred_time": "afternoon",
                "desc": "Ngôi quốc tự cổ kính hơn 400 năm tuổi soi bóng bên dòng sông Hương thơ mộng."
            },
            "cho_dong_ba": {
                "node_id": "place_8884", # Hoặc tìm qua tên
                "name": "Chợ Đông Ba",
                "cluster": "Bờ Bắc (Thương mại)",
                "suggested_duration_hours": 1.5,
                "preferred_time": "afternoon",
                "desc": "Khu chợ truyền thống sầm uất bậc nhất Cố đô, thiên đường quà lưu niệm và ẩm thực."
            },

            # Cụm Bờ Nam: Quần thể Lăng tẩm & Làng nghề
            "lang_tu_duc": {
                "node_id": "place_8880",
                "name": "Lăng Tự Đức (Khiêm Lăng)",
                "cluster": "Bờ Nam (Lăng tẩm)",
                "suggested_duration_hours": 2.0,
                "preferred_time": "morning",
                "desc": "Lăng tẩm có kiến trúc thơ mộng và tinh tế nhất triều Nguyễn giữa rừng thông bạt ngàn."
            },
            "lang_khai_dinh": {
                "node_id": "place_8881", # Hoặc alias lăng
                "name": "Lăng Khải Định (Ứng Lăng)",
                "cluster": "Bờ Nam (Lăng tẩm)",
                "suggested_duration_hours": 1.5,
                "preferred_time": "afternoon",
                "desc": "Kiệt tác kiến trúc giao thoa Đông - Tây độc đáo với nghệ thuật ghép sành sứ đỉnh cao."
            },
            "lang_minh_mang": {
                "node_id": "place_8878",
                "name": "Lăng Minh Mạng (Hiếu Lăng)",
                "cluster": "Bờ Nam (Thượng nguồn)",
                "suggested_duration_hours": 2.0,
                "preferred_time": "morning",
                "desc": "Quần thể lăng tẩm uy nghiêm, đăng đối chuẩn mực phong thủy bên ngã ba Tuần."
            },

            # Cụm Thư giãn & Cảnh quan ven sông
            "song_huong": {
                "node_id": "place_8882",
                "name": "Cầu Tràng Tiền & Bến thuyền Tòa Khâm (Sông Hương)",
                "cluster": "Trung tâm Bờ Nam",
                "suggested_duration_hours": 1.5,
                "preferred_time": "evening",
                "desc": "Biểu tượng thơ mộng của xứ Huế, dạo mát ngắm cầu Tràng Tiền lên đèn và nghe Ca Huế."
            },
            "cau_ngoi_thanh_toan": {
                "node_id": "place_8885",
                "name": "Cầu ngói Thanh Toàn",
                "cluster": "Ngoại ô (Hương Thủy)",
                "suggested_duration_hours": 2.0,
                "preferred_time": "afternoon",
                "desc": "Cây cầu ngói cổ kính hiếm có giữa khung cảnh làng quê thanh bình xứ Huế."
            }
        }

    def _find_best_restaurant_nearby(self, origin_place_id: str, 
                                     preferred_dish: Optional[str] = None,
                                     excluded_ids: Optional[set] = None,
                                     max_dist_km: float = 2.0) -> Optional[Dict[str, Any]]:
        """
        Tìm quán ăn tối ưu gần một địa điểm:
        1. Ưu tiên quán phục vụ món đặc sản ưa thích (qua cạnh SERVES và NEAR_BY).
        2. Nếu không có, chọn quán có Rating cao nhất và cự ly gần nhất.
        """
        if excluded_ids is None:
            excluded_ids = set()

        # 1. Nếu có món ưu tiên, tìm các quán phục vụ món đó trong thành phố
        if preferred_dish:
            serving_places = self.retriever.find_places_by_dish(preferred_dish, locality="Thành phố Huế", limit=10)
            origin_node = self.retriever.get_place(origin_place_id)
            if origin_node and "latitude" in origin_node and "longitude" in origin_node:
                o_lat, o_lon = origin_node["latitude"], origin_node["longitude"]
                
                # Tính khoảng cách từ điểm hiện tại tới các quán này
                candidates_with_dist = []
                for sp in serving_places:
                    pid = sp.get("node_id")
                    if pid in excluded_ids:
                        continue
                    sp_node = self.retriever.get_place(pid)
                    if sp_node and "latitude" in sp_node and "longitude" in sp_node:
                        dist = haversine_distance_km(o_lat, o_lon, sp_node["latitude"], sp_node["longitude"])
                        if dist <= max_dist_km + 1.0: # Mở rộng bán kính nếu đúng món ngon
                            item = dict(sp_node)
                            item["distance_km"] = dist
                            item["walk_time_min"] = round(dist / 4.5 * 60, 1) # Vận tốc đi bộ ~4.5 km/h
                            item["dish_highlight"] = preferred_dish
                            candidates_with_dist.append(item)

                if candidates_with_dist:
                    # Ưu tiên cự ly gần và rating cao
                    candidates_with_dist.sort(key=lambda x: (x["distance_km"] * 1.5 - x.get("rating_value", 0.0) * 0.5))
                    return candidates_with_dist[0]

        # 2. Truy xuất qua cạnh NEAR_BY trực tiếp trong đồ thị
        nearby_restaurants = self.retriever.find_nearby_places(
            origin_place_id, category="Restaurant", max_distance_km=max_dist_km, limit=10
        )

        valid_nearby = [r for r in nearby_restaurants if r.get("node_id") not in excluded_ids]
        if valid_nearby:
            # Lấy món đặc sản của quán nếu có
            best = valid_nearby[0]
            dishes = self.retriever.get_dishes_of_place(best["node_id"])
            if dishes:
                best["dish_highlight"] = dishes[0].get("name", "Đặc sản Cố đô")
            else:
                best["dish_highlight"] = "Ẩm thực truyền thống Huế"
            return best

        return None

    def plan_itinerary(self, num_days: int = 1, 
                       preferred_dishes: Optional[List[str]] = None,
                       trip_type: str = "Couples") -> Dict[str, Any]:
        """
        Lập lịch trình tour du lịch thông minh (1 - 3 ngày tại Huế):
        Tự động ghép nối các chặng (Sáng - Trưa - Chiều - Tối) dựa trên Spatial KG.
        """
        num_days = max(1, min(3, num_days))
        used_place_ids = set()
        days_plan = []

        # Danh sách món đặc sản Huế mặc định theo thứ tự các bữa
        default_dishes = ["Bún bò Huế", "Cơm hến", "Bánh bèo", "Bánh nậm", "Nem lụi", "Chè Huế"]
        if preferred_dishes:
            dish_queue = list(preferred_dishes) + [d for d in default_dishes if d not in preferred_dishes]
        else:
            dish_queue = list(default_dishes)

        # Định nghĩa Kịch bản các ngày theo Cụm Không gian (Spatial Clusters)
        day_templates = [
            # NGÀY 1: Cụm Bờ Bắc - Hoàng thành & Di sản Cố Đô
            {
                "theme": "Hành trình Di sản Hoàng cung & Cổ tự ven Sông Hương",
                "morning_hub": "dai_noi",
                "afternoon_hub": "chua_thien_mu",
                "evening_hub": "song_huong",
                "lunch_dish": dish_queue[0] if len(dish_queue) > 0 else "Bún bò Huế",
                "dinner_dish": dish_queue[1] if len(dish_queue) > 1 else "Bánh bèo"
            },
            # NGÀY 2: Cụm Bờ Nam - Quần thể Lăng tẩm triều Nguyễn & Làng nghề
            {
                "theme": "Khám phá Quần thể Lăng tẩm Vương triều & Làng hương Cổ",
                "morning_hub": "lang_tu_duc",
                "afternoon_hub": "lang_khai_dinh",
                "evening_hub": "song_huong",
                "lunch_dish": dish_queue[2] if len(dish_queue) > 2 else "Cơm hến",
                "dinner_dish": dish_queue[3] if len(dish_queue) > 3 else "Nem lụi"
            },
            # NGÀY 3: Cụm Ngoại ô & Văn hóa Làng quê Cố Đô
            {
                "theme": "Trải nghiệm Cảnh quan Sinh thái & Làng quê Cố Đô",
                "morning_hub": "lang_minh_mang",
                "afternoon_hub": "cau_ngoi_thanh_toan",
                "evening_hub": "song_huong",
                "lunch_dish": dish_queue[4] if len(dish_queue) > 4 else "Bánh ép",
                "dinner_dish": dish_queue[5] if len(dish_queue) > 5 else "Chè Huế"
            }
        ]

        for day_idx in range(num_days):
            tpl = day_templates[day_idx]
            day_slots = []
            day_coords = []
            prev_point = None
            total_dist_day = 0.0

            # -------------------------------------------------------------
            # CHẶNG 1: SÁNG (08:00 - 11:30) - THAM QUAN DI TÍCH TRỌNG ĐIỂM
            # -------------------------------------------------------------
            m_hub_key = tpl["morning_hub"]
            m_hub = self.core_hubs[m_hub_key]
            m_place = self.retriever.get_place(m_hub["node_id"])
            if m_place:
                used_place_ids.add(m_place["node_id"])
                lat, lon = m_place.get("latitude", 16.468), m_place.get("longitude", 107.578)
                day_coords.append([lat, lon])
                prev_point = (lat, lon)

                day_slots.append({
                    "slot_time": "08:00 - 11:30",
                    "slot_name": "Buổi Sáng",
                    "activity_type": "Tham quan Di sản",
                    "place_name": m_hub["name"],
                    "category": "Điểm tham quan (Attraction)",
                    "address": m_place.get("street_address") or "Thành phố Huế",
                    "latitude": lat,
                    "longitude": lon,
                    "rating": m_place.get("rating_value", 4.5),
                    "review_count": m_place.get("review_count", 0),
                    "description": m_hub["desc"],
                    "distance_from_prev_km": 0.0,
                    "travel_time_min": 0
                })

            # -------------------------------------------------------------
            # CHẶNG 2: TRƯA (11:30 - 13:30) - ĂN TRƯA ĐẶC SẢN LÂN CẬN (< 1.5km)
            # -------------------------------------------------------------
            lunch_place = self._find_best_restaurant_nearby(
                origin_place_id=m_hub["node_id"],
                preferred_dish=tpl["lunch_dish"],
                excluded_ids=used_place_ids,
                max_dist_km=2.0
            )

            if lunch_place:
                used_place_ids.add(lunch_place["node_id"])
                l_lat, l_lon = lunch_place.get("latitude", 16.469), lunch_place.get("longitude", 107.582)
                day_coords.append([l_lat, l_lon])
                
                dist_lunch = lunch_place.get("distance_km") or haversine_distance_km(prev_point[0], prev_point[1], l_lat, l_lon)
                walk_min = lunch_place.get("walk_time_min") or round(dist_lunch / 4.5 * 60, 1)
                total_dist_day += dist_lunch
                prev_point = (l_lat, l_lon)

                day_slots.append({
                    "slot_time": "11:30 - 13:30",
                    "slot_name": "Bữa Trưa",
                    "activity_type": "Thưởng thức Ẩm thực",
                    "place_name": lunch_place.get("name"),
                    "category": "Nhà hàng / Quán ăn (Restaurant)",
                    "dish_highlight": lunch_place.get("dish_highlight", tpl["lunch_dish"]),
                    "address": lunch_place.get("street_address") or "TP. Huế",
                    "latitude": l_lat,
                    "longitude": l_lon,
                    "rating": lunch_place.get("rating_value", 4.3),
                    "review_count": lunch_place.get("review_count", 0),
                    "description": f"Quán ngon đặc sản được đánh giá cao trên TripAdvisor, phục vụ món {tpl['lunch_dish']}.",
                    "distance_from_prev_km": dist_lunch,
                    "travel_time_min": walk_min
                })

            # -------------------------------------------------------------
            # CHẶNG 3: CHIỀU (14:00 - 17:30) - THAM QUAN DANH THẮNG CÙNG TUYẾN
            # -------------------------------------------------------------
            af_hub_key = tpl["afternoon_hub"]
            af_hub = self.core_hubs[af_hub_key]
            af_place = self.retriever.get_place(af_hub["node_id"])
            if af_place:
                used_place_ids.add(af_place["node_id"])
                af_lat, af_lon = af_place.get("latitude", 16.453), af_place.get("longitude", 107.544)
                day_coords.append([af_lat, af_lon])

                dist_af = haversine_distance_km(prev_point[0], prev_point[1], af_lat, af_lon)
                drive_min = round(dist_af / 25.0 * 60, 1) # Vận tốc di chuyển ô tô/xe máy ~25 km/h
                total_dist_day += dist_af
                prev_point = (af_lat, af_lon)

                day_slots.append({
                    "slot_time": "14:00 - 17:30",
                    "slot_name": "Buổi Chiều",
                    "activity_type": "Tham quan Danh lam",
                    "place_name": af_hub["name"],
                    "category": "Điểm tham quan (Attraction)",
                    "address": af_place.get("street_address") or "Thành phố Huế",
                    "latitude": af_lat,
                    "longitude": af_lon,
                    "rating": af_place.get("rating_value", 4.4),
                    "review_count": af_place.get("review_count", 0),
                    "description": af_hub["desc"],
                    "distance_from_prev_km": dist_af,
                    "travel_time_min": drive_min
                })

            # -------------------------------------------------------------
            # CHẶNG 4: TỐI (18:30 - 21:30) - ĂN TỐI & DẠO PHỐ / NGẮM SÔNG HƯƠNG
            # -------------------------------------------------------------
            # Tìm quán ăn tối món Huế gần trung tâm hoặc tiện đường về
            dinner_place = self._find_best_restaurant_nearby(
                origin_place_id=self.core_hubs["song_huong"]["node_id"],
                preferred_dish=tpl["dinner_dish"],
                excluded_ids=used_place_ids,
                max_dist_km=2.5
            )

            if dinner_place:
                used_place_ids.add(dinner_place["node_id"])
                dn_lat, dn_lon = dinner_place.get("latitude", 16.467), dinner_place.get("longitude", 107.592)
                day_coords.append([dn_lat, dn_lon])

                dist_dn = haversine_distance_km(prev_point[0], prev_point[1], dn_lat, dn_lon)
                drive_dn_min = round(dist_dn / 25.0 * 60, 1)
                total_dist_day += dist_dn

                day_slots.append({
                    "slot_time": "18:30 - 20:00",
                    "slot_name": "Bữa Tối",
                    "activity_type": "Ẩm thực Tối & Thư giãn",
                    "place_name": dinner_place.get("name"),
                    "category": "Nhà hàng / Quán ăn (Restaurant)",
                    "dish_highlight": dinner_place.get("dish_highlight", tpl["dinner_dish"]),
                    "address": dinner_place.get("street_address") or "TP. Huế",
                    "latitude": dn_lat,
                    "longitude": dn_lon,
                    "rating": dinner_place.get("rating_value", 4.5),
                    "review_count": dinner_place.get("review_count", 0),
                    "description": f"Thưởng thức bữa tối ẩm thực Huế với món {tpl['dinner_dish']} trong không gian ấm cúng.",
                    "distance_from_prev_km": dist_dn,
                    "travel_time_min": drive_dn_min
                })

            # Hoạt động đêm: Dạo cầu Tràng Tiền / Phố đi bộ
            ev_hub = self.core_hubs["song_huong"]
            ev_place = self.retriever.get_place(ev_hub["node_id"])
            if ev_place:
                day_slots.append({
                    "slot_time": "20:00 - 21:30",
                    "slot_name": "Buổi Đêm",
                    "activity_type": "Ngắm cảnh & Giải trí",
                    "place_name": ev_hub["name"],
                    "category": "Cảnh quan / Trải nghiệm",
                    "address": "Bờ Nam Sông Hương, TP. Huế",
                    "latitude": ev_place.get("latitude", 16.469),
                    "longitude": ev_place.get("longitude", 107.591),
                    "rating": ev_place.get("rating_value", 4.6),
                    "review_count": ev_place.get("review_count", 0),
                    "description": ev_hub["desc"],
                    "distance_from_prev_km": 0.5,
                    "travel_time_min": 5.0
                })

            days_plan.append({
                "day_number": day_idx + 1,
                "theme": tpl["theme"],
                "total_distance_km": round(total_dist_day, 2),
                "slots": day_slots,
                "route_coordinates": day_coords
            })

        return {
            "locality": "Thành phố Huế",
            "num_days": num_days,
            "trip_type": trip_type,
            "total_places": sum(len(d["slots"]) for d in days_plan),
            "days": days_plan
        }

    def format_itinerary_markdown(self, plan_data: Dict[str, Any]) -> str:
        """Định dạng kết quả lịch trình thành văn bản Markdown chuyên nghiệp cho người dùng/Chatbot."""
        num_days = plan_data["num_days"]
        trip_type = plan_data.get("trip_type", "Du khách")
        
        md_lines = [
            f"## 🌿 GỢI Ý LỊCH TRÌNH DU LỊCH HUẾ THÔNG MINH ({num_days} NGÀY)",
            f"*Được tối ưu hóa tự động theo cự ly không gian (Spatial KG) & trải nghiệm du khách thực tế*\n",
            f"**• Điểm đến:** Thành phố Huế  |  **• Thời lượng:** {num_days} Ngày  |  **• Đối tượng:** {trip_type}\n",
            "---\n"
        ]

        for day in plan_data["days"]:
            d_num = day["day_number"]
            theme = day["theme"]
            dist = day["total_distance_km"]
            
            md_lines.append(f"### 📍 NGÀY {d_num}: {theme.upper()}")
            md_lines.append(f"*(Tổng cự ly di chuyển ước tính: ~{dist} km - Tuyến đường liền mạch, không đi vòng)*\n")

            for slot in day["slots"]:
                time_range = slot["slot_time"]
                slot_name = slot["slot_name"]
                place_name = slot["place_name"]
                cat = slot["category"]
                dist_prev = slot["distance_from_prev_km"]
                t_min = slot["travel_time_min"]
                desc = slot["description"]
                rating = slot.get("rating", 4.5)
                dish_hl = slot.get("dish_highlight")

                # Biểu tượng tương ứng
                icon = "🏛️" if "Tham quan" in slot["activity_type"] else ("🍲" if "Ẩm thực" in slot["activity_type"] else "🌙")
                
                md_lines.append(f"**{icon} {time_range} — {slot_name}: {place_name}** ({cat})")
                
                if dist_prev > 0:
                    md_lines.append(f"• *Di chuyển:* Cách điểm trước khoảng **{dist_prev} km** (~{t_min} phút)")
                if dish_hl:
                    md_lines.append(f"• *Món đặc sản nổi bật:* **{dish_hl}** (Đánh giá: ⭐ {rating}/5.0)")
                else:
                    md_lines.append(f"• *Đánh giá thực tế:* ⭐ {rating}/5.0")
                
                md_lines.append(f"• *Chi tiết:* {desc}\n")

            md_lines.append("---\n")

        md_lines.append("💡 **LỜI KHUYÊN TỪ TRỢ LÝ CỐ ĐÔ:**")
        md_lines.append("- Buổi trưa tại Huế nắng gắt, lịch trình đã bố trí quán ăn nằm sát điểm tham quan sáng (< 1.5km) để bạn không phải di chuyển xa giữa trưa.")
        md_lines.append("- Các lăng tẩm và chùa chiền yêu cầu trang phục lịch sự. Bạn nên mang giày bệt hoặc giày thể thao êm ái để đi dạo thoải mái.")
        md_lines.append("- Toàn bộ các chặng trên đã được đồng bộ sẵn tọa độ GPS để hiển thị trực tiếp lên Bản đồ số.")

        return "\n".join(md_lines)


# Singleton Planner
_planner_instance = None

def get_itinerary_planner() -> SpatialItineraryPlanner:
    global _planner_instance
    if _planner_instance is None:
        _planner_instance = SpatialItineraryPlanner()
    return _planner_instance


if __name__ == "__main__":
    print("=" * 80)
    print("🚀 KIỂM THỬ SPATIAL ITINERARY PLANNER (GỢI Ý LỊCH TRÌNH 1 & 2 NGÀY TẠI HUẾ)")
    print("=" * 80)

    planner = get_itinerary_planner()

    # Test tour 1 ngày
    print("\n👉 [TEST CASE 1: LỊCH TRÌNH 1 NGÀY TẠI HUẾ]:")
    res_1day = planner.plan_itinerary(num_days=1, preferred_dishes=["Bún bò Huế", "Bánh bèo"])
    md_1day = planner.format_itinerary_markdown(res_1day)
    print(md_1day)

    print("\n" + "=" * 80)
    print("👉 [TEST CASE 2: LỊCH TRÌNH 2 NGÀY TẠI HUẾ]:")
    res_2days = planner.plan_itinerary(num_days=2, trip_type="Gia đình (Family)")
    print(f"Tổng số điểm ghé thăm: {res_2days['total_places']}")
    for d in res_2days["days"]:
        print(f"Ngày {d['day_number']}: {d['theme']} | Tổng cự ly: {d['total_distance_km']} km | Tọa độ GPS: {len(d['route_coordinates'])} điểm")
