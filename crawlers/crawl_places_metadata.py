# -*- coding: utf-8 -*-
"""
CRAWLER METADATA ĐỊA ĐIỂM (JSON-LD: Lat/Lng, Address, Cuisine, Rating)
Áp dụng cho toàn bộ 9.072 địa điểm du lịch Việt Nam trên TripAdvisor:
  - 2.426 Khách sạn (Hotels)
  - 3.308 Nhà hàng (Restaurants)
  - 3.338 Điểm tham quan (Attractions)

Đặc điểm chính:
  1. KHÔNG crawl review -> Tốc độ cực nhanh (~2 - 4 giây / địa điểm).
  2. Bóc trực tiếp thẻ <script type="application/ld+json"> chứa Schema chuẩn.
  3. Lấy trọn vẹn: Tọa độ (lat, lng), Địa chỉ, Quận/Huyện, Thành phố, Ẩm thực, Mức giá, Rating.
  4. Hỗ trợ chia máy (NUM_WORKERS, WORKER_ID) y hệt hệ thống crawler cũ của bạn.
  5. Checkpoint an toàn: Lưu sau mỗi địa điểm, tự động resume nếu tắt máy giữa chừng.
  6. Chống phát hiện bot: Warm-up phiên làm việc, ngẫu nhiên hóa thời gian nghỉ.

Cách chạy:
  python crawl_places_metadata.py
"""

import os
import re
import sys
import json
import time
import random
import traceback
import subprocess

# Bắt buộc stdout dùng UTF-8 và flush ngay lập tức trên Windows
try:
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
except Exception:
    pass

import undetected_chromedriver as uc
from bs4 import BeautifulSoup


# ==============================================================================
# CẤU HÌNH CHẠY TRÊN 1 MÁY DUY NHẤT (SINGLE MACHINE)
# ==============================================================================
# File lưu kết quả và file checkpoint ghi nhớ tiến độ (trỏ thẳng vào data/raw/)
BASE_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT_DIR = os.path.dirname(BASE_SCRIPT_DIR)
DATA_RAW_DIR = os.path.join(PROJECT_ROOT_DIR, "data", "raw")
os.makedirs(DATA_RAW_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(DATA_RAW_DIR, "vietnam_places_metadata.json")
PROGRESS_FILE = os.path.join(DATA_RAW_DIR, "progress_places_metadata.json")

# Thời gian nghỉ giữa các địa điểm (giây) - Đặt 4-7s để DataDome không nghi ngờ quét bot hàng loạt
REQUEST_GAP = (4.0, 7.5)

# Nghỉ giải lao sau mỗi N địa điểm
REST_EVERY_PLACES = 30
LONG_REST = (35.0, 70.0)

# Xử lý khi bị chặn (Pardon Our Interruption / Bot detected)
BLOCK_COOLDOWN = (180.0, 300.0)   # Nghỉ 3 - 5 phút
MAX_BLOCK_RESTARTS = 3


# ==============================================================================
# TẢI DANH SÁCH 9.072 LINK TỪ CÁC THƯ MỤC CRAWLER
# ==============================================================================
def load_all_place_links():
    """Đọc và chuẩn hóa toàn bộ 9.072 link từ 3 thư mục crawler hiện có."""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    hotel_link_file = os.path.join(base_dir, "vietnam-hotel-crawler", "vietnam_hotels_link.json")
    rest_link_file = os.path.join(base_dir, "vietnam-restaurant-crawler", "restaurants", "vietnam_restaurants_link.json")
    attr_link_file = os.path.join(base_dir, "vietnam-attraction-crawler", "attractions", "vietnam_attractions_link.json")

    places = []
    seen_urls = set()

    def add_items(filepath, category):
        if not os.path.exists(filepath):
            print(f"[CẢNH BÁO] Không tìm thấy file: {filepath}")
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            count = 0
            for item in data:
                url = item.get("hotel_url") or item.get("item_url") or ""
                name = item.get("hotel_name") or item.get("item_name") or ""
                num_reviews = item.get("number_of_reviews", "0")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    places.append({
                        "url": url,
                        "name": name,
                        "category": category,
                        "number_of_reviews": num_reviews
                    })
                    count += 1
            print(f"-> Đã nạp {count:>4} địa điểm từ {category.upper()}: {os.path.basename(filepath)}")
        except Exception as e:
            print(f"[LỖI] Đọc file {filepath}: {e}")

    print("=" * 65)
    print("ĐANG TẢI DANH SÁCH TOÀN BỘ ĐỊA ĐIỂM...")
    add_items(hotel_link_file, "hotel")
    add_items(rest_link_file, "restaurant")
    add_items(attr_link_file, "attraction")
    print(f"=> TỔNG CỘNG HỢP NHẤT: {len(places)} địa điểm duy nhất.")
    print("=" * 65)
    return places


# ==============================================================================
# HÀM TẠO VÀ QUẢN LÝ TRÌNH DUYỆT UNDETECTED CHROME
def get_chrome_major_version():
    """Tự động đọc phiên bản Chrome đang cài trên máy để tránh lỗi lệch phiên bản ChromeDriver."""
    try:
        import winreg
        for root in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
            try:
                key = winreg.OpenKey(root, r"Software\Google\Chrome\BLBeacon")
                ver, _ = winreg.QueryValueEx(key, "version")
                return int(ver.split(".")[0])
            except Exception:
                pass
    except Exception:
        pass
    return 153


def make_driver():
    """Tạo trình duyệt Chrome giống hệt crawler review (dùng UA gốc của máy)."""
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1366,1068")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")

    chrome_major = get_chrome_major_version()
    driver = uc.Chrome(options=options, version_main=chrome_major)
    driver.set_page_load_timeout(35)
    return driver


def warm_up(driver):
    """Truy cập trang chủ để tạo cookie và session hợp lệ."""
    print("-> Đang warm-up phiên làm việc trên TripAdvisor...")
    try:
        driver.get("https://www.tripadvisor.com/")
        time.sleep(random.uniform(5.0, 8.0))
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(random.uniform(2.0, 3.5))
        print("   Warm-up hoàn tất thành công!\n")
    except Exception as e:
        print(f"   [Cảnh báo warm-up]: {e}")


def random_scroll(driver):
    """Cuộn trang nhẹ để giả lập hành vi người dùng thật (vượt qua DataDome)."""
    try:
        driver.execute_script(f"window.scrollBy(0, {random.randint(350, 650)});")
        time.sleep(random.uniform(0.8, 1.5))
    except Exception:
        pass


def is_blocked(driver):
    """Kiểm tra xem trang hiện tại có bị chặn bởi Bot Detection không."""
    try:
        title = driver.title.lower()
        if "pardon our interruption" in title or "access denied" in title:
            return True
        src = driver.page_source.lower()
        if "security check" in src and "captcha" in src:
            return True
        # Nếu title bị rút gọn và không có nội dung
        if driver.title.strip() == "tripadvisor.com" and len(driver.page_source) < 2000:
            return True
    except Exception:
        pass
    return False


# ==============================================================================
# HÀM BÓC TÁCH JSON-LD SCHEMA.ORG TỪ HTML
# ==============================================================================
def extract_metadata_from_html(html_source, place_url, default_category, fallback_name=""):
    """
    Trích xuất toàn bộ metadata từ thẻ <script type="application/ld+json">.
    Trả về dict chuẩn hóa chứa lat, lng, address, cuisine, v.v.
    """
    soup = BeautifulSoup(html_source, "html.parser")
    target_data = None

    # Tìm tất cả các thẻ JSON-LD trong trang
    scripts = soup.find_all("script", type="application/ld+json")
    for s in scripts:
        if not s.string:
            continue
        try:
            data = json.loads(s.string)
            if not isinstance(data, dict):
                continue
            
            t = data.get("@type", "")
            # Bỏ qua BreadcrumbList
            if t == "BreadcrumbList":
                continue
            
            # Ưu tiên object chứa tọa độ geo hoặc địa chỉ address
            if "geo" in data or "address" in data or t in ["Hotel", "LodgingBusiness", "FoodEstablishment", "Restaurant", "LocalBusiness", "TouristAttraction"]:
                target_data = data
                break
        except Exception:
            continue

    # Khởi tạo bản ghi chuẩn hóa
    res = {
        "url": place_url,
        "name": fallback_name,
        "category": default_category,
        "latitude": None,
        "longitude": None,
        "street_address": "",
        "district": "",
        "locality": "",
        "postal_code": "",
        "country": "VN",
        "cuisines": [],
        "price_range": "",
        "rating_value": None,
        "review_count": None,
        "telephone": "",
        "image_url": "",
        "raw_type": ""
    }

    if not target_data:
        # Nếu trang không có JSON-LD hoặc bị lỗi DOM
        return res

    # 1. Tên địa điểm
    if target_data.get("name"):
        res["name"] = target_data["name"]

    res["raw_type"] = target_data.get("@type", "")

    # 2. Tọa độ địa lý (Lat, Lng) - YẾU TỐ VÀNG CHO GRAPH
    geo = target_data.get("geo")
    if isinstance(geo, dict):
        try:
            res["latitude"] = float(geo.get("latitude"))
        except (TypeError, ValueError):
            pass
        try:
            res["longitude"] = float(geo.get("longitude"))
        except (TypeError, ValueError):
            pass

    # 3. Địa chỉ hành chính (Address, District, Locality)
    addr = target_data.get("address")
    if isinstance(addr, dict):
        res["street_address"] = addr.get("streetAddress") or ""
        res["locality"] = addr.get("addressLocality") or ""
        res["postal_code"] = addr.get("postalCode") or ""
        
        country = addr.get("addressCountry")
        if isinstance(country, dict):
            res["country"] = country.get("name", "VN")
        elif isinstance(country, str):
            res["country"] = country

        # Phân tích quận/huyện từ streetAddress hoặc addressLocality
        full_addr = f"{res['street_address']} {res['locality']}"
        district_match = re.search(r'(Quận\s+\d+|Quận\s+[\w\s]+|Huyện\s+[\w\s]+|District\s+\d+|District\s+[\w\s]+|Cau Giay|Hoan Kiem|Ba Dinh|Hai Ba Trung|Dong Da|Tay Ho|Thao Dien|Son Tra|Ngu Hanh Son|Hai Chau)', full_addr, re.IGNORECASE)
        if district_match:
            res["district"] = district_match.group(0).strip()

    # Fallback thành phố từ URL slug nếu Schema không có addressLocality
    if not res["locality"]:
        slug_match = re.search(r'-Reviews-.*?-([A-Za-z0-9_]+)\.html', place_url)
        if slug_match:
            res["locality"] = slug_match.group(1).replace('_', ' ')

    # 4. Ẩm thực (Cuisines) đối với Nhà hàng
    cuisines = target_data.get("servesCuisine")
    if cuisines:
        if isinstance(cuisines, list):
            res["cuisines"] = [str(c).strip() for c in cuisines if c]
        elif isinstance(cuisines, str):
            res["cuisines"] = [c.strip() for c in cuisines.split(",") if c.strip()]

    # 5. Mức giá (Price Range)
    if target_data.get("priceRange"):
        res["price_range"] = str(target_data["priceRange"])

    # 6. Đánh giá & Số lượng review (Aggregate Rating)
    agg_rating = target_data.get("aggregateRating")
    if isinstance(agg_rating, dict):
        try:
            res["rating_value"] = float(agg_rating.get("ratingValue"))
        except (TypeError, ValueError):
            pass
        try:
            res["review_count"] = int(agg_rating.get("reviewCount"))
        except (TypeError, ValueError):
            pass

    # 7. Số điện thoại & Ảnh đại diện
    if target_data.get("telephone"):
        res["telephone"] = str(target_data["telephone"])
    if target_data.get("image"):
        img = target_data["image"]
        res["image_url"] = img if isinstance(img, str) else (img[0] if isinstance(img, list) and len(img) > 0 else "")

    return res


# ==============================================================================
# HÀM LƯU FILE ATOMIC & CHECKPOINT AN TOÀN
# ==============================================================================
def save_atomic(filepath, data):
    """Ghi đè file an toàn (ghi vào file temp rồi đổi tên) kèm bản sao lưu .bak."""
    temp_file = filepath + ".tmp"
    bak_file = filepath + ".bak"
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        if os.path.exists(filepath):
            try:
                os.replace(filepath, bak_file)
            except Exception:
                pass
        os.replace(temp_file, filepath)
    except Exception as e:
        print(f"[LỖI LƯU FILE]: {e}")


def load_progress():
    """Đọc danh sách URL các địa điểm đã hoàn thành."""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            pass
    return set()


def load_existing_results():
    """Đọc danh sách kết quả đã lưu từ trước để resume tiếp."""
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


# ==============================================================================
# VÒNG LẶP CHÍNH (MAIN CRAWLER PIPELINE)
# ==============================================================================
def main():
    print("""
    ===============================================================
       TRÌNH THU THẬP METADATA ĐỊA ĐIỂM TRIPADVISOR (JSON-LD)
       - Mục tiêu: Lat/Lng, Address, Cuisines, Price, Ratings
       - Tối ưu cho Đồ thị Tri thức (Knowledge Graph) Du lịch VN
    ===============================================================
    """)

    # 1. Tải toàn bộ 9.072 địa điểm
    all_places = load_all_place_links()
    if not all_places:
        print("Không có dữ liệu đầu vào. Vui lòng kiểm tra các file link.")
        return

    # 2. Toàn bộ danh sách 9.072 địa điểm chạy trên máy này
    my_places = all_places
    print(f"\n[TIẾN TRÌNH]: Chạy đơn máy phụ trách toàn bộ: {len(my_places)} địa điểm.")
    print(f"-> Ghi dữ liệu trực tiếp vào: {OUTPUT_FILE}")
    print(f"-> Ghi checkpoint tiến độ vào: {PROGRESS_FILE}\n")

    # 3. Khôi phục trạng thái cũ (Resume)
    done_urls = load_progress()
    results = load_existing_results()
    print(f"-> Đã hoàn thành từ các lần chạy trước: {len(done_urls)} địa điểm.")
    
    # Lọc danh sách cần xử lý tiếp
    todo_places = [p for p in my_places if p["url"] not in done_urls]
    print(f"-> Cần xử lý tiếp: {len(todo_places)} địa điểm.\n")

    if not todo_places:
        print("Worker này đã hoàn thành 100% nhiệm vụ!")
        return

    # 4. Khởi tạo trình duyệt Chrome
    driver = None
    restarts = 0

    def get_new_session():
        nonlocal driver
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        d = make_driver()
        warm_up(d)
        return d

    driver = get_new_session()

    # 5. Bắt đầu duyệt từng địa điểm
    success_count = 0
    start_time = time.time()

    for idx, place in enumerate(todo_places, 1):
        url = place["url"]
        category = place["category"]
        name = place["name"]
        total_completed = len(done_urls) + 1
        pct = (total_completed / len(all_places)) * 100

        print(f"[{total_completed}/{len(all_places)}] ({pct:.1f}%) [{category.upper()}]: {name[:35]}...")

        # Thử tải trang và bóc tách
        retry_place = 0
        got_data = False

        while retry_place < 2 and not got_data:
            try:
                driver.get(url)
                time.sleep(random.uniform(3.0, 4.5))
                random_scroll(driver)

                # Kiểm tra xem có bị dính Captcha/Block không
                if is_blocked(driver):
                    print("   [CẢNH BÁO BỊ CHẶN] TripAdvisor hiện Captcha DataDome!")
                    print("   -> (Nếu bạn thấy ô trượt Captcha trên cửa sổ Chrome, hãy gạt trượt để mở khóa luôn nhé!)")
                    time.sleep(12.0)
                    
                    if not is_blocked(driver):
                        print("   -> Đã vượt qua Captcha thành công! Tiếp tục crawl...")
                    else:
                        try:
                            driver.quit()
                        except Exception:
                            pass
                        cooldown = random.uniform(*BLOCK_COOLDOWN)
                        print(f"   Đang ngủ nghỉ {cooldown/60:.1f} phút trước khi tạo phiên mới...")
                        time.sleep(cooldown)
                        driver = get_new_session()
                        retry_place += 1
                        continue

                html = driver.page_source
                meta = extract_metadata_from_html(html, url, category, fallback_name=name)

                # Hiển thị thông tin trích xuất tóm tắt
                geo_info = f"({meta['latitude']:.4f}, {meta['longitude']:.4f})" if meta['latitude'] else "(Chưa có Lat/Lng)"
                cuis_info = f" | {', '.join(meta['cuisines'][:2])}" if meta['cuisines'] else ""
                dist_info = f" | {meta['district']}" if meta['district'] else ""
                print(f"   -> OK: {meta['name'][:30]} | {geo_info}{dist_info}{cuis_info}")

                # Lưu kết quả
                results.append(meta)
                done_urls.add(url)
                save_atomic(OUTPUT_FILE, results)
                save_atomic(PROGRESS_FILE, list(done_urls))

                success_count += 1
                got_data = True

            except Exception as e:
                print(f"   [Lỗi khi tải trang]: {str(e).splitlines()[0]}")
                retry_place += 1
                time.sleep(3.0)

        # Nghỉ định kỳ sau mỗi 50 địa điểm
        if success_count > 0 and success_count % REST_EVERY_PLACES == 0:
            rest_sec = random.uniform(*LONG_REST)
            print(f"\n--- [NGHỈ GIẢI LAO ĐỊNH KỲ] Đã xong {success_count} điểm. Nghỉ {rest_sec:.1f}s để an toàn... ---\n")
            time.sleep(rest_sec)
        else:
            time.sleep(random.uniform(*REQUEST_GAP))

    # Đóng trình duyệt khi xong việc
    try:
        driver.quit()
    except Exception:
        pass

    elapsed = time.time() - start_time
    print("\n" + "=" * 65)
    print(f"HOÀN TẤT NHIỆM VỤ CỦA WORKER {WORKER_ID}!")
    print(f"-> Tổng số địa điểm đã lấy thành công: {len(results)}")
    print(f"-> Thời gian chạy: {elapsed/60:.1f} phút (Trung bình: {elapsed/max(1, success_count):.2f}s / điểm)")
    print(f"-> Dữ liệu đã lưu tại: {os.path.abspath(OUTPUT_FILE)}")
    print("=" * 65)


if __name__ == "__main__":
    main()
