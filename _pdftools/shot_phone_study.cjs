const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const width = Number(process.argv[2] || 340);
const height = Number(process.argv[3] || 740);
const out = process.argv[4] || `E:/单词/preview/phone-study-${width}.png`;

(async () => {
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    headless: true, args: ['--disable-gpu'],
  });
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto('http://127.0.0.1:8765');
  await page.getByRole('button', { name: '开始今日学习' }).waitFor();
  await page.getByRole('button', { name: '开始今日学习' }).click();
  await page.locator('.word-large').first().waitFor();
  const reveal = page.getByRole('button', { name: '展开完整词条', exact: true });
  if (await reveal.count()) await reveal.first().click();
  await page.locator('.blocks').first().waitFor();
  const metrics = await page.evaluate(() => {
    const c = document.querySelector('.study-card').getBoundingClientRect();
    return { vw: innerWidth, vh: innerHeight, card: { top: Math.round(c.top), bottom: Math.round(c.bottom), height: Math.round(c.height) }, overflowX: document.documentElement.scrollWidth > innerWidth };
  });
  await page.screenshot({ path: out, fullPage: true });
  console.log(JSON.stringify({ width, out, metrics, errors }));
  await browser.close();
})().catch(e => { console.error('PHONE_STUDY_FAIL', e.message); process.exit(2); });
