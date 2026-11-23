from pathlib import Path

root = Path(r"E:\单词")
js_path = root / "app/src/main/assets/app.js"
js = js_path.read_text(encoding="utf-8")

# 1) rate()：记录评价计数与可撤销的上一次状态
old_rate = ("function rate(rating){const w=current();if(!w||!revealed)return;"
            "const k=C.key(book().id,w.id),old=state.progress[k];state.progress[k]=C.grade(old,rating);")
new_rate = ("function rate(rating){const w=current();if(!w||!revealed)return;"
            "const k=C.key(book().id,w.id),old=state.progress[k];"
            "const prev=old?JSON.parse(JSON.stringify(old)):null;if(prev)delete prev.undo;"
            "const np=C.grade(old,rating);"
            "np.r={g:((old&&old.r&&old.r.g)||0)+(rating==='good'?1:0),h:((old&&old.r&&old.r.h)||0)+(rating==='hard'?1:0),a:((old&&old.r&&old.r.a)||0)+(rating==='again'?1:0)};"
            "np.last=rating;np.undo=prev;state.progress[k]=np;")
assert old_rate in js, "rate() head not found"
js = js.replace(old_rate, new_rate, 1)

# 2) 记录展示与清除/撤销
helpers = '''function recOf(id){
  const p=state.progress[C.key(book().id,id)];
  return p||null;
}
function ratingName(r){return r==='good'?'记得':r==='hard'?'模糊':r==='again'?'忘记':'';}
function recordHTML(id){
  const p=recOf(id);
  if(!p)return `<div class="study-log"><div class="row"><b>学习记录</b><span class="small muted">还没学过</span></div></div>`;
  const r=p.r||{g:0,h:0,a:0};
  const when=p.lastSeen?new Date(p.lastSeen).toLocaleDateString('zh-CN'):'';
  return `<div class="study-log"><div class="row"><b>学习记录</b><span class="small muted">阶段 ${p.stage||0}${when?' · 上次 '+when:''}</span></div>`
    +`<p class="small">上次评价：<b>${ratingName(p.last)||'—'}</b>　记得 <b>${r.g||0}</b> · 模糊 <b>${r.h||0}</b> · 忘记 <b>${r.a||0}</b></p>`
    +`<div class="mark-row">${action('undo-rating','撤销上一次','tag-btn',`data-id="${esc(id)}"`)}${action('clear-word','清除该词记录','tag-btn',`data-id="${esc(id)}"`)}</div></div>`;
}
function undoRating(id){
  const k=C.key(book().id,id),p=state.progress[k];
  if(!p||!p.undo){toast('没有可撤销的评价');return;}
  state.progress[k]=p.undo;save();closeModal();showWord(id);render();toast('已撤销上一次评价');
}
function clearWord(id){
  const k=C.key(book().id,id);
  delete state.progress[k];
  Object.values(state.history||{}).forEach(m=>{if(m&&m[k])delete m[k];});
  save();closeModal();showWord(id);render();toast('已清除该词的学习记录');
}
'''
if "function recordHTML(" not in js:
    js = js.replace("function showWord(id){", helpers + "function showWord(id){", 1)

# 3) 词条弹窗插入学习记录
old_mark = '<div class="mark-row">${action(\'mark\',\'重点\''
assert old_mark in js
js = js.replace(old_mark, '${recordHTML(id)}' + old_mark, 1)

# 4) 列表行显示上次评价
old_tag = 'const mk=markOf(w.id);return action(\'detail\',`<div><b>${esc(w.word)}</b>'
new_tag = 'const mk=markOf(w.id),pp=state.progress[C.key(book().id,w.id)],ln=pp&&pp.last?ratingName(pp.last):\'\';return action(\'detail\',`<div><b>${esc(w.word)}</b>'
assert old_tag in js
js = js.replace(old_tag, new_tag, 1)

old_status = '<span class="status ${cls}">${label}</span>`'
new_status = '<span class="status ${cls}">${label}</span>${ln?`<span class="rec-tag ${pp.last}">${ln}</span>`:\'\'}`'
assert old_status in js
js = js.replace(old_status, new_status, 1)

# 5) 动作分发
anchor = "else if(a==='mark'){setMark(b.dataset.id,b.dataset.kind);}"
assert anchor in js
js = js.replace(anchor, anchor + "\n else if(a==='undo-rating'){undoRating(b.dataset.id);}"
                            "\n else if(a==='clear-word'){clearWord(b.dataset.id);}", 1)

js_path.write_text(js, encoding="utf-8", newline="\n")
print("app.js: records + undo/clear")

css_path = root / "app/src/main/assets/style.css"
css = css_path.read_text(encoding="utf-8")
if ".rec-tag{" not in css:
    css += ("\n.study-log{border-top:1px solid var(--line);margin-top:14px;padding-top:12px}"
            "\n.study-log .row{margin-bottom:4px}"
            "\n.rec-tag{display:inline-block;margin-left:6px;padding:1px 6px;border-radius:6px;font-size:10px;font-weight:600;vertical-align:middle}"
            "\n.rec-tag.good{background:#e4f2d8;color:#4b7a2f}"
            "\n.rec-tag.hard{background:#fdf0d5;color:#8a6a1f}"
            "\n.rec-tag.again{background:#fbe2de;color:#a84b3b}")
    css_path.write_text(css, encoding="utf-8", newline="\n")
print("css: record styles")
