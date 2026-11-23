from pathlib import Path
from collections import defaultdict, Counter
from difflib import SequenceMatcher
import re, json, unicodedata
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'app/src/main/assets'
OCR = ROOT / 'tmp/ocr-full'
def canon(s):
    return re.sub('[^a-z]', '', s.lower())
def tidy(s):
    s = re.sub(r'(?<=[\u3400-\u9fff])\s+(?=[\u3400-\u9fff，。；：、“”])', '', s)
    s = re.sub(r'(?<=[，。；：、“”])\s+(?=[\u3400-\u9fff])', '', s)
    return s.strip()

pages = {}
for f in OCR.glob('*.json'):
    data = json.loads(f.read_text(encoding='utf-8-sig'))
    for line in data['lines']:
        ww = line['words']
        line.update(x=min(w['x'] for w in ww), y=min(w['y'] for w in ww), right=max(w['x']+w['w'] for w in ww), bottom=max(w['y']+w['h'] for w in ww))
    if int(f.stem)<316:
        rows=[]
        for col in [0,1]:
            source=sorted([l for l in data['lines'] if int(l['x']>data['width']*.48)==col],key=lambda l:(l['y']+l['bottom'])/2)
            grouped=[]
            for l in source:
                center=(l['y']+l['bottom'])/2
                if grouped and abs(center-grouped[-1]['center'])<data['height']*.006:
                    grouped[-1]['words'].extend(l['words'])
                else: grouped.append({'center':center,'words':list(l['words'])})
            for group in grouped:
                ww=sorted(group['words'],key=lambda w:w['x'])
                rows.append({'words':ww,'text':' '.join(w['text'] for w in ww),'x':min(w['x'] for w in ww),'y':min(w['y'] for w in ww),'right':max(w['x']+w['w'] for w in ww),'bottom':max(w['y']+w['h'] for w in ww)})
        data['lines']=rows
    pages[int(f.stem)] = data

index = {}
for n in range(316,337):
    for l in pages[n]['lines']:
        text = l['text'].replace('／','/').strip()
        m = re.search(r'^([A-Za-z][A-Za-z\s()/\-\'’▲△]*?)[/ ](\d[\d ]{0,6})\s*$',text)
        if not m: continue
        word, num = m.groups()
        word = word.rstrip(' /▲△A').strip()
        num = int(num.replace(' ',''))
        if num<1 or num>341: continue
        # Index entries are single words except these visibly printed phrases.
        word = re.sub(r'\s+','',word).replace('’',"'").strip('/')
        if word.lower()=='accordingto': word='according to'
        if word.lower()=='aan': word='a/an'
        key = canon(word)
        if not key or len(key)>35: continue
        if word!='AIDS' and any(c.isupper() for c in word[1:]): word=word.lower()
        word={'cosycozy':'cosy/cozy','oughtto':'ought to'}.get(word,word)
        index[key] = {'word':word, 'printed':num, 'indexPage':n}

candidates = defaultdict(list)
votes = {}
for n in range(10,316):
    p=pages[n]
    for line in p['lines']:
        if line['y'] < p['height']*.05 or line['y'] > p['height']*.94: continue
        text = line['text'].replace('／','/')
        # Entry heads begin with a Latin word, sometimes after an OCR checkbox/number.
        text=re.sub(r'/\s*-([A-Za-z]+)',r'-\1',text)
        text=re.sub(r'\ba\s*/\s*an\b','a-an',text)
        head = text.split('/')[0]
        m = re.search(r'[A-Za-z][A-Za-z\s()\-\'’]*',head)
        if not m: continue
        raw = m.group().strip()
        key=canon(raw)
        if key not in index: continue
        if len(head[:m.start()]) > 12 or re.search(r"['’æəɑɒɪ]",head[:m.start()]): continue
        if head[m.end():].strip(' .，．:：'): continue
        col = int(line['x'] > p['width']*.48)
        candidates[n].append({'key':key,'line':line,'col':col,'raw':raw})
    votes[n] = Counter(index[c['key']]['printed'] for c in candidates[n])

page_map = {}
for n, counts in votes.items():
    if counts:
        printed,count = counts.most_common(1)[0]
        if count>=2: page_map[n]=printed
for n in range(10,316):
    if n not in page_map:
        before=page_map.get(n-1); after=page_map.get(n+1)
        if before is not None and after==before+2: page_map[n]=before+1

byprinted=defaultdict(list)
for n,p in page_map.items(): byprinted[p].append(n)
words=[]
pending=[]
thumbs=ASSETS/'cards'; thumbs.mkdir(exist_ok=True)
for key, entry in index.items():
    locations=[]
    for n in candidates:
        for candidate in candidates[n]:
            if candidate['key']==key: locations.append((n,candidate))
    if not locations:
        pending.append(entry)
        continue
    # Prefer the largest printed occurrence over a small word in a word map.
    def location_score(nc):
        n,c=nc; l=c['line']; p=pages[n]
        size=max(w['h'] for w in l['words'])
        on_page=page_map.get(n)==entry['printed']
        # An entry's font and its match to the printed index locate it better
        # than any occurrence in an example sentence or word map.
        return size + (18 if on_page else 0) + (8 if '/' in l['text'] or '／' in l['text'] else 0)
    n,c=max(locations,key=location_score)
    p=pages[n]; line=c['line']; col=c['col']
    section='core' if n<260 else 'basic'
    x0=(.025 if n%2 else .078) if col==0 else (.49 if n%2 else .54)
    x1=(.47 if n%2 else .515) if col==0 else (.94 if n%2 else .975)
    x0=min(x0,line['x']/p['width'])
    following=sorted([l for l in p['lines'] if int(l['x']>p['width']*.48)==col and l['y']>=line['y']-3],key=lambda l:l['y'])
    if section=='core':
        # Main entries have a separate definition row; expansions share their row.
        body_text=line['text'].split('/')[-1] if '/' in line['text'] else line['text']
        same_han = re.search(r'[\u4e00-\u9fff]',body_text)
        if same_han:
            meaning=tidy(body_text[same_han.start():])
            crop_bottom=line['bottom']+6
            continuation=[l for l in following if l['y']>line['bottom']-2 and l['y']<line['bottom']+p['height']*.025]
            for l in continuation:
                t=l['text'].strip()
                if re.search('[A-Za-z]',t) or l['x']>line['x']+p['width']*.03 or not re.match(r'^[\u4e00-\u9fff，。；、（(]',t): break
                if any(mark in t.replace(' ','') for mark in ['联想','构词','谐音','对照','词以群记']): break
                meaning=tidy(meaning+' '+t)
                crop_bottom=l['bottom']+6
        else:
            meaning_lines=[l for l in following if l['y']>line['bottom']-3 and l['y']<line['bottom']+p['height']*.05]
            chosen=[]
            for l in meaning_lines:
                t=l['text']
                if chosen and (l['x']>chosen[0]['x']+p['width']*.025 or l['y']-chosen[-1]['bottom']>p['height']*.012): break
                if any(mark in t for mark in ['联 想','构 词','音 译','对 照','谐 音','C)','C 》','（ ）']): break
                if re.search('[\u4e00-\u9fff]',t): chosen.append(l)
                if len(chosen)>=2: break
            meaning=tidy(' '.join(l['text'] for l in chosen))
            crop_bottom=max([l['bottom'] for l in chosen]+[line['bottom']+p['height']*.024])+5
    else:
        next_heads=[other['y'] for other in p['lines'] if int(other['x']>p['width']*.48)==col and other['y']>line['y']+15 and (re.match(r'^[囗口日□匚0○]',other['text']) or other['x']<=line['x']+5)]
        limit=min(next_heads+[line['bottom']+p['height']*.035])
        chosen=[l for l in following if l['y']<limit-4]
        head_text=line['text'].split('/')[-1] if '/' in line['text'] else line['text']
        full=tidy(head_text+' '+' '.join(l['text'] for l in chosen if l is not line))
        chinese=re.search('[\u4e00-\u9fff]',full)
        meaning=full[chinese.start():] if chinese else ''
        crop_bottom=max([l['bottom'] for l in chosen]+[line['bottom']])+5
    # Keep accurate scanned definitions alongside machine-readable search text.
    if not meaning or (len(key)<3 and key not in {'a','i','an','am','as','at','ad','be','by','do','go','he','hi','if','in','is','it','me','my','no','of','on','or','ox','so','to','up','us','we'}):
        pending.append(dict(entry,reason='未取得可靠释义或词形，需要人工对照原页'))
        continue
    y0=max(.045,(line['y']-5)/p['height']); y1=min(.94,crop_bottom/p['height'])
    img=Image.open(ASSETS/'book'/f'{n:03}.webp')
    scale_x=img.width/p['width']; scale_y=img.height/(p['height']*.943)
    box=(int(x0*img.width),int(y0*p['height']*scale_y),int(x1*img.width),min(img.height,int(y1*p['height']*scale_y)))
    if box[3]<=box[1] or box[2]<=box[0]: continue
    ident=key
    img.crop(box).save(thumbs/f'{ident}.webp',quality=90,method=4)
    words.append({'id':ident,'word':entry['word'],'meaning':meaning,'page':n,'position':col*100000+line['y'],'printedPage':entry['printed'],'section':section,'card':f'cards/{ident}.webp','indexPage':entry['indexPage']})

words.sort(key=lambda w:(w['page'],w['position']))
report={'indexed':len(index),'cards':len(words),'core':sum(w['section']=='core' for w in words),'basic':sum(w['section']=='basic' for w in words),'pending':len(pending),'pendingEntries':pending,'pageMap':page_map}
(ROOT/'tmp/extraction-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
book={'id':'liuxiaoyan-cet6-2026','title':'你还在背单词吗','subtitle':'刘晓燕 · 英语六级','source':'26英语六级-你还在背单词吗--刘晓燕.pdf','pageCount':338,'words':words,'pendingCount':len(pending),'indexedCount':len(index)}
(ROOT/'output').mkdir(exist_ok=True)
(ROOT/'output/pending-entries.json').write_text(json.dumps({'说明':'扫描索引中尚未匹配到正文的条目，可能含识别错误；未加入学习词库。','entries':pending},ensure_ascii=False,indent=2),encoding='utf-8')
(ASSETS/'book-data.js').write_text('window.BOOK_DATA = '+json.dumps(book,ensure_ascii=False,separators=(',',':'))+';',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['pendingEntries','pageMap']},ensure_ascii=False))
