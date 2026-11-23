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
        data = body[m.end():m.end() + int(lm.group(1))]
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
                    if lo + idx > hi:
                        break
                    mapping[lo + idx] = bytes.fromhex(it).decode("utf-16-be", "ignore")
    return mapping


cmap = {}
for m in re.finditer(r"/ToUnicode\s+(\d+)\s+0\s+R", s):
    data = get_stream(int(m.group(1)))
    if data:
        cmap.update(parse_cmap(data))
print("cmap", len(cmap), file=sys.stderr)

pages = [n for n in objs if "/Type" in objs[n] and re.search(r"/Type\s*/Page(?![sA-Za-z])", objs[n])]
pages.sort()
print("pages", len(pages), file=sys.stderr)

tok_re = re.compile(rb"(\[.*?\]|\((?:\\.|[^\\()])*\)|<[0-9A-Fa-f\s]*>|/[^\s/\[\]<>()]+|[-+]?\d*\.?\d+|<<|>>|[A-Za-z*'\"]+)", re.S)


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
    if len(b) % 2:
        b += b"\x00"
    return "".join(cmap.get((b[i] << 8) | b[i+1], "") for i in range(0, len(b) - 1, 2))


def runs2(content):
    runs = []
    stack = []
    x = y = 0.0
    for m in tok_re.finditer(content):
        tok = m.group(1)
        if tok.startswith(b"("):
            stack.append(("str", unescape(tok[1:-1])))
        elif tok.startswith(b"<") and len(tok) > 1:
            hx = re.sub(rb"[^0-9A-Fa-f]", b"", tok[1:-1])
            if len(hx) % 2:
                hx += b"0"
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
                                if len(hx) % 2:
                                    hx += b"0"
                                parts.append(dec(bytes.fromhex(hx.decode())))
                        t = "".join(parts)
                        if t.strip():
                            runs.append({"x": round(x, 2), "y": round(y, 2), "t": t})
                        break
            elif op in ("Td", "TD"):
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
    return runs


rows = []
for idx, pnum in enumerate(pages, start=1):
    body = objs[pnum]
    m = re.search(r"/Contents\s*(\[[^\]]*\]|\d+\s+0\s+R)", body)
    if not m:
        continue
    refs = sorted(set(int(v) for v in re.findall(r"(\d+)\s+0\s+R", m.group(1))))
    rs = []
    for r in refs:
        data = get_stream(r)
        if data:
            rs.extend(runs2(data))
    rs = [r for r in rs if r["y"] > 72]

    ln = sorted([r for r in rs if r["x"] < 60 and re.fullmatch(r"\d+", r["t"].strip()) and r["y"] < 745], key=lambda r: -r["y"])
    lw = [r for r in rs if 60 <= r["x"] < 290 and r["y"] < 745]
    rn = sorted([r for r in rs if 290 <= r["x"] < 380 and re.fullmatch(r"\d+", r["t"].strip()) and r["y"] < 745], key=lambda r: -r["y"])
    rt = [r for r in rs if r["x"] >= 380 and r["y"] < 745]

    def bands(nums):
        ys = [n["y"] for n in nums]
        top = 860.0
        out = []
        for i, n in enumerate(nums):
            hi = top if i == 0 else (ys[i - 1] + ys[i]) / 2
            lo = 0.0 if i == len(nums) - 1 else (ys[i] + ys[i + 1]) / 2
            out.append((n, lo, hi))
        return out

    words = {}
    for n, lo, hi in bands(ln):
        lines = sorted([w for w in lw if lo < w["y"] <= hi], key=lambda r: (-r["y"], r["x"]))
        words[int(n["t"])] = " ".join(w["t"].strip() for w in lines)

    means = {}
    for n, lo, hi in bands(rn):
        d = {}
        for r in rt:
            if lo < r["y"] <= hi:
                d.setdefault(round(r["y"] * 2) / 2, []).append(r)
        means[int(n["t"])] = ["".join(x["t"] for x in sorted(d[k], key=lambda r: r["x"])).strip()
                              for k in sorted(d, reverse=True)]

    for n, _, _ in bands(ln):
        num = int(n["t"])
        rows.append({"n": num, "w": words.get(num, ""), "m": [x for x in means.get(num, []) if x.strip()]})

rows.sort(key=lambda r: r["n"])
print("entries", len(rows), file=sys.stderr)
bad = [r for r in rows if not r["w"] or not r["m"]]
print("bad", len(bad), [b["n"] for b in bad][:10], file=sys.stderr)

json.dump(rows, open(r"E:\单词\_pdftools\pdf_all_entries.json", "w", encoding="utf-8"), ensure_ascii=False)
