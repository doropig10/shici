const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm');
const scope={window:{}};vm.runInNewContext(fs.readFileSync('app/src/main/assets/book-data.js','utf8'),scope);
const book=scope.window.BOOK_DATA,find=id=>book.words.find(w=>w.id===id);
function ocr(page){return JSON.parse(fs.readFileSync(`tmp/ocr-full/${String(page).padStart(3,'0')}.json`,'utf8').replace(/^\uFEFF/,''));}
function bottomOf(page,term,after){const p=ocr(page),lines=p.lines.filter(l=>l.text.includes(term)&&Math.min(...l.words.map(w=>w.y))/p.height>after);assert.ok(lines.length,term);return Math.max(...lines[0].words.map(w=>w.y+w.h))/p.height;}
test('all core cards use full entry regions with valid bounds',()=>{for(const w of book.words.filter(w=>w.section==='core')){assert.equal(w.fullEntry,true,w.id);assert.ok(w.cardRegions.length>=1&&w.cardRegions.length<=4);for(const r of w.cardRegions){assert.ok(r.top<r.bottom);assert.ok(r.top>=0&&r.bottom<=1);}}});
test('ambition retains the example and complete ambitious expansion',()=>{const w=find('ambition'),r=w.cardRegions[0];assert.ok(r.bottom>=bottomOf(10,'ambitious',.4));assert.ok(r.bottom-r.top>.15);});
test('remark joins the continuation in the right column',()=>{const w=find('remark');assert.equal(w.cardRegions.length,2);assert.equal(w.cardRegions[0].column,0);assert.equal(w.cardRegions[1].column,1);assert.equal(w.cardRegions[1].page,11);assert.ok(w.cardRegions[1].top>.25);assert.ok(w.cardRegions[1].bottom>=bottomOf(11,'remarkable',.3));});
test('eminent contains the mnemonic, example and complete eminence expansion',()=>{const w=find('eminent');assert.ok(w.cardRegions[0].bottom>=bottomOf(11,'eminence',.4));assert.ok(w.cardRegions[0].bottom-w.cardRegions[0].top>.21);});
