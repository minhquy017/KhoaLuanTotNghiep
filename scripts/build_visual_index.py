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
CHROMA_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "chroma_db")
METADATA_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "visual_database", "landmark_image_index.json")
COLLECTION_NAME = "hue_landmarks_visual"
CLIP_MODEL_NAME = "clip-ViT-B-32"


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
    clip_model = SentenceTransformer(CLIP_MODEL_NAME, device=device)
    print(f"✅ Tải CLIP hoàn tất trong {time.time() - start_load:.2f}s!", flush=True)

    # 2. Khởi tạo ChromaDB
    print(f"📁 Kết nối ChromaDB tại: {CHROMA_DIR}...", flush=True)
    chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
    
    # Xóa collection cũ nếu muốn làm mới hoàn toàn
    try:
        chroma_client.delete_collection(name=COLLECTION_NAME)
        print(f"🔄 Đã làm mới collection '{COLLECTION_NAME}'...", flush=True)
    except Exception:
        pass

    collection = chroma_client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    ids = []
    embeddings = []
    metadatas = []
    documents = []

    success_count = 0
    t0 = time.time()

    for idx, item in enumerate(landmarks_meta, 1):
        rel_path = item.get("file_path", "")
        abs_path = os.path.join(PROJECT_ROOT, rel_path.replace("/", os.sep))
        
        if not os.path.exists(abs_path):
            print(f"   ⚠️ Bỏ qua ảnh không tồn tại: {rel_path}", flush=True)
            continue
            
        try:
            pil_img = Image.open(abs_path).convert("RGB")
            # Trích xuất vector đặc trưng 512 chiều từ ảnh
            emb = clip_model.encode(pil_img, normalize_embeddings=True)
            
            img_id = item.get("image_id", f"img_{item['place_id']}_{idx:02d}")
            caption = item.get("caption", f"Ảnh {item['place_name']}")
            
            ids.append(img_id)
            embeddings.append(emb.tolist())
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
            
            if success_count % 5 == 0 or success_count == len(landmarks_meta):
                print(f"   ⚡ Đã trích xuất đặc trưng {success_count}/{len(landmarks_meta)} ảnh ({time.time() - t0:.1f}s)...", flush=True)
        except Exception as e:
            print(f"   ❌ Lỗi trích xuất ảnh {rel_path}: {e}", flush=True)

    # 3. Lưu vào ChromaDB theo batch
    if ids:
        print(f"\n💾 Đang ghi {len(ids)} vector đặc trưng vào ChromaDB...", flush=True)
        collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
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
