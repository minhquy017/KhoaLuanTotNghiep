# -*- coding: utf-8 -*-
"""
Crawl TOÀN BỘ REVIEW cho từng địa điểm ở Việt Nam trên TripAdvisor.

Đầu vào : vietnam_attractions_link.json  (item_url, item_name, number_of_reviews)
Đầu ra  : attraction_reviews.json         (mỗi review theo schema bên dưới)

Điểm chính:
  - Phân trang review bằng '-orN-'; bung 'Read more'; langdetect gán ngôn ngữ.
  - BỎ QUA địa điểm 0 review.
  - CHỐNG CHẶN: phát hiện bị chặn (hotel có review mà trang trả 0) -> nghỉ dài,
    mở phiên MỚI (đổi User-Agent), THỬ LẠI ĐÚNG HOTEL. KHÔNG mark done khi bị chặn
    -> không mất review; chạy lại sẽ resume.
  - Hỗ trợ giao diện + review TIẾNG VIỆT: đổi DOMAIN = "www.tripadvisor.com.vn"
    (parser nhận cả nhãn tiếng Anh lẫn tiếng Việt).
  - Checkpoint: ghi attraction_reviews.json + progress_attraction_reviews.json sau MỖI địa điểm.

Chạy:  python crawl_attraction_reviews.py
Cài nếu thiếu: pip install undetected-chromedriver beautifulsoup4 langdetect
"""

import re
import os
import json
import time
import random
import subprocess

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

try:
    from langdetect import detect
except Exception:
    detect = None

# --- Cấu hình ---
INPUT_FILE = "vietnam_attractions_link.json"

# ==================================================================
#  CHIA VIỆC (CHIA ĐỀU CHO TẤT CẢ MỌI NGƯỜI)
#  >>> MỖI MÁY CHỈ ĐỔI DUY NHẤT DÒNG "WORKER_ID" BÊN DƯỚI <<<
#        Người 1 -> WORKER_ID = 0
#        Người 2 -> WORKER_ID = 1
#        Người 3 -> WORKER_ID = 2
#        Người 4 -> WORKER_ID = 3
#  * TẤT CẢ PHẢI DÙNG CHUNG NUM_WORKERS GIỐNG NHAU *
# ==================================================================
NUM_WORKERS = 4      # TỔNG SỐ NGƯỜI CHIA VIỆC
WORKER_ID = 2        # <<< ĐỔI SỐ NÀY: Từ 0 đến NUM_WORKERS - 1

OUTPUT_FILE = f"attraction_reviews_w{WORKER_ID}.json"
PROGRESS_FILE = f"progress_attraction_reviews_w{WORKER_ID}.json"
PARTIAL_FILE = f"progress_attraction_reviews_partial_w{WORKER_ID}.json"   # resume GIỮA hotel
EMPTY_FILE = f"progress_attraction_reviews_empty_w{WORKER_ID}.json"       # hotel THẬT SỰ 0 review

CHROME_MAIN_VERSION = None

# Đổi sang "www.tripadvisor.com.vn" để lấy giao diện + review tiếng Việt.
DOMAIN = "www.tripadvisor.com"
LANG_FILTER = "all"

REVIEW_STEP_FALLBACK = 10
MAX_PAGES_PER_ITEM = 500
PAGE_REST_EVERY = 20            # trong 1 hotel nhiều review: cứ N trang nghỉ ngắn
REST_EVERY_ITEMS = 5
LONG_REST = (60.0, 150.0)
ITEM_GAP = (6.0, 12.0)

# Chống chặn
BLOCK_COOLDOWN = (600.0, 1200.0)   # bị chặn -> nghỉ 10-20 phút rồi mở phiên mới
MAX_BLOCK_RESTARTS = 2
BLOCK_STREAK = 3        # số địa điểm 0-review LIÊN TIẾP -> nghi soft-block (dù không thấy trang chặn)
# Dấu hiệu TRANG CHẶN thật sự (để phân biệt với hotel 0 review bình thường)
BLOCK_MARKERS = (
    "pardon our interruption", "access denied", "please verify you are a human",
    "verify you are a human", "unusual activity", "px-captcha", "captcha-delivery",
    "reference #", "bị từ chối truy cập", "Access is temporarily restricted",
)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
]

# Nhãn song ngữ (Anh + Việt) để parser chạy được trên cả .com và .com.vn
DATE_LABELS = ("Date of stay:", "Ngày lưu trú:")
TRIP_LABELS = ("Trip type:", "Loại chuyến đi:")
WROTE_MARK = ("wrote a review", "đã viết đánh giá", "đã viết một đánh giá")

LANG_MAP = {'en': 'English', 'vi': 'Vietnamese', 'es': 'Spanish', 'fr': 'French', 'ja': 'Japanese',
            'ko': 'Korean', 'zh-cn': 'Chinese (Sim.)', 'zh-tw': 'Chinese (Trad.)', 'de': 'German',
            'ru': 'Russian', 'th': 'Thai', 'it': 'Italian', 'id': 'Indonesian', 'nl': 'Dutch',
            'pt': 'Portuguese', 'ar': 'Arabic', 'hu': 'Hungarian', 'pl': 'Polish', 'sv': 'Swedish',
            'tr': 'Turkish'}


# ---------------------------------------------------------------- driver
def detect_chrome_major():
    if CHROME_MAIN_VERSION:
        return CHROME_MAIN_VERSION
    try:
        out = subprocess.check_output(
            r'reg query "HKCU\Software\Google\Chrome\BLBeacon" /v version',
            shell=True, stderr=subprocess.DEVNULL).decode(errors="ignore")
        m = re.search(r"(\d+)\.\d+\.\d+\.\d+", out)
        if m:
            return int(m.group(1))
    except Exception:
        pass
    return None


def make_driver(major, ua=None):
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1366,1068")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    if ua:
        options.add_argument(f"--user-agent={ua}")
    # Dùng .com.vn -> đặt ngôn ngữ trình duyệt tiếng Việt để KHÔNG bị popup 'đổi sang English'
    if DOMAIN.endswith(".vn"):
        options.add_argument("--lang=vi-VN")
        try:
            options.add_experimental_option("prefs", {"intl.accept_languages": "vi-VN,vi"})
        except Exception:
            pass
    if major:
        return uc.Chrome(options=options, version_main=major)
    return uc.Chrome(options=options)


def warm_up(driver):
    try:
        driver.get(f"https://{DOMAIN}/")
        time.sleep(random.uniform(5.0, 9.0))
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(random.uniform(2.0, 4.0))
    except Exception:
        pass


def random_scroll(driver):
    try:
        for _ in range(random.randint(2, 4)):
            driver.execute_script(f"window.scrollBy(0, {random.randint(400, 800)});")
            time.sleep(random.uniform(0.6, 1.4))
        driver.execute_script("window.scrollBy(0, -200);")
    except Exception:
        pass


def dismiss_lang_popup(driver):
    """Đóng popup 'preferred browser language / Visit our English website' trên .com.vn.
    Bấm nút X hoặc gỡ hẳn modal — KHÔNG bao giờ bấm 'Visit our English website'."""
    try:
        driver.execute_script("""
          let killed = 0;
          const sel = '[role="dialog"], div[class*="modal"], div[class*="Modal"], div[class*="overlay"], div[class*="Overlay"]';
          document.querySelectorAll(sel).forEach(d => {
            const t = (d.innerText || '');
            if (t.includes('preferred browser language') || t.includes('Visit our English')
                || t.includes('accurate experience') || t.includes('English (US) website')) {
              let closed = false;
              d.querySelectorAll('button, [aria-label], svg, span').forEach(b => {
                const al = (b.getAttribute && (b.getAttribute('aria-label') || '') || '').toLowerCase();
                const tx = (b.innerText || '').trim();
                if (al.includes('close') || al.includes('đóng') || tx === '×' || tx === '✕' || tx === 'X') {
                  try { b.click(); closed = true; } catch (e) {}
                }
              });
              if (!closed) { try { d.remove(); } catch (e) {} }
              killed++;
            }
          });
          return killed;
        """)
    except Exception:
        pass


# ---------------------------------------------------------------- url / parse
def apply_domain(url):
    return re.sub(r"https?://[^/]+", "https://" + DOMAIN, url)


def review_page_url(item_url, offset):
    u = apply_domain(item_url)
    if offset <= 0:
        return u
    return u.replace("-Reviews-", f"-Reviews-or{offset}-", 1)


def get_rating(card):
    for svg in card.find_all("svg"):
        t = svg.find("title")
        if t:
            m = re.search(r"(\d(?:[.,]\d)?)\s*(?:of|trên|/)\s*5", t.get_text())
            if m:
                return int(round(float(m.group(1).replace(",", "."))))
    span = card.find("span", class_=re.compile(r"bubble_(\d+)"))
    if span:
        m = re.search(r"bubble_(\d+)", " ".join(span.get("class", [])))
        if m:
            return int(round(int(m.group(1)) / 10))
    el = card.find(attrs={"aria-label": re.compile(r"(of 5|trên 5)")})
    if el:
        m = re.search(r"(\d(?:[.,]\d)?)", el["aria-label"])
        if m:
            return int(round(float(m.group(1).replace(",", "."))))
    return 0


def _sibling_text(info):
    sib = info.find_next_sibling("span")
    return sib.get_text(strip=True) if sib else ""


def parse_reviews(soup, item_url):
    out = []
    cards = soup.find_all("div", attrs={"data-test-target": re.compile(r".*_CC_CARD")})
    if not cards:
        cards = soup.find_all("div", attrs={"data-reviewid": True})
    if not cards:
        cards = soup.find_all(attrs={"data-automation": "reviewCard"})
    
    # Fallback tự động nội suy nhóm thẻ review nếu TripAdvisor giấu class/ID
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
        
        # Thử kiểu 1: tìm theo class F_
        for info in card.find_all("div", class_=re.compile(r"F_")):
            txt = info.get_text()
            if any(lb in txt for lb in DATE_LABELS):
                visit_date = _sibling_text(info) or visit_date
            elif any(lb in txt for lb in TRIP_LABELS):
                trip_type = _sibling_text(info) or trip_type

        # Thử kiểu 2: Nội dung gộp dạng "Aug 2026 • Friends" (giao diện mới)
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

        # Thử kiểu 3: "wrote a review"
        if not visit_date:
            w = card.find("div", class_=re.compile(r"ZRBpD"))
            if w:
                wt = w.get_text()
                for mark in WROTE_MARK:
                    if mark in wt:
                        visit_date = wt.split(mark)[-1].strip()
                        break

        reviewer_url, title, comment = "", "", ""
        prof = card.find("a", href=re.compile(r"/Profile/"))
        if prof:
            reviewer_url = f"https://{DOMAIN}" + prof["href"]
            
        t_el = card.find(attrs={"data-test-target": "review-title"})
        if not t_el:
            t_el = card.find("a", href=re.compile(r"/ShowUserReviews-"))
            
        if t_el:
            title = t_el.get_text(strip=True)
            
        cspan = card.find("span", class_="JguWG") or card.find(attrs={"data-test-target": "review-body"}) or card.find("span", class_="yCepI")
        if cspan:
            comment = cspan.get_text(" ", strip=True)

        language = "Unknown"
        if comment and detect:
            try:
                code = detect(comment)
                language = LANG_MAP.get(code, code.upper())
            except Exception:
                pass

        out.append({
            "url": apply_domain(item_url),
            "reviewer_url": reviewer_url,
            "title": title,
            "comment": comment,
            "reviews_rating": get_rating(card),
            "trip_type": trip_type,
            "visit_date": visit_date,
            "language": language,
        })
    return out
def expand_read_more(driver):
    xp = ("//button[.//span[contains(text(),'Read more') or contains(text(),'Đọc thêm')]]"
          " | //span[contains(text(),'Read more') or contains(text(),'Đọc thêm')]")
    try:
        for btn in driver.find_elements(By.XPATH, xp):
            try:
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.2)
            except Exception:
                pass
    except Exception:
        pass


def apply_language_filter(driver):
    """Chọn bộ lọc ngôn ngữ: 'all' = tất cả, 'vi' = chỉ tiếng Việt."""
    try:
        fb = WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.XPATH,
              "//button[.//span[contains(text(),'Filter') or contains(text(),'Bộ lọc')]]")))
        driver.execute_script("arguments[0].click();", fb)
        time.sleep(random.uniform(1.2, 2.2))
        lang = WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.XPATH,
              "//button[contains(@aria-label,'Language') or contains(@aria-label,'Ngôn ngữ')]")))
        driver.execute_script("arguments[0].click();", lang)
        time.sleep(random.uniform(1.0, 1.8))

        if LANG_FILTER == "vi":
            opt = WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH,
                  "//label[.//text()[contains(.,'Tiếng Việt') or contains(.,'Vietnamese')]]"
                  " | //span[contains(text(),'Tiếng Việt') or contains(text(),'Vietnamese')]")))
        else:
            opt = WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH,
                  "//span[@data-automation='ugcLanguageFilterOption_0']")))
        driver.execute_script("arguments[0].click();", opt)
        time.sleep(random.uniform(1.0, 1.5))

        ap = WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.XPATH,
              "//button[contains(.,'Apply') or contains(.,'Áp dụng')]")))
        driver.execute_script("arguments[0].click();", ap)
        time.sleep(random.uniform(3.0, 5.0))
    except Exception:
        pass


# ---------------------------------------------------------------- io
def load_json(path, default):
    # Đọc AN TOÀN: nếu file chính lỗi (đọc dở/hỏng) -> thử bản .bak trước khi bỏ cuộc,
    # tránh việc coi là rỗng rồi ghi đè làm MẤT dữ liệu.
    for p in (path, path + ".bak"):
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                continue
    return default


def save_json(path, data):
    # Ghi AN TOÀN (atomic): ghi ra file tạm rồi đổi tên; giữ bản trước làm .bak.
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
            os.replace(path, path + ".bak")   # bản tốt trước đó -> .bak
        except Exception:
            pass
    os.replace(tmp, path)


def item_id(url):
    m = re.search(r"(d\d+)", url or "")
    return m.group(1) if m else None


def page_blocked(driver):
    """True nếu trang hiện tại là TRANG CHẶN thật (không phải hotel 0 review)."""
    try:
        title = (driver.title or "").lower()
        # chỉ soi đầu HTML cho nhanh + tránh false positive từ script cuối trang
        src = driver.page_source[:6000].lower()
    except Exception:
        return False
    return any(m in title or m in src for m in BLOCK_MARKERS)


# ---------------------------------------------------------------- crawl 1 hotel
def crawl_item(driver, item_url, nrev, all_reviews, partial):
    """Ghi review THẲNG vào all_reviews + lưu sau MỖI trang (resume giữa địa điểm).

    Trả blocked=True nếu nghi bị chặn (hotel có review mà tổng lấy được vẫn = 0).
    """
    hid = item_id(item_url)

    # Nạp lại 'seen' + số review đã có của hotel này (để resume, tránh trùng)
    seen = set()
    have = 0
    for r in all_reviews:
        if item_id(r.get("url")) == hid:
            seen.add((r["reviewer_url"], r["title"], r["visit_date"], r["comment"][:60]))
            have += 1

    offset = int(partial.get(hid, 0))          # tiếp từ trang dang dở nếu có
    if offset:
        print(f"   (resume giữa địa điểm: đã có {have} review, tiếp từ or{offset})")

    step, empty, saw_block = None, 0, False
    for page in range(MAX_PAGES_PER_ITEM):
        try:
            driver.get(review_page_url(item_url, offset))
        except Exception as e:
            print(f"   Lỗi tải: {str(e).splitlines()[0]}")
            break
        time.sleep(random.uniform(4.0, 7.0))

        dismiss_lang_popup(driver)             # đóng popup 'đổi sang English' trên .com.vn

        if page_blocked(driver):               # TRANG CHẶN thật -> dừng, báo bị chặn
            saw_block = True
            print("   [!] Gặp TRANG CHẶN (Pardon Our Interruption/Access Denied...).")
            break

        if offset == 0 and page == 0:          # chỉ lọc ngôn ngữ ở trang đầu thật sự
            apply_language_filter(driver)
        random_scroll(driver)
        expand_read_more(driver)
        time.sleep(1.0)

        page_reviews = parse_reviews(BeautifulSoup(driver.page_source, "html.parser"), item_url)
        
        # DUMP HTML ĐỂ DEBUG: Nếu không gom được review nào dù trang đầu tiên, lưu lại source code.
        if not page_reviews and offset == 0:
            try:
                with open("failed_page_source.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
            except Exception:
                pass

        if step is None:
            step = len(page_reviews) or REVIEW_STEP_FALLBACK

        new = 0
        for r in page_reviews:
            sig = (r["reviewer_url"], r["title"], r["visit_date"], r["comment"][:60])
            if sig in seen:
                continue
            seen.add(sig)
            all_reviews.append(r)
            new += 1
        have += new
        print(f"   or{offset}: {len(page_reviews)} review, mới {new} (tổng: {have})")

        offset += step
        # CHECKPOINT sau mỗi trang: lưu review + offset đã tới
        partial[hid] = offset
        save_json(OUTPUT_FILE, all_reviews)
        save_json(PARTIAL_FILE, partial)

        if not page_reviews or new == 0:
            empty += 1
            if empty >= 2:
                break
        else:
            empty = 0

        if (page + 1) % PAGE_REST_EVERY == 0:
            time.sleep(random.uniform(20.0, 40.0))   # nghỉ ngắn giữa địa điểm nhiều review

    return have, saw_block


# ---------------------------------------------------------------- main
def main():
    items = load_json(INPUT_FILE, [])
    if not items:
        print(f"Không đọc được {INPUT_FILE}. Dừng.")
        return

    all_reviews = load_json(OUTPUT_FILE, [])
    done = set(load_json(PROGRESS_FILE, []))
    empty = set(load_json(EMPTY_FILE, []))   # địa điểm thật sự 0 review (bỏ qua vĩnh viễn)
    partial = load_json(PARTIAL_FILE, {})   # resume giữa địa điểm: {item_id: offset}
    print(f"Có {len(items)} địa điểm. Đã xong {len(done)}. Review đã có: {len(all_reviews)}. "
          f"Domain: {DOMAIN} | lọc ngôn ngữ: {LANG_FILTER}")
    if partial:
        print(f"-> Có {len(partial)} địa điểm dang dở sẽ được tiếp tục giữa chừng.")

    # Dọn progress HỎNG từ lần chạy cũ: hotel bị đánh 'done' nhưng có review (>0) mà
    # KHÔNG lấy được review nào (do bị chặn) -> gỡ khỏi done để crawl lại.
    urls_with_reviews = {r.get("url") for r in all_reviews}
    nrev_map = {}
    for item in items:
        hu = apply_domain((item.get("item_url") or "").split("?")[0])
        try:
            nrev_map[hu] = int(str(item.get("number_of_reviews", "0")).replace(",", "").strip() or "0")
        except Exception:
            nrev_map[hu] = 0
    removed = 0
    for u in list(done):
        if nrev_map.get(u, 0) > 0 and u not in urls_with_reviews:
            done.discard(u)
            removed += 1
    if removed:
        print(f"-> Gỡ {removed} địa điểm bị đánh done nhầm (0 review do bị chặn) để crawl lại.")
        save_json(PROGRESS_FILE, list(done))

    major = detect_chrome_major()
    print(f"-> Chrome major = {major}" if major else "-> uc tự xử lý version")
    driver = make_driver(major, ua=random.choice(USER_AGENTS))
    warm_up(driver)

    processed = 0
    consecutive_empty = 0        # số địa điểm 0-review LIÊN TIẾP (để phát hiện soft-block)
    def _mine(idx):
        # Chia đều bằng phép chia lấy dư
        return idx % NUM_WORKERS == WORKER_ID

    assigned = sum(1 for k in range(len(items)) if _mine(k))
    print(f"### WORKER {WORKER_ID} -> phụ trách {assigned} địa điểm (ghi ra {OUTPUT_FILE}) ###")
    for i, item in enumerate(items, 1):
        # CHIA VIỆC: mỗi máy chỉ xử lý phần của mình
        if not _mine(i - 1):
            continue
        item_url = (item.get("item_url") or "").split("?")[0]
        if not item_url or "/Attraction_Review-" not in item_url:
            continue
        adu = apply_domain(item_url)
        if adu in done or item_url in done or adu in empty or item_url in empty:
            continue

        try:
            nrev = int(str(item.get("number_of_reviews", "0")).replace(",", "").strip() or "0")
        except Exception:
            nrev = 0
        if nrev <= 0:
            empty.add(adu)
            save_json(EMPTY_FILE, list(empty))
            continue

        name = item.get("item_name", "")
        print(f"\n[{i}/{len(items)}] {name} ({nrev} đánh giá)")

        # crawl_item ghi thẳng vào all_reviews + lưu từng trang (resume giữa địa điểm).
        before = len(all_reviews)
        have, saw_block = crawl_item(driver, item_url, nrev, all_reviews, partial)

        # CHỈ coi là bị chặn khi: gặp TRANG CHẶN thật, HOẶC nhiều hotel 0-review LIÊN TIẾP.
        # -> hotel 0 review bình thường (trang tải OK, không có review) sẽ KHÔNG bị nhầm là chặn.
        def _blocked_now(h, sb):
            return h == 0 and nrev > 0 and (sb or consecutive_empty >= BLOCK_STREAK - 1)

        restarts = 0
        while _blocked_now(have, saw_block) and restarts < MAX_BLOCK_RESTARTS:
            restarts += 1
            cd = random.uniform(*BLOCK_COOLDOWN) * restarts
            reason = "trang chặn" if saw_block else f"{consecutive_empty+1} địa điểm 0-review liên tiếp"
            print(f"   [!] Nghi BỊ CHẶN ({reason}). Nghỉ {cd/60:.1f} phút, mở phiên mới rồi thử lại "
                  f"(lần {restarts}/{MAX_BLOCK_RESTARTS})...")
            try:
                driver.quit()
            except Exception:
                pass
            time.sleep(cd)
            driver = make_driver(major, ua=random.choice(USER_AGENTS))
            warm_up(driver)
            have, saw_block = crawl_item(driver, item_url, nrev, all_reviews, partial)

        # Vẫn gặp TRANG CHẶN thật sau nhiều lần thử -> dừng để resume
        if have == 0 and nrev > 0 and saw_block:
            print("   [!] Vẫn bị chặn sau nhiều lần thử. LƯU tiến độ & DỪNG (chạy lại để resume).")
            save_json(OUTPUT_FILE, all_reviews)
            save_json(PROGRESS_FILE, list(done))
            save_json(PARTIAL_FILE, partial)
            try:    
                driver.quit()
            except Exception:
                pass
            return

        # Tới đây: lấy được review, HOẶC 0 review nhưng KHÔNG phải chặn -> BỎ QUA địa điểm đó.
        partial.pop(item_id(item_url), None)
        if have == 0:
            consecutive_empty += 1
            empty.add(adu)          # địa điểm trống -> ghi vào EMPTY_FILE, KHÔNG re-crawl lần sau
            save_json(EMPTY_FILE, list(empty))
            print(f"   -> {name}: 0 review lấy được (địa điểm trống/không đọc được) -> bỏ qua.")
        else:
            consecutive_empty = 0
            done.add(adu)
            save_json(PROGRESS_FILE, list(done))
            print(f"   -> Xong {name}: +{len(all_reviews) - before} review. TỔNG: {len(all_reviews)}")
        save_json(OUTPUT_FILE, all_reviews)
        save_json(PARTIAL_FILE, partial)

        processed += 1
        if processed % REST_EVERY_ITEMS == 0:
            rest = random.uniform(*LONG_REST)
            print(f"   ... nghỉ {rest:.0f}s ...")
            time.sleep(rest)
        else:
            time.sleep(random.uniform(*ITEM_GAP))

    try:
        driver.quit()
    except Exception:
        pass
    print(f"\nHoàn tất! Tổng {len(all_reviews)} review -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
