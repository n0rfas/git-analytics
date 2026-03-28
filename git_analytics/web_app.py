import os
from typing import Dict
from dataclasses import is_dataclass, asdict
from datetime import date, datetime

from falcon import App as FalconApp


def create_web_app(data: Dict[str, object]) -> FalconApp:
    app = FalconApp()

    class StatisticsResource:
        def _to_json_serializable(self, obj):
            """Recursively convert dataclasses and other objects to JSON-serializable dict."""
            if isinstance(obj, (date, datetime)):
                return obj.isoformat()
            elif is_dataclass(obj) and not isinstance(obj, type):
                return self._to_json_serializable(asdict(obj))
            elif isinstance(obj, dict):
                return {key: self._to_json_serializable(value) for key, value in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [self._to_json_serializable(item) for item in obj]
            else:
                return obj

        def on_get(self, req, resp):
            resp.media = self._to_json_serializable(data)

    app.add_route("/api/statistics", StatisticsResource())

    static_path = os.path.dirname(os.path.abspath(__file__)) + "/static/"
    app.add_static_route("/", static_path)

    return app
