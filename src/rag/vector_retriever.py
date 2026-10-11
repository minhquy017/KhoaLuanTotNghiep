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

        try:
            results = self.collection.query(
                query_embeddings=query_emb,
                n_results=n_results,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
        except Exception as e:
            # Fallback nếu filter gặp lỗi
            results = self.collection.query(
                query_embeddings=query_emb,
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        dists = results.get("distances", [[]])[0]

        formatted_reviews = []
        max_confidence = 0.0

        for doc, meta, dist in zip(docs, metas, dists):
            # Với normalized embedding, Cosine distance d in [0, 2]
            # Similarity = 1 - (dist / 2) hoặc 1 - dist (nếu metric là cosine chuẩn)
            # ChromaDB cosine distance: dist = 1 - cosine_similarity
            similarity = max(0.0, min(1.0, 1.0 - (dist / 2.0) if dist > 1.0 else 1.0 - dist))
            
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
            return "Không có dữ liệu đánh giá thực tế phù hợp."

        lines = ["### [TRẢI NGHIỆM THỰC TẾ CỦA DU KHÁCH (CHROMA REVIEWS)]"]
        for idx, rev in enumerate(reviews, 1):
            rating_star = f"⭐ {rev['rating']}/5" if rev['rating'] > 0 else ""
            trip = f"[{rev['trip_type']}]" if rev['trip_type'] else ""
            snippet = rev['text'].replace('\n', ' ').strip()
            lines.append(f"{idx}. {rating_star} {trip} \"{snippet}\"")
        return "\n".join(lines)


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
