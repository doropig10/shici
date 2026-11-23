from pathlib import Path

p = Path(r"E:\单词\app\src\main\assets\app.js")
s = p.read_text(encoding="utf-8")

old = ("return `<div class=\"block\"><span class=\"k\">${esc(b.k)}</span><div class=\"v\">"
       "${parts.map(p=>`<div class=\"pv\">${esc(p.v)}</div>`).join('')}</div>`;")
new = ("return `<div class=\"block\"><span class=\"k\">${esc(b.k)}</span><div class=\"v\">"
       "${parts.map(p=>`<div class=\"pv\">${esc(p.v)}</div>`).join('')}</div></div>`;")
assert s.count(old) == 1, s.count(old)
p.write_text(s.replace(old, new, 1), encoding="utf-8")
print("closed plain block div")
