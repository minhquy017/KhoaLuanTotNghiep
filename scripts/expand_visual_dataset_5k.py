# -*- coding: utf-8 -*-
"""
EXPAND VISUAL DATASET TO 5,000 IMAGES (DOMAIN-SPECIFIC HERITAGE AUGMENTATION)
Khóa luận Tốt nghiệp ngành Khoa học Dữ liệu và Trí tuệ Nhân tạo (DS&AI - HUET)
Đề tài: Spatial GraphRAG - Cố đô Huế

Mục tiêu:
- Nâng quy mô cơ sở dữ liệu ảnh mẫu di sản Huế từ 1.594 ảnh lên chuẩn 5.000 ảnh
- Sử dụng phương pháp Tăng cường Dữ liệu Thị giác thích nghi miền (Heritage Domain Augmentation):
  1. weather_rain_hue: Mô phỏng mưa phùn, sương mù Cố đô Huế (giảm tương phản, phủ sương nhẹ)
  2. golden_hour: Mô phỏng nắng chiều hoàng hôn sông Hương (tăng ấm sắc độ, chiều tà)
  3. sunny_contrast: Mô phỏng nắng trưa nhiệt đới Cố đô (tương phản sắc nét)
  4. mobile_crop_zoom: Mô phỏng du khách chụp cự ly gần / phóng to chi tiết kiến trúc (crop 88%)
  5. symmetry_flip: Mô phỏng góc nhìn đối xứng của các công trình cung đình, lăng tẩm
- Lưu metadata rõ ràng từng ảnh và cập nhật file `landmark_image_index.json`
"""

import os
import sys
import json
import time
import random
from PIL import Image, ImageEnhance, ImageFilter

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
IMAGE_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "visual_database", "images")
METADATA_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "visual_database", "landmark_image_index.json")
BACKUP_METADATA_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "visual_database", "landmark_image_index_1594_backup.json")

TARGET_TOTAL_IMAGES = 5000


def apply_rain_hue(img: Image.Image) -> Image.Image:
    """Mô phỏng mưa phùn, mây mù xứ Huế: Giảm tương phản nhẹ, phủ tông lạnh nhẹ."""
    enhancer_con = ImageEnhance.Contrast(img)
    img_con = enhancer_con.enhance(0.88)
    enhancer_bri = ImageEnhance.Brightness(img_con)
    img_bri = enhancer_bri.enhance(0.95)
    return img_bri.filter(ImageFilter.GaussianBlur(radius=0.4))


def apply_golden_hour(img: Image.Image) -> Image.Image:
    """Mô phỏng hoàng hôn chiều tà sông Hương: Tông màu ấm vàng."""
    rgb = img.convert("RGB")
    r, g, b = rgb.split()
    r = r.point(lambda i: min(255, int(i * 1.08)))
    b = b.point(lambda i: int(i * 0.90))
    img_warm = Image.merge("RGB", (r, g, b))
    enhancer = ImageEnhance.Contrast(img_warm)
    return enhancer.enhance(1.05)


def apply_sunny_contrast(img: Image.Image) -> Image.Image:
    """Mô phỏng nắng gắt trưa hè miền Trung: Tăng tương phản và độ sáng."""
    enhancer_con = ImageEnhance.Contrast(img)
    img_con = enhancer_con.enhance(1.15)
    enhancer_bri = ImageEnhance.Brightness(img_con)
    return enhancer_bri.enhance(1.05)


def apply_crop_zoom(img: Image.Image) -> Image.Image:
    """Mô phỏng góc chụp cận cảnh hoặc du khách zoom số trên điện thoại (crop 88%)."""
    w, h = img.size
    crop_w = int(w * 0.88)
    crop_h = int(h * 0.88)
    left = (w - crop_w) // 2
    top = (h - crop_h) // 2
    cropped = img.crop((left, top, left + crop_w, top + crop_h))
    return cropped.resize((w, h), Image.Resampling.LANCZOS)


def apply_symmetry_flip(img: Image.Image) -> Image.Image:
    """Mô phỏng góc nhìn đối xứng trục của kiến trúc đền đài cung điện."""
    return img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)


AUGMENTATION_OPS = [
    ("rain_hue", "Mô phỏng mưa phùn sương mù Cố đô Huế", apply_rain_hue),
    ("golden_hour", "Mô phỏng nắng chiều hoàng hôn sông Hương", apply_golden_hour),
    ("sunny_noon", "Mô phỏng nắng hè tương phản cao", apply_sunny_contrast),
    ("crop_detail", "Mô phỏng góc chụp cận cảnh kiến trúc di sản", apply_crop_zoom),
    ("symmetry_view", "Mô phỏng góc nhìn đối xứng trục kiến trúc", apply_symmetry_flip),
]


def expand_dataset():
    print("=" * 80)
    print("🎨 TIẾN TRÌNH NÂNG CẤP KHO DỮ LIỆU THỊ GIÁC DI SẢN HUẾ LÊN 5.000 ẢNH")
    print("=" * 80)

    if not os.path.exists(METADATA_FILE):
        print(f"❌ Không tìm thấy file: {METADATA_FILE}")
        return

    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        metadata_list = json.load(f)

    current_count = len(metadata_list)
    print(f"📂 Hiện tại kho ảnh có: {current_count} ảnh gốc.")
    
    if current_count >= TARGET_TOTAL_IMAGES:
        print(f"✅ Kho ảnh đã có sẵn {current_count} ảnh (đạt/vượt mục tiêu {TARGET_TOTAL_IMAGES}).")
        return

    # Tạo backup nếu chưa có
    if not os.path.exists(BACKUP_METADATA_FILE):
        with open(BACKUP_METADATA_FILE, "w", encoding="utf-8") as f_bak:
            json.dump(metadata_list, f_bak, ensure_ascii=False, indent=2)
        print(f"💾 Đã sao lưu {current_count} bản ghi gốc sang: {os.path.basename(BACKUP_METADATA_FILE)}")

    needed_count = TARGET_TOTAL_IMAGES - current_count
    print(f"🎯 Cần bổ sung thêm: {needed_count} ảnh biến thể thực tế để đạt chuẩn 5.000 ảnh.")

    # Phân bổ đều các phép tăng cường trên toàn bộ 1.594 ảnh gốc
    # Trung bình mỗi ảnh gốc sẽ sinh ~2.14 ảnh biến thể
    aug_candidates = []
    round_idx = 0
    while len(aug_candidates) < needed_count:
        op_code, op_desc, op_func = AUGMENTATION_OPS[round_idx % len(AUGMENTATION_OPS)]
        # Xáo trộn danh sách ảnh gốc để các phép biến đổi được phân bổ đều cho 121 địa danh
        shuffled_indices = list(range(current_count))
        random.seed(42 + round_idx)
        random.shuffle(shuffled_indices)
        
        for idx in shuffled_indices:
            aug_candidates.append((idx, op_code, op_desc, op_func))
            if len(aug_candidates) >= needed_count:
                break
        round_idx += 1

    print(f"⚡ Đã lập kế hoạch tạo {len(aug_candidates)} ảnh biến thể với 5 kịch bản thị giác thực tế.")

    new_metadata_entries = []
    generated_count = 0
    t0 = time.time()

    for item_idx, op_code, op_desc, op_func in aug_candidates:
        orig_item = metadata_list[item_idx]
        orig_rel_path = orig_item["file_path"]
        orig_abs_path = os.path.join(PROJECT_ROOT, orig_rel_path.replace("/", os.sep))

        if not os.path.exists(orig_abs_path):
            continue

        try:
            with Image.open(orig_abs_path) as raw_img:
                raw_rgb = raw_img.convert("RGB")
                aug_img = op_func(raw_rgb)

            # Tên file mới theo chuẩn: <tên_gốc>_aug_<op_code>.jpg
            dir_name = os.path.dirname(orig_abs_path)
            base_name, ext = os.path.splitext(os.path.basename(orig_abs_path))
            new_filename = f"{base_name}_aug_{op_code}.jpg"
            new_abs_path = os.path.join(dir_name, new_filename)
            new_rel_path = os.path.relpath(new_abs_path, PROJECT_ROOT).replace(os.sep, "/")

            # Lưu ảnh JPEG với chất lượng 88 tối ưu dung lượng và sắc nét
            aug_img.save(new_abs_path, format="JPEG", quality=88, optimize=True)

            generated_count += 1
            new_id = f"img_aug_{orig_item['place_id']}_{generated_count:04d}"
            
            new_item = {
                "image_id": new_id,
                "place_id": orig_item["place_id"],
                "place_name": orig_item["place_name"],
                "sub_location": orig_item.get("sub_location", ""),
                "category": orig_item.get("category", "Attraction"),
                "file_path": new_rel_path,
                "source_title": f"{orig_item.get('source_title', '')} [{op_desc}]",
                "source_url": orig_item.get("source_url", ""),
                "caption": f"{orig_item.get('caption', '')} ({op_desc})",
                "latitude": orig_item.get("latitude", 0.0),
                "longitude": orig_item.get("longitude", 0.0),
                "is_augmented": True,
                "augmentation_type": op_code
            }
            new_metadata_entries.append(new_item)

            if generated_count % 500 == 0 or generated_count == needed_count:
                print(f"   📸 Đã sinh {generated_count}/{needed_count} ảnh mới ({time.time() - t0:.1f}s)...")
        except Exception as e:
            print(f"   ⚠️ Lỗi xử lý ảnh {orig_rel_path}: {e}")

    # Gộp danh sách metadata gốc + ảnh mới
    full_metadata_list = metadata_list + new_metadata_entries
    with open(METADATA_FILE, "w", encoding="utf-8") as f_out:
        json.dump(full_metadata_list, f_out, ensure_ascii=False, indent=2)

    total_images_on_disk = len(full_metadata_list)
    print("\n" + "=" * 80)
    print("🎉 HOÀN THÀNH TĂNG CƯỜNG DỮ LIỆU THỊ GIÁC!")
    print(f"📊 Tổng số ảnh ban đầu: {current_count} ảnh")
    print(f"📸 Số ảnh biến thể mới sinh: {len(new_metadata_entries)} ảnh")
    print(f"🏆 TỔNG CỘNG KHO ẢNH HIỆN TẠI: {total_images_on_disk} ẢNH")
    print(f"📄 File Metadata đã cập nhật: {METADATA_FILE}")
    print("=" * 80)


if __name__ == "__main__":
    expand_dataset()

