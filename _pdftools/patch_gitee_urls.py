from pathlib import Path

main = Path(r"E:\单词\app\src\main\java\cn\shici\wordbook\MainActivity.java")
s = main.read_text(encoding="utf-8")

old_urls = '''    private static final String[] UPDATE_URLS = {
        "https://github.com/doropig10/shici/releases/latest/download/version.json",
        "https://raw.githubusercontent.com/doropig10/shici/main/version.json",
        "https://cdn.jsdelivr.net/gh/doropig10/shici@main/version.json"
    };'''
new_urls = '''    private static final String[] UPDATE_URLS = {
        "https://gitee.com/doro_pig/shici/raw/master/version.json",
        "https://github.com/doropig10/shici/releases/latest/download/version.json",
        "https://raw.githubusercontent.com/doropig10/shici/main/version.json",
        "https://cdn.jsdelivr.net/gh/doropig10/shici@main/version.json"
    };'''
assert old_urls in s
s = s.replace(old_urls, new_urls, 1)

old_sig = "        @JavascriptInterface public void downloadUpdate(String url, String fallback, String sha256) {"
new_sig = "        @JavascriptInterface public void downloadUpdate(String url, String fallback, String mirror, String sha256) {"
assert old_sig in s
s = s.replace(old_sig, new_sig, 1)

old_urls2 = '''                    String[] urls = (fallback != null && !fallback.isEmpty())
                        ? new String[]{url, fallback} : new String[]{url};'''
new_urls2 = '''                    java.util.List<String> list = new ArrayList<>();
                    if (url != null && !url.isEmpty()) list.add(url);
                    if (fallback != null && !fallback.isEmpty()) list.add(fallback);
                    if (mirror != null && !mirror.isEmpty()) list.add(mirror);
                    String[] urls = list.toArray(new String[0]);'''
assert old_urls2 in s
s = s.replace(old_urls2, new_urls2, 1)

main.write_text(s, encoding="utf-8", newline="\n")
print("MainActivity: gitee first + 3 apk urls")

js_path = Path(r"E:\单词\app\src\main\assets\app.js")
js = js_path.read_text(encoding="utf-8")
old_js = "Android.downloadUpdate(u.apk,u.apkFallback||'',u.sha256||'');"
new_js = "Android.downloadUpdate(u.apk,u.apkFallback||'',u.apkMirror||'',u.sha256||'');"
assert old_js in js
js_path.write_text(js.replace(old_js, new_js, 1), encoding="utf-8", newline="\n")
print("app.js: mirror passed")
