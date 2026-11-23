const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    headless: true, args: ['--disable-gpu'],
  });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  const goal = () => page.evaluate(() => JSON.parse(localStorage.getItem('shici-state')).goal);

  await page.goto('http://127.0.0.1:8765');
  await page.getByRole('button', { name: '开始今日学习' }).waitFor();
  await page.getByRole('button', { name: '我的', exact: true }).click();
  await page.locator('#goal').waitFor();
  const initial = await page.locator('#goal').inputValue();

  await page.getByRole('button', { name: '增加五个' }).click();
  const afterPlus = await page.locator('#goal').inputValue();

  await page.locator('#goal').fill('37');
  await page.locator('#goal').blur();
  await page.waitForTimeout(300);
  const afterType = await page.locator('#goal').inputValue();
  const stored = await goal();

  await page.getByRole('button', { name: '100', exact: true }).click();
  const afterChip = await page.locator('#goal').inputValue();

  await page.locator('#goal').fill('999');
  await page.locator('#goal').blur();
  await page.waitForTimeout(300);
  const afterMax = await page.locator('#goal').inputValue();

  await page.locator('#goal').fill('0');
  await page.locator('#goal').blur();
  await page.waitForTimeout(300);
  const afterMin = await page.locator('#goal').inputValue();

  await page.locator('#goal').fill('25');
  await page.locator('#goal').blur();
  await page.waitForTimeout(300);
  await page.getByRole('button', { name: '今日', exact: true }).click();
  await page.locator('.metric').first().waitFor();
  const todayMetric = await page.locator('.metric').first().locator('strong').textContent();
  await page.screenshot({ path: 'E:/单词/preview/9-today.png', fullPage: true });

  await page.getByRole('button', { name: '我的', exact: true }).click();
  await page.locator('#goal').waitFor();
  await page.screenshot({ path: 'E:/单词/preview/6-settings.png', fullPage: true });

  console.log(JSON.stringify({ initial, afterPlus, afterType, stored, afterChip, afterMax, afterMin, todayMetric, errors }));
  await browser.close();
})().catch(e => { console.error('GOAL_TEST_FAIL', e.message); process.exit(2); });

