# -*- coding: utf-8 -*-
"""
INCREMENTAL CHROMA EMBEDDER: NHÚNG BỔ SUNG REVIEW CỐ ĐÔ HUẾ
Khóa luận: Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh
-----------------------------------------------------------------------------------------------------
- Nguồn: Các bài review MỚI của Thừa Thiên Huế (Điểm tham quan + Nhà hàng: ~7,134 bài)
  (28,757 bài khách sạn Huế trước đó đã được nhúng trong 1.69M bài).
- Mục tiêu: Mã hóa GPU bằng SentenceTransformer và upsert nối tiếp vào ChromaDB
- Model: paraphrase-multilingual-MiniLM-L12-v2 (đồng bộ 100% với toàn bộ hệ thống)
"""

import os
import sys
import time
import sqlite3
from typing import List, Dict

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import torch
import chromadb
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

DB_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "tourism_vietnam.db")
CHROMA_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "chroma_db")

GPU_BATCH_SIZE = 128
CHROMA_INSERT_BATCH = 1000
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


def clean_incomplete_hnsw_segments(chroma_dir: str):
    """Dọn dẹp các file index_metadata.pickle mồ côi (khi segment chưa build xong do tiến trình bị ngắt) để tránh lỗi Rust HNSW segment reader."""
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
                    print(f"🧹 Đã tự động dọn dẹp segment HNSW mồ côi tại: {item}", flush=True)
                except Exception:
                    pass


def embed_supplemental_hue():
    print("=" * 75)
    print("🚀 NHÚNG BỔ SUNG REVIEW MỚI CỦA HUẾ VÀO CHROMADB (INCREMENTAL)")
    print("=" * 75)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"• Thiết bị tính toán: {device.upper()}")
    if device == "cuda":
        print(f"  + GPU: {torch.cuda.get_device_name(0)}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Chỉ truy vấn các review MỚI được cào bổ sung của Huế (review_id >= 1691509)
    # Bao gồm 4,125 điểm tham quan + 3,009 nhà hàng
    cur.execute("""
        SELECT r.review_id, r.place_url, r.title, r.comment, r.reviews_rating, r.trip_type, r.visit_date
        FROM reviews r
        JOIN places p ON r.place_url = p.url
        WHERE p.is_hue = 1 AND r.review_id >= 1691509
          AND r.comment IS NOT NULL AND length(trim(r.comment)) > 0;
    """)
    rows = cur.fetchall()
    total_new_reviews = len(rows)
    print(f"• Số lượng review mới cần nhúng (Điểm tham quan & Nhà hàng Huế): {total_new_reviews:,} bài")

    if not rows:
        print("-> Không có review mới nào cần nhúng.")
        conn.close()
        return

    # Dọn dẹp HNSW mồ côi trước khi kết nối
    clean_incomplete_hnsw_segments(CHROMA_DIR)

    # Kết nối ChromaDB
    print(f"\n📦 Đang kết nối ChromaDB tại: {CHROMA_DIR}...")
    chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = chroma_client.get_or_create_collection(
        name="vietnam_reviews",
        metadata={"description": "Toàn bộ review du lịch Việt Nam gắn place_url"}
    )
    cur_count = collection.count()
    print(f"-> Collection 'vietnam_reviews' đã sẵn sàng! (Hiện có: {cur_count:,} vectors)")

    # Nạp Model
    print(f"\n🧠 Đang nạp mô hình: {MODEL_NAME} lên {device.upper()}...")
    model = SentenceTransformer(MODEL_NAME, device=device)

    # Chia batch và nạp
    t0 = time.time()
    total_upserted = 0

    print(f"\n⚡ Bắt đầu mã hóa và upsert {total_new_reviews:,} review mới vào ChromaDB...")
    for block_start in range(0, total_new_reviews, CHROMA_INSERT_BATCH):
        block = rows[block_start:block_start + CHROMA_INSERT_BATCH]
        
        block_texts = []
        block_ids = []
        block_metas = []

        for r in block:
            r_id, r_url, title, comment, rating, trip_type, visit_date = r
            full_text = f"{title}. {comment}" if title else comment
            block_texts.append(full_text[:400])
            block_ids.append(f"rev_{r_id}")
            block_metas.append({
                "place_url": r_url or "",
                "rating": float(rating) if rating is not None else 0.0,
                "trip_type": trip_type or "",
                "visit_date": visit_date or ""
            })

        # Encode GPU
        block_embs = model.encode(
            block_texts,
            batch_size=GPU_BATCH_SIZE,
            show_progress_bar=False,
            normalize_embeddings=True,
            device=device
        ).tolist()

        # Upsert với cơ chế tự dọn HNSW nếu có xung đột
        try:
            collection.upsert(
                ids=block_ids,
                documents=block_texts,
                embeddings=block_embs,
                metadatas=block_metas
            )
        except Exception as e:
            if "hnsw" in str(e).lower() or "segment" in str(e).lower():
                clean_incomplete_hnsw_segments(CHROMA_DIR)
                collection.upsert(
                    ids=block_ids,
                    documents=block_texts,
                    embeddings=block_embs,
                    metadatas=block_metas
                )
            else:
                raise e

        total_upserted += len(block)
        pct = total_upserted / total_new_reviews * 100
        print(f"   -> Đã nhúng: {total_upserted:>6,}/{total_new_reviews:,} bài ({pct:5.1f}%)")

    elapsed = time.time() - t0
    final_count = collection.count()
    print("\n" + "=" * 75)
    print(f"✅ HOÀN TẤT NHÚNG BỔ SUNG REVIEW HUẾ!")
    print(f"• Số review mới đã thêm vào ChromaDB : {total_upserted:,} bài")
    print(f"• Tổng số vectors hiện tại trong DB   : {final_count:,} bài")
    print(f"• Thời gian xử lý                     : {elapsed:.1f}s ({elapsed/60:.2f} phút)")
    print("=" * 75)

    conn.close()


if __name__ == "__main__":
    embed_supplemental_hue()
