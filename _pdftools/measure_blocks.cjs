const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    headless: true, args: ['--disable-gpu'],
  });
  const page = await browser.newPage({ viewport: { width: 340, height: 740 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
  await page.goto('http://127.0.0.1:8765');
  await page.getByRole('button', { name: '开始今日学习' }).waitFor();
  await page.getByRole('button', { name: '词库', exact: true }).click();
  await page.getByRole('textbox', { name: '搜索词库' }).fill('eminent');
  await page.locator('.word-row').first().click();
  await page.locator('.blocks').first().waitFor();

  const data = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('.block').forEach(b => {
      const br = b.getBoundingClientRect();
      const style = getComputedStyle(b);
      const parts = [...b.querySelectorAll('.part')].map(p => {
        const r = p.getBoundingClientRect();
        const pv = p.querySelector('.pv').getBoundingClientRect();
        return { top: +(r.top - br.top).toFixed(1), bottom: +(r.bottom - br.top).toFixed(1), h: +r.height.toFixed(1), textH: +pv.height.toFixed(1) };
      });
      out.push({ k: b.querySelector('.k').textContent, h: +br.height.toFixed(1), padding: style.padding, parts });
    });
    return out;
  });
  console.log(JSON.stringify(data, null, 1));
  await browser.close();
})().catch(e => { console.error('MEASURE_FAIL', e.message); process.exit(2); });
