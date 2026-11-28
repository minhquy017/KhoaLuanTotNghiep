# -*- coding: utf-8 -*-
"""
KIỂM THỬ HYBRID ROUTING 2 TẦNG + CÂN BẰNG ĐA DANH MỤC LÂN CẬN + STRICT GROUNDING
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


class TestHybridIntentAndGrounding(unittest.TestCase):
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

    def test_diverse_nearby_places_covers_all_three_categories(self):
        res = self.gr.find_diverse_nearby_places("place_8875", max_distance_km=2.0, per_category=2)
        cats = {(p.get("category") or "").lower() for p in res}
        self.assertIn("attraction", cats)
        self.assertIn("restaurant", cats)
        self.assertIn("hotel", cats)

    def test_generic_nearby_query_uses_diverse_categories(self):
        kg = self.ag.node_extract_and_retrieve_kg(self._state("Quanh Đại Nội Huế có chỗ nào hay?"))
        cats = {(p.get("category") or "").lower() for p in kg["matched_places"][1:]}
        self.assertIn("hotel", cats)
        self.assertIn("restaurant", cats)

    def test_llm_intent_fallback_handles_unseen_slang_query(self):
        class FakeClassifierLLM:
            def __init__(self, label):
                self.label = label

            def bind(self, **_kwargs):
                return self

            def invoke(self, _messages):
                return type("R", (), {"content": self.label})()

        orig = self.ag.llm
        try:
            self.ag.llm = FakeClassifierLLM("lodging")
            kg = self.ag.node_extract_and_retrieve_kg(
                self._state("Kiếm chỗ nào ngả lưng yên tĩnh buổi tối ở Huế?")
            )
            self.assertEqual(len(kg["matched_places"]), 5)
            self.assertTrue(all((p.get("category") or "").lower() == "hotel" for p in kg["matched_places"]))
            steps = [s.get("step") for s in kg["graph_trace"]]
            self.assertIn("llm_intent_kg_retrieval", steps)

            self.ag.llm = FakeClassifierLLM("other")
            kg_other = self.ag.node_extract_and_retrieve_kg(
                self._state("Giá vàng hôm nay ở Huế bao nhiêu?")
            )
            self.assertEqual(kg_other["matched_places"], [])
        finally:
            self.ag.llm = orig

    def test_global_strict_grounding_in_both_languages(self):
        prep_vi = self.ag._prepare_generation_inputs(self._state("Quanh Đại Nội có gì?"))
        self.assertIn("TRUNG THỰC TUYỆT ĐỐI THEO NGỮ CẢNH", prep_vi["system_prompt"])

        st_en = {**self._state("What is near the Citadel?"), "language": "en"}
        prep_en = self.ag._prepare_generation_inputs(st_en)
        self.assertIn("STRICT CONTEXT GROUNDING", prep_en["system_prompt"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

