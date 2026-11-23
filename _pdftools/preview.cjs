const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('node:fs');

(async () => {
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    headless: true,
    args: ['--disable-gpu'],
  });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));

  await page.goto('http://127.0.0.1:8765');
  await page.getByRole('button', { name: '开始今日学习' }).waitFor();
  fs.mkdirSync('E:/单词/preview', { recursive: true });
  await page.screenshot({ path: 'E:/单词/preview/1-today.png', fullPage: true });

  await page.getByRole('button', { name: '开始今日学习' }).click();
  await page.locator('.word-large').first().waitFor();
  await page.screenshot({ path: 'E:/单词/preview/2-study-front.png', fullPage: true });

  const reveal = page.getByRole('button', { name: '展开完整词条', exact: true });
  if (await reveal.count()) await reveal.first().click();
  await page.locator('.definition').first().waitFor();
  await page.screenshot({ path: 'E:/单词/preview/3-study-back.png', fullPage: true });

  await page.getByRole('button', { name: '退出本轮学习' }).click();
  await page.getByRole('button', { name: '回到今日', exact: true }).click();
  await page.getByRole('button', { name: '词库', exact: true }).click();
  await page.locator('.word-row').first().waitFor();
  await page.screenshot({ path: 'E:/单词/preview/4-words.png', fullPage: true });

  await page.getByRole('button', { name: '书架', exact: true }).click();
  await page.locator('.book-item').first().waitFor();
  await page.screenshot({ path: 'E:/单词/preview/5-books.png', fullPage: true });

  await page.getByRole('button', { name: '我的', exact: true }).click();
  await page.screenshot({ path: 'E:/单词/preview/6-settings.png', fullPage: true });

  console.log('errors:', JSON.stringify(errors));
  await browser.close();
})().catch(e => { console.error('PREVIEW_FAIL', e.message); process.exit(1); });
