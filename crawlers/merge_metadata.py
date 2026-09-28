# -*- coding: utf-8 -*-
"""
HỢP NHẤT DỮ LIỆU METADATA TỪ CÁC WORKER
Tìm kiếm tất cả các file 'vietnam_metadata_w*.json' và gộp thành:
  - vietnam_places_metadata.json
Kèm thống kê chất lượng dữ liệu (tọa độ, quận huyện, ẩm thực).

Chạy:
  python merge_metadata.py
"""

import os
import re
import sys
import json

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

OUTPUT_MERGED = "vietnam_places_metadata.json"

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    merged_data = {}

    print("=" * 60)
    print("ĐANG TÌM KIẾM VÀ GỘP DỮ LIỆU METADATA TỪ CÁC WORKER...")
    print("=" * 60)

    # Quét tất cả file vietnam_metadata_w*.json
    files_found = 0
    for f in sorted(os.listdir(base_dir)):
        if f.startswith("vietnam_metadata_w") and f.endswith(".json") and "bak" not in f and "progress" not in f:
            fpath = os.path.join(base_dir, f)
            try:
                with open(fpath, "r", encoding="utf-8") as fp:
                    items = json.load(fp)
                files_found += 1
                before_count = len(merged_data)
                for item in items:
                    url = item.get("url")
                    if url:
                        merged_data[url] = item
                print(f"-> File [{f}]: Có {len(items)} bản ghi (Thêm mới {len(merged_data) - before_count})")
            except Exception as e:
                print(f"[LỖI] Đọc file {f}: {e}")

    if not merged_data:
        print("\nChưa tìm thấy dữ liệu metadata nào để gộp.")
        return

    result_list = list(merged_data.values())

    # Lưu file kết quả
    out_path = os.path.join(base_dir, OUTPUT_MERGED)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result_list, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"HỢP NHẤT THÀNH CÔNG -> {OUTPUT_MERGED}")
    print(f"Tổng số địa điểm hợp nhất: {len(result_list)}")
    print("=" * 60)

    # Thống kê chất lượng
    has_geo = sum(1 for x in result_list if x.get("latitude") and x.get("longitude"))
    has_addr = sum(1 for x in result_list if x.get("street_address"))
    has_cuis = sum(1 for x in result_list if x.get("cuisines"))
    has_dist = sum(1 for x in result_list if x.get("district"))

    cats = {}
    for x in result_list:
        c = x.get("category", "unknown")
        cats[c] = cats.get(c, 0) + 1

    print("\nTHỐNG KÊ CHẤT LƯỢNG DỮ LIỆU:")
    print(f"  * Có tọa độ GPS (Lat/Lng): {has_geo:>5} / {len(result_list)} ({has_geo/len(result_list)*100:.1f}%)")
    print(f"  * Có địa chỉ đường phố:   {has_addr:>5} / {len(result_list)} ({has_addr/len(result_list)*100:.1f}%)")
    print(f"  * Có Quận / Khu vực:       {has_dist:>5} / {len(result_list)} ({has_dist/len(result_list)*100:.1f}%)")
    print(f"  * Có danh sách Ẩm thực:   {has_cuis:>5} / {len(result_list)} ({has_cuis/len(result_list)*100:.1f}%)")
    print("\nPHÂN BỐ THEO LOẠI HÌNH:")
    for k, v in cats.items():
        print(f"  * {k.upper():<12}: {v:>5} địa điểm")
    print("=" * 60)


if __name__ == "__main__":
    main()
