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

  const rate = async (name) => {
    const reveal = page.getByRole('button', { name: '展开完整词条', exact: true });
    if (await reveal.count()) await reveal.first().click();
    await page.getByRole('button', { name: new RegExp(name) }).click();
    await page.locator('.word-large').first().waitFor();
  };
  await page.getByRole('button', { name: '开始今日学习' }).click();
  await page.locator('.word-large').first().waitFor();
  const w1 = await page.locator('.word-large').textContent();
  await rate('记得');
  await rate('模糊');
  await rate('记得');
  const w2 = await page.locator('.word-large').textContent();
  await rate('忘记');

  await page.getByRole('button', { name: '退出本轮学习' }).click();
  await page.getByRole('button', { name: '回到今日', exact: true }).click();
  await page.getByRole('button', { name: '词库', exact: true }).click();
  await page.locator('.word-row').first().waitFor();
  const tags = await page.locator('.rec-tag').allTextContents();
  await page.screenshot({ path: 'E:/单词/preview/records-list.png' });

  await page.locator('.word-row').first().click();
  await page.locator('.study-log').waitFor();
  const log = (await page.locator('.study-log').textContent()).replace(/\s+/g, ' ').trim();
  await page.screenshot({ path: 'E:/单词/preview/records-modal.png' });

  await page.getByRole('button', { name: '撤销上一次' }).click();
  await page.locator('.study-log').waitFor();
  const logAfterUndo = (await page.locator('.study-log').textContent()).replace(/\s+/g, ' ').trim();

  await page.getByRole('button', { name: '清除该词记录' }).click();
  await page.locator('.study-log').waitFor();
  const logAfterClear = (await page.locator('.study-log').textContent()).replace(/\s+/g, ' ').trim();
  await page.getByRole('button', { name: '关闭词条' }).click();
  const tagCountAfter = await page.locator('.word-row').first().locator('.rec-tag').count();

  console.log(JSON.stringify({ w1, w2, tags, log, logAfterUndo, logAfterClear, tagCountAfter, errors }, null, 1));
  await browser.close();
})().catch(e => { console.error('REC_TEST_FAIL', e.message); process.exit(2); });
