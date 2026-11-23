import json, re
from collections import Counter
from pathlib import Path

b = json.loads(Path(r"E:\单词\app\src\main\assets\book-data.js").read_text(encoding="utf-8").split("=", 1)[1].strip().rstrip(";"))
ws = b["words"]
print("words:", len(ws), "ids unique:", len({w["id"] for w in ws}))
print("keys:", sorted(ws[0].keys()))
print("no phonetic:", sum(1 for w in ws if not w.get("phonetic")))
print("no entry:", sum(1 for w in ws if not w.get("entry")))
print("empty meaning:", [w["word"] for w in ws if not w.get("meaning")][:5])
print("meaning > 120 chars:", [(w["word"], len(w["meaning"])) for w in ws if len(w["meaning"]) > 120][:5])

# 词性重复：pos 出现在 gloss 开头
pos_re = re.compile(r"^(adj|adv|n|v|vt|vi|prep|conj|pron|num|det|art|int)\.", re.I)
dup_pos = [w["word"] for w in ws if pos_re.match(w["gloss"] or "")]
print("gloss starts with POS:", len(dup_pos), dup_pos[:8])

# 截断 / 占位
print("gloss ends with …:", [(w["word"], w["gloss"]) for w in ws if (w["gloss"] or "").endswith("…")][:5])
print("blocks with …:", sum(1 for w in ws for blk in w["entry"] for p in blk.get("parts", []) if p["v"].endswith("…")))
print("说明 rows:", [w["word"] for w in ws if w["entry"] and w["entry"][0]["k"] == "说明"])

# 词形异常
odd = [w["word"] for w in ws if not re.fullmatch(r"[A-Za-z][A-Za-z'’\- ()/.]*", w["word"])]
print("odd forms:", odd)

# 每课数量
cnt = Counter((w["unit"], w["lesson"]) for w in ws)
print("lessons:", sorted(cnt.items()))
print("units:", Counter(w["unit"] for w in ws))
