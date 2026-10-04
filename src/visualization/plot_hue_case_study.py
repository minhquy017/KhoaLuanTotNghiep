# -*- coding: utf-8 -*-
"""
TRỰC QUAN HÓA DỮ LIỆU THỰC NGHIỆM TRỌNG ĐIỂM: THỪA THIÊN HUẾ (CASE STUDY)
Khóa luận Tốt nghiệp ngành Khoa học Dữ liệu và Trí tuệ Nhân tạo (DS&AI K3 - HUET)
Đề tài: Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh dựa trên Đồ thị Tri thức Không gian và LLM
-----------------------------------------------------------------------------------------------------
- Nguồn dữ liệu: data/processed/tourism_vietnam.db (Bảng `places` và `reviews` với `is_hue = 1`)
- Phân tích 3 trụ cột khoa học:
  1. Cơ cấu loại hình dịch vụ du lịch (479 Nhà hàng, 104 Khách sạn, 29 Di tích/Danh thắng)
  2. Phân bố điểm số đánh giá thực tế từ 28,757 bài review (1.0 đến 5.0 sao)
  3. Cơ cấu phân khúc du khách (Trip Types: Cặp đôi, Bạn bè, Gia đình, Đơn hành, Công tác)
- Xuất bản phẩm: docs/figures/hue_case_study_analysis.png (300 DPI Academic Quality)
"""

import os
import sys
import re
import sqlite3
import pandas as pd
import numpy as np

# Bắt buộc UTF-8 stdout
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns


# ==============================================================================
# CẤU HÌNH THƯ MỤC VÀ STYLE CHUẨN HỌC THUẬT
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "tourism_vietnam.db")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "docs", "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Typography tiếng Việt
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Segoe UI Symbol', 'Arial', 'Tahoma', 'DejaVu Sans']
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#EAEAEA'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7


def load_hue_data():
    """Truy vấn dữ liệu riêng cho Thừa Thiên Huế từ SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Cơ cấu địa điểm
    cur.execute("SELECT category, count(*) FROM places WHERE is_hue = 1 GROUP BY category")
    places_cat = dict(cur.fetchall())

    # 2. Phân bố sao đánh giá
    cur.execute("""
        SELECT CAST(r.reviews_rating AS INTEGER) as stars, count(*)
        FROM reviews r
        JOIN places p ON r.place_url = p.url
        WHERE p.is_hue = 1 AND r.reviews_rating IS NOT NULL
        GROUP BY stars
        ORDER BY stars
    """)
    ratings_raw = dict(cur.fetchall())

    # 3. Phân loại loại hình chuyến đi (Trip types)
    cur.execute("""
        SELECT r.trip_type, count(*)
        FROM reviews r
        JOIN places p ON r.place_url = p.url
        WHERE p.is_hue = 1 AND r.trip_type IS NOT NULL AND length(trim(r.trip_type)) > 0
        GROUP BY r.trip_type
    """)
    raw_trips = cur.fetchall()
    conn.close()

    # Chuẩn hóa Trip types
    trip_map = {
        'couple': 0,
        'friends': 0,
        'family': 0,
        'solo': 0,
        'business': 0
    }
    for t_str, cnt in raw_trips:
        s = t_str.lower()
        if 'couple' in s:
            trip_map['couple'] += cnt
        elif 'friend' in s:
            trip_map['friends'] += cnt
        elif 'family' in s:
            trip_map['family'] += cnt
        elif 'solo' in s:
            trip_map['solo'] += cnt
        elif 'business' in s:
            trip_map['business'] += cnt

    return places_cat, ratings_raw, trip_map


def plot_hue_case_study():
    print("=" * 80)
    print("🏛️ TRỰC QUAN HÓA THÁM NGHIỆM DỮ LIỆU ĐỊA BÀN THỪA THIÊN HUẾ (CASE STUDY)")
    print("=" * 80)

    places_cat, ratings_raw, trip_map = load_hue_data()

    total_places = sum(places_cat.values())
    total_reviews = sum(ratings_raw.values())
    total_trips = sum(trip_map.values())

    print(f"• Tổng số địa điểm du lịch tại Huế: {total_places:,}")
    print(f"  + Ẩm thực (Restaurant) : {places_cat.get('restaurant', 0):,} ({places_cat.get('restaurant', 0)/total_places*100:.1f}%)")
    print(f"  + Lưu trú (Hotel)      : {places_cat.get('hotel', 0):,} ({places_cat.get('hotel', 0)/total_places*100:.1f}%)")
    print(f"  + Tham quan (Attraction): {places_cat.get('attraction', 0):,} ({places_cat.get('attraction', 0)/total_places*100:.1f}%)")

    print(f"\n• Tổng số bài review đánh giá tại Huế: {total_reviews:,}")
    for s in [5, 4, 3, 2, 1]:
        cnt = ratings_raw.get(s, 0)
        print(f"  + {s} sao: {cnt:>6,} bài ({cnt/total_reviews*100:>5.1f}%)")

    print(f"\n• Cơ cấu phân khúc du khách (Trip Types - {total_trips:,} lượt phân loại):")
    vn_trip_labels = {
        'couple': 'Cặp đôi (Couples)',
        'friends': 'Bạn bè (Friends)',
        'family': 'Gia đình (Family)',
        'solo': 'Đơn hành (Solo)',
        'business': 'Công tác (Business)'
    }
    for k, v in trip_map.items():
        print(f"  + {vn_trip_labels[k]}: {v:,} ({v/total_trips*100:.1f}%)")

    # --------------------------------------------------------------------------
    # THIẾT KẾ FIGURE 3 PANEL CHUẨN ẤN PHẨM HỌC THUẬT
    # --------------------------------------------------------------------------
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6.5), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')

    # PANEL 1: CƠ CẤU ĐỊA ĐIỂM (DONUT CHART)
    ax1.set_facecolor('#FFFFFF')
    cat_labels = [
        f"Ẩm thực / Quán ăn\n({places_cat.get('restaurant', 0):,} quán)",
        f"Lưu trú / Khách sạn\n({places_cat.get('hotel', 0):,} KS)",
        f"Di tích / Danh lam\n({places_cat.get('attraction', 0):,} điểm)"
    ]
    cat_counts = [
        places_cat.get('restaurant', 0),
        places_cat.get('hotel', 0),
        places_cat.get('attraction', 0)
    ]
    cat_colors = ['#E76F51', '#2A9D8F', '#E9C46A']

    wedges, texts, autotexts = ax1.pie(
        cat_counts,
        labels=cat_labels,
        autopct='%1.1f%%',
        startangle=140,
        colors=cat_colors,
        wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2),
        pctdistance=0.76
    )
    for t in texts:
        t.set_fontsize(10)
        t.set_fontweight('semibold')
        t.set_color('#2B2D42')
    for at in autotexts:
        at.set_fontsize(10.5)
        at.set_fontweight('bold')
        at.set_color('white')

    ax1.text(0, 0, f"HUẾ\n{total_places:,}\nĐịa điểm", ha='center', va='center',
             fontsize=12, fontweight='bold', color='#1D3557')
    ax1.set_title("A. CƠ CẤU CƠ SỞ DU LỊCH TẠI HUẾ\n"
                  f"(Tổng cộng {total_places:,} địa điểm đã chuẩn hóa)",
                  fontsize=11.5, fontweight='bold', color='#1D3557', pad=14)

    # PANEL 2: PHÂN BỐ ĐIỂM ĐÁNH GIÁ (RATING 1-5 SAO)
    ax2.set_facecolor('#FAFAFA')
    stars = [1, 2, 3, 4, 5]
    star_labels = ['1 Sao', '2 Sao', '3 Sao', '4 Sao', '5 Sao']
    counts_stars = [ratings_raw.get(s, 0) for s in stars]
    star_colors = ['#D90429', '#EF233C', '#F4A261', '#2A9D8F', '#1D3557']

    bars_rating = ax2.bar(range(5), counts_stars, color=star_colors, width=0.62, edgecolor='white', linewidth=1.2)
    for bar, c in zip(bars_rating, counts_stars):
        h = bar.get_height()
        pct = (c / total_reviews) * 100
        ax2.text(bar.get_x() + bar.get_width()/2., h + 350, f"{c:,}\n({pct:.1f}%)",
                 ha='center', va='bottom', fontsize=9, fontweight='bold', color='#1D3557')

    ax2.set_xticks(range(5))
    ax2.set_xticklabels(star_labels, fontsize=9.5, fontweight='semibold')
    ax2.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
    ax2.set_ylim(0, max(counts_stars) * 1.18)
    ax2.set_ylabel("Số lượng bài review", fontsize=10.5, fontweight='bold', color='#2B2D42')
    ax2.grid(axis='y', linestyle='--', alpha=0.6)

    # Highlight box: 93.8% hài lòng
    high_satisfaction = ((ratings_raw.get(4, 0) + ratings_raw.get(5, 0)) / total_reviews) * 100
    ax2.text(0.05, 0.92, f"4 & 5 Sao chiếm {high_satisfaction:.1f}%\n(Mức độ hài lòng rất cao)",
             transform=ax2.transAxes, fontsize=10, fontweight='bold', color='#1D3557',
             bbox=dict(boxstyle='round,pad=0.4', facecolor='#E8F8F5', edgecolor='#2A9D8F', alpha=0.9))

    ax2.set_title("B. PHÂN BỐ ĐIỂM ĐÁNH GIÁ CỦA DU KHÁCH\n"
                  f"(Tổng cộng {total_reviews:,} bài đánh giá thực tế)",
                  fontsize=11.5, fontweight='bold', color='#1D3557', pad=14)

    # PANEL 3: PHÂN LOẠI PHÂN KHÚC DU KHÁCH (TRIP TYPES)
    ax3.set_facecolor('#FAFAFA')
    trip_order = ['couple', 'friends', 'family', 'solo', 'business']
    trip_display_names = ['Cặp đôi (Couples)', 'Bạn bè (Friends)', 'Gia đình (Family)', 'Đơn hành (Solo)', 'Công tác (Business)']
    trip_counts_ordered = [trip_map[k] for k in trip_order]
    trip_colors = ['#E76F51', '#457B9D', '#2A9D8F', '#E9C46A', '#6C757D']

    y_pos = np.arange(len(trip_order))[::-1]
    bars_trips = ax3.barh(y_pos, trip_counts_ordered, color=trip_colors, height=0.55, edgecolor='white', linewidth=1.2)

    for bar, c in zip(bars_trips, trip_counts_ordered):
        w = bar.get_width()
        pct = (c / total_trips) * 100
        ax3.text(w + (max(trip_counts_ordered) * 0.02), bar.get_y() + bar.get_height()/2.,
                 f"{c:,} ({pct:.1f}%)", va='center', ha='left', fontsize=9.5, fontweight='bold', color='#1D3557')

    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(trip_display_names, fontsize=10, fontweight='semibold', color='#2B2D42')
    ax3.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
    ax3.set_xlim(0, max(trip_counts_ordered) * 1.25)
    ax3.set_xlabel("Số lượt du khách", fontsize=10.5, fontweight='bold', color='#2B2D42')
    ax3.grid(axis='x', linestyle='--', alpha=0.6)

    ax3.set_title("C. CƠ CẤU ĐỐI TƯỢNG DU KHÁCH ĐẾN HUẾ\n"
                  "(Cặp đôi & Bạn bè chiếm gần 70% tổng lượt khách)",
                  fontsize=11.5, fontweight='bold', color='#1D3557', pad=14)

    # Viền các đồ thị
    for ax in [ax2, ax3]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    plt.suptitle("PHÂN TÍCH THÁM NGHIỆM DỮ LIỆU ĐỊA BÀN THỰC NGHIỆM CHUYÊN SÂU: THỪA THIÊN HUẾ (CASE STUDY)\n"
                 "(Luận điểm bảo vệ: Độ phủ dữ liệu thực tế dày đặc 612 địa điểm và 28,757 bài review phục vụ Đồ thị Không gian và LLM)",
                 fontsize=13.5, fontweight='bold', color='#1D3557', y=0.99)

    plt.tight_layout()

    output_png = os.path.join(OUTPUT_DIR, "hue_case_study_analysis.png")
    output_pdf = os.path.join(OUTPUT_DIR, "hue_case_study_analysis.pdf")

    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    plt.savefig(output_pdf, bbox_inches='tight')
    plt.close()

    print(f"\n✅ ĐÃ XUẤT ẢNH BIỂU ĐỒ HUẾ TỔNG HỢP (3-IN-1):")
    print(f"👉 File PNG: {output_png}")
    print(f"👉 File PDF: {output_pdf}")

    # ==========================================================================
    # HÌNH RIÊNG 1: CƠ CẤU ĐỊA ĐIỂM DU LỊCH (DONUT CHART ĐỘC LẬP)
    # ==========================================================================
    fig1, ax = plt.subplots(figsize=(7.5, 6.2), dpi=300)
    fig1.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    wedges, texts, autotexts = ax.pie(
        cat_counts,
        labels=cat_labels,
        autopct='%1.1f%%',
        startangle=140,
        colors=cat_colors,
        wedgeprops=dict(width=0.46, edgecolor='white', linewidth=2.5),
        pctdistance=0.74,
        explode=(0.02, 0.02, 0.04)
    )
    for t in texts:
        t.set_fontsize(11)
        t.set_fontweight('semibold')
        t.set_color('#2B2D42')
    for at in autotexts:
        at.set_fontsize(11)
        at.set_fontweight('bold')
        at.set_color('white')

    ax.text(0, 0, f"THỪA THIÊN HUẾ\n{total_places:,}\nĐịa điểm", ha='center', va='center',
            fontsize=13, fontweight='bold', color='#1D3557', linespacing=1.3)
    ax.set_title("CƠ CẤU PHÂN BỐ CÁC LOẠI HÌNH CƠ SỞ DU LỊCH TẠI HUẾ\n"
                 f"(Mẫu dữ liệu thực nghiệm chuẩn hóa N = {total_places:,} địa điểm)",
                 fontsize=13, fontweight='bold', color='#1D3557', pad=18)

    plt.tight_layout()
    f1_png = os.path.join(OUTPUT_DIR, "hue_places_category_donut.png")
    f1_pdf = os.path.join(OUTPUT_DIR, "hue_places_category_donut.pdf")
    plt.savefig(f1_png, dpi=300, bbox_inches='tight')
    plt.savefig(f1_pdf, bbox_inches='tight')
    plt.close()
    print(f"\n✅ ĐÃ XUẤT HÌNH 1 RIÊNG BIỆT (CƠ CẤU ĐỊA ĐIỂM):")
    print(f"👉 File PNG: {f1_png}")

    # ==========================================================================
    # HÌNH RIÊNG 2: PHÂN BỐ ĐIỂM ĐÁNH GIÁ (BAR CHART ĐỘC LẬP)
    # ==========================================================================
    fig2, ax = plt.subplots(figsize=(8.2, 5.8), dpi=300)
    fig2.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FAFAFA')

    bars = ax.bar(range(5), counts_stars, color=star_colors, width=0.58, edgecolor='white', linewidth=1.5)
    for bar, c in zip(bars, counts_stars):
        h = bar.get_height()
        pct = (c / total_reviews) * 100
        ax.text(bar.get_x() + bar.get_width()/2., h + 380, f"{c:,}\n({pct:.1f}%)",
                ha='center', va='bottom', fontsize=10, fontweight='bold', color='#1D3557')

    ax.set_xticks(range(5))
    ax.set_xticklabels(star_labels, fontsize=11, fontweight='semibold')
    ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
    ax.set_ylim(0, max(counts_stars) * 1.18)
    ax.set_ylabel("Số lượng bài review thực tế", fontsize=11, fontweight='bold', color='#2B2D42')
    ax.grid(axis='y', linestyle='--', alpha=0.6)

    # Box thông số
    avg_rating = sum(s * ratings_raw.get(s, 0) for s in stars) / total_reviews
    info_box = (
        f"Tổng đánh giá: {total_reviews:,}\n"
        f"Điểm trung bình: {avg_rating:.2f} / 5.0\n"
        f"Tỷ lệ hài lòng (4-5 Sao): {high_satisfaction:.1f}%\n"
        f"(Hiện tượng lệch dương J-shaped)"
    )
    ax.text(0.04, 0.94, info_box, transform=ax.transAxes, fontsize=10, fontweight='semibold',
            color='#1D3557', verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='#E8F8F5', edgecolor='#2A9D8F', linewidth=1.2, alpha=0.95))

    ax.set_title("PHÂN BỐ ĐIỂM SỐ ĐÁNH GIÁ (RATING) CỦA DU KHÁCH TẠI HUẾ\n"
                 f"(Dữ liệu khai phóng từ {total_reviews:,} bài phản hồi trên TripAdvisor)",
                 fontsize=12.5, fontweight='bold', color='#1D3557', pad=16)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    f2_png = os.path.join(OUTPUT_DIR, "hue_ratings_distribution.png")
    f2_pdf = os.path.join(OUTPUT_DIR, "hue_ratings_distribution.pdf")
    plt.savefig(f2_png, dpi=300, bbox_inches='tight')
    plt.savefig(f2_pdf, bbox_inches='tight')
    plt.close()
    print(f"\n✅ ĐÃ XUẤT HÌNH 2 RIÊNG BIỆT (PHÂN BỐ ĐIỂM ĐÁNH GIÁ):")
    print(f"👉 File PNG: {f2_png}")

    # ==========================================================================
    # HÌNH RIÊNG 3: PHÂN KHÚC ĐỐI TƯỢNG DU KHÁCH (TRIP TYPES ĐỘC LẬP)
    # ==========================================================================
    fig3, ax = plt.subplots(figsize=(8.8, 5.8), dpi=300)
    fig3.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FAFAFA')

    bars = ax.barh(y_pos, trip_counts_ordered, color=trip_colors, height=0.52, edgecolor='white', linewidth=1.5)
    for bar, c in zip(bars, trip_counts_ordered):
        w = bar.get_width()
        pct = (c / total_trips) * 100
        ax.text(w + (max(trip_counts_ordered) * 0.02), bar.get_y() + bar.get_height()/2.,
                f"{c:,} ({pct:.1f}%)", va='center', ha='left', fontsize=10.5, fontweight='bold', color='#1D3557')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(trip_display_names, fontsize=11, fontweight='semibold', color='#2B2D42')
    ax.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
    ax.set_xlim(0, max(trip_counts_ordered) * 1.25)
    ax.set_xlabel("Số lượt du khách ghi nhận", fontsize=11, fontweight='bold', color='#2B2D42')
    ax.grid(axis='x', linestyle='--', alpha=0.6)

    # Box thông số đối tượng
    leisure_pct = ((trip_map['couple'] + trip_map['friends']) / total_trips) * 100
    persona_box = (
        f"Tổng lượt gắn nhãn: {total_trips:,}\n"
        f"Du lịch Trải nghiệm & Cặp đôi: {leisure_pct:.1f}%\n"
        f"Công tác (Business): Chỉ chiếm {trip_map['business']/total_trips*100:.1f}%\n"
        f"-> Căn cứ thiết kế Persona cho LLM"
    )
    ax.text(0.55, 0.28, persona_box, transform=ax.transAxes, fontsize=10, fontweight='semibold',
            color='#1D3557', verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='#FEF3C7', edgecolor='#F59E0B', linewidth=1.2, alpha=0.95))

    ax.set_title("CƠ CẤU ĐỐI TƯỢNG DU KHÁCH ĐẾN THỪA THIÊN HUẾ\n"
                 "(Phân loại theo loại hình chuyến đi - Trip Types từ phản hồi du khách)",
                 fontsize=12.5, fontweight='bold', color='#1D3557', pad=16)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    f3_png = os.path.join(OUTPUT_DIR, "hue_trip_types_breakdown.png")
    f3_pdf = os.path.join(OUTPUT_DIR, "hue_trip_types_breakdown.pdf")
    plt.savefig(f3_png, dpi=300, bbox_inches='tight')
    plt.savefig(f3_pdf, bbox_inches='tight')
    plt.close()
    print(f"\n✅ ĐÃ XUẤT HÌNH 3 RIÊNG BIỆT (PHÂN LOẠI DU KHÁCH):")
    print(f"👉 File PNG: {f3_png}")
    print("=" * 80)


if __name__ == "__main__":
    plot_hue_case_study()
