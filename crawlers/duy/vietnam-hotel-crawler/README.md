--------------------------------------------------------
 HƯỚNG DẪN CHẠY CRAWL REVIEW
 (CHỦ FILE: 200 hotel đầu | 4 người: chia phần còn lại)
--------------------------------------------------------

PHÂN CÔNG (tổng 2.425 hotel):
    
    WORKER_ID = 0  -> CHỦ FILE, crawl 200 hotel ĐẦU
    
    WORKER_ID = 1  -> Người 1  (~557 hotel)
    
    WORKER_ID = 2  -> Người 2  (~556 hotel)
    
    WORKER_ID = 3  -> Người 3  (~556 hotel)
    
    WORKER_ID = 4  -> Người 4  (~556 hotel)
    
Mỗi máy ghi ra file riêng, cuối cùng gộp lại thành 1 file.

--------------------------------------------------------
BƯỚC 1 — CÀI ĐẶT (chỉ làm 1 lần)
--------------------------------------------------------
1. Cài Google Chrome (bản mới).
2. Cài Python 3 (tick "Add Python to PATH" khi cài).
3. Mở CMD/PowerShell, gõ:
       pip install undetected-chromedriver selenium beautifulsoup4 langdetect

--------------------------------------------------------
BƯỚC 2 — CHÉP FILE
--------------------------------------------------------
Chép NGUYÊN thư mục này sang máy của bạn. Bắt buộc có:

    - crawl_vietnam_hotels_reviews.py
    
    - crawl_vietnam_hotels_reviews_vi.py
    
    - vietnam_hotels_link.json

--------------------------------------------------------
BƯỚC 3 — ĐỔI SỐ RỒI CHẠY
--------------------------------------------------------
Mở  crawl_vietnam_reviews.py  bằng Notepad. Tìm gần đầu file dòng:

       WORKER_ID = 0

Sửa theo phân công (xem bảng trên): 0, 1, 2, 3 hoặc 4.

4 người phải để 4 số KHÁC NHAU (1,2,3,4). CHỦ FILE để 0.

(KHÔNG đổi LEAD_COUNT và NUM_WORKERS — mọi người để y nguyên.)

Lưu file.

Mở CMD/PowerShell ngay trong thư mục này rồi chạy:
       python crawl_vietnam_reviews.py

Nếu đúng, dòng đầu sẽ hiện, ví dụ:
       ### NGƯỜI 2/4 -> phụ trách 556 khách sạn (ghi ra vietnam_reviews_w2.json) ###
       (CHỦ FILE sẽ thấy: CHỦ FILE (200 hotel đầu) -> ... vietnam_reviews_w0.json)

Cứ để nó chạy. Kết quả tự lưu vào  vietnam_reviews_wX.json  (X là số của từng người).

--------------------------------------------------------
BƯỚC 4 — GỬI LẠI KẾT QUẢ
--------------------------------------------------------
Chạy xong, gửi lại file:
       vietnam_reviews_wX.json     (X = WORKER_ID)

--------------------------------------------------------
 CÂU HỎI
--------------------------------------------------------
* Lỡ tắt máy / đứt mạng giữa chừng?
    -> Cứ chạy lại  python crawl_vietnam_reviews.py.
       Nó TỰ TIẾP TỤC đúng chỗ (kể cả giữa một khách sạn nhiều review).
       Dữ liệu được ghi an toàn (atomic + bản .bak) nên KHÔNG bị mất.

* Thấy in "0 review" ở vài khách sạn?
    -> Bình thường. Khách sạn không có đánh giá sẽ tự bỏ qua.

* Lỗi "session not created ... version"?
    -> Chrome khác phiên bản. Mở file, tìm  CHROME_MAIN_VERSION = None
       đổi thành số Chrome, ví dụ  CHROME_MAIN_VERSION = 150
       (Xem số Chrome ở: chrome://settings/help)

* Bị chặn (hiện trang lạ / Pardon Our Interruption)?
    -> Script tự nghỉ rồi thử lại. Nếu kẹt lâu, tắt đi, vài chục phút
       sau chạy lại (vẫn tiếp tục đúng chỗ).
