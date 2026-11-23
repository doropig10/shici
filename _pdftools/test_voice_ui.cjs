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
    const voices = [
      { name: 'en-us-x-sfg#female_2-local', locale: 'en_US', network: false, quality: 400 },
      { name: 'en-us-x-iom#male_1-local', locale: 'en_US', network: false, quality: 300 },
      { name: 'en-us-x-tpf#female_1-network', locale: 'en_US', network: true, quality: 500 },
    ];
    window.Android = {
      loadState: () => '', saveState: () => true,
      appVersion: () => '1.0.30|31',
      checkUpdate: () => {},
      downloadUpdate: () => {},
      listVoices: () => JSON.stringify({ current: voices[0].name, voices }),
      setVoice: (n) => { window.__calls.push(n); return true; },
      speak: () => {},
    };
  });

  await page.goto('http://127.0.0.1:8765');
  await page.getByRole('button', { name: '开始今日学习' }).waitFor();
  await page.getByRole('button', { name: '我的', exact: true }).click();
  await page.locator('#goal').waitFor();
  const row = await page.getByRole('button', { name: /发音音色/ }).textContent();
  await page.getByRole('button', { name: /发音音色/ }).click();
  await page.locator('.voice-row').first().waitFor();
  const rowsText = await page.locator('.voice-row').allTextContents();
  await page.screenshot({ path: 'E:/单词/preview/voice-picker.png' });
  await page.locator('.voice-row').nth(2).click();
  const calls = await page.evaluate(() => window.__calls);
  const toast = await page.locator('#toast').textContent();

  console.log(JSON.stringify({ row: row.replace(/\s+/g, ' ').trim(), rows: rowsText.map(t => t.replace(/\s+/g, ' ').trim()), calls, toast, errors }, null, 1));
  await browser.close();
})().catch(e => { console.error('VOICE_TEST_FAIL', e.message); process.exit(2); });
