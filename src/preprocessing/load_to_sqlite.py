# -*- coding: utf-8 -*-
"""
ETL PIPELINE: NẠP DỮ LIỆU ĐỊA ĐIỂM, ĐÁNH GIÁ VÀ BỘ TỪ ĐIỂN ẨM THỰC VÀO SQLITE
- Metadata: 8,363 địa điểm (vietnam_places_metadata.json)
- Reviews: 13 files JSON (~1.4 triệu bài đánh giá đã khớp URL)
- Từ điển ẩm thực: 570 món ăn chuẩn hóa (culinary_gazetteer.json)
- Cơ sở dữ liệu đích: data/processed/tourism_vietnam.db
Tối ưu hóa hiệu năng: WAL mode, Batch Insertion (10,000 rows/batch), Indexing sau nạp.
"""

import os
import sys
import glob
import json
import sqlite3
import time
from collections import Counter

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def normalize_url(url):
    """Chuẩn hóa URL: cắt query parameters và hash fragments"""
    if not url:
        return ""
    return url.split("?")[0].split("#")[0].strip()

def is_hue_place(p, norm_url):
    """Nhận diện địa điểm thuộc địa bàn Thừa Thiên Huế (geoId g293926 hoặc locality Hue)"""
    loc = (p.get("locality") or "").strip()
    return 1 if ("-g293926-" in norm_url or loc == "Hue" or "thua thien" in loc.lower()) else 0

def init_schema(conn):
    """Tạo cấu trúc bảng cho cơ sở dữ liệu quan hệ du lịch"""
    cursor = conn.cursor()
    
    # Bảng 1: Địa điểm du lịch (Places)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS places (
        place_id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        category TEXT,
        latitude REAL,
        longitude REAL,
        street_address TEXT,
        district TEXT,
        locality TEXT,
        postal_code TEXT,
        country TEXT,
        cuisines TEXT,
        price_range TEXT,
        rating_value REAL,
        review_count INTEGER,
        telephone TEXT,
        image_url TEXT,
        raw_type TEXT,
        is_hue INTEGER DEFAULT 0
    );
    """)

    # Bảng 2: Bài đánh giá của du khách (Reviews)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        review_id INTEGER PRIMARY KEY AUTOINCREMENT,
        place_url TEXT NOT NULL,
        reviewer_url TEXT,
        title TEXT,
        comment TEXT,
        reviews_rating REAL,
        trip_type TEXT,
        visit_date TEXT,
        language TEXT
    );
    """)

    # Bảng 3: Danh mục món ăn đặc sản toàn quốc (Dishes)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dishes (
        dish_id TEXT PRIMARY KEY,
        canonical_name TEXT NOT NULL,
        category TEXT,
        region_origin TEXT,
        aliases TEXT,
        alias_count INTEGER
    );
    """)

    # Bảng 4: Thực đơn ngầm khai phá từ đánh giá (Restaurant Dishes)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS restaurant_dishes (
        place_url TEXT NOT NULL,
        dish_id TEXT NOT NULL,
        mention_count INTEGER DEFAULT 0,
        avg_rating REAL,
        sentiment_score REAL,
        PRIMARY KEY (place_url, dish_id)
    );
    """)
    conn.commit()

def create_indexes(conn):
    """Tạo chỉ mục tối ưu hóa tốc độ truy vấn cho RAG và Planner"""
    cursor = conn.cursor()
    print("\n[Indexing] Đang tạo các chỉ mục tìm kiếm tối ưu...")
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_places_url ON places(url);",
        "CREATE INDEX IF NOT EXISTS idx_places_cat ON places(category);",
        "CREATE INDEX IF NOT EXISTS idx_places_locality ON places(locality);",
        "CREATE INDEX IF NOT EXISTS idx_places_is_hue ON places(is_hue);",
        "CREATE INDEX IF NOT EXISTS idx_reviews_place_url ON reviews(place_url);",
        "CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(reviews_rating);",
        "CREATE INDEX IF NOT EXISTS idx_reviews_lang ON reviews(language);",
        "CREATE INDEX IF NOT EXISTS idx_dishes_category ON dishes(category);",
        "CREATE INDEX IF NOT EXISTS idx_dishes_region ON dishes(region_origin);",
        "CREATE INDEX IF NOT EXISTS idx_rest_dishes_place ON restaurant_dishes(place_url);",
        "CREATE INDEX IF NOT EXISTS idx_rest_dishes_dish ON restaurant_dishes(dish_id);"
    ]
    for idx_sql in indexes:
        cursor.execute(idx_sql)
    conn.commit()
    print("-> Đã hoàn thành tạo 11 chỉ mục tìm kiếm.")

def run_etl():
    start_time = time.time()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, "..", ".."))
    
    metadata_path = os.path.join(project_root, "data", "raw", "vietnam_places_metadata.json")
    raw_dataset_dir = os.path.join(project_root, "data", "raw", "raw_dataset")
    gazetteer_path = os.path.join(project_root, "data", "processed", "culinary_gazetteer.json")
    db_path = os.path.join(project_root, "data", "processed", "tourism_vietnam.db")

    print("=" * 75)
    print("BƯỚC 1.2: ETL DỮ LIỆU TOÀN DIỆN VÀO CƠ SỞ DỮ LIỆU SQLITE")
    print(f"• Cơ sở dữ liệu: {db_path}")
    print("=" * 75)

    # Nếu DB đã tồn tại thì xóa để tạo mới sạch sẽ
    if os.path.exists(db_path):
        os.remove(db_path)
        print("-> Đã làm sạch cơ sở dữ liệu cũ.")

    conn = sqlite3.connect(db_path)
    # Tối ưu I/O cho SQLite
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA cache_size = 200000;")
    conn.execute("PRAGMA temp_store = MEMORY;")

    init_schema(conn)

    # ---------------------------------------------------------
    # 1. NẠP PLACES METADATA
    # ---------------------------------------------------------
    print("\n[1/3] Đang nạp Metadata địa điểm (vietnam_places_metadata.json)...")
    with open(metadata_path, "r", encoding="utf-8") as f:
        places_data = json.load(f)

    place_rows = []
    valid_urls = set()
    places_cat_count = Counter()
    hue_count = 0

    for p in places_data:
        raw_url = p.get("url", "")
        norm_url = normalize_url(raw_url)
        if not norm_url or norm_url in valid_urls:
            continue
        
        valid_urls.add(norm_url)
        cat = p.get("category", "")
        places_cat_count[cat] += 1
        is_hue = is_hue_place(p, norm_url)
        if is_hue:
            hue_count += 1

        cuisines_str = json.dumps(p.get("cuisines", []), ensure_ascii=False)
        
        row = (
            norm_url,
            p.get("name", "").strip(),
            cat,
            p.get("latitude"),
            p.get("longitude"),
            p.get("street_address", ""),
            p.get("district", ""),
            p.get("locality", ""),
            p.get("postal_code", ""),
            p.get("country", ""),
            cuisines_str,
            p.get("price_range", ""),
            p.get("rating_value"),
            p.get("review_count"),
            p.get("telephone", ""),
            p.get("image_url", ""),
            p.get("raw_type", ""),
            is_hue
        )
        place_rows.append(row)

    conn.executemany("""
    INSERT INTO places (
        url, name, category, latitude, longitude, street_address, district,
        locality, postal_code, country, cuisines, price_range, rating_value,
        review_count, telephone, image_url, raw_type, is_hue
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, place_rows)
    conn.commit()
    print(f"-> Đã nạp {len(place_rows):,} địa điểm thành công!")
    for cat, cnt in places_cat_count.items():
        print(f"   • {cat.capitalize():<15}: {cnt:>5,} địa điểm")
    print(f"   • Riêng Thừa Thiên Huế: {hue_count:>5,} địa điểm trọng tâm")

    # ---------------------------------------------------------
    # 2. NẠP CULINARY GAZETTEER
    # ---------------------------------------------------------
    print("\n[2/3] Đang nạp Từ điển ẩm thực Việt Nam (culinary_gazetteer.json)...")
    if os.path.exists(gazetteer_path):
        with open(gazetteer_path, "r", encoding="utf-8") as f:
            gazetteer_data = json.load(f)

        dish_rows = []
        for d in gazetteer_data:
            aliases_str = json.dumps(d.get("aliases", []), ensure_ascii=False)
            dish_rows.append((
                d["dish_id"],
                d["canonical_name"],
                d.get("category", ""),
                d.get("region_origin", ""),
                aliases_str,
                d.get("alias_count", 0)
            ))
        conn.executemany("""
        INSERT INTO dishes (dish_id, canonical_name, category, region_origin, aliases, alias_count)
        VALUES (?, ?, ?, ?, ?, ?);
        """, dish_rows)
        conn.commit()
        print(f"-> Đã nạp {len(dish_rows):,} món ăn chuẩn hóa vào bảng dishes.")
    else:
        print("-> [Cảnh báo] Chưa tìm thấy culinary_gazetteer.json!")

    # ---------------------------------------------------------
    # 3. NẠP REVIEWS TỪ 13 FILES JSON
    # ---------------------------------------------------------
    print("\n[3/3] Đang nạp 13 file reviews (~1.25 GB) vào bảng reviews...")
    review_files = sorted(glob.glob(os.path.join(raw_dataset_dir, "**/*.json"), recursive=True))
    
    total_reviews_inserted = 0
    total_reviews_skipped = 0
    batch_size = 20000
    batch_rows = []

    for idx, fpath in enumerate(review_files, 1):
        fname = os.path.basename(fpath)
        folder = os.path.basename(os.path.dirname(fpath))
        file_inserted = 0
        file_skipped = 0

        with open(fpath, "r", encoding="utf-8") as fp:
            data = json.load(fp)

        for rev in data:
            r_url = normalize_url(rev.get("url", ""))
            if not r_url or r_url not in valid_urls:
                file_skipped += 1
                continue

            comment = (rev.get("comment") or "").strip()
            title = (rev.get("title") or "").strip()
            # Bỏ qua review hoàn toàn trống nội dung
            if not comment and not title:
                file_skipped += 1
                continue

            row = (
                r_url,
                rev.get("reviewer_url", ""),
                title,
                comment,
                rev.get("reviews_rating"),
                rev.get("trip_type", ""),
                rev.get("visit_date", ""),
                rev.get("language", "English")
            )
            batch_rows.append(row)
            file_inserted += 1

            if len(batch_rows) >= batch_size:
                conn.executemany("""
                INSERT INTO reviews (
                    place_url, reviewer_url, title, comment, reviews_rating,
                    trip_type, visit_date, language
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """, batch_rows)
                conn.commit()
                batch_rows = []

        total_reviews_inserted += file_inserted
        total_reviews_skipped += file_skipped
        print(f"   [{idx:02d}/13] {folder}/{fname:<30}: nạp {file_inserted:>7,} reviews (bỏ qua {file_skipped:>6,})")

    # Nạp batch cuối cùng còn dư
    if batch_rows:
        conn.executemany("""
        INSERT INTO reviews (
            place_url, reviewer_url, title, comment, reviews_rating,
            trip_type, visit_date, language
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, batch_rows)
        conn.commit()
        batch_rows = []

    print(f"\n-> Tổng số review đã nạp thành công: {total_reviews_inserted:,}")
    print(f"-> Số review bị bỏ qua (không khớp Metadata hoặc rỗng): {total_reviews_skipped:,}")

    # 4. TẠO INDEXES SAU KHI BULK INSERT
    create_indexes(conn)

    # 5. THỐNG KÊ CUỐI CÙNG
    conn.commit()
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM places;")
    final_places = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM reviews;")
    final_reviews = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM dishes;")
    final_dishes = cursor.fetchone()[0]

    db_size_mb = os.path.getsize(db_path) / (1024 * 1024)
    elapsed = time.time() - start_time

    print("\n" + "=" * 75)
    print("HOÀN TẤT ETL DATABASE DU LỊCH VIỆT NAM:")
    print("=" * 75)
    print(f"• File Database SQLite : {db_path} ({db_size_mb:,.1f} MB)")
    print(f"• Bảng places          : {final_places:,} địa điểm")
    print(f"• Bảng reviews         : {final_reviews:,} bài đánh giá")
    print(f"• Bảng dishes          : {final_dishes:,} món ăn chuẩn hóa")
    print(f"• Tổng thời gian xử lý : {elapsed:.1f} giây ({elapsed/60:.2f} phút)")
    print("=" * 75)

    conn.close()

if __name__ == "__main__":
    run_etl()
