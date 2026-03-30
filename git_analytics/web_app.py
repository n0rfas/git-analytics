import json
import os
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from typing import Callable, Dict


def create_web_app(data: Dict[str, object]) -> Callable:
    static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

    def _to_json_serializable(obj):
        """Recursively convert dataclasses and other objects to JSON-serializable dict."""
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        elif is_dataclass(obj) and not isinstance(obj, type):
            return _to_json_serializable(asdict(obj))
        elif isinstance(obj, dict):
            return {key: _to_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [_to_json_serializable(item) for item in obj]
        else:
            return obj

    def _serve_static_file(environ, start_response, file_path):
        try:
            with open(file_path, "rb") as f:
                content = f.read()

            if file_path.endswith(".html"):
                content_type = "text/html; charset=utf-8"
            elif file_path.endswith(".js"):
                content_type = "application/javascript; charset=utf-8"
            elif file_path.endswith(".css"):
                content_type = "text/css; charset=utf-8"
            elif file_path.endswith(".json"):
                content_type = "application/json; charset=utf-8"
            elif file_path.endswith(".png"):
                content_type = "image/png"
            elif file_path.endswith(".jpg") or file_path.endswith(".jpeg"):
                content_type = "image/jpeg"
            elif file_path.endswith(".svg"):
                content_type = "image/svg+xml"
            elif file_path.endswith(".ico"):
                content_type = "image/x-icon"
            else:
                content_type = "application/octet-stream"

            start_response("200 OK", [("Content-Type", content_type), ("Content-Length", str(len(content)))])
            return [content]
        except FileNotFoundError:
            start_response("404 Not Found", [("Content-Type", "text/plain")])
            return [b"404 - File Not Found"]
        except Exception as e:
            start_response("500 Internal Server Error", [("Content-Type", "text/plain")])
            return [f"500 - Internal Server Error: {str(e)}".encode("utf-8")]

    def wsgi_app(environ, start_response):
        """WSGI application."""
        path = environ.get("PATH_INFO", "/")
        method = environ.get("REQUEST_METHOD", "GET")

        # API endpoint
        if path == "/api/statistics" and method == "GET":
            try:
                serializable_data = _to_json_serializable(data)
                json_data = json.dumps(serializable_data, ensure_ascii=False, indent=2)
                response_body = json_data.encode("utf-8")

                start_response(
                    "200 OK",
                    [("Content-Type", "application/json; charset=utf-8"), ("Content-Length", str(len(response_body)))],
                )
                return [response_body]
            except Exception as e:
                error_body = json.dumps({"error": str(e)}).encode("utf-8")
                start_response(
                    "500 Internal Server Error",
                    [("Content-Type", "application/json; charset=utf-8"), ("Content-Length", str(len(error_body)))],
                )
                return [error_body]

        # static files
        if path == "/":
            path = "/index.html"

        # Security: prevent path traversal
        path = path.lstrip("/")
        if ".." in path or path.startswith("/"):
            start_response("403 Forbidden", [("Content-Type", "text/plain")])
            return [b"403 - Forbidden"]

        file_path = os.path.join(static_path, path)

        # Security: ensure the file is within the static directory
        if not os.path.abspath(file_path).startswith(os.path.abspath(static_path)):
            start_response("403 Forbidden", [("Content-Type", "text/plain")])
            return [b"403 - Forbidden"]

        return _serve_static_file(environ, start_response, file_path)

    return wsgi_app
