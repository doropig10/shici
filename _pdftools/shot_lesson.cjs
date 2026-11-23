const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const unit = process.argv[2] || '8';
const lesson = process.argv[3] || '3';
const out = process.argv[4] || `E:/单词/preview/u${unit}l${lesson}.png`;

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
  await page.getByRole('button', { name: '词库', exact: true }).click();
  await page.locator('#scope-unit').selectOption(unit);
  await page.locator('#scope-lesson').selectOption(lesson);
  await page.locator('.word-row').first().waitFor();
  const words = await page.locator('.word-row b').allTextContents();
  const caption = await page.locator('.scope-caption').textContent().catch(() => '');
  await page.screenshot({ path: out, fullPage: true });
  console.log(JSON.stringify({ unit, lesson, count: words.length, first6: words.slice(0, 6), caption: caption.trim(), errors }));
  await browser.close();
})().catch(e => { console.error('FAIL', e.message); process.exit(2); });
