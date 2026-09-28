# 🇻🇳 Smart Tourism QA & Itinerary Recommendation System via Spatial Knowledge Graph and Large Language Models
> **ĐỀ TÀI KHÓA LUẬN TỐT NGHIỆP ĐẠI HỌC — NGÀNH TRÍ TUỆ NHÂN TẠO (AI)**  
> **Trường Đại học Khoa học — Đại học Huế** · Khoa Công nghệ Thông tin · Khóa 3 (2022 - 2026)  
> *Địa bàn nghiên cứu:* Quy mô toàn quốc (Việt Nam) & Thực nghiệm trọng điểm tại Thừa Thiên Huế.

---

## 🗂️ CẤU TRÚC THƯ MỤC CHUẨN ĐỒ ÁN (PROJECT STRUCTURE)

```text
d:/Khóa luận/
│
├── docs/                                # Hồ sơ học thuật, đề cương, báo cáo Word
│   ├── DE_CUONG_CHI_TIET_KHOA_LUAN_TOT_NGHIEP.docx
│   ├── KHUNG_NGHIEN_CUU_VA_THI_NGHIEM_KHOA_LUAN.docx
│   ├── generate_full_thesis_proposal_docx.py
│   └── generate_thesis_framework_docx.py
│
├── data/                                # Quản trị dữ liệu đa tầng
│   ├── raw/                             # Dữ liệu thô ban đầu (13 file review + metadata)
│   │   ├── raw_dataset/                 # 13 file JSON (~1.7 triệu reviews, 1.25 GB)
│   │   └── vietnam_places_metadata.json # 8,363 địa điểm du lịch (GPS, Address, Category)
│   ├── processed/                       # Dữ liệu sạch, SQLite Database, Từ điển ẩm thực
│   │   ├── culinary_gazetteer.json      # Bộ từ điển 250+ món ăn Việt & xứ Huế
│   │   └── tourism_vietnam.db           # SQLite DB quan hệ chuẩn hóa
│   └── exports/                         # Bảng dữ liệu trích xuất, báo cáo thống kê
│
├── crawlers/                            # Mã nguồn thu thập dữ liệu (TripAdvisor)
│   ├── crawl_places_metadata.py         # Crawler JSON-LD toạ độ GPS & địa chỉ
│   ├── merge_metadata.py                # Hợp nhất metadata từ các worker
│   ├── vietnam-attraction-crawler/      # Crawler điểm tham quan
│   ├── vietnam-hotel-crawler/           # Crawler khách sạn
│   └── vietnam-restaurant-crawler/      # Crawler nhà hàng
│
├── src/                                 # MÃ NGUỒN CỐT LÕI (CORE AI SYSTEM)
│   ├── preprocessing/                   # [GĐ 1] Nối bảng (JOIN), làm sạch dữ liệu
│   ├── mining/                          # [GĐ 1] Khai phá thực thể món ăn (spaCy + Gazetteer)
│   ├── graph/                           # [GĐ 2] Xây dựng Spatial Knowledge Graph (NetworkX/Neo4j)
│   ├── rag/                             # [GĐ 2-3] Kiến trúc 2-Tier RAG & Embedding (BAAI/bge-m3)
│   ├── planner/                         # [GĐ 3] Tối ưu hóa chuỗi điểm dừng (TSP / Clustering)
│   └── app/                             # [GĐ 4] Giao diện Web tương tác (Streamlit + Folium)
│
├── experiments/                         # Các bài thực nghiệm & đo đạc định lượng (Tuần 7-8)
│   ├── survey_dataset_linkage.py        # Khảo sát độ khớp dữ liệu (82.3% khớp, 420k nhà hàng)
│   └── ...
│
├── notebooks/                           # Phân tích dữ liệu thăm dò (EDA) & Trực quan hóa
├── requirements.txt                     # Danh sách thư viện Python cần thiết
└── README.md                            # Tài liệu hướng dẫn tổng quan dự án
```

---

## 📈 LỘ TRÌNH 4 GIAI ĐOẠN TRIỂN KHAI (WORKFLOW PHASES)

1. **Giai đoạn 1 (Tuần 1 - 2):** Tiền xử lý dữ liệu, làm sạch, Relational JOIN vào SQLite và Khai phá Thực thể Ẩm thực (Food Entity Mining).
2. **Giai đoạn 2 (Tuần 3 - 4):** Xây dựng Đồ thị Tri thức Không gian (Spatial KG) và Lập chỉ mục Vector 2 tầng (Two-Tier Hierarchical RAG).
3. **Giai đoạn 3 (Tuần 5 - 6):** Thiết lập đường ống GraphRAG và Thuật toán tối ưu hóa hành trình (Heuristic TSP / Spatial Clustering).
4. **Giai đoạn 4 (Tuần 7 - 8):** Đóng gói Giao diện Web tương tác (Streamlit) và Thực hiện 4 bài Thí nghiệm định lượng (RAGAS, F1-Score, Spatial Feasibility Rate).

---

## 🛠️ CÀI ĐẶT MÔI TRƯỜNG (GETTING STARTED)

```bash
# 1. Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# 2. Chạy khảo sát kiểm tra liên kết dữ liệu
python experiments/survey_dataset_linkage.py
```
