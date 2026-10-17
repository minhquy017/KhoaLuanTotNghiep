# -*- coding: utf-8 -*-
"""
UNIT TEST: SPATIAL INDEXER & HAVERSINE PROXIMITY
Kiểm thử công thức tính khoảng cách mặt cầu và thuật toán gom cụm không gian cKDTree.
"""
import unittest
import math
from src.graph.spatial_indexer import (
    haversine_distance,
    latlon_to_cartesian,
    compute_spatial_edges,
    EARTH_RADIUS_KM
)


class TestSpatialIndexer(unittest.TestCase):
    def setUp(self):
        # Tọa độ thực tế các địa danh tại Huế
        self.dai_noi = (16.4699, 107.5786)        # Đại Nội Huế
        self.chua_thien_mu = (16.4528, 107.5451)   # Chùa Thiên Mụ
        self.cho_dong_ba = (16.4725, 107.5886)     # Chợ Đông Ba (Trần Hưng Đạo)

    def test_haversine_same_point(self):
        """Khoảng cách giữa hai điểm trùng nhau phải bằng 0."""
        dist = haversine_distance(self.dai_noi[0], self.dai_noi[1], self.dai_noi[0], self.dai_noi[1])
        self.assertAlmostEqual(dist, 0.0, places=5)

    def test_haversine_symmetry(self):
        """Khoảng cách d(A, B) phải bằng d(B, A)."""
        d_ab = haversine_distance(self.dai_noi[0], self.dai_noi[1], self.cho_dong_ba[0], self.cho_dong_ba[1])
        d_ba = haversine_distance(self.cho_dong_ba[0], self.cho_dong_ba[1], self.dai_noi[0], self.dai_noi[1])
        self.assertAlmostEqual(d_ab, d_ba, places=4)
        # Khoảng cách Đại Nội - Chợ Đông Ba tầm 1.0 - 1.5 km
        self.assertGreater(d_ab, 0.5)
        self.assertLess(d_ab, 2.0)

    def test_latlon_to_cartesian(self):
        """Chuyển đổi sang tọa độ Descartes 3D có bán kính bằng bán kính Trái Đất."""
        import numpy as np
        lats = np.array([self.dai_noi[0]])
        lons = np.array([self.dai_noi[1]])
        cart = latlon_to_cartesian(lats, lons)
        radius = np.linalg.norm(cart[0])
        self.assertAlmostEqual(radius, EARTH_RADIUS_KM, delta=0.1)

    def test_compute_spatial_edges(self):
        """Kiểm thử cKDTree sinh cạnh NEAR_BY cho các điểm lân cận."""
        places = [
            {"id": "p1", "name": "Đại Nội", "latitude": 16.4699, "longitude": 107.5786},
            {"id": "p2", "name": "Quán Cẩm (gần)", "latitude": 16.4715, "longitude": 107.5812},
            {"id": "p3", "name": "Lăng Khải Định (xa)", "latitude": 16.3989, "longitude": 107.5905}
        ]
        # Bán kính 1.5 km -> chỉ p1 và p2 lân cận nhau, p3 cách xa ~8km không nối cạnh
        edges = compute_spatial_edges(places, max_distance_km=1.5)
        connected_pairs = {(e[0], e[1]) for e in edges}
        
        # p1 nối p2
        self.assertTrue(("p1", "p2") in connected_pairs or ("p2", "p1") in connected_pairs)
        # p3 không nối với p1
        self.assertFalse(("p1", "p3") in connected_pairs)


if __name__ == "__main__":
    unittest.main()
