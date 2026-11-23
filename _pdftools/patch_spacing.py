from pathlib import Path

css_path = Path(r"E:\单词\app\src\main\assets\style.css")
css = css_path.read_text(encoding="utf-8")

# 1) 记忆块之间的留白收紧
old_block = ".block{display:grid;grid-template-columns:40px 1fr;gap:10px;padding:10px 0;border-bottom:1px solid var(--line)}"
new_block = ".block{display:grid;grid-template-columns:40px 1fr;gap:10px;padding:7px 0;border-bottom:1px solid var(--line)}"
assert old_block in css
css = css.replace(old_block, new_block)

old_gap = ".block .v .part+.part{margin-top:7px}"
new_gap = ".block .v .part+.part{margin-top:5px}"
assert old_gap in css
css = css.replace(old_gap, new_gap)

# 2) 展开后的学习卡片：内容从顶部排，别把短词条挤在中间留一片空白
old_card = ".study-card{background:var(--paper);border:1px solid var(--line);border-radius:26px;margin:26px 0 20px;padding:30px 21px;min-height:360px;display:flex;align-items:center;flex-direction:column;justify-content:center;text-align:center}"
new_card = ".study-card{background:var(--paper);border:1px solid var(--line);border-radius:26px;margin:26px 0 20px;padding:30px 21px;min-height:360px;display:flex;align-items:center;flex-direction:column;justify-content:center;text-align:center}"
assert old_card in css
if ".study-card.revealed{" not in css:
    css = css.replace(new_card, new_card + "\n.study-card.revealed{justify-content:flex-start;min-height:auto;padding-top:26px}", 1)

# 3) 窄屏再紧一点
old_narrow = "  .block{grid-template-columns:32px 1fr;gap:8px;padding:9px 0}"
new_narrow = "  .block{grid-template-columns:32px 1fr;gap:8px;padding:7px 0}"
if old_narrow in css:
    css = css.replace(old_narrow, new_narrow)
else:
    css = css.replace("@media (max-width:400px){", "@media (max-width:400px){\n  .block{padding:7px 0}", 1)

css_path.write_text(css, encoding="utf-8")
print("css tightened")

# 4) 学习卡片在展开时挂 revealed 类
app = Path(r"E:\单词\app\src\main\assets\app.js")
js = app.read_text(encoding="utf-8")
old_div = '<div class="study-card"><div class="source-tag">'
new_div = '<div class="study-card ${revealed?\'revealed\':\'\'}"><div class="source-tag">'
assert old_div in js, "study-card markup not found"
app.write_text(js.replace(old_div, new_div, 1), encoding="utf-8")
print("app.js: revealed class")
