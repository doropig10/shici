const {chromium}=require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const path=require('node:path');
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true,args:['--disable-gpu']});
 try{
  const page=await browser.newPage({viewport:{width:390,height:844}}),errors=[],network=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))network.push(r.url());});
  // Android persists progress in SharedPreferences, independent of the page origin.
  await page.addInitScript(()=>{let saved='';window.Android={loadState:()=>saved,saveState:s=>{saved=s;return true},speak:()=>{}};});
  await page.goto(pathToFileURL(path.resolve('app/src/main/assets/index.html')).href);
  await page.getByRole('button',{name:'开始今日学习'}).click();
  await page.getByRole('button',{name:'展开完整词条',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('.scan-card')?.naturalWidth>0);
  await page.getByRole('button',{name:'放大完整词条',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('.card-zoom img')?.naturalWidth>0);
  await page.getByRole('button',{name:'关闭放大',exact:true}).click();
  await page.getByRole('button',{name:'查看原书上下文',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('.reader img')?.naturalWidth>0);
  // Exercise core, stitched, basic and full-page images with all networking disabled.
  await page.context().setOffline(true);
  const samples=await page.evaluate(async()=>{
   const paths=['cards/ambition.webp','cards/remark.webp',BOOK_DATA.words.find(w=>w.section==='basic').card,'book/222.webp','book/338.webp'];
   return Promise.all(paths.map(src=>new Promise(resolve=>{const im=new Image();im.onload=()=>resolve({src,ok:im.naturalWidth>0});im.onerror=()=>resolve({src,ok:false});im.src=src;})));
  });
  assert.ok(samples.every(s=>s.ok),JSON.stringify(samples));assert.deepEqual(errors,[]);assert.deepEqual(network,[]);
  await page.screenshot({path:'output/screenshots/offline-reader.png'});
  console.log('File-origin image check passed: full entry, zoom, original reader, basic cards, stitched cards and offline pages. Android WebView still needs device verification.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
