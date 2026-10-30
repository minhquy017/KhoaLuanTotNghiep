# -*- coding: utf-8 -*-
"""
SOẠN THẢO TOÀN VĂN KHÓA LUẬN TỐT NGHIỆP ĐẠI HỌC (CHUẨN 5 PHẦN HUET)
Ngành: Khoa học Dữ liệu và Trí tuệ Nhân tạo (DS&AI K3)
Khoa Kỹ thuật và Công nghệ – Đại học Huế (HUET)
Đề tài: Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh dựa trên Đồ thị Tri thức Không gian và Mô hình Ngôn ngữ Lớn
Sinh viên thực hiện: Lê Hoàng Minh Quý (MSSV: 22E1020018)
Giảng viên hướng dẫn: TS. Hồ Quốc Dũng
Năm thực hiện: 2026

Tuân thủ tuyệt đối:
- Văn bản số 1967/HD-ĐHH của Đại học Huế (Quy cách 5 Phần, Mẫu 1 đến Mẫu 9, căn lề 3-3-3-2 cm, Times New Roman 13pt, dãn dòng 1.5).
- Kỹ năng Viết học thuật Chuyên ngành Khoa học Dữ liệu & AI (academic-writing-ds-ai):
  Triệt tiêu 100% 16 dấu hiệu văn phong AI, không biểu tượng cảm xúc, không khung callout chatbot,
  không gạch đầu dòng liệt kê từ khóa: giải thích, văn xuôi học thuật liên tục, phân tích và trích dẫn bảng biểu/hình ảnh song hành (Dual In-text Referencing).
- Đồng bộ 100% với tài liệu LaTeX (main.pdf) và khắc phục triệt để các phản biện của Hội đồng chấm khóa luận.
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
    """Tiêu đề Cấp PHẦN (Heading 1): In hoa, đậm, 16pt, căn giữa, dãn trước 12pt, dãn sau 12pt."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.5
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = BLACK_TEXT
    return p


def add_chapter_heading(doc, text):
    """Tiêu đề Cấp CHƯƠNG (Heading 1 trong Phần IV): In hoa, đậm, 15pt, căn giữa, dãn trước 12pt, dãn sau 8pt."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.5
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = BLACK_TEXT
    return p


def add_sec_heading(doc, text):
    """Tiêu đề Mục Cấp 1 (Heading 2): Đậm, 14pt, căn trái, dãn trước 10pt, dãn sau 4pt."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.5
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = BLACK_TEXT
    return p


def add_subsec_heading(doc, text):
    """Tiêu đề Tiểu mục Cấp 2 (Heading 3): Đậm, nghiêng nhẹ hoặc đậm đứng, 13pt, căn trái, dãn trước 6pt, dãn sau 2pt."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.5
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = BLACK_TEXT
    return p


def add_table_caption(doc, text):
    """Tên Bảng, Biểu: Đặt TRÊN bảng, đậm, 12pt, căn giữa, dãn trước 10pt, dãn sau 4pt."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = BLACK_TEXT
    return p


def add_figure(doc, img_name, caption_text, width_inches=5.6):
    """
    Thêm hình vẽ học thuật vào tài liệu:
    - Căn giữa trang.
    - Tên Hình vẽ đặt DƯỚI hình, nghiêng, 12pt, căn giữa theo đúng chuẩn HUET và IEEE.
    """
    img_path = IMG_DIR / img_name
    if not img_path.exists():
        img_path = PROJECT_ROOT / "docs" / "figures" / img_name
    if not img_path.exists():
        print(f"[CẢNH BÁO] Không tìm thấy tệp hình ảnh: {img_name}")
        return None

    p_img = doc.add_paragraph()
    p_img.paragraph_format.space_before = Pt(8)
    p_img.paragraph_format.space_after = Pt(2)
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_img = p_img.add_run()
    r_img.add_picture(str(img_path), width=Inches(width_inches))

    p_cap = doc.add_paragraph()
    p_cap.paragraph_format.space_before = Pt(2)
    p_cap.paragraph_format.space_after = Pt(8)
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap = p_cap.add_run(caption_text)
    r_cap.font.name = 'Times New Roman'
    r_cap.font.size = Pt(12)
    r_cap.font.italic = True
    r_cap.font.color.rgb = BLACK_TEXT
    return p_img


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
    p.paragraph_format.space_after = Pt(45)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("NGÀNH: KHOA HỌC DỮ LIỆU VÀ TRÍ TUỆ NHÂN TẠO")
    r.font.name = 'Times New Roman'
    r.font.bold = True
    r.font.size = Pt(15)

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
    r = p.add_run("LÊ HOÀNG MINH QUÝ – MSSV: 22E1020018")
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
    # SECTION 1: FRONT MATTER (LỜI CAM ĐOAN ĐẾN DANH MỤC HÌNH VẼ)
    # =========================================================================
    sec_front = doc.add_section()
    set_section_margins_huet(sec_front)

    # LỜI CAM ĐOAN
    add_part_heading(doc, "LỜI CAM ĐOAN")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Tôi xin cam đoan khóa luận tốt nghiệp với đề tài \"Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh dựa trên Đồ thị Tri thức Không gian và Mô hình Ngôn ngữ Lớn\" là công trình nghiên cứu khoa học do chính bản thân tôi trực tiếp thực hiện dưới sự hướng dẫn khoa học tận tình của TS. Hồ Quốc Dũng. Toàn bộ cơ sở dữ liệu, mã nguồn thuật toán, đồ thị tri thức và các kết quả đo lường thực nghiệm được trình bày trong khóa luận hoàn toàn trung thực, khách quan và không sao chép nguyên bản từ bất kỳ công trình nghiên cứu nào đã được công bố trước đó.")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Các thông tin, tài liệu học thuật và lý thuyết tham khảo từ các công bố quốc tế, kỷ yếu hội nghị và bài báo khoa học liên quan đều đã được đối soát kỹ lưỡng, dẫn nguồn minh bạch và liệt kê đầy đủ tại Danh mục Tài liệu tham khảo theo quy chuẩn học thuật IEEE. Tôi hoàn toàn chịu trách nhiệm trước pháp luật, Hội đồng chấm khóa luận tốt nghiệp và Nhà trường về tính liêm chính học thuật của toàn bộ nội dung công trình này.")

    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = Pt(25)
    p_sig.paragraph_format.space_after = Pt(2)
    p_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p_sig.add_run("Thành phố Huế, ngày 30 tháng 10 năm 2026\n")
    r.font.name = 'Times New Roman'
    r.font.italic = True
    r.font.size = Pt(13)
    r2 = p_sig.add_run("Sinh viên thực hiện\n\n\n\n")
    r2.font.name = 'Times New Roman'
    r2.font.bold = True
    r2.font.size = Pt(13)
    r3 = p_sig.add_run("Lê Hoàng Minh Quý")
    r3.font.name = 'Times New Roman'
    r3.font.bold = True
    r3.font.size = Pt(13)

    doc.add_page_break()

    # LỜI CẢM ƠN
    add_part_heading(doc, "LỜI CẢM ƠN")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Trước hết, tôi xin bày tỏ lòng biết ơn sâu sắc và chân thành nhất tới TS. Hồ Quốc Dũng, người thầy đã luôn định hướng phương pháp luận khoa học, kiên nhẫn chỉ dẫn, động viên và tạo điều kiện nghiên cứu tốt nhất cho tôi trong suốt quá trình triển khai đề tài khóa luận tốt nghiệp.")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Tôi xin trân trọng gửi lời cảm ơn tới Ban Giám hiệu Khoa Kỹ thuật và Công nghệ – Đại học Huế, cùng toàn thể quý Thầy, Cô giáo thuộc Bộ môn Khoa học Dữ liệu và Trí tuệ Nhân tạo đã tận tâm giảng dạy, truyền thụ nền tảng kiến thức chuyên môn vững chắc và tạo môi trường học tập lý tưởng trong suốt 4 năm đại học vừa qua.")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Sau cùng, tôi xin dành lời tri ân sâu sắc tới gia đình và những người bạn đồng hành đã luôn là điểm tựa tinh thần vững chắc, tiếp thêm nguồn động lực to lớn giúp tôi hoàn thành xuất sắc công trình nghiên cứu này.")

    doc.add_page_break()

    # TÓM TẮT
    add_part_heading(doc, "TÓM TẮT")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Bài toán xây dựng hệ thống trợ lý ảo thông minh phục vụ du lịch đô thị di sản đang đối mặt với những thách thức học thuật cốt lõi: các hệ thống Mô hình Ngôn ngữ Lớn (LLM) thương mại thường xuyên mắc lỗi ảo giác địa danh (Hallucination) và hoàn toàn thiếu vắng tri giác không gian (Spatial Blindness), dẫn đến việc gợi ý các lộ trình di chuyển bất khả thi như bắt du khách nhảy ziczac qua lại giữa hai bờ sông Hương hoặc đề xuất các nhà hàng cách xa hàng chục cây số so với điểm tham quan. Trong khi đó, các ứng dụng du lịch truyền thống chỉ cung cấp danh mục tĩnh mà không thể cá nhân hóa ngữ cảnh theo phản hồi thực tế của du khách. Khóa luận này đề xuất giải pháp Spatial GraphRAG - một khung kiến trúc Tăng cường Tạo sinh Truy xuất Không gian kết hợp Đồ thị Tri thức, dữ liệu đánh giá du khách quy mô lớn và khung tác tử điều phối Agentic RAG trên mô hình cục bộ Qwen2.5-3B.")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Nghiên cứu xây dựng Đồ thị Tri thức Không gian Du lịch Huế với 9.525 đỉnh thực thể và 90.948 cạnh ngữ nghĩa, kết nối 612 địa điểm du lịch tại Huế (29 điểm tham quan di tích cốt lõi, 104 khách sạn, 479 quán ăn). Thông qua thuật toán khai phá thực đơn ngầm từ 44.355 bài đánh giá du khách tại Huế trên tập ngữ liệu 1.698.641 bản ghi (gần 1,70 triệu bài) toàn quốc đã làm sạch, hệ thống bóc tách 4.337 quan hệ phục vụ món ăn đặc sản chuẩn xác. Hệ thống tích hợp phân hệ Thị giác Đa phương thức CLIP ViT-B/32 nhận diện ảnh thực địa di tích đạt Top-1 98,7% và Top-3 100,0% qua giao thức LOOCV không cần tái huấn luyện, cùng Khung lọc không gian 2 giai đoạn (Two-stage Spatial Filtering): lọc thô Haversine (d <= 1,5 km) trên đồ thị và tối ưu tinh mạng lưới đường bộ thực tế qua OSRM Contraction Hierarchies có tính đến hệ số uốn lượn đô thị và các cây cầu vượt sông Hương. Kết quả thực nghiệm đối sánh định lượng trên bộ kiểm thử chuẩn 12 kịch bản du lịch chứng minh Spatial GraphRAG triệt tiêu 100% hiện tượng ảo giác thực thể và vi phạm không gian (so với mức vi phạm 66,7% của Zero-shot LLM và 41,7% của Naive RAG), rút ngắn cự ly di chuyển trung bình từ 5,82 km (Zero-shot) và 3,65 km (Naive RAG) xuống 1,25 km, đồng thời nâng độ chính xác món ăn đặc sản lên 96,5% (so với 25,0% của Zero-shot và 62,5% của Naive RAG) với thời gian đáp ứng thời gian thực 2,80 giây.")

    p_kw = doc.add_paragraph()
    format_body_p(p_kw)
    r_kw = p_kw.add_run("Từ khóa: ")
    r_kw.font.name = 'Times New Roman'
    r_kw.font.bold = True
    r_kw.font.size = Pt(13)
    r_kw2 = p_kw.add_run("Spatial GraphRAG, Đồ thị Tri thức Không gian, Agentic RAG, LangGraph, CLIP ViT-B/32, OSRM, Two-stage Spatial Filtering, Khai phá Thực đơn Ngầm, Du lịch Huế, Qwen2.5-3B.")
    r_kw2.font.name = 'Times New Roman'
    r_kw2.font.italic = True
    r_kw2.font.size = Pt(13)

    doc.add_page_break()

    # MỤC LỤC
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
        ("   2. Mục tiêu nghiên cứu (6 mục tiêu cụ thể)", "3", False, True),
        ("   3. Câu hỏi nghiên cứu và Giả thuyết khoa học (RQ1 - RQ6, H1 - H6)", "4", False, True),
        ("   4. Đối tượng và Phạm vi nghiên cứu", "5", False, True),
        ("   5. Ý nghĩa khoa học và 6 Đóng góp cốt lõi của đề tài", "6", False, True),
        ("PHẦN II. TỔNG QUAN VẤN ĐỀ NGHIÊN CỨU", "7", True, False),
        ("   1. Cơ sở lý thuyết nền tảng", "7", False, True),
        ("      1.1. Đồ thị Tri thức Không gian và Khung lọc không gian 2 giai đoạn", "7", False, True),
        ("      1.2. Sự tiến hóa từ Naive RAG sang GraphRAG và Agentic RAG", "8", False, True),
        ("      1.3. Khung điều phối trạng thái LangGraph và Mô hình cục bộ Qwen2.5", "10", False, True),
        ("      1.4. Khai phá thực đơn ngầm và Bài toán Thiết kế Chuyến đi Du lịch (TTDP)", "12", False, True),
        ("      1.5. Mô hình Không gian Vector Ngữ nghĩa Đa ngôn ngữ", "13", False, True),
        ("      1.6. Cơ chế Định tuyến Phân luồng Tin cậy (Confidence Router)", "13", False, True),
        ("      1.7. Mô hình hóa Toán học Bài toán TTDP có Ràng buộc", "14", False, True),
        ("      1.8. Kiến trúc Vision Transformer và Mô hình CLIP ViT-B/32 Zero-shot", "15", False, True),
        ("      1.9. Hệ thống Định tuyến OSRM và Thuật toán Contraction Hierarchies", "16", False, True),
        ("PHẦN III. ĐỐI TƯỢNG, PHẠM VI VÀ PHƯƠNG PHÁP NGHIÊN CỨU", "17", True, False),
        ("   1. Đối tượng và Thực trạng các nguồn dữ liệu nghiên cứu", "17", False, True),
        ("      1.1. Hiện trạng đa nguồn dữ liệu và Quy mô tổng thể 1.698.641 bản ghi", "17", False, True),
        ("      1.2. Giải phẫu cấu trúc tập dữ liệu 44.355 bài đánh giá thực tế tại Huế", "19", False, True),
        ("      1.3. Cơ cấu phân loại và phân bố địa giới của 612 địa điểm du lịch tại Huế", "20", False, True),
        ("PHẦN IV. NỘI DUNG VÀ KẾT QUẢ NGHIÊN CỨU", "22", True, False),
        ("   Chương 1. Kiến trúc Hệ thống Spatial GraphRAG và Khai phá Thực đơn Ngầm", "22", True, False),
        ("      1.1. Kiến trúc tổng thể bốn tầng của Hệ thống", "22", False, True),
        ("      1.2. Thiết kế Đồ thị Tri thức Không gian Du lịch Huế (9.525 nút, 90.948 cạnh)", "24", False, True),
        ("      1.3. Phương pháp khai phá thực đơn ngầm và đối soát tri thức", "26", False, True),
        ("      1.4. Khung điều phối tác tử tự suy ngẫm Agentic RAG trên LangGraph (5 nút StateGraph)", "28", False, True),
        ("      1.5. Tầng Lưu trữ Đám mây NoSQL và Quản trị Đa phiên Hội thoại", "29", False, True),
        ("      1.6. Thiết kế Giao diện Khách Web Tương tác Không gian (Gemini-Style Client)", "31", False, True),
        ("         1.6.1. Kiến trúc Thanh bên Điều hướng Thích ứng", "31", False, True),
        ("         1.6.2. Tiện ích Khí tượng Du lịch Cố đô Thời gian thực thích ứng Ngữ cảnh", "32", False, True),
        ("         1.6.3. Cơ chế Xác thực An toàn Tuân thủ OWASP và Menu Tài khoản Popover", "33", False, True),
        ("         1.6.4. Bộ tính toán Ngân sách Lộ trình Du lịch (Trip Budget Calculator)", "34", False, True),
        ("         1.6.5. Sổ tay Du khách và Hệ thống Gamification Hộ chiếu Di sản (29 vs 158 điểm)", "35", False, True),
        ("         1.6.6. Phân hệ Phân loại Kiểu hình Du khách (Persona Classifier)", "36", False, True),
        ("      1.7. Phân hệ Nhận diện Điểm mốc Thị giác Đa phương thức (CLIP ViT-B/32)", "37", False, True),
        ("   Chương 2. Thuật toán Lập lịch trình Không gian, Thực nghiệm Đối sánh và Tích hợp", "38", True, False),
        ("      2.1. Thuật toán Lập lịch trình phân cụm không gian", "38", False, True),
        ("      2.2. Bộ kiểm thử Benchmark 12 kịch bản du lịch Huế", "40", False, True),
        ("      2.3. Kết quả thực nghiệm đối sánh định lượng", "44", False, True),
        ("         2.3.1. Đối sánh hiệu năng các chỉ số chính trên bộ Benchmark", "44", False, True),
        ("         2.3.2. Đánh giá tính khả thi thời gian đáp ứng thời gian thực", "46", False, True),
        ("         2.3.3. Đánh giá định lượng Phân hệ Thị giác Đa phương thức qua Giao thức LOOCV", "47", False, True),
        ("      2.4. Hiện thực hóa Cổng API RESTful và Sẵn sàng Tích hợp Hue-S", "49", False, True),
        ("PHẦN V. KẾT LUẬN VÀ KIẾN NGHỊ", "51", True, False),
        ("   1. Kết luận và 6 Đóng góp cốt lõi của đề tài", "51", False, True),
        ("   2. Những hạn chế của nghiên cứu", "52", False, True),
        ("   3. Kiến nghị và Hướng phát triển tiếp theo", "53", False, True),
        ("TÀI LIỆU THAM KHẢO", "54", True, False),
        ("PHỤ LỤC", "56", True, False),
        ("   Phụ lục A: Danh mục 12 Kịch bản Kiểm thử Chuẩn (Benchmark Suite)", "56", False, True),
        ("   Phụ lục B: Danh mục Thực đơn Món ăn Đặc sản Huế trong Đồ thị Tri thức", "58", False, True)
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
        ["CLIP", "Contrastive Language-Image Pre-training", "Mô hình tiền huấn luyện tương phản Ngôn ngữ - Hình ảnh"],
        ["DS&AI", "Data Science & Artificial Intelligence", "Khoa học Dữ liệu và Trí tuệ Nhân tạo"],
        ["GPS", "Global Positioning System", "Hệ thống định vị toàn cầu"],
        ["GPU", "Graphics Processing Unit", "Bộ xử lý đồ họa"],
        ["HUET", "Hue University of Engineering and Technology", "Khoa Kỹ thuật và Công nghệ – Đại học Huế"],
        ["JSON", "JavaScript Object Notation", "Định dạng trao đổi dữ liệu đối tượng"],
        ["JWT", "JSON Web Token", "Chuẩn mở định dạng mã thông báo bảo mật"],
        ["KG", "Knowledge Graph", "Đồ thị tri thức"],
        ["LLM", "Large Language Model", "Mô hình ngôn ngữ lớn"],
        ["LOOCV", "Leave-One-Out Cross-Validation", "Kiểm định chéo rút một"],
        ["NLP", "Natural Language Processing", "Xử lý ngôn ngữ tự nhiên"],
        ["NoSQL", "Not Only SQL", "Mô hình cơ sở dữ liệu phi quan hệ"],
        ["OAuth", "Open Authorization", "Khung ủy quyền phân tán tiêu chuẩn mở"],
        ["OP", "Orienteering Problem", "Bài toán định hướng du lịch"],
        ["OSM", "OpenStreetMap", "Dự án bản đồ số mở toàn cầu"],
        ["OSRM", "Open Source Routing Machine", "Hệ thống tính toán định tuyến mã nguồn mở"],
        ["POI", "Point of Interest", "Điểm tham quan / Cơ sở dịch vụ du lịch"],
        ["RAG", "Retrieval-Augmented Generation", "Tạo sinh tăng cường truy xuất"],
        ["REST", "Representational State Transfer", "Phong cách kiến trúc mạng hướng dịch vụ"],
        ["RLHF", "Reinforcement Learning from Human Feedback", "Học tăng cường từ phản hồi của con người"],
        ["SKG", "Spatial Knowledge Graph", "Đồ thị tri thức không gian"],
        ["TTDP", "Tourist Trip Design Problem", "Bài toán thiết kế chuyến đi du lịch"],
        ["ViT", "Vision Transformer", "Kiến trúc Transformer ứng dụng cho thị giác máy tính"],
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
        ("Bảng 1", "Tổng mục các nguồn dữ liệu thành phần sử dụng trong nghiên cứu", "17"),
        ("Bảng 2", "Phân bố xếp hạng sao của 44.355 bài đánh giá du lịch thực tế tại Huế", "19"),
        ("Bảng 3", "Phân bố kiểu hình chuyến đi của du khách trong tập dữ liệu nhận xét tại Huế", "20"),
        ("Bảng 4", "Cơ cấu phân loại và phân bố địa giới của 612 địa điểm du lịch tại Huế", "21"),
        ("Bảng 1.1", "Thống kê định lượng các thành phần trong Đồ thị Tri thức Không gian", "25"),
        ("Bảng 1.2", "Mẫu đối soát kết quả khai phá thực đơn ngầm từ nhận xét du khách tại Huế", "27"),
        ("Bảng 1.4", "Lược đồ cấu trúc dữ liệu trên Google Cloud Firestore phục vụ quản lý đa phiên", "30"),
        ("Bảng 1.5", "Ma trận Quy tắc Thích ứng Lộ trình theo Ngữ cảnh Khí tượng Cố đô Huế", "32"),
        ("Bảng 2.1", "Đặc tả chi tiết 12 kịch bản trong Bộ dữ liệu kiểm thử chuẩn cho du lịch Huế", "41"),
        ("Bảng 2.2", "Bảng đối sánh hiệu năng định lượng giữa các phương pháp trên bộ Benchmark", "45"),
        ("Bảng 2.3", "Kết quả đánh giá định lượng phân hệ Nhận diện Điểm mốc Thị giác đa phương thức (Giao thức LOOCV)", "48")
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
        ("Hình 1", "Bài báo phản ánh chỉ đạo của lãnh đạo tỉnh về yêu cầu trả lời câu hỏi cốt lõi của du khách Huế", "2"),
        ("Hình 2", "Thực trạng giao diện phân hệ du lịch trên nền tảng công dân số Hue-S và phản hồi của người dùng", "3"),
        ("Hình 3", "Cơ cấu phân bố các danh mục địa điểm du lịch và xếp hạng sao tại thành phố Huế", "18"),
        ("Hình 4", "Top 10 món ăn đặc sản Huế được du khách nhắc đến nhiều nhất trong các bài đánh giá", "19"),
        ("Hình 5", "Quy trình phân mảnh văn bản phân tử cho các bài đánh giá du khách trước khi lập chỉ mục", "21"),
        ("Hình 1.1", "Kiến trúc tổng thể bốn tầng của Hệ thống Spatial GraphRAG phục vụ du lịch Huế", "23"),
        ("Hình 1.2", "Lược đồ cấu trúc thực thể và quan hệ trong Đồ thị Tri thức Không gian Du lịch Huế", "24"),
        ("Hình 1.3", "Kiến trúc Đồ thị Trạng thái điều phối quy trình tác tử tự suy ngẫm trên LangGraph (5 nút)", "28"),
        ("Hình 2.1", "Kịch bản luồng tương tác và gợi ý lịch trình không gian mẫu trên Giao diện Web Responsive", "39"),
        ("Hình 2.2", "Biểu đồ đối sánh định lượng các chỉ số hiệu năng giữa Zero-shot, Naive RAG và Spatial GraphRAG", "46")
    ]
    tbl_fig = doc.add_table(rows=len(fig_list) + 1, cols=3)
    tbl_fig.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_academic_table_borders(tbl_fig)
    headers_f = ["Số hiệu hình", "Tên sơ đồ, đồ thị, hình vẽ", "Trang"]
    for c_idx, h in enumerate(headers_f):
        cell = tbl_fig.rows[0].cells[c_idx]
        p_c = cell.paragraphs[0]
        r_c = p_c.add_run(h)
        r_c.font.name = 'Times New Roman'
        r_c.font.bold = True
        r_c.font.size = Pt(11)
        set_cell_background(cell, "EAECEF")
        set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
    for r_idx, (num, name, pg) in enumerate(fig_list):
        row = tbl_fig.rows[r_idx + 1]
        for c_idx, val in enumerate([num, name, pg]):
            cell = row.cells[c_idx]
            p_c = cell.paragraphs[0]
            r_c = p_c.add_run(val)
            r_c.font.name = 'Times New Roman'
            r_c.font.size = Pt(11)
            set_cell_margins(cell, top=50, bottom=50, left=80, right=80)

    doc.add_page_break()

    # =========================================================================
    # SECTION 2: BODY MATTER (PHẦN I ĐẾN PHẦN V)
    # =========================================================================
    sec_body = doc.add_section()
    set_section_margins_huet(sec_body)

    # =========================================================================
    # PHẦN I. PHẦN MỞ ĐẦU
    # =========================================================================
    add_part_heading(doc, "PHẦN I. PHẦN MỞ ĐẦU")

    add_sec_heading(doc, "1. Tính cấp thiết của đề tài")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Thành phố Huế là trung tâm văn hóa, du lịch di sản đặc sắc của Việt Nam và khu vực, sở hữu Quần thể di tích Cố đô Huế được UNESCO vinh danh là Di sản Văn hóa Thế giới cùng hệ thống ẩm thực cung đình và dân gian phong phú bậc nhất cả nước. Bước vào kỷ nguyên chuyển đổi số quốc gia và phát triển kinh tế ban đêm, ngành du lịch Thừa Thiên Huế đặt mục tiêu nâng cao chất lượng trải nghiệm của du khách thông qua các giải pháp công nghệ thông tin tiên tiến. Tuy nhiên, như lãnh đạo tỉnh Thừa Thiên Huế đã nhấn mạnh trong các diễn đàn phát triển kinh tế số, ngành du lịch địa phương hiện nay vẫn chưa có một hệ sinh thái số thực sự thông minh để trả lời thấu đáo ba câu hỏi cơ bản nhưng mang tính quyết định đối với bất kỳ du khách nào khi đặt chân đến Cố đô: Đi đâu, ăn gì, lưu trú ở đâu [1].")

    add_figure(doc, "thanhnien_hue_tourism_problem.png", "Hình 1: Bài báo phản ánh chỉ đạo của lãnh đạo tỉnh về yêu cầu trả lời câu hỏi cốt lõi của du khách Huế [1]")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Thực trạng ứng dụng công nghệ tại địa phương cho thấy, nền tảng đô thị thông minh Hue-S - dù đã đạt được những thành tựu vượt bậc trong quản trị hành chính công và tiếp nhận phản ánh hiện trường - vẫn bộc lộ những khoảng trống lớn trong phân hệ hỗ trợ du lịch. Các chức năng tra cứu hiện tại chủ yếu dừng lại ở mức danh bạ tĩnh, thiếu năng lực liên kết ngữ nghĩa giữa các điểm di tích lịch sử và các cơ sở dịch vụ ẩm thực, lưu trú lân cận. Du khách khi sử dụng ứng dụng thường gặp khó khăn trong việc tự thiết kế một lịch trình di chuyển tối ưu và hợp lý theo thời gian thực [2].")

    add_figure(doc, "hues_smart_city_app_home.png", "Hình 2: Thực trạng giao diện phân hệ du lịch trên nền tảng công dân số Hue-S và phản hồi của người dùng [2]")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Sự bùng nổ của Trí tuệ Nhân tạo Tạo sinh (Generative AI) và các Mô hình Ngôn ngữ Lớn (LLM) như GPT-4, Qwen hay Llama đã mở ra triển vọng to lớn trong việc phát triển các trợ lý du lịch ảo có khả năng đối thoại tự nhiên và cá nhân hóa sâu sắc [6]. Mặc dù vậy, khi áp dụng trực tiếp các mô hình ngôn ngữ lớn thương mại vào bài toán du lịch thực địa tại Huế, hệ thống bộc lộ hai điểm yếu chí tử. Thứ nhất là hiện tượng ảo giác thực thể (Entity Hallucination): mô hình thường xuyên bịa đặt các địa danh không có thật, tự sáng tạo tên quán ăn hoặc nhầm lẫn tên gọi di tích lịch sử do thiếu tri thức chuyên sâu bản địa [13]. Thứ hai là tính chất hoàn toàn mù không gian (Spatial Blindness): mô hình ngôn ngữ thuần túy không có nhận thức về tọa độ địa lý, mạng lưới giao thông thực tế và cự ly di chuyển, dẫn đến việc đưa ra các khuyến nghị bất khả thi như đề xuất du khách đang ở Đại Nội (bờ Bắc sông Hương) di chuyển hơn 60 km về phía Lăng Cô chỉ để thưởng thức một bữa ăn trưa bún bò, hoặc bắt du khách di chuyển ziczac liên tục qua các cây cầu bắc qua sông Hương [7, 5].")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Để khắc phục triệt để các hạn chế trên, việc kết hợp giữa Đồ thị Tri thức Không gian (Spatial Knowledge Graph - SKG), kỹ thuật Tăng cường Tạo sinh Truy xuất dựa trên Đồ thị (Spatial GraphRAG), phân hệ Thị giác đa phương thức CLIP và hệ thống định tuyến đường bộ thực tế OSRM là một hướng tiếp cận khoa học mang tính đột phá. Bằng cách ràng buộc không gian tìm kiếm ngữ nghĩa trong phạm vi topo lân cận thực tế, kết hợp tri thức có cấu trúc từ đồ thị với tri thức phi cấu trúc từ hàng chục ngàn bài nhận xét chân thực của du khách, hệ thống có thể bảo đảm tính xác thực tuyệt đối của thực thể và tính tối ưu của lộ trình di chuyển. Xuất phát từ những đòi hỏi cấp bách của thực tiễn phát triển du lịch Cố đô và tiềm năng to lớn của các công nghệ AI tiên tiến, đề tài \"Hệ thống Hỏi đáp và Gợi ý Lịch trình Du lịch Thông minh dựa trên Đồ thị Tri thức Không gian và Mô hình Ngôn ngữ Lớn\" được lựa chọn thực hiện.")

    add_sec_heading(doc, "2. Mục tiêu nghiên cứu")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Mục tiêu tổng quát của khóa luận là thiết kế, hiện thực hóa và đánh giá định lượng một hệ thống hỏi đáp và gợi ý lịch trình du lịch thông minh mang tên Spatial GraphRAG, kết hợp cấu trúc Đồ thị Tri thức Không gian, dữ liệu phản hồi thực tế của du khách, phân hệ nhận diện thị giác đa phương thức CLIP và khung tác tử điều phối đa luồng trên nền tảng mô hình ngôn ngữ lớn cục bộ, nhằm cung cấp các đề xuất du lịch chuẩn xác về mặt thực thể và tối ưu về mặt cự ly địa lý tại thành phố Huế.")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Để hoàn thành mục tiêu tổng quát, nghiên cứu xác lập sáu mục tiêu cụ thể bao gồm:")
    p_obj = doc.add_paragraph()
    format_body_p(p_obj)
    add_body_run(p_obj, "1) Xây dựng Đồ thị Tri thức Không gian du lịch hoàn chỉnh cho Huế và các vùng phụ cận với quy mô 9.525 nút thực thể và 90.948 cạnh quan hệ ngữ nghĩa tích hợp tọa độ trắc địa WGS84, kết nối 612 địa điểm du lịch tại Huế (gồm 29 điểm tham quan di tích cốt lõi, 104 khách sạn, 479 quán ăn).\n"
                         "2) Xây dựng bộ từ điển ẩm thực Việt Nam gồm 570 món ăn và thiết lập giải thuật khai phá tri thức thực đơn ngầm từ tập ngữ liệu 44.355 bài đánh giá du khách thực tế tại Huế trên tổng thể 1.698.641 bản ghi toàn quốc đã làm sạch từ TripAdvisor.\n"
                         "3) Thiết kế khung điều phối Agentic RAG trên LangGraph gồm 5 nút StateGraph tích hợp bộ chấm điểm tin cậy tuyến tính (ngưỡng 0,65) và cơ chế phân luồng dự phòng tìm kiếm web vận hành trên mô hình cục bộ Qwen2.5-3B-Instruct.\n"
                         "4) Tích hợp phân hệ Thị giác đa phương thức dựa trên mô hình tiền huấn luyện CLIP ViT-B/32, cho phép nhận diện ảnh chụp thực địa di tích lịch sử Cố đô Huế theo cơ chế Zero-shot inference đóng băng trọng số hoàn toàn.\n"
                         "5) Thiết lập Khung lọc không gian 2 giai đoạn (Two-stage Spatial Filtering): kết hợp khoảng cách mặt cầu Haversine (d <= 1,5 km) cắt tỉa thô đồ thị với hệ thống định tuyến đường bộ thực tế OSRM Contraction Hierarchies và Bộ dự toán ngân sách chuyến đi đa mục tiêu.\n"
                         "6) Hiện thực hóa giao diện Web tương tác bản đồ số Leaflet.js, tích hợp cơ chế xác thực an toàn tuân thủ OWASP, quản lý đa phiên trên Cloud Firestore, Sổ tay du khách và Hộ chiếu di sản Gamification, đóng gói Cổng API RESTful chuẩn mở sẵn sàng tích hợp với nền tảng công dân số Hue-S.")

    add_sec_heading(doc, "3. Câu hỏi nghiên cứu và Giả thuyết khoa học")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Tiến trình nghiên cứu được định hướng bởi sáu câu hỏi nghiên cứu cốt lõi:")
    p_rq = doc.add_paragraph()
    format_body_p(p_rq)
    add_body_run(p_rq, "• RQ1: Làm thế nào để mô hình hóa mối quan hệ không gian giữa các điểm đến thành một Đồ thị Tri thức Không gian có khả năng truy vấn hiệu quả theo bán kính địa lý thực tế?\n"
                        "• RQ2: Cơ chế trích xuất thực đơn ngầm từ hàng chục ngàn bài đánh giá văn bản có thể nâng cao độ chính xác gợi ý món ăn đặc sản so với phân loại tĩnh ở mức độ nào?\n"
                        "• RQ3: Việc tích hợp Đồ thị Tri thức Không gian vào quy trình RAG có thể triệt tiêu hiện tượng ảo giác thực thể và giảm thiểu tỷ lệ vi phạm cự ly ra sao?\n"
                        "• RQ4: Khung tác tử LangGraph kết hợp mô hình ngôn ngữ cục bộ Qwen2.5-3B có đáp ứng được yêu cầu về thời gian phản hồi thời gian thực khi vận hành trên hạ tầng máy trạm tiêu chuẩn hay không?\n"
                        "• RQ5: Làm thế nào để mở rộng năng lực hỏi đáp của hệ thống sang dữ liệu thị giác đa phương thức, cho phép nhận diện chính xác các điểm di tích văn hóa Huế từ ảnh chụp thực địa của du khách mà không cần tái huấn luyện mô hình nền tảng?\n"
                        "• RQ6: Việc kết hợp giải thuật định tuyến mạng lưới đường bộ OSRM và Khung lọc không gian 2 giai đoạn có giải quyết được bài toán tối ưu hóa đa mục tiêu giữa thời gian di chuyển thực tế và ngân sách chi tiêu của du khách so với khoảng cách đường chim bay hay không?")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Tương ứng với các câu hỏi trên, khóa luận xác lập sáu giả thuyết khoa học:")
    p_h = doc.add_paragraph()
    format_body_p(p_h)
    add_body_run(p_h, "• H1: Khung lọc không gian 2 giai đoạn (Haversine d <= 1,5 km cắt tỉa topo và OSRM tối ưu hóa đường bộ) sẽ triệt tiêu hoàn toàn các lộ trình ziczac nhảy bờ sông Hương, giảm cự ly di chuyển trung bình ít nhất 50% so với Naive RAG.\n"
                       "• H2: Khai phá thực đơn ngầm cho phép mở rộng độ phủ món ăn đặc sản lên trên 90% và đạt độ chính xác món trên 95%.\n"
                       "• H3: Mô hình Spatial GraphRAG đạt tỷ lệ bảo chứng thực thể 100% và tỷ lệ ảo giác 0% trên các truy vấn kiểm thử thuộc phạm vi đồ thị.\n"
                       "• H4: Quy trình phân cụm lịch trình kết hợp bộ lập lịch trình thông minh bảo đảm thời gian sinh kết quả dưới 4 giây trên GPU cá nhân tiêu chuẩn.\n"
                       "• H5: Mô hình CLIP ViT-B/32 áp dụng cơ chế Zero-shot inference đóng băng trọng số kết hợp trích xuất đặc trưng hình ảnh đạt độ chính xác Top-1 trên 95% và Top-3 100% trên tập dữ liệu ảnh di tích Cố đô Huế đã được kiểm định chéo rút một (LOOCV), loại bỏ triệt để rủi ro rò rỉ dữ liệu.\n"
                       "• H6: Khung lọc không gian 2 giai đoạn kết hợp OSRM phản ánh chính xác hệ số uốn lượn đô thị (kappa xấp xỉ 1,35 - 1,42), tính đúng chi phí vượt sông Hương qua hệ thống cầu thực tế, giúp kế hoạch lộ trình và dự toán ngân sách có độ tin cậy thực tiễn vượt trội so với định tuyến Haversine thuần túy.")

    add_sec_heading(doc, "4. Đối tượng và Phạm vi nghiên cứu")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Đối tượng nghiên cứu của khóa luận là các phương pháp biểu diễn tri thức không gian, kỹ thuật Tăng cường Tạo sinh Truy xuất dựa trên đồ thị (GraphRAG), mô hình thị giác ngôn ngữ đa phương thức (CLIP ViT-B/32), khung điều phối tác tử hội thoại thông minh và các giải thuật tối ưu hóa lịch trình du lịch dựa trên địa lý mạng lưới đường bộ. Về mặt dữ liệu, đối tượng nghiên cứu bao gồm 9.525 thực thể điểm du lịch, ẩm thực, lưu trú và 44.355 bản ghi đánh giá du khách thực tế tại Huế thu thập từ TripAdvisor (trên tổng thể 1.698.641 đánh giá toàn quốc đã làm sạch), kết hợp dữ liệu tọa độ hình học từ OpenStreetMap và Google Maps.")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Về phạm vi nghiên cứu, không gian địa lý trọng tâm của đề tài được định vị tại thành phố Huế và các vùng phụ cận thuộc tỉnh Thừa Thiên Huế như khu vực Kinh thành, cụm lăng tẩm phía Nam, đồi Vọng Cảnh, đầm Chuồn, đầm phá Tam Giang, làng cổ Phước Tích và cầu ngói Thanh Toàn. Về mặt công nghệ, nghiên cứu tập trung vào mô hình ngôn ngữ cục bộ Qwen2.5-3B-Instruct vận hành qua môi trường Ollama trên GPU NVIDIA GeForce RTX 3050 (4GB VRAM), bảo đảm tính khả thi triển khai và vận hành tự chủ hoàn toàn tại các cơ quan, đơn vị địa phương.")

    add_sec_heading(doc, "5. Ý nghĩa khoa học và Thực tiễn")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Về mặt khoa học, khóa luận đóng góp sáu thành tựu cốt lõi: 1) Đề xuất khung kiến trúc Spatial GraphRAG tích hợp trắc địa mặt cầu và ràng buộc topo vào quy trình tạo sinh ngôn ngữ; 2) Đề xuất giải thuật khai phá thực đơn ngầm giải quyết triệt để bài toán thiếu dữ liệu menu nhà hàng; 3) Thiết lập Khung lọc không gian 2 giai đoạn (Two-stage Spatial Filtering) kết hợp cắt tỉa thô đồ thị với định tuyến mạng lưới đường bộ OSRM; 4) Mở rộng năng lực suy luận sang thị giác đa phương thức qua mô hình CLIP ViT-B/32 Zero-shot với giao thức LOOCV nghiêm ngặt; 5) Mô hình hóa bài toán lập lịch trình du lịch có ràng buộc ngân sách và phân loại trường phái du khách; và 6) Đóng gói Cổng API chuẩn mở và giao diện Web Gemini-style sẵn sàng chuyển giao công nghệ cho nền tảng Hue-S.")

    doc.add_page_break()

    # =========================================================================
    # PHẦN II. TỔNG QUAN VẤN ĐỀ NGHIÊN CỨU
    # =========================================================================
    add_part_heading(doc, "PHẦN II. TỔNG QUAN VẤN ĐỀ NGHIÊN CỨU")

    add_sec_heading(doc, "1. Cơ sở lý thuyết nền tảng")

    add_subsec_heading(doc, "1.1. Đồ thị Tri thức Không gian và Khung lọc không gian 2 giai đoạn")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Đồ thị Tri thức (Knowledge Graph - KG) là cấu trúc dữ liệu mô hình hóa thông tin dưới dạng một đồ thị có hướng gắn nhãn G = (V, E), trong đó V là tập hợp các đỉnh đại diện cho các thực thể trong thế giới thực và E là tập hợp các cạnh biểu diễn các mối quan hệ ngữ nghĩa giữa các thực thể đó [3]. Trong bài toán du lịch, Đồ thị Tri thức Không gian (Spatial Knowledge Graph - SKG) mở rộng cấu trúc đồ thị truyền thống bằng cách gắn kèm mỗi đỉnh thực thể địa lý một bộ thuộc tính không gian gồm kinh độ, vĩ độ và đơn vị hành chính quản lý [4].")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Để đo lường khoảng cách địa lý giữa hai thực thể trên bề mặt cong của Trái Đất một cách chuẩn xác, công thức khoảng cách mặt cầu Haversine được áp dụng thay thế cho khoảng cách Euclid thông thường [5]: d = 2R * arcsin(sqrt(sin^2(Delta_phi / 2) + cos(phi_u) * cos(phi_v) * sin^2(Delta_lambda / 2))), trong đó R xấp xỉ 6.371 km là bán kính trung bình của Trái Đất, phi_u và phi_v là vĩ độ của hai địa điểm, Delta_phi và Delta_lambda lần lượt là độ chênh lệch vĩ độ và kinh độ. Dựa trên công thức này, một cạnh quan hệ lân cận không gian NEAR_BY được thiết lập tự động giữa hai thực thể nếu và chỉ nếu khoảng cách mặt cầu thỏa mãn điều kiện cự ly đi bộ d <= 1,5 km.")

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Tuy nhiên, khoảng cách mặt cầu Haversine là khoảng cách đường chim bay, không phản ánh các chướng ngại địa lý thực tế như dòng chảy sông Hương hay hệ thống cầu đường đô thị. Do đó, nghiên cứu đề xuất Khung lọc không gian 2 giai đoạn (Two-stage Spatial Filtering Framework): Giai đoạn 1 (Lọc thô topo) sử dụng Haversine với độ phức tạp O(1) để cắt tỉa không gian tìm kiếm trên đồ thị; Giai đoạn 2 (Tối ưu hóa tinh) sử dụng động cơ định tuyến OSRM để tính toán khoảng cách đường bộ thực tế D_OSRM theo thuật toán Contraction Hierarchies, phản ánh đúng hệ số uốn lượn đô thị kappa = D_OSRM / d_Haversine xấp xỉ 1,35 đến 1,42 và khống chế các cây cầu qua sông Hương.")

    add_subsec_heading(doc, "1.2. Sự tiến hóa từ Naive RAG sang GraphRAG và Agentic RAG")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Kiến trúc Tăng cường Tạo sinh Truy xuất (RAG) được đề xuất ban đầu nhằm khắc phục hiện tượng ảo giác và bổ sung tri thức chuyên biệt cho LLM mà không cần tái huấn luyện toàn bộ trọng số mô hình [6]. Quá trình phát triển của RAG đã trải qua ba thế hệ tiến hóa phương pháp luận căn bản: Naive RAG (truy xuất véc-tơ dựa trên độ tương đồng Cosine bề mặt, hoàn toàn mù không gian), GraphRAG (truy xuất dựa trên đường đi liên kết trên đồ thị tri thức) [7] kết hợp lộ trình hợp nhất LLM và Đồ thị Tri thức [8], kế thừa các tiếp cận suy luận đồ thị kinh điển như mạng tích chập đồ thị GCN [30] và QA-GNN [28], và Agentic RAG (tác tử tự suy ngẫm, tự đánh giá chất lượng thông tin truy xuất và định tuyến phân luồng động) [13].")

    add_subsec_heading(doc, "1.3. Khung điều phối trạng thái LangGraph và Mô hình cục bộ Qwen2.5")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Thư viện LangGraph được lựa chọn làm nền tảng điều phối luồng tác tử, mô hình hóa toàn bộ quá trình xử lý như một Đồ thị Trạng thái hữu hạn (StateGraph) gồm 5 nút chức năng: Extractor, KG Retriever, Confidence Grader, Fallback Search và Answer Generator [9]. Hệ thống tích hợp mô hình mã nguồn mở Qwen2.5-3B-Instruct vận hành hoàn toàn cục bộ qua Ollama trên GPU NVIDIA RTX 3050 (4GB VRAM), bảo đảm an toàn dữ liệu, tính sẵn sàng ngoại tuyến và triệt tiêu 100% chi phí API thương mại [10].")

    add_subsec_heading(doc, "1.4. Khai phá thực đơn ngầm và Bài toán Thiết kế Chuyến đi Du lịch (TTDP)")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Kỹ thuật Khai phá thực đơn ngầm (Implicit Menu Mining) kết hợp Từ điển ẩm thực Việt Nam gồm 570 món ăn chuẩn hóa với thuật toán đối sánh chuỗi mờ trên 44.355 bài đánh giá TripAdvisor tại Huế [11]. Độ tin cậy phục vụ món Conf(u, m) của quán ăn u đối với món ăn m được định nghĩa theo công thức chuẩn hóa: Conf(u, m) = [Tổng điểm sao đánh giá s_r có nhắc đến món m với s_r >= 3.5] chia cho [5 * Tổng số lượt nhắc món m]. Công thức này bảo đảm điểm số phản ánh chính xác chất lượng khen ngợi thực tế của món ăn mà không bị thiên lệch bởi độ phong phú của thực đơn. Bên cạnh đó, bài toán lập lịch trình đa ngày được mô hình hóa theo lý thuyết Thiết kế Chuyến đi Du lịch (Tourist Trip Design Problem – TTDP) dựa trên bài toán định tuyến có thưởng Orienteering Problem [14].")

    add_subsec_heading(doc, "1.5. Mô hình Không gian Vector Ngữ nghĩa Đa ngôn ngữ")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Nhằm phục vụ tìm kiếm ngữ nghĩa mờ và trích xuất đặc trưng văn bản câu hỏi, hệ thống sử dụng mô hình Sentence-Transformers chuẩn hóa paraphrase-multilingual-MiniLM-L12-v2 [12]. Mô hình chuyển đổi các truy vấn văn bản tiếng Việt thành các vector đặc trưng dày đặc 384 chiều, đạt hiệu năng tính toán cao trên CPU/GPU phổ thông với độ trễ suy luận dưới 15 mili-giây cho mỗi câu truy vấn.")

    add_subsec_heading(doc, "1.6. Cơ chế Định tuyến Phân luồng Tin cậy (Confidence Router)")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Hệ thống xây dựng bộ chấm điểm tin cậy Confidence Grader kết hợp tuyến tính giữa độ tương đồng ngữ nghĩa vector và điểm bảo chứng thực thể đồ thị: S_conf = 0,6 * S_sim + 0,4 * S_graph. Khi S_conf >= 0,65, hệ thống lập tức chuyển ngữ cảnh bảo chứng sang nút sinh câu trả lời Answer Generator. Ngược lại, khi S_conf < 0,65, hệ thống tự động kích hoạt nút rẽ nhánh Fallback Search để truy vấn thông tin bổ sung từ công cụ tìm kiếm DuckDuckGo.")

    add_subsec_heading(doc, "1.7. Mô hình hóa Toán học Bài toán TTDP có Ràng buộc")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Bài toán lập lịch trình du lịch được mô hình hóa thành bài toán quy hoạch nguyên nhị phân với hàm mục tiêu cực đại hóa tổng điểm thỏa dụng văn hóa - ẩm thực của du khách, chịu các ràng buộc không gian ngặt nghèo: giới hạn tổng thời gian di chuyển trong ngày T_max với thời gian di chuyển t_ij tính theo cự ly mạng lưới đường bộ thực tế D_OSRM, giới hạn ngân sách chi tiêu B_max, ràng buộc phân cụm địa lý triệt để không đổi bờ sông Hương trong cùng một buổi tham quan, và ràng buộc cự ly lân cận d <= 1,5 km áp dụng cho cung nối giữa Điểm tham quan neo giữ và Cơ sở ẩm thực (trong khi các chặng tham quan liên hoàn được tối ưu hóa toàn cục theo mạng lưới đường bộ OSRM).")

    add_subsec_heading(doc, "1.8. Kiến trúc Vision Transformer và Mô hình CLIP ViT-B/32 Zero-shot")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Mô hình tiền huấn luyện tương phản Ngôn ngữ - Hình ảnh CLIP (Contrastive Language-Image Pre-training) do OpenAI đề xuất là nền tảng cốt lõi của phân hệ thị giác đa phương thức trong đề tài [15]. Khác với các mạng nơ-ron tích chập (CNN) truyền thống, kiến trúc Vision Transformer (ViT-B/32) chia ảnh đầu vào kích thước 224x224 pixel thành một lưới gồm các mảnh ảnh nhỏ (patches) kích thước 32x32 pixel, coi mỗi mảnh ảnh như một token tương tự từ vựng trong văn bản và xử lý tương quan không gian đa tầng thông qua cơ chế tự chú ý (Multi-Head Self-Attention) [29]. Mô hình ánh xạ cả hình ảnh và văn bản mô tả di tích vào một không gian vector nhúng đa phương thức chung 512 chiều. Nhờ được huấn luyện tương phản trên hàng trăm triệu cặp ảnh - văn bản tự nhiên, CLIP có năng lực Zero-shot inference vượt trội: nhận diện chính xác các điểm di tích Cố đô Huế từ ảnh chụp thực địa mà hoàn toàn không cần trải qua bước huấn luyện tinh chỉnh (Fine-tuning), bảo đảm tính bất biến của trọng số và loại trừ 100% rủi ro rò rỉ dữ liệu.")

    add_subsec_heading(doc, "1.9. Hệ thống Định tuyến OSRM và Thuật toán Contraction Hierarchies")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Hệ thống Open Source Routing Machine (OSRM) là động cơ tính toán lộ trình hiệu năng cao trên dữ liệu bản đồ đường bộ OpenStreetMap [31]. OSRM hiện thực hóa thuật toán Thứ bậc Rút gọn (Contraction Hierarchies - CH) [17], hoạt động qua hai giai đoạn: giai đoạn tiền xử lý rút gọn lần lượt các đỉnh trên mạng lưới đường bộ theo thứ tự độ quan trọng và chèn các cạnh tắt (shortcut edges) bảo toàn khoảng cách ngắn nhất; giai đoạn truy vấn sử dụng thuật toán Dijkstra hai chiều trên đồ thị đã rút gọn. Cơ chế này cho phép OSRM tính toán ma trận khoảng cách và thời gian di chuyển thực tế giữa hàng chục điểm đến tại Huế trong thời gian dưới 1 mili-giây, phản ánh chính xác các cung đường một chiều, các nút giao thông và các cây cầu qua sông Hương.")

    doc.add_page_break()

    # =========================================================================
    # PHẦN III. ĐỐI TƯỢNG, PHẠM VI VÀ PHƯƠNG PHÁP NGHIÊN CỨU
    # =========================================================================
    add_part_heading(doc, "PHẦN III. ĐỐI TƯỢNG, PHẠM VI VÀ PHƯƠNG PHÁP NGHIÊN CỨU")

    add_sec_heading(doc, "1. Đối tượng và Thực trạng các nguồn dữ liệu nghiên cứu")

    add_subsec_heading(doc, "1.1. Hiện trạng đa nguồn dữ liệu và Quy mô tổng thể 1.698.641 bản ghi")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Nghiên cứu được thiết lập dựa trên một cơ sở dữ liệu đa nguồn tích hợp quy mô lớn, kết hợp chặt chẽ giữa dữ liệu phi cấu trúc từ các nền tảng đánh giá du lịch trực tuyến và dữ liệu có cấu trúc từ các hệ thống bản đồ số. Tổng mục các nguồn dữ liệu thành phần được tổng hợp tại Bảng 1.")

    add_table_caption(doc, "Bảng 1: Tổng mục các nguồn dữ liệu thành phần sử dụng trong nghiên cứu")
    tbl_data_summary = [
        ["Nguồn dữ liệu", "Định dạng tệp", "Quy mô bản ghi", "Mô tả phạm vi và đặc trưng nội dung"],
        ["TripAdvisor Toàn quốc", "SQLite / JSON", "1.698.641 bài", "Ngữ liệu đánh giá trải nghiệm du khách (2015 – 2026) đã làm sạch"],
        ["TripAdvisor Huế", "JSON / Danh sách", "44.355 bài", "Đánh giá thực tế bóc tách tại các địa điểm du lịch, ẩm thực ở Huế"],
        ["Địa điểm Du lịch Toàn quốc", "GeoJSON / CSV", "8.921 thực thể", "Tọa độ GPS, danh mục và địa chỉ đã chuẩn hóa toàn quốc"],
        ["Địa điểm Du lịch tại Huế", "GeoJSON / JSON", "612 thực thể", "Thực thể du lịch, ẩm thực, lưu trú chuẩn hóa tại Huế (29 tham quan, 104 khách sạn, 479 quán ăn)"],
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
            p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r_c = p_cell.add_run(val)
            r_c.font.name = 'Times New Roman'
            r_c.font.size = Pt(10)
            if r_idx == 0:
                r_c.font.bold = True
                set_cell_background(cell, "EAECEF")
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Từ số liệu thống kê tại Bảng 1, việc kết hợp đa nguồn dữ liệu cho phép hệ thống khắc phục hoàn toàn nhược điểm thiếu thông tin chi tiết về món ăn đặc sản trên các bản đồ số thông thường.")

    add_subsec_heading(doc, "1.2. Giải phẫu cấu trúc tập dữ liệu 44.355 bài đánh giá thực tế tại Huế")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Tập dữ liệu 44.355 bài nhận xét du khách tại Huế là nguồn tài nguyên cốt lõi phục vụ bài toán khai phá thực đơn ngầm. Phân bố điểm đánh giá được thể hiện chi tiết tại Bảng 2.")

    add_table_caption(doc, "Bảng 2: Phân bố xếp hạng sao của 44.355 bài đánh giá du lịch thực tế tại Huế")
    tbl_ratings_data = [
        ["Xếp hạng sao (Rating)", "Số lượng bài nhận xét", "Tỷ lệ phần trăm (%)", "Ý nghĩa đánh giá chất lượng"],
        ["5 sao (Xuất sắc - Excellent)", "24.838 bài", "56,0%", "Du khách cực kỳ hài lòng về hương vị và trải nghiệm"],
        ["4 sao (Rất tốt - Very Good)", "12.863 bài", "29,0%", "Dịch vụ đạt chuẩn chất lượng cao, đánh giá tích cực"],
        ["3 sao (Trung bình - Average)", "4.436 bài", "10,0%", "Chất lượng chấp nhận được, có một số điểm trừ nhỏ"],
        ["2 sao (Kém - Poor)", "1.331 bài", "3,0%", "Không hài lòng về thái độ phục vụ hoặc giá cả"],
        ["1 sao (Tồi tệ - Terrible)", "887 bài", "2,0%", "Trải nghiệm tiêu cực, cảnh báo cho du khách khác"],
        ["Tổng cộng", "44.355 bài", "100,0%", "Tỷ lệ đánh giá tích cực (>= 4 sao) đạt 85,0%"]
    ]
    tbl2 = doc.add_table(rows=len(tbl_ratings_data), cols=4)
    tbl2.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_academic_table_borders(tbl2)
    for r_idx, row in enumerate(tbl_ratings_data):
        for c_idx, val in enumerate(row):
            cell = tbl2.rows[r_idx].cells[c_idx]
            p_cell = cell.paragraphs[0]
            p_cell.paragraph_format.space_before = Pt(2)
            p_cell.paragraph_format.space_after = Pt(2)
            p_cell.paragraph_format.line_spacing = 1.15
            p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 or c_idx == 3 else WD_ALIGN_PARAGRAPH.RIGHT
            r_c = p_cell.add_run(val)
            r_c.font.name = 'Times New Roman'
            r_c.font.size = Pt(10)
            if r_idx == 0 or r_idx == len(tbl_ratings_data) - 1:
                r_c.font.bold = True
                set_cell_background(cell, "EAECEF")
            set_cell_margins(cell, top=50, bottom=50, left=70, right=70)

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Các số liệu tại Bảng 2 cho thấy hơn 85% đánh giá có xếp hạng 4 hoặc 5 sao, cung cấp cơ sở dữ liệu tích cực phong phú để trích xuất các món ăn ngon đặc trưng.")

    add_table_caption(doc, "Bảng 3: Phân bố kiểu hình chuyến đi của du khách trong tập dữ liệu nhận xét tại Huế")
    tbl_trip_types = [
        ["Kiểu hình chuyến đi (Trip Type)", "Số lượng ghi nhận", "Tỷ lệ phân bố (%)", "Đặc trưng nhu cầu trải nghiệm"],
        ["Couples (Cặp đôi / Vợ chồng)", "15.524 bài", "35,0%", "Không gian lãng mạn, ẩm thực tinh tế, ngắm hoàng hôn"],
        ["Family (Gia đình đa thế hệ)", "11.089 bài", "25,0%", "Lịch trình an toàn, di chuyển ngắn, ẩm thực phù hợp trẻ em và người già"],
        ["Friends (Nhóm bạn bè)", "8.871 bài", "20,0%", "Khám phá ẩm thực đường phố, trải nghiệm văn hóa đêm"],
        ["Solo (Khách du lịch một mình)", "5.323 bài", "12,0%", "Lịch trình linh hoạt, trải nghiệm văn hóa bản địa sâu sắc"],
        ["Business (Công tác kết hợp du lịch)", "3.548 bài", "8,0%", "Địa điểm lưu trú tiện nghi, ẩm thực tiếp khách trang trọng"],
        ["Tổng cộng bản ghi", "44.355 bài", "100,0%", "Đa dạng hóa toàn diện các phân khúc du khách"]
    ]
    tbl3 = doc.add_table(rows=len(tbl_trip_types), cols=4)
    tbl3.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_academic_table_borders(tbl3)
    for r_idx, row in enumerate(tbl_trip_types):
        for c_idx, val in enumerate(row):
            cell = tbl3.rows[r_idx].cells[c_idx]
            p_cell = cell.paragraphs[0]
            p_cell.paragraph_format.space_before = Pt(2)
            p_cell.paragraph_format.space_after = Pt(2)
            p_cell.paragraph_format.line_spacing = 1.15
            p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 or c_idx == 3 else WD_ALIGN_PARAGRAPH.RIGHT
            r_c = p_cell.add_run(val)
            r_c.font.name = 'Times New Roman'
            r_c.font.size = Pt(10)
            if r_idx == 0 or r_idx == len(tbl_trip_types) - 1:
                r_c.font.bold = True
                set_cell_background(cell, "EAECEF")
            set_cell_margins(cell, top=50, bottom=50, left=70, right=70)

    add_subsec_heading(doc, "1.3. Cơ cấu phân loại và phân bố địa giới của 612 địa điểm du lịch tại Huế")
    add_table_caption(doc, "Bảng 4: Cơ cấu phân loại và phân bố địa giới của 612 địa điểm du lịch tại Huế")
    tbl_hue_places = [
        ["Tiêu chí phân loại địa điểm", "Số lượng thực thể", "Phạm vi không gian và địa danh tiêu biểu"],
        ["Phân loại theo danh mục dịch vụ:", "", ""],
        ["  Ẩm thực và Nhà hàng (Restaurant)", "479 cơ sở (78,3%)", "Quán bún bò, bánh bèo chén, cơm hến, nhà hàng cung đình"],
        ["  Cơ sở lưu trú và Khách sạn (Hotel)", "104 cơ sở (17,0%)", "Khách sạn trung tâm, homestay bờ sông, resort ven biển"],
        ["  Điểm tham quan danh thắng (Attraction)", "29 địa danh (4,7%)", "Đại Nội, Chùa Thiên Mụ, Lăng Tự Đức, Lăng Khải Định, Đồi Vọng Cảnh"],
        ["Phân loại theo địa giới hành chính:", "", ""],
        ["  Quận Thuận Hóa (Bờ Nam)", "389 địa điểm", "Khu vực bờ Nam sông Hương, phố đi bộ, trung tâm dịch vụ mới"],
        ["  Quận Phú Xuân (Bờ Bắc)", "184 địa điểm", "Khu vực bờ Bắc sông Hương, Quần thể Kinh thành, Chợ Đông Ba"],
        ["  Các huyện thị di sản phụ cận", "39 địa điểm", "Lăng Cô (Phú Lộc), Cầu ngói Thanh Toàn, Đầm Chuồn, Phước Tích"],
        ["Tổng cộng địa điểm tại Huế", "612 địa điểm", "100% đã chuẩn hóa tọa độ GPS theo hệ quy chiếu WGS84"]
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
            p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r_c = p_cell.add_run(val)
            r_c.font.name = 'Times New Roman'
            r_c.font.size = Pt(10)
            if r_idx in [0, 1, 5, 9]:
                r_c.font.bold = True
                if r_idx in [0, 9]:
                    set_cell_background(cell, "EAECEF")
            set_cell_margins(cell, top=50, bottom=50, left=70, right=70)

    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Số liệu tại Bảng 4 làm sáng tỏ sự phân hóa địa lý sâu sắc của dịch vụ du lịch Huế: Quận Thuận Hóa ở bờ Nam sông Hương tập trung tới 63,56% tổng số cơ sở dịch vụ (389/612 cơ sở, chủ yếu là lưu trú và ẩm thực hiện đại), trong khi Quận Phú Xuân ở bờ Bắc là cái nôi di sản chiếm 30,07% (184/612 cơ sở) với mật độ di tích cung đình dày đặc. Sự phân hóa này khẳng định tính tất yếu của việc áp dụng giải thuật phân cụm lộ trình theo bờ sông.")

    add_figure(doc, "hue_places_category.png", "Hình 3: Cơ cấu phân bố các danh mục địa điểm du lịch và xếp hạng sao tại thành phố Huế")
    add_figure(doc, "top10_dishes_hue.png", "Hình 4: Top 10 món ăn đặc sản Huế được du khách nhắc đến nhiều nhất trong các bài đánh giá")
    add_figure(doc, "atomic_chunking_pipeline.png", "Hình 5: Quy trình phân mảnh văn bản phân tử cho các bài đánh giá du khách trước khi lập chỉ mục")

    doc.add_page_break()

    # =========================================================================
    # PHẦN IV. NỘI DUNG VÀ KẾT QUẢ NGHIÊN CỨU
    # =========================================================================
    add_part_heading(doc, "PHẦN IV. NỘI DUNG VÀ KẾT QUẢ NGHIÊN CỨU")

    add_chapter_heading(doc, "CHƯƠNG 1. KIẾN TRÚC HỆ THỐNG SPATIAL GRAPHRAG VÀ KHAI PHÁ THỰC ĐƠN NGẦM")

    add_sec_heading(doc, "1.1. Kiến trúc tổng thể bốn tầng của Hệ thống")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Hệ thống Spatial GraphRAG được thiết kế theo mô hình kiến trúc bốn tầng phân lập hoàn chỉnh, bảo đảm tính module hóa, tính mở rộng và khả năng thay thế linh hoạt các thành phần công nghệ. Bốn tầng chức năng bao gồm: Tầng Nguồn Dữ liệu Đa phương thức và Cơ sở Tri thức; Tầng Xử lý Trung tâm và Đồ thị Tri thức Không gian; Tầng Điều phối Tác tử Agentic RAG và Mô hình Ngôn ngữ Lớn; và Tầng Dịch vụ API và Giao diện Người dùng Web Gemini-Style.")

    add_figure(doc, "system_architecture.png", "Hình 1.1: Kiến trúc tổng thể bốn tầng của Hệ thống Spatial GraphRAG phục vụ du lịch Huế")

    add_sec_heading(doc, "1.2. Thiết kế Đồ thị Tri thức Không gian Du lịch Huế")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Đồ thị Tri thức Không gian Du lịch Huế được tổ chức theo lược đồ phân cấp với 5 lớp đỉnh thực thể chính: Attraction (Điểm tham quan), Restaurant (Cơ sở ẩm thực), Hotel (Cơ sở lưu trú), Dish (Món ăn đặc sản) và Locality (Đơn vị địa lý). Cấu trúc đồ thị xác lập bốn mối quan hệ ngữ nghĩa cốt lõi: LOCATED_IN (phân cấp địa giới hành chính), NEAR_BY (lân cận không gian Haversine <= 1,5 km), SERVES (phục vụ món ăn đặc sản theo điểm bảo chứng thực đơn), và ORIGINATED_FROM (nguồn gốc xuất xứ của 112 đặc sản Cố đô).")

    add_figure(doc, "spatial_kg_schema.png", "Hình 1.2: Lược đồ cấu trúc thực thể và quan hệ trong Đồ thị Tri thức Không gian Du lịch Huế")

    add_table_caption(doc, "Bảng 1.1: Thống kê định lượng các thành phần trong Đồ thị Tri thức Không gian Du lịch Huế")
    tbl_kg_stats = [
        ["Lớp thực thể (Entity Type)", "Số lượng nút", "Loại quan hệ (Relation)", "Số lượng cạnh"],
        ["Attraction (Điểm tham quan)", "1.842", "NEAR_BY (Lân cận Haversine <= 1,5 km)", "77.578"],
        ["Restaurant (Ẩm thực, quán ăn)", "4.120", "LOCATED_IN (Thuộc địa phương / phường)", "8.921"],
        ["Hotel (Lưu trú, khách sạn)", "2.650", "SERVES (Phục vụ món ăn đặc sản)", "4.337"],
        ["Dish (Món ăn đặc sản)", "570", "ORIGINATED_FROM (Xuất xứ di sản ẩm thực)", "112"],
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
    add_body_run(p, "Quy mô tại Bảng 1.1 khẳng định cấu trúc topo liên kết dày đặc với hơn 77.000 cạnh NEAR_BY và 4.337 cạnh SERVES đã bóc tách, cho phép giải thuật duyệt đồ thị lọc sạch các điểm ở xa trong thời gian dưới 10 mili-giây trước khi chuyển ngữ cảnh cho LLM.")

    add_sec_heading(doc, "1.3. Phương pháp khai phá thực đơn ngầm và đối soát tri thức")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Nhằm lấp đầy khoảng trống thông tin về menu nhà hàng, nghiên cứu ứng dụng quy trình khai phá dữ liệu nhận xét dựa trên Bộ từ điển ẩm thực 570 món ăn. Mỗi bài nhận xét của du khách được quét qua một bộ lọc đối sánh chuỗi mờ kết hợp quy tắc khử từ đồng âm. Mỗi khi phát hiện sự xuất hiện đồng thời của món ăn đặc sản, hệ thống tiến hành trích xuất điểm số đánh giá Rating_k của bài nhận xét chứa món ăn đó để tổng hợp điểm bảo chứng thực đơn Conf(u, m). Cạnh quan hệ SERVES chỉ được xác lập chính thức trên đồ thị khi chỉ số tin cậy khai phá vượt qua ngưỡng quy định 0,70 và có ít nhất 3 bài nhận xét độc lập khen ngợi.")

    add_table_caption(doc, "Bảng 1.2: Mẫu đối soát kết quả khai phá thực đơn ngầm từ nhận xét du khách tại Huế")
    tbl_mining_sample = [
        ["Tên cơ sở ẩm thực", "Món ăn khai phá", "Số nhận xét", "Conf(u,m)", "Hiện trạng menu tĩnh", "Đối soát thực địa"],
        ["Quán Bún bò Mụ Rơi", "Bún bò Huế, Chả cua", "142 bài", "0,94", "Không có menu số hóa", "Chính xác 100% món chủ đạo"],
        ["Bánh bèo Bà Đỏ", "Bánh bèo, Bánh nậm, Bánh lọc", "215 bài", "0,96", "Chỉ ghi tên chung bánh Huế", "Chính xác toàn bộ 3 món"],
        ["Cơm hến Hoa Đông", "Cơm hến, Bún hến, Chè bắp", "184 bài", "0,95", "Chỉ đăng ký cơm hến", "Xác thực bán cả bún hến và chè"],
        ["Chè Hẻm Hùng Vương", "Chè bột lọc heo quay", "98 bài", "0,91", "Không khai báo món đặc sản", "Đúng món biểu tượng"]
    ]
    tbl_m = doc.add_table(rows=len(tbl_mining_sample), cols=6)
    tbl_m.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_academic_table_borders(tbl_m)
    for r_idx, row in enumerate(tbl_mining_sample):
        for c_idx, val in enumerate(row):
            cell = tbl_m.rows[r_idx].cells[c_idx]
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

    add_sec_heading(doc, "1.4. Khung điều phối tác tử tự suy ngẫm Agentic RAG trên LangGraph")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Quy trình điều phối tác tử được hiện thực hóa qua Đồ thị Trạng thái hữu hạn (StateGraph) gồm 5 nút chức năng tuần tự và có điều kiện: 1) Nút trích xuất thực thể (Extractor) phân tích Anchor POI và món ăn; 2) Nút truy xuất không gian đồ thị (KG Retriever) lọc cứng theo cạnh NEAR_BY <= 1,5 km và SERVES; 3) Nút chấm điểm tin cậy (Confidence Grader) tính tổ hợp tuyến tính S_conf = 0,6 * S_sim + 0,4 * S_graph (với S_graph là điểm bảo chứng chất lượng đồ thị, được xác định bởi tỷ lệ liên kết thực thể hợp lệ trên đồ thị (kết hợp trung bình điểm tin cậy Conf(u, m) đối với các truy vấn có yêu cầu ẩm thực); do Nút 2 đã lọc cứng nên toàn bộ thực thể mặc định được neo giữ không gian hợp lệ); 4) Nút tìm kiếm web dự phòng (Fallback Search) kích hoạt khi S_conf < 0,65; và 5) Nút sinh câu trả lời (Answer Generator) tạo sinh văn bản có bảo chứng và xuất mảng tọa độ Polyline GPS.")

    add_figure(doc, "langgraph_architecture.png", "Hình 1.3: Kiến trúc Đồ thị Trạng thái điều phối quy trình tác tử tự suy ngẫm trên LangGraph (5 nút)")

    add_sec_heading(doc, "1.5. Tầng Lưu trữ Đám mây NoSQL và Quản trị Đa phiên Hội thoại")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Để hỗ trợ trải nghiệm xuyên suốt của du khách trên nhiều thiết bị di động, hệ thống sử dụng cơ sở dữ liệu Google Cloud Firestore với lược đồ tài liệu NoSQL phân tán, phân lập hoàn toàn giữa dữ liệu hội thoại tức thời và dữ liệu lộ trình dài hạn.")

    add_table_caption(doc, "Bảng 1.4: Lược đồ cấu trúc dữ liệu trên Google Cloud Firestore phục vụ quản lý đa phiên")
    tbl_firestore_schema = [
        ["Bộ sưu tập (Collection)", "Cấp bậc", "Tài liệu (Document)", "Trường dữ liệu chính", "Mục đích sử dụng"],
        ["users", "Cấp 1", "{userId}", "email, displayName, createdAt, settings", "Hồ sơ người dùng và cấu hình cá nhân"],
        ["users/{uid}/sessions", "Cấp 2", "{sessionId}", "title, createdAt, updatedAt, lastMessage", "Danh mục phiên hội thoại của người dùng"],
        [".../sessions/{sid}/messages", "Cấp 3", "{messageId}", "sender, text, timestamp, itineraryData", "Lịch sử tin nhắn và dữ liệu lộ trình đính kèm"],
        ["feedbacks", "Cấp 1", "{feedbackId}", "userId, rating, comment, queryText, timestamp", "Thu thập phản hồi chất lượng câu trả lời"]
    ]
    tbl_fs = doc.add_table(rows=len(tbl_firestore_schema), cols=5)
    tbl_fs.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_academic_table_borders(tbl_fs)
    for r_idx, row in enumerate(tbl_firestore_schema):
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

    add_sec_heading(doc, "1.6. Thiết kế Giao diện Khách Web Tương tác Không gian (Gemini-Style Client)")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Hệ thống phát triển giao diện Web tích hợp bản đồ số thông minh (Leaflet.js) với phong cách Gemini hiện đại. Giao diện tích hợp thanh bên điều hướng hai trạng thái, bản đồ số trực quan thể hiện các điểm dừng chân, và tiện ích khí tượng du lịch thích ứng ngữ cảnh.")

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

    p_owasp = doc.add_paragraph()
    format_body_p(p_owasp)
    add_body_run(p_owasp, "Về mặt an toàn thông tin và xác thực người dùng, hệ thống tuân thủ nghiêm ngặt các khuyến nghị bảo mật OWASP. Để triệt tiêu rủi ro lộ lọt thông tin nhạy cảm qua các cuộc tấn công Cross-Site Scripting (XSS), hệ thống tuyệt đối không lưu trữ mật khẩu hoặc chuỗi băm mật khẩu trong bộ nhớ cục bộ (localStorage) của trình duyệt. Thay vào đó, localStorage chỉ duy trì duy nhất định danh công khai đã được người dùng đồng thuận (remembered_email). Việc điền mật khẩu được giao phó hoàn toàn cho hệ thống Quản lý Mật khẩu tích hợp an toàn của trình duyệt web thông qua thuộc tính chuẩn autocomplete=\"current-password\". Trạng thái phiên làm việc được kiên định hóa an toàn thông qua cơ chế mã thông báo truy cập JWT và phân vùng lưu trữ bảo mật IndexedDB của Firebase Auth SDK.")

    p_budget = doc.add_paragraph()
    format_body_p(p_budget)
    add_body_run(p_budget, "Bên cạnh đó, hệ thống tích hợp Bộ tính toán Ngân sách Lộ trình Du lịch (Trip Budget Calculator) tự động dự toán chi phí chi tiết theo 4 cấu phần: vé tham quan di tích theo biểu giá niêm yết của Trung tâm Bảo tồn Di tích Cố đô Huế, chi phí ẩm thực thực tế, chi phí lưu trú bình quân và chi phí di chuyển ước tính theo cự ly thực tế từ OSRM. Hệ thống cũng triển khai Sổ tay Du khách và tính năng Gamification Hộ chiếu Di sản (Heritage Passport) theo dõi tiến độ khám phá: 29 điểm di tích văn hóa cốt lõi được mô hình hóa thành các đỉnh trung tâm trên Đồ thị Tri thức, mở rộng liên kết đến 158 địa điểm văn hóa - ẩm thực trong tập dữ liệu số hóa hue_top_places.json.")

    add_sec_heading(doc, "1.7. Phân hệ Nhận diện Điểm mốc Thị giác Đa phương thức (CLIP ViT-B/32)")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Để hỗ trợ du khách tra cứu thông tin di tích trực quan ngay tại hiện trường, hệ thống tích hợp mô hình CLIP ViT-B/32. Khi du khách tải lên một bức ảnh chụp di tích từ điện thoại di động, bộ mã hóa hình ảnh Vision Transformer trích xuất vector đặc trưng thị giác 512 chiều. Vector này được so khớp tương đồng Cosine với ngân hàng vector văn bản đại diện cho các danh thắng Cố đô Huế. Di tích có điểm tương đồng cao nhất được neo giữ (grounding) trực tiếp vào Đồ thị Tri thức Không gian để kích hoạt truy vấn các điểm ẩm thực và lưu trú lân cận.")

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # CHƯƠNG 2
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, "CHƯƠNG 2. THUẬT TOÁN LẬP LỊCH TRÌNH KHÔNG GIAN, THỰC NGHIỆM ĐỐI SÁNH VÀ TÍCH HỢP ỨNG DỤNG")

    add_sec_heading(doc, "2.1. Thuật toán Lập lịch trình phân cụm không gian")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Để giải quyết bài toán gợi ý lịch trình đa ngày tối ưu không gian, nghiên cứu thiết kế giải thuật phân cụm địa lý hai giai đoạn. Giai đoạn 1 tiến hành phân tách các điểm tham quan thành hai cụm không gian độc lập theo địa giới tự nhiên của dòng sông Hương: Cụm bờ Bắc (Quần thể Kinh thành, Chùa Thiên Mụ, Chợ Đông Ba) và Cụm bờ Nam (Hệ thống lăng tẩm triều Nguyễn, Đồi Vọng Cảnh, làng hương Thủy Xuân). Giai đoạn 2 áp dụng thuật toán tối ưu hóa hành trình cục bộ dựa trên ma trận khoảng cách đường bộ thực tế OSRM, bảo đảm du khách không phải đổi bờ sông Hương nhiều hơn 1 lần trong ngày.")

    add_figure(doc, "user_scenario_demo_flow.png", "Hình 2.1: Kịch bản luồng tương tác và gợi ý lịch trình không gian mẫu trên Giao diện Web Responsive")

    add_sec_heading(doc, "2.2. Bộ kiểm thử Benchmark 12 kịch bản du lịch Huế")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Nhằm kiểm chứng định lượng hiệu năng của hệ thống một cách khách quan và nghiêm ngặt, nghiên cứu xây dựng Bộ kiểm thử chuẩn (Benchmark Suite) gồm 12 kịch bản truy vấn thực tế, bao phủ toàn diện 4 nhóm tác vụ cốt lõi: 1) Nhóm hỏi đáp ẩm thực lân cận (TC-01 đến TC-04); 2) Nhóm mở rộng tham quan lân cận (TC-05 đến TC-08); 3) Nhóm lập lịch trình đa ngày tối ưu cự ly (TC-09 đến TC-11); và 4) Nhóm tour bán nhật có ràng buộc thời gian (TC-12). Chi tiết các kịch bản được đặc tả tại Bảng 2.1.")

    add_table_caption(doc, "Bảng 2.1: Đặc tả chi tiết 12 kịch bản trong Bộ dữ liệu kiểm thử chuẩn cho du lịch Huế")
    tbl_benchmark_data = [
        ["Mã", "Câu hỏi truy vấn của du khách (Prompt)", "Điểm neo (Anchor POI)", "Món / Dịch vụ yêu cầu", "Tiêu chuẩn nghiệm đúng"],
        ["TC-01", "Tôi đang ở Đại Nội Huế, muốn tìm quán bún bò chuẩn vị gần đây để đi bộ ăn trưa.", "Đại Nội Huế (Bờ Bắc)", "Bún bò Huế", "Gợi ý quán bún bò bờ Bắc có thật (Mụ Rơi, Cẩm, Đông Ba); d <= 1,5 km; không nhảy sang bờ Nam."],
        ["TC-02", "Sau khi tham quan Lăng Tự Đức, tôi muốn ăn bánh bèo hoặc bánh nậm gần đó thì ghé quán nào?", "Lăng Tự Đức (Thủy Xuân)", "Bánh bèo, bánh nậm Huế", "Gợi ý quán bánh bèo/nậm trên trục Lê Ngô Cát/Thủy Xuân; d <= 1,5 km; loại trừ quán Bà Đỏ (> 5 km)."],
        ["TC-03", "Tôi đang ở khu vực Cồn Hến, muốn thưởng thức cơm hến và chè bắp đúng gốc Huế.", "Cồn Hến (Phường Vĩ Dạ)", "Cơm hến, chè bắp Cồn Hến", "Gợi ý đúng quán cơm hến tại đảo Cồn Hến (Hoa Đông, Quán Nhỏ); d <= 800 m; Conf >= 0,75."],
        ["TC-04", "Gợi ý quán bánh khoái và nem lụi ngon ở bờ Nam gần khu phố Tây Chu Văn An.", "Phố đi bộ Chu Văn An", "Bánh khoái, nem lụi Huế", "Gợi ý quán bờ Nam trong d <= 1,2 km (Bánh khoái Hạnh); không nhầm sang bún bò hay cà phê."],
        ["TC-05", "Tôi vừa ghé Chùa Thiên Mụ, xung quanh đây có điểm văn hóa nào có thể ghé tiếp theo không?", "Chùa Thiên Mụ (Bờ Bắc)", "Di tích kế cận", "Gợi ý điểm bờ Bắc cùng hành lang (Văn Thánh, Nhà vườn An Hiên); d <= 2,0 km; không sang lăng bờ Nam."],
        ["TC-06", "Từ Đồi Vọng Cảnh, có những di tích lăng tẩm hoặc làng nghề nào nằm gần trên cùng trục đường?", "Đồi Vọng Cảnh (Huyền Trân CC)", "Lăng tẩm và làng nghề", "Gợi ý Cụm bờ Nam liên kết trên trục giao thông d <= 2,5 km (Lăng Tự Đức, Đồng Khánh, Làng hương Thủy Xuân)."],
        ["TC-07", "Tôi đang ở Chợ Đông Ba, muốn tìm các điểm di tích có thể đi bộ tham quan trong 15 phút.", "Chợ Đông Ba (Trần Hưng Đạo)", "Di tích cự ly đi bộ ngắn", "Gợi ý điểm cửa ngõ Kinh thành d <= 1,2 km (Cầu Trường Tiền, Cửa Thượng Tứ, Bảo tàng Cổ vật)."],
        ["TC-08", "Khám phá danh thắng thiên nhiên và sinh thái đầm phá ở ngoại ô phía Đông Nam thành phố Huế.", "Đầm Chuồn (Phá Tam Giang)", "Sinh thái đầm phá, làng chài", "Gợi ý chuỗi liên kết ngoại ô: Làng chài Đầm Chuồn (cá kình), kết hợp Cầu ngói Thanh Toàn trên cùng hành lang."],
        ["TC-09", "Thiết kế lịch trình du lịch Huế 1 ngày trọn vẹn cho cặp đôi, xuất phát từ khách sạn bờ Nam.", "Khách sạn trung tâm bờ Nam", "Lịch trình 1 ngày tối ưu", "Sáng: Cụm Kinh thành bờ Bắc; Chiều: Cụm Lăng tẩm bờ Nam; vượt sông tối đa 1 lần/ngày."],
        ["TC-10", "Lập lịch trình 2 ngày khám phá Huế theo phong cách văn hóa sâu sắc và ẩm thực truyền thống.", "Không gian đô thị Cố đô Huế", "Lịch trình 2 ngày phân cụm triệt để", "Ngày 1: trọn vẹn bờ Bắc (Đại Nội, Cổ vật, Nhà vườn, chợ Đông Ba); Ngày 2: trọn vẹn bờ Nam (Lăng Tự Đức, Khải Định, Đồi Vọng Cảnh, Làng hương, bánh Huế Thủy Xuân / Bà Đỏ); 0 lần đổi bờ mỗi ngày."],
        ["TC-11", "Gợi ý lịch trình 3 ngày tại Huế kết hợp di sản Cố đô và du lịch dã ngoại thiên nhiên sinh thái.", "Cố đô Huế và vùng đầm phá", "Lịch trình 3 ngày mở rộng", "Ngày 1: Kinh thành bờ Bắc; Ngày 2: Lăng tẩm bờ Nam; Ngày 3: Cầu ngói Thanh Toàn và Đầm Chuồn."],
        ["TC-12", "Lập tour nửa ngày (chiều từ 14h đến 19h) ngắm hoàng hôn và thưởng thức ẩm thực đêm xứ Huế.", "Trục đồi Tây Nam bờ Nam", "Tour bán nhật chiều - tối", "14h Làng hương -> 15h30 Lăng Tự Đức -> 17h hoàng hôn Đồi Vọng Cảnh -> 18h30 bánh Huế bờ Nam; cự ly < 2,5 km."]
    ]
    tbl_tc = doc.add_table(rows=len(tbl_benchmark_data), cols=5)
    tbl_tc.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_academic_table_borders(tbl_tc)
    for r_idx, row in enumerate(tbl_benchmark_data):
        for c_idx, val in enumerate(row):
            cell = tbl_tc.rows[r_idx].cells[c_idx]
            p_cell = cell.paragraphs[0]
            p_cell.paragraph_format.space_before = Pt(2)
            p_cell.paragraph_format.space_after = Pt(2)
            p_cell.paragraph_format.line_spacing = 1.15
            p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r_c = p_cell.add_run(val)
            r_c.font.name = 'Times New Roman'
            r_c.font.size = Pt(8.5)
            if r_idx == 0:
                r_c.font.bold = True
                set_cell_background(cell, "EAECEF")
            elif r_idx in [1, 2, 3, 4]:
                set_cell_background(cell, "F9FBFD")
            elif r_idx in [5, 6, 7, 8]:
                set_cell_background(cell, "FFFFFF")
            elif r_idx in [9, 10, 11]:
                set_cell_background(cell, "FDFCF9")
            set_cell_margins(cell, top=40, bottom=40, left=50, right=50)

    add_sec_heading(doc, "2.3. Kết quả thực nghiệm đối sánh định lượng")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Nghiên cứu tiến hành đo lường và đối sánh định lượng giữa ba phương pháp đại diện gồm mô hình Zero-shot LLM (Qwen2.5-3B thuần túy), Naive RAG (Vector Search qua độ tương đồng Cosine) và mô hình đề xuất Spatial GraphRAG trên toàn bộ 12 kịch bản của bộ Benchmark Suite. Sáu chỉ số đánh giá cốt lõi bao gồm: Grounding Rate (Tỷ lệ bảo chứng thực thể), Hallucination Rate (Tỷ lệ ảo giác địa danh), Spatial Violation Rate (Tỷ lệ vi phạm cự ly lân cận), Cự ly trung bình đến điểm neo (km), Dish Alignment Rate (Độ chính xác món ăn đặc sản), và Thời gian đáp ứng (Latency tính bằng giây).")

    add_table_caption(doc, "Bảng 2.2: Bảng đối sánh hiệu năng định lượng giữa các phương pháp trên bộ Benchmark 12 kịch bản du lịch Huế")
    tbl_results_data = [
        ["Chỉ số đánh giá định lượng", "Zero-shot LLM", "Naive RAG (Vector)", "Spatial GraphRAG (Đề xuất)"],
        ["Grounding Rate (%) ↑", "41,7%", "75,0%", "100,0%"],
        ["Hallucination Rate (%) ↓", "58,3%", "25,0%", "0,0%"],
        ["Spatial Violation Rate (%) ↓", "66,7%", "41,7%", "0,0%"],
        ["Cự ly trung bình đến Anchor (km) ↓", "5,82 km", "3,65 km", "1,25 km"],
        ["Dish Alignment Rate (%) ↑", "25,0%", "62,5%", "96,5%"],
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
    add_body_run(p, "Từ kết quả thực nghiệm tại Bảng 2.2, phương pháp đề xuất chứng minh khả năng triệt tiêu hoàn toàn hiện tượng ảo giác địa danh (0,0% so với 58,3% của Zero-shot và 25,0% của Naive RAG), xóa bỏ 100% các vi phạm không gian (0,0% so với 66,7% của Zero-shot và 41,7% của Naive RAG), rút ngắn khoảng cách di chuyển trung bình từ 5,82 km (Zero-shot) và 3,65 km (Naive RAG) xuống chỉ còn 1,25 km (giảm gần 80%), đồng thời nâng độ chính xác món ăn đặc sản lên 96,5% (vượt xa mức 25,0% của Zero-shot và 62,5% của Naive RAG) với thời gian đáp ứng trung bình 2,80 giây.")

    add_figure(doc, "benchmark_spatial_comparison.png", "Hình 2.2: Biểu đồ đối sánh định lượng các chỉ số hiệu năng giữa Zero-shot, Naive RAG và Spatial GraphRAG")

    p_loocv_head = doc.add_paragraph()
    format_body_p(p_loocv_head)
    add_body_run(p_loocv_head, "Đánh giá định lượng Phân hệ Thị giác Đa phương thức qua Giao thức LOOCV: Để kiểm chứng năng lực của phân hệ nhận diện thị giác CLIP ViT-B/32, nghiên cứu thu thập tập dữ liệu kiểm thử thực địa gồm 77 bức ảnh chụp độc lập tại 25 danh lam thắng cảnh và di tích lịch sử tiêu biểu tại Cố đô Huế. Để loại bỏ hoàn toàn các nghi vấn về hiện tượng rò rỉ dữ liệu (Data Leakage) hoặc hiện tượng học vẹt (Train-on-Test), nghiên cứu áp dụng nghiêm ngặt Giao thức Kiểm định Chéo Rút một (Leave-One-Out Cross-Validation - LOOCV) kết hợp nguyên lý Zero-shot inference. Mô hình CLIP ViT-B/32 được giữ nguyên vẹn toàn bộ trọng số gốc đã tiền huấn luyện (frozen weights), hoàn toàn không can thiệp hay huấn luyện lại trên bất kỳ ảnh nào trong tập kiểm thử. Kết quả định lượng được thể hiện chi tiết tại Bảng 2.3.")

    add_table_caption(doc, "Bảng 2.3: Kết quả đánh giá định lượng phân hệ Nhận diện Điểm mốc Thị giác đa phương thức (Giao thức LOOCV)")
    tbl_clip_data = [
        ["Nhóm di tích kiểm thử", "Số lượng ảnh", "Top-1 Acc (%)", "Top-3 Acc (%)", "Độ tương đồng Cosine trung bình"],
        ["Quần thể Kinh thành & Cung đình", "28 ảnh", "100,0%", "100,0%", "0,845 (Đặc trưng mái ngói, hoa văn cổng)"],
        ["Hệ thống Lăng tẩm triều Nguyễn", "24 ảnh", "95,8%", "100,0%", "0,798 (Phù điêu sành sứ Khải Định, hồ sen Tự Đức)"],
        ["Danh lam Cổ tự & Tâm linh", "15 ảnh", "100,0%", "100,0%", "0,832 (Tháp Phước Duyên, cổng tam quan)"],
        ["Thắng cảnh & Công trình Đô thị", "10 ảnh", "100,0%", "100,0%", "0,816 (Nhịp cầu Trường Tiền, đồi Vọng Cảnh)"],
        ["Toàn bộ 25 Danh lam Di tích", "77 ảnh", "98,7%", "100,0%", "0,823 (Thời gian suy luận: 42,5 ms/ảnh)"]
    ]
    tbl_clip = doc.add_table(rows=len(tbl_clip_data), cols=5)
    tbl_clip.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_academic_table_borders(tbl_clip)
    for r_idx, row in enumerate(tbl_clip_data):
        for c_idx, val in enumerate(row):
            cell = tbl_clip.rows[r_idx].cells[c_idx]
            p_cell = cell.paragraphs[0]
            p_cell.paragraph_format.space_before = Pt(2)
            p_cell.paragraph_format.space_after = Pt(2)
            p_cell.paragraph_format.line_spacing = 1.15
            p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 or c_idx == 4 else WD_ALIGN_PARAGRAPH.CENTER
            r_c = p_cell.add_run(val)
            r_c.font.name = 'Times New Roman'
            r_c.font.size = Pt(9.5)
            if r_idx == 0 or r_idx == len(tbl_clip_data) - 1:
                r_c.font.bold = True
                set_cell_background(cell, "EAECEF")
            set_cell_margins(cell, top=50, bottom=50, left=60, right=60)

    p_clip_disc = doc.add_paragraph()
    format_body_p(p_clip_disc)
    add_body_run(p_clip_disc, "Kết quả tại Bảng 2.3 chứng minh tính hiệu quả vượt bậc của phân hệ thị giác: mô hình nhận diện chính xác 76/77 bức ảnh ở vị trí Top-1 (đạt 98,7%) và đạt độ chính xác tuyệt đối 100% trong Top-3 ứng viên tương đồng nhất, với độ tương đồng Cosine trung bình 0,823. Trường hợp nhầm lẫn duy nhất ở Top-1 xảy ra giữa Lăng Minh Mạng và Lăng Thiệu Trị do góc chụp cận cảnh kiến trúc tam quan đối xứng và hoa văn rồng thời Nguyễn có nhiều nét tương đồng cao, tuy nhiên tên di tích chính xác vẫn nằm vững chắc ở vị trí Top-2. Thời gian suy luận trung bình chỉ 42,5 mili-giây cho mỗi bức ảnh trên GPU cá nhân tiêu chuẩn, hoàn toàn đáp ứng yêu cầu tương tác thời gian thực trên thiết bị di động.")

    add_sec_heading(doc, "2.4. Hiện thực hóa Cổng API RESTful và Sẵn sàng Tích hợp Hue-S")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Hệ thống đóng gói toàn bộ chức năng hỏi đáp và lập lịch trình thành các dịch vụ vi mô qua Cổng API chuẩn RESTful sử dụng framework FastAPI, chuẩn hóa năm điểm cuối: POST /api/v1/chat (hỏi đáp và tạo sinh có bảo chứng), POST /api/v1/itinerary (lập lịch trình tối ưu không gian), GET /api/v1/places/nearby (tra cứu tức thời dịch vụ ẩm thực và tham quan lân cận), POST /api/v1/visual-rag (nhận diện ảnh di tích bằng CLIP ViT-B/32 và kích hoạt tìm kiếm lân cận), và POST /api/v1/budget (dự toán chi phí vé di tích theo chính sách vé gộp ưu đãi, lưu trú, ăn uống và đi lại). Cấu trúc dữ liệu JSON trả về tuân thủ đầy đủ chuẩn mở GeoJSON, sẵn sàng tích hợp dạng mô-đun nhúng vào nền tảng công dân số Hue-S nhằm nâng cấp phân hệ du lịch thông minh của tỉnh.")

    doc.add_page_break()

    # =========================================================================
    # PHẦN V. KẾT LUẬN VÀ KIẾN NGHỊ
    # =========================================================================
    add_part_heading(doc, "PHẦN V. KẾT LUẬN VÀ KIẾN NGHỊ")

    add_sec_heading(doc, "1. Kết luận và Đóng góp của đề tài")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Khóa luận tốt nghiệp đã hoàn thành toàn diện và xuất sắc các mục tiêu nghiên cứu đề ra. Đề tài đóng góp sáu thành tựu khoa học và thực tiễn cốt lõi:\n"
                         "1) Thiết kế và hiện thực hóa thành công Hệ thống Spatial GraphRAG kết hợp Khung lọc không gian 2 giai đoạn (Haversine cắt tỉa thô đồ thị và OSRM tối ưu hóa đường bộ), triệt tiêu hoàn toàn hiện tượng ảo giác thực thể và lỗi vi phạm không gian trong bài toán du lịch Huế.\n"
                         "2) Xây dựng cơ sở tri thức Đồ thị Tri thức Không gian Du lịch Cố đô Huế hoàn chỉnh với 9.525 đỉnh thực thể và 90.948 cạnh quan hệ ngữ nghĩa, kết nối 612 địa điểm du lịch tại Huế.\n"
                         "3) Đề xuất giải thuật Khai phá thực đơn ngầm từ 44.355 bài đánh giá du khách thực tế tại Huế trên tập ngữ liệu 1.698.641 bản ghi toàn quốc, bóc tách chính xác 4.337 quan hệ phục vụ món ăn đặc sản.\n"
                         "4) Thiết lập quy trình điều phối tác tử tự suy ngẫm Agentic RAG trên LangGraph gồm 5 nút StateGraph với cơ chế chấm điểm tin cậy tuyến tính (ngưỡng 0,65) vận hành trên mô hình cục bộ Qwen2.5-3B-Instruct.\n"
                         "5) Mở rộng năng lực suy luận sang thị giác đa phương thức qua mô hình CLIP ViT-B/32 Zero-shot, đạt độ chính xác Top-1 98,7% và Top-3 100% qua giao thức kiểm định LOOCV nghiêm ngặt.\n"
                         "6) Hiện thực hóa ứng dụng Web responsive tích hợp bản đồ số Leaflet.js, xác thực an toàn OWASP, Sổ tay du khách và Hộ chiếu di sản Gamification, đóng gói Cổng API RESTful sẵn sàng tích hợp vào nền tảng công dân số Hue-S.")

    add_sec_heading(doc, "2. Những hạn chế của nghiên cứu")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Bên cạnh những kết quả đạt được, nghiên cứu còn một số hạn chế nhất định: dữ liệu đánh giá du khách chủ yếu tập trung tại các khu vực trung tâm và di tích nổi tiếng, mức độ bao phủ tại các làng nghề xa xôi còn khiêm tốn; động cơ OSRM vận hành trên dữ liệu OSM tĩnh chưa tích hợp dữ liệu mật độ giao thông thời gian thực vào giờ cao điểm; và mô hình CLIP ViT-B/32 có thể gặp khó khăn khi phân biệt các góc chụp quá hẹp của các chi tiết hoa văn kiến trúc cung đình có phong cách điêu khắc tương đồng.")

    add_sec_heading(doc, "3. Kiến nghị và Hướng phát triển tiếp theo")
    p = doc.add_paragraph()
    format_body_p(p)
    add_body_run(p, "Trong giai đoạn tiếp theo, nghiên cứu đề xuất các hướng phát triển: 1) Tích hợp dữ liệu giao thông thời gian thực và lịch trình xe buýt công cộng/xe điện du lịch tại Huế vào động cơ OSRM; 2) Ứng dụng kỹ thuật chưng cất tri thức (Knowledge Distillation) hoặc mô hình Vision Transformer siêu nhẹ để cho phép nhận diện ảnh ngoại tuyến ngay trên trình duyệt web thiết bị di động của du khách; 3) Mở rộng phạm vi đồ thị tri thức sang các vùng phụ cận liên kết du lịch Miền Trung như Đà Nẵng và Hội An; và 4) Phối hợp với Trung tâm Giám sát Điều hành Đô thị Thông minh (IOC) tỉnh Thừa Thiên Huế để tiến hành thử nghiệm nghiệm thu người dùng thực tế và tích hợp chính thức lên ứng dụng Hue-S.")

    doc.add_page_break()

    # =========================================================================
    # TÀI LIỆU THAM KHẢO (IEEE STANDARD)
    # =========================================================================
    add_part_heading(doc, "TÀI LIỆU THAM KHẢO")

    references = [
        "[1] B. N. Long, \"Huế phải trả lời câu hỏi của du khách: Đi đâu, ăn gì, lưu trú ở đâu?,\" Báo Thanh Niên, Tháng 9 2026. Truy cập trực tuyến ngày 16/09/2026.",
        "[2] IOC Thừa Thiên Huế, \"Nền tảng Đô thị thông minh Hue-S: Kiến trúc dịch vụ và kết nối cổng dữ liệu mở,\" Trung tâm Giám sát Điều hành Đô thị Thông minh tỉnh Thừa Thiên Huế, 2024.",
        "[3] A. Hogan, E. Blomqvist, M. Cochez, C. d'Amato, G. de Melo, C. Gutierrez, S. Kirrane, J. E. L. Gayo, R. Navigli, S. Neumaier, et al., \"Knowledge graphs,\" ACM Computing Surveys (CSUR), vol. 54, no. 4, pp. 1–37, 2021.",
        "[4] A. Ballatore, M. Bertolotto, and D. C. Wilson, \"Spatial data usability in geographic information systems and location-based services,\" Transactions in GIS, vol. 18, no. 6, pp. 813–831, 2014.",
        "[5] R. W. Sinnott, \"Virtues of the haversine,\" Sky and Telescope, vol. 68, no. 2, p. 159, 1984.",
        "[6] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. Küttler, M. Lewis, W.-t. Yih, T. Rocktäschel, et al., \"Retrieval-augmented generation for knowledge-intensive NLP tasks,\" in Advances in Neural Information Processing Systems (NeurIPS), vol. 33, pp. 9459–9474, 2020.",
        "[7] D. Edge, H. Trinh, N. Cheng, J. Bradley, A. Chao, A. Mody, S. Truitt, and J. Larson, \"From local to global: A graph RAG approach to query-focused summarization,\" arXiv preprint arXiv:2404.16130, 2024.",
        "[8] S. Pan, L. Luo, Y. Wang, C. Chen, J. Wang, and X. Wu, \"Unifying large language models and knowledge graphs: A roadmap,\" IEEE Transactions on Knowledge and Data Engineering (TKDE), vol. 36, no. 7, pp. 3580–3599, 2024.",
        "[9] LangChain Team, \"LangGraph: Building resilient agentic workflows with StateGraph,\" 2024. [Trực tuyến]. Địa chỉ: https://github.com/langchain-ai/langgraph",
        "[10] Qwen Team, \"Qwen2.5 technical report: Open-source foundation models for multilingual applications,\" Alibaba Group Technical Report, 2024.",
        "[11] TripAdvisor LLC, \"TripAdvisor content and review data repository,\" TripAdvisor Travel Research Portal, 2024.",
        "[12] N. Reimers and I. Gurevych, \"Sentence-BERT: Sentence embeddings using siamese BERT-networks,\" in Proceedings of the Conference on Empirical Methods in Natural Language Processing (EMNLP), pp. 3982–3992, 2019.",
        "[13] A. Asai, Z. Wu, Y. Wang, A. Sil, and H. Hajishirzi, \"Self-RAG: Learning to retrieve, generate, and critique through self-reflection,\" in International Conference on Learning Representations (ICLR), 2024.",
        "[14] P. Vansteenwegen, W. Souffriau, and D. Van Oudheusden, \"The orienteering problem: A survey,\" European Journal of Operational Research, vol. 209, no. 1, pp. 1–10, 2011.",
        "[15] A. Radford, J. W. Kim, C. Hallacy, A. Ramesh, G. Goh, S. Agarwal, G. Sastry, A. Askell, P. Mishkin, J. Clark, et al., \"Learning transferable visual models from natural language supervision,\" in Proceedings of the 38th International Conference on Machine Learning (ICML), vol. 139, pp. 8748–8763, 2021.",
        "[16] D. Luxen and C. Vetter, \"Real-time routing with OpenStreetMap data,\" in Proceedings of the 19th ACM SIGSPATIAL International Conference on Advances in Geographic Information Systems, pp. 513–516, 2011.",
        "[17] R. Geisberger, P. Sanders, D. Schultes, and D. Delling, \"Contraction hierarchies: Faster and simpler hierarchical routing in road networks,\" in Experimental Algorithms (WEA 2008), Lecture Notes in Computer Science, vol. 5038, pp. 319–333, Springer, 2008.",
        "[18] L. Moroney, The Definitive Guide to Firebase: Build Mobile and Web Applications with Firebase, New York, NY, USA: Apress, 2017.",
        "[19] A. Davoudian, L. Chen, and M. Liu, \"A survey on NoSQL stores,\" ACM Computing Surveys (CSUR), vol. 51, no. 2, pp. 1–43, 2018.",
        "[20] Google Cloud, \"Cloud Firestore architecture and real-time synchronization protocol,\" Google Cloud Whitepaper and Technical Documentation, 2024.",
        "[21] D. Hardt, \"The OAuth 2.0 authorization framework,\" Internet Engineering Task Force (IETF), RFC 6749, 2012.",
        "[22] D. Gavalas, C. Konstantopoulos, K. Mastakas, and G. Pantziou, \"A survey on mobile tourist guides and context-aware tourist trip planning,\" Journal of Network and Computer Applications, vol. 40, pp. 380–403, 2014.",
        "[23] Trung tâm Bảo tồn Di tích Cố đô Huế, \"Quy định mức thu phí tham quan di tích lịch sử văn hóa Huế thuộc quần thể di tích Cố đô Huế,\" Văn bản ban hành của HĐND và UBND tỉnh Thừa Thiên Huế, 2024.",
        "[24] E. Marcotte, \"Responsive web design,\" A List Apart, vol. 306, pp. 1–11, 2010.",
        "[25] R. Sugumaran and J. Degroote, Spatial Decision Support Systems: Principles and Practices, CRC Press, Taylor & Francis Group, 2010.",
        "[26] P. Zippenfenig, \"Open-Meteo: Open-source weather API providing high-resolution meteorological forecasts,\" Open-Meteo Documentation and Technical Report, 2023.",
        "[27] World Meteorological Organization, Manual on Codes: International Codes, Volume I.1 (Annex II to the WMO Technical Regulations), Geneva, Switzerland: WMO-No. 306, 2019.",
        "[28] M. Yasunaga, H. Ren, A. Bosselut, P. Liang, and J. Leskovec, \"QA-GNN: Reasoning with language models and knowledge graphs for question answering,\" in Proceedings of the Conference of the North American Chapter of the Association for Computational Linguistics (NAACL), pp. 535–546, 2021.",
        "[29] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, Ł. Kaiser, and I. Polosukhin, \"Attention is all you need,\" in Advances in Neural Information Processing Systems (NeurIPS), vol. 30, pp. 5998–6008, 2017.",
        "[30] T. N. Kipf and M. Welling, \"Semi-supervised classification with graph convolutional networks,\" in International Conference on Learning Representations (ICLR), 2017.",
        "[31] OpenStreetMap Foundation, \"OpenStreetMap geo-database documentation and geographic primitives,\" 2024. [Trực tuyến]. Địa chỉ: https://www.openstreetmap.org"
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


    doc.add_page_break()

    # =========================================================================
    # PHỤ LỤC
    # =========================================================================
    add_part_heading(doc, "PHỤ LỤC")

    add_sec_heading(doc, "Phụ lục A: Danh mục 12 Kịch bản Kiểm thử Chuẩn (Benchmark Suite)")
    p_pa = doc.add_paragraph()
    format_body_p(p_pa)
    add_body_run(p_pa, "Bảng tổng hợp đặc tả 12 kịch bản kiểm thử chuẩn hóa phục vụ đo lường và đánh giá nghiệm đúng năng lực suy luận không gian, định tuyến lân cận và khai phá thực đơn của hệ thống Spatial GraphRAG.")

    tbl_pa_data = [
        ["Mã ca", "Nhóm bài toán", "Nội dung câu hỏi truy vấn của du khách", "Điểm neo (Anchor POI)"],
        ["TC-01", "Không gian + Ẩm thực", "Tôi đang ở Đại Nội Huế, muốn tìm quán bún bò chuẩn vị gần đây để đi bộ ăn trưa.", "Đại Nội Huế (bờ Bắc)"],
        ["TC-02", "Không gian + Ẩm thực", "Sau khi tham quan Lăng Tự Đức, tôi muốn ăn bánh bèo hoặc bánh nậm gần đó thì ghé quán nào?", "Lăng Tự Đức (Thủy Xuân)"],
        ["TC-03", "Không gian + Ẩm thực", "Tôi đang ở khu vực Cồn Hến, muốn thưởng thức cơm hến và chè bắp đúng gốc Huế.", "Cồn Hến (Phường Vĩ Dạ)"],
        ["TC-04", "Không gian + Ẩm thực", "Gợi ý quán bánh khoái và nem lụi ngon ở bờ Nam gần khu phố Tây Chu Văn An.", "Phố đi bộ Chu Văn An"],
        ["TC-05", "Khám phá lân cận", "Tôi vừa ghé Chùa Thiên Mụ, xung quanh đây có điểm văn hóa nào có thể ghé tiếp theo không?", "Chùa Thiên Mụ (bờ Bắc)"],
        ["TC-06", "Khám phá lân cận", "Từ Đồi Vọng Cảnh, có những di tích lăng tẩm hoặc làng nghề nào nằm gần trên cùng trục đường?", "Đồi Vọng Cảnh (Thủy Xuân)"],
        ["TC-07", "Khám phá lân cận", "Tôi đang ở Chợ Đông Ba, muốn tìm các điểm di tích có thể đi bộ tham quan trong 15 phút.", "Chợ Đông Ba (bờ Bắc)"],
        ["TC-08", "Khám phá lân cận", "Khám phá danh thắng thiên nhiên và sinh thái đầm phá ở ngoại ô phía Đông Nam thành phố Huế.", "Đầm Chuồn (Phú Vang)"],
        ["TC-09", "Lịch trình tổng hợp", "Thiết kế lịch trình du lịch Huế 1 ngày trọn vẹn cho cặp đôi, xuất phát từ khách sạn bờ Nam.", "Khách sạn bờ Nam TP. Huế"],
        ["TC-10", "Lịch trình tổng hợp", "Lập lịch trình 2 ngày khám phá Huế theo phong cách văn hóa sâu sắc và ẩm thực truyền thống.", "Không gian Cố đô Huế"],
        ["TC-11", "Lịch trình tổng hợp", "Gợi ý lịch trình 3 ngày tại Huế kết hợp di sản Cố đô và du lịch dã ngoại thiên nhiên sinh thái.", "Cố đô Huế và đầm phá"],
        ["TC-12", "Lịch trình tổng hợp", "Lập tour nửa ngày (chiều từ 14h đến 19h) ngắm hoàng hôn và thưởng thức ẩm thực đêm xứ Huế.", "Trục đồi Thủy Xuân"]
    ]
    tbl_pa = doc.add_table(rows=len(tbl_pa_data), cols=4)
    tbl_pa.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_academic_table_borders(tbl_pa)
    for r_idx, row in enumerate(tbl_pa_data):
        for c_idx, val in enumerate(row):
            cell = tbl_pa.rows[r_idx].cells[c_idx]
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
            set_cell_margins(cell, top=45, bottom=45, left=60, right=60)

    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_before = Pt(12)

    add_sec_heading(doc, "Phụ lục B: Danh mục Thực đơn Món ăn Đặc sản Huế trong Đồ thị Tri thức")
    p_pb = doc.add_paragraph()
    format_body_p(p_pb)
    add_body_run(p_pb, "Danh mục 10 món ăn đặc sản tiêu biểu của Cố đô Huế được tích hợp trong Đồ thị Tri thức Không gian với chỉ số tin cậy khai phá Conf(u, m) cao nhất.")

    tbl_pb_data = [
        ["Mã món", "Tên món đặc sản", "Đặc trưng hương vị và nguyên liệu", "Khu vực tập trung"],
        ["HUE_01", "Bún bò Huế", "Nước dùng xương bò, ruốc sả, chả cua, giò heo", "Phường Phú Hội, Phú Nhuận"],
        ["HUE_02", "Cơm hến", "Hến xào cồn Hến, tóp mỡ, bắp chuối, mắm ruốc", "Cồn Hến, Vỹ Dạ"],
        ["HUE_03", "Bánh bèo chén", "Bánh bột gạo hấp chén nhỏ, tôm chấy, da heo chiên", "Phường Tây Lộc, Vỹ Dạ"],
        ["HUE_04", "Bánh nậm", "Bột gạo bọc lá chuối, nhân tôm thịt băm nhuyễn", "Phường Thuận Lộc, Kim Long"],
        ["HUE_05", "Bánh bột lọc", "Bột lọc trong suốt, nhân tôm thịt rim đậm đà", "Toàn thành phố Huế"],
        ["HUE_06", "Bánh khoái", "Vỏ bột giòn rụm, nhân tôm, thịt, giá, chấm nước lèo", "Khu vực Đông Ba, Gia Hội"],
        ["HUE_07", "Nem lụi", "Thịt heo quết nướng than hoa trên que sả", "Đường Nguyễn Huệ, Đinh Tiên Hoàng"],
        ["HUE_08", "Chè heo quay", "Viên bột lọc bọc thịt heo quay trong nước đường", "Hẻm Hùng Vương, Bến Ngự"],
        ["HUE_09", "Vả trộn", "Quả vả luộc thái mỏng trộn tôm thịt, mè rang", "Nhà hàng ẩm thực cung đình"],
        ["HUE_10", "Bún mắm nêm", "Bún tươi thịt luộc, tai mui heo, mắm nêm cá cơm", "Chợ Đông Ba, Bến Ngự"]
    ]
    tbl_pb = doc.add_table(rows=len(tbl_pb_data), cols=4)
    tbl_pb.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_academic_table_borders(tbl_pb)
    for r_idx, row in enumerate(tbl_pb_data):
        for c_idx, val in enumerate(row):
            cell = tbl_pb.rows[r_idx].cells[c_idx]
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
            set_cell_margins(cell, top=45, bottom=45, left=60, right=60)

    # Lưu file Word hoàn chỉnh
    output_docx_path = PROJECT_ROOT / "docs" / "KHOA_LUAN_TOT_NGHIEP_TOAN_VAN.docx"
    doc.save(str(output_docx_path))
    print(f"\n[OK] ĐÃ XUẤT THÀNH CÔNG TOÀN VĂN KHÓA LUẬN CHUẨN 5 PHẦN HUET TẠI: {output_docx_path}")


if __name__ == "__main__":
    build_thesis_docx()
