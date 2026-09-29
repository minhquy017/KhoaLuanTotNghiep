# -*- coding: utf-8 -*-
"""
MODULE 1: LÀM SẠCH VÀ CHUẨN HÓA DỮ LIỆU KHÔNG GIAN ĐA TẦNG (2-TIER SPATIAL CLEANING)
Khóa luận Tốt nghiệp: Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh
Khoa Kỹ thuật và Công nghệ — Đại học Huế (HUET)
Chuyên ngành: Khoa học Dữ liệu & Trí tuệ Nhân tạo (K3)

Đặc điểm nâng cấp:
  1. Cấp 1 (`standard_province`):
     - Áp dụng địa giới hành chính mới nhất: "Thành phố Huế" là Thành phố trực thuộc Trung ương
       (Nghị quyết số 175/2024/QH15 của Quốc hội).
     - Ưu tiên URL & Locality trước để chống false positive (ví dụ: phố đi bộ "Nguyễn Huệ" ở Quận 1,
       hay "Phố Huế" ở Hai Bà Trưng, Hà Nội sẽ KHÔNG bị nhầm thành Thành phố Huế).
  2. Cấp 2 (`standard_district`):
     - Phân định chuẩn Quận/Huyện/Thị xã/Thành phố trực thuộc tỉnh:
       * Thành phố Huế: Quận Phú Xuân (Bắc sông Hương), Quận Thuận Hóa (Nam sông Hương),
         Huyện Nam Đông, Huyện A Lưới, Huyện Phú Lộc, Huyện Phú Vang, Thị xã Hương Thủy,
         Thị xã Hương Trà, Thị xã Phong Điền, Huyện Quảng Điền.
       * TP.HCM: Thành phố Thủ Đức, Quận 1, Quận 3, Quận 7...
       * Ninh Bình: Thành phố Hoa Lư (sau đề án sáp nhập TP Ninh Bình và Hoa Lư).
       * Kiên Giang: Thành phố Phú Quốc (Dương Đông, An Thới, Gành Dầu...).
  3. Tách biệt hoàn toàn từ điển tri thức tại: `data/processed/vietnam_provinces_gazetteer.json`.
"""

import os
import re
import sys
import json
import unicodedata
from collections import Counter

# Bắt buộc UTF-8 stdout trên Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass


def load_gazetteer(gazetteer_path: str):
    """Nạp cơ sở tri thức địa danh từ file JSON cấu hình riêng biệt."""
    if not os.path.exists(gazetteer_path):
        raise FileNotFoundError(f"Không tìm thấy file từ điển địa danh: {gazetteer_path}")

    with open(gazetteer_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    bbox = data.get("vietnam_bounding_box", {"lat_min": 8.0, "lat_max": 24.0, "lng_min": 102.0, "lng_max": 110.0})
    foreign_kws = [re.compile(r'\b' + re.escape(kw) + r'\b') for kw in data.get("foreign_keywords", [])]

    province_rules = {}
    region_mapping = {}
    district_rules = {}

    for prov, info in data.get("provinces", {}).items():
        region_mapping[prov] = info.get("region", "Khác")
        province_rules[prov] = [re.compile(r'\b' + re.escape(alias) + r'\b') for alias in info.get("aliases", [])]

        dist_dict = {}
        for dist_name, dist_aliases in info.get("districts", {}).items():
            dist_dict[dist_name] = [re.compile(r'\b' + re.escape(alias) + r'\b') for alias in dist_aliases]
        district_rules[prov] = dist_dict

    return bbox, foreign_kws, province_rules, region_mapping, district_rules


def normalize_search_text(input_str: str) -> str:
    """Chuẩn hóa chuỗi: bỏ dấu tiếng Việt, thay thế các ký tự phân tách URL thành dấu cách."""
    if not input_str:
        return ""
    s = input_str.replace('_', ' ').replace('-', ' ').replace('/', ' ').replace('.', ' ')
    nfkd = unicodedata.normalize('NFKD', s)
    return ''.join([c for c in nfkd if not unicodedata.combining(c)]).lower()


def is_foreign_place(place: dict, bbox: dict, foreign_regex_list: list) -> bool:
    """Xác định các địa điểm ngoại lai nằm ngoài lãnh thổ Việt Nam."""
    country = (place.get('country') or '').strip().upper()
    if country and country not in ['VN', 'VIETNAM', '']:
        return True

    search_str = ' '.join([
        place.get('locality', '') or '',
        place.get('street_address', '') or '',
        place.get('url', '') or ''
    ])
    norm_str = normalize_search_text(search_str)
    for kw_re in foreign_regex_list:
        if kw_re.search(norm_str):
            return True

    lat = place.get('latitude')
    lng = place.get('longitude')
    if lat is not None and lng is not None:
        try:
            flat, flng = float(lat), float(lng)
            if not (bbox['lat_min'] <= flat <= bbox['lat_max'] and bbox['lng_min'] <= flng <= bbox['lng_max']):
                return True
        except (ValueError, TypeError):
            pass

    return False


def standardize_province_high_precision(place: dict, province_rules: dict) -> str:
    """
    Chuẩn hóa Tỉnh/Thành phố với thuật toán phân tầng độ chính xác cao:
      Tầng 1: URL & Locality (tín hiệu định danh chuẩn xác nhất, loại bỏ nhầm lẫn tên đường).
      Tầng 2: Địa chỉ chi tiết (Address) & Tên (Name).
      Tầng 3: Bounding box GPS thực tế.
    """
    url_norm = normalize_search_text(place.get('url', '') or '')
    loc_norm = normalize_search_text(place.get('locality', '') or '')
    lead_text = f"{url_norm} {loc_norm}"

    # 1. Ưu tiên kiểm tra các đô thị đặc biệt theo URL và Locality
    if re.search(r'\b(ho chi minh|saigon|sai gon|hcmc|district 1|district 2|district 3|district 7)\b', lead_text):
        return 'TP. Hồ Chí Minh'
    if re.search(r'\b(hanoi|ha noi|hoan kiem|ba dinh|tay ho|cau giay)\b', lead_text):
        return 'Hà Nội'
    if re.search(r'\b(da nang|danang|quang nam|hoi an|tam ky|hai chau|son tra|ngu hanh son)\b', lead_text):
        return 'Thành phố Đà Nẵng'
    if re.search(r'\b(thua thien|thua thien hue|hue thua thien|thanh pho hue)\b', lead_text) or loc_norm == 'hue':
        return 'Thành phố Huế'

    # 2. Quét toàn bộ 63 tỉnh trên URL và Locality
    for prov, regex_list in province_rules.items():
        for pat in regex_list:
            if pat.search(lead_text):
                return prov

    # 3. Quét trên tên đường và tên quán (loại trừ trường hợp dính tên danh nhân như 'nguyen hue')
    addr_norm = normalize_search_text(place.get('street_address', '') or '')
    name_norm = normalize_search_text(place.get('name', '') or '')
    full_text = f"{lead_text} {addr_norm} {name_norm}"

    for prov, regex_list in province_rules.items():
        for pat in regex_list:
            if prov == "Thành phố Huế":
                # Tránh nhầm phố Nguyễn Huệ hoặc Phố Huế
                if re.search(r'\b(nguyen hue|pho hue)\b', addr_norm) and not (re.search(r'\bhue\b', lead_text)):
                    continue
            if pat.search(full_text):
                return prov

    # 4. Fallback theo tọa độ GPS thực tế
    lat = place.get('latitude')
    lng = place.get('longitude')
    if lat is not None and lng is not None:
        try:
            flat, flng = float(lat), float(lng)
            # Khung tọa độ Thành phố Huế
            if 16.0 <= flat <= 16.7 and 107.2 <= flng <= 108.1:
                return 'Thành phố Huế'
            # Khung Hà Nội
            if 20.8 <= flat <= 21.4 and 105.6 <= flng <= 106.0:
                return 'Hà Nội'
            # Khung TP.HCM
            if 10.6 <= flat <= 11.0 and 106.5 <= flng <= 107.0:
                return 'TP. Hồ Chí Minh'
            # Khung Thành phố Đà Nẵng (gồm cả Hội An/Quảng Nam)
            if 15.5 <= flat <= 16.3 and 107.8 <= flng <= 108.7:
                return 'Thành phố Đà Nẵng'
        except (ValueError, TypeError):
            pass

    return "Khác / Chưa xác định"


def standardize_district(place: dict, province: str, district_rules: dict) -> str:
    """Tự động bóc tách Quận/Huyện chuẩn thuộc Tỉnh/Thành phố tương ứng (kết hợp từ điển + GPS)."""
    prov_districts = district_rules.get(province, {})

    search_components = [
        place.get('street_address', '') or '',
        place.get('locality', '') or '',
        place.get('district', '') or '',
        place.get('name', '') or '',
        place.get('url', '') or ''
    ]
    norm_text = normalize_search_text(' '.join(search_components))

    # 1. Quét theo từ điển tên quận/phường/đường phố
    if prov_districts:
        for dist_name, regex_list in prov_districts.items():
            for pat in regex_list:
                if pat.search(norm_text):
                    return dist_name

    # 2. Xử lý riêng cho Thành phố Huế theo phân định sông Hương
    if province == "Thành phố Huế":
        lat = place.get('latitude')
        if lat is not None:
            try:
                flat = float(lat)
                if flat >= 16.467:
                    return "Quận Phú Xuân"   # Bờ Bắc (Đại Nội, Kim Long, Gia Hội)
                else:
                    return "Quận Thuận Hóa"  # Bờ Nam (Phú Hội, Vĩnh Ninh, Vỹ Dạ)
            except (ValueError, TypeError):
                pass

    # 3. Xử lý GPS cho Thành phố Đà Nẵng (Hợp nhất Đà Nẵng & Quảng Nam)
    if province == "Thành phố Đà Nẵng":
        lat, lng = place.get('latitude'), place.get('longitude')
        if lat is not None and lng is not None:
            try:
                flat, flng = float(lat), float(lng)
                # Khu vực Phố cổ Hội An & Bãi biển An Bàng/Cửa Đại
                if 15.84 <= flat <= 15.94 and 108.28 <= flng <= 108.40:
                    return "Thành phố Hội An"
                # Khu vực Quận Hải Châu (Trung tâm sông Hàn)
                if 16.02 <= flat <= 16.085 and 108.20 <= flng <= 108.235:
                    return "Quận Hải Châu"
                # Khu vực Quận Sơn Trà (Bán đảo & Bờ Đông Mỹ Khê)
                if 16.04 <= flat <= 16.12 and 108.235 <= flng <= 108.28:
                    return "Quận Sơn Trà"
                # Khu vực Quận Ngũ Hành Sơn (Mỹ An, An Thượng, Non Nước)
                if 15.98 <= flat <= 16.04 and 108.235 <= flng <= 108.275:
                    return "Quận Ngũ Hành Sơn"
            except (ValueError, TypeError):
                pass

    # 4. Xử lý GPS cho TP. Hồ Chí Minh
    if province == "TP. Hồ Chí Minh":
        lat, lng = place.get('latitude'), place.get('longitude')
        if lat is not None and lng is not None:
            try:
                flat, flng = float(lat), float(lng)
                # Quận 1 trung tâm (Bến Nghé, Bến Thành, Hồ Tùng Mậu, Nguyễn Huệ)
                if 10.760 <= flat <= 10.795 and 106.685 <= flng <= 106.710:
                    return "Quận 1"
                # Quận 3
                if 10.770 <= flat <= 10.790 and 106.670 <= flng <= 106.690:
                    return "Quận 3"
                # Thành phố Thủ Đức
                if flng >= 106.720:
                    return "Thành phố Thủ Đức"
            except (ValueError, TypeError):
                pass

    # 5. Xử lý GPS cho Hà Nội
    if province == "Hà Nội":
        lat, lng = place.get('latitude'), place.get('longitude')
        if lat is not None and lng is not None:
            try:
                flat, flng = float(lat), float(lng)
                # Quận Hoàn Kiếm trung tâm (Phố cổ, Hồ Gươm)
                if 21.018 <= flat <= 21.042 and 105.845 <= flng <= 105.865:
                    return "Quận Hoàn Kiếm"
                # Quận Tây Hồ
                if 21.050 <= flat <= 21.085 and 105.805 <= flng <= 105.845:
                    return "Quận Tây Hồ"
            except (ValueError, TypeError):
                pass

    return "Chưa phân loại"


def run_spatial_cleaning():
    """Thực thi toàn bộ quy trình Làm sạch Không gian 2 tầng."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    raw_file = os.path.join(base_dir, "data", "raw", "vietnam_places_metadata.json")
    gazetteer_file = os.path.join(base_dir, "data", "processed", "vietnam_provinces_gazetteer.json")
    out_file = os.path.join(base_dir, "data", "processed", "vietnam_places_spatial_cleaned.json")

    print("=" * 80)
    print("BẮT ĐẦU BƯỚC 1: LÀM SẠCH VÀ CHUẨN HÓA DỮ LIỆU KHÔNG GIAN ĐA TẦNG (2-TIER SPATIAL)")
    print("=" * 80)
    print(f"-> Nạp từ điển địa danh chuẩn: {gazetteer_file}")
    bbox, foreign_regex_list, province_rules, region_mapping, district_rules = load_gazetteer(gazetteer_file)

    print(f"-> Đọc dữ liệu địa điểm thô: {raw_file}")
    if not os.path.exists(raw_file):
        print(f"[LỖI] Không tìm thấy file {raw_file}")
        return

    with open(raw_file, "r", encoding="utf-8") as f:
        places = json.load(f)

    total_raw = len(places)
    print(f"-> Tổng số địa điểm ban đầu: {total_raw:,} địa điểm")

    foreign_removed = 0
    cleaned_places = []
    prov_counter = Counter()
    region_counter = Counter()
    hue_district_counter = Counter()
    gps_valid_count = 0
    gps_missing_count = 0

    for p in places:
        # 1. Lọc bỏ địa điểm ngoại lai
        if is_foreign_place(p, bbox, foreign_regex_list):
            foreign_removed += 1
            continue

        # 2. Kiểm tra GPS
        lat = p.get('latitude')
        lng = p.get('longitude')
        has_valid_gps = 0
        if lat is not None and lng is not None:
            try:
                flat, flng = float(lat), float(lng)
                if bbox['lat_min'] <= flat <= bbox['lat_max'] and bbox['lng_min'] <= flng <= bbox['lng_max']:
                    has_valid_gps = 1
                    gps_valid_count += 1
                else:
                    gps_missing_count += 1
            except (ValueError, TypeError):
                gps_missing_count += 1
        else:
            gps_missing_count += 1

        # 3. Chuẩn hóa Tầng 1: Tỉnh / Thành phố
        std_prov = standardize_province_high_precision(p, province_rules)
        region = region_mapping.get(std_prov, "Khác")

        # 4. Chuẩn hóa Tầng 2: Quận / Huyện / Thị xã
        std_dist = standardize_district(p, std_prov, district_rules)

        prov_counter[std_prov] += 1
        region_counter[region] += 1
        if std_prov == "Thành phố Huế":
            hue_district_counter[std_dist] += 1

        # 5. Gắn các trường chuẩn hóa (giữ nguyên vẹn 100% dữ liệu gốc)
        cleaned_item = dict(p)
        cleaned_item['has_valid_gps'] = has_valid_gps
        cleaned_item['standard_province'] = std_prov
        cleaned_item['standard_district'] = std_dist
        cleaned_item['region'] = region

        cleaned_places.append(cleaned_item)

    # 6. Lưu ra file JSON sạch
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(cleaned_places, f, ensure_ascii=False, indent=2)

    # 7. Báo cáo thống kê
    print("\n" + "=" * 80)
    print("KẾT QUẢ LÀM SẠCH KHÔNG GIAN ĐA TẦNG:")
    print("=" * 80)
    print(f"1. Tổng địa điểm ban đầu:            {total_raw:>8,} địa điểm")
    print(f"2. Địa điểm ngoại lai loại bỏ:        {foreign_removed:>8,} địa điểm ({foreign_removed/total_raw*100:.2f}%)")
    print(f"3. ĐỊA ĐIỂM VIỆT NAM HỢP LỆ GIỮ LẠI:  {len(cleaned_places):>8,} địa điểm ({len(cleaned_places)/total_raw*100:.2f}%)")
    print(f"   - Tọa độ GPS hợp lệ đầy đủ:       {gps_valid_count:>8,} địa điểm ({gps_valid_count/len(cleaned_places)*100:.2f}%)")
    print(f"   - Tọa độ GPS khuyết thiếu:        {gps_missing_count:>8,} địa điểm ({gps_missing_count/len(cleaned_places)*100:.2f}%)")

    print("\n4. PHÂN BỐ THEO VÙNG MIỀN:")
    for reg, cnt in region_counter.most_common():
        print(f"   * {reg:<12}: {cnt:>6,} địa điểm ({cnt/len(cleaned_places)*100:.2f}%)")

    print("\n5. TOP 10 TỈNH/THÀNH PHỐ TIÊU BIỂU:")
    for prov, cnt in prov_counter.most_common(10):
        print(f"   * {prov:<20}: {cnt:>6,} địa điểm ({cnt/len(cleaned_places)*100:.2f}%)")

    print("\n" + "-" * 80)
    print(f"🎯 ĐỊA BÀN TRỌNG ĐIỂM NGHIÊN CỨU: THÀNH PHỐ HUẾ ({prov_counter.get('Thành phố Huế', 0)} địa điểm)")
    print("   Phân bố theo Quận/Huyện/Thị xã trực thuộc TP. Huế (mới nhất):")
    for dist, cnt in hue_district_counter.most_common():
        print(f"   - {dist:<22}: {cnt:>4} địa điểm ({cnt/prov_counter.get('Thành phố Huế', 1)*100:.1f}%)")
    print("-" * 80)
    print(f"-> File kết quả đã ghi tại: {out_file}\n")


if __name__ == "__main__":
    run_spatial_cleaning()
