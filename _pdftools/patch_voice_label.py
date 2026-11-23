from pathlib import Path

js_path = Path(r"E:\单词\app\src\main\assets\app.js")
js = js_path.read_text(encoding="utf-8")

old = '''function shortVoice(n){
  const p=String(n||'').split('/');
  return p[p.length-1]||'跟随系统';
}'''
new = '''function shortVoice(n){
  const p=String(n||'').split('/');
  return p[p.length-1]||'跟随系统';
}
function voiceLabel(v){
  const raw=String((v&&v.name)||'').toLowerCase();
  let label='音色';
  if(raw.includes('female'))label='女声';
  else if(raw.includes('male'))label='男声';
  const m=raw.match(/(?:female|male)_?(\\d+)/);
  if(m)label+=' '+m[1];
  return label;
}'''
assert old in js
js = js.replace(old, new, 1)

old_row = 'return `<button class="voice-row ${on?\'on\':\'\'}" data-act="set-voice" data-name="${esc(v.name)}">`\n      +`<div><b>${esc(shortVoice(v.name))}</b><p>${esc(v.locale)} · ${v.network?\'需联网\':\'本地\'}${on?\' · 当前\':\'\'}</p></div>`'
new_row = 'return `<button class="voice-row ${on?\'on\':\'\'}" data-act="set-voice" data-name="${esc(v.name)}">`\n      +`<div><b>${esc(voiceLabel(v))}</b><p>${esc(v.locale)} · ${v.network?\'需联网\':\'本地\'}${on?\' · 当前\':\'\'}</p></div>`'
assert old_row in js, "voice row template not found"
js = js.replace(old_row, new_row, 1)

js_path.write_text(js, encoding="utf-8", newline="\n")
print("voice labels friendly")
