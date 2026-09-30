# -*- coding: utf-8 -*-
"""
CRAWLER DANH SÁCH NHÀ HÀNG & ẨM THỰC TOÀN QUỐC (TRIPADVISOR)
Áp dụng cho toàn bộ các trung tâm du lịch trọng điểm của 34 Tỉnh Thành Việt Nam:
  - Thành phố Huế (Ưu tiên số 1 - Địa bàn nghiên cứu khóa luận HUET)
  - Thành phố Đà Nẵng, Hội An, Nha Trang, Đà Lạt, Phú Quốc, Sa Pa, Hạ Long...

Cải tiến khắc phục lỗi cũ:
  1. Hạn ngạch theo từng tỉnh (MAX_ITEMS_PER_DESTINATION): Đảm bảo MỌI tỉnh thành đều có dữ liệu,
     không bị tình trạng Hà Nội / Sài Gòn chiếm hết hạn ngạch rồi script tự thoát.
  2. Tự động gộp và loại trùng với danh sách đã có tại:
     'crawlers/vietnam-restaurant-crawler/restaurants/vietnam_restaurants_link.json'.
  3. Cơ chế checkpoint an toàn, tự động resume nếu tắt máy giữa chừng.

Cách chạy:
  python crawlers/crawl_nationwide_restaurants.py
"""

import os
import re
import sys
import json
import time
import random
import subprocess
import winreg

# Bắt buộc UTF-8 output trên Windows
try:
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
except Exception:
    pass

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


# ==============================================================================
# CẤU HÌNH THU THẬP DỮ LIỆU
# ==============================================================================
MAX_ITEMS_PER_DESTINATION = 60   # Số lượng nhà hàng tối đa thu thập cho MỖI tỉnh/thành
STEP = 30                        # Số lượng mục trên 1 trang TripAdvisor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "vietnam-restaurant-crawler", "restaurants", "vietnam_restaurants_link.json")
PROGRESS_FILE = os.path.join(BASE_DIR, "vietnam-restaurant-crawler", "restaurants", "progress_nationwide_restaurants.json")

# Danh sách đầy đủ toàn bộ 34 Tỉnh Thành Mới của Việt Nam
# (Thành phố Huế được đặt ƯU TIÊN SỐ 1 - Địa bàn nghiên cứu trọng điểm!)
DESTINATIONS = [
    # --- 9 THÀNH PHỐ TRỰC THUỘC TRUNG ƯƠNG ---
    {"geo": "293926", "slug": "Hue_Thua_Thien_Hue_Province", "name": "Thành phố Huế"},
    {"geo": "298085", "slug": "Da_Nang", "name": "Thành phố Đà Nẵng"},
    {"geo": "298082", "slug": "Hoi_An_Quang_Nam_Province", "name": "Phố cổ Hội An (TP. Đà Nẵng)"},
    {"geo": "293924", "slug": "Hanoi", "name": "Thủ Đô Hà Nội"},
    {"geo": "293925", "slug": "Ho_Chi_Minh_City", "name": "Thành phố Hồ Chí Minh"},
    {"geo": "303946", "slug": "Vung_Tau_Ba_Ria_Vung_Tau_Province", "name": "Vũng Tàu (TP. Hồ Chí Minh)"},
    {"geo": "293923", "slug": "Halong_Bay_Quang_Ninh_Province", "name": "Thành phố Quảng Ninh (Hạ Long)"},
    {"geo": "303943", "slug": "Hai_Phong", "name": "Thành phố Hải Phòng"},
    {"geo": "737051", "slug": "Cat_Ba_Hai_Phong", "name": "Cát Bà (TP. Hải Phòng)"},
    {"geo": "659848", "slug": "Bac_Ninh_Bac_Ninh_Province", "name": "Thành phố Bắc Ninh"},
    {"geo": "1025219", "slug": "Bien_Hoa_Dong_Nai_Province", "name": "Thành phố Đồng Nai"},
    {"geo": "303942", "slug": "Can_Tho_Mekong_Delta", "name": "Thành phố Cần Thơ"},

    # --- 25 TỈNH THÀNH MỚI CÒN LẠI ---
    # Đồng bằng sông Hồng
    {"geo": "303944", "slug": "Ninh_Binh_Ninh_Binh_Province", "name": "Tỉnh Ninh Bình (Tràng An, Bái Đính)"},
    {"geo": "2028696", "slug": "Hung_Yen_Hung_Yen_Province", "name": "Tỉnh Hưng Yên"},

    # Trung du & Miền núi phía Bắc
    {"geo": "311304", "slug": "Sapa_Lao_Cai_Province", "name": "Tỉnh Lào Cai (Sa Pa, Fansipan)"},
    {"geo": "2028701", "slug": "Viet_Tri_Phu_Tho_Province", "name": "Tỉnh Phú Thọ (Đền Hùng)"},
    {"geo": "659859", "slug": "Mai_Chau_Hoa_Binh_Province", "name": "Mai Châu (Tỉnh Phú Thọ mới)"},
    {"geo": "1096181", "slug": "Ha_Giang_Ha_Giang_Province", "name": "Hà Giang (Tỉnh Tuyên Quang mới)"},
    {"geo": "2028706", "slug": "Tuyen_Quang_Tuyen_Quang_Province", "name": "Tỉnh Tuyên Quang"},
    {"geo": "2028705", "slug": "Thai_Nguyen_Thai_Nguyen_Province", "name": "Tỉnh Thái Nguyên"},
    {"geo": "2028698", "slug": "Lang_Son_Lang_Son_Province", "name": "Tỉnh Lạng Sơn"},
    {"geo": "2028690", "slug": "Cao_Bang_Cao_Bang_Province", "name": "Tỉnh Cao Bằng (Thác Bản Giốc)"},
    {"geo": "659858", "slug": "Moc_Chau_Son_La_Province", "name": "Mộc Châu (Tỉnh Sơn La)"},
    {"geo": "2028692", "slug": "Dien_Bien_Phu_Dien_Bien_Province", "name": "Tỉnh Điện Biên"},
    {"geo": "2028699", "slug": "Lai_Chau_Lai_Chau_Province", "name": "Tỉnh Lai Châu"},

    # Bắc Trung Bộ
    {"geo": "659584", "slug": "Phong_Nha_Ke_Bang_National_Park", "name": "Phong Nha (Tỉnh Quảng Trị mới)"},
    {"geo": "1414449", "slug": "Dong_Ha_Quang_Tri_Province", "name": "Tỉnh Quảng Trị"},
    {"geo": "659851", "slug": "Thanh_Hoa_Thanh_Hoa_Province", "name": "Tỉnh Thanh Hóa (Sầm Sơn)"},
    {"geo": "659847", "slug": "Vinh_Nghe_An_Province", "name": "Tỉnh Nghệ An (Cửa Lò)"},
    {"geo": "2028694", "slug": "Ha_Tinh_Ha_Tinh_Province", "name": "Tỉnh Hà Tĩnh"},

    # Duyên hải Nam Trung Bộ & Tây Nguyên
    {"geo": "293922", "slug": "Da_Lat_Lam_Dong_Province", "name": "Đà Lạt (Tỉnh Lâm Đồng)"},
    {"geo": "298086", "slug": "Phan_Thiet_Binh_Thuan_Province", "name": "Mũi Né - Phan Thiết (Tỉnh Lâm Đồng)"},
    {"geo": "293928", "slug": "Nha_Trang_Khanh_Hoa_Province", "name": "Nha Trang (Tỉnh Khánh Hòa)"},
    {"geo": "659850", "slug": "Quy_Nhon_Binh_Dinh_Province", "name": "Quy Nhơn (Tỉnh Gia Lai mới)"},
    {"geo": "659853", "slug": "Pleiku_Gia_Lai_Province", "name": "Pleiku (Tỉnh Gia Lai)"},
    {"geo": "659849", "slug": "Buon_Ma_Thuot_Dak_Lak_Province", "name": "Buôn Ma Thuột (Tỉnh Đắk Lắk)"},
    {"geo": "659855", "slug": "Tuy_Hoa_Phu_Yen_Province", "name": "Phú Yên (Tỉnh Đắk Lắk mới)"},
    {"geo": "659852", "slug": "Quang_Ngai_Quang_Ngai_Province", "name": "Tỉnh Quảng Ngãi (Đảo Lý Sơn)"},

    # Đông Nam Bộ & Đồng bằng sông Cửu Long
    {"geo": "2028709", "slug": "Tay_Ninh_Tay_Ninh_Province", "name": "Tỉnh Tây Ninh (Núi Bà Đen)"},
    {"geo": "469418", "slug": "Phu_Quoc_Island_Kien_Giang_Province", "name": "Đảo Phú Quốc (Tỉnh An Giang)"},
    {"geo": "659857", "slug": "Chau_Doc_An_Giang_Province", "name": "Châu Đốc (Tỉnh An Giang)"},
    {"geo": "303945", "slug": "My_Tho_Tien_Giang_Province", "name": "Mỹ Tho (Tỉnh Đồng Tháp mới)"},
    {"geo": "659860", "slug": "Sa_Dec_Dong_Thap_Province", "name": "Sa Đéc (Tỉnh Đồng Tháp)"},
    {"geo": "303941", "slug": "Ben_Tre_Ben_Tre_Province", "name": "Bến Tre (Tỉnh Vĩnh Long mới)"},
    {"geo": "2028715", "slug": "Ca_Mau_Ca_Mau_Province", "name": "Tỉnh Cà Mau (Mũi Cà Mau)"}
]


# ==============================================================================
# HÀM HỖ TRỢ TRÌNH DUYỆT CHROME
# ==============================================================================
def get_chrome_version():
    """Tự động kiểm tra phiên bản Google Chrome cài đặt trên hệ thống."""
    for root in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        try:
            key = winreg.OpenKey(root, r"Software\Google\Chrome\BLBeacon")
            ver, _ = winreg.QueryValueEx(key, "version")
            return int(ver.split(".")[0])
        except Exception:
            pass
    return 153


def make_driver():
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1366,1068")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")

    chrome_ver = get_chrome_version()
    print(f"-> Khởi tạo Undetected ChromeDriver (Chrome Version: {chrome_ver})...")
    driver = uc.Chrome(options=options, version_main=chrome_ver)
    driver.set_page_load_timeout(35)
    return driver


def warm_up(driver):
    print("-> Đang warm-up phiên làm việc trên TripAdvisor để tạo Session hợp lệ...")
    try:
        driver.get("https://www.tripadvisor.com/")
        time.sleep(random.uniform(4.0, 6.0))
        driver.execute_script("window.scrollBy(0, 400);")
        time.sleep(random.uniform(2.0, 3.0))
        print("   Warm-up hoàn tất thành công!\n")
    except Exception as e:
        print(f"   [Cảnh báo warm-up]: {e}")


def load_existing_links():
    """Tải các link đã có sẵn từ trước để không crawl lại trùng lặp."""
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {item.get("item_url") or item.get("url"): item for item in data if item.get("item_url") or item.get("url")}
        except Exception:
            pass
    return {}


def save_links(unique_items):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(list(unique_items.values()), f, indent=2, ensure_ascii=False)


def extract_restaurants_from_page(soup, acc, dest_name):
    """Trích xuất danh sách nhà hàng từ HTML snapshot."""
    count_new = 0
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/Restaurant_Review-" not in href:
            continue
        
        mid = re.search(r"(d\d+)", href)
        if not mid:
            continue
        
        raw_text = a.get_text(" ", strip=True)
        if not raw_text:
            continue

        clean_name = re.sub(r"^\s*\d+\.\s*", "", raw_text).strip()
        clean_url = href if href.startswith("http") else "https://www.tripadvisor.com" + href
        clean_url = clean_url.split("?")[0].split("#")[0]

        d_id = mid.group(1)
        if d_id not in acc:
            acc[d_id] = {
                "item_url": clean_url,
                "item_name": clean_name,
                "destination": dest_name,
                "category": "restaurant"
            }
            count_new += 1

    return count_new


# ==============================================================================
# HÀM CHÍNH THỰC THI CRAWLER
# ==============================================================================
def main():
    print("=" * 80)
    print("CRAWLER DANH SÁCH NHÀ HÀNG & ẨM THỰC TOÀN QUỐC (VIETNAM RESTAURANTS)")
    print(f"Tổng số trung tâm du lịch quét: {len(DESTINATIONS)} tỉnh/thành")
    print(f"Hạn ngạch mỗi địa phương: {MAX_ITEMS_PER_DESTINATION} nhà hàng")
    print("=" * 80)

    unique_items = load_existing_links()
    print(f"-> Đã có sẵn trong database: {len(unique_items):,} nhà hàng từ trước.")

    done_destinations = set()
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                done_destinations = set(json.load(f))
        except Exception:
            pass

    driver = make_driver()
    try:
        warm_up(driver)

        for idx, dest in enumerate(DESTINATIONS, 1):
            geo = dest["geo"]
            slug = dest["slug"]
            name = dest["name"]

            if geo in done_destinations:
                print(f"[{idx}/{len(DESTINATIONS)}] [BỎ QUA] Đã hoàn thành: {name}")
                continue

            print(f"\n[{idx}/{len(DESTINATIONS)}] BẮT ĐẦU CÀO: {name} (Mã TripAdvisor: g{geo})...")
            dest_acc = {}
            empty_pages = 0

            # Lặp qua các trang (mỗi trang 30 nhà hàng)
            for offset in range(0, MAX_ITEMS_PER_DESTINATION * 2, STEP):
                if len(dest_acc) >= MAX_ITEMS_PER_DESTINATION:
                    print(f"   -> Đã đạt hạn ngạch {MAX_ITEMS_PER_DESTINATION} nhà hàng cho {name}.")
                    break

                page_url = f"https://www.tripadvisor.com/Restaurants-g{geo}-oa{offset}-{slug}.html" if offset > 0 else f"https://www.tripadvisor.com/Restaurants-g{geo}-{slug}.html"
                print(f"   * Tải trang: oa{offset} -> {page_url}")

                try:
                    driver.get(page_url)
                    time.sleep(random.uniform(3.5, 5.5))

                    # Cuộn trang để tải dữ liệu động
                    driver.execute_script("window.scrollBy(0, 1000);")
                    time.sleep(1.5)
                    driver.execute_script("window.scrollBy(0, 1500);")
                    time.sleep(1.5)

                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    new_found = extract_restaurants_from_page(soup, dest_acc, name)
                    print(f"     + Thu thập được {new_found} nhà hàng mới (Tổng hiện tại của {name}: {len(dest_acc)})")

                    if new_found == 0:
                        empty_pages += 1
                        if empty_pages >= 2:
                            print(f"     [Thông báo] Đã hết danh sách nhà hàng tại {name}.")
                            break
                    else:
                        empty_pages = 0

                except Exception as e:
                    print(f"     [Lỗi tải trang]: {e}")
                    time.sleep(5)

                time.sleep(random.uniform(2.0, 4.0))

            # Hợp nhất vào bộ nhớ tổng và lưu file
            for item in dest_acc.values():
                unique_items[item["item_url"]] = item

            save_links(unique_items)
            done_destinations.add(geo)
            with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
                json.dump(list(done_destinations), f, indent=2, ensure_ascii=False)

            print(f"-> ĐÃ LƯU: Tổng số nhà hàng toàn quốc hiện tại: {len(unique_items):,} địa điểm.")
            time.sleep(random.uniform(3.0, 6.0))

        print("\n" + "=" * 80)
        print("HOÀN TẤT TOÀN BỘ QUÁ TRÌNH CÀO NHÀ HÀNG TOÀN QUỐC!")
        print(f"File kết quả cập nhật tại: {OUTPUT_FILE}")
        print("=" * 80)

    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
