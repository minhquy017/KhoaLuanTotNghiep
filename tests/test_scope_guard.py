# -*- coding: utf-8 -*-
"""
KIỂM THỬ SCOPE GUARD (CHỈ TRẢ LỜI CÁC CÂU HỎI DU LỊCH, ĐI LẠI, ĂN UỐNG, LƯU TRÚ TẠI HUẾ)
"""
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


class TestHueScopeGuard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from src.rag import agent_graph
        cls.ag = agent_graph

    def _state(self, query, language="vi"):
        return {
            "query": query, "locality": "Thành phố Huế", "preferences": {}, "image_base64": None,
            "image_detected": None, "visual_matches": None, "visual_confidence": 0.0,
            "target_dish": None, "target_place": None, "matched_places": [],
            "nearby_map": {}, "dishes_map": {}, "reviews": [], "web_results": [],
            "confidence_score": 0.0, "route_taken": "local_knowledge",
            "formatted_context": "", "final_answer": "", "graph_trace": [],
            "user_lat": None, "user_lng": None, "language": language,
            "session_id": None, "history": [], "session_context": None,
            "weather_context": None, "resolved_query": None, "anaphora": None,
            "is_out_of_scope": False,
        }

    def test_off_topic_sports_refused_in_invoke_and_stream(self):
        q = "ronaldo hay messi ai hay hơn?"
        res = self.ag.get_tourism_agent().invoke(self._state(q))
        self.assertTrue(res["is_out_of_scope"])
        self.assertEqual(res["matched_places"], [])
        self.assertEqual(res["web_results"], [])
        self.assertIn("Trợ lý Du lịch Cố đô Huế", res["final_answer"])

        events = list(self.ag.stream_tourism_agent_response(self._state(q)))
        tokens = [p for k, p in events if k == "token"]
        finals = [p for k, p in events if k == "final"]
        self.assertEqual(len(tokens), 1)
        self.assertIn("Trợ lý Du lịch Cố đô Huế", tokens[0])
        self.assertTrue(finals[0]["is_out_of_scope"])

    def test_other_city_tourism_refused_but_transit_to_hue_allowed(self):
        other = self.ag.node_extract_and_retrieve_kg(self._state("Du lịch Đà Nẵng có gì hay?"))
        self.assertTrue(other["is_out_of_scope"])
        self.assertEqual(other["matched_places"], [])

        to_hue = self.ag.node_extract_and_retrieve_kg(self._state("Từ Đà Nẵng đi Huế bằng tàu hỏa mất bao lâu?"))
        self.assertFalse(to_hue["is_out_of_scope"])

    def test_llm_classifier_blocks_other_and_allows_transport(self):
        class FakeClassifierLLM:
            def __init__(self, label):
                self.label = label

            def bind(self, **_kwargs):
                return self

            def invoke(self, _messages):
                return type("R", (), {"content": self.label})()

        orig = self.ag.llm
        try:
            self.ag.llm = FakeClassifierLLM("other")
            kg_other = self.ag.node_extract_and_retrieve_kg(self._state("Giải giúp tôi phương trình bậc hai?"))
            self.assertTrue(kg_other["is_out_of_scope"])
            self.assertEqual(self.ag.grade_confidence({**self._state("Giải giúp tôi phương trình bậc hai?"), **kg_other}), "node_generate_response")

            self.ag.llm = FakeClassifierLLM("transport")
            kg_transit = self.ag.node_extract_and_retrieve_kg(self._state("Ở Huế đi Grab hay thuê xe máy tiện hơn?"))
            self.assertFalse(kg_transit["is_out_of_scope"])
        finally:
            self.ag.llm = orig

    def test_english_off_topic_refused_in_english(self):
        res = self.ag.get_tourism_agent().invoke(self._state("Who is better, Ronaldo or Messi?", language="en"))
        self.assertTrue(res["is_out_of_scope"])
        self.assertIn("Huế Smart Tourism Assistant", res["final_answer"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

