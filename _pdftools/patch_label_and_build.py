import json, subprocess, sys
from pathlib import Path

ROOT = Path(r"E:\单词")
APP = ROOT / "app/src/main/assets/app.js"
s = APP.read_text(encoding="utf-8")
old = ":'我的词表 · '+book().title;"
new = ":chapterLabel(w)||('我的词表 · '+book().title);"
if new in s:
    print("already patched")
elif old in s:
    APP.write_text(s.replace(old, new), encoding="utf-8", newline="\n")
    print("patched source label")
else:
    print("pattern not found")
    sys.exit(5)

r = subprocess.run([sys.executable, str(ROOT / "_pdftools/build_staged.py")], capture_output=True, text=True)
tail = [ln for ln in (r.stdout + r.stderr).splitlines() if any(k in ln for k in ("PACKED", "APK:", "SHA256", "Verified using v2", "Verifies", "rror"))]
print("\n".join(tail[-12:]))
sys.exit(r.returncode)
