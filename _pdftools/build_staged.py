import os, re, shutil, subprocess, zipfile, json, hashlib, sys
from pathlib import Path

ROOT = Path(r"E:\单词")
STAGE = Path(os.environ["TEMP"]) / "shici_build"
SRC = ROOT / "app/src/main"
STAGE_SRC = STAGE / "src/main"
TOOLING = ROOT / ".tooling"
BUILD = STAGE / "build"
OUT = STAGE / "out"

for d in (BUILD, BUILD / "classes", BUILD / "dex", OUT, STAGE):
    d.mkdir(parents=True, exist_ok=True)

if False:
    r = subprocess.run(["cmd", "/c", "mklink", "/J", str(TOOLING), str(ROOT / ".tooling")],
                       capture_output=True, text=True)
    print("junction:", r.returncode, (r.stdout or r.stderr).strip())

BT = TOOLING / "android/build-tools/android-15"
JAR = STAGE / "android.jar"
JAVA = Path(r"D:\app\PyCharm 2025.2\jbr\bin")

if STAGE_SRC.exists():
    shutil.rmtree(STAGE_SRC)
print("staging assets ...", flush=True)
shutil.copyfile(TOOLING / "android/platform/android-35/android.jar", JAR)
shutil.copyfile(TOOLING / "shici-release.jks", STAGE / "shici-release.jks")
shutil.copytree(SRC, STAGE_SRC, dirs_exist_ok=True)


def run(args, cwd=STAGE):
    print("+", " ".join(str(a) for a in args[-3:]), flush=True)
    subprocess.run([str(a) for a in args], check=True, cwd=str(cwd))


run([BT / "aapt2.exe", "compile", "--dir", STAGE_SRC / "res", "-o", BUILD / "resources.zip"])
run([BT / "aapt2.exe", "link", "-o", BUILD / "base.apk", "-I", JAR,
     "--manifest", STAGE_SRC / "AndroidManifest.xml", BUILD / "resources.zip",
     "-A", STAGE_SRC / "assets", "--min-sdk-version", "26", "--target-sdk-version", "35"])
run([JAVA / "javac.exe", "-encoding", "UTF-8", "-source", "8", "-target", "8",
     "-classpath", JAR, "-d", BUILD / "classes", *STAGE_SRC.glob("java/**/*.java")])
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

key = STAGE / "shici-release.jks"
version = re.search(r'android:versionName="([^"]+)"', (STAGE_SRC / "AndroidManifest.xml").read_text(encoding="utf-8")).group(1)
password = json.loads((TOOLING / "signing.json").read_text(encoding="utf-8"))["password"]
apk = OUT / f"shici-{version}.apk"
run([JAVA / "java.exe", "-jar", BT / "lib/apksigner.jar", "sign", "--ks", key,
     "--ks-key-alias", "shici", "--ks-pass", "pass:" + password,
     "--key-pass", "pass:" + password, "--out", apk, BUILD / "aligned.apk"])
r = subprocess.run([str(JAVA / "java.exe"), "-jar", str(BT / "lib/apksigner.jar"), "verify", "--verbose", str(apk)],
                   capture_output=True, text=True)
print(r.stdout.strip()[:600])
if r.returncode != 0:
    print(r.stderr[:800])
    sys.exit(4)

with zipfile.ZipFile(apk) as archive:
    assert archive.testzip() is None
    packed = json.loads(archive.read("assets/book-data.js").decode("utf-8").split("=", 1)[1].strip().rstrip(";"))
    print("PACKED words:", len(packed["words"]))
    print("PACKED with card:", sum(1 for w in packed["words"] if w.get("card")))

dest = ROOT / f"shici-{version}.apk"
shutil.copyfile(apk, dest)
sha = hashlib.sha256(dest.read_bytes()).hexdigest()
(ROOT / f"shici-{version}.sha256.txt").write_text(sha + "  " + dest.name + "\n", encoding="utf-8")
print("APK:", dest, "MB:", round(dest.stat().st_size / 1024 / 1024, 1))
print("SHA256:", sha)




