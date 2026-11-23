from pathlib import Path

a = Path(r"E:\单词\app\src\main\assets\app.js")
s = a.read_text(encoding="utf-8")
old = ("${p.s?`<span class=\"src src-${p.s==='口述'?'oral':p.s==='板面'?'board':'misc'}\">${esc(p.s)}</span>`:''}")
new = ("<span class=\"src src-${p.s==='口述'?'oral':p.s==='板面'?'board':'misc'}\">${esc(p.s||'')}</span>")
assert old in s, "renderer pattern not found"
a.write_text(s.replace(old, new, 1), encoding="utf-8")

c = Path(r"E:\单词\app\src\main\assets\style.css")
t = c.read_text(encoding="utf-8")
o = ".src{flex:0 0 auto;font-size:10px;font-weight:600;line-height:1.9;padding:0 5px;border-radius:6px;background:#efeaff;color:#5b4bc4;letter-spacing:.5px}"
n = (".src{flex:0 0 42px;width:42px;text-align:center;font-size:10px;font-weight:600;line-height:1.9;padding:0;"
     "border-radius:6px;background:#efeaff;color:#5b4bc4;letter-spacing:.5px}.src:empty{background:none}")
assert o in t, "src rule not found"
c.write_text(t.replace(o, n), encoding="utf-8")
print("aligned badges")
