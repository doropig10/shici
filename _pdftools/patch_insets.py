from pathlib import Path

p = Path(r"E:\单词\app\src\main\java\cn\shici\wordbook\MainActivity.java")
s = p.read_text(encoding="utf-8")

if "WindowInsets.Type.systemBars" not in s:
    s = s.replace(
        "import android.os.Bundle;",
        "import android.os.Build;\nimport android.os.Bundle;",
        1,
    )
    s = s.replace(
        "import android.view.View;",
        "import android.view.View;\nimport android.view.WindowInsets;",
        1,
    )
    old = """        web.setOnApplyWindowInsetsListener((v,insets) -> {
            v.setPadding(insets.getSystemWindowInsetLeft(), insets.getSystemWindowInsetTop(), insets.getSystemWindowInsetRight(), insets.getSystemWindowInsetBottom());
            return insets.consumeSystemWindowInsets();
        });"""
    new = """        // Android 15+ 强制 edge-to-edge：旧的 getSystemWindowInsetXxx() 在部分机型上返回 0，
        // 内容会钻到状态栏/导航栏下面，这里改用 Type 接口取系统栏与刘海的内边距。
        web.setOnApplyWindowInsetsListener((v,insets) -> {
            int left, top, right, bottom;
            if (Build.VERSION.SDK_INT >= 30) {
                android.graphics.Insets bars = insets.getInsets(WindowInsets.Type.systemBars() | WindowInsets.Type.displayCutout());
                left = bars.left; top = bars.top; right = bars.right; bottom = bars.bottom;
            } else {
                left = insets.getSystemWindowInsetLeft();
                top = insets.getSystemWindowInsetTop();
                right = insets.getSystemWindowInsetRight();
                bottom = insets.getSystemWindowInsetBottom();
            }
            v.setPadding(left, top, right, bottom);
            return Build.VERSION.SDK_INT >= 30 ? WindowInsets.CONSUMED : insets.consumeSystemWindowInsets();
        });"""
    assert old in s, "inset listener not found"
    s = s.replace(old, new, 1)
    p.write_text(s, encoding="utf-8", newline="\n")
    print("insets fixed")
else:
    print("already patched")
