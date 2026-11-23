import json, re, sys, unicodedata

runs = json.load(open(r"E:\单词\_pdftools\runs1-164.json", encoding="utf-8"))

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0x2E80 <= o <= 0x2FDF or 0xF900 <= o <= 0xFAFF:
            out.append(unicodedata.normalize("NFKC", ch))
        else:
            out.append(ch)
    return "".join(out)

rows = []
for pno in range(1, 165):
    rs = runs[str(pno)]
    left_nums = sorted([r for r in rs if r["x"] < 60 and re.fullmatch(r"\d+", r["t"].strip()) and r["y"] < 745], key=lambda r: -r["y"])
    left_words = [r for r in rs if 60 <= r["x"] < 290 and r["y"] < 745]
    right_nums = sorted([r for r in rs if 290 <= r["x"] < 380 and re.fullmatch(r"\d+", r["t"].strip()) and r["y"] < 745], key=lambda r: -r["y"])
    right_text = [r for r in rs if r["x"] >= 380 and r["y"] < 745]

    def bands(nums):
        ys = [n["y"] for n in nums]
        top = 860.0
        out = []
        for i, n in enumerate(nums):
            hi = top if i == 0 else (ys[i - 1] + ys[i]) / 2
            lo = 0.0 if i == len(nums) - 1 else (ys[i] + ys[i + 1]) / 2
            out.append((n, lo, hi))
        return out

    words = {}
    for n, lo, hi in bands(left_nums):
        lines = [w for w in left_words if lo < w["y"] <= hi]
        lines.sort(key=lambda r: (-r["y"], r["x"]))
        words[int(n["t"])] = " ".join(norm(w["t"]).strip() for w in lines)

    means = {}
    for n, lo, hi in bands(right_nums):
        lines = {}
        for r in right_text:
            if lo < r["y"] <= hi:
                lines.setdefault(round(r["y"] * 2) / 2, []).append(r)
        out = []
        for key in sorted(lines, reverse=True):
            parts = sorted(lines[key], key=lambda r: r["x"])
            out.append("".join(p["t"] for p in parts).strip())
        means[int(n["t"])] = [norm(x) for x in out if x.strip()]

    for n, _, _ in bands(left_nums):
        num = int(n["t"])
        rows.append({"n": num, "w": words.get(num, ""), "m": means.get(num, [])})

rows.sort(key=lambda r: r["n"])
print("rows:", len(rows), file=sys.stderr)
nums = [r["n"] for r in rows]
print("first/last:", nums[0], nums[-1], "unique:", len(set(nums)), file=sys.stderr)
print("missing:", [x for x in range(1, 3268) if x not in set(nums)], file=sys.stderr)

multi = [r for r in rows if " " in r["w"]]
print("multi-word entries:", len(multi), [(r["n"], r["w"]) for r in multi][:10], file=sys.stderr)

maxlines = max(len(r["m"]) for r in rows)
print("max meaning lines:", maxlines, file=sys.stderr)
print("rows with >=4 meaning lines:", sum(1 for r in rows if len(r["m"]) >= 4), file=sys.stderr)

nopos = [r for r in rows if r["m"] and not re.match(r"[a-zA-Z]", r["m"][0])]
print("meaning w/o pos:", len(nopos), [(r["n"], r["w"], r["m"]) for r in nopos][:8], file=sys.stderr)

empty = [r for r in rows if not r["w"].strip()]
print("empty word:", [(r["n"], r["m"]) for r in empty], file=sys.stderr)

for r in rows:
    if r["n"] in (985, 986, 987, 2000, 3267):
        print(r["n"], "|", r["w"], "|", " / ".join(r["m"]), file=sys.stderr)

kept = [r for r in rows if r["n"] <= 3267]
json.dump(kept, open(r"E:\单词\_pdftools\entries_v2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("kept:", len(kept), file=sys.stderr)
