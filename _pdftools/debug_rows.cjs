const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    headless: true, args: ['--disable-gpu'],
  });
  const page = await browser.newPage({ viewport: { width: 340, height: 740 }, deviceScaleFactor: 2, isMobile: true });
  await page.goto('http://127.0.0.1:8765');
  await page.getByRole('button', { name: '开始今日学习' }).waitFor();
  await page.getByRole('button', { name: '词库', exact: true }).click();
  await page.getByRole('textbox', { name: '搜索词库' }).fill('eminent');
  await page.locator('.word-row').first().click();
  await page.locator('.blocks').first().waitFor();

  const dump = await page.evaluate(() => [...document.querySelectorAll('.block')].map(b => {
    const br = b.getBoundingClientRect();
    return {
      cls: b.className,
      k: b.querySelector('.bk')?.textContent || b.querySelector('.k')?.textContent,
      blockW: Math.round(br.width),
      rows: [...b.querySelectorAll('.brow')].map(r => {
        const rr = r.getBoundingClientRect();
        const src = r.querySelector('.src');
        const pv = r.querySelector('.pv');
        return {
          rowW: Math.round(rr.width),
          srcW: src ? Math.round(src.getBoundingClientRect().width) : null,
          pvW: pv ? Math.round(pv.getBoundingClientRect().width) : null,
          pvText: pv ? pv.textContent.slice(0, 20) : null,
        };
      }),
      plainV: b.querySelector('.v') ? Math.round(b.querySelector('.v').getBoundingClientRect().width) : null,
    };
  }));
  console.log(JSON.stringify(dump, null, 1));
  await browser.close();
})().catch(e => { console.error('DBG_FAIL', e.message); process.exit(2); });
