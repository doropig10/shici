const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    headless: true, args: ['--disable-gpu'],
  });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));

  await page.goto('http://127.0.0.1:8765');
  await page.getByRole('button', { name: '开始今日学习' }).waitFor();
  await page.getByRole('button', { name: '词库', exact: true }).click();
  await page.locator('.word-row').first().waitFor();
  const chips = await page.locator('.chip').allTextContents();
  const subtitle = await page.locator('h1 + p.sub').first().textContent();
  await page.screenshot({ path: 'E:/单词/preview/audit-words.png', fullPage: false });

  await page.getByRole('button', { name: '我的', exact: true }).click();
  await page.locator('#goal').waitFor();
  const footer = await page.locator('.footer-note').last().textContent();
  await page.screenshot({ path: 'E:/单词/preview/audit-settings.png', fullPage: false });

  // Unit 9 是否出现
  await page.getByRole('button', { name: '词库', exact: true }).click();
  const unitOpts = await page.locator('#scope-unit option').allTextContents();

  console.log(JSON.stringify({ chips, subtitle: subtitle.trim(), footer: footer.trim(), unitOpts, errors }, null, 1));
  await browser.close();
})().catch(e => { console.error('AUDIT_FAIL', e.message); process.exit(2); });
