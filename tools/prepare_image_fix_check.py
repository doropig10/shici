"""Prepare PNG fixtures from shipping assets for simulated native image replies."""
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[1]
for asset in ['cards/terror.webp','cards/ambition.webp','cards/remark.webp','book/020.webp','book/222.webp']:
    dest=root/'tmp/image-fallback-fixtures'/Path(asset).with_suffix('.png')
    dest.parent.mkdir(parents=True,exist_ok=True)
    with Image.open(root/'app/src/main/assets'/asset) as im: im.save(dest)
