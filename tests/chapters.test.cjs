const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const C=require('../app/src/main/assets/core.js');
const scope={window:{}};vm.runInNewContext(fs.readFileSync('app/src/main/assets/book-data.js','utf8'),scope);
const book=scope.window.BOOK_DATA,find=id=>book.words.find(w=>w.id===id);
test('all words resolve to the original chapter hierarchy',()=>{
 assert.equal(book.structure.units.length,14);assert.equal(book.structure.units.reduce((n,u)=>n+u.pages.length,0),54);
 assert.equal(new Set(book.structure.groups.map(g=>g.id)).size,book.structure.groups.length);
 for(const w of book.words){const u=book.structure.units.find(u=>u.number===w.unit);assert.ok(u,w.id);assert.ok(w.lesson>=1&&w.lesson<=u.pages.length,w.id);if(w.section==='core'){const g=book.structure.groups.find(g=>g.id===w.groupId);assert.ok(g,w.id);assert.equal(g.unit,w.unit,w.id);assert.equal(g.lesson,w.lesson,w.id);}else assert.equal(w.groupId,undefined);}
});
test('same-page group and chapter boundaries preserve the book sections',()=>{
 assert.equal(find('ambition').groupId,'u1-g1');assert.equal(find('eminent').groupId,'u1-g2');
 assert.equal(find('voter').unit,2);assert.equal(find('attribute').unit,3);
 assert.equal(find('sense').unit,9);assert.equal(find('ashamed').unit,10);
 assert.equal(find('less').lesson,2);assert.equal(find('inspect').lesson,3);
 assert.equal(find('stifle').groupId,'u5-unconfirmed');
});
test('scoped study shares progress and the whole-book daily new-word cap',()=>{
 const now=Date.now(),s=C.fresh();s.goal=5;
 const sample={id:'sample',words:[{id:'old',unit:2,lesson:1,groupId:'b'},{id:'review',unit:1,lesson:1,groupId:'a'},...Array.from({length:6},(_,i)=>({id:'new'+i,unit:1,lesson:1,groupId:'a'})),{id:'outside',unit:2,lesson:2,groupId:'c'}]};
 s.progress['sample:old']=C.grade(null,'good',now);s.progress['sample:review']={...C.grade(null,'good',now-C.DAY*2),due:now-1};
 const ids=C.queue(s,sample,'mixed',now,{unit:1,lesson:1,groupId:'a'});
 assert.deepEqual(ids,['review','new0','new1','new2','new3']);assert.deepEqual(C.queue(s,sample,'review',now,{unit:2}),[]);
 assert.equal(C.queue(s,sample,'mixed',now,{unit:99}).length,0);assert.ok(!ids.includes('outside'));
});
