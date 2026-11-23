const assert=require('node:assert/strict');
const test=require('node:test');
const C=require('../app/src/main/assets/core.js');
const fs=require('node:fs');
const vm=require('node:vm');
test('a new correct word is due in one day; failure resets interval',()=>{
 const now=1700000000000,p=C.grade(null,'good',now);assert.equal(p.due,now+C.DAY);assert.equal(p.stage,1);
 const q=C.grade(p,'good',now+C.DAY);assert.equal(q.interval,3);
 const r=C.grade(q,'again',now+2*C.DAY);assert.equal(r.stage,0);assert.equal(r.lapses,1);assert.equal(r.due,now+2*C.DAY+600000);assert.equal(r.firstSeen,now);
});
test('due reviews are first; daily new-word limit persists across sessions',()=>{
 const s=C.fresh(),b={id:'book',words:['a','b','c','d'].map(id=>({id,word:id,meaning:id}))},now=Date.now();s.goal=2;
 s.progress['book:a']={...C.grade(null,'good',now-2*C.DAY),due:now-1000};
 s.progress['book:b']=C.grade(null,'good',now);
 assert.deepEqual(C.queue(s,b,'mixed',now),['a','c']);assert.deepEqual(C.queue(s,b,'review',now),['a']);
 assert.deepEqual(C.queue(s,{...b,id:'other'},'mixed',now),['a','b']);
});
test('CSV quoted commas, CRLF, unicode, duplicate words and missing fields',()=>{
 const b=C.importWords('word,meaning\r\neminent,"杰出的,有名的"\r\neminent,重复\r\ncomment,评论');assert.equal(b.words.length,2);assert.equal(b.words[0].meaning,'杰出的,有名的');
 assert.throws(()=>C.importWords('[{"word":"missing"}]'));
 assert.throws(()=>C.importWords('word,meaning\na,"unfinished'));
});
test('backup rejects malformed progress and round-trips valid data',()=>{
 const state=C.fresh();state.progress['book:a']=C.grade(null,'hard');const b={app:'shici',version:1,state};assert.deepEqual(C.validBackup(JSON.parse(JSON.stringify(b))),state);
 assert.throws(()=>C.validBackup({app:'other',version:1,state}));state.progress['book:a'].due='bad';assert.throws(()=>C.validBackup(b));
});
test('spelling accepts the variants actually printed in the wordbook',()=>{
 assert.deepEqual(C.spellings('realise/-ize'),['realise','realize']);assert.deepEqual(C.spellings('vapo(u)r'),['vapour','vapor']);assert.deepEqual(C.spellings('cosy/cozy'),['cosy','cozy']);
});
test('bundled cards have unique words and existing source assets; no external vocabulary',()=>{
 const sandbox={window:{}};vm.runInNewContext(fs.readFileSync('app/src/main/assets/book-data.js','utf8'),sandbox);const b=sandbox.window.BOOK_DATA;
 assert.ok(b.words.length>5000);assert.equal(new Set(b.words.map(w=>w.id)).size,b.words.length);
 for(const w of b.words){assert.ok(w.word&&!w.word.endsWith('/'),w.word);assert.ok(w.page>=10&&w.page<=315);assert.ok(fs.existsSync('app/src/main/assets/'+w.card),w.id);assert.ok(fs.existsSync('app/src/main/assets/book/'+String(w.page).padStart(3,'0')+'.webp'));assert.ok(w.indexPage>=316&&w.indexPage<=336);}
});
