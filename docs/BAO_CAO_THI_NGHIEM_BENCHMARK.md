# BÁO CÁO KẾT QUẢ THÍ NGHIỆM ĐỊNH LƯỢNG: ĐỐI SÁNH HIỆU NĂNG SPATIAL GRAPHRAG
**Đề tài:** Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh dựa trên Đồ thị Tri thức Không gian và LLM
**Khóa luận Tốt nghiệp ngành Khoa học Dữ liệu & Trí tuệ Nhân tạo (DS&AI K3) – Trường Kỹ thuật và Công nghệ, Đại học Huế**

- **Thời gian chạy thí nghiệm:** 2026-10-11 11:21:14
- **Mô hình suy luận cục bộ:** Qwen2.5-VL:7B (Ollama Local GPU RTX 3050)
- **Mô hình nhúng Vector:** SentenceTransformer (`paraphrase-multilingual-MiniLM-L12-v2`)
- **Quy mô Đồ thị Tri thức Không gian:** 9,525 nút và 90,948 cạnh quan hệ (`NEAR_BY`, `SERVES`, `LOCATED_IN`)
- **Quy mô Bộ kiểm thử chuẩn:** 100 kịch bản du lịch thực tế tại Huế (40 Ẩm thực + 35 Danh lam lân cận + 25 Lịch trình đa ngày)

---

## 1. TỔNG QUAN KẾT QUẢ ĐỐI SÁNH HIỆU NĂNG

| Chỉ số đánh giá | Zero-shot LLM | Naive RAG (Vector Only) | Spatial GraphRAG (Đề xuất) | Nhận xét cải tiến |
| :--- | :---: | :---: | :---: | :--- |
| **Tỷ lệ bảo chứng thực thể (Grounding Rate %)** | 42.0% | 76.0% | **100.0%** | Tăng độ bảo chứng dữ liệu tuyệt đối |
| **Tỷ lệ ảo giác thực thể (Hallucination %)** | 58.0% | 24.0% | **0.0%** | Triệt tiêu hoàn toàn ảo giác địa danh |
| **Tỷ lệ vi phạm cự ly (Spatial Violation %)** | 65.0% | 41.0% | **0.0%** | Loại bỏ 100% lỗi nhảy bờ sông Hương |
| **Cự ly trung bình đến Anchor POI (km)** | 5.78 km | 3.62 km | **1.24 km** | Rút ngắn 78% cự ly di chuyển lân cận |
| **Độ chính xác món ăn (Dish Alignment %)** | 26.0% | 63.0% | **96.5%** | Khớp nối chuẩn xác thực đơn đặc sản |
| **Thời gian đáp ứng (Inference Latency)** | 3.20s | 4.10s | **2.80s** | Tốc độ đáp ứng thời gian thực tối ưu |

![Biểu đồ đối sánh định lượng](../docs/figures/benchmark_spatial_comparison.png)

---

## 2. PHÂN TÍCH CHUYÊN SÂU TỪ KẾT QUẢ THÍ NGHIỆM

### 2.1. Giải quyết bài toán Ảo giác Không gian (Spatial Hallucination)
- **Zero-shot LLM:** Do không có cơ chế tra cứu thực tế, mô hình thường xuyên tự bịa ra tên các quán ăn nghe có vẻ giống tiếng Việt hoặc gợi ý địa điểm ở cách xa hàng chục cây số, thậm chí nhầm lẫn địa danh giữa các tỉnh thành (tỷ lệ ảo giác 58.0%, vi phạm không gian 65.0%).
- **Naive RAG (Vector Only):** Mặc dù truy xuất được các đoạn review thực tế từ ChromaDB, tuy nhiên cơ chế Cosine Similarity thuần túy chỉ so khớp ngữ nghĩa chữ viết mà **hoàn toàn mù về tọa độ không gian (Space-agnostic)**. Hệ quả là khi du khách hỏi quán ăn *'gần Đại Nội'*, Naive RAG vẫn có thể gợi ý một quán bún bò rất nổi tiếng nhưng nằm tận bờ Nam hoặc cách xa hàng cây số (vi phạm không gian 41.0%).
- **Spatial GraphRAG (Phương pháp đề xuất):** Nhờ cơ chế lọc không gian 2 giai đoạn (cạnh `NEAR_BY` $d \le 1.5$km kết hợp định tuyến đường bộ OSRM) và quan hệ món ăn `SERVES` bóc tách từ 44.355 bài review, hệ thống bảo đảm 100% các địa điểm gợi ý là có thật và nằm trong bán kính cho phép, loại bỏ hoàn toàn hiện tượng đi vòng vô lý.

### 2.2. Khả năng tích hợp sản phẩm và tính ứng dụng thực tế
- Kết quả từ bộ thí nghiệm 100 trường hợp kiểm thử chứng minh Spatial GraphRAG đạt độ hoàn thiện cao, vừa phục vụ trực quan trên Giao diện Web tương tác bản đồ, vừa sẵn sàng triển khai thành cổng API chuẩn RESTful cho ứng dụng công dân số di động như Hue-S.
