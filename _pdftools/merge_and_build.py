import json, re, shutil, subprocess, sys, zipfile, hashlib, secrets
from pathlib import Path
from collections import Counter, defaultdict
import xml.etree.ElementTree as ET

ROOT = Path(r"E:\单词")
ASSETS = ROOT / "app/src/main/assets"
BOOK = ASSETS / "book-data.js"
MANIFEST = ROOT / "app/src/main/AndroidManifest.xml"
NOTES = ROOT / "_pdftools/notes_entries.json"
IMPORT_JSON = ROOT / "刘晓艳六级词汇_精讲18课_导入.json"
BACKUP = ROOT / "_pdftools/book-data.orig.js"

JAVA = Path(r"D:\app\PyCharm 2025.2\jbr\bin")
SDK = ROOT / ".tooling/android"
BT = SDK / "build-tools/android-15"
JAR = SDK / "platform/android-35/android.jar"
BUILD = ROOT / "_pdftools/build"
OUT_APK = ROOT / "shici-1.0.6.apk"

# 0. probe write access to the app assets directory
probe = ASSETS / "_write_probe.tmp"
try:
    probe.write_text("x", encoding="utf-8")
    probe.unlink()
    print("PROBE ok: assets writable")
except Exception as e:
    print("PROBE denied:", e)
    sys.exit(3)

# 1. merge md entries into book-data.js
if not BACKUP.exists():
    shutil.copyfile(BOOK, BACKUP)
raw = BOOK.read_text(encoding="utf-8")
head, body = raw.split("=", 1)
body = body.strip()
assert body.endswith(";")
data = json.loads(body[:-1])
words = data["words"]

notes = json.load(open(NOTES, encoding="utf-8"))
imp = json.load(open(IMPORT_JSON, encoding="utf-8"))
composed = {w["word"].lower(): w["meaning"] for w in imp["words"]}
by_word = {w["word"].lower(): w for w in words}
by_exact = {(w["word"].lower(), w["unit"], w["lesson"]): w for w in words}

file_scope = {}
for e in notes:
    hit = by_word.get(e["word"].lower())
    if hit:
        file_scope.setdefault(e["file"], Counter())[(hit["unit"], hit["lesson"])] += 1
file_scope = {k: v.most_common(1)[0][0] for k, v in file_scope.items()}

new_words, updated, skipped = [], 0, 0
for e in notes:
    key = e["word"].lower()
    meaning = composed.get(key)
    if not meaning:
        skipped += 1
        continue
    unit, lesson = file_scope.get(e["file"], (e["unit"], e["lesson"]))
    target = by_exact.get((key, unit, lesson)) or by_word.get(key)
    if target is not None:
        if target.get("meaning") != meaning:
            target["meaning"] = meaning
            updated += 1
    elif key not in {w["id"] for w in new_words}:
        new_words.append({
            "id": key, "word": e["word"].strip(), "meaning": meaning,
            "page": None, "position": None, "printedPage": None,
            "section": "core", "card": None, "indexPage": None,
            "cardRegions": [], "fullEntry": False,
            "unit": unit, "lesson": lesson, "groupId": None,
        })

anchor = {}
for i, w in enumerate(words):
    anchor[(w["unit"], w["lesson"])] = i
inserts = defaultdict(list)
appended = []
for nw in new_words:
    k = (nw["unit"], nw["lesson"])
    (inserts[anchor[k]] if k in anchor else appended).append(nw)

merged = []
for i, w in enumerate(words):
    merged.append(w)
    if i in inserts:
        merged.extend(inserts[i])
merged.extend(appended)
data["words"] = merged
book_out = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
BOOK.write_text(head + "=" + book_out + ";\n", encoding="utf-8", newline="\n")
print(f"MERGE updated={updated} added={len(new_words)} total={len(merged)}")

# 2. bump version
xml = MANIFEST.read_text(encoding="utf-8")
xml2 = re.sub(r'android:versionCode="\d+"', 'android:versionCode="7"', xml)
xml2 = re.sub(r'android:versionName="[^"]+"', 'android:versionName="1.0.6"', xml2)
if xml2 != xml:
    MANIFEST.write_text(xml2, encoding="utf-8", newline="\n")
    print("VERSION bumped to 1.0.6/6")

# 3. build
for d in (BUILD, BUILD / "classes", BUILD / "dex"):
    d.mkdir(parents=True, exist_ok=True)
src = ROOT / "app/src/main"


def run(args, cwd=ROOT):
    subprocess.run([str(a) for a in args], check=True, cwd=str(cwd))


run([BT / "aapt2.exe", "compile", "--dir", src / "res", "-o", BUILD / "resources.zip"])
run([BT / "aapt2.exe", "link", "-o", BUILD / "base.apk", "-I", JAR,
     "--manifest", src / "AndroidManifest.xml", BUILD / "resources.zip",
     "-A", src / "assets", "--min-sdk-version", "26", "--target-sdk-version", "35"])
run([JAVA / "javac.exe", "-encoding", "UTF-8", "-source", "8", "-target", "8",
     "-classpath", JAR, "-d", BUILD / "classes", *src.glob("java/**/*.java")])
run([JAVA / "java.exe", "-cp", BT / "lib/d8.jar", "com.android.tools.r8.D8",
     "--lib", JAR, "--min-api", "26", "--output", BUILD / "dex",
     *(BUILD / "classes").rglob("*.class")])
run([BT / "aapt.exe", "add", BUILD / "base.apk", *[p.name for p in (BUILD / "dex").glob("*.dex")]],
    cwd=BUILD / "dex")

with zipfile.ZipFile(BUILD / "base.apk") as source, zipfile.ZipFile(BUILD / "image-streams.apk", "w") as target:
    for entry in source.infolist():
        payload = source.read(entry)
        if entry.filename.startswith("assets/") and entry.filename.endswith(".webp"):
            entry.compress_type = zipfile.ZIP_DEFLATED
        target.writestr(entry, payload)
run([BT / "zipalign.exe", "-f", "-p", "4", BUILD / "image-streams.apk", BUILD / "aligned.apk"])

key = ROOT / ".tooling/shici-release.jks"
password = json.loads((ROOT / ".tooling/signing.json").read_text(encoding="utf-8"))["password"]
run([JAVA / "java.exe", "-jar", BT / "lib/apksigner.jar", "sign", "--ks", key,
     "--ks-key-alias", "shici", "--ks-pass", "pass:" + password,
     "--key-pass", "pass:" + password, "--out", OUT_APK, BUILD / "aligned.apk"])
run([JAVA / "java.exe", "-jar", BT / "lib/apksigner.jar", "verify", "--verbose", OUT_APK])

with zipfile.ZipFile(OUT_APK) as archive:
    assert archive.testzip() is None
    packed = json.loads(archive.read("assets/book-data.js").decode("utf-8").split("=", 1)[1].strip().rstrip(";"))
    print("PACKED words:", len(packed["words"]))
sha = hashlib.sha256(OUT_APK.read_bytes()).hexdigest()
(ROOT / "shici-1.0.6.sha256.txt").write_text(sha + "  " + OUT_APK.name + "\n", encoding="utf-8")
print("APK:", OUT_APK, "MB:", round(OUT_APK.stat().st_size / 1024 / 1024, 1), "SHA256:", sha)
