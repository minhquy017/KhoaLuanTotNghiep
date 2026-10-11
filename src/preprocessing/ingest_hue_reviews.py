# -*- coding: utf-8 -*-
"""
INGESTION PIPELINE: NẠP REVIEW BỔ SUNG CỦA HUẾ VÀO SQLITE & KHAI PHÁ MÓN ĂN
Khóa luận: Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh
-----------------------------------------------------------------------------------------------------
1. Đọc data/raw/hue_reviews_supplement.json
2. Lọc trùng lặp với các review đã có trong SQLite
3. Nạp vào bảng `reviews` trong data/processed/tourism_vietnam.db
4. Tự động kích hoạt extract_dishes.py để bóc tách món ăn cho toàn bộ nhà hàng tại Huế!
"""

import os
import sys
import json
import sqlite3
import subprocess

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

INPUT_FILE = os.path.join(PROJECT_ROOT, "data", "raw", "hue_reviews_supplement.json")
DB_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "tourism_vietnam.db")
EXTRACT_SCRIPT = os.path.join(PROJECT_ROOT, "src", "mining", "extract_dishes.py")


def ingest_hue_reviews():
    print("=" * 75)
    print("NẠP BỔ SUNG REVIEW THỪA THIÊN HUẾ VÀO HỆ THỐNG")
    print("=" * 75)

    if not os.path.exists(INPUT_FILE):
        print(f"[LỖI] Chưa tìm thấy file dữ liệu: {INPUT_FILE}")
        print("Vui lòng chạy crawler trước: python crawlers/crawl_hue_reviews_specialized.py")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        reviews = json.load(f)

    print(f"-> Đọc được {len(reviews):,} review từ {os.path.basename(INPUT_FILE)}")
    if not reviews:
        print("[THÔNG BÁO] File rỗng, chưa có dữ liệu mới.")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Lấy các review đã tồn tại để tránh nạp trùng
    print("-> Đang kiểm tra các review đã có trong CSDL...")
    c.execute("SELECT place_url, title, comment FROM reviews WHERE place_url IN (SELECT url FROM places WHERE is_hue = 1)")
    existing = set()
    for row in c.fetchall():
        existing.add((row[0], (row[1] or "").strip(), (row[2] or "").strip()[:50]))

    new_rows = []
    for r in reviews:
        purl = r.get("place_url", "")
        title = (r.get("title") or "").strip()
        comment = (r.get("comment") or "").strip()
        key = (purl, title, comment[:50])

        if key in existing:
            continue
        existing.add(key)

        new_rows.append((
            purl,
            r.get("reviewer_url", ""),
            title,
            comment,
            r.get("reviews_rating", 4.0),
            r.get("trip_type", ""),
            r.get("visit_date", ""),
            r.get("language", "English")
        ))

    print(f"-> Số lượng review mới cần nạp: {len(new_rows):,}")
    if new_rows:
        c.executemany("""
            INSERT INTO reviews (
                place_url, reviewer_url, title, comment, reviews_rating,
                trip_type, visit_date, language
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, new_rows)
        conn.commit()
        print(f"✅ Đã chèn thành công {len(new_rows):,} bài review vào CSDL SQLite!")

    # Thống kê lại
    c.execute("""
        SELECT p.category, COUNT(r.review_id)
        FROM places p 
        LEFT JOIN reviews r ON p.url = r.place_url 
        WHERE p.is_hue = 1 
        GROUP BY p.category
    """)
    print("\nThống kê review Thừa Thiên Huế sau khi nạp:")
    for row in c.fetchall():
        print(f"  • {row[0]:<12}: {row[1]:>8,} reviews")

    conn.close()

    # Kích hoạt chạy lại khai phá món ăn
    print("\n" + "=" * 75)
    print("BƯỚC KẾ TIẾP: CẬP NHẬT THỰC ĐƠN NGẦM HUẾ (EXTRACT DISHES)")
    print("=" * 75)
    ans = input("Bạn có muốn chạy lại extract_dishes.py ngay bây giờ không? (y/n): ").strip().lower()
    if ans == 'y':
        subprocess.run([sys.executable, "-X", "utf8", EXTRACT_SCRIPT])


if __name__ == "__main__":
    ingest_hue_reviews()
