import json
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

rows = json.load(open(r"E:\单词\_pdftools\entries_clean.json", encoding="utf-8"))
units = json.load(open(r"E:\单词\_pdftools\units.json", encoding="utf-8"))
by_num = {r["n"]: r for r in rows}

# 词库 xlsx 里有、但 PDF 前 3267 条里没有的 Unit 1 开头两个词
PRE = [
    {"tag": "补1", "w": "ambition", "m": ["n. 雄心，抱负；野心"]},
    {"tag": "补2", "w": "ambitious", "m": ["adj. 有雄心的，有抱负的"]},
]

# ---------------- markdown ----------------
def md_meaning(item):
    return "；".join(x.strip() for x in item["m"] if x.strip())

lines = [
    "# 六级词汇 1–3267 · 按单元",
    "",
    "> 数据源：D:\\BaiduNetdiskDownload\\六级词汇.pdf 前 3267 条（#1 aggressive — #3267 metaphorical），"
    "单元结构取自原词库 `词库-Unit1-10.xlsx`（原文件已删除）。",
    "> xlsx 只收了原书部分词（有缺页），所以用**每个单元第一个词 / 该单元词群起始词**在 3267 条里的位置切分。",
    "> 另补 **2 条**（ambition、ambitious）：书里 Unit 1 从这两个词起头，但 PDF 词表直接从 aggressive 开始，标〔补〕。",
    "",
    "| 单元 | 编号范围 | 词数 |",
    "|---|---|---|",
]
for i, u in enumerate(units):
    n = u["end"] - u["start"] + 1 + (len(PRE) if i == 0 else 0)
    rng = f"#{u['start']}–#{u['end']}" + ("（+补 2）" if i == 0 else "")
    lines.append(f"| {u['name']} | {rng} | {n} |")

for i, u in enumerate(units):
    n = u["end"] - u["start"] + 1
    extra = f" + 补 {len(PRE)}" if i == 0 else ""
    lines += ["", f"## {u['name']} · #{u['start']}–#{u['end']}{extra} · {n + (len(PRE) if i == 0 else 0)} 词", ""]
    if i == 0:
        for p in PRE:
            lines.append(f"{p['tag']}. **{p['w']}** — {'；'.join(p['m'])}　〔词库补入〕")
    for num in range(u["start"], u["end"] + 1):
        it = by_num[num]
        lines.append(f"{it['n']}. **{it['w']}** — {md_meaning(it)}")

lines += [
    "",
    "---",
    "",
    "备注：",
    "",
    "- **补 2 条**：ambition、ambitious 来自词库 xlsx 的 Unit 1 第 1–2 行，PDF 词表里没有这两条，编号用「补1/补2」，不影响原有 #1–#3267 的编号。",
    "- Unit 9 末尾 #2848–#2872（25 条，从 condensation、capital、capacity 到 crumble）在 xlsx 中因缺页没有收录，"
    "按位置归入 Unit 9；如果原书里这段属于 Unit 10，把这一段的 25 行整体上移即可。",
    "- 词库 xlsx 的 Unit 1 还提到 relationship（#157 行，re/er 词群），PDF 词表同样没有，但它不在单元开头，未补。",
]

with open(r"E:\单词\六级词汇_1-3267_按单元.md", "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines) + "\n")
print("md ok")

# ---------------- docx ----------------
HEADBG = "FCE4D8"
DIVBG = "F7DFD1"
LIGHT = "FFF6F1"
SUPBG = "FFF3E8"


def set_run(run, size=8.5, bold=False, color="333333", ascii_font="Calibri", ea_font="宋体"):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = ascii_font
    run._element.rPr.rFonts.set(qn("w:eastAsia"), ea_font)
    run.font.color.rgb = RGBColor.from_string(color)


def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def cant_split(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(OxmlElement("w:cantSplit"))


def table_borders(tbl):
    tblPr = tbl._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), "E8C4B0")
        borders.append(el)
    tblPr.append(borders)
    lay = OxmlElement("w:tblLayout")
    lay.set(qn("w:type"), "fixed")
    tblPr.append(lay)


doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.top_margin, sec.bottom_margin = Cm(1.5), Cm(1.4)
sec.left_margin, sec.right_margin = Cm(1.5), Cm(1.5)
sec.footer_distance = Cm(0.7)

style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(8.5)
style.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
style.paragraph_format.space_before = Pt(0)
style.paragraph_format.space_after = Pt(0)
style.paragraph_format.line_spacing = 1.0

p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(2)
set_run(p.add_run("六级词汇 1–3267 · 按单元"), 20, True, "222222")

p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(1)
set_run(p.add_run(
    "共 3269 条 · PDF 前 3267 条 + 按词库补入 2 条（ambition、ambitious） · 10 个单元"), 8, False, "777777")
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(6)
set_run(p.add_run(
    "单元边界取自原词库《词库-Unit1-10.xlsx》各单元首个词在词表中的位置（原文件已删除）"), 8, False, "777777")

sum_tbl = doc.add_table(rows=1, cols=3)
sum_tbl.alignment = WD_TABLE_ALIGNMENT.LEFT
sum_tbl.autofit = False
table_borders(sum_tbl)
SW = [Cm(3.2), Cm(6.4), Cm(2.6)]
for i, text in enumerate(("单元", "编号范围", "词数")):
    cell = sum_tbl.rows[0].cells[i]
    cell.width = SW[i]
    shade(cell, HEADBG)
    cp = cell.paragraphs[0]
    cp.paragraph_format.space_before = Pt(2)
    cp.paragraph_format.space_after = Pt(2)
    set_run(cp.add_run(text), 8.5, True, "8A3B16")
for i, w in enumerate(SW):
    sum_tbl.columns[i].width = w
for i, u in enumerate(units):
    r = sum_tbl.add_row()
    n = u["end"] - u["start"] + 1 + (len(PRE) if i == 0 else 0)
    rng = f"#{u['start']}–#{u['end']}" + ("（+补 2）" if i == 0 else "")
    for j, v in enumerate((u["name"], rng, str(n))):
        c = r.cells[j]
        c.width = SW[j]
        cp = c.paragraphs[0]
        cp.paragraph_format.space_before = Pt(1)
        cp.paragraph_format.space_after = Pt(1)
        set_run(cp.add_run(v), 8.5, False, "444444")

doc.add_paragraph().paragraph_format.space_after = Pt(4)

table = doc.add_table(rows=1, cols=3)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
table.autofit = False
tblPr = table._tbl.tblPr
table_borders(table)
mar = OxmlElement("w:tblCellMar")
for side, w in (("top", "14"), ("left", "80"), ("bottom", "14"), ("right", "80")):
    el = OxmlElement(f"w:{side}")
    el.set(qn("w:w"), w)
    el.set(qn("w:type"), "dxa")
    mar.append(el)
tblPr.append(mar)

WIDTHS = [Cm(1.4), Cm(4.7), Cm(11.9)]

hdr = table.rows[0]
cant_split(hdr)
for i, text in enumerate(("序号", "单词", "释义")):
    cell = hdr.cells[i]
    cell.width = WIDTHS[i]
    shade(cell, HEADBG)
    cp = cell.paragraphs[0]
    cp.paragraph_format.space_before = Pt(3)
    cp.paragraph_format.space_after = Pt(3)
    set_run(cp.add_run(text), 9, True, "8A3B16")
for i, w in enumerate(WIDTHS):
    table.columns[i].width = w
hdr._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))


def add_entry(num_label, item, light=False):
    row = table.add_row()
    cant_split(row)
    c0, c1, c2 = row.cells
    for i, c in enumerate((c0, c1, c2)):
        c.width = WIDTHS[i]
    if light:
        for c in (c0, c1, c2):
            shade(c, LIGHT)
    p0 = c0.paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_run(p0.add_run(str(num_label)), 8 if len(str(num_label)) <= 4 else 7, False, "A06A50")
    set_run(c1.paragraphs[0].add_run(item["w"]), 8.5, True, "1A1A1A")
    p2 = c2.paragraphs[0]
    for j, ln in enumerate(item["m"]):
        if j:
            p2.add_run().add_break()
        set_run(p2.add_run(ln), 8.5, False, "333333")


for i, u in enumerate(units):
    n = u["end"] - u["start"] + 1
    extra = f"　+ 补 {len(PRE)}" if i == 0 else ""
    div = table.add_row()
    cant_split(div)
    merged = div.cells[0].merge(div.cells[2])
    merged.width = Cm(18.0)
    shade(merged, DIVBG)
    dp = merged.paragraphs[0]
    dp.paragraph_format.space_before = Pt(5)
    dp.paragraph_format.space_after = Pt(5)
    set_run(dp.add_run(f"{u['name']}　#{u['start']}–#{u['end']}{extra}　{n + (len(PRE) if i == 0 else 0)} 条"),
            11, True, "8A3B16")

    k = 0
    if i == 0:
        for p_item in PRE:
            add_entry(p_item["tag"], p_item, light=False)
            k += 1
    for num in range(u["start"], u["end"] + 1):
        add_entry(num, by_num[num], light=(k % 2 == 1))
        k += 1

footer = sec.footer
fp = footer.paragraphs[0]
fp.paragraph_format.tab_stops.add_tab_stop(Cm(18.0), WD_TAB_ALIGNMENT.RIGHT)
set_run(fp.add_run("六级词汇 1–3267 · 按单元"), 8, False, "999999")
fp.add_run("\t")
set_run(fp.add_run("第 "), 8, False, "999999")
for instr in ("PAGE", None, "NUMPAGES"):
    if instr is None:
        set_run(fp.add_run(" 页 / 共 "), 8, False, "999999")
        continue
    run = fp.add_run()
    set_run(run, 8, False, "999999")
    b = OxmlElement("w:fldChar"); b.set(qn("w:fldCharType"), "begin")
    it_el = OxmlElement("w:instrText"); it_el.set(qn("xml:space"), "preserve"); it_el.text = f" {instr} "
    s = OxmlElement("w:fldChar"); s.set(qn("w:fldCharType"), "separate")
    t = OxmlElement("w:t"); t.text = "1"
    e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), "end")
    for el in (b, it_el, s, t, e):
        run._r.append(el)
set_run(fp.add_run(" 页"), 8, False, "999999")

out = r"E:\单词\_pdftools\六级词汇_1-3267_按单元.docx"
doc.save(out)
print("docx ok", out)

