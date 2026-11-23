import json, re

rows = json.load(open(r"E:\单词\_pdftools\entries_clean.json", encoding="utf-8"))
assert len(rows) == 3267 and rows[0]["n"] == 1 and rows[-1]["n"] == 3267

# ---------- markdown ----------
def meaning_md(m):
    parts = [x.strip() for x in m if x.strip()]
    return "；".join(parts)

lines = [
    "# 六级词汇 1–3267",
    "",
    "> 共 **3267** 词，按原书顺序编号（与《英语六级 你还在背单词吗（新版）》PDF 词条编号一致）。",
    "> 范围：#1 aggressive — #3267 metaphorical（原书第 1–164 页）。后 4270 条已剔除。",
    "",
]
group_start = 1
for r in rows:
    if (r["n"] - 1) % 100 == 0:
        if r["n"] != 1:
            lines.append("")
        lines.append(f"## {r['n']}–{min(r['n'] + 99, 3267)}")
        lines.append("")
    lines.append(f"{r['n']}. **{r["w"]}** — {meaning_md(r['m'])}")

with open(r"E:\单词\六级词汇_1-3267.md", "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines) + "\n")

print("md written:", len(lines), "lines")

