import re
from pathlib import Path

app = Path(r"E:\单词\app\src\main\assets\app.js")
js = app.read_text(encoding="utf-8")

start = js.find("function blockBody")
end = js.find("function entryHTML")
assert start > 0 and end > start, "functions not found"

new_block = """function srcClass(s){
  return s==='口述'?'oral':s==='板面'?'board':s==='词表'?'list':'misc';
}
function blockBody(b){
  const parts = (b.parts&&b.parts.length)?b.parts:[{s:'',v:b.v||''}];
  const hasSrc = parts.some(p=>p.s);
  if(!hasSrc){
    return `<div class="block"><span class="k">${esc(b.k)}</span><div class="v">${parts.map(p=>`<div class="pv">${esc(p.v)}</div>`).join('')}</div>`;
  }
  return `<div class="block sourced"><div class="bk">${esc(b.k)}</div>${parts.map(p=>`<div class="brow"><span class="src src-${srcClass(p.s)}">${esc(p.s||'')}</span><span class="pv">${esc(p.v)}</span></div>`).join('')}</div>`;
}
function blockHTML(b){
  return blockBody(b);
}
"""
js = js[:start] + new_block + js[end:]

# entryHTML 里原来的 block 包裹结构换成 blockHTML 直接输出
js = js.replace(
    "+`<div class=\"blocks\">${w.entry.map(b=>`<div class=\"block\"><span class=\"k\">${esc(b.k)}</span><div class=\"v\">${blockBody(b)}</div></div>`).join('')}</div>`;",
    "+`<div class=\"blocks\">${w.entry.map(blockBody).join('')}</div>`;",
    1,
)
app.write_text(js, encoding="utf-8", newline="\n")
print("app.js: source labels moved into the label column")

css_path = Path(r"E:\单词\app\src\main\assets\style.css")
css = css_path.read_text(encoding="utf-8")

old = (".block{display:grid;grid-template-columns:40px 1fr;gap:10px;padding:7px 0;border-bottom:1px solid var(--line)}")
new = (".block{display:grid;grid-template-columns:40px 1fr;gap:10px;padding:7px 0;border-bottom:1px solid var(--line)}"
       "\n.block.sourced{display:block}"
       "\n.bk{font-size:10px;font-weight:700;letter-spacing:1.5px;color:var(--purple);margin:0 0 2px}"
       "\n.brow{display:grid;grid-template-columns:40px 1fr;gap:10px;align-items:start}"
       "\n.brow+.brow{margin-top:4px}")
assert old in css
css = css.replace(old, new, 1)

# 来源标签从「药丸」改成纯色小字，放在标签列
old_src = (".src{flex:0 0 42px;width:42px;text-align:center;font-size:10px;font-weight:600;line-height:1.9;padding:0;"
           "border-radius:6px;background:#efeaff;color:#5b4bc4;letter-spacing:.5px}.src:empty{background:none}")
new_src = (".src{font-size:10px;font-weight:600;line-height:1.85;color:#5b4bc4;letter-spacing:.5px;white-space:nowrap}"
           "\n.src-board{color:#5b4bc4}"
           "\n.src-oral{color:#b06a2c}"
           "\n.src-list{color:#2f8f7a}"
           "\n.src-misc{color:#8a8a7c}")
if old_src in css:
    css = css.replace(old_src, new_src, 1)

# 旧的 .src-oral / .src-misc 叠色规则清掉（改用上面的纯文字色）
for stray in (".src-oral{background:#fff0e4;color:#b06a2c}", ".src-misc{background:#eeede8;color:#7c7b70}"):
    css = css.replace(stray, "")

css_path.write_text(css, encoding="utf-8", newline="\n")
print("css: label column layout")
