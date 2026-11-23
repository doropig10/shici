import json, re, subprocess, sys
from collections import Counter
from pathlib import Path

ROOT = Path(r"E:\单词")
version = sys.argv[1] if len(sys.argv) > 1 else "1.0.14"
code = sys.argv[2] if len(sys.argv) > 2 else "15"

m = ROOT / "app/src/main/AndroidManifest.xml"
s = m.read_text(encoding="utf-8")
s = re.sub(r'android:versionCode="\d+"', f'android:versionCode="{code}"', s)
s = re.sub(r'android:versionName="[^"]+"', f'android:versionName="{version}"', s)
m.write_text(s, encoding="utf-8")

b = json.loads((ROOT / "app/src/main/assets/book-data.js").read_text(encoding="utf-8").split("=", 1)[1].strip().rstrip(";"))
w = b["words"]
print("words:", len(w), "units:", [u["number"] for u in b["structure"]["units"]])
print("per lesson:", sorted(Counter((x["unit"], x["lesson"]) for x in w).items()))
print("with phonetic:", sum(1 for x in w if x["phonetic"]), "with blocks:", sum(1 for x in w if x["entry"]))

r = subprocess.run([sys.executable, str(ROOT / "_pdftools/build_staged.py")],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
for line in (r.stdout + r.stderr).splitlines():
    if any(k in line for k in ("PACKED", "APK:", "SHA256", "Verified using v2")):
        print(line)
