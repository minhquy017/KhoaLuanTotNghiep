# -*- coding: utf-8 -*-
"""
FOOD ENTITY MINING PIPELINE (KHAI PHÁ THỰC ĐƠN NGẦM TỪ BÀI ĐÁNH GIÁ)
- Sử dụng spaCy PhraseMatcher (Aho-Corasick C-optimized Trie)
- Khai phá thực đơn ngầm cho 3,308 nhà hàng từ hơn 420,000 bài đánh giá ẩm thực.
- Tính toán tần suất xuất hiện (mention_count), điểm đánh giá trung bình (avg_rating)
  và chỉ số cảm xúc chuẩn hóa (sentiment_score [-1.0, +1.0]).
- Lưu kết quả vào bảng `restaurant_dishes` trong SQLite `data/processed/tourism_vietnam.db`.
"""

import os
import sys
import json
import sqlite3
import time
from collections import defaultdict, Counter
import spacy
from spacy.matcher import PhraseMatcher
from spacy.util import filter_spans

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def load_gazetteer(gazetteer_path):
    """Nạp từ điển ẩm thực Việt Nam và xây dựng ánh xạ thông tin món"""
    with open(gazetteer_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    dish_meta = {}
    for item in data:
        dish_meta[item["dish_id"]] = {
            "canonical_name": item["canonical_name"],
            "category": item.get("category", ""),
            "region_origin": item.get("region_origin", ""),
            "aliases": item.get("aliases", [])
        }
    return data, dish_meta

def build_matcher(nlp, gazetteer_data):
    """Khởi tạo spaCy PhraseMatcher đa ngữ tối ưu hóa tốc độ cao"""
    print("[Matcher] Đang biên dịch đồ thị Aho-Corasick PhraseMatcher từ 570+ món ăn...")
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    
    pattern_count = 0
    for item in gazetteer_data:
        dish_id = item["dish_id"]
        aliases = item.get("aliases", [])
        # Lọc alias hợp lệ
        valid_aliases = [a.strip() for a in aliases if len(a.strip()) > 1]
        patterns = [nlp.make_doc(text) for text in valid_aliases]
        if patterns:
            matcher.add(dish_id, patterns)
            pattern_count += len(patterns)
            
    print(f"-> Đã nạp thành công {pattern_count:,} mẫu từ khóa đối sánh vào bộ nhớ.")
    return matcher

def run_food_mining():
    start_time = time.time()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, "..", ".."))
    
    db_path = os.path.join(project_root, "data", "processed", "tourism_vietnam.db")
    gazetteer_path = os.path.join(project_root, "data", "processed", "culinary_gazetteer.json")

    print("=" * 75)
    print("BƯỚC 1.3: KHAI PHÁ THỰC ĐƠN NGẦM BẰNG SPACY PHRASEMATCHER")
    print("=" * 75)

    if not os.path.exists(db_path):
        print(f"[LỖI] Không tìm thấy cơ sở dữ liệu: {db_path}")
        return

    # 1. Nạp từ điển
    gazetteer_data, dish_meta = load_gazetteer(gazetteer_path)
    
    # 2. Khởi tạo spaCy tokenizer siêu tốc
    nlp = spacy.blank("en")
    matcher = build_matcher(nlp, gazetteer_data)

    # 3. Kết nối SQLite
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA cache_size = 200000;")
    cursor = conn.cursor()

    # 4. Đếm số lượng review nhà hàng
    print("\n[Data] Đang truy vấn bài đánh giá thuộc các nhà hàng ẩm thực...")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM reviews r
        JOIN places p ON r.place_url = p.url
        WHERE p.category = 'restaurant';
    """)
    total_reviews = cursor.fetchone()[0]
    print(f"-> Tổng số review nhà hàng cần khai phá: {total_reviews:,} bài")

    # Cấu trúc lưu trữ: rest_dish_stats[place_url][dish_id] = [ratings...]
    rest_dish_stats = defaultdict(lambda: defaultdict(list))
    
    # Thống kê toàn cục
    global_dish_mentions = Counter()

    batch_size = 25000
    offset = 0
    processed_count = 0
    total_matched_spans = 0

    print(f"\n[Mining] Bắt đầu quét qua {total_reviews:,} review (batch {batch_size:,} bài)...")

    while offset < total_reviews:
        cursor.execute(f"""
            SELECT r.place_url, r.title, r.comment, r.reviews_rating
            FROM reviews r
            JOIN places p ON r.place_url = p.url
            WHERE p.category = 'restaurant'
            LIMIT {batch_size} OFFSET {offset};
        """)
        rows = cursor.fetchall()
        if not rows:
            break

        for place_url, title, comment, rating in rows:
            text = f"{title or ''}. {comment or ''}"
            if not text.strip():
                continue
                
            doc = nlp.make_doc(text)
            matches = matcher(doc, as_spans=True)
            
            if matches:
                # Lọc bỏ các span chồng lấn (chọn cụm từ dài nhất, đặc thù nhất)
                distinct_spans = filter_spans(matches)
                # Tập món ăn xuất hiện trong bài review này (tránh đếm lặp trong cùng 1 bài)
                review_dishes = set()
                
                for span in distinct_spans:
                    dish_id = span.label_
                    review_dishes.add(dish_id)
                    total_matched_spans += 1
                
                # Cập nhật rating và đếm lượt nhắc cho từng món của nhà hàng
                r_val = rating if (rating is not None and 1 <= rating <= 5) else 4.0
                for dish_id in review_dishes:
                    rest_dish_stats[place_url][dish_id].append(r_val)
                    global_dish_mentions[dish_id] += 1

        processed_count += len(rows)
        offset += batch_size
        elapsed = time.time() - start_time
        speed = processed_count / elapsed if elapsed > 0 else 0
        pct = processed_count / total_reviews * 100
        print(f"   * Tiến độ: {processed_count:>7,}/{total_reviews:,} ({pct:5.1f}%) | Tốc độ: {speed:6.1f} rev/s | Món đã match: {total_matched_spans:>7,}")

    # 5. Lưu vào bảng restaurant_dishes
    print("\n[Database] Đang tính toán chỉ số và ghi dữ liệu vào bảng restaurant_dishes...")
    cursor.execute("DELETE FROM restaurant_dishes;")
    
    insert_rows = []
    for place_url, dishes in rest_dish_stats.items():
        for dish_id, ratings in dishes.items():
            mention_cnt = len(ratings)
            avg_r = round(sum(ratings) / mention_cnt, 2)
            # Sentiment score normalized to [-1.0, 1.0]: (rating - 3) / 2.0
            sentiment = round(sum((r - 3.0) / 2.0 for r in ratings) / mention_cnt, 2)
            insert_rows.append((place_url, dish_id, mention_cnt, avg_r, sentiment))

    cursor.executemany("""
        INSERT INTO restaurant_dishes (place_url, dish_id, mention_count, avg_rating, sentiment_score)
        VALUES (?, ?, ?, ?, ?);
    """, insert_rows)
    conn.commit()

    # Tạo lại chỉ mục nếu chưa có
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rest_dishes_place ON restaurant_dishes(place_url);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rest_dishes_dish ON restaurant_dishes(dish_id);")
    conn.commit()

    print(f"-> Đã ghi thành công {len(insert_rows):,} quan hệ (Nhà hàng - Món ăn) vào SQLite!")

    # 6. Thống kê báo cáo chuyên sâu
    print("\n" + "=" * 75)
    print("KẾT QUẢ KHAI PHÁ THỰC ĐƠN NGẦM (FOOD ENTITY MINING REPORT):")
    print("=" * 75)
    print(f"• Số nhà hàng tìm thấy ít nhất 1 món: {len(rest_dish_stats):,} / 3,308 nhà hàng ({len(rest_dish_stats)/3308*100:.1f}%)")
    print(f"• Tổng số lượt thực khách nhắc đến món: {total_matched_spans:,} lượt")
    print(f"• Số món ăn đặc sản được nhắc đến: {len(global_dish_mentions):,} / {len(gazetteer_data)} món trong từ điển")

    print("\nTOP 20 MÓN ĂN VIỆT NAM ĐƯỢC NHẮC ĐẾN NHIỀU NHẤT TOÀN QUỐC:")
    print(f"{'Hạng':<5} {'Tên món ăn':<32} {'Nhóm món':<24} {'Lượt nhắc':>12}")
    print("-" * 75)
    for rank, (dish_id, count) in enumerate(global_dish_mentions.most_common(20), 1):
        meta = dish_meta.get(dish_id, {})
        name = meta.get("canonical_name", dish_id)
        cat = meta.get("category", "")
        print(f"#{rank:<4} {name:<32} {cat:<24} {count:>12,}")

    # Top món ăn tại riêng Thừa Thiên Huế
    cursor.execute("""
        SELECT rd.dish_id, SUM(rd.mention_count) as total_mentions
        FROM restaurant_dishes rd
        JOIN places p ON rd.place_url = p.url
        WHERE p.is_hue = 1
        GROUP BY rd.dish_id
        ORDER BY total_mentions DESC
        LIMIT 15;
    """)
    hue_top = cursor.fetchall()
    print("\nTOP 15 MÓN ĂN ĐƯỢC NHẮC ĐẾN NHIỀU NHẤT TẠI THỪA THIÊN HUẾ:")
    print(f"{'Hạng':<5} {'Tên món ăn':<32} {'Nhóm món':<24} {'Lượt nhắc':>12}")
    print("-" * 75)
    for rank, (dish_id, count) in enumerate(hue_top, 1):
        meta = dish_meta.get(dish_id, {})
        name = meta.get("canonical_name", dish_id)
        cat = meta.get("category", "")
        print(f"#{rank:<4} {name:<32} {cat:<24} {count:>12,}")

    # Khám phá thực đơn ngầm của 2 nhà hàng biểu tượng tại Huế
    sample_queries = [
        ("Quán Bánh Bà Đỏ (Huế)", "%Ba_Do%"),
        ("Quán Hạnh (Huế)", "%Hanh%"),
        ("Bếp Mẹ Ỉn (Sài Gòn)", "%Bếp_Mẹ_Ỉn%"),
        ("Phở Gia Truyền Bát Đàn (Hà Nội)", "%Bat_Dan%")
    ]
    print("\nVÍ DỤ THỰC ĐƠN NGẦM KHAI PHÁ TỪ BÀI ĐÁNH GIÁ CỦA MỘT SỐ QUÁN NỔI TIẾNG:")
    for label, pattern in sample_queries:
        cursor.execute("""
            SELECT p.name, p.street_address, rd.dish_id, rd.mention_count, rd.avg_rating, rd.sentiment_score
            FROM restaurant_dishes rd
            JOIN places p ON rd.place_url = p.url
            WHERE p.url LIKE ?
            ORDER BY rd.mention_count DESC
            LIMIT 5;
        """, (pattern,))
        res = cursor.fetchall()
        if res:
            p_name = res[0][0]
            p_addr = res[0][1]
            print(f"\n[+] {label} - {p_name} ({p_addr}):")
            for _, _, d_id, m_cnt, a_rat, sent in res:
                d_name = dish_meta.get(d_id, {}).get("canonical_name", d_id)
                print(f"    * {d_name:<28}: {m_cnt:>4} reviews | Rating: {a_rat:.1f}* | Sentiment: {sent:+.2f}")

    total_time = time.time() - start_time
    print("\n" + "=" * 75)
    print(f"HOÀN TẤT KHAI PHÁ THỰC ĐƠN NGẦM TRONG {total_time:.1f} GIÂY ({total_time/60:.2f} PHÚT)!")
    print("=" * 75)

    conn.close()

if __name__ == "__main__":
    run_food_mining()
