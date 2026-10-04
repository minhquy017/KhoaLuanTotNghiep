# -*- coding: utf-8 -*-
"""
TRỰC QUAN HÓA CHUỖI THỜI GIAN & MÙA VỤ DU LỊCH VIỆT NAM (2015 - 2026)
Khóa luận Tốt nghiệp ngành Khoa học Dữ liệu và Trí tuệ Nhân tạo (DS&AI K3 - HUET)
Đề tài: Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh dựa trên Đồ thị Tri thức Không gian và LLM
-----------------------------------------------------------------------------------------------------
- Nguồn dữ liệu: data/processed/tourism_vietnam.db (Bảng `reviews`, 1.69 triệu bài)
- Mục tiêu phân tích:
  + Xu hướng chuỗi thời gian (Time-series) giai đoạn 2015 – 2026
  + Sự sụt giảm nghiêm trọng thời kỳ Covid-19 (2020 – 2021) và phục hồi kỷ lục từ 2022 – nay
  + Phân tích quy luật mùa vụ (Seasonality): Mùa Tết & khách quốc tế (T1 - T4), Mùa hè nội địa (T7 - T8)
- Xuất bản phẩm: docs/figures/temporal_tourism_trends_2015_2026.png (300 DPI Academic Quality)
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
import matplotlib.dates as mdates
import seaborn as sns


# ==============================================================================
# CẤU HÌNH THƯ MỤC & STYLE CHUẨN HỌC THUẬT
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "tourism_vietnam.db")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "docs", "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Cấu hình Typography tiếng Việt
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'Tahoma', 'DejaVu Sans']
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#E0E0E0'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.6


# Bảng tra cứu tên tháng tiếng Anh & tiếng Việt
MONTH_MAPPING = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
    'thg 1': 1, 'thg 2': 2, 'thg 3': 3, 'thg 4': 4, 'thg 5': 5, 'thg 6': 6,
    'thg 7': 7, 'thg 8': 8, 'thg 9': 9, 'thg 10': 10, 'thg 11': 11, 'thg 12': 12,
    'tháng 1': 1, 'tháng 2': 2, 'tháng 3': 3, 'tháng 4': 4, 'tháng 5': 5, 'tháng 6': 6,
    'tháng 7': 7, 'tháng 8': 8, 'tháng 9': 9, 'tháng 10': 10, 'tháng 11': 11, 'tháng 12': 12,
}


def parse_visit_date(date_str):
    """Trích xuất năm (year) và tháng (month) từ chuỗi ngày đánh giá."""
    if not date_str:
        return None, None
    s = str(date_str).lower().strip()
    year_match = re.search(r'\b(20\d\d|19\d\d)\b', s)
    if not year_match:
        return None, None
    year = int(year_match.group(1))

    month = None
    for k, v in MONTH_MAPPING.items():
        if k in s:
            month = v
            break
    return year, month


def load_temporal_data():
    """Tải và tổng hợp dữ liệu đánh giá theo tháng/năm từ SQLite."""
    print("⏳ Đang truy vấn và trích xuất thời gian từ SQLite...")
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT visit_date, count(*) as count
        FROM reviews
        WHERE visit_date IS NOT NULL AND length(trim(visit_date)) > 0
        GROUP BY visit_date
    """
    df = pd.read_sql(query, conn)
    conn.close()

    parsed = []
    for _, row in df.iterrows():
        y, m = parse_visit_date(row['visit_date'])
        if y and m:
            parsed.append({'year': y, 'month': m, 'count': row['count']})

    pdf = pd.DataFrame(parsed)
    agg = pdf.groupby(['year', 'month'])['count'].sum().reset_index()

    # Lọc phạm vi trọng tâm: 2015 - 2026
    agg = agg[(agg['year'] >= 2015) & (agg['year'] <= 2026)].copy()
    agg['date'] = pd.to_datetime(agg.apply(lambda r: f"{int(r['year'])}-{int(r['month']):02d}-01", axis=1))
    agg = agg.sort_values('date').reset_index(drop=True)
    return agg


def plot_temporal_analysis():
    print("=" * 80)
    print("📈 TRỰC QUAN HÓA CHUỖI THỜI GIAN & MÙA VỤ DU LỊCH VIỆT NAM (2015 - 2026)")
    print("=" * 80)

    df_time = load_temporal_data()

    # 1. Thống kê theo năm
    yearly = df_time.groupby('year')['count'].sum()
    print("\n📋 BẢNG THỐNG KÊ LƯỢNG BÀI ĐÁNH GIÁ THEO NĂM (2015 - 2026):")
    for y, c in yearly.items():
        note = ""
        if y == 2019:
            note = "<- Đỉnh cao trước đại dịch"
        elif y in [2020, 2021]:
            note = "<- Giai đoạn khủng hoảng COVID-19"
        elif y == 2022:
            note = "<- Bắt đầu mở cửa & phục hồi"
        elif y >= 2024:
            note = "<- Bùng nổ vượt đỉnh lịch sử"
        print(f"  • Năm {y}: {c:>9,} bài review  {note}")

    # Khởi tạo Figure 3 panel chuẩn ấn phẩm
    fig = plt.figure(figsize=(16, 12), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    gs = fig.add_gridspec(2, 2, height_ratios=[1.2, 1.0], hspace=0.32, wspace=0.22)

    # --------------------------------------------------------------------------
    # PANEL 1 (TOP): CHUỖI THỜI GIAN THEO THÁNG (2015 - 2026)
    # --------------------------------------------------------------------------
    ax1 = fig.add_subplot(gs[0, :])
    ax1.set_facecolor('#FAFAFA')

    # Vẽ đường xu hướng và diện tích (Line & Area)
    ax1.plot(df_time['date'], df_time['count'], color='#1D3557', linewidth=2.2, label='Số lượng bài review / tháng', zorder=4)
    ax1.fill_between(df_time['date'], df_time['count'], color='#457B9D', alpha=0.25, zorder=3)

    # Đánh dấu vùng bóng thời kỳ COVID-19 (Tháng 02/2020 đến Tháng 03/2022)
    covid_start = pd.to_datetime('2020-02-01')
    covid_end = pd.to_datetime('2022-03-15')
    ax1.axvspan(covid_start, covid_end, color='#E63946', alpha=0.14, label='Giai đoạn Đại dịch COVID-19 & Phong tỏa', zorder=2)

    # Các điểm Annotations quan trọng
    # 1. Đỉnh 2019
    max_2019_row = df_time[df_time['year'] == 2019].sort_values('count', ascending=False).iloc[0]
    ax1.annotate('Đỉnh cao trước dịch (T5/2019)\n10,179 bài/tháng',
                 xy=(max_2019_row['date'], max_2019_row['count']),
                 xytext=(pd.to_datetime('2017-06-01'), 16000),
                 arrowprops=dict(arrowstyle='->', color='#1D3557', lw=1.5),
                 fontsize=10, fontweight='bold', color='#1D3557',
                 bbox=dict(boxstyle='round,pad=0.4', facecolor='#F1FAEE', edgecolor='#1D3557', alpha=0.9))

    # 2. Đáy dịch 2021
    min_covid_row = df_time[(df_time['year'] == 2021) & (df_time['month'] == 8)].iloc[0]
    ax1.annotate('Chạm đáy đóng băng\n(T8/2021: 82 bài)',
                 xy=(min_covid_row['date'], min_covid_row['count']),
                 xytext=(pd.to_datetime('2020-07-01'), 8500),
                 arrowprops=dict(arrowstyle='->', color='#E63946', lw=1.5),
                 fontsize=9.5, fontweight='bold', color='#E63946',
                 bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFE3E3', edgecolor='#E63946', alpha=0.9))

    # 3. Mở cửa 15/03/2022
    reopen_date = pd.to_datetime('2022-03-15')
    ax1.axvline(reopen_date, color='#2A9D8F', linestyle='--', linewidth=1.8, zorder=5)
    ax1.text(reopen_date + pd.Timedelta(days=25), 17000, '15/03/2022: Việt Nam mở cửa\ndu lịch toàn diện',
             fontsize=9.5, fontweight='bold', color='#2A9D8F',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#E8F8F5', edgecolor='#2A9D8F', alpha=0.9))

    # 4. Kỷ lục 2025 - 2026
    max_all = df_time.sort_values('count', ascending=False).iloc[0]
    ax1.annotate(f'Kỷ lục phục hồi ({max_all["month"]}/{max_all["year"]})\n{max_all["count"]:,} bài/tháng',
                 xy=(max_all['date'], max_all['count']),
                 xytext=(pd.to_datetime('2023-04-01'), 20500),
                 arrowprops=dict(arrowstyle='->', color='#E76F51', lw=1.5),
                 fontsize=10, fontweight='bold', color='#E76F51',
                 bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFF3EE', edgecolor='#E76F51', alpha=0.9))

    # Định dạng trục
    ax1.xaxis.set_major_locator(mdates.YearLocator(1))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax1.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
    ax1.set_ylabel("Số lượng bài review / tháng", fontsize=11, fontweight='bold', color='#2B2D42')
    ax1.set_ylim(0, 23500)
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend(loc='upper left', frameon=True, facecolor='white', edgecolor='#CCC', fontsize=10)

    ax1.set_title("A. XU HƯỚNG TỔNG LƯỢNG BÀI ĐÁNH GIÁ DU LỊCH THEO THỜI GIAN (2015 - 2026)\n"
                 "(Thể hiện rõ nét giai đoạn sụt giảm sâu do COVID-19 và đà phục hồi bùng nổ kỷ lục)",
                 fontsize=12.5, fontweight='bold', color='#1D3557', pad=14, loc='left')

    # --------------------------------------------------------------------------
    # PANEL 2 (BOTTOM-LEFT): PHÂN TÍCH QUY LUẬT MÙA VỤ (SEASONALITY BY MONTH)
    # --------------------------------------------------------------------------
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_facecolor('#FAFAFA')

    monthly_stats = df_time.groupby('month')['count'].sum().reset_index()
    month_names = ['T1\n(Tết)', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7\n(Hè)', 'T8\n(Hè)', 'T9', 'T10', 'T11', 'T12\n(Noel)']

    # Phối màu cột: Nhấn mạnh tháng cao điểm
    bar_colors = []
    for m in monthly_stats['month']:
        if m in [1, 2, 3, 4]:          # Mùa Tết & Mùa Xuân du lịch quốc tế
            bar_colors.append('#E76F51')
        elif m in [7, 8]:              # Mùa Hè nội địa
            bar_colors.append('#2A9D8F')
        else:
            bar_colors.append('#457B9D')

    bars = ax2.bar(monthly_stats['month'], monthly_stats['count'], color=bar_colors, width=0.68, edgecolor='white', linewidth=1.2)

    # Ghi nhãn số lượng trên đỉnh cột
    for bar in bars:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., h + 2000, f"{int(h/1000):,}k",
                 ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#1D3557')

    ax2.set_xticks(range(1, 13))
    ax2.set_xticklabels(month_names, fontsize=9.5, fontweight='semibold')
    ax2.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
    ax2.set_ylabel("Tổng lượng review tích lũy", fontsize=10.5, fontweight='bold', color='#2B2D42')
    ax2.set_ylim(0, 148000)
    ax2.grid(axis='y', linestyle='--', alpha=0.6)

    ax2.set_title("B. QUY LUẬT MÙA VỤ DU LỊCH THEO 12 THÁNG\n"
                 "(Cam: Mùa Tết & Lễ hội; Xanh ngọc: Mùa hè cao điểm)",
                 fontsize=11.5, fontweight='bold', color='#1D3557', pad=12, loc='left')

    # --------------------------------------------------------------------------
    # PANEL 3 (BOTTOM-RIGHT): MA TRẬN NHIỆT (HEATMAP NĂM x THÁNG)
    # --------------------------------------------------------------------------
    ax3 = fig.add_subplot(gs[1, 1])

    # Tạo Pivot table: Index = Năm, Columns = Tháng
    heatmap_data = df_time.pivot(index='year', columns='month', values='count').fillna(0)
    heatmap_data = heatmap_data.sort_index(ascending=False)  # Năm mới nhất ở trên

    # Vẽ Heatmap bằng Seaborn
    sns.heatmap(heatmap_data, ax=ax3, cmap='YlOrRd', cbar_kws={'label': 'Số lượng bài review / tháng'},
                linewidths=0.5, linecolor='white')

    ax3.set_xlabel("Tháng trong năm", fontsize=10.5, fontweight='bold', color='#2B2D42')
    ax3.set_ylabel("Năm", fontsize=10.5, fontweight='bold', color='#2B2D42')
    ax3.set_xticklabels([f"T{m}" for m in range(1, 13)], fontsize=9)
    ax3.set_yticklabels(heatmap_data.index, fontsize=9, rotation=0)

    ax3.set_title("C. MA TRẬN NHIỆT MẬT ĐỘ ĐÁNH GIÁ (NĂM x THÁNG)\n"
                 "(Thấy rõ vệt đóng băng màu nhạt 2020-2021 và vùng đỏ rực 2023-2026)",
                 fontsize=11.5, fontweight='bold', color='#1D3557', pad=12, loc='left')

    # Tinh chỉnh viền
    for ax in [ax1, ax2]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    plt.suptitle("PHÂN TÍCH CHUỖI THỜI GIAN & QUY LUẬT MÙA VỤ CỦA DU KHÁCH TẠI VIỆT NAM (2015 - 2026)\n"
                 "(Phân tích thám nghiệm trên 1.44 triệu bài đánh giá có thông tin ngày đi thực tế - Khóa luận Tốt nghiệp DS&AI K3)",
                 fontsize=14.5, fontweight='bold', color='#1D3557', y=0.985)

    output_png = os.path.join(OUTPUT_DIR, "temporal_tourism_trends_2015_2026.png")
    output_pdf = os.path.join(OUTPUT_DIR, "temporal_tourism_trends_2015_2026.pdf")

    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    plt.savefig(output_pdf, bbox_inches='tight')
    plt.close()

    print(f"\n✅ ĐÃ XUẤT ẢNH BIỂU ĐỒ CHUỖI THỜI GIAN THÀNH CÔNG:")
    print(f"👉 File PNG (300 DPI): {output_png}")
    print(f"👉 File PDF (Vector) : {output_pdf}")
    print("=" * 80)


if __name__ == "__main__":
    plot_temporal_analysis()
