# -*- coding: utf-8 -*-
"""
GRAPH RETRIEVER (BỘ TRUY XUẤT ĐỒ THỊ TRI THỨC DU LỊCH)
Khóa luận Tốt nghiệp ngành Khoa học Dữ liệu và Trí tuệ Nhân tạo (DS&AI K3 - HUET)
Trường Kỹ thuật và Công nghệ - Đại học Huế
Đề tài: Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh dựa trên Đồ thị Tri thức Không gian và LLM
-----------------------------------------------------------------------------------------------------
Nhiệm vụ:
- Tải nhanh đồ thị tri thức NetworkX (data/processed/knowledge_graph.pkl)
- Hỗ trợ các phép duyệt đồ thị (Graph Traversal):
  1. find_places_by_dish: Tìm nhà hàng phục vụ món ăn đặc sản qua cạnh SERVES
  2. find_nearby_places: Tìm địa điểm lân cận qua cạnh NEAR_BY (theo bán kính, danh mục)
  3. find_dishes_of_place: Liệt kê thực đơn đặc sản của một quán ăn
  4. search_places: Tìm kiếm địa điểm theo tên/từ khóa, lọc theo tỉnh/thành
  5. get_entity_subgraph: Trích xuất mạng con (Sub-graph 1-2 hops) bao quanh các thực thể
  6. format_context_for_llm: Định dạng tri thức đồ thị thành văn bản ngữ cảnh rõ ràng cho LLM
"""

import os
import sys
import pickle
import unicodedata
from typing import Dict, List, Any, Optional, Tuple
import networkx as nx

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
KG_PKL_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "knowledge_graph.pkl")


def strip_accents(text: str) -> str:
    """Loại bỏ dấu tiếng Việt để tìm kiếm mờ (fuzzy keyword matching)."""
    if not text:
        return ""
    text = unicodedata.normalize('NFD', text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != 'Mn')
    return unicodedata.normalize('NFC', text).lower().strip()


class SpatialGraphRetriever:
    _instance = None

    def __init__(self, kg_path: str = KG_PKL_PATH):
        self.kg_path = kg_path
        self.G: nx.MultiDiGraph = None
        self._place_name_index: Dict[str, str] = {}      # normalized_name -> node_id
        self._dish_name_index: Dict[str, str] = {}       # normalized_dish -> node_id
        self._province_name_index: Dict[str, str] = {}   # normalized_prov -> node_id
        self._all_place_nodes: List[Tuple[str, Dict[str, Any]]] = []
        self._load_graph()

    def _load_graph(self):
        if not os.path.exists(self.kg_path):
            raise FileNotFoundError(f"Không tìm thấy file Knowledge Graph tại: {self.kg_path}")
        
        with open(self.kg_path, "rb") as f:
            self.G = pickle.load(f)

        # Xây dựng index tra cứu nhanh theo tên
        for node_id, data in self.G.nodes(data=True):
            ntype = data.get("node_type", "")
            raw_name = data.get("name", "")
            norm_name = strip_accents(raw_name)

            if ntype in ["Restaurant", "Hotel", "Attraction", "Place"]:
                self._place_name_index[norm_name] = node_id
                self._all_place_nodes.append((node_id, data))
            elif ntype == "Dish":
                self._dish_name_index[norm_name] = node_id
            elif ntype == "Province":
                self._province_name_index[norm_name] = node_id

    def get_place(self, place_id_or_name: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin chi tiết một địa điểm qua ID hoặc Tên."""
        if place_id_or_name in self.G:
            data = dict(self.G.nodes[place_id_or_name])
            data["node_id"] = place_id_or_name
            return data
        
        norm = strip_accents(place_id_or_name)
        if norm in self._place_name_index:
            node_id = self._place_name_index[norm]
            data = dict(self.G.nodes[node_id])
            data["node_id"] = node_id
            return data
        
        # Thử tìm gần đúng
        for p_name_norm, node_id in self._place_name_index.items():
            if norm in p_name_norm or p_name_norm in norm:
                data = dict(self.G.nodes[node_id])
                data["node_id"] = node_id
                return data
        return None

    def search_places(self, query: str, locality: Optional[str] = None, 
                      category: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Tìm kiếm địa điểm theo từ khóa, hỗ trợ lọc theo địa phương và danh mục."""
        norm_q = strip_accents(query)
        norm_loc = strip_accents(locality) if locality else None
        norm_cat = category.lower() if category else None

        candidates = []
        for node_id, data in self._all_place_nodes:
            # Lọc danh mục
            if norm_cat and data.get("category", "").lower() != norm_cat:
                continue

            # Lọc địa phương
            if norm_loc:
                loc_val = strip_accents(data.get("locality", ""))
                dist_val = strip_accents(data.get("district", ""))
                if norm_loc not in loc_val and norm_loc not in dist_val:
                    continue

            name = data.get("name", "")
            norm_name = strip_accents(name)

            # Tính điểm match
            score = 0
            if norm_q == norm_name:
                score = 100
            elif norm_q in norm_name:
                score = 70 + len(norm_q) / max(len(norm_name), 1) * 20
            elif any(part in norm_name for part in norm_q.split()):
                score = 40

            if score > 0:
                # Ưu tiên rating và số review
                rank_score = score + (data.get("rating_value", 0.0) * 2) + min(data.get("review_count", 0) / 100, 10)
                item = dict(data)
                item["node_id"] = node_id
                item["_match_score"] = rank_score
                candidates.append(item)

        candidates.sort(key=lambda x: x["_match_score"], reverse=True)
        return candidates[:limit]

    def find_nearby_places(self, place_id_or_name: str, category: Optional[str] = None, 
                           max_distance_km: float = 1.2, limit: int = 5) -> List[Dict[str, Any]]:
        """Truy xuất các địa điểm lân cận qua cạnh NEAR_BY trong Knowledge Graph."""
        place = self.get_place(place_id_or_name)
        if not place:
            return []

        origin_id = place["node_id"]
        neighbors = []

        if origin_id in self.G:
            for neighbor_id in self.G.neighbors(origin_id):
                edge_dict = self.G.get_edge_data(origin_id, neighbor_id)
                if not edge_dict:
                    continue
                
                # Duyệt qua các cạnh đa quan hệ (MultiDiGraph)
                for key, edge_data in edge_dict.items():
                    if edge_data.get("relation") == "NEAR_BY":
                        dist = edge_data.get("distance_km", 999.0)
                        if dist <= max_distance_km:
                            n_data = dict(self.G.nodes[neighbor_id])
                            n_cat = n_data.get("category", "").lower()
                            if category and n_cat != category.lower():
                                continue

                            n_data["node_id"] = neighbor_id
                            n_data["distance_km"] = dist
                            n_data["walk_time_min"] = edge_data.get("walk_time_min", 0)
                            n_data["drive_time_min"] = edge_data.get("drive_time_min", 0)
                            neighbors.append(n_data)

        neighbors.sort(key=lambda x: x.get("distance_km", 999.0))
        return neighbors[:limit]

    def find_places_by_dish(self, dish_name: str, locality: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Truy xuất các quán ăn/nhà hàng phục vụ món ăn đặc sản qua cạnh SERVES."""
        norm_dish = strip_accents(dish_name)
        norm_loc = strip_accents(locality) if locality else None

        # Tìm Dish Node
        target_dish_id = None
        target_dish_name = ""
        for d_norm, d_node_id in self._dish_name_index.items():
            if norm_dish == d_norm or norm_dish in d_norm or d_norm in norm_dish:
                target_dish_id = d_node_id
                target_dish_name = self.G.nodes[d_node_id].get("name", "")
                break

        if not target_dish_id:
            return []

        # Trong MultiDiGraph, cạnh SERVES đi từ (Restaurant) -> (Dish)
        # Nên ta tìm predecessors (các nút trỏ tới Dish Node)
        results = []
        for rest_node_id in self.G.predecessors(target_dish_id):
            edge_dict = self.G.get_edge_data(rest_node_id, target_dish_id)
            if not edge_dict:
                continue

            for key, edge_data in edge_dict.items():
                if edge_data.get("relation") == "SERVES":
                    r_data = dict(self.G.nodes[rest_node_id])

                    # Lọc theo địa phương nếu có
                    if norm_loc:
                        loc_val = strip_accents(r_data.get("locality", ""))
                        dist_val = strip_accents(r_data.get("district", ""))
                        if norm_loc not in loc_val and norm_loc not in dist_val:
                            continue

                    r_data["node_id"] = rest_node_id
                    r_data["dish_name"] = target_dish_name
                    r_data["mention_count"] = edge_data.get("mention_count", 0)
                    r_data["dish_avg_rating"] = edge_data.get("avg_rating", 4.0)
                    r_data["sentiment_score"] = edge_data.get("sentiment_score", 0.0)
                    results.append(r_data)

        # Sắp xếp ưu tiên: số lượt nhắc món (mention_count) + rating món ăn
        results.sort(key=lambda x: (x.get("mention_count", 0) * 2 + x.get("dish_avg_rating", 0.0) * 5), reverse=True)
        return results[:limit]

    def get_dishes_of_place(self, place_id_or_name: str) -> List[Dict[str, Any]]:
        """Lấy danh sách các món đặc sản được phục vụ tại một nhà hàng."""
        place = self.get_place(place_id_or_name)
        if not place:
            return []

        node_id = place["node_id"]
        dishes = []
        if node_id in self.G:
            for neighbor_id in self.G.neighbors(node_id):
                edge_dict = self.G.get_edge_data(node_id, neighbor_id)
                if not edge_dict:
                    continue
                for key, edge_data in edge_dict.items():
                    if edge_data.get("relation") == "SERVES":
                        d_data = dict(self.G.nodes[neighbor_id])
                        d_data["mention_count"] = edge_data.get("mention_count", 0)
                        d_data["dish_avg_rating"] = edge_data.get("avg_rating", 4.0)
                        dishes.append(d_data)

        dishes.sort(key=lambda x: x.get("mention_count", 0), reverse=True)
        return dishes

    def format_graph_context(self, retrieved_places: List[Dict[str, Any]], 
                             nearby_info: Optional[Dict[str, List[Dict[str, Any]]]] = None,
                             dishes_info: Optional[Dict[str, List[Dict[str, Any]]]] = None) -> str:
        """Định dạng kết quả truy xuất đồ thị thành chuỗi Markdown cô đọng, giàu ngữ nghĩa cho LLM."""
        if not retrieved_places:
            return "Không tìm thấy dữ liệu địa điểm trong Đồ thị Tri thức."

        lines = ["### [TRI THỨC XÁC THỰC TỪ ĐỒ THỊ KHÔNG GIAN (KNOWLEDGE GRAPH)]"]
        for idx, p in enumerate(retrieved_places, 1):
            p_name = p.get("name", "N/A")
            cat = p.get("category", "").capitalize()
            rating = p.get("rating_value", 0.0)
            rev_cnt = p.get("review_count", 0)
            addr = p.get("street_address") or p.get("locality") or "Huế"
            price = p.get("price_range") or "Bình dân"

            header = f"{idx}. **{p_name}** ({cat}) — ⭐ {rating}/5 ({rev_cnt:,} đánh giá) | Địa chỉ: {addr} | Giá: {price}"
            lines.append(header)

            # Món đặc sản nếu có
            p_node_id = p.get("node_id")
            if dishes_info and p_node_id in dishes_info:
                d_list = dishes_info[p_node_id]
                if d_list:
                    d_strs = [f"{d['name']} (nhắc {d.get('mention_count', 0)} lần)" for d in d_list[:4]]
                    lines.append(f"   🍲 Món đặc sản nổi bật: {', '.join(d_strs)}")

            # Điểm lân cận nếu có
            if nearby_info and p_node_id in nearby_info:
                near_list = nearby_info[p_node_id]
                if near_list:
                    near_strs = [f"{n['name']} ({n.get('distance_km', 0):.2f}km, ~{n.get('walk_time_min', 0)}p đi bộ)" for n in near_list[:3]]
                    lines.append(f"   📍 Lân cận: {'; '.join(near_strs)}")

        return "\n".join(lines)


# Singleton instance helper
_retriever = None

def get_graph_retriever() -> SpatialGraphRetriever:
    global _retriever
    if _retriever is None:
        _retriever = SpatialGraphRetriever()
    return _retriever


if __name__ == "__main__":
    retriever = get_graph_retriever()
    print(f"✅ Đã nạp Graph Retriever thành công ({retriever.G.number_of_nodes():,} nodes, {retriever.G.number_of_edges():,} edges)")

    print("\n🔍 Thử nghiệm 1: Tìm quán phục vụ 'Bún bò' ở Huế:")
    bun_bo_rests = retriever.find_places_by_dish("Bún bò", locality="Huế", limit=3)
    for r in bun_bo_rests:
        print(f"  • {r['name']} - ⭐ {r.get('dish_avg_rating')} (Nhắc {r.get('mention_count')} lần)")

    print("\n🔍 Thử nghiệm 2: Tìm địa điểm lân cận 'Đại Nội Huế':")
    near_dai_noi = retriever.find_nearby_places("Đại Nội", limit=3)
    for n in near_dai_noi:
        print(f"  • {n['name']} ({n.get('category')}) - Cách {n.get('distance_km'):.2f} km")
