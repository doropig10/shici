"""对比两份 book-data 快照，输出变更清单（Markdown）。

用法：python _pdftools/diff_snapshots.py <旧.js> <新.js> [输出.md]
"""
import json, sys
from pathlib import Path


def load(p):
    raw = Path(p).read_text(encoding="utf-8")
    body = raw.split("=", 1)[1].strip().rstrip(";")
    return {w["id"]: w for w in json.loads(body)["words"]}


old_p, new_p = sys.argv[1], sys.argv[2]
out = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(r"E:\单词\_pdftools\变更清单.md")
old, new = load(old_p), load(new_p)

added = [new[i] for i in new if i not in old]
removed = [old[i] for i in old if i not in new]
meaning = [(new[i], old[i]) for i in new if i in old and new[i].get("meaning") != old[i].get("meaning")]
blocks = [(new[i], old[i]) for i in new if i in old and new[i].get("entry") != old[i].get("entry")]


def brief(w):
    return f"{w['word']}（U{w.get('unit')}L{w.get('lesson')}）"


lines = [
    f"# 变更清单",
    "",
    f"- 旧：{len(old)} 词　新：{len(new)} 词",
    f"- 新增 {len(added)}　删除 {len(removed)}　释义变化 {len(meaning)}　讲解块变化 {len(blocks)}",
    "",
]
if added:
    lines += ["## 新增", ""] + [f"- {brief(w)}" for w in added] + [""]
if removed:
    lines += ["## 删除", ""] + [f"- {brief(w)}" for w in removed] + [""]
if meaning:
    lines += ["## 释义变化", ""]
    for n, o in meaning:
        lines.append(f"- **{brief(n)}**：`{o.get('meaning','')}` → `{n.get('meaning','')}`")
    lines.append("")
if blocks:
    lines += ["## 讲解块变化", ""]
    for n, o in blocks:
        before = {b["k"] for b in o.get("entry", [])}
        after = {b["k"] for b in n.get("entry", [])}
        added_k = after - before
        removed_k = before - after
        detail = []
        if added_k:
            detail.append("新增块 " + "/".join(sorted(added_k)))
        if removed_k:
            detail.append("删除块 " + "/".join(sorted(removed_k)))
        if not detail:
            detail.append("内容修改")
        lines.append(f"- {brief(n)}：{'；'.join(detail)}")
    lines.append("")

out.write_text("\n".join(lines), encoding="utf-8")
print(f"written {out}  added={len(added)} removed={len(removed)} meaning={len(meaning)} blocks={len(blocks)}")
