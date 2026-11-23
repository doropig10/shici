import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(r"E:\单词")
PY = sys.executable
NODE = Path(r"C:\Users\ASUS\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe")
BOOK = ROOT / "app/src/main/assets/book-data.js"
MANIFEST = ROOT / "app/src/main/AndroidManifest.xml"

before = json.loads(BOOK.read_text(encoding="utf-8").split("=", 1)[1].strip().rstrip(";"))
old_ids = {w["id"]: w["word"] for w in before["words"]}

print(subprocess.run([PY, str(ROOT / "_pdftools/build_book_rich.py")], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.strip())

after = json.loads(BOOK.read_text(encoding="utf-8").split("=", 1)[1].strip().rstrip(";"))
new_ids = {w["id"]: w["word"] for w in after["words"]}
added = [new_ids[i] for i in new_ids if i not in old_ids]
removed = [old_ids[i] for i in old_ids if i not in new_ids]
print("words:", len(after["words"]), "added:", len(added), "removed:", len(removed))
print("added:", added[:20])
print("removed:", removed[:20])

xml = MANIFEST.read_text(encoding="utf-8")
xml = re.sub(r'android:versionCode="\d+"', 'android:versionCode="12"', xml)
xml = re.sub(r'android:versionName="[^"]+"', 'android:versionName="1.0.11"', xml)
MANIFEST.write_text(xml, encoding="utf-8", newline="\n")

r = subprocess.run([PY, str(ROOT / "_pdftools/build_staged.py")], capture_output=True, text=True, encoding="utf-8", errors="replace")
print("\n".join([l for l in (r.stdout + r.stderr).splitlines() if any(k in l for k in ("PACKED", "APK:", "SHA256", "Verified using v2"))]))
r = subprocess.run([str(NODE), str(ROOT / "_pdftools/shot.cjs")], capture_output=True, text=True, encoding="utf-8", errors="replace")
print(r.stdout.strip()[-200:])

