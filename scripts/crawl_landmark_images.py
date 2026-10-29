# -*- coding: utf-8 -*-
"""
BƯỚC 2: THU THẬP BỘ DỮ LIỆU ẢNH MẪU CHECK-IN HUẾ (VISUAL BENCHMARK DATASET)
Khóa luận Tốt nghiệp ngành Khoa học Dữ liệu và Trí tuệ Nhân tạo (DS&AI - HUET)
Đề tài: Spatial GraphRAG - Cố đô Huế

Nguồn ảnh: Wikimedia Commons (Public Domain / CC-BY-SA)
Đảm bảo tính pháp lý, ảnh quang học chuẩn di sản văn hóa, tối ưu hóa cho CLIP ViT-B/32.
"""

import os
import sys
import json
import time
import io
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

os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)

# 25 ĐỊA ĐIỂM CHECK-IN VÀ THẮNG CẢNH TIÊU BIỂU TẠI HUẾ (Khớp 100% ID với Spatial KG)
LANDMARKS_CONFIG = [
    {
        "place_id": "place_8875",
        "name": "Đại Nội Huế (Hoàng Thành & Kinh Thành)",
        "sub_name": "Ngọ Môn & Kỳ Đài",
        "category": "Attraction",
        "search_keywords": ["Ngo Mon Hue", "Imperial City Hue", "Thai Hoa Hue", "Ky Dai Hue"],
        "lat": 16.468744,
        "lng": 107.57835
    },
    {
        "place_id": "place_8876",
        "name": "Chùa Thiên Mụ",
        "sub_name": "Tháp Phước Duyên",
        "category": "Attraction",
        "search_keywords": ["Thien Mu pagoda", "Phuoc Duyen pagoda Hue", "Thien Mu temple"],
        "lat": 16.453144,
        "lng": 107.54485
    },
    {
        "place_id": "place_8879",
        "name": "Lăng Khải Định (Ứng Lăng)",
        "sub_name": "Sân chầu tượng đá & Khải Thành Điện",
        "category": "Attraction",
        "search_keywords": ["Khai Dinh tomb", "Khai Thanh Palace Hue", "Lang Khai Dinh"],
        "lat": 16.3986,
        "lng": 107.5906
    },
    {
        "place_id": "place_8880",
        "name": "Lăng Tự Đức (Khiêm Lăng)",
        "sub_name": "Hồ Lưu Khiêm & Xung Khiêm Tạ",
        "category": "Attraction",
        "search_keywords": ["Tu Duc tomb", "Luu Khiem lake Hue", "Lang Tu Duc"],
        "lat": 16.4328,
        "lng": 107.5647
    },
    {
        "place_id": "place_8878",
        "name": "Lăng Minh Mạng (Hiếu Lăng)",
        "sub_name": "Cầu Thông Minh Chính Trực & Minh Lâu",
        "category": "Attraction",
        "search_keywords": ["Minh Mang tomb", "Minh Lau Hue", "Lang Minh Mang"],
        "lat": 16.387653,
        "lng": 107.56918
    },
    {
        "place_id": "custom_attr_03",
        "name": "Làng hương Thủy Xuân",
        "sub_name": "Con đường chân hương xòe quạt",
        "category": "Attraction",
        "search_keywords": ["Thuy Xuan incense", "Incense Hue Vietnam", "Thuy Xuan Hue"],
        "lat": 16.4412,
        "lng": 107.5684
    },
    {
        "place_id": "custom_local_31",
        "name": "Cung An Định",
        "sub_name": "Lâu đài Tân cổ điển Pháp - Việt",
        "category": "Attraction",
        "search_keywords": ["An Dinh Palace Hue", "An Dinh Palace", "Khai Tuong Lau Hue"],
        "lat": 16.4589,
        "lng": 107.5947
    },
    {
        "place_id": "place_8919",
        "name": "Cầu Trường Tiền",
        "sub_name": "Cây cầu 6 vài 12 nhịp sông Hương",
        "category": "Attraction",
        "search_keywords": ["Trang Tien bridge Hue", "Truong Tien bridge Hue", "Trang Tien Hue"],
        "lat": 16.4682,
        "lng": 107.5898
    },
    {
        "place_id": "place_8920",
        "name": "Chợ Đông Ba",
        "sub_name": "Cổng chợ & Tháp đồng hồ",
        "category": "Attraction",
        "search_keywords": ["Dong Ba market Hue", "Dong Ba market", "Cho Dong Ba"],
        "lat": 16.47262,
        "lng": 107.58850
    },
    {
        "place_id": "custom_attr_02",
        "name": "Đồi Vọng Cảnh",
        "sub_name": "Vọng lâu ngắm khúc quanh sông Hương",
        "category": "Attraction",
        "search_keywords": ["Vong Canh hill Hue", "Vong Canh Hue", "Huong river Vong Canh"],
        "lat": 16.4358,
        "lng": 107.5582
    },
    {
        "place_id": "custom_local_21",
        "name": "Công Viên Hồ Thủy Tiên (Tượng Rồng)",
        "sub_name": "Tượng đầu rồng khổng lồ bỏ hoang",
        "category": "Attraction",
        "search_keywords": ["Ho Thuy Tien dragon", "Ho Thuy Tien abandoned", "Thuy Tien lake Hue"],
        "lat": 16.4182,
        "lng": 107.5753
    },
    {
        "place_id": "place_8886",
        "name": "Chùa Từ Hiếu",
        "sub_name": "Cổ tự nghĩa trang thái giám triều Nguyễn",
        "category": "Attraction",
        "search_keywords": ["Tu Hieu pagoda", "Tu Hieu temple Hue", "Chua Tu Hieu"],
        "lat": 16.4397,
        "lng": 107.5621
    },
    {
        "place_id": "custom_attr_05",
        "name": "Chùa Huyền Không Sơn Thượng",
        "sub_name": "Vườn thiền ẩn mình giữa rừng thông",
        "category": "Attraction",
        "search_keywords": ["Huyen Khong Son Thuong", "Huyen Khong pagoda Hue", "Huyen Khong Hue"],
        "lat": 16.4851,
        "lng": 107.4952
    },
    {
        "place_id": "custom_local_20",
        "name": "Nhà Thờ Dòng Chúa Cứu Thế Huế",
        "sub_name": "Thánh đường tam giác vút cao đường Nguyễn Huệ",
        "category": "Attraction",
        "search_keywords": ["Redemptorist Church Hue", "Dong Chua Cuu The Hue", "Our Lady of Perpetual Help Hue"],
        "lat": 16.4593,
        "lng": 107.5956
    },
    {
        "place_id": "place_8922",
        "name": "Văn Miếu Huế",
        "sub_name": "Văn Thánh miếu bờ sông Hương",
        "category": "Attraction",
        "search_keywords": ["Temple of Literature Hue", "Van Mieu Hue", "Van Thanh Hue"],
        "lat": 16.4552,
        "lng": 107.5385
    },
    {
        "place_id": "place_8885",
        "name": "Cầu ngói Thanh Toàn",
        "sub_name": "Cầu ngói cổ bắc qua sông Như Ý",
        "category": "Attraction",
        "search_keywords": ["Thanh Toan tile-roofed bridge", "Thanh Toan bridge", "Cau ngoi Thanh Toan"],
        "lat": 16.4529,
        "lng": 107.6322
    },
    {
        "place_id": "custom_attr_01",
        "name": "Lăng Gia Long (Thiên Thọ Lăng)",
        "sub_name": "Lăng mộ vua sáng lập triều Nguyễn",
        "category": "Attraction",
        "search_keywords": ["Gia Long tomb", "Lang Gia Long", "Thien Tho tomb Hue"],
        "lat": 16.3534,
        "lng": 107.5756
    },
    {
        "place_id": "custom_attr_04",
        "name": "Điện Hòn Chén",
        "sub_name": "Điện thờ Mẫu Liễu Hạnh cheo leo vách núi",
        "category": "Attraction",
        "search_keywords": ["Hon Chen temple", "Dien Hon Chen", "Hon Chen Hue"],
        "lat": 16.4258,
        "lng": 107.5389
    },
    {
        "place_id": "place_8882",
        "name": "Sông Hương (Bến thuyền Tòa Khâm)",
        "sub_name": "Cầu đi bộ gỗ Lim & Thuyền rồng ca Huế",
        "category": "Attraction",
        "search_keywords": ["Perfume River Hue", "Huong river boat", "Song Huong Hue"],
        "lat": 16.4678,
        "lng": 107.5925
    },
    {
        "place_id": "custom_local_32",
        "name": "Đầm Lập An & Làng Chài Lăng Cô",
        "sub_name": "Con đường rẽ nước giữa đầm lãng mạn",
        "category": "Attraction",
        "search_keywords": ["Lap An lagoon", "Lang Co lagoon", "Dam Lap An"],
        "lat": 16.2341,
        "lng": 108.0125
    },
    {
        "place_id": "place_8917",
        "name": "Bãi biển Lăng Cô",
        "sub_name": "Vịnh biển đẹp nhất thế giới dưới đèo Hải Vân",
        "category": "Attraction",
        "search_keywords": ["Lang Co beach", "Lang Co bay", "Lang Co Hue"],
        "lat": 16.2285,
        "lng": 108.0315
    },
    {
        "place_id": "place_8918",
        "name": "Phá Tam Giang (Đầm Chuồn)",
        "sub_name": "Làng chài & nhà chồ ngắm hoàng hôn",
        "category": "Attraction",
        "search_keywords": ["Tam Giang lagoon", "Dam Chuon Hue", "Pha Tam Giang"],
        "lat": 16.5124,
        "lng": 107.6482
    },
    {
        "place_id": "custom_local_30",
        "name": "Chùa Từ Đàm",
        "sub_name": "Tổ đình trung tâm Phật giáo Huế",
        "category": "Attraction",
        "search_keywords": ["Tu Dam pagoda Hue", "Tu Dam temple", "Chua Tu Dam"],
        "lat": 16.4502,
        "lng": 107.5815
    },
    {
        "place_id": "custom_local_15",
        "name": "Cà Phê Mắt Biếc (Phố Cổ Bao Vinh)",
        "sub_name": "Ngôi nhà gỗ phố cổ bối cảnh phim Mắt Biếc",
        "category": "Attraction",
        "search_keywords": ["Bao Vinh ancient town", "Bao Vinh Hue", "Pho co Bao Vinh"],
        "lat": 16.4885,
        "lng": 107.5892
    },
    {
        "place_id": "custom_attr_con_hen",
        "name": "Cồn Hến (Đảo Cồn Hến)",
        "sub_name": "Cù lao sông Hương cái nôi cơm hến",
        "category": "Attraction",
        "search_keywords": ["Con Hen Hue", "Con Hen island", "Con Hen river Hue"],
        "lat": 16.4782,
        "lng": 107.5995
    }
]

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
HTTP_HEADERS = {
    "User-Agent": "HueTourismAcademicResearch/1.0 (contact@huetourism.edu.vn; Computer Science Dept)"
}


def search_commons_images(query: str, max_results: int = 6):
    """Tìm kiếm file ảnh trên Wikimedia Commons dựa trên từ khóa."""
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,  # 6 = File: namespace
        "gsrlimit": max_results,
        "prop": "imageinfo",
        "iiprop": "url|mime|size"
    }
    try:
        resp = requests.get(COMMONS_API, headers=HTTP_HEADERS, params=params, timeout=10)
        if resp.status_code != 200:
            return []
        data = resp.json()
        pages = data.get("query", {}).get("pages", {})
        results = []
        for page in pages.values():
            title = page.get("title", "")
            imageinfo = page.get("imageinfo", [])
            if not imageinfo:
                continue
            info = imageinfo[0]
            mime = info.get("mime", "").lower()
            if "image" not in mime or "svg" in mime or "tif" in mime:
                continue
            url = info.get("url")
            if url:
                results.append({
                    "title": title,
                    "url": url,
                    "size": info.get("size", 0)
                })
        return results
    except Exception:
        return []


def download_and_process_image(url: str, save_path: str, max_size: int = 800) -> bool:
    """Tải ảnh từ URL, đổi sang RGB, resize và lưu dạng JPEG chuẩn nhẹ tối ưu cho CLIP."""
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        resp = requests.get(url, headers=HTTP_HEADERS, timeout=12)
        if resp.status_code != 200 or len(resp.content) < 4000:
            return False
        
        img = Image.open(io.BytesIO(resp.content))
        img = img.convert("RGB")
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        img.save(save_path, "JPEG", quality=85, optimize=True)
        return True
    except Exception as e:
        return False


def crawl_images_for_landmarks():
    metadata_list = []
    total_downloaded = 0

    print("=" * 75, flush=True)
    print("🚀 BẮT ĐẦU CÀO BỘ DỮ LIỆU ẢNH CHECK-IN HUẾ (25 ĐỊA ĐIỂM)", flush=True)
    print("=" * 75, flush=True)

    for idx, lm in enumerate(LANDMARKS_CONFIG, 1):
        place_id = lm["place_id"]
        place_name = lm["name"]
        sub_name = lm["sub_name"]
        lat = lm["lat"]
        lng = lm["lng"]
        
        place_dir = os.path.join(IMAGE_OUTPUT_DIR, place_id)
        os.makedirs(place_dir, exist_ok=True)
        
        print(f"\n[{idx}/25] 📍 {place_name} ({place_id})", flush=True)
        
        collected_for_place = 0
        seen_urls = set()
        
        for query in lm["search_keywords"]:
            if collected_for_place >= 3:
                break
            
            items = search_commons_images(query, max_results=5)
            for item in items:
                img_url = item["url"]
                if img_url in seen_urls:
                    continue
                seen_urls.add(img_url)
                
                file_name = f"img_{collected_for_place + 1:02d}.jpg"
                save_path = os.path.join(place_dir, file_name)
                
                success = download_and_process_image(img_url, save_path)
                if success:
                    collected_for_place += 1
                    total_downloaded += 1
                    rel_path = os.path.relpath(save_path, PROJECT_ROOT).replace("\\", "/")
                    
                    metadata_list.append({
                        "image_id": f"img_{place_id}_{collected_for_place:02d}",
                        "place_id": place_id,
                        "place_name": place_name,
                        "sub_location": sub_name,
                        "category": lm["category"],
                        "file_path": rel_path,
                        "source_title": item["title"],
                        "source_url": img_url,
                        "caption": f"Ảnh tư liệu check-in tại {place_name} ({sub_name}) Cố đô Huế",
                        "latitude": lat,
                        "longitude": lng
                    })
                    print(f"   ✓ [Ảnh {collected_for_place}/3] {file_name} -> {item['title'][:40]}...", flush=True)
                    time.sleep(0.15)
                    
                    if collected_for_place >= 3:
                        break
        
        if collected_for_place == 0:
            print(f"   ⚠️ Chưa tìm thấy ảnh tự động cho {place_name}", flush=True)

    # Ghi file metadata JSON
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata_list, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 75, flush=True)
    print(f"🎉 HOÀN TẤT THU THẬP! Tổng cộng đã tải {total_downloaded} ảnh cho các địa điểm Huế.", flush=True)
    print(f"📁 Thư mục ảnh: {IMAGE_OUTPUT_DIR}", flush=True)
    print(f"📄 File Metadata: {METADATA_FILE}", flush=True)
    print("=" * 75, flush=True)


if __name__ == "__main__":
    crawl_images_for_landmarks()
