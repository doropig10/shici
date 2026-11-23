from pathlib import Path

app = Path(r"E:\单词\app\src\main\assets\app.js")
js = app.read_text(encoding="utf-8")

def rep(old, new):
    global js
    assert old in js, f"not found: {old[:50]}"
    js = js.replace(old, new, 1)

# 页脚版本号不再写死
rep("拾词 1.0.10 · 只收录你给的词书", "拾词 · 只收录你的词书")

# 去掉没有意义的「核心词 / 基础词」筛选（这本书没有基础部分）
rep("[['all','全部'],['new','未学'],['learned','已学'],['starred','收藏'],['core','核心词'],['basic','基础词']]",
    "[['all','全部'],['new','未学'],['learned','已学'],['starred','收藏']]")

# 词库副标题说清楚「出处」是什么
rep("${esc(book().title)} · 每个词都有出处", "${esc(book().title)} · 每个词都标了 Unit / Lesson")

app.write_text(js, encoding="utf-8", newline="\n")
print("app.js text fixed")
