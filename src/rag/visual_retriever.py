# -*- coding: utf-8 -*-
"""
VISUAL RETRIEVER (BỘ TRUY XUẤT THỊ GIÁC MULTIMODAL TỪ CHROMADB)
Khóa luận: Spatial GraphRAG - Cố đô Huế (HUET)
- Quản lý bộ sưu tập vector ảnh mẫu: `hue_landmarks_visual` trong ChromaDB
- Mô hình nhúng thị giác: OpenAI CLIP ViT-B/32 (512 chiều)
- Tính toán độ tương đồng Cosine giữa ảnh du khách và kho ảnh địa danh Huế
- Khớp định danh thực thể (Entity Alignment) trực tiếp với Spatial Knowledge Graph qua `place_id`
"""

import os
import sys
import io
import base64
import torch
import numpy as np
from PIL import Image
from typing import List, Dict, Any, Optional, Tuple, Union
import chromadb
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
CHROMA_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "chroma_db")
COLLECTION_NAME = "hue_landmarks_visual"
CLIP_MODEL_NAME = "clip-ViT-B-32"


class VisualRetriever:
    _instance = None

    def __init__(self, chroma_dir: str = CHROMA_DIR, model_name: str = CLIP_MODEL_NAME):
        self.chroma_dir = chroma_dir
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.chroma_client = None
        self.collection = None
        self.model = None
        self._initialize()

    @classmethod
    def get_instance(cls, chroma_dir: str = CHROMA_DIR) -> "VisualRetriever":
        if cls._instance is None:
            cls._instance = cls(chroma_dir=chroma_dir)
        return cls._instance

    def _initialize(self):
        """Khởi tạo kết nối tới ChromaDB và mô hình CLIP."""
        if not os.path.exists(self.chroma_dir):
            print(f"⚠️ [VisualRetriever] Chưa phát hiện ChromaDB tại: {self.chroma_dir}")
            return

        try:
            self.chroma_client = chromadb.PersistentClient(path=self.chroma_dir)
            try:
                self.collection = self.chroma_client.get_collection(name=COLLECTION_NAME)
                print(f"✅ [VisualRetriever] Đã kết nối Collection '{COLLECTION_NAME}' ({self.collection.count()} ảnh)!")
            except Exception:
                print(f"⚠️ [VisualRetriever] Collection '{COLLECTION_NAME}' chưa được khởi tạo. Cần chạy scripts/build_visual_index.py.")
                self.collection = None

            self.model = SentenceTransformer(self.model_name, device=self.device)
            print(f"✅ [VisualRetriever] Đã tải mô hình thị giác CLIP ({self.model_name}) trên {self.device.upper()}!")
        except Exception as e:
            print(f"⚠️ [VisualRetriever] Không thể khởi tạo VisualRetriever: {e}")

    def is_ready(self) -> bool:
        """Kiểm tra xem hệ thống Visual RAG đã sẵn sàng hoạt động hay chưa."""
        return self.collection is not None and self.model is not None and self.collection.count() > 0

    def _decode_image_input(self, image_input: Union[str, Image.Image]) -> Optional[Image.Image]:
        """Chuyển đổi file path, chuỗi base64 hoặc PIL Image thành đối tượng PIL Image chuẩn RGB."""
        if isinstance(image_input, Image.Image):
            return image_input.convert("RGB")
        
        if isinstance(image_input, str):
            # 1. Nếu là đường dẫn file ảnh cục bộ
            if os.path.exists(image_input):
                try:
                    return Image.open(image_input).convert("RGB")
                except Exception as e:
                    print(f"⚠️ [VisualRetriever] Lỗi đọc file ảnh {image_input}: {e}")
                    return None

            # 2. Nếu là chuỗi Base64
            try:
                raw_b64 = image_input
                if "base64," in raw_b64:
                    raw_b64 = raw_b64.split("base64,")[1]
                
                img_bytes = base64.b64decode(raw_b64)
                img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                return img
            except Exception as e:
                print(f"⚠️ [VisualRetriever] Lỗi giải mã chuỗi ảnh base64: {e}")
                return None
        return None

    def query_by_image(self, image_input: Union[str, Image.Image], 
                       n_results: int = 3) -> Tuple[List[Dict[str, Any]], float]:
        """
        Truy vấn các địa danh Huế có đặc trưng thị giác tương đồng nhất với ảnh đầu vào.
        
        Args:
            image_input: Chuỗi Base64 hoặc PIL Image
            n_results: Số lượng địa danh gần nhất cần lấy
            
        Returns:
            - List[Dict]: Danh sách top địa danh khớp kèm place_id, similarity, metadata
            - float: Điểm tương đồng Cosine cao nhất (max_similarity) trong khoảng [0.0, 1.0]
        """
        if not self.is_ready():
            return [], 0.0

        pil_img = self._decode_image_input(image_input)
        if pil_img is None:
            return [], 0.0

        try:
            # 1. Trích xuất vector đặc trưng thị giác 512-dim
            query_emb = self.model.encode(
                pil_img, 
                normalize_embeddings=True, 
                device=self.device
            ).tolist()

            # 2. Truy vấn vector trong ChromaDB theo khoảng cách Cosine
            results = self.collection.query(
                query_embeddings=[query_emb],
                n_results=min(n_results, self.collection.count()),
                include=["metadatas", "distances", "documents"]
            )

            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]
            documents = results.get("documents", [[]])[0]

            matched_results = []
            max_sim = 0.0

            for meta, dist, doc in zip(metadatas, distances, documents):
                # Trong ChromaDB với cosine space: distance = 1 - cosine_similarity
                cosine_sim = max(0.0, min(1.0, 1.0 - dist))
                if cosine_sim > max_sim:
                    max_sim = cosine_sim

                matched_results.append({
                    "place_id": meta.get("place_id"),
                    "place_name": meta.get("place_name"),
                    "sub_location": meta.get("sub_location"),
                    "category": meta.get("category", "Attraction"),
                    "file_path": meta.get("file_path"),
                    "latitude": meta.get("latitude"),
                    "longitude": meta.get("longitude"),
                    "caption": doc,
                    "similarity": round(float(cosine_sim), 4),
                    "confidence_pct": round(float(cosine_sim) * 100, 1)
                })

            return matched_results, round(float(max_sim), 4)
        except Exception as e:
            print(f"⚠️ [VisualRetriever] Lỗi khi truy vấn ảnh: {e}")
            return [], 0.0

    def query_by_text(self, text_query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Tìm kiếm ảnh địa danh Huế bằng mô tả văn bản (Cross-Modal Zero-Shot Search).
        """
        if not self.is_ready():
            return []

        try:
            text_emb = self.model.encode(
                text_query, 
                normalize_embeddings=True, 
                device=self.device
            ).tolist()

            results = self.collection.query(
                query_embeddings=[text_emb],
                n_results=min(n_results, self.collection.count()),
                include=["metadatas", "distances", "documents"]
            )

            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]
            documents = results.get("documents", [[]])[0]

            matches = []
            for meta, dist, doc in zip(metadatas, distances, documents):
                cosine_sim = max(0.0, min(1.0, 1.0 - dist))
                matches.append({
                    "place_id": meta.get("place_id"),
                    "place_name": meta.get("place_name"),
                    "sub_location": meta.get("sub_location"),
                    "category": meta.get("category"),
                    "file_path": meta.get("file_path"),
                    "similarity": round(float(cosine_sim), 4),
                    "confidence_pct": round(float(cosine_sim) * 100, 1)
                })
            return matches
        except Exception as e:
            print(f"⚠️ [VisualRetriever] Lỗi truy vấn text-to-image: {e}")
            return []


def get_visual_retriever() -> VisualRetriever:
    return VisualRetriever.get_instance()

