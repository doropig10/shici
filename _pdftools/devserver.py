"""拾词开发用静态服务器：改动 assets 后浏览器自动刷新，手机同网段也能直接打开。

用法：
    python _pdftools/devserver.py [端口]

打开输出的地址即可。改 index.html / app.js / core.js / book-data.js / style.css 后，
已打开的页面会在约 0.6 秒内自动刷新，不用重装 APK。
"""
import hashlib
import http.server
import socket
import sys
from pathlib import Path

ROOT = Path(r"E:\单词\app\src\main\assets")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765

INJECT = (
    "<script>(function(){var r=null;function poll(){"
    "fetch('/__rev',{cache:'no-store'}).then(function(x){return x.text();}).then(function(t){"
    "if(r===null){r=t;}else if(t!==r){location.reload();}}).catch(function(){});}"
    "poll();setInterval(poll,600);})();</script>"
)


def revision():
    h = hashlib.md5()
    for p in sorted(ROOT.rglob("*")):
        if p.is_file():
            st = p.stat()
            h.update(f"{p.name}:{st.st_mtime_ns}:{st.st_size}".encode())
    return h.hexdigest()


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, max-age=0")
        super().end_headers()

    def do_GET(self):
        if self.path.split("?")[0] == "/__rev":
            body = revision().encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path.split("?")[0] in ("/", "/index.html"):
            html = (ROOT / "index.html").read_text(encoding="utf-8")
            if "</body>" in html:
                html = html.replace("</body>", INJECT + "</body>")
            body = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def lan_ips():
    ips = set()
    try:
        for res in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ips.add(res[4][0])
    except OSError:
        pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ips.add(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    return sorted(i for i in ips if not i.startswith("127."))


if __name__ == "__main__":
    if not (ROOT / "index.html").exists():
        sys.exit(f"assets not found: {ROOT}")
    print(f"serving {ROOT}")
    print(f"  本机预览  http://127.0.0.1:{PORT}")
    for ip in lan_ips():
        print(f"  手机预览  http://{ip}:{PORT}")
    http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
