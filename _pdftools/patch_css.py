import json, re
from pathlib import Path

ROOT = Path(r"E:\单词")
CSS = ROOT / "app/src/main/assets/style.css"
BOOK = ROOT / "app/src/main/assets/book-data.js"
MANIFEST = ROOT / "app/src/main/AndroidManifest.xml"

css = CSS.read_text(encoding="utf-8")
old = ".definition{font-size:18px;line-height:1.8;margin:16px 0;word-break:break-word}"
new = ".definition{font-size:17px;line-height:1.85;margin:16px 0;word-break:break-word;white-space:pre-line;text-align:left;width:100%}"
assert old in css, "definition rule not found"
CSS.write_text(css.replace(old, new), encoding="utf-8", newline="\n")

raw = BOOK.read_text(encoding="utf-8")
body = json.loads(raw.split("=", 1)[1].strip().rstrip(";"))
body["subtitle"] = "刘晓燕 · 六级 · 讲义词条"
BOOK.write_text("window.BOOK_DATA = " + json.dumps(body, ensure_ascii=False, separators=(",", ":")) + ";\n",
                encoding="utf-8", newline="\n")

xml = MANIFEST.read_text(encoding="utf-8")
xml = re.sub(r'android:versionCode="\d+"', 'android:versionCode="9"', xml)
xml = re.sub(r'android:versionName="[^"]+"', 'android:versionName="1.0.8"', xml)
MANIFEST.write_text(xml, encoding="utf-8", newline="\n")
print("patched css, subtitle, version 1.0.8")
