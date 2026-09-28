import docx
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

doc = docx.Document()

# Set A4 Page Size & Margins (1 page fit)
section = doc.sections[0]
section.page_width = Cm(21.0)
section.page_height = Cm(29.7)
section.top_margin = Cm(1.5)
section.bottom_margin = Cm(1.5)
section.left_margin = Cm(1.8)
section.right_margin = Cm(1.8)

# Set Normal Style
style = doc.styles['Normal']
style.font.name = 'Times New Roman'
style.font.size = Pt(10)
style.font.color.rgb = RGBColor(0, 0, 0)
style.paragraph_format.line_spacing = 1.15
style.paragraph_format.space_after = Pt(2)
style.paragraph_format.space_before = Pt(0)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_table_margins(table, top=60, bottom=60, left=100, right=100):
    tblPr = table._tbl.tblPr
    tblCellMar = parse_xml(
        f'<w:tblCellMar {nsdecls("w")}>'
        f'  <w:top w:w="{top}" w:type="dxa"/>'
        f'  <w:left w:w="{left}" w:type="dxa"/>'
        f'  <w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'  <w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tblCellMar>'
    )
    tblPr.append(tblCellMar)

# TITLE
p_title = doc.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run_title = p_title.add_run("TÓM TẮT HƯỚNG NGHIÊN CỨU KHÓA LUẬN TỐT NGHIỆP")
run_title.bold = True
run_title.font.size = Pt(13)
p_title.paragraph_format.space_after = Pt(2)

# SUBTITLE / METADATA
p_sub = doc.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_sub = p_sub.add_run("Đề tài: Xây dựng hệ thống hỏi đáp và gợi ý du lịch thông minh ứng dụng đồ thị tri thức\nvà mô hình ngôn ngữ lớn trên dữ liệu đánh giá du lịch Việt Nam")
r_sub.italic = True
r_sub.font.size = Pt(9.5)
r_sub.font.color.rgb = RGBColor(60, 60, 60)
p_sub.paragraph_format.space_after = Pt(6)

# SECTION 1
p_h1 = doc.add_paragraph()
r_h1 = p_h1.add_run("1. BÀI TOÁN NGHIÊN CỨU")
r_h1.bold = True
r_h1.font.size = Pt(10.5)
r_h1.font.color.rgb = RGBColor(0, 51, 102)
p_h1.paragraph_format.space_before = Pt(3)
p_h1.paragraph_format.space_after = Pt(2)

p_body1 = doc.add_paragraph(
    "Du khách khi lên kế hoạch du lịch tại Việt Nam phải đối mặt với lượng thông tin khổng lồ và rời rạc trên các nền tảng trực tuyến như TripAdvisor, gây tốn thời gian và dễ bỏ sót tri thức thực tế. Các mô hình ngôn ngữ lớn (LLM) hiện nay tuy có khả năng trả lời tự nhiên nhưng thiếu dữ liệu cục bộ chuyên sâu và thường gặp hiện tượng sinh thông tin sai lệch (hallucination)."
)
p_body1.paragraph_format.space_after = Pt(2)

p_body2 = doc.add_paragraph(
    "Khóa luận tập trung giải quyết bài toán trên thông qua hai mục tiêu chính: (1) Khai phá tri thức du lịch có cấu trúc từ bộ dữ liệu hơn 313.000 bài đánh giá thực tế bao phủ đầy đủ 3 trụ cột (Khách sạn – Nhà hàng – Điểm tham quan), xây dựng Đồ thị Tri thức (Knowledge Graph) biểu diễn mối quan hệ đa chiều giữa địa điểm và trải nghiệm du khách; (2) Thiết kế pipeline RAG (Retrieval-Augmented Generation) kết hợp Đồ thị Tri thức với LLM nhằm tạo Trợ lý du lịch thông minh — đảm bảo mọi gợi ý và câu trả lời đều có trích dẫn nguồn thực tế."
)
p_body2.paragraph_format.space_after = Pt(5)

# SECTION 2
p_h2 = doc.add_paragraph()
r_h2 = p_h2.add_run("2. DỮ LIỆU NGHIÊN CỨU")
r_h2.bold = True
r_h2.font.size = Pt(10.5)
r_h2.font.color.rgb = RGBColor(0, 51, 102)
p_h2.paragraph_format.space_before = Pt(3)
p_h2.paragraph_format.space_after = Pt(2)

p_d1 = doc.add_paragraph(
    "Dữ liệu được thu thập tự động từ TripAdvisor bằng hệ thống crawler phân tán (Selenium + BeautifulSoup), chống phát hiện bot và hỗ trợ checkpoint an toàn. Thống kê bộ dữ liệu hiện có:"
)
p_d1.paragraph_format.space_after = Pt(3)

# Table for Dataset
table_data = doc.add_table(rows=5, cols=4)
table_data.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_margins(table_data, top=60, bottom=60, left=100, right=100)

headers = ["Loại dữ liệu", "Số lượng địa điểm", "Số đánh giá thu thập", "Phạm vi địa lý"]
widths = [Cm(3.5), Cm(3.2), Cm(3.8), Cm(6.9)]
data_rows = [
    ["Khách sạn (Hotels)", "2.426 địa điểm", "~125.000 reviews (EN + VI)", "Hơn 20 tỉnh thành toàn quốc"],
    ["Nhà hàng (Restaurants)", "3.308 địa điểm", "~101.000 reviews", "HCM, Hà Nội, Đà Nẵng, Hội An, Huế..."],
    ["Điểm tham quan (Attractions)", "3.338 địa điểm", "~102.000 reviews", "Tất cả điểm tham quan chính tại Việt Nam"],
    ["TỔNG CỘNG HỆ THỐNG", "9.072 địa điểm", "~313.000 reviews", "Toàn bộ hệ sinh thái du lịch Việt Nam"]
]

hdr_cells = table_data.rows[0].cells
for i, head in enumerate(headers):
    hdr_cells[i].text = head
    set_cell_background(hdr_cells[i], "003366")
    p = hdr_cells[i].paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in p.runs:
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.size = Pt(9.0)

for r_idx, row_data in enumerate(data_rows):
    row_cells = table_data.rows[r_idx + 1].cells
    is_total = (r_idx == len(data_rows) - 1)
    bg_color = "E6EEF4" if is_total else ("F2F5F8" if r_idx % 2 == 1 else "FFFFFF")
    for c_idx, val in enumerate(row_data):
        row_cells[c_idx].text = val
        set_cell_background(row_cells[c_idx], bg_color)
        p = row_cells[c_idx].paragraphs[0]
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.space_before = Pt(1)
        p.style.font.size = Pt(9.0)
        if is_total:
            p.runs[0].font.bold = True
        if c_idx in [1, 2]:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER

for row in table_data.rows:
    for i, w in enumerate(widths):
        row.cells[i].width = w

doc.add_paragraph().paragraph_format.space_after = Pt(3)

# SECTION 3
p_h3 = doc.add_paragraph()
r_h3 = p_h3.add_run("3. CÁC BƯỚC THÍ NGHIỆM VÀ KỸ THUẬT DỰ ĐỊNH")
r_h3.bold = True
r_h3.font.size = Pt(10.5)
r_h3.font.color.rgb = RGBColor(0, 51, 102)
p_h3.paragraph_format.space_before = Pt(3)
p_h3.paragraph_format.space_after = Pt(2)

table_exp = doc.add_table(rows=6, cols=3)
table_exp.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_margins(table_exp, top=55, bottom=55, left=90, right=90)

exp_headers = ["Bước thí nghiệm", "Nội dung thực hiện", "Mô hình & Kỹ thuật dự định"]
exp_widths = [Cm(3.5), Cm(7.7), Cm(6.2)]

exp_rows = [
    [
        "Bước 1: Tiền xử lý & EDA",
        "Gộp dữ liệu từ các worker, khử trùng lặp, xử lý lỗi dính chữ (trip_type), chuẩn hóa văn bản. Thống kê phân bố 3 loại địa điểm theo thành phố, rating, thời gian.",
        "Pandas, Matplotlib, Seaborn, NLTK/spaCy text cleaning"
    ],
    [
        "Bước 2: Trích xuất thực thể (NER)",
        "Trích xuất 4 nhóm thực thể: Địa điểm, Nhà hàng, Hoạt động, Món ăn từ review text. Chuẩn hóa tên thực thể trùng lặp (Entity Resolution).",
        "LLM Structured Extraction (GPT-4o/Gemini), spaCy NER, FuzzyWuzzy matching"
    ],
    [
        "Bước 3: Xây dựng Knowledge Graph",
        "Xây dựng đồ thị kết nối 9.072 Nút (Hotel, Restaurant, Attraction, Activity) và Cạnh (đồng xuất hiện). Trích xuất mẫu hành vi du khách (Ở đâu -> Đi đâu -> Ăn gì).",
        "NetworkX / Neo4j, Thuật toán Apriori (Association Rules)"
    ],
    [
        "Bước 4: Pipeline RAG & Retrieval",
        "Chunking văn bản, tạo Embeddings lưu Vector DB. Thiết kế tìm kiếm lai (Hybrid: Vector + BM25) kết hợp truy vấn đồ thị (Graph Query). Gọi LLM sinh câu trả lời.",
        "Sentence-BERT (all-MiniLM-L6-v2), ChromaDB, Ollama (Qwen2.5) / GPT-4o API"
    ],
    [
        "Bước 5: Web App & Evaluation",
        "Xây dựng Web App tương tác (Chatbot Q&A, gợi ý trải nghiệm 3 trong 1, sơ đồ đồ thị). Đánh giá chất lượng bằng bộ chỉ tiêu chuẩn và khảo sát.",
        "Streamlit, Pyvis / D3.js, RAGAS Framework (Faithfulness, Relevancy)"
    ]
]

hdr_cells_e = table_exp.rows[0].cells
for i, head in enumerate(exp_headers):
    hdr_cells_e[i].text = head
    set_cell_background(hdr_cells_e[i], "003366")
    p = hdr_cells_e[i].paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in p.runs:
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.size = Pt(9.0)

for r_idx, row_data in enumerate(exp_rows):
    row_cells = table_exp.rows[r_idx + 1].cells
    bg_color = "F2F5F8" if r_idx % 2 == 1 else "FFFFFF"
    for c_idx, val in enumerate(row_data):
        row_cells[c_idx].text = val
        set_cell_background(row_cells[c_idx], bg_color)
        p = row_cells[c_idx].paragraphs[0]
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.space_before = Pt(1)
        p.style.font.size = Pt(8.5)
        if c_idx == 0:
            p.runs[0].font.bold = True

for row in table_exp.rows:
    for i, w in enumerate(exp_widths):
        row.cells[i].width = w

doc.add_paragraph().paragraph_format.space_after = Pt(3)

# SECTION 4
p_h4 = doc.add_paragraph()
r_h4 = p_h4.add_run("4. KẾT QUẢ VÀ ĐẦU RA MONG ĐỜI")
r_h4.bold = True
r_h4.font.size = Pt(10.5)
r_h4.font.color.rgb = RGBColor(0, 51, 102)
p_h4.paragraph_format.space_before = Pt(3)
p_h4.paragraph_format.space_after = Pt(2)

outcomes = [
    "(1) Bộ Đồ thị Tri thức du lịch Việt Nam kết nối toàn diện hơn 9.000 địa điểm (Khách sạn, Nhà hàng, Điểm tham quan) và hàng chục nghìn thực thể trải nghiệm.",
    "(2) Ứng dụng Web Trợ lý du lịch thông minh tích hợp 3 tính năng: Hỏi đáp RAG có trích dẫn nguồn, Gợi ý trải nghiệm hoàn chỉnh (Ở đâu - Ăn gì - Đi đâu), và Khám phá đồ thị tương tác.",
    "(3) Báo cáo đánh giá thực nghiệm định lượng (F1-score cho NER, RAGAS score cho RAG) và định tính (khảo sát người dùng)."
]

for out_text in outcomes:
    p = doc.add_paragraph(out_text)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.space_before = Pt(0)
    p.style.font.size = Pt(9.5)

out_file = r"d:\Khóa luận\vietnam-hotel-crawler\Tom_Tat_Huong_Nghien_Cuu_Khoa_Luan_Full.docx"
doc.save(out_file)
print(f"Successfully generated updated docx at: {out_file}")
