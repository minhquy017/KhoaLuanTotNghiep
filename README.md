# 🇻🇳 Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh dựa trên Spatial GraphRAG & LLM
> **ĐỀ TÀI KHÓA LUẬN TỐT NGHIỆP ĐẠI HỌC — NGÀNH KHOA HỌC DỮ LIỆU & TRÍ TUỆ NHÂN TẠO**  
> **Khoa Kỹ thuật và Công nghệ — Đại học Huế (HUET)** · Khóa K3 (2022 - 2026)  
> **Sinh viên thực hiện:** Lê Hoàng Minh Quý (`22E1020025`) · **GVHD:** TS. Hồ Quốc Dũng  
> *Địa bàn nghiên cứu:* Quy mô toàn quốc (Việt Nam) & Thực nghiệm chuyên sâu tại Cố đô Huế.

---

## 🗂️ CẤU TRÚC THƯ MỤC DỰ ÁN (PROJECT STRUCTURE)

```text
d:/Khóa luận/
│
├── thesis-latex/                        # Toàn văn Khóa luận Tốt nghiệp & Slide LaTeX Beamer chuẩn HUET
│   ├── main.tex                         # Tệp điều phối biên dịch LaTeX chính (chuẩn 1967/HD-ĐHH)
│   ├── thong-tin.tex                    # Quản lý tập trung biến thông tin đề tài, sinh viên, GVHD
│   ├── references.bib                   # Danh mục tài liệu tham khảo chuẩn IEEE
│   ├── bia/                             # Các trang bìa ngoài, bìa phụ, cam đoan, tóm tắt, mục lục
│   ├── noi-dung/                        # Nội dung 5 Phần (Mở đầu, Tổng quan, Phương pháp, Thực nghiệm, Kết luận)
│   └── slide/                           # Slide bảo vệ LaTeX Beamer 16:9 chuẩn thương hiệu HUET
│
├── data/                                # Quản trị dữ liệu đa tầng
│   ├── raw/                             # Dữ liệu thô ban đầu (13 file review + metadata)
│   │   ├── raw_dataset/                 # 13 file JSON (1.698.641 reviews TripAdvisor)
│   │   └── vietnam_places_metadata.json # 8.921 địa điểm du lịch (GPS, Address, Category)
│   └── processed/                       # Dữ liệu sạch, SQLite Database, ChromaDB, Đồ thị Tri thức
│       ├── culinary_gazetteer.json      # Bộ từ điển ẩm thực chuẩn hóa 570 món ăn Việt & xứ Huế
│       ├── knowledge_graph.gpickle      # Spatial Knowledge Graph (9.525 nút, 90.948 cạnh)
│       ├── chroma_db/                   # Kho Vector ChromaDB (vietnam_reviews & hue_landmarks_visual)
│       ├── visual_database/             # Kho hình ảnh địa danh Huế phục vụ Multimodal Visual RAG
│       └── tourism_vietnam.db           # Cơ sở dữ liệu quan hệ SQLite chuẩn hóa
│
├── src/                                 # MÃ NGUỒN CỐT LÕI (CORE AI & BACKEND SYSTEM)
│   ├── preprocessing/                   # Tiền xử lý, làm sạch ngữ liệu và chuẩn hóa SQLite
│   ├── mining/                          # Khai phá thực đơn ngầm từ reviews (Gazetteer 570 món)
│   ├── graph/                           # Xây dựng & truy vấn Spatial KG (NetworkX + cKDTree Haversine)
│   ├── rag/                             # Agentic GraphRAG (LangGraph + MiniLM-L12-v2 + CLIP ViT-B/32 + Qwen2.5-VL:7b)
│   ├── planner/                         # Lập lịch trình phân cụm không gian 2 bờ sông Hương & OSRM
│   └── app/                             # Cổng RESTful API Modular (FastAPI: chat, itinerary, kg, system)
│
├── frontend/                            # GIAO DIỆN WEB TƯƠNG TÁC ĐA NỀN TẢNG (VITE + LEAFLET + FIREBASE)
│   ├── index.html                       # Giao diện Adaptive Studio (Chatbot + Bản đồ + Sổ tay + Dự toán chi phí)
│   └── src/                             # Các mô-đun điều khiển (main.js, map.js, api.js, auth.js, firebase.js, budgetEstimator.js)
│
├── experiments/                         # Kịch bản đánh giá thực nghiệm & Benchmark 12 kịch bản Huế
├── tests/                               # Bộ kiểm thử tự động toàn diện (7 phân hệ / 55 test cases)
├── scripts/                             # Kịch bản tiện ích & Notebook chạy GPU Backend trên Google Colab
├── requirements.txt                     # Danh sách thư viện Python cần thiết
├── run_demo.bat                         # Khởi chạy đồng bộ FastAPI Backend + Vite Frontend + Ollama
└── stop_demo.bat                        # Đóng an toàn các tiến trình Demo (:8000, :5173)
```

---

## 🛠️ HƯỚNG DẪN CÀI ĐẶT & KHỞI CHẠY (GETTING STARTED)

```bash
# 1. Cài đặt các thư viện Python cần thiết
pip install -r requirements.txt

# 2. Chạy bộ kiểm thử tự động toàn hệ thống (7 suites / 55 test cases)
python tests/run_all_tests.py

# 3. Khởi chạy FastAPI Backend (http://localhost:8000/docs)
python -m src.app.main

# 4. Khởi chạy Giao diện Web Frontend (http://localhost:5173)
cd frontend && npm install && npm run dev
```
