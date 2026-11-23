import json, re, sys

pages = json.load(open(r"E:\单词\_pdftools\pages.json", encoding="utf-8"))
print("total pages:", len(pages), file=sys.stderr)

target = "metaphor"
hits = []
for pno, txt in pages.items():
    low = txt.lower()
    for m in re.finditer(target, low):
        hits.append((int(pno), m.start()))

print("hit count:", len(hits), file=sys.stderr)
by_page = {}
for pno, pos in hits:
    by_page.setdefault(pno, []).append(pos)

out = []
for pno in sorted(by_page):
    txt = pages[str(pno)]
    for pos in by_page[pno]:
        ctx = txt[max(0, pos-200):pos+200].replace("\n", " | ")
        out.append(f"page {pno}: ...{ctx}...")

with open(r"E:\单词\_pdftools\hits.txt", "w", encoding="utf-8") as f:
    f.write("\n\n".join(out))
print(f"pages with hits: {sorted(by_page)}", file=sys.stderr)
