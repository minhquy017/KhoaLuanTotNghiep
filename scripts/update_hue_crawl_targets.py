# -*- coding: utf-8 -*-
"""
Script to expand hue_crawl_targets.json:
- Add 18 missing famous Hue attractions (Lăng Khải Định, Làng Hương Thủy Xuân, Đồi Vọng Cảnh, Lăng Gia Long, Cung An Định...)
- Add 104 Hue Hotels & Resorts (Melia Vinpearl, Eldora, Moonlight, Rosaleen...)
- Separate and expand 89 Cafes & Beverage spots (Cà phê Muối, Nina's, Vỹ Dạ Xưa...)
- Add remaining Hue dining restaurants from tourism_vietnam.db (total 391 dining spots)
"""

import os
import sys
import json
import sqlite3

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "tourism_vietnam.db")
TARGETS_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "hue_crawl_targets.json")

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    existing_data = {}
    if os.path.exists(TARGETS_FILE):
        with open(TARGETS_FILE, "r", encoding="utf-8") as f:
            existing_data = json.load(f)

    # 1. Attractions
    existing_attr = existing_data.get("attractions", [])
    existing_attr_urls = {a["url"] for a in existing_attr}

    new_attr_list = [
        {
            "place_id": 9901,
            "name": "Tomb of Khai Dinh",
            "url": "https://www.tripadvisor.com/Attraction_Review-g293926-d451125-Reviews-Tomb_of_Khai_Dinh-Hue_Thua_Thien_Hue_Province.html",
            "review_count": 4500,
            "rating_value": 4.5,
            "category": "attraction"
        },
        {
            "place_id": 9902,
            "name": "Thuy Xuan Incense Village",
            "url": "https://www.tripadvisor.com/Attraction_Review-g293926-d25087310-Reviews-Thuy_Xuan_Incense_Village-Hue_Thua_Thien_Hue_Province.html",
            "review_count": 250,
            "rating_value": 4.6,
            "category": "attraction"
        },
        {
            "place_id": 9903,
            "name": "Vong Canh Hill",
            "url": "https://www.tripadvisor.com/Attraction_Review-g293926-d2417765-Reviews-Vong_Canh_Hill-Hue_Thua_Thien_Hue_Province.html",
            "review_count": 180,
            "rating_value": 4.3,
            "category": "attraction"
        },
        {
            "place_id": 9904,
            "name": "An Dinh Palace",
            "url": "https://www.tripadvisor.com/Attraction_Review-g293926-d2058475-Reviews-An_Dinh_Palace-Hue_Thua_Thien_Hue_Province.html",
            "review_count": 320,
            "rating_value": 4.4,
            "category": "attraction"
        },
        {
            "place_id": 9905,
            "name": "Gia Long Tomb",
            "url": "https://www.tripadvisor.com/Attraction_Review-g293926-d2417757-Reviews-Gia_Long_Tomb-Hue_Thua_Thien_Hue_Province.html",
            "review_count": 190,
            "rating_value": 4.4,
            "category": "attraction"
        },
        {
            "place_id": 9906,
            "name": "Thieu Tri Tomb",
            "url": "https://www.tripadvisor.com/Attraction_Review-g293926-d2058476-Reviews-Thieu_Tri_Tomb-Hue_Thua_Thien_Hue_Province.html",
            "review_count": 95,
            "rating_value": 4.1,
            "category": "attraction"
        },
        {
            "place_id": 9907,
            "name": "Duc Duc Tomb",
            "url": "https://www.tripadvisor.com/Attraction_Review-g293926-d12534571-Reviews-Duc_Duc_Tomb-Hue_Thua_Thien_Hue_Province.html",
            "review_count": 50,
            "rating_value": 4.0,
            "category": "attraction"
        },
        {
            "place_id": 9908,
            "name": "Ho Thuy Tien Abandoned Water Park",
            "url": "https://www.tripadvisor.com/Attraction_Review-g293926-d10129758-Reviews-Ho_Thuy_Tien_Abandoned_Water_Park-Hue_Thua_Thien_Hue_Province.html",
            "review_count": 350,
            "rating_value": 4.2,
            "category": "attraction"
        },
        {
            "place_id": 9909,
            "name": "Ho Quyen",
            "url": "https://www.tripadvisor.com/Attraction_Review-g293926-d456108-Reviews-Ho_Quyen-Hue_Thua_Thien_Hue_Province.html",
            "review_count": 120,
            "rating_value": 4.0,
            "category": "attraction"
        },
        {
            "place_id": 9910,
            "name": "Nam Giao Esplanade",
            "url": "https://www.tripadvisor.com/Attraction_Review-g293926-d451124-Reviews-Nam_Giao_Esplanade-Hue_Thua_Thien_Hue_Province.html",
            "review_count": 85,
            "rating_value": 4.0,
            "category": "attraction"
        },
        {
            "place_id": 9911,
            "name": "Chuon Lagoon",
            "url": "https://www.tripadvisor.com/Attraction_Review-g293926-d12579624-Reviews-Chuon_Lagoon-Hue_Thua_Thien_Hue_Province.html",
            "review_count": 60,
            "rating_value": 4.5,
            "category": "attraction"
        },
        {
            "place_id": 9912,
            "name": "Elephant Springs",
            "url": "https://www.tripadvisor.com/Attraction_Review-g11923533-d2551469-Reviews-Elephant_Springs-Lang_Co_Phu_Loc_District_Thua_Thien_Hue_Province.html",
            "review_count": 310,
            "rating_value": 4.0,
            "category": "attraction"
        },
        {
            "place_id": 9913,
            "name": "Thuan An Beach",
            "url": "https://www.tripadvisor.com/Attraction_Review-g293926-d2058474-Reviews-Thuan_An_Beach-Hue_Thua_Thien_Hue_Province.html",
            "review_count": 90,
            "rating_value": 3.8,
            "category": "attraction"
        },
        {
            "place_id": 9914,
            "name": "Alba Hot Springs Resort",
            "url": "https://www.tripadvisor.com/Attraction_Review-g293926-d8014522-Reviews-Alba_Hot_Springs_Resort-Hue_Thua_Thien_Hue_Province.html",
            "review_count": 120,
            "rating_value": 4.3,
            "category": "attraction"
        },
        {
            "place_id": 9915,
            "name": "Huyen Khong Son Thuong Pagoda",
            "url": "https://www.tripadvisor.com/Attraction_Review-g293926-d13101683-Reviews-Huyen_Khong_Son_Thuong_Pagoda-Hue_Thua_Thien_Hue_Province.html",
            "review_count": 80,
            "rating_value": 4.7,
            "category": "attraction"
        },
        {
            "place_id": 9916,
            "name": "Tu Dam Pagoda",
            "url": "https://www.tripadvisor.com/Attraction_Review-g293926-d2417761-Reviews-Tu_Dam_Pagoda-Hue_Thua_Thien_Hue_Province.html",
            "review_count": 75,
            "rating_value": 4.2,
            "category": "attraction"
        },
        {
            "place_id": 9917,
            "name": "Hue Museum of Royal Antiquities",
            "url": "https://www.tripadvisor.com/Attraction_Review-g293926-d1863583-Reviews-Hue_Museum_of_Royal_Antiquities-Hue_Thua_Thien_Hue_Province.html",
            "review_count": 160,
            "rating_value": 4.2,
            "category": "attraction"
        },
        {
            "place_id": 9918,
            "name": "Phu Cam Cathedral",
            "url": "https://www.tripadvisor.com/Attraction_Review-g293926-d8095431-Reviews-Phu_Cam_Cathedral-Hue_Thua_Thien_Hue_Province.html",
            "review_count": 50,
            "rating_value": 4.3,
            "category": "attraction"
        }
    ]

    attractions = list(existing_attr)
    for na in new_attr_list:
        if na["url"] not in existing_attr_urls:
            attractions.append(na)
            existing_attr_urls.add(na["url"])

    # 2. Hotels
    c.execute("SELECT place_id, name, url, review_count, rating_value FROM places WHERE is_hue = 1 AND category = 'hotel' ORDER BY review_count DESC")
    hotels = [
        {
            "place_id": r[0],
            "name": r[1],
            "url": r[2],
            "review_count": r[3] or 0,
            "rating_value": r[4] or 4.0,
            "category": "hotel"
        }
        for r in c.fetchall()
    ]

    # 3. Restaurants & Cafes
    all_rest_dict = {}
    for r in existing_data.get("restaurants", []):
        all_rest_dict[r["url"]] = r

    c.execute("SELECT place_id, name, url, review_count, rating_value, cuisines FROM places WHERE is_hue = 1 AND category = 'restaurant'")
    for pid, name, url, rev_cnt, rating, cuisines in c.fetchall():
        if url not in all_rest_dict:
            all_rest_dict[url] = {
                "place_id": pid,
                "name": name,
                "url": url,
                "review_count": rev_cnt or 0,
                "rating_value": rating or 4.0,
                "category": "restaurant"
            }
        if cuisines:
            all_rest_dict[url]["cuisines"] = cuisines

    salt_coffee_url = "https://www.tripadvisor.com/Restaurant_Review-g293926-d23194098-Reviews-Ca_Phe_Muoi_Salt_Coffee-Hue_Thua_Thien_Hue_Province.html"
    if salt_coffee_url not in all_rest_dict:
        all_rest_dict[salt_coffee_url] = {
            "place_id": 9950,
            "name": "Ca Phe Muoi (Salt Coffee Hue)",
            "url": salt_coffee_url,
            "review_count": 120,
            "rating_value": 4.6,
            "category": "cafe"
        }

    cafes = []
    restaurants = []
    cafe_keywords = ["cafe", "coffee", "cà phê", "tea", "trà"]

    for url, item in all_rest_dict.items():
        name_low = (item.get("name") or "").lower()
        cuisines_low = (item.get("cuisines") or "").lower()
        clean_item = {
            "place_id": item.get("place_id"),
            "name": item.get("name"),
            "url": item.get("url"),
            "review_count": item.get("review_count", 0),
            "rating_value": item.get("rating_value", 4.0)
        }
        is_cafe = any(k in name_low for k in cafe_keywords) or any(k in cuisines_low for k in cafe_keywords)
        if is_cafe or item.get("category") == "cafe":
            clean_item["category"] = "cafe"
            cafes.append(clean_item)
        else:
            clean_item["category"] = "restaurant"
            restaurants.append(clean_item)

    # Sort each group by review_count DESC
    attractions.sort(key=lambda x: x.get("review_count", 0), reverse=True)
    hotels.sort(key=lambda x: x.get("review_count", 0), reverse=True)
    cafes.sort(key=lambda x: x.get("review_count", 0), reverse=True)
    restaurants.sort(key=lambda x: x.get("review_count", 0), reverse=True)

    final_payload = {
        "metadata": {
            "description": "Danh sách mục tiêu thu thập dữ liệu review du lịch Cố Đô Huế (Attractions, Hotels, Restaurants, Cafes)",
            "total_places": len(attractions) + len(hotels) + len(cafes) + len(restaurants),
            "attractions_count": len(attractions),
            "hotels_count": len(hotels),
            "cafes_count": len(cafes),
            "restaurants_count": len(restaurants)
        },
        "attractions": attractions,
        "hotels": hotels,
        "cafes": cafes,
        "restaurants": restaurants
    }

    with open(TARGETS_FILE, "w", encoding="utf-8") as f:
        json.dump(final_payload, f, ensure_ascii=False, indent=2)

    print(f"Cập nhật thành công {TARGETS_FILE}:")
    print(f" - Attractions: {len(attractions)}")
    print(f" - Hotels: {len(hotels)}")
    print(f" - Cafes: {len(cafes)}")
    print(f" - Restaurants: {len(restaurants)}")
    print(f" -> Tổng cộng: {final_payload['metadata']['total_places']} địa điểm Huế!")

if __name__ == "__main__":
    main()
