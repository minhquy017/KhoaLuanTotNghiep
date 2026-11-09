# -*- coding: utf-8 -*-
"""
BƯỚC 3: XÂY DỰNG CHỨC NĂNG VISUAL EMBEDDINGS & CHROMADB INDEX CHO ẢNH CHECK-IN HUẾ
Khóa luận Tốt nghiệp ngành Khoa học Dữ liệu và Trí tuệ Nhân tạo (DS&AI - HUET)
Đề tài: Spatial GraphRAG - Cố đô Huế

Mô hình thị giác: OpenAI CLIP ViT-B/32 (Sentence-Transformers)
Không gian vector: 512 chiều, chuẩn hóa Euclidean (Unit Sphere)
Cơ sở dữ liệu vector: ChromaDB Collection `hue_landmarks_visual` (HNSW Cosine Space)
"""

import os
import sys

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import json
import time
import torch
import numpy as np
from PIL import Image
import chromadb
from sentence_transformers import SentenceTransformer

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

CHROMA_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "chroma_db")
METADATA_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "visual_database", "landmark_image_index.json")
COLLECTION_NAME = "hue_landmarks_visual"
CLIP_MODEL_NAME = "clip-ViT-B-32"

try:
    from src.rag.vector_retriever import (
        clean_incomplete_hnsw_segments,
        get_ascii_safe_path,
        load_sentence_transformer_fast,
    )
except ImportError:
    def get_ascii_safe_path(path: str) -> str:
        return os.path.relpath(path) if os.path.exists(path) else path

    def load_sentence_transformer_fast(model_name: str, device: str) -> SentenceTransformer:
        try:
            return SentenceTransformer(model_name, device=device, local_files_only=True)
        except Exception:
            return SentenceTransformer(model_name, device=device)

    def clean_incomplete_hnsw_segments(chroma_dir: str):
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


def build_visual_vector_index():
    print("=" * 75, flush=True)
    print("🚀 BẮT ĐẦU XÂY DỰNG HỆ THỐNG VISUAL VECTOR INDEX CHO CỐ ĐÔ HUẾ", flush=True)
    print("=" * 75, flush=True)

    if not os.path.exists(METADATA_FILE):
        print(f"❌ Không tìm thấy file metadata: {METADATA_FILE}", flush=True)
        return

    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        landmarks_meta = json.load(f)

    print(f"📂 Đã đọc {len(landmarks_meta)} ảnh mẫu từ metadata.", flush=True)

    # 1. Khởi tạo mô hình CLIP
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"⚙️ Khởi tạo mô hình CLIP ({CLIP_MODEL_NAME}) trên thiết bị: {device.upper()}...", flush=True)
    start_load = time.time()
    clip_model = load_sentence_transformer_fast(CLIP_MODEL_NAME, device=device)
    print(f"✅ Tải CLIP hoàn tất trong {time.time() - start_load:.2f}s!", flush=True)

    # 2. Khởi tạo ChromaDB với đường dẫn ASCII-safe trên Windows
    safe_chroma_dir = get_ascii_safe_path(CHROMA_DIR)
    clean_incomplete_hnsw_segments(safe_chroma_dir)
    print(f"📁 Kết nối ChromaDB tại: {safe_chroma_dir}...", flush=True)
    chroma_client = chromadb.PersistentClient(path=safe_chroma_dir)
    
    # Xóa collection cũ và collection test tạm nếu có
    for col_to_drop in (COLLECTION_NAME, "test_flush"):
        try:
            chroma_client.delete_collection(name=col_to_drop)
            if col_to_drop == COLLECTION_NAME:
                print(f"🔄 Đã làm mới collection '{COLLECTION_NAME}'...", flush=True)
        except Exception:
            pass

    collection = chroma_client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    ids = []
    metadatas = []
    documents = []
    pil_batch = []
    embeddings = []

    success_count = 0
    t0 = time.time()
    encode_batch_size = 64

    for idx, item in enumerate(landmarks_meta, 1):
        rel_path = item.get("file_path", "")
        abs_path = os.path.join(PROJECT_ROOT, rel_path.replace("/", os.sep))
        
        if not os.path.exists(abs_path):
            print(f"   ⚠️ Bỏ qua ảnh không tồn tại: {rel_path}", flush=True)
            continue
            
        try:
            with Image.open(abs_path) as raw_img:
                pil_img = raw_img.convert("RGB")
            
            img_id = item.get("image_id", f"img_{item['place_id']}_{idx:02d}")
            caption = item.get("caption", f"Ảnh {item['place_name']}")
            
            ids.append(img_id)
            pil_batch.append(pil_img)
            metadatas.append({
                "place_id": item["place_id"],
                "place_name": item["place_name"],
                "sub_location": item.get("sub_location", ""),
                "category": item.get("category", "Attraction"),
                "file_path": rel_path,
                "latitude": float(item.get("latitude", 0.0)),
                "longitude": float(item.get("longitude", 0.0))
            })
            documents.append(caption)
            success_count += 1
            
            if len(pil_batch) >= encode_batch_size:
                batch_embs = clip_model.encode(pil_batch, batch_size=encode_batch_size, normalize_embeddings=True, show_progress_bar=False)
                embeddings.extend(batch_embs.tolist())
                pil_batch.clear()
                print(f"   ⚡ Đã trích xuất đặc trưng {success_count}/{len(landmarks_meta)} ảnh ({time.time() - t0:.1f}s)...", flush=True)
        except Exception as e:
            print(f"   ❌ Lỗi trích xuất ảnh {rel_path}: {e}", flush=True)

    if pil_batch:
        batch_embs = clip_model.encode(pil_batch, batch_size=encode_batch_size, normalize_embeddings=True, show_progress_bar=False)
        embeddings.extend(batch_embs.tolist())
        pil_batch.clear()
        print(f"   ⚡ Đã trích xuất đặc trưng {success_count}/{len(landmarks_meta)} ảnh ({time.time() - t0:.1f}s)...", flush=True)

    # 3. Lưu vào ChromaDB theo batch để tránh giới hạn tham số SQLite
    if ids:
        print(f"\n💾 Đang ghi {len(ids)} vector đặc trưng vào ChromaDB...", flush=True)
        batch_size = 500
        for b_idx in range(0, len(ids), batch_size):
            b_end = min(b_idx + batch_size, len(ids))
            collection.add(
                ids=ids[b_idx:b_end],
                embeddings=embeddings[b_idx:b_end],
                metadatas=metadatas[b_idx:b_end],
                documents=documents[b_idx:b_end]
            )
            print(f"   💾 Đã nạp batch {b_end}/{len(ids)} vector...", flush=True)
        print(f"✅ Ghi thành công {collection.count()} bản ghi vào ChromaDB '{COLLECTION_NAME}'!", flush=True)

    # 4. Kiểm thử kiểm chứng thực nghiệm (Self-Verification)
    print("\n" + "=" * 75, flush=True)
    print("🔍 KIỂM THỬ KHẢ NĂNG TRUY XUẤT THỊ GIÁC (CROSS-MODAL ZERO-SHOT TEST)", flush=True)
    print("=" * 75, flush=True)

    test_queries = [
        "Cổng Ngọ Môn Đại Nội Huế",
        "Tháp chùa Thiên Mụ bảy tầng bên bờ sông Hương",
        "Lăng mộ vua Khải Định kiến trúc chạm khảm sành sứ",
        "Cây cầu Trường Tiền 6 vài 12 nhịp bắc qua sông Hương"
    ]

    for q in test_queries:
        q_emb = clip_model.encode(q, normalize_embeddings=True).tolist()
        res = collection.query(
            query_embeddings=[q_emb],
            n_results=2,
            include=["metadatas", "distances", "documents"]
        )
        print(f"\n🔎 Query Text: '{q}'", flush=True)
        metas = res["metadatas"][0]
        distances = res["distances"][0]
        for m, d in zip(metas, distances):
            cosine_sim = 1.0 - d
            print(f"   → Top Match: {m['place_name']} ({m['place_id']}) | Cosine Sim: {cosine_sim*100:.2f}% | File: {m['file_path']}", flush=True)

    print("\n" + "=" * 75, flush=True)
    print("🎉 HOÀN TẤT BƯỚC 3! HỆ THỐNG VISUAL RAG SẴN SÀNG TÍCH HỢP ĐỒ THỊ.", flush=True)
    print("=" * 75, flush=True)


if __name__ == "__main__":
    build_visual_vector_index()
