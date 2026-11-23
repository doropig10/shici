const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    headless: true, args: ['--disable-gpu'],
  });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto('http://127.0.0.1:8765');
  await page.getByRole('button', { name: '开始今日学习' }).waitFor();

  await page.getByRole('button', { name: '词库', exact: true }).click();
  await page.locator('.word-row').first().waitFor();
  await page.screenshot({ path: 'E:/单词/preview/7-chips.png' });

  await page.getByRole('textbox', { name: '搜索词库' }).fill('expert');
  await page.locator('.word-row').first().click();
  await page.locator('.blocks').first().waitFor();
  await page.screenshot({ path: 'E:/单词/preview/8-entry-modal.png', fullPage: true });

  console.log(JSON.stringify({ errors }));
  await browser.close();
})().catch(e => { console.error('SHOT2_FAIL', e.message); process.exit(2); });
