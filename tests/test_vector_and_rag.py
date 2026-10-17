# -*- coding: utf-8 -*-
"""
UNIT TEST: VECTOR RETRIEVER & AGENTIC RAG PIPELINE
Kiểm thử kho vector ChromaDB, mô hình SentenceTransformer và các bước phân luồng Agentic Graph.
"""
import unittest
from src.rag.vector_retriever import get_vector_retriever
from src.rag.agent_graph import node_extract_and_retrieve_kg, get_tourism_agent


class TestVectorAndRag(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vector_retriever = get_vector_retriever()
        cls.agent = get_tourism_agent()

    def test_chromadb_connection_and_collection(self):
        """ChromaDB phải kết nối được với collection vietnam_reviews."""
        self.assertIsNotNone(self.vector_retriever.collection)
        count = self.vector_retriever.collection.count()
        self.assertGreater(count, 0, "ChromaDB collection không được rỗng")

    def test_query_reviews_similarity(self):
        """Truy vấn kho review với từ khóa ẩm thực Cố Đô."""
        reviews, conf = self.vector_retriever.query_reviews(query_text="Bún bò Huế ngon chuẩn vị", n_results=3)
        self.assertIsInstance(reviews, list)
        self.assertGreater(len(reviews), 0)
        self.assertGreater(conf, 0.0)
        self.assertLessEqual(conf, 1.0)
        
        first_rev = reviews[0]
        self.assertTrue("text" in first_rev or "snippet" in first_rev)
        self.assertIn("rating", first_rev)

    def test_node_extract_and_retrieve_kg(self):
        """Kiểm thử node bóc tách thực thể và tra cứu đồ thị."""
        state = {
            "query": "Ăn bún bò Huế ở đâu ngon gần Đại Nội?",
            "locality": "Thành phố Huế",
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
            "final_answer": ""
        }
        res_state = node_extract_and_retrieve_kg(state)
        # Phải bóc tách được món Bún bò Huế và địa điểm Đại Nội
        self.assertIsNotNone(res_state.get("target_dish"))
        self.assertIsNotNone(res_state.get("target_place"))
        self.assertGreater(len(res_state.get("matched_places", [])), 0)

    def test_tourism_agent_runnable(self):
        """Agentic Graph phải được biên dịch thành công thành đối tượng Runnable."""
        self.assertIsNotNone(self.agent)


if __name__ == "__main__":
    unittest.main()
