# -*- coding: utf-8 -*-
"""
UNIT & INTEGRATION TEST: VISUAL IMAGE RAG & MULTIMODAL SPATIAL AGENT
Hệ thống Khóa luận Tốt nghiệp DS & AI - HUET
"""

import os
import sys
import base64
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.rag.visual_retriever import get_visual_retriever
from src.rag.agent_graph import get_tourism_agent


class TestVisualRAG(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vr = get_visual_retriever()
        cls.agent = get_tourism_agent()
        cls.test_image_path = os.path.join(
            PROJECT_ROOT, "data", "processed", "visual_database", "images", "place_8875", "img_01.jpg"
        )

    def test_01_visual_retriever_ready(self):
        self.assertTrue(self.vr.is_ready(), "VisualRetriever must be initialized with collection ready")
        self.assertGreaterEqual(self.vr.collection.count(), 70)

    def test_02_query_by_image_file(self):
        if not os.path.exists(self.test_image_path):
            self.skipTest("Sample test image not found")
        matches, conf = self.vr.query_by_image(self.test_image_path, n_results=3)
        self.assertGreater(len(matches), 0)
        self.assertGreaterEqual(conf, 0.70)
        self.assertEqual(matches[0]["place_id"], "place_8875")

    def test_03_query_by_image_base64(self):
        if not os.path.exists(self.test_image_path):
            self.skipTest("Sample test image not found")
        with open(self.test_image_path, "rb") as f:
            b64_str = base64.b64encode(f.read()).decode("utf-8")
        matches, conf = self.vr.query_by_image(f"data:image/jpeg;base64,{b64_str}", n_results=3)
        self.assertGreater(len(matches), 0)
        self.assertGreaterEqual(conf, 0.70)
        self.assertEqual(matches[0]["place_id"], "place_8875")

    def test_04_agent_graph_with_image(self):
        if not os.path.exists(self.test_image_path):
            self.skipTest("Sample test image not found")
        with open(self.test_image_path, "rb") as f:
            b64_str = base64.b64encode(f.read()).decode("utf-8")

        initial_state = {
            "query": "Ảnh này chụp ở đâu thế?",
            "locality": "Thành phố Huế",
            "preferences": {},
            "image_base64": b64_str,
            "image_detected": None,
            "visual_matches": None,
            "visual_confidence": 0.0,
            "target_dish": None,
            "target_place": None,
            "matched_places": [],
            "nearby_map": {},
            "dishes_map": {},
            "reviews": [],
            "web_results": [],
            "confidence_score": 0.0,
            "route_taken": "local_knowledge",
            "formatted_context": "",
            "final_answer": "",
            "graph_trace": []
        }
        res = self.agent.invoke(initial_state)
        self.assertIsNotNone(res.get("visual_matches"))
        self.assertGreaterEqual(res.get("visual_confidence", 0.0), 0.70)
        matched_ids = [p.get("node_id") for p in res.get("matched_places", [])]
        self.assertIn("place_8875", matched_ids)
        step_names = [s.get("step") for s in res.get("graph_trace", [])]
        self.assertIn("visual_rag_match", step_names)
        self.assertIn("Đại Nội", res.get("final_answer", ""))


if __name__ == "__main__":
    unittest.main()
