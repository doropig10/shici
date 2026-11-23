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
  page.on('pageerror', e => events.push('err:' + e.message));

  await page.goto('http://127.0.0.1:8765');
  await page.getByRole('button', { name: '开始今日学习' }).waitFor();

  const injected = await page.evaluate(() => {
    const scripts = [...document.querySelectorAll('script')].map(s => s.textContent.slice(0, 40));
    return scripts;
  });

  await page.evaluate(() => {
    window.__polls = 0;
    window.__r = null;
    setInterval(() => {
      window.__polls++;
      fetch('/__rev', { cache: 'no-store' }).then(x => x.text()).then(t => {
        if (window.__r === null) window.__r = t;
        else if (t !== window.__r) location.reload();
      });
    }, 600);
  });

  await page.waitForTimeout(1200);
  const polls1 = await page.evaluate(() => window.__polls);
  fs.writeFileSync('E:/单词/app/src/main/assets/style.css', fs.readFileSync('E:/单词/app/src/main/assets/style.css'));
  await page.waitForTimeout(2500);
  const state = await page.evaluate(() => ({ polls: window.__polls, r: window.__r })).catch(e => 'ERR');
  console.log(JSON.stringify({ injected, polls1, state, events }, null, 1));
  await browser.close();
})().catch(e => { console.error('DBG2_FAIL', e.message); process.exit(2); });
