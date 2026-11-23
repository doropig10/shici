import json, re, shutil
from collections import Counter, defaultdict

ROOT = r"E:\单词"
BOOK = ROOT + r"\app\src\main\assets\book-data.js"
ORIG = ROOT + r"\_pdftools\book-data.orig.js"
NOTES = ROOT + r"\_pdftools\notes_entries.json"
IMPORT_JSON = ROOT + r"\刘晓艳六级词汇_精讲18课_导入.json"

raw = open(ORIG, encoding="utf-8").read()
head, body = raw.split("=", 1)
body = body.strip()
assert body.endswith(";")
data = json.loads(body[:-1])
words = data["words"]

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
for w in words:
    for v in variants(w["word"]):
        index[v].append(w)

ambiguous = {k: v for k, v in index.items() if len({id(x) for x in v}) > 1}
print("ambiguous keys:", {k: [x["word"] for x in v] for k, v in list(ambiguous.items())[:5]})

file_scope = {}
for e in notes:
    hits = index.get(e["word"].lower())
    if hits:
        hit = hits[0]
        file_scope.setdefault(e["file"], Counter())[(hit["unit"], hit["lesson"])] += 1
file_scope = {k: v.most_common(1)[0][0] for k, v in file_scope.items()}

updated, new_words, used_ids = 0, [], {w["id"] for w in words}
for e in notes:
    key = e["word"].lower()
    meaning = composed.get(key)
    if not meaning:
        continue
    unit, lesson = file_scope.get(e["file"], (e["unit"], e["lesson"]))
    cands = index.get(key, [])
    target = next((c for c in cands if c["unit"] == unit and c["lesson"] == lesson), cands[0] if cands else None)
    if target is not None:
        if target["meaning"] != meaning:
            target["meaning"] = meaning
            updated += 1
        continue
    wid = key
    if wid in used_ids:
        continue
    used_ids.add(wid)
    new_words.append({
        "id": wid, "word": e["word"].strip(), "meaning": meaning,
        "page": None, "position": None, "printedPage": None,
        "section": "core", "card": None, "indexPage": None,
        "cardRegions": [], "fullEntry": False,
        "unit": unit, "lesson": lesson, "groupId": None,
    })

anchor = {}
for i, w in enumerate(words):
    anchor[(w["unit"], w["lesson"])] = i
inserts = defaultdict(list)
appended = []
for nw in new_words:
    k = (nw["unit"], nw["lesson"])
    (inserts[anchor[k]] if k in anchor else appended).append(nw)

merged = []
for i, w in enumerate(words):
    merged.append(w)
    if i in inserts:
        merged.extend(inserts[i])
merged.extend(appended)
data["words"] = merged
open(BOOK, "w", encoding="utf-8", newline="\n").write(
    head + "=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")

ids = [w["id"] for w in merged]
print("updated:", updated, "new:", len(new_words), "total:", len(merged))
print("unique ids:", len(set(ids)))
print("with card:", sum(1 for w in merged if w.get("card")))
