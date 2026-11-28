# -*- coding: utf-8 -*-
"""
KIỂM THỬ TRUY XUẤT & ĐỊNH TUYẾN LƯU TRÚ (HOTEL / HOMESTAY / RESORT) TRONG GRAPHRAG
"""
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass


class TestLodgingRAG(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from src.graph.graph_retriever import get_graph_retriever
        from src.rag import agent_graph
        cls.gr = get_graph_retriever()
        cls.ag = agent_graph

    def _state(self, query, weather=None):
        return {
            "query": query, "locality": "Thành phố Huế", "preferences": {}, "image_base64": None,
            "matched_places": [], "nearby_map": {}, "dishes_map": {}, "reviews": [], "web_results": [],
            "confidence_score": 0.0, "route_taken": "local_knowledge", "graph_trace": [],
            "language": "vi", "history": [], "weather_context": weather,
        }

    def test_find_places_by_category_hotel_hue(self):
        hotels = self.gr.find_places_by_category("hotel", locality="Thành phố Huế", limit=5)
        self.assertEqual(len(hotels), 5)
        for h in hotels:
            self.assertEqual((h.get("category") or "").lower(), "hotel")

    def test_find_nearby_hotels_supplements_haversine(self):
        hotels = self.gr.find_nearby_places("place_8875", category="hotel", max_distance_km=2.0, limit=5)
        self.assertGreaterEqual(len(hotels), 3)
        for h in hotels:
            self.assertEqual((h.get("category") or "").lower(), "hotel")

    def test_general_lodging_query_uses_local_kg(self):
        q = "Gợi ý khách sạn đẹp ở trung tâm Huế?"
        kg = self.ag.node_extract_and_retrieve_kg(self._state(q))
        self.assertEqual(len(kg["matched_places"]), 5)
        self.assertTrue(all((p.get("category") or "").lower() == "hotel" for p in kg["matched_places"]))
        steps = [t.get("step") for t in kg["graph_trace"]]
        self.assertIn("lodging_kg_retrieval", steps)
        vec = self.ag.node_retrieve_vector_reviews({**self._state(q), **kg})
        self.assertEqual(self.ag.grade_confidence({**self._state(q), **kg, **vec}), "node_generate_response")

    def test_nearby_lodging_query_returns_hotels_around_landmark(self):
        q = "Gần Đại Nội Huế có khách sạn hay homestay nào tốt?"
        kg = self.ag.node_extract_and_retrieve_kg(self._state(q))
        hotels = [p for p in kg["matched_places"] if (p.get("category") or "").lower() == "hotel"]
        self.assertGreaterEqual(len(hotels), 3)
        self.assertEqual(kg["matched_places"][0].get("node_id"), "place_8875")

    def test_weather_aware_lodging_query_stays_local_and_keeps_hotels(self):
        q = "Trời mưa ở Huế nên ở khách sạn nào tiện đi lại?"
        w = {"temp": 24, "humidity": 90, "precipitation": 1.0, "weather_code": 80}
        kg = self.ag.node_extract_and_retrieve_kg(self._state(q, weather=w))
        self.assertTrue(all((p.get("category") or "").lower() == "hotel" for p in kg["matched_places"]))
        vec = self.ag.node_retrieve_vector_reviews({**self._state(q, weather=w), **kg})
        self.assertEqual(self.ag.grade_confidence({**self._state(q, weather=w), **kg, **vec}), "node_generate_response")

    def test_named_hotel_review_and_nearby_dining_ignores_stale_session_anchor(self):
        q = "Review khách sạn Meliá Vinpearl Hue thế nào và gần đó ăn gì tiện?"
        stale_ctx = {
            "anchor_place_id": "place_8875",
            "anchor_place_label": "Đại Nội Huế",
            "anchor_place_kind": "site",
            "topic_domain": "lodging",
        }
        st = {**self._state(q), "session_context": stale_ctx}
        kg = self.ag.node_extract_and_retrieve_kg(st)
        self.assertEqual(kg["target_place"], "place_37")
        self.assertEqual(kg["matched_places"][0].get("node_id"), "place_37")
        self.assertNotIn("place_8875", [p.get("node_id") for p in kg["matched_places"]])
        nearby_cats = [p.get("category", "").lower() for p in kg["matched_places"][1:]]
        self.assertTrue(any(c == "restaurant" for c in nearby_cats))
        vec = self.ag.node_retrieve_vector_reviews({**st, **kg})
        self.assertGreater(len(vec["reviews"]), 0)

    def test_format_graph_context_hides_raw_dollar_price_placeholder(self):
        hotel = self.gr.get_place("place_37")
        ctx = self.gr.format_graph_context([hotel])
        self.assertNotIn("$", ctx)
        self.assertNotIn("Partners", ctx)
        self.assertNotIn("Giá vé/Chi phí", ctx)

        dai_noi = self.gr.get_place("place_8875")
        ctx_dn = self.gr.format_graph_context([dai_noi])
        self.assertIn("200.000 VNĐ", ctx_dn)


if __name__ == "__main__":
    unittest.main(verbosity=2)

