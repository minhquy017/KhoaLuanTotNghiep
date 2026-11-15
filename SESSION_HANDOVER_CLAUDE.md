# BIÊN BẢN GHI NHỚ TIẾN ĐỘ PHIÊN LÀM VIỆC (SESSION CHECKPOINT & HANDOVER)
**Dự án:** Khóa luận Tốt nghiệp - Hệ thống Trợ lý Du lịch Thông minh Cố đô Huế (Spatial GraphRAG + Qwen2.5-VL:7B)  
**Thời điểm ghi nhận:** Ngày 15/11/2026  
**Lý do tạm dừng:** Model `Claude Opus 4.6 (Thinking)` hết hạn ngạch quota (0% remaining, dự kiến reset vào `2026-11-20T13:34:51Z`).  
**Mục tiêu phiên:** Rà soát chuyên sâu (audit) toàn bộ 18 file mã nguồn LaTeX (`thesis-latex/`), phát hiện và xử lý dứt điểm các lỗi định dạng, lỗi công thức, mâu thuẫn số liệu, và nâng cấp văn phong học thuật chuẩn mực theo 16 nguyên tắc bài trừ văn phong AI (`@academic-writing-ds-ai`) và Quy chuẩn Khoa KT&CN - Đại học Huế (`@huet-thesis-compliance`).

---

## 1. TÌNH TRẠNG HIỆN TẠI VÀ CÔNG VIỆC ĐÃ HOÀN THÀNH

### A. Đã đọc và thẩm định toàn bộ các file:
- [x] `thesis-latex/main.tex` & `thong-tin.tex`: Cấu trúc tổng thể, metadata đồ án.
- [x] Khối bìa và thủ tục:
  - `bia/bia-ngoai.tex`: Khung viền Mẫu 1, logo, thông tin sinh viên, tên đề tài.
  - `bia/bia-phu.tex`: Khung viền Mẫu 2, người hướng dẫn, thông tin đề tài.
  - `bia/loi-cam-doan.tex`, `bia/loi-cam-on.tex`, `bia/tom-tat.tex` (Tóm tắt tiếng Việt & Abstract tiếng Anh).
  - `bia/ky-hieu.tex` (Danh mục từ viết tắt), `bia/danh-muc-bang.tex`, `bia/danh-muc-hinh.tex`, `bia/muc-luc.tex`.
- [x] Khối nội dung chính:
  - `noi-dung/phan-1-mo-dau/mo-dau.tex`: 6 mục tiêu, 6 câu hỏi nghiên cứu (RQ1-RQ6), 6 giả thuyết (H1-H6). Viết rất chắc chắn.
  - `noi-dung/phan-2-tong-quan/tong-quan.tex`: Cơ sở lý thuyết Haversine, GraphRAG, Agentic RAG, Qwen2.5-VL:7B, CLIP, OSRM, Firebase Firestore, OAuth 2.0, các khoảng trống nghiên cứu.
  - `noi-dung/phan-3-phuong-phap/phuong-phap.tex`: Thu thập dữ liệu (44.355 review, 9.525 nút thực thể, 3.528 ảnh), phân cụm không gian, trắc địa di sản.
  - `noi-dung/phan-4-thuc-nghiem/chuong-1-kien-truc.tex`: Kiến trúc 4 tầng, thuật toán ghim session, công thức (1.4), dark mode, i18n, biểu giá vé tham quan.
  - `noi-dung/phan-4-thuc-nghiem/chuong-2-ket-qua.tex`: Bảng 11 (12 kịch bản đại diện), đánh giá Benchmark 100 câu, độ trễ và tỷ lệ hallucination.
  - `noi-dung/phan-5-ket-luan/ket-luan.tex`: 6 đóng góp, 3 hạn chế thực tế, 5 hướng phát triển.
  - `noi-dung/phu-luc/phu-luc.tex`: Phụ lục A (100 kịch bản benchmark chia 3 nhóm chuẩn xác: TC-01..TC-40 ẩm thực, TC-41..TC-75 lân cận, TC-76..TC-100 lịch trình), Phụ lục B (thực đơn 10 món đặc sản).

### B. Các lỗi đã được xử lý ở các phiên trước (CẦN GIỮ NGUYÊN, KHÔNG HOÀN TÁC):
1. **Công thức (1.4) tại `chuong-1-kien-truc.tex` (Dòng 311-317):**
   - Đã sửa thành `Timestamp_{\text{updated}}(S_i)` (không còn gõ thiếu chữ `t` thành `updaed`).
   - Đã bổ sung đầy đủ điều kiện `$S_i.\text{isPinned} = \text{true}$` và `$S_i.\text{isPinned} = \text{false}$`.
2. **Khớp mã kịch bản giữa Bảng 11 và Phụ lục A:**
   - Mã 12 kịch bản đại diện tại Bảng 11 và diễn giải trang kết quả đã khớp mã thực trong Phụ lục A (TC-01, TC-03, TC-04, TC-06, TC-42, TC-43, TC-44, TC-57, TC-76, TC-77, TC-78, TC-79).
3. **Mâu thuẫn số liệu cấu trúc đồ thị:**
   - Khẳng định chuẩn: **9.525 nút thực thể** = 8.921 điểm dịch vụ (2.036 Attraction + 4.462 Restaurant + 2.423 Hotel) + 570 món ăn (Dish) + 34 khu vực (Locality).
4. **Nhãn mô hình tại Hình 9:**
   - Đã đồng nhất sử dụng nhãn mô hình đa phương thức `Qwen2.5-VL:7B Local`.

---

## 2. DANH SÁCH CÁC ĐIỂM CẦN XỬ LÝ TIẾP (KHI CLAUDE HOẶC AGENT MỚI TIẾP QUẢN)

### Việc 1: Tinh chỉnh cỡ chữ Trang bìa theo Văn bản 1967/HD-ĐHH mà KHÔNG làm tràn trang 2 (Ưu tiên cao nhất)
- **Hiện trạng:**
  - `bia-ngoai.tex`: Dòng 30-32 (Trường, Khoa, Bộ môn) đang dùng `\fontsize{13pt}{16pt}` (chuẩn quy định là 14pt). Dòng 44 (Tên đề tài) dùng `18pt` (chuẩn quy định là 24pt). Dòng 49, 51 dùng `16pt` (chuẩn là 24pt).
  - `bia-phu.tex`: Dòng 18-20 dùng `13pt` (chuẩn 14pt), dòng 32 dùng `18pt` (chuẩn 22pt), dòng 37, 39 dùng `15pt` (chuẩn 20pt).
- **Lý do trước đây để size nhỏ:** Tránh bị tràn chữ (VÀ TRÍ TUỆ NHÂN TẠO / THÀNH PHỐ HUẾ, NĂM 2026) sang trang thứ 2.
- **Giải pháp xử lý:**
  - Nâng cỡ chữ theo sát chuẩn nhất có thể.
  - Đồng thời giảm khoảng cách `\vspace*{-0.9cm}`, giảm kích thước logo từ `3.6cm` xuống `3.0cm` - `3.2cm`, giảm `\vspace*{0.3cm}` giữa các khối để bảo đảm tuyệt đối gói gọn trong 1 trang duy nhất, không tạo trang trắng số 2.
  - Biên dịch và kiểm tra trang 1 và trang 2 trên PDF ngay sau khi sửa.

### Việc 2: Tinh lọc văn phong học thuật tại `noi-dung/phan-2-tong-quan/tong-quan.tex`
- **Thay thế các từ ngữ sáo rỗng / tuyệt đối hóa (AI Patterns):**
  - "triệt để", "tuyệt đối", "cốt tử", "vượt trội", "nhược điểm chí tử".
  - *Ví dụ:* "ưu thế cốt tử" $\to$ "lợi thế trọng yếu"; "triệt tiêu 100% chi phí" $\to$ "loại bỏ chi phí gọi API thương mại"; "Nhược điểm chí tử" $\to$ "Hạn chế căn bản".
- **Bổ sung trích dẫn còn thiếu (Missing Citations):**
  - Dòng 51: Thiếu `\cite{}` cho DuckDuckGo fallback / Web Search RAG.
  - Dòng 189, 191: Thêm trích dẫn cho kiến trúc NoSQL Document Store và Real-time Listeners (đã có `google2024firestore`, cần chèn cụ thể).
- **Sửa xung đột ký hiệu toán học ở dòng 178:**
  - Phương trình hiện tại: `w(u, w) = w(u, v) + w(v, w)` $\to$ Chữ `$w$` vừa là tên hàm trọng số vừa là tên đỉnh. Sửa thành: `w(u, z) = w(u, v) + w(v, z)` để chuẩn mực toán học.
- **Tinh giản công thức `IsOwner` (Dòng 201-206):**
  - Công thức Firestore Security Rules viết dưới dạng logic toán vị từ chuẩn thay vì code if-else thô sơ.

### Việc 3: Rà soát triệt tiêu `\textbf{}` trong thân đoạn văn (Rule 1.11 - `@academic-writing-ds-ai`)
- Trong văn bản học thuật quốc tế và quy chuẩn, không dùng chữ in đậm `\textbf{}` ở giữa đoạn văn xuôi để nhấn mạnh từ ngữ. Chữ đậm chỉ dùng cho tiêu đề mục và tiêu đề bảng/hình.
- File cần kiểm tra: `ket-luan.tex` dòng 9 (`\textbf{\tendetai}`), `mo-dau.tex`, `tong-quan.tex`, `chuong-1-kien-truc.tex`. Chuyển về văn phong diễn đạt tự nhiên hoặc dùng ngoặc kép / thuật ngữ in nghiêng nếu là thuật ngữ kỹ thuật tiếng Anh.

### Việc 4: Biên dịch kiểm thử toàn bộ (Full Compilation & Zero Warning)
- Chạy lệnh biên dịch LaTeX (trên Windows MiKTeX yêu cầu `BypassSandbox: true`):
  ```powershell
  cd "d:\Khóa luận\thesis-latex"
  pdflatex -interaction=nonstopmode main.tex
  pdflatex -interaction=nonstopmode main.tex
  ```
- Kiểm tra file log xem còn lỗi `Overfull \hbox` nào vượt quá 10pt không (đặc biệt các dòng chứa tên mô hình dài hoặc URL).
- Kiểm tra danh mục bảng, danh mục hình xem số thứ tự có bị nhảy (Bảng 1, Bảng 2...) không.

---

## 3. CÂU LỆNH NHANH ĐỂ GỌI LẠI CLAUDE KHI RESET TOKEN

Khi quota của Claude Opus 4.6 đã được làm mới, bạn chỉ cần gửi câu lệnh sau vào khung chat:

```markdown
Chào bạn, quota Claude đã được mở lại. Bạn hãy đọc file `d:\Khóa luận\SESSION_HANDOVER_CLAUDE.md` để nắm chính xác trạng thái bàn giao và tiếp tục thực hiện:
1. Sửa cỡ chữ trang bìa ngoài & bìa phụ theo Mẫu 1 và Mẫu 2 của ĐH Huế mà vẫn giữ đúng 1 trang không bị tràn.
2. Tinh chỉnh từ ngữ sáo rỗng và ký hiệu toán học trong `tong-quan.tex`.
3. Kiểm tra các lỗi `\textbf{}` trong thân văn bản và biên dịch lại PDF hoàn chỉnh.
```

---
*Biên bản này được lập tự động để lưu trữ trạng thái ngữ cảnh vĩnh viễn trong workspace.*

