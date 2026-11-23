"""Crop complete book entries, joining continuation columns/pages in reading order."""
from pathlib import Path
from functools import lru_cache
import io, json, re, argparse
import numpy as np
from PIL import Image, ImageDraw
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'app/src/main/assets'
SOURCE=Path(r'E:\26英语六级-你还在背单词吗--刘晓燕.pdf')

def runs(values, max_gap=3):
    points=np.flatnonzero(values)
    if not len(points): return []
    groups=[]; start=last=int(points[0])
    for point in points[1:]:
        point=int(point)
        if point-last>max_gap+1: groups.append((start,last+1));start=point
        last=point
    groups.append((start,last+1))
    return groups

def margins(n,col):
    return ((.075,.52) if n%2==0 else (.022,.475)) if col==0 else ((.537,.978) if n%2==0 else (.49,.945))

def analyze(n,image,ocr):
    scaled=image.resize((700,round(image.height*700/image.width)))
    pixels=np.asarray(scaled).astype(np.int16)
    red,green,blue=pixels[:,:,0],pixels[:,:,1],pixels[:,:,2]
    orange=(red>200)&(green>45)&(green<178)&(blue<115)&(red-green>60)
    h,w=orange.shape
    heads={0:[],1:[]}
    for col in [0,1]:
        x0,x1=margins(n,col)
        x=int((x0+.005)*w)
        strip=orange[:,x:x+int(w*.055)]
        for y0,y1 in runs(strip.sum(axis=1)>w*.018):
            if not (.05*h<y0<.947*h and h*.005<y1-y0<h*.025): continue
            yy=(y0+y1)//2
            # Section banners are wider than the orange numbered entry marker.
            if orange[y0:y1,x+int(w*.066):x+int(w*.12)].sum()>w*(y1-y0)*.016: continue
            nearby=[]
            for line in ocr['lines']:
                for word in line['words']:
                    wx=word['x']/ocr['width'];wy=word['y']/ocr['height']
                    if x0+.05<wx<x1 and y0/h-.018<wy<y1/h and word['h']>ocr['height']*.01 and re.search('[A-Za-z]',word['text']):nearby.append(wy)
            heads[col].append(max(.045,min([y0/h]+nearby)-.002))
    barriers=[]
    for line in ocr['lines']:
        compact=line['text'].replace(' ','')
        if ('词以群记' in compact or re.match(r'Lesson\d',compact) or re.match(r'Unit\d',compact)):
            words=line['words']
            xx=min(word['x'] for word in words)/ocr['width']
            yy=min(word['y'] for word in words)/ocr['height']
            # Side tabs are outside the body columns and are not block boundaries.
            minimum=.009 if '词以群记' in compact else .026
            if .05<yy<.94 and .015<xx<.8 and max(word['h'] for word in words)>ocr['height']*minimum:
                barriers.append(max(.05,yy-.006))
    # Colored, wide section labels also catch labels the OCR missed.
    left0=int((.08 if n%2==0 else .025)*w)
    for y0,y1 in runs(orange[:,left0:left0+int(w*.23)].sum(axis=1)>w*.065):
        if .05*h<y0<.94*h and y1-y0>h*.009:
            barriers.append(max(.05,(y0-4)/h))
    barriers=sorted(set(round(y,4) for y in barriers))
    bands=[]
    breaks=[.05]+barriers+[.951]
    for i,(begin,end) in enumerate(zip(breaks,breaks[1:])):
        hs=[y for y in heads[0]+heads[1] if begin<y<end]
        start=.052 if i==0 else min(hs+[end])-.002
        if end-start>.004:bands.append({'top':start,'end':end})
    return {'heads':heads,'barriers':barriers,'bands':bands}

def expand_cards(samples_only=False):
    data_path=ASSETS/'book-data.js'
    book=json.loads(data_path.read_text(encoding='utf-8')[19:-1])
    reader=PdfReader(SOURCE)
    @lru_cache(maxsize=8)
    def source(n):
        return Image.open(io.BytesIO(reader.pages[n-1].images[0].data)).convert('RGB')
    @lru_cache(maxsize=338)
    def ocr(n):
        return json.loads((ROOT/'tmp/ocr-full'/f'{n:03}.json').read_text(encoding='utf-8-sig'))
    info={}
    for n in range(10,260):
        info[n]=analyze(n,source(n),ocr(n))
    if samples_only:
        for n in [10,11,12,21,100,201,250,258]:
            im=source(n).copy();draw=ImageDraw.Draw(im)
            for col in [0,1]:
                x0,x1=margins(n,col)
                for y in info[n]['heads'][col]: draw.line((x0*im.width,y*im.height,x1*im.width,y*im.height),fill='magenta',width=3)
            for y in info[n]['barriers']:draw.line((0,y*im.height,im.width,y*im.height),fill='blue',width=3)
            im.thumbnail((750,1100));im.save(ROOT/'tmp'/f'boundaries-{n}.png')
            print(n,info[n],flush=True)
        return

    page_map={int(k):v for k,v in json.loads((ROOT/'tmp/extraction-report.json').read_text(encoding='utf-8'))['pageMap'].items()}
    def adjacent(n):return n+1 in info and page_map.get(n+1,0)-page_map.get(n,0)<=2
    def band_at(n,y):
        bands=info[n]['bands']
        return next((i for i,b in enumerate(bands) if b['top']-.012<=y<b['end']),max(0,len(bands)-1))
    def crop_piece(n,col,y0,y1):
        im=source(n);x0,x1=margins(n,col)
        return im.crop((round(x0*im.width),round(y0*im.height),round(x1*im.width),min(im.height,round(y1*im.height))))
    def parent(n,col,y):
        bi=band_at(n,y);band=info[n]['bands'][bi]
        heads=[h for h in info[n]['heads'][col] if band['top']-.01<h<y+.012]
        if heads:
            candidate=max(heads)
            if not any(candidate+.015<b<y-.01 for b in info[n]['barriers']):return n,col,candidate,bi
        # An expansion at the top of a column may belong to the previous column.
        pn,pc=(n,0) if col==1 else (n-1,1)
        if pn in info and (col==1 or (bi==0 and adjacent(pn))):
            pbi=bi if col==1 else len(info[pn]['bands'])-1
            pb=info[pn]['bands'][pbi]
            hs=[h for h in info[pn]['heads'][pc] if pb['top']-.01<h<pb['end']]
            if hs:return pn,pc,max(hs),pbi
        return n,col,max(.05,y-.004),bi

    changes=[]
    for word in book['words']:
        if word['section']!='core':continue
        n=word['page'];col=int(word['position']//100000);y=(word['position']%100000)/ocr(n)['height']
        sn,sc,sy,bi=parent(n,col,y)
        pieces=[];regions=[];pn,pc,start=sn,sc,sy
        # Normal entries occupy one column; long ones can continue in the next.
        for _ in range(4):
            if pn not in info:break
            band=info[pn]['bands'][bi]
            stops=[v for v in info[pn]['heads'][pc] if start+.014<v<band['end']]
            end=min(stops+[band['end']])
            if end-start>.005:
                bottom=end-.001 if stops else end
                if not stops and bottom>.95 and pc==0:
                    # The uploader footer begins just below the left-column body.
                    # Keep extra space where a genuine final text line needs it.
                    x0,x1=margins(pn,pc);page_ocr=ocr(pn)
                    final_bottoms=[(w['y']+w['h'])/page_ocr['height']
                        for line in page_ocr['lines'] for w in line['words']
                        if x0<w['x']/page_ocr['width']<x1
                        and .90<w['y']/page_ocr['height']<.944]
                    bottom=min(bottom,max(.947,max(final_bottoms,default=0)+.002))
                pieces.append(crop_piece(pn,pc,start,max(start+.003,bottom)))
                regions.append({'page':pn,'column':pc,'top':round(start,5),'bottom':round(bottom,5)})
            if stops:break
            if pc==0:pc=1
            else:
                if band['end']<.947 or not adjacent(pn):break
                pn+=1;pc=0;bi=0
            start=info[pn]['bands'][bi]['top']
            if any(abs(h-start)<.014 for h in info[pn]['heads'][pc]):break
        if not pieces:continue
        width=max(p.width for p in pieces)
        resized=[p.resize((width,round(p.height*width/p.width)),Image.Resampling.LANCZOS) for p in pieces]
        card=Image.new('RGB',(width,sum(p.height for p in resized)+14*(len(resized)-1)),'white')
        cy=0
        for p in resized:card.paste(p,(0,cy));cy+=p.height+14
        path=ASSETS/word['card']
        card.save(path,quality=89,method=4)
        word['cardRegions']=regions
        word['fullEntry']=True
        changes.append({'word':word['word'],'regions':regions,'height':card.height})
        if len(changes)%300==0:print('Full entries',len(changes),flush=True)
    book['cardFormat']='full-entry-v1'
    data_path.write_text('window.BOOK_DATA = '+json.dumps(book,ensure_ascii=False,separators=(',',':'))+';',encoding='utf-8')
    (ROOT/'tmp/full-entry-report.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Updated',len(changes),'core cards; stitched',sum(len(c['regions'])>1 for c in changes),'continuations.',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--samples',action='store_true');args=parser.parse_args()
    expand_cards(args.samples)
