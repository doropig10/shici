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

  // 1) 真实评分两次：ambition 记得 → 模糊（借回看前先记两次，用 state 直接造第二次）
  await page.getByRole('button', { name: '开始今日学习' }).click();
  await page.locator('.word-large').first().waitFor();
  const reveal = page.getByRole('button', { name: '展开完整词条', exact: true });
  if (await reveal.count()) await reveal.first().click();
  await page.getByRole('button', { name: /记得/ }).click();
  await page.locator('.word-large').first().waitFor();

  const stored = await page.evaluate(() => {
    const w = BOOK_DATA.words.find(x => x.word === 'ambition');
    const k = 'liuxiaoyan-cet6-2026:' + w.id;
    return JSON.parse(localStorage.getItem('shici-state')).progress[k];
  });

  // 2) 造一条“已评两次”的记录，验证撤销
  const afterUndo = await page.evaluate(() => {
    const w = BOOK_DATA.words.find(x => x.word === 'ambition');
    const k = 'liuxiaoyan-cet6-2026:' + w.id;
    const now = Date.now();
    state.progress[k] = { stage: 2, due: now + 86400000, reps: 2, lapses: 0, firstSeen: now, lastSeen: now,
      r: { g: 1, h: 1, a: 0 }, last: 'hard',
      undo: { stage: 1, due: now, reps: 1, lapses: 0, firstSeen: now, lastSeen: now, r: { g: 1, h: 0, a: 0 }, last: 'good' } };
    save();
    return JSON.parse(localStorage.getItem('shici-state')).progress[k].last;
  });

  await page.getByRole('button', { name: '退出本轮学习' }).click();
  await page.getByRole('button', { name: '回到今日', exact: true }).click();
  await page.getByRole('button', { name: '词库', exact: true }).click();
  await page.locator('.word-row').first().click();
  await page.locator('.study-log').waitFor();
  const before = (await page.locator('.study-log').textContent()).replace(/\s+/g, ' ').trim();
  await page.getByRole('button', { name: '撤销上一次' }).click();
  await page.locator('.study-log').waitFor();
  const after = (await page.locator('.study-log').textContent()).replace(/\s+/g, ' ').trim();
  const storedAfter = await page.evaluate(() => {
    const w = BOOK_DATA.words.find(x => x.word === 'ambition');
    return JSON.parse(localStorage.getItem('shici-state')).progress['liuxiaoyan-cet6-2026:' + w.id];
  });

  console.log(JSON.stringify({ storedAfterFirstRate: stored, madeLast: afterUndo, before, after, undoRestoredLast: storedAfter && storedAfter.last, errors }, null, 1));
  await browser.close();
})().catch(e => { console.error('REC2_FAIL', e.message); process.exit(2); });
