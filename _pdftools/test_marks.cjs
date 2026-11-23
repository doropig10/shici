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

  await page.locator('.word-row').first().click();
  await page.locator('.mark-row').waitFor();
  await page.screenshot({ path: 'E:/单词/preview/mark-modal.png' });
  await page.getByRole('button', { name: '重点', exact: true }).click();
  await page.locator('.mark-row').waitFor();
  const onState = await page.locator('.tag-btn.on').textContent();
  await page.getByRole('button', { name: '关闭词条' }).click();

  const rowTag = await page.locator('.word-row').first().locator('.mark-tag').textContent();
  await page.getByRole('button', { name: '标记', exact: true }).click();
  await page.locator('.word-row').first().waitFor();
  const markedCount = await page.locator('.word-row').count();
  const markedWords = await page.locator('.word-row b').allTextContents();
  await page.screenshot({ path: 'E:/单词/preview/mark-list.png' });

  const stored = await page.evaluate(() => JSON.parse(localStorage.getItem('shici-state')).marks);

  // 取消标记
  await page.locator('.word-row').first().click();
  await page.getByRole('button', { name: '取消标记' }).click();
  await page.getByRole('button', { name: '关闭词条' }).click();
  await page.getByRole('button', { name: '全部', exact: true }).click();
  const rowTagAfter = await page.locator('.word-row').first().locator('.mark-tag').count();

  console.log(JSON.stringify({ onState: onState.trim(), rowTag: rowTag.trim(), markedCount, markedWords, stored, rowTagAfter, errors }, null, 1));
  await browser.close();
})().catch(e => { console.error('MARK_TEST_FAIL', e.message); process.exit(2); });
