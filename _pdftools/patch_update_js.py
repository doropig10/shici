from pathlib import Path

p = Path(r"E:\单词\app\src\main\assets\app.js")
s = p.read_text(encoding="utf-8")

def rep(old, new):
    global s
    assert old in s, f"not found: {old[:60]}"
    s = s.replace(old, new, 1)

# 版本信息 + 更新入口
rep("function settings(){const s=C.stats(state,book());",
    "function appVersion(){try{return (window.Android&&Android.appVersion)?Android.appVersion():'';}catch(e){return '';}}\n"
    "function appVersionName(){const v=appVersion();return v?v.split('|')[0]:'网页预览';}\n"
    "function settings(){const s=C.stats(state,book());")

rep("${action('export',`<div><b>导出学习备份</b>",
    "${action('check-update',`<div><b>检查更新</b><p>当前 ${esc(appVersionName())}</p></div>${icon('download')}`,'setting')}"
    "${action('export',`<div><b>导出学习备份</b>")

# 动作分发
anchor = "else if(a==='go-forward'){goForward();}"
assert anchor in s
s = s.replace(anchor, anchor + "\n else if(a==='check-update'){checkUpdate();}"
                            "\n else if(a==='do-update'){startUpdate();}", 1)

# 更新逻辑与原生回调
helpers = '''function checkUpdate(){
  if(!window.Android||!Android.checkUpdate){toast('网页预览模式不支持检查更新');return;}
  toast('正在检查更新…');Android.checkUpdate();
}
function startUpdate(){
  const u=window.__update;
  if(!u){toast('没有可用的更新信息');return;}
  if(!window.Android||!Android.downloadUpdate){toast('当前环境不支持下载安装');return;}
  closeModal();toast('开始下载…');Android.downloadUpdate(u.apk,u.sha256||'');
}
window.receiveUpdate=function(raw,err){
  if(err){toast('检查更新失败：'+err);return;}
  let info=null;try{info=JSON.parse(raw||'{}');}catch(e){toast('更新信息格式不对');return;}
  const cur=appVersion(),curCode=Number((cur.split('|')[1]||'0'));
  if(!info||!info.versionCode||Number(info.versionCode)<=curCode){toast('已是最新版本 '+appVersionName());return;}
  window.__update=info;
  showModal(`<h2>发现新版本 ${esc(info.versionName||'')}</h2><p class="sub">${esc(info.notes||'')}</p>`
    +`<p class="small muted">当前 ${esc(appVersionName())} · 新版本 ${esc(info.versionName||'')}${info.size?` · ${(info.size/1024).toFixed(0)} KB`:''}</p>`
    +`<div class="modal-footer">${action('close-modal','稍后','outline')}${action('do-update','下载并安装','primary')}</div>`);
};
window.receiveUpdateProgress=function(pct){
  const t=$('#toast');if(!t)return;
  t.textContent=pct>=0?('下载中 '+pct+'%'):'下载中…';
  t.classList.add('show');
};
window.receiveUpdateError=function(msg){toast('更新失败：'+msg);};
'''
if "function checkUpdate(){" not in s:
    s = s.replace("function settings(){", helpers + "function settings(){", 1)

p.write_text(s, encoding="utf-8", newline="\n")
print("app.js update UI added")
