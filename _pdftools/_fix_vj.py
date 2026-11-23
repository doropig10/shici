import hashlib, json
from pathlib import Path

ROOT = Path(r"E:\单词")
version = "1.0.38"
code = "39"
notes = "词库显示记得/模糊/忘记记录，可撤销上一次或清除该词记录"
apk = ROOT / f"shici-{version}.apk"
v = json.loads((ROOT / "version.json").read_text(encoding="utf-8"))
v.update({
    "versionCode": int(code),
    "versionName": version,
    "apk": f"https://github.com/doropig10/shici/releases/download/v{version}/shici-{version}.apk",
    "apkFallback": f"https://cdn.jsdelivr.net/gh/doropig10/shici@main/shici-{version}.apk",
    "sha256": hashlib.sha256(apk.read_bytes()).hexdigest(),
    "size": apk.stat().st_size,
    "notes": notes,
})
(ROOT / "version.json").write_text(json.dumps(v, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("version.json now:", v["versionName"], v["versionCode"], v["sha256"][:12], v["size"])
