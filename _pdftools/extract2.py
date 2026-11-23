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
    body = objs.get(num)
    if body is None:
        return None
    m = stream_re.search(body)
    if not m:
        return None
    dict_part = body[:m.start()]
    data = body[m.end():]
    e = data.rfind("endstream")
    if e != -1:
        data = data[:e]
    data = data.rstrip("\r\n")
    b = data.encode("latin-1")
    if "FlateDecode" in dict_part:
        try:
            b = zlib.decompress(b)
        except Exception:
            try:
                b = zlib.decompressobj().decompress(b)
            except Exception:
                return None
    return b

def parse_cmap(cmap_bytes):
    txt = cmap_bytes.decode("latin-1")
    mapping = {}
    for m in re.finditer(r"beginbfchar(.*?)endbfchar", txt, re.S):
        for pair in re.finditer(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", m.group(1)):
            src = int(pair.group(1), 16)
            dst_hex = pair.group(2)
            dst = bytes.fromhex(dst_hex).decode("utf-16-be", "ignore")
            mapping[src] = dst
    for m in re.finditer(r"beginbfrange(.*?)endbfrange", txt, re.S):
        body = m.group(1)
        for r in re.finditer(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*(<[0-9A-Fa-f]+>|\[[^\]]*\])", body):
            lo = int(r.group(1), 16)
            hi = int(r.group(2), 16)
            dst = r.group(3)
            if dst.startswith("<"):
                base = bytes.fromhex(dst[1:-1]).decode("utf-16-be", "ignore")
                for k in range(lo, min(hi, lo + 65535) + 1):
                    if base:
                        mapping[k] = base[:-1] + chr(ord(base[-1]) + (k - lo))
            else:
                items = re.findall(r"<([0-9A-Fa-f]+)>", dst)
                for idx, it in enumerate(items):
                    code = lo + idx
                    if code > hi:
                        break
                    mapping[code] = bytes.fromhex(it).decode("utf-16-be", "ignore")
    return mapping

# collect all ToUnicode refs
cmap = {}
for m in re.finditer(r"/ToUnicode\s+(\d+)\s+0\s+R", s):
    ref = int(m.group(1))
    data = get_stream(ref)
    if data:
        cmap.update(parse_cmap(data))
print("cmap size:", len(cmap), file=sys.stderr)

pages = []
for num, body in objs.items():
    if "/Type" in body and re.search(r"/Type\s*/Page(?![sA-Za-z])", body):
        pages.append(num)
pages.sort()

def content_refs(body):
    m = re.search(r"/Contents\s*(\[[^\]]*\]|\d+\s+0\s+R)", body)
    if not m:
        return []
    return sorted(set(int(x) for x in re.findall(r"(\d+)\s+0\s+R", m.group(1))))

def unescape(b):
    out = bytearray(); i = 0; n = len(b)
    while i < n:
        c = b[i]
        if c == 0x5C and i + 1 < n:
            d = b[i+1]
            mp = {0x6E: 10, 0x72: 13, 0x74: 9, 0x62: 8, 0x66: 12, 0x28: 40, 0x29: 41, 0x5C: 92}
            if d in mp:
                out.append(mp[d]); i += 2; continue
            if 0x30 <= d <= 0x37:
                j = i + 1; o = b""
                while j < n and len(o) < 3 and 0x30 <= b[j] <= 0x37:
                    o += bytes([b[j]]); j += 1
                out.append(int(o, 8) & 0xFF); i = j; continue
            if d == 0x0A:
                i += 2; continue
            if d == 0x0D:
                i += 3 if i + 2 < n and b[i+2] == 0x0A else 2
                continue
            out.append(d); i += 2; continue
        out.append(c); i += 1
    return bytes(out)

def decode_str(b):
    if len(b) % 2:
        b = b + b"\x00"
    out = []
    for i in range(0, len(b) - 1, 2):
        code = (b[i] << 8) | b[i+1]
        out.append(cmap.get(code, ""))
    return "".join(out)

def extract_text(content):
    parts = []
    i = 0; n = len(content)
    last_str = None; arr = None
    while i < n:
        c = content[i]
        if c == 0x28:
            depth = 1; j = i + 1; buf = bytearray()
            while j < n:
                ch = content[j]
                if ch == 0x5C:
                    buf.append(ch)
                    if j + 1 < n:
                        buf.append(content[j+1])
                    j += 2; continue
                if ch == 0x28:
                    depth += 1
                elif ch == 0x29:
                    depth -= 1
                    if depth == 0:
                        break
                buf.append(ch); j += 1
            last_str = unescape(bytes(buf)); arr = None
            i = j + 1; continue
        if c == 0x3C and i + 1 < n and content[i+1] != 0x3C:
            j = content.find(b">", i)
            if j == -1: break
            hx = re.sub(rb"[^0-9A-Fa-f]", b"", content[i+1:j])
            if len(hx) % 2: hx += b"0"
            try:
                last_str = bytes.fromhex(hx.decode())
            except Exception:
                last_str = b""
            arr = None; i = j + 1; continue
        if c == 0x3C and i + 1 < n and content[i+1] == 0x3C:
            i += 2; continue
        if c == 0x5B:
            j = content.find(b"]", i)
            if j == -1: break
            arr = content[i+1:j]; i = j + 1; continue
        if (0x41 <= c <= 0x5A) or (0x61 <= c <= 0x7A) or c in (0x2A, 0x27, 0x22):
            j = i
            while j < n and ((0x41 <= content[j] <= 0x5A) or (0x61 <= content[j] <= 0x7A) or content[j] in (0x2A, 0x27, 0x22)):
                j += 1
            op = content[i:j].decode("latin-1")
            if op == "Tj":
                if last_str is not None:
                    parts.append(decode_str(last_str))
            elif op == "TJ":
                if arr is not None:
                    for m2 in re.finditer(rb"\((?:\\.|[^\\()])*\)|<[0-9A-Fa-f\s]*>", arr):
                        tok = m2.group(0)
                        if tok.startswith(b"("):
                            parts.append(decode_str(unescape(tok[1:-1])))
                        else:
                            hx = re.sub(rb"[^0-9A-Fa-f]", b"", tok[1:-1])
                            if len(hx) % 2: hx += b"0"
                            try:
                                parts.append(decode_str(bytes.fromhex(hx.decode())))
                            except Exception:
                                pass
            elif op in ("Td", "TD", "T*", "ET"):
                parts.append("\n")
            last_str = None; arr = None
            i = j; continue
        i += 1
    return "".join(parts)

result = {}
for idx, pnum in enumerate(pages, start=1):
    chunks = []
    for ref in content_refs(objs[pnum]):
        data = get_stream(ref)
        if data:
            chunks.append(extract_text(data))
    result[str(idx)] = "".join(chunks)

with open(r"E:\单词\_pdftools\pages.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False)
print("extracted pages:", len(result), file=sys.stderr)
