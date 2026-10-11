# -*- coding: utf-8 -*-
"""
SPATIAL INDEXER & HAVERSINE PROXIMITY CALCULATOR
Khóa luận: Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh
-----------------------------------------------------------------------------------------------------
- Sử dụng công thức Haversine chuẩn và cấu trúc dữ liệu cKDTree (3D Cartesian Projection)
- Khai thác quan hệ không gian NEAR_BY giữa các địa điểm du lịch trong bán kính R:
  + Khoảng cách đường chim bay (distance_km)
  + Thời gian đi bộ ước tính (walk_time_min, tốc độ v = 4.5 km/h)
  + Thời gian đi xe máy/ô tô đô thị ước tính (drive_time_min, tốc độ v = 25 km/h + 2 phút chờ đèn/giao thông)
"""

import math
import numpy as np
from typing import List, Tuple, Dict, Any
from scipy.spatial import cKDTree

EARTH_RADIUS_KM = 6371.0088


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Tính khoảng cách Haversine giữa 2 tọa độ GPS (km)."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return EARTH_RADIUS_KM * c


def latlon_to_cartesian(lats: np.ndarray, lons: np.ndarray) -> np.ndarray:
    """Chuyển đổi tọa độ vĩ độ/kinh độ sang tọa độ Descartes 3D trên mặt cầu Trái Đất (km)."""
    phi = np.radians(lats)
    lam = np.radians(lons)
    x = EARTH_RADIUS_KM * np.cos(phi) * np.cos(lam)
    y = EARTH_RADIUS_KM * np.cos(phi) * np.sin(lam)
    z = EARTH_RADIUS_KM * np.sin(phi)
    return np.column_stack((x, y, z))


def compute_spatial_edges(
    places: List[Dict[str, Any]], 
    max_distance_km: float = 1.2,
    max_neighbors_per_node: int = 10
) -> List[Tuple[str, str, Dict[str, Any]]]:
    """
    Tìm kiếm nhanh các cặp địa điểm lân cận trong bán kính `max_distance_km` bằng cKDTree.
    
    Quy tắc nghiệp vụ:
    - Chỉ kết nối các địa điểm có tọa độ hợp lệ (lat, lon != 0.0 và nằm trong VN).
    - Cùng tỉnh/thành hoặc bán kính <= max_distance_km.
    - Giới hạn tối đa `max_neighbors_per_node` cạnh cho mỗi địa điểm để tránh làm đồ thị quá dày đặc.
    """
    valid_places = []
    for p in places:
        lat = p.get("latitude")
        lon = p.get("longitude")
        if lat and lon and (8.0 <= lat <= 24.0) and (102.0 <= lon <= 110.0):
            valid_places.append(p)

    if len(valid_places) < 2:
        return []

    lats = np.array([p["latitude"] for p in valid_places], dtype=np.float64)
    lons = np.array([p["longitude"] for p in valid_places], dtype=np.float64)
    coords_3d = latlon_to_cartesian(lats, lons)

    # Khoảng cách dây cung (chord distance) tương ứng với khoảng cách vòng cung trên mặt cầu
    # chord = 2 * R * sin(d / (2 * R))
    chord_threshold = 2.0 * EARTH_RADIUS_KM * math.sin(max_distance_km / (2.0 * EARTH_RADIUS_KM))

    tree = cKDTree(coords_3d)
    
    # Tìm kiếm các cặp lân cận
    edge_candidates = tree.query_pairs(r=chord_threshold, output_type='ndarray')

    # Nhóm theo từng node để kiểm soát bậc (degree cap)
    from collections import defaultdict
    node_neighbors = defaultdict(list)

    for i, j in edge_candidates:
        p_i = valid_places[i]
        p_j = valid_places[j]

        # Kiểm tra cùng tỉnh/thành nếu có thông tin (tránh nối xuyên địa giới cách sông/núi)
        loc_i = p_i.get("locality", "").strip()
        loc_j = p_j.get("locality", "").strip()
        if loc_i and loc_j and loc_i != loc_j:
            continue

        # Tính khoảng cách bề mặt thực tế
        dist = haversine_distance(p_i["latitude"], p_i["longitude"], p_j["latitude"], p_j["longitude"])
        if dist <= max_distance_km:
            node_neighbors[p_i["id"]].append((p_j["id"], dist))
            node_neighbors[p_j["id"]].append((p_i["id"], dist))

    edges = []
    seen_pairs = set()

    for u, neighbors in node_neighbors.items():
        # Sắp xếp các điểm gần nhất trước, lấy tối đa max_neighbors_per_node
        neighbors.sort(key=lambda x: x[1])
        for v, dist in neighbors[:max_neighbors_per_node]:
            pair_key = tuple(sorted([u, v]))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            walk_time = round((dist / 4.5) * 60.0, 1)  # v = 4.5 km/h
            drive_time = round((dist / 25.0) * 60.0 + 2.0, 1)  # v = 25 km/h + 2 phút chờ

            edge_data = {
                "relation": "NEAR_BY",
                "distance_km": round(dist, 3),
                "distance_m": int(round(dist * 1000)),
                "walk_time_min": max(1.0, walk_time),
                "drive_time_min": max(1.0, drive_time)
            }
            # Thêm cạnh vô hướng (đồ thị có hướng thì thêm 2 chiều u -> v và v -> u)
            edges.append((u, v, edge_data))
            edges.append((v, u, edge_data))

    return edges
