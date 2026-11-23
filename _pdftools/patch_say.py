from pathlib import Path

app = Path(r"E:\单词\app\src\main\assets\app.js")
js = app.read_text(encoding="utf-8")

helper = "function say(w){return String(w).replace(/\\(([^)]*)\\)/g,'$1');}\n"
if "function say(w){" not in js:
    js = js.replace("function srcClass(s){", helper + "function srcClass(s){", 1)

count = js.count('data-word="${esc(w.word)}"')
js = js.replace('data-word="${esc(w.word)}"', 'data-word="${esc(say(w.word))}"')
app.write_text(js, encoding="utf-8", newline="\n")
print("speak text sanitized:", count, "call sites")
