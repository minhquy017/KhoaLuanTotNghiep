# -*- coding: utf-8 -*-
"""
BƯỚC 2: THU THẬP BỘ DỮ LIỆU ẢNH DI SẢN & CHECK-IN HUẾ QUY MÔ LỚN (EXPANDED VISUAL DATASET)
Khóa luận Tốt nghiệp ngành Khoa học Dữ liệu và Trí tuệ Nhân tạo (DS&AI - HUET)
Đề tài: Spatial GraphRAG - Cố đô Huế

Quy mô mở rộng:
- 50 địa danh văn hóa, di tích lịch sử, danh thắng tự nhiên, cổ tự và làng nghề Huế.
- Hạn ngạch mục tiêu: 10 - 15 ảnh chất lượng cao / địa điểm (Tổng quy mô ~500 - 650 ảnh).
- Nguồn dữ liệu: Wikimedia Commons API kết hợp Wikipedia Infobox/Article Images (CC-BY-SA / Public Domain).
- Chuẩn hóa: RGB, Thumbnail tối đa 1024px, JPEG chất lượng cao, tối ưu hóa cho CLIP ViT-B/32.
"""

import os
import sys
import json
import time
import io
import hashlib
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

TARGET_IMAGES_PER_LANDMARK = 12  # Mục tiêu từ 10 - 15 ảnh / địa điểm
MAX_IMAGES_LIMIT = 15

# ==============================================================================
# DANH MỤC 50 ĐỊA DANH TIÊU BIỂU TOÀN TỈNH THỪA THIÊN HUẾ (CHUẨN HÓA KHỚP SPATIAL KG)
# ==============================================================================
LANDMARKS_CONFIG = [
    # --- NHÓM 1: QUẦN THỂ DI TÍCH HOÀNG THÀNH & TỬ CẤM THÀNH (ĐẠI NỘI HUẾ) ---
    {
        "place_id": "place_8875",
        "name": "Đại Nội Huế (Hoàng Thành & Kinh Thành)",
        "sub_name": "Ngọ Môn & Kỳ Đài",
        "category": "Attraction",
        "wiki_title": "Hoàng thành Huế",
        "search_keywords": ["Ngo Mon Hue", "Imperial City Hue", "Kỳ Đài Huế", "Kinh thanh Hue", "Meridian Gate Hue"],
        "lat": 16.468744,
        "lng": 107.57835
    },
    {
        "place_id": "place_8884",
        "name": "Điện Thái Hòa & Tử Cấm Thành",
        "sub_name": "Ngai vàng triều Nguyễn & Sân Đại Triều Nghi",
        "category": "Attraction",
        "wiki_title": "Điện Thái Hòa (Hoàng thành Huế)",
        "search_keywords": ["Thai Hoa Palace Hue", "Dien Thai Hoa Hue", "Tu Cam Thanh Hue", "Purple Forbidden City Hue"],
        "lat": 16.46925,
        "lng": 107.57792
    },
    {
        "place_id": "custom_attr_the_mieu",
        "name": "Thế Tổ Miếu & Cửu Đỉnh",
        "sub_name": "Nơi thờ các vua triều Nguyễn & 9 đỉnh đồng bảo vật quốc gia",
        "category": "Attraction",
        "wiki_title": "Thế Tổ Miếu (Hoàng thành Huế)",
        "search_keywords": ["The Mieu Hue", "Nine Dynastic Urns Hue", "Cuu Dinh Hue", "Hien Lam Cac Hue"],
        "lat": 16.4678,
        "lng": 107.5765
    },
    {
        "place_id": "custom_attr_dien_tho",
        "name": "Cung Diên Thọ & Cung Trường Sanh",
        "sub_name": "Chốn hoàng cung cựu hoàng thái hậu triều Nguyễn",
        "category": "Attraction",
        "wiki_title": "Cung Diên Thọ",
        "search_keywords": ["Dien Tho residence Hue", "Cung Dien Tho", "Cung Truong Sanh Hue", "Truong Sanh palace"],
        "lat": 16.4705,
        "lng": 107.5761
    },
    {
        "place_id": "place_9917",
        "name": "Bảo tàng Cổ vật Cung đình Huế (Điện Long An)",
        "sub_name": "Tuyệt tác kiến trúc gỗ trùng thiềm điệp ốc thời Thiệu Trị",
        "category": "Attraction",
        "wiki_title": "Bảo tàng Cổ vật Cung đình Huế",
        "search_keywords": ["Hue Museum of Royal Antiquities", "Dien Long An Hue", "Long An Palace Hue", "Bao tang co vat Hue"],
        "lat": 16.4712,
        "lng": 107.5815
    },

    # --- NHÓM 2: HỆ THỐNG LĂNG TẨM VƯƠNG TRIỀU NGUYỄN (7 LĂNG CHÍNH) ---
    {
        "place_id": "place_8879",
        "name": "Lăng Khải Định (Ứng Lăng)",
        "sub_name": "Sân chầu tượng đá & Khải Thành Điện khảm sành sứ",
        "category": "Attraction",
        "wiki_title": "Lăng Khải Định",
        "search_keywords": ["Khai Dinh tomb", "Khai Thanh Palace Hue", "Lang Khai Dinh", "Tomb of Khai Dinh"],
        "lat": 16.3986,
        "lng": 107.5906
    },
    {
        "place_id": "place_8880",
        "name": "Lăng Tự Đức (Khiêm Lăng)",
        "sub_name": "Hồ Lưu Khiêm, Xung Khiêm Tạ & Nhà bia Khiêm Cung Ký",
        "category": "Attraction",
        "wiki_title": "Lăng Tự Đức",
        "search_keywords": ["Tu Duc tomb", "Luu Khiem lake Hue", "Lang Tu Duc", "Tomb of Tu Duc", "Xung Khiem Ta"],
        "lat": 16.4328,
        "lng": 107.5647
    },
    {
        "place_id": "place_8878",
        "name": "Lăng Minh Mạng (Hiếu Lăng)",
        "sub_name": "Hồ Tân Nguyệt, Cầu Thông Minh Chính Trực & Minh Lâu",
        "category": "Attraction",
        "wiki_title": "Lăng Minh Mạng",
        "search_keywords": ["Minh Mang tomb", "Minh Lau Hue", "Lang Minh Mang", "Tomb of Minh Mang"],
        "lat": 16.387653,
        "lng": 107.56918
    },
    {
        "place_id": "custom_attr_01",
        "name": "Lăng Gia Long (Thiên Thọ Lăng)",
        "sub_name": "Quần thể lăng mộ vua sáng lập triều Nguyễn giữa rừng thông",
        "category": "Attraction",
        "wiki_title": "Lăng Gia Long",
        "search_keywords": ["Gia Long tomb", "Lang Gia Long", "Thien Tho tomb Hue", "Tomb of Gia Long"],
        "lat": 16.3534,
        "lng": 107.5756
    },
    {
        "place_id": "place_8881",
        "name": "Lăng Đồng Khánh (Tư Lăng)",
        "sub_name": "Điện Ngưng Hy kiến trúc sơn son thếp vàng giao thoa Á - Âu",
        "category": "Attraction",
        "wiki_title": "Lăng Đồng Khánh",
        "search_keywords": ["Dong Khanh tomb", "Lang Dong Khanh", "Dien Ngung Hy Hue", "Tomb of Dong Khanh"],
        "lat": 16.429956,
        "lng": 107.5700
    },
    {
        "place_id": "place_9906",
        "name": "Lăng Thiệu Trị (Xương Lăng)",
        "sub_name": "Lăng tẩm vương triều thanh bình giữa đồng lúa Thủy Bằng",
        "category": "Attraction",
        "wiki_title": "Lăng Thiệu Trị",
        "search_keywords": ["Thieu Tri tomb", "Lang Thieu Tri", "Xuong Lang Hue", "Tomb of Thieu Tri"],
        "lat": 16.4175,
        "lng": 107.5732
    },
    {
        "place_id": "place_9907",
        "name": "Lăng Dục Đức (An Lăng)",
        "sub_name": "Nơi an nghỉ của ba thế hệ vua triều Nguyễn (Dục Đức, Thành Thái, Duy Tân)",
        "category": "Attraction",
        "wiki_title": "Lăng Dục Đức",
        "search_keywords": ["Duc Duc tomb", "Lang Duc Duc", "An Lang Hue", "Tomb of Duc Duc"],
        "lat": 16.4468,
        "lng": 107.5872
    },

    # --- NHÓM 3: CUNG ĐIỆN VĂN HÓA, TẾ LỄ & ĐẤU TRƯỜNG HOÀNG GIA ---
    {
        "place_id": "custom_local_31",
        "name": "Cung An Định",
        "sub_name": "Lâu đài Khải Tường Lâu Tân cổ điển Pháp - Việt bên bờ sông An Cựu",
        "category": "Attraction",
        "wiki_title": "Cung An Định",
        "search_keywords": ["An Dinh Palace Hue", "An Dinh Palace", "Khai Tuong Lau Hue", "Cung An Dinh"],
        "lat": 16.4589,
        "lng": 107.5947
    },
    {
        "place_id": "custom_attr_04",
        "name": "Điện Hòn Chén",
        "sub_name": "Điện thờ Mẫu Thiên Y A Na cheo leo vách núi Ngọc Trản bên sông Hương",
        "category": "Attraction",
        "wiki_title": "Điện Hòn Chén",
        "search_keywords": ["Hon Chen temple", "Dien Hon Chen", "Hon Chen Hue", "Ngoc Tran temple Hue"],
        "lat": 16.4258,
        "lng": 107.5389
    },
    {
        "place_id": "place_9910",
        "name": "Đàn Nam Giao",
        "sub_name": "Đàn tế trời đất quan trọng nhất của vương triều Nguyễn",
        "category": "Attraction",
        "wiki_title": "Đàn Nam Giao (triều Nguyễn)",
        "search_keywords": ["Nam Giao Hue", "Esplanade of Sacrifice to Heaven and Earth Hue", "Dan Nam Giao"],
        "lat": 16.4418,
        "lng": 107.5842
    },
    {
        "place_id": "place_8922",
        "name": "Văn Miếu Huế (Văn Thánh Miếu)",
        "sub_name": "Quần thể 32 bia tiến sĩ ngự bên bờ sông Hương",
        "category": "Attraction",
        "wiki_title": "Văn miếu Huế",
        "search_keywords": ["Temple of Literature Hue", "Van Mieu Hue", "Van Thanh Hue", "Bia Tien Si Hue"],
        "lat": 16.4552,
        "lng": 107.5385
    },
    {
        "place_id": "place_9909",
        "name": "Đấu trường Hổ Quyền",
        "sub_name": "Đấu trường La Mã phương Đông dành cho voi và hổ thời Nguyễn",
        "category": "Attraction",
        "wiki_title": "Hổ Quyền",
        "search_keywords": ["Ho Quyen Hue", "Ho Quyen amphitheater", "Ho Quyen arena Hue", "Tiger Colosseum Hue"],
        "lat": 16.4442,
        "lng": 107.5598
    },
    {
        "place_id": "custom_attr_voire",
        "name": "Điện Voi Ré",
        "sub_name": "Đền thờ linh tượng quả cảm và các vị thần hộ quốc",
        "category": "Attraction",
        "wiki_title": "Điện Voi Ré",
        "search_keywords": ["Dien Voi Re", "Voi Re temple Hue", "Voi Re Hue", "Elephant shrine Hue"],
        "lat": 16.4435,
        "lng": 107.5585
    },
    {
        "place_id": "custom_attr_quoctugiam",
        "name": "Quốc Tử Giám Huế",
        "sub_name": "Trường đại học duy nhất thời phong kiến còn nguyên vẹn tại Việt Nam",
        "category": "Attraction",
        "wiki_title": "Quốc Tử Giám (Huế)",
        "search_keywords": ["Quoc Tu Giam Hue", "Imperial Academy Hue", "Bao tang lich su Hue"],
        "lat": 16.4718,
        "lng": 107.5819
    },

    # --- NHÓM 4: DANH LAM CỔ TỰ & CÔNG TRÌNH TÔN GIÁO HUẾ ---
    {
        "place_id": "place_8876",
        "name": "Chùa Thiên Mụ",
        "sub_name": "Tháp Phước Duyên 7 tầng bên bờ sông Hương hữu tình",
        "category": "Attraction",
        "wiki_title": "Chùa Thiên Mụ",
        "search_keywords": ["Thien Mu pagoda", "Phuoc Duyen pagoda Hue", "Thien Mu temple", "Chua Thien Mu"],
        "lat": 16.453144,
        "lng": 107.54485
    },
    {
        "place_id": "place_8886",
        "name": "Chùa Từ Hiếu",
        "sub_name": "Cổ tự nghĩa trang thái giám triều Nguyễn & thiền viện thanh tịnh",
        "category": "Attraction",
        "wiki_title": "Chùa Từ Hiếu",
        "search_keywords": ["Tu Hieu pagoda", "Tu Hieu temple Hue", "Chua Tu Hieu", "Eunuch pagoda Hue"],
        "lat": 16.4397,
        "lng": 107.5621
    },
    {
        "place_id": "custom_attr_05",
        "name": "Chùa Huyền Không Sơn Thượng",
        "sub_name": "Vườn thiền ẩn mình giữa đại ngàn rừng thông Hòn Vượn",
        "category": "Attraction",
        "wiki_title": "Chùa Huyền Không",
        "search_keywords": ["Huyen Khong Son Thuong", "Huyen Khong pagoda Hue", "Chua Huyen Khong Son Thuong"],
        "lat": 16.4851,
        "lng": 107.4952
    },
    {
        "place_id": "custom_local_30",
        "name": "Chùa Từ Đàm",
        "sub_name": "Tổ đình trung tâm phong trào Phật giáo miền Trung",
        "category": "Attraction",
        "wiki_title": "Chùa Từ Đàm",
        "search_keywords": ["Tu Dam pagoda Hue", "Tu Dam temple", "Chua Tu Dam Hue"],
        "lat": 16.4502,
        "lng": 107.5815
    },
    {
        "place_id": "custom_attr_baoquoc",
        "name": "Chùa Báo Quốc",
        "sub_name": "Cổ tự danh tiếng lập từ thế kỷ 17 trên đồi Hàm Long",
        "category": "Attraction",
        "wiki_title": "Chùa Báo Quốc (Huế)",
        "search_keywords": ["Bao Quoc pagoda", "Chua Bao Quoc Hue", "Bao Quoc temple Hue"],
        "lat": 16.4538,
        "lng": 107.5812
    },
    {
        "place_id": "custom_attr_thienlam",
        "name": "Chùa Thiền Lâm (Chùa Vàng Miến Điện)",
        "sub_name": "Ngôi chùa phong cách Phật giáo Nam truyền Theravada độc đáo",
        "category": "Attraction",
        "wiki_title": "Chùa Thiền Lâm (Huế)",
        "search_keywords": ["Chua Thien Lam Hue", "Thien Lam pagoda Hue", "Golden pagoda Hue"],
        "lat": 16.4425,
        "lng": 107.5748
    },
    {
        "place_id": "custom_local_20",
        "name": "Nhà Thờ Dòng Chúa Cứu Thế Huế",
        "sub_name": "Thánh đường tam giác vút cao kiến trúc Á - Âu đường Nguyễn Huệ",
        "category": "Attraction",
        "wiki_title": "Nhà thờ Dòng Chúa Cứu Thế Huế",
        "search_keywords": ["Redemptorist Church Hue", "Dong Chua Cuu The Hue", "Nha tho Dong Chua Cuu The"],
        "lat": 16.4593,
        "lng": 107.5956
    },
    {
        "place_id": "place_9918",
        "name": "Nhà Thờ Chính Tòa Phủ Cam",
        "sub_name": "Tuyệt phẩm thánh đường hiện đại của kiến trúc sư Ngô Viết Thụ",
        "category": "Attraction",
        "wiki_title": "Nhà thờ chính tòa Phủ Cam",
        "search_keywords": ["Phu Cam Cathedral", "Phu Cam Church Hue", "Nha tho Phu Cam"],
        "lat": 16.4547,
        "lng": 107.5869
    },

    # --- NHÓM 5: THẮNG CẢNH THIÊN NHIÊN, BIỂN & ĐẦM PHÁ ---
    {
        "place_id": "place_8882",
        "name": "Sông Hương & Bến Thuyền Tòa Khâm",
        "sub_name": "Dòng sông di sản, Cầu đi bộ gỗ Lim & Ca Huế trên thuyền rồng",
        "category": "Attraction",
        "wiki_title": "Sông Hương",
        "search_keywords": ["Perfume River Hue", "Huong river boat", "Song Huong Hue", "Toa Kham Hue"],
        "lat": 16.4678,
        "lng": 107.5925
    },
    {
        "place_id": "custom_attr_02",
        "name": "Đồi Vọng Cảnh",
        "sub_name": "Vọng lâu ngắm trọn khúc quanh mềm mại nhất của sông Hương",
        "category": "Attraction",
        "wiki_title": "Đồi Vọng Cảnh",
        "search_keywords": ["Vong Canh hill Hue", "Vong Canh Hue", "Huong river Vong Canh", "Doi Vong Canh"],
        "lat": 16.4358,
        "lng": 107.5582
    },
    {
        "place_id": "custom_local_21",
        "name": "Công Viên Hồ Thủy Tiên (Tượng Rồng)",
        "sub_name": "Tượng đầu rồng khổng lồ huyền bí giữa hồ nước đồi Thiên An",
        "category": "Attraction",
        "wiki_title": "Công viên nước Hồ Thủy Tiên",
        "search_keywords": ["Ho Thuy Tien dragon", "Ho Thuy Tien abandoned", "Thuy Tien lake Hue", "Ho Thuy Tien"],
        "lat": 16.4182,
        "lng": 107.5753
    },
    {
        "place_id": "custom_attr_thienan",
        "name": "Đồi Thiên An & Đan Viện Benedict",
        "sub_name": "Đồi thông ngút ngàn ví như Đà Lạt giữa lòng Cố đô",
        "category": "Attraction",
        "wiki_title": "Đan viện Thiên An",
        "search_keywords": ["Thien An hill Hue", "Doi Thien An", "Dan vien Thien An", "Benedictine monastery Hue"],
        "lat": 16.4215,
        "lng": 107.5721
    },
    {
        "place_id": "place_8918",
        "name": "Phá Tam Giang (Đầm Chuồn)",
        "sub_name": "Đầm phá nước lợ lớn nhất Đông Nam Á & nhà chồ ngắm hoàng hôn",
        "category": "Attraction",
        "wiki_title": "Phá Tam Giang",
        "search_keywords": ["Tam Giang lagoon", "Dam Chuon Hue", "Pha Tam Giang", "Tam Giang lagoon sunset"],
        "lat": 16.5124,
        "lng": 107.6482
    },
    {
        "place_id": "custom_local_32",
        "name": "Đầm Lập An & Làng Chài Lăng Cô",
        "sub_name": "Con đường rẽ nước giữa đầm lãng mạn dưới chân đèo Phú Gia",
        "category": "Attraction",
        "wiki_title": "Đầm Lập An",
        "search_keywords": ["Lap An lagoon", "Lang Co lagoon", "Dam Lap An", "Lap An oyster farm"],
        "lat": 16.2341,
        "lng": 108.0125
    },
    {
        "place_id": "place_8917",
        "name": "Bãi biển Lăng Cô & Vịnh Lăng Cô",
        "sub_name": "Vịnh biển đẹp bậc nhất thế giới nằm nép mình bên đèo Hải Vân",
        "category": "Attraction",
        "wiki_title": "Vịnh Lăng Cô",
        "search_keywords": ["Lang Co beach", "Lang Co bay", "Lang Co Hue", "Bai bien Lang Co"],
        "lat": 16.2285,
        "lng": 108.0315
    },
    {
        "place_id": "place_8895",
        "name": "Đèo Hải Vân (Hải Vân Quan)",
        "sub_name": "Cổng thiên hạ đệ nhất hùng quan nối liền Thừa Thiên Huế và Đà Nẵng",
        "category": "Attraction",
        "wiki_title": "Đèo Hải Vân",
        "search_keywords": ["Hai Van Pass", "Hai Van Gate", "Hai Van Quan", "Deo Hai Van"],
        "lat": 16.200014,
        "lng": 108.13334
    },
    {
        "place_id": "place_8877",
        "name": "Vườn Quốc gia Bạch Mã",
        "sub_name": "Đỉnh Hải Vọng Đài mây phủ, Thác Đỗ Quyên & Ngũ Hồ",
        "category": "Attraction",
        "wiki_title": "Vườn quốc gia Bạch Mã",
        "search_keywords": ["Bach Ma National Park", "Hai Vong Dai Bach Ma", "Do Quyen waterfall", "Vuon quoc gia Bach Ma"],
        "lat": 16.216366,
        "lng": 107.893715
    },
    {
        "place_id": "place_9912",
        "name": "Suối Voi (Thác Voi Lộc Tiến)",
        "sub_name": "Khu sinh thái suối đá tự nhiên với tượng voi đá khổng lồ",
        "category": "Attraction",
        "wiki_title": "Suối Voi",
        "search_keywords": ["Elephant Springs Hue", "Suoi Voi Hue", "Suoi Voi Loc Tien"],
        "lat": 16.2152,
        "lng": 108.0185
    },
    {
        "place_id": "place_9913",
        "name": "Bãi biển Thuận An",
        "sub_name": "Bãi biển cửa ngõ biển Đông gắn liền với Trấn Hải Thành thời Nguyễn",
        "category": "Attraction",
        "wiki_title": "Thuận An (phường)",
        "search_keywords": ["Thuan An beach Hue", "Bai bien Thuan An", "Thuan An Hue"],
        "lat": 16.5512,
        "lng": 107.6489
    },
    {
        "place_id": "custom_attr_rucha",
        "name": "Rừng ngập mặn nguyên sinh Rú Chá",
        "sub_name": "Khu rừng chá ngập mặn nguyên sinh duy nhất trên đầm phá Tam Giang",
        "category": "Attraction",
        "wiki_title": "Rú Chá",
        "search_keywords": ["Ru Cha", "Ru Cha Hue", "Ru Cha mangrove forest", "Rung ngap man Ru Cha"],
        "lat": 16.5385,
        "lng": 107.6085
    },
    {
        "place_id": "place_9914",
        "name": "Suối khoáng nóng Alba Thanh Tân",
        "sub_name": "Khu nghỉ dưỡng suối khoáng tự nhiên & trò chơi Zipline mạo hiểm",
        "category": "Attraction",
        "wiki_title": "Alba Thanh Tân",
        "search_keywords": ["Alba Thanh Tan", "Thanh Tan hot springs Hue", "Alba Wellness Hue"],
        "lat": 16.5295,
        "lng": 107.4582
    },
    {
        "place_id": "custom_attr_hotinhtam",
        "name": "Hồ Tịnh Tâm (Kinh thành Huế)",
        "sub_name": "Hồ sen ngự uyển đệ nhất danh thắng chốn Hoàng thành",
        "category": "Attraction",
        "wiki_title": "Hồ Tịnh Tâm",
        "search_keywords": ["Tinh Tam lake Hue", "Ho Tinh Tam", "Lotus lake Hue Citadel"],
        "lat": 16.4758,
        "lng": 107.5792
    },

    # --- NHÓM 6: CẦU CỔ, NHÀ VƯỜN, LÀNG NGHỀ & VĂN HÓA TRUYỀN THỐNG ---
    {
        "place_id": "place_8919",
        "name": "Cầu Trường Tiền",
        "sub_name": "Cây cầu 6 vài 12 nhịp bắc qua sông Hương biểu tượng Cố đô",
        "category": "Attraction",
        "wiki_title": "Cầu Trường Tiền",
        "search_keywords": ["Trang Tien bridge Hue", "Truong Tien bridge Hue", "Trang Tien Hue", "Cau Truong Tien"],
        "lat": 16.4682,
        "lng": 107.5898
    },
    {
        "place_id": "place_8885",
        "name": "Cầu ngói Thanh Toàn",
        "sub_name": "Cầu ngói cổ thời Hậu Lê bắc qua sông Như Ý làng Thủy Thanh",
        "category": "Attraction",
        "wiki_title": "Cầu ngói Thanh Toàn",
        "search_keywords": ["Thanh Toan tile-roofed bridge", "Thanh Toan bridge", "Cau ngoi Thanh Toan"],
        "lat": 16.4529,
        "lng": 107.6322
    },
    {
        "place_id": "custom_attr_davien",
        "name": "Cầu Dã Viên & Cồn Dã Viên",
        "sub_name": "Cây cầu mang tên Bạch Hổ phong thủy che chắn kinh thành",
        "category": "Attraction",
        "wiki_title": "Cầu Dã Viên",
        "search_keywords": ["Da Vien bridge Hue", "Cau Da Vien", "Con Da Vien Hue"],
        "lat": 16.4558,
        "lng": 107.5725
    },
    {
        "place_id": "custom_attr_03",
        "name": "Làng hương Thủy Xuân",
        "sub_name": "Con đường chân hương xòe quạt đa sắc màu rực rỡ",
        "category": "Attraction",
        "wiki_title": "Làng hương Thủy Xuân",
        "search_keywords": ["Thuy Xuan incense", "Incense Hue Vietnam", "Thuy Xuan Hue", "Lang huong Thuy Xuan"],
        "lat": 16.4412,
        "lng": 107.5684
    },
    {
        "place_id": "place_8920",
        "name": "Chợ Đông Ba",
        "sub_name": "Cổng chợ & Tháp đồng hồ trung tâm giao thương ẩm thực Huế",
        "category": "Attraction",
        "wiki_title": "Chợ Đông Ba",
        "search_keywords": ["Dong Ba market Hue", "Dong Ba market", "Cho Dong Ba", "Dong Ba market Vietnam"],
        "lat": 16.47262,
        "lng": 107.58850
    },
    {
        "place_id": "custom_local_15",
        "name": "Cà Phê Mắt Biếc & Phố Cổ Bao Vinh",
        "sub_name": "Ngôi nhà gỗ cổ bối cảnh phim Mắt Biếc bên bến đò Bao Vinh",
        "category": "Attraction",
        "wiki_title": "Bao Vinh",
        "search_keywords": ["Bao Vinh ancient town", "Bao Vinh Hue", "Pho co Bao Vinh", "Mat Biec cafe Hue"],
        "lat": 16.4885,
        "lng": 107.5892
    },
    {
        "place_id": "custom_attr_con_hen",
        "name": "Cồn Hến (Đảo Cồn Hến)",
        "sub_name": "Cù lao sông Hương (Thanh Long) cái nôi của Cơm hến & Chè bắp",
        "category": "Attraction",
        "wiki_title": "Cồn Hến",
        "search_keywords": ["Con Hen Hue", "Con Hen island", "Con Hen river Hue", "Con Hen"],
        "lat": 16.4782,
        "lng": 107.5995
    },
    {
        "place_id": "custom_attr_anhien",
        "name": "Nhà Vườn An Hiên (Kim Long)",
        "sub_name": "Nhà rường truyền thống xứ Huế với vườn cây ăn trái cổ kính",
        "category": "Attraction",
        "wiki_title": "Nhà vườn An Hiên",
        "search_keywords": ["An Hien", "Nha vuon An Hien", "An Hien house", "An Hien garden Hue"],
        "lat": 16.4558,
        "lng": 107.5518
    },
    {
        "place_id": "place_8904",
        "name": "Không gian lưu niệm Lê Bá Đảng (Lebadang Memory Space)",
        "sub_name": "Bảo tàng nghệ thuật đương đại trắng muốt giữa đồi núi Kim Sơn",
        "category": "Attraction",
        "wiki_title": "Lê Bá Đảng",
        "search_keywords": ["Lebadang Memory Space", "Lebadang museum Hue", "Khong gian Le Ba Dang"],
        "lat": 16.404272,
        "lng": 107.58311
    },
    {
        "place_id": "custom_attr_phuoctich",
        "name": "Làng cổ Phước Tích",
        "sub_name": "Làng di sản gốm cổ và quần thể nhà rường cổ kính bên sông Ô Lâu",
        "category": "Attraction",
        "wiki_title": "Phước Tích",
        "search_keywords": ["Phuoc Tich ancient village", "Lang co Phuoc Tich", "Phuoc Tich pottery Hue"],
        "lat": 16.6575,
        "lng": 107.3042
    }
]


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

            # Lọc bỏ file không phải ảnh, icon bé, file svg hoặc tiff
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


DOWNLOAD_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 (HueTourismVisualRAG; contact@huetourism.edu.vn)",
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    "Referer": "https://commons.wikimedia.org/"
}


def download_and_process_image(url: str, save_path: str, max_size: int = 1024) -> bool:
    """Tải ảnh từ URL, chuyển sang RGB, kiểm tra chất lượng, resize và lưu dạng JPEG chuẩn tối ưu cho CLIP."""
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        # Timeout kết nối 2.5s, đọc dữ liệu tối đa 4.0s để không bị treo
        resp = requests.get(url, headers=DOWNLOAD_HEADERS, timeout=(2.5, 4.0))
        if resp.status_code != 200 or len(resp.content) < 8000:
            return False

        img = Image.open(io.BytesIO(resp.content))
        img = img.convert("RGB")
        w, h = img.size
        if w < 250 or h < 250:
            return False

        # Resize giữ nguyên tỷ lệ với bộ lọc chất lượng cao LANCZOS
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        img.save(save_path, "JPEG", quality=88, optimize=True)
        return True
    except Exception:
        return False


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


def crawl_images_for_landmarks():
    metadata_list = []
    total_downloaded = 0
    seen_hashes = set()
    existing_meta_by_path = {}

    # Nạp các metadata cũ nếu có để hỗ trợ cào bù và tái sử dụng
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                old_meta = json.load(f)
                for item in old_meta:
                    rel_p = item.get("file_path", "")
                    existing_meta_by_path[rel_p] = item
                    abs_p = os.path.join(PROJECT_ROOT, rel_p.replace("/", os.sep))
                    if os.path.exists(abs_p):
                        h = get_image_hash(abs_p)
                        if h:
                            seen_hashes.add(h)
        except Exception:
            pass

    print("=" * 80, flush=True)
    print(f"🚀 BẮT ĐẦU CÀO BỘ DỮ LIỆU ẢNH HUẾ QUY MÔ LỚN ({len(LANDMARKS_CONFIG)} ĐỊA DANH)", flush=True)
    print(f"🎯 Mục tiêu: {TARGET_IMAGES_PER_LANDMARK} - {MAX_IMAGES_LIMIT} ảnh chất lượng cao / địa danh", flush=True)
    print("=" * 80, flush=True)

    t_start = time.time()

    for idx, lm in enumerate(LANDMARKS_CONFIG, 1):
        place_id = lm["place_id"]
        place_name = lm["name"]
        sub_name = lm["sub_name"]
        lat = lm["lat"]
        lng = lm["lng"]
        wiki_title = lm.get("wiki_title", "")

        place_dir = os.path.join(IMAGE_OUTPUT_DIR, place_id)
        os.makedirs(place_dir, exist_ok=True)

        print(f"\n[{idx:02d}/{len(LANDMARKS_CONFIG)}] 📍 {place_name} ({place_id})", flush=True)

        collected_for_place = 0
        seen_urls = set()

        # 1. Đếm các ảnh hợp lệ sẵn có nếu đã tải từ trước
        existing_files = [f for f in sorted(os.listdir(place_dir)) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        for ef in existing_files:
            abs_p = os.path.join(place_dir, ef)
            if os.path.getsize(abs_p) > 5000:
                h = get_image_hash(abs_p)
                if h:
                    seen_hashes.add(h)
                collected_for_place += 1
                rel_path = os.path.relpath(abs_p, PROJECT_ROOT).replace("\\", "/")
                prev_item = existing_meta_by_path.get(rel_path, {})
                metadata_list.append({
                    "image_id": f"img_{place_id}_{collected_for_place:02d}",
                    "place_id": place_id,
                    "place_name": place_name,
                    "sub_location": sub_name,
                    "category": lm["category"],
                    "file_path": rel_path,
                    "source_title": prev_item.get("source_title", f"Tư liệu ảnh {place_name} ({ef})"),
                    "source_url": prev_item.get("source_url", ""),
                    "caption": prev_item.get("caption", f"Ảnh tư liệu check-in di sản tại {place_name} ({sub_name}) Cố đô Huế"),
                    "latitude": lat,
                    "longitude": lng
                })

        if collected_for_place > 0:
            print(f"   ℹ️ Đã có sẵn {collected_for_place} ảnh hợp lệ trong thư mục.", flush=True)

        if collected_for_place >= TARGET_IMAGES_PER_LANDMARK:
            print(f"   ✅ Đã đạt hạn ngạch ({collected_for_place}/{TARGET_IMAGES_PER_LANDMARK} ảnh). Chuyển địa điểm tiếp theo.", flush=True)
            continue

        # 2. Thu thập ứng viên ảnh từ các nguồn
        candidate_items = []

        # Nguồn 1: Tìm kiếm từ khóa trên Wikimedia Commons
        for query in lm["search_keywords"]:
            if len(candidate_items) >= 40:
                break
            items = search_commons_images(query, max_results=20)
            for item in items:
                u = item["url"]
                if u not in seen_urls:
                    seen_urls.add(u)
                    candidate_items.append(item)
            time.sleep(0.2)

        # Nguồn 2: Bổ sung từ bài viết Wikipedia tương ứng (nếu có)
        if wiki_title and len(candidate_items) < 30:
            wiki_items = search_wikipedia_article_images(wiki_title, lang="vi", max_results=15)
            for item in wiki_items:
                u = item["url"]
                if u not in seen_urls:
                    seen_urls.add(u)
                    candidate_items.append(item)
            time.sleep(0.2)

        # Ưu tiên các ảnh CDN thumbnail (thumb.wikimedia.org) tải siêu tốc và ổn định
        candidate_items.sort(key=lambda x: not ("thumb.wikimedia.org" in x.get("url", "")))

        # 3. Tiến hành tải và chuẩn hóa ảnh
        new_downloads = 0
        for item in candidate_items:
            if collected_for_place >= TARGET_IMAGES_PER_LANDMARK:
                break

            img_url = item["url"]
            file_name = f"img_{collected_for_place + 1:02d}.jpg"
            save_path = os.path.join(place_dir, file_name)

            success = download_and_process_image(img_url, save_path)
            if success:
                # Kiểm tra trùng lặp nội dung qua MD5 hash
                img_hash = get_image_hash(save_path)
                if img_hash and img_hash in seen_hashes:
                    try:
                        os.remove(save_path)
                    except Exception:
                        pass
                    continue

                seen_hashes.add(img_hash)
                collected_for_place += 1
                new_downloads += 1
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
                    "caption": f"Ảnh tư liệu check-in di sản tại {place_name} ({sub_name}) Cố đô Huế",
                    "latitude": lat,
                    "longitude": lng
                })
                print(f"   ✓ [Ảnh {collected_for_place:02d}/{TARGET_IMAGES_PER_LANDMARK}] {file_name} <- {item['title'][:45]}", flush=True)
                time.sleep(0.15)

        print(f"   📊 Tổng cộng địa điểm này: {collected_for_place} ảnh (Mới tải thêm: {new_downloads})", flush=True)

    # 4. Ghi file Metadata JSON hoàn chỉnh
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata_list, f, ensure_ascii=False, indent=2)

    elapsed = time.time() - t_start
    print("\n" + "=" * 80, flush=True)
    print(f"🎉 HOÀN TẤT THU THẬP BỘ DỮ LIỆU ẢNH DI SẢN HUẾ!", flush=True)
    print(f"📊 Tổng số địa danh: {len(LANDMARKS_CONFIG)} địa danh", flush=True)
    print(f"🖼️ Tổng số ảnh trong cơ sở dữ liệu: {len(metadata_list)} ảnh (Mới tải phiên này: {total_downloaded})", flush=True)
    print(f"⏱️ Tổng thời gian thực hiện: {elapsed/60:.2f} phút", flush=True)
    print(f"📁 Thư mục lưu ảnh: {IMAGE_OUTPUT_DIR}", flush=True)
    print(f"📄 Metadata Index: {METADATA_FILE}", flush=True)
    print("=" * 80, flush=True)


if __name__ == "__main__":
    crawl_images_for_landmarks()
