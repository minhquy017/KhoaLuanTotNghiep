# -*- coding: utf-8 -*-
"""
CRAWLER CHUYÊN BIỆT: THU THẬP BỔ SUNG REVIEW CỐ ĐÔ HUẾ
Khóa luận Tốt nghiệp ngành Khoa học Dữ liệu và Trí tuệ Nhân tạo (DS&AI K3 - HUET)
-----------------------------------------------------------------------------------------------------
- Mục tiêu: Thu thập khoảng 15.000 - 20.000 bài review thực tế của du khách tại Thừa Thiên Huế:
    + 29 Điểm tham quan (Attractions): Top di sản lấy 300 - 500 review; các điểm khác lấy 100 - 200 review.
    + 380 Nhà hàng (Restaurants): Quán nổi tiếng lấy 150 - 200 review; quán vừa lấy 50 - 100; quán nhỏ lấy hết.
- Dữ liệu đích: data/raw/hue_reviews_supplement.json
- Checkpoint: data/raw/progress_hue_reviews.json (Lưu sau mỗi địa điểm, tự động resume khi chạy lại).
"""

import os
import sys
import re
import json
import time
import random
import winreg
import subprocess
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

try:
    from langdetect import detect
except Exception:
    detect = None

# Bắt buộc UTF-8 stdout
try:
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
TARGETS_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "hue_crawl_targets.json")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "data", "raw", "hue_reviews_supplement.json")
PROGRESS_FILE = os.path.join(PROJECT_ROOT, "data", "raw", "progress_hue_reviews.json")
PARTIAL_FILE = os.path.join(PROJECT_ROOT, "data", "raw", "partial_hue_reviews.json")

DOMAIN = "www.tripadvisor.com"

# Cấu hình hạn mức (Quotas)
MAX_REVIEWS_TOP_ATTRACTION = 400    # Đại Nội, Thiên Mụ, Lăng Minh Mạng...
MAX_REVIEWS_NORMAL_ATTRACTION = 150 # Các điểm tham quan khác
MAX_REVIEWS_TOP_RESTAURANT = 180    # Quán ăn nổi tiếng > 500 review
MAX_REVIEWS_MID_RESTAURANT = 80     # Quán ăn 50 - 500 review
MAX_REVIEWS_SMALL_RESTAURANT = 30   # Quán ăn < 50 review

REQUEST_GAP = (3.5, 6.0)
LONG_REST = (30.0, 60.0)
REST_EVERY_N_PLACES = 15
BLOCK_COOLDOWN = (300.0, 600.0)
BLOCK_MARKERS = (
    "pardon our interruption", "access denied", "please verify you are a human",
    "verify you are a human", "unusual activity", "px-captcha", "captcha-delivery",
    "reference #", "bị từ chối truy cập", "access is temporarily restricted",
)

DATE_LABELS = ("Date of stay:", "Ngày lưu trú:", "Date of experience:")
TRIP_LABELS = ("Trip type:", "Loại chuyến đi:")
WROTE_MARK = ("wrote a review", "đã viết đánh giá", "đã viết một đánh giá")

LANG_MAP = {
    'en': 'English', 'vi': 'Vietnamese', 'es': 'Spanish', 'fr': 'French', 'ja': 'Japanese',
    'ko': 'Korean', 'zh-cn': 'Chinese (Sim.)', 'zh-tw': 'Chinese (Trad.)', 'de': 'German',
    'ru': 'Russian', 'th': 'Thai', 'it': 'Italian', 'id': 'Indonesian', 'nl': 'Dutch'
}


def get_chrome_version():
    for root in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        try:
            key = winreg.OpenKey(root, r"Software\Google\Chrome\BLBeacon")
            ver, _ = winreg.QueryValueEx(key, "version")
            return int(ver.split(".")[0])
        except Exception:
            pass
    return 133


def make_driver():
    ver = get_chrome_version()
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1366,900")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    print(f"-> Khởi tạo Undetected ChromeDriver (Chrome Version: {ver})...")
    driver = uc.Chrome(options=options, version_main=ver)
    driver.set_page_load_timeout(35)
    return driver


def load_json(path, default):
    for p in (path, path + ".bak"):
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                continue
    return default


def save_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        try:
            os.fsync(f.fileno())
        except Exception:
            pass
    if os.path.exists(path):
        try:
            os.replace(path, path + ".bak")
        except Exception:
            pass
    os.replace(tmp, path)


def place_id_from_url(url):
    m = re.search(r"-d(\d+)-", url or "")
    return m.group(1) if m else url


def review_page_url(base_url, offset):
    u = re.sub(r"https?://[^/]+", f"https://{DOMAIN}", base_url).split("?")[0]
    if offset <= 0:
        return u
    return u.replace("-Reviews-", f"-Reviews-or{offset}-", 1)


def get_rating(card):
    for svg in card.find_all("svg"):
        t = svg.find("title")
        if t:
            m = re.search(r"(\d(?:[.,]\d)?)\s*(?:of|trên|/)\s*5", t.get_text())
            if m:
                return float(m.group(1).replace(",", "."))
    span = card.find("span", class_=re.compile(r"bubble_(\d+)"))
    if span:
        m = re.search(r"bubble_(\d+)", " ".join(span.get("class", [])))
        if m:
            return float(m.group(1)) / 10.0
    el = card.find(attrs={"aria-label": re.compile(r"(of 5|trên 5)")})
    if el:
        m = re.search(r"(\d(?:[.,]\d)?)", el["aria-label"])
        if m:
            return float(m.group(1).replace(",", "."))
    return 4.0


def _sibling_text(info):
    sib = info.find_next_sibling("span")
    return sib.get_text(strip=True) if sib else ""


def parse_reviews(soup, place_url):
    out = []
    cards = soup.find_all("div", attrs={"data-test-target": re.compile(r".*_CC_CARD")})
    if not cards:
        cards = soup.find_all("div", attrs={"data-reviewid": True})
    if not cards:
        for title_el in soup.find_all(attrs={"data-test-target": "review-title"}):
            p = title_el.parent
            while p and p.name != 'body':
                if p.find(attrs={"data-test-target": "review-body"}) or p.find("span", class_="JguWG") or p.find(href=re.compile(r"/Profile/")):
                    if p not in cards:
                        cards.append(p)
                    break
                p = p.parent

    for card in cards:
        visit_date, trip_type = "", ""
        for info in card.find_all("div", class_=re.compile(r"F_")):
            txt = info.get_text()
            if any(lb in txt for lb in DATE_LABELS):
                visit_date = _sibling_text(info) or visit_date
            elif any(lb in txt for lb in TRIP_LABELS):
                trip_type = _sibling_text(info) or trip_type

        if not visit_date:
            for el in card.find_all(["div", "span"]):
                txt = el.get_text(strip=True)
                if "•" in txt and len(txt) < 40 and "Read more" not in txt and "Đọc thêm" not in txt:
                    parts = [pt.strip() for pt in txt.split("•")]
                    if len(parts) >= 1:
                        visit_date = parts[0]
                    if len(parts) >= 2:
                        trip_type = parts[1]
                    break

        reviewer_url, title, comment = "", "", ""
        prof = card.find("a", href=re.compile(r"/Profile/"))
        if prof:
            reviewer_url = f"https://{DOMAIN}" + prof["href"]

        t_el = card.find(attrs={"data-test-target": "review-title"})
        if t_el:
            title = t_el.get_text(strip=True)

        cspan = (card.find("span", class_="JguWG") or 
                 card.find(attrs={"data-test-target": "review-body"}) or 
                 card.find("span", class_="yCepI"))
        if cspan:
            comment = cspan.get_text(" ", strip=True)

        if not comment and not title:
            continue

        language = "English"
        if comment and detect:
            try:
                code = detect(comment)
                language = LANG_MAP.get(code, code.upper())
            except Exception:
                pass

        out.append({
            "place_url": place_url,
            "reviewer_url": reviewer_url,
            "title": title,
            "comment": comment,
            "reviews_rating": get_rating(card),
            "trip_type": trip_type,
            "visit_date": visit_date,
            "language": language
        })
    return out


def expand_read_more(driver):
    xp = ("//button[.//span[contains(text(),'Read more') or contains(text(),'Đọc thêm')]]"
          " | //span[contains(text(),'Read more') or contains(text(),'Đọc thêm')]")
    try:
        for btn in driver.find_elements(By.XPATH, xp):
            try:
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.15)
            except Exception:
                pass
    except Exception:
        pass


def dismiss_popup(driver):
    try:
        driver.execute_script("""
          const sel = '[role="dialog"], div[class*="modal"], div[class*="Modal"], div[class*="overlay"]';
          document.querySelectorAll(sel).forEach(d => {
            const t = (d.innerText || '');
            if (t.includes('preferred browser language') || t.includes('Visit our English')
                || t.includes('accurate experience')) {
              d.querySelectorAll('button, [aria-label], span').forEach(b => {
                const al = (b.getAttribute('aria-label') || '').toLowerCase();
                const tx = (b.innerText || '').trim();
                if (al.includes('close') || al.includes('đóng') || tx === '×' || tx === '✕' || tx === 'X') {
                  try { b.click(); } catch(e){}
                }
              });
              try { d.remove(); } catch(e){}
            }
          });
        """)
    except Exception:
        pass


def is_blocked(driver):
    try:
        title = (driver.title or "").lower()
        src = driver.page_source[:5000].lower()
        return any(m in title or m in src for m in BLOCK_MARKERS)
    except Exception:
        return False


def get_target_quota(item):
    cat = item.get("category", "")
    rev_cnt = item.get("review_count", 0)
    if cat == "attraction":
        return MAX_REVIEWS_TOP_ATTRACTION if rev_cnt >= 1000 else MAX_REVIEWS_NORMAL_ATTRACTION
    else:
        if rev_cnt >= 500:
            return MAX_REVIEWS_TOP_RESTAURANT
        elif rev_cnt >= 100:
            return MAX_REVIEWS_MID_RESTAURANT
        else:
            return min(rev_cnt, MAX_REVIEWS_SMALL_RESTAURANT)


def crawl_place(driver, place, all_reviews, partial):
    purl = place["url"]
    pid = place_id_from_url(purl)
    max_rev = get_target_quota(place)
    
    seen = set()
    have = 0
    for r in all_reviews:
        if r.get("place_url") == purl:
            seen.add((r.get("reviewer_url"), r.get("title"), r.get("comment", "")[:50]))
            have += 1

    if have >= max_rev:
        return have, False

    offset = int(partial.get(pid, 0))
    step = 10
    saw_block = False

    while have < max_rev:
        target_url = review_page_url(purl, offset)
        try:
            driver.get(target_url)
        except Exception as e:
            print(f"   [Lỗi tải]: {e}")
            break

        time.sleep(random.uniform(*REQUEST_GAP))
        dismiss_popup(driver)

        if is_blocked(driver):
            saw_block = True
            print("   [!] BỊ CHẶN: Phát hiện trang kiểm tra captcha/Cloudflare!")
            break

        driver.execute_script("window.scrollBy(0, 700);")
        time.sleep(1.0)
        expand_read_more(driver)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        page_revs = parse_reviews(soup, purl)

        if not page_revs:
            # Không còn review ở offset này
            break

        new_count = 0
        for r in page_revs:
            key = (r.get("reviewer_url"), r.get("title"), r.get("comment", "")[:50])
            if key not in seen:
                seen.add(key)
                all_reviews.append(r)
                new_count += 1
                have += 1
                if have >= max_rev:
                    break

        if new_count == 0:
            # Đã lặp lại toàn bộ review
            break

        offset += step
        partial[pid] = offset
        save_json(OUTPUT_FILE, all_reviews)
        save_json(PARTIAL_FILE, partial)

    return have, saw_block


def main():
    print("=" * 75)
    print("CHƯƠNG TRÌNH THU THẬP BỔ SUNG REVIEW CỐ ĐÔ HUẾ (CASE STUDY HUET)")
    print("=" * 75)

    if not os.path.exists(TARGETS_FILE):
        print(f"[LỖI] Không tìm thấy file mục tiêu: {TARGETS_FILE}")
        return

    with open(TARGETS_FILE, "r", encoding="utf-8") as f:
        targets_data = json.load(f)

    attractions = targets_data.get("attractions", [])
    restaurants = targets_data.get("restaurants", [])
    
    # Ưu tiên cào 29 điểm tham quan trước, sau đó tới các nhà hàng
    queue = attractions + restaurants
    print(f"Tổng số địa điểm cần cào: {len(queue)} (29 Attractions + {len(restaurants)} Restaurants)")

    all_reviews = load_json(OUTPUT_FILE, [])
    done_places = set(load_json(PROGRESS_FILE, []))
    partial = load_json(PARTIAL_FILE, {})

    print(f"-> Đã có sẵn: {len(all_reviews):,} review từ {len(done_places)} địa điểm đã hoàn thành.")

    driver = make_driver()

    try:
        processed = 0
        for idx, place in enumerate(queue, 1):
            purl = place["url"]
            pid = place_id_from_url(purl)
            name = place["name"]
            cat = place["category"]
            quota = get_target_quota(place)

            if pid in done_places or purl in done_places:
                continue

            print(f"\n[{idx}/{len(queue)}] [{cat.upper()}] {name} (Mục tiêu: {quota} reviews)")

            have, blocked = crawl_place(driver, place, all_reviews, partial)

            if blocked:
                print(f"   [!] Nghỉ chống chặn {BLOCK_COOLDOWN[0]/60:.1f} phút...")
                time.sleep(random.uniform(*BLOCK_COOLDOWN))
                driver.quit()
                driver = make_driver()
                have, blocked = crawl_place(driver, place, all_reviews, partial)

            # Hoàn thành địa điểm này
            partial.pop(pid, None)
            done_places.add(pid)
            save_json(PROGRESS_FILE, list(done_places))
            save_json(PARTIAL_FILE, partial)
            save_json(OUTPUT_FILE, all_reviews)

            print(f"   -> Hoàn thành {name}: đã lấy {have} reviews. (Tổng toàn bộ Huế: {len(all_reviews):,})")

            processed += 1
            if processed % REST_EVERY_N_PLACES == 0:
                rest_time = random.uniform(*LONG_REST)
                print(f"\n   ... Nghỉ giải lao chống bot {rest_time:.0f} giây ...")
                time.sleep(rest_time)

    except KeyboardInterrupt:
        print("\n[DỪNG THỦ CÔNG] Đang lưu tiến độ an toàn...")
    finally:
        save_json(OUTPUT_FILE, all_reviews)
        save_json(PROGRESS_FILE, list(done_places))
        save_json(PARTIAL_FILE, partial)
        try:
            driver.quit()
        except Exception:
            pass
        print(f"\n✅ ĐÃ HOÀN TẤT PHIÊN CRAWL: Tổng cộng {len(all_reviews):,} review đã được lưu tại {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
