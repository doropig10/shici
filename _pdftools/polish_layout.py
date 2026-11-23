import re, subprocess, sys
from pathlib import Path

ROOT = Path(r"E:\单词")
APPJS = ROOT / "app/src/main/assets/app.js"
CSS = ROOT / "app/src/main/assets/style.css"
MANIFEST = ROOT / "app/src/main/AndroidManifest.xml"
NODE = Path(r"C:\Users\ASUS\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe")

js = APPJS.read_text(encoding="utf-8")
old = '<div class="word-large">${esc(w.word)}</div>${action(\'speak\',icon(\'sound\'),\'sound\',`data-word="${esc(w.word)}" aria-label="朗读单词"`)}'
new = '<div class="word-line"><div class="word-large">${esc(w.word)}</div>${action(\'speak\',icon(\'sound\'),\'sound\',`data-word="${esc(w.word)}" aria-label="朗读单词"`)}</div>'
if "word-line" not in js:
    assert old in js, "study word markup not found"
    js = js.replace(old, new, 1)
    APPJS.write_text(js, encoding="utf-8", newline="\n")
    print("app.js: word-line wrapped")

r = subprocess.run([str(NODE), "--check", str(APPJS)], capture_output=True, text=True)
if r.returncode != 0:
    print(r.stderr[:800])
    sys.exit(4)

css = CSS.read_text(encoding="utf-8")
if ".word-line{" not in css:
    css = css.replace(".chips{display:flex;gap:7px;overflow-x:auto;padding:0 0 14px;scrollbar-width:none}",
                      ".chips{display:flex;flex-wrap:wrap;gap:7px;padding:0 0 14px}")
    css += (
        "\n.word-line{display:flex;align-items:center;justify-content:center;gap:12px;margin:18px 0 4px;width:100%}"
        "\n.word-line .word-large{margin:0}"
        "\n.word-line .sound{margin:0}"
    )
    CSS.write_text(css, encoding="utf-8", newline="\n")
    print("css: word-line + chips wrap")

xml = MANIFEST.read_text(encoding="utf-8")
xml = re.sub(r'android:versionCode="\d+"', 'android:versionCode="10"', xml)
xml = re.sub(r'android:versionName="[^"]+"', 'android:versionName="1.0.9"', xml)
MANIFEST.write_text(xml, encoding="utf-8", newline="\n")

print(subprocess.run([sys.executable, str(ROOT / "_pdftools/build_staged.py")],
                     capture_output=True, text=True).stdout[-600:])
print(subprocess.run([str(NODE), str(ROOT / "_pdftools/shot.cjs")],
                     capture_output=True, text=True).stdout[-200:])
