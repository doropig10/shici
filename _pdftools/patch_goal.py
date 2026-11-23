import re, subprocess, sys
from pathlib import Path

ROOT = Path(r"E:\单词")
ASSETS = ROOT / "app/src/main/assets"
APPJS = ASSETS / "app.js"
CORE = ASSETS / "core.js"
CSS = ASSETS / "style.css"
MANIFEST = ROOT / "app/src/main/AndroidManifest.xml"
NODE = Path(r"C:\Users\ASUS\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe")

js = APPJS.read_text(encoding="utf-8")

old_select = ('<select id="goal" aria-label="每日新词数量">${[5,10,15,20,30,50,80,100].map(n=>'
              '`<option value="${n}" ${n===state.goal?\'selected\':\'\'}>${n} 词</option>`).join(\'\')}</select></div>')
new_select = ('<div class="goal-editor"><button class="goal-step" data-act="goal-step" data-step="-5" aria-label="减少五个">−</button>'
              '<input id="goal" type="number" inputmode="numeric" min="1" max="200" step="1" value="${state.goal}" aria-label="每日新词数量">'
              '<button class="goal-step" data-act="goal-step" data-step="5" aria-label="增加五个">+</button></div></div>'
              '<div class="goal-presets">${[5,10,20,30,50,100].map(n=>`<button class="chip ${n===state.goal?\'selected\':\'\'}" data-act="goal-set" data-n="${n}">${n}</button>`).join(\'\')}</div>')

if "goal-editor" not in js:
    assert old_select in js, "goal select not found"
    js = js.replace(old_select, new_select, 1)

    helper = ("function setGoal(n){state.goal=Math.max(1,Math.min(200,Math.round(Number(n))||20));"
              "save();render();toast('每日新词：'+state.goal+' 个');}\n")
    js = js.replace("function settings(){", helper + "function settings(){", 1)

    anchor = "else if(a==='filter'){filter=b.dataset.filter;limit=60;render();}"
    assert anchor in js
    js = js.replace(anchor, anchor + "\n else if(a==='goal-step'){setGoal(Number(state.goal)+Number(b.dataset.step));}"
                                  "\n else if(a==='goal-set'){setGoal(Number(b.dataset.n));}", 1)

    old_change = "else if(e.target.id==='goal'){state.goal=Number(e.target.value);save();toast('每日新词目标已更新');}"
    assert old_change in js
    new_change = "else if(e.target.id==='goal'){setGoal(e.target.value);}"
    js = js.replace(old_change, new_change, 1)

    js = js.replace("拾词 1.0.5 · 只收录你给的词书", "拾词 1.0.10 · 只收录你给的词书", 1)
    APPJS.write_text(js, encoding="utf-8", newline="\n")
    print("app.js: goal editor")

core = CORE.read_text(encoding="utf-8")
old_clamp = "goal:Math.max(5,Math.min(100,Number(s.goal)||20))"
if old_clamp in core:
    CORE.write_text(core.replace(old_clamp, "goal:Math.max(1,Math.min(200,Number(s.goal)||20))"),
                    encoding="utf-8", newline="\n")
    print("core.js: clamp 1..200")

css = CSS.read_text(encoding="utf-8")
if ".goal-editor{" not in css:
    css += (
        "\n.goal-editor{display:flex;align-items:center;gap:8px}"
        "\n.goal-step{width:34px;height:34px;border-radius:11px;background:var(--lav);color:var(--purple);font-size:19px;font-weight:700;line-height:1}"
        "\n.goal-editor input{width:66px;padding:7px 4px;text-align:center;border:1px solid var(--line);border-radius:11px;background:var(--bg);font-size:16px;font-weight:700;color:var(--ink);-moz-appearance:textfield}"
        "\n.goal-editor input::-webkit-outer-spin-button,.goal-editor input::-webkit-inner-spin-button{-webkit-appearance:none;margin:0}"
        "\n.goal-presets{display:flex;flex-wrap:wrap;gap:8px;padding:0 0 6px;margin-top:-6px}"
    )
    CSS.write_text(css, encoding="utf-8", newline="\n")
    print("css: goal editor styles")

xml = MANIFEST.read_text(encoding="utf-8")
xml = re.sub(r'android:versionCode="\d+"', 'android:versionCode="11"', xml)
xml = re.sub(r'android:versionName="[^"]+"', 'android:versionName="1.0.10"', xml)
MANIFEST.write_text(xml, encoding="utf-8", newline="\n")

r = subprocess.run([str(NODE), "--check", str(APPJS)], capture_output=True, text=True)
if r.returncode != 0:
    print(r.stderr[:900])
    sys.exit(4)
r = subprocess.run([str(NODE), "--check", str(CORE)], capture_output=True, text=True)
if r.returncode != 0:
    print(r.stderr[:900])
    sys.exit(4)
print("syntax ok")
