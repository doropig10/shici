import re, subprocess, sys
from pathlib import Path

ROOT = Path(r"E:\单词")
APPJS = ROOT / "app/src/main/assets/app.js"
CSS = ROOT / "app/src/main/assets/style.css"
MANIFEST = ROOT / "app/src/main/AndroidManifest.xml"
NODE = Path(r"C:\Users\ASUS\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe")

js = APPJS.read_text(encoding="utf-8")

old_fn = re.search(r"function entryHTML\(w\)\{.*?\n\}\n", js, re.S)
assert old_fn, "entryHTML not found"

new_fn = """function blockBody(b){
  if(b.parts&&b.parts.length){
    return b.parts.map(p=>`<div class="part">${p.s?`<span class="src src-${p.s==='口述'?'oral':p.s==='板面'?'board':'misc'}">${esc(p.s)}</span>`:''}<span class="pv">${esc(p.v)}</span></div>`).join('');
  }
  return `<div class="part"><span class="pv">${esc(b.v||'')}</span></div>`;
}
function entryHTML(w){
  const edited=state.edits[C.key(book().id,w.id)]?.meaning;
  if(edited)return `<div class="definition">${esc(edited)}</div>`;
  if(!w.entry||!w.entry.length)return `<div class="definition">${esc(w.meaning)}</div>`;
  const meta=[w.pos,w.phonetic&&('/'+w.phonetic+'/')].filter(Boolean).map(esc).join(' · ');
  return (meta?`<div class="entry-meta">${meta}</div>`:'')
    +`<div class="gloss">${esc(w.gloss||w.meaning)}</div>`
    +`<div class="blocks">${w.entry.map(b=>`<div class="block"><span class="k">${esc(b.k)}</span><div class="v">${blockBody(b)}</div></div>`).join('')}</div>`;
}
"""
js = js[:old_fn.start()] + new_fn + js[old_fn.end():]
APPJS.write_text(js, encoding="utf-8", newline="\n")
print("app.js: parts renderer")

css = CSS.read_text(encoding="utf-8")
marker = ".block .v{font-size:14px;line-height:1.8;color:#3b3b48}"
assert marker in css, "block .v rule not found"
css = css.replace(marker, marker +
                  "\n.block .v .part{display:flex;gap:8px;align-items:flex-start}"
                  "\n.block .v .part+.part{margin-top:7px}"
                  "\n.src{flex:0 0 auto;font-size:10px;font-weight:600;line-height:1.9;padding:0 5px;border-radius:6px;background:#efeaff;color:#5b4bc4;letter-spacing:.5px}"
                  "\n.src-oral{background:#fff0e4;color:#b06a2c}"
                  "\n.src-misc{background:#eeede8;color:#7c7b70}"
                  "\n.pv{flex:1 1 auto}")
CSS.write_text(css, encoding="utf-8", newline="\n")
print("css: source badges")

xml = MANIFEST.read_text(encoding="utf-8")
xml = re.sub(r'android:versionCode="\d+"', 'android:versionCode="14"', xml)
xml = re.sub(r'android:versionName="[^"]+"', 'android:versionName="1.0.13"', xml)
MANIFEST.write_text(xml, encoding="utf-8", newline="\n")

r = subprocess.run([str(NODE), "--check", str(APPJS)], capture_output=True, text=True)
if r.returncode:
    print(r.stderr[:800]); sys.exit(4)
print("syntax ok")
