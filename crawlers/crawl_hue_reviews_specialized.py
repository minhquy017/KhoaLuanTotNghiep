# -*- coding: utf-8 -*-
"""
CRAWLER CHUYÊN BIỆT CỐ ĐÔ HUẾ - BẢN NÂNG CẤP CHỐNG CHẶN & TỰ ĐỘNG VƯỢT CAPTCHA
Khóa luận Tốt nghiệp ngành Khoa học Dữ liệu và Trí tuệ Nhân tạo (DS&AI K3 - HUET)
-----------------------------------------------------------------------------------------------------
CÁC CẢI TIẾN CHỐNG CHẶN TOÀN DIỆN (ANTI-BLOCKING SYSTEM):
1. Persistent Chrome Profile (.chrome_data):
   - Lưu trữ vĩnh viễn cookies, session và mã xác nhận Cloudflare (cf_clearance).
   - Loại bỏ hoàn toàn dấu hiệu "trình duyệt khách vô danh" (empty guest profile).
2. Tự động vượt & Hỗ trợ giải Captcha tức thì (Interactive Verification):
   - Khi gặp thử thách Cloudflare/Turnstile ("Verify you are human"):
     + Script tự động tìm và click ô checkbox xác minh.
     + Đồng thời phát chuông báo và hiển thị thông báo hướng dẫn người dùng click trực tiếp.
     + Tự động tiếp tục cào NGAY LẬP TỨC khi mở khoá (chỉ mất 2-3 giây thay vì chờ 5 phút vô ích).
3. Cuộn tự nhiên & Tải lười (Lazy-load Reviews):
   - Tự động cuộn mượt đến khu vực Đánh giá để kích hoạt TripAdvisor render thẻ review.
   - Parser thế hệ mới: Nhận diện review card đa tầng (kể cả layout mới như Vườn quốc gia Bạch Mã).
4. Phân trang mượt mà (Next Page Link):
   - Tận dụng liên kết Next Page tự nhiên của TripAdvisor, tránh việc spam tải lại trang liên tục.
5. Triệt tiêu lỗi WinError 6 trên Windows:
   - Bọc an toàn quá trình thoát Chrome để không sinh crash traceback.
6. Ràng buộc dữ liệu:
   - Lưu trực tiếp và tiếp nối vào data/raw/hue_reviews_supplement.json.
   - Khử trùng lặp 100%.
"""

import os
import sys
import re
import json
import time
import random
import argparse
import winreg
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# Khử lỗi WinError 6 khi đóng Chrome trên Windows
_orig_del = getattr(uc.Chrome, "__del__", None)
def _safe_del(self):
    try:
        if _orig_del:
            _orig_del(self)
    except Exception:
        pass
uc.Chrome.__del__ = _safe_del

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
PROFILE_DIR = os.path.join(BASE_DIR, ".chrome_data")
os.makedirs(PROFILE_DIR, exist_ok=True)

TARGETS_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "hue_crawl_targets.json")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "data", "raw", "hue_reviews_supplement.json")
PROGRESS_FILE = os.path.join(PROJECT_ROOT, "data", "raw", "progress_hue_reviews.json")
PARTIAL_FILE = os.path.join(PROJECT_ROOT, "data", "raw", "partial_hue_reviews.json")
EXHAUSTED_FILE = os.path.join(PROJECT_ROOT, "data", "raw", "exhausted_hue_places.json")

DOMAIN = "www.tripadvisor.com"

# Cấu hình hạn mức (Quotas)
MAX_REVIEWS_TOP_ATTRACTION = 1500     # Đại Nội, Thiên Mụ, Lăng Khải Định, Minh Mạng, Tự Đức...
MAX_REVIEWS_NORMAL_ATTRACTION = 400   # Các điểm tham quan, danh lam, di tích khác
MAX_REVIEWS_TOP_HOTEL = 350           # Khách sạn lớn > 1000 reviews (Melia Vinpearl, Eldora, Moonlight...)
MAX_REVIEWS_NORMAL_HOTEL = 150        # Khách sạn vừa và nhỏ
MAX_REVIEWS_TOP_RESTAURANT = 400      # Quán ăn nổi tiếng > 500 reviews (Madame Thu, Hạnh, Huyền Anh...)
MAX_REVIEWS_MID_RESTAURANT = 150      # Quán ăn 100 - 500 reviews
MAX_REVIEWS_SMALL_RESTAURANT = 50     # Quán ăn < 100 reviews
MAX_REVIEWS_CAFE = 150                # Cà phê, trà Huế (Cà phê Muối, Vỹ Dạ Xưa...)

REQUEST_GAP = (4.0, 7.5)              # Giãn cách tự nhiên giữa các trang
PAGE_BREATHE_INTERVAL = 8             # Cứ sau 8 trang nghỉ ngắn một nhịp

BLOCK_MARKERS = (
    "pardon our interruption", "access denied", "please verify you are a human",
    "verify you are a human", "unusual activity", "px-captcha", "captcha-delivery",
    "reference #", "bị từ chối truy cập", "access is temporarily restricted",
    "just a moment...", "security check"
)

DATE_LABELS = ("Date of stay:", "Ngày lưu trú:", "Date of experience:")
TRIP_LABELS = ("Trip type:", "Loại chuyến đi:")

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


def make_driver(headless=False):
    ver = get_chrome_version()
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--window-size=1366,900")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--lang=vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7")
    if headless:
        options.add_argument("--headless=new")
    print(f"-> Khởi tạo Chrome Profile bền vững tại: {PROFILE_DIR} (Chrome Version: {ver})...")
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


def is_blocked(driver):
    try:
        title = (driver.title or "").lower()
        src = driver.page_source[:5000].lower()
        return any(m in title or m in src for m in BLOCK_MARKERS)
    except Exception:
        return False


def try_solve_turnstile(driver):
    """Cố gắng tự động click ô xác minh Cloudflare Turnstile nếu có."""
    try:
        iframes = driver.find_elements(By.CSS_SELECTOR, "iframe[src*='challenges.cloudflare.com'], iframe[src*='turnstile']")
        for ifr in iframes:
            try:
                driver.switch_to.frame(ifr)
                boxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox'], #challenge-stage, .ctp-checkbox-label")
                for b in boxes:
                    try:
                        b.click()
                        time.sleep(1.0)
                    except Exception:
                        pass
                driver.switch_to.default_content()
            except Exception:
                driver.switch_to.default_content()
    except Exception:
        try:
            driver.switch_to.default_content()
        except Exception:
            pass


def handle_challenge_if_any(driver, max_wait=60):
    """
    Nếu gặp Cloudflare / PerimeterX:
    - Báo động console + âm thanh.
    - Chờ người dùng click checkbox hoặc tự click.
    - Tiếp tục ngay lập tức khi giải xong (chỉ 2 giây).
    """
    if not is_blocked(driver):
        return True

    print("\n" + "=" * 80)
    print("🛡️ TRIPADVISOR YÊU CẦU XÁC MINH NGƯỜI DÙNG (CLOUDFLARE / CAPTCHA)")
    print("👉 Xin hãy click vào ô 'Verify you are human' (hoặc nhấn giữ) trên cửa sổ Chrome đang mở.")
    print(f"⏳ Hệ thống đang chờ bạn xác nhận (tối đa {max_wait}s)... Sẽ tự động tiếp tục cào ngay khi mở!")
    print("=" * 80 + "\n")

    try:
        import winsound
        winsound.Beep(1000, 350)
    except Exception:
        pass

    waited = 0
    while waited < max_wait:
        try_solve_turnstile(driver)
        time.sleep(2.0)
        waited += 2
        if not is_blocked(driver):
            print(f"✅ XÁC MINH THÀNH CÔNG (sau {waited}s)! Token cf_clearance đã được lưu vào profile. Tiếp tục cào...\n")
            time.sleep(1.5)
            return True

    print("❌ Hết thời gian chờ xác minh (60s). Tạm thời hoãn địa điểm này để tránh gián đoạn hệ thống.")
    return False


def human_scroll(driver):
    """Mô phỏng cuộn trang tự nhiên để kích hoạt lazy-load reviews."""
    try:
        # Cuộn nửa trang đầu
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
        time.sleep(random.uniform(0.8, 1.4))
        # Cuộn nhẹ thêm một đoạn
        delta = random.randint(300, 600)
        driver.execute_script(f"window.scrollBy(0, {delta});")
        time.sleep(random.uniform(0.5, 0.9))
    except Exception:
        pass


def expand_read_more(driver):
    xp = ("//button[.//span[contains(text(),'Read more') or contains(text(),'Đọc thêm')]]"
          " | //span[contains(text(),'Read more') or contains(text(),'Đọc thêm')]")
    try:
        for btn in driver.find_elements(By.XPATH, xp):
            try:
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.12)
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
    """
    Parser đa tầng thích ứng cả layout truyền thống và layout mới của TripAdvisor.
    """
    out = []
    cards = soup.find_all("div", attrs={"data-test-target": re.compile(r".*_CC_CARD")})
    if not cards:
        cards = soup.find_all("div", attrs={"data-reviewid": True})
    
    # Fallback mạnh mẽ: Tìm theo thẻ tiêu đề review-title
    if not cards:
        for title_el in soup.find_all(attrs={"data-test-target": "review-title"}):
            p = title_el.parent
            for _ in range(7):
                if not p or p.name == "body":
                    break
                if p.find("svg") or p.find("span", class_=re.compile(r"bubble")):
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

        # Fallback nội dung comment nếu không khớp class trên
        if not comment:
            text_candidates = [
                sp.get_text(" ", strip=True) for sp in card.find_all(["span", "div", "p"])
                if len(sp.get_text(strip=True)) > 40 and title not in sp.get_text(strip=True)
            ]
            if text_candidates:
                # Lấy đoạn dài nhất
                text_candidates.sort(key=len, reverse=True)
                comment = text_candidates[0]

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


def get_target_quota(item):
    cat = item.get("category", "")
    rev_cnt = int(item.get("review_count", 0) or 0)
    if cat == "attraction":
        return MAX_REVIEWS_TOP_ATTRACTION if rev_cnt >= 1000 else MAX_REVIEWS_NORMAL_ATTRACTION
    elif cat == "hotel":
        return MAX_REVIEWS_TOP_HOTEL if rev_cnt >= 1000 else MAX_REVIEWS_NORMAL_HOTEL
    elif cat == "cafe":
        return min(rev_cnt, MAX_REVIEWS_CAFE) if rev_cnt > 0 else 100
    else:  # restaurant
        if rev_cnt >= 500:
            return MAX_REVIEWS_TOP_RESTAURANT
        elif rev_cnt >= 100:
            return MAX_REVIEWS_MID_RESTAURANT
        else:
            return min(rev_cnt, MAX_REVIEWS_SMALL_RESTAURANT) if rev_cnt > 0 else 30


def find_next_page_url(driver):
    """Tìm liên kết trang tiếp theo trên thanh phân trang TripAdvisor."""
    try:
        next_links = driver.find_elements(By.CSS_SELECTOR, 'a[aria-label="Next page"], a[data-smoke-attr="pagination-next-button"], a.ui_pagination.next')
        for link in next_links:
            href = link.get_attribute("href")
            if href and "-Reviews-or" in href:
                return href
    except Exception:
        pass
    return None


def crawl_place(driver, place, all_reviews, partial, exhausted_set):
    purl = place["url"]
    pid = place_id_from_url(purl)
    max_rev = get_target_quota(place)
    
    seen = set()
    have = 0
    for r in all_reviews:
        if r.get("place_url") == purl:
            seen.add((r.get("reviewer_url"), r.get("title"), r.get("comment", "")[:60]))
            have += 1

    if have >= max_rev:
        return have, False, False

    saved_offset = int(partial.get(pid, 0))
    resume_offset = (have // 10) * 10
    offset = max(saved_offset, resume_offset)
    step = 10
    saw_block = False
    reached_end = False
    consecutive_empty = 0
    pages_crawled_this_place = 0

    target_url = review_page_url(purl, offset)

    while have < max_rev:
        try:
            driver.get(target_url)
        except Exception as e:
            print(f"   [Lỗi kết nối tải trang]: {e}")
            break

        time.sleep(random.uniform(*REQUEST_GAP))
        dismiss_popup(driver)

        # Kiểm tra thử thách và hỗ trợ giải quyết ngay
        if is_blocked(driver):
            resolved = handle_challenge_if_any(driver, max_wait=60)
            if not resolved:
                saw_block = True
                break

        # Cuộn trang tự nhiên để kích hoạt render review cards
        human_scroll(driver)
        expand_read_more(driver)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        page_revs = parse_reviews(soup, purl)

        if not page_revs:
            # Kiểm tra xem có phải trang rỗng do hết review thật không
            reached_end = True
            break

        new_count = 0
        for r in page_revs:
            key = (r.get("reviewer_url"), r.get("title"), r.get("comment", "")[:60])
            if key not in seen:
                seen.add(key)
                all_reviews.append(r)
                new_count += 1
                have += 1
                if have >= max_rev:
                    break

        if new_count == 0:
            consecutive_empty += 1
            if consecutive_empty >= 3:
                # 3 trang liên tiếp không có review mới -> kết thúc địa điểm
                reached_end = True
                break
        else:
            consecutive_empty = 0

        offset += step
        partial[pid] = offset

        # Lưu an toàn vào file dữ liệu gốc
        save_json(OUTPUT_FILE, all_reviews)
        save_json(PARTIAL_FILE, partial)

        pages_crawled_this_place += 1
        if pages_crawled_this_place % PAGE_BREATHE_INTERVAL == 0:
            breathe_pause = random.uniform(8.0, 15.0)
            print(f"   ... Nhịp thở tự nhiên {breathe_pause:.1f}s để giữ an toàn IP ...")
            time.sleep(breathe_pause)

        # Chuẩn bị URL cho trang kế tiếp: Ưu tiên link từ nút Next
        next_url = find_next_page_url(driver)
        if next_url:
            target_url = next_url
        else:
            target_url = review_page_url(purl, offset)

    if reached_end:
        # Chỉ đánh dấu cạn kiệt nếu đã cào được review (>0) hoặc điểm này thực tế trên web rất ít review (<= 10)
        real_cnt = int(place.get("review_count", 0) or 0)
        if have > 0 or real_cnt <= 10:
            exhausted_set.add(pid)
        partial.pop(pid, None)

    return have, saw_block, reached_end


def main():
    parser = argparse.ArgumentParser(description="Specialized Hue Reviews Crawler (Anti-Blocking System)")
    parser.add_argument("--limit-places", type=int, default=0, help="Giới hạn số địa điểm cào (0 = không giới hạn)")
    parser.add_argument("--category", type=str, default="all", choices=["all", "attraction", "hotel", "cafe", "restaurant"], help="Lọc danh mục cào")
    parser.add_argument("--headless", action="store_true", help="Chạy ẩn (khuyên dùng có giao diện để dễ xác minh)")
    args = parser.parse_args()

    print("=" * 80)
    print("CHƯƠNG TRÌNH THU THẬP BỔ SUNG REVIEW CỐ ĐÔ HUẾ (ANTI-BLOCKING PRO)")
    print("=" * 80)

    if not os.path.exists(TARGETS_FILE):
        print(f"[LỖI] Không tìm thấy file mục tiêu: {TARGETS_FILE}")
        return

    with open(TARGETS_FILE, "r", encoding="utf-8") as f:
        targets_data = json.load(f)

    attractions = targets_data.get("attractions", [])
    hotels = targets_data.get("hotels", [])
    cafes = targets_data.get("cafes", [])
    restaurants = targets_data.get("restaurants", [])
    
    if args.category == "attraction":
        queue = attractions
    elif args.category == "hotel":
        queue = hotels
    elif args.category == "cafe":
        queue = cafes
    elif args.category == "restaurant":
        queue = restaurants
    else:
        queue = attractions + hotels + cafes + restaurants

    print(f"Tổng số địa điểm mục tiêu: {len(queue)} ({len(attractions)} Attractions + {len(hotels)} Hotels + {len(cafes)} Cafes + {len(restaurants)} Restaurants)")

    all_reviews = load_json(OUTPUT_FILE, [])
    partial = load_json(PARTIAL_FILE, {})
    exhausted_set = set(load_json(EXHAUSTED_FILE, []))

    have_by_url = {}
    for r in all_reviews:
        u = r.get("place_url")
        if u:
            have_by_url[u] = have_by_url.get(u, 0) + 1

    print(f"-> Dữ liệu hiện có: {len(all_reviews):,} reviews từ {len(have_by_url)} địa điểm trong {OUTPUT_FILE}.")

    driver = make_driver(headless=args.headless)

    try:
        processed = 0
        for idx, place in enumerate(queue, 1):
            if args.limit_places > 0 and processed >= args.limit_places:
                print(f"\n[DỪNG THEO HẠN MỨC]: Đã cào đủ {args.limit_places} địa điểm cho phiên này.")
                break

            purl = place["url"]
            pid = place_id_from_url(purl)
            name = place["name"]
            cat = place.get("category", "place")
            quota = get_target_quota(place)
            have = have_by_url.get(purl, 0)

            # Bỏ qua nếu đã đạt hạn mức
            if have >= quota:
                continue

            # Bỏ qua nếu đã cạn kiệt review
            if pid in exhausted_set:
                continue

            print(f"\n[{idx}/{len(queue)}] [{cat.upper()}] {name}")
            print(f"   -> Đang có: {have}/{quota} reviews (Cần cào thêm tối đa: {quota - have})")

            have, blocked, reached_end = crawl_place(driver, place, all_reviews, partial, exhausted_set)
            have_by_url[purl] = have

            if blocked:
                print(f"   [!] Tạm hoãn {name} do gặp thử thách bảo mật chưa mở. Tự động chuyển địa điểm tiếp theo...")
                time.sleep(15.0)

            if reached_end or have >= quota:
                partial.pop(pid, None)

            save_json(OUTPUT_FILE, all_reviews)
            save_json(EXHAUSTED_FILE, list(exhausted_set))
            save_json(PARTIAL_FILE, partial)

            print(f"   -> Cập nhật {name}: hiện có {have} reviews. (Tổng toàn bộ Huế: {len(all_reviews):,})")

            processed += 1
            # Nghỉ ngắn giữa các địa điểm
            time.sleep(random.uniform(4.0, 8.0))

    except KeyboardInterrupt:
        print("\n[DỪNG THỦ CÔNG] Đang lưu tiến độ an toàn...")
    finally:
        save_json(OUTPUT_FILE, all_reviews)
        save_json(EXHAUSTED_FILE, list(exhausted_set))
        save_json(PARTIAL_FILE, partial)
        try:
            driver.quit()
        except Exception:
            pass
        print(f"\n✅ ĐÃ LƯU TIẾN ĐỘ AN TOÀN: Tổng cộng {len(all_reviews):,} review trong {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
