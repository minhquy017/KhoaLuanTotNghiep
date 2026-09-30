# -*- coding: utf-8 -*-
"""
Script đọc file Word HIỆN TẠI (giữ nguyên toàn bộ nội dung người dùng đã sửa),
chỉ thêm phần: 'CÁC CÂU HỎI NGHIÊN CỨU & THÍ NGHIỆM ĐIỀU TRA DỮ LIỆU BAN ĐẦU'.
"""

import os
import sys
import docx

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def set_table_borders(table, color="D3D3D3"):
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        borders = parse_xml(f'''
            <w:tblBorders {nsdecls("w")}>
                <w:top w:val="single" w:sz="6" w:space="0" w:color="{color}"/>
                <w:bottom w:val="single" w:sz="6" w:space="0" w:color="{color}"/>
                <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>
                <w:insideV w:val="none"/>
                <w:left w:val="none"/>
                <w:right w:val="none"/>
            </w:tblBorders>
        ''')
        tblPr[0].append(borders)

def format_paragraph(p, space_before=2, space_after=4, line_spacing=1.15):
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing

def add_callout_box(doc, title, content_lines, border_color="1B365D", bg_color="F4F6F9"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.rows[0].cells[0]
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=110, bottom=110, left=150, right=150)
    
    tcPr = cell._element.get_or_add_tcPr()
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>
            <w:top w:val="none"/>
            <w:right w:val="none"/>
            <w:bottom w:val="none"/>
        </w:tcBorders>
    ''')
    tcPr.append(borders)

    p0 = cell.paragraphs[0]
    format_paragraph(p0, space_before=0, space_after=2)
    r0 = p0.add_run(f"📌 {title}")
    r0.font.bold = True
    r0.font.color.rgb = RGBColor(27, 54, 93)
    r0.font.size = Pt(10)

    for line in content_lines:
        p = cell.add_paragraph()
        format_paragraph(p, space_before=1, space_after=2)
        r = p.add_run(line)
        r.font.size = Pt(9.5)
        r.font.name = 'Calibri'
    
    p_after = doc.add_paragraph()
    format_paragraph(p_after, space_before=0, space_after=3)


def append_data_experiments(input_path="docs/KHUNG_NGHIEN_CUU_VA_THI_NGHIEM_KHOA_LUAN.docx", output_path=None):
    if output_path is None:
        output_path = input_path

    # Đọc tài liệu hiện tại của người dùng (giữ 100% nội dung đã sửa)
    doc = docx.Document(input_path)

    PRIMARY_COLOR = RGBColor(27, 54, 93)     # Deep Navy
    SECONDARY_COLOR = RGBColor(43, 108, 176) # Slate Blue

    # Thêm trang mới
    doc.add_page_break()

    # Tiêu đề mục mới
    h1 = doc.add_heading(level=1)
    format_paragraph(h1, space_before=10, space_after=3)
    r = h1.add_run("VI. CÁC CÂU HỎI NGHIÊN CỨU & THÍ NGHIỆM ĐIỀU TRA DỮ LIỆU BAN ĐẦU (DATA EXPLORATION)")
    r.font.name = 'Calibri'
    r.font.color.rgb = PRIMARY_COLOR

    p = doc.add_paragraph()
    format_paragraph(p)
    p.add_run(
        "Bên cạnh các bài thí nghiệm đánh giá thuật toán AI ở giai đoạn sau, ngay trên tập dữ liệu "
        "1,4 triệu bài đánh giá và 11.441 địa điểm đã làm sạch, em thiết lập 4 câu hỏi nghiên cứu "
        "để 'điều tra' và khám phá các quy luật thực tế từ dữ liệu. Đây là căn cứ thực nghiệm quan trọng "
        "chứng minh tính cần thiết của đề tài trước khi xây dựng mô hình AI:"
    )

    # --- Câu hỏi 1 ---
    h2 = doc.add_heading(level=2)
    format_paragraph(h2, space_before=8, space_after=2)
    r = h2.add_run("1. Câu hỏi 1: Số sao đánh giá (Rating) có thực sự phản ánh đúng chất lượng từng món ăn hay không?")
    r.font.name = 'Calibri'
    r.font.color.rgb = SECONDARY_COLOR

    p = doc.add_paragraph()
    format_paragraph(p)
    p.add_run("• Vấn đề đặt ra: ").bold = True
    p.add_run(
        "Khi tìm quán ăn, du khách thường chỉ nhìn vào số sao tổng quan (ví dụ 4.5/5★). "
        "Tuy nhiên, liệu quán 4.5 sao có đồng nghĩa là món nào cũng ngon, hay điểm số bị ảnh hưởng bởi không gian, phục vụ? "
        "Ngược lại, có những quán chỉ đạt 3.8 sao vì chỗ ngồi chật, nhưng món đặc sản lại nấu rất xuất sắc?"
    )

    p = doc.add_paragraph()
    format_paragraph(p)
    p.add_run("• Cách làm thí nghiệm trên dữ liệu: ").bold = True
    p.add_run(
        "Đối sánh giữa điểm rating tổng quan của nhà hàng (bảng places) với điểm cảm xúc (sentiment score) "
        "và rating cụ thể của từng món ăn bóc tách được từ review (bảng restaurant_dishes). "
        "Tính hệ số tương quan và tìm các trường hợp 'lệch pha' (outliers)."
    )

    p = doc.add_paragraph()
    format_paragraph(p)
    p.add_run("• Ý nghĩa: ").bold = True
    p.add_run(
        "Chứng minh rằng việc chỉ dựa vào số sao tổng quan là không đủ, khẳng định giá trị thực tế của công đoạn "
        "khai phá thực đơn ngầm mà đề tài đã thực hiện."
    )

    add_callout_box(
        doc,
        "Ví dụ minh họa điều tra",
        [
            "Một quán bún bò nổi tiếng tại bờ Nam TP. Huế có điểm trung bình 3.9★ (do khách chê quán đông, phục vụ chậm vào giờ cao điểm).",
            "Tuy nhiên, khi bóc tách 350 review nhắc tới món 'bún bò giò heo', điểm cảm xúc riêng cho món ăn này đạt tới +0.82 và 4.6★ khen ngợi nước dùng đậm đà.",
            "-> Kết luận dữ liệu: Khai phá thực thể giúp tìm ra 'quán có món ngon thực thụ' mà nếu chỉ lọc theo rating >= 4.5★ thì hệ thống sẽ bỏ sót."
        ]
    )

    # --- Câu hỏi 2 ---
    h2 = doc.add_heading(level=2)
    format_paragraph(h2, space_before=8, space_after=2)
    r = h2.add_run("2. Câu hỏi 2: Mức giá có tương quan với mức độ hài lòng không, hay quán bình dân lại được khen nhiều hơn?")
    r.font.name = 'Calibri'
    r.font.color.rgb = SECONDARY_COLOR

    p = doc.add_paragraph()
    format_paragraph(p)
    p.add_run("• Vấn đề đặt ra: ").bold = True
    p.add_run(
        "TripAdvisor phân loại mức giá nhà hàng theo 4 bậc (từ $ bình dân đến $$$$ cao cấp). "
        "Một giả định phổ biến là quán càng đắt thì chất lượng càng tốt. "
        "Nhưng thực tế ở Việt Nam, nhiều quán ăn vỉa hè, quán gia truyền giá rẻ lại nấu ngon hơn nhà hàng sang trọng — "
        "đặc biệt với ẩm thực đường phố và đặc sản địa phương."
    )

    p = doc.add_paragraph()
    format_paragraph(p)
    p.add_run("• Cách làm thí nghiệm trên dữ liệu: ").bold = True
    p.add_run(
        "Phân nhóm các nhà hàng theo trường price_level ($, $$, $$$, $$$$). "
        "So sánh điểm rating trung bình, điểm cảm xúc của các món ăn bóc tách được "
        "và tỷ lệ review tích cực/tiêu cực ở từng nhóm giá. "
        "Đặc biệt tập trung vào nhóm ẩm thực đặc sản địa phương tại Huế."
    )

    p = doc.add_paragraph()
    format_paragraph(p)
    p.add_run("• Ý nghĩa: ").bold = True
    p.add_run(
        "Nếu kết quả cho thấy quán bình dân có tỷ lệ khen cao hơn về mặt ẩm thực, "
        "thì hệ thống gợi ý lịch trình nên ưu tiên đề xuất theo chất lượng món ăn thực tế "
        "thay vì xếp hạng theo giá tiền — giúp du khách tiết kiệm chi phí mà vẫn ăn ngon."
    )

    # --- Câu hỏi 3 ---
    h2 = doc.add_heading(level=2)
    format_paragraph(h2, space_before=8, space_after=2)
    r = h2.add_run("3. Câu hỏi 3: Loại hình chuyến đi (Gia đình, Cặp đôi, Đi một mình) ảnh hưởng thế nào đến đánh giá?")
    r.font.name = 'Calibri'
    r.font.color.rgb = SECONDARY_COLOR

    p = doc.add_paragraph()
    format_paragraph(p)
    p.add_run("• Vấn đề đặt ra: ").bold = True
    p.add_run(
        "Trong dữ liệu review có trường trip_type (Family, Couples, Friends, Solo). "
        "Nhóm khách gia đình có trẻ nhỏ/người già thường có yêu cầu khắt khe hơn về không gian và khoảng cách di chuyển, "
        "trong khi nhóm đi một mình (Solo) hoặc bạn bè (Friends) linh hoạt hơn."
    )

    p = doc.add_paragraph()
    format_paragraph(p)
    p.add_run("• Cách làm thí nghiệm trên dữ liệu: ").bold = True
    p.add_run(
        "Thống kê điểm rating trung bình, độ dài bài viết review và tỷ lệ phàn nàn về 'khoảng cách xa / mệt mỏi' "
        "chia theo từng nhóm trip_type."
    )

    p = doc.add_paragraph()
    format_paragraph(p)
    p.add_run("• Ý nghĩa: ").bold = True
    p.add_run(
        "Làm căn cứ để thuật toán tối ưu lộ trình (Route Optimizer) áp dụng các ràng buộc khác nhau: "
        "lịch trình cho gia đình phải có bán kính di chuyển hẹp hơn (< 1km) và ít điểm dừng hơn so với khách đi một mình."
    )

    # --- Câu hỏi 4 ---
    h2 = doc.add_heading(level=2)
    format_paragraph(h2, space_before=8, space_after=2)
    r = h2.add_run("4. Câu hỏi 4: Mật độ không gian thực tế tại Huế có tập trung thành các cụm du lịch rõ rệt không?")
    r.font.name = 'Calibri'
    r.font.color.rgb = SECONDARY_COLOR

    p = doc.add_paragraph()
    format_paragraph(p)
    p.add_run("• Vấn đề đặt ra: ").bold = True
    p.add_run(
        "Khi xây dựng Đồ thị Tri thức Không gian (Spatial KG), việc tạo cạnh liên kết NEAR_BY cần một ngưỡng khoảng cách hợp lý. "
        "Nếu chọn bán kính quá nhỏ (ví dụ 500m) thì đồ thị bị rời rạc; nếu chọn quá lớn (ví dụ 5km) thì đồ thị bị quá tải và mất ý nghĩa đi bộ."
    )

    p = doc.add_paragraph()
    format_paragraph(p)
    p.add_run("• Cách làm thí nghiệm trên dữ liệu: ").bold = True
    p.add_run(
        "Tính toán phân bố khoảng cách Haversine giữa tất cả các cặp khách sạn - nhà hàng - điểm tham quan tại TP. Huế. "
        "Vẽ biểu đồ phân bố mật độ khoảng cách (Distance Distribution Histogram) để tìm ra điểm gãy (elbow point) "
        "tối ưu về khoảng cách di chuyển của du khách."
    )

    p = doc.add_paragraph()
    format_paragraph(p)
    p.add_run("• Ý nghĩa: ").bold = True
    p.add_run(
        "Đưa ra bằng chứng khoa học cho việc chọn ngưỡng d <= 1.5 km cho các cạnh NEAR_BY trong Đồ thị tri thức, "
        "thay vì đặt một con số cảm tính."
    )

    # Bảng tóm tắt các câu hỏi điều tra
    tbl = doc.add_table(rows=1, cols=4)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl)

    headers = ["Câu hỏi Điều tra", "Trường dữ liệu sử dụng", "Phương pháp phân tích", "Kết quả / Ứng dụng thực tế"]
    for i, title in enumerate(headers):
        cell = tbl.rows[0].cells[i]
        cell.text = title
        set_cell_background(cell, "1B365D")
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        p = cell.paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
        p.runs[0].font.size = Pt(9.5)

    q_rows = [
        ("CH1: Rating vs. Chất lượng món", "places.rating, restaurant_dishes.avg_rating, sentiment", "Tương quan Pearson, phát hiện ngoại lệ (outliers)", "Chứng minh cần bóc tách món ăn thay vì chỉ nhìn sao quán"),
        ("CH2: Giá cả vs. Hài lòng", "places.price_level, rating, restaurant_dishes.sentiment", "Phân nhóm giá ($–$$$$), so sánh rating và cảm xúc", "Gợi ý theo chất lượng thực tế thay vì theo giá"),
        ("CH3: Loại chuyến đi & Độ hài lòng", "reviews.trip_type, visit_date, rating", "Thống kê mô tả (ANOVA), phân tích chuỗi thời gian mùa vụ", "Đặt ràng buộc bán kính cho thuật toán tối ưu lịch trình"),
        ("CH4: Mật độ không gian & Ngưỡng NEAR_BY", "places.latitude, places.longitude", "Ma trận khoảng cách Haversine, phân bố mật độ", "Cơ sở khoa học chọn ngưỡng d <= 1.5 km cho Đồ thị")
    ]

    for row_idx, r_data in enumerate(q_rows):
        row = tbl.add_row()
        fill = "F7FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(r_data):
            cell = row.cells[c_idx]
            cell.text = val
            set_cell_background(cell, fill)
            set_cell_margins(cell, top=80, bottom=80, left=110, right=110)
            p = cell.paragraphs[0]
            p.runs[0].font.size = Pt(9)
            p.paragraph_format.line_spacing = 1.15

    # Lưu lại tài liệu
    doc.save(output_path)
    print(f"Đã cập nhật thành công vào file: {output_path}")

if __name__ == "__main__":
    in_file = "docs/KHUNG_NGHIEN_CUU_VA_THI_NGHIEM_KHOA_LUAN.docx"
    # Thử lưu trực tiếp hoặc lưu ra bản mới nếu file đang mở
    out_file = in_file
    try:
        append_data_experiments(in_file, out_file)
    except PermissionError:
        out_file = "docs/KHUNG_NGHIEN_CUU_VA_THI_NGHIEM_KHOA_LUAN_CAP_NHAT.docx"
        print(f"File đang mở trong Word, đang lưu sang file mới: {out_file}")
        append_data_experiments(in_file, out_file)
