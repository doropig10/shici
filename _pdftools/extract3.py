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
        return None
    lm = re.search(r"/Length\s+(\d+)", body[:m.start()])
    if lm:
        ln = int(lm.group(1))
        data = body[m.end():m.end() + ln]
    else:
        data = body[m.end():]
        e = data.rfind("endstream")
        if e != -1:
            data = data[:e]
        data = data.rstrip("\r\n")
    b = data.encode("latin-1")
    if "FlateDecode" in body[:m.start()]:
        b = zlib.decompress(b)
    return b

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
    data = get_stream(int(m.group(1)))
    if data:
        cmap.update(parse_cmap(data))

pages = [num for num in objs if "/Type" in objs[num] and re.search(r"/Type\s*/Page(?![sA-Za-z])", objs[num])]
pages.sort()

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

def dec(b):
    if len(b) % 2: b += b"\x00"
    return "".join(cmap.get((b[i] << 8) | b[i+1], "") for i in range(0, len(b) - 1, 2))

num_re = re.compile(rb"^[-\d.]+$")

def runs_of(content):
    runs = []
    i = 0; n = len(content)
    x = y = 0.0
    pending_str = None
    pending_arr = None
    while i < n:
        c = content[i]
        if c == 0x28:
            depth = 1; j = i + 1; buf = bytearray()
            while j < n:
                ch = content[j]
                if ch == 0x5C:
                    buf.append(ch)
                    if j + 1 < n: buf.append(content[j+1])
                    j += 2; continue
                if ch == 0x28: depth += 1
                elif ch == 0x29:
                    depth -= 1
                    if depth == 0: break
                buf.append(ch); j += 1
            pending_str = unescape(bytes(buf)); pending_arr = None
            i = j + 1; continue
        if c == 0x3C and i + 1 < n and content[i+1] != 0x3C:
            j = content.find(b">", i)
            if j == -1: break
            hx = re.sub(rb"[^0-9A-Fa-f]", b"", content[i+1:j])
            if len(hx) % 2: hx += b"0"
            pending_str = bytes.fromhex(hx.decode()); pending_arr = None
            i = j + 1; continue
        if c == 0x3C and i + 1 < n and content[i+1] == 0x3C:
            i += 2; continue
        if c == 0x5B:
            j = content.find(b"]", i)
            if j == -1: break
            pending_arr = content[i+1:j]; pending_str = None
            i = j + 1; continue
        if (0x41 <= c <= 0x5A) or (0x61 <= c <= 0x7A) or c in (0x2A, 0x27, 0x22):
            j = i
            while j < n and ((0x41 <= content[j] <= 0x5A) or (0x61 <= content[j] <= 0x7A) or content[j] in (0x2A, 0x27, 0x22)):
                j += 1
            op = content[i:j].decode("latin-1")
            if op == "Tj" and pending_str is not None:
                t = dec(pending_str)
                if t.strip(): runs.append({"x": round(x, 2), "y": round(y, 2), "t": t})
            elif op == "TJ" and pending_arr is not None:
                parts = []
                for m2 in re.finditer(rb"\((?:\\.|[^\\()])*\)|<[0-9A-Fa-f\s]*>", pending_arr):
                    tok = m2.group(0)
                    if tok.startswith(b"("):
                        parts.append(dec(unescape(tok[1:-1])))
                    else:
                        hx = re.sub(rb"[^0-9A-Fa-f]", b"", tok[1:-1])
                        if len(hx) % 2: hx += b"0"
                        parts.append(dec(bytes.fromhex(hx.decode())))
                t = "".join(parts)
                if t.strip(): runs.append({"x": round(x, 2), "y": round(y, 2), "t": t})
            elif op in ("Td", "TD"):
                # operands preceding: numbers already consumed by tokenizer below
                pass
            elif op == "Tm":
                pass
            pending_str = None; pending_arr = None
            i = j; continue
        i += 1
    return runs

# need operand-aware Td/Tm handling; do a second pass tokenizer
tok_re = re.compile(rb"(\[.*?\]|\((?:\\.|[^\\()])*\)|<[0-9A-Fa-f\s]*>|/[^\s/\[\]<>()]+|[-+]?\d*\.?\d+|<<|>>|[A-Za-z*'\"]+)", re.S)

def runs2(content):
    runs = []
    stack = []
    x = y = 0.0
    for m in tok_re.finditer(content):
        tok = m.group(1)
        c0 = tok[:1]
        if tok.startswith(b"("):
            stack.append(("str", unescape(tok[1:-1])))
        elif tok.startswith(b"<") and len(tok) > 1:
            hx = re.sub(rb"[^0-9A-Fa-f]", b"", tok[1:-1])
            if len(hx) % 2: hx += b"0"
            stack.append(("str", bytes.fromhex(hx.decode())))
        elif tok.startswith(b"["):
            stack.append(("arr", tok))
        elif tok.startswith(b"/"):
            stack.append(("name", tok))
        elif re.fullmatch(rb"[-+]?\d*\.?\d+", tok):
            stack.append(("num", float(tok)))
        else:
            op = tok.decode("latin-1")
            if op == "Tj":
                for kind, val in reversed(stack):
                    if kind == "str":
                        t = dec(val)
                        if t.strip():
                            runs.append({"x": round(x, 2), "y": round(y, 2), "t": t})
                        break
            elif op == "TJ":
                for kind, val in reversed(stack):
                    if kind == "arr":
                        parts = []
                        for m2 in re.finditer(rb"\((?:\\.|[^\\()])*\)|<[0-9A-Fa-f\s]*>", val):
                            t2 = m2.group(0)
                            if t2.startswith(b"("):
                                parts.append(dec(unescape(t2[1:-1])))
                            else:
                                hx = re.sub(rb"[^0-9A-Fa-f]", b"", t2[1:-1])
                                if len(hx) % 2: hx += b"0"
                                parts.append(dec(bytes.fromhex(hx.decode())))
                        t = "".join(parts)
                        if t.strip():
                            runs.append({"x": round(x, 2), "y": round(y, 2), "t": t})
                        break
            elif op == "Td":
                nums = [v for k, v in stack if k == "num"]
                if len(nums) >= 2:
                    x += nums[-2]; y += nums[-1]
            elif op == "TD":
                nums = [v for k, v in stack if k == "num"]
                if len(nums) >= 2:
                    x += nums[-2]; y += nums[-1]
            elif op == "Tm":
                nums = [v for k, v in stack if k == "num"]
                if len(nums) >= 6:
                    x, y = nums[-2], nums[-1]
            elif op == "BT":
                x = y = 0.0
                stack = []
                continue
            elif op == "ET":
                stack = []
                continue
            stack = []
    return runs

out = {}
for idx in range(1, 165):
    pnum = pages[idx - 1]
    body = objs[pnum]
    m = re.search(r"/Contents\s*(\[[^\]]*\]|\d+\s+0\s+R)", body)
    refs = sorted(set(int(v) for v in re.findall(r"(\d+)\s+0\s+R", m.group(1))))
    allruns = []
    for r in refs:
        data = get_stream(r)
        allruns.extend(runs2(data))
    out[str(idx)] = allruns

with open(r"E:\单词\_pdftools\runs1-164.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False)

print("pages:", len(out))
sample = out["164"]
for r in sample[:40]:
    print(r)
