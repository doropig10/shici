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
  await page.getByRole('button', { name: '重点', exact: true }).click();
  await page.locator('#mark-note').waitFor();
  await page.locator('#mark-note').fill('释义存疑，待核对原书');
  await page.getByRole('button', { name: '保存原因' }).click();
  await page.locator('.mark-row').waitFor();
  const textareaValue = await page.locator('#mark-note').inputValue();
  await page.screenshot({ path: 'E:/单词/preview/mark-note.png' });
  await page.getByRole('button', { name: '关闭词条' }).click();

  const stored = await page.evaluate(() => JSON.parse(localStorage.getItem('shici-state')).marks);
  const csv = await page.evaluate(() => markCSV());
  const count = await page.evaluate(() => markCount());

  await page.getByRole('button', { name: '我的', exact: true }).click();
  const exportRow = await page.getByRole('button', { name: /导出标记/ }).textContent();

  console.log(JSON.stringify({ textareaValue, stored, count, exportRow: exportRow.replace(/\s+/g, ' ').trim(), csv: csv.replace(/\r?\n/g, ' | '), errors }, null, 1));
  await browser.close();
})().catch(e => { console.error('MARK_NOTE_FAIL', e.message); process.exit(2); });
