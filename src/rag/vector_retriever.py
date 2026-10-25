# -*- coding: utf-8 -*-
"""
VECTOR RETRIEVER (BỘ TRUY XUẤT VECTOR TỪ CHROMADB)
Khóa luận: Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh
- Quản lý kết nối ChromaDB `vietnam_reviews`
- Mô hình nhúng: SentenceTransformer ('paraphrase-multilingual-MiniLM-L12-v2')
- Tính toán điểm tin cậy (Relevance/Confidence Score) dựa trên khoảng cách Cosine
"""

import os
import sys
import torch
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
CHROMA_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "chroma_db")


def clean_incomplete_hnsw_segments(chroma_dir: str):
    """Dọn dẹp các file index_metadata.pickle mồ côi khi segment chưa hoàn tất để tránh lỗi Rust HNSW segment reader."""
    if not os.path.exists(chroma_dir):
        return
    for item in os.listdir(chroma_dir):
        sub = os.path.join(chroma_dir, item)
        if os.path.isdir(sub):
            files = os.listdir(sub)
            bin_files = [f for f in files if f.endswith(".bin")]
            if "index_metadata.pickle" in files and len(bin_files) == 0:
                try:
                    os.remove(os.path.join(sub, "index_metadata.pickle"))
                except Exception:
                    pass


class VectorRetriever:
    _instance = None

    def __init__(self, chroma_dir: str = CHROMA_DIR, 
                 model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.chroma_dir = chroma_dir
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.chroma_client = None
        self.collection = None
        self.model = None
        self._initialize()

    def _initialize(self):
        if not os.path.exists(self.chroma_dir):
            raise FileNotFoundError(f"Không tìm thấy thư mục ChromaDB tại: {self.chroma_dir}")

        clean_incomplete_hnsw_segments(self.chroma_dir)
        self.chroma_client = chromadb.PersistentClient(path=self.chroma_dir)
        self.collection = self.chroma_client.get_collection(name="vietnam_reviews")

        self.model = SentenceTransformer(self.model_name, device=self.device)

    def query_reviews(self, query_text: str, n_results: int = 5, 
                      place_urls: Optional[List[str]] = None) -> Tuple[List[Dict[str, Any]], float]:
        """
        Truy vấn các review liên quan nhất.
        Trả về:
            - Danh sách reviews (kèm rating, trip_type, snippet)
            - max_confidence_score: float trong khoảng [0, 1]
        """
        # Encode câu query
        query_emb = self.model.encode(
            [query_text], 
            normalize_embeddings=True, 
            device=self.device
        ).tolist()

        # Tạo bộ lọc where nếu có danh sách place_urls
        where_filter = None
        if place_urls:
            valid_urls = [u for u in place_urls if u]
            if len(valid_urls) == 1:
                where_filter = {"place_url": valid_urls[0]}
            elif len(valid_urls) > 1:
                where_filter = {"place_url": {"$in": valid_urls[:10]}}

        # Nếu có bộ lọc địa điểm cụ thể từ Knowledge Graph (Graph-Guided Retrieval):
        if where_filter:
            try:
                get_res = self.collection.get(
                    where=where_filter,
                    limit=max(n_results * 3, 10),
                    include=["documents", "metadatas"]
                )
                docs = get_res.get("documents", [])
                metas = get_res.get("metadatas", [])
                if docs:
                    import numpy as np
                    doc_embs = self.model.encode(docs, normalize_embeddings=True, device=self.device)
                    q_arr = np.array(query_emb[0])
                    sims = np.dot(doc_embs, q_arr)
                    # Sắp xếp review theo độ tương đồng giảm dần
                    sorted_indices = np.argsort(sims)[::-1][:n_results]
                    formatted_reviews = []
                    max_conf = 0.0
                    for idx in sorted_indices:
                        s = float(sims[idx])
                        # Giới hạn trong khoảng [0, 1]
                        norm_s = max(0.0, min(1.0, s / 1.5 if s > 1.0 else s))
                        if norm_s > max_conf:
                            max_conf = norm_s
                        formatted_reviews.append({
                            "text": docs[idx],
                            "rating": metas[idx].get("rating", 5.0) if metas[idx] else 5.0,
                            "trip_type": metas[idx].get("trip_type", "") if metas[idx] else "",
                            "place_url": metas[idx].get("place_url", "") if metas[idx] else "",
                            "similarity": round(norm_s, 4)
                        })
                    return formatted_reviews, round(max_conf, 4)
            except Exception:
                pass
            return [], 0.0

        try:
            results = self.collection.query(
                query_embeddings=query_emb,
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
        except Exception:
            return [], 0.0

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        dists = results.get("distances", [[]])[0]

        formatted_reviews = []
        max_confidence = 0.0

        for doc, meta, dist in zip(docs, metas, dists):
            similarity = max(0.0, min(1.0, 1.0 - (dist / 2.0) if dist > 1.0 else 1.0 - dist))
            # Chỉ lấy các review có độ tương đồng tối thiểu để tránh kéo review rác
            if similarity < 0.40:
                continue
            
            if similarity > max_confidence:
                max_confidence = similarity

            formatted_reviews.append({
                "text": doc,
                "rating": meta.get("rating", 0.0),
                "trip_type": meta.get("trip_type", ""),
                "place_url": meta.get("place_url", ""),
                "similarity": round(similarity, 4)
            })

        return formatted_reviews, round(max_confidence, 4)

    def format_reviews_context(self, reviews: List[Dict[str, Any]]) -> str:
        """Định dạng các review thành đoạn trích dẫn cô đọng cho LLM."""
        if not reviews:
            return ""

        lines = ["### [NHẬN XÉT THỰC TẾ CỦA KHÁCH DU LỊCH (THAM KHẢO THÊM)]"]
        for idx, rev in enumerate(reviews, 1):
            rating_star = f"⭐ {rev['rating']}/5" if rev['rating'] > 0 else ""
            snippet = rev['text'].replace('\n', ' ').strip()
            if len(snippet) < 15:
                continue
            lines.append(f"{idx}. {rating_star} \"{snippet[:250]}\"")
        return "\n".join(lines) if len(lines) > 1 else ""


_vector_retriever = None

def get_vector_retriever() -> VectorRetriever:
    global _vector_retriever
    if _vector_retriever is None:
        _vector_retriever = VectorRetriever()
    return _vector_retriever


if __name__ == "__main__":
    v_retriever = get_vector_retriever()
    print(f"✅ Đã nạp Vector Retriever thành công (Device: {v_retriever.device.upper()})")
    
    q = "Bún bò Huế ở đâu ngon đậm đà?"
    revs, score = v_retriever.query_reviews(q, n_results=3)
    print(f"🔍 Truy vấn: '{q}' -> Confidence Score: {score}")
    print(v_retriever.format_reviews_context(revs))
