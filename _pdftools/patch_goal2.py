import re, subprocess, sys
from pathlib import Path

ROOT = Path(r"E:\单词")
ASSETS = ROOT / "app/src/main/assets"
APPJS = ASSETS / "app.js"
CORE = ASSETS / "core.js"
NODE = Path(r"C:\Users\ASUS\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe")

js = APPJS.read_text(encoding="utf-8")
old_fn = ("function setGoal(n){state.goal=Math.max(1,Math.min(200,Math.round(Number(n))||20));"
          "save();render();toast('每日新词：'+state.goal+' 个');}")
new_fn = ("function setGoal(n){const v=Math.round(Number(n));"
          "state.goal=Number.isFinite(v)?Math.min(500,Math.max(1,v)):20;"
          "save();render();toast('每日新词：'+state.goal+' 个');}")
assert old_fn in js, "setGoal not found"
js = js.replace(old_fn, new_fn, 1)
js = js.replace('min="1" max="200"', 'min="1" max="500"', 1)
js = js.replace("到期复习会优先安排", "每日 1–500 个，到期复习优先", 1)
APPJS.write_text(js, encoding="utf-8", newline="\n")

core = CORE.read_text(encoding="utf-8")
if "Math.min(200,Number(s.goal)" in core:
    CORE.write_text(core.replace("Math.min(200,Number(s.goal)", "Math.min(500,Number(s.goal)"),
                    encoding="utf-8", newline="\n")
    print("core clamp -> 500")
print("app.js updated")

for f in (APPJS, CORE):
    r = subprocess.run([str(NODE), "--check", str(f)], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[:800]); sys.exit(4)
print("syntax ok")
