# 🇻🇳 Spatial GraphRAG Tourism System
### Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh dựa trên Đồ thị Tri thức Không gian & Vision-Language Model

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/Framework-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/LLM-Qwen2.5--VL--7B-orange?style=for-the-badge" alt="Qwen2.5-VL" />
  <img src="https://img.shields.io/badge/VectorDB-ChromaDB-purple?style=for-the-badge" alt="ChromaDB" />
  <img src="https://img.shields.io/badge/Orchestrator-LangGraph-darkgreen?style=for-the-badge" alt="LangGraph" />
  <img src="https://img.shields.io/badge/Frontend-Vite%20%7C%20Leaflet-blueviolet?style=for-the-badge&logo=vite&logoColor=white" alt="Vite Leaflet" />
  <img src="https://img.shields.io/badge/LaTeX-HUET%20Standard-darkred?style=for-the-badge&logo=latex&logoColor=white" alt="LaTeX HUET" />
</p>

---

## 📌 GIỚI THIỆU TỔNG QUAN (EXECUTIVE SUMMARY)

Đề tài giải quyết triệt để vấn đề **Ảo giác Không gian (Spatial Hallucination)** và **Mù vị trí địa lý (Space-agnostic)** vốn là điểm yếu cố hữu của các mô hình Zero-shot LLM và hệ thống Naive Vector RAG truyền thống khi ứng dụng vào bài toán du lịch. 

Bằng cách tích hợp **Đồ thị Tri thức Không gian (Spatial Knowledge Graph)** với **Mô hình Thị giác - Ngôn ngữ Đa phương thức (Qwen2.5-VL-7B & CLIP)** và cơ chế điều hướng định tuyến đường bộ (OSRM), hệ thống mang lại khả năng truy xuất địa điểm, gợi ý ẩm thực bản địa và lập lộ trình du lịch thực tế với **độ chính xác cự ly tuyệt đối (0% vi phạm không gian)**.

* **Đề tài:** Khóa luận Tốt nghiệp Đại học — Ngành Khoa học Dữ liệu & Trí tuệ Nhân tạo (DS&AI K3, 2022 - 2026).
* **Đơn vị:** Khoa Kỹ thuật và Công nghệ — Đại học Huế (HUET).
* **Tác giả:** Sinh viên **Lê Hoàng Minh Quý** (MSSV: `22E1020018`).
* **Cán bộ Hướng dẫn:** **TS. Hồ Quốc Dũng**.
* **Phạm vi thử nghiệm:** Dữ liệu toàn quốc (8.921 POI) & Thực nghiệm chuyên sâu tại Cố đô Huế.

---

## 🚀 ĐÓNG GÓP & KẾT QUẢ ĐỐI SÁNH NỔI BẬT

Kết quả đánh giá định lượng trên **100 kịch bản du lịch thực tế tại Huế** (đo đạc trên môi trường GPU NVIDIA Tesla T4) cho thấy phương pháp đề xuất vượt trội so với các kỹ thuật hiện hành:

| Chỉ số Đánh giá | Zero-shot LLM | Naive RAG (Vector Only) | Spatial GraphRAG (Đề xuất) | Ý nghĩa Kỹ thuật |
| :--- | :---: | :---: | :---: | :--- |
| **Bảo chứng Thực thể (Grounding Rate)** | 85.8% | 76.0% | **100.0%** | Khắc phục hoàn toàn tình trạng bịa thực thể |
| **Tỷ lệ Ảo giác (Hallucination Rate)** | 14.2% | 24.0% | **0.0%** | Mọi địa danh và quán ăn gợi ý đều có thật |
| **Vi phạm Không gian (Spatial Violation)** | 39.1% | 39.1% | **0.0%** | Triệt tiêu lỗi nhảy bờ sông Hương & đi vòng phi lý |
| **Cự ly Trung bình đến Anchor POI** | 22.2 km | 42.3 km | **1.2 km** | Rút ngắn **97%** quãng đường tìm kiếm lân cận |
| **Độ chính xác Món ăn (Dish Alignment)** | 56.9% | 56.2% | **62.5%** | Khớp nối chính xác thực đơn đặc sản |
| **Độ trễ Suy luận (Inference Latency)** | 2.0s | 1.6s | **7.7s** | Đồ thị suy luận đa bước ổn định và tin cậy |

---

## 🏗️ KIẾN TRÚC HỆ THỐNG (SYSTEM ARCHITECTURE)

```
                         [NGƯỜI DÙNG / DU KHÁCH]
                                    │
               (Câu hỏi tự nhiên / Tọa độ GPS / Ảnh chụp địa danh)
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │   ADAPTIVE WEB STUDIO (Vite + Leaflet + Glassmorphism)   │
       └────────────────────────────┬───────────────────────────┘
                                    │ REST API
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      FASTAPI MODULAR BACKEND GATEWAY                    │
│   ├── /api/chat (LangGraph Agent)    ├── /api/itinerary (Routing)       │
│   ├── /api/kg (Graph Explorer)       └── /api/multimodal (Visual RAG)   │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │
      ┌─────────────────────────────┴─────────────────────────────┐
      ▼                                                           ▼
┌───────────────────────────────┐           ┌────────────────────────────────┐
│   SPATIAL KNOWLEDGE GRAPH     │           │     MULTIMODAL VECTOR STORE    │
│ • 9.582 nodes (POI, Dish, ...)│           │ • ChromaDB Text: 1.7M reviews  │
│ • 126.313 edges (NEAR_BY,     │           │ • ChromaDB Visual: CLIP ViT    │
│   SERVES, LOCATED_IN)         │           │ • Gazetteer: 570 món ăn Việt   │
│ • cKDTree Haversine Indexing  │           │ • MiniLM-L12-v2 Embeddings     │
└──────────────┬────────────────┘           └───────────────┬────────────────┘
               │                                            │
               └──────────────────────┬─────────────────────┘
                                      ▼
             ┌─────────────────────────────────────────────────┐
             │       REASONING ENGINE & AGENTIC WORKFLOW       │
             │   • LangGraph Multi-step State Machine          │
             │   • OSRM Engine: Tối ưu lộ trình đường bộ thật  │
             │   • Vision-Language Model: Qwen2.5-VL-7B (Colab)│
             └─────────────────────────────────────────────────┘
```

---

## 📂 CẤU TRÚC THƯ MỤC DỰ ÁN (PROJECT REPOSITORY)

```text
.
├── thesis-latex/                # Báo cáo Khóa luận & Slide thuyết trình LaTeX chuẩn HUET
│   ├── main.tex                 # File điều phối biên dịch chính (chuẩn 1967/HD-ĐHH)
│   ├── thong-tin.tex            # Biến thông tin tác giả, đề tài, hội đồng
│   ├── references.bib           # Danh mục tài liệu tham khảo chuẩn IEEE
│   ├── noi-dung/                # 5 Phần: Mở đầu, Tổng quan, Phương pháp, Thực nghiệm, Kết luận
│   └── slide/                   # Slide bảo vệ Beamer 16:9 bộ nhận diện thương hiệu HUET
│
├── data/                        # Dữ liệu & Đồ thị tri thức
│   ├── raw/                     # 1.698.641 reviews TripAdvisor & 8.921 POI toàn quốc
│   └── processed/               # SQLite, ChromaDB, Spatial KG (.gpickle), Gazetteer 570 món
│
├── src/                         # Mã nguồn hệ thống AI Core & Backend
│   ├── preprocessing/           # Làm sạch dữ liệu, chuẩn hóa tọa độ không gian
│   ├── mining/                  # Khai phá thực đơn ngầm bản địa từ 44k+ reviews
│   ├── graph/                   # Xây dựng Spatial Knowledge Graph & cKDTree
│   ├── rag/                     # Agentic GraphRAG (LangGraph + CLIP + Qwen2.5-VL)
│   ├── planner/                 # Thuật toán phân cụm không gian bờ sông Hương & OSRM
│   └── app/                     # Modular FastAPI REST API Server
│
├── frontend/                    # Giao diện Web tương tác (Vite + Leaflet + Firebase)
│   ├── index.html               # Adaptive Studio: Chatbot + Interactive Map + Cost Estimator
│   └── src/                     # Logic giao diện (main.js, map.js, api.js, budgetEstimator.js)
│
├── experiments/                 # Kịch bản thực nghiệm, đối sánh Benchmark 100 test cases
├── tests/                       # Test suite tự động toàn diện (7 modules, 55 test cases)
├── docs/                        # Tài liệu đặc tả hệ thống, báo cáo định lượng
├── requirements.txt             # Danh sách thư viện Python
├── run_demo.bat                 # Script chạy nhanh 1-click toàn bộ hệ thống
└── stop_demo.bat                # Script tắt an toàn toàn bộ tiến trình
```

---

## ⚡ HƯỚNG DẪN KHỞI CHẠY NHANH (QUICK START)

### 1. Yêu cầu Tiên quyết
* Python `3.10` trở lên.
* Node.js `18.x` trở lên & npm.
* GPU Colab / Ollama Local (chạy `Qwen2.5-VL:7b`).

### 2. Cài đặt Môi trường
```bash
# Clone kho lưu trữ
git clone https://github.com/lehoangminhquy/Spatial-GraphRAG-Tourism.git
cd Spatial-GraphRAG-Tourism

# Tạo môi trường ảo và cài đặt thư viện Python
python -m venv venv
venv\Scripts\activate       # Trên Windows (hoặc `source venv/bin/activate` trên Linux)
pip install -r requirements.txt
```

### 3. Kiểm thử Toàn hệ thống
Chạy bộ kiểm thử tự động 7 phân hệ (55 test cases) để bảo đảm toàn bộ dữ liệu, đồ thị và API hoạt động ổn định:
```bash
python tests/run_all_tests.py
```

### 4. Khởi chạy Ứng dụng
Bạn có thể khởi chạy nhanh bằng script tự động trên Windows:
```cmd
run_demo.bat
```
Hoặc khởi chạy từng phân hệ thủ công:
```bash
# Terminal 1: Khởi chạy FastAPI Backend
python -m src.app.main
# Swagger API Docs: http://localhost:8000/docs

# Terminal 2: Khởi chạy Frontend Web Studio
cd frontend
npm install
npm run dev
# Giao diện tương tác: http://localhost:5173
```

---

## 📡 TỔNG QUAN API ENDPOINTS (FASTAPI)

| Phương thức | Endpoint | Mô tả Chức năng |
| :--- | :--- | :--- |
| `POST` | `/api/chat` | Hỏi đáp tự nhiên & truy vấn du lịch đa bước qua LangGraph |
| `POST` | `/api/itinerary` | Lập lịch trình phân bổ thời gian & định tuyến cự ly ngắn nhất OSRM |
| `POST` | `/api/multimodal/identify` | Nhận diện địa danh qua hình ảnh chụp thực tế bằng CLIP & Qwen-VL |
| `GET` | `/api/kg/subgraph` | Trích xuất đồ thị con cục bộ xung quanh một địa danh/món ăn |
| `GET` | `/api/system/health` | Kiểm tra trạng thái kết nối SQLite, ChromaDB và LLM Backend |

Chi tiết các tham số và schema dữ liệu có thể tham khảo trực tiếp tại `http://localhost:8000/docs`.

---

## 🎓 BIÊN DỊCH BÁO CÁO KHÓA LUẬN (LATEX THESIS)

Báo cáo khóa luận được soạn thảo hoàn toàn bằng LaTeX, tuân thủ tuyệt đối quy định trình bày khóa luận tốt nghiệp của Đại học Huế (*Văn bản số 1967/HD-ĐHH*):

```bash
cd thesis-latex
# Biên dịch tài liệu chính
xelatex -synctex=1 -interaction=nonstopmode main.tex
bibtex main
xelatex -synctex=1 -interaction=nonstopmode main.tex
xelatex -synctex=1 -interaction=nonstopmode main.tex
```
* Bản PDF sau khi xuất sẽ được tạo tại [thesis-latex/main.pdf](file:///d:/Khóa%20luận/thesis-latex/main.pdf).

---

## 📜 GIẤY PHÉP & BẢN QUYỀN (LICENSE)

Dự án được phân phối dưới giấy phép **MIT License**. Mọi mã nguồn và dữ liệu thực nghiệm phục vụ mục đích nghiên cứu học thuật và giảng dạy đều được hoan nghênh trích dẫn theo định dạng:

```bibtex
@mastersthesis{quy2026spatialgraphrag,
  author       = {Lê Hoàng Minh Quý},
  title        = {Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh dựa trên Spatial GraphRAG và LLM},
  school       = {Khoa Kỹ thuật và Công nghệ, Đại học Huế},
  year         = {2026},
  type         = {Khóa luận Tốt nghiệp Đại học},
  address      = {Thừa Thiên Huế, Việt Nam}
}
```

---
<p align="center">
  <b>Khoa Kỹ thuật và Công nghệ — Đại học Huế (HUET)</b><br>
  <i>Ngành Khoa học Dữ liệu & Trí tuệ Nhân tạo · Niên khóa 2022 - 2026</i>
</p>
