const {chromium}=require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true,args:['--disable-gpu']});
 const page=await browser.newPage({viewport:{width:390,height:844}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8765');await page.getByRole('button',{name:'词库',exact:true}).click();
 await page.getByLabel('选择 Unit').selectOption('1');await page.getByLabel('选择 Lesson').selectOption('1');await page.getByLabel('选择词以群记').selectOption('u1-g2');
 assert.ok((await page.locator('.word-row').first().textContent()).includes('eminent'));
 assert.equal(await page.locator('.word-row').filter({hasText:'ambition'}).count(),0);
 await page.getByLabel('搜索词库').fill('eminent');assert.equal(await page.locator('.word-row').count(),1);await page.getByLabel('搜索词库').fill('');
 await page.screenshot({path:'output/screenshots/chapters.png',fullPage:true});
 for(const width of [320,390,600]){await page.setViewportSize({width,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));}
 await page.getByRole('button',{name:'学习当前范围'}).click();assert.equal(await page.locator('.word-large').textContent(),'eminent');
 assert.ok((await page.locator('.study-top').textContent()).includes('词群 2'));
 await page.getByRole('button',{name:'展开完整词条',exact:true}).click();await page.getByRole('button',{name:'记得'}).click();
 const snapshot=await page.evaluate(()=>JSON.parse(localStorage.getItem('shici-state')));assert.equal(Object.keys(snapshot.progress).length,1);
 await page.reload();await page.getByRole('button',{name:'词库',exact:true}).click();assert.equal(await page.getByLabel('选择词以群记').inputValue(),'u1-g2');
 await page.getByLabel('选择 Lesson').selectOption('2');assert.equal(await page.getByLabel('选择词以群记').inputValue(),'');assert.equal(await page.getByLabel('选择词以群记').locator('option[value="u1-g2"]').count(),0);
 await page.getByLabel('选择 Unit').selectOption('11');assert.equal(await page.getByLabel('选择 Lesson').inputValue(),'');assert.ok(await page.getByLabel('选择词以群记').isDisabled());
 await page.getByLabel('选择 Lesson').selectOption('2');assert.ok(await page.locator('.word-row').count()>0);
 await page.getByLabel('选择 Unit').selectOption('5');await page.getByLabel('选择 Lesson').selectOption('2');assert.equal(await page.locator('.word-row').count(),0);assert.ok(await page.getByRole('button',{name:'学习当前范围'}).isDisabled());
 await page.getByRole('button',{name:'查看全部',exact:true}).click();assert.equal(await page.getByLabel('选择 Unit').inputValue(),'');assert.equal(await page.locator('.word-row').count(),60);
 assert.deepEqual(await page.evaluate(()=>JSON.parse(localStorage.getItem('shici-state')).progress),snapshot.progress);assert.deepEqual(errors,[]);
 console.log('Chapter UI passed: hierarchy, search, scoped study, persisted selection/progress, empty sections, basic vocabulary, responsive layout.');await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});

