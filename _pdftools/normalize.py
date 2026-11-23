import json, re, sys, unicodedata

rows = json.load(open(r"E:\单词\_pdftools\entries.json", encoding="utf-8"))
print("count:", len(rows), file=sys.stderr)

for r in rows:
    if not r["w"].strip():
        print("EMPTY WORD:", r, file=sys.stderr)

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0x2E80 <= o <= 0x2FDF or 0xF900 <= o <= 0xFAFF:
            out.append(unicodedata.normalize("NFKC", ch))
        else:
            out.append(ch)
    return "".join(out)

for r in rows:
    r["w"] = re.sub(r"\s+", " ", norm(r["w"])).strip()
    r["m"] = [norm(x).strip() for x in r["m"] if x.strip()]

json.dump(rows, open(r"E:\单词\_pdftools\entries_norm.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)

# checks
weird = [r for r in rows if re.search(r"[^\x20-\x7e]", r["w"])]
print("words with non-ascii:", len(weird), [r["w"] for r in weird][:10], file=sys.stderr)
caps = [r for r in rows if r["w"] and not re.fullmatch(r"[A-Za-z][A-Za-z'’\- ]*", r["w"])]
print("odd word forms:", len(caps), [(r["n"], r["w"]) for r in caps][:15], file=sys.stderr)

for r in rows[:3] + rows[1500:1503] + rows[-3:]:
    print(r["n"], "|", r["w"], "|", " / ".join(r["m"]), file=sys.stderr)
