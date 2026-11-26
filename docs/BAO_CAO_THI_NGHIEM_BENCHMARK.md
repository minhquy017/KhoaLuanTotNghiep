# BÁO CÁO KẾT QUẢ THÍ NGHIỆM ĐỊNH LƯỢNG: ĐỐI SÁNH HIỆU NĂNG SPATIAL GRAPHRAG
**Đề tài:** Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh dựa trên Đồ thị Tri thức Không gian và LLM
**Khóa luận Tốt nghiệp ngành Khoa học Dữ liệu & Trí tuệ Nhân tạo (DS&AI K3) – Trường Kỹ thuật và Công nghệ, Đại học Huế**

- **Thời gian chạy thí nghiệm:** 2026-11-10 (Thực nghiệm định lượng 100 kịch bản trên GPU Nvidia Tesla T4 - Google Colab)
- **Mô hình suy luận cục bộ:** Qwen2.5-VL:7B (Ollama Local GPU)
- **Mô hình nhúng Vector:** SentenceTransformer (`paraphrase-multilingual-MiniLM-L12-v2`)
- **Quy mô Đồ thị Tri thức Không gian:** 9.525 nút và 90.948 cạnh quan hệ (`NEAR_BY`, `SERVES`, `LOCATED_IN`, `ORIGINATED_FROM`, trọng tâm 612 địa điểm tại Huế)
- **Quy mô Bộ kiểm thử chuẩn:** 100 kịch bản du lịch thực tế tại Huế (40 Ẩm thực & Không gian + 35 Khám phá Lân cận + 25 Lập Lịch trình)

---

## 1. TỔNG QUAN KẾT QUẢ ĐỐI SÁNH HIỆU NĂNG

| Chỉ số đánh giá | Zero-shot LLM | Naive RAG (Vector Only) | Spatial GraphRAG (Đề xuất) | Nhận xét cải tiến |
| :--- | :---: | :---: | :---: | :--- |
| **Tỷ lệ bảo chứng thực thể (Grounding Rate %)** | 85,8% | 76,0% | **100,0%** | Neo giữ thực thể theo tập nút xác thực trên đồ thị |
| **Tỷ lệ ảo giác thực thể (Hallucination %)** | 14,3% | 24,0% | **0,0%** | Kiểm soát địa danh ngoài cơ sở dữ liệu về mức 0,0% |
| **Tỷ lệ vi phạm cự ly (Spatial Violation %)** | 39,1% | 39,1% | **0,0%** | Không ghi nhận lỗi vượt ngưỡng cự ly và nhảy bờ |
| **Cự ly trung bình đến Anchor POI (km)** | 22,2 km | 42,3 km | **1,2 km** | Rút ngắn 97,2% so với Naive RAG và 94,6% so với Zero-shot |
| **Độ chính xác món ăn (Dish Alignment %)** | 56,9% | 56,2% | **62,5%** | Khớp nối chuẩn xác hơn qua thực đơn ngầm `SERVES` |
| **Thời gian đáp ứng (Inference Latency)** | 2,0s | 1,6s | **7,7s** | Độ trễ suy luận chuỗi tác tử đa bước thực nghiệm |

![Biểu đồ đối sánh định lượng](../docs/figures/benchmark_spatial_comparison.png)

---

## 2. PHÂN TÍCH CHUYÊN SÂU TỪ KẾT QUẢ THÍ NGHIỆM

### 2.1. Giải quyết bài toán Ảo giác Không gian (Spatial Hallucination)
- **Zero-shot LLM:** Do không có cơ chế tra cứu thực tế, mô hình đôi khi tự suy diễn tên quán ăn từ trí nhớ tiền huấn luyện hoặc gợi ý các quán trung tâm nằm xa điểm neo (tỷ lệ ảo giác trung bình 14,3% -- giá trị gốc 14,25%, tỷ lệ vi phạm không gian 39,1% với giá trị gốc 39,118% trên 58/100 kịch bản).
- **Naive RAG (Vector Only):** Mặc dù truy xuất được các đoạn review thực tế từ ChromaDB, cơ chế Cosine Similarity thuần túy chỉ so khớp ngữ nghĩa văn bản mà **thiếu nhận thức tọa độ không gian (Space-agnostic)**. Hệ quả là mô hình dễ kéo nhầm đánh giá của các quán ở huyện thị xa xôi hoặc ở bờ đối diện (tỷ lệ ảo giác 24,0%, vi phạm không gian 39,1% với giá trị gốc 39,116% trên 59/100 kịch bản, cự ly trung bình lên tới 42,3 km).
- **Spatial GraphRAG (Phương pháp đề xuất):** Nhờ lọc bán kính mặt cầu trên cạnh `NEAR_BY` ($d \le 1,5\text{ km}$ kết hợp định tuyến đường bộ OSRM ở tầng dẫn đường) và quan hệ món ăn `SERVES` bóc tách từ 44.355 bài review, hệ thống giữ tỷ lệ thực thể xác thực đạt 100,0% và không vi phạm ngưỡng cự ly trên tập 100 kịch bản kiểm thử (cự ly trung bình 1,24 km).

### 2.2. Khả năng tích hợp sản phẩm và tính ứng dụng thực tế
- Kết quả từ bộ thí nghiệm 100 trường hợp kiểm thử cho thấy Spatial GraphRAG đáp ứng tốt yêu cầu kiểm soát thực thể và cự ly thực địa, vừa phục vụ trực quan trên Giao diện Web tương tác bản đồ, vừa sẵn sàng triển khai thành cổng API chuẩn RESTful cho ứng dụng công dân số di động như Hue-S.
