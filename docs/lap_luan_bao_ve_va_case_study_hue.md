# TÀI LIỆU LẬP LUẬN BẢO VỆ & CHIẾN LƯỢC CASE STUDY THỪA THIÊN HUẾ
**Khóa luận Tốt nghiệp ngành Khoa học Dữ liệu & Trí tuệ Nhân tạo (DS&AI K3 - Trường Kỹ thuật và Công nghệ - Đại học Huế - HUET)**  
**Đề tài:** *Hệ thống hỏi đáp và gợi ý lịch trình du lịch thông minh dựa trên Đồ thị Tri thức Không gian và LLM*

---

## MỤC LỤC
1. [Chiến lược Tên đề tài & Phạm vi Nghiên cứu](#1-chiến-lược-tên-đề-tài--phạm-vi-nghiên-cứu)
2. [Chiến lược Dữ liệu 2 Tầng (Two-Tier Data Strategy)](#2-chiến-lược-dữ-liệu-2-tầng-two-tier-data-strategy)
3. [Bộ 3 Luận điểm Đanh thép: "Tại sao có ChatGPT/Gemini mà vẫn làm?"](#3-bộ-3-luận-điểm-đanh-thép-tại-sao-có-chatgptgemini-mà-vẫn-làm)
4. [Diễn giải Học thuật cho 3 Biểu đồ Thực nghiệm Huế](#4-diễn-giải-học-thuật-cho-3-biểu-đồ-thực-nghiệm-huế)
5. [Kịch bản Trình bày & Mạch Lập luận Hình Phễu (Funnel Approach)](#5-kịch-bản-trình-bày--mạch-lập-luận-hình-phễu-funnel-approach)

---

## 1. CHIẾN LƯỢC TÊN ĐỀ TÀI & PHẠM VI NGHIÊN CỨU

### 1.1. Giữ nguyên Tên đề tài Tổng quát
- **Tên đề tài chính thức:** *"Hệ thống hỏi đáp và gợi ý lịch trình du lịch thông minh dựa trên Đồ thị Tri thức Không gian và LLM"*
- **Lý do học thuật:** Đề tài đóng góp về mặt **Kiến trúc & Giải pháp công nghệ (Framework / Architecture)** gồm Spatial KG + Vector RAG + Open-source LLM. Khung giải pháp này mang tính tổng quát, có thể triển khai cho bất kỳ tỉnh thành hay quốc gia nào.
- **Lý do hành chính:** Không cần làm đơn xin đổi tên đề tài với Khoa và Nhà trường.

### 1.2. Định vị Thừa Thiên Huế trong cuốn Luận văn
- **Chương 1 (Phạm vi nghiên cứu):** Đề tài xây dựng giải pháp tổng quát, đồng thời chọn **Thừa Thiên Huế làm Địa bàn nghiên cứu trọng điểm (Focal Case Study)** nhằm kiểm chứng thực nghiệm chuyên sâu trên dữ liệu thực tế dày đặc.
- **Chương 4 (Thực nghiệm):** Đặt riêng một tiểu mục lớn: *4.X. Thực nghiệm chuyên sâu trên địa bàn Thừa Thiên Huế (Focal Case Study)*.

---

## 2. CHIẾN LƯỢC DỮ LIỆU 2 TẦNG (TWO-TIER DATA STRATEGY)

Khi bảo vệ, **tuyệt đối không nói:** *"Em cào 1,4 triệu cái nhưng nhiều quá nên bỏ bớt, chỉ lấy 30k của Huế"*.  
**Thay vào đó, trình bày theo mô hình 2 tầng chuẩn Data Science:**

```
                  ┌──────────────────────────────────────────────┐
                  │          TẦNG VĨ MÔ (MACRO SCALE)            │
                  │   8.921 Địa điểm • 1.691.507 Reviews         │
                  │   >1.000.000 Vector Embeddings trong ChromaDB│
                  │   => Chứng minh khả năng Mở rộng (Scalable)  │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │         TẦNG VI MÔ (FOCAL CASE STUDY)        │
                  │       612 Địa điểm Huế • 28.757 Reviews       │
                  │    => Kiểm chứng thực địa (Ground Truth)     │
                  │    => Đánh giá chất lượng RAG & Không gian    │
                  └──────────────────────────────────────────────┘
```

1. **Tầng Vĩ mô (Big Data Engineering):**
   - Lưu trữ và quản lý tập dữ liệu du lịch quy mô lớn toàn quốc với 8.921 địa điểm và 1,69 triệu đánh giá.
   - Nhúng thành công hơn 1.000.000 vector ngữ nghĩa vào ChromaDB.
   - Khai phá xu hướng biến động chuỗi thời gian 2015 – 2026 (Phục hồi mạnh mẽ sau đại dịch).
   - **Mục tiêu:** Chứng minh hệ sinh thái dữ liệu có khả năng mở rộng (scalability) và chịu tải ở quy mô Big Data.

2. **Tầng Vi mô (Focal Case Study Thừa Thiên Huế):**
   - Khoanh vùng 612 địa điểm và 28.757 đánh giá được cào vét cạn không giới hạn quota.
   - **Mục tiêu:** 
     - Mật độ dữ liệu cực cao (~50 review/địa điểm), đảm bảo đồ thị tri thức không gian hoạt động chính xác.
     - **Kiểm chứng thực địa (Ground Truth Verification):** Hội đồng và nhóm nghiên cứu nắm rõ địa bàn Huế, dễ dàng kiểm chứng xem chatbot có trả lời chính xác từng ngõ ngách, tên món, địa chỉ hay có bịa đặt (hallucinate) hay không.

---

## 3. BỘ 3 LUẬN ĐIỂM ĐANH THÉP: "TẠI SAO CÓ CHATGPT/GEMINI MÀ VẪN LÀM?"

Hội đồng chắc chắn sẽ hỏi: *"Hiện nay ChatGPT, Gemini đã rất thông minh rồi, người dùng chỉ cần mở app lên hỏi là xong, tại sao em phải xây dựng hệ thống này?"*

Trả lời bằng **3 luận điểm then chốt**:

### 🎯 Luận điểm 1: Chuyên biệt hóa địa phương & Triệt tiêu Hallucination
- **ChatGPT / Gemini:** Là mô hình tổng quát toàn cầu, dữ liệu du lịch Việt Nam bị mỏng và lỗi thời. Khi hỏi chi tiết (ví dụ: *"quán bún bò Huế chuẩn vị gần Đại Nội mở sau 21h"*), GPT rất dễ **bịa đặt địa chỉ, số nhà, hoặc gợi ý các quán đã đóng cửa từ lâu (Hallucination)**.
- **Hệ thống đề tài:** Vận hành trên **Spatial Knowledge Graph** với 612 địa điểm và gần 29.000 đánh giá thực tế cập nhật đến 2026. Mọi câu trả lời của LLM đều bị ràng buộc (grounded) bởi tri thức thực tế được trích xuất từ đồ thị và vector database, cam kết không bịa đặt thông tin.

### 🎯 Luận điểm 2: Bài toán Chi phí (Zero API Cost) cho Doanh nghiệp & Địa phương
- **ChatGPT / Gemini API:** Chi phí gọi API thương mại rất đắt (khoảng $0.03 – $0.06 / truy vấn phức tạp kèm context). Nếu một ứng dụng du lịch địa phương phục vụ 1.000 lượt khách/ngày, chi phí API sẽ tốn hàng chục đến hàng trăm triệu đồng mỗi tháng – một gánh nặng tài chính không khả thi cho các doanh nghiệp vừa và nhỏ hoặc cơ quan quản lý nhà nước.
- **Hệ thống đề tài:** Ứng dụng mô hình mã nguồn mở kết hợp RAG nội bộ (Self-hosted / On-premise). Chi phí bản quyền API = **0 VNĐ**.

### 🎯 Luận điểm 3: Khả năng Tích hợp Hệ sinh thái Số Địa phương (Hue-S) & Chủ quyền Dữ liệu
- Hệ thống được thiết kế dạng module API mở, sẵn sàng tích hợp trực tiếp làm trợ lý ảo du lịch thông minh cho ứng dụng đô thị thông minh **Hue-S** hoặc cổng thông tin du lịch Thừa Thiên Huế.
- Dữ liệu hoàn toàn được quản trị tại chỗ, không gửi thông tin người dùng ra máy chủ nước ngoài, đảm bảo tuyệt đối tính riêng tư và chủ quyền số địa phương.

---

## 4. DIỄN GIẢI HỌC THUẬT CHO 3 BIỂU ĐỒ THỰC NGHIỆM HUẾ

### 4.1. Hình 1: Cơ cấu Loại hình Cơ sở Du lịch (`hue_places_category_donut.png`)
* **Số liệu:** 612 địa điểm: Ẩm thực 78.3% (479 quán), Lưu trú 17.0% (104 khách sạn), Di tích/Danh thắng 4.7% (29 điểm).
* **Diễn giải học thuật:** Phản ánh đúng đặc thù cố đô Huế – di tích lịch sử tập trung ở quy mô lớn, bao quanh bởi mạng lưới ẩm thực truyền thống dày đặc.
* **Ý nghĩa với hệ thống:** Đồ thị Tri thức Không gian cần tận dụng các quan hệ không gian (`NEARBY`, `LOCATED_IN`) để tự động kết nối các điểm tham quan với các cụm ẩm thực lân cận nhằm sinh lịch trình "Food Tour" tối ưu khoảng cách di chuyển.

### 4.2. Hình 2: Phân bố Điểm số Đánh giá (`hue_ratings_distribution.png`)
* **Số liệu:** 28.757 review: Điểm trung bình 4.68/5.0; Tỷ lệ 4-5 sao chiếm **93.8%** (5 sao: 77.5%, 4 sao: 16.3%).
* **Diễn giải học thuật:** Hiện tượng "Độ lệch tích cực" (*Positive Skewness / J-shaped distribution*) trong phản hồi du lịch trực tuyến.
* **Ý nghĩa với hệ thống (RẤT QUAN TRỌNG):** Nếu chỉ dùng bộ lọc số sao thông thường (ví dụ: lọc quán rating $\ge$ 4.5), hệ thống sẽ bị bão hòa vì hầu hết quán đều điểm cao. Điều này **chứng minh vai trò sống còn của RAG + LLM**: hệ thống bắt buộc phải đọc hiểu ngữ nghĩa bài viết (Aspect-based Sentiment) để bóc tách xem quán được khen về món gì (nước dùng, không gian, hay giá cả) và bị chê ở điểm nào (phục vụ chậm, chỗ để xe hẹp) để tư vấn chính xác.

### 4.3. Hình 3: Cơ cấu Phân khúc Du khách - Trip Types (`hue_trip_types_breakdown.png`)
* **Số liệu:** 26.317 lượt gắn nhãn: Cặp đôi 48.8% (12.847), Bạn bè 19.8% (5.200), Gia đình 15.7% (4.133), Đơn hành 14.4% (3.789), Công tác chỉ 1.3% (348).
* **Diễn giải học thuật:** Huế là điểm đến du lịch lãng mạn, trải nghiệm, văn hóa, không phải trung tâm tài chính/hội nghị lớn. Cặp đôi và bạn bè chiếm xấp xỉ 70%.
* **Ý nghĩa với hệ thống:** Căn cứ thực nghiệm thực tế để thiết kế các **User Personas** trong Prompt Engineering của LLM:
  - *Persona Cặp đôi:* Ưu tiên không gian lãng mạn, view sông Hương, cà phê yên tĩnh, ẩm thực cung đình.
  - *Persona Bạn bè:* Ưu tiên ẩm thực đường phố, check-in sôi động, hoạt động trải nghiệm đêm.
  - *Persona Gia đình:* Ưu tiên quán ăn không gian rộng, món ăn hợp khẩu vị trẻ em và người lớn tuổi.

---

## 5. KỊCH BẢN TRÌNH BÀY & MẠCH LẬP LUẬN HÌNH PHỄU (FUNNEL APPROACH)

Khi thuyết trình trước Hội đồng, chia làm **2 nửa mạch lạc**:

1. **Nửa đầu: Tổng thể Khung Công nghệ (Framework Overview)**
   - Trình bày bài toán du lịch thông minh và tập dữ liệu lớn toàn quốc (8.9k địa điểm, 1.69M reviews, đồ thị phục hồi sau Covid 2015–2026).
   - Trình bày các kỹ thuật nền tảng: Mô hình hóa Đồ thị Không gian (Spatial KG), Kỹ thuật Chunking & Embedding hơn 1 triệu vector vào ChromaDB, Thuật toán lai Hybrid GraphRAG.
   - *(Nói 1 lần duy nhất trên quy mô tổng thể để tránh trùng lặp).*

2. **Nửa sau: Thực nghiệm Chuyên sâu & Đánh giá (Hue Case Study Verification)**
   - Giải thích vì sao chọn Huế làm Case Study (Độ dày dữ liệu 612 địa điểm, 28k review, khả năng kiểm chứng thực địa Ground Truth, ứng dụng cho địa phương/Hue-S).
   - Trình bày 3 biểu đồ thực nghiệm của Huế để rút ra các kết luận thiết kế hệ thống (J-shaped rating đòi hỏi RAG, Trip types định hình Personas).
   - Đo đạc định lượng: Thời gian phản hồi (Latency), độ chính xác thông tin (Precision/Faithfulness), tỷ lệ triệt tiêu hallucination.
   - Demo kịch bản thực tế tại Huế để thuyết phục Hội đồng.

---
*Tài liệu này được lưu trữ tại `docs/lap_luan_bao_ve_va_case_study_hue.md` để tác giả tra cứu và chèn trực tiếp vào cuốn luận văn và slide bảo vệ.*
