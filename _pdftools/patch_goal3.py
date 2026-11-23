import subprocess, sys
from pathlib import Path

ROOT = Path(r"E:\单词")
ASSETS = ROOT / "app/src/main/assets"
APPJS = ASSETS / "app.js"
CSS = ASSETS / "style.css"
NODE = Path(r"C:\Users\ASUS\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe")

js = APPJS.read_text(encoding="utf-8")
if "goal-setting" not in js:
    old = '<div class="setting"><div><b>每日新词</b>'
    assert old in js
    js = js.replace(old, '<div class="setting goal-setting"><div><b>每日新词</b>', 1)
    APPJS.write_text(js, encoding="utf-8", newline="\n")
    print("app.js: goal-setting class")

css = CSS.read_text(encoding="utf-8")
old_css = "\n.goal-presets{display:flex;flex-wrap:wrap;gap:8px;padding:0 0 6px;margin-top:-6px}"
new_css = ("\n.goal-setting{border-bottom:0;padding-bottom:8px}"
           "\n.goal-presets{display:flex;flex-wrap:wrap;gap:8px;padding:0 18px 16px;border-bottom:1px solid var(--line);margin:0}")
assert old_css in css, "goal-presets rule not found"
CSS.write_text(css.replace(old_css, new_css), encoding="utf-8", newline="\n")
print("css: presets spacing")

for f in (APPJS,):
    r = subprocess.run([str(NODE), "--check", str(f)], capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[:600]); sys.exit(4)
print("ok")
