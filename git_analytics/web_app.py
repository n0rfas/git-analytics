import os
from datetime import datetime

import falcon  # type: ignore

from git_analytics.engine import CommitAnalyticsEngine


class GitAnalyticsResource:
    def __init__(self, engine: CommitAnalyticsEngine) -> None:
        self._engine = engine

    def on_get_index(self, req, resp):
        raise falcon.HTTPMovedPermanently("index.html")

    def on_get_statistics(self, req, resp):
        start_str = req.get_param("start_date")
        stop_str = req.get_param("stop_date")

        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date() if start_str else None
            stop_date = datetime.strptime(stop_str, "%Y-%m-%d").date() if stop_str else None
        except ValueError:
            raise falcon.HTTPBadRequest("Invalid date format", "Use YYYY-MM-DD")

        data = self._engine.run(start_date=start_date, stop_date=stop_date)
        result = {key: value.to_dict() for key, value in data.items()}

        resp.media = result


def create_web_app(engine: CommitAnalyticsEngine) -> falcon.App:
    app = falcon.App()
    analytics_resource = GitAnalyticsResource(engine)

    static_path = os.path.dirname(os.path.abspath(__file__)) + "/static/"
    app.add_static_route("/", static_path)
    app.add_route("/", analytics_resource, suffix="index")
    app.add_route("/api/statistics", analytics_resource, suffix="statistics")

    return app
