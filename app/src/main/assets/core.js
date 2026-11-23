(function(root){
'use strict';
const DAY=86400000;
function dayKey(time=Date.now()){const d=new Date(time);return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;}
function fresh(){return {version:1,activeBook:'liuxiaoyan-cet6-2026',goal:20,progress:{},history:{},customBooks:[],edits:{},bookmarks:{},marks:{}};}
function key(book,id){return book+':'+id;}
function grade(previous,rating,now=Date.now()){
 const p=previous||{stage:0,interval:0,reps:0,lapses:0};
 if(!['again','hard','good'].includes(rating))throw Error('无效的复习评分');
 let interval,stage;
 if(rating==='again'){interval=10/1440;stage=0;}
 else if(rating==='hard'){interval=Math.max(1,Math.min(7,(p.interval||1)*1.2));stage=Math.max(1,p.stage||0);}
 else{stage=Math.min(8,(p.stage||0)+1);interval=[0,1,3,7,14,30,60,120,180][stage];}
 return {stage,interval,due:now+Math.round(interval*DAY),reps:(p.reps||0)+1,lapses:(p.lapses||0)+(rating==='again'?1:0),firstSeen:p.firstSeen||now,lastSeen:now};
}
function stats(state,book,now=Date.now()){
 const out={total:book.words.length,learned:0,mastered:0,due:0,newToday:0,today:0,starred:0};
 const today=dayKey(now);
 for(const w of book.words){let p=state.progress[key(book.id,w.id)];if(p){out.learned++;if(p.stage>=4)out.mastered++;if(p.due<=now)out.due++;if(dayKey(p.firstSeen)===today)out.newToday++;}if(state.bookmarks[key(book.id,w.id)])out.starred++;}
 out.today=Object.keys(state.history[today]||{}).filter(k=>k.startsWith(book.id+':')).length;
 return out;
}
function inScope(word,scope={}){return (!scope.unit||word.unit===Number(scope.unit))&&(!scope.lesson||word.lesson===Number(scope.lesson))&&(!scope.groupId||word.groupId===scope.groupId);}
function queue(state,book,mode='mixed',now=Date.now(),scope=null){
 const dailyNew=stats(state,book,now).newToday;
 if(scope)book={...book,words:book.words.filter(w=>inScope(w,scope))};
 const due=book.words.filter(w=>{const p=state.progress[key(book.id,w.id)];return p&&p.due<=now;}).sort((a,b)=>state.progress[key(book.id,a.id)].due-state.progress[key(book.id,b.id)].due);
 const freshWords=book.words.filter(w=>!state.progress[key(book.id,w.id)]);
 if(mode==='starred')return book.words.filter(w=>state.bookmarks[key(book.id,w.id)]).map(w=>w.id);
 if(mode==='spell')return book.words.filter(w=>state.progress[key(book.id,w.id)]&&w.meaning).slice().sort((a,b)=>(state.progress[key(book.id,a.id)].stage||0)-(state.progress[key(book.id,b.id)].stage||0)).slice(0,20).map(w=>w.id);
 if(mode==='review')return due.map(w=>w.id);
 return [...due,...freshWords.slice(0,Math.max(0,state.goal-dailyNew))].map(w=>w.id);
}
function streak(history,now=Date.now()){
 let d=new Date(now);d.setHours(12,0,0,0);let total=0;
 if(!Object.keys(history[dayKey(d.getTime())]||{}).length)d.setDate(d.getDate()-1);
 while(Object.keys(history[dayKey(d.getTime())]||{}).length){total++;d.setDate(d.getDate()-1);}return total;
}
function csv(text){
 let rows=[],row=[],cell='',quote=false;
 for(let i=0;i<text.length;i++){const c=text[i];if(c==='"'){if(quote&&text[i+1]==='"'){cell+='"';i++;}else quote=!quote;}else if((c===','||c==='\t')&&!quote){row.push(cell);cell='';}else if((c==='\n'||c==='\r')&&!quote){if(c==='\r'&&text[i+1]==='\n')i++;row.push(cell);if(row.some(x=>x.trim()))rows.push(row);row=[];cell='';}else cell+=c;}
 if(quote)throw Error('CSV 引号未闭合');row.push(cell);if(row.some(x=>x.trim()))rows.push(row);return rows;
}
function importWords(text){
 text=text.replace(/^\uFEFF/,'').trim();let title='我的单词书',list;
 if(text[0]==='{'||text[0]==='['){let data=JSON.parse(text);list=Array.isArray(data)?data:data.words;title=String(data.title||title);}
 else{let rows=csv(text);if(rows[0]&&/^(word|单词|英文)$/i.test(rows[0][0].trim()))rows.shift();list=rows.map(r=>({word:r[0],meaning:r[1]}));}
 if(!Array.isArray(list)||!list.length)throw Error('词表为空。请提供 word 和 meaning 两列。');
 if(list.length>30000)throw Error('单本词表最多导入 30,000 条');
 let seen=new Set(),words=[];
 for(const item of list){if(!item||typeof item.word!=='string'||typeof item.meaning!=='string')throw Error('每条词目都需要 word（单词）和 meaning（释义）');const word=item.word.trim(),meaning=item.meaning.trim();if(!word||word.length>100||!meaning||meaning.length>3000)throw Error('单词或释义为空、过长，请检查词表');const id=word.toLowerCase();if(seen.has(id))continue;seen.add(id);words.push({id,word,meaning,section:'custom'});}
 return {id:'custom-'+Date.now()+'-'+Math.random().toString(36).slice(2,6),title:title.slice(0,100),subtitle:'我导入的词表',words};
}
function validBackup(data){
 if(!data||data.app!=='shici'||data.version!==1||!data.state)throw Error('这不是有效的拾词备份');
 const s=data.state;if(!s.progress||Array.isArray(s.progress)||typeof s.progress!=='object'||!s.history||typeof s.history!=='object'||!Array.isArray(s.customBooks))throw Error('备份内容不完整');
 for(const p of Object.values(s.progress))if(!p||!Number.isFinite(p.due)||!Number.isFinite(p.stage)||p.stage<0||p.stage>8||!Number.isFinite(p.firstSeen))throw Error('备份中的复习记录无效');
 for(const b of s.customBooks){if(!b||typeof b.id!=='string'||typeof b.title!=='string'||!Array.isArray(b.words))throw Error('备份中的词书无效');for(const w of b.words)if(!w||typeof w.id!=='string'||typeof w.word!=='string'||typeof w.meaning!=='string')throw Error('备份中的词目无效');}
 return Object.assign(fresh(),s,{goal:Math.max(1,Math.min(500,Number(s.goal)||20))});
}
function spellings(word){
 const pieces=word.toLowerCase().split('/'),base=pieces[0],out=[];
 for(const piece of pieces){const full=piece.startsWith('-')?base.slice(0,-(piece.length-1))+piece.slice(1):piece;out.push(full.replace(/[()]/g,''));out.push(full.replace(/\([^)]*\)/g,''));}
 return [...new Set(out.map(s=>s.trim()).filter(Boolean))];
}
const api={DAY,dayKey,fresh,key,grade,stats,queue,inScope,streak,csv,importWords,validBackup,spellings};
if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.StudyCore=api;
})(typeof window!=='undefined'?window:globalThis);
