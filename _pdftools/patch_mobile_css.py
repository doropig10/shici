from pathlib import Path

css_path = Path(r"E:\单词\app\src\main\assets\style.css")
css = css_path.read_text(encoding="utf-8")

# 弹窗：用动态视口高度，避免被系统栏裁掉
old_overlay = ".modal-overlay{position:fixed;inset:0;background:#26233777;display:flex;align-items:center;justify-content:center;padding:20px;z-index:30}"
new_overlay = ".modal-overlay{position:fixed;inset:0;background:#26233777;display:flex;align-items:center;justify-content:center;padding:14px;z-index:30}"
assert old_overlay in css
css = css.replace(old_overlay, new_overlay)

old_modal = ".modal{width:100%;max-width:480px;background:var(--bg);border-radius:24px;padding:25px;max-height:88vh;overflow:auto}"
new_modal = (".modal{width:100%;max-width:480px;background:var(--bg);border-radius:24px;padding:22px;"
             "max-height:min(86vh,calc(100dvh - 28px));overflow:auto;overscroll-behavior:contain}")
assert old_modal in css
css = css.replace(old_modal, new_modal)

narrow = """
@media (max-width:400px){
  .shell{padding:20px 16px 104px}
  .modal{padding:18px;border-radius:20px}
  .modal .word-large{font-size:30px}
  .gloss{font-size:18px;line-height:1.55;margin:2px 0 12px}
  .block{grid-template-columns:32px 1fr;gap:8px;padding:9px 0}
  .block .k{font-size:10px;letter-spacing:0}
  .block .v{font-size:13.5px;line-height:1.72}
  .src{flex:0 0 30px;width:30px;font-size:9px;letter-spacing:0}
  .entry-meta{font-size:11px;margin:8px 0 2px}
  .study-card{padding:22px 15px}
  .word-line{margin:14px 0 2px;gap:10px}
  .chips{gap:6px}
}
"""
if "@media (max-width:400px)" not in css:
    css += narrow
css_path.write_text(css, encoding="utf-8")
print("css updated")
