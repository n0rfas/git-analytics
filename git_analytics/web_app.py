import os
from typing import Any, Dict

import falcon


class GitAnalyticsResource:
    def __init__(self, data: Dict[str, Any] = None) -> None:
        self._data = data or {}

    def on_get_index(self, req, resp):
        raise falcon.HTTPMovedPermanently("index.html")

    def on_get_about(self, req, resp):
        resp.media = {
            "url_repository": self._data.get("about", {}).get("url_repository", ""),
            "branch_name": self._data.get("about", {}).get("branch_name", ""),
            "date_first_commit": self._data.get("about", {}).get(
                "date_first_commit", ""
            ),
            "date_last_commit": self._data.get("about", {}).get("date_last_commit", ""),
            "total_number_commit": self._data.get("about", {}).get(
                "total_number_commit", 0
            ),
        }

    def on_get_authors(self, req, resp):
        resp.media = self._data.get("authors_statistics", {})

    def on_get_month(self, req, resp):
        resp.media = {
            day: self._data.get("historical_statistics", {})
            .get("dict_day_of_month", {})
            .get(day, {})
            for day in range(1, 32)
        }

    def on_get_week(self, req, resp):
        dict_day_of_week = self._data.get("historical_statistics", {}).get(
            "dict_day_of_week", {}
        )
        resp.media = {
            "Monday": dict_day_of_week[0],
            "Tuesday": dict_day_of_week[1],
            "Wednesday": dict_day_of_week[2],
            "Thursday": dict_day_of_week[3],
            "Friday": dict_day_of_week[4],
            "Saturday": dict_day_of_week[5],
            "Sunday": dict_day_of_week[6],
        }

    def on_get_day(self, req, resp):
        resp.media = {
            day: self._data.get("historical_statistics", {})
            .get("dict_hour_of_day", {})
            .get(day, {})
            for day in range(0, 24)
        }

    def on_get_number_lines(self, req, resp):
        resp.media = self._data.get("lines_statistics", {})


def create_web_app(data: Dict[str, Any]) -> falcon.App:
    app = falcon.App()
    analytics_resource = GitAnalyticsResource(data)

    static_path = os.path.dirname(os.path.abspath(__file__)) + "/static/"
    app.add_static_route("/", static_path)
    app.add_route("/", analytics_resource, suffix="index")
    app.add_route("/api/about", analytics_resource, suffix="about")
    app.add_route("/api/authors", analytics_resource, suffix="authors")
    app.add_route("/api/month", analytics_resource, suffix="month")
    app.add_route("/api/week", analytics_resource, suffix="week")
    app.add_route("/api/day", analytics_resource, suffix="day")
    app.add_route("/api/lines", analytics_resource, suffix="number_lines")

    return app
