from pathlib import Path

ROOT = Path(r"E:\单词")
main = ROOT / "app/src/main/java/cn/shici/wordbook/MainActivity.java"
manifest = ROOT / "app/src/main/AndroidManifest.xml"
js_path = ROOT / "app/src/main/assets/app.js"

# ---------------- Java ----------------
s = main.read_text(encoding="utf-8")

if "checkUpdate" not in s:
    s = s.replace("import android.content.Intent;",
                  "import android.content.Intent;\nimport android.content.pm.PackageInfo;\nimport android.content.pm.PackageManager;", 1)
    s = s.replace("import java.util.Locale;",
                  "import java.net.HttpURLConnection;\nimport java.net.URL;\nimport java.security.MessageDigest;\nimport java.util.Locale;", 1)
    s = s.replace('    private static final int OPEN_WORDS = 101, SAVE_BACKUP = 102, OPEN_BACKUP = 103;',
                  '    private static final int OPEN_WORDS = 101, SAVE_BACKUP = 102, OPEN_BACKUP = 103;\n'
                  '    private static final String UPDATE_URL = "https://raw.githubusercontent.com/doropig10/shici/main/version.json";', 1)

    bridge_tail = "        }\n    }\n    private byte[] readBundledImage"
    assert bridge_tail in s, "bridge tail not found"

    methods = '''        }

        @JavascriptInterface public String appVersion() {
            try {
                PackageInfo info = getPackageManager().getPackageInfo(getPackageName(), 0);
                return info.versionName + "|" + info.versionCode;
            } catch (Exception e) { return "?|0"; }
        }

        @JavascriptInterface public void checkUpdate() {
            new Thread(() -> {
                String json = null, error = "";
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
                } catch (Exception e) { error = e.getClass().getSimpleName() + ": " + e.getMessage(); }
                final String payload = json, err = error;
                runOnUiThread(() -> web.evaluateJavascript(
                    "window.receiveUpdate && window.receiveUpdate(" + JSONObject.quote(err.isEmpty() && payload != null ? payload : "")
                    + "," + JSONObject.quote(err) + ")", null));
            }).start();
        }

        @JavascriptInterface public void downloadUpdate(String url, String sha256) {
            new Thread(() -> {
                try {
                    File target = new File(getCacheDir(), "update.apk");
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
                    }
                    if (sha256 != null && !sha256.isEmpty() && !sha256.equalsIgnoreCase(sha256Of(target))) {
                        target.delete();
                        throw new IOException("校验失败，文件可能不完整");
                    }
                    runOnUiThread(this::installApk);
                } catch (Exception e) {
                    final String msg = e.getClass().getSimpleName() + ": " + e.getMessage();
                    runOnUiThread(() -> web.evaluateJavascript(
                        "window.receiveUpdateError && window.receiveUpdateError(" + JSONObject.quote(msg) + ")", null));
                }
            }).start();
        }

        private void emitProgress(int pct) {
            runOnUiThread(() -> web.evaluateJavascript(
                "window.receiveUpdateProgress && window.receiveUpdateProgress(" + pct + ")", null));
        }

        private String sha256Of(File f) throws Exception {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            try (InputStream in = new FileInputStream(f)) {
                byte[] buf = new byte[8192]; int n;
                while ((n = in.read(buf)) != -1) md.update(buf, 0, n);
            }
            StringBuilder sb = new StringBuilder();
            for (byte b : md.digest()) sb.append(String.format("%02x", b));
            return sb.toString();
        }

        private void installApk() {
            File apk = new File(getCacheDir(), "update.apk");
            if (!apk.exists()) { Toast.makeText(MainActivity.this, "安装包已不存在，请重新下载", Toast.LENGTH_LONG).show(); return; }
            Uri uri = Uri.parse("content://" + UpdateProvider.AUTHORITY + "/update.apk");
            Intent i = new Intent(Intent.ACTION_VIEW);
            i.setDataAndType(uri, "application/vnd.android.package-archive");
            i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_ACTIVITY_NEW_TASK);
            try {
                startActivity(i);
            } catch (Exception e) {
                Toast.makeText(MainActivity.this, "无法启动安装器，请在系统设置里允许「拾词」安装未知应用", Toast.LENGTH_LONG).show();
            }
        }
    }
    private byte[] readBundledImage'''

    s = s.replace(bridge_tail, methods, 1)
    main.write_text(s, encoding="utf-8", newline="\n")
    print("MainActivity patched")

# ---------------- UpdateProvider ----------------
provider = ROOT / "app/src/main/java/cn/shici/wordbook/UpdateProvider.java"
provider.write_text('''package cn.shici.wordbook;

import android.content.ContentProvider;
import android.content.ContentValues;
import android.database.Cursor;
import android.net.Uri;
import android.os.ParcelFileDescriptor;

import java.io.File;
import java.io.FileNotFoundException;

/** 把下载到 cache 的安装包以 content:// 暴露给系统安装器（不引入 AndroidX）。 */
public final class UpdateProvider extends ContentProvider {
    public static final String AUTHORITY = "cn.shici.wordbook.updates";

    @Override public boolean onCreate() { return true; }

    @Override public ParcelFileDescriptor openFile(Uri uri, String mode) throws FileNotFoundException {
        File apk = new File(getContext().getCacheDir(), "update.apk");
        return ParcelFileDescriptor.open(apk, ParcelFileDescriptor.MODE_READ_ONLY);
    }

    @Override public String getType(Uri uri) { return "application/vnd.android.package-archive"; }

    @Override public Cursor query(Uri uri, String[] projection, String selection, String[] args, String sort) { return null; }
    @Override public Uri insert(Uri uri, ContentValues values) { return null; }
    @Override public int delete(Uri uri, String selection, String[] args) { return 0; }
    @Override public int update(Uri uri, ContentValues values, String selection, String[] args) { return 0; }
}
''', encoding="utf-8", newline="\n")
print("UpdateProvider created")

# ---------------- Manifest ----------------
xml = manifest.read_text(encoding="utf-8")
if "REQUEST_INSTALL_PACKAGES" not in xml:
    xml = xml.replace('  <uses-sdk android:minSdkVersion="26" android:targetSdkVersion="35" />',
        '  <uses-sdk android:minSdkVersion="26" android:targetSdkVersion="35" />\n'
        '  <uses-permission android:name="android.permission.INTERNET" />\n'
        '  <uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES" />', 1)
if "UpdateProvider" not in xml:
    xml = xml.replace('  </application>',
        '    <provider android:name=".UpdateProvider" android:authorities="cn.shici.wordbook.updates"\n'
        '      android:exported="false" android:grantUriPermissions="true" />\n'
        '  </application>', 1)
manifest.write_text(xml, encoding="utf-8", newline="\n")
print("manifest patched")
