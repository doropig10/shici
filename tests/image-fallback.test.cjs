const {chromium}=require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const assets=path.resolve('app/src/main/assets');
(async()=>{
 const server=http.createServer((req,res)=>{
  const target=path.resolve(assets,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));
  if(!target.startsWith(assets+path.sep)){res.writeHead(404).end();return;}
  fs.readFile(target,(error,data)=>{if(error){res.writeHead(404).end();return;}res.setHeader('Content-Type',target.endsWith('.js')?'application/javascript':target.endsWith('.css')?'text/css':'text/html');res.end(data);});
 });
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true,args:['--disable-gpu']});
 try{
  const page=await browser.newPage({viewport:{width:390,height:844}}),calls=[],errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.exposeFunction('nativeImageRequest',async(asset,token)=>{
   calls.push(asset);await new Promise(resolve=>setTimeout(resolve,100));
   const file=path.resolve('tmp/image-fallback-fixtures',asset.replace(/\.webp$/,'.png'));
   return fs.existsSync(file)?{token,data:'data:image/png;base64,'+fs.readFileSync(file).toString('base64'),error:''}:{token,data:'',error:'READ'};
  });
  await page.addInitScript(()=>{
   let saved='';window.Android={loadState:()=>saved,saveState:s=>{saved=s;return true},speak:()=>{},requestImage:(asset,token)=>window.nativeImageRequest(asset,token).then(r=>window.receiveNativeImage(r.token,r.data,r.error))};
  });
  // Every normal image fails, reproducing the user's broken-image symptom.
  await page.route('**/*.webp',route=>route.abort('failed'));
  await page.goto(`http://127.0.0.1:${server.address().port}/index.html`);
  await page.getByRole('button',{name:'词库',exact:true}).click();await page.getByLabel('搜索词库').fill('terror');
  await page.locator('.word-row').filter({has:page.locator('b',{hasText:/^terror$/})}).click();
  await page.waitForFunction(()=>document.querySelector('.scan-card')?.naturalWidth===466);
  assert.ok((await page.locator('.scan-card').getAttribute('src')).startsWith('data:image/png;base64,'));
  assert.equal(await page.locator('.image-status').count(),0);
  await page.screenshot({path:'output/screenshots/terror-fallback.png'});
  await page.getByRole('button',{name:'放大完整词条',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('.card-zoom img')?.naturalWidth===466);
  await page.getByRole('button',{name:'关闭放大',exact:true}).click();
  await page.locator('.word-row').filter({has:page.locator('b',{hasText:/^terror$/})}).click();
  await page.getByRole('button',{name:'查看原书上下文'}).click();
  await page.waitForFunction(()=>document.querySelector('.reader img')?.naturalWidth>0);
  // An image removed during native decoding must never replace a newer image.
  await page.evaluate(()=>{const old=document.createElement('img');old.src='cards/terror.webp';document.body.appendChild(old);old.dispatchEvent(new Event('error'));old.remove();});
  await page.evaluate(()=>{const img=document.createElement('img');img.id='missing-image';img.src='cards/missing.webp';document.body.appendChild(img);});
  await page.waitForFunction(()=>document.querySelector('#missing-image')?.nextElementSibling?.textContent.includes('READ'));
  const before=calls.length;await page.evaluate(()=>{const img=document.createElement('img');img.src='../secret.webp';document.body.appendChild(img);img.dispatchEvent(new Event('error'));});
  await page.waitForTimeout(250);assert.equal(calls.length,before);
  assert.ok(calls.filter(p=>p==='cards/terror.webp').length>=3);assert.ok(calls.includes('book/020.webp'));
  assert.deepEqual(errors,[]);
  console.log('Forced image-failure recovery passed: terror detail, zoom, original page, stale callback, missing resource, path rejection. Native Android execution still requires device verification.');
 }finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(e=>{console.error(e);process.exit(1)});
