const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const width = Number(process.argv[2] || 340);
const height = Number(process.argv[3] || 740);
const out = process.argv[4] || `E:/单词/preview/phone-${width}.png`;

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
  await page.getByRole('button', { name: '词库', exact: true }).click();
  await page.getByRole('textbox', { name: '搜索词库' }).fill('eminent');
  await page.locator('.word-row').first().click();
  await page.locator('.blocks').first().waitFor();

  const metrics = await page.evaluate(() => {
    const m = document.querySelector('.modal');
    const r = m.getBoundingClientRect();
    return {
      vw: innerWidth, vh: innerHeight,
      modal: { top: Math.round(r.top), bottom: Math.round(r.bottom), height: Math.round(r.height), width: Math.round(r.width) },
      scrollH: m.scrollHeight, clientH: m.clientHeight,
      docScrollW: document.documentElement.scrollWidth,
      fontGloss: getComputedStyle(document.querySelector('.gloss')).fontSize,
      fontBlock: getComputedStyle(document.querySelector('.block .v')).fontSize,
    };
  });
  await page.screenshot({ path: out, fullPage: false });
  console.log(JSON.stringify({ width, height, out, metrics, errors }));
  await browser.close();
})().catch(e => { console.error('PHONE_FAIL', e.message); process.exit(2); });
