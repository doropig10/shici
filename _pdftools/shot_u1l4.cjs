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
  await page.locator('#scope-unit').selectOption('1');
  await page.locator('#scope-lesson').selectOption('4');
  await page.locator('.word-row').first().waitFor();
  const count = await page.locator('.word-row').count();
  await page.screenshot({ path: 'E:/单词/preview/10-u1l4.png', fullPage: true });
  console.log(JSON.stringify({ count, errors }));
  await browser.close();
})().catch(e => { console.error('SHOT3_FAIL', e.message); process.exit(2); });
