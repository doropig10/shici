from pathlib import Path

a = Path(r"E:\单词\app\src\main\assets\app.js")
s = a.read_text(encoding="utf-8")
old = '<div class="part"><span class="pv">'
new = '<div class="part"><span class="src src-misc"></span><span class="pv">'
assert s.count(old) == 1, s.count(old)
a.write_text(s.replace(old, new, 1), encoding="utf-8")
print("anchor fallback aligned")
