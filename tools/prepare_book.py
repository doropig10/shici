from pathlib import Path
from pypdf import PdfReader
from PIL import Image, ImageOps
import io, json

ROOT = Path(__file__).resolve().parents[1]
source = Path(r'E:\26英语六级-你还在背单词吗--刘晓燕.pdf')
reader = PdfReader(source)
ocr = ROOT / 'tmp' / 'pages'
pages = ROOT / 'app' / 'src' / 'main' / 'assets' / 'book'
ocr.mkdir(parents=True, exist_ok=True)
pages.mkdir(parents=True, exist_ok=True)
for n, page in enumerate(reader.pages, 1):
    name = f'{n:03}'
    if (ocr / f'{name}.jpg').exists():
        continue
    im = Image.open(io.BytesIO(page.images[0].data)).convert('RGB')
    # Exclude the scanned uploader's bottom banner from the study view.
    study = im.crop((0, 0, im.width, int(im.height * .943)))
    study.save(pages / f'{name}.webp', quality=83, method=4)
    scaled = ImageOps.contain(im, (1700, 2400))
    if scaled.width < 1500:
        scaled = im.resize((1500, round(im.height * 1500 / im.width)), Image.Resampling.LANCZOS)
    scaled.save(ocr / f'{name}.jpg', quality=95)
    if n % 20 == 0:
        print(f'Prepared {n}/{len(reader.pages)}', flush=True)
print('Done', len(reader.pages), flush=True)
