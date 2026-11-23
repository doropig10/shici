"""git 走不通时的发布办法：全部走 GitHub API（release + contents）。"""
import base64, json, subprocess, sys
from pathlib import Path

ROOT = Path(r"E:\单词")
GH = r"C:\Program Files\GitHub CLI\gh.exe"
REPO = "doropig10/shici"

version = sys.argv[1]
code = sys.argv[2]
notes = sys.argv[3] if len(sys.argv) > 3 else ""
apk = ROOT / f"shici-{version}.apk"
tag = f"v{version}"

vj = json.loads((ROOT / "version.json").read_text(encoding="utf-8"))


def gh(*args):
    return subprocess.run([GH, *args], capture_output=True, text=True, encoding="utf-8", errors="replace")


# 1) release（含 APK 与 version.json 资产）
view = gh("release", "view", tag, "--repo", REPO)
if view.returncode != 0:
    r = gh("release", "create", tag, str(apk), str(ROOT / "version.json"), "--repo", REPO,
           "--title", f"拾词 {version}", "--notes", notes or f"拾词 {version}")
    print("release:", "ok" if r.returncode == 0 else r.stderr.strip()[:200])
else:
    r = gh("release", "upload", tag, str(apk), str(ROOT / "version.json"), "--repo", REPO, "--clobber")
    print("release upload:", "ok" if r.returncode == 0 else r.stderr.strip()[:200])

# 2) 用 API 更新仓库里的 version.json 与 APK（jsDelivr 兜底用）
def put(path, data: bytes, message):
    body = {
        "message": message,
        "content": base64.b64encode(data).decode(),
        "branch": "main",
    }
    cur = gh("api", f"/repos/{REPO}/contents/{path}", "--jq", ".sha")
    if cur.returncode == 0 and cur.stdout.strip():
        body["sha"] = cur.stdout.strip()
    tmp = ROOT / "_pdftools/_put_body.json"
    tmp.write_text(json.dumps(body), encoding="utf-8")
    r = gh("api", "-X", "PUT", f"/repos/{REPO}/contents/{path}", "--input", str(tmp))
    tmp.unlink(missing_ok=True)
    print(path, "->", "ok" if r.returncode == 0 else r.stderr.strip()[:200])


put("version.json", (ROOT / "version.json").read_bytes(), f"chore: version.json -> {version}")
put(apk.name, apk.read_bytes(), f"build: {apk.name}")
print("done", tag, vj.get("sha256"))
