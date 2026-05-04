"""Презентационный HTTP-сервер на Python для вариативной части практики.

Запуск: python src/main.py
Адрес:  http://127.0.0.1:8080/

Сервер реализован на низком уровне через TCP-сокеты, без Flask/Django.
"""

from __future__ import annotations

import json
import socket
from dataclasses import dataclass
from datetime import UTC, datetime
from html import escape
from urllib.parse import parse_qs, urlparse


HOST = "127.0.0.1"
PORT = 8080
BUFFER_SIZE = 8192
PROJECT_NAME = "PolyQuest"
SERVER_NAME = "PolyQuestSocketHTTP/2.0"
STARTED_AT = datetime.now(UTC)


@dataclass(frozen=True)
class HttpRequest:
    method: str
    target: str
    version: str
    path: str
    query: dict[str, list[str]]


def http_date() -> str:
    return datetime.now(UTC).strftime("%a, %d %b %Y %H:%M:%S GMT")


def build_response(status_code: int, reason: str, body: str | bytes, content_type: str = "text/html; charset=utf-8", extra_headers: dict[str, str] | None = None) -> bytes:
    body_bytes = body if isinstance(body, bytes) else body.encode("utf-8")
    headers = [
        f"HTTP/1.1 {status_code} {reason}",
        f"Date: {http_date()}",
        f"Server: {SERVER_NAME}",
        f"Content-Type: {content_type}",
        f"Content-Length: {len(body_bytes)}",
        "Connection: close",
        "Cache-Control: no-store",
    ]
    if extra_headers:
        headers.extend(f"{name}: {value}" for name, value in extra_headers.items())
    headers.extend(["", ""])
    return "\r\n".join(headers).encode("utf-8") + body_bytes


def parse_request(raw_request: bytes) -> HttpRequest:
    request_text = raw_request.decode("utf-8", errors="replace")
    request_line = request_text.splitlines()[0]
    method, target, version = request_line.split(" ", maxsplit=2)
    parsed_url = urlparse(target)
    return HttpRequest(method.upper(), target, version, parsed_url.path or "/", parse_qs(parsed_url.query))


def page_template(title: str, content: str, active: str = "home") -> str:
    nav_items = {"home": ("/", "Главная"), "about": ("/about", "О сервере"), "routes": ("/routes", "Маршруты"), "status": ("/api/status", "JSON API")}
    nav = "".join(f'<a class="{"active" if key == active else ""}" href="{href}">{label}</a>' for key, (href, label) in nav_items.items())
    return f"""<!doctype html>
<html lang="ru"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{escape(title)} — {PROJECT_NAME} HTTP</title><style>
:root{{--bg:#07111f;--panel:#10223c;--text:#edf7ff;--muted:#a9bed5;--accent:#25d5ff;--green:#45f0a6;--purple:#8b5cf6}}*{{box-sizing:border-box}}body{{margin:0;font-family:Segoe UI,Arial,sans-serif;color:var(--text);line-height:1.65;background:radial-gradient(circle at top left,rgba(37,213,255,.22),transparent 32rem),radial-gradient(circle at top right,rgba(139,92,246,.18),transparent 28rem),var(--bg)}}.wrap{{width:min(1100px,92%);margin:0 auto}}header{{position:sticky;top:0;backdrop-filter:blur(14px);background:rgba(7,17,31,.82);border-bottom:1px solid rgba(255,255,255,.12)}}.nav{{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:14px 0;flex-wrap:wrap}}.brand{{display:flex;align-items:center;gap:10px;font-weight:900}}.badge{{display:grid;place-items:center;width:40px;height:40px;border-radius:14px;color:#06111f;background:linear-gradient(135deg,var(--accent),var(--green))}}nav{{display:flex;gap:8px;flex-wrap:wrap}}nav a{{color:var(--muted);text-decoration:none;padding:8px 12px;border-radius:999px}}nav a.active,nav a:hover{{color:var(--text);background:rgba(37,213,255,.14)}}main{{padding:54px 0}}.hero{{display:grid;grid-template-columns:1.1fr .9fr;gap:28px;align-items:center}}h1{{font-size:clamp(2.2rem,5vw,4.5rem);line-height:1.05;margin:0 0 18px}}h2{{margin-top:0}}.lead{{color:#d8eafa;font-size:1.13rem}}.panel,.card{{background:rgba(16,34,60,.88);border:1px solid rgba(255,255,255,.13);border-radius:24px;padding:24px;box-shadow:0 20px 54px rgba(0,0,0,.25)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px;margin-top:24px}}.metric{{font-size:2.2rem;color:var(--accent);font-weight:900;display:block}}.button{{display:inline-flex;margin-top:18px;padding:12px 18px;border-radius:14px;background:linear-gradient(135deg,var(--accent),var(--green));color:#06111f;text-decoration:none;font-weight:900}}code,pre{{background:#071827;border:1px solid rgba(255,255,255,.12);border-radius:12px;color:#b9f8ff}}code{{padding:2px 7px}}pre{{padding:16px;overflow:auto}}.terminal{{min-height:300px;background:#06111f;border-radius:24px;padding:20px;border:1px solid rgba(37,213,255,.24)}}.dot{{width:12px;height:12px;border-radius:50%;display:inline-block;margin-right:6px;background:var(--green);box-shadow:0 0 18px var(--green)}}footer{{padding:24px 0;color:var(--muted);border-top:1px solid rgba(255,255,255,.12)}}@media(max-width:800px){{.hero{{grid-template-columns:1fr}}}}
</style></head><body><header><div class="wrap nav"><div class="brand"><span class="badge">PQ</span><span>PolyQuest HTTP Server</span></div><nav>{nav}</nav></div></header><main class="wrap">{content}</main><footer><div class="wrap">Вариативная часть практики • собственный HTTP-сервер на Python sockets • {datetime.now().year}</div></footer></body></html>"""


def home_page() -> str:
    uptime = str(datetime.now(UTC) - STARTED_AT).split(".")[0]
    content = f"""<section class="hero"><div><p class="lead">Вариативная часть проекта</p><h1>Красивый HTTP-сервер без фреймворков</h1><p class="lead">Этот сервер написан на чистом Python через TCP-сокеты. Он показывает работу HTTP на низком уровне, но выглядит как полноценная презентационная страница проекта PolyQuest.</p><a class="button" href="/about">Как это работает</a></div><div class="terminal"><p><span class="dot"></span><strong>server online</strong></p><pre>GET / HTTP/1.1\nHost: 127.0.0.1:8080\n\nHTTP/1.1 200 OK\nServer: {SERVER_NAME}</pre></div></section><section class="grid"><article class="card"><span class="metric">{HOST}</span><p>локальный адрес сервера</p></article><article class="card"><span class="metric">{PORT}</span><p>порт для подключения браузера</p></article><article class="card"><span class="metric">{uptime}</span><p>время работы процесса</p></article></section>"""
    return page_template("Главная", content, "home")


def about_page() -> str:
    content = """<section class="panel"><h1>О сервере</h1><p class="lead">Проект не использует веб-фреймворки: соединение принимается через <code>socket</code>, запрос разбирается вручную, ответ собирается из строки статуса, заголовков и HTML-тела.</p><div class="grid"><article class="card"><h2>1. TCP</h2><p>Сервер открывает сокет, привязывается к адресу и ждёт подключения клиента.</p></article><article class="card"><h2>2. HTTP</h2><p>Читается первая строка запроса: метод, путь и версия протокола.</p></article><article class="card"><h2>3. Routing</h2><p>Маршрутизатор выбирает HTML-страницу, JSON-ответ или ошибку 404.</p></article></div></section>"""
    return page_template("О сервере", content, "about")


def routes_page() -> str:
    rows = [("GET /", "главная презентационная страница"), ("GET /about", "описание архитектуры сервера"), ("GET /routes", "список доступных маршрутов"), ("GET /api/status", "JSON со статусом, временем и названием проекта"), ("GET /hello?name=Георгий", "динамическое приветствие через query string")]
    items = "".join(f"<article class='card'><h2>{escape(route)}</h2><p>{text}</p></article>" for route, text in rows)
    return page_template("Маршруты", f"<h1>Маршруты сервера</h1><div class='grid'>{items}</div>", "routes")


def hello_page(request: HttpRequest) -> str:
    name = request.query.get("name", ["гость PolyQuest"])[0]
    safe_name = escape(name[:60])
    content = f"<section class='panel'><h1>Привет, {safe_name}!</h1><p class='lead'>Это динамическая страница: имя берётся из параметра <code>?name=...</code>.</p><a class='button' href='/hello?name=Георгий'>Пример с именем</a></section>"
    return page_template("Приветствие", content, "routes")


def status_json() -> str:
    payload = {"status": "ok", "project": PROJECT_NAME, "server": SERVER_NAME, "host": HOST, "port": PORT, "started_at": STARTED_AT.isoformat(), "time_utc": datetime.now(UTC).isoformat(), "routes": ["/", "/about", "/routes", "/api/status", "/hello?name=Георгий"]}
    return json.dumps(payload, ensure_ascii=False, indent=2)


def error_page(status_code: int, reason: str, message: str) -> str:
    content = f"<section class='panel'><h1>{status_code} — {escape(reason)}</h1><p class='lead'>{escape(message)}</p><a class='button' href='/'>Вернуться на главную</a></section>"
    return page_template(reason, content)


def handle_request(raw_request: bytes) -> tuple[bytes, str, str]:
    try:
        request = parse_request(raw_request)
    except (IndexError, ValueError):
        body = error_page(400, "Bad Request", "Сервер не смог разобрать первую строку HTTP-запроса.")
        return build_response(400, "Bad Request", body), "?", "?"
    if request.method != "GET":
        body = error_page(405, "Method Not Allowed", "Этот учебный сервер поддерживает только GET-запросы.")
        return build_response(405, "Method Not Allowed", body, extra_headers={"Allow": "GET"}), request.method, request.path
    routes = {
        "/": lambda: build_response(200, "OK", home_page()),
        "/about": lambda: build_response(200, "OK", about_page()),
        "/routes": lambda: build_response(200, "OK", routes_page()),
        "/hello": lambda: build_response(200, "OK", hello_page(request)),
        "/api/status": lambda: build_response(200, "OK", status_json(), "application/json; charset=utf-8"),
        "/health": lambda: build_response(200, "OK", '{"status":"ok"}', "application/json; charset=utf-8"),
    }
    if request.path in routes:
        return routes[request.path](), request.method, request.path
    body = error_page(404, "Not Found", f"Маршрут {request.path} не найден. Откройте /routes, чтобы увидеть доступные адреса.")
    return build_response(404, "Not Found", body), request.method, request.path


def run_server() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(10)
        print(f"[INFO] {SERVER_NAME} запущен: http://{HOST}:{PORT}")
        print("[INFO] Доступные страницы: /, /about, /routes, /api/status, /hello?name=Георгий")
        print("[INFO] Для остановки нажмите Ctrl+C")
        while True:
            client_socket, client_address = server.accept()
            with client_socket:
                request_data = client_socket.recv(BUFFER_SIZE)
                if not request_data:
                    continue
                response, method, path = handle_request(request_data)
                client_socket.sendall(response)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {client_address[0]}:{client_address[1]} -> {method} {path}")


if __name__ == "__main__":
    try:
        run_server()
    except KeyboardInterrupt:
        print("\n[INFO] Сервер остановлен пользователем")