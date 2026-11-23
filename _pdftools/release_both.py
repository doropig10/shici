"""双平台发布：Gitee（首选）+ GitHub（备用）+ jsDelivr（镜像）。

用法：python _pdftools/release_both.py 1.0.40 41 "说明"
"""
import base64, hashlib, json, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(r"E:\单词")
GH = r"C:\Program Files\GitHub CLI\gh.exe"
GH_REPO = "doropig10/shici"
GITEE_REPO = "doro_pig/shici"
GITEE_WORK = ROOT / "_pdftools/gitee_repo"

version = sys.argv[1]
code = sys.argv[2]
notes = sys.argv[3] if len(sys.argv) > 3 else ""
apk = ROOT / f"shici-{version}.apk"
tag = f"v{version}"

sha = hashlib.sha256(apk.read_bytes()).hexdigest()
size = apk.stat().st_size

info = {
    "versionCode": int(code),
    "versionName": version,
    "apk": f"https://gitee.com/{GITEE_REPO}/raw/master/{apk.name}",
    "apkFallback": f"https://github.com/{GH_REPO}/releases/download/{tag}/{apk.name}",
    "apkMirror": f"https://cdn.jsdelivr.net/gh/{GH_REPO}@main/{apk.name}",
    "sha256": sha,
    "size": size,
    "notes": notes,
}
(ROOT / "version.json").write_text(json.dumps(info, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def run(cmd, cwd=None, check=False):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       cwd=str(cwd) if cwd else None)
    if check and r.returncode != 0:
        raise SystemExit(f"命令失败: {' '.join(cmd)}\n{r.stderr[:400]}")
    return r


# 1) Gitee：clone/pull、提交 APK + version.json、push master
if not GITEE_WORK.exists():
    run(["git", "clone", f"https://gitee.com/{GITEE_REPO}.git", str(GITEE_WORK)], check=True)
else:
    run(["git", "fetch", "origin"], cwd=GITEE_WORK)
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=GITEE_WORK).stdout.strip()
    if run(["git", "rev-parse", "--verify", "HEAD"], cwd=GITEE_WORK).returncode == 0:
        run(["git", "reset", "--hard", f"origin/{branch or 'master'}"], cwd=GITEE_WORK)

shutil.copyfile(apk, GITEE_WORK / apk.name)
(GITEE_WORK / "version.json").write_text((ROOT / "version.json").read_text(encoding="utf-8"), encoding="utf-8")
run(["git", "add", "-A"], cwd=GITEE_WORK)
run(["git", "-c", "user.name=doro_pig", "-c", "user.email=doropig@users.noreply.gitee.com",
     "commit", "-m", f"build: 拾词 {version}"], cwd=GITEE_WORK)
push = run(["git", "push", "origin", "HEAD:master"], cwd=GITEE_WORK)
print("gitee push:", "ok" if push.returncode == 0 else (push.stderr.strip()[:200] or "already up to date"))

# 2) GitHub：Release + 仓库文件（git 不通就走 API）
gh = lambda *a: run([GH, *a])
view = gh("release", "view", tag, "--repo", GH_REPO)
if view.returncode != 0:
    r = gh("release", "create", tag, str(apk), str(ROOT / "version.json"), "--repo", GH_REPO,
           "--title", f"拾词 {version}", "--notes", notes or f"拾词 {version}")
else:
    r = gh("release", "upload", tag, str(apk), str(ROOT / "version.json"), "--repo", GH_REPO, "--clobber")
print("github release:", "ok" if r.returncode == 0 else r.stderr.strip()[:200])


def put(path, data: bytes, message):
    body = {"message": message, "content": base64.b64encode(data).decode(), "branch": "main"}
    cur = gh("api", f"/repos/{GH_REPO}/contents/{path}", "--jq", ".sha")
    if cur.returncode == 0 and cur.stdout.strip():
        body["sha"] = cur.stdout.strip()
    tmp = ROOT / "_pdftools/_put_body.json"
    tmp.write_text(json.dumps(body), encoding="utf-8")
    r = gh("api", "-X", "PUT", f"/repos/{GH_REPO}/contents/{path}", "--input", str(tmp))
    tmp.unlink(missing_ok=True)
    print(path, "->", "ok" if r.returncode == 0 else r.stderr.strip()[:160])


put("version.json", (ROOT / "version.json").read_bytes(), f"chore: version.json -> {version}")
put(apk.name, apk.read_bytes(), f"build: {apk.name}")

print("apk:", info["apk"])
print("sha256:", sha, "size:", size)
