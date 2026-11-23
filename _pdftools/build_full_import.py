import json, re, unicodedata
from collections import Counter

rows = json.load(open(r"E:\单词\_pdftools\pdf_all_entries.json", encoding="utf-8"))


def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0x2E80 <= o <= 0x2FDF or 0xF900 <= o <= 0xFAFF:
            out.append(unicodedata.normalize("NFKC", ch))
        else:
            out.append(ch)
    return "".join(out)


REPL = {"\u2ecb": "车", "\u2ed3": "长", "\u2ea0": "民", "\u2ec5": "见", "\u2ec6": "角",
        "\u2ec9": "贝", "\u2ed4": "门", "\u2ed8": "青", "\u2eda": "页", "\u2edb": "风",
        "\u2edc": "飞", "\u2edd": "食", "\u2ee2": "马", "\u2ee3": "骨", "\u2ee4": "鬼",
        "\u2ee5": "鱼", "\u2ee6": "鸟", "\u2ee9": "黄", "\u2eec": "齐", "\u2eee": "齿",
        "\u2ef0": "龙", "\u3b35": "胶"}


def clean(s):
    s = norm(s)
    s = "".join(REPL.get(c, c) for c in s)
    s = s.replace("…", "…")
    s = re.sub(r"\s{2,}", " ", s)
    return s.strip()


words, seen = [], set()
dups = []
for r in rows:
    w = clean(r["w"])
    m = "；".join(clean(x) for x in r["m"] if clean(x))
    if not w or not m:
        continue
    key = w.lower()
    if key in seen:
        dups.append(w)
        continue
    seen.add(key)
    words.append({"word": w, "meaning": m})

print("kept:", len(words), "dups:", len(dups), dups[:8])
print("rim/grim positions:", [i for i, w in enumerate(words, 1) if w["word"].lower() in ("rim", "grim")])

doc = {"title": "英语六级 你还在背单词吗（新版）· 全书词表", "words": words}
json.dump(doc, open(r"E:\单词\六级词汇_全书7537_导入.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)

# 讲义覆盖情况
notes = json.load(open(r"E:\单词\_pdftools\notes_entries.json", encoding="utf-8"))
note_words = {e["word"].strip().lower() for e in notes}
pdf_words = {w["word"].lower() for w in words}
print("讲义词条:", len(note_words), "其中在 PDF 词表里:", len(note_words & pdf_words))
print("讲义有但 PDF 没有:", list(note_words - pdf_words)[:10])
