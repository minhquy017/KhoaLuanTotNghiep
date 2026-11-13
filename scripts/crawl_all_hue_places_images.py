# -*- coding: utf-8 -*-
"""
CRAWLER MỞ RỘNG TOÀN BỘ ĐỊA ĐIỂM DU LỊCH, KHÁCH SẠN, CAFE & ẨM THỰC TẠI HUẾ
Khóa luận Tốt nghiệp ngành Khoa học Dữ liệu và Trí tuệ Nhân tạo (DS&AI - HUET)
Đề tài: Spatial GraphRAG - Cố đô Huế

Mục tiêu:
- Mở rộng kho ảnh nhận diện thị giác cho toàn bộ 631 địa điểm thực tế tại Huế
- Bao phủ:
  1. Attractions: 47 danh lam thắng cảnh, di tích lịch sử
  2. Hotels: 104 khách sạn, resort, homestay
  3. Cafes: 89 quán cà phê check-in nổi tiếng
  4. Restaurants: 391 nhà hàng, quán ăn đặc sản
- Thu thập ảnh thực địa từ đa nguồn: TripAdvisor CDN, Wikimedia Commons, Wikipedia
- Tự động bỏ qua các địa điểm đã có đủ ảnh, hỗ trợ lưu nối tiếp (Atomic Auto-Save)
"""

import os
import sys
import json
import time
import io
import hashlib
import argparse
import requests
from PIL import Image

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
IMAGE_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "visual_database", "images")
METADATA_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "visual_database", "landmark_image_index.json")
TARGETS_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "hue_crawl_targets.json")
CLEANED_PLACES_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "vietnam_places_spatial_cleaned.json")

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
HTTP_HEADERS = {
    "User-Agent": "HueTourismVisualRAG/2.0 (contact@huetourism.edu.vn; University of Hue CS Dept)"
}
DOWNLOAD_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8"
}

os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)


def get_image_hash(filepath: str) -> str:
    if not os.path.exists(filepath):
        return ""
    try:
        hasher = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return ""


def download_and_process_image(url: str, save_path: str, max_size: int = 1024) -> bool:
    try:
        resp = requests.get(url, headers=DOWNLOAD_HEADERS, timeout=15)
        if resp.status_code != 200 or len(resp.content) < 3000:
            return False

        img = Image.open(io.BytesIO(resp.content))
        if img.mode != "RGB":
            img = img.convert("RGB")

        w, h = img.size
        if w < 200 or h < 200:
            return False

        if max(w, h) > max_size:
            ratio = max_size / float(max(w, h))
            new_w = int(w * ratio)
            new_h = int(h * ratio)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        img.save(save_path, format="JPEG", quality=88, optimize=True)
        return True
    except Exception:
        return False


def search_commons_images(query: str, max_results: int = 10):
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,
        "gsrlimit": max_results,
        "prop": "imageinfo",
        "iiprop": "url|mime|size|width|height",
        "iiurlwidth": 1024
    }
    try:
        resp = requests.get(COMMONS_API, headers=HTTP_HEADERS, params=params, timeout=12)
        if resp.status_code != 200:
            return []
        data = resp.json()
        pages = data.get("query", {}).get("pages", {})
        results = []
        for page in pages.values():
            imageinfo = page.get("imageinfo", [])
            if not imageinfo:
                continue
            info = imageinfo[0]
            mime = info.get("mime", "").lower()
            if "image" not in mime or "svg" in mime or "gif" in mime:
                continue
            url = info.get("thumburl") or info.get("url")
            if url:
                results.append({
                    "title": page.get("title", ""),
                    "url": url
                })
        return results
    except Exception:
        return []


def load_metadata_map(filepath: str) -> dict:
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {item["file_path"]: item for item in data if "file_path" in item}
    except Exception:
        return {}


def atomic_save_metadata(metadata_dict: dict, file_path: str):
    tmp_path = file_path + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(list(metadata_dict.values()), f, ensure_ascii=False, indent=2)
        if os.path.exists(file_path):
            os.replace(tmp_path, file_path)
        else:
            os.rename(tmp_path, file_path)
    except Exception as e:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        print(f"⚠️ [Lỗi lưu metadata]: {e}")


def run_crawler_for_category(category_choice: str = "all", target_per_place: int = 8):
    print("=" * 80)
    print("🚀 BẮT ĐẦU CÀO DỮ LIỆU ẢNH THỰC TẾ CHO TOÀN BỘ ĐỊA ĐIỂM HUẾ")
    print("=" * 80)

    if not os.path.exists(TARGETS_FILE):
        print(f"❌ Không tìm thấy file targets: {TARGETS_FILE}")
        return

    with open(TARGETS_FILE, "r", encoding="utf-8") as f:
        targets_data = json.load(f)

    cleaned_map = {}
    if os.path.exists(CLEANED_PLACES_FILE):
        with open(CLEANED_PLACES_FILE, "r", encoding="utf-8") as f:
            cleaned_list = json.load(f)
            for p in cleaned_list:
                name_key = p.get("name", "").lower().strip()
                cleaned_map[name_key] = p

    metadata_map = load_metadata_map(METADATA_FILE)
    seen_hashes = set()
    for rel_path in metadata_map:
        abs_path = os.path.join(PROJECT_ROOT, rel_path.replace("/", os.sep))
        h = get_image_hash(abs_path)
        if h:
            seen_hashes.add(h)

    # Chọn danh mục
    cat_mapping = {
        "1": ("attractions", "Danh lam Thắng cảnh & Di tích lịch sử"),
        "2": ("hotels", "Khách sạn, Resort & Homestay"),
        "3": ("cafes", "Quán Cà phê check-in Huế"),
        "4": ("restaurants", "Nhà hàng & Quán ăn ẩm thực đặc sản"),
    }

    selected_places = []
    if category_choice in cat_mapping:
        key, label = cat_mapping[category_choice]
        selected_places = targets_data.get(key, [])
        print(f"📋 Danh mục chọn: {label} ({len(selected_places)} địa điểm)")
    else:
        for k in ["attractions", "hotels", "cafes", "restaurants"]:
            selected_places.extend(targets_data.get(k, []))
        print(f"📋 Danh mục chọn: Toàn bộ địa bàn Huế ({len(selected_places)} địa điểm)")

    print(f"📂 Hiện có {len(metadata_map)} ảnh trong cơ sở dữ liệu.")
    print(f"🎯 Mục tiêu: {target_per_place} ảnh/địa điểm.")
    print("-" * 80)

    total_new_downloads = 0
    t0 = time.time()

    for idx, place in enumerate(selected_places, 1):
        place_id_raw = place.get("place_id")
        place_id = f"place_{place_id_raw}" if str(place_id_raw).isdigit() else str(place_id_raw)
        place_name = place.get("name", "")
        category = place.get("category", "General")
        
        # Tìm tọa độ và thông tin bổ trợ từ cleaned map nếu có
        cleaned_info = cleaned_map.get(place_name.lower().strip(), {})
        lat = cleaned_info.get("latitude") or place.get("latitude") or 16.467
        lng = cleaned_info.get("longitude") or place.get("longitude") or 107.585
        address = cleaned_info.get("street_address", "Thành phố Huế")
        direct_img_url = cleaned_info.get("image_url", "")

        place_dir = os.path.join(IMAGE_OUTPUT_DIR, place_id)
        os.makedirs(place_dir, exist_ok=True)

        existing_files = [f for f in sorted(os.listdir(place_dir)) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        collected = len(existing_files)

        if collected >= target_per_place:
            continue

        print(f"\n[{idx:03d}/{len(selected_places)}] 📍 {place_name} ({place_id}) [{category.upper()}] (Đã có: {collected}/{target_per_place})")

        candidate_urls = []
        if direct_img_url:
            candidate_urls.append(("TripAdvisor", direct_img_url))

        # Tìm kiếm trên Wikimedia Commons với tên địa điểm
        commons_queries = [
            f"{place_name} Hue",
            f"{place_name}"
        ]
        for q in commons_queries:
            if len(candidate_urls) >= 15:
                break
            items = search_commons_images(q, max_results=8)
            for itm in items:
                candidate_urls.append((itm.get("title", "Wikimedia"), itm.get("url", "")))
            time.sleep(0.1)

        new_for_place = 0
        for title, img_url in candidate_urls:
            if collected >= target_per_place:
                break
            if not img_url:
                continue

            collected += 1
            file_name = f"img_{collected:02d}.jpg"
            save_path = os.path.join(place_dir, file_name)

            success = download_and_process_image(img_url, save_path)
            if success:
                h = get_image_hash(save_path)
                if h and h in seen_hashes:
                    try:
                        os.remove(save_path)
                    except Exception:
                        pass
                    collected -= 1
                    continue

                seen_hashes.add(h)
                new_for_place += 1
                total_new_downloads += 1
                rel_path = os.path.relpath(save_path, PROJECT_ROOT).replace(os.sep, "/")

                cap = f"Ảnh thực địa check-in tại {place_name} ({address}) Cố đô Huế"
                metadata_map[rel_path] = {
                    "image_id": f"img_{place_id}_{collected:02d}",
                    "place_id": place_id,
                    "place_name": place_name,
                    "sub_location": address,
                    "category": category,
                    "file_path": rel_path,
                    "source_title": title[:60],
                    "source_url": img_url,
                    "caption": cap,
                    "latitude": lat,
                    "longitude": lng
                }
                print(f"   ✓ [Ảnh {collected:02d}/{target_per_place}] {file_name} <- {title[:35]}")
                time.sleep(0.15)
            else:
                collected -= 1

        if new_for_place > 0:
            atomic_save_metadata(metadata_map, METADATA_FILE)

    elapsed = time.time() - t0
    print("\n" + "=" * 80)
    print("🎉 HOÀN TẤT ĐỢT CÀO ẢNH!")
    print(f"📥 Tải mới: +{total_new_downloads} ảnh thực tế")
    print(f"📚 Tổng kho ảnh hiện tại: {len(metadata_map)} ảnh")
    print(f"⏱️ Thời gian chạy: {elapsed/60:.2f} phút")
    print(f"📄 Metadata: {METADATA_FILE}")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Hue Full Places Image Crawler")
    parser.add_argument("--category", choices=["1", "2", "3", "4", "all"], default=None, help="1: Di tích, 2: Khách sạn, 3: Cafe, 4: Quán ăn, all: Toàn bộ")
    parser.add_argument("--target", type=int, default=8, help="Số ảnh mục tiêu cho mỗi địa điểm (mặc định: 8)")
    args = parser.parse_args()

    if args.category:
        run_crawler_for_category(category_choice=args.category, target_per_place=args.target)
        return

    print("""
======================================================================
🌸 CÀO DỮ LIỆU ẢNH THỰC TẾ CHO 631 ĐỊA ĐIỂM TẠI HUẾ
======================================================================
Chọn phân nhóm địa điểm bạn muốn cào thêm ảnh về máy:

  [1] Danh lam Thắng cảnh & Di tích còn thiếu (47 điểm)
  [2] Khách sạn, Resort & Homestay Huế (104 điểm)
  [3] Quán Cà phê check-in đẹp xứ Huế (89 điểm)
  [4] Nhà hàng & Quán ăn ẩm thực đặc sản Huế (391 quán)
  [5] Cào toàn bộ (Tất cả 631 địa điểm trên khắp Huế)
  [0] Thoát
======================================================================
""")
    try:
        c = input("👉 Nhập số bạn muốn chạy [0-5] (Mặc định 5): ").strip()
    except Exception:
        c = "5"
    if not c or c == "5":
        c = "all"
    elif c == "0":
        return
    run_crawler_for_category(category_choice=c, target_per_place=args.target)


if __name__ == "__main__":
    main()

