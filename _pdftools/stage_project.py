"""把完整项目拷进 Gitee 仓库工作区（过滤构建产物/嵌套仓库/大件）。"""
import shutil
from pathlib import Path

ROOT = Path(r"E:\单词")
DEST = ROOT / "_pdftools/gitee_repo"

EXCLUDE_DIRS = {"__pycache__", "ghrepo", "gitee_repo", "snapshots", "tmp", "tmp134", "build", "output", "preview", ".tooling"}

def copy_tree(src: Path, dst: Path):
    for item in src.rglob("*"):
        if any(part in EXCLUDE_DIRS for part in item.relative_to(src).parts):
            continue
        target = dst / item.relative_to(src)
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)

for name in ("app", "tools", "tests", "_pdftools"):
    copy_tree(ROOT / name, DEST / name)

# _pdftools 里只保留脚本与少量数据
pd = DEST / "_pdftools"
for f in pd.iterdir():
    if f.is_file() and f.suffix in {".js", ".pyc"} or f.name == "book-data.orig.js" or f.name == "hits.txt":
        f.unlink()

for name in ("README.md", ".gitignore", "version.json", "shici-1.0.40.apk", "shici-1.0.40.sha256.txt",
             "六级词汇_1-3267.md", "六级词汇_1-3267_按单元.md", "六级词汇_1-3267_按课划分.md",
             "六级词汇_全书7537_导入.json", "刘晓艳六级词汇_精讲18课_导入.json"):
    src = ROOT / name
    if src.exists():
        shutil.copy2(src, DEST / name)

(DEST / ".gitignore").write_text(
    ".tooling/\ntmp/\nbuild/\noutput/\npreview/\n__pycache__/\n*.pyc\n"
    "_pdftools/ghrepo/\n_pdftools/gitee_repo/\n_pdftools/snapshots/\n",
    encoding="utf-8")

n = sum(1 for _ in DEST.rglob("*") if _.is_file())
size = sum(f.stat().st_size for f in DEST.rglob("*") if f.is_file())
print(f"staged {n} files, {size/1024/1024:.1f} MB")
