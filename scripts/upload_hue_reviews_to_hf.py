# -*- coding: utf-8 -*-
"""
TOOL UPLOAD DỮ LIỆU ĐÁNH GIÁ DU LỊCH CỐ ĐÔ HUẾ LÊN HUGGING FACE DATASETS
Khóa luận Tốt nghiệp ngành Khoa học Dữ liệu và Trí tuệ Nhân tạo (DS&AI - HUET)
Repo đích: quylhm/reviews-hue
Tệp tải lên:
  - hue_reviews_supplement.json (File JSON thô đầy đủ 44.355 reviews)
  - hue_reviews.parquet (Định dạng Parquet chuẩn nén Snappy tối ưu cho HF Dataset Viewer)
  - hue_crawl_targets.json (Danh mục 631 địa điểm mục tiêu tại Huế)
  - README.md (Dataset Card chuẩn chỉ với metadata YAML và thống kê phân phối)
"""

import os
import sys
import io
import json
import argparse
import pandas as pd
from huggingface_hub import HfApi

# Thiết lập UTF-8 stdout cho môi trường Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def generate_dataset_card(total_reviews: int, unique_places: int, ratings_dist: dict, columns: list) -> str:
    """Tạo nội dung Dataset Card (README.md) chuẩn Hugging Face."""
    r1 = ratings_dist.get(1, ratings_dist.get(1.0, 0))
    r2 = ratings_dist.get(2, ratings_dist.get(2.0, 0))
    r3 = ratings_dist.get(3, ratings_dist.get(3.0, 0))
    r4 = ratings_dist.get(4, ratings_dist.get(4.0, 0))
    r5 = ratings_dist.get(5, ratings_dist.get(5.0, 0))

    card = f"""---
annotations_creators:
- no-annotation
language:
- en
- vi
language_creators:
- crowdsourced
license: cc-by-4.0
size_categories:
- 10K<n<100K
source_datasets:
- original
task_categories:
- text-classification
- feature-extraction
task_ids:
- sentiment-analysis
tags:
- tourism
- hue
- vietnam
- tripadvisor
- reviews
- spatial-graphrag
- travel
pretty_name: "Hue Tourism & Cultural Heritage Reviews Dataset"
dataset_info:
  features:
  - name: place_url
    dtype: string
  - name: reviewer_url
    dtype: string
  - name: title
    dtype: string
  - name: comment
    dtype: string
  - name: reviews_rating
    dtype: int64
  - name: trip_type
    dtype: string
  - name: visit_date
    dtype: string
  - name: language
    dtype: string
  splits:
  - name: train
    num_bytes: 31727271
    num_examples: {total_reviews}
configs:
- config_name: default
  data_files:
  - split: train
    path: hue_reviews.parquet
---

# 🏯 Hue Tourism & Cultural Heritage Reviews Dataset

Tập dữ liệu phản hồi, đánh giá thực tế của du khách tại **Cố đô Huế (Thừa Thiên Huế)** được thu thập tự động từ TripAdvisor. Dữ liệu phục vụ nghiên cứu và thực nghiệm cho đề tài Khóa luận Tốt nghiệp: **"Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh dựa trên Kiến trúc Spatial GraphRAG"** — Khoa Kỹ thuật và Công nghệ, Đại học Huế (HUET).

---

## 📊 Tổng quan Thống kê (Dataset Summary)

| Chỉ số | Giá trị |
| :--- | :--- |
| **Tổng số đánh giá (Total Reviews)** | **{total_reviews:,}** |
| **Số địa điểm khảo sát (Unique POIs)** | **{unique_places:,}** địa điểm tại Huế |
| **Phạm vi phân loại** | Di tích lịch sử (Attractions), Ẩm thực (Restaurants), Cà phê (Cafes), Lưu trú (Hotels) |
| **Ngôn ngữ chính** | Tiếng Anh (English) & Tiếng Việt (Vietnamese) |
| **Định dạng lưu trữ** | `.parquet` (kích hoạt Dataset Viewer), `.json` (dữ liệu thô) |

### Phân bố Điểm đánh giá (Ratings Distribution)

| Đánh giá (Star) | Số lượng | Tỷ lệ (%) |
| :---: | :---: | :---: |
| ⭐⭐⭐⭐⭐ (5.0) | {r5:,} | {r5 / total_reviews * 100:.2f}% |
| ⭐⭐⭐⭐ (4.0) | {r4:,} | {r4 / total_reviews * 100:.2f}% |
| ⭐⭐⭐ (3.0) | {r3:,} | {r3 / total_reviews * 100:.2f}% |
| ⭐⭐ (2.0) | {r2:,} | {r2 / total_reviews * 100:.2f}% |
| ⭐ (1.0) | {r1:,} | {r1 / total_reviews * 100:.2f}% |

---

## 🗂️ Cấu trúc Dữ liệu (Schema)

| Thuộc tính (Field) | Kiểu dữ liệu | Mô tả |
| :--- | :--- | :--- |
| `place_url` | `string` | Đường dẫn URL của địa điểm trên TripAdvisor |
| `reviewer_url` | `string` | Hồ sơ người đánh giá |
| `title` | `string` | Tiêu đề của bài đánh giá |
| `comment` | `string` | Nội dung phản hồi chi tiết của du khách |
| `reviews_rating` | `int64` | Điểm số đánh giá từ 1 đến 5 sao |
| `trip_type` | `string` | Hình thức chuyến đi (Couples, Family, Friends, Solo, Business) |
| `visit_date` | `string` | Thời gian trải nghiệm (Tháng/Năm) |
| `language` | `string` | Ngôn ngữ bài viết |

---

## 💻 Cách nạp dữ liệu (Quickstart)

### 1. Sử dụng thư viện `datasets` của Hugging Face
```python
from datasets import load_dataset

dataset = load_dataset("quylhm/reviews-hue")
print(dataset["train"][0])
```

### 2. Sử dụng thư viện `pandas`
```python
import pandas as pd

df = pd.read_parquet("https://huggingface.co/datasets/quylhm/reviews-hue/resolve/main/hue_reviews.parquet")
print(f"Tổng số bản ghi: {{len(df)}}")
print(df.head())
```

---

## 📜 Bản quyền & Giấy phép (License)
Dữ liệu được chia sẻ cho mục đích nghiên cứu học thuật, giáo dục theo giấy phép **Creative Commons Attribution 4.0 International (CC BY 4.0)**.
"""
    return card


def main():
    parser = argparse.ArgumentParser(description="Upload Hue reviews dataset to Hugging Face")
    parser.add_argument("--token", type=str, default="", help="HF Access Token (hoặc thiết lập biến môi trường HF_TOKEN)")
    parser.add_argument("--repo", type=str, default="quylhm/reviews-hue", help="Hugging Face Dataset Repo ID")
    parser.add_argument("--public", action="store_true", default=True, help="Set dataset visibility to Public")
    args = parser.parse_args()

    token = (args.token or os.getenv("HF_TOKEN", "")).strip()
    repo_id = args.repo.strip()

    if not token:
        print("❌ Lỗi: Chưa cung cấp Hugging Face Access Token.")
        print("   Cách 1: Chạy lệnh kèm tham số: python scripts/upload_hue_reviews_to_hf.py --token <YOUR_HF_TOKEN>")
        print("   Cách 2: Đặt biến môi trường: set HF_TOKEN=<YOUR_HF_TOKEN> (Windows) hoặc export HF_TOKEN=<YOUR_HF_TOKEN>")
        sys.exit(1)

    print("=" * 80)
    print("🚀 TIẾN TRÌNH TẢI DỮ LIỆU ĐÁNH GIÁ HUẾ LÊN HUGGING FACE DATASETS")
    print(f"🎯 Repository: https://huggingface.co/datasets/{repo_id}")
    print("=" * 80)

    # 1. Kiểm tra xác thực Token
    print("\n🔑 1. Xác thực tài khoản Hugging Face...")
    api = HfApi(token=token)
    try:
        user_info = api.whoami()
        print(f"   ✅ Đăng nhập thành công với tài khoản: {user_info['name']}")
    except Exception as e:
        print(f"   ❌ Lỗi xác thực Hugging Face: {e}")
        sys.exit(1)

    # 2. Đảm bảo Repo đã tồn tại
    print(f"\n📦 2. Khởi tạo/Kiểm tra Dataset Repository: {repo_id}...")
    try:
        api.create_repo(
            repo_id=repo_id,
            repo_type="dataset",
            private=not args.public,
            exist_ok=True
        )
        print("   ✅ Repository đã sẵn sàng tiếp nhận tệp.")
    except Exception as e:
        print(f"   ⚠️ Thông báo repo: {e}")

    # 3. Đọc dữ liệu JSON thô và chuẩn bị Parquet
    raw_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "raw", "hue_reviews_supplement.json"))
    if not os.path.exists(raw_json_path):
        print(f"❌ Không tìm thấy tệp dữ liệu thô: {raw_json_path}")
        sys.exit(1)

    raw_size_mb = os.path.getsize(raw_json_path) / (1024 * 1024)
    print(f"\n📂 3. Đọc dữ liệu đánh giá từ: {raw_json_path}")
    print(f"   • Dung lượng file thô: {raw_size_mb:.2f} MB")

    df = pd.read_json(raw_json_path)
    total_reviews = len(df)
    unique_places = df['place_url'].nunique()
    ratings_dist = df['reviews_rating'].value_counts().to_dict()

    print(f"   • Tổng số bản ghi (reviews): {total_reviews:,}")
    print(f"   • Số địa điểm duy nhất (POIs): {unique_places:,}")
    print(f"   • Phân bố rating: {sorted(ratings_dist.items())}")

    # Xuất ra Parquet tối ưu cho Hugging Face
    exports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "exports"))
    os.makedirs(exports_dir, exist_ok=True)
    parquet_path = os.path.join(exports_dir, "hue_reviews.parquet")

    print("\n⚙️ 4. Chuyển đổi dữ liệu sang định dạng Parquet (Snappy)...")
    df.to_parquet(parquet_path, engine="pyarrow", compression="snappy", index=False)
    parquet_size_mb = os.path.getsize(parquet_path) / (1024 * 1024)
    print(f"   ✅ Đã tạo tệp Parquet thành công: {parquet_path}")
    print(f"   • Dung lượng Parquet: {parquet_size_mb:.2f} MB (Tối ưu giảm ~{(1 - parquet_size_mb/raw_size_mb)*100:.1f}% dung lượng so với JSON!)")

    # Tạo tệp README.md Dataset Card
    print("\n📝 5. Sinh tài liệu Dataset Card (README.md)...")
    readme_content = generate_dataset_card(total_reviews, unique_places, ratings_dist, df.columns.tolist())
    readme_path = os.path.join(exports_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print(f"   ✅ Đã tạo Dataset Card: {readme_path}")

    # Đính kèm danh mục crawl targets nếu có
    targets_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "processed", "hue_crawl_targets.json"))

    # 6. Tải các tệp lên Hugging Face Dataset
    print("\n📤 6. Bắt đầu tải các tệp lên Hugging Face Dataset...")

    files_to_upload = [
        (parquet_path, "hue_reviews.parquet", "Upload optimized Parquet dataset for Dataset Viewer"),
        (raw_json_path, "hue_reviews_supplement.json", "Upload raw reviews JSON (44,355 items)"),
        (readme_path, "README.md", "Add comprehensive academic Dataset Card with YAML metadata")
    ]

    if os.path.exists(targets_json_path):
        files_to_upload.append(
            (targets_json_path, "hue_crawl_targets.json", "Upload Hue crawl targets catalog (631 POIs)")
        )

    for local_file, repo_path, commit_msg in files_to_upload:
        size_mb = os.path.getsize(local_file) / (1024 * 1024)
        print(f"\n   ⏳ Đang tải lên: {repo_path} ({size_mb:.2f} MB)...")
        res = api.upload_file(
            path_or_fileobj=local_file,
            path_in_repo=repo_path,
            repo_id=repo_id,
            repo_type="dataset",
            commit_message=commit_msg
        )
        print(f"   ✅ Tải lên thành công: {repo_path}")

    print("\n" + "=" * 80)
    print("🎉 TẤT CẢ DỮ LIỆU ĐÃ ĐƯỢC ĐƯA LÊN HUGGING FACE THÀNH CÔNG RỰC RỠ!")
    print(f"👉 Link Dataset trực tuyến: https://huggingface.co/datasets/{repo_id}")
    print("=" * 80)


if __name__ == "__main__":
    main()
