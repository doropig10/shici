from pathlib import Path

p = Path(r"E:\单词\_pdftools\release.py")
s = p.read_text(encoding="utf-8")

# 1) 在 git 尝试之前就写好 version.json（API 回退时也能用最新的）
old_head = '''def run(cmd, cwd=None, check=True):'''
new_head = '''info = {
    "versionCode": int(code),
    "versionName": version,
    "apk": release_url,
    "apkFallback": cdn_url,
    "sha256": sha,
    "size": size,
    "notes": notes,
}
(ROOT / "version.json").write_text(json.dumps(info, ensure_ascii=False, indent=1) + "\\n", encoding="utf-8")


def run(cmd, cwd=None, check=True):'''
assert old_head in s
s = s.replace(old_head, new_head, 1)

# 2) git 分支里不再重复构造 info，只拷贝
old_info = '''info = {
    "versionCode": int(code),
    "versionName": version,
    "apk": release_url,
    "apkFallback": cdn_url,
    "sha256": sha,
    "size": size,
    "notes": notes,
}
(WORK / "version.json").write_text(json.dumps(info, ensure_ascii=False, indent=1) + "\\n", encoding="utf-8")
(ROOT / "version.json").write_text(json.dumps(info, ensure_ascii=False, indent=1) + "\\n", encoding="utf-8")'''
new_info = '''(WORK / "version.json").write_text(json.dumps(info, ensure_ascii=False, indent=1) + "\\n", encoding="utf-8")'''
assert old_info in s
s = s.replace(old_info, new_info, 1)

p.write_text(s, encoding="utf-8", newline="\n")
print("release.py: version.json written before git attempt")
