const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    headless: true, args: ['--disable-gpu'],
  });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await page.goto('http://127.0.0.1:8765');
  await page.getByRole('button', { name: '开始今日学习' }).waitFor();
  await page.getByRole('button', { name: '词库', exact: true }).click();
  await page.getByRole('textbox', { name: '搜索词库' }).fill('aggressive');
  await page.locator('.word-row').first().click();
  await page.locator('.blocks').first().waitFor();
  const dump = await page.evaluate(() => {
    return [...document.querySelectorAll('.block')].map(b => ({
      k: b.querySelector('.k')?.textContent,
      parts: [...b.querySelectorAll('.part')].map(p => {
        const src = p.querySelector('.src');
        const pv = p.querySelector('.pv');
        return {
          src: src ? src.textContent : null,
          srcW: src ? Math.round(src.getBoundingClientRect().width) : null,
          pvX: pv ? Math.round(pv.getBoundingClientRect().left) : null,
        };
      }),
    }));
  });
  console.log(JSON.stringify(dump, null, 1));
  await browser.close();
})().catch(e => { console.error('MEASURE_FAIL', e.message); process.exit(2); });
