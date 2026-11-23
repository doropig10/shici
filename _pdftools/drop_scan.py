import json, re
from pathlib import Path

ROOT = Path(r"E:\单词")
app = ROOT / "app/src/main/assets/app.js"
css = ROOT / "app/src/main/assets/style.css"
book = ROOT / "app/src/main/assets/book-data.js"

js = app.read_text(encoding="utf-8")

def rep(old, new, count=1):
    global js
    assert old in js, f"not found: {old[:60]}"
    js = js.replace(old, new, count)

# 1) 不再有「翻阅原书」视图
rep("try{if(view==='reader'){renderReader();return;}", "try{")

# 2) 章节标题措辞
rep('<h2>按原书章节</h2>', '<h2>按讲义章节</h2>')
rep('<p class="sub">Unit → Lesson → 词以群记</p>', '<p class="sub">Unit → Lesson → 词群</p>')

# 3) 词库行：只显示释义
rep("${w.card?esc(chapterLabel(w)||'原书词条')+' · PDF 第 '+w.page+' 页':esc(w.meaning)}", "${esc(w.meaning)}")

# 4) 出处：只讲所属课
rep("function source(w){return w.card?`${chapterLabel(w)||'原书词条'} · PDF 第 ${w.page} 页`:chapterLabel(w)||('我的词表 · '+book().title);}",
    "function source(w){return chapterLabel(w)||'讲义词条';}")

# 5) answer() 去掉扫描卡片分支
m = re.search(r"function answer\(w\)\{.*?\n", js)
assert m, "answer() not found"
js = js[:m.start()] + ("function answer(w){return entryHTML(w);}\n") + js[m.end():]

# 6) 学习页去掉「查看原书上下文」按钮
rep("${w.card&&revealed?action('source','查看原书上下文','quiet','style=\"width:100%\"'):''}", "")

# 7) 词条弹窗去掉「查看原书上下文」
rep("${w.card?action('word-source','查看原书上下文 '+icon('arrow'),'secondary',`data-page=\"${w.page}\" style=\"width:100%;margin-top:12px\"`):''}", "")

# 8) 修改词条弹窗不再显示扫描图
rep("<h2>按原书核对词条</h2>${w.card?`<img class=\"scan-card\" src=\"${esc(w.card)}\" alt=\"原书词条\">`:''}", "<h2>修改词条</h2>")

# 9) 删掉阅读器函数
for fn in ("function openReader(", "function renderReader("):
    m = re.search(re.escape(fn) + r".*?\n(?=function |\Z)", js, re.S)
    assert m, fn
    js = js[:m.start()] + js[m.end():]

# 10) 删掉与扫描相关的动作分发
lines = js.split("\n")
drop_keys = ("openReader(", "renderReader(", "a==='read'", "a==='source'", "a==='word-source'",
             "a==='zoom-card'", "a==='reader-", "readerPage", "readerScale", "readerReturn")
kept = []
for line in lines:
    if any(k in line for k in ("openReader(", "renderReader(")) and "function " in line:
        kept.append(line)
        continue
    if any(k in line for k in ("a==='read'", "a==='source'", "a==='word-source'", "a==='zoom-card'", "a==='reader-")):
        continue
    kept.append(line)
js = "\n".join(kept)

app.write_text(js, encoding="utf-8", newline="\n")
print("app.js cleaned")

# 11) book-data：去掉扫描时期字段
raw = book.read_text(encoding="utf-8")
body = json.loads(raw.split("=", 1)[1].strip().rstrip(";"))
drop = {"page", "position", "printedPage", "card", "cardRegions", "indexPage", "fullEntry", "groupId"}
for w in body["words"]:
    for k in drop:
        w.pop(k, None)
for k in ("pageCount", "source", "cardFormat", "pendingCount", "indexedCount"):
    body.pop(k, None)
book.write_text("window.BOOK_DATA = " + json.dumps(body, ensure_ascii=False, separators=(",", ":")) + ";\n",
                encoding="utf-8", newline="\n")
print("book-data stripped; words:", len(body["words"]))
