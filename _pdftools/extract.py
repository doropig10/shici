import re, zlib, json, sys

PATH = r"D:\BaiduNetdiskDownload\六级词汇.pdf"
raw = open(PATH, "rb").read()
s = raw.decode("latin-1")

# index all indirect objects
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

# page objects
pages = []
for num, body in objs.items():
    if "/Type" in body and re.search(r"/Type\s*/Page(?![sA-Za-z])", body):
        pages.append(num)
pages.sort()
print("pages found:", len(pages), file=sys.stderr)

def content_refs(body):
    m = re.search(r"/Contents\s*(\[[^\]]*\]|\d+\s+0\s+R)", body)
    if not m:
        return []
    seg = m.group(1)
    return sorted(set(int(x) for x in re.findall(r"(\d+)\s+0\s+R", seg)))

def unescape(b):
    out = bytearray()
    i = 0
    n = len(b)
    while i < n:
        c = b[i]
        if c == 0x5C and i + 1 < n:
            d = b[i+1]
            mp = {0x6E: 10, 0x72: 13, 0x74: 9, 0x62: 8, 0x66: 12,
                  0x28: 40, 0x29: 41, 0x5C: 92}
            if d in mp:
                out.append(mp[d]); i += 2; continue
            if 0x30 <= d <= 0x37:
                j = i + 1
                oct_s = b""
                while j < n and len(oct_s) < 3 and 0x30 <= b[j] <= 0x37:
                    oct_s += bytes([b[j]]); j += 1
                out.append(int(oct_s, 8) & 0xFF); i = j; continue
            if d == 0x0A:
                i += 2; continue
            if d == 0x0D:
                i += 3 if i + 2 < n and b[i+2] == 0x0A else 2
                continue
            out.append(d); i += 2; continue
        out.append(c); i += 1
    return bytes(out)

def extract_text(content):
    parts = []
    i = 0
    n = len(content)
    last_str = None
    arr = None
    while i < n:
        c = content[i]
        if c == 0x28:  # (
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
        if c == 0x3C and i + 1 < n and content[i+1] != 0x3C:  # <hex>
            j = content.find(b">", i)
            if j == -1: break
            hx = re.sub(rb"[^0-9A-Fa-f]", b"", content[i+1:j])
            if len(hx) % 2: hx += b"0"
            try:
                last_str = bytes.fromhex(hx.decode())
            except Exception:
                last_str = b""
            arr = None
            i = j + 1; continue
        if c == 0x3C and i + 1 < n and content[i+1] == 0x3C:
            i += 2; continue
        if c == 0x5B:  # [
            j = content.find(b"]", i)
            if j == -1: break
            arr = content[i+1:j]
            i = j + 1; continue
        if 0x41 <= c <= 0x5A or 0x61 <= c <= 0x7A or c in (0x2A, 0x27, 0x22):
            j = i
            while j < n and (0x41 <= content[j] <= 0x5A or 0x61 <= content[j] <= 0x7A or content[j] in (0x2A, 0x27, 0x22)):
                j += 1
            op = content[i:j].decode("latin-1")
            if op in ("Tj",):
                if last_str is not None:
                    parts.append(last_str)
            elif op == "TJ":
                if arr is not None:
                    for m2 in re.finditer(rb"\((?:\\.|[^\\()])*\)|<[0-9A-Fa-f\s]*>", arr):
                        tok = m2.group(0)
                        if tok.startswith(b"("):
                            parts.append(unescape(tok[1:-1]))
            elif op in ("Td", "TD", "T*", "ET"):
                parts.append(b"\n")
            last_str = None; arr = None
            i = j; continue
        i += 1
    txt = b"".join(parts).decode("latin-1")
    return txt

result = {}
for idx, pnum in enumerate(pages, start=1):
    body = objs[pnum]
    chunks = []
    for ref in content_refs(body):
        data = get_stream(ref)
        if data:
            chunks.append(extract_text(data))
    result[str(idx)] = "".join(chunks)

with open(r"E:\单词\_pdftools\pages.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False)

print("extracted pages:", len(result), file=sys.stderr)
print(result.get("1", "")[:800])
