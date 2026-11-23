// 验证 devserver 的自动刷新：改一次 style.css 的 mtime，页面应自动 reload。
const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('node:fs');

(async () => {
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    headless: true, args: ['--disable-gpu'],
  });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  let loads = 0;
  page.on('load', () => loads++);
  await page.goto('http://127.0.0.1:8765');
  await page.getByRole('button', { name: '开始今日学习' }).waitFor();
  await page.waitForTimeout(1200);
  const first = loads;

  const css = 'E:/单词/app/src/main/assets/style.css';
  const before = fs.readFileSync(css);
  fs.writeFileSync(css, before);           // 只改 mtime，内容不变

  await page.waitForTimeout(2000);
  const second = loads;
  console.log(JSON.stringify({ loadsBeforeEdit: first, loadsAfterEdit: second, reloaded: second > first }));
  await browser.close();
  process.exit(second > first ? 0 : 1);
})().catch(e => { console.error('RELOAD_TEST_FAIL', e.message); process.exit(2); });

