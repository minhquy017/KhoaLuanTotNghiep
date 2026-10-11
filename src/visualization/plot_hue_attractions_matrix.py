# -*- coding: utf-8 -*-
"""
MA TRẬN ĐỊNH VỊ CHIẾN LƯỢC: TOP 12 ĐIỂM THAM QUAN DI SẢN CỐ ĐÔ HUẾ
Khóa luận Tốt nghiệp ngành Khoa học Dữ liệu và Trí tuệ Nhân tạo (DS&AI K3 - HUET)
Trường Kỹ thuật và Công nghệ - Đại học Huế
Đề tài: Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh dựa trên Đồ thị Tri thức Không gian và LLM
-----------------------------------------------------------------------------------------------------
- Nguồn: data/processed/tourism_vietnam.db (Bảng `places` - Category: Attraction, is_hue = 1)
- Dạng biểu đồ: Ma trận Tọa độ Bong bóng (Strategic Positioning Matrix / Quadrant Bubble Plot)
  + Trục X: Điểm đánh giá mức độ hài lòng (Rating Value: 3.2 - 4.7 sao)
  + Trục Y: Sức hút du khách (Log scale: Số lượt bài đánh giá từ 300 đến 12,000)
  + Kích thước bong bóng: Tỷ lệ theo lượt review
  + Màu sắc: Phân loại nhóm di sản theo sắc tím Cố đô Huế
- Xuất bản phẩm: docs/figures/top_hue_attractions_matrix.png (300 DPI) & .pdf
"""

import os
import sys
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Rectangle

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "docs", "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Typography tiếng Việt
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'Tahoma', 'DejaVu Sans']
plt.rcParams['axes.edgecolor'] = '#4B5563'
plt.rcParams['axes.linewidth'] = 0.9

# Danh mục 12 điểm tham quan nổi tiếng nhất Cố đô Huế chuẩn hóa tên tiếng Việt
ATTRACTIONS_DATA = [
    {"name": "Đại Nội Huế (Hoàng Thành)", "reviews": 11417, "rating": 4.30, "group": "Quần thể Di tích Hoàng cung"},
    {"name": "Chùa Thiên Mụ", "reviews": 3922, "rating": 4.20, "group": "Di tích Tâm linh & Văn hóa"},
    {"name": "Lăng vua Minh Mạng", "reviews": 2657, "rating": 4.50, "group": "Quần thể Lăng tẩm Hoàng gia"},
    {"name": "Sông Hương (Ca Huế / Du thuyền)", "reviews": 2277, "rating": 3.60, "group": "Danh lam & Sinh hoạt Đô thị"},
    {"name": "Lăng vua Tự Đức", "reviews": 2137, "rating": 4.20, "group": "Quần thể Lăng tẩm Hoàng gia"},
    {"name": "Lăng vua Khải Định", "reviews": 974, "rating": 4.50, "group": "Quần thể Lăng tẩm Hoàng gia"},
    {"name": "Đèo Hải Vân (Thiên hạ đệ nhất hùng quan)", "reviews": 643, "rating": 4.30, "group": "Danh thắng Thiên nhiên"},
    {"name": "Cầu Trường Tiền", "reviews": 628, "rating": 3.90, "group": "Danh lam & Sinh hoạt Đô thị"},
    {"name": "Lăng vua Đồng Khánh", "reviews": 585, "rating": 4.50, "group": "Quần thể Lăng tẩm Hoàng gia"},
    {"name": "Cầu ngói Thanh Toàn", "reviews": 429, "rating": 4.40, "group": "Di tích Tâm linh & Văn hóa"},
    {"name": "Chợ Đông Ba", "reviews": 400, "rating": 3.40, "group": "Danh lam & Sinh hoạt Đô thị"},
    {"name": "Vườn Quốc gia Bạch Mã", "reviews": 346, "rating": 4.50, "group": "Danh thắng Thiên nhiên"}
]

GROUP_COLORS = {
    "Quần thể Di tích Hoàng cung": "#3B0764",   # Tím hoàng cung đậm
    "Quần thể Lăng tẩm Hoàng gia": "#7E22CE",   # Tím hoàng gia quý tộc
    "Di tích Tâm linh & Văn hóa": "#A855F7",    # Tím phong lan tâm linh
    "Danh lam & Sinh hoạt Đô thị": "#EA580C",   # Cam gạch nung đô thị
    "Danh thắng Thiên nhiên": "#0D9488"        # Xanh ngọc bích thiên nhiên
}

def plot_attractions_matrix():
    df = pd.DataFrame(ATTRACTIONS_DATA)

    fig, ax = plt.subplots(figsize=(12.5, 8.2), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FAF9FD')

    # Phân vùng 3 Nhóm Chiến lược (Quadrant background / shading)
    x_threshold = 4.1
    y_threshold = 1000

    # Vùng I (Góc trên phải): Di sản Biểu tượng Toàn cầu
    ax.fill_between([x_threshold, 4.85], y_threshold, 25000, color='#F3E8FF', alpha=0.55, zorder=0)
    # Vùng II (Góc dưới phải): Điểm đến Tiềm năng / Viên ngọc Di sản
    ax.fill_between([x_threshold, 4.85], 150, y_threshold, color='#EDE9FE', alpha=0.35, zorder=0)
    # Vùng III (Góc trái): Danh thắng Sinh hoạt & Đô thị
    ax.fill_between([3.15, x_threshold], 150, 25000, color='#FFF7ED', alpha=0.4, zorder=0)

    # Đường phân cách các vùng chiến lược
    ax.axvline(x=x_threshold, color='#94A3B8', linestyle='--', linewidth=1.2, alpha=0.8, zorder=1)
    ax.axhline(y=y_threshold, color='#94A3B8', linestyle='--', linewidth=1.2, alpha=0.8, zorder=1)

    # Tiêu đề các phân vùng (Đặt ở vị trí thoáng, không đè bubble)
    ax.text(4.45, 17500, "VÙNG I: DI SẢN BIỂU TƯỢNG HÀNG ĐẦU\n(Sức hút áp đảo & Đánh giá xuất sắc)",
            fontsize=9.5, fontweight='bold', color='#4C1D95', ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFFFFF', edgecolor='#C084FC', alpha=0.95))

    ax.text(4.48, 190, "VÙNG II: VIÊN NGỌC DI SẢN TIỀM NĂNG\n(Hài lòng rất cao - Đang thu hút du khách)",
            fontsize=9, fontweight='bold', color='#6B21A8', ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFFFFF', edgecolor='#DDD6FE', alpha=0.95))

    ax.text(3.38, 17500, "VÙNG III: VĂN HÓA ĐÔ THỊ & ĐỜI SỐNG\n(Lưu lượng lớn - Trải nghiệm phong phú)",
            fontsize=9, fontweight='bold', color='#C2410C', ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFFFFF', edgecolor='#FDBA74', alpha=0.95))

    # Scale bubble size: min 180, max 1600
    min_size, max_size = 180, 1600
    df['bubble_size'] = np.interp(df['reviews'], (df['reviews'].min(), df['reviews'].max()), (min_size, max_size))

    # Tọa độ offset điều chỉnh nhãn tránh đè nhau (dx, dy, ha_align, va_align)
    label_offsets = {
        "Đại Nội Huế (Hoàng Thành)": (0, -2600, 'center', 'top'),
        "Chùa Thiên Mụ": (0.035, 200, 'left', 'center'),
        "Lăng vua Minh Mạng": (0.035, 100, 'left', 'center'),
        "Sông Hương (Ca Huế / Du thuyền)": (0.035, 0, 'left', 'center'),
        "Lăng vua Tự Đức": (-0.035, -350, 'right', 'center'),
        "Lăng vua Khải Định": (0.035, 80, 'left', 'center'),
        "Đèo Hải Vân (Thiên hạ đệ nhất hùng quan)": (-0.035, 70, 'right', 'center'),
        "Cầu Trường Tiền": (0.035, -40, 'left', 'center'),
        "Lăng vua Đồng Khánh": (0.035, -80, 'left', 'center'),
        "Cầu ngói Thanh Toàn": (0.035, 0, 'left', 'center'),
        "Chợ Đông Ba": (0.035, 0, 'left', 'center'),
        "Vườn Quốc gia Bạch Mã": (0.035, 0, 'left', 'center')
    }

    # Vẽ bubbles theo nhóm
    groups_plotted = set()
    for _, row in df.iterrows():
        g = row['group']
        color = GROUP_COLORS.get(g, '#7E22CE')
        label = g if g not in groups_plotted else None
        groups_plotted.add(g)

        ax.scatter(row['rating'], row['reviews'], s=row['bubble_size'],
                   color=color, alpha=0.88, edgecolors='white', linewidth=2.2,
                   label=label, zorder=3)

        # Ghi nhãn tên điểm tham quan và thông số chuẩn, không dùng ký tự Unicode đặc biệt
        dx, dy, ha_align, va_align = label_offsets.get(row['name'], (0.035, 0, 'left', 'center'))
        rating_badge = f"{row['rating']:.2f}/5"
        rev_badge = f"{row['reviews']:,} lượt"

        if row['name'] == "Đại Nội Huế (Hoàng Thành)":
            ax.annotate(f"{row['name']}\n[Điểm: {rating_badge}  •  {rev_badge}]",
                        xy=(row['rating'], row['reviews']),
                        xytext=(row['rating'] + dx, row['reviews'] + dy),
                        ha=ha_align, va=va_align, fontsize=10, fontweight='bold', color='#2E0854',
                        bbox=dict(boxstyle='round,pad=0.35', facecolor='#FFFFFF', edgecolor=color, linewidth=1.4, alpha=0.95),
                        arrowprops=dict(arrowstyle='->', color='#2E0854', lw=1.2))
        else:
            ax.annotate(f"{row['name']}  [{rating_badge} • {rev_badge}]",
                        xy=(row['rating'], row['reviews']),
                        xytext=(row['rating'] + dx, row['reviews'] + dy),
                        ha=ha_align, va=va_align, fontsize=9.2, fontweight='bold', color='#1E293B',
                        bbox=dict(boxstyle='round,pad=0.25', facecolor='#FFFFFF', edgecolor='#CBD5E1', linewidth=0.8, alpha=0.92))

    # Cấu hình trục
    ax.set_yscale('log')
    ax.set_ylim(150, 24000)
    ax.set_xlim(3.18, 4.82)

    # Format ticks
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda y, _: f'{int(y):,}'))
    ax.set_yticks([200, 500, 1000, 2000, 5000, 10000])

    ax.set_xlabel("Mức độ Hài lòng Trung bình của Du khách (Rating trên thang 5.0)", fontsize=11, fontweight='bold', color='#1E293B', labelpad=8)
    ax.set_ylabel("Sức hút Du khách: Số lượt Đánh giá ghi nhận (Thang Logarit)", fontsize=11, fontweight='bold', color='#1E293B', labelpad=8)

    ax.grid(True, which='both', linestyle='--', linewidth=0.6, alpha=0.5, color='#CBD5E1', zorder=1)

    ax.set_title("MA TRẬN ĐỊNH VỊ CHIẾN LƯỢC: TOP 12 ĐIỂM THAM QUAN DI SẢN CỐ ĐÔ HUẾ\n"
                 "(Phân tích Đa chiều giữa Sức hút Du khách & Độ hài lòng - Khung Tri thức cho Lập Lịch trình)",
                 fontsize=12.5, fontweight='bold', color='#3B0764', pad=16)

    # Chú thích nhóm phân loại di sản đặt ở dưới cùng ngang hàng (Tránh che lấp dữ liệu)
    legend = ax.legend(title="Phân loại Cụm Di sản & Danh thắng Huế",
                       loc='upper center', bbox_to_anchor=(0.5, -0.11),
                       ncol=3, frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1',
                       fontsize=9, title_fontsize=9.5)
    legend.get_title().set_fontweight('bold')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    out_png = os.path.join(OUTPUT_DIR, "top_hue_attractions_matrix.png")
    out_pdf = os.path.join(OUTPUT_DIR, "top_hue_attractions_matrix.pdf")
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.savefig(out_pdf, bbox_inches='tight')
    plt.close()

    print(f"\n✅ ĐÃ XUẤT MA TRẬN ĐỊNH VỊ ĐIỂM THAM QUAN HUẾ:")
    print(f"👉 File PNG: {out_png}")
    print(f"👉 File PDF: {out_pdf}")

if __name__ == "__main__":
    plot_attractions_matrix()
