# -*- coding: utf-8 -*-
"""
TRỰC QUAN HÓA THỰC ĐƠN NGẦM: TOP 10 MÓN ĂN TOÀN QUỐC VS. TOP 10 ĐẶC SẢN HUẾ
Khóa luận Tốt nghiệp ngành Khoa học Dữ liệu và Trí tuệ Nhân tạo (DS&AI K3 - HUET)
Trường Kỹ thuật và Công nghệ - Đại học Huế
Đề tài: Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh dựa trên Đồ thị Tri thức Không gian và LLM
-----------------------------------------------------------------------------------------------------
- Nguồn dữ liệu: data/processed/tourism_vietnam.db (Bảng `restaurant_dishes`, `dishes`, `places`)
- Xuất 2 biểu đồ độc lập (300 DPI Academic Quality):
  1. docs/figures/top10_dishes_vietnam.png (Toàn quốc - Khai phá từ 1.7M review)
  2. docs/figures/top10_dishes_hue.png (Thừa Thiên Huế - Khai phá từ review địa phương)
"""

import os
import sys
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

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


def load_dishes_data():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Top 10 toàn quốc
    cur.execute("""
        SELECT d.canonical_name, d.category, SUM(rd.mention_count) as total_mentions,
               ROUND(AVG(rd.avg_rating), 2) as avg_rating
        FROM restaurant_dishes rd
        JOIN dishes d ON rd.dish_id = d.dish_id
        GROUP BY rd.dish_id
        ORDER BY total_mentions DESC
        LIMIT 10;
    """)
    vn_dishes = cur.fetchall()

    # 2. Top 10 Đặc sản gốc Cố đô Huế (Hue Heritage Cuisine)
    cur.execute("""
        SELECT d.canonical_name, d.category, SUM(rd.mention_count) as total_mentions,
               ROUND(AVG(rd.avg_rating), 2) as avg_rating
        FROM restaurant_dishes rd
        JOIN dishes d ON rd.dish_id = d.dish_id
        WHERE d.region_origin = 'Huế'
        GROUP BY rd.dish_id
        ORDER BY total_mentions DESC
        LIMIT 10;
    """)
    hue_dishes = cur.fetchall()

    # Thống kê tổng số lượt nhắc
    cur.execute("SELECT SUM(mention_count) FROM restaurant_dishes")
    total_vn_mentions = cur.fetchone()[0] or 1

    cur.execute("""
        SELECT SUM(rd.mention_count)
        FROM restaurant_dishes rd
        JOIN dishes d ON rd.dish_id = d.dish_id
        WHERE d.region_origin = 'Huế'
    """)
    total_hue_mentions = cur.fetchone()[0] or 1

    conn.close()
    return vn_dishes, hue_dishes, total_vn_mentions, total_hue_mentions


def plot_top_dishes():
    print("=" * 80)
    print("🍜 TRỰC QUAN HÓA THỰC ĐƠN NGẦM: TOP 10 TOÀN QUỐC VS. TOP 10 HUẾ")
    print("=" * 80)

    vn_dishes, hue_dishes, total_vn, total_hue = load_dishes_data()

    print(f"• Tổng số lượt nhắc món toàn quốc : {total_vn:,}")
    print(f"• Tổng số lượt nhắc món tại Huế  : {total_hue:,}")

    # ==========================================================================
    # BIỂU ĐỒ 1: TOP 10 MÓN ĂN TOÀN VIỆT NAM (NATIONWIDE)
    fig1, ax1 = plt.subplots(figsize=(10, 6.2), dpi=300)
    fig1.patch.set_facecolor('#FFFFFF')
    ax1.set_facecolor('#FAFAFA')

    vn_names = [d[0] for d in vn_dishes][::-1]
    vn_counts = [d[2] for d in vn_dishes][::-1]
    vn_ratings = [d[3] for d in vn_dishes][::-1]

    # Bảng màu ẩm thực Việt Nam: Gradient Hổ phách - Cam nướng - Đỏ gốm - Rượu vang
    vn_colors = [
        "#FDBA74", "#FB923C", "#F97316", "#EA580C", "#D9480F",
        "#C92A2A", "#B91C1C", "#991B1B", "#7F1D1D", "#58121A"
    ]

    y_pos = np.arange(len(vn_names))
    bars1 = ax1.barh(y_pos, vn_counts, color=vn_colors, height=0.6, edgecolor='white', linewidth=1.5)

    max_vn = max(vn_counts)
    for bar, c, r in zip(bars1, vn_counts, vn_ratings):
        w = bar.get_width()
        label_text = f"[Đánh giá: {r:.2f} / 5]"
        ax1.text(w + (max_vn * 0.015), bar.get_y() + bar.get_height()/2., label_text,
                 va='center', ha='left', fontsize=10.5, fontweight='bold', color='#7F1D1D')

    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(vn_names, fontsize=11, fontweight='semibold', color='#2B2D42')
    ax1.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
    ax1.set_xlim(0, max_vn * 1.25)
    ax1.set_xlabel("Số lượt du khách quốc tế & nội địa đề cập trong bài review", fontsize=11, fontweight='bold', color='#2B2D42')
    ax1.grid(axis='x', linestyle='--', alpha=0.6)

    ax1.set_title("TOP 10 MÓN ĂN VIỆT NAM ĐƯỢC DU KHÁCH ĐỀ CẬP NHIỀU NHẤT TOÀN QUỐC\n"
                  "(Khai phá thực thể ẩm thực từ 1.7 triệu đánh giá - Phục vụ Đồ thị Tri thức)",
                  fontsize=12.5, fontweight='bold', color='#7F1D1D', pad=16)

    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    plt.tight_layout()
    out1_png = os.path.join(OUTPUT_DIR, "top10_dishes_vietnam.png")
    out1_pdf = os.path.join(OUTPUT_DIR, "top10_dishes_vietnam.pdf")
    plt.savefig(out1_png, dpi=300, bbox_inches='tight')
    plt.savefig(out1_pdf, bbox_inches='tight')
    plt.close()

    print(f"\n✅ ĐÃ XUẤT BIỂU ĐỒ 1 (TOP 10 VIỆT NAM):")
    print(f"👉 File PNG: {out1_png}")
    print(f"👉 File PDF: {out1_pdf}")

    # ==========================================================================
    # BIỂU ĐỒ 2: TOP 10 ĐẶC SẢN THỪA THIÊN HUẾ (CASE STUDY)
    # ==========================================================================
    fig2, ax2 = plt.subplots(figsize=(10, 6.2), dpi=300)
    fig2.patch.set_facecolor('#FFFFFF')
    ax2.set_facecolor('#FAFAFA')

    hue_names = [d[0] for d in hue_dishes][::-1]
    hue_counts = [d[2] for d in hue_dishes][::-1]
    hue_ratings = [d[3] for d in hue_dishes][::-1]

    # Bảng màu Tím Hoàng gia Cố đô Huế (Royal Hue Violet / Plum)
    hue_colors = [
        "#D8B4FE", "#C084FC", "#A855F7", "#9333EA", "#7E22CE",
        "#6B21A8", "#581C87", "#4C1D95", "#3B0764", "#2E0854"
    ]

    y_pos2 = np.arange(len(hue_names))
    bars2 = ax2.barh(y_pos2, hue_counts, color=hue_colors, height=0.6, edgecolor='white', linewidth=1.5)

    max_hue = max(hue_counts)
    for bar, c, r in zip(bars2, hue_counts, hue_ratings):
        w = bar.get_width()
        label_text = f"[Đánh giá: {r:.2f} / 5]"
        ax2.text(w + (max_hue * 0.015), bar.get_y() + bar.get_height()/2., label_text,
                 va='center', ha='left', fontsize=10.5, fontweight='bold', color='#3B0764')

    ax2.set_yticks(y_pos2)
    ax2.set_yticklabels(hue_names, fontsize=11, fontweight='semibold', color='#2B2D42')
    ax2.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
    ax2.set_xlim(0, max_hue * 1.25)
    ax2.set_xlabel("Số lượt du khách đề cập đến các món ăn đặc sản gốc Cố đô Huế", fontsize=11, fontweight='bold', color='#2B2D42')
    ax2.grid(axis='x', linestyle='--', alpha=0.6)

    ax2.set_title("TOP 10 ĐẶC SẢN ẨM THỰC CỐ ĐÔ HUẾ ĐƯỢC DU KHÁCH ĐỀ CẬP NHIỀU NHẤT\n"
                  "(Khai phá thực thể ẩm thực từ tập dữ liệu - Phục vụ Đồ thị Tri thức)",
                  fontsize=12.5, fontweight='bold', color='#3B0764', pad=16)

    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    plt.tight_layout()
    out2_png = os.path.join(OUTPUT_DIR, "top10_dishes_hue.png")
    out2_pdf = os.path.join(OUTPUT_DIR, "top10_dishes_hue.pdf")
    plt.savefig(out2_png, dpi=300, bbox_inches='tight')
    plt.savefig(out2_pdf, bbox_inches='tight')
    plt.close()

    print(f"\n✅ ĐÃ XUẤT BIỂU ĐỒ 2 (TOP 10 HUẾ):")
    print(f"👉 File PNG: {out2_png}")
    print(f"👉 File PDF: {out2_pdf}")
    print("=" * 80)


if __name__ == "__main__":
    plot_top_dishes()

