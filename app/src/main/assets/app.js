'use strict';
const C=StudyCore, $=s=>document.querySelector(s), esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const icons={book:'M3 4c4-1 7 0 9 2 2-2 5-3 9-2v15c-4-1-7 0-9 2-2-2-5-3-9-2z M12 6v15',home:'M3 10l9-7 9 7v10H3z M9 20v-7h6v7',list:'M8 5h13M8 12h13M8 19h13M3 5h.1M3 12h.1M3 19h.1',settings:'M4 6h16M4 12h16M4 18h16M8 3v6M16 9v6M10 15v6',arrow:'M4 12h16M14 6l6 6-6 6',back:'M15 5l-7 7 7 7',close:'M6 6l12 12M6 18L18 6',sound:'M4 9v6h4l5 4V5L8 9z M17 8c3 2 3 6 0 8M19 4c6 4 6 12 0 16',star:'M12 3l2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9z',search:'M20 20l-5-5M17 10a7 7 0 1 1-14 0 7 7 0 0 1 14 0',check:'M5 12l4 4L19 6',repeat:'M4 8h13l-3-3M20 16H7l3 3M4 8v7M20 16V9',pen:'M4 20l4-1L20 7l-4-4L4 15zM13 6l4 4',plus:'M12 4v16M4 12h16',download:'M12 3v12M7 10l5 5 5-5M4 16v5h16v-5',shield:'M12 3l8 3v6c0 5-8 9-8 9s-8-4-8-9V6zM8 12l3 3 5-6',sun:'M12 8a4 4 0 1 1 0 8 4 4 0 0 1 0-8M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1 1M18 18l1 1M5 19l1-1M18 6l1-1'};
const icon=name=>`<svg viewBox="0 0 24 24" aria-hidden="true"><path d="${icons[name]||icons.book}"/></svg>`;
const action=(a,label,cls='',extra='')=>`<button class="${cls}" data-act="${a}" ${extra}>${label}</button>`;
let state,view='today',filter='all',query='',limit=60,session=null,revealed=false,readerPage=10,readerReturn='books',readerScale=1,modalWord=null,filePurpose=false,spellResult=null,cachedBook=null,cachedWords=null;
try{const raw=window.Android?Android.loadState():localStorage.getItem('shici-state');state=raw?Object.assign(C.fresh(),JSON.parse(raw)):C.fresh();}catch(e){state=C.fresh();setTimeout(()=>toast('学习记录未能读取，请从备份恢复'),300);}
function books(){return [BOOK_DATA,...state.customBooks];}
function book(){return books().find(b=>b.id===state.activeBook)||BOOK_DATA;}
function word(id){const b=book();if(cachedBook!==b){cachedBook=b;cachedWords=new Map(b.words.map(w=>[w.id,w]));}const w=cachedWords.get(id);return w?Object.assign({},w,state.edits[C.key(b.id,id)]||{}):null;}
function save(){try{const data=JSON.stringify(state);if(window.Android){if(!Android.saveState(data))throw Error();}else localStorage.setItem('shici-state',data);return true;}catch(e){toast('存储失败，请先导出备份，避免丢失进度');return false;}}
function toast(message){$('#toast').textContent=message;$('#toast').classList.add('show');clearTimeout(toast.timer);toast.timer=setTimeout(()=>$('#toast').classList.remove('show'),3300);}
function shell(content,tab=view){return `<main class="shell">${content}</main>${nav(tab)}`;}
function nav(tab){return `<nav aria-label="主要导航">${[['today','home','今日'],['words','list','词库'],['books','book','书架'],['settings','settings','我的']].map(([id,i,label])=>action('nav',icon(i)+label,id===tab?'active':'',`data-view="${id}" aria-label="${label}"`)).join('')}</nav>`;}
function head(){return `<header><div><div class="brand"><span class="logo">${icon('book')}</span>拾词</div></div><div class="date">${new Date().toLocaleDateString('zh-CN',{month:'long',day:'numeric',weekday:'short'})}</div></header>`;}
function render(){
 try{let html=view==='today'?today():view==='words'?wordList():view==='books'?shelf():view==='settings'?settings():view==='study'?study():view==='finish'?finish():today();$('#app').innerHTML=(view==='study'||view==='finish')?`<main class="shell">${html}</main>`:shell(html);}
 catch(e){$('#app').innerHTML='<div class="error-box">页面未能加载。请重新打开应用；已有学习记录保存在本机。</div>';console.error(e);}
}
function today(){const b=book(),s=C.stats(state,b),remaining=Math.max(0,state.goal-s.newToday),streak=C.streak(state.history);return `${head()}<div class="greeting">ONE WORD AT A TIME</div><h1>每天拾起一点，<br>让单词留在记忆里。</h1><div class="hero"><div class="eyebrow">正在学习 · MY WORDBOOK</div><h2>${esc(b.title)}</h2><p class="sub">${esc(b.subtitle)}</p><div class="pill">${icon('shield')} 只学我选的词书</div><div class="book-art" aria-hidden="true"><span>拾<br>词</span><small>KEEP GROWING</small></div></div><div class="metrics"><div class="metric"><strong>${remaining}</strong><span>今日待学新词</span></div><div class="metric"><strong>${s.due}</strong><span>到期复习</span></div><div class="metric"><strong>${streak}</strong><span>连续学习 / 天</span></div></div>${action('start',`开始今日学习 ${icon('arrow')}`,'primary')}<div class="section-title"><h2>我的学习节奏</h2><span class="small muted">今天已练 ${s.today} 词</span></div><div class="progress-card"><div class="row"><span class="small">词书进度</span><span class="small"><b>${s.learned}</b> <span class="muted">/ ${s.total}</span></span></div><div class="progress"><i style="width:${s.total?100*s.learned/s.total:0}%"></i></div><div class="row small muted"><span>稳稳记住 ${s.mastered} 个词</span><span>${s.total?(100*s.learned/s.total).toFixed(1):0}%</span></div>${week()}</div><div class="mini-grid">${action('review',`${icon('repeat')}<b>温故知新</b><span>${s.due?`${s.due} 个单词等你复习`:'到期单词会在这里出现'}</span>`,'mini')}${action('spell',`${icon('pen')}<b>拼写自测</b><span>把记住的词拼出来</span>`,'mini')}</div><p class="footer-note">没有广告，没有陌生词库。只有你的书，和每天的一点进步。</p>`;}
function week(){let now=new Date();return `<div class="week">${Array.from({length:7},(_,i)=>{let d=new Date(now);d.setDate(d.getDate()-6+i);let done=Object.keys(state.history[C.dayKey(d.getTime())]||{}).length;return `<div class="day ${done?'done':''} ${i===6?'current':''}">${['日','一','二','三','四','五','六'][d.getDay()]}<b>${done?'✓':d.getDate()}</b></div>`;}).join('')}</div>`;}
function status(w){const p=state.progress[C.key(book().id,w.id)];return !p?['未学','']:p.stage>=4?['已巩固','mastered']:['学习中','learned'];}
function libraryScope(){return book().structure?(state.libraryScopes?.[book().id]||{}):{};}
function setScope(scope){state.libraryScopes=state.libraryScopes||{};state.libraryScopes[book().id]=scope;filter='all';limit=(scope&&scope.unit)?300:60;save();}
function scopeWords(){return book().words.filter(w=>C.inScope(w,libraryScope()));}
function groupTitle(g){return (g.number?'词以群记 '+g.number+' · ':'')+g.title;}
function chapterLabel(w){const g=book().structure?.groups.find(g=>g.id===w.groupId);return w.unit?`Unit ${w.unit} · Lesson ${w.lesson}${g?' · '+(g.number?'词以群记 '+g.number:'词群待核对'):''}`:'';}
function scopeLabel(scope){const g=book().structure?.groups.find(g=>g.id===scope.groupId);return g?`Unit ${g.unit} · Lesson ${g.lesson} · ${g.number?'词群 '+g.number:'待核对词群'}`:`Unit ${scope.unit}${scope.lesson?' · Lesson '+scope.lesson:''}`;}
function chapterPicker(){
 const b=book(),structure=b.structure;if(!structure)return '';
 const scope=libraryScope(),unit=structure.units.find(u=>u.number===Number(scope.unit)),groups=structure.groups.filter(g=>g.unit===unit?.number&&(!scope.lesson||g.lesson===Number(scope.lesson)));
 const option=(value,label,selected)=>`<option value="${esc(value)}" ${String(value)===String(selected)?'selected':''}>${esc(label)}</option>`;
 const count=s=>b.words.filter(w=>C.inScope(w,s)).length;
 return `<section class="chapter-picker" aria-label="章节分类"><div class="row"><h2>按讲义章节</h2>${scope.unit?action('clear-scope','查看全部','chapter-reset'):''}</div><p class="sub">Unit → Lesson → 词群</p><div class="chapter-grid"><label>单元 Unit<select id="scope-unit" aria-label="选择 Unit">${option('','全部 Unit',scope.unit)}${structure.units.map(u=>option(u.number,`Unit ${u.number} · ${u.section==='core'?'核心':'基础'}（${count({unit:u.number})}）`,scope.unit)).join('')}</select></label><label>课程 Lesson<select id="scope-lesson" aria-label="选择 Lesson" ${unit?'':'disabled'}>${option('','全部 Lesson',scope.lesson)}${(unit?.pages||[]).map((_,i)=>option(i+1,`Lesson ${i+1}（${count({unit:unit.number,lesson:i+1})}）`,scope.lesson)).join('')}</select></label><label class="group-select">词以群记<select id="scope-group" aria-label="选择词以群记" ${groups.length?'':'disabled'}>${option('',unit?.section==='basic'?'基础词按 Lesson 编排':'全部词群',scope.groupId)}${groups.map(g=>option(g.id,groupTitle(g)+`（${count({groupId:g.id})}）`,scope.groupId)).join('')}</select></label></div>${scope.unit?`<p class="scope-caption">${esc(scopeLabel(scope))} · ${scopeWords().length} 个词卡</p>${action('study-scope','学习当前范围 '+icon('arrow'),'secondary',scopeWords().length?'':'disabled')}<p class="scope-hint">仅学习所选章节；到期复习优先，新词仍计入每日目标。</p>`:''}${unit?.number===5||unit?.number===9||unit?.number===10?'<p class="scope-hint">原 PDF 部分书页缺失，数量为当前已收录词卡；缺少标题的续页标为“词群待核对”。</p>':''}</section>`;
}
function filteredWords(){return scopeWords().filter(original=>{const w=word(original.id),p=state.progress[C.key(book().id,w.id)];return (!query||(w.word+' '+w.meaning).toLowerCase().includes(query.toLowerCase()))&&(filter==='all'||filter==='new'&&!p||filter==='learned'&&!!p||filter==='starred'&&state.bookmarks[C.key(book().id,w.id)]||filter==='marked'&&(state.marks||{})[C.key(book().id,w.id)]||(filter==='good'||filter==='hard'||filter==='again')&&p&&p.last===filter||filter==='core'&&w.section==='core'||filter==='basic'&&w.section==='basic');});}
function listRows(){const rows=filteredWords();return `<div class="row small muted" style="margin:3px 0 13px"><span>共 ${rows.length} 个单词</span><span>按讲义顺序</span></div><div class="word-list">${rows.slice(0,limit).map(w=>{const [label,cls]=status(w);const mk=markOf(w.id),pp=state.progress[C.key(book().id,w.id)],ln=pp&&pp.last?ratingName(pp.last):'';return action('detail',`<div><b>${esc(w.word)}</b>${mk?`<span class="mark-tag ${mk}">${mk==='special'?'重点':'待核对'}</span>`:''}<p>${esc(w.meaning)}</p></div><span class="status ${cls}">${label}</span>${ln?`<span class="rec-tag ${pp.last}">${ln}</span>`:''}`,'word-row',`data-id="${esc(w.id)}"`);}).join('')||'<div class="empty">这里还没有单词。<br>试试其他分类或搜索词。</div>'}</div>${rows.length>limit?action('more','再看 '+Math.min(60,rows.length-limit)+' 个单词','outline','style="width:100%;margin-top:15px"'):''}`;}
function wordList(){return `${head()}<h1>我的词库</h1><p class="sub">${esc(book().title)} · 每个词都标了 Unit / Lesson</p>${chapterPicker()}<div class="search">${icon('search')}<input id="search" value="${esc(query)}" placeholder="搜索英文或书中释义" aria-label="搜索词库" autocomplete="off"></div><div class="chips">${[['all','全部'],['new','未学'],['learned','已学'],['starred','收藏'],['marked','标记'],['good','记得'],['hard','模糊'],['again','忘记']].map(([id,label])=>action('filter',label,`chip ${filter===id?'selected':''}`,`data-filter="${id}"`)).join('')}</div><div id="list-results">${listRows()}</div>`;}
function shelf(){return `${head()}<h1>只属于你的书架</h1><p class="sub">从你提供的单词书开始，慢慢积累。</p>${books().map(b=>`<div class="book-item ${book().id===b.id?'active':''}"><div class="row-start"><div class="book-icon">${icon('book')}</div><div><div class="book-title">${esc(b.title)}</div><p class="sub">${esc(b.subtitle)}<br>${b.words.length.toLocaleString()} 个词卡 ${book().id===b.id?'· 正在学习':''}</p></div></div><div class="book-actions">${action('switch-book',book().id===b.id?'继续学习':'学习这本书','secondary',`data-book="${esc(b.id)}"`)}</div>${b.pendingCount?`<p class="sub" style="font-size:11px;margin-top:14px">扫描词书已生成 ${b.words.length.toLocaleString()} 张词卡；另有 ${b.pendingCount} 条索引未匹配正文，暂未加入学习。词目可对照原文修改。</p>`:''}</div>`).join('')}${action('import',`${icon('plus')} 导入我的词表`,'outline','style="width:100%;padding:18px"')}<div class="info">支持你整理的 JSON / CSV / TSV 词表，包含英文和中文释义。词条来自讲义文本，可直接导入或修改。</div><div class="setting-group">${action('template',`<div><b>查看词表格式</b><p>便于导入你下一本单词书</p></div>${icon('arrow')}`,'setting')}</div>`;}
function setGoal(n){const v=Math.round(Number(n));state.goal=Number.isFinite(v)?Math.min(500,Math.max(1,v)):20;save();render();toast('每日新词：'+state.goal+' 个');}
function appVersion(){try{return (window.Android&&Android.appVersion)?Android.appVersion():'';}catch(e){return '';}}
function appVersionName(){const v=appVersion();return v?v.split('|')[0]:'网页预览';}
function checkUpdate(){
  if(!window.Android||!Android.checkUpdate){toast('网页预览模式不支持检查更新');return;}
  toast('正在检查更新…');Android.checkUpdate();
}
function startUpdate(){
  const u=window.__update;
  if(!u){toast('没有可用的更新信息');return;}
  if(!window.Android||!Android.downloadUpdate){toast('当前环境不支持下载安装');return;}
  closeModal();toast('开始下载…');Android.downloadUpdate(u.apk,u.apkFallback||'',u.apkMirror||'',u.sha256||'');
}
window.receiveUpdate=function(raw,err){
  let list=[];try{list=JSON.parse(raw||'[]');}catch(e){list=[];}
  if(!Array.isArray(list))list=[];
  let info=null;
  for(const s of list){
    try{const it=JSON.parse(s);if(it&&it.versionCode&&(!info||Number(it.versionCode)>Number(info.versionCode)))info=it;}catch(e){}
  }
  if(!info){toast(err?('检查更新失败：'+err):'检查更新失败，请稍后再试');return;}
  const cur=appVersion(),curCode=Number((cur.split('|')[1]||'0'));
  if(Number(info.versionCode)<=curCode){toast('已是最新版本 '+appVersionName());return;}
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
function voiceInfo(){
  if(!window.Android||!Android.listVoices)return null;
  try{return JSON.parse(Android.listVoices());}catch(e){return null;}
}
function shortVoice(n){
  const p=String(n||'').split('/');
  return p[p.length-1]||'跟随系统';
}
function voiceLabel(v){
  const raw=String((v&&v.name)||'').toLowerCase();
  let label='音色';
  if(raw.includes('female'))label='女声';
  else if(raw.includes('male'))label='男声';
  const m=raw.match(/(?:female|male)_?(\d+)/);
  if(m)label+=' '+m[1];
  return label;
}
function currentVoiceLabel(){
  const info=voiceInfo();
  if(!info||!info.current)return '跟随系统';
  return voiceLabel({name:info.current});
}
function showVoices(){
  const info=voiceInfo();
  if(!info){toast('当前环境不支持选择音色');return;}
  const cur=info.current||'';
  const list=(info.voices||[]).map(v=>{
    const on=v.name===cur;
    return `<button class="voice-row ${on?'on':''}" data-act="set-voice" data-name="${esc(v.name)}">`
      +`<div><b>${esc(voiceLabel(v))}</b><p>${esc(v.locale)} · ${v.network?'需联网':'本地'}${on?' · 当前':''}</p></div>`
      +`<span class="voice-mark">${on?'✓':''}</span></button>`;
  }).join('');
  showModal(`<h2>发音音色</h2><p class="sub">这些是手机语音引擎里的英文音色，选一个试试；带「需联网」的通常更自然。</p>`
    +`<div class="voice-list">${list||'<p class="sub">没有找到英文音色，请先在系统设置里安装英语语音包</p>'}</div>`
    +`<div class="modal-footer">${action('close-modal','关闭','outline')}</div>`);
}
function settings(){const s=C.stats(state,book());return `${head()}<h1>按自己的节奏来</h1><p class="sub">已学 ${s.learned} 词 · 已巩固 ${s.mastered} 词</p><div class="setting-group"><div class="setting goal-setting"><div><b>每日新词</b><p>每日 1–500 个，到期复习优先</p></div><div class="goal-editor"><button class="goal-step" data-act="goal-step" data-step="-5" aria-label="减少五个">−</button><input id="goal" type="number" inputmode="numeric" min="1" max="500" step="1" value="${state.goal}" aria-label="每日新词数量"><button class="goal-step" data-act="goal-step" data-step="5" aria-label="增加五个">+</button></div></div><div class="goal-presets">${[5,10,20,30,50,100].map(n=>`<button class="chip ${n===state.goal?'selected':''}" data-act="goal-set" data-n="${n}">${n}</button>`).join('')}</div>${(window.Android&&Android.listVoices)?action('voices',`<div><b>发音音色</b><p>${esc(currentVoiceLabel())}</p></div>${icon('sound')}`,'setting'):''}${action('export-marks',`<div><b>导出标记</b><p>${markCount()} 个词，CSV（含原因）</p></div>${icon('download')}`,'setting')}${action('check-update',`<div><b>检查更新</b><p>当前 ${esc(appVersionName())}</p></div>${icon('download')}`,'setting')}${action('export',`<div><b>导出学习备份</b><p>保存词表、收藏、修改和复习进度</p></div>${icon('download')}`,'setting')}${action('restore',`<div><b>恢复学习备份</b><p>更换手机后，接着学</p></div>${icon('arrow')}`,'setting')}</div><div class="setting-group"><div class="setting"><div><b>离线使用 · 数据留在本机</b><p>只有「检查更新」会联网；不申请传感器或广告权限，学习数据只存本机。</p></div>${icon('shield')}</div><div class="setting"><div><b>发音来自手机语音引擎</b><p>需系统已安装英语语音包；没有时仍可背词。</p></div>${icon('sound')}</div></div><div class="info">新词答对后按 1、3、7、14、30 天逐渐拉长复习间隔。选择“忘记”会在本轮再次出现；选择“模糊”会更早复习。<br><br>卸载应用会删除本机学习数据，请提前导出备份。</div><p class="footer-note">拾词 · 只收录你的词书</p>`;}
function start(mode='mixed',scope=null){const ids=C.queue(state,book(),mode,Date.now(),scope);if(!ids.length){toast(scope?'所选范围暂无待学或到期词，或今日新词目标已达成':mode==='spell'?'先学习几个单词，再来拼写自测':mode==='review'?'暂时没有到期单词，晚些时候再来':'今日任务已完成，可以去词库自由浏览');return;}session={mode,scopeLabel:scope?scopeLabel(scope):'',queue:ids,total:ids.length,done:0,correct:0,started:Date.now(),back:[],peekPos:-1};revealed=false;spellResult=null;view='study';render();window.scrollTo(0,0);}
function current(){return session?word(session.queue[0]):null;}
function source(w){return chapterLabel(w)||'讲义词条';}
function say(w){return String(w).replace(/\(([^)]*)\)/g,'$1');}
function srcClass(s){
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
function entryHTML(w){
  const edited=state.edits[C.key(book().id,w.id)]?.meaning;
  if(edited)return `<div class="definition">${esc(edited)}</div>`;
  if(!w.entry||!w.entry.length)return `<div class="definition">${esc(w.meaning)}</div>`;
  const meta=[w.pos,w.phonetic&&('/'+w.phonetic+'/')].filter(Boolean).map(esc).join(' · ');
  return (meta?`<div class="entry-meta">${meta}</div>`:'')
    +`<div class="gloss">${esc(w.gloss||w.meaning)}</div>`
    +`<div class="blocks">${w.entry.map(blockBody).join('')}</div>`;
}
function answer(w){return entryHTML(w);}
function peekWord(){
  if(!session||session.peekPos<0)return null;
  const idx=session.back.length-1-session.peekPos;
  return idx>=0?word(session.back[idx]):null;
}
function goBack(){
  if(!session)return;
  if(!session.back.length){toast('\u8fd8\u6ca1\u6709\u4e0a\u4e00\u4e2a\u8bcd');return;}
  const max=session.back.length-1;
  if(session.peekPos>=max){toast('\u5df2\u7ecf\u662f\u7b2c\u4e00\u4e2a\u4e86');return;}
  session.peekPos=session.peekPos<0?0:session.peekPos+1;
  revealed=true;spellResult=null;render();window.scrollTo(0,0);
}
function goForward(){
  if(!session)return;
  session.peekPos=-1;
  revealed=false;render();window.scrollTo(0,0);
}
function study(){const peeking=!!(session&&session.peekPos>=0);const w=peeking?peekWord():current();if(!w)return finish();const starred=state.bookmarks[C.key(book().id,w.id)],spell=session.mode==='spell';return `<div class="study-top">${action('exit-study',icon('close'),'icon-btn','aria-label="退出本轮学习"')}<span class="small muted">${esc(session.scopeLabel||(spell?'拼写自测':'今日学习'))} · ${session.done} / ${Math.max(session.total,session.done+session.queue.length)}</span>${action('star',icon('star'),`icon-btn favorite ${starred?'on':''}`,`data-id="${esc(w.id)}" aria-label="${starred?'取消收藏':'收藏单词'}"`)}</div><div class="progress"><i style="width:${session.done/(session.done+session.queue.length)*100}%"></i></div><div class="study-nav">${spell?"":`${action('go-back',icon('back')+' 上一个','quiet',session.back.length?'':'disabled')}`}${peeking?action('go-forward','回到当前 '+icon('arrow'),'quiet'):''}</div><div class="study-card ${revealed?'revealed':''}"><div class="source-tag">${esc(source(w))}</div>${spell?`<div class="scan-label">请根据中文写出单词 · 可在词库核对或修改释义</div><div class="definition">${esc(w.meaning||'请先在词库补充这条释义')}</div><input class="spell-input" id="spelling" placeholder="输入英文" autocomplete="off" autocapitalize="off" spellcheck="false" aria-label="单词拼写" ${spellResult?'disabled':''}>${spellResult?`<p class="${spellResult.correct?'correct':'incorrect'}">${spellResult.correct?'拼对了 ✓':'正确拼写：'+esc(w.word)}</p>`:''}`:`<div class="word-line"><div class="word-large">${esc(w.word)}</div>${action('speak',icon('sound'),'sound',`data-word="${esc(say(w.word))}" aria-label="朗读单词"`)}</div>${revealed?answer(w):'<div class="hint">在心里想一想，它是什么意思？</div>'}`}</div>${peeking?'<p class="sub" style="text-align:center;margin:4px 0 0">回看中 · 不会改动学习进度</p>':spell?(spellResult?action('next-spell','下一个 '+icon('arrow'),'primary'):action('check-spell','检查拼写','primary')):revealed?`<div class="ratings">${action('rate','忘记<small>本轮再练</small>','again','data-rating="again"')}${action('rate','模糊<small>早点复习</small>','hard','data-rating="hard"')}${action('rate','记得<small>继续巩固</small>','good','data-rating="good"')}</div>`:action('reveal','展开完整词条','primary')}<p class="quiet" style="${peeking?'display:none':''}">${spell?'自测不改变复习间隔':'诚实地选择，才能安排合适的复习时间。'}</p>`;}
function rate(rating){const w=current();if(!w||!revealed)return;const k=C.key(book().id,w.id),old=state.progress[k];const prev=old?JSON.parse(JSON.stringify(old)):null;if(prev)delete prev.undo;const np=C.grade(old,rating);np.r={g:((old&&old.r&&old.r.g)||0)+(rating==='good'?1:0),h:((old&&old.r&&old.r.h)||0)+(rating==='hard'?1:0),a:((old&&old.r&&old.r.a)||0)+(rating==='again'?1:0)};np.last=rating;np.undo=prev;state.progress[k]=np;const today=C.dayKey();state.history[today]=state.history[today]||{};state.history[today][k]=true;if(!save())return;session.back.push(w.id);session.peekPos=-1;session.queue.shift();session.done++;if(rating==='again')session.queue.push(w.id);else session.correct++;revealed=false;spellResult=null;if(!session.queue.length)view='finish';render();window.scrollTo(0,0);}
function finish(){return `<div class="center"><div class="success-art">${icon('check')}</div><div class="greeting">A LITTLE BETTER, EVERY DAY</div><h1>今天的努力，<br>已经存进记忆里。</h1><p class="sub">${session?.mode==='spell'?'拼写自测':'本轮学习'}完成 ${session?.done||0} 次<br>不用一口气记住所有，坚持就好。</p><div class="metrics" style="margin-top:30px"><div class="metric"><strong>${session?.correct||0}</strong><span>${session?.mode==='spell'?'拼写正确':'成功回忆'}</span></div><div class="metric"><strong>${Math.max(1,Math.round((Date.now()-(session?.started||Date.now()))/60000))}</strong><span>专注 / 分钟</span></div><div class="metric"><strong>${C.streak(state.history)}</strong><span>连续 / 天</span></div></div>${action('finish-home','回到今日','primary')}</div>`;}
function showModal(content){document.querySelector('.modal-overlay')?.remove();const d=document.createElement('div');d.className='modal-overlay';d.innerHTML=`<section class="modal" role="dialog" aria-modal="true">${content}</section>`;document.body.appendChild(d);d.addEventListener('click',e=>{if(e.target===d)d.remove();});d.querySelector('button,input')?.focus();}
function closeModal(){document.querySelector('.modal-overlay')?.remove();modalWord=null;}
function markData(id){
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
  return '\ufeff'+rows.map(r=>r.map(c=>'"'+String(c==null?'':c).replace(/"/g,'""')+'"').join(',')).join('\r\n')+'\r\n';
}
function exportMarks(){
  if(!markCount()){toast('还没有标记任何单词');return;}
  const csv=markCSV();
  if(window.Android&&Android.exportText){Android.exportText('拾词-标记.csv',csv);return;}
  const blob=new Blob([csv],{type:'text/csv;charset=utf-8'});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(blob);a.download='拾词-标记.csv';a.click();
  setTimeout(()=>URL.revokeObjectURL(a.href),2000);
}
function recOf(id){
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
function showWord(id){modalWord=id;const w=word(id),starred=state.bookmarks[C.key(book().id,id)];showModal(`<div class="row"><span class="source-tag">${esc(source(w))}</span>${action('close-modal',icon('close'),'icon-btn','aria-label="关闭词条"')}</div><div class="row"><div class="word-large">${esc(w.word)}</div>${action('speak',icon('sound'),'sound',`data-word="${esc(say(w.word))}" aria-label="朗读"`)}</div>${answer(w)}${recordHTML(id)}<div class="mark-row">${action('mark','重点',`tag-btn ${markOf(id)==='special'?'on':''}`,`data-id="${esc(id)}" data-kind="special"`)}${action('mark','待核对',`tag-btn ${markOf(id)==='issue'?'on':''}`,`data-id="${esc(id)}" data-kind="issue"`)}${markOf(id)?action('mark','取消标记','tag-btn',`data-id="${esc(id)}" data-kind=""`):''}</div>
    ${markOf(id)?`<label class="small muted" for="mark-note" style="display:block;margin-top:12px">标记原因（可选）</label><textarea id="mark-note" rows="2" placeholder="例如：释义存疑 / 例句看不懂 / 重点词">${esc(markNote(id))}</textarea>${action('save-mark-note','保存原因','outline',`data-id="${esc(id)}" style="width:100%"`)}`:''}<div class="modal-footer">${action('star',starred?'已收藏 ★':'收藏单词 ☆','outline',`data-id="${esc(id)}"`)}${action('edit','修改词条','outline',`data-id="${esc(id)}"`)}</div>`);}
function editWord(id){modalWord=id;const w=word(id);showModal(`<h2>修改词条</h2><label for="edit-word">英文单词</label><input id="edit-word" value="${esc(w.word)}"><label for="edit-meaning">中文释义（用于搜索与拼写自测）</label><textarea id="edit-meaning">${esc(w.meaning)}</textarea><div class="modal-footer">${action('close-modal','取消','outline')}${action('save-edit','保存修改','secondary',`data-id="${esc(id)}"`)}</div>`);}
function speak(text){if(window.Android){Android.speak(text);return;}if('speechSynthesis' in window){const u=new SpeechSynthesisUtterance(text);u.lang='en-US';u.rate=.8;speechSynthesis.cancel();speechSynthesis.speak(u);}else toast('当前设备未提供英语语音');}
function chooseFile(backup){filePurpose=backup;if(window.Android){backup?Android.chooseBackup():Android.chooseWords();}else{$('#file-input').value='';$('#file-input').click();}}
function backup(){const text=JSON.stringify({app:'shici',version:1,exportedAt:new Date().toISOString(),state},null,2);if(window.Android){Android.exportBackup(text);return;}const url=URL.createObjectURL(new Blob([text],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='拾词-学习备份.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
window.receiveFile=function(text,isBackup){try{if(isBackup){const parsed=C.validBackup(JSON.parse(text));showModal(`<h2>恢复这份学习备份？</h2><p class="sub">将替换本机当前的学习记录、收藏和自建词表。建议先导出当前备份。</p><div class="modal-footer">${action('close-modal','取消','outline')}${action('confirm-restore','恢复备份','secondary')}</div>`);window.pendingRestore=parsed;}else{const b=C.importWords(text);state.customBooks.push(b);state.activeBook=b.id;save();view='books';render();toast(`已导入 ${b.words.length} 个单词`);}}catch(e){toast(e.message||'文件格式不正确');}};
$('#file-input').addEventListener('change',async e=>{const f=e.target.files[0];if(!f)return;if(f.size>20000000){toast('请选择小于 20 MB 的词表文件');return;}receiveFile(await f.text(),filePurpose);});
document.addEventListener('input',e=>{if(e.target.id==='search'){query=e.target.value;limit=60;$('#list-results').innerHTML=listRows();}});
document.addEventListener('change',e=>{if(['scope-unit','scope-lesson','scope-group'].includes(e.target.id)){const current=libraryScope(),v=e.target.value;if(e.target.id==='scope-unit')setScope({unit:v});else if(e.target.id==='scope-lesson')setScope({unit:current.unit,lesson:v});else setScope({...current,groupId:v});render();}else if(e.target.id==='goal'){setGoal(e.target.value);}});
document.addEventListener('keydown',e=>{if(e.key==='Enter'&&e.target.id==='spelling')checkSpell();if(e.key==='Escape')window.handleBack();});
function checkSpell(){if(spellResult||!current())return;const input=$('#spelling').value.trim().toLowerCase(),w=current();if(!input){toast('先输入你的答案');return;}spellResult={correct:C.spellings(w.word).includes(input)||input===w.word.toLowerCase()};render();}
document.addEventListener('click',e=>{const b=e.target.closest('[data-act]');if(!b)return;const a=b.dataset.act;
 if(a==='nav'){view=b.dataset.view;render();window.scrollTo(0,0);}
 else if(a==='start')start();else if(a==='review')start('review');else if(a==='spell')start('spell');
 else if(a==='study-scope')start('mixed',libraryScope());
 else if(a==='clear-scope'){setScope({});render();}
 else if(a==='filter'){filter=b.dataset.filter;limit=60;render();}
 else if(a==='goal-step'){setGoal(Number(state.goal)+Number(b.dataset.step));}
 else if(a==='goal-set'){setGoal(Number(b.dataset.n));}
 else if(a==='go-back'){goBack();}
 else if(a==='go-forward'){goForward();}
 else if(a==='check-update'){checkUpdate();}
 else if(a==='do-update'){startUpdate();}
 else if(a==='voices'){showVoices();}
 else if(a==='mark'){setMark(b.dataset.id,b.dataset.kind);}
 else if(a==='undo-rating'){undoRating(b.dataset.id);}
 else if(a==='clear-word'){clearWord(b.dataset.id);}
 else if(a==='save-mark-note'){const id=b.dataset.id;const el=$('#mark-note');const cur=markData(id);if(cur){cur.n=(el?el.value.trim():'');save();toast('原因已保存');}closeModal();showWord(id);render();}
 else if(a==='export-marks'){exportMarks();}
 else if(a==='set-voice'){if(window.Android&&Android.setVoice&&Android.setVoice(b.dataset.name)){toast('音色已切换');closeModal();render();}else{toast('切换失败，换个音色试试');}}
 else if(a==='more'){limit+=60;$('#list-results').innerHTML=listRows();}
 else if(a==='detail')showWord(b.dataset.id);
 else if(a==='close-modal')closeModal();
 else if(a==='speak')speak(b.dataset.word);
 else if(a==='reveal'){revealed=true;render();}
 else if(a==='rate')rate(b.dataset.rating);
 else if(a==='star'){const k=C.key(book().id,b.dataset.id);state.bookmarks[k]=!state.bookmarks[k];save();if(view==='study')render();else if(modalWord)showWord(b.dataset.id);}
 else if(a==='exit-study'){showModal(`<h2>先休息一下？</h2><p class="sub">已经评分的单词会保留进度，未完成的任务下次可以继续。</p><div class="modal-footer">${action('close-modal','接着学','outline')}${action('confirm-exit','回到今日','secondary')}</div>`);}
 else if(a==='confirm-exit'||a==='finish-home'){closeModal();session=null;view='today';render();}

 else if(a==='edit')editWord(b.dataset.id);
 else if(a==='save-edit'){const wordText=$('#edit-word').value.trim(),meaning=$('#edit-meaning').value.trim();if(!wordText||!meaning){toast('英文和释义都需要填写');return;}if(wordText.length>100||meaning.length>3000){toast('词条内容过长');return;}state.edits[C.key(book().id,b.dataset.id)]={word:wordText,meaning};save();showWord(b.dataset.id);}
 else if(a==='switch-book'){state.activeBook=b.dataset.book;query='';filter='all';limit=60;save();view='today';render();window.scrollTo(0,0);}
 else if(a==='import')chooseFile(false);else if(a==='export')backup();else if(a==='restore')chooseFile(true);
 else if(a==='confirm-restore'){if(window.pendingRestore){state=window.pendingRestore;delete window.pendingRestore;save();closeModal();view='today';render();toast('学习备份已恢复');}}
 else if(a==='template')showModal(`<h2>你的词表，可以这样写</h2><p class="sub">CSV / TSV：第一列英文，第二列中文释义，使用 UTF-8 编码。含逗号的释义需要用双引号包围。</p><pre style="white-space:pre-wrap;font-size:12px;background:#eeece5;padding:15px;border-radius:12px">word,meaning\neminent,杰出的；有名的\nprominent,突出的；重要的</pre><p class="sub">JSON 支持书名与词条：</p><pre style="white-space:pre-wrap;font-size:12px;background:#eeece5;padding:15px;border-radius:12px">${esc(JSON.stringify({title:'我的单词书',words:[{word:'eminent',meaning:'杰出的；有名的'}]},null,2))}</pre>${action('close-modal','明白了','primary')}`);
 else if(a==='check-spell')checkSpell();
 else if(a==='next-spell'){if(!spellResult)return;session.done++;if(spellResult.correct)session.correct++;session.queue.shift();spellResult=null;if(!session.queue.length)view='finish';render();}
});
window.handleBack=function(){if(document.querySelector('.modal-overlay')){closeModal();return true;}if(view==='reader'){view=readerReturn;render();return true;}if(view==='study'){document.querySelector('[data-act="exit-study"]').click();return true;}if(view!=='today'){view='today';render();return true;}return false;};
render();
