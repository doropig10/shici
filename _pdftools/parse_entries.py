import json, re, sys

runs = json.load(open(r"E:\单词\_pdftools\runs1-164.json", encoding="utf-8"))

rows = []  # (num, word, meaning_lines)

for pno in range(1, 165):
    rs = runs[str(pno)]
    left_nums = [r for r in rs if r["x"] < 60 and re.fullmatch(r"\d+", r["t"].strip()) and r["y"] < 745]
    left_words = [r for r in rs if 60 <= r["x"] < 290 and r["y"] < 745]
    right_nums = [r for r in rs if 290 <= r["x"] < 380 and re.fullmatch(r"\d+", r["t"].strip()) and r["y"] < 745]
    right_text = [r for r in rs if r["x"] >= 380 and r["y"] < 745]

    left_words.sort(key=lambda r: (-r["y"], r["x"]))
    left_pairs = []
    for n in sorted(left_nums, key=lambda r: -r["y"]):
        num = int(n["t"])
        cands = [w for w in left_words if -3.5 < (n["y"] - w["y"]) < 3.5]
        word = " ".join(w["t"].strip() for w in sorted(cands, key=lambda r: r["x"]))
        left_pairs.append((num, word))

    right_map = {}
    for n in sorted(right_nums, key=lambda r: -r["y"]):
        num = int(n["t"])
        y0 = n["y"]
        lines = {}
        for r in right_text:
            if y0 - 33.75 < r["y"] <= y0 + 8:
                key = round(r["y"] * 2) / 2
                lines.setdefault(key, []).append(r)
        out_lines = []
        for key in sorted(lines, reverse=True):
            parts = sorted(lines[key], key=lambda r: r["x"])
            out_lines.append("".join(p["t"] for p in parts))
        right_map[num] = out_lines

    for num, word in left_pairs:
        rows.append((num, word, right_map.get(num, [])))

print("total rows:", len(rows), file=sys.stderr)
nums = [r[0] for r in rows]
print("first:", nums[0], "last:", nums[-1], "unique:", len(set(nums)), file=sys.stderr)
missing = [n for n in range(1, 3268) if n not in set(nums)]
print("missing in 1..3267:", missing[:20], len(missing), file=sys.stderr)
dup = [n for n in set(nums) if nums.count(n) > 1]
print("dups:", dup[:10], file=sys.stderr)

bad_word = [r for r in rows if not r[1].strip()]
bad_mean = [r for r in rows if not r[2]]
print("empty word:", len(bad_word), "empty meaning:", len(bad_mean), file=sys.stderr)
for r in bad_mean[:10]:
    print("  ->", r, file=sys.stderr)

kept = [r for r in rows if r[0] <= 3267]
print("kept:", len(kept), file=sys.stderr)
print("sample:", kept[0], kept[-1], file=sys.stderr)
for r in kept:
    if r[0] in (1, 2, 3261, 3265, 3266, 3267):
        print(r[0], r[1], "|", r[2], file=sys.stderr)

json.dump([{"n": n, "w": w, "m": m} for n, w, m in kept],
          open(r"E:\单词\_pdftools\entries.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
