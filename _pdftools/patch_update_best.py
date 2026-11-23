from pathlib import Path

main = Path(r"E:\单词\app\src\main\java\cn\shici\wordbook\MainActivity.java")
s = main.read_text(encoding="utf-8")

s = s.replace("import java.util.Locale;", "import java.util.ArrayList;\nimport java.util.List;\nimport java.util.Locale;", 1)

old = '''                String json = null, error = "";
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
                }
                final String payload = json, err = error;
                runOnUiThread(() -> web.evaluateJavascript(
                    "window.receiveUpdate && window.receiveUpdate(" + JSONObject.quote(err.isEmpty() && payload != null ? payload : "")
                    + "," + JSONObject.quote(err) + ")", null));'''

new = '''                List<String> bodies = new ArrayList<>();
                List<String> errors = new ArrayList<>();
                long stamp = System.currentTimeMillis();
                for (String url : UPDATE_URLS) {
                    try {
                        String u = url + (url.contains("?") ? "&" : "?") + "t=" + stamp;
                        HttpURLConnection c = (HttpURLConnection) new URL(u).openConnection();
                        c.setConnectTimeout(6000); c.setReadTimeout(6000);
                        c.setRequestProperty("Accept", "application/json");
                        c.setRequestProperty("Cache-Control", "no-cache");
                        if (c.getResponseCode() != 200) throw new IOException("HTTP " + c.getResponseCode());
                        try (InputStream in = c.getInputStream()) {
                            ByteArrayOutputStream out = new ByteArrayOutputStream();
                            byte[] buf = new byte[8192]; int n;
                            while ((n = in.read(buf)) != -1) { out.write(buf, 0, n); if (out.size() > 200_000) break; }
                            bodies.add(out.toString("UTF-8"));
                        }
                    } catch (Exception e) { errors.add(e.getClass().getSimpleName() + ": " + e.getMessage()); }
                }
                StringBuilder arr = new StringBuilder("[");
                for (String b : bodies) { if (arr.length() > 1) arr.append(','); arr.append(JSONObject.quote(b)); }
                arr.append(']');
                final String payload = arr.toString(), err = String.join(" / ", errors);
                runOnUiThread(() -> web.evaluateJavascript(
                    "window.receiveUpdate && window.receiveUpdate(" + JSONObject.quote(payload)
                    + "," + JSONObject.quote(err) + ")", null));'''
assert old in s, "checkUpdate body not found"
s = s.replace(old, new, 1)
main.write_text(s, encoding="utf-8", newline="\n")
print("MainActivity: multi-source + cache-buster")

js_path = Path(r"E:\单词\app\src\main\assets\app.js")
js = js_path.read_text(encoding="utf-8")
old_js = '''window.receiveUpdate=function(raw,err){
  if(err){toast('检查更新失败：'+err);return;}
  let info=null;try{info=JSON.parse(raw||'{}');}catch(e){toast('更新信息格式不对');return;}
  const cur=appVersion(),curCode=Number((cur.split('|')[1]||'0'));
  if(!info||!info.versionCode||Number(info.versionCode)<=curCode){toast('已是最新版本 '+appVersionName());return;}
  window.__update=info;'''
new_js = '''window.receiveUpdate=function(raw,err){
  let list=[];try{list=JSON.parse(raw||'[]');}catch(e){list=[];}
  if(!Array.isArray(list))list=[];
  let info=null;
  for(const s of list){
    try{const it=JSON.parse(s);if(it&&it.versionCode&&(!info||Number(it.versionCode)>Number(info.versionCode)))info=it;}catch(e){}
  }
  if(!info){toast(err?('检查更新失败：'+err):'检查更新失败，请稍后再试');return;}
  const cur=appVersion(),curCode=Number((cur.split('|')[1]||'0'));
  if(Number(info.versionCode)<=curCode){toast('已是最新版本 '+appVersionName());return;}
  window.__update=info;'''
assert old_js in js, "receiveUpdate not found"
js = js.replace(old_js, new_js, 1)
js_path.write_text(js, encoding="utf-8", newline="\n")
print("app.js: pick highest versionCode")
