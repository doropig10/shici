import json
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

rows = json.load(open(r"E:\单词\_pdftools\entries_clean.json", encoding="utf-8"))
assert len(rows) == 3267

ORANGE = "E8622C"
LIGHT = "FFF6F1"
HEADBG = "FCE4D8"

doc = Document()

# page setup
sec = doc.sections[0]
sec.page_width = Cm(21.0)
sec.page_height = Cm(29.7)
sec.top_margin = Cm(1.5)
sec.bottom_margin = Cm(1.4)
sec.left_margin = Cm(1.5)
sec.right_margin = Cm(1.5)
sec.header_distance = Cm(0.8)
sec.footer_distance = Cm(0.7)

# default font
style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(8.5)
style.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
style.paragraph_format.space_before = Pt(0)
style.paragraph_format.space_after = Pt(0)
style.paragraph_format.line_spacing = 1.0


def set_run_font(run, size=8.5, bold=False, color=None, ascii_font="Calibri", ea_font="宋体"):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = ascii_font
    run._element.rPr.rFonts.set(qn("w:eastAsia"), ea_font)
    if color:
        run.font.color.rgb = RGBColor.from_string(color)


# title
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(2)
r = p.add_run("六级词汇 1–3267")
set_run_font(r, 20, True, "222222")

p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(6)
r = p.add_run("共 3267 词 · 按原书词条编号 #1 aggressive — #3267 metaphorical · 取自《英语六级 你还在背单词吗（新版）》第 1–164 页")
set_run_font(r, 8, False, "777777")

table = doc.add_table(rows=1, cols=3)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
table.autofit = False
tbl = table._tbl
tblPr = tbl.tblPr

# borders
borders = OxmlElement("w:tblBorders")
for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
    el = OxmlElement(f"w:{edge}")
    el.set(qn("w:val"), "single")
    el.set(qn("w:sz"), "4")
    el.set(qn("w:space"), "0")
    el.set(qn("w:color"), "E8C4B0")
    borders.append(el)
tblPr.append(borders)

# cell margins
mar = OxmlElement("w:tblCellMar")
for side, w in (("top", "14"), ("left", "80"), ("bottom", "14"), ("right", "80")):
    el = OxmlElement(f"w:{side}")
    el.set(qn("w:w"), w)
    el.set(qn("w:type"), "dxa")
    mar.append(el)
tblPr.append(mar)

# fixed layout
layout = OxmlElement("w:tblLayout")
layout.set(qn("w:type"), "fixed")
tblPr.append(layout)

WIDTHS = [Cm(1.4), Cm(4.7), Cm(11.9)]


def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def cant_split(row):
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:cantSplit")
    trPr.append(el)


def set_widths(row):
    for i, cell in enumerate(row.cells):
        cell.width = WIDTHS[i]


# header row
hdr = table.rows[0]
cant_split(hdr)
set_widths(hdr)
for i, text in enumerate(("序号", "单词", "释义")):
    cell = hdr.cells[i]
    shade(cell, HEADBG)
    cp = cell.paragraphs[0]
    cp.paragraph_format.space_before = Pt(3)
    cp.paragraph_format.space_after = Pt(3)
    run = cp.add_run(text)
    set_run_font(run, 9, True, "8A3B16")
trPr = hdr._tr.get_or_add_trPr()
th = OxmlElement("w:tblHeader")
trPr.append(th)

for idx, item in enumerate(rows, start=1):
    row = table.add_row()
    cant_split(row)
    set_widths(row)
    if idx % 2 == 0:
        for c in row.cells:
            shade(c, LIGHT)

    c0, c1, c2 = row.cells
    p0 = c0.paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r0 = p0.add_run(str(item["n"]))
    set_run_font(r0, 8, False, "A06A50")

    p1 = c1.paragraphs[0]
    r1 = p1.add_run(item["w"])
    set_run_font(r1, 8.5, True, "1A1A1A")

    p2 = c2.paragraphs[0]
    for j, ln in enumerate(item["m"]):
        if j:
            p2.add_run().add_break()
        r2 = p2.add_run(ln)
        set_run_font(r2, 8.5, False, "333333")

# footer with page numbers
footer = sec.footer
fp = footer.paragraphs[0]
fp.paragraph_format.tab_stops.add_tab_stop(Cm(18.0), WD_TAB_ALIGNMENT.RIGHT)
r = fp.add_run("六级词汇 1–3267")
set_run_font(r, 8, False, "999999")
fp.add_run("\t")
r = fp.add_run("第 ")
set_run_font(r, 8, False, "999999")
for instr in ("PAGE", None, "NUMPAGES"):
    if instr is None:
        r = fp.add_run(" 页 / 共 ")
        set_run_font(r, 8, False, "999999")
        continue
    run = fp.add_run()
    set_run_font(run, 8, False, "999999")
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr_el = OxmlElement("w:instrText")
    instr_el.set(qn("xml:space"), "preserve")
    instr_el.text = f" {instr} "
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    txt = OxmlElement("w:t")
    txt.text = "1"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr_el)
    run._r.append(fld_sep)
    run._r.append(txt)
    run._r.append(fld_end)
r = fp.add_run(" 页")
set_run_font(r, 8, False, "999999")

out = r"E:\单词\_pdftools\六级词汇_1-3267.docx"
doc.save(out)
print("docx saved", out)

