import json, re, sys

entries = json.load(open(r"E:\单词\_pdftools\notes_entries.json", encoding="utf-8"))

TAG_RE = re.compile(r"〔[^〕]{1,8}〕")
TIME_RE = re.compile(r"[（(]\s*\d+(?:\.\d+)?\s*[–\-~]\s*\d+(?:\.\d+)?\s*s\s*[）)]")
ORDER = ["拆字", "画面", "回锚", "例句", "派生", "冲突"]


def clean_one(s):
    s = TAG_RE.sub("", s)
    s = TIME_RE.sub("", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"(?<!\*)\*([^*\n]{1,40}?)\*(?!\*)", r"\1", s)
    s = s.replace("`", "")
    s = s.replace("两套都留着——", "")
    s = re.sub(r"[ \t]{2,}", " ", s)
    return s.strip(" ；;，,、" )


def similar(a, b):
    if not a or not b:
        return False
    if a in b or b in a:
        return True
    short, long_ = sorted((a, b), key=len)
    return len(short) / len(long_) > 0.72 and short[:12] == long_[:12]


def join_field(raw):
    segs = [clean_one(x) for x in re.split(r"〔[^〕]{1,8}〕", raw)]
    segs = [s for s in segs if len(s) > 1]
    out = []
    for s in segs:
        if any(similar(s, o) for o in out):
            if out and len(s) > len(out[0]) and similar(s, out[0]):
                out[0] = s
            continue
        out.append(s)
    return "；".join(out)


def compose(e):
    head = f"{e['pos']} {clean_one(e['gloss'])}".strip()
    lines = [head]
    for key in ORDER:
        for k, vals in e["fields"].items():
            if k.startswith(key):
                txt = join_field(" ".join(vals))
                if txt and txt not in ("（无）", "无"):
                    lines.append(f"{key}：{txt}")
    return "\n".join(lines)


words, seen, dropped = [], set(), []
for e in entries:
    key = e["word"].strip().lower()
    if key in seen:
        dropped.append(e["word"])
        continue
    seen.add(key)
    words.append({"word": e["word"].strip(), "meaning": compose(e)})

print("words:", len(words), "dropped:", dropped, file=sys.stderr)
lens = sorted(len(x["meaning"]) for x in words)
print("len min/median/p95/max:", lens[0], lens[len(lens) // 2], lens[int(len(lens) * .95)], lens[-1],
      file=sys.stderr)
print("over 3000:", [x["word"] for x in words if len(x["meaning"]) > 3000], file=sys.stderr)

doc = {"title": "刘晓艳六级词汇 · 精讲 18 课", "words": words}
json.dump(doc, open(r"E:\单词\刘晓艳六级词汇_精讲18课_导入.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("written", file=sys.stderr)

for x in words[:3]:
    print("=====", x["word"], file=sys.stderr)
    print(x["meaning"], file=sys.stderr)
