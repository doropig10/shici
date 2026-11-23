import re, glob, os, json, sys

FILES = sorted(glob.glob(r"C:\Users\ASUS\Desktop\英语\*双轨版*.md"))
HEAD_RE = re.compile(r"^(?:#{2,3}\s+)?\*\*(.+?)\*\*\s*(?:`?(/[^`]*?/)`?)?\s*(?:\*(.+?)\*)?\s*(.*)$")
FIELD_RE = re.compile(r"^-\s+\*\*(.+?)\*\*\s*[：:]\s*(.*)$")

entries = []
for path in FILES:
    base = os.path.basename(path)
    m = re.search(r"U(\d+)L(\d+)_P(\d+)", base)
    unit = int(m.group(1)) if m else None
    lesson = int(m.group(2)) if m else None
    page = int(m.group(3)) if m else None

    cur = None
    field = None
    for raw in open(path, encoding="utf-8").read().split("\n"):
        line = raw.strip()
        hm = HEAD_RE.match(line)
        ok = bool(hm) and not line.startswith("- ") and not line.startswith(">") and not line.startswith("|")
        if ok:
            word = hm.group(1).strip()
            if not re.fullmatch(r"[A-Za-z][A-Za-z'’\- ()/.,]*", word) or len(word) > 40:
                ok = False
        if ok:
            cur = {
                "file": base, "unit": unit, "lesson": lesson, "page": page,
                "word": word,
                "phonetic": (hm.group(2) or "").strip("/"),
                "pos": (hm.group(3) or "").strip(),
                "gloss": (hm.group(4) or "").strip(),
                "fields": {},
            }
            entries.append(cur)
            field = None
            continue
        if cur is None:
            continue
        fm = FIELD_RE.match(line)
        if fm:
            field = fm.group(1).strip()
            cur["fields"].setdefault(field, [])
            if fm.group(2).strip():
                cur["fields"][field].append(fm.group(2).strip())
        elif line.startswith(">") and "记忆锚点" in line:
            txt = re.sub(r"^>\s*", "", line).replace("**记忆锚点**", "").strip("　 ")
            cur["fields"].setdefault("锚点", [])
            if txt:
                cur["fields"]["锚点"].append(txt)
            field = "锚点"
        elif line.startswith(">") and field == "锚点":
            txt = re.sub(r"^>\s*", "", line).strip("　 ")
            if txt:
                cur["fields"]["锚点"].append(txt)
        elif field == "锚点":
            field = None  # 引用块结束，后续正文不再并入锚点
        elif field and line and not line.startswith("#") and not line.startswith(">"):
            cur["fields"][field].append(re.sub(r"^-\s*", "", line))
        elif line.startswith("## ") or line == "---":
            field = None

print("files:", len(FILES), "entries:", len(entries), file=sys.stderr)
print("without phonetic:", sum(1 for e in entries if not e["phonetic"]), file=sys.stderr)
print("without gloss:", [(e["word"], e["gloss"]) for e in entries if not e["gloss"]][:6], file=sys.stderr)
words = [e["word"].lower() for e in entries]
from collections import Counter
dups = {w: c for w, c in Counter(words).items() if c > 1}
print("dups:", dups, file=sys.stderr)

for e in entries[:2]:
    print("---", e["word"], e["phonetic"], "|", e["pos"], "|", e["gloss"], file=sys.stderr)
    for k, v in e["fields"].items():
        print("   ", k, "=>", " ".join(v)[:100], file=sys.stderr)

json.dump(entries, open(r"E:\单词\_pdftools\notes_entries.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
