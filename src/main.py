"""
Минимальный HTTP-сервер на Python (вариативная часть практики).

Запуск:
    python src/main.py

Проверка:
    http://127.0.0.1:8080/
    http://127.0.0.1:8080/health
"""

from __future__ import annotations

import socket
from datetime import datetime, UTC


HOST = "127.0.0.1"
PORT = 8080


def build_response(status_code: int, reason: str, body: str, content_type: str = "text/html; charset=utf-8") -> bytes:
    body_bytes = body.encode("utf-8")
    headers = [
        f"HTTP/1.1 {status_code} {reason}",
        f"Date: {datetime.now(UTC).strftime('%a, %d %b %Y %H:%M:%S GMT')}",
        "Server: PracticeHTTP/1.0",
        f"Content-Type: {content_type}",
        f"Content-Length: {len(body_bytes)}",
        "Connection: close",
        "",
        "",
    ]
    return "\r\n".join(headers).encode("utf-8") + body_bytes


def handle_request(raw_request: bytes) -> bytes:
    try:
        request_text = raw_request.decode("utf-8", errors="replace")
        request_line = request_text.splitlines()[0]
        method, path, _ = request_line.split(" ")
    except (IndexError, ValueError):
        return build_response(400, "Bad Request", "<h1>400 Bad Request</h1>")

    if method != "GET":
        return build_response(405, "Method Not Allowed", "<h1>405 Method Not Allowed</h1>")

    if path == "/":
        body = """
        <html>
          <head><title>Practice HTTP Server</title></head>
          <body>
            <h1>Сервер работает</h1>
            <p>Это минимальный HTTP-сервер на сокетах.</p>
          </body>
        </html>
        """
        return build_response(200, "OK", body)

    if path == "/health":
        return build_response(200, "OK", '{"status":"ok"}', "application/json; charset=utf-8")

    return build_response(404, "Not Found", "<h1>404 Not Found</h1>")


def run_server() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(5)

        print(f"[INFO] HTTP-сервер запущен: http://{HOST}:{PORT}")

        while True:
            client_socket, client_address = server.accept()
            with client_socket:
                request_data = client_socket.recv(4096)
                if not request_data:
                    continue

                response = handle_request(request_data)
                client_socket.sendall(response)
                print(f"[INFO] Обработан запрос от {client_address}")


if __name__ == "__main__":
    run_server()
