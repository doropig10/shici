"""Attach the book's reviewed Unit/Lesson/group hierarchy without changing word IDs."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'app/src/main/assets'

def group_words():
    source = json.loads((ROOT/'tools/book-structure.json').read_text(encoding='utf-8'))
    data_path = ASSETS/'book-data.js'
    book = json.loads(data_path.read_text(encoding='utf-8')[19:-1])
    page_map = {int(k): v for k,v in json.loads((ROOT/'tmp/extraction-report.json').read_text())['pageMap'].items()}
    # Visually checked OCR mistakes; composite pages need position-aware mapping.
    page_map.update({62:56,104:98,145:157,150:162,160:172})
    def printed(page,y):
        if page==54:return 46 if y<.68 else 48
        if page==222:return 244 if y<.70 else 248
        return page_map[page]
    def chapter(page,y):
        p=printed(page,y)
        unit=max((u for u in source['units'] if u['pages'][0]<=p), key=lambda u:u['number'])
        lesson=max(i+1 for i,start in enumerate(unit['pages']) if start<=p)
        return unit['number'],lesson
    groups=source['groups']
    for group in groups:
        group['unit'],group['lesson']=chapter(group['page'],group['top'])
        group['id']=f"u{group['unit']}-g{group['number']}" if group['number'] else f"u{group['unit']}-unconfirmed"
    heights={}
    for w in book['words']:
        n=w['page']
        if n not in heights:heights[n]=json.loads((ROOT/f'tmp/ocr-full/{n:03}.json').read_text(encoding='utf-8-sig'))['height']
        y=(w['position']%100000)/heights[n]
        w['unit'],w['lesson']=chapter(n,y)
        w.pop('groupId',None)
        if w['section']=='core':
            candidates=[g for g in groups if g['unit']==w['unit'] and (g['page'],g['top']-.008)<=(n,y)]
            if not candidates:raise ValueError(f"No group for {w['id']} at {n}, {y}")
            group=max(candidates,key=lambda g:(g['page'],g['top']))
            w['groupId']=group['id']
            w['lesson']=group['lesson']
    book['structure']={'units':source['units'],'groups':groups}
    data_path.write_text('window.BOOK_DATA = '+json.dumps(book,ensure_ascii=False,separators=(',',':'))+';',encoding='utf-8')
    print(f"Grouped {len(book['words'])} words into {len(source['units'])} units and {len(groups)} word groups.")

if __name__=='__main__':group_words()
