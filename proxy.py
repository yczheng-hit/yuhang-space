#!/usr/bin/env python3
import http.server
import socketserver
import urllib.request
import os

FRONTEND_DIR = "/home/zycccccc/workspace/web-dev/yuhang-space/frontend/dist"
BACKEND_URL = "http://localhost:8000"

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def _is_api(self):
        return self.path.startswith('/api/') or self.path.startswith('/docs') or self.path.startswith('/openapi.json')

    def do_GET(self):
        if self._is_api():
            self.proxy_request()
        else:
            # SPA fallback: if file doesn't exist, serve index.html
            file_path = os.path.join(FRONTEND_DIR, self.path.lstrip('/'))
            if os.path.isfile(file_path):
                super().do_GET()
            else:
                self.path = '/index.html'
                super().do_GET()

    def do_POST(self):
        if self._is_api():
            self.proxy_request()
        else:
            self.send_error(404)

    def do_PUT(self):
        if self._is_api():
            self.proxy_request()
        else:
            self.send_error(404)

    def do_DELETE(self):
        if self._is_api():
            self.proxy_request()
        else:
            self.send_error(404)

    def do_PATCH(self):
        if self._is_api():
            self.proxy_request()
        else:
            self.send_error(404)

    def proxy_request(self):
        url = BACKEND_URL + self.path
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        req = urllib.request.Request(url, data=body, method=self.command)
        for key, value in self.headers.items():
            if key.lower() not in ('host', 'transfer-encoding'):
                req.add_header(key, value)

        try:
            with urllib.request.urlopen(req) as response:
                self.send_response(response.status)
                for key, value in response.getheaders():
                    if key.lower() not in ('transfer-encoding', 'connection'):
                        self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            for key, value in e.headers.items():
                if key.lower() not in ('transfer-encoding', 'connection'):
                    self.send_header(key, value)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_error(502, str(e))

if __name__ == "__main__":
    PORT = 8080
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), ProxyHandler) as httpd:
        print(f"Proxy server running on port {PORT}")
        httpd.serve_forever()
