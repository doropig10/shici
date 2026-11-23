from pathlib import Path

root = Path(r"E:\单词")

# ---------- Java: 通用导出 ----------
main = root / "app/src/main/java/cn/shici/wordbook/MainActivity.java"
s = main.read_text(encoding="utf-8")
old_export = '''        @JavascriptInterface public void exportBackup(String data) {
            runOnUiThread(() -> {
                pendingExport = data;
                Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
                intent.setType("application/json"); intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.putExtra(Intent.EXTRA_TITLE,"拾词-学习备份.json");
                startActivityForResult(intent,SAVE_BACKUP);
            });
        }'''
new_export = '''        @JavascriptInterface public void exportBackup(String data) {
            exportText("拾词-学习备份.json", data);
        }

        @JavascriptInterface public void exportText(String name, String data) {
            runOnUiThread(() -> {
                pendingExport = data;
                Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
                intent.setType(name != null && name.endsWith(".csv") ? "text/csv" : "application/json");
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.putExtra(Intent.EXTRA_TITLE, name == null || name.isEmpty() ? "拾词-导出.txt" : name);
                startActivityForResult(intent,SAVE_BACKUP);
            });
        }'''
assert old_export in s, "exportBackup not found"
main.write_text(s.replace(old_export, new_export, 1), encoding="utf-8", newline="\n")
print("MainActivity: exportText")

# ---------- app.js ----------
js_path = root / "app/src/main/assets/app.js"
js = js_path.read_text(encoding="utf-8")

old_helpers = '''function markOf(id){
  return (state.marks||{})[C.key(book().id,id)]||'';
}
function setMark(id,kind){
  state.marks=state.marks||{};
  const k=C.key(book().id,id);
  if(markOf(id)===kind)delete state.marks[k];else state.marks[k]=kind;
  save();
  if(modalWord===id){closeModal();showWord(id);}
  render();
}'''
new_helpers = '''function markData(id){
  const v=(state.marks||{})[C.key(book().id,id)];
  if(!v)return null;
  return typeof v==='string'?{t:v,n:''}:v;
}
function markOf(id){const m=markData(id);return m?m.t:'';}
function markNote(id){const m=markData(id);return m?(m.n||''):'';}
function markCount(){return Object.keys(state.marks||{}).filter(k=>k.startsWith(book().id+':')).length;}
function setMark(id,kind){
  state.marks=state.marks||{};
  const k=C.key(book().id,id);
  const cur=markData(id);
  if(cur&&cur.t===kind)delete state.marks[k];
  else state.marks[k]={t:kind,n:cur?(cur.n||''):'',at:Date.now()};
  save();
  if(modalWord===id){closeModal();showWord(id);}
  render();
}
function markCSV(){
  const rows=[['单词','Unit','Lesson','标记','原因','释义']];
  book().words.forEach(w=>{
    const m=markData(w.id);
    if(!m)return;
    rows.push([w.word,String(w.unit||''),String(w.lesson||''),m.t==='special'?'重点':'待核对',m.n||'',w.meaning||'']);
  });
  return '\\ufeff'+rows.map(r=>r.map(c=>'"'+String(c==null?'':c).replace(/"/g,'""')+'"').join(',')).join('\\r\\n')+'\\r\\n';
}
function exportMarks(){
  if(!markCount()){toast('还没有标记任何单词');return;}
  const csv=markCSV();
  if(window.Android&&Android.exportText){Android.exportText('拾词-标记.csv',csv);return;}
  const blob=new Blob([csv],{type:'text/csv;charset=utf-8'});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(blob);a.download='拾词-标记.csv';a.click();
  setTimeout(()=>URL.revokeObjectURL(a.href),2000);
}'''
assert old_helpers in js, "mark helpers not found"
js = js.replace(old_helpers, new_helpers, 1)

# 弹窗：标记后显示原因输入框
old_markrow = '''${markOf(id)?action('mark','取消标记','tag-btn',`data-id="${esc(id)}" data-kind=""`):''}</div>'''
new_markrow = '''${markOf(id)?action('mark','取消标记','tag-btn',`data-id="${esc(id)}" data-kind=""`):''}</div>
    ${markOf(id)?`<label class="small muted" for="mark-note" style="display:block;margin-top:12px">标记原因（可选）</label><textarea id="mark-note" rows="2" placeholder="例如：释义存疑 / 例句看不懂 / 重点词">${esc(markNote(id))}</textarea>${action('save-mark-note','保存原因','outline',`data-id="${esc(id)}" style="width:100%"`)}`:''}'''
assert old_markrow in js, "mark row not found"
js = js.replace(old_markrow, new_markrow, 1)

# 动作分发
anchor = "else if(a==='mark'){setMark(b.dataset.id,b.dataset.kind);}"
assert anchor in js
js = js.replace(anchor, anchor + "\n else if(a==='save-mark-note'){const id=b.dataset.id;const el=$('#mark-note');const cur=markData(id);if(cur){cur.n=(el?el.value.trim():'');save();toast('原因已保存');}closeModal();showWord(id);render();}"
                            "\n else if(a==='export-marks'){exportMarks();}", 1)

# 我的页：导出标记
old_row = "${action('check-update',`<div><b>检查更新</b>"
new_row = ("${action('export-marks',`<div><b>导出标记</b><p>${markCount()} 个词，CSV（含原因）</p></div>${icon('download')}`,'setting')}"
           "${action('check-update',`<div><b>检查更新</b>")
assert old_row in js
js = js.replace(old_row, new_row, 1)

js_path.write_text(js, encoding="utf-8", newline="\n")
print("app.js: mark notes + export")
