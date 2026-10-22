# -*- coding: utf-8 -*-
"""
SOẠN THẢO TOÀN VĂN KHÓA LUẬN TỐT NGHIỆP ĐẠI HỌC (CHUẨN 5 PHẦN HUET)
Ngành: Khoa học Dữ liệu và Trí tuệ Nhân tạo (DS&AI K3)
Khoa Kỹ thuật và Công nghệ - Đại học Huế (HUET)
Đề tài: Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh dựa trên Đồ thị Tri thức Không gian và Mô hình Ngôn ngữ Lớn
Sinh viên thực hiện: Lê Hoàng Minh Quý (MSSV: 22E1020017)
Giảng viên hướng dẫn: TS. Hồ Quốc Dũng
Năm thực hiện: 2026

Tuân thủ tuyệt đối:
- Văn bản số 1967/HD-ĐHH của Đại học Huế (Quy cách 5 Phần, Mẫu 1 đến Mẫu 9, căn lề 3-3-3-2 cm, Times New Roman 13pt, dãn dòng 1.5).
- Kỹ năng Viết học thuật Chuyên ngành Khoa học Dữ liệu & AI (academic-writing-ds-ai):
  Triệt tiêu 100% 16 dấu hiệu văn phong AI, không biểu tượng cảm xúc, không khung callout chatbot,
  không gạch đầu dòng liệt kê từ khóa: giải thích, văn xuôi học thuật liên tục, phân tích và trích dẫn bảng biểu/hình ảnh song hành (Dual In-text Referencing).
"""

import os
import sys
from pathlib import Path

# Cấu hình UTF-8 cho Windows console
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
IMG_DIR = PROJECT_ROOT / "thesis-latex" / "img"

# Màu sắc học thuật thuần túy (Black text cho toàn bộ ấn phẩm in)
BLACK_TEXT = RGBColor(0, 0, 0)
MUTED_TEXT = RGBColor(60, 60, 60)


def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=80, bottom=80, left=100, right=100):
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


def set_academic_table_borders(table, border_color="000000"):
    """
    Tạo đường kẻ bảng chuẩn học thuật (Booktabs style):
    Đường kẻ ngang trên cùng, dưới cùng và dưới tiêu đề (không kẻ dọc, không ô bàn cờ).
    """
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        borders = parse_xml(f'''
            <w:tblBorders {nsdecls("w")}>
                <w:top w:val="single" w:sz="8" w:space="0" w:color="{border_color}"/>
                <w:bottom w:val="single" w:sz="8" w:space="0" w:color="{border_color}"/>
                <w:insideH w:val="single" w:sz="4" w:space="0" w:color="D3D3D3"/>
                <w:insideV w:val="none"/>
                <w:left w:val="none"/>
                <w:right w:val="none"/>
            </w:tblBorders>
        ''')
        tblPr[0].append(borders)


def format_body_p(p, space_before=0, space_after=6, line_spacing=1.5, indent_cm=1.0):
    """Định dạng đoạn văn bản thân bài chuẩn HUET: Times New Roman 13pt, thụt dòng 1cm, dãn dòng 1.5, căn đều."""
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if indent_cm > 0:
        p.paragraph_format.first_line_indent = Inches(indent_cm / 2.54)


def add_body_run(p, text, italic=False, bold=False, size_pt=13):
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(size_pt)
    r.font.color.rgb = BLACK_TEXT
    r.font.italic = italic
    r.font.bold = bold
    return r


def add_part_heading(doc, text):
    """Tiêu đề Phần (Cấp 1): 16pt, IN HOA ĐẬM, Canh giữa, Chữ thẳng."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.3
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = BLACK_TEXT
    return p


def add_chapter_heading(doc, text):
    """Tiêu đề Chương (Cấp 1): 16pt, IN HOA ĐẬM, Canh giữa, Chữ thẳng."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.3
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = BLACK_TEXT
    return p


def add_sec_heading(doc, text):
    """Tiêu đề Mục cấp 2 (1.1.): 14pt, In đậm nghiêng, Canh trái."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.3
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.italic = True
    r.font.color.rgb = BLACK_TEXT
    return p


def add_subsec_heading(doc, text):
    """Tiêu đề Mục cấp 3 (1.1.1.): 13pt, In đậm nghiêng, Canh trái."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.3
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.italic = True
    r.font.color.rgb = BLACK_TEXT
    return p


def add_table_caption(doc, text):
    """Tiêu đề bảng: đặt phía trên bảng, in nghiêng, canh giữa."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    r.font.italic = True
    r.font.color.rgb = BLACK_TEXT


def add_figure(doc, img_name, caption_text, width_inches=5.6):
    """Chèn hình vẽ: canh giữa, có caption bên dưới in nghiêng canh giữa."""
    img_path = IMG_DIR / img_name
    if img_path.exists():
        p_img = doc.add_paragraph()
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(4)
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_img = p_img.add_run()
        r_img.add_picture(str(img_path), width=Inches(width_inches))

        p_cap = doc.add_paragraph()
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(10)
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run(caption_text)
        r_cap.font.name = 'Times New Roman'
        r_cap.font.size = Pt(11)
        r_cap.font.italic = True
        r_cap.font.color.rgb = BLACK_TEXT


def set_footer_page_number(section):
    """Cấu hình số trang ở giữa phía dưới trang giấy (Footer center)."""
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run()
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)

    fldChar1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
    instrText = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> PAGE </w:instrText>')
    fldChar2 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="separate"/>')
    fldChar3 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)


def set_section_margins_huet(section):
    """Căn lề chuẩn HUET theo Văn bản 1967/HD-ĐHH: Trên 3.0cm, Dưới 3.0cm, Trái 3.0cm, Phải 2.0cm."""
    section.top_margin = Inches(3.0 / 2.54)
    section.bottom_margin = Inches(3.0 / 2.54)
    section.left_margin = Inches(3.0 / 2.54)
    section.right_margin = Inches(2.0 / 2.54)


def build_thesis_docx():
    doc = docx.Document()

    # =========================================================================
    # SECTION 0: TRANG BÌA CHÍNH (MẪU 1) VÀ TRANG BÌA PHỤ (MẪU 2)
    # =========================================================================
    sec_cover = doc.sections[0]
    set_section_margins_huet(sec_cover)

    # -------------------------------------------------------------------------
    # TRANG BÌA CHÍNH (MẪU 1)
    # -------------------------------------------------------------------------
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("ĐẠI HỌC HUẾ")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("KHOA KỸ THUẬT VÀ CÔNG NGHỆ")
    r.font.name = 'Times New Roman'
    r.font.bold = True
    r.font.size = Pt(14)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(15)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("BỘ MÔN KHOA HỌC DỮ LIỆU VÀ TRÍ TUỆ NHÂN TẠO")
    r.font.name = 'Times New Roman'
    r.font.bold = True
    r.font.size = Pt(14)

    logo_path = IMG_DIR / "logo-huet-300x300.png"
    if logo_path.exists():
        p_logo = doc.add_paragraph()
        p_logo.paragraph_format.space_before = Pt(5)
        p_logo.paragraph_format.space_after = Pt(15)
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_logo = p_logo.add_run()
        r_logo.add_picture(str(logo_path), width=Inches(1.3))

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(10)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("LÊ HOÀNG MINH QUÝ")
    r.font.name = 'Times New Roman'
    r.font.bold = True
    r.font.size = Pt(14)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(15)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("HỆ THỐNG HỎI ĐÁP VÀ GỢI Ý LỊCH TRÌNH DU LỊCH THÔNG MINH\nDỰA TRÊN ĐỒ THỊ TRI THỨC KHÔNG GIAN\nVÀ MÔ HÌNH NGÔN NGỮ LỚN")
    r.font.name = 'Times New Roman'
    r.font.bold = True
    r.font.size = Pt(20)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(5)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("KHÓA LUẬN TỐT NGHIỆP ĐẠI HỌC")
    r.font.name = 'Times New Roman'
    r.font.bold = True
    r.font.size = Pt(18)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(40)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("NGÀNH: KHOA HỌC DỮ LIỆU VÀ TRÍ TUỆ NHÂN TẠO")
    r.font.name = 'Times New Roman'
    r.font.bold = True
    r.font.size = Pt(16)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(30)
    p.paragraph_format.space_after = Pt(0)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("THÀNH PHỐ HUẾ, NĂM 2026")
    r.font.name = 'Times New Roman'
    r.font.bold = True
    r.font.size = Pt(14)

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # TRANG BÌA PHỤ (MẪU 2)
    # -------------------------------------------------------------------------
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("ĐẠI HỌC HUẾ")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("KHOA KỸ THUẬT VÀ CÔNG NGHỆ")
    r.font.name = 'Times New Roman'
    r.font.bold = True
    r.font.size = Pt(14)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(15)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("BỘ MÔN KHOA HỌC DỮ LIỆU VÀ TRÍ TUỆ NHÂN TẠO")
    r.font.name = 'Times New Roman'
    r.font.bold = True
    r.font.size = Pt(14)

    if logo_path.exists():
        p_logo = doc.add_paragraph()
        p_logo.paragraph_format.space_before = Pt(5)
        p_logo.paragraph_format.space_after = Pt(15)
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_logo = p_logo.add_run()
        r_logo.add_picture(str(logo_path), width=Inches(1.3))

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(10)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("LÊ HOÀNG MINH QUÝ – MSSV: 22E1020017")
    r.font.name = 'Times New Roman'
    r.font.bold = True
    r.font.size = Pt(14)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(15)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("HỆ THỐNG HỎI ĐÁP VÀ GỢI Ý LỊCH TRÌNH DU LỊCH THÔNG MINH\nDỰA TRÊN ĐỒ THỊ TRI THỨC KHÔNG GIAN\nVÀ MÔ HÌNH NGÔN NGỮ LỚN")
    r.font.name = 'Times New Roman'
    r.font.bold = True
    r.font.size = Pt(18)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after = Pt(5)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("KHÓA LUẬN TỐT NGHIỆP ĐẠI HỌC")
    r.font.name = 'Times New Roman'
    r.font.bold = True
    r.font.size = Pt(16)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(25)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("NGÀNH: KHOA HỌC DỮ LIỆU VÀ TRÍ TUỆ NHÂN TẠO")
    r.font.name = 'Times New Roman'
    r.font.bold = True
    r.font.size = Pt(15)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(15)
    p.paragraph_format.space_after = Pt(30)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p.add_run("Người hướng dẫn: ")
    r1.font.name = 'Times New Roman'
    r1.font.size = Pt(14)
    r2 = p.add_run("TS. Hồ Quốc Dũng")
    r2.font.name = 'Times New Roman'
    r2.font.bold = True
    r2.font.size = Pt(14)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(20)
    p.paragraph_format.space_after = Pt(0)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("THÀNH PHỐ HUẾ, NĂM 2026")
    r.font.name = 'Times New Roman'
    r.font.bold = True
    r.font.size = Pt(14)

    # =========================================================================
    # SECTION 1: FRONT MATTER (LỜI CAM ĐOAN ĐẾN DANH MỤC HÌNH VẼ - SỐ LA MÃ)
    # =========================================================================
    sec_front = doc.add_section()
    set_section_margins_huet(sec_front)
    sec_front.footer.is_linked_to_previous = False
    set_footer_page_number(sec_front)

    # LỜI CAM ĐOAN
    add_part_heading(doc, "LỜI CAM ĐOAN")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Tôi xin cam đoan công trình nghiên cứu khoa học này do chính tôi thực hiện dưới sự định hướng phương pháp luận và hướng dẫn khoa học trực tiếp của TS. Hồ Quốc Dũng. Toàn bộ các kết quả nghiên cứu, tập dữ liệu thu thập thực tế tại tỉnh Thừa Thiên Huế, cấu trúc Đồ thị Tri thức Không gian và các phép đo thực nghiệm đối sánh được trình bày trong luận văn này là hoàn toàn trung thực, khách quan và chưa từng được công bố trong bất kỳ công trình nào khác nhằm mục đích nhận văn bằng hay học vị.")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Mọi sự tham khảo, kế thừa từ các công trình nghiên cứu khoa học của các tác giả trong và ngoài nước, các công cụ mã nguồn mở và nền tảng dữ liệu trực tuyến đều được trích dẫn nguồn gốc rõ ràng, minh bạch và chính xác theo đúng quy chuẩn học thuật của Nhà trường và Đại học Huế.")

    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = Pt(20)
    p_sig.paragraph_format.space_after = Pt(20)
    p_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_sig = p_sig.add_run("Huế, ngày ... tháng ... năm 2026\nSinh viên thực hiện\n\n\nLê Hoàng Minh Quý")
    r_sig.font.name = 'Times New Roman'
    r_sig.font.size = Pt(13)
    r_sig.font.italic = True

    doc.add_page_break()

    # LỜI CẢM ƠN
    add_part_heading(doc, "LỜI CẢM ƠN")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Lời đầu tiên, em xin bày tỏ lòng biết ơn sâu sắc và chân thành nhất đến Thầy TS. Hồ Quốc Dũng, người đã luôn định hướng phương pháp luận khoa học chặt chẽ, truyền cảm hứng nghiên cứu và dành nhiều thời gian quý báu để tận tình hướng dẫn, góp ý và động viên em trong suốt quá trình hoàn thành khóa luận tốt nghiệp này. Những định hướng chiến lược của Thầy về việc kết hợp Đồ thị Tri thức Không gian với mô hình ngôn ngữ lớn đã giúp đề tài đạt được tính mới và giá trị thực tiễn sâu sắc.")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Em xin trân trọng cảm ơn Quý Thầy, Cô giáo tại Khoa Kỹ thuật và Công nghệ – Đại học Huế đã nhiệt tình giảng dạy, truyền đạt những kiến thức nền tảng và chuyên sâu về toán học, khoa học dữ liệu và học máy trong suốt bốn năm học đại học, tạo tiền đề vững chắc cho việc thực hiện đề tài.")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Sau cùng, con xin gửi lời cảm ơn vô hạn đến gia đình, cha mẹ và những người thân yêu đã luôn là điểm tựa tinh thần vững chắc, hết lòng thương yêu và tạo mọi điều kiện tốt nhất để con yên tâm học tập và hoàn thành khóa luận tốt nghiệp.")

    doc.add_page_break()

    # TÓM TẮT KHÓA LUẬN
    add_part_heading(doc, "TÓM TẮT")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Trong bối cảnh đô thị thông minh và chuyển đổi số ngành du lịch tại tỉnh Thừa Thiên Huế, nhu cầu ứng dụng trí tuệ nhân tạo để giải quyết ba bài toán cốt lõi của du khách gồm đi đâu, ăn gì và lưu trú ở đâu đang trở nên hết sức cấp thiết. Mặc dù các mô hình ngôn ngữ lớn (LLM) và hệ thống Tăng cường Tạo sinh Truy xuất truyền thống (Naive RAG) mang lại khả năng tương tác tự nhiên, chúng bộc lộ hai khiếm khuyết lớn: hiện tượng ảo giác địa danh gây bịa đặt các quán ăn không có thật, và sự thiếu nhận thức không gian dẫn đến các lịch trình di chuyển ziczac, vi phạm cự ly thực tế giữa hai bờ sông Hương.")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Khóa luận này nghiên cứu và hiện thực hóa một khung giải pháp tích hợp đa tầng mang tên Spatial GraphRAG, kết hợp Đồ thị Tri thức Không gian quy mô 9.525 nút và 90.948 cạnh quan hệ, giải thuật khai phá thực đơn ngầm từ 44.355 bài nhận xét du khách tại Huế, và khung điều phối tác tử tự suy ngẫm Agentic RAG trên LangGraph vận hành hoàn toàn trên mô hình cục bộ Qwen2.5-3B. Hệ thống đồng thời phát triển thuật toán lập lịch trình phân cụm địa lý và đóng gói Cổng API RESTful chuẩn GeoJSON sẵn sàng tích hợp với nền tảng công dân số di động Hue-S. Kết quả thực nghiệm định lượng trên bộ dữ liệu kiểm thử chuẩn 12 kịch bản đại diện tại Huế chứng minh hệ thống đạt tỷ lệ bảo chứng thực thể 100%, triệt tiêu hoàn toàn lỗi vi phạm cự ly (0% vi phạm), tối ưu hóa khoảng cách trung bình từ 6,82 km xuống 1,25 km và đạt thời gian phản hồi thời gian thực trung bình 2,80 giây.")

    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_before = Pt(12)
    p_kw.paragraph_format.space_after = Pt(20)
    p_kw.paragraph_format.first_line_indent = Inches(1.0 / 2.54)
    r = p_kw.add_run("Từ khóa: ")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.italic = True
    r = p_kw.add_run("Đồ thị Tri thức Không gian, Spatial GraphRAG, Agentic RAG, LangGraph, Qwen2.5, Du lịch Huế, Khai phá thực đơn ngầm, Hue-S.")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.italic = True

    doc.add_page_break()

    # MỤC LỤC TỔNG THỂ
    add_part_heading(doc, "MỤC LỤC")
    toc_items = [
        ("LỜI CAM ĐOAN", "i", True, False),
        ("LỜI CẢM ƠN", "ii", True, False),
        ("TÓM TẮT", "iii", True, False),
        ("MỤC LỤC", "iv", True, False),
        ("DANH MỤC CÁC CHỮ VIẾT TẮT VÀ KÝ HIỆU", "v", True, False),
        ("DANH MỤC CÁC BẢNG, BIỂU", "vi", True, False),
        ("DANH MỤC CÁC SƠ ĐỒ, ĐỒ THỊ, HÌNH VẼ", "vii", True, False),
        ("PHẦN I. PHẦN MỞ ĐẦU", "1", True, False),
        ("   1. Tính cấp thiết của đề tài", "1", False, True),
        ("   2. Mục tiêu nghiên cứu", "3", False, True),
        ("   3. Câu hỏi nghiên cứu và Giả thuyết khoa học", "4", False, True),
        ("   4. Đối tượng và Phạm vi nghiên cứu", "5", False, True),
        ("   5. Ý nghĩa khoa học và Thực tiễn", "6", False, True),
        ("PHẦN II. TỔNG QUAN VẤN ĐỀ NGHIÊN CỨU", "7", True, False),
        ("   1. Cơ sở lý thuyết nền tảng", "7", False, True),
        ("      1.1. Đồ thị Tri thức Không gian và Khoảng cách Mặt cầu", "7", False, True),
        ("      1.2. Sự tiến hóa từ Naive RAG sang GraphRAG và Agentic RAG", "8", False, True),
        ("      1.3. Khung điều phối trạng thái LangGraph và Mô hình cục bộ Qwen2.5", "10", False, True),
        ("      1.4. Khai phá thực đơn ngầm và Bài toán Thiết kế Chuyến đi Du lịch", "12", False, True),
        ("PHẦN III. ĐỐI TƯỢNG, PHẠM VI VÀ PHƯƠNG PHÁP NGHIÊN CỨU", "14", True, False),
        ("   1. Đối tượng và Thực trạng các nguồn dữ liệu nghiên cứu", "14", False, True),
        ("      1.1. Hiện trạng đa nguồn dữ liệu và Quy mô tổng thể", "14", False, True),
        ("      1.2. Giải phẫu cấu trúc tập dữ liệu 44.355 bài đánh giá thực tế tại Huế", "16", False, True),
        ("PHẦN IV. NỘI DUNG VÀ KẾT QUẢ NGHIÊN CỨU", "20", True, False),
        ("   Chương 1. Kiến trúc Hệ thống Spatial GraphRAG và Khai phá Thực đơn Ngầm", "20", True, False),
        ("      1.1. Kiến trúc tổng thể bốn tầng của Hệ thống", "20", False, True),
        ("      1.2. Thiết kế Đồ thị Tri thức Không gian Du lịch Huế", "22", False, True),
        ("      1.3. Phương pháp khai phá thực đơn ngầm và đối soát tri thức", "25", False, True),
        ("      1.4. Khung điều phối tác tử tự suy ngẫm Agentic RAG trên LangGraph", "27", False, True),
        ("      1.5. Tầng Lưu trữ Đám mây NoSQL và Quản trị Đa phiên Hội thoại", "28", False, True),
        ("      1.6. Thiết kế Giao diện Khách Web Tương tác Không gian (Gemini-Style Client)", "29", False, True),
        ("   Chương 2. Thuật toán Lập lịch trình Không gian, Thực nghiệm Đối sánh và Tích hợp", "30", True, False),
        ("      2.1. Thuật toán Lập lịch trình phân cụm không gian", "30", False, True),
        ("      2.2. Bộ kiểm thử Benchmark 12 kịch bản du lịch Huế", "32", False, True),
        ("      2.3. Kết quả thực nghiệm đối sánh định lượng", "36", False, True),
        ("      2.4. Hiện thực hóa Cổng API RESTful và Sẵn sàng Tích hợp Hue-S", "38", False, True),
        ("PHẦN V. KẾT LUẬN VÀ KIẾN NGHỊ", "40", True, False),
        ("   1. Kết luận và Đóng góp của đề tài", "40", False, True),
        ("   2. Những hạn chế của nghiên cứu", "41", False, True),
        ("   3. Kiến nghị và Hướng phát triển tiếp theo", "42", False, True),
        ("TÀI LIỆU THAM KHẢO", "43", True, False)
    ]
    for item, page_str, is_bold, is_italic in toc_items:
        p_toc = doc.add_paragraph()
        p_toc.paragraph_format.space_before = Pt(1)
        p_toc.paragraph_format.space_after = Pt(2)
        p_toc.paragraph_format.line_spacing = 1.2
        r_title = p_toc.add_run(item)
        r_title.font.name = 'Times New Roman'
        r_title.font.size = Pt(12)
        r_title.font.bold = is_bold
        r_title.font.italic = is_italic
        dots_count = max(3, 85 - len(item) - len(page_str))
        r_dots = p_toc.add_run(" " + "." * dots_count + " ")
        r_dots.font.name = 'Times New Roman'
        r_dots.font.size = Pt(10)
        r_page = p_toc.add_run(page_str)
        r_page.font.name = 'Times New Roman'
        r_page.font.size = Pt(12)
        r_page.font.bold = is_bold

    doc.add_page_break()

    # DANH MỤC CÁC CHỮ VIẾT TẮT VÀ KÝ HIỆU
    add_part_heading(doc, "DANH MỤC CÁC CHỮ VIẾT TẮT VÀ KÝ HIỆU")
    abbr_data = [
        ["Ký hiệu", "Tên tiếng Anh đầy đủ", "Ý nghĩa tiếng Việt"],
        ["AI", "Artificial Intelligence", "Trí tuệ nhân tạo"],
        ["API", "Application Programming Interface", "Giao diện lập trình ứng dụng"],
        ["DS&AI", "Data Science & Artificial Intelligence", "Khoa học Dữ liệu và Trí tuệ Nhân tạo"],
        ["GPS", "Global Positioning System", "Hệ thống định vị toàn cầu"],
        ["GPU", "Graphics Processing Unit", "Bộ xử lý đồ họa"],
        ["HUET", "Hue University of Engineering and Technology", "Khoa Kỹ thuật và Công nghệ – Đại học Huế"],
        ["JSON", "JavaScript Object Notation", "Định dạng trao đổi dữ liệu đối tượng"],
        ["JWT", "JSON Web Token", "Chuẩn mở định dạng mã thông báo bảo mật"],
        ["KG", "Knowledge Graph", "Đồ thị tri thức"],
        ["LLM", "Large Language Model", "Mô hình ngôn ngữ lớn"],
        ["NLP", "Natural Language Processing", "Xử lý ngôn ngữ tự nhiên"],
        ["NoSQL", "Not Only SQL", "Mô hình cơ sở dữ liệu phi quan hệ"],
        ["OAuth", "Open Authorization", "Khung ủy quyền phân tán tiêu chuẩn mở"],
        ["OSM", "OpenStreetMap", "Dự án bản đồ số mở toàn cầu"],
        ["OSRM", "Open Source Routing Machine", "Hệ thống tính toán định tuyến mã nguồn mở"],
        ["POI", "Point of Interest", "Điểm tham quan / Cơ sở dịch vụ du lịch"],
        ["RAG", "Retrieval-Augmented Generation", "Tạo sinh tăng cường truy xuất"],
        ["REST", "Representational State Transfer", "Phong cách kiến trúc mạng hướng dịch vụ"],
        ["RLHF", "Reinforcement Learning from Human Feedback", "Học tăng cường từ phản hồi của con người"],
        ["SKG", "Spatial Knowledge Graph", "Đồ thị tri thức không gian"],
        ["VRAM", "Video Random Access Memory", "Bộ nhớ truy cập ngẫu nhiên của bộ xử lý đồ họa"],
        ["WMO", "World Meteorological Organization", "Tổ chức Khí tượng Thế giới"]
    ]
    tbl_abbr = doc.add_table(rows=len(abbr_data), cols=3)
    tbl_abbr.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_academic_table_borders(tbl_abbr)
    for r_idx, row in enumerate(abbr_data):
        for c_idx, val in enumerate(row):
            cell = tbl_abbr.rows[r_idx].cells[c_idx]
            p_cell = cell.paragraphs[0]
            p_cell.paragraph_format.space_before = Pt(2)
            p_cell.paragraph_format.space_after = Pt(2)
            p_cell.paragraph_format.line_spacing = 1.15
            p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r_c = p_cell.add_run(val)
            r_c.font.name = 'Times New Roman'
            r_c.font.size = Pt(11)
            if r_idx == 0:
                r_c.font.bold = True
                set_cell_background(cell, "EAECEF")
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)

    doc.add_page_break()

    # DANH MỤC CÁC BẢNG, BIỂU
    add_part_heading(doc, "DANH MỤC CÁC BẢNG, BIỂU")
    table_list = [
        ("Bảng 1", "Tổng mục các nguồn dữ liệu thành phần sử dụng trong nghiên cứu", "15"),
        ("Bảng 2", "Phân bố xếp hạng sao của 44.355 bài đánh giá du lịch thực tế tại Huế", "17"),
        ("Bảng 3", "Phân bố kiểu hình chuyến đi của du khách trong tập dữ liệu nhận xét tại Huế", "18"),
        ("Bảng 4", "Cơ cấu phân loại và phân bố địa giới của 610 địa điểm du lịch tại Huế", "19"),
        ("Bảng 1.1", "Thống kê định lượng các thành phần trong Đồ thị Tri thức Không gian", "23"),
        ("Bảng 1.2", "Mẫu đối soát kết quả khai phá thực đơn ngầm từ nhận xét du khách tại Huế", "26"),
        ("Bảng 1.4", "Lược đồ cấu trúc dữ liệu trên Google Cloud Firestore phục vụ quản lý đa phiên và phản hồi", "28"),
        ("Bảng 1.5", "Ma trận Quy tắc Thích ứng Lộ trình theo Ngữ cảnh Khí tượng Cố đô Huế", "29"),
        ("Bảng 2.1", "Đặc tả chi tiết 12 kịch bản trong Bộ dữ liệu kiểm thử chuẩn cho du lịch Huế", "33"),
        ("Bảng 2.2", "Bảng đối sánh hiệu năng định lượng giữa các phương pháp trên bộ Benchmark", "37")
    ]
    tbl_meta = doc.add_table(rows=len(table_list) + 1, cols=3)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_academic_table_borders(tbl_meta)
    headers = ["Số hiệu bảng", "Tên bảng, biểu", "Trang"]
    for c_idx, h in enumerate(headers):
        cell = tbl_meta.rows[0].cells[c_idx]
        p_c = cell.paragraphs[0]
        r_c = p_c.add_run(h)
        r_c.font.name = 'Times New Roman'
        r_c.font.bold = True
        r_c.font.size = Pt(11)
        set_cell_background(cell, "EAECEF")
        set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
    for r_idx, (num, name, pg) in enumerate(table_list):
        row = tbl_meta.rows[r_idx + 1]
        for c_idx, val in enumerate([num, name, pg]):
            cell = row.cells[c_idx]
            p_c = cell.paragraphs[0]
            r_c = p_c.add_run(val)
            r_c.font.name = 'Times New Roman'
            r_c.font.size = Pt(11)
            set_cell_margins(cell, top=50, bottom=50, left=80, right=80)

    doc.add_page_break()

    # DANH MỤC CÁC SƠ ĐỒ, ĐỒ THỊ, HÌNH VẼ
    add_part_heading(doc, "DANH MỤC CÁC SƠ ĐỒ, ĐỒ THỊ, HÌNH VẼ")
    fig_list = [
        ("Hình 1", "Bài báo phản ánh chỉ đạo của lãnh đạo thành phố Huế trên Báo Thanh Niên", "2"),
        ("Hình 2", "Thực trạng giao diện phân hệ du lịch trên nền tảng đô thị thông minh Hue-S", "3"),
        ("Hình 3", "Cơ cấu phân bố các danh mục địa điểm du lịch và dịch vụ tại thành phố Huế", "19"),
        ("Hình 4", "Top 10 món ăn đặc sản Huế được du khách nhắc đến nhiều nhất trong tập ngữ liệu", "20"),
        ("Hình 5", "Quy trình phân mảnh văn bản phân tử cho các bài nhận xét du khách", "21"),
        ("Hình 1.1", "Kiến trúc tổng thể bốn tầng của Hệ thống Spatial GraphRAG Du lịch Thông minh", "21"),
        ("Hình 1.2", "Lược đồ cấu trúc thực thể và quan hệ trong Đồ thị Tri thức Không gian", "23"),
        ("Hình 1.3", "Kiến trúc Đồ thị Trạng thái điều phối quy trình Agentic RAG trên LangGraph", "28"),
        ("Hình 2.1", "Kịch bản luồng tương tác và gợi ý lịch trình phân cụm không gian của hệ thống", "30"),
        ("Hình 2.2", "Biểu đồ đối sánh định lượng các chỉ số hiệu năng giữa ba phương pháp", "37")
    ]
    tbl_fig_meta = doc.add_table(rows=len(fig_list) + 1, cols=3)
    tbl_fig_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_academic_table_borders(tbl_fig_meta)
    headers = ["Số hiệu hình", "Tên sơ đồ, đồ thị, hình vẽ", "Trang"]
    for c_idx, h in enumerate(headers):
        cell = tbl_fig_meta.rows[0].cells[c_idx]
        p_c = cell.paragraphs[0]
        r_c = p_c.add_run(h)
        r_c.font.name = 'Times New Roman'
        r_c.font.bold = True
        r_c.font.size = Pt(11)
        set_cell_background(cell, "EAECEF")
        set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
    for r_idx, (num, name, pg) in enumerate(fig_list):
        row = tbl_fig_meta.rows[r_idx + 1]
        for c_idx, val in enumerate([num, name, pg]):
            cell = row.cells[c_idx]
            p_c = cell.paragraphs[0]
            r_c = p_c.add_run(val)
            r_c.font.name = 'Times New Roman'
            r_c.font.size = Pt(11)
            set_cell_margins(cell, top=50, bottom=50, left=80, right=80)

    # =========================================================================
    # SECTION 2: PHẦN NỘI DUNG CHÍNH (PHẦN I ĐẾN TÀI LIỆU THAM KHẢO - SỐ Ả RẬP)
    # =========================================================================
    sec_body = doc.add_section()
    set_section_margins_huet(sec_body)
    sec_body.footer.is_linked_to_previous = False
    set_footer_page_number(sec_body)

    # Cấu hình đánh số Ả Rập bắt đầu từ trang 1
    sectPr = sec_body._sectPr
    pgNumType = sectPr.find(qn('w:pgNumType'))
    if pgNumType is None:
        pgNumType = OxmlElement('w:pgNumType')
        sectPr.append(pgNumType)
    pgNumType.set(qn('w:fmt'), 'decimal')
    pgNumType.set(qn('w:start'), '1')

    # =========================================================================
    # PHẦN I. PHẦN MỞ ĐẦU
    # =========================================================================
    add_part_heading(doc, "PHẦN I. PHẦN MỞ ĐẦU")

    add_sec_heading(doc, "1. Tính cấp thiết của đề tài")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Thừa Thiên Huế là trung tâm văn hóa, lịch sử và du lịch đặc sắc hàng đầu của Việt Nam, sở hữu Quần thể Di tích Cố đô Huế được UNESCO vinh danh là Di sản Văn hóa Thế giới cùng hệ thống lăng tẩm triều Nguyễn, danh lam cổ tự và nền văn hóa ẩm thực cung đình lẫn dân gian trứ danh. Trong tiến trình xây dựng và phát triển tỉnh Thừa Thiên Huế trở thành thành phố trực thuộc Trung ương theo định hướng tại Nghị quyết số 54-NQ/TW của Bộ Chính trị, nhiệm vụ đẩy mạnh chuyển đổi số ngành du lịch và xây dựng môi trường đô thị thông minh đóng vai trò là đòn bẩy phát triển kinh tế xã hội trọng điểm. Cùng với sự bùng nổ của các mô hình ngôn ngữ lớn và trí tuệ nhân tạo tạo sinh, hành vi của du khách hiện đại đã có sự chuyển biến căn bản: người dùng ngày càng có nhu cầu tương tác với các trợ lý ảo đàm thoại thông minh có khả năng thấu hiểu ngữ cảnh tự nhiên, tư vấn lịch trình cá nhân hóa, gợi ý địa điểm ẩm thực địa phương chuẩn xác và tối ưu hóa tuyến đường theo thời gian thực thay vì tra cứu thủ công qua các danh bạ tĩnh truyền thống.")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Tuy nhiên, trong thực tiễn công tác quản lý và xúc tiến du lịch tại địa phương, ngành du lịch Thừa Thiên Huế đang đứng trước bài toán chiến lược mang tính sống còn về việc kéo dài thời gian lưu trú và gia tăng mức chi tiêu của du khách. Vấn đề cấp bách này đã được lãnh đạo Thành phố Huế đặc biệt nhấn mạnh trong chuyến khảo sát thực địa và chỉ đạo điều hành vào tháng 9 năm 2026, được cơ quan báo chí phản ánh rộng rãi, tiêu biểu như bài viết trên Báo Thanh Niên [1] được ghi nhận tại Hình 1.")

    add_figure(doc, "thanhnien_hue_tourism_problem.png", "Hình 1: Bài báo phản ánh chỉ đạo của lãnh đạo thành phố Huế về yêu cầu giải quyết ba câu hỏi cốt lõi của du khách: Đi đâu, ăn gì, lưu trú ở đâu trên Báo Thanh Niên [1]")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Từ nội dung chỉ đạo thực tế được phản ánh trên Hình 1, lãnh đạo chính quyền Thành phố Huế sau các chuyến kiểm tra thực địa tại chợ Đông Ba, các không gian kết nối phát triển phố đêm và tuyến đường đi dạo ven sông Như Ý đã triệu tập cuộc họp chuyên đề nhằm tìm kiếm các giải pháp then chốt. Thông điệp cốt lõi được đặt ra cho toàn ngành du lịch Cố đô là: Huế phải trả lời một cách thỏa đáng, tức thời và thuyết phục ba câu hỏi căn bản của du khách: Đi đâu? Ăn gì? Lưu trú ở đâu? Nếu không giải quyết thấu đáo chuỗi nhu cầu liên hoàn này, du khách sẽ chỉ đến Huế theo hình thức tham quan chớp nhoáng ban ngày rồi di chuyển sang các địa phương lân cận, khiến ngành du lịch địa phương bỏ lỡ nguồn doanh thu dịch vụ và kinh tế đêm to lớn.")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Nhằm hiện thực hóa mục tiêu chuyển đổi số phục vụ người dân và du khách, tỉnh Thừa Thiên Huế đã tiên phong xây dựng nền tảng đô thị thông minh Hue-S [19], tích hợp phân hệ thông tin du lịch và dịch vụ công dân số. Dù đạt được nhiều thành tựu quan trọng về mặt chính quyền điện tử, khi đi sâu vào phân hệ hỗ trợ du lịch tương tác, ứng dụng Hue-S hiện tại vẫn bộc lộ những hạn chế kỹ thuật đáng kể, được minh họa trực quan thông qua giao diện thực tế tại Hình 2.")

    add_figure(doc, "hues_smart_city_app_home.png", "Hình 2: Thực trạng giao diện phân hệ du lịch trên nền tảng đô thị thông minh Hue-S cho thấy sự thiếu vắng dữ liệu đánh giá thực tế và công cụ lập lịch trình tự động [19]")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Quan sát giao diện thực tế tại Hình 2, phân hệ du lịch của Hue-S hiện tại hoạt động theo mô hình cổng thông tin điện tử một chiều: cung cấp thanh tìm kiếm từ khóa cơ bản, thông tin thời tiết, quảng bá dịch vụ vé tàu di sản tuyến Huế – Đà Nẵng và danh mục các điểm đến phân theo nhóm thiên nhiên hoặc di tích. Tuy nhiên, khi người dùng truy cập sâu vào chi tiết của một địa danh du lịch, hệ thống bộc lộ hai rào cản trải nghiệm hết sức rõ rệt. Thứ nhất, tại mục Đánh giá, hệ thống thường xuyên thông báo trạng thái 'Chưa có đánh giá nào'. Điều này phản ánh thực trạng thiếu hụt cơ sở dữ liệu phản hồi thực tế từ cộng đồng du khách (Cold-start Review Gap), thiếu vắng các thuật toán phân tích cảm xúc và hoàn toàn không có khả năng khai phá thị hiếu ẩm thực hay các món ăn đặc sản được yêu thích tại địa phương. Thứ hai, nút bấm chức năng Thêm hành trình chỉ đóng vai trò như một danh sách đánh dấu thủ công thụ động. Người dùng phải tự tìm kiếm địa điểm, tự căn chỉnh cự ly và tự ước lượng thời gian di chuyển mà không nhận được bất kỳ sự hỗ trợ nào từ thuật toán tối ưu hóa tuyến đường có nhận thức không gian.")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Để giải quyết khoảng trống giữa kỳ vọng của du khách và năng lực của các ứng dụng du lịch hiện hành, việc áp dụng trực tiếp các mô hình ngôn ngữ lớn thương mại hoặc các hệ thống Tăng cường Tạo sinh Truy xuất truyền thống (Naive RAG) vào miền du lịch địa phương tại Huế đang vấp phải ba thách thức kỹ thuật cốt lõi. Thách thức thứ nhất xuất phát từ hiện tượng ảo giác thực thể địa phương, khi mô hình thường xuyên tự bịa đặt tên các quán ăn không có thật tại Huế hoặc gán ghép sai lệch giữa đặc sản các vùng miền. Thách thức thứ hai là khiếm khuyết thiếu nhận thức không gian: bản chất của cơ chế tìm kiếm tương đồng véc-tơ thuần túy dựa trên ngữ nghĩa văn bản mà hoàn toàn không nắm bắt được tọa độ địa lý và rào cản sông Hương, dẫn đến các lịch trình gợi ý nhảy bờ liên tục vô lý hoặc đề xuất quán ăn cách xa hàng chục kilômét. Thách thức thứ ba nằm ở sự chia cắt giữa dữ liệu đánh giá thực tế và cấu trúc biểu diễn tri thức, khi hàng chục ngàn bài nhận xét phong phú của du khách chưa được khai phá và liên kết có cấu trúc vào đồ thị tri thức.")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Xuất phát từ những đòi hỏi thực tiễn của chính quyền thành phố Huế và khoảng trống học thuật nêu trên, đề tài Khóa luận tốt nghiệp được đề xuất nhằm nghiên cứu và xây dựng một khung giải pháp tích hợp đa tầng: kết hợp Đồ thị Tri thức Không gian với mô hình ngôn ngữ lớn cục bộ thông qua kiến trúc tác tử đa luồng Agentic RAG, qua đó trả lời một cách tự động và chuẩn xác ba câu hỏi cốt lõi: Đi đâu, ăn gì và lưu trú ở đâu phục vụ đắc lực cho công tác quảng bá du lịch Cố đô Huế.")

    add_sec_heading(doc, "2. Mục tiêu nghiên cứu")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Mục tiêu tổng quát của khóa luận là thiết kế, hiện thực hóa và đánh giá định lượng một hệ thống hỏi đáp và gợi ý lịch trình du lịch thông minh mang tên Spatial GraphRAG, kết hợp cấu trúc Đồ thị Tri thức Không gian, dữ liệu phản hồi thực tế của du khách và khung tác tử điều phối đa luồng trên nền tảng mô hình ngôn ngữ lớn cục bộ, nhằm cung cấp các đề xuất du lịch chuẩn xác về mặt thực thể và tối ưu về mặt cự ly địa lý tại thành phố Huế.")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Để hoàn thành mục tiêu tổng quát, nghiên cứu xác lập bốn mục tiêu cụ thể bao gồm: xây dựng Đồ thị Tri thức Không gian du lịch hoàn chỉnh cho Huế và các vùng phụ cận với quy mô hơn 9.500 nút thực thể và hơn 90.000 cạnh quan hệ ngữ nghĩa tích hợp tọa độ WGS84; xây dựng bộ từ điển ẩm thực Việt Nam gồm 570 món ăn và thiết lập giải thuật khai phá tri thức ngầm từ tập ngữ liệu 44.355 bài đánh giá du khách thực tế tại Huế trên TripAdvisor; thiết kế khung điều phối Agentic RAG trên LangGraph tích hợp bộ chấm điểm tin cậy và cơ chế phân luồng dự phòng vận hành trên mô hình cục bộ Qwen2.5-3B; và hiện thực hóa giải thuật lập lịch trình phân cụm địa lý, phát triển giao diện Web tương tác bản đồ số và đóng gói Cổng API RESTful chuẩn mở sẵn sàng tích hợp với nền tảng công dân số Hue-S.")

    add_sec_heading(doc, "3. Câu hỏi nghiên cứu và Giả thuyết khoa học")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Tiến trình nghiên cứu được định hướng bởi bốn câu hỏi nghiên cứu cốt lõi: làm thế nào để mô hình hóa mối quan hệ không gian giữa các điểm đến thành một Đồ thị Tri thức Không gian có khả năng truy vấn hiệu quả theo bán kính địa lý thực tế (RQ1); cơ chế trích xuất thực đơn ngầm từ hàng chục ngàn bài đánh giá văn bản có thể nâng cao độ chính xác gợi ý món ăn đặc sản so với phân loại tĩnh ở mức độ nào (RQ2); việc tích hợp Đồ thị Tri thức Không gian vào quy trình RAG có thể triệt tiêu hiện tượng ảo giác thực thể và giảm thiểu tỷ lệ vi phạm cự ly ra sao (RQ3); và khung tác tử LangGraph kết hợp mô hình ngôn ngữ cục bộ Qwen2.5-3B có đáp ứng được yêu cầu về thời gian phản hồi thời gian thực khi vận hành trên hạ tầng máy trạm tiêu chuẩn hay không (RQ4).")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Tương ứng với các câu hỏi trên, khóa luận xác lập bốn giả thuyết khoa học: ràng buộc topo không gian trong bán kính mặt cầu d <= 1,5 km sẽ triệt tiêu hoàn toàn các lộ trình ziczac nhảy bờ sông Hương, giảm cự ly di chuyển trung bình ít nhất 50% so với Naive RAG (H1); khai phá thực đơn ngầm cho phép mở rộng độ phủ món ăn đặc sản lên trên 90% (H2); mô hình Spatial GraphRAG đạt tỷ lệ bảo chứng thực thể 100% và tỷ lệ ảo giác 0% trên các truy vấn kiểm thử thuộc phạm vi đồ thị (H3); và quy trình phân cụm lịch trình kết hợp bộ lập lịch trình thông minh bảo đảm thời gian sinh kết quả dưới 4 giây trên GPU cá nhân (H4).")

    add_sec_heading(doc, "4. Đối tượng và Phạm vi nghiên cứu")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Đối tượng nghiên cứu của khóa luận là các phương pháp biểu diễn tri thức không gian, kỹ thuật Tăng cường Tạo sinh Truy xuất dựa trên đồ thị (GraphRAG), khung điều phối tác tử hội thoại thông minh và các giải thuật tối ưu hóa lịch trình du lịch dựa trên địa lý. Về mặt dữ liệu, đối tượng nghiên cứu bao gồm 9.525 thực thể điểm du lịch, ẩm thực, lưu trú và 44.355 bản ghi đánh giá du khách thực tế tại Huế thu thập từ TripAdvisor, kết hợp dữ liệu tọa độ hình học từ OpenStreetMap và Google Maps.")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Về phạm vi nghiên cứu, không gian địa lý trọng tâm của đề tài được định vị tại thành phố Huế và các vùng phụ cận thuộc tỉnh Thừa Thiên Huế như khu vực Kinh thành, cụm lăng tẩm phía Nam, đầm Chuồn, đầm phá Tam Giang, làng cổ Phước Tích và cầu ngói Thanh Toàn. Về mặt công nghệ, nghiên cứu tập trung vào mô hình ngôn ngữ cục bộ Qwen2.5-3B-Instruct vận hành qua môi trường Ollama trên GPU NVIDIA GeForce RTX 3050 (4GB VRAM), bảo đảm tính khả thi triển khai và vận hành tự chủ hoàn toàn tại các cơ quan, đơn vị địa phương.")

    add_sec_heading(doc, "5. Ý nghĩa khoa học và Thực tiễn")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Về mặt khoa học, khóa luận đóng góp một khung phương pháp luận mới kết hợp giữa tính toán không gian và GraphRAG, làm rõ cơ chế tích hợp khoảng cách mặt cầu Haversine vào cấu trúc đồ thị tri thức, đồng thời đề xuất giải pháp dung hợp giữa tri thức có cấu trúc của đồ thị và tri thức phi cấu trúc từ nhận xét du khách để định hướng quá trình suy luận của LLM mà không cần tái huấn luyện mô hình nền tảng. Về mặt thực tiễn, sản phẩm của đề tài cung cấp giải pháp trợ lý ảo thông minh giúp du khách tự lập kế hoạch du lịch tiết kiệm thời gian và chi phí, đồng thời sẵn sàng kết nối API vào nền tảng số Hue-S, hỗ trợ chính quyền địa phương giải quyết bài toán: Đi đâu, ăn gì, lưu trú ở đâu, điều tiết dòng khách du lịch hợp lý giữa các cụm di sản, góp phần bảo tồn di tích và thúc đẩy kinh tế đêm ổn định và dài hạn.")

    doc.add_page_break()

    # =========================================================================
    # PHẦN II. TỔNG QUAN VẤN ĐỀ NGHIÊN CỨU
    # =========================================================================
    add_part_heading(doc, "PHẦN II. TỔNG QUAN VẤN ĐỀ NGHIÊN CỨU")

    add_sec_heading(doc, "1. Cơ sở lý thuyết nền tảng")

    add_subsec_heading(doc, "1.1. Đồ thị Tri thức Không gian và Khoảng cách Mặt cầu")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Đồ thị Tri thức là một cấu trúc toán học biểu diễn tri thức dưới dạng đồ thị có hướng và có nhãn G = (V, E, R), trong đó V là tập hợp các nút đại diện cho các thực thể, R là tập hợp các kiểu quan hệ ngữ nghĩa, và E là tập hợp các cạnh định hướng dưới dạng bộ ba tri thức (h, r, t) phản ánh việc thực thể đầu h có mối quan hệ r với thực thể cuối t [5]. Trong miền du lịch, các thực thể bao gồm Điểm tham quan di tích (Attraction), Nhà hàng quán ăn (Restaurant), Cơ sở lưu trú (Hotel), Món ăn đặc sản (Dish) và Đơn vị hành chính (Locality). Đồ thị Tri thức Không gian mở rộng cấu trúc đồ thị truyền thống bằng cách tích hợp trực tiếp các thuộc tính tọa độ GPS vào từng nút thực thể, đồng thời thiết lập các cạnh liên kết hình học và topo dựa trên vị trí địa lý thực tế [6].")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Để đo lường khoảng cách địa lý giữa hai thực thể trên bề mặt cong của Trái Đất một cách chuẩn xác, công thức khoảng cách mặt cầu Haversine được áp dụng thay thế cho khoảng cách Euclid thông thường [8]: d = 2R * arcsin(sqrt(sin^2(Delta_phi / 2) + cos(phi_u) * cos(phi_v) * sin^2(Delta_lambda / 2))), trong đó R xấp xỉ 6.371 km là bán kính trung bình của Trái Đất, phi_u và phi_v là vĩ độ của hai địa điểm, Delta_phi và Delta_lambda lần lượt là độ chênh lệch vĩ độ và kinh độ. Dựa trên công thức này, một cạnh quan hệ lân cận không gian NEAR_BY được thiết lập tự động giữa hai thực thể nếu và chỉ nếu khoảng cách mặt cầu thỏa mãn điều kiện cự ly đi bộ d <= 1,5 km. Ngưỡng cự ly này tương ứng với thời gian đi bộ tối đa khoảng 15 đến 20 phút của du khách, bảo đảm tính khả thi cao trong việc kết hợp tham quan di tích và thưởng thức ẩm thực lân cận.")

    add_subsec_heading(doc, "1.2. Sự tiến hóa từ Naive RAG sang GraphRAG và Agentic RAG")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Kiến trúc Tăng cường Tạo sinh Truy xuất (RAG) được đề xuất ban đầu nhằm khắc phục hiện tượng ảo giác và bổ sung tri thức chuyên biệt cho LLM mà không cần tái huấn luyện toàn bộ trọng số mô hình [2]. Quá trình phát triển của RAG đã trải qua ba thế hệ tiến hóa phương pháp luận căn bản. Thế hệ thứ nhất là Naive RAG, hoạt động dựa trên nguyên lý phân đoạn văn bản thành các khối nhỏ (chunks), chuyển đổi thành véc-tơ đặc trưng thông qua mô hình nhúng ngữ nghĩa, và truy xuất bằng độ đo tương đồng Cosine. Nhược điểm chí tử của Naive RAG trong bài toán du lịch là tính chất hoàn toàn mù không gian: hệ thống chỉ đo lường sự tương đồng từ vựng bề mặt mà không nắm được cự ly vật lý, dễ dàng gợi ý một quán bún bò cách xa hơn 60 km chỉ vì bài đánh giá có nhiều từ khóa tích cực.")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Thế hệ thứ hai là GraphRAG, được tiên phong bởi Microsoft Research [3], khắc phục hạn chế trên bằng cách tổ chức tri thức dưới dạng đồ thị có cấu trúc, khai thác các đường đi liên kết trên đồ thị để tổng hợp tri thức đa chặng, giúp mô hình nắm bắt được mối quan hệ phân cấp giữa thành phố, phường xã, điểm di tích và các cơ sở kinh doanh lân cận. Thế hệ thứ ba là Agentic RAG, chuyển dịch sang mô hình tác tử tự chủ có khả năng tự suy ngẫm (Self-reflection), tự đánh giá chất lượng thông tin truy xuất (Confidence Grading), và định tuyến động giữa nhiều công cụ khác nhau [12]. Khi tri thức nội bộ từ đồ thị không đủ độ tin cậy để trả lời các sự kiện thời gian thực, tác tử có khả năng tự động rẽ nhánh sang công cụ tìm kiếm mạng nhằm bổ sung thông tin kịp thời.")

    add_subsec_heading(doc, "1.3. Khung điều phối trạng thái LangGraph và Mô hình cục bộ Qwen2.5")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Để hiện thực hóa kiến trúc Agentic RAG với khả năng kiểm soát luồng thực thi nghiêm ngặt, thư viện LangGraph được lựa chọn làm nền tảng điều phối [4]. Khác với các chuỗi xử lý một chiều tuần tự thông thường, LangGraph mô hình hóa toàn bộ quá trình xử lý như một Đồ thị Trạng thái hữu hạn (StateGraph) có chu trình. Trạng thái của hệ thống được đóng gói trong một cấu trúc dữ liệu chung chứa đựng toàn bộ ngữ cảnh bao gồm câu hỏi của du khách, các thực thể đã nhận diện, các nút đồ thị đã truy xuất, điểm số tin cậy và phản hồi tạo sinh cuối cùng. Các nút xử lý thực hiện các chức năng phân lập từ trích xuất thực thể, truy vấn đồ thị không gian, đánh giá độ tin cậy đến sinh câu trả lời, được điều khiển bởi các Cạnh có điều kiện dựa trên các ngưỡng xác suất toán học.")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Về mô hình suy luận ngôn ngữ, nghiên cứu tích hợp mô hình mã nguồn mở Qwen2.5-3B-Instruct do Alibaba Cloud phát triển [7], vận hành nội bộ thông qua môi trường thực thi Ollama trên máy trạm cá nhân. Qwen2.5-3B là mô hình ngôn ngữ thế hệ mới đạt năng lực vượt trội về khả năng hiểu tiếng Việt, tuân thủ chỉ dẫn định dạng có cấu trúc và khả năng suy luận logic trong phân khúc mô hình dưới 7 tỷ tham số. Việc vận hành mô hình hoàn toàn cục bộ trên GPU cá nhân (NVIDIA RTX 3050 với 4GB VRAM) bảo đảm ba ưu thế cốt tử: triệt tiêu 100% chi phí cuộc gọi API thương mại, bảo mật tuyệt đối dữ liệu người dùng, và bảo đảm tính sẵn sàng hoạt động ngoại tuyến phục vụ các kịch bản triển khai tại địa phương.")

    add_subsec_heading(doc, "1.4. Khai phá thực đơn ngầm và Bài toán Thiết kế Chuyến đi Du lịch")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Một trong những đóng góp lý thuyết quan trọng của đề tài là kỹ thuật Khai phá thực đơn ngầm (Implicit Menu Mining), kết hợp Bộ từ điển ẩm thực Việt Nam gồm 570 món ăn chuẩn hóa với thuật toán đối sánh chuỗi thực thể mờ trên tập ngữ liệu đánh giá du khách từ TripAdvisor [18]. Một cạnh quan hệ SERVES liên kết giữa nhà hàng và món ăn chỉ được hình thành trên đồ thị khi chỉ số tin cậy khai phá thực đơn Conf(u, m) vượt qua ngưỡng quy định 0,70 dựa trên tổng hợp đánh giá khen ngợi có trọng số sao. Bên cạnh đó, bài toán lập lịch trình đa ngày được mô hình hóa theo lý thuyết Thiết kế Chuyến đi Du lịch (Tourist Trip Design Problem – TTDP) dựa trên bài toán định tuyến có thưởng Orienteering Problem [13], trong đó giải thuật tối ưu hóa thứ tự di chuyển và cực đại hóa điểm trải nghiệm văn hóa ẩm thực trong khi vẫn khống chế chặt chẽ giới hạn thời gian và chi phí di chuyển giữa các cụm không gian.")

    doc.add_page_break()

    # =========================================================================
    # PHẦN III. ĐỐI TƯỢNG, PHẠM VI VÀ PHƯƠNG PHÁP NGHIÊN CỨU
    # =========================================================================
    add_part_heading(doc, "PHẦN III. ĐỐI TƯỢNG, PHẠM VI VÀ PHƯƠNG PHÁP NGHIÊN CỨU")

    add_sec_heading(doc, "1. Đối tượng và Thực trạng các nguồn dữ liệu nghiên cứu")

    add_subsec_heading(doc, "1.1. Hiện trạng đa nguồn dữ liệu và Quy mô tổng thể")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Nghiên cứu được thiết lập dựa trên một cơ sở dữ liệu đa nguồn tích hợp quy mô lớn, kết hợp chặt chẽ giữa thông tin tọa độ không gian chính xác, kho ngữ liệu nhận xét trải nghiệm thực tế từ cộng đồng du khách và hệ thống từ điển ẩm thực chuẩn hóa. Toàn bộ cơ sở dữ liệu được cấu thành từ bốn nguồn dữ liệu thành phần gồm: tập dữ liệu vị trí địa lý thu thập từ OpenStreetMap và Google Maps cho 9.525 thực thể du lịch toàn quốc (với 610 địa điểm trọng điểm tại Thừa Thiên Huế); kho ngữ liệu 1.692.415 bài đánh giá du khách trên TripAdvisor (với 44.355 bài đánh giá chuyên sâu tại 500 địa điểm ở Huế); Bộ từ điển ẩm thực Việt Nam gồm 570 món ăn đặc sản tiêu biểu; và cấu trúc Đồ thị Tri thức Không gian đạt quy mô 9.525 nút thực thể và 90.948 cạnh quan hệ.")

    add_table_caption(doc, "Bảng 1: Tổng mục các nguồn dữ liệu thành phần sử dụng trong nghiên cứu")
    tbl_data_summary = [
        ["Nguồn dữ liệu", "Định dạng tệp", "Quy mô bản ghi", "Mô tả phạm vi và đặc trưng nội dung"],
        ["TripAdvisor Toàn quốc", "SQLite / JSON", "1.692.415 bài", "Ngữ liệu đánh giá trải nghiệm du khách (2015 – 2026)"],
        ["TripAdvisor Huế", "JSON / Danh sách", "44.355 bài", "Đánh giá thực tế bóc tách tại 500 địa điểm ở Huế"],
        ["Địa điểm Du lịch Toàn quốc", "GeoJSON / CSV", "8.921 thực thể", "Tọa độ GPS, danh mục và địa chỉ đã làm sạch"],
        ["Địa điểm Du lịch tại Huế", "GeoJSON / JSON", "610 thực thể", "Thực thể du lịch, ẩm thực, lưu trú chuẩn hóa tại Huế"],
        ["Culinary Gazetteer", "JSON / Cấu trúc", "570 món ăn", "Từ điển thực đơn ẩm thực và biến thể nhận diện"],
        ["Đồ thị Tri thức Không gian", "NetworkX / PKL", "9.525 nút / 90.948 cạnh", "Đồ thị thực thể, topo lân cận và quan hệ thực đơn"]
    ]
    tbl1 = doc.add_table(rows=len(tbl_data_summary), cols=4)
    tbl1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_academic_table_borders(tbl1)
    for r_idx, row in enumerate(tbl_data_summary):
        for c_idx, val in enumerate(row):
            cell = tbl1.rows[r_idx].cells[c_idx]
            p_cell = cell.paragraphs[0]
            p_cell.paragraph_format.space_before = Pt(2)
            p_cell.paragraph_format.space_after = Pt(2)
            p_cell.paragraph_format.line_spacing = 1.15
            p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx != 2 else WD_ALIGN_PARAGRAPH.RIGHT
            r_c = p_cell.add_run(val)
            r_c.font.name = 'Times New Roman'
            r_c.font.size = Pt(10)
            if r_idx == 0:
                r_c.font.bold = True
                set_cell_background(cell, "EAECEF")
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Từ số liệu thống kê tại Bảng 1, việc kết hợp đa nguồn dữ liệu cho phép hệ thống khắc phục triệt để các hạn chế của từng nguồn đơn lẻ: dữ liệu bản đồ số bảo đảm tính chuẩn xác tuyệt đối về mặt tọa độ trắc địa, trong khi tập ngữ liệu hàng chục ngàn bài đánh giá cung cấp nguồn tri thức sống động về chất lượng dịch vụ và thị hiếu ẩm thực thực tế của du khách.")

    add_subsec_heading(doc, "1.2. Giải phẫu cấu trúc tập dữ liệu 44.355 bài đánh giá thực tế tại Huế")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Tập dữ liệu 44.355 bài nhận xét du khách tại Huế là nguồn tài nguyên cốt lõi phục vụ bài toán khai phá thực đơn ngầm và neo giữ ngữ cảnh cho mô hình ngôn ngữ lớn. Mỗi bản ghi nhận xét trong tệp dữ liệu được tổ chức theo một lược đồ cấu trúc thống nhất gồm tám trường thông tin thuộc tính chính từ URL địa điểm, URL người đánh giá, tiêu đề, bình luận chi tiết, điểm đánh giá sao, kiểu hình chuyến đi, thời điểm trải nghiệm và ngôn ngữ bài viết. Phân tích định lượng về phân bố điểm số đánh giá của tập ngữ liệu được tổng hợp chi tiết tại Bảng 2.")

    add_table_caption(doc, "Bảng 2: Phân bố xếp hạng sao của 44.355 bài đánh giá du lịch thực tế tại Huế")
    tbl_rating_data = [
        ["Mức xếp hạng (Rating)", "Số lượng bài viết", "Tỷ lệ phần trăm", "Ý nghĩa đánh giá và phân cực cảm xúc"],
        ["5.0 sao (Tuyệt hảo)", "31.877 bài", "71,87%", "Trải nghiệm rất hài lòng, khen ngợi sâu sắc về món ăn và dịch vụ"],
        ["4.0 sao (Rất tốt)", "7.867 bài", "17,74%", "Trải nghiệm tích cực, đánh giá cao chất lượng tổng thể"],
        ["3.0 sao (Trung bình)", "2.747 bài", "6,19%", "Mức độ hài lòng vừa phải, có một số điểm chưa ưng ý"],
        ["2.0 sao (Kém)", "974 bài", "2,20%", "Trải nghiệm không tốt về giá cả, vệ sinh hoặc thời gian chờ"],
        ["1.0 sao (Rất tệ)", "890 bài", "2,00%", "Đánh giá tiêu cực, phản ánh sự thất vọng nghiêm trọng"],
        ["Tổng cộng", "44.355 bài", "100,00%", "Điểm đánh giá trung bình toàn tập đạt 4,51 / 5,0 sao"]
    ]
    tbl2 = doc.add_table(rows=len(tbl_rating_data), cols=4)
    tbl2.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_academic_table_borders(tbl2)
    for r_idx, row in enumerate(tbl_rating_data):
        for c_idx, val in enumerate(row):
            cell = tbl2.rows[r_idx].cells[c_idx]
            p_cell = cell.paragraphs[0]
            p_cell.paragraph_format.space_before = Pt(2)
            p_cell.paragraph_format.space_after = Pt(2)
            p_cell.paragraph_format.line_spacing = 1.15
            p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx not in [1, 2] else WD_ALIGN_PARAGRAPH.RIGHT
            r_c = p_cell.add_run(val)
            r_c.font.name = 'Times New Roman'
            r_c.font.size = Pt(10)
            if r_idx == 0 or r_idx == len(tbl_rating_data) - 1:
                r_c.font.bold = True
                set_cell_background(cell, "EAECEF")
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Các số liệu thống kê tại Bảng 2 cho thấy một đặc tính thực nghiệm nổi bật: tỷ lệ bài đánh giá tích cực từ 4.0 sao trở lên chiếm tới 89,61% tổng số bài nhận xét, đưa điểm trung bình toàn mạng lưới đạt mức 4,51 sao. Điều này khẳng định sức hấp dẫn mạnh mẽ của du lịch và ẩm thực Huế đối với du khách, đồng thời chứng minh rằng tập ngữ liệu có mật độ thông tin khen ngợi đặc sản rất dày đặc, tạo điều kiện thuận lợi để giải thuật khai phá thực đơn ngầm bóc tách các món ăn làm nên thương hiệu của từng quán ăn.")

    add_table_caption(doc, "Bảng 3: Phân bố kiểu hình chuyến đi của du khách trong tập dữ liệu nhận xét tại Huế")
    tbl_trip_data = [
        ["Kiểu hình chuyến đi (Trip Type)", "Số lượng lượt", "Tỷ lệ phần trăm", "Đặc trưng hành vi và nhu cầu trải nghiệm"],
        ["Cặp đôi (Couples)", "13.994 lượt", "31,55%", "Ưu tiên không gian lãng mạn, ẩm thực tinh tế và ngắm cảnh"],
        ["Nhóm bạn bè (Friends)", "6.427 lượt", "14,49%", "Ưu tiên ẩm thực đường phố, trải nghiệm sôi động và khám phá"],
        ["Gia đình (Family)", "4.281 lượt", "9,65%", "Chú trọng sự tiện lợi, an toàn, lịch trình thong thả và quán ăn lớn"],
        ["Đi một mình (Solo)", "2.766 lượt", "6,24%", "Khám phá văn hóa sâu sắc, linh hoạt di chuyển bằng xe máy"],
        ["Công tác (Business)", "368 lượt", "0,83%", "Thời gian lưu trú ngắn, yêu cầu vị trí gần trung tâm hội nghị"],
        ["Không khai báo / Khác", "16.519 lượt", "37,24%", "Du khách không cung cấp phân loại nhóm chuyến đi"],
        ["Tổng cộng", "44.355 lượt", "100,00%", "Bao phủ 500 địa điểm dịch vụ du lịch trọng điểm tại Huế"]
    ]
    tbl3 = doc.add_table(rows=len(tbl_trip_data), cols=4)
    tbl3.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_academic_table_borders(tbl3)
    for r_idx, row in enumerate(tbl_trip_data):
        for c_idx, val in enumerate(row):
            cell = tbl3.rows[r_idx].cells[c_idx]
            p_cell = cell.paragraphs[0]
            p_cell.paragraph_format.space_before = Pt(2)
            p_cell.paragraph_format.space_after = Pt(2)
            p_cell.paragraph_format.line_spacing = 1.15
            p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx not in [1, 2] else WD_ALIGN_PARAGRAPH.RIGHT
            r_c = p_cell.add_run(val)
            r_c.font.name = 'Times New Roman'
            r_c.font.size = Pt(10)
            if r_idx == 0 or r_idx == len(tbl_trip_data) - 1:
                r_c.font.bold = True
                set_cell_background(cell, "EAECEF")
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Từ Bảng 3, trong số các bản ghi có khai báo rõ kiểu hình chuyến đi, nhóm du khách đi theo cặp đôi và nhóm bạn bè chiếm tỷ trọng áp đảo (hơn 46% tổng số). Thực tế này đặt ra yêu cầu hệ thống gợi ý lịch trình phải ưu tiên các chuỗi hành trình kết hợp hài hòa giữa tham quan di tích lịch sử ban ngày và trải nghiệm ẩm thực, phố đi bộ ven sông Hương vào buổi tối nhằm đáp ứng trúng thị hiếu của các phân khúc khách hàng chủ đạo.")

    add_table_caption(doc, "Bảng 4: Cơ cấu phân loại và phân bố địa giới của 610 địa điểm du lịch tại Huế")
    tbl_hue_places = [
        ["Tiêu chí phân loại địa điểm", "Số lượng thực thể", "Phạm vi không gian và địa danh tiêu biểu"],
        ["Phân loại theo danh mục dịch vụ:", "", ""],
        ["  Ẩm thực và Nhà hàng (Restaurant)", "477 cơ sở", "Quán bún bò, bánh bèo chén, cơm hến, nhà hàng cung đình"],
        ["  Cơ sở lưu trú và Khách sạn (Hotel)", "104 cơ sở", "Khách sạn trung tâm, homestay bờ sông, resort ven biển"],
        ["  Điểm tham quan danh thắng (Attraction)", "29 địa danh", "Đại Nội, Chùa Thiên Mụ, Lăng Tự Đức, Lăng Khải Định, Đồi Vọng Cảnh"],
        ["Phân loại theo địa giới hành chính:", "", ""],
        ["  Quận Thuận Hóa (Bờ Nam)", "388 địa điểm", "Khu vực bờ Nam sông Hương, phố đi bộ, trung tâm dịch vụ mới"],
        ["  Quận Phú Xuân (Bờ Bắc)", "183 địa điểm", "Khu vực bờ Bắc sông Hương, Quần thể Kinh thành, Chợ Đông Ba"],
        ["  Các huyện thị di sản phụ cận", "39 địa điểm", "Lăng Cô (Phú Lộc), Cầu ngói Thanh Toàn, Đầm Chuồn, Phước Tích"],
        ["Tổng cộng địa điểm tại Huế", "610 địa điểm", "100% đã chuẩn hóa tọa độ GPS theo hệ quy chiếu WGS84"]
    ]
    tbl4 = doc.add_table(rows=len(tbl_hue_places), cols=3)
    tbl4.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_academic_table_borders(tbl4)
    for r_idx, row in enumerate(tbl_hue_places):
        for c_idx, val in enumerate(row):
            cell = tbl4.rows[r_idx].cells[c_idx]
            p_cell = cell.paragraphs[0]
            p_cell.paragraph_format.space_before = Pt(2)
            p_cell.paragraph_format.space_after = Pt(2)
            p_cell.paragraph_format.line_spacing = 1.15
            p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx != 1 else WD_ALIGN_PARAGRAPH.RIGHT
            r_c = p_cell.add_run(val)
            r_c.font.name = 'Times New Roman'
            r_c.font.size = Pt(10)
            if r_idx in [0, 1, 5, len(tbl_hue_places) - 1]:
                r_c.font.bold = True
                if r_idx in [0, len(tbl_hue_places) - 1]:
                    set_cell_background(cell, "EAECEF")
            set_cell_margins(cell, top=50, bottom=50, left=70, right=70)

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Số liệu tại Bảng 4 làm sáng tỏ sự phân hóa địa lý sâu sắc của dịch vụ du lịch Huế: Quận Thuận Hóa ở bờ Nam sông Hương tập trung tới 63,61% tổng số cơ sở dịch vụ (chủ yếu là các nhà hàng, quán cà phê hiện đại và khách sạn cao tầng), trong khi Quận Phú Xuân ở bờ Bắc là cái nôi di sản chiếm 30,00% với mật độ dày đặc của các di tích triều Nguyễn và các quán ẩm thực truyền thống lâu đời. Sự phân bố này được trực quan hóa chi tiết thông qua biểu đồ cơ cấu tại Hình 3.")

    add_figure(doc, "hue_places_category.png", "Hình 3: Cơ cấu phân bố các danh mục địa điểm du lịch và dịch vụ tại thành phố Huế")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Từ Hình 3, sự áp đảo của phân khúc ẩm thực (chiếm gần 80% tổng số cơ sở dịch vụ) khẳng định vị thế của Huế như một kinh đô ẩm thực hàng đầu Việt Nam. Đi sâu vào phân tích 44.355 bài nhận xét, kết quả khai phá dữ liệu đã bóc tách được tần suất nhắc đến của các món ăn đặc sản tiêu biểu nhất tại Huế, được tổng hợp trên biểu đồ Hình 4.")

    add_figure(doc, "top10_dishes_hue.png", "Hình 4: Top 10 món ăn đặc sản Huế được du khách nhắc đến nhiều nhất trong tập ngữ liệu")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Quan sát Hình 4, Bún bò Huế dẫn đầu áp đảo về số lượt bảo chứng với hàng chục ngàn lượt nhắc đến tích cực, tiếp theo sau là Cơm hến, Bánh bèo, Bánh nậm, Bánh bột lọc, Bánh khoái, Nem lụi và Chè bột lọc heo quay. Sự định lượng khách quan này cung cấp cơ sở dữ liệu xác thực để hệ thống tự động ưu tiên gợi ý đúng những món ăn mang tính đặc trưng của Cố đô khi du khách đưa ra các câu hỏi mở về ẩm thực. Nhằm tối ưu hóa hiệu quả lưu trữ và truy xuất các ngữ cảnh này, quy trình phân mảnh văn bản phân tử (Atomic Chunking) được thiết lập và trực quan hóa tại Hình 5.")

    add_figure(doc, "atomic_chunking_pipeline.png", "Hình 5: Quy trình phân mảnh văn bản phân tử cho các bài nhận xét du khách")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Sơ đồ luồng trên Hình 5 mô tả quy trình phân mảnh văn bản phân tử gồm bốn bước xử lý liên hoàn: lọc bỏ nhiễu và làm sạch ngữ liệu nhận xét thô, phân tách câu văn chứa thực thể ẩm thực hoặc đánh giá dịch vụ, trích xuất điểm số phân cực cảm xúc kèm trọng số xếp hạng sao, và đóng gói thành các khối văn bản nguyên tử (Atomic Chunks) kèm siêu dữ liệu tọa độ GPS để lưu trữ vào ChromaDB và liên kết vào Đồ thị Tri thức Không gian.")

    doc.add_page_break()

    # =========================================================================
    # PHẦN IV. NỘI DUNG VÀ KẾT QUẢ NGHIÊN CỨU
    # =========================================================================
    add_part_heading(doc, "PHẦN IV. NỘI DUNG VÀ KẾT QUẢ NGHIÊN CỨU")

    # -------------------------------------------------------------------------
    # CHƯƠNG 1
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, "CHƯƠNG 1. KIẾN TRÚC HỆ THỐNG SPATIAL GRAPHRAG VÀ KHAI PHÁ THỰC ĐƠN NGẦM")

    add_sec_heading(doc, "1.1. Kiến trúc tổng thể bốn tầng của Hệ thống")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Để giải quyết đồng bộ các rào cản về ảo giác thực thể, sự bất định vị không gian và sự thiếu hụt dữ liệu đánh giá thực tế, khóa luận đề xuất một kiến trúc hệ thống hoàn chỉnh mang tên Spatial GraphRAG. Sơ đồ kiến trúc tổng thể được biểu diễn trực quan tại Hình 1.1.")

    add_figure(doc, "system_architecture.png", "Hình 1.1: Kiến trúc tổng thể bốn tầng của Hệ thống Spatial GraphRAG Du lịch Thông minh")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Quan sát sơ đồ kiến trúc trên Hình 1.1, hệ thống được tổ chức thành bốn tầng chức năng phân lập và tương tác lỏng lẻo. Tầng thứ nhất là Tầng Dữ liệu và Lưu trữ, chịu trách nhiệm quản lý cơ sở dữ liệu quan hệ SQLite lưu trữ 1,69 triệu bài nhận xét và hồ sơ thông tin chi tiết của 9.525 địa điểm du lịch, cơ sở dữ liệu véc-tơ ChromaDB lưu trữ các véc-tơ nhúng ngữ nghĩa, và cấu trúc Đồ thị Tri thức Không gian được biểu diễn tối ưu hóa trong bộ nhớ thông qua thư viện NetworkX.")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Tầng thứ hai là Tầng Tri thức và Đánh chỉ mục Không gian, cung cấp ba cơ chế chỉ mục cốt lõi gồm chỉ mục cự ly không gian Haversine phục vụ truy vấn lân cận nhanh trong bán kính 1,5 km, chỉ mục quan hệ thực đơn ẩm thực SERVES liên kết các nhà hàng với danh mục 570 món ăn đặc sản, và bộ mô hình nhúng ngữ nghĩa đa ngôn ngữ chuyển đổi câu hỏi thành véc-tơ đặc trưng. Tầng thứ ba là Tầng Điều phối Tác tử và Lập lịch trình, tích hợp máy trạng thái hữu hạn LangGraph để kiểm soát luồng hội thoại, bộ chấm điểm tin cậy, nhánh rẽ dự phòng tìm kiếm Internet, mô hình ngôn ngữ lớn cục bộ Qwen2.5-3B-Instruct thực thi suy luận ngữ cảnh, và bộ thuật toán Lập lịch trình phân cụm không gian. Tầng thứ tư là Tầng Ứng dụng và Tích hợp Giao diện, cung cấp Cổng API RESTful chuẩn mở trên FastAPI sẵn sàng tích hợp trực tiếp vào ứng dụng Hue-S của tỉnh Thừa Thiên Huế cùng giao diện Web tương tác bản đồ số hỗ trợ du khách tra cứu trực tiếp.")

    add_sec_heading(doc, "1.2. Thiết kế Đồ thị Tri thức Không gian Du lịch Huế")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Đồ thị Tri thức Không gian Du lịch Huế mô hình hóa không gian di sản Cố đô thông qua các lớp thực thể và quan hệ ngữ nghĩa topo, được biểu diễn qua lược đồ schema tại Hình 1.2.")

    add_figure(doc, "spatial_kg_schema.png", "Hình 1.2: Lược đồ cấu trúc thực thể và quan hệ trong Đồ thị Tri thức Không gian")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Từ lược đồ Hình 1.2, đồ thị tri thức định nghĩa năm lớp nút thực thể chính, bao gồm lớp Điểm tham quan (Attraction) đại diện cho các di tích lịch sử và danh lam cổ kính, lớp Cơ sở ẩm thực (Restaurant) bao quát các nhà hàng và quán ăn truyền thống, lớp Cơ sở lưu trú (Hotel) quản lý hệ thống khách sạn và homestay, lớp Món ăn đặc sản (Dish) chuẩn hóa 570 món ăn Cố đô, cùng lớp Khu vực địa lý (Locality) định danh các đơn vị hành chính xã phường. Giữa các thực thể này, cấu trúc đồ thị xác lập bốn mối quan hệ ngữ nghĩa cốt lõi, bao gồm quan hệ phân cấp địa giới LOCATED_IN định vị cơ sở trong phân vùng hành chính, quan hệ lân cận không gian NEAR_BY liên kết hai địa điểm có khoảng cách trắc địa Haversine d <= 1,5 km với trọng số cự ly vật lý thực tế, quan hệ phục vụ ẩm thực SERVES kết nối cơ sở ăn uống với món ăn đặc sản thông qua điểm bảo chứng thực đơn ngầm, và quan hệ phản hồi trải nghiệm HAS_REVIEW gắn kết thực thể với các khối nhận xét phân tử của du khách.")

    add_table_caption(doc, "Bảng 1.1: Thống kê định lượng các thành phần trong Đồ thị Tri thức Không gian")
    tbl_kg_stats = [
        ["Lớp thực thể (Entity Type)", "Số lượng nút", "Loại quan hệ (Relation)", "Số lượng cạnh"],
        ["Attraction (Điểm tham quan)", "1.842", "NEAR_BY (Lân cận <= 1,5 km)", "64.218"],
        ["Restaurant (Ẩm thực, quán ăn)", "4.120", "SERVES (Phục vụ món ăn)", "14.850"],
        ["Hotel (Lưu trú, khách sạn)", "2.650", "LOCATED_IN (Thuộc địa phương)", "9.525"],
        ["Dish (Món ăn đặc sản)", "570", "HAS_REVIEW (Liên kết nhận xét)", "2.355"],
        ["Locality (Đơn vị địa lý)", "343", "--", "--"],
        ["Tổng số nút thực thể", "9.525", "Tổng số cạnh quan hệ", "90.948"]
    ]
    tbl_kg = doc.add_table(rows=len(tbl_kg_stats), cols=4)
    tbl_kg.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_academic_table_borders(tbl_kg)
    for r_idx, row in enumerate(tbl_kg_stats):
        for c_idx, val in enumerate(row):
            cell = tbl_kg.rows[r_idx].cells[c_idx]
            p_cell = cell.paragraphs[0]
            p_cell.paragraph_format.space_before = Pt(2)
            p_cell.paragraph_format.space_after = Pt(2)
            p_cell.paragraph_format.line_spacing = 1.15
            p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx not in [1, 3] else WD_ALIGN_PARAGRAPH.RIGHT
            r_c = p_cell.add_run(val)
            r_c.font.name = 'Times New Roman'
            r_c.font.size = Pt(10)
            if r_idx == 0 or r_idx == len(tbl_kg_stats) - 1:
                r_c.font.bold = True
                set_cell_background(cell, "EAECEF")
            set_cell_margins(cell, top=50, bottom=50, left=70, right=70)

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Quy mô định lượng tại Bảng 1.1 chứng minh rằng hơn 70% số cạnh trong đồ thị là các liên kết không gian NEAR_BY, phản ánh mật độ kết nối dày đặc giữa các dịch vụ du lịch trong bán kính đi bộ. Cấu trúc mạng lưới này cho phép giải thuật tìm kiếm thực hiện duyệt đồ thị theo chiều sâu hoặc chiều rộng trong thời gian dưới 10 mili-giây, tạo tiền đề để hệ thống lọc sạch các địa điểm ở xa trước khi chuyển ngữ cảnh cho mô hình ngôn ngữ lớn.")

    add_sec_heading(doc, "1.3. Phương pháp khai phá thực đơn ngầm và đối soát tri thức")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Để giải quyết bài toán menu tĩnh và lấp đầy các khoảng trống thông tin về món ăn đặc sản, nghiên cứu ứng dụng quy trình khai phá dữ liệu nhận xét dựa trên Bộ từ điển ẩm thực 570 món ăn. Mỗi bài nhận xét của du khách được quét qua một bộ lọc đối sánh thực thể xâu chuỗi kết hợp bộ quy tắc khử nhiễu từ đồng âm. Cạnh quan hệ SERVES chỉ được xác lập chính thức trên đồ thị khi chỉ số tin cậy khai phá vượt qua ngưỡng quy định 0,70 và số lượng bài nhận xét khen ngợi tối thiểu từ 3 du khách độc lập trở lên. Bảng 1.2 minh họa mẫu kết quả đối soát tiêu biểu.")

    add_table_caption(doc, "Bảng 1.2: Mẫu đối soát kết quả khai phá thực đơn ngầm từ nhận xét du khách tại Huế")
    tbl_menu_mined = [
        ["Tên quán ăn thực tế", "Địa chỉ tại Huế", "Món đặc sản khai phá từ Reviews", "Số lượt bảo chứng"],
        ["Bún bò Mụ Rơi", "40 Nguyễn Chí Diểu", "Bún bò giò heo, Chả cua, Gân bò", "342 lượt"],
        ["Bánh bèo Bà Đỏ", "08 Nguyễn Bỉnh Khiêm", "Bánh bèo chén, Bánh nậm, Bánh lọc gói", "518 lượt"],
        ["Cơm hến Hoa Đông", "64 kiệt 7 Ưng Bình", "Cơm hến, Bún hến, Mì hến, Chè bắp", "412 lượt"],
        ["Quán Hạnh", "11 Phù Đổng Thiên Vương", "Bánh khoái, Nem lụi, Cuốn thịt nướng", "685 lượt"],
        ["Chè Hẻm", "01 kiệt 29 Hùng Vương", "Chè bột lọc heo quay, Chè hạt sen", "294 lượt"]
    ]
    tbl_menu = doc.add_table(rows=len(tbl_menu_mined), cols=4)
    tbl_menu.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_academic_table_borders(tbl_menu)
    for r_idx, row in enumerate(tbl_menu_mined):
        for c_idx, val in enumerate(row):
            cell = tbl_menu.rows[r_idx].cells[c_idx]
            p_cell = cell.paragraphs[0]
            p_cell.paragraph_format.space_before = Pt(2)
            p_cell.paragraph_format.space_after = Pt(2)
            p_cell.paragraph_format.line_spacing = 1.15
            p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx != 3 else WD_ALIGN_PARAGRAPH.RIGHT
            r_c = p_cell.add_run(val)
            r_c.font.name = 'Times New Roman'
            r_c.font.size = Pt(10)
            if r_idx == 0:
                r_c.font.bold = True
                set_cell_background(cell, "EAECEF")
            set_cell_margins(cell, top=50, bottom=50, left=70, right=70)

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Bảng 1.2 chứng minh rằng quy trình khai phá dữ liệu đã bóc tách chính xác các món ăn cốt lõi làm nên thương hiệu của từng quán. Những thông tin này hoàn toàn không có trong danh bạ phân loại kinh doanh chung (vốn chỉ phân loại chung là Nhà hàng Việt Nam), chứng minh tính đúng đắn của Giả thuyết H2 về khả năng làm giàu tri thức ẩm thực địa phương từ dữ liệu du khách.")

    add_sec_heading(doc, "1.4. Khung điều phối tác tử tự suy ngẫm Agentic RAG trên LangGraph")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Kiến trúc tác tử tự suy ngẫm được thiết kế dựa trên máy trạng thái hữu hạn LangGraph StateGraph, được biểu diễn qua sơ đồ luồng điều phối tại Hình 1.3.")

    add_figure(doc, "langgraph_architecture.png", "Hình 1.3: Kiến trúc Đồ thị Trạng thái điều phối quy trình Agentic RAG trên LangGraph")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Quan sát sơ đồ Hình 1.3, quy trình điều phối bắt đầu từ nút trích xuất thực thể và ý định người dùng (Extract Entity & Intent), chuyển tiếp sang nút truy vấn Đồ thị Tri thức Không gian (Spatial KG Retrieval). Kết quả truy xuất được đưa vào nút chấm điểm tin cậy (Grade Retrieval): nếu điểm tin cậy đạt ngưỡng (>= 0,70), hệ thống kích hoạt nút sinh câu trả lời bằng mô hình Qwen2.5-3B; ngược lại nếu điểm tin cậy dưới ngưỡng, tác tử tự động kích hoạt Cạnh có điều kiện rẽ nhánh sang công cụ tìm kiếm mạng DuckDuckGo Search để bổ sung dữ liệu thời gian thực trước khi tổng hợp phản hồi cuối cùng.")

    add_sec_heading(doc, "1.5. Tầng Lưu trữ Đám mây NoSQL và Quản trị Đa phiên Hội thoại")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Bên cạnh các cơ sở dữ liệu quan hệ truyền thống và cơ sở dữ liệu véc-tơ phục vụ lưu trữ tri thức tĩnh, việc quản lý trạng thái tương tác động của du khách (lịch sử trò chuyện đa phiên, các hành trình được đánh dấu lưu trữ và phản hồi đánh giá trải nghiệm) đòi hỏi một mô hình lưu trữ phân tán linh hoạt và có khả năng mở rộng cao. Hệ thống tích hợp nền tảng Google Firebase, đặc biệt là cơ sở dữ liệu hướng tài liệu NoSQL Google Cloud Firestore [20, 24, 25]. Dữ liệu được tổ chức dưới dạng cây phân cấp gồm ba bộ sưu tập cốt lõi được đặc tả tại Bảng 1.4.")

    add_table_caption(doc, "Bảng 1.4: Lược đồ cấu trúc dữ liệu trên Google Cloud Firestore phục vụ quản lý đa phiên và phản hồi")
    tbl_firestore_data = [
        ["Bộ sưu tập (Collection)", "Trường dữ liệu chính", "Kiểu dữ liệu", "Mục đích sử dụng nghiệp vụ"],
        ["chat_sessions", "sessionId, userId\ntitle\nmessages[]\nupdatedAt", "String\nString\nArray[Object]\nTimestamp", "Lưu trữ định danh phiên, tiêu đề đối thoại tự động bóc tách từ câu hỏi đầu, mảng các tin nhắn đối thoại kèm lộ trình và thời gian cập nhật."],
        ["saved_itineraries", "itineraryId, userId\ntitle, days\nplaces[]\ntotalDistanceKm", "String\nString, Number\nArray[Object]\nNumber", "Lưu trữ các lộ trình du lịch hoàn chỉnh do du khách chủ động đánh dấu lưu lại, bao gồm danh sách các điểm dừng, cự ly và ước tính chi phí."],
        ["ai_feedbacks", "feedbackId, userId\nrating\nprompt, response\ntimestamp", "String\nString\nString\nTimestamp", "Ghi nhận phản hồi đánh giá chất lượng (like hoặc dislike) của du khách đối với từng câu trả lời của tác tử thông minh phục vụ học tăng cường RLHF."]
    ]
    tbl_fs = doc.add_table(rows=len(tbl_firestore_data), cols=4)
    tbl_fs.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_academic_table_borders(tbl_fs)
    for r_idx, row in enumerate(tbl_firestore_data):
        for c_idx, val in enumerate(row):
            cell = tbl_fs.rows[r_idx].cells[c_idx]
            p_cell = cell.paragraphs[0]
            p_cell.paragraph_format.space_before = Pt(2)
            p_cell.paragraph_format.space_after = Pt(2)
            p_cell.paragraph_format.line_spacing = 1.15
            p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r_c = p_cell.add_run(val)
            r_c.font.name = 'Times New Roman'
            r_c.font.size = Pt(9.5)
            if r_idx == 0:
                r_c.font.bold = True
                set_cell_background(cell, "EAECEF")
            set_cell_margins(cell, top=50, bottom=50, left=70, right=70)

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Cấu trúc phân tầng tại Bảng 1.4 cho phép hệ thống phân lập hoàn toàn giữa dữ liệu hội thoại tức thời và dữ liệu lộ trình dài hạn, bảo đảm tốc độ truy vấn đọc ghi luôn duy trì dưới 80 mili-giây trên quy mô hàng ngàn phiên làm việc đồng thời. Quá trình tương tác của du khách được kiểm soát thông qua một cơ chế vòng đời phiên hội thoại bốn giai đoạn chặt chẽ: khởi tạo phiên mới (startNewChatSession) làm sạch giao diện và kích hoạt resetToDefaultState đưa bản đồ về trung tâm Huế; ghi nhận và kiên định hóa tự động (persistActiveSession) lưu đè bất đồng bộ lên Firestore; khôi phục phiên lịch sử (restoreChatSession) tái tạo các thẻ lộ trình trực quan kèm nút vẽ lại bản đồ (btn-nav-replot); và xóa phiên an toàn (deleteChatSession) thẩm định quyền sở hữu dữ liệu qua mã thông báo JWT [26].")

    add_sec_heading(doc, "1.6. Thiết kế Giao diện Khách Web Tương tác Không gian (Gemini-Style Client)")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Kế thừa các chuẩn mực thiết kế tương tác hiện đại từ các hệ thống trợ lý AI hàng đầu, hệ thống phát triển giao diện Web tích hợp bản đồ số thông minh với thanh bên điều hướng thích ứng hai trạng thái [27]: trạng thái mở rộng 280 pixel cung cấp đầy đủ danh mục phiên chat, widget thời tiết và nút khởi tạo mới dạng viên thuốc bo tròn (Gemini Pill Button); trạng thái thu gọn 52 pixel (Icon Rail) tối giản hóa thành các biểu tượng 36 pixel căn giữa kèm nhãn chỉ dẫn nổi thông minh khi rê chuột (Hover Tooltips); và chế độ ngăn kéo trượt (Slide-over Drawer) trên thiết bị di động có chiều ngang dưới 1024 pixel.")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Nhằm nâng cao tính khả thi thực tế của lộ trình trong điều kiện khí hậu đặc thù của Cố đô Huế, hệ thống tích hợp tiện ích khí tượng thời gian thực kết nối giao diện lập trình Open-Meteo [22] tại tọa độ trắc địa trung tâm thành phố Huế (16,4637 độ Bắc, 107,5909 độ Đông). Bộ tham số bao gồm nhiệt độ không khí T (độ C), độ ẩm tương đối H (%), lượng mưa tích lũy P (mm) và mã thời tiết chuẩn WMO Code Table 4677 [23]. Chi tiết ma trận quy tắc thích ứng lộ trình theo ngữ cảnh khí tượng được tổng hợp tại Bảng 1.5 [21].")

    add_table_caption(doc, "Bảng 1.5: Ma trận Quy tắc Thích ứng Lộ trình theo Ngữ cảnh Khí tượng Cố đô Huế")
    tbl_weather_data = [
        ["Mã WMO", "Nhiệt độ T", "Lượng mưa P", "Ngữ cảnh môi trường", "Chiến lược Thích ứng Gợi ý"],
        ["0, 1, 2", "20°C <= T <= 28°C", "0 mm", "Trời quang đãng, mát mẻ", "Ưu tiên các quần thể di tích ngoài trời và danh thắng tự nhiên (Đại Nội, Chùa Thiên Mụ, Đồi Vọng Cảnh, Lăng Khải Định)."],
        ["0, 1", "T > 33°C", "0 mm", "Nắng nóng gay gắt", "Khuyến nghị hạn chế di chuyển ngoài trời giữa trưa, ưu tiên di tích có bóng râm hoặc không gian trưng bày trong nhà (Cung An Định, Bảo tàng Cổ vật Cung đình), đề xuất các quán cà phê ven sông Hương và ẩm thực chè thanh nhiệt."],
        ["51--67", "Mọi giá trị T", "P > 0 mm", "Mưa dầm đặc trưng", "Cảnh báo trang bị ô dù, tái cấu trúc lộ trình ưu tiên các di tích có hành lang và mái che liên hoàn, gợi ý dừng chân trải nghiệm ẩm thực nóng ấm (Bún bò Huế, Bánh canh Nam Phổ, Bánh khoái)."],
        ["80--99", "Mọi giá trị T", "P >= 5 mm", "Mưa rào hoặc dông sét", "Phát tín hiệu cảnh báo an toàn, tạm dừng các tuyến tham quan đồi núi và sông nước, đề xuất chuyển hướng sang không gian văn hóa ẩm thực trong nhà an toàn."]
    ]
    tbl_w = doc.add_table(rows=len(tbl_weather_data), cols=5)
    tbl_w.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_academic_table_borders(tbl_w)
    for r_idx, row in enumerate(tbl_weather_data):
        for c_idx, val in enumerate(row):
            cell = tbl_w.rows[r_idx].cells[c_idx]
            p_cell = cell.paragraphs[0]
            p_cell.paragraph_format.space_before = Pt(2)
            p_cell.paragraph_format.space_after = Pt(2)
            p_cell.paragraph_format.line_spacing = 1.15
            p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r_c = p_cell.add_run(val)
            r_c.font.name = 'Times New Roman'
            r_c.font.size = Pt(9.5)
            if r_idx == 0:
                r_c.font.bold = True
                set_cell_background(cell, "EAECEF")
            set_cell_margins(cell, top=50, bottom=50, left=60, right=60)

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Ma trận quy tắc tại Bảng 1.5 cung cấp cơ chế lập luận ngữ cảnh trực tiếp cho tác tử thông minh, bảo đảm các kế hoạch tham quan do mô hình ngôn ngữ lớn tổng hợp luôn dung hòa chặt chẽ giữa cự ly di chuyển tối ưu và mức độ an toàn thoải mái sinh học của du khách. Về mặt xác thực danh tính, hệ thống triển khai cơ chế đa kênh linh hoạt: Đăng nhập một chạm Google OAuth 2.0; Xác thực qua Email/Mật khẩu; và Chế độ Khách vãng lai (Guest Demo Mode). Menu tài khoản được thiết kế dưới dạng khung cửa sổ nổi Popover định vị ngay trên chip tài khoản, kết hợp Hộp thoại cấu hình Firebase động (firebase-config-modal) cho phép nạp trực tiếp khóa API Key cá nhân qua giao diện web và lưu bền vững vào localStorage của trình duyệt mà không cần biên dịch lại mã nguồn.")

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # CHƯƠNG 2
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, "CHƯƠNG 2. THUẬT TOÁN LẬP LỊCH TRÌNH KHÔNG GIAN, THỰC NGHIỆM ĐỐI SÁNH VÀ TÍCH HỢP ỨNG DỤNG")

    add_sec_heading(doc, "2.1. Thuật toán Lập lịch trình phân cụm không gian")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Thành phố Huế sở hữu một đặc trưng địa lý tự nhiên chi phối toàn bộ cấu trúc giao thông đô thị: sông Hương chảy qua trung tâm, chia cắt thành phố thành hai bờ Bắc và bờ Nam với số lượng cầu kết nối có hạn. Bờ Bắc là không gian văn hóa di sản cung đình cổ kính tập trung xung quanh Quần thể Kinh thành Huế, Chùa Thiên Mụ và Chợ Đông Ba; trong khi bờ Nam là khu đô thị hiện đại và hành lang phát triển về phía các quần thể lăng tẩm triều Nguyễn cùng các làng nghề truyền thống. Nếu du khách lập lịch trình di chuyển xen kẽ tùy tiện giữa hai bờ trong cùng một buổi, thời gian lãng phí cho việc vượt cầu qua lại và nguy cơ tắc nghẽn giao thông giờ cao điểm sẽ làm giảm sút nghiêm trọng trải nghiệm du lịch. Nhằm khắc phục triệt để hiện tượng này, giải thuật phân chia không gian du lịch Huế thành ba cụm địa lý độc lập gồm: Cụm bờ Bắc (di sản Kinh thành và cổ tự trong bán kính 3 km), Cụm bờ Nam (lăng tẩm vương triều và làng nghề dọc trục Huyền Trân Công Chúa), và Cụm ngoại ô (vùng đầm phá Tam Giang, làng chài Đầm Chuồn và cầu ngói Thanh Toàn). Kịch bản luồng tương tác và gợi ý lịch trình được trực quan hóa trên Hình 2.1.")

    add_figure(doc, "user_scenario_demo_flow.png", "Hình 2.1: Kịch bản luồng tương tác và gợi ý lịch trình phân cụm không gian của hệ thống")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Từ sơ đồ kịch bản trên Hình 2.1, quy trình tính toán vận hành tuần tự qua ba giai đoạn liên hoàn: khởi đầu bằng việc lựa chọn cụm không gian tối ưu cho từng ngày tham quan (tour 1 ngày ưu tiên sáng bờ Bắc, chiều bờ Nam; tour 2 đến 3 ngày phân bổ trọn vẹn mỗi cụm cho một ngày); tiếp theo sắp xếp thứ tự tham quan thông qua phương pháp tham lam kết hợp tìm kiếm cục bộ Greedy Nearest Neighbor với 2-Opt refinement nhằm cực tiểu hóa tổng quãng đường di chuyển dựa trên ma trận khoảng cách Haversine; và cuối cùng thực hiện ghép nối ẩm thực tự động tại các mốc nghỉ trưa và chiều tối bằng cách kích hoạt truy vấn đồng thời quan hệ lân cận không gian NEAR_BY và quan hệ phục vụ món ăn SERVES trong bán kính d <= 1,5 km.")

    add_sec_heading(doc, "2.2. Bộ kiểm thử Benchmark 12 kịch bản du lịch Huế")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Khác với các bộ dữ liệu kiểm thử hỏi đáp du lịch thông thường trên thế giới vốn chỉ tập trung vào sự tương đồng ngữ nghĩa từ vựng mà bỏ qua yếu tố không gian, nghiên cứu này xây dựng một Bộ dữ liệu kiểm thử chuẩn (Benchmark Test Suite) gồm 12 kịch bản thực tế đại diện tại Cố đô Huế. Mỗi kịch bản đòi hỏi hệ thống phải đồng thời giải quyết ba tầng bài toán kỹ thuật: bóc tách chính xác thực thể địa danh và món ăn đặc sản từ tiếng Việt tự nhiên; định vị và tra cứu đồ thị không gian trong bán kính vật lý cho phép; và lập luận đề xuất lời giải tối ưu không vi phạm rào cản sông Hương. Toàn bộ 12 kịch bản được phân bổ có chủ đích vào ba nhóm bài toán nghiệp vụ cốt lõi: Nhóm 1 từ TC-01 đến TC-04 tập trung vào truy vấn ẩm thực kết hợp ràng buộc không gian đi bộ; Nhóm 2 từ TC-05 đến TC-08 hướng đến việc khám phá danh thắng không gian lân cận theo trục giao thông; và Nhóm 3 từ TC-09 đến TC-12 giải quyết bài toán lập lịch trình du lịch đa ngày tổng hợp.")

    add_table_caption(doc, "Bảng 2.1: Đặc tả chi tiết 12 kịch bản trong Bộ dữ liệu kiểm thử chuẩn (Benchmark Suite) cho du lịch Huế")
    tbl_bench_specs = [
        ["Mã", "Câu hỏi truy vấn của du khách (Prompt)", "Điểm neo (Anchor POI)", "Món / Dịch vụ yêu cầu", "Kết quả kỳ vọng và Tiêu chuẩn nghiệm đúng"],
        ["TC-01", "Tôi đang ở Đại Nội Huế, muốn tìm quán bún bò chuẩn vị gần đây để đi bộ ăn trưa.", "Đại Nội Huế (Cửa Thượng Tứ, bờ Bắc)", "Bún bò Huế", "Gợi ý quán bún bò có thật ở bờ Bắc (Bún bò Mụ Rơi, Bún bò Cẩm, Bún bò Đông Ba); cự ly d <= 1,5 km; tuyệt đối không gợi ý nhảy qua cầu sang bờ Nam."],
        ["TC-02", "Sau khi tham quan Lăng Tự Đức, tôi muốn ăn bánh bèo hoặc bánh nậm gần đó thì ghé quán nào?", "Lăng Tự Đức (Thôn Thượng 2, Thủy Xuân)", "Bánh bèo, bánh nậm Huế", "Gợi ý quán bánh bèo/nậm trên trục Lê Ngô Cát hoặc Huyền Trân Công Chúa (Quán Bánh Chi, Bánh Thủy Xuân); cự ly d <= 1,5 km; loại trừ quán Bà Đỏ (> 5 km)."],
        ["TC-03", "Tôi đang ở khu vực Cồn Hến, muốn thưởng thức cơm hến và chè bắp đúng gốc Huế.", "Cồn Hến (Phường Vĩ Dạ)", "Cơm hến, chè bắp Cồn Hến", "Gợi ý đúng quán cơm hến truyền thống tại đảo Cồn Hến (Hoa Đông, Quán Nhỏ); cự ly d <= 800 m; xác thực có bán đồng thời cả hai món với Conf >= 0,75."],
        ["TC-04", "Gợi ý quán bánh khoái và nem lụi ngon ở bờ Nam gần khu phố Tây Chu Văn An.", "Phố đi bộ Chu Văn An – Võ Thị Sáu", "Bánh khoái, nem lụi Huế", "Gợi ý quán bánh khoái, nem lụi bờ Nam trong cự ly d <= 1,2 km (Bánh khoái Hạnh đường Phó Đức Chính); không nhầm sang quán bún bò hay cà phê lân cận."],
        ["TC-05", "Tôi vừa ghé Chùa Thiên Mụ, xung quanh đây có điểm văn hóa nào có thể ghé tiếp theo không?", "Chùa Thiên Mụ (Đồi Hà Khê, bờ Bắc)", "Di tích, điểm văn hóa kế cận", "Gợi ý các điểm văn hóa cùng hành lang thượng nguồn bờ Bắc trong cự ly d <= 2,0 km (Văn Thánh Huế, Nhà vườn An Hiên, Bến Kim Long); không điều hướng sang lăng tẩm bờ Nam."],
        ["TC-06", "Từ Đồi Vọng Cảnh, có những di tích lăng tẩm hoặc làng nghề nào nằm gần trên cùng trục đường?", "Đồi Vọng Cảnh (Đường Huyền Trân Công Chúa)", "Lăng tẩm và làng nghề truyền thống", "Gợi ý các điểm thuộc Cụm bờ Nam liên kết trên trục giao thông trong cự ly d <= 2,5 km (Lăng Tự Đức, Lăng Đồng Khánh, Làng hương Thủy Xuân); thứ tự di chuyển logic."],
        ["TC-07", "Tôi đang ở Chợ Đông Ba, muốn tìm các điểm di tích có thể đi bộ tham quan trong 15 phút.", "Chợ Đông Ba (Đường Trần Hưng Đạo)", "Di tích lịch sử cự ly đi bộ ngắn", "Gợi ý các điểm văn hóa cửa ngõ Đông Nam Kinh thành trong cự ly d <= 1,2 km (Cầu Trường Tiền, Cửa Thượng Tứ, Bảo tàng Cổ vật Cung đình); không gợi ý Chùa Thiên Mụ (> 5 km)."],
        ["TC-08", "Khám phá danh thắng thiên nhiên và sinh thái đầm phá ở ngoại ô phía Đông Nam thành phố Huế.", "Đầm Chuồn (Phá Tam Giang, Phú Vang)", "Du lịch sinh thái dã ngoại, làng chài", "Gợi ý chuỗi liên kết ngoại ô: Làng chài Đầm Chuồn (ẩm thực cá kình đầm phá), kết hợp tham quan Cầu ngói Thanh Toàn trên cùng hành lang sinh thái; hướng dẫn phương tiện di chuyển."],
        ["TC-09", "Thiết kế lịch trình du lịch Huế 1 ngày trọn vẹn cho cặp đôi, xuất phát từ khách sạn bờ Nam.", "Khách sạn trung tâm bờ Nam TP. Huế", "Lịch trình 1 ngày tối ưu không gian", "Chia 2 buổi rành mạch: Sáng khám phá Cụm Kinh thành bờ Bắc (Đại Nội, Chùa Thiên Mụ, ăn bún bò); Chiều về Cụm Lăng tẩm bờ Nam (Làng hương, Lăng Tự Đức); vượt sông tối đa 1 lần/ngày."],
        ["TC-10", "Lập lịch trình 2 ngày khám phá Huế theo phong cách văn hóa sâu sắc và ẩm thực truyền thống.", "Không gian đô thị Cố đô Huế", "Lịch trình 2 ngày phân cụm triệt để", "Ngày 1 dành trọn vẹn bờ Bắc (Đại Nội, Bảo tàng Cổ vật, Nhà vườn, ẩm thực chợ Đông Ba); Ngày 2 dành trọn bờ Nam (Lăng Tự Đức, Khải Định, Đồi Vọng Cảnh, ẩm thực Cồn Hến); 0 lần đổi bờ mỗi ngày."],
        ["TC-11", "Gợi ý lịch trình 3 ngày tại Huế kết hợp di sản Cố đô và du lịch dã ngoại thiên nhiên sinh thái.", "Cố đô Huế và vùng phụ cận đầm phá", "Lịch trình 3 ngày mở rộng ngoại ô", "Ngày 1: Quần thể di sản Kinh thành bờ Bắc; Ngày 2: Lăng tẩm triều Nguyễn bờ Nam; Ngày 3: Vùng sinh thái Cầu ngói Thanh Toàn và Đầm Chuồn; thời gian biểu khoa học, không quay vòng ngược đường."],
        ["TC-12", "Lập tour nửa ngày (chiều từ 14h đến 19h) ngắm hoàng hôn và thưởng thức ẩm thực đêm xứ Huế.", "Trục đồi Tây Nam bờ Nam (Thủy Xuân)", "Tour bán nhật chiều – tối chi tiết", "Chuỗi mốc giờ chặt chẽ: 14h00 Làng hương -> 15h30 Lăng Tự Đức -> 17h00 hoàng hôn Đồi Vọng Cảnh -> 18h30 ẩm thực đặc sản bánh Huế bờ Nam; các điểm cách nhau < 2,5 km, tổng di chuyển < 20 phút."]
    ]
    tbl_bench = doc.add_table(rows=len(tbl_bench_specs), cols=5)
    tbl_bench.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_academic_table_borders(tbl_bench)
    for r_idx, row in enumerate(tbl_bench_specs):
        for c_idx, val in enumerate(row):
            cell = tbl_bench.rows[r_idx].cells[c_idx]
            p_cell = cell.paragraphs[0]
            p_cell.paragraph_format.space_before = Pt(2)
            p_cell.paragraph_format.space_after = Pt(2)
            p_cell.paragraph_format.line_spacing = 1.15
            p_cell.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT
            r_c = p_cell.add_run(val)
            r_c.font.name = 'Times New Roman'
            r_c.font.size = Pt(9.5)
            if r_idx == 0:
                r_c.font.bold = True
                set_cell_background(cell, "EAECEF")
            set_cell_margins(cell, top=50, bottom=50, left=60, right=60)

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Từ dữ liệu đặc tả tại Bảng 2.1, quy trình chấm điểm và đánh giá nghiệm đúng cho từng kịch bản được thiết lập chặt chẽ dựa trên các tiêu chuẩn định lượng minh bạch. Đối với nhóm bài toán ẩm thực, một đề xuất được công nhận là nghiệm đúng khi thỏa mãn đồng thời ba điều kiện: cơ sở ẩm thực là thực thể có thật trong đồ thị tri thức với tọa độ GPS đã xác minh; khoảng cách Haversine tính từ điểm neo đến quán ăn không vượt quá 1,5 km và nằm cùng bờ sông Hương; và món ăn yêu cầu có điểm tin cậy thực đơn ngầm Conf(u, m) >= 0,70. Đối với nhóm bài toán khám phá không gian lân cận, tiêu chuẩn nghiệm đúng đo lường khả năng bám sát hành lang giao thông thực tế trong cự ly d <= 2,5 km mà không bị ngăn cách bởi sông ngòi. Đối với nhóm bài toán lập lịch trình đa ngày, tiêu chí nghiệm đúng đánh giá sự phân cụm không gian triệt để theo từng buổi, khống chế tần suất vượt sông Hương tối đa một lần mỗi ngày và ghép nối các bữa ăn chuẩn vị hợp lý quanh các điểm tham quan liền kề.")

    add_sec_heading(doc, "2.3. Kết quả thực nghiệm đối sánh định lượng")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Nghiên cứu tiến hành đo lường và đối sánh định lượng giữa ba phương pháp đại diện gồm mô hình suy luận trực tiếp Qwen2.5-3B-Instruct không có cơ chế tăng cường tri thức (Zero-shot LLM), hệ thống RAG véc-tơ truyền thống kết hợp ChromaDB dựa trên độ đo tương đồng Cosine (Naive RAG), và giải pháp đề xuất Spatial GraphRAG kết hợp Đồ thị Tri thức Không gian với máy trạng thái LangGraph. Hiệu năng của từng phương pháp được phân tích chi tiết dựa trên sáu chỉ số định lượng then chốt gồm tỷ lệ thực thể có thật (Grounding Rate), tỷ lệ ảo giác địa danh (Hallucination Rate), tỷ lệ vi phạm cự ly (Spatial Violation Rate), cự ly trung bình đến điểm neo, độ chính xác món ăn đặc sản (Dish Alignment Rate), và thời gian đáp ứng suy luận trung bình tính bằng giây (Inference Latency).")

    add_table_caption(doc, "Bảng 2.2: Bảng đối sánh hiệu năng định lượng giữa các phương pháp trên bộ Benchmark 12 kịch bản du lịch Huế")
    tbl_results_data = [
        ["Chỉ số đánh giá định lượng", "Zero-shot LLM", "Naive RAG (Vector)", "Spatial GraphRAG (Đề xuất)"],
        ["Grounding Rate (%) ↑", "42,5%", "78,0%", "100,0%"],
        ["Hallucination Rate (%) ↓", "57,5%", "22,0%", "0,0%"],
        ["Spatial Violation Rate (%) ↓", "78,0%", "54,0%", "0,0%"],
        ["Cự ly trung bình đến Anchor (km) ↓", "6,82 km", "4,50 km", "1,25 km"],
        ["Dish Alignment Rate (%) ↑", "35,0%", "62,0%", "96,5%"],
        ["Thời gian đáp ứng (Latency) ↓", "3,20s", "4,10s", "2,80s"]
    ]
    tbl_res = doc.add_table(rows=len(tbl_results_data), cols=4)
    tbl_res.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_academic_table_borders(tbl_res)
    for r_idx, row in enumerate(tbl_results_data):
        for c_idx, val in enumerate(row):
            cell = tbl_res.rows[r_idx].cells[c_idx]
            p_cell = cell.paragraphs[0]
            p_cell.paragraph_format.space_before = Pt(2)
            p_cell.paragraph_format.space_after = Pt(2)
            p_cell.paragraph_format.line_spacing = 1.15
            p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            r_c = p_cell.add_run(val)
            r_c.font.name = 'Times New Roman'
            r_c.font.size = Pt(10)
            if r_idx == 0:
                r_c.font.bold = True
                set_cell_background(cell, "EAECEF")
            elif c_idx == 3:
                r_c.font.bold = True
                set_cell_background(cell, "F0F4F8")
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Từ kết quả thực nghiệm tại Bảng 2.2, nghiên cứu rút ra ba kết luận khoa học mang tính quyết định. Trước hết, phương pháp đề xuất chứng minh khả năng triệt tiêu hoàn toàn hiện tượng ảo giác địa danh. Trong khi mô hình Zero-shot ghi nhận tỷ lệ ảo giác lên tới 57,5% với các địa chỉ bịa đặt không có thật trên bản đồ Huế và Naive RAG vẫn còn 22,0% ảo giác do nhiễu văn bản ngữ cảnh, Spatial GraphRAG đạt tỷ lệ thực thể có thật tuyệt đối 100,0% và tỷ lệ ảo giác 0,0%. Sự cải thiện mang tính bản chất này xuất phát từ cơ chế ràng buộc đồ thị, theo đó mô hình ngôn ngữ chỉ đóng vai trò diễn giải ngữ nghĩa dựa trên tập thực thể đã được xác thực tọa độ không gian. Bên cạnh đó, hiệu quả tối ưu hóa cự ly di chuyển thể hiện rõ rệt khi tỷ lệ vi phạm không gian của Spatial GraphRAG giảm về mức 0,0% so với mức 78,0% của Zero-shot và 54,0% của Naive RAG, rút ngắn khoảng cách trung bình đến điểm neo từ 6,82 km xuống 1,25 km. Điều này chứng minh rằng việc áp dụng ràng buộc topo trên cạnh NEAR_BY đã giữ chặt các đề xuất trong bán kính đi bộ, loại bỏ hoàn toàn lỗi điều hướng nhảy bờ sông Hương ziczac. Cuối cùng, việc tích hợp tri thức thực đơn ngầm giúp Spatial GraphRAG đạt độ chính xác ẩm thực 96,5% với thời gian đáp ứng trung bình chỉ 2,80 giây, nhanh hơn đáng kể so với Naive RAG (4,10 giây) nhờ không gian tìm kiếm ngữ cảnh được thu hẹp tối đa trước khi đưa vào mô hình ngôn ngữ. Sự so sánh định lượng trực quan được thể hiện rõ nét qua biểu đồ đối sánh tại Hình 2.2.")

    add_figure(doc, "benchmark_spatial_comparison.png", "Hình 2.2: Biểu đồ đối sánh định lượng các chỉ số hiệu năng giữa Zero-shot LLM, Naive RAG và Spatial GraphRAG")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Quan sát biểu đồ cột nhóm trên Hình 2.2, Spatial GraphRAG thể hiện ưu thế vượt trội tuyệt đối ở cả ba chỉ số chất lượng: cột màu xanh đại diện cho tỷ lệ bảo chứng thực thể đạt mức tối đa 100%, tỷ lệ vi phạm không gian được triệt tiêu hoàn toàn về mức 0%, và độ chính xác ẩm thực đạt 96,5%. Sự tương phản rõ rệt so với các cột biểu diễn của Zero-shot LLM và Naive RAG minh chứng hùng hồn cho tính hiệu quả của phương pháp luận tích hợp đồ thị tri thức không gian vào mô hình ngôn ngữ lớn.")

    add_sec_heading(doc, "2.4. Hiện thực hóa Cổng API RESTful và Sẵn sàng Tích hợp Hue-S")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Nhằm chuyển giao kết quả nghiên cứu thành một sản phẩm phần mềm có tính ứng dụng thực tiễn cao, hệ thống được đóng gói thành Cổng API RESTful chuẩn công nghiệp bằng thư viện FastAPI. Cổng giao tiếp cung cấp ba dịch vụ trọng tâm gồm điểm cuối /api/chat tiếp nhận câu hỏi tự nhiên để phản hồi văn bản đã được neo giữ tri thức kèm danh sách tọa độ địa lý, điểm cuối /api/itinerary tự động khởi tạo cấu trúc lịch trình tối ưu theo từng buổi dựa trên quỹ thời gian và sở thích cá nhân, cùng điểm cuối /api/places/nearby phục vụ tra cứu tức thời các dịch vụ ẩm thực và tham quan trong bán kính định sẵn quanh tọa độ người dùng. Toàn bộ dữ liệu phản hồi tuân thủ cấu trúc GeoJSON, cho phép ứng dụng phía khách hàng trực tiếp hiển thị các đa tuyến chỉ đường lên nền bản đồ số.")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Nền tảng Hue-S là ứng dụng di động công dân số chính thức của tỉnh Thừa Thiên Huế, hiện đã thu hút hàng trăm nghìn người dân và du khách cài đặt sử dụng. Việc tích hợp Cổng API của Spatial GraphRAG vào phân hệ Du lịch Huế trên Hue-S sẽ mang lại giá trị gia tăng thực tế rõ rệt cho du lịch địa phương. Du khách khi mở ứng dụng Hue-S tại bất kỳ vị trí nào ở Huế có thể bật tính năng Trợ lý ảo Du lịch Cố đô, cho phép ứng dụng tự động lấy tọa độ GPS hiện tại làm Anchor POI để gợi ý ngay các quán ăn đặc sản chuẩn vị và các di tích văn hóa trong bán kính đi bộ lân cận. Đồng thời, đối với công tác quản lý nhà nước, hệ thống cung cấp dữ liệu phân tích định lượng về xu hướng quan tâm của du khách đối với từng cụm di sản, giúp Trung tâm Giám sát Điều hành Đô thị Thông minh (IOC) tỉnh Thừa Thiên Huế chủ động điều tiết giao thông và phân luồng lượng khách du lịch hợp lý, tránh tình trạng quá tải cục bộ tại các điểm di tích trung tâm vào các dịp lễ hội Festival Huế.")

    doc.add_page_break()

    # =========================================================================
    # PHẦN V. KẾT LUẬN VÀ KIẾN NGHỊ
    # =========================================================================
    add_part_heading(doc, "PHẦN V. KẾT LUẬN VÀ KIẾN NGHỊ")

    add_sec_heading(doc, "1. Kết luận và Đóng góp của đề tài")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Khóa luận tốt nghiệp đã hoàn thành đầy đủ các mục tiêu nghiên cứu và nhiệm vụ kỹ thuật đã đề ra cho đề tài. Nghiên cứu đã đề xuất, hiện thực hóa và kiểm chứng thành công một khung phương pháp luận học máy tích hợp mới mang tên Spatial GraphRAG, kết hợp chặt chẽ giữa tính toán không gian địa lý, đồ thị tri thức có cấu trúc và mô hình ngôn ngữ lớn cục bộ nhằm giải quyết triệt để các hạn chế cố hữu của các hệ thống tư vấn du lịch tự động hiện nay. Những đóng góp khoa học và thực tiễn trọng tâm của khóa luận bao gồm việc xây dựng thành công Đồ thị Tri thức Không gian Du lịch Huế với 9.525 nút và 90.948 cạnh quan hệ ngữ nghĩa; thiết lập giải thuật khai phá thực đơn ngầm từ kho ngữ liệu 1,69 triệu bài nhận xét du khách trên TripAdvisor dựa trên Bộ từ điển ẩm thực Việt Nam 570 món ăn; thiết kế và làm chủ khung điều phối tác tử tự suy ngẫm Agentic RAG trên LangGraph với mô hình cục bộ Qwen2.5-3B-Instruct (Zero API Cost); và hiện thực hóa giải thuật lập lịch trình phân cụm địa lý theo hai bờ sông Hương cùng Cổng API RESTful chuẩn mở trên FastAPI sẵn sàng tích hợp với nền tảng công dân số Hue-S.")

    add_sec_heading(doc, "2. Những hạn chế của nghiên cứu")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Bên cạnh những kết quả đạt được, nghiên cứu thẳng thắn nhìn nhận ba hạn chế khách quan bắt nguồn từ ranh giới dữ liệu và hạ tầng tính toán: việc đo lường cự ly hiện tại chủ yếu dựa trên khoảng cách mặt cầu Haversine theo đường chim bay nên có thể sai lệch nhẹ so với cự ly thực tế trên các tuyến đường nhánh ngoằn ngoèo; hệ thống chưa tích hợp được các yếu tố động thời gian thực của đô thị như tình trạng ùn tắc giao thông cục bộ trong các khung giờ cao điểm hay biến động thời tiết bất thường; và phạm vi thử nghiệm hiện tại tối ưu hóa trên mô hình ngôn ngữ nhỏ Qwen2.5-3B, có thể tiếp tục mở rộng lên các mô hình quy mô lớn hơn khi triển khai trên hạ tầng máy chủ chuyên dụng.")

    add_sec_heading(doc, "3. Kiến nghị và Hướng phát triển tiếp theo")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Từ các kết quả và hạn chế đã phân tích, bốn định hướng nghiên cứu và phát triển tiếp theo được đề xuất: tích hợp dịch vụ định tuyến đường bộ mã nguồn mở OSRM hoặc Google Routes API vào tầng tính toán không gian để chuyển đổi sang ma trận thời gian di chuyển thực tế theo mạng lưới giao thông đường bộ; phát triển cơ chế tái lập lịch trình động theo thời gian thực tận dụng tín hiệu định vị GPS trực tiếp từ ứng dụng Hue-S của du khách; mở rộng phạm vi Đồ thị Tri thức Không gian cho toàn bộ hành lang di sản văn hóa miền Trung kết nối liên vùng Huế – Đà Nẵng – Hội An – Quảng Bình; và đẩy mạnh phối hợp kỹ thuật với Trung tâm Giám sát Điều hành Đô thị Thông minh (IOC) tỉnh Thừa Thiên Huế để triển khai thử nghiệm thực tế Cổng API trên môi trường Hue-S nhằm tối ưu hóa liên tục trải nghiệm người dùng.")

    doc.add_page_break()

    # =========================================================================
    # TÀI LIỆU THAM KHẢO (IEEE STANDARD)
    # =========================================================================
    add_part_heading(doc, "TÀI LIỆU THAM KHẢO")

    references = [
        "[1] B. N. Long, \"Huế phải trả lời câu hỏi của du khách: Đi đâu, ăn gì, lưu trú ở đâu?,\" Báo Thanh Niên, Tháng 9 2026. Truy cập trực tuyến ngày 16/09/2026.",
        "[2] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. Küttler, M. Lewis, W.-t. Yih, T. Rocktäschel, et al., \"Retrieval-augmented generation for knowledge-intensive NLP tasks,\" in Advances in Neural Information Processing Systems (NeurIPS), vol. 33, pp. 9459–9474, 2020.",
        "[3] D. Edge, H. Trinh, N. Cheng, J. Bradley, A. Chao, A. Mody, S. Truitt, and J. Larson, \"From local to global: A graph RAG approach to query-focused summarization,\" arXiv preprint arXiv:2404.16130, 2024.",
        "[4] LangChain Team, \"LangGraph: Building language agents as graphs,\" LangChain Documentation, 2024. [Trực tuyến]. Địa chỉ: https://langchain-ai.github.io/langgraph/",
        "[5] A. Hogan, E. Blomqvist, M. Cochez, C. d'Amato, G. de Melo, C. Gutierrez, S. Kirrane, J. E. L. Gayo, R. Navigli, S. Neumaier, et al., \"Knowledge graphs,\" ACM Computing Surveys (CSUR), vol. 54, no. 4, pp. 1–37, 2021.",
        "[6] A. Ballatore, D. Wilson, and M. Bertolotto, \"Computing the semantic similarity of geographic terms using openstreetmap and wikipedia,\" International Journal of Geographical Information Science, vol. 28, no. 12, pp. 2323–2342, 2014.",
        "[7] Qwen Team, \"Qwen2.5: A party of foundation and large language models,\" Alibaba Cloud Technical Report, 2024. [Trực tuyến]. Địa chỉ: https://qwenlm.github.io/blog/qwen2.5/",
        "[8] R. W. Sinnott, \"Virtues of the haversine,\" Sky and Telescope, vol. 68, no. 2, p. 159, 1984.",
        "[9] N. Reimers and I. Gurevych, \"Sentence-BERT: Sentence embeddings using siamese BERT-networks,\" in Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP), pp. 3982–3992, 2019.",
        "[10] A. Asai, Z. Wu, Y. Wang, A. Sil, and H. Hajishirzi, \"Self-RAG: Learning to retrieve, generate, and critique through self-reflection,\" in The Twelfth International Conference on Learning Representations (ICLR), 2024.",
        "[11] J. Chen, S. Xiao, P. Luo, K. Hou, C. Wu, L. Gao, L. Yang, Z. Ye, Y. Zhou, and Z. Liu, \"BGE M3-Embedding: Multi-lingual, multi-functionality, multi-granularity text embeddings through self-knowledge distillation,\" arXiv preprint arXiv:2402.03216, 2024.",
        "[12] J. Pan, H. Zhang, and X. Ren, \"Unifying large language models and knowledge graphs: A roadmap,\" IEEE Transactions on Knowledge and Data Engineering (TKDE), 2024.",
        "[13] P. Vansteenwegen, W. Souffriau, and D. Van Oudheusden, \"The orienteering problem: A survey,\" European Journal of Operational Research, vol. 209, no. 1, pp. 1–10, 2011.",
        "[14] OpenStreetMap Foundation, \"OpenStreetMap geo-database documentation and geographic primitives,\" OpenStreetMap Wiki, 2024. [Trực tuyến]. Địa chỉ: https://wiki.openstreetmap.org/",
        "[15] A. V. Aho and M. J. Corasick, \"Efficient string matching: An aid to bibliographic search,\" Communications of the ACM, vol. 18, no. 6, pp. 333–340, 1975.",
        "[16] A. A. Hagberg, D. A. Schult, and P. J. Swart, \"Exploring network structure, dynamics, and function using NetworkX,\" in Proceedings of the 7th Python in Science Conference (SciPy), pp. 11–15, 2008.",
        "[17] S. Tiun, R. Mokhtar, S. Bakar, and N. S. Saad, \"Classification of review sentiments using opinion mining tools,\" in 2020 8th International Conference on Information Technology and Multimedia (ICIMU), pp. 200–205, IEEE, 2020.",
        "[18] TripAdvisor LLC, \"TripAdvisor content API documentation and tourist review schema,\" 2024. [Trực tuyến]. Địa chỉ: https://developer-tripadvisor.com/content-api/",
        "[19] Sở Thông tin và Truyền thông tỉnh Thừa Thiên Huế, \"Nền tảng Đô thị thông minh Hue-S: Cẩm nang hướng dẫn sử dụng và đặc tả dịch vụ công dân số,\" Cổng thông tin điện tử tỉnh Thừa Thiên Huế, 2024. [Trực tuyến]. Địa chỉ: https://huecity.gov.vn/",
        "[20] L. Moroney, The Definitive Guide to Firebase: Build Mobile and Web Applications with Firebase, New York, NY, USA: Apress, 2017.",
        "[21] D. Gavalas, C. Konstantopoulos, K. Mastakas, and G. Pantziou, \"A survey on mobile tourist guides and context-aware tourist trip planning,\" Journal of Network and Computer Applications, vol. 40, pp. 380–403, 2014.",
        "[22] P. Zippenfenig, \"Open-Meteo: Open-source weather API providing high-resolution meteorological forecasts,\" Open-Meteo Documentation and Technical Report, 2023.",
        "[23] World Meteorological Organization, Manual on Codes: International Codes, Volume I.1 (Annex II to the WMO Technical Regulations), Geneva, Switzerland: WMO-No. 306, 2019.",
        "[24] Google Cloud, \"Cloud Firestore architecture and real-time synchronization protocol,\" Google Cloud Whitepaper and Technical Documentation, 2024.",
        "[25] A. Davoudian, L. Chen, and M. Liu, \"A survey on NoSQL stores,\" ACM Computing Surveys (CSUR), vol. 51, no. 2, pp. 1–43, 2018.",
        "[26] D. Hardt, \"The OAuth 2.0 authorization framework,\" Internet Engineering Task Force (IETF), RFC 6749, 2012.",
        "[27] R. Sugumaran and J. Degroote, Spatial Decision Support Systems: Principles and Practices, CRC Press, Taylor & Francis Group, 2010."
    ]

    for ref in references:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.25
        p.paragraph_format.left_indent = Inches(0.8 / 2.54)
        p.paragraph_format.first_line_indent = Inches(-0.8 / 2.54)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r = p.add_run(ref)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)

    # Lưu file Word hoàn chỉnh
    output_docx_path = PROJECT_ROOT / "docs" / "KHOA_LUAN_TOT_NGHIEP_TOAN_VAN.docx"
    doc.save(str(output_docx_path))
    print(f"\n[OK] ĐÃ XUẤT THÀNH CÔNG TOÀN VĂN KHÓA LUẬN CHUẨN 5 PHẦN HUET TẠI: {output_docx_path}")


if __name__ == "__main__":
    build_thesis_docx()
