import re, zlib, json, sys

PATH = r"D:\BaiduNetdiskDownload\六级词汇.pdf"
raw = open(PATH, "rb").read()
s = raw.decode("latin-1")

objs = {}
for m in re.finditer(r"(?<![0-9])(\d+)\s+0\s+obj\b", s):
    num = int(m.group(1))
    end = s.find("endobj", m.end())
    if end == -1:
        end = len(s)
    objs[num] = s[m.end():end]

stream_re = re.compile(r"stream\r?\n")

def get_stream(num):
    body = objs[num]
    m = stream_re.search(body)
    if not m:
        return None, body[:m.start()] if m else body
    dict_part = body[:m.start()]
    data = body[m.end():]
    e = data.rfind("endstream")
    if e != -1:
        data = data[:e]
    data = data.rstrip("\r\n")
    b = data.encode("latin-1")
    if "FlateDecode" in dict_part:
        b = zlib.decompress(b)
    return b, dict_part

def parse_cmap(cmap_bytes):
    txt = cmap_bytes.decode("latin-1")
    mapping = {}
    for m in re.finditer(r"beginbfchar(.*?)endbfchar", txt, re.S):
        for pair in re.finditer(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", m.group(1)):
            mapping[int(pair.group(1), 16)] = bytes.fromhex(pair.group(2)).decode("utf-16-be", "ignore")
    for m in re.finditer(r"beginbfrange(.*?)endbfrange", txt, re.S):
        body = m.group(1)
        for r in re.finditer(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*(<[0-9A-Fa-f]+>|\[[^\]]*\])", body):
            lo = int(r.group(1), 16); hi = int(r.group(2), 16); dst = r.group(3)
            if dst.startswith("<"):
                base = bytes.fromhex(dst[1:-1]).decode("utf-16-be", "ignore")
                for k in range(lo, min(hi, lo + 65535) + 1):
                    if base:
                        mapping[k] = base[:-1] + chr(ord(base[-1]) + (k - lo))
            else:
                for idx, it in enumerate(re.findall(r"<([0-9A-Fa-f]+)>", dst)):
                    if lo + idx > hi: break
                    mapping[lo + idx] = bytes.fromhex(it).decode("utf-16-be", "ignore")
    return mapping

cmap = {}
for m in re.finditer(r"/ToUnicode\s+(\d+)\s+0\s+R", s):
    data, _ = get_stream(int(m.group(1)))
    if data:
        cmap.update(parse_cmap(data))
inv = {}
for k, v in cmap.items():
    if len(v) == 1:
        inv.setdefault(v, k)
print("digit codes:", {c: hex(inv[c]) if c in inv else None for c in "0123456789/"})
sys.stdout.flush()

pages = [num for num in objs if "/Type" in objs[num] and re.search(r"/Type\s*/Page(?![sA-Za-z])", objs[num])]
pages.sort()
print("page count:", len(pages))
target = pages[163]
print("page164 obj:", target)
print("dict:", objs[target][:400])
m = re.search(r"/Contents\s*(\[[^\]]*\]|\d+\s+0\s+R)", objs[target])
print("contents:", m.group(1))
refs = sorted(set(int(x) for x in re.findall(r"(\d+)\s+0\s+R", m.group(1))))
print("refs:", refs)
for r in refs:
    b, d = get_stream(r)
    print("stream", r, "decompressed len", len(b), "dict", d.strip()[:200])
    open(rf"E:\单词\_pdftools\p164_{r}.bin", "wb").write(b)
