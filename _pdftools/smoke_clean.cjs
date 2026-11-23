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
  await page.getByRole('button', { name: '开始今日学习' }).click();
  await page.locator('.word-large').first().waitFor();
  const reveal = page.getByRole('button', { name: '展开完整词条', exact: true });
  if (await reveal.count()) await reveal.first().click();
  await page.locator('.blocks').first().waitFor();
  const sourceTag = await page.locator('.source-tag').textContent();
  const hasSourceButton = await page.getByRole('button', { name: /查看原书上下文/ }).count();
  await page.screenshot({ path: 'E:/单词/preview/clean-study.png', fullPage: false });

  await page.getByRole('button', { name: '退出本轮学习' }).click();
  await page.getByRole('button', { name: '回到今日', exact: true }).click();
  await page.getByRole('button', { name: '词库', exact: true }).click();
  await page.locator('.word-row').first().waitFor();
  const row = await page.locator('.word-row').first().textContent();
  await page.locator('.word-row').first().click();
  await page.locator('.blocks').first().waitFor();
  await page.screenshot({ path: 'E:/单词/preview/clean-entry.png', fullPage: false });
  await page.getByRole('button', { name: '修改词条' }).click();
  const modalTitle = await page.locator('.modal h2').first().textContent();
  const scanImg = await page.locator('.scan-card').count();
  await page.screenshot({ path: 'E:/单词/preview/clean-edit.png', fullPage: false });

  console.log(JSON.stringify({ sourceTag, hasSourceButton, row: row.replace(/\s+/g, ' ').slice(0, 40), modalTitle, scanImg, errors }, null, 1));
  await browser.close();
})().catch(e => { console.error('SMOKE_FAIL', e.message); process.exit(2); });
