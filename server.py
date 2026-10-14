# -*- coding: utf-8 -*-
"""英语翻译工具 —— 本地中转服务。

作用：在前端(index.html)和 DeepSeek API 之间做中转，
把 API key 保留在本机，避免泄露，同时解决浏览器跨域限制。
零依赖，仅用 Python 标准库。
"""
import json
import os
import threading
import time
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')
API_URL = 'https://api.deepseek.com/chat/completions'
MODEL = 'deepseek-chat'


def load_api_key():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    key = (cfg.get('api_key') or '').strip()
    if not key or key.startswith('在这里'):
        return ''
    return key


def call_deepseek(messages, json_mode=False):
    key = load_api_key()
    if not key:
        raise RuntimeError('未配置 API key：请用记事本打开 config.json，填入 DeepSeek 的 api_key')
    payload = {
        'model': MODEL,
        'messages': messages,
        'temperature': 0.3,
        'max_tokens': 8192,
    }
    if json_mode:
        payload['response_format'] = {'type': 'json_object'}
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + key,
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    return data['choices'][0]['message']['content']


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, filename):
        path = os.path.join(BASE_DIR, filename)
        with open(path, 'rb') as f:
            data = f.read()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.end_headers()

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            self._serve_file('index.html')
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/api/deepseek':
            try:
                length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(length).decode('utf-8'))
                messages = body.get('messages')
                json_mode = bool(body.get('json_mode'))
                content = call_deepseek(messages, json_mode)
                self._send_json({'ok': True, 'content': content})
            except Exception as e:
                self._send_json({'ok': False, 'error': str(e)}, 500)
        else:
            self.send_error(404)

    def log_message(self, fmt, *args):
        pass


def open_browser():
    time.sleep(0.8)
    webbrowser.open('http://127.0.0.1:%d/' % PORT)


if __name__ == '__main__':
    httpd = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
    threading.Thread(target=open_browser, daemon=True).start()
    print('English translation tool running at http://127.0.0.1:%d' % PORT)
    print('Press Ctrl+C to stop.')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Bye.')
