# -*- coding: utf-8 -*-
"""
KHẢO SÁT & ĐÁNH GIÁ ĐỘ KHỚP DỮ LIỆU (DATASET LINKAGE SURVEY)
Kiểm tra mối liên kết giữa 8,363 địa điểm (vietnam_places_metadata.json)
và 13 file reviews thô (~1.7 triệu reviews) trong thư mục raw_dataset.
"""

import os
import sys
import glob
import json
from collections import Counter

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def normalize_url(url):
    if not url:
        return ""
    # Cắt bỏ query params và hash nếu có
    url = url.split("?")[0].split("#")[0].strip()
    return url

def main():
    # Tự động tìm đường dẫn tới data/raw dù chạy từ root hay experiments/
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, "..")) if os.path.basename(base_dir) == "experiments" else base_dir
    metadata_path = os.path.join(project_root, "data", "raw", "vietnam_places_metadata.json")
    raw_dataset_dir = os.path.join(project_root, "data", "raw", "raw_dataset")

    print("=" * 70)
    print("BƯỚC 1.1: KHẢO SÁT VÀ NỐI THỬ DỮ LIỆU (DRY-RUN LINKAGE SURVEY)")
    print("=" * 70)

    # 1. Đọc metadata địa điểm
    print("\n[1/3] Đang nạp Metadata địa điểm...")
    with open(metadata_path, "r", encoding="utf-8") as f:
        places_data = json.load(f)

    place_dict = {}
    places_by_cat = Counter()
    hue_places = set()

    for p in places_data:
        raw_url = p.get("url", "")
        norm_url = normalize_url(raw_url)
        if norm_url:
            place_dict[norm_url] = p
            cat = p.get("category", "unknown")
            places_by_cat[cat] += 1
            
            # Kiểm tra địa bàn Huế
            loc = (p.get("locality") or "").lower()
            addr = (p.get("street_address") or "").lower()
            url_str = norm_url.lower()
            if "hue" in loc or "thua thien" in loc or "hue" in addr or "-hue" in url_str:
                hue_places.add(norm_url)

    print(f"-> Tổng số địa điểm hợp lệ trong Metadata: {len(place_dict):,}")
    for cat, cnt in places_by_cat.items():
        print(f"   • {cat.capitalize():<12}: {cnt:>5,} địa điểm")
    print(f"   • Riêng địa bàn Thừa Thiên Huế: {len(hue_places):,} địa điểm")

    # 2. Quét qua 13 file reviews
    print("\n[2/3] Đang quét qua 13 file review trong raw_dataset (khoảng 1.25 GB)...")
    review_files = sorted(glob.glob(os.path.join(raw_dataset_dir, "**/*.json"), recursive=True))
    print(f"-> Tìm thấy {len(review_files)} file JSON review.")

    total_reviews = 0
    matched_reviews = 0
    unmatched_reviews = 0
    unique_review_urls = set()

    reviews_by_cat = Counter()
    reviews_by_lang = Counter()
    reviews_by_rating = Counter()
    hue_reviews_count = 0

    for idx, fpath in enumerate(review_files, 1):
        fname = os.path.basename(fpath)
        folder = os.path.basename(os.path.dirname(fpath))
        file_size_mb = os.path.getsize(fpath) / (1024 * 1024)

        try:
            with open(fpath, "r", encoding="utf-8") as fp:
                data = fp.load() if hasattr(fp, "load") else json.load(fp)
            
            count = len(data)
            total_reviews += count
            file_matched = 0

            for rev in data:
                r_url = normalize_url(rev.get("url", ""))
                if r_url:
                    unique_review_urls.add(r_url)
                    if r_url in place_dict:
                        matched_reviews += 1
                        file_matched += 1
                        p_info = place_dict[r_url]
                        cat = p_info.get("category", "unknown")
                        reviews_by_cat[cat] += 1

                        if r_url in hue_places:
                            hue_reviews_count += 1
                    else:
                        unmatched_reviews += 1

                    # Ngôn ngữ & Rating
                    lang = rev.get("language") or "Unknown"
                    reviews_by_lang[lang] += 1
                    rating = rev.get("reviews_rating")
                    if rating is not None:
                        reviews_by_rating[rating] += 1

            match_pct = (file_matched / count * 100) if count > 0 else 0
            print(f"   [{idx:02d}/13] {folder}/{fname:<30} ({file_size_mb:>6.1f} MB): {count:>7,} reviews -> Khớp: {file_matched:>7,} ({match_pct:.1f}%)")

        except Exception as e:
            print(f"   [LỖI] Đọc file {fname}: {e}")

    # 3. Tổng kết thống kê
    print("\n" + "=" * 70)
    print("KẾT QUẢ TỔNG HỢP LIÊN KẾT DỮ LIỆU:")
    print("=" * 70)
    match_rate = (matched_reviews / total_reviews * 100) if total_reviews > 0 else 0
    print(f"• Tổng số bài review trong 13 file:     {total_reviews:>10,}")
    print(f"• Số review khớp với Metadata (Nối URL): {matched_reviews:>10,} ({match_rate:.2f}%)")
    print(f"• Số review chưa có trong Metadata:      {unmatched_reviews:>10,}")
    print(f"• Số địa điểm có ít nhất 1 review:       {len(unique_review_urls & set(place_dict.keys())):>10,} / {len(place_dict):,}")

    print("\nPHÂN BỔ REVIEW ĐÃ KHỚP THEO LOẠI HÌNH:")
    for cat, cnt in reviews_by_cat.items():
        print(f"  * {cat.capitalize():<12}: {cnt:>10,} reviews ({cnt/matched_reviews*100:.1f}%)")

    print(f"\nĐỊA BÀN TRỌNG TÂM THỪA THIÊN HUẾ:")
    print(f"  * Số địa điểm tại Huế:                 {len(hue_places):>10,} địa điểm")
    print(f"  * Tổng số review tại Huế:              {hue_reviews_count:>10,} reviews")

    print("\nTOP NGÔN NGỮ ĐÁNH GIÁ (CROSS-LINGUAL):")
    for lang, cnt in reviews_by_lang.most_common(5):
        print(f"  * {lang:<15}: {cnt:>10,} reviews ({cnt/total_reviews*100:.1f}%)")

    print("\nPHÂN BỔ ĐIỂM ĐÁNH GIÁ (RATING 1-5 SAO):")
    for r in sorted(reviews_by_rating.keys()):
        cnt = reviews_by_rating[r]
        print(f"  * {r} sao: {cnt:>10,} reviews ({cnt/total_reviews*100:.1f}%)")

    print("=" * 70)

if __name__ == "__main__":
    main()
