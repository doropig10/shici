import json, re, shutil, sys
from collections import Counter, defaultdict

ASSET = r"E:\单词\app\src\main\assets\book-data.js"
BACKUP = r"E:\单词\_pdftools\book-data.orig.js"

shutil.copyfile(ASSET, BACKUP)
raw = open(ASSET, encoding="utf-8").read()
head, body = raw.split("=", 1)
body = body.strip()
assert body.endswith(";")
data = json.loads(body[:-1])
words = data["words"]

notes = json.load(open(r"E:\单词\_pdftools\notes_entries.json", encoding="utf-8"))
imp = json.load(open(r"E:\单词\刘晓艳六级词汇_精讲18课_导入.json", encoding="utf-8"))
composed = {w["word"].lower(): w["meaning"] for w in imp["words"]}

by_word = {w["word"].lower(): w for w in words}
by_exact = {(w["word"].lower(), w["unit"], w["lesson"]): w for w in words}

# majority (unit, lesson) per md file, taken from words already in the app
file_scope = {}
for e in notes:
    if e["word"].lower() in by_word:
        w = by_word[e["word"].lower()]
        file_scope.setdefault(e["file"], Counter())[(w["unit"], w["lesson"])] += 1
file_scope = {k: v.most_common(1)[0][0] for k, v in file_scope.items()}

new_words, updated = [], 0
for e in notes:
    key = e["word"].lower()
    unit, lesson = file_scope.get(e["file"], (e["unit"], e["lesson"]))
    target = by_exact.get((key, unit, lesson)) or by_word.get(key)
    meaning = composed.get(key)
    if not meaning:
        continue
    if target is not None:
        target["meaning"] = meaning
        updated += 1
    else:
        new_words.append({
            "id": key,
            "word": e["word"].strip(),
            "meaning": meaning,
            "page": None,
            "position": None,
            "printedPage": None,
            "section": "core",
            "card": None,
            "indexPage": None,
            "cardRegions": [],
            "fullEntry": False,
            "unit": unit,
            "lesson": lesson,
            "groupId": None,
            "_fromNotes": e["file"],
        })

# anchor each new word after the last existing word of the same unit/lesson
anchor = {}
for i, w in enumerate(words):
    anchor[(w["unit"], w["lesson"])] = i
inserts = defaultdict(list)
appended = []
for nw in new_words:
    k = (nw["unit"], nw["lesson"])
    if k in anchor:
        inserts[anchor[k]].append(nw)
    else:
        appended.append(nw)

merged = []
for i, w in enumerate(words):
    merged.append(w)
    merged.extend(inserts.get(i, []))
merged.extend(appended)
data["words"] = merged

out = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
open(ASSET, "w", encoding="utf-8", newline="\n").write(head + "=" + out + ";\n")

ids = [w["id"] for w in merged]
print("updated:", updated, "new:", len(new_words), "appended at end:", len(appended))
print("total words:", len(merged), "unique ids:", len(set(ids)))
print("sections:", Counter(w["section"] for w in merged))
print("with card:", sum(1 for w in merged if w.get("card")))
print("scope map:", {k.split("_")[2] if len(k.split("_")) > 2 else k: v for k, v in list(file_scope.items())[:5]})
