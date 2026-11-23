import re, json, collections
from pathlib import Path

notes = json.load(open(r"E:\单词\_pdftools\notes_entries.json", encoding="utf-8"))
parsed = collections.Counter(x["file"] for x in notes)
HEAD = re.compile(r"^(?:#{2,3}\s+)?\*\*(?P<w>[^*]+)\*\*", re.M)
for f in sorted(Path(r"C:\Users\ASUS\Desktop\英语").glob("*双轨版*.md")):
    t = f.read_text(encoding="utf-8")
    heads = [m.group("w").strip() for m in HEAD.finditer(t)]
    # 粗略过滤：只数形如单词的标题
    heads = [h for h in heads if re.fullmatch(r"[A-Za-z][A-Za-z'’\- ()/.,]*", h) and len(h) <= 40]
    print(f"{f.name[-20:]:22s} parsed={parsed.get(f.name,0):3d} headings={len(heads):3d}")
