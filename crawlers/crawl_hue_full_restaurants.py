# -*- coding: utf-8 -*-
"""
==============================================================================
CRAWLER QUÉT TOÀN BỘ 100% NHÀ HÀNG & ẨM THỰC TẠI THÀNH PHỐ HUẾ
Địa bàn nghiên cứu trọng điểm: Thừa Thiên Huế (TripAdvisor Geo ID: g293926)
Thu thập sạch sành sanh toàn bộ các trang (không giới hạn quota 60 quán)
và tự động lưu nối tiếp vào database: vietnam_restaurants_link.json
==============================================================================
"""

import os
import sys
import json
import time
import re
import random
import winreg
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# CẤU HÌNH TRỌNG TÂM HUẾ
GEO = "293926"
SLUG = "Hue_Thua_Thien_Hue_Province"
DEST_NAME = "Thành phố Huế"
STEP = 30
MAX_PAGES = 25  # Tối đa 25 trang (~750 quán, thực tế Huế có khoảng ~350 quán)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "vietnam-restaurant-crawler", "restaurants", "vietnam_restaurants_link.json")


def get_chrome_version():
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


def load_existing_links():
    if not os.path.exists(OUTPUT_FILE):
        return {}
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            unique_map = {}
            for item in data:
                url = item.get("item_url", "")
                mid = re.search(r"-d(\d+)-", url)
                if mid:
                    unique_map[mid.group(1)] = item
                else:
                    unique_map[url] = item
            return unique_map
    except Exception as e:
        print(f"[Cảnh báo] Lỗi đọc file link cũ: {e}")
        return {}


def save_links(unique_items_map):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    items_list = list(unique_items_map.values())
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(items_list, f, ensure_ascii=False, indent=2)
    print(f"-> ĐÃ LƯU: Tổng số nhà hàng trong database hiện tại: {len(items_list):,} địa điểm.")


def extract_items_from_html(soup, acc):
    count_new = 0
    total_on_page = 0
    anchors = soup.find_all("a", href=True)
    seen_on_this_page = set()
    for a in anchors:
        href = a["href"]
        if "/Restaurant_Review-" not in href:
            continue

        raw_name = a.get_text(strip=True)
        if not raw_name or len(raw_name) < 2:
            continue

        clean_name = re.sub(r"^\d+\.\s*", "", raw_name).strip()
        if not clean_name or len(clean_name) < 2:
            continue

        if any(skip in clean_name.lower() for skip in ["write a review", "see all", "more", "tripadvisor"]):
            continue

        clean_url = urljoin("https://www.tripadvisor.com", href.split("?")[0].split("#")[0])
        mid = re.search(r"-d(\d+)-", clean_url)
        if not mid:
            continue

        d_id = mid.group(1)
        if d_id not in seen_on_this_page:
            seen_on_this_page.add(d_id)
            total_on_page += 1
            if d_id not in acc:
                acc[d_id] = {
                    "item_url": clean_url,
                    "item_name": clean_name,
                    "destination": DEST_NAME,
                    "category": "restaurant"
                }
                count_new += 1

    return count_new, total_on_page


def main():
    print("=" * 80)
    print("CRAWLER QUÉT TOÀN BỘ 100% NHÀ HÀNG & ẨM THỰC TẠI THÀNH PHỐ HUẾ")
    print(f"Địa bàn: {DEST_NAME} (Mã TripAdvisor: g{GEO})")
    print("Mục tiêu: Cào vét cạn kiệt toàn bộ các trang (không giới hạn quota)")
    print("=" * 80)

    unique_items = load_existing_links()
    initial_count = len(unique_items)
    hue_initial = sum(1 for item in unique_items.values() if "huế" in item.get("destination", "").lower() or "hue" in item.get("item_url", "").lower())
    print(f"-> Database đang có: {initial_count:,} nhà hàng (Trong đó Huế: ~{hue_initial} quán).")

    driver = make_driver()
    consecutive_empty = 0
    hue_collected = 0

    try:
        print("-> Warm-up phiên TripAdvisor...")
        driver.get("https://www.tripadvisor.com/")
        time.sleep(random.uniform(4.0, 5.5))

        for page_idx in range(MAX_PAGES):
            offset = page_idx * STEP
            page_url = f"https://www.tripadvisor.com/Restaurants-g{GEO}-oa{offset}-{SLUG}.html" if offset > 0 else f"https://www.tripadvisor.com/Restaurants-g{GEO}-{SLUG}.html"
            print(f"\n[Trang {page_idx + 1}] Tải: oa{offset} -> {page_url}")

            try:
                driver.get(page_url)
                time.sleep(random.uniform(3.5, 5.0))
                driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(1.0)
                driver.execute_script("window.scrollBy(0, 1500);")
                time.sleep(1.5)

                body_text = driver.find_element(By.TAG_NAME, "body").text
                if "datadome" in driver.current_url.lower() or "verify you are human" in body_text.lower() or "enter the characters you see below" in body_text.lower():
                    print("   [CẢNH BÁO BỊ CHẶN] TripAdvisor hiện Captcha! Vui lòng trượt captcha trên cửa sổ Chrome...")
                    time.sleep(15.0)

                soup = BeautifulSoup(driver.page_source, "html.parser")
                new_found, total_on_page = extract_items_from_html(soup, unique_items)
                print(f"   + Quét được {total_on_page} nhà hàng trên trang ({new_found} quán mới tinh, tổng cào thêm: {hue_collected + new_found})")
                hue_collected += new_found

                if total_on_page == 0:
                    consecutive_empty += 1
                    if consecutive_empty >= 2:
                        print("   -> Đã hết danh sách quán ăn tại Huế (trang không còn dữ liệu). Hoàn thành!")
                        break
                else:
                    consecutive_empty = 0
                    if new_found > 0:
                        save_links(unique_items)


            except Exception as e:
                print(f"   [Lỗi tải trang]: {e}")
                time.sleep(3.0)

    finally:
        try:
            driver.quit()
        except Exception:
            pass

    save_links(unique_items)
    final_count = len(unique_items)
    print("\n" + "=" * 80)
    print(f"HOÀN TẤT QUÉT HUẾ! Bổ sung thành công: +{final_count - initial_count} nhà hàng.")
    print(f"Tổng số nhà hàng toàn quốc hiện có: {final_count:,} địa điểm.")
    print("=" * 80)


if __name__ == "__main__":
    main()
