# -*- coding: utf-8 -*-
"""
SCRIPT ĐẨY CƠ SỞ DỮ LIỆU VECTOR (CHROMADB) LÊN HUGGING FACE DATASET
- Hỗ trợ Git LFS tự động cho file chroma.sqlite3 (4.56 GB).
- Tự động tạo Dataset Card (README.md) chuẩn khoa học.
- Hỗ trợ resume (tiếp tục tải lên nếu rớt mạng).
"""

import os
import sys
import argparse
from huggingface_hub import HfApi, create_repo

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
CHROMA_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "chroma_db")
CHECKPOINT_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "chroma_reviews_checkpoint.json")

DATASET_README_TEMPLATE = """---
license: mit
task_categories:
- feature-extraction
- text-retrieval
language:
- vi
- en
tags:
- tourism
- vietnam
- rag
- chromadb
- graphrag
- graduation-thesis
size_categories:
- 1M<n<10M
---

# 🇻🇳 Vietnam Tourism Reviews - ChromaDB Vector Database (1.69M Vectors)

## 📌 Tổng quan Đề tài
- **Khóa luận Tốt nghiệp ngành Khoa học Dữ liệu & Trí tuệ Nhân tạo (DS&AI K3 - Trường Kỹ thuật và Công nghệ, Đại học Huế - HUET)**
- **Đề tài:** Hệ thống hỏi đáp và gợi ý lịch trình du lịch thông minh dựa trên Đồ thị Tri thức Không gian và LLM
- **Địa bàn nghiên cứu trọng điểm (Focal Case Study):** Thừa Thiên Huế

## 📊 Thông số Kỹ thuật Dataset
- **Tổng số vectors:** 1,691,507 bài đánh giá du lịch thực tế (Places & Reviews)
- **Mô hình Embedding:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Số chiều vector:** 384 dimensions
- **Framework lưu trữ:** ChromaDB (Persistent Client với chỉ mục HNSW)
- **Dung lượng file cơ sở dữ liệu:** ~4.56 GB (`chroma.sqlite3`)

## 🚀 Cách tải và sử dụng lại (Python):
```python
from huggingface_hub import snapshot_download
import chromadb

# 1. Tải thư mục ChromaDB về máy (chỉ mất vài phút):
local_dir = snapshot_download(
    repo_id="{repo_id}",
    repo_type="dataset",
    local_dir="data/processed/chroma_db"
)

# 2. Khởi tạo ChromaDB client và truy vấn tức thì:
client = chromadb.PersistentClient(path="data/processed/chroma_db")
collection = client.get_collection("vietnam_reviews")
print(f"Tổng số vectors sẵn sàng: {{collection.count():,}}")
```
"""

def main():
    parser = argparse.ArgumentParser(description="Upload ChromaDB to Hugging Face Datasets")
    parser.add_argument("--repo_id", type=str, required=True, help="Tên repo trên Hugging Face (ví dụ: username/vietnam-tourism-chromadb)")
    parser.add_argument("--token", type=str, default=None, help="Hugging Face User Access Token (Quyền Write)")
    parser.add_argument("--private", action="store_true", default=True, help="Đặt repo ở chế độ Riêng tư (Private)")
    parser.add_argument("--public", action="store_true", help="Đặt repo ở chế độ Công khai (Public)")
    args = parser.parse_args()

    token = args.token or os.environ.get("HF_TOKEN")
    if not token:
        print("\n❌ LỖI: Bạn chưa cung cấp Hugging Face Token!")
        print("👉 Vui lòng lấy Token có quyền WRITE tại: https://huggingface.co/settings/tokens")
        print("👉 Sau đó chạy lệnh với tham số: python src/rag/upload_to_huggingface.py --repo_id YOUR_NAME/REPO --token YOUR_TOKEN\n")
        return

    is_private = not args.public if args.public else args.private

    print("=" * 80)
    print("🚀 BẮT ĐẦU ĐẨY CƠ SỞ DỮ LIỆU CHROMADB LÊN HUGGING FACE DATASETS")
    print("=" * 80)
    print(f"• Repo ID: {args.repo_id}")
    print(f"• Chế độ: {'Riêng tư (Private)' if is_private else 'Công khai (Public)'}")
    print(f"• Thư mục nguồn: {CHROMA_DIR}")

    if not os.path.exists(CHROMA_DIR):
        print(f"❌ Không tìm thấy thư mục: {CHROMA_DIR}")
        return

    api = HfApi(token=token)

    # 1. Tạo repo nếu chưa có
    print("\n[1/3] Kiểm tra / Khởi tạo Repository trên Hugging Face...")
    try:
        repo_url = create_repo(
            repo_id=args.repo_id,
            repo_type="dataset",
            private=is_private,
            token=token,
            exist_ok=True
        )
        print(f"-> Repository đã sẵn sàng: {repo_url}")
    except Exception as e:
        print(f"-> Thông báo repo: {e}")

    # 2. Tạo file README.md Dataset Card tạm
    print("\n[2/3] Chuẩn bị thông tin Dataset Card (README.md)...")
    readme_path = os.path.join(CHROMA_DIR, "README.md")
    readme_content = DATASET_README_TEMPLATE.format(repo_id=args.repo_id)
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    # 3. Tải toàn bộ thư mục lên qua Git LFS
    print("\n[3/3] Đang tải lên Hugging Face (File chroma.sqlite3 ~4.56 GB sẽ được đẩy qua Git LFS)...")
    print("⏳ Quá trình tải lên phụ thuộc vào tốc độ mạng (khoảng 3 - 8 phút). Vui lòng không tắt máy...")

    try:
        api.upload_folder(
            folder_path=CHROMA_DIR,
            repo_id=args.repo_id,
            repo_type="dataset",
            token=token
        )
        print("\n" + "=" * 80)
        print("🎉 TẢI LÊN HUGGING FACE DATASETS THÀNH CÔNG RỰC RỠ!")
        print(f"👉 Link dataset của bạn: https://huggingface.co/datasets/{args.repo_id}")
        print("=" * 80)
    except Exception as e:
        print(f"\n❌ Lỗi trong quá trình tải lên: {e}")
        print("💡 Gợi ý: Nếu rớt mạng, bạn chỉ cần chạy lại lệnh, hệ thống sẽ tự động upload tiếp từ phần dở dang.")

if __name__ == "__main__":
    main()
