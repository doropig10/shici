from pathlib import Path

main = Path(r"E:\单词\app\src\main\java\cn\shici\wordbook\MainActivity.java")
s = main.read_text(encoding="utf-8")

# 1) 多源检查更新（jsDelivr 优先，raw 兜底）
old_const = '    private static final String UPDATE_URL = "https://raw.githubusercontent.com/doropig10/shici/main/version.json";'
new_const = ('    private static final String[] UPDATE_URLS = {\n'
             '        "https://cdn.jsdelivr.net/gh/doropig10/shici@main/version.json",\n'
             '        "https://raw.githubusercontent.com/doropig10/shici/main/version.json"\n'
             '    };')
assert old_const in s
s = s.replace(old_const, new_const, 1)

old_check = '''                String json = null, error = "";
                try {
                    HttpURLConnection c = (HttpURLConnection) new URL(UPDATE_URL).openConnection();
                    c.setConnectTimeout(8000); c.setReadTimeout(8000);
                    c.setRequestProperty("Accept", "application/json");
                    if (c.getResponseCode() != 200) throw new IOException("HTTP " + c.getResponseCode());
                    try (InputStream in = c.getInputStream()) {
                        ByteArrayOutputStream out = new ByteArrayOutputStream();
                        byte[] buf = new byte[8192]; int n;
                        while ((n = in.read(buf)) != -1) { out.write(buf, 0, n); if (out.size() > 200_000) break; }
                        json = out.toString("UTF-8");
                    }
                } catch (Exception e) { error = e.getClass().getSimpleName() + ": " + e.getMessage(); }'''
new_check = '''                String json = null, error = "";
                for (String url : UPDATE_URLS) {
                    try {
                        HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
                        c.setConnectTimeout(6000); c.setReadTimeout(6000);
                        c.setRequestProperty("Accept", "application/json");
                        if (c.getResponseCode() != 200) throw new IOException("HTTP " + c.getResponseCode());
                        try (InputStream in = c.getInputStream()) {
                            ByteArrayOutputStream out = new ByteArrayOutputStream();
                            byte[] buf = new byte[8192]; int n;
                            while ((n = in.read(buf)) != -1) { out.write(buf, 0, n); if (out.size() > 200_000) break; }
                            json = out.toString("UTF-8");
                        }
                        error = "";
                        break;
                    } catch (Exception e) { error = e.getClass().getSimpleName() + ": " + e.getMessage(); }
                }'''
assert old_check in s
s = s.replace(old_check, new_check, 1)

# 2) 下载支持备用地址
old_sig = "        @JavascriptInterface public void downloadUpdate(String url, String sha256) {"
new_sig = "        @JavascriptInterface public void downloadUpdate(String url, String fallback, String sha256) {"
assert old_sig in s
s = s.replace(old_sig, new_sig, 1)

old_dl = '''                    File target = new File(getCacheDir(), "update.apk");
                    HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
                    c.setConnectTimeout(10000); c.setReadTimeout(20000);
                    c.setInstanceFollowRedirects(true);
                    if (c.getResponseCode() != 200) throw new IOException("HTTP " + c.getResponseCode());
                    long total = c.getContentLengthLong();
                    try (InputStream in = c.getInputStream(); FileOutputStream out = new FileOutputStream(target)) {
                        byte[] buf = new byte[16384]; int n; long done = 0; int last = -2;
                        while ((n = in.read(buf)) != -1) {
                            out.write(buf, 0, n); done += n;
                            int pct = total > 0 ? (int) (done * 100 / total) : -1;
                            if (pct != last) { last = pct; emitProgress(pct); }
                        }
                    }'''
new_dl = '''                    File target = new File(getCacheDir(), "update.apk");
                    String[] urls = (fallback != null && !fallback.isEmpty())
                        ? new String[]{url, fallback} : new String[]{url};
                    Exception lastError = null;
                    boolean ok = false;
                    for (String u : urls) {
                        try {
                            HttpURLConnection c = (HttpURLConnection) new URL(u).openConnection();
                            c.setConnectTimeout(10000); c.setReadTimeout(25000);
                            c.setInstanceFollowRedirects(true);
                            c.setRequestProperty("User-Agent", "shici-app");
                            if (c.getResponseCode() != 200) throw new IOException("HTTP " + c.getResponseCode());
                            long total = c.getContentLengthLong();
                            try (InputStream in = c.getInputStream(); FileOutputStream out = new FileOutputStream(target)) {
                                byte[] buf = new byte[16384]; int n; long done = 0; int last = -2;
                                while ((n = in.read(buf)) != -1) {
                                    out.write(buf, 0, n); done += n;
                                    int pct = total > 0 ? (int) (done * 100 / total) : -1;
                                    if (pct != last) { last = pct; emitProgress(pct); }
                                }
                            }
                            ok = true;
                            break;
                        } catch (Exception e) { lastError = e; }
                    }
                    if (!ok) throw (lastError != null ? lastError : new IOException("下载失败"));'''
assert old_dl in s
s = s.replace(old_dl, new_dl, 1)

main.write_text(s, encoding="utf-8", newline="\n")
print("MainActivity multi-source patched")

js_path = Path(r"E:\单词\app\src\main\assets\app.js")
js = js_path.read_text(encoding="utf-8")
old_js = "Android.downloadUpdate(u.apk,u.sha256||'');"
new_js = "Android.downloadUpdate(u.apk,u.apkFallback||'',u.sha256||'');"
assert old_js in js
js_path.write_text(js.replace(old_js, new_js, 1), encoding="utf-8", newline="\n")
print("app.js fallback passed")
