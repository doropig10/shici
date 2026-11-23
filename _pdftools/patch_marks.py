from pathlib import Path

root = Path(r"E:\单词")

# 1) state 里加 marks
core = root / "app/src/main/assets/core.js"
c = core.read_text(encoding="utf-8")
old_fresh = "function fresh(){return {version:1,activeBook:'liuxiaoyan-cet6-2026',goal:20,progress:{},history:{},customBooks:[],edits:{},bookmarks:{}};}"
new_fresh = "function fresh(){return {version:1,activeBook:'liuxiaoyan-cet6-2026',goal:20,progress:{},history:{},customBooks:[],edits:{},bookmarks:{},marks:{}};}"
assert old_fresh in c
core.write_text(c.replace(old_fresh, new_fresh, 1), encoding="utf-8", newline="\n")
print("core.js: marks field")

js_path = root / "app/src/main/assets/app.js"
js = js_path.read_text(encoding="utf-8")

# 2) 标记辅助函数
helpers = '''function markOf(id){
  return (state.marks||{})[C.key(book().id,id)]||'';
}
function setMark(id,kind){
  state.marks=state.marks||{};
  const k=C.key(book().id,id);
  if(markOf(id)===kind)delete state.marks[k];else state.marks[k]=kind;
  save();
  if(modalWord===id){closeModal();showWord(id);}else render();
}
'''
if "function markOf(" not in js:
    js = js.replace("function showWord(id){", helpers + "function showWord(id){", 1)

# 3) 词条弹窗加标记按钮
old_modal = '<div class="modal-footer">${action(\'star\',starred?\'已收藏 ★\':\'收藏单词 ☆\',\'outline\',`data-id="${esc(id)}"`)}'
new_modal = ('<div class="mark-row">${action(\'mark\',\'重点\',`tag-btn ${markOf(id)===\'special\'?\'on\':\'\'}`,`data-id="${esc(id)}" data-kind="special"`)}'
             '${action(\'mark\',\'待核对\',`tag-btn ${markOf(id)===\'issue\'?\'on\':\'\'}`,`data-id="${esc(id)}" data-kind="issue"`)}'
             '${markOf(id)?action(\'mark\',\'取消标记\',\'tag-btn\',`data-id="${esc(id)}" data-kind=""`):\'\'}</div>'
             '<div class="modal-footer">${action(\'star\',starred?\'已收藏 ★\':\'收藏单词 ☆\',\'outline\',`data-id="${esc(id)}"`)}')
assert old_modal in js
js = js.replace(old_modal, new_modal, 1)

# 4) 列表行显示标记
old_row = 'return action(\'detail\',`<div><b>${esc(w.word)}</b><p>${esc(w.meaning)}</p></div><span class="status ${cls}">${label}</span>`'
new_row = ('const mk=markOf(w.id);return action(\'detail\',`<div><b>${esc(w.word)}</b>${mk?`<span class="mark-tag ${mk}">${mk===\'special\'?\'重点\':\'待核对\'}</span>`:\'\'}<p>${esc(w.meaning)}</p></div><span class="status ${cls}">${label}</span>`')
assert old_row in js
js = js.replace(old_row, new_row, 1)

# 5) 筛选：标记
old_filter = "filter==='starred'&&state.bookmarks[C.key(book().id,w.id)]"
new_filter = "filter==='starred'&&state.bookmarks[C.key(book().id,w.id)]||filter==='marked'&&(state.marks||{})[C.key(book().id,w.id)]"
assert old_filter in js
js = js.replace(old_filter, new_filter, 1)

old_chips = "[['all','全部'],['new','未学'],['learned','已学'],['starred','收藏']]"
new_chips = "[['all','全部'],['new','未学'],['learned','已学'],['starred','收藏'],['marked','标记']]"
assert old_chips in js
js = js.replace(old_chips, new_chips, 1)

# 6) 动作分发
anchor = "else if(a==='set-voice')"
assert anchor in js
js = js.replace(anchor, "else if(a==='mark'){setMark(b.dataset.id,b.dataset.kind);}\n " + anchor, 1)

js_path.write_text(js, encoding="utf-8", newline="\n")
print("app.js: marks")

css_path = root / "app/src/main/assets/style.css"
css = css_path.read_text(encoding="utf-8")
if ".mark-tag{" not in css:
    css += ("\n.mark-tag{display:inline-block;margin-left:6px;padding:1px 6px;border-radius:6px;font-size:10px;font-weight:600;vertical-align:middle}"
            "\n.mark-tag.special{background:#efeaff;color:#5b4bc4}"
            "\n.mark-tag.issue{background:#ffe9e3;color:#b5533c}"
            "\n.mark-row{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0 4px}"
            "\n.tag-btn{font-size:12px;padding:7px 12px;border-radius:10px;border:1px solid var(--line);background:var(--paper);color:var(--muted)}"
            "\n.tag-btn.on{border-color:var(--purple);background:var(--lav);color:var(--purple);font-weight:600}")
    css_path.write_text(css, encoding="utf-8", newline="\n")
print("css: mark styles")
