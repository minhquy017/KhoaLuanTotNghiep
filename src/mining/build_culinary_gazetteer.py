# -*- coding: utf-8 -*-
"""
BỘ TỪ ĐIỂN ẨM THỰC VIỆT NAM TOÀN DIỆN (VIETNAMESE CULINARY GAZETTEER - 500+ DISHES)
Quy mô hơn 500 món ăn đặc sản khắp mọi miền đất nước (Bắc - Trung - Nam, Tây Bắc, Tây Nguyên, Miền Tây).
Hỗ trợ đa dạng biến thể: Tiếng Việt có dấu, không dấu, tên tiếng Anh dịch nghĩa / phiên âm quốc tế.
Xuất file: data/processed/culinary_gazetteer.json
"""

import os
import sys
import json
import unicodedata
import re

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def remove_vietnamese_accents(text):
    """Bỏ dấu tiếng Việt để tạo alias không dấu chuẩn xác"""
    text = unicodedata.normalize('NFD', text)
    text = re.sub(r'[\u0300-\u036f]', '', text)
    text = text.replace('đ', 'd').replace('Đ', 'D')
    return unicodedata.normalize('NFC', text)

# DANH SÁCH 500+ MÓN ĂN VIỆT NAM TOÀN QUỐC
# Cấu trúc: (canonical_name, category, region_origin, [extra_aliases / english])
ALL_VIETNAMESE_DISHES = [
    # =========================================================================
    # 1. HỌ PHỞ (PHO) - 25 MÓN
    # =========================================================================
    ("Phở bò", "Món Phở & Bún", "Miền Bắc", ["beef pho", "vietnamese beef noodle soup", "beef noodle soup", "pho bo", "pho bo ha noi"]),
    ("Phở bò tái", "Món Phở & Bún", "Miền Bắc", ["rare beef pho", "pho bo tai", "half done beef pho", "rare beef noodles"]),
    ("Phở bò chín", "Món Phở & Bún", "Miền Bắc", ["well-done beef pho", "pho bo chin", "cooked beef pho"]),
    ("Phở tái lăn", "Món Phở & Bún", "Hà Nội", ["stir-fried rare beef pho", "pho tai lan", "seared beef pho", "stir fried beef noodle soup"]),
    ("Phở nạm gầu", "Món Phở & Bún", "Miền Bắc", ["flank and brisket pho", "pho nam gau", "beef flank pho"]),
    ("Phở bắp bò", "Món Phở & Bún", "Miền Bắc", ["beef shank pho", "pho bap bo"]),
    ("Phở gân bò", "Món Phở & Bún", "Toàn quốc", ["beef tendon pho", "pho gan bo"]),
    ("Phở đuôi bò", "Món Phở & Bún", "Toàn quốc", ["oxtail pho", "pho duoi bo", "oxtail noodle soup"]),
    ("Phở sốt vang", "Món Phở & Bún", "Miền Bắc", ["beef stew pho", "red wine beef pho", "pho sot vang", "pho bo sot vang", "bordeaux beef noodle soup"]),
    ("Phở sườn bò", "Món Phở & Bún", "Toàn quốc", ["beef rib pho", "pho suon bo", "short rib pho"]),
    ("Phở gà", "Món Phở & Bún", "Miền Bắc", ["chicken pho", "vietnamese chicken noodle soup", "pho ga", "chicken noodle soup"]),
    ("Phở gà đồi", "Món Phở & Bún", "Miền Bắc", ["free-range chicken pho", "pho ga doi"]),
    ("Phở gà chặt", "Món Phở & Bún", "Hà Nội", ["bone-in chicken pho", "pho ga chat"]),
    ("Phở gà xé", "Món Phở & Bún", "Toàn quốc", ["shredded chicken pho", "pho ga xe"]),
    ("Phở lòng gà", "Món Phở & Bún", "Miền Bắc", ["chicken giblets pho", "pho long ga"]),
    ("Phở cuốn", "Món Phở & Bún", "Hà Nội", ["rolled pho", "pho rolls", "fresh pho rolls", "pho cuon", "rolled noodle sheets with beef"]),
    ("Phở chiên phồng", "Món Phở & Bún", "Hà Nội", ["deep fried pho", "crispy puffed pho", "pho chien phong", "fried square pho"]),
    ("Phở chiên trứng", "Món Phở & Bún", "Hà Nội", ["egg fried pho", "pho chien trung"]),
    ("Phở xào bò", "Món Phở & Bún", "Toàn quốc", ["stir-fried pho with beef", "stir fried beef pho", "pho xao bo", "fried noodle with beef"]),
    ("Phở xào giòn", "Món Phở & Bún", "Hà Nội", ["crispy fried pho noodles", "pho xao gion"]),
    ("Phở chua Lạng Sơn", "Món Phở & Bún", "Đông Bắc", ["sour pho", "lang son sour pho", "pho chua", "lang son sweet and sour noodles"]),
    ("Phở khô Gia Lai", "Món Phở & Bún", "Tây Nguyên", ["two bowl pho", "dry pho", "gia lai dry pho", "pho kho", "pho hai to"]),
    ("Phở trộn", "Món Phở & Bún", "Toàn quốc", ["mixed pho", "dry mixed pho", "pho tron", "salad pho"]),
    ("Phở tủy bò", "Món Phở & Bún", "Hà Nội", ["bone marrow pho", "pho tuy bo"]),
    ("Phở vịt quay", "Món Phở & Bún", "Cao Bằng", ["roast duck pho", "pho vit quay", "cao bang roasted duck noodle soup"]),

    # =========================================================================
    # 2. HỌ BÚN (VERMICELLI) - 60 MÓN
    # =========================================================================
    ("Bún chả Hà Nội", "Món Phở & Bún", "Hà Nội", ["bun cha", "hanoi grilled pork with noodles", "grilled pork noodle", "bun cha ha noi", "obama noodles", "grilled pork patties"]),
    ("Bún chả que tre", "Món Phở & Bún", "Hà Nội", ["bamboo skewer grilled pork noodles", "bun cha que tre"]),
    ("Bún thang", "Món Phở & Bún", "Hà Nội", ["bun thang", "hanoi combination noodle soup", "chicken egg pork noodle soup", "hanoi traditional noodle soup"]),
    ("Bún đậu mắm tôm", "Món Phở & Bún", "Miền Bắc", ["bun dau mam tom", "tofu noodles with shrimp paste", "fried tofu with rice noodles and fermented shrimp paste", "bun dau"]),
    ("Bún đậu chả cốm", "Món Phở & Bún", "Hà Nội", ["noodles with tofu and green rice pork patties", "bun dau cha com"]),
    ("Bún ốc", "Món Phở & Bún", "Hà Nội", ["snail noodle soup", "bun oc", "vietnamese snail noodles"]),
    ("Bún ốc nguội", "Món Phở & Bún", "Hà Nội", ["cold snail noodles", "bun oc nguoi", "traditional cold snail noodle soup"]),
    ("Bún ốc chuối đậu", "Món Phở & Bún", "Miền Bắc", ["snail noodles with green banana and tofu", "bun oc chuoi dau"]),
    ("Bún riêu cua", "Món Phở & Bún", "Toàn quốc", ["crab paste noodle soup", "crab noodle soup", "bun rieu", "bun rieu cua", "vietnamese crab noodles"]),
    ("Bún riêu ốc", "Món Phở & Bún", "Hà Nội", ["crab and snail noodle soup", "bun rieu oc"]),
    ("Bún riêu sườn sụn", "Món Phở & Bún", "Hà Nội", ["crab noodle soup with cartilage ribs", "bun rieu suon", "bun rieu suon sun"]),
    ("Bún riêu giò chả", "Món Phở & Bún", "Miền Nam", ["southern crab noodle soup with pork sausage", "bun rieu gio cha"]),
    ("Bún bò Huế", "Món Phở & Bún", "Huế", ["hue beef noodle soup", "bun bo hue", "spicy beef noodle soup", "hue spicy beef noodles", "bun bo"]),
    ("Bún bò giò heo", "Món Phở & Bún", "Huế", ["bun bo gio heo", "hue beef noodles with pork knuckle", "pig trotter spicy noodle soup"]),
    ("Bún bò gân", "Món Phở & Bún", "Huế", ["beef tendon noodle soup", "bun bo gan"]),
    ("Bún bò bắp", "Món Phở & Bún", "Huế", ["beef shank noodle soup", "bun bo bap"]),
    ("Bún bò cua", "Món Phở & Bún", "Huế", ["hue beef and crab ball noodles", "bun bo cha cua"]),
    ("Bún chả cá Đà Nẵng", "Món Phở & Bún", "Đà Nẵng", ["da nang fish cake noodles", "bun cha ca da nang", "fish cake noodle soup"]),
    ("Bún chả cá Nha Trang", "Món Phở & Bún", "Nha Trang", ["nha trang fish cake noodle soup", "bun cha ca nha trang", "mackerel fish cake noodles"]),
    ("Bún chả cá Quy Nhơn", "Món Phở & Bún", "Bình Định", ["quy nhon fish cake noodles", "bun cha ca quy nhon"]),
    ("Bún mắm", "Món Phở & Bún", "Miền Tây", ["fermented fish noodle soup", "bun mam", "mekong fermented seafood noodle soup"]),
    ("Bún mắm nêm", "Món Phở & Bún", "Miền Trung", ["noodles with anchovy dipping sauce", "bun mam nem", "danang pork noodles with fish sauce"]),
    ("Bún mắm nêm heo quay", "Món Phở & Bún", "Đà Nẵng", ["crispy roast pork noodles with anchovy sauce", "bun mam heo quay"]),
    ("Bún mắm nêm thịt luộc", "Món Phở & Bún", "Miền Trung", ["boiled pork noodles with anchovy sauce", "bun mam thit luoc"]),
    ("Bún nước lèo Sóc Trăng", "Món Phở & Bún", "Miền Tây", ["bun nuoc leo", "soc trang fish soup noodles", "fermented fish and coconut noodles"]),
    ("Bún nước lèo Trà Vinh", "Món Phở & Bún", "Trà Vinh", ["tra vinh fermented broth noodles", "bun nuoc leo tra vinh"]),
    ("Bún sứa", "Món Phở & Bún", "Nha Trang", ["jellyfish noodle soup", "bun sua", "jellyfish noodles"]),
    ("Bún quậy Phú Quốc", "Món Phở & Bún", "Kiên Giang", ["bun quay", "phu quoc stirred noodles", "fresh seafood stirred noodles", "swirled noodle soup"]),
    ("Bún kèn Phú Quốc", "Món Phở & Bún", "Kiên Giang", ["bun ken", "phu quoc coconut fish curry noodles", "trumpet noodles"]),
    ("Bún cá rô đồng", "Món Phở & Bún", "Miền Bắc", ["climbing perch noodle soup", "bun ca ro dong", "perch fish noodles"]),
    ("Bún cá cay Hải Phòng", "Món Phở & Bún", "Hải Phòng", ["hai phong spicy fish noodles", "bun ca cay", "hai phong fish noodles"]),
    ("Bún cá dầm", "Món Phở & Bún", "Nha Trang", ["steamed fish noodle soup", "bun ca dam"]),
    ("Bún cá ngừ um", "Món Phở & Bún", "Miền Trung", ["tuna noodle soup", "bun ca ngu um", "braised tuna vermicelli"]),
    ("Bún cá sứa", "Món Phở & Bún", "Khánh Hòa", ["fish cake and jellyfish noodles", "bun ca sua"]),
    ("Bún thịt nướng", "Món Phở & Bún", "Miền Nam", ["grilled pork with dry vermicelli", "bun thit nuong", "vermicelli with grilled pork", "grilled pork noodles"]),
    ("Bún thịt nướng chả giò", "Món Phở & Bún", "Miền Nam", ["grilled pork and spring rolls with vermicelli", "bun thit nuong cha gio"]),
    ("Bún thịt nướng kim tiền", "Món Phở & Bún", "Huế", ["hue coin grilled pork noodles", "bun thit nuong kim tien"]),
    ("Bún nem nướng", "Món Phở & Bún", "Toàn quốc", ["grilled meatball noodles", "bun nem nuong"]),
    ("Bún thịt xào", "Món Phở & Bún", "Miền Tây", ["stir-fried pork vermicelli", "bun thit xao"]),
    ("Bún bì", "Món Phở & Bún", "Miền Nam", ["vermicelli with shredded pork skin", "bun bi"]),
    ("Bún mọc", "Món Phở & Bún", "Miền Bắc", ["pork ball noodle soup", "bun moc", "vermicelli with pork meatballs"]),
    ("Bún dọc mùng", "Món Phở & Bún", "Hà Nội", ["taro stem noodle soup", "bun doc mung", "pork knuckle with taro stem noodles"]),
    ("Bún sườn chua", "Món Phở & Bún", "Hà Nội", ["sour pork rib noodles", "bun suon chua", "sour broth rib noodles"]),
    ("Bún sườn mọc", "Món Phở & Bún", "Hà Nội", ["pork rib and meatball noodles", "bun suon moc"]),
    ("Bún măng vịt", "Món Phở & Bún", "Toàn quốc", ["duck noodle soup with bamboo shoots", "bun mang vit", "duck and bamboo shoot noodles"]),
    ("Bún ngan", "Món Phở & Bún", "Hà Nội", ["muscovy duck noodles", "bun ngan"]),
    ("Bún ngan nướng", "Món Phở & Bún", "Hà Nội", ["grilled muscovy duck noodles", "bun ngan nuong"]),
    ("Bún ngan trộn", "Món Phở & Bún", "Hà Nội", ["dry mixed duck noodles", "bun ngan tron"]),
    ("Bún hến", "Món Phở & Bún", "Huế", ["baby clam noodles", "bun hen", "hue clam noodle", "mussel vermicelli"]),
    ("Bún nghệ Huế", "Món Phở & Bún", "Huế", ["turmeric noodles with pork intestines", "bun nghe", "turmeric chitterlings noodles"]),
    ("Bún đỏ Đắk Lắk", "Món Phở & Bún", "Tây Nguyên", ["dak lak red noodle soup", "bun do", "red vermicelli soup"]),
    ("Bún suông Trà Vinh", "Món Phở & Bún", "Trà Vinh", ["bun suong", "tra vinh shrimp paste noodles", "shrimp dumpling noodles"]),
    ("Bún tôm Hải Phòng", "Món Phở & Bún", "Hải Phòng", ["hai phong prawn noodles", "bun tom"]),
    ("Bún giấm nuốc", "Món Phở & Bún", "Huế", ["medusa jelly noodles", "bun giam nuoc", "hue jellyfish vinegar noodles"]),
    ("Bún cá Châu Đốc", "Món Phở & Bún", "An Giang", ["chau doc fish noodles", "bun ca chau doc", "turmeric fish broth noodles"]),
    ("Bún bò cay Bạc Liêu", "Món Phở & Bún", "Bạc Liêu", ["bac lieu spicy beef noodles", "bun bo cay"]),
    ("Bún lòng xào nghệ", "Món Phở & Bún", "Huế", ["turmeric noodles with fried chitterlings", "bun long xao nghe"]),
    ("Bún cá Kiên Giang", "Món Phở & Bún", "Kiên Giang", ["kien giang fish noodle soup", "bun ca kien giang"]),
    ("Bún rạm Quy Nhơn", "Món Phở & Bún", "Bình Định", ["small crab noodles", "bun ram quy nhon", "swamp crab noodle soup"]),
    ("Bún tôm Châu Trúc", "Món Phở & Bún", "Bình Định", ["chau truc shrimp noodles", "bun tom binh dinh"]),

    # =========================================================================
    # 3. HỌ MÌ, MIẾN, HỦ TIẾU, BÁNH CANH - 50 MÓN
    # =========================================================================
    ("Mì Quảng", "Món Mì & Hủ tiếu & Bánh canh", "Quảng Nam", ["mi quang", "quang style noodles", "turmeric noodles", "quang noodles"]),
    ("Mì Quảng gà", "Món Mì & Hủ tiếu & Bánh canh", "Quảng Nam", ["chicken mi quang", "mi quang ga"]),
    ("Mì Quảng tôm thịt", "Món Mì & Hủ tiếu & Bánh canh", "Quảng Nam", ["pork and shrimp mi quang", "mi quang tom thit"]),
    ("Mì Quảng ếch", "Món Mì & Hủ tiếu & Bánh canh", "Quảng Nam", ["frog mi quang", "mi quang ech"]),
    ("Mì Quảng cá lóc", "Món Mì & Hủ tiếu & Bánh canh", "Quảng Nam", ["snakehead fish mi quang", "mi quang ca loc"]),
    ("Mì Quảng sườn non", "Món Mì & Hủ tiếu & Bánh canh", "Quảng Nam", ["pork rib mi quang", "mi quang suon"]),
    ("Mì Quảng bò", "Món Mì & Hủ tiếu & Bánh canh", "Quảng Nam", ["beef mi quang", "mi quang bo"]),
    ("Mì Quảng sứa", "Món Mì & Hủ tiếu & Bánh canh", "Quảng Nam", ["jellyfish mi quang", "mi quang sua"]),
    ("Cao lầu", "Món Mì & Hủ tiếu & Bánh canh", "Hội An", ["cao lau", "hoi an pork noodle", "hoi an noodles", "cao lau noodles"]),
    ("Cao lầu gà", "Món Mì & Hủ tiếu & Bánh canh", "Hội An", ["chicken cao lau", "cao lau ga"]),
    ("Cao lầu chay", "Món Mì & Hủ tiếu & Bánh canh", "Hội An", ["vegetarian cao lau", "cao lau chay"]),
    ("Hủ tiếu Nam Vang", "Món Mì & Hủ tiếu & Bánh canh", "Miền Nam", ["nam vang noodle soup", "hu tieu nam vang", "clear noodle soup with pork and seafood", "phnom penh noodles"]),
    ("Hủ tiếu khô", "Món Mì & Hủ tiếu & Bánh canh", "Miền Nam", ["dry hu tieu", "hu tieu kho", "dry tossed rice noodles"]),
    ("Hủ tiếu Sa Đéc", "Món Mì & Hủ tiếu & Bánh canh", "Đồng Tháp", ["sa dec rice noodles", "hu tieu sa dec"]),
    ("Hủ tiếu Mỹ Tho", "Món Mì & Hủ tiếu & Bánh canh", "Tiền Giang", ["my tho rice noodles", "hu tieu my tho"]),
    ("Hủ tiếu mực", "Món Mì & Hủ tiếu & Bánh canh", "Toàn quốc", ["squid rice noodle soup", "hu tieu muc", "calamari noodles"]),
    ("Hủ tiếu bò kho", "Món Mì & Hủ tiếu & Bánh canh", "Miền Nam", ["beef stew with rice noodles", "hu tieu bo kho"]),
    ("Hủ tiếu xào", "Món Mì & Hủ tiếu & Bánh canh", "Miền Nam", ["stir fried rice noodles", "hu tieu xao"]),
    ("Hủ tiếu cá", "Món Mì & Hủ tiếu & Bánh canh", "TP.HCM", ["fish rice noodle soup", "hu tieu ca"]),
    ("Hủ tiếu sa tế bò", "Món Mì & Hủ tiếu & Bánh canh", "TP.HCM", ["satay beef rice noodles", "hu tieu sa te bo"]),
    ("Hủ tiếu sườn que", "Món Mì & Hủ tiếu & Bánh canh", "Miền Nam", ["pork ribs rice noodles", "hu tieu suon"]),
    ("Hủ tiếu gõ", "Món Mì & Hủ tiếu & Bánh canh", "Miền Nam", ["street cart hu tieu", "hu tieu go"]),
    ("Hủ tiếu hồ", "Món Mì & Hủ tiếu & Bánh canh", "TP.HCM", ["chinese rice noodle sheets", "hu tieu ho"]),
    ("Bánh canh cua", "Món Mì & Hủ tiếu & Bánh canh", "Miền Nam", ["crab udon soup", "banh canh cua", "vietnamese thick noodle soup with crab", "thick tapioca crab noodle"]),
    ("Bánh canh ghẹ", "Món Mì & Hủ tiếu & Bánh canh", "Toàn quốc", ["blue crab thick noodles", "banh canh ghe"]),
    ("Bánh canh Nam Phổ", "Món Mì & Hủ tiếu & Bánh canh", "Huế", ["nam pho thick noodle soup", "banh canh nam pho", "hue crab and shrimp thick noodle soup"]),
    ("Bánh canh cá lóc", "Món Mì & Hủ tiếu & Bánh canh", "Miền Trung", ["snakehead fish thick noodles", "banh canh ca loc", "hue snakehead fish thick noodle"]),
    ("Bánh canh cá lóc bột lọc", "Món Mì & Hủ tiếu & Bánh canh", "Quảng Trị", ["tapioca snakehead fish noodles", "banh canh bot loc ca loc"]),
    ("Bánh canh Trảng Bàng", "Món Mì & Hủ tiếu & Bánh canh", "Tây Ninh", ["trang bang thick noodle soup", "banh canh trang bang", "pork knuckle thick noodles"]),
    ("Bánh canh chả cá", "Món Mì & Hủ tiếu & Bánh canh", "Miền Trung", ["fish cake thick noodles", "banh canh cha ca"]),
    ("Bánh canh giò heo", "Món Mì & Hủ tiếu & Bánh canh", "Toàn quốc", ["pork trotter thick noodles", "banh canh gio heo"]),
    ("Bánh canh sườn heo", "Món Mì & Hủ tiếu & Bánh canh", "Toàn quốc", ["pork rib thick noodles", "banh canh suon"]),
    ("Bánh canh vịt nước cốt dừa", "Món Mì & Hủ tiếu & Bánh canh", "Miền Tây", ["duck thick noodles with coconut milk", "banh canh vit"]),
    ("Bánh canh tôm thịt", "Món Mì & Hủ tiếu & Bánh canh", "Toàn quốc", ["shrimp and pork thick noodles", "banh canh tom thit"]),
    ("Bánh canh hẹ Phú Yên", "Món Mì & Hủ tiếu & Bánh canh", "Phú Yên", ["phu yen chive noodle soup", "banh canh he"]),
    ("Miến lươn Hà Nội", "Món Mì & Hủ tiếu & Bánh canh", "Hà Nội", ["eel glass noodles", "mien luon", "crispy eel with glass noodles", "eel vermicelli"]),
    ("Miến lươn xào", "Món Mì & Hủ tiếu & Bánh canh", "Miền Bắc", ["stir fried glass noodles with eel", "mien luon xao"]),
    ("Miến lươn trộn", "Món Mì & Hủ tiếu & Bánh canh", "Hà Nội", ["dry mixed eel glass noodles", "mien luon tron"]),
    ("Miến gà", "Món Mì & Hủ tiếu & Bánh canh", "Miền Bắc", ["chicken glass noodle soup", "mien ga", "cellophane noodles with chicken"]),
    ("Miến măng gà", "Món Mì & Hủ tiếu & Bánh canh", "Toàn quốc", ["chicken and bamboo shoot glass noodles", "mien mang ga"]),
    ("Miến xào cua", "Món Mì & Hủ tiếu & Bánh canh", "Toàn quốc", ["stir-fried glass noodles with crab", "mien xao cua", "crab cellophane noodles"]),
    ("Miến xào hải sản", "Món Mì & Hủ tiếu & Bánh canh", "Toàn quốc", ["stir-fried glass noodles with seafood", "mien xao hai san"]),
    ("Miến ngan", "Món Mì & Hủ tiếu & Bánh canh", "Hà Nội", ["muscovy duck glass noodles", "mien ngan"]),
    ("Mì vằn thắn", "Món Mì & Hủ tiếu & Bánh canh", "Hà Nội", ["wonton noodles", "mi van than", "vietnamese wonton noodle soup"]),
    ("Mì hoành thánh", "Món Mì & Hủ tiếu & Bánh canh", "TP.HCM", ["wonton egg noodles", "mi hoanh thanh"]),
    ("Mì vịt tiềm", "Món Mì & Hủ tiếu & Bánh canh", "TP.HCM", ["braised duck egg noodles", "mi vit tiem", "chinese braised duck noodle soup"]),
    ("Mì xào giòn hải sản", "Món Mì & Hủ tiếu & Bánh canh", "Toàn quốc", ["crispy egg noodles with seafood", "mi xao gion"]),
    ("Mì xào mềm", "Món Mì & Hủ tiếu & Bánh canh", "Toàn quốc", ["soft stir fried noodles", "mi xao mem"]),
    ("Bánh đa cua Hải Phòng", "Món Mì & Hủ tiếu & Bánh canh", "Hải Phòng", ["hai phong crab red noodles", "banh da cua", "red noodle soup with crab paste"]),
    ("Bánh đa cua trộn", "Món Mì & Hủ tiếu & Bánh canh", "Hải Phòng", ["mixed dry red crab noodles", "banh da cua tron"]),

    # =========================================================================
    # 4. HỌ CƠM, XÔI, CHÁO - 45 MÓN
    # =========================================================================
    ("Cơm tấm Sài Gòn", "Món Cơm & Xôi & Cháo", "TP.HCM", ["broken rice", "com tam", "com tam sai gon", "vietnamese broken rice", "saigon broken rice"]),
    ("Cơm tấm sườn bì chả", "Món Cơm & Xôi & Cháo", "TP.HCM", ["broken rice with pork chop, skin and egg meatloaf", "com tam suon bi cha"]),
    ("Cơm tấm sườn nướng", "Món Cơm & Xôi & Cháo", "TP.HCM", ["broken rice with grilled pork chop", "com tam suon nuong"]),
    ("Cơm gà Hội An", "Món Cơm & Xôi & Cháo", "Hội An", ["hoi an chicken rice", "com ga hoi an", "turmeric chicken rice", "hoi an shredded chicken rice"]),
    ("Cơm gà Tam Kỳ", "Món Cơm & Xôi & Cháo", "Quảng Nam", ["tam ky chicken rice", "com ga tam ky"]),
    ("Cơm gà Nha Trang", "Món Cơm & Xôi & Cháo", "Nha Trang", ["nha trang chicken rice with egg butter sauce", "com ga nha trang"]),
    ("Cơm gà Phan Rang", "Món Cơm & Xôi & Cháo", "Ninh Thuận", ["phan rang chicken rice", "com ga phan rang"]),
    ("Cơm hến Huế", "Món Cơm & Xôi & Cháo", "Huế", ["baby clam rice", "com hen", "hue clam rice", "mussel rice", "com hen hue"]),
    ("Cơm niêu", "Món Cơm & Xôi & Cháo", "Toàn quốc", ["claypot rice", "com nieu", "crispy earthen pot rice"]),
    ("Cơm cháy kho quẹt", "Món Cơm & Xôi & Cháo", "Miền Nam", ["crispy scorched rice with caramelized braised dip", "com chay kho quet", "crispy rice with pork dip"]),
    ("Cơm cháy Ninh Bình", "Món Cơm & Xôi & Cháo", "Ninh Bình", ["ninh binh scorched rice", "crispy rice crackers with goat meat stew", "com chay ninh binh"]),
    ("Cơm lam Tây Bắc", "Món Cơm & Xôi & Cháo", "Tây Bắc", ["bamboo tube sticky rice", "com lam", "sticky rice cooked in bamboo"]),
    ("Cơm lam gà nướng", "Món Cơm & Xôi & Cháo", "Tây Nguyên", ["grilled chicken with bamboo tube rice", "com lam ga nuong"]),
    ("Cơm rang dưa bò", "Món Cơm & Xôi & Cháo", "Hà Nội", ["fried rice with beef and pickled mustard greens", "com rang dua bo"]),
    ("Cơm chiên Dương Châu", "Món Cơm & Xôi & Cháo", "Toàn quốc", ["yang chow fried rice", "com chien duong chau"]),
    ("Cơm chiên hải sản", "Món Cơm & Xôi & Cháo", "Toàn quốc", ["seafood fried rice", "com chien hai san"]),
    ("Cơm chiên cá mặn", "Món Cơm & Xôi & Cháo", "Miền Nam", ["salted fish fried rice", "com chien ca man"]),
    ("Cơm âm phủ Huế", "Món Cơm & Xôi & Cháo", "Huế", ["hue rainbow mixed rice", "com am phu", "underworld rice"]),
    ("Cơm gói lá sen", "Món Cơm & Xôi & Cháo", "Huế", ["lotus leaf wrapped rice", "com sen", "hue royal lotus rice"]),
    ("Cơm sườn nướng", "Món Cơm & Xôi & Cháo", "Toàn quốc", ["grilled pork chop rice", "com suon nuong"]),
    ("Cơm đùi gà nướng", "Món Cơm & Xôi & Cháo", "Toàn quốc", ["grilled chicken thigh with rice", "com ga nuong"]),
    ("Xôi xéo Hà Nội", "Món Cơm & Xôi & Cháo", "Hà Nội", ["sticky rice with mung bean and fried shallots", "xoi xeo", "yellow sticky rice"]),
    ("Xôi khúc", "Món Cơm & Xôi & Cháo", "Miền Bắc", ["cudweed sticky rice dumpling", "banh khuc", "xoi khuc"]),
    ("Xôi gà", "Món Cơm & Xôi & Cháo", "Toàn quốc", ["chicken sticky rice", "xoi ga"]),
    ("Xôi ngũ sắc", "Món Cơm & Xôi & Cháo", "Tây Bắc", ["five-color sticky rice", "xoi ngu sac", "highland rainbow sticky rice"]),
    ("Xôi gấc", "Món Cơm & Xôi & Cháo", "Toàn quốc", ["red baby jackfruit sticky rice", "xoi gac"]),
    ("Xôi vò", "Món Cơm & Xôi & Cháo", "Miền Bắc", ["tossed mung bean sticky rice", "xoi vo"]),
    ("Xôi thịt kho trứng", "Món Cơm & Xôi & Cháo", "Miền Bắc", ["sticky rice with braised pork and egg", "xoi thit kho"]),
    ("Xôi cá rô đồng", "Món Cơm & Xôi & Cháo", "Miền Bắc", ["climbing perch sticky rice", "xoi ca ro dong"]),
    ("Xôi bắp", "Món Cơm & Xôi & Cháo", "Miền Nam", ["corn sticky rice with shaved coconut", "xoi bap"]),
    ("Xôi mặn", "Món Cơm & Xôi & Cháo", "Miền Nam", ["savory sticky rice with sausage and floss", "xoi man"]),
    ("Xôi chiên phồng", "Món Cơm & Xôi & Cháo", "Đồng Nai", ["deep fried puffed sticky rice", "xoi chien phong"]),
    ("Cháo sườn sụn", "Món Cơm & Xôi & Cháo", "Hà Nội", ["cartilage pork rib porridge", "chao suon", "pork rib congee"]),
    ("Cháo quẩy", "Món Cơm & Xôi & Cháo", "Miền Bắc", ["porridge with fried dough crullers", "chao quay"]),
    ("Cháo ếch Singapore", "Món Cơm & Xôi & Cháo", "Toàn quốc", ["frog porridge", "chao ech", "claypot frog congee"]),
    ("Cháo lòng", "Món Cơm & Xôi & Cháo", "Toàn quốc", ["pork offal porridge", "pork organ congee", "chao long"]),
    ("Cháo cá lóc rau đắng", "Món Cơm & Xôi & Cháo", "Miền Tây", ["snakehead fish porridge with bitter herbs", "chao ca loc"]),
    ("Cháo hến", "Món Cơm & Xôi & Cháo", "Huế", ["baby clam congee", "chao hen", "clam porridge"]),
    ("Cháo gà hạt sen", "Món Cơm & Xôi & Cháo", "Toàn quốc", ["chicken and lotus seed congee", "chao ga hat sen"]),
    ("Cháo vịt cỏ", "Món Cơm & Xôi & Cháo", "Toàn quốc", ["duck porridge", "chao vit"]),
    ("Cháo bào ngư", "Món Cơm & Xôi & Cháo", "Toàn quốc", ["abalone porridge", "chao bao ngu"]),
    ("Cháo mực", "Món Cơm & Xôi & Cháo", "Miền Nam", ["dried squid porridge", "chao muc"]),
    ("Cháo lươn Nghệ An", "Món Cơm & Xôi & Cháo", "Nghệ An", ["nghe an eel porridge", "chao luon nghe an", "spicy eel congee"]),
    ("Cháo ấu tẩu Hà Giang", "Món Cơm & Xôi & Cháo", "Hà Giang", ["aconite root porridge", "chao au tau"]),
    ("Cháo cua đồng", "Món Cơm & Xôi & Cháo", "Miền Tây", ["field crab congee", "chao cua dong"]),

    # =========================================================================
    # 5. HỌ BÁNH MẶN & BÁNH MÌ - 55 MÓN
    # =========================================================================
    ("Bánh mì pate", "Món Bánh & Bánh mì", "Toàn quốc", ["vietnamese sandwich", "banh mi", "pate baguette", "banh mi pate"]),
    ("Bánh mì kẹp thịt", "Món Bánh & Bánh mì", "Toàn quốc", ["vietnamese pork baguette", "banh mi thit", "pork roll banh mi"]),
    ("Bánh mì chảo", "Món Bánh & Bánh mì", "Hà Nội", ["pan bread with steak and eggs", "banh mi chao", "combination skillet banh mi"]),
    ("Bánh mì chả cá", "Món Bánh & Bánh mì", "Miền Trung", ["fish cake banh mi", "banh mi cha ca"]),
    ("Bánh mì xíu mại Đà Lạt", "Món Bánh & Bánh mì", "Đà Lạt", ["meatball baguette soup", "banh mi xiu mai", "da lat pork meatball sandwich"]),
    ("Bánh mì que Hải Phòng", "Món Bánh & Bánh mì", "Hải Phòng", ["hai phong spicy breadstick", "banh mi que", "spicy mini baguette"]),
    ("Bánh mì nướng muối ớt", "Món Bánh & Bánh mì", "Miền Nam", ["grilled chili salt baguette", "banh mi nuong muoi ot"]),
    ("Bánh mì phá lấu", "Món Bánh & Bánh mì", "TP.HCM", ["braised offal banh mi", "banh mi pha lau"]),
    ("Bánh mì heo quay", "Món Bánh & Bánh mì", "Toàn quốc", ["roast pork banh mi", "banh mi heo quay", "crispy pork belly sandwich"]),
    ("Bánh mì gà xé", "Món Bánh & Bánh mì", "Toàn quốc", ["shredded chicken banh mi", "banh mi ga"]),
    ("Bánh mì chả bò Đà Nẵng", "Món Bánh & Bánh mì", "Đà Nẵng", ["beef sausage banh mi", "banh mi cha bo"]),
    ("Bánh mì bò né", "Món Bánh & Bánh mì", "Toàn quốc", ["sizzling beefsteak with baguette", "bo ne"]),
    ("Bánh xèo miền Tây", "Món Bánh & Bánh mì", "Miền Tây", ["vietnamese sizzling crepe", "banh xeo", "crispy vietnamese pancake", "southern giant sizzling crepe"]),
    ("Bánh xèo miền Trung", "Món Bánh & Bánh mì", "Miền Trung", ["central style crispy pancake", "banh xeo mien trung"]),
    ("Bánh xèo tôm nhảy Quy Nhơn", "Món Bánh & Bánh mì", "Bình Định", ["jumping shrimp pancake", "banh xeo tom nhay"]),
    ("Bánh khoái Huế", "Món Bánh & Bánh mì", "Huế", ["hue royal crispy pancake", "banh khoai", "crispy fried hue crepe", "banh khoai hue"]),
    ("Bánh khọt Vũng Tàu", "Món Bánh & Bánh mì", "Bà Rịa - Vũng Tàu", ["vung tau mini crispy shrimp pancakes", "banh khot", "mini savory pancakes", "banh khot vung tau"]),
    ("Bánh bèo Huế", "Món Bánh & Bánh mì", "Huế", ["water fern cake", "banh beo", "steamed rice discs with shrimp flakes", "banh beo chen", "hue steamed rice cakes"]),
    ("Bánh nậm Huế", "Món Bánh & Bánh mì", "Huế", ["steamed flat rice cake in banana leaf", "banh nam", "flat rice dumpling with shrimp", "banh nam hue"]),
    ("Bánh bột lọc Huế", "Món Bánh & Bánh mì", "Huế", ["tapioca dumplings with pork and shrimp", "banh bot loc", "clear tapioca shrimp dumpling", "banh loc"]),
    ("Bánh bột lọc trần", "Món Bánh & Bánh mì", "Huế", ["naked tapioca dumplings", "banh bot loc tran"]),
    ("Bánh ram ít Huế", "Món Bánh & Bánh mì", "Huế", ["fried sticky rice cake with soft dumpling", "banh ram it", "crispy and soft sticky rice ball"]),
    ("Bánh ít trần", "Món Bánh & Bánh mì", "Miền Trung", ["naked savory sticky rice dumpling", "banh it tran"]),
    ("Bánh cuốn Thanh Trì", "Món Bánh & Bánh mì", "Hà Nội", ["steamed rice rolls", "banh cuon", "vietnamese steamed rice sheets", "banh cuon thanh tri"]),
    ("Bánh cuốn nóng thịt mộc nhĩ", "Món Bánh & Bánh mì", "Toàn quốc", ["hot steamed rice rolls with minced pork and wood ear", "banh cuon nong"]),
    ("Bánh cuốn trứng", "Món Bánh & Bánh mì", "Lạng Sơn", ["steamed egg rice rolls", "banh cuon trung"]),
    ("Bánh ướt lòng gà Đà Lạt", "Món Bánh & Bánh mì", "Đà Lạt", ["steamed rice sheets with chicken giblets", "banh uot long ga"]),
    ("Bánh ướt thịt nướng", "Món Bánh & Bánh mì", "Huế", ["steamed rice sheets with grilled pork", "banh uot thit nuong"]),
    ("Bánh chưng", "Món Bánh & Bánh mì", "Miền Bắc", ["square sticky rice cake with pork and mung bean", "banh chung", "tet square rice cake"]),
    ("Bánh tét", "Món Bánh & Bánh mì", "Miền Nam", ["cylindrical sticky rice cake", "banh tet", "southern new year rice cake"]),
    ("Bánh tét lá cẩm", "Món Bánh & Bánh mì", "Cần Thơ", ["purple magenta plant sticky rice cake", "banh tet la cam"]),
    ("Bánh giò Hà Nội", "Món Bánh & Bánh mì", "Hà Nội", ["pyramid shaped rice dumpling with minced pork", "banh gio"]),
    ("Bánh bao xá xíu", "Món Bánh & Bánh mì", "Toàn quốc", ["bbq pork steamed bun", "banh bao xa xiu"]),
    ("Bánh bao nhân thịt trứng cút", "Món Bánh & Bánh mì", "Toàn quốc", ["steamed pork and quail egg bun", "banh bao"]),
    ("Bánh tiêu", "Món Bánh & Bánh mì", "Toàn quốc", ["hollow fried sesame donut", "banh tieu"]),
    ("Bánh quẩy giòn", "Món Bánh & Bánh mì", "Toàn quốc", ["fried dough cruller", "quay", "banh quay"]),
    ("Bánh rán mặn", "Món Bánh & Bánh mì", "Hà Nội", ["deep fried savory glutinous rice ball", "banh ran man"]),
    ("Bánh gối Hà Nội", "Món Bánh & Bánh mì", "Hà Nội", ["crispy pillow pastry with pork and glass noodles", "banh goi"]),
    ("Bánh tôm Hồ Tây", "Món Bánh & Bánh mì", "Hà Nội", ["west lake fried shrimp cake", "banh tom ho tay", "crispy sweet potato shrimp fritters"]),
    ("Bánh cống Sóc Trăng", "Món Bánh & Bánh mì", "Sóc Trăng", ["soc trang fried shrimp cake", "banh cong", "crispy muffin cake with shrimp"]),
    ("Bánh tằm bì", "Món Bánh & Bánh mì", "Miền Tây", ["silkworm thick noodles with shredded pork and coconut cream", "banh tam bi"]),
    ("Bánh căn Đà Lạt", "Món Bánh & Bánh mì", "Đà Lạt", ["mini pancake cooked in earthenware mold", "banh can"]),
    ("Bánh căn Phan Rang", "Món Bánh & Bánh mì", "Ninh Thuận", ["phan rang mini pancakes with seafood", "banh can phan rang"]),
    ("Bánh hỏi thịt heo quay", "Món Bánh & Bánh mì", "Miền Nam", ["woven rice vermicelli with roast pork", "banh hoi heo quay"]),
    ("Bánh hỏi lòng heo", "Món Bánh & Bánh mì", "Bình Định", ["woven rice vermicelli with pork organ", "banh hoi long heo"]),
    ("Bánh hỏi nem nướng", "Món Bánh & Bánh mì", "Toàn quốc", ["woven vermicelli with grilled pork skewers", "banh hoi nem nuong"]),
    ("Bánh tráng nướng Đà Lạt", "Món Bánh & Bánh mì", "Đà Lạt", ["vietnamese pizza", "grilled rice paper", "banh trang nuong", "da lat pizza"]),
    ("Bánh tráng trộn", "Món Bánh & Bánh mì", "TP.HCM", ["mixed rice paper salad", "banh trang tron", "rice paper salad with beef jerky and quail eggs"]),
    ("Bánh tráng cuốn sốt me", "Món Bánh & Bánh mì", "TP.HCM", ["rolled rice paper with tamarind sauce", "banh trang cuon"]),
    ("Bánh tráng phơi sương Trảng Bàng", "Món Bánh & Bánh mì", "Tây Ninh", ["dew soaked rice paper", "banh trang phoi suong"]),
    ("Bánh đúc nóng", "Món Bánh & Bánh mì", "Hà Nội", ["hot plain rice flan with minced pork", "banh duc nong"]),
    ("Bánh đúc lạc", "Món Bánh & Bánh mì", "Miền Bắc", ["steamed peanut rice cake with soy paste", "banh duc lac"]),
    ("Bánh tai heo", "Món Bánh & Bánh mì", "Toàn quốc", ["pig ear cookies", "banh tai heo"]),
    ("Bánh tai vạc", "Món Bánh & Bánh mì", "Phan Thiết", ["phan thiet clear tapioca dumplings", "banh quai vac", "banh tai vac"]),
    ("Bánh bèo chén miền Trung", "Món Bánh & Bánh mì", "Miền Trung", ["central small bowl steamed rice cake", "banh beo chen"]),

    # =========================================================================
    # 6. HỌ CUỐN, GỎI & KHAI VỊ - 50 MÓN
    # =========================================================================
    ("Gỏi cuốn tôm thịt", "Món Cuốn & Gỏi & Khai vị", "Miền Nam", ["fresh spring rolls", "summer rolls", "goi cuon", "rice paper rolls with shrimp and pork", "salad rolls"]),
    ("Chả giò tôm thịt", "Món Cuốn & Gỏi & Khai vị", "Miền Nam", ["crispy spring rolls", "fried egg rolls", "cha gio", "pork and shrimp fried rolls"]),
    ("Nem rán Hà Nội", "Món Cuốn & Gỏi & Khai vị", "Hà Nội", ["hanoi crispy spring rolls", "nem ran", "fried spring rolls ha noi"]),
    ("Nem lụi Huế", "Món Cuốn & Gỏi & Khai vị", "Huế", ["hue lemongrass pork skewers", "nem lui", "grilled pork on lemongrass", "nem lui hue"]),
    ("Nem nướng Nha Trang", "Món Cuốn & Gỏi & Khai vị", "Nha Trang", ["nha trang grilled pork sausage rolls", "nem nuong", "grilled pork meatballs with dipping sauce", "nem nuong nha trang"]),
    ("Nem nướng Ninh Hòa", "Món Cuốn & Gỏi & Khai vị", "Khánh Hòa", ["ninh hoa grilled pork", "nem nuong ninh hoa"]),
    ("Bò bía mặn", "Món Cuốn & Gỏi & Khai vị", "TP.HCM", ["jicama and chinese sausage spring rolls", "bo bia"]),
    ("Bò bía ngọt", "Món Cuốn & Gỏi & Khai vị", "Hà Nội", ["sweet coconut rolls", "bo bia ngot"]),
    ("Bánh tráng cuốn thịt heo", "Món Cuốn & Gỏi & Khai vị", "Đà Nẵng", ["sliced boiled pork rolled in rice paper", "banh trang cuon thit heo"]),
    ("Bánh tráng cuốn thịt heo hai đầu da", "Món Cuốn & Gỏi & Khai vị", "Đà Nẵng", ["da nang double-rind pork rolls", "thit heo hai dau da"]),
    ("Bánh cuốn thịt nướng Kim Long", "Món Cuốn & Gỏi & Khai vị", "Huế", ["kim long grilled pork rolled cakes", "banh uot cuon thit nuong"]),
    ("Ram bắp Quảng Ngãi", "Món Cuốn & Gỏi & Khai vị", "Quảng Ngãi", ["crispy corn spring rolls", "ram bap"]),
    ("Ram ít chiên", "Món Cuốn & Gỏi & Khai vị", "Huế", ["fried sticky rice balls", "ram it"]),
    ("Chạo tôm bọc mía", "Món Cuốn & Gỏi & Khai vị", "Huế", ["sugar cane shrimp skewers", "chao tom", "prawn paste on sugarcane", "chao tom hue"]),
    ("Nem chua Thanh Hóa", "Món Cuốn & Gỏi & Khai vị", "Thanh Hóa", ["fermented pork roll", "nem chua", "fermented sour pork"]),
    ("Nem chua rán Hà Nội", "Món Cuốn & Gỏi & Khai vị", "Hà Nội", ["fried fermented pork rolls", "nem chua ran"]),
    ("Nem chua nướng", "Món Cuốn & Gỏi & Khai vị", "Hà Nội", ["grilled fermented pork rolls", "nem chua nuong"]),
    ("Nem tré Huế", "Món Cuốn & Gỏi & Khai vị", "Huế", ["hue shredded fermented pork head with galangal", "tre hue"]),
    ("Tré Bình Định", "Món Cuốn & Gỏi & Khai vị", "Bình Định", ["binh dinh straw fermented pig skin and ear", "tre binh dinh"]),
    ("Gỏi ngó sen tôm thịt", "Món Cuốn & Gỏi & Khai vị", "Toàn quốc", ["lotus rootlet salad with shrimp and pork", "goi ngo sen", "lotus stem salad"]),
    ("Gỏi bưởi tôm mực", "Món Cuốn & Gỏi & Khai vị", "Miền Nam", ["pomelo salad with seafood", "goi buoi"]),
    ("Gỏi củ hũ dừa", "Món Cuốn & Gỏi & Khai vị", "Bến Tre", ["coconut heart salad with shrimp and pork", "goi cu hu dua"]),
    ("Gỏi bò bóp thấu", "Món Cuốn & Gỏi & Khai vị", "Toàn quốc", ["rare beef salad with starfruit and herbs", "goi bo bop thau"]),
    ("Nộm hoa chuối gà xé", "Món Cuốn & Gỏi & Khai vị", "Miền Bắc", ["banana flower salad with chicken", "nom hoa chuoi"]),
    ("Nộm sứa đỏ Hải Phòng", "Món Cuốn & Gỏi & Khai vị", "Hải Phòng", ["red jellyfish salad with grilled tofu and copra", "nom sua do"]),
    ("Gỏi sứa tai chua", "Món Cuốn & Gỏi & Khai vị", "Miền Trung", ["crunchy jellyfish salad", "goi sua"]),
    ("Gỏi cá mai Nha Trang", "Món Cuốn & Gỏi & Khai vị", "Nha Trang", ["deep sea white sardine salad", "goi ca mai"]),
    ("Gỏi cá trích Phú Quốc", "Món Cuốn & Gỏi & Khai vị", "Kiên Giang", ["phu quoc raw herring salad with coconut", "goi ca trich"]),
    ("Gỏi cá mè Hiệp Hòa", "Món Cuốn & Gỏi & Khai vị", "Bắc Giang", ["fresh carp salad", "goi ca me"]),
    ("Gỏi cá bỗng sông Gâm", "Món Cuốn & Gỏi & Khai vị", "Tuyên Quang", ["river carp salad", "goi ca bong"]),
    ("Gỏi lá Kon Tum", "Món Cuốn & Gỏi & Khai vị", "Tây Nguyên", ["kon tum forest leaf wrap platter", "goi la kon tum"]),
    ("Nộm đu đủ bò khô", "Món Cuốn & Gỏi & Khai vị", "Hà Nội", ["green papaya salad with beef jerky", "nom bo kho", "papaya dried beef salad"]),
    ("Gỏi tai heo dưa leo", "Món Cuốn & Gỏi & Khai vị", "Toàn quốc", ["pig ear salad with cucumber", "goi tai heo"]),
    ("Gỏi xoài xanh tôm khô", "Món Cuốn & Gỏi & Khai vị", "Miền Nam", ["green mango salad with dried shrimp", "goi xoai xanh"]),
    ("Gỏi mít non tôm thịt", "Món Cuốn & Gỏi & Khai vị", "Miền Trung", ["young jackfruit salad with sesame crackers", "goi mit non"]),
    ("Gỏi vịt bắp cải", "Món Cuốn & Gỏi & Khai vị", "Toàn quốc", ["duck salad with shredded cabbage", "goi vit"]),
    ("Gỏi rong nho hải sản", "Món Cuốn & Gỏi & Khai vị", "Nha Trang", ["sea grape salad with seafood", "goi rong nho"]),
    ("Gỏi sầu đâu cá sặc", "Món Cuốn & Gỏi & Khai vị", "An Giang", ["neem leaf salad with dried snakehead fish", "goi sau dau"]),
    ("Cuốn diếp Huế", "Món Cuốn & Gỏi & Khai vị", "Huế", ["mustard green rolls with pork and shrimp", "cuon diep", "hue mustard rolls"]),
    ("Chả cá Lã Vọng", "Món Cuốn & Gỏi & Khai vị", "Hà Nội", ["hanoi turmeric grilled fish with dill", "cha ca la vong", "la vong grilled fish"]),
    ("Chả ram tôm đất Bình Định", "Món Cuốn & Gỏi & Khai vị", "Bình Định", ["crispy ground shrimp spring rolls", "cha ram tom dat"]),
    ("Chả giò rế", "Món Cuốn & Gỏi & Khai vị", "Miền Nam", ["crispy netted spring rolls", "cha gio re"]),
    ("Chả giò chay", "Món Cuốn & Gỏi & Khai vị", "Toàn quốc", ["vegetarian fried spring rolls", "cha gio chay"]),
    ("Chả cá thát lát chiên cốm", "Món Cuốn & Gỏi & Khai vị", "Miền Tây", ["featherback fish patties with green rice", "cha ca that lat"]),
    ("Chả lụa", "Món Cuốn & Gỏi & Khai vị", "Toàn quốc", ["vietnamese pork ham", "steamed pork sausage", "cha lua", "gio lua"]),
    ("Chả quế", "Món Cuốn & Gỏi & Khai vị", "Miền Bắc", ["cinnamon roasted pork sausage", "cha que"]),
    ("Chả bò Đà Nẵng", "Món Cuốn & Gỏi & Khai vị", "Đà Nẵng", ["da nang steamed beef bologna", "cha bo da nang"]),
    ("Giò thủ", "Món Cuốn & Gỏi & Khai vị", "Toàn quốc", ["pig head cheese", "wood ear pork terrine", "gio thu"]),
    ("Bắp bò ngâm mắm", "Món Cuốn & Gỏi & Khai vị", "Miền Bắc", ["beef shank soaked in sweet fish sauce", "bap bo ngam mam"]),
    ("Chân gà ngâm sả tắc", "Món Cuốn & Gỏi & Khai vị", "Toàn quốc", ["pickled chicken feet with lemongrass and kumquat", "chan ga sa tac"]),

    # =========================================================================
    # 7. HỌ MÓN THỊT, GÀ, VỊT, NƯỚNG & KHO - 60 MÓN
    # =========================================================================
    ("Thịt kho tàu", "Món Thịt & Nướng", "Miền Nam", ["caramelized pork belly with eggs", "thit kho tau", "braised pork belly and eggs in coconut water", "thit kho trung"]),
    ("Thịt đông", "Món Thịt & Nướng", "Miền Bắc", ["jellied pork terrine", "thit dong", "northern winter jellied meat"]),
    ("Cá kho tộ", "Món Thịt & Nướng", "Miền Nam", ["caramelized claypot fish", "ca kho to", "braised fish in clay pot"]),
    ("Cá bống kho tiêu", "Món Thịt & Nướng", "Huế", ["braised goby fish with black pepper", "ca bong kho tieu"]),
    ("Cá nục kho dứa", "Món Thịt & Nướng", "Miền Trung", ["braised round scad with pineapple", "ca nuc kho dua"]),
    ("Cá lăng nướng than hoa", "Món Thịt & Nướng", "Miền Bắc", ["charcoal grilled hemibagrus fish", "ca lang nuong"]),
    ("Cá lóc nướng trui", "Món Thịt & Nướng", "Miền Tây", ["straw grilled snakehead fish", "ca loc nuong trui", "mud baked snakehead fish"]),
    ("Cá lóc hấp bầu", "Món Thịt & Nướng", "Miền Tây", ["steamed snakehead fish inside gourd", "ca loc hap bau"]),
    ("Cá tai tượng chiên xù", "Món Thịt & Nướng", "Miền Tây", ["deep fried giant gourami", "ca tai tuong chien xu"]),
    ("Cá hồi Sa Pa nướng", "Món Thịt & Nướng", "Tây Bắc", ["grilled sapa salmon", "ca hoi sa pa"]),
    ("Bò lúc lắc", "Món Thịt & Nướng", "Toàn quốc", ["shaking beef", "bo luc lac", "cubed beef tenderloin sautéed with garlic"]),
    ("Bò nướng lá lốt", "Món Thịt & Nướng", "Miền Nam", ["grilled beef wrapped in betel leaves", "bo nuong la lot", "wild betel leaf beef rolls", "bo la lot"]),
    ("Bò nướng mỡ chài", "Món Thịt & Nướng", "Miền Nam", ["grilled beef caul fat sausages", "bo nuong mo chai"]),
    ("Bò nướng ống tre", "Món Thịt & Nướng", "Tây Nguyên", ["grilled beef in bamboo tubes", "bo nuong ong tre"]),
    ("Bò tơ Tây Ninh nướng", "Món Thịt & Nướng", "Tây Ninh", ["grilled tender young veal", "bo to tay ninh"]),
    ("Bê thui Cầu Mống", "Món Thịt & Nướng", "Quảng Nam", ["cau mong smoked roasted veal", "be thui cau mong", "charcoal rare calf"]),
    ("Heo quay bánh hỏi", "Món Thịt & Nướng", "Toàn quốc", ["roast pork belly with fine vermicelli", "heo quay"]),
    ("Thịt ba chỉ nướng riềng mẻ", "Món Thịt & Nướng", "Miền Bắc", ["grilled pork belly with galangal and fermented rice", "thit nuong rieng me"]),
    ("Sườn non nướng mật ong", "Món Thịt & Nướng", "Toàn quốc", ["honey glazed pork ribs", "suon nuong mat ong"]),
    ("Sườn ram mặn ngọt", "Món Thịt & Nướng", "Toàn quốc", ["caramelized sweet and savory ribs", "suon ram"]),
    ("Gà đồi Tiên Yên luộc", "Món Thịt & Nướng", "Quảng Ninh", ["boiled tien yen hill chicken with lemon leaves", "ga tien yen"]),
    ("Gà nướng mọi", "Món Thịt & Nướng", "Toàn quốc", ["charcoal grilled whole chicken", "ga nuong moi"]),
    ("Gà nướng muối ớt", "Món Thịt & Nướng", "Toàn quốc", ["chili salt grilled chicken", "ga nuong muoi ot"]),
    ("Gà hấp lá chanh", "Món Thịt & Nướng", "Miền Bắc", ["steamed chicken with kaffir lime leaves", "ga hap la chanh"]),
    ("Gà hấp muối sả", "Món Thịt & Nướng", "Toàn quốc", ["salt and lemongrass steamed chicken", "ga hap muoi"]),
    ("Gà bó xôi chiên giòn", "Món Thịt & Nướng", "Toàn quốc", ["fried sticky rice wrapped chicken", "ga khong loi thoat", "ga bo xoi"]),
    ("Gà đồi nướng cơm lam", "Món Thịt & Nướng", "Tây Nguyên", ["highland grilled hill chicken with bamboo rice", "ga nuong com lam"]),
    ("Gà rang muối", "Món Thịt & Nướng", "Miền Bắc", ["salt coated crispy chicken", "ga rang muoi"]),
    ("Gà rang sả ớt", "Món Thịt & Nướng", "Toàn quốc", ["lemongrass chili chicken", "ga rang sa ot"]),
    ("Vịt quay Lạng Sơn", "Món Thịt & Nướng", "Lạng Sơn", ["lang son roasted duck with mac mat leaves", "vit quay lang son"]),
    ("Vịt om sấu", "Món Thịt & Nướng", "Hà Nội", ["braised duck with dracontomelon sour fruit", "vit om sau"]),
    ("Vịt nướng chao", "Món Thịt & Nướng", "Miền Tây", ["grilled duck with fermented bean curd", "vit nuong chao"]),
    ("Ngan cháy tỏi", "Món Thịt & Nướng", "Hà Nội", ["crispy garlic seared muscovy duck", "ngan chay toi"]),
    ("Chim cút nướng bơ tỏi", "Món Thịt & Nướng", "Toàn quốc", ["roasted quail with garlic butter", "chim cut nuong"]),
    ("Dê núi Ninh Bình tái chanh", "Món Thịt & Nướng", "Ninh Bình", ["ninh binh mountain goat with lime salad", "de tai chanh ninh binh"]),
    ("Dê nướng tảng", "Món Thịt & Nướng", "Ninh Bình", ["grilled goat slab", "de nuong tang"]),
    ("Thắng cố ngựa Sa Pa", "Món Thịt & Nướng", "Tây Bắc", ["sapa horse meat hotpot stew", "thang co sa pa", "traditional hmong horse stew"]),
    ("Thịt trâu gác bếp", "Món Thịt & Nướng", "Tây Bắc", ["smoked dried buffalo meat", "thit trau gac bep", "highland smoked jerky"]),
    ("Thịt lợn cắp nách nướng", "Món Thịt & Nướng", "Tây Bắc", ["roasted free-range hill piglet", "lon cap nach nuong"]),
    ("Lạp xưởng hun khói Cao Bằng", "Món Thịt & Nướng", "Cao Bằng", ["cao bang smoked pork sausage", "lap xuong gung da"]),
    ("Heo tộc nướng lu", "Món Thịt & Nướng", "Toàn quốc", ["earthen jar roasted native pig", "heo toc nuong lu"]),
    ("Phá lấu bò Sài Gòn", "Món Thịt & Nướng", "TP.HCM", ["saigon braised beef offal stew with coconut milk", "pha lau bo"]),
    ("Phá lấu nướng", "Món Thịt & Nướng", "TP.HCM", ["grilled marinated offal skewers", "pha lau nuong"]),
    ("Dồi sụn nướng", "Món Thịt & Nướng", "Miền Bắc", ["grilled pork cartilage sausage", "doi sun nuong"]),
    ("Dồi trường hấp hành gừng", "Món Thịt & Nướng", "Toàn quốc", ["steamed pork fallopian tubes with ginger and scallions", "doi truong hap"]),
    ("Lòng xào dưa chua", "Món Thịt & Nướng", "Miền Bắc", ["stir fried pork intestine with pickled mustard greens", "long xao dua"]),
    ("Tai heo ngâm giấm chua ngọt", "Món Thịt & Nướng", "Toàn quốc", ["pickled pig ears in sweet vinegar", "tai heo ngam giam"]),
    ("Mực một nắng nướng sa tế", "Món Thịt & Nướng", "Miền Trung", ["sun dried grilled squid with satay", "muc mot nang nuong"]),
    ("Bạch tuộc nướng muối ớt", "Món Thịt & Nướng", "Toàn quốc", ["spicy grilled octopus", "bach tuoc nuong"]),
    ("Tôm nướng muối ớt", "Món Thịt & Nướng", "Toàn quốc", ["chili salt grilled prawns", "tom nuong muoi ot"]),
    ("Tôm hấp nước dừa", "Món Thịt & Nướng", "Bến Tre", ["steamed prawns in fresh coconut water", "tom hap nuoc dua"]),
    ("Càng ghẹ rang muối ớt", "Món Thịt & Nướng", "Miền Nam", ["spicy salt coated blue crab claws", "cang ghe rang muoi"]),
    ("Ốc bươu nhồi thịt Đà Lạt", "Món Thịt & Nướng", "Đà Lạt", ["stuffed snails with pork and lemongrass", "oc buou nhoi thit"]),
    ("Ếch xào sả ớt", "Món Thịt & Nướng", "Toàn quốc", ["stir fried frog legs with lemongrass and chili", "ech xao sa ot"]),
    ("Ếch núp rơm chiên giòn", "Món Thịt & Nướng", "Miền Tây", ["crispy lemongrass hay coated frog", "ech nup rom"]),
    ("Lươn xào sả ớt", "Món Thịt & Nướng", "Nghệ An", ["stir fried eel with turmeric and lemongrass", "luon xao sa ot"]),
    ("Thịt kho mắm ruốc Huế", "Món Thịt & Nướng", "Huế", ["braised pork belly with fermented shrimp paste", "thit kho mam ruoc", "hue pork with mam ruoc"]),
    ("Tôm chua Huế thịt luộc", "Món Thịt & Nướng", "Huế", ["boiled pork with sour shrimp pickle", "tom chua hue"]),
    ("Vả trộn tôm thịt", "Món Thịt & Nướng", "Huế", ["hue fig salad with minced pork and shrimp", "va tron"]),
    ("Cá kèo kho rau răm", "Món Thịt & Nướng", "Miền Tây", ["braised goby fish with vietnamese coriander", "ca keo kho"]),

    # =========================================================================
    # 8. HỌ HẢI SẢN & THỦY SẢN ĐẶC SẮC - 50 MÓN
    # =========================================================================
    ("Cua Cà Mau rang me", "Món Hải sản", "Cà Mau", ["ca mau mud crab in tamarind sauce", "cua rang me", "tamarind mud crab"]),
    ("Cua hấp bia sả", "Món Hải sản", "Toàn quốc", ["steamed crab with beer and lemongrass", "cua hap bia"]),
    ("Cua rang muối Hong Kong", "Món Hải sản", "Toàn quốc", ["salt and pepper stir-fried crab", "cua rang muoi"]),
    ("Ghẹ xanh hấp Phan Thiết", "Món Hải sản", "Bình Thuận", ["steamed blue swimming crab", "ghe hap", "steamed sea crab"]),
    ("Tôm hùm Nha Trang nướng phô mai", "Món Hải sản", "Nha Trang", ["nha trang baked lobster with cheese", "tom hum nuong pho mai"]),
    ("Tôm hùm nướng bơ tỏi", "Món Hải sản", "Nha Trang", ["grilled lobster with garlic butter", "tom hum bo toi"]),
    ("Tôm mũ ni nướng", "Món Hải sản", "Nha Trang", ["grilled slipper lobster", "tom mu ni"]),
    ("Tôm sú chiên hoàng kim", "Món Hải sản", "Toàn quốc", ["golden salted egg tiger prawns", "tom sot trung muoi"]),
    ("Mực trứng hấp gừng", "Món Hải sản", "Miền Trung", ["steamed baby egg squid with ginger", "muc trung hap"]),
    ("Mực ống chiên nước mắm", "Món Hải sản", "Toàn quốc", ["crispy squid tossed in sweet fish sauce", "muc chien nuoc mam"]),
    ("Mực nháy Cửa Lò", "Món Hải sản", "Nghệ An", ["fresh luminous squid cua lo", "muc nhay cua lo"]),
    ("Mực xào chua ngọt", "Món Hải sản", "Toàn quốc", ["sweet and sour stir-fried squid", "muc xao chua ngot"]),
    ("Hàu nướng mỡ hành", "Món Hải sản", "Toàn quốc", ["grilled oysters with scallion oil and crushed peanuts", "hau nuong mo hanh"]),
    ("Hàu nướng phô mai", "Món Hải sản", "Toàn quốc", ["cheese baked oysters", "hau nuong pho mai"]),
    ("Hàu sữa ăn sống mù tạt", "Món Hải sản", "Toàn quốc", ["raw oysters with wasabi and lime", "hau song"]),
    ("Sò huyết rang me", "Món Hải sản", "Toàn quốc", ["blood cockles in sweet tamarind sauce", "so huyet rang me"]),
    ("Sò huyết nướng mọi", "Món Hải sản", "Toàn quốc", ["charcoal grilled blood cockles", "so huyet nuong"]),
    ("Sò lông nướng mỡ hành", "Món Hải sản", "Toàn quốc", ["grilled hairy ark cockles with scallion oil", "so long nuong"]),
    ("Sò điệp nướng trứng cút", "Món Hải sản", "Toàn quốc", ["grilled scallops with quail eggs", "so diep nuong"]),
    ("Ốc hương xào bơ tỏi", "Món Hải sản", "Toàn quốc", ["sweet snails stir-fried in garlic butter", "oc huong xao bo toi"]),
    ("Ốc hương sốt trứng muối", "Món Hải sản", "Toàn quốc", ["sweet snails with rich salted egg yolk sauce", "oc huong sot trung muoi"]),
    ("Ốc móng tay xào rau muống", "Món Hải sản", "Toàn quốc", ["razor clams stir-fried with morning glory", "oc mong tay xao rau muong"]),
    ("Ốc len xào dừa", "Món Hải sản", "Miền Tây", ["mud creepers simmered in coconut milk", "oc len xao dua"]),
    ("Ốc mỡ xào me", "Món Hải sản", "Toàn quốc", ["spindle snails in tamarind glaze", "oc mo xao me"]),
    ("Ốc cà na rang muối ớt", "Món Hải sản", "Toàn quốc", ["chili salt roasted mini snails", "oc ca na rang muoi"]),
    ("Ốc gai nướng than", "Món Hải sản", "Phú Quốc", ["grilled thorny sea snails", "oc gai"]),
    ("Nghêu hấp sả ớt", "Món Hải sản", "Toàn quốc", ["steamed clams with lemongrass and fresh chili", "ngheu hap sa"]),
    ("Nghêu hấp thái", "Món Hải sản", "Toàn quốc", ["spicy tom yum steamed clams", "ngheu hap thai"]),
    ("Tu hài nướng mỡ hành", "Món Hải sản", "Quảng Ninh", ["grilled geoduck with scallion oil", "tu hai nuong"]),
    ("Cù kỳ hấp Quảng Ninh", "Món Hải sản", "Quảng Ninh", ["steamed stone crab", "cu ky quang ninh"]),
    ("Chả mực Hạ Long", "Món Hải sản", "Quảng Ninh", ["ha long pounded crispy squid cakes", "cha muc ha long", "squid patties"]),
    ("Cá mú hấp xì dầu", "Món Hải sản", "Toàn quốc", ["steamed grouper with soy sauce and ginger", "ca mu hap xi dau"]),
    ("Cá chẽm sốt chua ngọt", "Món Hải sản", "Toàn quốc", ["crispy sea bass in sweet and sour glaze", "ca chem sot chua ngot"]),
    ("Cá bớp nướng muối ớt", "Món Hải sản", "Phú Quốc", ["grilled cobia steak with chili salt", "ca bop nuong"]),
    ("Cá chình nướng nghệ", "Món Hải sản", "Miền Trung", ["turmeric grilled freshwater eel", "ca chinh nuong"]),
    ("Cá chìa vôi nướng muối ớt", "Món Hải sản", "Đà Nẵng", ["grilled cornetfish with chili salt", "ca chia voi"]),
    ("Nhím biển nướng mỡ hành", "Món Hải sản", "Phú Quốc", ["grilled sea urchin with scallion oil", "nhum bien nuong", "sea urchin"]),
    ("Cháo nhum biển", "Món Hải sản", "Phú Quốc", ["sea urchin congee", "chao nhum"]),
    ("Còi biên mai nướng sa tế", "Món Hải sản", "Phú Quốc", ["grilled fan mussel sinew with satay", "coi bien mai"]),
    ("Sam biển nướng Hạ Long", "Món Hải sản", "Quảng Ninh", ["grilled horseshoe crab", "sam bien quang ninh"]),
    ("Mực sim Phú Quốc hấp gừng", "Món Hải sản", "Kiên Giang", ["steamed phu quoc wild baby squid", "muc sim"]),
    ("Sò mía hấp lá chanh", "Món Hải sản", "Miền Trung", ["steamed sugarcane clam with lime leaves", "so mia hap"]),
    ("Cá đuối nướng mỡ hành", "Món Hải sản", "Đà Nẵng", ["grilled stingray with scallion oil", "ca duoi nuong"]),
    ("Cá chim trắng nướng muối ớt", "Món Hải sản", "Toàn quốc", ["grilled white pomfret with chili salt", "ca chim nuong"]),
    ("Cá bò da nướng giấy bạc", "Món Hải sản", "Miền Trung", ["foil baked leatherjacket fish", "ca bo da nuong"]),
    ("Bào ngư nướng sốt dầu hào", "Món Hải sản", "Toàn quốc", ["grilled abalone in oyster glaze", "bao ngu nuong"]),
    ("Súp bào ngư vi cá", "Món Hải sản", "Toàn quốc", ["abalone and shark fin soup", "sup bao ngu"]),
    ("Cá chạch lấu nướng muối ớt", "Món Hải sản", "Miền Tây", ["grilled giant spiny eel with chili salt", "ca chach lau"]),
    ("Cá thát lát rút xương chiên giòn", "Món Hải sản", "Hậu Giang", ["crispy boneless featherback fish", "ca that lat rut xuong"]),
    ("Mắm cá linh kho tộ", "Món Hải sản", "An Giang", ["braised linh fish paste in earthenware pot", "mam ca linh"]),

    # =========================================================================
    # 9. HỌ MÓN LẨU & CANH ĐẶC TRƯNG - 45 MÓN
    # =========================================================================
    ("Lẩu thái hải sản", "Món Lẩu & Canh", "Toàn quốc", ["thai seafood hotpot", "spicy tom yum hotpot", "lau thai"]),
    ("Lẩu riêu cua bắp bò sườn sụn", "Món Lẩu & Canh", "Hà Nội", ["hanoi field crab paste hotpot with beef shank", "lau rieu cua bap bo", "crab paste hotpot"]),
    ("Lẩu gà lá é Đà Lạt", "Món Lẩu & Canh", "Đà Lạt", ["da lat chicken hotpot with lemon basil", "lau ga la e", "chicken and basil hotpot"]),
    ("Lẩu bò Ba Toa Đà Lạt", "Món Lẩu & Canh", "Đà Lạt", ["da lat ba toa beef hotpot", "lau bo ba toa"]),
    ("Lẩu mắm miền Tây", "Món Lẩu & Canh", "Miền Tây", ["fermented fish hotpot with water lily and herbs", "lau mam", "mekong fermented broth hotpot"]),
    ("Lẩu cá kèo lá giang", "Món Lẩu & Canh", "Miền Tây", ["goby fish hotpot with sour aganonerion leaves", "lau ca keo"]),
    ("Lẩu cá bớp măng chua", "Món Lẩu & Canh", "Miền Trung", ["cobia hotpot with sour bamboo shoots", "lau ca bop"]),
    ("Lẩu cá tầm Sa Pa", "Món Lẩu & Canh", "Tây Bắc", ["sapa sturgeon fish hotpot", "lau ca tam sa pa"]),
    ("Lẩu cá hồi Sa Pa", "Món Lẩu & Canh", "Tây Bắc", ["sapa salmon sour hotpot", "lau ca hoi sa pa"]),
    ("Lẩu cá linh bông điên điển", "Món Lẩu & Canh", "Miền Tây", ["siamese mud carp hotpot with sesbania sesban flowers", "lau ca linh bong dien dien"]),
    ("Lẩu vịt om sấu", "Món Lẩu & Canh", "Hà Nội", ["duck and dracontomelon hotpot", "lau vit om sau"]),
    ("Lẩu vịt nấu chao", "Món Lẩu & Canh", "Cần Thơ", ["braised duck hotpot with fermented bean curd", "lau vit nau chao"]),
    ("Lẩu cua đồng miền Bắc", "Món Lẩu & Canh", "Miền Bắc", ["freshwater crab hotpot", "lau cua dong"]),
    ("Lẩu cua Cà Mau", "Món Lẩu & Canh", "Cà Mau", ["ca mau fresh sea crab hotpot", "lau cua ca mau"]),
    ("Lẩu dê khô", "Món Lẩu & Canh", "Ninh Bình", ["dry goat hotpot with herbs", "lau de"]),
    ("Lẩu ếch măng cay", "Món Lẩu & Canh", "Hà Nội", ["spicy frog hotpot with bamboo shoots", "lau ech mang cay"]),
    ("Lẩu nấm thiên nhiên", "Món Lẩu & Canh", "Toàn quốc", ["assorted natural wild mushroom hotpot", "lau nam"]),
    ("Lẩu hải sản chua cay", "Món Lẩu & Canh", "Toàn quốc", ["hot and sour seafood hotpot", "lau hai san"]),
    ("Lẩu gà nấm đông cô", "Món Lẩu & Canh", "Toàn quốc", ["chicken and shiitake mushroom hotpot", "lau ga nam"]),
    ("Lẩu cháo chim câu", "Món Lẩu & Canh", "Miền Bắc", ["pigeon congee hotpot", "lau chao chim"]),
    ("Lẩu trâu nhúng mẻ", "Món Lẩu & Canh", "Miền Bắc", ["buffalo meat dipped in fermented rice broth hotpot", "lau trau nhung me"]),
    ("Bò nhúng dấm", "Món Lẩu & Canh", "Toàn quốc", ["beef slices dipped in simmering vinegar broth", "bo nhung dam"]),
    ("Canh chua cá lóc miền Tây", "Món Lẩu & Canh", "Miền Tây", ["mekong sour snakehead fish soup", "canh chua ca loc", "sour fish soup with tamarind and herbs"]),
    ("Canh chua cá bông lau", "Món Lẩu & Canh", "Miền Nam", ["catfish sour tamarind soup", "canh chua ca bong lau"]),
    ("Canh cua mồng tơi mướp", "Món Lẩu & Canh", "Miền Bắc", ["crab soup with malabar spinach and luffa", "canh cua mong toi"]),
    ("Canh hến nấu khế", "Món Lẩu & Canh", "Huế", ["baby clam soup with starfruit", "canh hen nau khe"]),
    ("Canh bóng thả thập cẩm", "Món Lẩu & Canh", "Hà Nội", ["traditional hanoi pig skin and dried shrimp banquet soup", "canh bong"]),
    ("Canh khổ qua nhồi thịt", "Món Lẩu & Canh", "Miền Nam", ["stuffed bitter melon soup with minced pork", "canh kho qua"]),
    ("Canh sườn nấu sấu", "Món Lẩu & Canh", "Miền Bắc", ["pork rib soup with dracontomelon", "canh suon sau"]),
    ("Canh ngao nấu chua", "Món Lẩu & Canh", "Miền Bắc", ["sour clam soup with tomatoes and dill", "canh ngao nau chua"]),
    ("Canh rong biển thịt bằm", "Món Lẩu & Canh", "Toàn quốc", ["seaweed soup with minced meat", "canh rong bien"]),
    ("Canh chua cá hồi", "Món Lẩu & Canh", "Toàn quốc", ["sour salmon head soup", "canh chua ca hoi"]),
    ("Canh măng sườn heo", "Món Lẩu & Canh", "Toàn quốc", ["pork rib soup with fresh bamboo shoots", "canh mang suon"]),
    ("Lẩu bò sa tế cay", "Món Lẩu & Canh", "Toàn quốc", ["spicy satay beef hotpot", "lau bo sa te"]),
    ("Lẩu đuôi bò hầm thuốc bắc", "Món Lẩu & Canh", "Toàn quốc", ["oxtail herbal hotpot", "lau duoi bo"]),
    ("Lẩu ghẹ kim chi", "Món Lẩu & Canh", "Toàn quốc", ["blue crab kimchi hotpot", "lau ghe"]),
    ("Lẩu gà ớt hiểm", "Món Lẩu & Canh", "Miền Nam", ["chicken hotpot with bird's eye chili", "lau ga ot hiem"]),
    ("Lẩu tôm càng sen", "Món Lẩu & Canh", "Đồng Tháp", ["giant freshwater prawn lotus hotpot", "lau tom cang"]),
    ("Lẩu đầu cá hồi nấu ngót", "Món Lẩu & Canh", "Toàn quốc", ["salmon head clear soup with celery and tomatoes", "lau ca hoi"]),
    ("Canh gà nấu lá giang", "Món Lẩu & Canh", "Miền Trung", ["sour leaf chicken soup", "canh ga la giang"]),
    ("Canh rau tập tàng nấu tôm", "Món Lẩu & Canh", "Huế", ["wild mixed garden green soup with shrimp", "canh tap tang"]),
    ("Lẩu cá bớp nấu ngót", "Món Lẩu & Canh", "Miền Trung", ["clear cobia broth hotpot", "lau ca bop"]),
    ("Lẩu lươn chua cay", "Món Lẩu & Canh", "Miền Tây", ["sour and spicy swamp eel hotpot", "lau luon"]),
    ("Lẩu cù lao miền Tây", "Món Lẩu & Canh", "Miền Tây", ["traditional mekong island chimney hotpot", "lau cu lao"]),
    ("Canh bí đỏ hầm xương", "Món Lẩu & Canh", "Toàn quốc", ["pumpkin pork bone stew", "canh bi do"]),

    # =========================================================================
    # 10. HỌ RAU, XÀO, NỘM CHAY & MÓN CHAY THANH TỊNH - 40 MÓN
    # =========================================================================
    ("Rau muống xào tỏi", "Món Rau & Xào & Chay", "Toàn quốc", ["morning glory stir-fried with garlic", "water spinach with garlic", "rau muong xao toi"]),
    ("Rau bí xào tỏi", "Món Rau & Xào & Chay", "Miền Bắc", ["pumpkin tendrils sautéed with fragrant garlic", "rau bi xao toi"]),
    ("Ngọn su su xào tỏi Tam Đảo", "Món Rau & Xào & Chay", "Vĩnh Phúc", ["chayote shoots stir-fried with garlic", "su su xao toi"]),
    ("Đậu bắp luộc chấm chao", "Món Rau & Xào & Chay", "Miền Nam", ["boiled okra with fermented bean curd dip", "dau bap luoc"]),
    ("Rau rừng Gia Lai xào tỏi", "Món Rau & Xào & Chay", "Tây Nguyên", ["stir fried wild forest greens with garlic", "rau rung xao toi"]),
    ("Cải ngồng xào nấm đông cô", "Món Rau & Xào & Chay", "Toàn quốc", ["baby gai lan stir-fried with shiitake mushrooms", "cai ngong xao nam"]),
    ("Đậu hũ lướt ván", "Món Rau & Xào & Chay", "Miền Bắc", ["crispy silky fried tofu", "dau hu luot van"]),
    ("Đậu hũ sốt cà chua", "Món Rau & Xào & Chay", "Toàn quốc", ["braised tofu in rich tomato gravy", "dau sot ca chua"]),
    ("Đậu hũ chiên sả ớt", "Món Rau & Xào & Chay", "Toàn quốc", ["crispy golden tofu with crispy lemongrass and chili", "dau chien sa ot"]),
    ("Đậu hũ non sốt nấm thịt bằm", "Món Rau & Xào & Chay", "Toàn quốc", ["silken tofu with mushroom and minced pork", "dau hu sot nam"]),
    ("Nấm đùi gà kho tiêu", "Món Rau & Xào & Chay", "Toàn quốc", ["braised king oyster mushroom with black pepper", "nam kho tieu"]),
    ("Cơm chay Huế", "Món Rau & Xào & Chay", "Huế", ["hue royal vegetarian platter", "com chay hue", "buddhist vegan meal"]),
    ("Bún bò Huế chay", "Món Rau & Xào & Chay", "Huế", ["vegetarian hue spicy noodle soup", "bun bo hue chay"]),
    ("Phở chay", "Món Rau & Xào & Chay", "Toàn quốc", ["vegan pho with tofu and assorted mushrooms", "pho chay"]),
    ("Bún riêu chay", "Món Rau & Xào & Chay", "Toàn quốc", ["vegan crab paste noodle soup with tofu", "bun rieu chay"]),
    ("Hủ tiếu chay", "Món Rau & Xào & Chay", "Miền Nam", ["vegan rice noodle soup", "hu tieu chay"]),
    ("Mì xào giòn chay", "Món Rau & Xào & Chay", "Toàn quốc", ["crispy noodles with stir fried vegetables and mushrooms", "mi xao chay"]),
    ("Lẩu nấm chay thanh đạm", "Món Rau & Xào & Chay", "Toàn quốc", ["herbal vegan mushroom hotpot", "lau nam chay"]),
    ("Chả giò nấm chay", "Món Rau & Xào & Chay", "Toàn quốc", ["vegan crispy mushroom spring rolls", "nem chay", "cha gio chay"]),
    ("Mít non kho chay", "Món Rau & Xào & Chay", "Miền Trung", ["caramelized braised young jackfruit", "mit non kho"]),
    ("Rau luộc chấm kho quẹt", "Món Rau & Xào & Chay", "Miền Nam", ["boiled garden vegetables with caramelized dip", "rau luoc kho quet"]),
    ("Bông điên điển xào tép", "Món Rau & Xào & Chay", "Miền Tây", ["sesbania flower sautéed with river shrimp", "bong dien dien xao"]),
    ("Bông bí xào tỏi", "Món Rau & Xào & Chay", "Miền Bắc", ["pumpkin blossoms stir fried with garlic", "bong bi xao toi"]),
    ("Mướp đắng xào trứng", "Món Rau & Xào & Chay", "Toàn quốc", ["scrambled eggs with sliced bitter melon", "muop dang xao trung"]),
    ("Cà pháo muối chua", "Món Rau & Xào & Chay", "Miền Bắc", ["pickled white round eggplants", "ca phao"]),
    ("Dưa cải muối chua", "Món Rau & Xào & Chay", "Toàn quốc", ["pickled mustard greens", "dua cai chua"]),
    ("Kim chi củ sen", "Món Rau & Xào & Chay", "Toàn quốc", ["spicy pickled lotus root", "kim chi cu sen"]),
    ("Ngó sen xào tôm", "Món Rau & Xào & Chay", "Toàn quốc", ["stir-fried lotus rhizome with shrimp", "ngo sen xao tom"]),
    ("Măng tây xào thịt bò", "Món Rau & Xào & Chay", "Toàn quốc", ["stir-fried asparagus with beef slices", "mang tay xao bo"]),
    ("Nấm rơm kho tộ", "Món Rau & Xào & Chay", "Toàn quốc", ["claypot braised straw mushrooms", "nam rom kho to"]),
    ("Sườn non chay chua ngọt", "Món Rau & Xào & Chay", "Toàn quốc", ["sweet and sour vegan gluten ribs", "suon chay chua ngot"]),
    ("Gỏi cuốn chay", "Món Rau & Xào & Chay", "Toàn quốc", ["vegan fresh salad rolls with tofu", "goi cuon chay"]),
    ("Bánh mì chay", "Món Rau & Xào & Chay", "Toàn quốc", ["vegetarian banh mi with tofu pate and seitan", "banh mi chay"]),
    ("Bánh xèo nấm chay", "Món Rau & Xào & Chay", "Toàn quốc", ["vegan crispy pancake with wild mushrooms", "banh xeo chay"]),
    ("Cơm chiên trái thơm", "Món Rau & Xào & Chay", "Toàn quốc", ["pineapple fried rice with cashews and peas", "com chien trai thom"]),
    ("Cà ri chay nước cốt dừa", "Món Rau & Xào & Chay", "Miền Nam", ["vegan vegetable curry with coconut cream", "ca ri chay"]),
    ("Nộm hoa chuối chay", "Món Rau & Xào & Chay", "Toàn quốc", ["vegan banana blossom salad with crushed peanuts", "nom chuoi chay"]),
    ("Chả lụa chay", "Món Rau & Xào & Chay", "Toàn quốc", ["steamed vegan ham made from tofu skin", "cha lua chay"]),
    ("Canh chua chay", "Món Rau & Xào & Chay", "Miền Nam", ["vegan tamarind sour soup with pineapple and okra", "canh chua chay"]),
    ("Khoai tây chiên lắc phô mai", "Món Rau & Xào & Chay", "Toàn quốc", ["french fries with cheese powder", "khoai tay chien"]),

    # =========================================================================
    # 11. HỌ CHÈ, BÁNH NGỌT & TRÁNG MIỆNG - 50 MÓN
    # =========================================================================
    ("Chè bưởi An Giang", "Món Chè & Tráng miệng", "An Giang", ["grapefruit pith sweet soup with mung beans", "che buoi", "pomelo sweet soup"]),
    ("Chè hạt sen long nhãn", "Món Chè & Tráng miệng", "Huế", ["lotus seeds wrapped in longan sweet soup", "che hat sen long nhan", "hue lotus seed dessert"]),
    ("Chè bột lọc bọc heo quay", "Món Chè & Tráng miệng", "Huế", ["tapioca balls with roast pork in ginger syrup", "che bot loc heo quay", "roast pork sweet soup"]),
    ("Chè bắp Cồn Hến", "Món Chè & Tráng miệng", "Huế", ["sweet corn dessert with coconut cream", "che bap", "sweet corn soup"]),
    ("Chè khoai tía Huế", "Món Chè & Tráng miệng", "Huế", ["purple sweet potato dessert", "che khoai tia"]),
    ("Chè sương sa hạt lựu", "Món Chè & Tráng miệng", "Miền Nam", ["rainbow sweet soup with water chestnuts and agar jelly", "che suong sa hat luu"]),
    ("Chè ba màu", "Món Chè & Tráng miệng", "Miền Nam", ["three-color sweet soup with red beans and jelly", "che ba mau", "rainbow dessert"]),
    ("Chè đậu đỏ bánh lọt", "Món Chè & Tráng miệng", "Miền Nam", ["red bean sweet soup with pandan rice droplets", "che dau do"]),
    ("Chè khúc bạch", "Món Chè & Tráng miệng", "Hà Nội", ["panna cotta almond jelly sweet dessert", "che khuc bach"]),
    ("Chè thái sầu riêng", "Món Chè & Tráng miệng", "Đà Nẵng", ["durian sweet soup with assorted tropical fruits", "che thai sau rieng", "che thai da nang"]),
    ("Chè chuối nếp nướng", "Món Chè & Tráng miệng", "Miền Tây", ["grilled banana sticky rice in coconut cream", "che chuoi nep nuong"]),
    ("Chè thưng", "Món Chè & Tráng miệng", "Miền Nam", ["sweet coconut soup with sweet potato and black-eyed peas", "che thung"]),
    ("Chè trôi nước ngũ sắc", "Món Chè & Tráng miệng", "Toàn quốc", ["glutinous rice balls in warm sweet ginger syrup", "che troi nuoc"]),
    ("Chè bà ba", "Món Chè & Tráng miệng", "Miền Tây", ["southern coconut milk dessert with tapioca and tubers", "che ba ba"]),
    ("Chè thập cẩm", "Món Chè & Tráng miệng", "Toàn quốc", ["mixed beans and jelly sweet soup", "che thap cam"]),
    ("Chè mè đen Huế", "Món Chè & Tráng miệng", "Huế", ["black sesame sweet soup", "che me den", "chi ma phu"]),
    ("Chè đậu xanh đánh", "Món Chè & Tráng miệng", "Huế", ["whipped mung bean puree with crushed ice", "che dau xanh danh"]),
    ("Chè sâm bổ lượng", "Món Chè & Tráng miệng", "TP.HCM", ["cooling sweet herbal soup with seaweed and barley", "che sam bo luong", "ching po leung"]),
    ("Tàu hũ nước đường gừng", "Món Chè & Tráng miệng", "Toàn quốc", ["silken tofu in warm ginger sugar syrup", "tau hu nuoc duong", "douhua"]),
    ("Tàu hũ đá nước cốt dừa", "Món Chè & Tráng miệng", "Miền Nam", ["chilled silken tofu with rich coconut milk", "tau hu da"]),
    ("Sữa chua dẻo", "Món Chè & Tráng miệng", "Hà Nội", ["cubed frozen yogurt with cocoa powder", "sua chua deo"]),
    ("Sữa chua trân châu Hạ Long", "Món Chè & Tráng miệng", "Quảng Ninh", ["ha long yogurt with warm tapioca pearls in coconut milk", "sua chua tran chau ha long"]),
    ("Kem bơ Đà Lạt", "Món Chè & Tráng miệng", "Đà Lạt", ["da lat avocado ice cream smoothie with shaved coconut", "kem bo da lat"]),
    ("Kem dừa Côn Đảo", "Món Chè & Tráng miệng", "Bà Rịa - Vũng Tàu", ["con dao fresh coconut ice cream served in coconut shell", "kem dua"]),
    ("Kem Tràng Tiền Hà Nội", "Món Chè & Tráng miệng", "Hà Nội", ["trang tien traditional hanoi ice cream pops", "kem trang tien"]),
    ("Bánh tiêu đường", "Món Chè & Tráng miệng", "Toàn quốc", ["sweet hollow fried pastry with sesame", "banh tieu"]),
    ("Bánh bò thốt nốt Châu Đốc", "Món Chè & Tráng miệng", "An Giang", ["palm sugar honeycomb sponge cake", "banh bo thot not"]),
    ("Bánh bò hấp nước cốt dừa", "Món Chè & Tráng miệng", "Miền Nam", ["steamed sponge cake with rich coconut drizzle", "banh bo hap"]),
    ("Bánh bò nướng", "Món Chè & Tráng miệng", "Miền Nam", ["baked honeycomb cake with pandan fragrance", "banh bo nuong"]),
    ("Bánh da lợn lá dứa", "Món Chè & Tráng miệng", "Miền Nam", ["steamed layered pandan and mung bean cake", "banh da lon", "pig skin layer cake"]),
    ("Bánh chuối nướng bơ sữa", "Món Chè & Tráng miệng", "Miền Nam", ["baked banana bread with condensed milk", "banh chuoi nuong"]),
    ("Bánh chuối hấp nước cốt dừa", "Món Chè & Tráng miệng", "Miền Nam", ["steamed banana slices with tapioca pearls", "banh chuoi hap"]),
    ("Bánh khoai mì nướng", "Món Chè & Tráng miệng", "Miền Nam", ["baked cassava cake with coconut milk", "banh khoai mi nuong"]),
    ("Bánh pía Sóc Trăng", "Món Chè & Tráng miệng", "Sóc Trăng", ["soc trang flaky pastry with durian and salted egg", "banh pia", "durian pia cake"]),
    ("Bánh đậu xanh Hải Dương", "Món Chè & Tráng miệng", "Hải Dương", ["hai duong sweet melt-in-mouth mung bean cake", "banh dau xanh"]),
    ("Bánh cáy Thái Bình", "Món Chè & Tráng miệng", "Thái Bình", ["thai binh spicy sweet crispy rice cracker", "banh cay"]),
    ("Bánh gai Nam Định", "Món Chè & Tráng miệng", "Nam Định", ["black thorn leaf cake with sweetened pork and coconut", "banh gai"]),
    ("Bánh phu thê Đình Bảng", "Món Chè & Tráng miệng", "Bắc Ninh", ["husband and wife matrimonial sticky cake", "banh xu xe", "banh phu the"]),
    ("Bánh cốm Hàng Than", "Món Chè & Tráng miệng", "Hà Nội", ["hang than sweet green rice cake with mung bean paste", "banh com"]),
    ("Kẹo cu đơ Hà Tĩnh", "Món Chè & Tráng miệng", "Hà Tĩnh", ["ha tinh peanut and molasses ginger wafer brittle", "keo cu do"]),
    ("Mè xửng Huế", "Món Chè & Tráng miệng", "Huế", ["hue chewy sesame peanut candy", "me xung hue"]),
    ("Kẹo dừa Bến Tre", "Món Chè & Tráng miệng", "Bến Tre", ["ben tre rich creamy coconut candy", "keo dua ben tre"]),
    ("Kẹo gương Quảng Ngãi", "Món Chè & Tráng miệng", "Quảng Ngãi", ["crispy glass peanut candy", "keo guong"]),
    ("Bánh tai heo ngọt", "Món Chè & Tráng miệng", "Toàn quốc", ["spiral ear crispy sweet biscuits", "banh tai heo"]),
    ("Bánh ít lá gai", "Món Chè & Tráng miệng", "Bình Định", ["black sticky rice dumpling wrapped in banana leaves", "banh it la gai"]),
    ("Chuối nếp nướng Cần Thơ", "Món Chè & Tráng miệng", "Cần Thơ", ["grilled sticky rice wrapped banana", "chuoi nep nuong"]),
    ("Thạch găng Hải Phòng", "Món Chè & Tráng miệng", "Hải Phòng", ["green gang leaf jelly with jasmine sweet syrup", "thach gang"]),
    ("Chè dừa dầm Hải Phòng", "Món Chè & Tráng miệng", "Hải Phòng", ["coconut jelly and young copra in sweet coconut milk", "dua dam hai phong"]),
    ("Bánh cam lúc lắc", "Món Chè & Tráng miệng", "Miền Nam", ["deep fried hollow sesame ball with mung bean ball", "banh cam"]),
    ("Bánh ống lá dứa Trà Vinh", "Món Chè & Tráng miệng", "Trà Vinh", ["steamed cylindrical pandan rice cake with coconut", "banh ong la dua"]),

    # =========================================================================
    # 12. HỌ ĐỒ UỐNG, CÀ PHÊ & GIẢI KHÁT - 40 MÓN
    # =========================================================================
    ("Cà phê sữa đá", "Đồ uống & Cà phê", "Toàn quốc", ["vietnamese iced coffee with condensed milk", "ca phe sua da", "vietnamese iced milk coffee"]),
    ("Cà phê đen đá", "Đồ uống & Cà phê", "Toàn quốc", ["vietnamese black iced coffee", "ca phe den da", "iced black drip coffee"]),
    ("Cà phê trứng Hà Nội", "Đồ uống & Cà phê", "Hà Nội", ["vietnamese egg coffee", "ca phe trung", "creamy whipped egg yolk coffee"]),
    ("Cà phê muối Huế", "Đồ uống & Cà phê", "Huế", ["hue salted foam coffee", "ca phe muoi", "salted cream coffee", "hue salt coffee"]),
    ("Bạc xỉu Sài Gòn", "Đồ uống & Cà phê", "TP.HCM", ["white iced coffee with extra milk", "bac xiu", "sweet condensed milk with coffee splash"]),
    ("Cà phê cốt dừa", "Đồ uống & Cà phê", "Hà Nội", ["coconut coffee smoothie", "ca phe cot dua", "frozen coconut milk coffee"]),
    ("Trà sen Tây Hồ", "Đồ uống & Cà phê", "Hà Nội", ["west lake lotus scented green tea", "tra sen tay ho", "lotus tea"]),
    ("Trà lài", "Đồ uống & Cà phê", "Toàn quốc", ["jasmine scented tea", "tra lai"]),
    ("Trà đào cam sả", "Đồ uống & Cà phê", "Toàn quốc", ["peach tea with fresh orange and lemongrass", "tra dao cam sa"]),
    ("Trà vải kim tuyền", "Đồ uống & Cà phê", "Toàn quốc", ["lychee iced fruit tea", "tra vai"]),
    ("Trà măng cụt", "Đồ uống & Cà phê", "Bình Dương", ["mangosteen iced tea", "tra mang cut"]),
    ("Trà mãng cầu xiêm", "Đồ uống & Cà phê", "Miền Nam", ["soursop fresh fruit tea", "tra mang cau"]),
    ("Nước mía sầu riêng", "Đồ uống & Cà phê", "Miền Nam", ["fresh sugarcane juice with durian aroma", "nuoc mia sau rieng"]),
    ("Nước mía tắc", "Đồ uống & Cà phê", "Toàn quốc", ["fresh pressed sugarcane juice with kumquat", "nuoc mia"]),
    ("Nước dừa xiêm tươi", "Đồ uống & Cà phê", "Bến Tre", ["fresh young xiem coconut water", "nuoc dua xiem"]),
    ("Dừa sáp Cầu Kè", "Đồ uống & Cà phê", "Trà Vinh", ["macapuno coconut smoothie with condensed milk", "dua sap tra vinh"]),
    ("Nước sâm bí đao la hán quả", "Đồ uống & Cà phê", "Miền Nam", ["winter melon herbal cooling tea", "nuoc sam bi dao"]),
    ("Nước rau má đậu xanh", "Đồ uống & Cà phê", "Miền Nam", ["pennywort juice blended with sweet mung beans", "rau ma dau xanh"]),
    ("Sinh tố bơ sáp Đắk Lắk", "Đồ uống & Cà phê", "Đắk Lắk", ["rich creamy avocado smoothie", "sinh to bo"]),
    ("Sinh tố xoài cát Hòa Lộc", "Đồ uống & Cà phê", "Miền Tây", ["hoa loc mango smoothie", "sinh to xoai"]),
    ("Sinh tố mãng cầu", "Đồ uống & Cà phê", "Toàn quốc", ["soursop smoothie", "sinh to mang cau"]),
    ("Nước chanh leo tuyết", "Đồ uống & Cà phê", "Toàn quốc", ["passion fruit iced drink", "nuoc chanh day"]),
    ("Trà tắc mật ong", "Đồ uống & Cà phê", "Toàn quốc", ["kumquat honey iced tea", "tra tac"]),
    ("Trà chanh phố cổ Hà Nội", "Đồ uống & Cà phê", "Hà Nội", ["hanoi old quarter iced lime tea", "tra chanh pho co"]),
    ("Bia hơi Hà Nội", "Đồ uống & Cà phê", "Hà Nội", ["hanoi draft beer", "bia hoi", "fresh street draft beer"]),
    ("Bia Sài Gòn Special", "Đồ uống & Cà phê", "TP.HCM", ["saigon special beer", "bia sai gon"]),
    ("Bia Huda Huế", "Đồ uống & Cà phê", "Huế", ["huda central beer", "bia huda"]),
    ("Rượu cần Tây Nguyên", "Đồ uống & Cà phê", "Tây Nguyên", ["highland fermented rice wine drunk through bamboo straw", "ruou can"]),
    ("Rượu sim Phú Quốc", "Đồ uống & Cà phê", "Kiên Giang", ["phu quoc rose myrtle berry wine", "ruou sim"]),
    ("Rượu ngô Bản Phố", "Đồ uống & Cà phê", "Lào Cai", ["ban pho highland sweet corn wine", "ruou ngo"]),
    ("Rượu nếp cái hoa vàng", "Đồ uống & Cà phê", "Miền Bắc", ["glutinous golden blossom rice wine", "ruou nep cai hoa vang"]),
    ("Sữa đậu nành nóng Đà Lạt", "Đồ uống & Cà phê", "Đà Lạt", ["warm fresh soy milk with pandan leaves", "sua dau nanh da lat"]),
    ("Sữa ngô non", "Đồ uống & Cà phê", "Toàn quốc", ["sweet baby corn milk", "sua ngo"]),
    ("Trà atiso Đà Lạt", "Đồ uống & Cà phê", "Đà Lạt", ["da lat artichoke herbal tea", "tra atiso"]),
    ("Nước sấu ngâm đường gừng", "Đồ uống & Cà phê", "Hà Nội", ["pickled dracontomelon juice with ginger", "nuoc sau"]),
    ("Nước mơ ngâm đường", "Đồ uống & Cà phê", "Hà Nội", ["pickled apricot juice with ice", "nuoc mo"]),
    ("Trà hoa cúc mật ong", "Đồ uống & Cà phê", "Miền Bắc", ["chrysanthemum tea with wild honey", "tra hoa cuc"]),
    ("Rau má dừa tươi", "Đồ uống & Cà phê", "Miền Nam", ["pennywort juice with sweet coconut water", "rau ma nuoc dua"]),
    ("Trà sữa trân châu đường đen", "Đồ uống & Cà phê", "Toàn quốc", ["brown sugar boba milk tea", "tra sua tran chau"]),
    ("Nước ép dưa hấu", "Đồ uống & Cà phê", "Toàn quốc", ["fresh watermelon juice", "nuoc ep dua hau"])
]

def generate_aliases(canonical_name, extra_variants):
    """Tự động sinh tập biến thể có dấu, không dấu và tiếng Anh"""
    aliases = set()
    
    # 1. Tên gốc có dấu (viết thường)
    c_lower = canonical_name.lower().strip()
    aliases.add(c_lower)
    
    # 2. Tên không dấu
    no_acc = remove_vietnamese_accents(c_lower)
    aliases.add(no_acc)
    
    # 3. Các biến thể bổ sung
    for var in extra_variants:
        v_lower = var.lower().strip()
        aliases.add(v_lower)
        aliases.add(remove_vietnamese_accents(v_lower))
        
    return sorted(list(aliases))

def build_culinary_gazetteer():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, "..", ".."))
    out_dir = os.path.join(project_root, "data", "processed")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "culinary_gazetteer.json")

    gazetteer = []
    dish_id = 1

    print("=" * 70)
    print("XÂY DỰNG BỘ TỪ ĐIỂN ẨM THỰC VIỆT NAM TOÀN DIỆN (500+ MÓN)")
    print("=" * 70)

    categories_count = {}
    regions_count = {}

    for name, cat, region, variants in ALL_VIETNAMESE_DISHES:
        aliases = generate_aliases(name, variants)
        item = {
            "dish_id": f"dish_{dish_id:04d}",
            "canonical_name": name,
            "category": cat,
            "region_origin": region,
            "aliases": aliases,
            "alias_count": len(aliases)
        }
        gazetteer.append(item)
        dish_id += 1
        categories_count[cat] = categories_count.get(cat, 0) + 1
        regions_count[region] = regions_count.get(region, 0) + 1

    # Lưu ra JSON
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(gazetteer, f, ensure_ascii=False, indent=2)

    total_aliases = sum(x["alias_count"] for x in gazetteer)

    print(f"\n-> XUẤT THÀNH CÔNG: {out_file}")
    print(f"• Tổng số món ăn chuẩn hóa: {len(gazetteer):,} món ăn đặc sản Việt Nam")
    print(f"• Tổng số từ khóa & biến thể (song ngữ Anh-Việt + không dấu): {total_aliases:,} patterns")
    print(f"• Trung bình: {total_aliases / len(gazetteer):.1f} biến thể tra cứu / mỗi món ăn")
    
    print("\nPHÂN BỔ THEO 12 NHÓM ẨM THỰC:")
    for cat, count in sorted(categories_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  * {cat:<32}: {count:>3} món")

    print("\nPHÂN BỔ THEO VÙNG MIỀN XUẤT XỨ TIÊU BIỂU:")
    for reg, count in sorted(regions_count.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  * {reg:<25}: {count:>3} món")

    print("=" * 70)
    return out_file

if __name__ == "__main__":
    build_culinary_gazetteer()
