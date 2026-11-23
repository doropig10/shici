const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('node:fs');

(async () => {
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    headless: true, args: ['--disable-gpu'],
  });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  const events = [];
  page.on('load', () => events.push('load'));
  page.on('framenavigated', f => events.push('nav:' + f.url()));

  await page.goto('http://127.0.0.1:8765');
  await page.getByRole('button', { name: '开始今日学习' }).waitFor();

  const rev1 = await page.evaluate(() => fetch('/__rev', { cache: 'no-store' }).then(r => r.text()));
  const scriptCount = await page.evaluate(() => document.querySelectorAll('script').length);

  const css = 'E:/单词/app/src/main/assets/style.css';
  fs.writeFileSync(css, fs.readFileSync(css));
  await page.waitForTimeout(2500);

  const rev2 = await page.evaluate(() => fetch('/__rev', { cache: 'no-store' }).then(r => r.text())).catch(e => 'ERR:' + e.message);
  console.log(JSON.stringify({ rev1, rev2, changed: rev1 !== rev2, scriptCount, events }, null, 1));
  await browser.close();
})().catch(e => { console.error('DBG_FAIL', e.message); process.exit(2); });
