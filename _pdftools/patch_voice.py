from pathlib import Path

main = Path(r"E:\单词\app\src\main\java\cn\shici\wordbook\MainActivity.java")
s = main.read_text(encoding="utf-8")

if "listVoices" not in s:
    s = s.replace("import android.speech.tts.TextToSpeech;",
                  "import android.speech.tts.TextToSpeech;\nimport android.speech.tts.Voice;", 1)

    # 启动时选音色
    old_init = '''                tts.setSpeechRate(0.82f);'''
    new_init = '''                tts.setSpeechRate(0.82f);
                applyVoice();'''
    assert old_init in s
    s = s.replace(old_init, new_init, 1)

    # applyVoice / score 放在 installApk 之后（Bridge 内）
    anchor = '''        private void installApk() {'''
    methods = '''        private int voiceScore(Voice v) {
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

        private void installApk() {'''
    assert anchor in s
    s = s.replace(anchor, methods, 1)
    main.write_text(s, encoding="utf-8", newline="\n")
    print("MainActivity: voice selection")

js_path = Path(r"E:\单词\app\src\main\assets\app.js")
js = js_path.read_text(encoding="utf-8")

if "listVoices" not in js:
    helpers = '''function voiceInfo(){
  if(!window.Android||!Android.listVoices)return null;
  try{return JSON.parse(Android.listVoices());}catch(e){return null;}
}
function shortVoice(n){
  const p=String(n||'').split('/');
  return p[p.length-1]||'跟随系统';
}
function currentVoiceLabel(){
  const info=voiceInfo();
  if(!info||!info.current)return '跟随系统';
  return shortVoice(info.current);
}
function showVoices(){
  const info=voiceInfo();
  if(!info){toast('当前环境不支持选择音色');return;}
  const cur=info.current||'';
  const list=(info.voices||[]).map(v=>{
    const on=v.name===cur;
    return `<button class="voice-row ${on?'on':''}" data-act="set-voice" data-name="${esc(v.name)}">`
      +`<div><b>${esc(shortVoice(v.name))}</b><p>${esc(v.locale)} · ${v.network?'需联网':'本地'}${on?' · 当前':''}</p></div>`
      +`<span class="voice-mark">${on?'✓':''}</span></button>`;
  }).join('');
  showModal(`<h2>发音音色</h2><p class="sub">这些是手机语音引擎里的英文音色，选一个试试；带「需联网」的通常更自然。</p>`
    +`<div class="voice-list">${list||'<p class="sub">没有找到英文音色，请先在系统设置里安装英语语音包</p>'}</div>`
    +`<div class="modal-footer">${action('close-modal','关闭','outline')}</div>`);
}
'''
    js = js.replace("function settings(){", helpers + "function settings(){", 1)

    # 设置页新增音色入口
    old_row = "${action('check-update',`<div><b>检查更新</b>"
    new_row = ("${(window.Android&&Android.listVoices)?action('voices',`<div><b>发音音色</b><p>${esc(currentVoiceLabel())}</p></div>${icon('sound')}`,'setting'):''}"
               "${action('check-update',`<div><b>检查更新</b>")
    assert old_row in js
    js = js.replace(old_row, new_row, 1)

    # 动作分发
    anchor2 = "else if(a==='do-update'){startUpdate();}"
    assert anchor2 in js
    js = js.replace(anchor2, anchor2 + "\n else if(a==='voices'){showVoices();}"
                                 "\n else if(a==='set-voice'){if(window.Android&&Android.setVoice&&Android.setVoice(b.dataset.name)){toast('音色已切换');closeModal();render();}else{toast('切换失败，换个音色试试');}}", 1)

    js_path.write_text(js, encoding="utf-8", newline="\n")
    print("app.js: voice picker")

cdd = Path(r"E:\单词\app\src\main\assets\style.css")
css = cdd.read_text(encoding="utf-8")
if ".voice-list{" not in css:
    css += ("\n.voice-list{max-height:52vh;overflow:auto;margin:12px 0}"
            "\n.voice-row{display:flex;align-items:center;justify-content:space-between;gap:12px;width:100%;text-align:left;padding:11px 12px;border:1px solid var(--line);border-radius:12px;background:var(--paper);margin-bottom:8px}"
            "\n.voice-row b{font-size:13px}"
            "\n.voice-row p{font-size:11px;color:var(--muted);margin:3px 0 0}"
            "\n.voice-row.on{border-color:var(--purple);background:var(--lav)}"
            "\n.voice-mark{color:var(--purple);font-weight:700}")
    cdd.write_text(css, encoding="utf-8", newline="\n")
print("css: voice list")
