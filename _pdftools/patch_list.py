from pathlib import Path

p = Path(r"E:\单词\app\src\main\assets\app.js")
s = p.read_text(encoding="utf-8")

# 选中单元/课程时一次列出全部（一节课最多 100 出头）
old = "function setScope(scope){state.libraryScopes=state.libraryScopes||{};state.libraryScopes[book().id]=scope;filter='all';limit=60;save();}"
new = "function setScope(scope){state.libraryScopes=state.libraryScopes||{};state.libraryScopes[book().id]=scope;filter='all';limit=(scope&&scope.unit)?300:60;save();}"
assert old in s, "setScope not found"
s = s.replace(old, new, 1)

# 排序说明改成讲义顺序
assert "按原书顺序" in s
s = s.replace("按原书顺序", "按讲义顺序")

# 「再看 60 个」显示真实剩余数量
old_more = "rows.length>limit?action('more','再看 60 个单词','outline','style=\"width:100%;margin-top:15px\"'):''"
new_more = "rows.length>limit?action('more','再看 '+Math.min(60,rows.length-limit)+' 个单词','outline','style=\"width:100%;margin-top:15px\"'):''"
assert old_more in s, "more button not found"
s = s.replace(old_more, new_more, 1)

p.write_text(s, encoding="utf-8", newline="\n")
print("list behaviour updated")
