from pathlib import Path

p = Path(r"E:\单词\app\src\main\java\cn\shici\wordbook\MainActivity.java")
s = p.read_text(encoding="utf-8")

start = s.index("        private int voiceScore(Voice v) {")
end = s.index("        @JavascriptInterface public String listVoices() {")
block = s[start:end]
s = s[:start] + s[end:]

# 放到 MainActivity 作用域（Bridge 类之外），onCreate 才能调用
anchor = "    private byte[] readBundledImage"
assert anchor in s
s = s.replace(anchor, block + anchor, 1)

p.write_text(s, encoding="utf-8", newline="\n")
print("voice methods moved to MainActivity scope")
