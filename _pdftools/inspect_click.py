import re
from pathlib import Path

s = Path(r"E:\单词\app\src\main\assets\app.js").read_text(encoding="utf-8")
i = s.find("document.addEventListener('click'")
print(s[i:i + 1200])
print("=== dispatcher tail ===")
j = s.find("else if(a==='filter'")
print(s[j - 300:j + 400])
print("=== goal handler ===")
k = s.find("e.target.id==='goal'")
print(s[k - 200:k + 200])
