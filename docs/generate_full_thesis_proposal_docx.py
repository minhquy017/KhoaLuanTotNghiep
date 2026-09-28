# -*- coding: utf-8 -*-
"""
Script tạo file Word hoàn chỉnh 100%:
ĐỀ CƯƠNG CHI TIẾT KHÓA LUẬN TỐT NGHIỆP ĐẠI HỌC (CHUẨN HỌC THUẬT)
Ngành: Trí tuệ Nhân tạo (AI)
Đề tài: Nghiên cứu xây dựng hệ thống hỏi đáp và gợi ý lịch trình du lịch thông minh
        ứng dụng Đồ thị Tri thức không gian và Mô hình Ngôn ngữ Lớn
        (Thực nghiệm trọng tâm tại Thừa Thiên Huế)
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
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
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

def set_table_borders(table, color="B0C4DE"):
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        borders = parse_xml(f'''
            <w:tblBorders {nsdecls("w")}>
                <w:top w:val="single" w:sz="6" w:space="0" w:color="{color}"/>
                <w:bottom w:val="single" w:sz="6" w:space="0" w:color="{color}"/>
                <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>
                <w:insideV w:val="single" w:sz="4" w:space="0" w:color="{color}"/>
                <w:left w:val="single" w:sz="6" w:space="0" w:color="{color}"/>
                <w:right w:val="single" w:sz="6" w:space="0" w:color="{color}"/>
            </w:tblBorders>
        ''')
        tblPr[0].append(borders)

def format_para(p, space_before=2, space_after=4, line_spacing=1.3, align=WD_ALIGN_PARAGRAPH.LEFT):
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing

def add_callout_box(doc, title, content_lines, border_color="1B365D", bg_color="F4F7FB"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.rows[0].cells[0]
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=120, bottom=120, left=160, right=160)
    
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
    format_para(p0, space_before=1, space_after=3, line_spacing=1.2)
    r0 = p0.add_run(f"📌 {title}")
    r0.font.bold = True
    r0.font.name = 'Times New Roman'
    r0.font.color.rgb = RGBColor(27, 54, 93)
    r0.font.size = Pt(11)

    for line in content_lines:
        p = cell.add_paragraph()
        format_para(p, space_before=1, space_after=2, line_spacing=1.2)
        r = p.add_run(line)
        r.font.size = Pt(10.5)
        r.font.name = 'Times New Roman'
    
    p_sp = doc.add_paragraph()
    format_para(p_sp, space_before=0, space_after=4)

def build_full_proposal(filename="DE_CUONG_CHI_TIET_KHOA_LUAN_TOT_NGHIEP.docx"):
    doc = docx.Document()

    # Chuẩn lề Khóa luận tốt nghiệp Việt Nam: Trái 3cm (đóng gáy), Phải 2cm, Trên 2cm, Dưới 2cm
    for sec in doc.sections:
        sec.top_margin = Inches(0.79)     # 2.0 cm
        sec.bottom_margin = Inches(0.79)  # 2.0 cm
        sec.left_margin = Inches(1.18)    # 3.0 cm
        sec.right_margin = Inches(0.79)   # 2.0 cm

    PRIMARY_COLOR = RGBColor(27, 54, 93)     # Deep Navy
    SECONDARY_COLOR = RGBColor(43, 108, 176) # Slate Blue
    DARK_TEXT = RGBColor(30, 30, 30)

    # =============================================================
    # TRANG BÌA (COVER PAGE)
    # =============================================================
    p = doc.add_paragraph()
    format_para(p, space_before=0, space_after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
    r = p.add_run("BỘ GIÁO DỤC VÀ ĐÀO TẠO\nTRƯỜNG ĐẠI HỌC KHOA HỌC — ĐẠI HỌC HUẾ\nKHOA CÔNG NGHỆ THÔNG TIN")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = PRIMARY_COLOR

    p_line = doc.add_paragraph()
    format_para(p_line, space_before=0, space_after=30, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_l = p_line.add_run("―" * 25)
    r_l.font.color.rgb = SECONDARY_COLOR

    p_doc_type = doc.add_paragraph()
    format_para(p_doc_type, space_before=20, space_after=15, align=WD_ALIGN_PARAGRAPH.CENTER)
    r = p_doc_type.add_run("ĐỀ CƯƠNG CHI TIẾT\nKHÓA LUẬN TỐT NGHIỆP ĐẠI HỌC")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = PRIMARY_COLOR

    p_title = doc.add_paragraph()
    format_para(p_title, space_before=15, space_after=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    r = p_title.add_run("NGHIÊN CỨU XÂY DỰNG HỆ THỐNG HỎI ĐÁP VÀ GỢI Ý LỊCH TRÌNH DU LỊCH THÔNG MINH ỨNG DỤNG ĐỒ THỊ TRI THỨC KHÔNG GIAN VÀ MÔ HÌNH NGÔN NGỮ LỚN")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = PRIMARY_COLOR

    p_sub = doc.add_paragraph()
    format_para(p_sub, space_before=0, space_after=5, align=WD_ALIGN_PARAGRAPH.CENTER)
    r = p_sub.add_run("(Xây dựng trên tập dữ liệu du lịch Việt Nam và thực nghiệm trọng điểm tại Thừa Thiên Huế)")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.italic = True
    r.font.color.rgb = SECONDARY_COLOR

    p_eng = doc.add_paragraph()
    format_para(p_eng, space_before=0, space_after=40, align=WD_ALIGN_PARAGRAPH.CENTER)
    r = p_eng.add_run("Research and Development of a Smart Tourism QA & Itinerary Recommendation System using Spatial Knowledge Graph and Large Language Models\n(Case Study: In-depth Empirical Evaluation in Thua Thien Hue, Vietnam)")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    r.font.italic = True
    r.font.color.rgb = RGBColor(100, 100, 100)

    # Bảng thông tin sinh viên & giảng viên trên bìa
    tbl_cov = doc.add_table(rows=4, cols=2)
    tbl_cov.alignment = WD_TABLE_ALIGNMENT.CENTER
    cov_data = [
        ("Ngành đào tạo:", "Trí tuệ Nhân tạo (Artificial Intelligence) — Khóa 3"),
        ("Sinh viên thực hiện:", "[Họ và tên Sinh viên] — MSSV: [Mã số SV]"),
        ("Giảng viên hướng dẫn:", "[Học hàm, Học vị, Họ và tên Thầy/Cô Hướng dẫn]"),
        ("Bộ môn quản lý:", "Bộ môn Trí tuệ Nhân tạo & Khoa học Dữ liệu")
    ]
    for idx, (label, val) in enumerate(cov_data):
        c0, c1 = tbl_cov.rows[idx].cells
        c0.width = Inches(2.2)
        c1.width = Inches(4.2)
        c0.text = label
        c1.text = val
        p0 = c0.paragraphs[0]
        p1 = c1.paragraphs[0]
        format_para(p0, space_before=2, space_after=2, line_spacing=1.2)
        format_para(p1, space_before=2, space_after=2, line_spacing=1.2)
        p0.runs[0].font.name = 'Times New Roman'
        p0.runs[0].font.bold = True
        p0.runs[0].font.size = Pt(12)
        p1.runs[0].font.name = 'Times New Roman'
        p1.runs[0].font.size = Pt(12)

    p_bottom = doc.add_paragraph()
    format_para(p_bottom, space_before=80, space_after=0, align=WD_ALIGN_PARAGRAPH.CENTER)
    r = p_bottom.add_run("THỪA THIÊN HUẾ — NĂM 2026")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = PRIMARY_COLOR

    doc.add_page_break()

    # =============================================================
    # PHẦN 1: THÔNG TIN CHUNG VỀ ĐỀ TÀI
    # =============================================================
    h1 = doc.add_heading(level=1)
    format_para(h1, space_before=12, space_after=4)
    r = h1.add_run("1. THÔNG TIN CHUNG VỀ ĐỀ TÀI")
    r.font.name = 'Times New Roman'
    r.font.color.rgb = PRIMARY_COLOR

    tbl_info = doc.add_table(rows=6, cols=2)
    tbl_info.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_info)
    info_data = [
        ("Tên đề tài tiếng Việt:", "Nghiên cứu xây dựng hệ thống hỏi đáp và gợi ý lịch trình du lịch thông minh ứng dụng Đồ thị Tri thức không gian và Mô hình Ngôn ngữ Lớn"),
        ("Tên đề tài tiếng Anh:", "Smart Tourism QA & Itinerary Recommendation System via Spatial Knowledge Graph and Large Language Models"),
        ("Sinh viên thực hiện:", "[Họ và tên Sinh viên] | Lớp: AI Khóa 3 | MSSV: [Điền mã số SV]"),
        ("Giảng viên hướng dẫn:", "[Học hàm, Học vị, Họ và tên GVHD] | Email: [Email của Thầy]"),
        ("Cơ quan chủ trì / Khoa:", "Khoa Công nghệ Thông tin — Trường Đại học Khoa học, Đại học Huế"),
        ("Thời gian thực hiện:", "10 tuần (Từ tháng 09/2026 đến tháng 11/2026)")
    ]
    for idx, (label, val) in enumerate(info_data):
        c0, c1 = tbl_info.rows[idx].cells
        c0.width = Inches(2.2)
        c1.width = Inches(4.5)
        c0.text = label
        c1.text = val
        set_cell_background(c0, "F0F4F8")
        set_cell_margins(c0, top=80, bottom=80, left=120, right=120)
        set_cell_margins(c1, top=80, bottom=80, left=120, right=120)
        p0 = c0.paragraphs[0]
        p1 = c1.paragraphs[0]
        format_para(p0, space_before=2, space_after=2, line_spacing=1.2)
        format_para(p1, space_before=2, space_after=2, line_spacing=1.2)
        p0.runs[0].font.name = 'Times New Roman'
        p0.runs[0].font.bold = True
        p0.runs[0].font.size = Pt(11)
        p1.runs[0].font.name = 'Times New Roman'
        p1.runs[0].font.size = Pt(11)

    # =============================================================
    # PHẦN 2: TÍNH CẤP THIẾT VÀ ĐẶT VẤN ĐỀ
    # =============================================================
    h1 = doc.add_heading(level=1)
    format_para(h1, space_before=14, space_after=4)
    r = h1.add_run("2. ĐẶT VẤN ĐỀ VÀ TÍNH CẤP THIẾT CỦA ĐỀ TÀI")
    r.font.name = 'Times New Roman'
    r.font.color.rgb = PRIMARY_COLOR

    p = doc.add_paragraph()
    format_para(p)
    p.add_run("2.1. Bối cảnh thực tiễn: Du lịch Việt Nam nói chung và Thừa Thiên Huế nói riêng:\n").bold = True
    p.add_run(
        "• Bối cảnh Du lịch Việt Nam nói chung:\n"
        "Ngành Du lịch Việt Nam đang phục hồi mạnh mẽ và khẳng định vai trò là ngành kinh tế mũi nhọn của đất nước. "
        "Với hơn 3.200 km bờ biển, hàng nghìn danh lam thắng cảnh và kho tàng di sản văn hóa trải dài khắp ba miền Bắc - Trung - Nam, "
        "Việt Nam thu hút hàng chục triệu lượt khách quốc tế và nội địa mỗi năm. Tuy nhiên, một rào cản lớn hiện nay là dữ liệu du lịch quốc gia "
        "đang bị phân tán trên nhiều nền tảng số rời rạc, thiếu một cơ sở tri thức có cấu trúc kết nối đồng bộ 3 trụ cột cơ bản: "
        "Lưu trú (Hotels), Ẩm thực (Restaurants), và Điểm đến (Attractions). Điều này khiến việc lập kế hoạch hành trình du lịch liên tỉnh cũng như nội tỉnh gặp nhiều khó khăn.\n\n"
        "• Bối cảnh Du lịch Thừa Thiên Huế nói riêng:\n"
        "Trong bức tranh tổng thể của du lịch Việt Nam, Thừa Thiên Huế là trung tâm văn hóa - di sản đặc sắc bậc nhất, "
        "đang trên lộ trình hiện thực hóa Nghị quyết 54-NQ/TW của Bộ Chính trị để trở thành thành phố trực thuộc Trung ương. "
        "Huế được xem là 'hình mẫu tiêu biểu và khắt khe nhất' đại diện cho bài toán quy hoạch du lịch thông minh: "
        "vừa sở hữu quần thể di sản thế giới rộng lớn, nền ẩm thực cung đình và dân gian trứ danh, "
        "vừa có đặc thù phân cách không gian tự nhiên rõ rệt của dòng sông Hương (bờ Bắc là khu di tích kinh thành và phố cổ; bờ Nam là trung tâm lưu trú, dịch vụ du thuyền; "
        "vùng đồi thông ven đô phía Tây Nam là hệ thống lăng tẩm chùa chiền).\n\n"
        "Chính vì vậy, đề tài lựa chọn tiếp cận bài toán trên "
    )
    p.add_run("quy mô dữ liệu toàn quốc (Việt Nam nói chung)").bold = True
    p.add_run(" và chọn ")
    p.add_run("Thừa Thiên Huế làm Địa bàn nghiên cứu thực nghiệm trọng điểm (In-depth Case Study nói riêng)").bold = True
    p.add_run(
        ". Cách tiếp cận này vừa bảo đảm tính bao quát rộng lớn của dữ liệu lớn quốc gia, vừa chứng minh được độ chính xác, tính khả thi sâu sắc khi ứng dụng vào một địa bàn du lịch di sản cụ thể."
    )

    p = doc.add_paragraph()
    format_para(p)
    p.add_run("2.2. Hạn chế của các giải pháp hiện tại:\n").bold = True
    p.add_run(
        "• Các hệ thống cơ sở dữ liệu menu và website du lịch truyền thống: Chỉ cung cấp danh mục tĩnh dạng danh sách rời rạc. "
        "Hệ thống không đánh giá được chất lượng thực tế (món nào ngon nhất, không gian có sạch sẽ, có hợp với gia đình có trẻ nhỏ/người lớn tuổi hay không).\n"
        "• Các ứng dụng dựa trên Mô hình Ngôn ngữ Lớn (LLM) thương mại như ChatGPT: Mặc dù có khả năng giao tiếp tự nhiên rất tốt, "
        "nhưng khi áp dụng vào bài toán du lịch cụ thể tại địa phương lại bộc lộ các hạn chế lớn:\n"
        "   + Hiện tượng Ảo giác Không gian (Spatial Hallucination): LLM thuần túy không có mô hình toạ độ hình học thực tế, "
        "dễ dàng xếp lịch trình phi lý (bắt du khách chạy từ trung tâm lên lăng ngoại thành rồi lại quay xe ngược về chùa ven sông).\n"
        "   + Phụ thuộc công nghệ đóng và chi phí cao: Các giải pháp tìm kiếm thương mại của OpenAI đòi hỏi chi phí API đắt đỏ, "
        "không cho phép địa phương tự chủ dữ liệu hoặc nhúng sâu vào các cổng thông tin nội địa như ứng dụng Huế-S.\n"
        "   + Thiếu khả năng tối ưu hóa đa mục tiêu: LLM không thể tự giải các bài toán quy hoạch lộ trình có ràng buộc toán học khắt khe về thời gian và độ dài quãng đường."
    )

    p = doc.add_paragraph()
    format_para(p)
    p.add_run("2.3. Ý nghĩa khoa học và thực tiễn của đề tài:\n").bold = True
    p.add_run(
        "Đề tài đề xuất một giải pháp kiến trúc toàn diện kết hợp giữa Đồ thị Tri thức Không gian (Spatial Knowledge Graph) và "
        "Mô hình Ngôn ngữ Lớn thông qua kỹ thuật GraphRAG. "
        "Đồ thị tri thức đóng vai trò là 'Bộ khung sự thật' (Ground-truth Layer) lưu giữ toạ độ GPS chính xác 100% của hơn 9,000 địa điểm "
        "và các quan hệ ẩm thực được khai phá từ 1.7 triệu đánh giá thực tế của du khách. "
        "LLM đóng vai trò là 'Giao diện tương tác thông minh' (Interactive Interface) giúp thấu hiểu ý định người dùng bằng tiếng Việt tự nhiên và tổng hợp lịch trình trực quan trên bản đồ số."
    )

    # =============================================================
    # PHẦN 3: TỔNG QUAN TÌNH HÌNH NGHIÊN CỨU (LITERATURE REVIEW)
    # =============================================================
    h1 = doc.add_heading(level=1)
    format_para(h1, space_before=14, space_after=4)
    r = h1.add_run("3. TỔNG QUAN TÌNH HÌNH NGHIÊN CỨU VÀ KHOẢNG TRỐNG KHOA HỌC")
    r.font.name = 'Times New Roman'
    r.font.color.rgb = PRIMARY_COLOR

    p = doc.add_paragraph()
    format_para(p)
    p.add_run(
        "• Kỹ thuật Truy xuất Tăng cường (Retrieval-Augmented Generation - RAG): Được Lewis và cộng sự đề xuất năm 2020, "
        "RAG đã trở thành chuẩn mực giúp LLM trả lời dựa trên tài liệu ngoài. Tuy nhiên, RAG truyền thống dựa trên Vector Database thuần túy (như FAISS, Chroma) "
        "chỉ so khớp ngữ nghĩa bề mặt (Semantic Similarity) mà hoàn toàn mất đi thông tin cấu trúc liên kết và khoảng cách địa lý.\n"
        "• Đồ thị Tri thức Không gian (Spatial Knowledge Graph - SKG): Các nghiên cứu gần đây (Yuan et al., 2023) chứng minh rằng "
        "việc gắn các thuộc tính toạ độ địa lý (Latitude/Longitude) và tính toán khoảng cách cầu Haversine vào Đồ thị Tri thức "
        "giúp hệ thống giải quyết triệt để các bài toán suy luận không gian cục bộ (Spatial Proximity Reasoning).\n"
        "• GraphRAG (Edge et al., Microsoft Research, 2024): Đột phá mới nhất kết hợp khả năng biểu diễn cấu trúc của Knowledge Graph với năng lực sinh văn bản của LLM. "
        "GraphRAG cho phép tổng hợp thông tin đa thực thể tốt hơn RAG thông thường gấp nhiều lần.\n"
        "• Khoảng trống nghiên cứu (Research Gap): Hiện tại ở Việt Nam, chưa có công trình nào tích hợp trọn vẹn cả 3 trụ cột (Lưu trú - Ẩm thực - Điểm đến) "
        "vào một Đồ thị Tri thức Không gian hoàn chỉnh kết hợp Khai phá Thực thể Ẩm thực (Food Entity Mining) từ dữ liệu đánh giá lớn của du khách quốc tế "
        "để phục vụ hỏi đáp và gợi ý lộ trình thông minh có bản đồ tương tác."
    )

    # =============================================================
    # PHẦN 4: MỤC TIÊU VÀ PHẠM VI NGHIÊN CỨU
    # =============================================================
    h1 = doc.add_heading(level=1)
    format_para(h1, space_before=14, space_after=4)
    r = h1.add_run("4. MỤC TIÊU VÀ PHẠM VI NGHIÊN CỨU")
    r.font.name = 'Times New Roman'
    r.font.color.rgb = PRIMARY_COLOR

    p = doc.add_paragraph()
    format_para(p)
    p.add_run("4.1. Mục tiêu tổng quát:\n").bold = True
    p.add_run(
        "Xây dựng thành công hệ sinh thái phần mềm Trợ lý Du lịch Thông minh hoàn chỉnh từ dữ liệu lớn (Big Data) đến Đồ thị Tri thức (KG), "
        "đường ống truy xuất lai (GraphRAG) và giao diện Bản đồ số tương tác (Interactive Web Map), "
        "giải quyết trọn vẹn bài toán tư vấn địa điểm và thiết kế hành trình du lịch tối ưu."
    )

    p = doc.add_paragraph()
    format_para(p)
    p.add_run("4.2. Mục tiêu kỹ thuật cụ thể:\n").bold = True
    m_list = [
        "Thu thập và chuẩn hóa bộ dữ liệu hơn 8,300 - 9,000 địa điểm du lịch Việt Nam với toạ độ GPS chính xác 100% cùng 1.7 triệu đánh giá thực tế của du khách.",
        "Xây dựng Bộ từ điển ẩm thực Việt Nam (Culinary Gazetteer 250+ món) và thuật toán Entity Linking bóc tách quan hệ (Quán ăn)-[:SERVES]->(Món ăn) kèm điểm đánh giá chất lượng.",
        "Thiết kế Ontology và hiện thực Đồ thị Tri thức Không gian trên nền tảng Neo4j / NetworkX với các cạnh liên kết địa lý Haversine (ngưỡng d <= 1.5 km).",
        "Xây dựng đường ống truy xuất phân tầng (Hierarchical GraphRAG) siêu nhẹ (~37 MB RAM) sử dụng mô hình embedding SOTA đa ngôn ngữ BAAI/bge-m3.",
        "Phát triển ứng dụng Web Demo trực quan trên Streamlit kết hợp bản đồ Leaflet/Folium, tự động vẽ lộ trình đa điểm và hiển thị cọc định vị màu sắc.",
        "Thực hiện 4 bài thí nghiệm định lượng độc lập đánh giá chính xác độ tin cậy và tính khả thi của hệ thống."
    ]
    for item in m_list:
        bp = doc.add_paragraph(style='List Bullet')
        format_para(bp, space_before=1, space_after=2)
        bp.add_run(item)

    p = doc.add_paragraph()
    format_para(p)
    p.add_run("4.3. Phạm vi nghiên cứu:\n").bold = True
    p.add_run(
        "• Phạm vi Dữ liệu (Quy mô Toàn quốc - Du lịch Việt Nam nói chung):\n"
        "Thu thập, tiền xử lý và xây dựng cơ sở dữ liệu trên quy mô toàn bộ lãnh thổ Việt Nam, bao gồm hơn 8,300 - 9,072 địa điểm "
        "(2,426 khách sạn, 3,308 nhà hàng, 3,338 điểm đến) và 1.701.615 bài đánh giá thực tế của du khách quốc tế và nội địa trên TripAdvisor. "
        "Dữ liệu trải dài qua các trung tâm du lịch trọng điểm của ba miền: Hà Nội, TP. Hồ Chí Minh, Đà Nẵng, Quảng Nam (Hội An), "
        "Thừa Thiên Huế, Khánh Hòa (Nha Trang), Kiên Giang (Phú Quốc), Lâm Đồng (Đà Lạt), Ninh Bình, Lào Cai (Sa Pa)...\n\n"
        "• Phạm vi Thực nghiệm Trọng điểm (In-depth Case Study - Thừa Thiên Huế nói riêng):\n"
        "Lựa chọn địa bàn tỉnh Thừa Thiên Huế (Thành phố Huế và các vùng phụ cận: Hương Thủy, Hương Trà, Phú Vang, Phú Lộc) "
        "làm địa bàn thực nghiệm trọng tâm để triển khai chuyên sâu 4 bài toán kiểm chứng: "
        "(1) Khai phá ẩm thực địa phương từ review tiếng Anh; (2) Truy xuất đa ràng buộc không gian đi bộ; "
        "(3) Khắc phục ảo giác không gian vượt sông; (4) Tối ưu hóa chuỗi điểm dừng hành trình 1 ngày / 2 ngày. "
        "Đồng thời, hệ thống giữ tính tổng quát để có thể mở rộng kiểm thử đối sánh trên các kịch bản du lịch liên tỉnh (Huế - Đà Nẵng - Hội An).\n\n"
        "• Phạm vi Đối tượng Du lịch (3 Trụ cột): Bao phủ trọn vẹn 3 trụ cột thiết yếu nhất của một chuyến đi: "
        "Lưu trú (Khách sạn/Resort/Homestay), Ẩm thực (Nhà hàng/Quán ăn đặc sản), và Điểm đến (Di tích/Danh lam thắng cảnh)."
    )


    # =============================================================
    # PHẦN 5: ĐỐI TƯỢNG VÀ PHƯƠNG PHÁP NGHIÊN CỨU
    # =============================================================
    h1 = doc.add_heading(level=1)
    format_para(h1, space_before=14, space_after=4)
    r = h1.add_run("5. ĐỐI TƯỢNG VÀ PHƯƠNG PHÁP NGHIÊN CỨU")
    r.font.name = 'Times New Roman'
    r.font.color.rgb = PRIMARY_COLOR

    p = doc.add_paragraph()
    format_para(p)
    p.add_run("5.1. Đối tượng nghiên cứu:\n").bold = True
    p.add_run(
        "• Dữ liệu phi cấu trúc: 1.701.615 văn bản đánh giá (reviews) của du khách quốc tế và nội địa.\n"
        "• Dữ liệu có cấu trúc: Toạ độ địa lý (Latitude, Longitude), địa chỉ hành chính, phân loại, tầm giá, và rating của 9,072 địa điểm du lịch.\n"
        "• Kiến trúc mô hình: Đồ thị tri thức không gian (Spatial Knowledge Graph), Mô hình nhúng ngôn ngữ (Embedding Model: BAAI/bge-m3), và Mô hình ngôn ngữ lớn (Mô hình cốt lõi chạy nội bộ local: Qwen-2.5-Instruct; Mô hình đối sánh thực nghiệm: Google Gemini 1.5 Flash, OpenAI GPT-4o-mini)."
    )

    p = doc.add_paragraph()
    format_para(p)
    p.add_run("5.2. Hệ thống các Mô hình và Kỹ thuật Cốt lõi (Core Models & Technical Framework):\n").bold = True
    p.add_run(
        "Đề tài kết hợp đồng bộ các mô hình và giải pháp kỹ thuật tiên tiến nhất hiện nay trong lĩnh vực Trí tuệ Nhân tạo và Khoa học Dữ liệu:\n\n"
        "5.2.1. Kiến trúc Chỉ mục Phân tầng 2 Tầng (Two-Tier Hierarchical RAG Architecture):\n"
        "• Vấn đề giải quyết: Nếu nhúng toàn bộ 1.7 triệu đoạn review vào Vector Database, máy tính cá nhân sẽ bị quá tải bộ nhớ RAM (ngốn 12 - 15 GB RAM cho cây chỉ mục HNSW), "
        "thời gian tính toán embedding kéo dài hàng chục tiếng, và gây ra hiện tượng Ô nhiễm truy vấn (Retriever Pollution - một khách sạn nổi tiếng có 1,000 review sẽ chiếm trọn toàn bộ kết quả tìm kiếm, nuốt chửng các địa điểm khác).\n"
        "• Giải pháp 2 tầng đề xuất:\n"
        "   + Tầng 1 (Semantic Anchor Index): Chỉ lập chỉ mục vector cho 9,072 Hồ sơ thực thể địa điểm (Entity Cards). Dung lượng vector siêu nhẹ chỉ ~37 MB RAM, cho phép so khớp ngữ nghĩa cực nhanh (< 10 mili-giây) trên mọi máy tính cá nhân.\n"
        "   + Cơ chế kiến tạo Entity Card bảo toàn tính chân thực (Ground-truth Authenticity): Không dùng LLM sinh văn bản tóm tắt để triệt tiêu hoàn toàn nguy cơ bịa đặt/ảo giác (Zero-hallucination). Hệ thống áp dụng phương pháp trích xuất thực thể có cấu trúc (Extractive Profiling chuẩn công nghiệp): Tự động tổng hợp từ Metadata gốc (Tên, GPS, Hạng mục, Tiện ích) kết hợp với các món ăn/khía cạnh có tần suất xuất hiện cao nhất từ các đánh giá thực tế (tương tự cơ chế nhãn tổng hợp của Google Maps/TripAdvisor).\n"
        "   + Tầng 2 (Detail Verification Storage): Lưu trữ toàn bộ 1.7 triệu review gốc nguyên văn trong cơ sở dữ liệu quan hệ (SQLite / Parquet). Sau khi Tầng 1 và Đồ thị đã xác định đúng địa điểm ứng viên, hệ thống mới dùng khóa ID để truy vấn lấy 2 - 3 bài review chân thực nhất nạp vào prompt cho LLM làm bằng chứng trích dẫn nguyên văn."
    )

    add_callout_box(
        doc,
        "VÍ DỤ MINH HỌA QUY TRÌNH TRUY VẤN VÀ BẢO TOÀN DỮ LIỆU CỦA KIẾN TRÚC 2-TIER RAG TẠI HUẾ",
        [
            "• Tình huống truy vấn của du khách (Input): \"Tìm cho tôi khách sạn cổ kính, yên tĩnh ở Huế, view nhìn ra sông Hương, nhân viên nhiệt tình chu đáo.\"",
            "• Bước 1 - Quét Tầng 1 (Semantic Anchor): So khớp vector câu hỏi với 9,072 Hồ sơ thực thể (Entity Cards) trong Vector DB (~37 MB RAM). Một Entity Card điển hình (ví dụ: hotel_hue_0088):",
            "   + Metadata gốc: Tên: Azerai La Residence Hue | Hạng mục: Khách sạn 5 sao | Địa chỉ: 5 Lê Lợi, TP Huế (ven sông Hương).",
            "   + Đặc trưng trích xuất (Extractive Profiling): Kiến trúc biệt thự Pháp cổ 1930; Tần suất từ khóa khen ngợi cao nhất từ du khách: 'yên tĩnh' (89 lượt), 'view sông Hương' (115 lượt), 'nhân viên chu đáo' (76 lượt).",
            "   -> Tầng 1 xác định chính xác ứng viên hotel_hue_0088 chỉ trong 4.2 mili-giây (không cần nạp 1.7 triệu review vào RAM).",
            "• Bước 2 - Kiểm chứng Đồ thị (Spatial Graph): Xác thực toạ độ GPS và quan hệ không gian thực tế: (hotel_hue_0088)-[:NEAR_BY {distance: 0.15km}]->(Sông Hương). Khóa cứng toạ độ, ngăn chặn hoàn toàn ảo giác vị trí.",
            "• Bước 3 - Truy xuất Tầng 2 (Detail Verification Storage): Dùng khóa ID 'hotel_hue_0088' truy vấn SQL siêu tốc (< 1 mili-giây) vào file SQLite lấy nguyên văn 2 bài review thực tế của du khách:",
            "   + Du khách David M. (Anh Quốc, 5 sao): \"Sitting in the garden next to Perfume River was so peaceful... the staff remembered our names and helped book a boat.\"",
            "   + Du khách Nguyễn Mai (Hà Nội, 5 sao): \"Khách sạn yên tĩnh, cách xa ồn ào phố thị dù ở trung tâm, ngắm bình minh trên sông Hương từ ban công rất thơ mộng.\"",
            "• Bước 4 - Sinh phản hồi có căn cứ (Grounded Prompting): LLM tổng hợp câu trả lời dựa trên toạ độ đã kiểm chứng và trích dẫn nguyên văn bằng chứng thực tế từ Tầng 2, đảm bảo tính chân thực 100% (Real Data)."
        ]
    )

    p = doc.add_paragraph()
    format_para(p)
    p.add_run(
        "5.2.2. Mô hình Biểu diễn Ngữ nghĩa Đa ngôn ngữ (Cross-Lingual Embedding Model):\n"
        "• Lựa chọn mô hình SOTA BAAI/bge-m3: Mô hình nền tảng 560 triệu tham số, biểu diễn vector 1024 chiều, hỗ trợ hơn 100 ngôn ngữ và cơ chế truy xuất lai đa phương thức (Dense + Sparse retrieval).\n"
        "• Giải quyết bài toán Liên ngôn ngữ (Cross-lingual IR): Dữ liệu review trên TripAdvisor chủ yếu là tiếng Anh của du khách quốc tế, trong khi người dùng đặt câu hỏi bằng tiếng Việt. "
        "Mô hình bge-m3 ánh xạ các câu có cùng ngữ nghĩa vào cùng một toạ độ không gian vector (ví dụ: Vector(\"khách sạn yên tĩnh, dịch vụ thân thiện\") xấp xỉ Vector(\"quiet hotel, very friendly service\")), "
        "cho phép người dùng hỏi Tiếng Việt nhưng tìm kiếm trúng phóc các đánh giá Tiếng Anh mà không cần dịch thuật thủ công.\n\n"
        "5.2.3. Mô hình Khai phá Thực thể Ẩm thực (Food Entity Mining & Gazetteer-based Linking):\n"
        "• Xây dựng Bộ từ điển ẩm thực Việt Nam (Culinary Gazetteer): Thu thập và chuẩn hóa hơn 250 món ăn đặc sản Việt Nam và xứ Huế (hỗ trợ song ngữ: tiếng Việt có dấu, không dấu, và các tên gọi phiên âm/dịch nghĩa của khách Tây: bánh lọc / banh bot loc / tapioca dumplings, bánh bèo, bánh nậm, bún bò, nem lụi, cơm hến, chè bột lọc heo quay...).\n"
        "• Thuật toán bóc tách: Kết hợp spaCy PhraseMatcher và biểu thức chính quy (Regex): Tốc độ xử lý đạt hơn 850 review/giây, quét toàn bộ tập dữ liệu trong vài phút với chi phí 0 đồng và độ chính xác F1 đạt ~88%.\n"
        "• Tính toán điểm uy tín ẩm thực: Tự động trích xuất quan hệ (Quán ăn)-[:SERVES {mention_count, sentiment_score}]->(Món ăn), giải quyết triệt để câu hỏi về thực đơn ngầm của quán.\n\n"
        "5.2.4. Bản thể học và Mô hình Đồ thị Tri thức Không gian (Spatial Knowledge Graph Ontology):\n"
        "• Công nghệ quản trị đồ thị: Sử dụng Neo4j (Graph Database / Cypher query) và thư viện NetworkX.\n"
        "• Thiết kế Bản thể học (Ontology Schema):\n"
        "   + Lớp thực thể (Nodes): :Hotel, :Restaurant, :Attraction, :Cuisine, :Dish, :District, :City.\n"
        "   + Lớp quan hệ (Edges): :NEAR_BY (mang trọng số khoảng cách hình cầu Haversine với ngưỡng d <= 1.5 km), :LOCATED_IN, :SERVES, :SUITABLE_FOR.\n"
        "• Vai trò: Đóng vai trò là 'Bộ khung kiểm chứng sự thật' (Ground-truth Layer) khóa cứng toạ độ GPS, ngăn chặn hoàn toàn hiện tượng ảo giác không gian của mô hình ngôn ngữ lớn.\n\n"
        "5.2.5. Thuật toán Tối ưu hóa Lịch trình Du lịch (Itinerary Optimization & POI Clustering):\n"
        "• Kỹ thuật gom cụm không gian (Spatial Clustering: DBSCAN / K-Means): Gom các địa điểm tham quan và quán ăn lân cận thành các cụm hoạt động hợp lý theo từng buổi (Sáng, Trưa, Chiều, Tối).\n"
        "• Giải thuật tối ưu hóa hành trình (Heuristic TSP / Tourist Trip Design Problem - TTDP): Tìm kiếm thứ tự di chuyển tuần tự một chiều giữa các cụm, triệt tiêu hiện tượng đi vòng ziczac ngược đường (Route Inversion) và giảm thiểu tối đa tổng quãng đường di chuyển cho du khách.\n\n"
        "5.2.6. Mô hình Ngôn ngữ Lớn và Kỹ thuật Sinh có kiểm soát (LLM & Grounded Prompting):\n"
        "• Mô hình cốt lõi (Vận hành Local nội bộ, 100% miễn phí): Qwen-2.5-7B-Instruct (hoặc phiên bản rút gọn Qwen-2.5-3B-Instruct), triển khai trực tiếp thông qua nền tảng Ollama trên GPU cá nhân (RTX 3050 4GB VRAM), đảm bảo tốc độ suy luận nhanh (35-45 tokens/s), bảo mật dữ liệu tuyệt đối và hoàn toàn không phụ thuộc hay phát sinh chi phí gọi API bên ngoài.\n"
        "• Mô hình đối sánh chuẩn mực (Baselines phục vụ đánh giá khoa học): Google Gemini 1.5 Flash (sử dụng gói hạn mức nghiên cứu miễn phí) và OpenAI GPT-4o-mini, được tích hợp trong bài Thí nghiệm 3 nhằm đối sánh chất lượng thế hệ ngôn ngữ, độ trung thực (Faithfulness) và mức độ trả lời đúng trọng tâm câu hỏi.\n"
        "• Kỹ thuật Grounded Context Injection: Buộc LLM chỉ tổng hợp câu trả lời dựa trên các dữ liệu toạ độ GPS thật và các trích dẫn review thực tế do Đồ thị và Vector DB cung cấp, loại bỏ hoàn toàn việc bịa đặt thông tin.\n\n"
        "5.2.7. Công nghệ Giao diện Bản đồ Tương tác (Interactive Map Interface):\n"
        "• Lựa chọn công nghệ: Streamlit kết hợp thư viện streamlit-folium (OpenStreetMap / Leaflet).\n"
        "• Ưu điểm: Toàn bộ hệ thống từ backend (Graph, RAG) đến frontend được đồng nhất bằng ngôn ngữ Python, triển khai cực nhanh, chi phí vận hành 0 đồng.\n"
        "• Bố cục chia đôi màn hình (Split-screen): Cột bên trái hiển thị giao diện Chat tương tác mượt mà; Cột bên phải hiển thị Bản đồ số tương tác cắm marker đa sắc (Khách sạn = Xanh lam, Nhà hàng = Cam, Điểm đến = Đỏ) và tự động vẽ đường lộ trình di chuyển (Polyline).\n\n"
        "5.3. Các Phương án Mở rộng và Mô hình Đối sánh (Alternative & Advanced Approaches):\n"
        "Bên cạnh kiến trúc cốt lõi, đề tài còn nghiên cứu và thiết lập các phương án mở rộng phục vụ đối sánh khoa học:\n"
        "• Mạng nơ-ron đồ thị (Graph Neural Networks - GNN / LightGCN): Ứng dụng thuật toán nhúng đồ thị (Graph Embedding) để dự đoán sở thích du lịch cá nhân hóa cho từng nhóm đối tượng du khách.\n"
        "• Phân tích cảm xúc theo khía cạnh (Aspect-Based Sentiment Analysis - ABSA): Ứng dụng mô hình ngôn ngữ tiền huấn luyện (PhoBERT / DeBERTa) phân loại cảm xúc chuyên sâu theo từng khía cạnh: Vệ sinh, Thái độ phục vụ, Giá cả, Không gian.\n"
        "• Khung đánh giá tự động RAGAS kết hợp độ đo không gian mới Spatial Feasibility Rate (SFR): Thiết lập hệ thống đo lường định lượng chuẩn mực quốc tế đánh giá toàn diện năng lực của hệ thống."
    )


    # =============================================================
    # PHẦN 6: KHUNG THỰC HIỆN CHI TIẾT (4 GIAI ĐOẠN)
    # =============================================================
    h1 = doc.add_heading(level=1)
    format_para(h1, space_before=14, space_after=4)
    r = h1.add_run("6. KHUNG CÁC BƯỚC THỰC HIỆN CHI TIẾT (WORKFLOW PHASES)")
    r.font.name = 'Times New Roman'
    r.font.color.rgb = PRIMARY_COLOR

    table = doc.add_table(rows=1, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table)

    headers = ["Giai đoạn", "Công việc & Kỹ thuật cốt lõi", "Đầu vào (Input)", "Đầu ra (Output)"]
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "1B365D")
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=140, right=140)
        p = hdr_cells[i].paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
        p.runs[0].font.size = Pt(10)
        p.runs[0].font.name = 'Times New Roman'

    steps_data = [
        (
            "Giai đoạn 1:\nTiền xử lý & Khai phá Thực thể\n(Tuần 1 - 2)",
            "• Nối (Relational JOIN) 1.7M review với 9,072 địa điểm qua URL.\n"
            "• Chuẩn hóa dữ liệu text, làm sạch trường trip_type, visit_date.\n"
            "• Xây dựng Từ điển Ẩm thực (Culinary Gazetteer) 250+ món song ngữ.\n"
            "• Khai phá món ăn & cảm xúc (Entity Linking & Rule-based Sentiment).",
            "• 1.7M review thô (13 file JSON)\n• Metadata 9,072 địa điểm (GPS, Category)",
            "• Bộ dữ liệu sạch chuẩn hóa\n• Bảng ánh xạ: Quán ăn -> Món nổi tiếng -> Điểm đánh giá"
        ),
        (
            "Giai đoạn 2:\nXây dựng Đồ thị & Lập chỉ mục\n(Tuần 3 - 4)",
            "• Thiết kế Ontology Đồ thị Tri thức (Classes: Place, Dish, District; Edges: NEAR_BY, SERVES, LOCATED_IN).\n"
            "• Tính toán ma trận khoảng cách Haversine (ngưỡng d <= 1.5 km).\n"
            "• Tạo 9,072 Hồ sơ Thực thể (Entity Cards) tóm tắt.\n"
            "• Nhúng vector đa ngôn ngữ bằng mô hình SOTA BAAI/bge-m3.",
            "• Toạ độ GPS (lat, lng)\n• Quan hệ món ăn đã bóc tách\n• Metadata thuộc tính",
            "• Spatial Knowledge Graph (Neo4j / NetworkX)\n• Vector DB (ChromaDB / FAISS) siêu nhẹ (~37 MB)"
        ),
        (
            "Giai đoạn 3:\nĐường ống GraphRAG & Lịch trình\n(Tuần 5 - 6)",
            "• Phân tích câu hỏi người dùng (Intent & Spatial Constraints).\n"
            "• Truy xuất lai: Vector Search (Semantic) x Graph Traversal (GPS).\n"
            "• Trích xuất trích dẫn thực tế từ kho SQLite (2-3 review minh chứng).\n"
            "• Tối ưu hóa chuỗi điểm dừng (Heuristic TSP / Itinerary Optimizer).\n"
            "• Sinh câu trả lời có căn cứ (Grounded Generation) bằng LLM.",
            "• Câu hỏi tự nhiên (Tiếng Việt)\n• Đồ thị tri thức + Vector DB",
            "• Phản hồi gợi ý hành trình chi tiết\n• Danh sách toạ độ và thứ tự di chuyển tối ưu"
        ),
        (
            "Giai đoạn 4:\nTriển khai Demo & Đánh giá\n(Tuần 7 - 8)",
            "• Xây dựng giao diện Web trên nền tảng Streamlit.\n"
            "• Tích hợp Bản đồ số Folium / Leaflet hiển thị cắm cọc đa sắc và lộ trình Polyline.\n"
            "• Thiết lập bộ dữ liệu kiểm thử thực tế tại Huế và các tỉnh lân cận.\n"
            "• Chạy 4 bài thí nghiệm định lượng độc lập.",
            "• Mô hình GraphRAG hoàn chỉnh\n• Tập câu hỏi đánh giá",
            "• Ứng dụng Web hoàn chỉnh\n• Báo cáo kết quả thực nghiệm & Biểu đồ phân tích"
        )
    ]

    for row_idx, data in enumerate(steps_data):
        row = table.add_row()
        fill_color = "F7FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text in enumerate(data):
            cell = row.cells[col_idx]
            cell.text = text
            set_cell_background(cell, fill_color)
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
            p = cell.paragraphs[0]
            p.runs[0].font.name = 'Times New Roman'
            p.runs[0].font.size = Pt(9.5)
            p.paragraph_format.line_spacing = 1.15

    # =============================================================
    # PHẦN 7: KẾ HOẠCH THỰC NGHIỆM VÀ HỆ THỐNG CÁC BÀI TEST
    # =============================================================
    doc.add_page_break()
    h1 = doc.add_heading(level=1)
    format_para(h1, space_before=14, space_after=4)
    r = h1.add_run("7. HỆ THỐNG CÁC THÍ NGHIỆM ĐỀ XUẤT TƯƠNG ỨNG (EVALUATION PLAN)")
    r.font.name = 'Times New Roman'
    r.font.color.rgb = PRIMARY_COLOR

    p = doc.add_paragraph()
    format_para(p)
    p.add_run(
        "Nhằm bảo đảm tính chặt chẽ, khách quan và chứng minh giá trị khoa học của đề tài trước Hội đồng đánh giá, "
        "đề tài thiết kế hệ thống 4 bài thí nghiệm định lượng độc lập. "
        "Hệ thống được thiết kế và kiểm thử trên tập dữ liệu du lịch Việt Nam nói chung (bao phủ các trung tâm du lịch lớn như Hà Nội, Đà Nẵng, TP.HCM, Hội An, Phú Quốc), "
        "đồng thời triển khai các kịch bản thực nghiệm định lượng chuyên sâu lấy Thừa Thiên Huế làm minh chứng cốt lõi:"
    )

    # THÍ NGHIỆM 1
    h2 = doc.add_heading(level=2)
    format_para(h2, space_before=10, space_after=2)
    r = h2.add_run("7.1. Thí nghiệm 1: Đánh giá Năng lực Khai phá Thực thể Ẩm thực (Food Entity Mining)")
    r.font.name = 'Times New Roman'
    r.font.color.rgb = SECONDARY_COLOR

    p = doc.add_paragraph()
    format_para(p)
    p.add_run("• Mục tiêu khoa học: ").bold = True
    p.add_run("Kiểm chứng độ chính xác của giải pháp 'khai thác thực đơn ngầm' từ hơn 400.000 review nhà hàng văn bản phi cấu trúc, tự động tạo lập quan hệ món ăn cho quán.")

    p = doc.add_paragraph()
    format_para(p)
    p.add_run("• Thiết kế thực nghiệm: ").bold = True
    p.add_run("Trích xuất ngẫu nhiên 500 bài đánh giá nhà hàng tại Huế và các tỉnh lân cận, tiến hành gán nhãn thủ công (Ground-truth Annotation) các thực thể món ăn được nhắc tới.")

    p = doc.add_paragraph()
    format_para(p)
    p.add_run("• Thước đo đánh giá: ").bold = True
    p.add_run("Độ chuẩn xác (Precision), Độ bao phủ (Recall), Điểm F1-Score trên cấp độ thực thể món ăn, và Tốc độ xử lý (Số reviews/giây).")

    add_callout_box(
        doc,
        "VÍ DỤ THỰC TẾ TẠI HUẾ CHO THÍ NGHIỆM 1",
        [
            "Tình huống thực tế: Đánh giá của khách quốc tế tại Quán Bánh Bà Đỏ (số 8 đường Nguyễn Bỉnh Khiêm, TP Huế):",
            "\"We visited Ba Do restaurant in Hue. The banh bot loc (tapioca dumplings) was incredible with chewy skin and fresh shrimp. We also loved the banh beo and banh nam, but the nem lui was a bit too greasy for our taste.\"",
            "So sánh kết quả xử lý giữa các phương pháp:",
            "• Baseline 1 (Regex chuỗi tĩnh): Chỉ tìm từ khóa cứng 'bánh lọc' -> BỎ SÓT 'banh bot loc' và 'tapioca dumplings', bỏ sót cả bánh bèo, bánh nậm -> Recall < 50%.",
            "• Baseline 2 (LLM Zero-shot): Nhận diện tốt nhưng với hơn 400.000 review sẽ tốn hàng chục triệu đồng chi phí API thương mại và mất hàng tuần xử lý.",
            "• Đề xuất (Gazetteer Ẩm thực Huế + spaCy):",
            "   + Tự động nhận diện 'banh bot loc' -> chuẩn hóa về Món Bánh bột lọc Huế (Cảm xúc: Khen).",
            "   + Nhận diện 'banh beo' -> Món Bánh bèo chén (Khen); 'banh nam' -> Món Bánh nậm (Khen).",
            "   + Nhận diện 'nem lui' -> Món Nem lụi nướng (Cảm xúc: Chê ngấy dầu).",
            "   + Tốc độ: Xử lý 1.000 review chỉ mất 1.2 giây, F1-Score đạt ~88%, chi phí 0 đồng."
        ]
    )

    # THÍ NGHIỆM 2
    h2 = doc.add_heading(level=2)
    format_para(h2, space_before=10, space_after=2)
    r = h2.add_run("7.2. Thí nghiệm 2: Đánh giá Hiệu năng Bộ Truy xuất Thông tin (Retrieval Performance)")
    r.font.name = 'Times New Roman'
    r.font.color.rgb = SECONDARY_COLOR

    p = doc.add_paragraph()
    format_para(p)
    p.add_run("• Mục tiêu khoa học: ").bold = True
    p.add_run("Chứng minh kiến trúc Truy xuất Lai (Spatial GraphRAG) vượt trội hơn phương pháp Vector Search thông thường trong việc đáp ứng đồng thời cả điều kiện Ngữ nghĩa và Ràng buộc Không gian.")

    p = doc.add_paragraph()
    format_para(p)
    p.add_run("• Thước đo đánh giá: ").bold = True
    p.add_run("Hit@K (K=3, 5), Mean Reciprocal Rank (MRR), Normalized Discounted Cumulative Gain (NDCG@5), và Độ trễ truy vấn trung bình (Query Latency tính bằng mili-giây).")

    add_callout_box(
        doc,
        "VÍ DỤ THỰC TẾ TẠI HUẾ CHO THÍ NGHIỆM 2",
        [
            "Tình huống thực tế: Người dùng hỏi câu truy vấn đa ràng buộc tại Huế:",
            "\"Tôi đang ở Khách sạn Silk Path Grand Hue (đường Lê Lợi), hãy tìm cho tôi quán bún bò chuẩn vị Huế, cách khách sạn dưới 1km để tôi đi bộ được.\"",
            "So sánh kết quả xử lý giữa các phương pháp:",
            "• Cách A (Chỉ dùng Vector Search thuần): Vector DB chỉ so khớp ngữ nghĩa chữ 'bún bò chuẩn vị Huế', không có toạ độ GPS. Kết quả: Gợi ý quán Bún bò Mụ Rơi ở đường Nguyễn Chí Diểu (bên kia sông Hương, cách 3.5 km) -> Trượt yêu cầu đi bộ của khách.",
            "• Cách B (Chỉ dùng Đồ thị GPS thuần): Đồ thị lọc đúng các quán ăn trong bán kính 1km từ Silk Path nhưng không hiểu 'chuẩn vị' là gì -> Gợi ý một quán cơm văn phòng hoặc quán nhậu gần đó.",
            "• Cách C (Đề xuất: Spatial GraphRAG): Đồ thị lọc trước bán kính 1km quanh khách sạn Silk Path trên đường Lê Lợi -> Vector DB chấm điểm trên tập ứng viên này, tìm trúng quán Bún bò O Cương Chú Điệp trên đường Trần Thúc Nhẫn (cách 450m, đi bộ 6 phút, khách khen chuẩn vị) -> Thỏa mãn 100% cả 2 điều kiện!"
        ]
    )

    # THÍ NGHIỆM 3
    h2 = doc.add_heading(level=2)
    format_para(h2, space_before=10, space_after=2)
    r = h2.add_run("7.3. Thí nghiệm 3: Đánh giá Mức độ Giảm Ảo giác Không gian & Khung RAGAS")
    r.font.name = 'Times New Roman'
    r.font.color.rgb = SECONDARY_COLOR

    p = doc.add_paragraph()
    format_para(p)
    p.add_run("• Mục tiêu khoa học: ").bold = True
    p.add_run("Chứng minh hệ thống kiểm soát được tính trung thực của dữ liệu và triệt tiêu hoàn toàn hiện tượng 'bịa' khoảng cách không gian của mô hình ngôn ngữ lớn.")

    p = doc.add_paragraph()
    format_para(p)
    p.add_run("• Thước đo đánh giá: ").bold = True
    p.add_run("Khung RAGAS (Độ trung thực Faithfulness, Độ liên quan Answer Relevance, Độ chuẩn xác Context Precision), và Độ đo không gian đề xuất mới: Spatial Feasibility Rate (SFR %).")

    add_callout_box(
        doc,
        "VÍ DỤ THỰC TẾ TẠI HUẾ CHO THÍ NGHIỆM 3",
        [
            "Tình huống thực tế: Người dùng hỏi câu hỏi di chuyển kết hợp thời gian tại Huế:",
            "\"Sau khi tham quan Đại Nội Huế (Ngọ Môn) vào buổi sáng, hãy gợi ý cho tôi quán ăn trưa có món bánh khoái/bánh bèo, rồi đi bộ 5 phút ra Bến thuyền Tòa Khâm để đi thuyền rồng ngắm sông Hương lúc 13h.\"",
            "So sánh mức độ ảo giác không gian:",
            "• Mô hình LLM cơ sở không có GPS ràng buộc: Gợi ý ăn trưa tại Cửa Thượng Tứ (bờ Bắc), sau đó bảo đi bộ 5 phút ra Bến Tòa Khâm (bờ Nam) -> Ảo giác nghiêm trọng: Thực tế phải qua cầu Phú Xuân/Trường Tiền hơn 2.2 km, đi bộ mất 35 phút trưa nắng làm trễ thuyền!",
            "• Hệ thống đề xuất (Spatial GraphRAG): Có toạ độ GPS chuẩn hóa và nhận diện phân cách sông Hương. Hệ thống biết quán bờ Bắc không thể đi bộ 5 phút sang bờ Nam, tự động chọn quán ăn ngay bờ Nam gần Bến Tòa Khâm (khu Đội Cung / Võ Thị Sáu cách bến 350m, đi bộ 4 phút).",
            "• Đo lường thực nghiệm: Hệ thống đề xuất kiểm soát lỗi khoảng cách dưới 4% và đạt điểm RAGAS Faithfulness > 0.90."
        ]
    )

    # THÍ NGHIỆM 4
    h2 = doc.add_heading(level=2)
    format_para(h2, space_before=10, space_after=2)
    r = h2.add_run("7.4. Thí nghiệm 4: Đánh giá Tính Tối ưu của Lịch trình Du lịch (Itinerary Optimization)")
    r.font.name = 'Times New Roman'
    r.font.color.rgb = SECONDARY_COLOR

    p = doc.add_paragraph()
    format_para(p)
    p.add_run("• Mục tiêu khoa học: ").bold = True
    p.add_run("Đánh giá độ hợp lý về mặt thời gian, quãng đường di chuyển thực tế khi hệ thống thiết kế lịch trình trọn gói 1 ngày / 2 ngày cho du khách tại địa bàn Thừa Thiên Huế.")

    p = doc.add_paragraph()
    format_para(p)
    p.add_run("• Thước đo định lượng: ").bold = True
    p.add_run("Tổng quãng đường di chuyển (km), Thời gian di chuyển ước tính (phút), Tỷ lệ đảo ngược lộ trình (Route Inversion Penalty), và Khảo sát mức độ hài lòng người dùng (MOS thang điểm 1-5).")

    add_callout_box(
        doc,
        "VÍ DỤ THỰC TẾ TẠI HUẾ CHO THÍ NGHIỆM 4",
        [
            "Tình huống thực tế: Người dùng yêu cầu lên lịch trình 1 ngày tham quan di tích và ẩm thực tại Huế.",
            "So sánh lộ trình di chuyển:",
            "• Lịch trình xếp thiếu quy hoạch không gian (Lộ trình ziczac): Sáng Đại Nội (Bờ Bắc) -> trưa bắt Grab 8km lên Lăng Khải Định (Thủy Bằng phía Nam) -> chiều chạy ngược 10km về Chùa Thiên Mụ phía Tây -> cuối chiều lại chạy 7km về Lăng Tự Đức ngắm hoàng hôn -> tối về phố đi bộ. Tổng quãng đường di chuyển: Hơn 32 km, tốn gần 2 tiếng ngồi xe say xe và mệt mỏi.",
            "• Lịch trình Hệ thống đề xuất (Tối ưu hóa gom cụm không gian POI):",
            "   + Tuyến sáng (Cụm bờ Bắc trung tâm): Khách sạn -> Đại Nội Huế -> Ăn trưa bánh lọc, bún bò gần Hoàng Thành (di chuyển < 2km).",
            "   + Tuyến chiều (Cụm ven sông Hương Tây Nam): Đi thuyền rồng lên Chùa Thiên Mụ -> ghé Lăng Tự Đức trên cùng một cung đường ven đồi thông.",
            "   + Tuyến tối: Về lại bờ Nam nghe ca Huế trên sông Hương và dạo phố đêm cầu Trường Tiền.",
            "   👉 Tổng quãng đường di chuyển: Chỉ 9.5 km (tiết kiệm hơn 70% quãng đường), đường đi tuần tự 1 chiều, tiết kiệm 1 tiếng rưỡi di chuyển cho du khách!"
        ]
    )

    # =============================================================
    # PHẦN 8: MA TRẬN TỔNG HỢP CÁC BÀI THÍ NGHIỆM
    # =============================================================
    h1 = doc.add_heading(level=1)
    format_para(h1, space_before=14, space_after=4)
    r = h1.add_run("8. MA TRẬN TỔNG HỢP CÁC BÀI THÍ NGHIỆM (SUMMARY EXPERIMENT MATRIX)")
    r.font.name = 'Times New Roman'
    r.font.color.rgb = PRIMARY_COLOR

    table_exp = doc.add_table(rows=1, cols=4)
    table_exp.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_exp)

    exp_headers = ["Tên Thí nghiệm", "Mục tiêu kiểm chứng", "Tập dữ liệu thử nghiệm", "Chỉ số đo lường (Metrics)"]
    hdr_exp_cells = table_exp.rows[0].cells
    for i, title in enumerate(exp_headers):
        hdr_exp_cells[i].text = title
        set_cell_background(hdr_exp_cells[i], "1B365D")
        set_cell_margins(hdr_exp_cells[i], top=120, bottom=120, left=140, right=140)
        p = hdr_exp_cells[i].paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
        p.runs[0].font.size = Pt(10)
        p.runs[0].font.name = 'Times New Roman'

    exp_matrix_data = [
        (
            "TN 1: Khai phá Ẩm thực\n(Food Entity Mining)",
            "Chứng minh trích xuất được món ăn và cảm xúc chính xác từ review thô.",
            "500 review nhà hàng được gán nhãn thủ công (Ground-truth)",
            "Precision, Recall, F1-Score, Processing Speed (rev/s)"
        ),
        (
            "TN 2: Hiệu năng Truy xuất\n(Retrieval Performance)",
            "Chứng minh GraphRAG tìm đúng ứng viên hơn Vector thuần túy.",
            "100 câu truy vấn đa điều kiện (Món ăn + GPS + Gu du lịch)",
            "Hit@3, Hit@5, MRR, NDCG@5, Query Latency (ms)"
        ),
        (
            "TN 3: Giảm Ảo giác Không gian\n(Spatial Hallucination & RAGAS)",
            "Chứng minh hệ thống không bịa toạ độ hay khoảng cách vô lý.",
            "50 câu hỏi tạo lịch trình phức tạp tại địa bàn Huế",
            "RAGAS (Faithfulness, Answer Relevance), Spatial Feasibility Rate (SFR %)"
        ),
        (
            "TN 4: Tối ưu Lịch trình\n(Itinerary Route Optimization)",
            "Đánh giá tính khả thi và tiết kiệm công sức di chuyển của lịch trình.",
            "20 kịch bản du lịch tại Huế và các địa bàn trọng điểm",
            "Tổng quãng đường (km), Thời gian đi (phút), Điểm hài lòng MOS (1-5)"
        )
    ]

    for row_idx, data in enumerate(exp_matrix_data):
        row = table_exp.add_row()
        fill_color = "F7FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text in enumerate(data):
            cell = row.cells[col_idx]
            cell.text = text
            set_cell_background(cell, fill_color)
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
            p = cell.paragraphs[0]
            p.runs[0].font.name = 'Times New Roman'
            p.runs[0].font.size = Pt(9.5)
            p.paragraph_format.line_spacing = 1.15

    # =============================================================
    # PHẦN 9: SẢN PHẨM DỰ KIẾN VÀ ĐÓNG GÓP CỦA ĐỀ TÀI
    # =============================================================
    h1 = doc.add_heading(level=1)
    format_para(h1, space_before=14, space_after=4)
    r = h1.add_run("9. SẢN PHẨM DỰ KIẾN VÀ ĐÓNG GÓP CỦA ĐỀ TÀI")
    r.font.name = 'Times New Roman'
    r.font.color.rgb = PRIMARY_COLOR

    p = doc.add_paragraph()
    format_para(p)
    p.add_run("9.1. Sản phẩm khoa học và công nghệ bàn giao:\n").bold = True
    prod_list = [
        "Cơ sở dữ liệu sạch: Hơn 8,300 - 9,000 địa điểm du lịch có toạ độ GPS chính xác 100% cùng 1.7 triệu review được chuẩn hóa.",
        "Cơ sở tri thức đồ thị (Spatial Knowledge Graph): Cơ sở dữ liệu đồ thị Neo4j/NetworkX hoàn chỉnh bao phủ quan hệ không gian và ẩm thực.",
        "Bộ mã nguồn chương trình (Source Code): Toàn bộ pipeline tiền xử lý, trích xuất thực thể, đường ống GraphRAG và giao diện Web App.",
        "Ứng dụng Web Demo tương tác (Streamlit App): Hệ thống Trợ lý Du lịch Thông minh tích hợp bản đồ tương tác phục vụ kiểm thử và trình diễn.",
        "Báo cáo toàn văn Khóa luận tốt nghiệp: Quyển báo cáo học thuật đầy đủ 4-5 chương theo đúng quy định của Trường Đại học Khoa học — Đại học Huế."
    ]
    for item in prod_list:
        bp = doc.add_paragraph(style='List Bullet')
        format_para(bp, space_before=1, space_after=2)
        bp.add_run(item)

    p = doc.add_paragraph()
    format_para(p)
    p.add_run("9.2. Đóng góp mới của đề tài:\n").bold = True
    p.add_run(
        "• Về mặt học thuật: Đóng góp phương pháp luận kết hợp Spatial Graph với LLM để giải quyết triệt để vấn đề ảo giác không gian; "
        "đề xuất bộ độ đo Spatial Feasibility Rate (SFR) đánh giá tính khả thi không gian trong bài toán gợi ý lịch trình.\n"
        "• Về mặt thực tiễn: Cung cấp một giải pháp phần mềm độc lập, tự chủ công nghệ, có thể chuyển giao trực tiếp cho các đơn vị quản lý du lịch tại Thừa Thiên Huế "
        "hoặc các doanh nghiệp lữ hành để tích hợp vào ứng dụng đô thị thông minh mà không phụ thuộc vào chi phí API thương mại của nước ngoài."
    )

    # =============================================================
    # PHẦN 10: TIẾN ĐỘ THỰC HIỆN DỰ KIẾN (TIMELINE)
    # =============================================================
    h1 = doc.add_heading(level=1)
    format_para(h1, space_before=14, space_after=4)
    r = h1.add_run("10. KẾ HOẠCH TIẾN ĐỘ THỰC HIỆN CHI TIẾT (10 TUẦN)")
    r.font.name = 'Times New Roman'
    r.font.color.rgb = PRIMARY_COLOR

    tbl_time = doc.add_table(rows=1, cols=3)
    tbl_time.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_time)

    t_headers = ["Thời gian", "Nội dung công việc thực hiện", "Kết quả đầu ra dự kiến"]
    t_hdr_cells = tbl_time.rows[0].cells
    for i, title in enumerate(t_headers):
        t_hdr_cells[i].text = title
        set_cell_background(t_hdr_cells[i], "1B365D")
        set_cell_margins(t_hdr_cells[i], top=100, bottom=100, left=140, right=140)
        p = t_hdr_cells[i].paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
        p.runs[0].font.size = Pt(10)
        p.runs[0].font.name = 'Times New Roman'

    timeline_data = [
        ("Tuần 1 - 2", "• Thu thập, làm sạch và nối dữ liệu metadata với 1.7M review.\n• Xây dựng bộ từ điển ẩm thực song ngữ 250+ món.\n• Chạy thuật toán Entity Linking & Sentiment trích xuất món ăn.", "Dataset sạch chuẩn hóa; Bảng ánh xạ Quán ăn - Món ăn - Điểm đánh giá; Báo cáo Thí nghiệm 1."),
        ("Tuần 3 - 4", "• Thiết kế Ontology Đồ thị Tri thức không gian.\n• Tính toán khoảng cách Haversine và xây dựng đồ thị Neo4j/NetworkX.\n• Tạo 9,072 thẻ thực thể và lập chỉ mục Vector DB với bge-m3.", "Đồ thị Tri thức hoàn chỉnh; Vector Database sẵn sàng; Báo cáo phân tích EDA."),
        ("Tuần 5 - 6", "• Xây dựng module phân tích ý định và trích xuất ràng buộc câu hỏi.\n• Hiện thực đường ống truy xuất lai Spatial GraphRAG.\n• Xây dựng thuật toán tối ưu hóa chuỗi hành trình và prompt sinh lời thoại.", "Pipeline GraphRAG hoàn chỉnh; Chạy thử nghiệm và tinh chỉnh prompt."),
        ("Tuần 7 - 8", "• Thiết lập bộ câu hỏi kiểm thử Benchmark thực tế tại Huế.\n• Chạy độc lập 4 bài thí nghiệm (TN1, TN2, TN3, TN4).\n• Thu thập số liệu, tính toán độ đo và vẽ biểu đồ kết quả.", "Bảng số liệu thực nghiệm đầy đủ; Các biểu đồ so sánh định lượng phục vụ Chương Thực nghiệm."),
        ("Tuần 9 - 10", "• Hoàn thiện giao diện Web App tương tác (Streamlit + Folium).\n• Viết toàn văn Báo cáo Khóa luận tốt nghiệp (4-5 chương).\n• Chuẩn bị slide báo cáo và tập dượt bảo vệ trước Hội đồng.", "Ứng dụng Web hoàn chỉnh; Quyển Báo cáo Khóa luận hoàn thiện; Slide thuyết trình sẵn sàng.")
    ]

    for row_idx, data in enumerate(timeline_data):
        row = tbl_time.add_row()
        fill_color = "F7FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text in enumerate(data):
            cell = row.cells[col_idx]
            cell.text = text
            set_cell_background(cell, fill_color)
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
            p = cell.paragraphs[0]
            p.runs[0].font.name = 'Times New Roman'
            p.runs[0].font.size = Pt(9.5)
            p.paragraph_format.line_spacing = 1.15

    # =============================================================
    # PHẦN 11: TÀI LIỆU THAM KHẢO DỰ KIẾN (REFERENCES)
    # =============================================================
    h1 = doc.add_heading(level=1)
    format_para(h1, space_before=14, space_after=4)
    r = h1.add_run("11. TÀI LIỆU THAM KHẢO DỰ KIẾN (REFERENCES)")
    r.font.name = 'Times New Roman'
    r.font.color.rgb = PRIMARY_COLOR

    refs = [
        "[1] Lewis, P., et al. (2020). \"Retrieval-augmented generation for knowledge-intensive NLP tasks.\" Advances in Neural Information Processing Systems (NeurIPS 2020), 33, 9459-9474.",
        "[2] Edge, D., et al. (2024). \"From Local to Global: A Graph RAG Approach to Query-Focused Summarization.\" Microsoft Research, arXiv preprint arXiv:2404.16130.",
        "[3] Xiao, S., et al. (2024). \"C-Pack: Packaged Resources to Advance General Chinese and Multilingual Embedding.\" BAAI, arXiv preprint arXiv:2309.07597 (Mô hình BAAI/bge-m3).",
        "[4] Es, S., et al. (2023). \"RAGAS: Automated Evaluation of Retrieval Augmented Generation.\" arXiv preprint arXiv:2309.15217.",
        "[5] Hogan, A., et al. (2021). \"Knowledge graphs.\" ACM Computing Surveys (CSUR), 54(4), 1-37.",
        "[6] Lim, K. H., et al. (2019). \"PersTour: A personalized tour recommendation and planning system.\" Information Systems, 89, 101460.",
        "[7] Yuan, N. J., et al. (2023). \"Spatial-Temporal Graph Neural Networks for Travel Recommendation: A Survey.\" IEEE Transactions on Knowledge and Data Engineering (TKDE)."
    ]
    for rf in refs:
        p_rf = doc.add_paragraph()
        format_para(p_rf, space_before=2, space_after=3, line_spacing=1.2)
        r = p_rf.add_run(rf)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)

    # =============================================================
    # PHẦN 12: CHỮ KÝ XÁC NHẬN
    # =============================================================
    p_sp = doc.add_paragraph()
    format_para(p_sp, space_before=20, space_after=10)

    tbl_sign = doc.add_table(rows=3, cols=2)
    tbl_sign.alignment = WD_TABLE_ALIGNMENT.CENTER
    c00, c01 = tbl_sign.rows[0].cells
    c00.width = Inches(3.3)
    c01.width = Inches(3.3)
    c00.text = ""
    c01.text = "Thừa Thiên Huế, ngày      tháng      năm 2026"
    p01 = c01.paragraphs[0]
    format_para(p01, space_before=0, space_after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
    p01.runs[0].font.name = 'Times New Roman'
    p01.runs[0].font.italic = True
    p01.runs[0].font.size = Pt(11)

    c10, c11 = tbl_sign.rows[1].cells
    c10.width = Inches(3.3)
    c11.width = Inches(3.3)
    c10.text = "GIẢNG VIÊN HƯỚNG DẪN\n(Ký và ghi rõ họ tên)"
    c11.text = "SINH VIÊN THỰC HIỆN\n(Ký và ghi rõ họ tên)"
    for cell in (c10, c11):
        p = cell.paragraphs[0]
        format_para(p, space_before=2, space_after=60, align=WD_ALIGN_PARAGRAPH.CENTER)
        p.runs[0].font.name = 'Times New Roman'
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(11)

    c20, c21 = tbl_sign.rows[2].cells
    c20.width = Inches(3.3)
    c21.width = Inches(3.3)
    c20.text = "[Họ tên Giảng viên hướng dẫn]"
    c21.text = "[Họ tên Sinh viên]"
    for cell in (c20, c21):
        p = cell.paragraphs[0]
        format_para(p, space_before=0, space_after=0, align=WD_ALIGN_PARAGRAPH.CENTER)
        p.runs[0].font.name = 'Times New Roman'
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(11)

    # Lưu file
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, filename)
    try:
        doc.save(out_path)
        print(f"ĐÃ TẠO THÀNH CÔNG ĐỀ CƯƠNG CHI TIẾT KHÓA LUẬN: {out_path}")
        return out_path
    except PermissionError:
        latest_filename = "DE_CUONG_CHI_TIET_KHOA_LUAN_TOT_NGHIEP_BAN_MOI_NHAT.docx"
        latest_path = os.path.join(out_dir, latest_filename)
        doc.save(latest_path)
        print(f"Do file {filename} đang mở trong Microsoft Word, đã lưu toàn bộ nội dung mới nhất vào: {latest_path}")
        return latest_path

if __name__ == "__main__":
    build_full_proposal()
