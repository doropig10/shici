import json, openpyxl

rows = json.load(open(r"E:\单词\_pdftools\entries_clean.json", encoding="utf-8"))
by_num = {r["n"]: r for r in rows}
pos = {}
for r in rows:
    pos.setdefault(r["w"].lower(), r["n"])

wb = openpyxl.load_workbook(r"E:\单词\词库-按单元\词库-Unit1-10.xlsx", data_only=True)

units = []
for ws in wb.worksheets[1:]:
    data = [r for r in ws.iter_rows(min_row=3, values_only=True) if r[5]]
    words = [str(r[5]).strip().lower() for r in data]
    first_word = words[0]
    hits = [pos[w] for w in words if w in pos]
    start = min(hits)
    units.append({
        "name": ws.title,
        "first_word": first_word,
        "first_pos": pos.get(first_word),
        "start": start,
        "words_in_xlsx": len(words),
        "found": len(hits),
    })

units.sort(key=lambda u: u["start"])
assert units[0]["start"] == 1

for i, u in enumerate(units):
    end = units[i + 1]["start"] - 1 if i + 1 < len(units) else 3267
    u["end"] = end

prev_end = 0
for u in units:
    assert u["start"] == prev_end + 1, (u["name"], u["start"], prev_end)
    prev_end = u["end"]

print("units:")
for u in units:
    print(f"  {u['name']}: #{u['start']}-#{u['end']}  {u['end'] - u['start'] + 1} 词 "
          f"(xlsx 首词 {u['first_word']} @ {u['first_pos']}, xlsx 收录 {u['found']}/{u['words_in_xlsx']})")

json.dump(units, open(r"E:\单词\_pdftools\units.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
