package cn.shici.wordbook;

import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.util.Base64;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.speech.tts.TextToSpeech;
import android.speech.tts.Voice;
import android.webkit.*;
import android.view.View;
import android.view.WindowInsets;
import android.widget.Toast;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.net.HttpURLConnection;
import java.net.URL;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.RejectedExecutionException;
import java.util.zip.ZipFile;
import java.util.zip.ZipEntry;

public final class MainActivity extends Activity {
    private WebView web;
    private TextToSpeech tts;
    private boolean speechReady = false;
    private String pendingExport = "";
    private final ThreadPoolExecutor imageWorker = new ThreadPoolExecutor(1, 1, 0L, TimeUnit.MILLISECONDS, new ArrayBlockingQueue<Runnable>(4));
    private static final int OPEN_WORDS = 101, SAVE_BACKUP = 102, OPEN_BACKUP = 103;
    private static final String[] UPDATE_URLS = {
        "https://gitee.com/doro_pig/shici/raw/master/version.json",
        "https://github.com/doropig10/shici/releases/latest/download/version.json",
        "https://raw.githubusercontent.com/doropig10/shici/main/version.json",
        "https://cdn.jsdelivr.net/gh/doropig10/shici@main/version.json"
    };

    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        getWindow().setStatusBarColor(Color.rgb(248,247,243));
        getWindow().setNavigationBarColor(Color.rgb(255,254,250));
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR | View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
        web = new WebView(this);
        web.setBackgroundColor(Color.rgb(248,247,243));
        web.setPadding(0,0,0,0);
        // Android 15+ 强制 edge-to-edge：旧的 getSystemWindowInsetXxx() 在部分机型上返回 0，
        // 内容会钻到状态栏/导航栏下面，这里改用 Type 接口取系统栏与刘海的内边距。
        web.setOnApplyWindowInsetsListener((v,insets) -> {
            int left, top, right, bottom;
            if (Build.VERSION.SDK_INT >= 30) {
                android.graphics.Insets bars = insets.getInsets(WindowInsets.Type.systemBars() | WindowInsets.Type.displayCutout());
                left = bars.left; top = bars.top; right = bars.right; bottom = bars.bottom;
            } else {
                left = insets.getSystemWindowInsetLeft();
                top = insets.getSystemWindowInsetTop();
                right = insets.getSystemWindowInsetRight();
                bottom = insets.getSystemWindowInsetBottom();
            }
            v.setPadding(left, top, right, bottom);
            return Build.VERSION.SDK_INT >= 30 ? WindowInsets.CONSUMED : insets.consumeSystemWindowInsets();
        });
        WebSettings settings = web.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        settings.setAllowFileAccessFromFileURLs(false);
        settings.setAllowUniversalAccessFromFileURLs(false);
        settings.setBlockNetworkLoads(true);
        settings.setLoadsImagesAutomatically(true);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setSupportZoom(false);
        settings.setTextZoom(100);
        web.addJavascriptInterface(new Bridge(), "Android");
        web.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest request) {
                return !isBundledAsset(request.getUrl());
            }
            @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                // android_asset is served directly by WebView, even with general
                // filesystem access disabled. HTTPS images can be blocked before
                // interception when the app has no INTERNET permission.
                if (isBundledAsset(request.getUrl())) return null;
                String url = request.getUrl().toString();
                if (url.startsWith("data:image/png;base64,") || url.startsWith("data:image/jpeg;base64,")) return null;
                return new WebResourceResponse("text/plain", "UTF-8", 403, "Forbidden", null, new ByteArrayInputStream(new byte[0]));
            }
        });
        setContentView(web);
        tts = new TextToSpeech(this, status -> {
            if (status == TextToSpeech.SUCCESS) {
                int available = tts.setLanguage(Locale.US);
                speechReady = available != TextToSpeech.LANG_MISSING_DATA && available != TextToSpeech.LANG_NOT_SUPPORTED;
                tts.setSpeechRate(0.82f);
                applyVoice();
            }
        });
        web.loadUrl("file:///android_asset/index.html");
    }
    private static boolean isBundledAsset(Uri uri) {
        String path = uri.getPath();
        return "file".equals(uri.getScheme()) && (uri.getAuthority() == null || uri.getAuthority().isEmpty())
            && path != null && path.startsWith("/android_asset/") && !path.contains("..") && !path.contains("\\");
    }
    public final class Bridge {
        @JavascriptInterface public void requestImage(String path, String token) {
            if (token == null || !token.matches("image-[0-9]+")) return;
            if (path == null || !path.matches("(?:cards|book)/[A-Za-z0-9_().-]+\\.webp") || path.contains("..")) {
                deliverImage(token, "", "PATH"); return;
            }
            try {
                imageWorker.execute(() -> {
                    Bitmap bitmap = null;
                    String failure = "APK_READ";
                    try {
                        byte[] bytes = readBundledImage(path);
                        failure = "IMAGE_DECODE";
                        BitmapFactory.Options options = new BitmapFactory.Options();
                        options.inJustDecodeBounds = true;
                        BitmapFactory.decodeByteArray(bytes, 0, bytes.length, options);
                        if (options.outWidth <= 0 || options.outHeight <= 0) throw new IOException("decode");
                        options.inSampleSize = 1;
                        // Decode only one visible image at a time; bound large scan memory.
                        while (options.outWidth / options.inSampleSize > 2048 || options.outHeight / options.inSampleSize > 4096) options.inSampleSize *= 2;
                        options.inJustDecodeBounds = false;
                        bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.length, options);
                        if (bitmap == null) throw new IOException("decode");
                        failure = "IMAGE_ENCODE";
                        ByteArrayOutputStream out = new ByteArrayOutputStream();
                        if (!bitmap.compress(Bitmap.CompressFormat.PNG, 100, out)) throw new IOException("encode");
                        String mime = "image/png";
                        if (out.size() > 4_000_000) {
                            out.reset(); mime = "image/jpeg";
                            if (!bitmap.compress(Bitmap.CompressFormat.JPEG, 92, out)) throw new IOException("encode");
                        }
                        deliverImage(token, "data:" + mime + ";base64," + Base64.encodeToString(out.toByteArray(), Base64.NO_WRAP), "");
                    } catch (IOException | RuntimeException e) {
                        deliverImage(token, "", failure + "_" + e.getClass().getSimpleName());
                    } catch (OutOfMemoryError e) {
                        deliverImage(token, "", "MEMORY");
                    } finally {
                        if (bitmap != null) bitmap.recycle();
                    }
                });
            } catch (RejectedExecutionException e) { deliverImage(token, "", "BUSY"); }
        }
        @JavascriptInterface public String loadState() { return getSharedPreferences("study",MODE_PRIVATE).getString("state", ""); }
        @JavascriptInterface public boolean saveState(String data) {
            if (data.length() > 20_000_000) return false;
            return getSharedPreferences("study",MODE_PRIVATE).edit().putString("state",data).commit();
        }
        @JavascriptInterface public void speak(String text) {
            runOnUiThread(() -> {
                if (speechReady) tts.speak(text.substring(0,Math.min(text.length(),100)),TextToSpeech.QUEUE_FLUSH,null,"word");
                else Toast.makeText(MainActivity.this,"系统尚未安装英语语音包，可在手机文字转语音设置中添加",Toast.LENGTH_LONG).show();
            });
        }
        @JavascriptInterface public void chooseWords() { runOnUiThread(() -> pickFile(OPEN_WORDS)); }
        @JavascriptInterface public void chooseBackup() { runOnUiThread(() -> pickFile(OPEN_BACKUP)); }
        @JavascriptInterface public void exportBackup(String data) {
            exportText("拾词-学习备份.json", data);
        }

        @JavascriptInterface public void exportText(String name, String data) {
            runOnUiThread(() -> {
                pendingExport = data;
                Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
                intent.setType(name != null && name.endsWith(".csv") ? "text/csv" : "application/json");
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.putExtra(Intent.EXTRA_TITLE, name == null || name.isEmpty() ? "拾词-导出.txt" : name);
                startActivityForResult(intent,SAVE_BACKUP);
            });
        }

        @JavascriptInterface public String appVersion() {
            try {
                PackageInfo info = getPackageManager().getPackageInfo(getPackageName(), 0);
                return info.versionName + "|" + info.versionCode;
            } catch (Exception e) { return "?|0"; }
        }

        private String fetchText(String url) throws IOException {
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

        @JavascriptInterface public void downloadUpdate(String url, String fallback, String mirror, String sha256) {
            new Thread(() -> {
                try {
                    File target = new File(getCacheDir(), "update.apk");
                    java.util.List<String> list = new ArrayList<>();
                    if (url != null && !url.isEmpty()) list.add(url);
                    if (fallback != null && !fallback.isEmpty()) list.add(fallback);
                    if (mirror != null && !mirror.isEmpty()) list.add(mirror);
                    String[] urls = list.toArray(new String[0]);
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
                    if (!ok) throw (lastError != null ? lastError : new IOException("下载失败"));
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

        @JavascriptInterface public String listVoices() {
            JSONObject out = new JSONObject();
            try {
                String current = (tts != null && tts.getVoice() != null) ? tts.getVoice().getName() : "";
                out.put("current", current);
                JSONArray arr = new JSONArray();
                if (tts != null) {
                    for (Voice v : tts.getVoices()) {
                        if (v.getLocale() == null || !"en".equals(v.getLocale().getLanguage())) continue;
                        JSONObject o = new JSONObject();
                        o.put("name", v.getName());
                        o.put("locale", v.getLocale().toString());
                        o.put("network", v.isNetworkConnectionRequired());
                        try { o.put("quality", v.getQuality()); } catch (Exception ignored) {}
                        arr.put(o);
                    }
                }
                out.put("voices", arr);
            } catch (Exception ignored) {}
            return out.toString();
        }

        @JavascriptInterface public boolean setVoice(String name) {
            try {
                for (Voice v : tts.getVoices()) {
                    if (v.getName().equals(name)) {
                        if (tts.setVoice(v) == TextToSpeech.SUCCESS) {
                            getSharedPreferences("study", MODE_PRIVATE).edit().putString("voice", name).apply();
                            return true;
                        }
                    }
                }
            } catch (Exception ignored) {}
            return false;
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
        private int voiceScore(Voice v) {
            int score = 0;
            try { score += v.getQuality() * 10; } catch (Exception ignored) {}
            if (!v.isNetworkConnectionRequired()) score += 1000; else score -= 500;
            try { if (v.getLatency() <= 300) score += 20; } catch (Exception ignored) {}
            return score;
        }

        private void applyVoice() {
            try {
                String saved = getSharedPreferences("study", MODE_PRIVATE).getString("voice", "");
                Voice best = null;
                for (Voice v : tts.getVoices()) {
                    if (v.getLocale() == null || !"en".equals(v.getLocale().getLanguage())) continue;
                    if (!saved.isEmpty() && v.getName().equals(saved)) { tts.setVoice(v); return; }
                    if (best == null || voiceScore(v) > voiceScore(best)) best = v;
                }
                if (best != null) tts.setVoice(best);
            } catch (Exception ignored) {}
        }

    private byte[] readBundledImage(String path) throws IOException {
        // Read the actual APK entry without relying on AssetManager's image mapping.
        try (ZipFile apk = new ZipFile(getApplicationInfo().sourceDir)) {
            ZipEntry entry = apk.getEntry("assets/" + path);
            if (entry != null) {
                try (InputStream in = apk.getInputStream(entry)) { return readImageBytes(in); }
            }
        } catch (IOException e) {
            // AssetManager also covers split-install asset locations.
        }
        try (InputStream in = getAssets().open(path)) { return readImageBytes(in); }
    }
    private static byte[] readImageBytes(InputStream in) throws IOException {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        byte[] buffer = new byte[8192]; int count;
        while ((count = in.read(buffer)) != -1) {
            if (out.size() + count > 16_000_000) throw new IOException("image too large");
            out.write(buffer, 0, count);
        }
        if (out.size() == 0) throw new IOException("empty image");
        return out.toByteArray();
    }
    private void deliverImage(String token, String data, String error) {
        runOnUiThread(() -> {
            if (isFinishing() || isDestroyed()) return;
            web.evaluateJavascript("window.receiveNativeImage && window.receiveNativeImage(" + JSONObject.quote(token) + "," + JSONObject.quote(data) + "," + JSONObject.quote(error) + ")", null);
        });
    }
    private void pickFile(int code) {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.setType("*/*"); intent.addCategory(Intent.CATEGORY_OPENABLE);
        startActivityForResult(intent,code);
    }
    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode,resultCode,data);
        if(resultCode != RESULT_OK || data == null || data.getData() == null) return;
        Uri uri = data.getData();
        new Thread(() -> {
            try {
                if (requestCode == SAVE_BACKUP) {
                    try (OutputStream out = getContentResolver().openOutputStream(uri)) { out.write(pendingExport.getBytes(StandardCharsets.UTF_8)); }
                    pendingExport = "";
                    runOnUiThread(() -> Toast.makeText(this,"学习备份已保存",Toast.LENGTH_SHORT).show());
                } else {
                    String text;
                    try(InputStream in = getContentResolver().openInputStream(uri); ByteArrayOutputStream out = new ByteArrayOutputStream()) {
                        byte[] bytes = new byte[8192]; int n;
                        while((n = in.read(bytes)) != -1) { out.write(bytes,0,n); if(out.size() > 20_000_000) throw new IOException("文件超过 20 MB，请选择词表 JSON 或 CSV"); }
                        text = out.toString("UTF-8");
                    }
                    final String js = "window.receiveFile(" + JSONObject.quote(text) + "," + (requestCode == OPEN_BACKUP ? "true" : "false") + ")";
                    runOnUiThread(() -> web.evaluateJavascript(js,null));
                }
            } catch(Exception e) { runOnUiThread(() -> Toast.makeText(this,"未能读取文件，请选择 UTF-8 编码的 JSON 或 CSV 词表",Toast.LENGTH_LONG).show()); }
        }).start();
    }
    @Override public void onBackPressed() { web.evaluateJavascript("window.handleBack && window.handleBack()", result -> { if (!"true".equals(result)) super.onBackPressed(); }); }
    @Override protected void onDestroy() { imageWorker.shutdownNow(); if(tts!=null) tts.shutdown(); if(web!=null) web.destroy(); super.onDestroy(); }
}
