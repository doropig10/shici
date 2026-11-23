const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    headless: true, args: ['--disable-gpu'],
  });
  const page = await browser.newPage({ viewport: { width: 340, height: 740 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));

  await page.goto('http://127.0.0.1:8765');
  await page.getByRole('button', { name: '开始今日学习' }).waitFor();
  await page.getByRole('button', { name: '开始今日学习' }).click();
  await page.locator('.word-large').first().waitFor();
  await page.screenshot({ path: 'E:/单词/preview/back-a-start.png', fullPage: false });

  const rate = async () => {
    const reveal = page.getByRole('button', { name: '展开完整词条', exact: true });
    if (await reveal.count()) await reveal.first().click();
    await page.getByRole('button', { name: /记得/ }).click();
    await page.locator('.word-large').first().waitFor();
  };
  await rate();
  await rate();
  await page.getByRole('button', { name: /上一个/ }).click();
  await page.locator('.word-large').first().waitFor();
  const hintHidden = await page.locator('p.quiet').evaluate(el => getComputedStyle(el).display === 'none');
  await page.screenshot({ path: 'E:/单词/preview/back-b-peek.png', fullPage: false });

  console.log(JSON.stringify({ peekingWord: await page.locator('.word-large').textContent(), hintHidden, errors }));
  await browser.close();
})().catch(e => { console.error('FAIL', e.message); process.exit(2); });
