const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    headless: true, args: ['--disable-gpu'],
  });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));

  await page.addInitScript(() => {
    window.__calls = [];
    window.Android = {
      loadState: () => '',
      saveState: () => true,
      appVersion: () => '1.0.20|21',
      checkUpdate: () => window.__calls.push(['checkUpdate']),
      downloadUpdate: (a, b, c) => window.__calls.push(['downloadUpdate', a, b, c]),
      speak: () => {},
    };
  });

  await page.goto('http://127.0.0.1:8765');
  await page.getByRole('button', { name: '开始今日学习' }).waitFor();
  await page.getByRole('button', { name: '我的', exact: true }).click();
  await page.locator('#goal').waitFor();
  const versionRow = await page.getByRole('button', { name: /检查更新/ }).textContent();
  await page.getByRole('button', { name: /检查更新/ }).click();

  await page.evaluate(() => {
    const info = { versionCode: 29, versionName: '1.0.28', apk: 'https://example.com/a.apk',
      apkFallback: 'https://example.com/b.apk', sha256: 'abc', size: 279376, notes: '测试更新' };
    window.receiveUpdate(JSON.stringify([JSON.stringify(info)]), '');
  });
  await page.locator('.modal').waitFor();
  const modalText = await page.locator('.modal').textContent();
  await page.screenshot({ path: 'E:/单词/preview/update-modal.png' });
  await page.getByRole('button', { name: '下载并安装' }).click();
  const calls = await page.evaluate(() => window.__calls);

  await page.evaluate(() => window.receiveUpdate(JSON.stringify([JSON.stringify({ versionCode: 21, versionName: '1.0.20' })]), ''));
  const toastText = await page.locator('#toast').textContent();

  console.log(JSON.stringify({ versionRow: versionRow.replace(/\s+/g, ' ').trim(), modal: modalText.replace(/\s+/g, ' ').slice(0, 80), calls, toastText, errors }, null, 1));
  await browser.close();
})().catch(e => { console.error('UPDATE_UI_FAIL', e.message); process.exit(2); });
