const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    headless: true, args: ['--disable-gpu'],
  });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true });
  await page.goto('http://127.0.0.1:8765');
  await page.getByRole('button', { name: '开始今日学习' }).waitFor();
  await page.getByRole('button', { name: '词库', exact: true }).click();
  const results = {};
  for (const q of ['odo', 'cata', 'ambition']) {
    await page.getByRole('textbox', { name: '搜索词库' }).fill(q);
    await page.locator('.word-row').first().click();
    const attr = await page.locator('.modal .sound').getAttribute('data-word');
    const shown = await page.locator('.modal .word-large').textContent();
    results[q] = { shown, spoken: attr };
    await page.getByRole('button', { name: '关闭词条' }).click();
  }
  console.log(JSON.stringify(results, null, 1));
  await browser.close();
})().catch(e => { console.error('FAIL', e.message); process.exit(2); });
