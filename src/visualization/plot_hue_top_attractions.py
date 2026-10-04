# -*- coding: utf-8 -*-
"""
TOP 12 ĐIỂM THAM QUAN NỔI BẬT TẠI CỐ ĐÔ HUẾ
Khóa luận Tốt nghiệp ngành Khoa học Dữ liệu và Trí tuệ Nhân tạo (DS&AI K3 - HUET)
-----------------------------------------------------------------------------------------------------
- Dạng biểu đồ: Lollipop Chart (Cleveland Dot Plot)
  + Trục Y: Tên địa điểm (sắp theo lượt đánh giá giảm dần)
  + Trục X: Số lượt đánh giá
  + Màu chấm: Mã hóa theo Rating trung bình (gradient tím Huế)
- Xuất bản phẩm: docs/figures/top_hue_attractions.png (300 DPI) & .pdf
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "docs", "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Typography
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'Tahoma', 'DejaVu Sans']

# ── Dữ liệu Top 12 điểm tham quan Huế ──
ATTRACTIONS = [
    {"name": "Đại Nội Huế (Hoàng Thành)",           "reviews": 11417, "rating": 4.30, "group": "Quần thể Hoàng cung"},
    {"name": "Chùa Thiên Mụ",                        "reviews": 3922,  "rating": 4.20, "group": "Tâm linh & Văn hóa"},
    {"name": "Lăng vua Minh Mạng",                   "reviews": 2657,  "rating": 4.50, "group": "Lăng tẩm Hoàng gia"},
    {"name": "Sông Hương (Ca Huế / Du thuyền)",      "reviews": 2277,  "rating": 3.60, "group": "Danh lam Đô thị"},
    {"name": "Lăng vua Tự Đức",                      "reviews": 2137,  "rating": 4.20, "group": "Lăng tẩm Hoàng gia"},
    {"name": "Lăng vua Khải Định",                   "reviews": 974,   "rating": 4.50, "group": "Lăng tẩm Hoàng gia"},
    {"name": "Đèo Hải Vân",                          "reviews": 643,   "rating": 4.30, "group": "Danh thắng Thiên nhiên"},
    {"name": "Cầu Trường Tiền",                      "reviews": 628,   "rating": 3.90, "group": "Danh lam Đô thị"},
    {"name": "Lăng vua Đồng Khánh",                  "reviews": 585,   "rating": 4.50, "group": "Lăng tẩm Hoàng gia"},
    {"name": "Cầu ngói Thanh Toàn",                  "reviews": 429,   "rating": 4.40, "group": "Tâm linh & Văn hóa"},
    {"name": "Chợ Đông Ba",                           "reviews": 400,   "rating": 3.40, "group": "Danh lam Đô thị"},
    {"name": "Vườn Quốc gia Bạch Mã",                "reviews": 346,   "rating": 4.50, "group": "Danh thắng Thiên nhiên"},
]

# Nhóm → Marker shape
GROUP_MARKERS = {
    "Quần thể Hoàng cung":    "D",   # Kim cương
    "Lăng tẩm Hoàng gia":     "s",   # Vuông
    "Tâm linh & Văn hóa":     "^",   # Tam giác
    "Danh lam Đô thị":        "o",   # Tròn
    "Danh thắng Thiên nhiên":  "p",   # Ngũ giác
}


def plot_top_attractions():
    # Sắp xếp tăng dần để hiển thị trên lên (matplotlib vẽ bottom-up)
    data = sorted(ATTRACTIONS, key=lambda x: x['reviews'])
    names = [d['name'] for d in data]
    reviews = np.array([d['reviews'] for d in data])
    ratings = np.array([d['rating'] for d in data])
    groups = [d['group'] for d in data]

    # ── Colormap: Rating → Gradient tím Huế (thấp = nhạt, cao = đậm) ──
    cmap = mcolors.LinearSegmentedColormap.from_list(
        'hue_purple', ['#E9D5FF', '#A855F7', '#6B21A8', '#3B0764']
    )
    norm = mcolors.Normalize(vmin=3.2, vmax=4.6)
    dot_colors = [cmap(norm(r)) for r in ratings]

    # ── Figure ──
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FDFCFF')

    y_pos = np.arange(len(names))

    # Vẽ "que kẹo" (lollipop stems)
    for i in range(len(names)):
        ax.hlines(y=y_pos[i], xmin=0, xmax=reviews[i],
                  color='#D8B4FE', linewidth=2.2, alpha=0.7, zorder=1)

    # Vẽ chấm tròn (dots) - với marker theo nhóm
    for i in range(len(names)):
        marker = GROUP_MARKERS.get(groups[i], 'o')
        ax.scatter(reviews[i], y_pos[i], s=180, color=dot_colors[i],
                   edgecolors='white', linewidth=2, zorder=3, marker=marker)

        # Rating badge bên phải chấm
        ax.text(reviews[i] + 250, y_pos[i],
                f"{ratings[i]:.1f}/5",
                fontsize=9.5, fontweight='bold',
                color=dot_colors[i], va='center', ha='left')

    # Trục Y: tên địa điểm
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=10.5, fontweight='medium', color='#1E1B4B')

    # Trục X
    ax.set_xlabel("Số lượt đánh giá từ du khách quốc tế (TripAdvisor)",
                  fontsize=11, fontweight='bold', color='#1E293B', labelpad=10)
    ax.set_xlim(-200, max(reviews) + 2500)

    # Grid nhẹ
    ax.xaxis.grid(True, linestyle='--', linewidth=0.6, alpha=0.4, color='#CBD5E1')
    ax.yaxis.grid(False)

    # Spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(0.8)
    ax.spines['left'].set_color('#94A3B8')
    ax.spines['bottom'].set_linewidth(0.8)
    ax.spines['bottom'].set_color('#94A3B8')

    # ── Tiêu đề ──
    ax.set_title(
        "TOP 12 ĐIỂM THAM QUAN NỔI BẬT TẠI CỐ ĐÔ HUẾ\n"
        "Xếp hạng theo Số lượt Đánh giá — Màu sắc thể hiện Rating trung bình",
        fontsize=13, fontweight='bold', color='#3B0764', pad=16
    )

    # ── Legend nhóm (markers) ──
    legend_elements = []
    for group_name, marker in GROUP_MARKERS.items():
        legend_elements.append(
            Line2D([0], [0], marker=marker, color='w', markerfacecolor='#7E22CE',
                   markeredgecolor='white', markersize=10, label=group_name, linewidth=0)
        )
    legend = ax.legend(handles=legend_elements,
                       title="Phân loại Di sản & Danh thắng",
                       loc='lower right',
                       fontsize=9, title_fontsize=9.5,
                       frameon=True, facecolor='#FFFFFF', edgecolor='#E5E7EB',
                       framealpha=0.95)
    legend.get_title().set_fontweight('bold')

    # ── Colorbar cho Rating ──
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, orientation='vertical', shrink=0.5, pad=0.08, aspect=20)
    cbar.set_label('Rating trung bình', fontsize=10, fontweight='bold', color='#3B0764')
    cbar.ax.tick_params(labelsize=9)

    plt.tight_layout()

    out_png = os.path.join(OUTPUT_DIR, "top_hue_attractions.png")
    out_pdf = os.path.join(OUTPUT_DIR, "top_hue_attractions.pdf")
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.savefig(out_pdf, bbox_inches='tight')
    plt.close()

    print(f"\n✅ ĐÃ XUẤT BIỂU ĐỒ TOP ĐIỂM THAM QUAN HUẾ:")
    print(f"👉 File PNG: {out_png}")
    print(f"👉 File PDF: {out_pdf}")


if __name__ == "__main__":
    plot_top_attractions()
