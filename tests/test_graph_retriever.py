# -*- coding: utf-8 -*-
"""
UNIT TEST: KNOWLEDGE GRAPH RETRIEVER (NETWORKX)
Kiểm thử nạp đồ thị tri thức, truy vấn cạnh SERVES, NEAR_BY, và tìm kiếm thực thể.
"""
import unittest
from src.graph.graph_retriever import get_graph_retriever, strip_accents


class TestGraphRetriever(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retriever = get_graph_retriever()

    def test_graph_loaded_successfully(self):
        """Đồ thị phải được nạp thành công và có quy mô thực tế (> 9.000 nodes, > 80.000 edges)."""
        self.assertIsNotNone(self.retriever.G)
        num_nodes = len(self.retriever.G.nodes)
        num_edges = len(self.retriever.G.edges)
        self.assertGreater(num_nodes, 9000, f"Số nodes quá ít: {num_nodes}")
        self.assertGreater(num_edges, 80000, f"Số edges quá ít: {num_edges}")

    def test_strip_accents(self):
        """Hàm chuẩn hóa tiếng Việt loại bỏ dấu thanh sắc, huyền, hỏi, ngã, nặng."""
        self.assertEqual(strip_accents("Đại Nội Huế"), "dai noi hue")
        self.assertEqual(strip_accents("Bún Bò"), "bun bo")
        self.assertEqual(strip_accents(""), "")

    def test_find_places_by_dish_serves_edge(self):
        """Truy vấn quán ăn qua cạnh SERVES với món Bún bò Huế."""
        results = self.retriever.find_places_by_dish(dish_name="Bún bò Huế", locality="Thành phố Huế", limit=5)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0, "Không tìm thấy quán nào phục vụ Bún bò Huế")
        first_place = results[0]
        self.assertIn("name", first_place)
        self.assertTrue("street_address" in first_place or "address" in first_place)

    def test_find_nearby_places_near_by_edge(self):
        """Truy vấn các địa điểm lân cận Đại Nội Huế trong bán kính 1.5km."""
        results = self.retriever.find_nearby_places(
            place_id_or_name="place_8875",
            max_distance_km=1.5,
            limit=5
        )
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0, "Không tìm thấy địa điểm lân cận nào")
        for p in results:
            self.assertIn("distance_km", p)
            self.assertLessEqual(p["distance_km"], 1.51, f"Cự ly vượt quá bán kính quy định: {p['distance_km']}")

    def test_search_places(self):
        """Tìm kiếm địa điểm theo từ khóa danh thắng."""
        results = self.retriever.search_places(query="Thiên Mụ", limit=3)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        names = [p.get("name", "") for p in results]
        found = any("Thiên Mụ" in n or "Thien Mu" in n for n in names)
        self.assertTrue(found, f"Không tìm thấy Chùa Thiên Mụ trong kết quả: {names}")


if __name__ == "__main__":
    unittest.main()
