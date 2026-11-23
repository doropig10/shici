const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const word = process.argv[2] || 'instance';
const out = process.argv[3] || `E:/单词/preview/study-${word}.png`;

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

  await page.evaluate((w) => {
    const b = window.BOOK_DATA;
    const target = b.words.find(x => x.word.toLowerCase() === w.toLowerCase());
    session = { mode: 'mixed', queue: [target.id], total: 1, done: 0, correct: 0, started: Date.now(), scopeLabel: '' };
    view = 'study';
    revealed = true;
    render();
  }, word);

  await page.locator('.blocks').first().waitFor();
  const metrics = await page.evaluate(() => {
    const c = document.querySelector('.study-card').getBoundingClientRect();
    const last = [...document.querySelectorAll('.block')].pop().getBoundingClientRect();
    return { cardTop: Math.round(c.top), cardBottom: Math.round(c.bottom), cardH: Math.round(c.height), lastBlockBottom: Math.round(last.bottom), blankBelow: Math.round(c.bottom - last.bottom) };
  });
  await page.screenshot({ path: out, fullPage: true });
  console.log(JSON.stringify({ word, out, metrics, errors }));
  await browser.close();
})().catch(e => { console.error('STUDY_FAIL', e.message); process.exit(2); });
