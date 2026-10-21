---
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
    num_examples: 44355
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
| **Tổng số đánh giá (Total Reviews)** | **44,355** |
| **Số địa điểm khảo sát (Unique POIs)** | **500** địa điểm tại Huế |
| **Phạm vi phân loại** | Di tích lịch sử (Attractions), Ẩm thực (Restaurants), Cà phê (Cafes), Lưu trú (Hotels) |
| **Ngôn ngữ chính** | Tiếng Anh (English) & Tiếng Việt (Vietnamese) |
| **Định dạng lưu trữ** | `.parquet` (kích hoạt Dataset Viewer), `.json` (dữ liệu thô) |

### Phân bố Điểm đánh giá (Ratings Distribution)

| Đánh giá (Star) | Số lượng | Tỷ lệ (%) |
| :---: | :---: | :---: |
| ⭐⭐⭐⭐⭐ (5.0) | 31,877 | 71.87% |
| ⭐⭐⭐⭐ (4.0) | 7,867 | 17.74% |
| ⭐⭐⭐ (3.0) | 2,747 | 6.19% |
| ⭐⭐ (2.0) | 974 | 2.20% |
| ⭐ (1.0) | 890 | 2.01% |

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
print(f"Tổng số bản ghi: {len(df)}")
print(df.head())
```

---

## 📜 Bản quyền & Giấy phép (License)
Dữ liệu được chia sẻ cho mục đích nghiên cứu học thuật, giáo dục theo giấy phép **Creative Commons Attribution 4.0 International (CC BY 4.0)**.
