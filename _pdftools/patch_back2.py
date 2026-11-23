from pathlib import Path

app = Path(r"E:\单词\app\src\main\assets\app.js")
js = app.read_text(encoding="utf-8")

old = "${peeking?action('go-forward','回到当前 '+icon('arrow'),'primary'):spell?"
new = ("${peeking?'<p class=\"sub\" style=\"text-align:center;margin:4px 0 0\">回看中 · 不会改动学习进度</p>':spell?")
assert old in js, "footer peeking branch not found"
js = js.replace(old, new, 1)
app.write_text(js, encoding="utf-8", newline="\n")
print("footer simplified")
