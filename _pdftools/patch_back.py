from pathlib import Path

app = Path(r"E:\单词\app\src\main\assets\app.js")
js = app.read_text(encoding="utf-8")

# 1) session 记住翻过的词
old_start = "session={mode,scopeLabel:scope?scopeLabel(scope):'',queue:ids,total:ids.length,done:0,correct:0,started:Date.now()};"
new_start = ("session={mode,scopeLabel:scope?scopeLabel(scope):'',queue:ids,total:ids.length,done:0,correct:0,"
             "started:Date.now(),back:[],peekPos:-1};")
assert old_start in js, "start() session literal not found"
js = js.replace(old_start, new_start, 1)

# 2) 评分时把当前词压入历史
old_rate = "if(!save())return;session.queue.shift();session.done++;"
new_rate = "if(!save())return;session.back.push(w.id);session.peekPos=-1;session.queue.shift();session.done++;"
assert old_rate in js, "rate() tail not found"
js = js.replace(old_rate, new_rate, 1)

# 3) 回看辅助函数
helpers = (
    "function peekWord(){\n"
    "  if(!session||session.peekPos<0)return null;\n"
    "  const idx=session.back.length-1-session.peekPos;\n"
    "  return idx>=0?word(session.back[idx]):null;\n"
    "}\n"
    "function goBack(){\n"
    "  if(!session)return;\n"
    "  if(!session.back.length){toast('\\u8fd8\\u6ca1\\u6709\\u4e0a\\u4e00\\u4e2a\\u8bcd');return;}\n"
    "  const max=session.back.length-1;\n"
    "  if(session.peekPos>=max){toast('\\u5df2\\u7ecf\\u662f\\u7b2c\\u4e00\\u4e2a\\u4e86');return;}\n"
    "  session.peekPos=session.peekPos<0?0:session.peekPos+1;\n"
    "  revealed=true;spellResult=null;render();window.scrollTo(0,0);\n"
    "}\n"
    "function goForward(){\n"
    "  if(!session)return;\n"
    "  session.peekPos=session.peekPos<=0?-1:session.peekPos-1;\n"
    "  revealed=false;render();window.scrollTo(0,0);\n"
    "}\n"
)
js = js.replace("function study(){", helpers + "function study(){", 1)

# 4) study()：回看时展示历史词
old_head = "function study(){const w=current();if(!w)return finish();"
new_head = ("function study(){const peeking=!!(session&&session.peekPos>=0);"
            "const w=peeking?peekWord():current();if(!w)return finish();")
assert old_head in js, "study() head not found"
js = js.replace(old_head, new_head, 1)

# 5) 进度条下加“上一个”导航
old_progress = '<div class="progress"><i style="width:${session.done/(session.done+session.queue.length)*100}%"></i></div>'
nav = (
    '<div class="study-nav">'
    '${spell?"":`${action(\'go-back\',icon(\'back\')+\' \u4e0a\u4e00\u4e2a\',\'quiet\',session.back.length?\'\':\'disabled\')}`}'
    '${peeking?action(\'go-forward\',\'\u56de\u5230\u5f53\u524d \'+icon(\'arrow\'),\'quiet\'):\'\'}'
    '</div>'
)
assert old_progress in js, "progress div not found"
js = js.replace(old_progress, old_progress + nav, 1)

# 6) 回看时底部只留“回到当前”
old_footer = "${spell?(spellResult?action('next-spell','\u4e0b\u4e00\u4e2a '+icon('arrow'),'primary'):action('check-spell','\u68c0\u67e5\u62fc\u5199','primary')):revealed?"
new_footer = ("${peeking?action('go-forward','\u56de\u5230\u5f53\u524d '+icon('arrow'),'primary'):"
              "spell?(spellResult?action('next-spell','\u4e0b\u4e00\u4e2a '+icon('arrow'),'primary'):action('check-spell','\u68c0\u67e5\u62fc\u5199','primary')):revealed?")
assert old_footer in js, "footer ternary not found"
js = js.replace(old_footer, new_footer, 1)

# 7) 点击分发
anchor = "else if(a==='goal-set'){setGoal(Number(b.dataset.n));}"
assert anchor in js
js = js.replace(anchor, anchor + "\n else if(a==='go-back'){goBack();}"
                            "\n else if(a==='go-forward'){goForward();}", 1)

app.write_text(js, encoding="utf-8", newline="\n")
print("app.js: back navigation added")

css_path = Path(r"E:\单词\app\src\main\assets\style.css")
css = css_path.read_text(encoding="utf-8")
if ".study-nav{" not in css:
    css += ("\n.study-nav{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:2px 0 12px;min-height:30px}"
            "\n.study-nav button{display:inline-flex;align-items:center;gap:6px;font-size:12px;color:var(--muted);padding:6px 9px;border-radius:10px;background:var(--paper);border:1px solid var(--line)}"
            "\n.study-nav button:disabled{opacity:.4}"
            "\n.study-nav svg{width:15px;height:15px}")
    css_path.write_text(css, encoding="utf-8", newline="\n")
print("css: study-nav")
