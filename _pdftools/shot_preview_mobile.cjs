const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const W = Number(process.argv[2] || 390);
const H = Number(process.argv[3] || 844);

(async () => {
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    headless: true, args: ['--disable-gpu'],
  });
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  const shot = (name) => page.screenshot({ path: `E:/单词/preview/v17-${name}.png`, fullPage: false });

  await page.goto('http://127.0.0.1:8765');
  await page.getByRole('button', { name: '开始今日学习' }).waitFor();
  await shot('1-home');

  await page.getByRole('button', { name: '开始今日学习' }).click();
  await page.locator('.word-large').first().waitFor();
  await shot('2-study-front');
  const reveal = page.getByRole('button', { name: '展开完整词条', exact: true });
  if (await reveal.count()) await reveal.first().click();
  await page.locator('.blocks').first().waitFor();
  await shot('3-study-back');

  await page.getByRole('button', { name: '退出本轮学习' }).click();
  await page.getByRole('button', { name: '回到今日', exact: true }).click();
  await page.getByRole('button', { name: '词库', exact: true }).click();
  await page.locator('.word-row').first().waitFor();
  await shot('4-words');

  await page.getByRole('textbox', { name: '搜索词库' }).fill('eminent');
  await page.locator('.word-row').first().click();
  await page.locator('.blocks').first().waitFor();
  await shot('5-entry');
  await page.getByRole('button', { name: '关闭词条' }).click();

  await page.getByRole('button', { name: '书架', exact: true }).click();
  await page.locator('.book-item').first().waitFor();
  await shot('6-books');

  await page.getByRole('button', { name: '我的', exact: true }).click();
  await page.locator('#goal').waitFor();
  await shot('7-settings');

  console.log(JSON.stringify({ W, H, errors }));
  await browser.close();
})().catch(e => { console.error('PREVIEW_FAIL', e.message); process.exit(2); });
