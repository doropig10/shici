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

  // 造三条不同评价
  await page.evaluate(() => {
    const now = Date.now();
    const put = (word, last, r) => {
      const w = BOOK_DATA.words.find(x => x.word === word);
      state.progress['liuxiaoyan-cet6-2026:' + w.id] =
        { stage: 1, due: now, reps: 1, lapses: 0, firstSeen: now, lastSeen: now, r, last, undo: null };
    };
    put('ambition', 'good', { g: 1, h: 0, a: 0 });
    put('aggressive', 'hard', { g: 0, h: 1, a: 0 });
    put('congress', 'again', { g: 0, h: 0, a: 1 });
    save(); render();
  });

  await page.getByRole('button', { name: '词库', exact: true }).click();
  await page.locator('.word-row').first().waitFor();
  const chips = await page.locator('.chip').allTextContents();

  const result = {};
  for (const label of ['记得', '模糊', '忘记']) {
    await page.getByRole('button', { name: label, exact: true }).click();
    await page.locator('.word-row').first().waitFor();
    result[label] = (await page.locator('.word-row b').allTextContents()).join(',');
  }
  await page.screenshot({ path: 'E:/单词/preview/rating-chips.png' });
  console.log(JSON.stringify({ chips, result, errors }, null, 1));
  await browser.close();
})().catch(e => { console.error('CHIPS_FAIL', e.message); process.exit(2); });
