# -*- coding: utf-8 -*-
"""
THU THẬP BỘ DỮ LIỆU ẢNH DI SẢN, ẨM THỰC & LÀNG NGHỀ HUẾ THEO PHÂN ĐOẠN (MODULAR 9-PHASE CRAWLER)
Khóa luận Tốt nghiệp ngành Khoa học Dữ liệu và Trí tuệ Nhân tạo (DS&AI - HUET)
Đề tài: Spatial GraphRAG - Cố đô Huế

Thiết kế tối ưu cho máy tính cá nhân (Nhẹ máy, chia nhỏ thành 9 đợt, chống quá tải/nóng máy):
- Phase 1: Cứu 10 địa danh di tích đang thiếu ảnh (Bổ sung từ khóa Anh/Pháp/Việt, tải bù ~50 ảnh).
- Phase 2: 12 món Ẩm thực di sản Cố đô Huế (Bún bò, Cơm hến, Bánh bèo nậm lọc, Bánh ép, Chè hẻm...).
- Phase 3: 8 Làng nghề truyền thống & Điểm văn hóa (Hoa giấy Thanh Tiên, Tranh Sình, Đúc đồng, Nón bài thơ...).
- Phase 4: Nâng hạn ngạch (Scale-up Quota) cho 41 di tích lịch sử cốt lõi từ 12 lên 20 ảnh/địa điểm.
- Phase 5: 10 Cổ tự, Thiền viện & Di sản Tâm linh (Diệu Đế, Trúc Lâm Bạch Mã, Thánh Duyên, Thuyền Tôn...).
- Phase 6: 10 Ẩm thực Đường phố, Chợ truyền thống & Quà biếu Cố đô (Bánh canh Nam Phổ, Tôm chua, Mè xửng...).
- Phase 7: 10 Cảnh quan Đầm phá, Suối thác & Vịnh biển hoang sơ (Hồ Truồi, Thác A Nôr, Biển Cảnh Dương...).
- Phase 8: 10 Làng nghề Mỹ nghệ, Thổ cẩm & Trúc Chỉ (Nghệ thuật Trúc Chỉ, Gốm Phước Tích, Dèng A Lưới...).
- Phase 9: 10 Kiến trúc Pháp, Trường cổ & Check-in Cố đô (Quốc Học, Đồng Khánh, Khách sạn Morin, Điềm Phùng Thị...).
- Hỗ trợ lưu tức thời (Atomic Auto-Save): Mỗi địa danh tải xong lập tức ghi đĩa, bấm Ctrl+C không mất dữ liệu.
- Cơ chế giải phóng RAM triệt để: Đóng file ảnh ngay sau khi lưu, không tích tụ bộ nhớ đệm.
"""

import os
import sys
import json
import time
import io
import hashlib
import argparse
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

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
VI_WIKI_API = "https://vi.wikipedia.org/w/api.php"
EN_WIKI_API = "https://en.wikipedia.org/w/api.php"

HTTP_HEADERS = {
    "User-Agent": "HueHeritageVisualRAG/2.0 (contact@huetourism.edu.vn; University of Hue CS Dept)"
}

DOWNLOAD_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 (HueTourismVisualRAG; contact@huetourism.edu.vn)",
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    "Referer": "https://commons.wikimedia.org/"
}

# ==============================================================================
# DANH MỤC 121 ĐỊA DANH / MÓN ĂN / LÀNG NGHỀ HUẾ THEO 9 PHÂN ĐOẠN (PHASES)
# ==============================================================================

PHASE_1_LANDMARKS = [
    {
        "place_id": "place_9912",
        "name": "Suối Voi (Thác Voi Lộc Tiến)",
        "sub_name": "Khu sinh thái suối đá tự nhiên với tượng voi đá khổng lồ",
        "category": "Attraction",
        "wiki_title": "Suối Voi",
        "search_keywords": [
            "Elephant Springs Vietnam",
            "Elephant Springs Hue",
            "Suoi Voi Hue",
            "Thac Voi Loc Tien",
            "Elephant Springs Phu Loc",
            "Suoi Voi Vietnam"
        ],
        "lat": 16.2152,
        "lng": 108.0185,
        "phase": 1,
        "default_target": 12
    },
    {
        "place_id": "place_9914",
        "name": "Suối khoáng nóng Alba Thanh Tân",
        "sub_name": "Khu nghỉ dưỡng suối khoáng tự nhiên & trò chơi Zipline mạo hiểm",
        "category": "Attraction",
        "wiki_title": "Alba Thanh Tân",
        "search_keywords": [
            "Alba Thanh Tan",
            "Thanh Tan hot springs Hue",
            "Thanh Tan hot springs",
            "Alba Wellness Valley",
            "Suoi khoang nong Thanh Tan",
            "Phong Dien Thua Thien Hue"
        ],
        "lat": 16.5295,
        "lng": 107.4582,
        "phase": 1,
        "default_target": 12
    },
    {
        "place_id": "place_8904",
        "name": "Không gian lưu niệm Lê Bá Đảng (Lebadang Memory Space)",
        "sub_name": "Bảo tàng nghệ thuật đương đại trắng muốt giữa đồi núi Kim Sơn",
        "category": "Attraction",
        "wiki_title": "Lê Bá Đảng",
        "search_keywords": [
            "Lebadang Memory Space",
            "Lebadang museum Hue",
            "Le Ba Dang artist",
            "Lebadang Hue",
            "Khong gian Le Ba Dang",
            "Lebadang art"
        ],
        "lat": 16.404272,
        "lng": 107.58311,
        "phase": 1,
        "default_target": 12
    },
    {
        "place_id": "custom_attr_02",
        "name": "Đồi Vọng Cảnh",
        "sub_name": "Vọng lâu ngắm trọn khúc quanh mềm mại nhất của sông Hương",
        "category": "Attraction",
        "wiki_title": "Đồi Vọng Cảnh",
        "search_keywords": [
            "Vong Canh hill Hue",
            "Vong Canh Hue",
            "Vong Canh hill",
            "Doi Vong Canh",
            "Bunker Vong Canh",
            "Huong river Vong Canh"
        ],
        "lat": 16.4358,
        "lng": 107.5582,
        "phase": 1,
        "default_target": 12
    },
    {
        "place_id": "custom_attr_voire",
        "name": "Điện Voi Ré",
        "sub_name": "Đền thờ linh tượng quả cảm và các vị thần hộ quốc",
        "category": "Attraction",
        "wiki_title": "Điện Voi Ré",
        "search_keywords": [
            "Dien Voi Re",
            "Voi Re temple Hue",
            "Voi Re temple",
            "Voi Re Hue",
            "Elephant shrine Hue",
            "Long Chau Mieu"
        ],
        "lat": 16.4435,
        "lng": 107.5585,
        "phase": 1,
        "default_target": 12
    },
    {
        "place_id": "place_9909",
        "name": "Đấu trường Hổ Quyền",
        "sub_name": "Đấu trường La Mã phương Đông dành cho voi và hổ thời Nguyễn",
        "category": "Attraction",
        "wiki_title": "Hổ Quyền",
        "search_keywords": [
            "Ho Quyen",
            "Arenes de Hue",
            "Tiger Arena Hue",
            "Ho Quyen amphitheater",
            "Ho Quyen arena Hue",
            "Arènes de Hué",
            "Tiger Colosseum Hue"
        ],
        "lat": 16.4442,
        "lng": 107.5598,
        "phase": 1,
        "default_target": 12
    },
    {
        "place_id": "custom_attr_04",
        "name": "Điện Hòn Chén",
        "sub_name": "Điện thờ Mẫu Thiên Y A Na cheo leo vách núi Ngọc Trản bên sông Hương",
        "category": "Attraction",
        "wiki_title": "Điện Hòn Chén",
        "search_keywords": [
            "Hon Chen temple",
            "Temple de Hon Chen",
            "Dien Hon Chen",
            "Hon Chen Hue",
            "Ngoc Tran temple Hue",
            "Hue Hon Chen"
        ],
        "lat": 16.4258,
        "lng": 107.5389,
        "phase": 1,
        "default_target": 12
    },
    {
        "place_id": "custom_attr_thienlam",
        "name": "Chùa Thiền Lâm (Chùa Vàng Miến Điện)",
        "sub_name": "Ngôi chùa phong cách Phật giáo Nam truyền Theravada độc đáo",
        "category": "Attraction",
        "wiki_title": "Chùa Thiền Lâm (Huế)",
        "search_keywords": [
            "Chua Thien Lam Hue",
            "Thien Lam pagoda Hue",
            "Thien Lam pagoda",
            "Golden pagoda Hue",
            "Theravada Hue",
            "Chua Vang Thien Lam"
        ],
        "lat": 16.4425,
        "lng": 107.5748,
        "phase": 1,
        "default_target": 12
    },
    {
        "place_id": "custom_local_15",
        "name": "Cà Phê Mắt Biếc & Phố Cổ Bao Vinh",
        "sub_name": "Ngôi nhà gỗ cổ bối cảnh phim Mắt Biếc bên bến đò Bao Vinh",
        "category": "Attraction",
        "wiki_title": "Bao Vinh",
        "search_keywords": [
            "Bao Vinh ancient town",
            "Bao Vinh Hue",
            "Pho co Bao Vinh",
            "Mat Biec cafe Hue",
            "Mat Biec filming location",
            "Bao Vinh"
        ],
        "lat": 16.4885,
        "lng": 107.5892,
        "phase": 1,
        "default_target": 12
    },
    {
        "place_id": "custom_attr_hotinhtam",
        "name": "Hồ Tịnh Tâm (Kinh thành Huế)",
        "sub_name": "Hồ sen ngự uyển đệ nhất danh thắng chốn Hoàng thành",
        "category": "Attraction",
        "wiki_title": "Hồ Tịnh Tâm",
        "search_keywords": [
            "Tinh Tam lake Hue",
            "Ho Tinh Tam",
            "Tinh Tam lake",
            "Lotus lake Hue Citadel",
            "Ho Tinh Tam Kinh thanh Hue"
        ],
        "lat": 16.4758,
        "lng": 107.5792,
        "phase": 1,
        "default_target": 12
    }
]

PHASE_2_CULINARY = [
    {
        "place_id": "culinary_bun_bo",
        "name": "Bún bò Huế",
        "sub_name": "Món ăn linh hồn Cố đô (nước dùng sả ruốc, giò heo, chả cua)",
        "category": "Culinary",
        "wiki_title": "Bún bò Huế",
        "search_keywords": [
            "Bun bo Hue",
            "Bun bo",
            "Hue beef noodle soup",
            "Bun bo Hue soup"
        ],
        "lat": 16.4715,
        "lng": 107.585,
        "phase": 2,
        "default_target": 12
    },
    {
        "place_id": "culinary_com_hen",
        "name": "Cơm hến & Bún hến Cồn Hến",
        "sub_name": "Đặc sản sông Hương dân dã đậm đà vị ruốc ớt cay nồng và tóp mỡ",
        "category": "Culinary",
        "wiki_title": "Cơm hến",
        "search_keywords": [
            "Com hen",
            "Com hen Hue",
            "Bun hen Hue",
            "Baby basket clams rice Hue",
            "Com hen Con Hen"
        ],
        "lat": 16.4782,
        "lng": 107.5995,
        "phase": 2,
        "default_target": 12
    },
    {
        "place_id": "culinary_banh_beo",
        "name": "Bánh bèo chén Cố đô",
        "sub_name": "Bánh bèo chén đất nung rắc tôm chấy, tóp mỡ, nước mắm ngọt cay",
        "category": "Culinary",
        "wiki_title": "Bánh bèo",
        "search_keywords": [
            "Banh beo",
            "Banh beo Hue",
            "Water fern cake Vietnam",
            "Banh beo chen",
            "Banh beo chén"
        ],
        "lat": 16.458,
        "lng": 107.592,
        "phase": 2,
        "default_target": 12
    },
    {
        "place_id": "culinary_banh_bot_loc",
        "name": "Bánh bột lọc xứ Huế",
        "sub_name": "Bánh lọc gói lá chuối nhân tôm thịt đậm đà vỏ trong suốt dai ngon",
        "category": "Culinary",
        "wiki_title": "Bánh bột lọc",
        "search_keywords": [
            "Banh bot loc",
            "Banh bot loc Hue",
            "Tapioca dumpling Hue",
            "Banh loc Hue",
            "Bánh bột lọc"
        ],
        "lat": 16.463,
        "lng": 107.589,
        "phase": 2,
        "default_target": 12
    },
    {
        "place_id": "culinary_banh_nam",
        "name": "Bánh nậm Huế",
        "sub_name": "Bánh bột gạo mỏng mịn gói lá dong nhân tôm thịt băm mềm tan",
        "category": "Culinary",
        "wiki_title": "Bánh nậm",
        "search_keywords": [
            "Banh nam",
            "Banh nam Hue",
            "Flat rice dumpling Hue",
            "Bánh nậm"
        ],
        "lat": 16.46,
        "lng": 107.587,
        "phase": 2,
        "default_target": 12
    },
    {
        "place_id": "culinary_banh_khoai",
        "name": "Bánh khoái Hoàng gia Huế",
        "sub_name": "Bánh chiên giòn rụm màu vàng nghệ kèm nước lèo đậu gan béo bùi",
        "category": "Culinary",
        "wiki_title": "Bánh khoái",
        "search_keywords": [
            "Banh khoai",
            "Banh khoai Hue",
            "Hue pancake",
            "Banh khoai Lac Thien",
            "Bánh khoái"
        ],
        "lat": 16.4735,
        "lng": 107.5875,
        "phase": 2,
        "default_target": 12
    },
    {
        "place_id": "culinary_banh_ep",
        "name": "Bánh ép Thuận An - Huế",
        "sub_name": "Món ăn vặt trứ danh ép nóng giòn thơm nức mũi chấm nước mắm ớt chua ngọt",
        "category": "Culinary",
        "wiki_title": "Bánh ép",
        "search_keywords": [
            "Banh ep Hue",
            "Banh ep Thuan An",
            "Banh ep",
            "Hue pressed cake"
        ],
        "lat": 16.545,
        "lng": 107.64,
        "phase": 2,
        "default_target": 12
    },
    {
        "place_id": "culinary_che_heo_quay",
        "name": "Chè bột lọc heo quay & Chè Hẻm Huế",
        "sub_name": "Nét chấm phá ẩm thực Cố đô giao thoa mặn ngọt độc nhất vô nhị",
        "category": "Culinary",
        "wiki_title": "Chè (ẩm thực)",
        "search_keywords": [
            "Che bot loc heo quay",
            "Che Hue",
            "Che hem Hue",
            "Sweet soup Hue",
            "Chè heo quay"
        ],
        "lat": 16.467,
        "lng": 107.593,
        "phase": 2,
        "default_target": 12
    },
    {
        "place_id": "culinary_nem_lui",
        "name": "Nem lụi nướng than hoa Huế",
        "sub_name": "Thịt quết nướng sả thơm phức cuốn bánh tráng rau sống và chấm nước lèo",
        "category": "Culinary",
        "wiki_title": "Nem nướng",
        "search_keywords": [
            "Nem lui",
            "Nem lui Hue",
            "Hue lemongrass pork skewers",
            "Nem nuong Hue",
            "Nem lụi"
        ],
        "lat": 16.471,
        "lng": 107.586,
        "phase": 2,
        "default_target": 12
    },
    {
        "place_id": "culinary_bun_mam_nem",
        "name": "Bún mắm nêm & Bún thịt nướng Huế",
        "sub_name": "Món ăn đậm vị mắm nêm cá cơm và thịt nướng mè thơm lừng",
        "category": "Culinary",
        "wiki_title": "Bún mắm",
        "search_keywords": [
            "Bun mam nem Hue",
            "Bun mam nem",
            "Bun thit nuong Hue",
            "Bún mắm nêm"
        ],
        "lat": 16.465,
        "lng": 107.59,
        "phase": 2,
        "default_target": 12
    },
    {
        "place_id": "culinary_ca_phe_muoi",
        "name": "Cà phê muối xứ Huế",
        "sub_name": "Thức uống khởi nguồn từ Cố đô với lớp kem muối mặn mà béo ngậy",
        "category": "Culinary",
        "wiki_title": "Cà phê muối",
        "search_keywords": [
            "Ca phe muoi Hue",
            "Salt coffee Hue",
            "Ca phe muoi",
            "Salt coffee Vietnam"
        ],
        "lat": 16.4608,
        "lng": 107.595,
        "phase": 2,
        "default_target": 12
    },
    {
        "place_id": "culinary_tra_cung_dinh",
        "name": "Trà Cung Đình Huế",
        "sub_name": "Danh trà thảo mộc tiến vua chế tác từ 16 vị thảo dược quý bồi bổ sức khỏe",
        "category": "Culinary",
        "wiki_title": "Trà Cung đình Huế",
        "search_keywords": [
            "Tra cung dinh Hue",
            "Royal tea Hue",
            "Tra Cung Dinh",
            "Imperial tea Hue",
            "Trà Cung Đình"
        ],
        "lat": 16.469,
        "lng": 107.582,
        "phase": 2,
        "default_target": 12
    }
]

PHASE_3_CRAFT_CULTURE = [
    {
        "place_id": "craft_hoa_giay_thanh_tien",
        "name": "Làng hoa giấy Thanh Tiên",
        "sub_name": "Làng nghề hoa sen giấy thủ công hơn 300 năm tuổi ven sông Hương",
        "category": "CraftVillage",
        "wiki_title": "Thanh Tiên",
        "search_keywords": [
            "Thanh Tien paper flowers",
            "Hoa giay Thanh Tien",
            "Thanh Tien village Hue",
            "Lang hoa giay Thanh Tien"
        ],
        "lat": 16.512,
        "lng": 107.615,
        "phase": 3,
        "default_target": 12
    },
    {
        "place_id": "craft_tranh_lang_sinh",
        "name": "Làng tranh dân gian Sình",
        "sub_name": "Dòng tranh mộc bản cổ truyền thờ cúng xứ Huế bên bờ sông Bồ",
        "category": "CraftVillage",
        "wiki_title": "Tranh làng Sình",
        "search_keywords": [
            "Tranh lang Sinh",
            "Sinh village painting",
            "Lang Sinh Hue",
            "Sinh village folk painting"
        ],
        "lat": 16.516,
        "lng": 107.608,
        "phase": 3,
        "default_target": 12
    },
    {
        "place_id": "craft_duc_dong_phuong_duc",
        "name": "Làng đúc đồng Phường Đúc",
        "sub_name": "Làng nghề đúc Đại hồng chung và Cửu Đỉnh bảo vật quốc gia",
        "category": "CraftVillage",
        "wiki_title": "Phường Đúc",
        "search_keywords": [
            "Phuong Duc bronze",
            "Phuong Duc Hue",
            "Lang duc dong Phuong Duc",
            "Hue bronze casting"
        ],
        "lat": 16.452,
        "lng": 107.568,
        "phase": 3,
        "default_target": 12
    },
    {
        "place_id": "craft_non_la_tay_ho",
        "name": "Làng nón lá Tây Hồ (Phú Vang)",
        "sub_name": "Cái nôi nón bài thơ xứ Huế mỏng nhẹ soi bóng di sản Cố đô",
        "category": "CraftVillage",
        "wiki_title": "Nón bài thơ",
        "search_keywords": [
            "Non la Hue",
            "Non bai tho Hue",
            "Tay Ho hat village",
            "Lang non Tay Ho",
            "Hue conical hat"
        ],
        "lat": 16.465,
        "lng": 107.652,
        "phase": 3,
        "default_target": 12
    },
    {
        "place_id": "craft_non_la_phu_cam",
        "name": "Làng nghề chằm nón Phủ Cam",
        "sub_name": "Làng chằm nón lá truyền thống lâu đời bên bờ sông An Cựu",
        "category": "CraftVillage",
        "wiki_title": "Phủ Cam",
        "search_keywords": [
            "Non la Phu Cam",
            "Phu Cam hat village",
            "Cham non Phu Cam",
            "Non Hue"
        ],
        "lat": 16.455,
        "lng": 107.585,
        "phase": 3,
        "default_target": 12
    },
    {
        "place_id": "custom_attr_cau_go_lim",
        "name": "Cầu đi bộ gỗ lim Sông Hương",
        "sub_name": "Đường dạo bộ lát gỗ lim Nam Phi sát mặt nước sông Hương thơ mộng",
        "category": "Attraction",
        "wiki_title": "",
        "search_keywords": [
            "Cau go lim Hue",
            "Song Huong pedestrian bridge",
            "Hue boardwalk",
            "Cau di bo song Huong"
        ],
        "lat": 16.467,
        "lng": 107.588,
        "phase": 3,
        "default_target": 12
    },
    {
        "place_id": "custom_attr_duyet_thi_duong",
        "name": "Nhà hát Duyệt Thị Đường",
        "sub_name": "Nhà hát cổ nhất Việt Nam biểu diễn Nhã nhạc Cung đình Huế (UNESCO)",
        "category": "Attraction",
        "wiki_title": "Duyệt Thị Đường",
        "search_keywords": [
            "Duyet Thi Duong theater",
            "Duyet Thi Duong Hue",
            "Nha hat Duyet Thi Duong",
            "Royal theater Hue"
        ],
        "lat": 16.47,
        "lng": 107.579,
        "phase": 3,
        "default_target": 12
    },
    {
        "place_id": "custom_attr_kim_long",
        "name": "Phố cổ & Nhà rường Kim Long",
        "sub_name": "Vùng đất thủ phủ xưa với hàng cau và những ngôi nhà rường cổ tích",
        "category": "Attraction",
        "wiki_title": "Kim Long, Huế",
        "search_keywords": [
            "Kim Long Hue",
            "Nha ruong Kim Long",
            "Kim Long ancient village",
            "Kim Long garden house"
        ],
        "lat": 16.458,
        "lng": 107.555,
        "phase": 3,
        "default_target": 12
    }
]

PHASE_4_CORE_HERITAGE = [
    {
        "place_id": "place_8875",
        "name": "Đại Nội Huế (Hoàng Thành & Kinh Thành)",
        "sub_name": "Ngọ Môn & Kỳ Đài",
        "category": "Attraction",
        "wiki_title": "Hoàng thành Huế",
        "search_keywords": [
            "Ngo Mon Hue",
            "Imperial City Hue",
            "Kỳ Đài Huế",
            "Kinh thanh Hue",
            "Meridian Gate Hue"
        ],
        "lat": 16.468744,
        "lng": 107.57835,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "place_8884",
        "name": "Điện Thái Hòa & Tử Cấm Thành",
        "sub_name": "Ngai vàng triều Nguyễn & Sân Đại Triều Nghi",
        "category": "Attraction",
        "wiki_title": "Điện Thái Hòa (Hoàng thành Huế)",
        "search_keywords": [
            "Thai Hoa Palace Hue",
            "Dien Thai Hoa Hue",
            "Tu Cam Thanh Hue",
            "Purple Forbidden City Hue"
        ],
        "lat": 16.46925,
        "lng": 107.57792,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "custom_attr_the_mieu",
        "name": "Thế Tổ Miếu & Cửu Đỉnh",
        "sub_name": "Nơi thờ các vua triều Nguyễn & 9 đỉnh đồng bảo vật quốc gia",
        "category": "Attraction",
        "wiki_title": "Thế Tổ Miếu (Hoàng thành Huế)",
        "search_keywords": [
            "The Mieu Hue",
            "Nine Dynastic Urns Hue",
            "Cuu Dinh Hue",
            "Hien Lam Cac Hue"
        ],
        "lat": 16.4678,
        "lng": 107.5765,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "custom_attr_dien_tho",
        "name": "Cung Diên Thọ & Cung Trường Sanh",
        "sub_name": "Chốn hoàng cung cựu hoàng thái hậu triều Nguyễn",
        "category": "Attraction",
        "wiki_title": "Cung Diên Thọ",
        "search_keywords": [
            "Dien Tho residence Hue",
            "Cung Dien Tho",
            "Cung Truong Sanh Hue",
            "Truong Sanh palace"
        ],
        "lat": 16.4705,
        "lng": 107.5761,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "place_9917",
        "name": "Bảo tàng Cổ vật Cung đình Huế (Điện Long An)",
        "sub_name": "Tuyệt tác kiến trúc gỗ trùng thiềm điệp ốc thời Thiệu Trị",
        "category": "Attraction",
        "wiki_title": "Bảo tàng Cổ vật Cung đình Huế",
        "search_keywords": [
            "Hue Museum of Royal Antiquities",
            "Dien Long An Hue",
            "Long An Palace Hue",
            "Bao tang co vat Hue"
        ],
        "lat": 16.4712,
        "lng": 107.5815,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "place_8879",
        "name": "Lăng Khải Định (Ứng Lăng)",
        "sub_name": "Sân chầu tượng đá & Khải Thành Điện khảm sành sứ",
        "category": "Attraction",
        "wiki_title": "Lăng Khải Định",
        "search_keywords": [
            "Khai Dinh tomb",
            "Khai Thanh Palace Hue",
            "Lang Khai Dinh",
            "Tomb of Khai Dinh"
        ],
        "lat": 16.3986,
        "lng": 107.5906,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "place_8880",
        "name": "Lăng Tự Đức (Khiêm Lăng)",
        "sub_name": "Hồ Lưu Khiêm, Xung Khiêm Tạ & Nhà bia Khiêm Cung Ký",
        "category": "Attraction",
        "wiki_title": "Lăng Tự Đức",
        "search_keywords": [
            "Tu Duc tomb",
            "Luu Khiem lake Hue",
            "Lang Tu Duc",
            "Tomb of Tu Duc",
            "Xung Khiem Ta"
        ],
        "lat": 16.4328,
        "lng": 107.5647,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "place_8878",
        "name": "Lăng Minh Mạng (Hiếu Lăng)",
        "sub_name": "Hồ Tân Nguyệt, Cầu Thông Minh Chính Trực & Minh Lâu",
        "category": "Attraction",
        "wiki_title": "Lăng Minh Mạng",
        "search_keywords": [
            "Minh Mang tomb",
            "Minh Lau Hue",
            "Lang Minh Mang",
            "Tomb of Minh Mang"
        ],
        "lat": 16.387653,
        "lng": 107.56918,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "custom_attr_01",
        "name": "Lăng Gia Long (Thiên Thọ Lăng)",
        "sub_name": "Quần thể lăng mộ vua sáng lập triều Nguyễn giữa rừng thông",
        "category": "Attraction",
        "wiki_title": "Lăng Gia Long",
        "search_keywords": [
            "Gia Long tomb",
            "Lang Gia Long",
            "Thien Tho tomb Hue",
            "Tomb of Gia Long"
        ],
        "lat": 16.3534,
        "lng": 107.5756,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "place_8881",
        "name": "Lăng Đồng Khánh (Tư Lăng)",
        "sub_name": "Điện Ngưng Hy kiến trúc sơn son thếp vàng giao thoa Á - Âu",
        "category": "Attraction",
        "wiki_title": "Lăng Đồng Khánh",
        "search_keywords": [
            "Dong Khanh tomb",
            "Lang Dong Khanh",
            "Dien Ngung Hy Hue",
            "Tomb of Dong Khanh"
        ],
        "lat": 16.429956,
        "lng": 107.56784,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "place_9906",
        "name": "Lăng Thiệu Trị (Xương Lăng)",
        "sub_name": "Lăng tẩm thanh bình nép mình dưới chân núi Thuận Đạo",
        "category": "Attraction",
        "wiki_title": "Lăng Thiệu Trị",
        "search_keywords": [
            "Thieu Tri tomb",
            "Lang Thieu Tri",
            "Tomb of Thieu Tri"
        ],
        "lat": 16.4172,
        "lng": 107.5721,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "place_9907",
        "name": "Lăng Dục Đức (An Lăng)",
        "sub_name": "Nơi an nghỉ của 3 thế hệ vua Dục Đức, Thành Thái và Duy Tân",
        "category": "Attraction",
        "wiki_title": "Lăng Dục Đức",
        "search_keywords": [
            "Duc Duc tomb",
            "Lang Duc Duc",
            "An Lang Hue"
        ],
        "lat": 16.4485,
        "lng": 107.5925,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "custom_local_31",
        "name": "Cung An Định",
        "sub_name": "Tòa lâu đài tráng lệ giao thoa kiến trúc Pháp - Việt bên sông An Cựu",
        "category": "Attraction",
        "wiki_title": "Cung An Định",
        "search_keywords": [
            "An Dinh palace",
            "Cung An Dinh Hue",
            "An Dinh residence",
            "Khach san An Dinh"
        ],
        "lat": 16.4578,
        "lng": 107.5952,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "place_9910",
        "name": "Đàn Nam Giao",
        "sub_name": "Nơi các vua triều Nguyễn tổ chức đại lễ tế Trời Đất hàng năm",
        "category": "Attraction",
        "wiki_title": "Đàn Nam Giao (triều Nguyễn)",
        "search_keywords": [
            "Dan Nam Giao Hue",
            "Esplanade of Sacrifice to Heaven and Earth",
            "Nam Giao altar"
        ],
        "lat": 16.4428,
        "lng": 107.5878,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "place_8922",
        "name": "Văn Miếu Huế (Văn Thánh Miếu)",
        "sub_name": "Biểu tượng tôn vinh Nho học với 32 tấm bia tiến sĩ thời Nguyễn",
        "category": "Attraction",
        "wiki_title": "Văn Miếu (Huế)",
        "search_keywords": [
            "Van Mieu Hue",
            "Van Thanh Hue",
            "Temple of Literature Hue",
            "Van Thanh Mieu Hue"
        ],
        "lat": 16.4538,
        "lng": 107.5422,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "custom_attr_quoctugiam",
        "name": "Quốc Tử Giám Huế",
        "sub_name": "Trường đại học duy nhất thời phong kiến còn sót lại ở miền Trung",
        "category": "Attraction",
        "wiki_title": "Quốc Tử Giám (Huế)",
        "search_keywords": [
            "Quoc Tu Giam Hue",
            "Imperial Academy Hue",
            "Truong Quoc Tu Giam"
        ],
        "lat": 16.4718,
        "lng": 107.5818,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "place_8876",
        "name": "Chùa Thiên Mụ",
        "sub_name": "Tháp Phước Duyên 7 tầng soi bóng xuống dòng sông Hương",
        "category": "Attraction",
        "wiki_title": "Chùa Thiên Mụ",
        "search_keywords": [
            "Thien Mu pagoda",
            "Chua Thien Mu",
            "Phuoc Duyen tower Hue",
            "Thien Mu Hue"
        ],
        "lat": 16.4528,
        "lng": 107.5458,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "place_8886",
        "name": "Chùa Từ Hiếu",
        "sub_name": "Ngôi cổ tự chốn thiền môn gắn liền nghĩa trang thái giám triều Nguyễn",
        "category": "Attraction",
        "wiki_title": "Chùa Từ Hiếu",
        "search_keywords": [
            "Tu Hieu pagoda",
            "Chua Tu Hieu",
            "Eunuch pagoda Hue",
            "Thich Nhat Hanh Tu Hieu"
        ],
        "lat": 16.4358,
        "lng": 107.5752,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "custom_attr_05",
        "name": "Chùa Huyền Không Sơn Thượng",
        "sub_name": "Không gian thiền tịnh thanh khiết giữa thung lũng thông reo",
        "category": "Attraction",
        "wiki_title": "Chùa Huyền Không Sơn Thượng",
        "search_keywords": [
            "Huyen Khong Son Thuong",
            "Chua Huyen Khong",
            "Huyen Khong pagoda Hue"
        ],
        "lat": 16.4722,
        "lng": 107.5135,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "custom_local_30",
        "name": "Chùa Từ Đàm",
        "sub_name": "Trung tâm Phật giáo xứ Huế gắn liền phong trào Phật giáo 1963",
        "category": "Attraction",
        "wiki_title": "Chùa Từ Đàm",
        "search_keywords": [
            "Tu Dam pagoda",
            "Chua Tu Dam Hue",
            "Tu Dam Hue"
        ],
        "lat": 16.4498,
        "lng": 107.5815,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "custom_attr_baoquoc",
        "name": "Chùa Báo Quốc",
        "sub_name": "Tổ đình cổ kính bậc nhất xứ Huế trên đồi Hàm Long",
        "category": "Attraction",
        "wiki_title": "Chùa Báo Quốc (Huế)",
        "search_keywords": [
            "Chua Bao Quoc Hue",
            "Bao Quoc pagoda",
            "Ham Long hill pagoda"
        ],
        "lat": 16.4542,
        "lng": 107.5832,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "custom_local_20",
        "name": "Nhà Thờ Dòng Chúa Cứu Thế Huế",
        "sub_name": "Kiến trúc Gothic tam giác độc đáo bậc nhất miền Trung",
        "category": "Attraction",
        "wiki_title": "Nhà thờ Dòng Chúa Cứu Thế (Huế)",
        "search_keywords": [
            "Redemptorist Church Hue",
            "Nha tho Dong Chua Cuu The Hue",
            "Our Lady of Perpetual Help Church Hue"
        ],
        "lat": 16.4632,
        "lng": 107.5975,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "place_9918",
        "name": "Nhà Thờ Chính Tòa Phủ Cam",
        "sub_name": "Kiến trúc hiện đại của KTS Ngô Viết Thụ trên đồi Phước Quả",
        "category": "Attraction",
        "wiki_title": "Nhà thờ chính tòa Phủ Cam",
        "search_keywords": [
            "Phu Cam Cathedral Hue",
            "Nha tho Phu Cam",
            "Phu Cam church"
        ],
        "lat": 16.4528,
        "lng": 107.5862,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "place_8882",
        "name": "Sông Hương & Bến Thuyền Tòa Khâm",
        "sub_name": "Dòng sông di sản ngắm hoàng hôn và nghe Ca Huế trên thuyền rồng",
        "category": "Attraction",
        "wiki_title": "Sông Hương",
        "search_keywords": [
            "Perfume River Hue",
            "Song Huong Hue",
            "Toa Kham pier",
            "Dragon boat Perfume River"
        ],
        "lat": 16.4688,
        "lng": 107.5898,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "custom_local_21",
        "name": "Công Viên Hồ Thủy Tiên (Tượng Rồng)",
        "sub_name": "Công viên nước bỏ hoang kỳ bí nổi tiếng truyền thông quốc tế",
        "category": "Attraction",
        "wiki_title": "Hồ Thủy Tiên",
        "search_keywords": [
            "Ho Thuy Tien abandoned water park",
            "Ho Thuy Tien dragon",
            "Abandoned water park Hue",
            "Thuy Tien lake"
        ],
        "lat": 16.4085,
        "lng": 107.5752,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "custom_attr_thienan",
        "name": "Đồi Thiên An & Đan Viện Benedict",
        "sub_name": "Đà Lạt giữa lòng cố đô với đồi thông xanh ngắt và tu viện cổ kính",
        "category": "Attraction",
        "wiki_title": "Đan viện Thiên An",
        "search_keywords": [
            "Thien An hill Hue",
            "Dan vien Thien An",
            "Thien An monastery Hue",
            "Doi Thien An"
        ],
        "lat": 16.4112,
        "lng": 107.5678,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "place_8918",
        "name": "Phá Tam Giang (Đầm Chuồn)",
        "sub_name": "Vùng đầm phá nước lợ lớn nhất Đông Nam Á rực rỡ hoàng hôn",
        "category": "Attraction",
        "wiki_title": "Phá Tam Giang",
        "search_keywords": [
            "Tam Giang lagoon Hue",
            "Pha Tam Giang",
            "Dam Chuon Hue",
            "Tam Giang lagoon sunset"
        ],
        "lat": 16.5478,
        "lng": 107.6152,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "custom_local_32",
        "name": "Đầm Lập An & Làng Chài Lăng Cô",
        "sub_name": "Tuyệt tình cốc xứ Huế dưới chân đèo Hải Vân",
        "category": "Attraction",
        "wiki_title": "Đầm Lập An",
        "search_keywords": [
            "Lap An lagoon",
            "Dam Lap An Hue",
            "Lang Co fishing village",
            "Lap An oyster farm"
        ],
        "lat": 16.2358,
        "lng": 108.0582,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "place_8917",
        "name": "Bãi biển Lăng Cô & Vịnh Lăng Cô",
        "sub_name": "Top những vịnh biển đẹp nhất thế giới bên chân đèo Hải Vân",
        "category": "Attraction",
        "wiki_title": "Lăng Cô",
        "search_keywords": [
            "Lang Co beach Hue",
            "Lang Co bay",
            "Vinh Lang Co",
            "Lang Co Vietnam"
        ],
        "lat": 16.2285,
        "lng": 108.0692,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "place_8895",
        "name": "Đèo Hải Vân (Hải Vân Quan)",
        "sub_name": "Thiên hạ đệ nhất hùng quan nối liền Huế và Đà Nẵng",
        "category": "Attraction",
        "wiki_title": "Đèo Hải Vân",
        "search_keywords": [
            "Hai Van Pass",
            "Hai Van Quan gate",
            "Deo Hai Van",
            "Hai Van Pass Vietnam"
        ],
        "lat": 16.1912,
        "lng": 108.1315,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "place_8877",
        "name": "Vườn Quốc gia Bạch Mã",
        "sub_name": "Khu nghỉ dưỡng sinh thái trên đỉnh núi cao với thác Đỗ Quyên hùng vĩ",
        "category": "Attraction",
        "wiki_title": "Vườn quốc gia Bạch Mã",
        "search_keywords": [
            "Bach Ma National Park",
            "Vuon quoc gia Bach Ma",
            "Do Quyen waterfall Bach Ma",
            "Hai Vong Dai Bach Ma"
        ],
        "lat": 16.1985,
        "lng": 107.8522,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "place_9913",
        "name": "Bãi biển Thuận An",
        "sub_name": "Cửa biển lịch sử và bãi tắm cát trắng mịn đón bình minh Cố đô",
        "category": "Attraction",
        "wiki_title": "Cửa Thuận An",
        "search_keywords": [
            "Thuan An beach Hue",
            "Cua Thuan An",
            "Thuan An port Hue"
        ],
        "lat": 16.5512,
        "lng": 107.6435,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "custom_attr_rucha",
        "name": "Rừng ngập mặn nguyên sinh Rú Chá",
        "sub_name": "Rừng ngập mặn nguyên sinh duy nhất còn sót lại trên phá Tam Giang",
        "category": "Attraction",
        "wiki_title": "Rú Chá",
        "search_keywords": [
            "Ru Cha mangrove forest",
            "Ru Cha Hue",
            "Rung ngap man Ru Cha",
            "Ru Cha autumn"
        ],
        "lat": 16.5412,
        "lng": 107.6328,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "place_8919",
        "name": "Cầu Trường Tiền",
        "sub_name": "Cây cầu 6 vài 12 nhịp biểu tượng thi ca bắc qua sông Hương",
        "category": "Attraction",
        "wiki_title": "Cầu Trường Tiền",
        "search_keywords": [
            "Truong Tien bridge",
            "Cau Truong Tien Hue",
            "Trang Tien bridge Hue",
            "Eiffel bridge Hue"
        ],
        "lat": 16.4682,
        "lng": 107.5912,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "place_8885",
        "name": "Cầu ngói Thanh Toàn",
        "sub_name": "Cây cầu ngói cổ kính kiến trúc thượng gia hạ kiều hiếm có",
        "category": "Attraction",
        "wiki_title": "Cầu ngói Thanh Toàn",
        "search_keywords": [
            "Thanh Toan tile roof bridge",
            "Cau ngoi Thanh Toan",
            "Thanh Toan bridge Hue"
        ],
        "lat": 16.4578,
        "lng": 107.6395,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "custom_attr_davien",
        "name": "Cầu Dã Viên & Cồn Dã Viên",
        "sub_name": "Bạch Hổ của Kinh thành Huế với công viên cầu cảnh hoàng hôn",
        "category": "Attraction",
        "wiki_title": "Cồn Dã Viên",
        "search_keywords": [
            "Da Vien bridge Hue",
            "Con Da Vien Hue",
            "Cau Da Vien"
        ],
        "lat": 16.4568,
        "lng": 107.5742,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "custom_attr_03",
        "name": "Làng hương Thủy Xuân",
        "sub_name": "Con đường chân hương xòe quạt đa sắc màu rực rỡ",
        "category": "Attraction",
        "wiki_title": "Làng hương Thủy Xuân",
        "search_keywords": [
            "Thuy Xuan incense",
            "Incense Hue Vietnam",
            "Thuy Xuan Hue",
            "Lang huong Thuy Xuan"
        ],
        "lat": 16.4412,
        "lng": 107.5684,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "place_8920",
        "name": "Chợ Đông Ba",
        "sub_name": "Cổng chợ & Tháp đồng hồ trung tâm giao thương ẩm thực Huế",
        "category": "Attraction",
        "wiki_title": "Chợ Đông Ba",
        "search_keywords": [
            "Dong Ba market Hue",
            "Dong Ba market",
            "Cho Dong Ba",
            "Dong Ba market Vietnam"
        ],
        "lat": 16.47262,
        "lng": 107.5885,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "custom_attr_con_hen",
        "name": "Cồn Hến (Đảo Cồn Hến)",
        "sub_name": "Cù lao sông Hương (Thanh Long) cái nôi của Cơm hến & Chè bắp",
        "category": "Attraction",
        "wiki_title": "Cồn Hến",
        "search_keywords": [
            "Con Hen Hue",
            "Con Hen island",
            "Con Hen river Hue",
            "Con Hen"
        ],
        "lat": 16.4782,
        "lng": 107.5995,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "custom_attr_anhien",
        "name": "Nhà Vườn An Hiên (Kim Long)",
        "sub_name": "Nhà rường truyền thống xứ Huế với vườn cây ăn trái cổ kính",
        "category": "Attraction",
        "wiki_title": "Nhà vườn An Hiên",
        "search_keywords": [
            "An Hien",
            "Nha vuon An Hien",
            "An Hien house",
            "An Hien garden Hue"
        ],
        "lat": 16.4558,
        "lng": 107.5518,
        "phase": 4,
        "default_target": 20
    },
    {
        "place_id": "custom_attr_phuoctich",
        "name": "Làng cổ Phước Tích",
        "sub_name": "Làng di sản gốm cổ và quần thể nhà rường cổ kính bên sông Ô Lâu",
        "category": "Attraction",
        "wiki_title": "Phước Tích",
        "search_keywords": [
            "Phuoc Tich ancient village",
            "Lang co Phuoc Tich",
            "Phuoc Tich pottery Hue"
        ],
        "lat": 16.6575,
        "lng": 107.3042,
        "phase": 4,
        "default_target": 20
    }
]

PHASE_5_SPIRITUAL = [
    {
        "place_id": "spiri_chua_dieu_de",
        "name": "Chùa Diệu Đế",
        "sub_name": "Quốc tự thứ ba triều Nguyễn với bích họa Long vân khế hội bên bờ sông Đông Ba",
        "category": "Attraction",
        "wiki_title": "Chùa Diệu Đế",
        "search_keywords": [
            "Dieu De pagoda",
            "Chua Dieu De Hue",
            "Dieu De Pagoda Hue",
            "Dieu De National pagoda"
        ],
        "lat": 16.476,
        "lng": 107.59,
        "phase": 5,
        "default_target": 12
    },
    {
        "place_id": "spiri_thien_vien_bach_ma",
        "name": "Thiền viện Trúc Lâm Bạch Mã",
        "sub_name": "Danh thắng thiền viện bồng lai tiên cảnh giữa lòng hồ Truồi",
        "category": "Attraction",
        "wiki_title": "Thiền viện Trúc Lâm Bạch Mã",
        "search_keywords": [
            "Truc Lam Bach Ma",
            "Thien vien Truc Lam Bach Ma",
            "Bach Ma Zen Monastery",
            "Ho Truoi Bach Ma"
        ],
        "lat": 16.275,
        "lng": 107.785,
        "phase": 5,
        "default_target": 12
    },
    {
        "place_id": "spiri_chua_thanh_duyen",
        "name": "Chùa Thánh Duyên",
        "sub_name": "Quốc tự cổ kính trên núi Túy Vân ngắm toàn cảnh đầm Cầu Hai và cửa Tư Hiền",
        "category": "Attraction",
        "wiki_title": "Chùa Thánh Duyên",
        "search_keywords": [
            "Thanh Duyen pagoda",
            "Chua Thanh Duyen",
            "Tuy Van pagoda",
            "Nui Tuy Van Hue"
        ],
        "lat": 16.328,
        "lng": 107.978,
        "phase": 5,
        "default_target": 12
    },
    {
        "place_id": "spiri_chua_thuyen_ton",
        "name": "Chùa Thuyền Tôn",
        "sub_name": "Tổ đình thiền môn cổ kính trên núi Ngũ Phong gắn liền lịch sử các chúa Nguyễn",
        "category": "Attraction",
        "wiki_title": "Chùa Thuyền Tôn",
        "search_keywords": [
            "Chua Thuyen Ton",
            "Thuyen Ton pagoda",
            "Thuyen Ton pagoda Hue"
        ],
        "lat": 16.431,
        "lng": 107.585,
        "phase": 5,
        "default_target": 12
    },
    {
        "place_id": "spiri_chua_ha_trung",
        "name": "Chùa Hà Trung",
        "sub_name": "Ngôi chùa cổ kính trầm mặc soi bóng xuống đầm phá Hà Trung",
        "category": "Attraction",
        "wiki_title": "Hà Trung, Phú Vang",
        "search_keywords": [
            "Chua Ha Trung",
            "Ha Trung pagoda",
            "Ha Trung Hue"
        ],
        "lat": 16.418,
        "lng": 107.732,
        "phase": 5,
        "default_target": 12
    },
    {
        "place_id": "spiri_den_hue_nam",
        "name": "Điện Huệ Nam (Lễ hội Điện Hòn Chén Mở Rộng)",
        "sub_name": "Đoàn thuyền rồng rước sắc Thánh Mẫu rực rỡ cờ hoa trên dòng sông Hương",
        "category": "Attraction",
        "wiki_title": "Điện Hòn Chén",
        "search_keywords": [
            "Dien Hue Nam",
            "Hue Nam temple",
            "Le hoi Dien Hon Chen",
            "Hon Chen festival Hue"
        ],
        "lat": 16.4258,
        "lng": 107.5389,
        "phase": 5,
        "default_target": 12
    },
    {
        "place_id": "spiri_chua_quoc_an",
        "name": "Chùa Quốc Ân",
        "sub_name": "Tổ đình sắc tứ đầu tiên xứ Đàng Trong do Thiền sư Nguyên Thiều khai sơn",
        "category": "Attraction",
        "wiki_title": "Chùa Quốc Ân",
        "search_keywords": [
            "Chua Quoc An",
            "Quoc An pagoda",
            "Quoc An Hue"
        ],
        "lat": 16.446,
        "lng": 107.584,
        "phase": 5,
        "default_target": 12
    },
    {
        "place_id": "spiri_chua_hong_an",
        "name": "Chùa Hồng Ân",
        "sub_name": "Tổ đình ni tự danh tiếng chốn thiền môn xứ Huế trên đồi Quảng Tế",
        "category": "Attraction",
        "wiki_title": "",
        "search_keywords": [
            "Chua Hong An",
            "Hong An pagoda",
            "Hong An pagoda Hue"
        ],
        "lat": 16.438,
        "lng": 107.579,
        "phase": 5,
        "default_target": 12
    },
    {
        "place_id": "spiri_chua_tay_thien",
        "name": "Chùa Tây Thiên",
        "sub_name": "Ngôi tịnh thất cổ kính trầm mặc thanh tịnh dưới chân núi Ngự Bình",
        "category": "Attraction",
        "wiki_title": "",
        "search_keywords": [
            "Chua Tay Thien Hue",
            "Tay Thien pagoda",
            "Tay Thien Hue"
        ],
        "lat": 16.435,
        "lng": 107.592,
        "phase": 5,
        "default_target": 12
    },
    {
        "place_id": "spiri_mieu_lich_doi",
        "name": "Miếu Lịch Đợi Đế Vương",
        "sub_name": "Nơi triều Nguyễn lập đền thờ phụng các bậc anh quân đế vương lập quốc",
        "category": "Attraction",
        "wiki_title": "Miếu Lịch Đợi Đế Vương",
        "search_keywords": [
            "Mieu Lich Doi De Vuong",
            "Lich Doi De Vuong Hue",
            "Temple of Ancient Dynasties Hue"
        ],
        "lat": 16.452,
        "lng": 107.568,
        "phase": 5,
        "default_target": 12
    }
]

PHASE_6_STREET_FOOD_GIFTS = [
    {
        "place_id": "culinary_banh_canh_nam_pho",
        "name": "Bánh canh Nam Phổ",
        "sub_name": "Sợi bánh canh bột gạo dai mềm nước dùng sánh màu đỏ gạch tôm cua đồng",
        "category": "Culinary",
        "wiki_title": "Bánh canh Nam Phổ",
        "search_keywords": [
            "Banh canh Nam Pho",
            "Banh canh Hue",
            "Nam Pho noodle soup",
            "Banh canh cua Hue"
        ],
        "lat": 16.495,
        "lng": 107.615,
        "phase": 6,
        "default_target": 12
    },
    {
        "place_id": "culinary_banh_trang_nuong",
        "name": "Bánh tráng nướng & Bánh tráng kẹp Huế",
        "sub_name": "Món ăn vặt đường phố nổi tiếng thơm lừng béo ngậy bờ nam sông Hương",
        "category": "Culinary",
        "wiki_title": "",
        "search_keywords": [
            "Banh trang nuong Hue",
            "Banh trang kep Hue",
            "Hue grilled rice paper",
            "Banh trang kep"
        ],
        "lat": 16.465,
        "lng": 107.595,
        "phase": 6,
        "default_target": 12
    },
    {
        "place_id": "culinary_che_hat_sen",
        "name": "Chè hạt sen hồ Tịnh Tâm",
        "sub_name": "Chè hạt sen ngự uyển bùi thơm bọc long nhãn tiến vua thanh mát",
        "category": "Culinary",
        "wiki_title": "Chè (ẩm thực)",
        "search_keywords": [
            "Che hat sen",
            "Che hat sen Hue",
            "Lotus seed sweet soup Hue",
            "Che long nhan hat sen"
        ],
        "lat": 16.4758,
        "lng": 107.5792,
        "phase": 6,
        "default_target": 12
    },
    {
        "place_id": "culinary_banh_it_den",
        "name": "Bánh ít lá gai & Bánh phu thê (su sê) xứ Huế",
        "sub_name": "Thức bánh cưới hỏi và giỗ chạp truyền thống thơm hương lá dứa dẻo bùi",
        "category": "Culinary",
        "wiki_title": "Bánh ít",
        "search_keywords": [
            "Banh it la gai",
            "Banh it Hue",
            "Banh su se Hue",
            "Banh phu the Hue"
        ],
        "lat": 16.46,
        "lng": 107.585,
        "phase": 6,
        "default_target": 12
    },
    {
        "place_id": "culinary_tre_hue",
        "name": "Tré Huế & Chả lụa Cố đô",
        "sub_name": "Tré rơm gói lá ổi lên men chua ngọt nồng nàn vị riềng tỏi ớt thơm cay",
        "category": "Culinary",
        "wiki_title": "Tré",
        "search_keywords": [
            "Tre Hue",
            "Cha lua Hue",
            "Tre rom Hue",
            "Hue fermented pork"
        ],
        "lat": 16.471,
        "lng": 107.586,
        "phase": 6,
        "default_target": 12
    },
    {
        "place_id": "culinary_tom_chua",
        "name": "Tôm chua xứ Huế",
        "sub_name": "Đặc sản tiến vua lên men từ tôm đất sông Hương ăn kèm thịt ba chỉ luộc",
        "category": "Culinary",
        "wiki_title": "Tôm chua",
        "search_keywords": [
            "Tom chua",
            "Tom chua Hue",
            "Sour shrimp Hue",
            "Mam tom chua"
        ],
        "lat": 16.468,
        "lng": 107.588,
        "phase": 6,
        "default_target": 12
    },
    {
        "place_id": "culinary_me_xung",
        "name": "Kẹo mè xửng Huế",
        "sub_name": "Mè xửng giòn mè xửng dẻo biểu tượng quà biếu Cố đô ngọt thơm bùi ngậy",
        "category": "Culinary",
        "wiki_title": "Mè xửng",
        "search_keywords": [
            "Me xung",
            "Me xung Hue",
            "Hue sesame candy",
            "Keo me xung"
        ],
        "lat": 16.465,
        "lng": 107.59,
        "phase": 6,
        "default_target": 12
    },
    {
        "place_id": "culinary_ruou_lang_chuon",
        "name": "Rượu tiến vua Làng Chuồn",
        "sub_name": "Men rượu thủ công ủ nếp cái hoa vàng nức tiếng đầm phá Tam Giang",
        "category": "Culinary",
        "wiki_title": "Làng Chuồn",
        "search_keywords": [
            "Ruou lang Chuon",
            "Lang Chuon",
            "Chuon village wine",
            "Ruou nep lang Chuon"
        ],
        "lat": 16.515,
        "lng": 107.65,
        "phase": 6,
        "default_target": 12
    },
    {
        "place_id": "culinary_pho_dem_han_thuyen",
        "name": "Phố ẩm thực đêm Hàn Thuyên",
        "sub_name": "Phố bánh canh đêm nổi tiếng bên vòm cổng thành Kinh thành Huế",
        "category": "Culinary",
        "wiki_title": "",
        "search_keywords": [
            "Pho dem Han Thuyen",
            "Banh canh Han Thuyen",
            "Am thuc Han Thuyen Hue"
        ],
        "lat": 16.474,
        "lng": 107.582,
        "phase": 6,
        "default_target": 12
    },
    {
        "place_id": "culinary_cho_an_cuu",
        "name": "Chợ An Cựu & Chợ Tây Lộc",
        "sub_name": "Hai khu chợ dân sinh sầm uất với thiên đường ẩm thực bản địa giá bình dân",
        "category": "Culinary",
        "wiki_title": "Sông An Cựu",
        "search_keywords": [
            "Cho An Cuu",
            "Cho Tay Loc Hue",
            "An Cuu market Hue",
            "Tay Loc market"
        ],
        "lat": 16.455,
        "lng": 107.595,
        "phase": 6,
        "default_target": 12
    }
]

PHASE_7_ECO_NATURE = [
    {
        "place_id": "nature_ho_truoi",
        "name": "Hồ Truồi & Đập tràn Lộc Hòa",
        "sub_name": "Lòng hồ nước xanh như ngọc bích dưới chân dãy núi Bạch Mã hùng vĩ",
        "category": "Attraction",
        "wiki_title": "Hồ Truồi",
        "search_keywords": [
            "Ho Truoi",
            "Truoi lake Hue",
            "Dap tran Ho Truoi",
            "Truoi lake Vietnam"
        ],
        "lat": 16.265,
        "lng": 107.775,
        "phase": 7,
        "default_target": 12
    },
    {
        "place_id": "nature_thac_truot_an_or",
        "name": "Thác Trượt A Nôr",
        "sub_name": "Ngọn thác 3 tầng kỳ vĩ giữa đại ngàn Trường Sơn tại huyện vùng cao A Lưới",
        "category": "Attraction",
        "wiki_title": "A Lưới",
        "search_keywords": [
            "Thac A Nor",
            "A Nor waterfall",
            "Thac truot A Nor A Luoi",
            "A Luoi waterfall"
        ],
        "lat": 16.275,
        "lng": 107.255,
        "phase": 7,
        "default_target": 12
    },
    {
        "place_id": "nature_thac_mo_nam_dong",
        "name": "Thác Mơ / Suối Mơ Nam Đông",
        "sub_name": "Quần thể hồ tắm suối tự nhiên giữa rừng nguyên sinh Nam Đông trong lành",
        "category": "Attraction",
        "wiki_title": "Nam Đông",
        "search_keywords": [
            "Thac Mo Nam Dong",
            "Suoi Mo Nam Dong",
            "Nam Dong waterfall",
            "Suoi Mo Hue"
        ],
        "lat": 16.155,
        "lng": 107.72,
        "phase": 7,
        "default_target": 12
    },
    {
        "place_id": "nature_bien_canh_duong",
        "name": "Bãi biển Cảnh Dương",
        "sub_name": "Bãi biển cát trắng hình vòng cung hoang sơ lý tưởng cho cắm trại ngắm bình minh",
        "category": "Attraction",
        "wiki_title": "Cảnh Dương",
        "search_keywords": [
            "Canh Duong beach",
            "Bai bien Canh Duong Hue",
            "Canh Duong Hue",
            "Chan May beach"
        ],
        "lat": 16.32,
        "lng": 108.015,
        "phase": 7,
        "default_target": 12
    },
    {
        "place_id": "nature_hai_dang_chan_may",
        "name": "Mũi Chân Mây Đông & Hải đăng Chân Mây",
        "sub_name": "Ngọn hải đăng cổ kính sừng sững trên vách đá ngắm trọn biển Đông",
        "category": "Attraction",
        "wiki_title": "Chân Mây",
        "search_keywords": [
            "Hai dang Chan May",
            "Mui Chan May",
            "Chan May lighthouse",
            "Chan May cape"
        ],
        "lat": 16.335,
        "lng": 108.035,
        "phase": 7,
        "default_target": 12
    },
    {
        "place_id": "nature_cua_bien_tu_hien",
        "name": "Cửa biển Tư Hiền",
        "sub_name": "Cửa biển lịch sử Tư Dung nơi dòng nước đầm Cầu Hai giao hòa cùng Biển Đông",
        "category": "Attraction",
        "wiki_title": "Cửa Tư Hiền",
        "search_keywords": [
            "Cua Tu Hien",
            "Tu Hien sea gate",
            "Cua bien Tu Hien",
            "Tu Dung sea gate"
        ],
        "lat": 16.335,
        "lng": 107.985,
        "phase": 7,
        "default_target": 12
    },
    {
        "place_id": "nature_bien_ham_rong",
        "name": "Bãi biển Hàm Rồng (Vinh Hiền)",
        "sub_name": "Bãi biển với những bãi đá phủ rêu xanh uốn lượn tuyệt đẹp nhìn ra cửa Tư Hiền",
        "category": "Attraction",
        "wiki_title": "",
        "search_keywords": [
            "Bien Ham Rong Hue",
            "Ham Rong beach Hue",
            "Bai bien Ham Rong Vinh Hien"
        ],
        "lat": 16.34,
        "lng": 107.995,
        "phase": 7,
        "default_target": 12
    },
    {
        "place_id": "nature_dam_sam_an_truyen",
        "name": "Đầm Chuồn - Đầm Sam ngắm bình minh",
        "sub_name": "Hệ thống nhà chòi sàn gỗ và thuyền chèo sup giữa mênh mông sông nước phá Tam Giang",
        "category": "Attraction",
        "wiki_title": "",
        "search_keywords": [
            "Dam Sam Hue",
            "Dam Chuon An Truyen",
            "Dam Sam lagoon",
            "Pha Tam Giang binh minh"
        ],
        "lat": 16.535,
        "lng": 107.635,
        "phase": 7,
        "default_target": 12
    },
    {
        "place_id": "nature_ngu_ho_bach_ma",
        "name": "Ngũ Hồ & Thác Đỗ Quyên (Bạch Mã)",
        "sub_name": "Chuỗi 5 hồ nước tự nhiên trên đỉnh Bạch Mã với dòng thác Đỗ Quyên hùng vĩ",
        "category": "Attraction",
        "wiki_title": "Vườn quốc gia Bạch Mã",
        "search_keywords": [
            "Ngu Ho Bach Ma",
            "Thac Do Quyen Bach Ma",
            "Do Quyen waterfall Hue",
            "Five Lakes Bach Ma"
        ],
        "lat": 16.205,
        "lng": 107.865,
        "phase": 7,
        "default_target": 12
    },
    {
        "place_id": "nature_thac_truot_loc_binh",
        "name": "Bãi biển Hải Bình & Cửa Lộc Bình",
        "sub_name": "Bãi biển hoang sơ thanh bình phía nam vịnh Chân Mây nép mình dưới rặng phi lao",
        "category": "Attraction",
        "wiki_title": "",
        "search_keywords": [
            "Bien Hai Binh Loc Binh",
            "Cua bien Loc Binh",
            "Hai Binh beach Hue"
        ],
        "lat": 16.325,
        "lng": 108.065,
        "phase": 7,
        "default_target": 12
    }
]

PHASE_8_CRAFT_ART = [
    {
        "place_id": "craft_truc_chi",
        "name": "Nghệ thuật Trúc Chỉ Huế",
        "sub_name": "Dòng tranh đồ họa giấy chế tác từ xơ tre độc bản đương đại của Cố đô",
        "category": "CraftVillage",
        "wiki_title": "",
        "search_keywords": [
            "Truc Chi Hue",
            "Nhe thuat Truc Chi",
            "Truc Chi art Hue",
            "Bamboo paper Hue"
        ],
        "lat": 16.467,
        "lng": 107.585,
        "phase": 8,
        "default_target": 12
    },
    {
        "place_id": "craft_gom_phuoc_tich",
        "name": "Làng gốm cổ Phước Tích mở rộng",
        "sub_name": "Nghệ thuật nung gốm đất sét hơn 500 năm bên bờ sông Ô Lâu",
        "category": "CraftVillage",
        "wiki_title": "Phước Tích",
        "search_keywords": [
            "Gom Phuoc Tich",
            "Phuoc Tich pottery",
            "Phuoc Tich ceramic",
            "Lang gom Phuoc Tich"
        ],
        "lat": 16.6575,
        "lng": 107.3042,
        "phase": 8,
        "default_target": 12
    },
    {
        "place_id": "craft_moc_my_xuyen",
        "name": "Làng mộc mỹ nghệ Mỹ Xuyên",
        "sub_name": "Bàn tay chạm khắc rường cột, hoành phi câu đối cung đình trứ danh",
        "category": "CraftVillage",
        "wiki_title": "Phong Hòa, Phong Điền",
        "search_keywords": [
            "Moc My Xuyen",
            "My Xuyen wood carving",
            "Lang moc My Xuyen Hue"
        ],
        "lat": 16.652,
        "lng": 107.295,
        "phase": 8,
        "default_target": 12
    },
    {
        "place_id": "craft_kim_hoan_ke_mon",
        "name": "Làng kim hoàn Kế Môn",
        "sub_name": "Cái nôi chế tác trang sức vàng bạc tiến vua thời phong kiến",
        "category": "CraftVillage",
        "wiki_title": "Điền Môn",
        "search_keywords": [
            "Kim hoan Ke Mon",
            "Ke Mon gold jewelry",
            "Lang kim hoan Ke Mon"
        ],
        "lat": 16.695,
        "lng": 107.385,
        "phase": 8,
        "default_target": 12
    },
    {
        "place_id": "craft_det_zeng_a_luoi",
        "name": "Dệt Dèng thổ cẩm A Lưới",
        "sub_name": "Di sản văn hóa phi vật thể quốc gia kết cườm trên vải của đồng bào Tà Ôi",
        "category": "CraftVillage",
        "wiki_title": "Tà Ôi",
        "search_keywords": [
            "Det Zeng A Luoi",
            "Zeng weaving Hue",
            "Tho cam A Luoi",
            "Zeng Ta Oi"
        ],
        "lat": 16.285,
        "lng": 107.265,
        "phase": 8,
        "default_target": 12
    },
    {
        "place_id": "craft_non_la_my_lam",
        "name": "Làng nón Mỹ Lâm / Dạ Lê",
        "sub_name": "Nơi khởi nguồn kỹ nghệ chuốt vành và chằm nón lá thanh thoát",
        "category": "CraftVillage",
        "wiki_title": "",
        "search_keywords": [
            "Non la My Lam",
            "Lang non Da Le",
            "My Lam conical hat",
            "Cham non Da Le"
        ],
        "lat": 16.445,
        "lng": 107.645,
        "phase": 8,
        "default_target": 12
    },
    {
        "place_id": "craft_banh_trang_luu_bao",
        "name": "Làng bánh tráng Lựu Bảo",
        "sub_name": "Làng nghề tráng bánh tráng gạo truyền thống ven dòng sông Hương",
        "category": "CraftVillage",
        "wiki_title": "",
        "search_keywords": [
            "Banh trang Luu Bao",
            "Luu Bao rice paper",
            "Lang banh trang Luu Bao"
        ],
        "lat": 16.485,
        "lng": 107.552,
        "phase": 8,
        "default_target": 12
    },
    {
        "place_id": "craft_lang_dan_lat_bao_la",
        "name": "Làng đan lát mây tre Bao La",
        "sub_name": "Sản phẩm thúng mủng, giỏ tre thủ công mỹ nghệ xuất khẩu",
        "category": "CraftVillage",
        "wiki_title": "Quảng Phú, Quảng Điền",
        "search_keywords": [
            "Dan lat Bao La",
            "Bao La bamboo",
            "Bao La basket weaving",
            "Lang Bao La Hue"
        ],
        "lat": 16.565,
        "lng": 107.545,
        "phase": 8,
        "default_target": 12
    },
    {
        "place_id": "craft_tra_sen_tinh_tam",
        "name": "Nghệ thuật ướp Trà Sen hồ Tịnh Tâm",
        "sub_name": "Quy trình gieo trà vào búp sen đêm ngậm sương cung đình tinh túy",
        "category": "CraftVillage",
        "wiki_title": "",
        "search_keywords": [
            "Tra sen Tinh Tam",
            "Lotus tea Hue",
            "Uop tra sen Hue",
            "Tra sen Cung Dinh Hue"
        ],
        "lat": 16.4758,
        "lng": 107.5792,
        "phase": 8,
        "default_target": 12
    },
    {
        "place_id": "craft_thuyen_rong_song_huong",
        "name": "Xưởng đóng thuyền rồng Ca Huế",
        "sub_name": "Nghề đóng thuyền rồng truyền thống phục vụ biểu diễn Ca Huế trên sông Hương",
        "category": "CraftVillage",
        "wiki_title": "",
        "search_keywords": [
            "Thuyen rong song Huong",
            "Dragon boat Hue",
            "Ca Hue tren song Huong",
            "Thuyen rong Hue"
        ],
        "lat": 16.4688,
        "lng": 107.5898,
        "phase": 8,
        "default_target": 12
    }
]

PHASE_9_COLONIAL_URBAN = [
    {
        "place_id": "arch_truong_quoc_hoc",
        "name": "Trường THPT Chuyên Quốc Học Huế",
        "sub_name": "Ngôi trường cổ kính màu đỏ son ven sông Hương nơi Bác Hồ và nhiều danh nhân từng theo học",
        "category": "Attraction",
        "wiki_title": "Trường Trung học phổ thông chuyên Quốc Học – Huế",
        "search_keywords": [
            "Quoc Hoc Hue",
            "Truong Quoc Hoc Hue",
            "Quoc Hoc High School Hue",
            "Quoc Hoc National High School"
        ],
        "lat": 16.4635,
        "lng": 107.584,
        "phase": 9,
        "default_target": 12
    },
    {
        "place_id": "arch_truong_dong_khanh",
        "name": "Trường THPT Hai Bà Trưng (Đồng Khánh xưa)",
        "sub_name": "Biểu tượng tà áo dài tím thướt tha và kiến trúc thuộc địa Pháp cổ kính",
        "category": "Attraction",
        "wiki_title": "Trường Trung học phổ thông Hai Bà Trưng, Huế",
        "search_keywords": [
            "Truong Dong Khanh",
            "Dong Khanh school Hue",
            "Hai Ba Trung High School Hue",
            "Dong Khanh Hue"
        ],
        "lat": 16.4628,
        "lng": 107.5855,
        "phase": 9,
        "default_target": 12
    },
    {
        "place_id": "arch_khach_san_morin",
        "name": "Khách sạn Saigon Morin (1901)",
        "sub_name": "Khách sạn cổ nhất miền Trung nằm ở ngã tư cầu Trường Tiền nơi Charlie Chaplin từng lưu trú",
        "category": "Attraction",
        "wiki_title": "Khách sạn Sài Gòn Morin",
        "search_keywords": [
            "Saigon Morin hotel",
            "Morin hotel Hue",
            "Hotel Saigon Morin",
            "Khach san Morin Hue"
        ],
        "lat": 16.468,
        "lng": 107.5905,
        "phase": 9,
        "default_target": 12
    },
    {
        "place_id": "arch_bao_tang_diem_phung_thi",
        "name": "Trung tâm Nghệ thuật Điềm Phùng Thị",
        "sub_name": "Biệt thự Pháp cổ trưng bày tác phẩm điêu khắc 7 module độc đáo ven sông Hương",
        "category": "Attraction",
        "wiki_title": "Điềm Phùng Thị",
        "search_keywords": [
            "Diem Phung Thi",
            "Diem Phung Thi art center",
            "Bao tang Diem Phung Thi",
            "Diem Phung Thi Hue"
        ],
        "lat": 16.4675,
        "lng": 107.5885,
        "phase": 9,
        "default_target": 12
    },
    {
        "place_id": "arch_nha_luu_niem_bac_ho",
        "name": "Cụm Di tích Nhà lưu niệm Bác Hồ",
        "sub_name": "Ngôi nhà tranh làng Dương Nỗ và phố Mai Thúc Loan lưu giữ kỷ niệm tuổi thơ Chủ tịch Hồ Chí Minh",
        "category": "Attraction",
        "wiki_title": "",
        "search_keywords": [
            "Nha luu niem Bac Ho Hue",
            "Duong No village Bac Ho",
            "Ho Chi Minh memorial house Hue"
        ],
        "lat": 16.488,
        "lng": 107.625,
        "phase": 9,
        "default_target": 12
    },
    {
        "place_id": "arch_cau_bach_ho",
        "name": "Cầu đường sắt Bạch Hổ (Dã Viên)",
        "sub_name": "Cây cầu sắt cổ kính vượt sông Hương góc ngắm hoàng hôn check-in quen thuộc",
        "category": "Attraction",
        "wiki_title": "Cầu Bạch Hổ",
        "search_keywords": [
            "Cau Bach Ho",
            "Bach Ho bridge Hue",
            "Cau duong sat Bach Ho",
            "Bach Ho railway bridge"
        ],
        "lat": 16.4575,
        "lng": 107.573,
        "phase": 9,
        "default_target": 12
    },
    {
        "place_id": "arch_pho_tay_hue",
        "name": "Phố đi bộ Chu Văn An - Phạm Ngũ Lão",
        "sub_name": "Tuyến phố đêm sôi động, sầm uất phong cách du lịch quốc tế ven sông Hương",
        "category": "Attraction",
        "wiki_title": "",
        "search_keywords": [
            "Pho di bo Hue",
            "Pho Tay Hue",
            "Pham Ngu Lao walking street Hue",
            "Chu Van An Hue"
        ],
        "lat": 16.4685,
        "lng": 107.596,
        "phase": 9,
        "default_target": 12
    },
    {
        "place_id": "arch_pho_di_bo_hoang_thanh",
        "name": "Phố đêm Hoàng Thành Huế",
        "sub_name": "Không gian phố đi bộ và biểu diễn nghệ thuật truyền thống trước Cửa Quảng Đức",
        "category": "Attraction",
        "wiki_title": "",
        "search_keywords": [
            "Pho dem Hoang Thanh Hue",
            "Hoang Thanh walking street Hue",
            "Quang Duc gate night"
        ],
        "lat": 16.467,
        "lng": 107.577,
        "phase": 9,
        "default_target": 12
    },
    {
        "place_id": "arch_nha_vuon_y_thao",
        "name": "Nhà vườn Ý Thảo & Không gian Văn hóa Cố đô",
        "sub_name": "Khu vườn rường cổ thưởng thức cơm chay nghệ thuật và trà đạo cung đình",
        "category": "Attraction",
        "wiki_title": "",
        "search_keywords": [
            "Nha vuon Y Thao",
            "Y Thao garden house",
            "Y Thao garden Hue"
        ],
        "lat": 16.471,
        "lng": 107.573,
        "phase": 9,
        "default_target": 12
    },
    {
        "place_id": "arch_ben_thuyen_van_lau",
        "name": "Nghinh Lương Đình & Phu Văn Lâu",
        "sub_name": "Cặp công trình kiến trúc gỗ biểu tượng soi bóng bến sông Hương bờ Bắc Kinh thành",
        "category": "Attraction",
        "wiki_title": "Phu Văn Lâu",
        "search_keywords": [
            "Phu Van Lau",
            "Nghinh Luong Dinh",
            "Phu Van Lau Hue",
            "Nghinh Luong Dinh Hue"
        ],
        "lat": 16.4675,
        "lng": 107.581,
        "phase": 9,
        "default_target": 12
    }
]

# TỔNG HỢP TOÀN BỘ 121 ĐỊA DANH CỐ ĐÔ HUẾ
ALL_LANDMARKS = (
    PHASE_1_LANDMARKS +
    PHASE_2_CULINARY +
    PHASE_3_CRAFT_CULTURE +
    PHASE_4_CORE_HERITAGE +
    PHASE_5_SPIRITUAL +
    PHASE_6_STREET_FOOD_GIFTS +
    PHASE_7_ECO_NATURE +
    PHASE_8_CRAFT_ART +
    PHASE_9_COLONIAL_URBAN
)


# ==============================================================================
# CÁC HÀM XỬ LÝ DỮ LIỆU & TẢI ẢNH CHUẨN HÓA (NHẸ MÁY & BẢO TOÀN DỮ LIỆU)
# ==============================================================================

def get_image_hash(filepath: str) -> str:
    """Tạo mã băm MD5 để loại trừ trùng lặp nội dung ảnh."""
    try:
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()
    except Exception:
        return ""


def search_commons_images(query: str, max_results: int = 20):
    """Tìm kiếm file ảnh trên Wikimedia Commons dựa trên từ khóa."""
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,  # 6 = File: namespace
        "gsrlimit": max_results,
        "prop": "imageinfo",
        "iiprop": "url|mime|size|width|height",
        "iiurlwidth": 1024
    }
    try:
        resp = requests.get(COMMONS_API, headers=HTTP_HEADERS, params=params, timeout=12)
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
            width = info.get("width", 0)
            height = info.get("height", 0)

            # Lọc bỏ file không phải ảnh, icon bé, file tài liệu số hóa, scan sách, svg hoặc tiff
            title_lower = title.lower()
            if any(title_lower.endswith(ext) for ext in ('.djvu', '.pdf', '.epub', '.tif', '.tiff', '.svg', '.gif')):
                continue
            if any(kw in title_lower for kw in ('(ia ', 'internet archive', 'declaration of', 'pronouncing', 'compendio', 'dictionary', 'diccionario', 'lettere', 'vol.')):
                continue
            if "image" not in mime or "svg" in mime or "tif" in mime or "gif" in mime:
                continue
            if width < 300 or height < 300:
                continue

            # Ưu tiên thumbnail 1024px để tải nhanh gấp 50 lần ảnh gốc siêu nặng
            url = info.get("thumburl") or info.get("url")
            if url:
                results.append({
                    "title": title,
                    "url": url,
                    "size": info.get("size", 0),
                    "width": width,
                    "height": height
                })
        return results
    except Exception:
        return []


def search_wikipedia_article_images(wiki_title: str, lang: str = "vi", max_results: int = 15):
    """Lấy danh sách ảnh trực tiếp từ bài viết Wikipedia tương ứng."""
    if not wiki_title:
        return []
    api_url = VI_WIKI_API if lang == "vi" else EN_WIKI_API
    params = {
        "action": "query",
        "titles": wiki_title,
        "generator": "images",
        "gimlimit": max_results,
        "prop": "imageinfo",
        "iiprop": "url|mime|size|width|height",
        "iiurlwidth": 1024,
        "format": "json"
    }
    try:
        resp = requests.get(api_url, headers=HTTP_HEADERS, params=params, timeout=12)
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
            width = info.get("width", 0)
            height = info.get("height", 0)

            title_lower = title.lower()
            if any(title_lower.endswith(ext) for ext in ('.djvu', '.pdf', '.epub', '.tif', '.tiff', '.svg', '.gif')):
                continue
            if any(kw in title_lower for kw in ('(ia ', 'internet archive', 'declaration of', 'pronouncing', 'compendio', 'dictionary', 'diccionario', 'lettere', 'vol.')):
                continue
            if "image" not in mime or "svg" in mime or "tif" in mime or "gif" in mime:
                continue
            if width < 300 or height < 300:
                continue

            url = info.get("thumburl") or info.get("url")
            if url:
                results.append({
                    "title": title,
                    "url": url,
                    "size": info.get("size", 0),
                    "width": width,
                    "height": height
                })
        return results
    except Exception:
        return []


def download_and_process_image(url: str, save_path: str, max_size: int = 1024) -> bool:
    """Tải ảnh, chuyển RGB, resize Lanczos 1024px, lưu JPEG chất lượng cao và giải phóng RAM ngay lập tức."""
    img = None
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        resp = requests.get(url, headers=DOWNLOAD_HEADERS, timeout=(3.0, 5.0))
        if resp.status_code != 200 or len(resp.content) < 8000:
            return False

        img = Image.open(io.BytesIO(resp.content))
        img = img.convert("RGB")
        w, h = img.size
        if w < 250 or h < 250:
            img.close()
            return False

        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        img.save(save_path, "JPEG", quality=88, optimize=True)
        img.close()
        return True
    except Exception:
        if img is not None:
            try:
                img.close()
            except Exception:
                pass
        return False


def atomic_save_metadata(metadata_dict: dict, file_path: str):
    """Ghi metadata ra file tạm rồi đổi tên (Atomic Write) để chống hỏng file nếu người dùng ngắt giữa chừng."""
    meta_list = list(metadata_dict.values())
    tmp_path = file_path + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(meta_list, f, ensure_ascii=False, indent=2)
        if os.path.exists(file_path):
            os.replace(tmp_path, file_path)
        else:
            os.rename(tmp_path, file_path)
    except Exception as e:
        print(f"⚠️ [Lỗi ghi metadata]: {e}", flush=True)


# ==============================================================================
# HÀM ĐIỀU PHỐI CÀO THEO PHÂN ĐOẠN (MODULAR CRAWL RUNNER)
# ==============================================================================

def run_crawler(
    phase_choice: str = "1",
    custom_target: int = None,
    limit_places: int = None,
    place_id_filter: str = None
):
    """
    Thực thi cào dữ liệu ảnh theo phân đoạn (Phase) được chọn.
    Chạy từng đợt nhỏ gọn, an toàn và bảo toàn dữ liệu 100%.
    """
    if place_id_filter:
        targets = [lm for lm in ALL_LANDMARKS if lm["place_id"] == place_id_filter]
        phase_desc = f"Đơn lẻ theo địa danh: {place_id_filter}"
    elif phase_choice == "1":
        targets = PHASE_1_LANDMARKS
        phase_desc = "Phase 1 - Cứu 10 địa danh thiếu ảnh (Siêu nhẹ, ~50 ảnh, 1-2 phút)"
    elif phase_choice == "2":
        targets = PHASE_2_CULINARY
        phase_desc = "Phase 2 - 12 món Ẩm thực di sản Cố đô Huế (~140 ảnh, 3-4 phút)"
    elif phase_choice == "3":
        targets = PHASE_3_CRAFT_CULTURE
        phase_desc = "Phase 3 - 8 Làng nghề truyền thống & Điểm văn hóa (~100 ảnh, 2-3 phút)"
    elif phase_choice == "4":
        targets = PHASE_4_CORE_HERITAGE
        phase_desc = "Phase 4 - Nâng hạn ngạch 41 Di tích lịch sử lên 20 ảnh/địa điểm"
    elif phase_choice == "5":
        targets = PHASE_5_SPIRITUAL
        phase_desc = "Phase 5 - 10 Cổ tự, Thiền viện & Di sản Tâm linh (~120 ảnh, 2-3 phút)"
    elif phase_choice == "6":
        targets = PHASE_6_STREET_FOOD_GIFTS
        phase_desc = "Phase 6 - 10 Ẩm thực Đường phố, Chợ & Quà biếu Cố đô (~120 ảnh, 2-3 phút)"
    elif phase_choice == "7":
        targets = PHASE_7_ECO_NATURE
        phase_desc = "Phase 7 - 10 Đầm phá, Suối thác & Vịnh biển hoang sơ (~120 ảnh, 2-3 phút)"
    elif phase_choice == "8":
        targets = PHASE_8_CRAFT_ART
        phase_desc = "Phase 8 - 10 Làng nghề Mỹ nghệ, Thổ cẩm & Trúc Chỉ (~120 ảnh, 2-3 phút)"
    elif phase_choice == "9":
        targets = PHASE_9_COLONIAL_URBAN
        phase_desc = "Phase 9 - 10 Kiến trúc Pháp, Trường cổ & Check-in Cố đô (~120 ảnh, 2-3 phút)"
    elif phase_choice in ["all", "10"]:
        targets = ALL_LANDMARKS
        phase_desc = "Tất cả 9 Phase (Toàn bộ 121 địa danh Cố đô Huế)"
    else:
        print(f"❌ Không nhận diện được Phase '{phase_choice}'!")
        return

    if limit_places and limit_places > 0:
        targets = targets[:limit_places]
        phase_desc += f" (Giới hạn: {limit_places} địa danh đầu tiên)"

    # Đọc metadata cũ để bảo toàn dữ liệu của các Phase khác
    metadata_map = {}
    seen_hashes = set()

    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                old_list = json.load(f)
                for item in old_list:
                    rel_p = item.get("file_path", "")
                    if rel_p:
                        metadata_map[rel_p] = item
                        abs_p = os.path.join(PROJECT_ROOT, rel_p.replace("/", os.sep))
                        if os.path.exists(abs_p):
                            h = get_image_hash(abs_p)
                            if h:
                                seen_hashes.add(h)
        except Exception as e:
            print(f"⚠️ [Cảnh báo] Lỗi đọc metadata cũ: {e}", flush=True)

    print("=" * 78, flush=True)
    print("🚀 BẮT ĐẦU CÀO BỘ DỮ LIỆU ẢNH DI SẢN & ẨM THỰC HUẾ (CHẾ ĐỘ NHẸ MÁY)", flush=True)
    print(f"📋 Phân đoạn thực hiện: {phase_desc}", flush=True)
    print(f"📍 Tổng số địa danh lượt này: {len(targets)} địa danh", flush=True)
    print(f"📂 Cơ sở dữ liệu hiện có: {len(metadata_map)} ảnh đã được lưu trong index", flush=True)
    print("=" * 78, flush=True)

    t_start = time.time()
    total_new_downloads = 0

    for idx, lm in enumerate(targets, 1):
        place_id = lm["place_id"]
        place_name = lm["name"]
        sub_name = lm["sub_name"]
        category = lm["category"]
        lat = lm["lat"]
        lng = lm["lng"]
        wiki_title = lm.get("wiki_title", "")
        keywords = lm.get("search_keywords", [])

        target_quota = custom_target if custom_target else lm.get("default_target", 12)

        place_dir = os.path.join(IMAGE_OUTPUT_DIR, place_id)
        os.makedirs(place_dir, exist_ok=True)

        print(f"\n[{idx:02d}/{len(targets)}] 📍 {place_name} ({place_id}) [{category}]", flush=True)

        existing_files = [f for f in sorted(os.listdir(place_dir)) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        collected_for_place = 0
        for ef in existing_files:
            abs_p = os.path.join(place_dir, ef)
            if os.path.getsize(abs_p) > 5000:
                h = get_image_hash(abs_p)
                if h:
                    seen_hashes.add(h)
                collected_for_place += 1
                rel_path = os.path.relpath(abs_p, PROJECT_ROOT).replace(os.sep, "/")
                if rel_path not in metadata_map:
                    metadata_map[rel_path] = {
                        "image_id": f"img_{place_id}_{collected_for_place:02d}",
                        "place_id": place_id,
                        "place_name": place_name,
                        "sub_location": sub_name,
                        "category": category,
                        "file_path": rel_path,
                        "source_title": f"Tư liệu ảnh {place_name} ({ef})",
                        "source_url": "",
                        "caption": f"Ảnh tư liệu check-in di sản tại {place_name} ({sub_name}) Cố đô Huế",
                        "latitude": lat,
                        "longitude": lng
                    }

        print(f"   ℹ️ Đã có sẵn: {collected_for_place}/{target_quota} ảnh hợp lệ.", flush=True)

        if collected_for_place >= target_quota:
            print(f"   ✅ Đã đạt hạn ngạch mục tiêu ({collected_for_place}/{target_quota} ảnh). Bỏ qua tải thêm.", flush=True)
            continue

        candidate_items = []
        seen_urls = set()

        for query in keywords:
            if len(candidate_items) >= 45:
                break
            items = search_commons_images(query, max_results=20)
            for itm in items:
                u = itm["url"]
                if u not in seen_urls:
                    seen_urls.add(u)
                    candidate_items.append(itm)
            time.sleep(0.15)

        if wiki_title and len(candidate_items) < 30:
            wiki_items = search_wikipedia_article_images(wiki_title, lang="vi", max_results=15)
            for itm in wiki_items:
                u = itm["url"]
                if u not in seen_urls:
                    seen_urls.add(u)
                    candidate_items.append(itm)
            time.sleep(0.15)

        candidate_items.sort(key=lambda x: not ("thumb.wikimedia.org" in x.get("url", "")))

        new_for_place = 0
        for item in candidate_items:
            if collected_for_place >= target_quota:
                break

            img_url = item["url"]
            file_name = f"img_{collected_for_place + 1:02d}.jpg"
            save_path = os.path.join(place_dir, file_name)

            success = download_and_process_image(img_url, save_path)
            if success:
                img_hash = get_image_hash(save_path)
                if img_hash and img_hash in seen_hashes:
                    try:
                        os.remove(save_path)
                    except Exception:
                        pass
                    continue

                seen_hashes.add(img_hash)
                collected_for_place += 1
                new_for_place += 1
                total_new_downloads += 1

                rel_path = os.path.relpath(save_path, PROJECT_ROOT).replace(os.sep, "/")
                if category == "Culinary":
                    cap = f"Hình ảnh món ngon đặc sản {place_name} ({sub_name}) trứ danh Cố đô Huế"
                elif category == "CraftVillage":
                    cap = f"Tư liệu làng nghề truyền thống {place_name} ({sub_name}) xứ Huế"
                else:
                    cap = f"Ảnh tư liệu di tích danh thắng {place_name} ({sub_name}) Cố đô Huế"

                metadata_map[rel_path] = {
                    "image_id": f"img_{place_id}_{collected_for_place:02d}",
                    "place_id": place_id,
                    "place_name": place_name,
                    "sub_location": sub_name,
                    "category": category,
                    "file_path": rel_path,
                    "source_title": item["title"],
                    "source_url": img_url,
                    "caption": cap,
                    "latitude": lat,
                    "longitude": lng
                }

                print(f"   ✓ [Ảnh {collected_for_place:02d}/{target_quota}] {file_name} <- {item['title'][:40]}", flush=True)
                time.sleep(0.15)

        print(f"   📊 Hoàn tất địa danh: hiện có {collected_for_place} ảnh (Tải mới: +{new_for_place})", flush=True)
        atomic_save_metadata(metadata_map, METADATA_FILE)

    elapsed = time.time() - t_start
    print("\n" + "=" * 78, flush=True)
    print("🎉 HOÀN THÀNH PHÂN ĐOẠN CÀO DỮ LIỆU!", flush=True)
    print(f"📥 Tổng số ảnh mới tải thêm trong đợt này: {total_new_downloads} ảnh", flush=True)
    print(f"📚 Tổng quy mô cơ sở dữ liệu ảnh hiện tại: {len(metadata_map)} ảnh", flush=True)
    print(f"⏱️ Tổng thời gian chạy: {elapsed/60:.2f} phút", flush=True)
    print(f"📄 File chỉ mục Metadata: {METADATA_FILE}", flush=True)
    print("💡 Gợi ý tiếp theo: Sau khi hoàn thành các Phase mong muốn, bạn có thể chạy:")
    print("   python scripts/build_visual_index.py  (Để trích xuất CLIP vector vào ChromaDB)")
    print("=" * 78, flush=True)


# ==============================================================================
# ENTRY POINT & GIAO DIỆN TƯƠNG TÁC DÒNG LỆNH
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Hue Heritage Visual Crawler (Modular 9-Phase Execution)")
    parser.add_argument("--phase", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "all"], help="Chọn Phase cào dữ liệu (1-9 hoặc 10/all: Toàn bộ 121 địa danh)")
    parser.add_argument("--place-id", type=str, help="Chỉ cào 1 địa danh cụ thể theo place_id")
    parser.add_argument("--target", type=int, default=None, help="Tùy chỉnh số ảnh mục tiêu cho mỗi địa điểm (mặc định: 12-20)")
    parser.add_argument("--limit", type=int, default=None, help="Giới hạn số địa danh xử lý trong lượt này (ví dụ: --limit 3 để siêu nhẹ máy)")

    args = parser.parse_args()

    if args.phase or args.place_id or args.limit:
        run_crawler(
            phase_choice=args.phase or "1",
            custom_target=args.target,
            limit_places=args.limit,
            place_id_filter=args.place_id
        )
        return

    print("""
======================================================================
🌸 HUE HERITAGE VISUAL CRAWLER - CÀO DỮ LIỆU ẢNH THEO 9 PHÂN ĐOẠN
======================================================================
Hệ thống hỗ trợ chạy từng phần để nhẹ máy, tránh nóng máy/quá tải:

  [1] Phase 1: Cứu 10 địa danh thiếu ảnh (Siêu nhẹ, ~50 ảnh, 1-2 phút)
  [2] Phase 2: Ẩm thực di sản Cố đô Huế (12 món, ~140 ảnh, 3-4 phút)
  [3] Phase 3: Làng nghề truyền thống & Văn hóa (8 điểm, ~100 ảnh, 2-3 phút)
  [4] Phase 4: Nâng hạn ngạch 41 di tích cốt lõi lên 20 ảnh/địa điểm
  [5] Phase 5: Cổ tự, Thiền viện & Di sản Tâm linh (10 điểm, ~120 ảnh, 2-3 phút)
  [6] Phase 6: Ẩm thực Đường phố, Chợ & Quà biếu Cố đô (10 món, ~120 ảnh, 2-3 phút)
  [7] Phase 7: Đầm phá, Suối thác & Vịnh biển hoang sơ (10 cảnh quan, ~120 ảnh, 2-3 phút)
  [8] Phase 8: Làng nghề Mỹ nghệ, Thổ cẩm & Trúc Chỉ (10 làng nghề, ~120 ảnh, 2-3 phút)
  [9] Phase 9: Kiến trúc Pháp, Trường cổ & Check-in Cố đô (10 điểm, ~120 ảnh, 2-3 phút)
  [10] Cào toàn bộ (Tất cả 121 địa danh Cố đô Huế)
  [0] Thoát
======================================================================
""")
    try:
        choice = input("👉 Nhập số bạn muốn chạy [0-10] (Mặc định 5): ").strip()
    except Exception:
        choice = "5"

    if not choice:
        choice = "5"

    if choice == "0":
        print("Tạm biệt!")
        return

    run_crawler(phase_choice=choice)


if __name__ == "__main__":
    main()
