"""发布：APK 与 version.json 推到 GitHub（Release 备用 + 仓库内 jsDelivr CDN）。

用法：python _pdftools/release.py 1.0.26 27 "更新说明"
"""
import hashlib, json, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(r"E:\单词")
GH = r"C:\Program Files\GitHub CLI\gh.exe"
REPO = "doropig10/shici"
WORK = ROOT / "_pdftools/ghrepo"

version = sys.argv[1]
code = sys.argv[2]
notes = sys.argv[3] if len(sys.argv) > 3 else ""

apk = ROOT / f"shici-{version}.apk"
if not apk.exists():
    sys.exit(f"APK 不存在：{apk}")

sha = hashlib.sha256(apk.read_bytes()).hexdigest()
size = apk.stat().st_size
tag = f"v{version}"
release_url = f"https://github.com/{REPO}/releases/download/{tag}/shici-{version}.apk"
cdn_url = f"https://cdn.jsdelivr.net/gh/{REPO}@main/shici-{version}.apk"


info = {
    "versionCode": int(code),
    "versionName": version,
    "apk": release_url,
    "apkFallback": cdn_url,
    "sha256": sha,
    "size": size,
    "notes": notes,
}
(ROOT / "version.json").write_text(json.dumps(info, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def run(cmd, cwd=None, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd) if cwd else None)
    if check and r.returncode != 0:
        raise SystemExit(f"命令失败: {' '.join(cmd)}\n{r.stderr[:400]}")
    return r


token = run([GH, "auth", "token"]).stdout.strip()
try:
    run(["git", "ls-remote", f"https://x-access-token:{token}@github.com/{REPO}.git", "HEAD"])
except SystemExit:
    print("git 不可用，改用 GitHub API 发布")
    sys.exit(subprocess.run([sys.executable, str(ROOT / "_pdftools/release_api.py"), version, code, notes]).returncode)
if not WORK.exists():
    run(["git", "clone", f"https://x-access-token:{token}@github.com/{REPO}.git", str(WORK)])
run(["git", "remote", "set-url", "origin", f"https://x-access-token:{token}@github.com/{REPO}.git"], cwd=WORK)
run(["git", "fetch", "origin", "main"], cwd=WORK)
run(["git", "reset", "--hard", "origin/main"], cwd=WORK)

shutil.copyfile(apk, WORK / apk.name)
(WORK / "version.json").write_text(json.dumps(info, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

run(["git", "add", "-A"], cwd=WORK)
run(["git", "-c", "user.name=doropig10", "-c", "user.email=doropig10@users.noreply.github.com",
     "commit", "-m", f"build: 拾词 {version}"], cwd=WORK)
run(["git", "push", "origin", "HEAD:main"], cwd=WORK)

view = run([GH, "release", "view", tag, "--repo", REPO], check=False)
if view.returncode != 0:
    r = run([GH, "release", "create", tag, str(apk), str(WORK / "version.json"), "--repo", REPO,
             "--title", f"拾词 {version}", "--notes", notes or f"拾词 {version}"], check=False)
    print("release:", "ok" if r.returncode == 0 else r.stderr.strip()[:200])
else:
    run([GH, "release", "upload", tag, str(apk), str(ROOT / "version.json"), "--repo", REPO, "--clobber"], check=False)
    print("release: asset updated")

print("apk:", release_url)
print("cdn:", cdn_url)
print("sha256:", sha, "size:", size)
