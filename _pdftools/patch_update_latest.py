from pathlib import Path
import re

main = Path(r"E:\单词\app\src\main\java\cn\shici\wordbook\MainActivity.java")
s = main.read_text(encoding="utf-8")

# 更新源：Release 的 latest/download（无缓存、无 API 限流）优先，静态文件兜底
old_urls = '''    private static final String RELEASES_API = "https://api.github.com/repos/doropig10/shici/releases/latest";
    private static final String[] UPDATE_URLS = {
        "https://raw.githubusercontent.com/doropig10/shici/main/version.json",
        "https://cdn.jsdelivr.net/gh/doropig10/shici@main/version.json"
    };'''
new_urls = '''    private static final String[] UPDATE_URLS = {
        "https://github.com/doropig10/shici/releases/latest/download/version.json",
        "https://raw.githubusercontent.com/doropig10/shici/main/version.json",
        "https://cdn.jsdelivr.net/gh/doropig10/shici@main/version.json"
    };'''
assert old_urls in s
s = s.replace(old_urls, new_urls, 1)

start = s.index("        @JavascriptInterface public void checkUpdate() {")
end = s.index("        @JavascriptInterface public void downloadUpdate(")
new_block = '''        @JavascriptInterface public void checkUpdate() {
            new Thread(() -> {
                List<String> bodies = new ArrayList<>();
                List<String> errors = new ArrayList<>();
                long stamp = System.currentTimeMillis();
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
main.write_text(s, encoding="utf-8", newline="\n")
print("checkUpdate: latest/download first, no API")
