import re
from pathlib import Path

app = Path(r"E:\单词\app\src\main\assets\app.js")
js = app.read_text(encoding="utf-8")

start = js.find("function srcClass")
end = js.find("function entryHTML")
assert start > 0 and end > start, "block functions not found"

new_block = """function srcClass(s){
  return s==='口述'?'oral':s==='板面'?'board':s==='词表'?'list':'misc';
}
function blockBody(b){
  const parts = (b.parts&&b.parts.length)?b.parts:[{s:'',v:b.v||''}];
  const hasSrc = parts.some(p=>p.s);
  if(!hasSrc){
    return `<div class="block"><span class="k">${esc(b.k)}</span><div class="v">${parts.map(p=>`<div class="pv">${esc(p.v)}</div>`).join('')}</div></div>`;
  }
  return `<div class="block sourced">` + parts.map((p,i)=>
    `<div class="brow"><span class="lab">${i===0?`<b>${esc(b.k)}</b>`:''}`
    + `<i class="src src-${srcClass(p.s)}">${esc(p.s||'')}</i></span>`
    + `<span class="pv">${esc(p.v)}</span></div>`).join('') + `</div>`;
}
function blockHTML(b){
  return blockBody(b);
}
"""
js = js[:start] + new_block + js[end:]
app.write_text(js, encoding="utf-8", newline="\n")
print("app.js: labels stacked in the left column")

css_path = Path(r"E:\单词\app\src\main\assets\style.css")
css = css_path.read_text(encoding="utf-8")

old_rules = (".block.sourced{display:block}"
             "\n.bk{font-size:10px;font-weight:700;letter-spacing:1.5px;color:var(--purple);margin:0 0 2px}"
             "\n.brow{display:grid;grid-template-columns:40px 1fr;gap:10px;align-items:start}"
             "\n.brow+.brow{margin-top:4px}")
new_rules = (".block.sourced{display:block}"
             "\n.brow{display:grid;grid-template-columns:40px 1fr;gap:10px;align-items:start}"
             "\n.brow+.brow{margin-top:4px}"
             "\n.lab{display:flex;flex-direction:column;line-height:1.35;padding-top:2px}"
             "\n.lab b{font-size:10px;font-weight:700;letter-spacing:1px;color:var(--purple)}"
             "\n.lab i{font-style:normal;font-size:10px;font-weight:600;letter-spacing:.5px}")
assert old_rules in css, "block rules not found"
css = css.replace(old_rules, new_rules, 1)

css = css.replace(".src-board{color:#5b4bc4}", ".lab i.src-board{color:#5b4bc4}", 1)
css = css.replace(".src-oral{color:#b06a2c}", ".lab i.src-oral{color:#b06a2c}", 1)
css = css.replace(".src-list{color:#2f8f7a}", ".lab i.src-list{color:#2f8f7a}", 1)
css = css.replace(".src-misc{color:#8a8a7c}", ".lab i.src-misc{color:#8a8a7c}", 1)

css_path.write_text(css, encoding="utf-8", newline="\n")
print("css: stacked label styles")
