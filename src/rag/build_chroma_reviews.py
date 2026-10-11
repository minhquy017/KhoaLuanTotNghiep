# -*- coding: utf-8 -*-
"""
CHROMA VECTOR DATABASE BUILDER (10-PART BATCHING WITH GPU ACCELERATION)
Khóa luận: Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh
- Dữ liệu nguồn: Bảng `reviews` trong SQLite `data/processed/tourism_vietnam.db` (~1.69 triệu bài)
- Mô hình nhúng: SentenceTransformer đa ngữ (chạy trên NVIDIA GPU RTX 3050)
- Cơ chế chia 10 phần (10 Parts):
    + Mỗi phần xử lý ~169.150 bài review
    + Tự động lưu Checkpoint sau mỗi phần
    + Có thể tạm dừng và chạy tiếp bất cứ lúc nào
    + Gắn kèm metadata `place_url`, `reviews_rating`, `trip_type` phục vụ lọc phân tầng
"""

import os
import sys
import json
import time
import sqlite3
import argparse
from typing import List, Dict

# Bắt buộc UTF-8 stdout trên Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import torch
import chromadb
from sentence_transformers import SentenceTransformer


# ==============================================================================
# CẤU HÌNH ĐƯỜNG DẪN & THAM SỐ
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

DB_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "tourism_vietnam.db")
CHROMA_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "chroma_db")
CHECKPOINT_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "chroma_reviews_checkpoint.json")

TOTAL_PARTS = 10
GPU_BATCH_SIZE = 128         # Batch size nạp vào GPU RTX 3050
CHROMA_INSERT_BATCH = 2000   # Batch size đẩy vào ChromaDB mỗi lần


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
                    print(f"🧹 Đã tự động dọn dẹp segment HNSW dở dang tại: {item}", flush=True)
                except Exception:
                    pass


def get_checkpoint() -> Dict:
    """Đọc checkpoint các phần đã hoàn thành."""
    if os.path.exists(CHECKPOINT_PATH):
        try:
            with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"completed_parts": [], "total_indexed": 0, "last_updated": ""}


def save_checkpoint(completed_parts: List[int], total_indexed: int):
    """Lưu checkpoint tiến độ."""
    os.makedirs(os.path.dirname(CHECKPOINT_PATH), exist_ok=True)
    with open(CHECKPOINT_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "completed_parts": sorted(list(set(completed_parts))),
            "total_indexed": total_indexed,
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
        }, f, ensure_ascii=False, indent=2)


def build_embeddings_10_parts(model_name="paraphrase-multilingual-MiniLM-L12-v2", target_part=None):
    print("=" * 80)
    print("🚀 PIPELINE NHÚNG REVIEW VÀO CHROMADB (10 PHẦN - GPU TĂNG TỐC)")
    print("=" * 80)

    # 1. Kiểm tra GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"• Thiết bị tính toán: {device.upper()}")
    if device == "cuda":
        print(f"  + Tên GPU: {torch.cuda.get_device_name(0)}")
        print(f"  + VRAM khả dụng: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB")
    else:
        print("  ⚠️ Không phát hiện CUDA, chạy trên CPU (chậm hơn)")

    # 2. Kiểm tra CSDL SQLite
    if not os.path.exists(DB_PATH):
        print(f"❌ Không tìm thấy CSDL SQLite tại: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM reviews WHERE comment IS NOT NULL AND length(trim(comment)) > 0")
    total_reviews = cur.fetchone()[0]
    print(f"• Tổng số bài review hợp lệ trong SQLite: {total_reviews:,} bài")

    part_size = total_reviews // TOTAL_PARTS
    print(f"• Chia làm {TOTAL_PARTS} phần: Mỗi phần ~{part_size:,} bài")

    # 3. Nạp Checkpoint
    checkpoint = get_checkpoint()
    completed = set(checkpoint.get("completed_parts", []))
    total_indexed = checkpoint.get("total_indexed", 0)
    print(f"• Các phần đã hoàn thành trước đó: {sorted(list(completed)) if completed else 'Chưa có'}")

    # 4. Tự động dọn dẹp segment HNSW mồ côi nếu có và khởi tạo ChromaDB
    clean_incomplete_hnsw_segments(CHROMA_DIR)
    print(f"\n📦 Đang kết nối ChromaDB tại: {CHROMA_DIR}...")
    os.makedirs(CHROMA_DIR, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = chroma_client.get_or_create_collection(
        name="vietnam_reviews",
        metadata={"description": "Toàn bộ review du lịch Việt Nam gắn place_url"}
    )
    try:
        cur_count = collection.count()
        print(f"-> Collection 'vietnam_reviews' đã sẵn sàng! (Hiện có: {cur_count:,} vectors)")
    except Exception:
        print("-> Collection 'vietnam_reviews' đã sẵn sàng! (Đang đồng bộ chỉ mục ngầm)")

    # 5. Nạp mô hình SentenceTransformer
    print(f"\n🧠 Đang nạp mô hình: {model_name} lên {device.upper()}...")
    model = SentenceTransformer(model_name, device=device)
    print("-> Mô hình đã tải thành công!")

    # 6. Vòng lặp chạy 10 phần
    parts_to_run = [target_part] if target_part is not None else list(range(1, TOTAL_PARTS + 1))

    for p in parts_to_run:
        part_idx = p - 1  # 0-indexed
        if p in completed and target_part is None:
            print(f"\n⏭️ Phần [{p}/{TOTAL_PARTS}] đã hoàn thành từ trước. Bỏ qua.")
            continue

        offset = part_idx * part_size
        limit = part_size if p < TOTAL_PARTS else (total_reviews - offset)

        print(f"\n" + "-" * 70)
        print(f"🔥 BẮT ĐẦU PHẦN [{p}/{TOTAL_PARTS}] ({limit:,} bài review, Offset: {offset:,})")
        print("-" * 70)

        # Đọc dữ liệu phần p từ SQLite
        t0 = time.time()
        print(f"-> Đang đọc dữ liệu Phần {p} từ SQLite...")
        cur.execute("""
            SELECT review_id, place_url, title, comment, reviews_rating, trip_type, visit_date
            FROM reviews
            WHERE comment IS NOT NULL AND length(trim(comment)) > 0
            LIMIT ? OFFSET ?
        """, (limit, offset))
        rows = cur.fetchall()
        print(f"-> Đã đọc {len(rows):,} bản ghi (mất {time.time() - t0:.2f}s). Bắt đầu mã hóa GPU...")

        # Xử lý theo từng block CHROMA_INSERT_BATCH
        part_inserted = 0
        start_part_time = time.time()
        for block_start in range(0, len(rows), CHROMA_INSERT_BATCH):
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

            # Encode block trên GPU với batch_size 128
            block_embs = model.encode(
                block_texts, 
                batch_size=GPU_BATCH_SIZE, 
                show_progress_bar=False, 
                normalize_embeddings=True,
                device=device
            ).tolist()

            # Insert vào ChromaDB
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

            part_inserted += len(block)
            elapsed = time.time() - start_part_time
            speed = part_inserted / elapsed if elapsed > 0 else 0
            percent = (part_inserted / len(rows)) * 100
            print(f"   [Phần {p}] Tiến độ: {part_inserted:>7,}/{len(rows):,} ({percent:>5.1f}%) "
                  f"- Tốc độ: {speed:>5.0f} rev/s - Đã lưu ChromaDB", end="\r", flush=True)

        print(f"\n✅ ĐÃ HOÀN THÀNH PHẦN [{p}/{TOTAL_PARTS}] trong {time.time() - start_part_time:.1f}s!", flush=True)
        completed.add(p)
        total_indexed += part_inserted
        save_checkpoint(list(completed), total_indexed)
        print(f"💾 Checkpoint đã lưu an toàn: {len(completed)}/{TOTAL_PARTS} phần hoàn tất (Tổng: {total_indexed:,} vectors).", flush=True)

    conn.close()
    print("\n" + "=" * 80)
    print("🎉 TẤT CẢ CÁC PHẦN ĐÃ ĐƯỢC XỬ LÝ XONG!")
    try:
        final_cnt = collection.count()
        print(f"• Tổng số vector lưu trữ trong ChromaDB: {final_cnt:,}")
    except Exception:
        print(f"• Tổng số vector lưu trữ trong ChromaDB: ~{total_indexed:,}")
    print(f"• Đường dẫn lưu: {CHROMA_DIR}")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build ChromaDB for Tourism Reviews in 10 Parts")
    parser.add_argument("--part", type=int, default=None, help="Chạy riêng 1 phần cụ thể (1 đến 10)")
    parser.add_argument("--model", type=str, default="paraphrase-multilingual-MiniLM-L12-v2", help="Tên model SentenceTransformer")
    args = parser.parse_args()

    build_embeddings_10_parts(model_name=args.model, target_part=args.part)
