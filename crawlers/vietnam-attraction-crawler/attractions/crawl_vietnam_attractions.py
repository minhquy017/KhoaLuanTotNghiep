# -*- coding: utf-8 -*-
"""
Crawl DANH SÁCH địa điểm ở Việt Nam trên TripAdvisor.
Geo: g293921  (Vietnam)

Điểm quan trọng:
  - undetected_chromedriver + BeautifulSoup, tự dò version Chrome.
  - Đóng popup lịch 'Select dates'; KHÔNG bấm 'See all attractions' (làm chuyển trang).
  - Danh sách chính là 'virtualized list' -> VỪA CUỘN VỪA GOM ở mỗi bước.
  - TÊN lấy từ chính URL.
  - Số review lấy từ link '#REVIEWS' ('4.9 of 5 bubbles(3,184)').
  - Chống chặn: warm-up trình duyệt + thử lại khi trang 0 link + nghỉ luân phiên.
  - Checkpoint: ghi vietnam_attractions_link.json sau mỗi trang; dedup theo item_url.

Chạy:  python crawl_vietnam_attractions.py
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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

# --- Cấu hình ---
GEO_ID = "g293921"
SLUG = "Vietnam"
TOTAL_ITEMS = 3300
STEP = 30
OUTPUT_FILE = "vietnam_attractions_link.json"
PROGRESS_FILE = "progress_attractions.json"   # lưu các trang (offset) đã xong -> resume theo trang
START_OFFSET = 0            # bắt đầu từ 1 trang cụ thể
CHROME_MAIN_VERSION = None   # None = tự dò; hoặc đặt cứng

# --- Chống bot detection ---
REST_EVERY = 3                 #    mỗi N trang (đặt nhỏ để đi chậm, ít bị chặn)
LONG_REST = (90.0, 200.0)      # thời gian nghỉ dài (giây)
PAGE_GAP = (10.0, 22.0)        # nghỉ thường giữa các trang (giây)
BLOCK_COOLDOWN = (600.0, 1200.0)   # bị chặn -> nghỉ 10-20 phút rồi mở phiên mới
MAX_BLOCK_RESTARTS = 4         # số lần mở lại trình duyệt khi bị chặn trước khi dừng hẳn

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
]

# --- PROXY ---
# Để trống [] nếu KHÔNG dùng proxy. Nếu có, liệt kê 1 hoặc nhiều proxy -> script sẽ
# XOAY (đổi proxy) mỗi lần mở lại phiên/bị chặn.
# Hỗ trợ 2 kiểu:
#   1) Không cần đăng nhập (hoặc đã whitelist IP trên dashboard nhà cung cấp):
#          "http://host:port"                (ĐƠN GIẢN & ỔN ĐỊNH NHẤT với uc)
#   2) Có user/mật khẩu:
#          "http://user:pass@host:port"      (cần: pip install selenium-wire blinker==1.7.0)
# Với residential rotating: thường chỉ cần 1 gateway "http://user:pass@gate.nhacc.com:7000",
# nhà cung cấp tự đổi IP mỗi request/phiên.

PROXIES = [

    # thêm nhiều dòng nếu có nhiều IP -> script tự xoay mỗi lần mở phiên/bị chặn
]

def pick_proxy():
    return random.choice(PROXIES) if PROXIES else None


# ---------------------------------------------------------------- helpers
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
    for p in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"):
        if os.path.exists(p):
            try:
                out = subprocess.check_output(
                    f'wmic datafile where name="{p.replace(chr(92), chr(92)*2)}" get Version /value',
                    shell=True, stderr=subprocess.DEVNULL).decode(errors="ignore")
                m = re.search(r"(\d+)\.\d+\.\d+\.\d+", out)
                if m:
                    return int(m.group(1))
            except Exception:
                continue
    return None


def make_driver(major, ua=None, proxy=None):
    """Tạo trình duyệt mới. Đổi User-Agent + (tuỳ chọn) dùng PROXY.

    - proxy None            -> không dùng proxy.
    - "http://host:port"    -> proxy không auth: dùng --proxy-server (uc thường).
    - "http://user:pass@h:p" -> proxy có auth: dùng selenium-wire để xử lý đăng nhập.
    """
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1366,1068")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    if ua:
        options.add_argument(f"--user-agent={ua}")

    kw = {"options": options}
    if major:
        kw["version_main"] = major

    if proxy:
        print(f"   -> Dùng proxy: {re.sub(r'//[^@]+@', '//***@', proxy)}")

    if proxy and "@" in proxy:
        # Proxy CÓ auth -> selenium-wire (bắt buộc: pip install selenium-wire blinker==1.7.0)
        import seleniumwire.undetected_chromedriver as swuc
        sw_opts = {"proxy": {"http": proxy, "https": proxy,
                             "no_proxy": "localhost,127.0.0.1"}}
        return swuc.Chrome(seleniumwire_options=sw_opts, **kw)

    if proxy:
        # Proxy KHÔNG auth (hoặc đã whitelist IP) -> đơn giản nhất
        options.add_argument(f"--proxy-server={proxy}")

    return uc.Chrome(**kw)


def check_ip(driver):
    """In IP công khai đang dùng (xác nhận proxy hoạt động). Không lỗi thì thôi."""
    try:
        driver.get("https://api.ipify.org?format=text")
        time.sleep(2.0)
        ip = driver.find_element(By.TAG_NAME, "body").text.strip()
        print(f"   -> IP hiện tại: {ip}")
    except Exception:
        print("   -> Không kiểm tra được IP (bỏ qua).")


def warm_up(driver):
    """Vào trang chủ TripAdvisor để 'làm nóng' phiên, giảm bị chặn."""
    try:
        driver.get("https://www.tripadvisor.com/")
        time.sleep(random.uniform(5.0, 9.0))
        driver.execute_script("window.scrollBy(0, 600);")
        time.sleep(random.uniform(2.0, 4.0))
    except Exception:
        pass


def dismiss_overlays(driver):
    """Đóng popup lịch (Select dates) / đăng nhập nếu che nội dung."""
    for _ in range(2):
        try:
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(0.3)
        except Exception:
            pass
    try:
        h1 = driver.find_elements(By.XPATH, "//h1")
        if h1:
            driver.execute_script("arguments[0].click();", h1[0])
            time.sleep(0.2)
    except Exception:
        pass
    try:
        driver.execute_script("""
            document.querySelectorAll('[role="dialog"],[data-automation*="calendar"],[class*="Calendar"],[class*="datepicker"]').forEach(e=>{
                const t=(e.innerText||'');
                if(t.includes('Select dates')||/August|September|Mon|Tue|Wed/.test(t)){ e.style.display='none'; }
            });
        """)
    except Exception:
        pass


def click_see_all_items(driver):
    """Bấm nút 'See all X hotels' (chỉ cần ở TRANG ĐẦU để bung danh sách 1..30)."""
    xpaths = [
        "//button[contains(normalize-space(.), 'See all') and contains(., 'hotel')]",
        "//a[contains(normalize-space(.), 'See all') and contains(., 'hotel')]",
        "//*[(self::button or self::a or @role='button') and contains(normalize-space(.), 'See all') and contains(., 'hotel')]",
    ]
    for xp in xpaths:
        try:
            btn = WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.XPATH, xp)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            time.sleep(random.uniform(1.0, 2.0))
            driver.execute_script("arguments[0].click();", btn)
            print("   -> Đã bấm 'See all attractions' (bung danh sách đầy đủ)")
            return True
        except Exception:
            continue
    print("   -> Không thấy nút 'See all attractions' (có thể trang đã ở dạng list)")
    return False


def _name_from_url(url):
    """Lấy tên địa điểm từ slug URL: ...-Reviews-<Ten>-<DiaDanh>.html"""
    m = re.search(r"-Reviews-(.+?)\.html", url)
    if not m:
        return None
    name_part = m.group(1).split("-")[0]      # phần trước dấu '-' là tên
    name = name_part.replace("_", " ").strip()
    return name or None


def count_item_links(driver):
    # Toàn quốc: hotel có geo con khác nhau -> đếm MỌI link Attraction_Review, không lọc geo.
    try:
        return driver.execute_script(
            'return document.querySelectorAll(\'a[href*="/Attraction_Review-"]\').length;')
    except Exception:
        return 0


def extract_items_from_soup(soup, geo_id, acc):
    """Gom địa điểm từ 1 snapshot HTML vào acc (dict: d-id -> {num,url,name,reviews}).

    Chỉ lấy các mục CÓ SỐ THỨ TỰ (danh sách chính '1.'..'30.'):
      - Đủ: mọi địa điểm đều xuất hiện đúng 1 lần dưới dạng có số trên trang của nó.
      - Sạch: bỏ địa điểm featured/quảng cáo (không số) -> tránh dính hotel ngoài Huế.
      - KHÔNG lọc theo geo -> không sót địa điểm Huế mà URL dùng geo con (vd Lăng Cô).
    """
    # 1) TÊN + URL (chỉ mục có số thứ tự)
    for a in soup.find_all("a", href=True):
        h = a["href"]
        if "/Attraction_Review-" not in h:
            continue
        raw = a.get_text(" ", strip=True)
        if not raw:
            continue
        mnum = re.match(r"^\s*(\d+)\.", raw)                 # số thứ tự (nếu có)
        # BỎ KIỂM TRA SỐ THỨ TỰ (Vì Nhà hàng/Địa điểm có thể không có số)
        mid = re.search(r"(d\d+)", h)
        if not mid:
            continue
        rec = acc.setdefault(mid.group(1), {})
        if mnum:
            rec["num"] = int(mnum.group(1))
        
        # Chỉ lấy text của link đầu tiên có chữ (thường là tên), 
        # tránh bị ghi đè bởi text của link review nằm phía dưới trong cùng 1 card.
        clean_name = re.sub(r"^\s*\d+\.\s*", "", raw).strip()
        if not rec.get("name"):
            rec["name"] = clean_name
            
        if not rec.get("url"):
            url = h if h.startswith("http") else "https://www.tripadvisor.com" + h
            rec["url"] = url.split("?")[0].split("#")[0]
    # 2) SỐ REVIEW: span[data-automation='bubbleReviewCount'], ghép theo d-id
    #    (chỉ cho các địa điểm đã có trong danh sách chính).
    for a in soup.find_all("a", href=True):
        h = a["href"]
        if "#REVIEWS" not in h:
            continue
        mid = re.search(r"(d\d+)", h)
        if not mid or mid.group(1) not in acc:
            continue
        rec = acc[mid.group(1)]
        if rec.get("reviews"):
            continue
        rv = a.find("span", attrs={"data-automation": "bubbleReviewCount"})
        txt = rv.get_text(" ", strip=True) if rv else a.get_text(" ", strip=True)
        nums = re.findall(r"\(([\d,]+)\)", txt) or re.findall(r"([\d,]+)\s*review", txt, re.I)
        if nums:
            rec["reviews"] = nums[-1].replace(",", "")


def harvest_current_page(driver, geo_id, max_scrolls=150):
    """Cuộn & gom toàn bộ danh sách (chống virtualized list).

    QUAN TRỌNG (fix trang đầu): trang overview (không có 'oa') có nhiều carousel
    ở trên, cuộn qua đó chưa gặp mục đánh số -> KHÔNG được dừng sớm.
    Vì vậy chỉ xét dừng SAU KHI đã cuộn CHẠM ĐÁY trang (đi hết vùng list), rồi
    thêm vài vòng để thẻ cuối kịp mount.
    """
    acc = {}
    last_count, stalls, bottom_hits = 0, 0, 0
    for _ in range(max_scrolls):
        extract_items_from_soup(BeautifulSoup(driver.page_source, "html.parser"), geo_id, acc)

        # cuộn từng đoạn nhỏ để thẻ virtualized kịp mount
        driver.execute_script("window.scrollBy(0, Math.round(window.innerHeight*0.55));")
        time.sleep(random.uniform(0.7, 1.4))
        dismiss_overlays(driver)
        at_bottom = driver.execute_script(
            "return (window.innerHeight + window.pageYOffset) >= (document.body.scrollHeight - 5);")

        if len(acc) > last_count:      # còn gom được địa điểm mới -> chưa dừng
            last_count = len(acc)
            stalls = 0
        else:
            stalls += 1

        if at_bottom:
            bottom_hits += 1

        # CHỈ dừng khi: đã chạm đáy >=2 lần VÀ không còn địa điểm mới >=4 vòng
        if bottom_hits >= 2 and stalls >= 4:
            break
    extract_items_from_soup(BeautifulSoup(driver.page_source, "html.parser"), geo_id, acc)
    return acc


def build_url(geo, slug, offset):
    if offset == 0:
        return f"https://www.tripadvisor.com/Attractions-g{geo}-Activities-{slug}.html"
    return f"https://www.tripadvisor.com/Attractions-g{geo}-Activities-oa{offset}-{slug}.html"


def load_existing():
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                return {h["item_url"]: h for h in json.load(f)}
        except Exception:
            pass
    return {}


def save(unique_items):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(list(unique_items.values()), f, indent=4, ensure_ascii=False)


# ---------------------------------------------------------------- main
def main():
    major = detect_chrome_major()
    print(f"-> Chrome major = {major}" if major else "-> Không dò được version Chrome (uc tự xử lý)")
    driver = make_driver(major, ua=random.choice(USER_AGENTS), proxy=pick_proxy())

    unique_items = load_existing()
    done_pages = set()
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                done_pages = set(json.load(f))
        except Exception:
            pass
    print(f"Đã có sẵn {len(unique_items)} mục; {len(done_pages)} trang đã xong (resume).")

    if PROXIES:
        check_ip(driver)   # xác nhận proxy hoạt động
    warm_up(driver)        # làm nóng phiên trước khi vào danh sách

    cities = [
        {"geo": "293925", "slug": "Ho_Chi_Minh_City"},
        {"geo": "293924", "slug": "Hanoi"},
        {"geo": "298085", "slug": "Da_Nang"},
        {"geo": "298082", "slug": "Hoi_An"},
        {"geo": "293928", "slug": "Nha_Trang"},
        {"geo": "469418", "slug": "Phu_Quoc_Island"},
        {"geo": "293926", "slug": "Hue"},
        {"geo": "293922", "slug": "Da_Lat"},
    ]

    for city in cities:
        geo = city["geo"]
        slug = city["slug"]
        empty_streak = 0
        
        for offset in range(0, 1500, STEP):
            if len(unique_items) >= TOTAL_ITEMS:
                print(f"\\n[HOÀN THÀNH] Đã thu thập đủ {TOTAL_ITEMS} mục tiêu. Dừng script.")
                save(unique_items)
                try: driver.quit()
                except: pass
                return
                
            page_id = f"{geo}_{offset}"
            current_url = build_url(geo, slug, offset)
            
            if page_id in done_pages or offset < START_OFFSET:
                print(f"[Bỏ qua] Đã xong {page_id}")
                continue
            
            print(f"\\n[Đang chạy: {slug} - oa{offset}] {current_url}")
            # --- Tải trang; tự phân biệt LỖI KẾT NỐI/PROXY vs BỊ CHẶN IP ---
            restarts = 0
            while True:
                load_err = None
                try:
                    driver.get(current_url)
                except Exception as e:
                    load_err = str(e).splitlines()[0]

                if not load_err:
                    time.sleep(random.uniform(5.0, 9.0))
                    dismiss_overlays(driver)
                    try:
                        WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, 'a[href*="/Attraction_Review-"]')))
                    except Exception:
                        pass
                    if count_item_links(driver) > 0:
                        break                        # OK -> xử lý trang

                restarts += 1
                if restarts > MAX_BLOCK_RESTARTS:
                    print("   [!] Thử nhiều lần vẫn hỏng. LƯU tiến độ & DỪNG (chạy lại để resume).")
                    save(unique_items)
                    try:
                        driver.quit()
                    except Exception:
                        pass
                    return

                if load_err:
                    # Lỗi kết nối / proxy chết -> đổi proxy NGAY, nghỉ NGẮN
                    print(f"   [!] Lỗi tải trang: {load_err}")
                    print(f"       -> Nghi proxy hỏng. Đổi proxy & mở lại (lần {restarts})...")
                    cd = random.uniform(3.0, 8.0)
                else:
                    # Tải được nhưng 0 link -> nghi CHẶN IP -> nghỉ DÀI + đổi proxy
                    print(f"   [!] 0 link địa điểm (nghi bị chặn IP). Nghỉ dài & đổi proxy "
                          f"(lần {restarts}/{MAX_BLOCK_RESTARTS})...")
                    cd = random.uniform(*BLOCK_COOLDOWN) * restarts

                try:
                    driver.quit()
                except Exception:
                    pass
                time.sleep(cd)
                driver = make_driver(major, ua=random.choice(USER_AGENTS), proxy=pick_proxy())
                warm_up(driver)

            # TRANG ĐẦU (overview) chỉ là bản xem trước -> bấm 'See all' để bung đủ 1..30.
            # Các trang sau (oa30, oa60, ...) đã ở dạng list nên không cần.
            if offset == 0:
                click_see_all_items(driver)
                time.sleep(random.uniform(4.0, 7.0))
                dismiss_overlays(driver)

            # Vừa cuộn vừa gom toàn bộ địa điểm trên trang
            acc = harvest_current_page(driver, geo)
            numbered = sum(1 for r in acc.values() if r.get("num"))
            print(f"   -> Gom được {len(acc)} địa điểm (có số thứ tự: {numbered})")

            new_count = 0
            for did, rec in acc.items():
                base_url = rec.get("url")
                name = rec.get("name")
                if not base_url or not name:
                    continue
                if base_url not in unique_items:
                    unique_items[base_url] = {
                        "item_url": base_url,
                        "item_name": name,
                        "number_of_reviews": rec.get("reviews", "0"),
                    }
                    new_count += 1
            print(f"   -> Trang này thêm mới {new_count}. Tổng: {len(unique_items)}")
            save(unique_items)

            # đánh dấu trang này ĐÃ XONG
            done_pages.add(page_id)
            try:
                with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
                    json.dump(list(done_pages), f)
            except Exception:
                pass

            empty_streak = empty_streak + 1 if new_count == 0 else 0
            if empty_streak >= 3:
                print("   -> 3 trang liên tiếp không có mục mới. Chuyển thành phố.")
                break
            # nghỉ giữa các trang; định kỳ nghỉ dài để tránh bị chặn
            if (offset // STEP + 1) % REST_EVERY == 0:
                rest = random.uniform(*LONG_REST)
                print(f"   ... nghỉ dài {rest:.0f}s cho an toàn ...")
                time.sleep(rest)
            else:
                time.sleep(random.uniform(*PAGE_GAP))

    driver.quit()
    print(f"\nHoàn tất! Thu được {len(unique_items)} địa điểm duy nhất -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
