from pathlib import Path
import re

main = Path(r"E:\单词\app\src\main\java\cn\shici\wordbook\MainActivity.java")
s = main.read_text(encoding="utf-8")

s = s.replace("import org.json.JSONObject;", "import org.json.JSONArray;\nimport org.json.JSONObject;", 1)

start = s.index("        @JavascriptInterface public void checkUpdate() {")
end = s.index("        @JavascriptInterface public void downloadUpdate(")
old_block = s[start:end]

new_block = '''        private String fetchText(String url) throws IOException {
            HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
            c.setConnectTimeout(6000); c.setReadTimeout(8000);
            c.setRequestProperty("Accept", "application/json");
            c.setRequestProperty("User-Agent", "shici-app");
            c.setRequestProperty("Cache-Control", "no-cache");
            if (c.getResponseCode() != 200) throw new IOException("HTTP " + c.getResponseCode());
            try (InputStream in = c.getInputStream()) {
                ByteArrayOutputStream out = new ByteArrayOutputStream();
                byte[] buf = new byte[8192]; int n;
                while ((n = in.read(buf)) != -1) { out.write(buf, 0, n); if (out.size() > 200_000) break; }
                return out.toString("UTF-8");
            }
        }

        @JavascriptInterface public void checkUpdate() {
            new Thread(() -> {
                List<String> bodies = new ArrayList<>();
                List<String> errors = new ArrayList<>();
                long stamp = System.currentTimeMillis();

                // 1) Releases API：没有 CDN 缓存，永远是最新；从中取 version.json 资产
                try {
                    JSONObject rel = new JSONObject(fetchText(RELEASES_API));
                    JSONArray assets = rel.optJSONArray("assets");
                    String vj = null;
                    if (assets != null) {
                        for (int i = 0; i < assets.length(); i++) {
                            JSONObject a = assets.optJSONObject(i);
                            if (a != null && "version.json".equals(a.optString("name"))) {
                                vj = a.optString("browser_download_url");
                            }
                        }
                    }
                    if (vj != null) bodies.add(fetchText(vj));
                } catch (Exception e) { errors.add("API " + e.getClass().getSimpleName()); }

                // 2) 静态 version.json（raw / jsDelivr）：可能被缓存，作为兜底
                for (String url : UPDATE_URLS) {
                    try {
                        bodies.add(fetchText(url + (url.contains("?") ? "&" : "?") + "t=" + stamp));
                    } catch (Exception e) { errors.add(e.getClass().getSimpleName()); }
                }

                StringBuilder arr = new StringBuilder("[");
                for (String b : bodies) { if (arr.length() > 1) arr.append(','); arr.append(JSONObject.quote(b)); }
                arr.append(']');
                final String payload = arr.toString(), err = String.join(" / ", errors);
                runOnUiThread(() -> web.evaluateJavascript(
                    "window.receiveUpdate && window.receiveUpdate(" + JSONObject.quote(payload)
                    + "," + JSONObject.quote(err) + ")", null));
            }).start();
        }

'''
s = s[:start] + new_block + s[end:]

s = s.replace('    private static final String[] UPDATE_URLS = {',
              '    private static final String RELEASES_API = "https://api.github.com/repos/doropig10/shici/releases/latest";\n'
              '    private static final String[] UPDATE_URLS = {', 1)

main.write_text(s, encoding="utf-8", newline="\n")
print("MainActivity: releases API + static fallbacks")

# release.py：把 version.json 也作为 release 资产上传
rel = Path(r"E:\单词\_pdftools\release.py")
r = rel.read_text(encoding="utf-8")
old_up = 'run([GH, "release", "upload", tag, str(apk), "--repo", REPO, "--clobber"], check=False)'
new_up = 'run([GH, "release", "upload", tag, str(apk), str(ROOT / "version.json"), "--repo", REPO, "--clobber"], check=False)'
assert old_up in r
r = r.replace(old_up, new_up, 1)
old_create = ('r = run([GH, "release", "create", tag, str(apk), "--repo", REPO,')
new_create = ('r = run([GH, "release", "create", tag, str(apk), str(WORK / "version.json"), "--repo", REPO,')
assert old_create in r
r = r.replace(old_create, new_create, 1)
rel.write_text(r, encoding="utf-8", newline="\n")
print("release.py: upload version.json asset")
