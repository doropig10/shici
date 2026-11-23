const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    headless: true, args: ['--disable-gpu'],
  });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  const word = () => page.locator('.word-large').textContent();
  const backBtn = () => page.getByRole('button', { name: /上一个/ });
  const fwdBtn = () => page.getByRole('button', { name: /回到当前/ });

  await page.goto('http://127.0.0.1:8765');
  await page.getByRole('button', { name: '开始今日学习' }).waitFor();
  await page.getByRole('button', { name: '开始今日学习' }).click();
  await page.locator('.word-large').first().waitFor();

  const w1 = await word();
  const disabledAtStart = await backBtn().isDisabled();

  const rate = async () => {
    const reveal = page.getByRole('button', { name: '展开完整词条', exact: true });
    if (await reveal.count()) await reveal.first().click();
    await page.getByRole('button', { name: /记得/ }).click();
    await page.locator('.word-large').first().waitFor();
  };
  await rate();
  const w2 = await word();
  await page.screenshot({ path: 'E:/单词/preview/back-1-current.png' });
  await rate();
  const w3 = await word();

  await backBtn().click();
  await page.locator('.word-large').first().waitFor();
  const back1 = await word();
  const ratingsVisibleWhenPeeking = await page.locator('.ratings').count();
  const fwdVisible = await fwdBtn().count();
  await page.screenshot({ path: 'E:/单词/preview/back-2-peek.png' });

  await backBtn().click();
  const back2 = await word();

  await fwdBtn().click();
  const afterForward = await word();
  const hintVisible = await page.locator('.hint').count();

  console.log(JSON.stringify({ w1, w2, w3, disabledAtStart, back1, back2, ratingsVisibleWhenPeeking, fwdVisible, afterForward, hintVisible, errors }, null, 1));
  await browser.close();
})().catch(e => { console.error('BACK_TEST_FAIL', e.message); process.exit(2); });
