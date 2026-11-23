import json

MAP = {
    "\u2ea0": "民", "\u2ec5": "见", "\u2ec6": "角", "\u2ec9": "贝", "\u2ecb": "车",
    "\u2ed3": "长", "\u2ed4": "门", "\u2ed8": "青", "\u2eda": "页", "\u2edb": "风",
    "\u2edc": "飞", "\u2edd": "食", "\u2ee2": "马", "\u2ee3": "骨", "\u2ee4": "鬼",
    "\u2ee5": "鱼", "\u2ee6": "鸟", "\u2ee9": "黄", "\u2eec": "齐", "\u2eee": "齿",
    "\u2ef0": "龙", "\u3b35": "胶",
}

rows = json.load(open(r"E:\单词\_pdftools\entries_final.json", encoding="utf-8"))
for r in rows:
    r["w"] = "".join(MAP.get(c, c) for c in r["w"])
    r["m"] = ["".join(MAP.get(c, c) for c in s) for s in r["m"]]

left = set()
for r in rows:
    for s in [r["w"]] + r["m"]:
        for c in s:
            if 0x2E80 <= ord(c) <= 0x2FDF or 0xF900 <= ord(c) <= 0xFAFF:
                left.add(hex(ord(c)))
print("remaining rare chars:", sorted(left))

json.dump(rows, open(r"E:\单词\_pdftools\entries_clean.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("entries:", len(rows))
