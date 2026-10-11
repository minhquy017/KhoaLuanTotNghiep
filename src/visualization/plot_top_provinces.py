# -*- coding: utf-8 -*-
"""
TRỰC QUAN HÓA DỮ LIỆU ĐỊA ĐIỂM DU LỊCH THEO TỈNH/THÀNH & VÙNG MIỀN
Khóa luận Tốt nghiệp ngành Khoa học Dữ liệu và Trí tuệ Nhân tạo (DS&AI K3 - HUET)
Đề tài: Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh dựa trên Đồ thị Tri thức Không gian và LLM
-----------------------------------------------------------------------------------------------------
- Nguồn dữ liệu: data/processed/tourism_vietnam.db (Bảng `places`)
- Xuất bản phẩm: docs/figures/top10_provinces_distribution.png (300 DPI Academic Quality)
- Phân tích: Top 10 tỉnh/thành có mật độ cơ sở du lịch cao nhất, bóc tách theo cơ cấu (Ẩm thực, Khách sạn, Điểm tham quan)
  và phân bổ theo 3 Vùng miền (Miền Bắc, Miền Trung, Miền Nam/Tây Nguyên).
"""

import os
import sys
import sqlite3
import pandas as pd
import numpy as np

# Đảm bảo UTF-8 cho Windows console
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns


# ==============================================================================
# CẤU HÌNH THƯ MỤC VÀ STYLE CHUẨN HỌC THUẬT (ACADEMIC PUBLICATION STYLE)
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "tourism_vietnam.db")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "docs", "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Cấu hình Typography tiếng Việt và Style chuẩn ấn phẩm
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'Tahoma', 'DejaVu Sans']
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#E0E0E0'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.6


# Từ điển ánh xạ chuẩn hóa tên Tỉnh/Thành và Vùng miền
PROVINCE_MAPPING = {
    "Thành phố Hồ Chí Minh": {"name": "TP. Hồ Chí Minh", "region": "Miền Nam"},
    "Thủ Đô Hà Nội": {"name": "Hà Nội", "region": "Miền Bắc"},
    "Thành phố Đà Nẵng": {"name": "Đà Nẵng", "region": "Miền Trung"},
    "Thành phố Huế": {"name": "Thừa Thiên Huế", "region": "Miền Trung"},
    "Tỉnh Lâm Đồng": {"name": "Lâm Đồng (Đà Lạt)", "region": "Tây Nguyên / Nam"},
    "Tỉnh Ninh Bình": {"name": "Ninh Bình", "region": "Miền Bắc"},
    "Tỉnh Lào Cai": {"name": "Lào Cai (Sa Pa)", "region": "Miền Bắc"},
    "Tỉnh Khánh Hòa": {"name": "Khánh Hòa (Nha Trang)", "region": "Miền Trung"},
    "Thành phố Hải Phòng": {"name": "Hải Phòng", "region": "Miền Bắc"},
    "Tỉnh An Giang": {"name": "An Giang", "region": "Miền Nam"},
    "Thành phố Quảng Ninh": {"name": "Quảng Ninh (Hạ Long)", "region": "Miền Bắc"},
    "Thành phố Cần Thơ": {"name": "Cần Thơ", "region": "Miền Nam"}
}

REGION_COLORS = {
    "Miền Bắc": "#2A9D8F",            # Xanh cổ vịt hiện đại
    "Miền Trung": "#E76F51",          # Cam đỏ di sản / Cố đô
    "Miền Nam": "#457B9D",            # Xanh lam năng động
    "Tây Nguyên / Nam": "#1D3557"     # Xanh đậm đại ngàn
}

CATEGORY_COLORS = {
    "restaurant": "#E76F51",   # Ẩm thực / Nhà hàng (Cam gạch ấm áp)
    "hotel": "#2A9D8F",        # Lưu trú / Khách sạn (Xanh ngọc trang nhã)
    "attraction": "#E9C46A"    # Điểm tham quan / Di tích (Vàng hổ phách nổi bật)
}

CATEGORY_NAMES = {
    "restaurant": "Ẩm thực (Restaurant)",
    "hotel": "Lưu trú (Hotel)",
    "attraction": "Tham quan / Di tích (Attraction)"
}


def load_data():
    """Truy vấn dữ liệu địa điểm từ SQLite database."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Không tìm thấy CSDL SQLite tại: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT locality, category, count(*) as count
        FROM places
        WHERE locality IS NOT NULL AND trim(locality) != ''
        GROUP BY locality, category
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def generate_top10_visualization():
    print("=" * 80)
    print("📊 TRỰC QUAN HÓA DỮ LIỆU ĐỊA ĐIỂM DU LỊCH (TOP 10 TỈNH/THÀNH & VÙNG MIỀN)")
    print("=" * 80)

    df = load_data()

    # Tính tổng số cơ sở du lịch theo từng locality
    locality_totals = df.groupby('locality')['count'].sum().sort_values(ascending=False)
    top10_raw = locality_totals.head(10).index.tolist()

    # Lọc lấy Top 10 và tạo Pivot table: rows = locality, cols = category
    df_top10 = df[df['locality'].isin(top10_raw)].copy()
    pivot = df_top10.pivot(index='locality', columns='category', values='count').fillna(0).loc[top10_raw]

    # Đảm bảo có đủ 3 cột category
    for col in ['restaurant', 'hotel', 'attraction']:
        if col not in pivot.columns:
            pivot[col] = 0

    pivot = pivot[['restaurant', 'hotel', 'attraction']]
    pivot['total'] = pivot.sum(axis=1)

    # Thêm thông tin Tên hiển thị chuẩn và Vùng miền
    pivot['clean_name'] = [PROVINCE_MAPPING.get(loc, {}).get("name", loc) for loc in pivot.index]
    pivot['region'] = [PROVINCE_MAPPING.get(loc, {}).get("region", "Khác") for loc in pivot.index]
    
    # Tính tỷ lệ % trên toàn bộ tập dữ liệu (8,363 địa điểm)
    total_nationwide = locality_totals.sum()
    pivot['pct_nationwide'] = (pivot['total'] / total_nationwide) * 100

    # In bảng số liệu thống kê ra console để đưa vào báo cáo
    print("\n📋 BẢNG THỐNG KÊ CHI TIẾT TOP 10 TỈNH/THÀNH CÓ MẬT ĐỘ CƠ SỞ DU LỊCH CAO NHẤT:")
    display_df = pivot[['clean_name', 'region', 'restaurant', 'hotel', 'attraction', 'total', 'pct_nationwide']].copy()
    display_df.columns = ['Tỉnh/Thành phố', 'Vùng miền', 'Ẩm thực', 'Khách sạn', 'Tham quan', 'Tổng số', 'Tỷ lệ toàn quốc (%)']
    print(display_df.to_string(index=False))
    print(f"\n• Tổng số cơ sở du lịch tại Top 10 tỉnh/thành: {pivot['total'].sum():,} / {total_nationwide:,} "
          f"({(pivot['total'].sum() / total_nationwide) * 100:.1f}% tổng quy mô toàn quốc)")

    # --------------------------------------------------------------------------
    # VẼ BIỂU ĐỒ THANH NGANG XẾP CHỒNG (HORIZONTAL STACKED BAR CHART)
    # --------------------------------------------------------------------------
    # Đảo ngược thứ tự để Top 1 (TP.HCM) nằm ở trên cùng
    plot_df = pivot.iloc[::-1].copy()

    fig, ax = plt.subplots(figsize=(13, 8), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FAFAFA')

    y_pos = np.arange(len(plot_df))
    bar_height = 0.62

    # Vẽ từng phần xếp chồng (Ẩm thực -> Khách sạn -> Tham quan)
    bars_rest = ax.barh(y_pos, plot_df['restaurant'], height=bar_height, 
                         label=CATEGORY_NAMES['restaurant'], color=CATEGORY_COLORS['restaurant'], 
                         edgecolor='white', linewidth=1.2)

    bars_hotel = ax.barh(y_pos, plot_df['hotel'], left=plot_df['restaurant'], height=bar_height, 
                          label=CATEGORY_NAMES['hotel'], color=CATEGORY_COLORS['hotel'], 
                          edgecolor='white', linewidth=1.2)

    bars_attr = ax.barh(y_pos, plot_df['attraction'], left=plot_df['restaurant'] + plot_df['hotel'], height=bar_height, 
                         label=CATEGORY_NAMES['attraction'], color=CATEGORY_COLORS['attraction'], 
                         edgecolor='white', linewidth=1.2)

    # Ghi chú tổng số lượng và tỷ lệ % ở đầu mỗi thanh
    max_val = plot_df['total'].max()
    for i, (idx, row) in enumerate(plot_df.iterrows()):
        total_val = int(row['total'])
        pct = row['pct_nationwide']
        region = row['region']
        
        # Nhãn tổng số
        label_text = f" {total_val:,} ({pct:.1f}%)"
        ax.text(total_val + (max_val * 0.01), i, label_text, 
                va='center', ha='left', fontsize=10.5, fontweight='bold', color='#1D3557')

        # Thêm nhãn phụ số lượng chi tiết vào bên trong đoạn thanh nếu kích thước đủ lớn
        if row['restaurant'] > 300:
            ax.text(row['restaurant'] / 2, i, f"{int(row['restaurant']):,}", 
                    va='center', ha='center', fontsize=9, color='white', fontweight='bold')
        if row['hotel'] > 200:
            ax.text(row['restaurant'] + row['hotel'] / 2, i, f"{int(row['hotel']):,}", 
                    va='center', ha='center', fontsize=9, color='white', fontweight='bold')
        if row['attraction'] > 200:
            ax.text(row['restaurant'] + row['hotel'] + row['attraction'] / 2, i, f"{int(row['attraction']):,}", 
                    va='center', ha='center', fontsize=9, color='white', fontweight='bold')

    # Định dạng trục tung (Y) với Nhãn tỉnh kèm Vùng miền
    y_labels = [f"{row['clean_name']}  [{row['region']}]" for _, row in plot_df.iterrows()]
    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_labels, fontsize=11, fontweight='semibold', color='#2B2D42')

    # Định dạng trục hoành (X)
    ax.set_xlim(0, max_val * 1.18)
    ax.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
    ax.set_xlabel("Số lượng cơ sở du lịch (Địa điểm)", fontsize=11.5, fontweight='bold', color='#2B2D42', labelpad=10)
    ax.grid(axis='x', color='#E0E0E0', linestyle='--', linewidth=0.8, alpha=0.7)
    ax.set_axisbelow(True)

    # Tiêu đề biểu đồ chuẩn học thuật
    ax.set_title("PHÂN BỐ MẬT ĐỘ CƠ SỞ DU LỊCH THEO TOP 10 TỈNH/THÀNH PHỐ VÀ VÙNG MIỀN TẠI VIỆT NAM\n"
                 "(Nguồn: Cơ sở Dữ liệu Không gian Du lịch Việt Nam - Khóa luận Tốt nghiệp DS&AI K3)",
                 fontsize=13.5, fontweight='bold', color='#1D3557', pad=18)

    # Chú giải (Legend)
    legend = ax.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='#CCCCCC', 
                       fontsize=10.5, title="Phân loại Cơ sở (Category)", title_fontsize=11)
    legend.get_title().set_fontweight('bold')

    # Loại bỏ đường viền thừa (Spines)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#888888')
    ax.spines['bottom'].set_color('#888888')

    plt.tight_layout()

    # Lưu ảnh độ phân giải cao
    output_png = os.path.join(OUTPUT_DIR, "top10_provinces_distribution.png")
    output_pdf = os.path.join(OUTPUT_DIR, "top10_provinces_distribution.pdf")
    
    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    plt.savefig(output_pdf, bbox_inches='tight')
    plt.close()

    print(f"\n✅ ĐÃ XUẤT ẢNH BIỂU ĐỒ THÀNH CÔNG:")
    print(f"👉 File PNG (300 DPI): {output_png}")
    print(f"👉 File PDF (Vector) : {output_pdf}")
    print("=" * 80)


if __name__ == "__main__":
    generate_top10_visualization()
