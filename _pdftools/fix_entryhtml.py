import re, subprocess, sys
from pathlib import Path

ROOT = Path(r"E:\单词")
APPJS = ROOT / "app/src/main/assets/app.js"

HELPER = """function entryHTML(w){
  const edited=state.edits[C.key(book().id,w.id)]?.meaning;
  if(edited)return `<div class="definition">${esc(edited)}</div>`;
  if(!w.entry||!w.entry.length)return `<div class="definition">${esc(w.meaning)}</div>`;
  const meta=[w.pos,w.phonetic&&('/'+w.phonetic+'/')].filter(Boolean).map(esc).join(' · ');
  return (meta?`<div class="entry-meta">${meta}</div>`:'')
    +`<div class="gloss">${esc(w.gloss||w.meaning)}</div>`
    +`<div class="blocks">${w.entry.map(b=>`<div class="block"><span class="k">${esc(b.k)}</span><span class="v">${esc(b.v)}</span></div>`).join('')}</div>`;
}
"""

js = APPJS.read_text(encoding="utf-8")
m = re.search(r"function entryHTML\(w\)\{.*?\n(?=function answer\(w\)\{)", js, re.S)
if not m:
    print("entryHTML block not found")
    sys.exit(3)
js = js[:m.start()] + HELPER + js[m.end():]
APPJS.write_text(js, encoding="utf-8", newline="\n")
print("entryHTML replaced")
