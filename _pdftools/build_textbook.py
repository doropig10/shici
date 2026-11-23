import json, re, shutil, sys
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(r"E:\单词")
ASSETS = ROOT / "app/src/main/assets"
ORIG = ROOT / "_pdftools/book-data.orig.js"
NOTES = ROOT / "_pdftools/notes_entries.json"
IMPORT_JSON = ROOT / "刘晓艳六级词汇_精讲18课_导入.json"
APPJS = ASSETS / "app.js"
MANIFEST = ROOT / "app/src/main/AndroidManifest.xml"

orig = json.loads(ORIG.read_text(encoding="utf-8").split("=", 1)[1].strip().rstrip(";"))
orig_words = orig["words"]
notes = json.load(open(NOTES, encoding="utf-8"))
imp = json.load(open(IMPORT_JSON, encoding="utf-8"))
composed = {w["word"].lower(): w["meaning"] for w in imp["words"]}


def variants(w):
    w = w.lower().strip()
    out = {w}
    if "(" in w:
        out.add(re.sub(r"[()]", "", w))
        out.add(re.sub(r"\([^)]*\)", "", w))
    return out


index = defaultdict(list)
orig_pos = {}
for i, w in enumerate(orig_words):
    orig_pos[id(w)] = i
    for v in variants(w["word"]):
        index[v].append(w)

file_scope = {}
for e in notes:
    hits = index.get(e["word"].lower())
    if hits:
        file_scope.setdefault(e["file"], Counter())[(hits[0]["unit"], hits[0]["lesson"])] += 1
file_scope = {k: v.most_common(1)[0][0] for k, v in file_scope.items()}

words, seen = [], set()
for n, e in enumerate(notes):
    key = e["word"].lower()
    meaning = composed.get(key)
    if not meaning or key in seen:
        continue
    seen.add(key)
    unit, lesson = file_scope.get(e["file"], (e["unit"], e["lesson"]))
    cands = index.get(key, [])
    target = next((c for c in cands if c["unit"] == unit and c["lesson"] == lesson), cands[0] if cands else None)
    if target:
        wid = target["id"]
        spelling = target["word"]
        order = (0, orig_pos[id(target)])
    else:
        wid = key
        spelling = e["word"].strip()
        order = (1, n)
    words.append({
        "id": wid, "word": spelling, "meaning": meaning,
        "page": None, "position": None, "printedPage": None,
        "section": "core", "card": None, "indexPage": None,
        "cardRegions": [], "fullEntry": False,
        "unit": unit, "lesson": lesson, "groupId": None,
        "_order": (unit, lesson) + order,
    })

words.sort(key=lambda w: w["_order"])
for w in words:
    del w["_order"]

units = [u for u in orig["structure"]["units"] if any(w["unit"] == u["number"] for w in words)]
book = {
    "id": orig["id"],
    "title": orig["title"],
    "subtitle": "刘晓燕 · 英语六级 · 讲义词条（无图版）",
    "source": "",
    "pageCount": 0,
    "words": words,
    "pendingCount": 0,
    "indexedCount": 0,
    "cardFormat": None,
    "structure": {"units": units, "groups": []},
}
(ASSETS / "book-data.js").write_text(
    "window.BOOK_DATA = " + json.dumps(book, ensure_ascii=False, separators=(",", ":")) + ";\n",
    encoding="utf-8", newline="\n")

# app.js: drop 原书阅读 entry points
js = APPJS.read_text(encoding="utf-8")
before = js
js = js.replace("${b.id===BOOK_DATA.id?action('read','翻阅原书','outline'):''}", "")
js = js.replace(" else if(a==='read')openReader(10);", "")
js = js.replace("扫描 PDF 需要先识别、核对，再制成词卡；当前书的原文已随应用保存。", "词条来自讲义文本，可直接导入或修改。")
if js != before:
    APPJS.write_text(js, encoding="utf-8", newline="\n")

# drop image assets
removed = []
for name in ("cards", "book"):
    d = ASSETS / name
    if d.exists():
        cnt = sum(1 for _ in d.rglob("*"))
        shutil.rmtree(d)
        removed.append((name, cnt))

# bump version
xml = MANIFEST.read_text(encoding="utf-8")
xml = re.sub(r'android:versionCode="\d+"', 'android:versionCode="8"', xml)
xml = re.sub(r'android:versionName="[^"]+"', 'android:versionName="1.0.7"', xml)
MANIFEST.write_text(xml, encoding="utf-8", newline="\n")

print("words:", len(words), "unique ids:", len({w["id"] for w in words}))
print("units:", [u["number"] for u in units])
print("by unit/lesson:", sorted(Counter((w["unit"], w["lesson"]) for w in words).items())[:12])
print("removed assets:", removed)
print("app.js changed:", js != before)
