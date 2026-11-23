import json, re, sys
from pathlib import Path
from collections import Counter

ROOT = Path(r"E:\单词")
ASSETS = ROOT / "app/src/main/assets"
ORIG = ROOT / "_pdftools/book-data.orig.js"
NOTES = ROOT / "_pdftools/notes_entries.json"
APPJS = ASSETS / "app.js"
CSS = ASSETS / "style.css"

TAG_RE = re.compile(r"〔[^〕]{1,8}〕")
TIME_RE = re.compile(r"[（(]\s*\d+(?:\.\d+)?\s*[–\-~]\s*\d+(?:\.\d+)?\s*s\s*[）)]")
NOTE_RE = re.compile(r"[（(]\s*注\s*[:：][^）)]*[）)]")
ORDER = ["拆字", "画面", "回锚", "例句", "派生", "锚点"]
POS_RE = re.compile(r"\s+(adj|adv|n|vt|vi|prep|conj|pron|num|det|art|int)\.\s*")
META_RE = re.compile(r"[（(][^）)]*(?:板面|词表|同页|已单列|交叉引用|\d+(?:\.\d+)?\s*[–\-~]\s*\d+(?:\.\d+)?\s*s)[^）)]*[）)]")
TAIL_META_RE = re.compile(r"[。；;]?\s*板面无词头[^。]*。")


def clean_one(s):
    s = TAG_RE.sub("", s)
    s = TIME_RE.sub("", s)
    s = NOTE_RE.sub("", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"(?<!\*)\*([^*\n]{1,40}?)\*(?!\*)", r"\1", s)
    s = s.replace("`", "").replace("两套都留着——", "")
    s = re.sub(r"[ \t]{2,}", " ", s)
    return s.strip(" ；;，,、")


def clean_anchor(s):
    s = clean_one(s)
    s = META_RE.sub("", s)
    s = TAIL_META_RE.sub("", s)
    s = re.sub(r"[（(]\s*[）)]", "", s)
    s = re.sub(r"\s{2,}", " ", s)
    return s.strip(" ；;，,、。")


def similar(a, b):
    if not a or not b:
        return False
    if a in b or b in a:
        return True
    short, long_ = sorted((a, b), key=len)
    return len(short) / len(long_) > 0.72 and short[:12] == long_[:12]


SOURCE_SPLIT = re.compile(r"〔([^〕]{1,10})〕")
SRC_MAP = {
    "口述": "口述",
    "板面": "板面", "板面例句": "板面", "板面·插播": "板面",
    "板面·她未讲": "板面", "板面/口述": "板面", "派生": "板面",
    "词表": "词表", "词表·未讲": "词表", "板面·词表": "词表",
    "整理": "整理", "推论": "整理", "原文如此": "整理",
    "口述+板面": "口述+板面", "板面+口述": "口述+板面",
}
EMPTY_RE = re.compile(r"^[（(]?\s*无")


def clean_part(txt):
    txt = clean_one(txt)
    txt = META_RE.sub("", txt)
    txt = re.sub(r"^\s*[-—]+\s*", "", txt)
    txt = re.sub(r"\s{2,}", " ", txt)
    txt = txt.strip(" ；;，,、。")
    if EMPTY_RE.match(txt) or txt in ("无", "暂无"):
        return ""
    return txt


def split_parts(raw):
    tokens = SOURCE_SPLIT.split(raw)
    parts = []
    src = ""
    for i, tok in enumerate(tokens):
        if i % 2 == 1:
            src = SRC_MAP.get(tok.strip(), "")
            continue
        txt = clean_part(tok)
        if len(txt) < 2 or txt in ("（无）", "无"):
            continue
        if parts and parts[-1]["s"] == src:
            parts[-1]["v"] += "；" + txt
        else:
            parts.append({"s": src, "v": txt})
    return parts


def join_field(raw):
    segs = [clean_one(x) for x in re.split(r"〔[^〕]{1,8}〕", raw)]
    segs = [s for s in segs if len(s) > 1]
    out = []
    for s in segs:
        if any(similar(s, o) for o in out):
            continue
        out.append(s)
    return "；".join(out)


def variants(w):
    w = w.lower().strip()
    out = {w}
    if "(" in w:
        out.add(re.sub(r"[()]", "", w))
        out.add(re.sub(r"\([^)]*\)", "", w))
    return out


orig = json.loads(ORIG.read_text(encoding="utf-8").split("=", 1)[1].strip().rstrip(";"))
orig_words = orig["words"]
notes = json.load(open(NOTES, encoding="utf-8"))

index = {}
for i, w in enumerate(orig_words):
    for v in variants(w["word"]):
        index.setdefault(v, []).append((i, w))

file_scope = {}
for e in notes:
    hit = index.get(e["word"].lower())
    if hit:
        file_scope.setdefault(e["file"], Counter())[(hit[0][1]["unit"], hit[0][1]["lesson"])] += 1
file_scope = {k: v.most_common(1)[0][0] for k, v in file_scope.items()}

words, seen = [], set()
for n, e in enumerate(notes):
    key = e["word"].strip().lower()
    if key in seen:
        continue
    seen.add(key)
    unit, lesson = file_scope.get(e["file"], (e["unit"], e["lesson"]))
    cands = index.get(key, [])
    pick = next((c for c in cands if c[1]["unit"] == unit and c[1]["lesson"] == lesson), cands[0] if cands else None)
    if pick:
        order, wid, spelling = (0, n), pick[1]["id"], pick[1]["word"]
    else:
        order, wid, spelling = (0, n), key, e["word"].strip()

    pos = clean_one(e["pos"])
    gloss = clean_one(e["gloss"])
    lead = re.match(r"^((?:adj|adv|n|v|vt|vi|prep|conj|pron|num|det|art|int)\.(?:\s*(?:vt|vi|n|adj|adv)\.)*)\s*(.+)$", gloss)
    if lead:
        gpos, rest = lead.group(1).strip(), lead.group(2).strip()
        if pos in ("v.", "v") and gpos.startswith(("vi.", "vt.")):
            pos = gpos
        elif pos in ("adj", "adj.") and gpos.startswith("adj"):
            pos = gpos
        gloss = rest
    gloss = POS_RE.sub(lambda m: "；" + m.group(1) + ". ", gloss).strip("； ")
    blocks = []
    for k in ORDER:
        for fk, vals in e["fields"].items():
            if fk.startswith(k):
                raw = " ".join(vals)
                if k == "锚点":
                    txt = clean_anchor(raw)
                    if txt and txt not in ("（无）", "无"):
                        blocks.append({"k": k, "v": txt})
                else:
                    parts = split_parts(raw)
                    if parts:
                        blocks.append({"k": k, "parts": parts})
    if not blocks:
        blocks.append({"k": "说明", "v": "词表收录，本课未讲"})
    words.append({
        "id": wid, "word": spelling,
        "phonetic": e.get("phonetic") or "",
        "pos": pos, "gloss": gloss, "entry": blocks,
        "meaning": (pos + " " + gloss).strip(),
        "page": None, "position": None, "printedPage": None,
        "section": "core", "card": None, "indexPage": None,
        "cardRegions": [], "fullEntry": False,
        "unit": unit, "lesson": lesson, "groupId": None,
        "_o": (unit, lesson) + order,
    })

words.sort(key=lambda w: w["_o"])
_seen_ids=set(); _uniq=[]
for _w in words:
    if _w["id"] in _seen_ids: continue
    _seen_ids.add(_w["id"]); _uniq.append(_w)
words=_uniq
for w in words:
    del w["_o"]

units = [u for u in orig["structure"]["units"] if any(w["unit"] == u["number"] for w in words)]
book = {
    "id": orig["id"], "title": orig["title"],
    "subtitle": "刘晓燕 · 六级 · 讲义词条",
    "source": "", "pageCount": 0, "words": words,
    "pendingCount": 0, "indexedCount": 0, "cardFormat": None,
    "structure": {"units": units, "groups": []},
}
(ASSETS / "book-data.js").write_text(
    "window.BOOK_DATA = " + json.dumps(book, ensure_ascii=False, separators=(",", ":")) + ";\n",
    encoding="utf-8", newline="\n")

# --- app.js: structured entry renderer ---
js = APPJS.read_text(encoding="utf-8")
if "function entryHTML" not in js:
    helper = (
        "function entryHTML(w){const edited=state.edits[C.key(book().id,w.id)]?.meaning;"
        "if(edited)return `<div class=\"definition\">${esc(edited)}</div>`;"
        "if(!w.entry||!w.entry.length)return `<div class=\"definition\">${esc(w.meaning)}</div>`;"
        "const meta=[w.pos,w.phonetic&&('/'+w.phonetic+'/')].filter(Boolean).map(esc).join(' · ');"
        "return `${meta?`<div class=\"entry-meta\">${meta}</div>`:''}"
        "`<div class=\"gloss\">${esc(w.gloss||w.meaning)}</div>`"
        "`<div class=\"blocks\">${w.entry.map(b=>`<div class=\"block\"><span class=\"k\">${esc(b.k)}</span><span class=\"v\">${esc(b.v)}</span></div>`).join('')}</div>`;}\n"
    )
    js = js.replace("function answer(w){", helper + "function answer(w){", 1)
    old_tail = ":`<div class=\"definition\">${esc(w.meaning)}</div>`;}"
    assert old_tail in js, "answer tail not found"
    js = js.replace(old_tail, ":entryHTML(w);}", 1)
    APPJS.write_text(js, encoding="utf-8", newline="\n")
    print("app.js patched")

# --- css ---
css = CSS.read_text(encoding="utf-8")
if ".gloss{" not in css:
    css += (
        "\n.entry-meta{font-size:12px;color:var(--muted);letter-spacing:.5px;margin:10px 0 4px;text-align:center}"
        "\n.gloss{font-size:20px;font-weight:650;line-height:1.55;color:var(--ink);margin:2px 0 16px;text-align:left;width:100%}"
        "\n.blocks{width:100%;text-align:left;margin-top:4px;border-top:1px solid var(--line);padding-top:4px}"
        "\n.block{display:grid;grid-template-columns:40px 1fr;gap:10px;padding:10px 0;border-bottom:1px solid var(--line)}"
        "\n.block:last-child{border-bottom:0}"
        "\n.block .k{font-size:11px;font-weight:700;letter-spacing:1px;color:var(--purple);padding-top:4px}"
        "\n.block .v{font-size:14px;line-height:1.8;color:#3b3b48}"
    )
    CSS.write_text(css, encoding="utf-8", newline="\n")
    print("css patched")

print("words:", len(words), "with blocks:", sum(1 for w in words if w["entry"]),
      "with phonetic:", sum(1 for w in words if w["phonetic"]))
print("sample:", json.dumps(words[0], ensure_ascii=False)[:300])


