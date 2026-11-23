from pathlib import Path

p = Path(r"E:\单词\app\src\main\assets\app.js")
s = p.read_text(encoding="utf-8")
old = "<p class=\"quiet\">${spell?'自测不改变复习间隔':'诚实地选择，才能安排合适的复习时间。'}</p>"
new = "<p class=\"quiet\" style=\"${peeking?'display:none':''}\">${spell?'自测不改变复习间隔':'诚实地选择，才能安排合适的复习时间。'}</p>"
assert s.count(old) == 1
p.write_text(s.replace(old, new, 1), encoding="utf-8")
print("hint hidden while peeking")
