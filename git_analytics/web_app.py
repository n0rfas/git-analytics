import os
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import falcon  # type: ignore

from git_analytics.engine import CommitAnalyticsEngine
from git_analytics.sources import GitCommitSource, populate_sqlite


class GitAnalyticsResource:
    def __init__(self, engine: CommitAnalyticsEngine, db_path: Path, repo=None) -> None:
        self._engine = engine
        self._db_path = db_path
        self._repo = repo

    def on_get_index(self, req, resp):
        raise falcon.HTTPMovedPermanently("index.html")

    def on_get_status(self, req, resp):
        resp.media = {
            "has_data": self._has_data(),
            "can_scan": self._repo is not None,
            "db_folder": str(self._db_path.parent),
        }

    def on_post_open_folder(self, req, resp):
        folder = self._db_path.parent
        folder.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            subprocess.Popen(["explorer", str(folder)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(folder)])
        else:
            subprocess.Popen(["xdg-open", str(folder)])
        resp.media = {"status": "ok"}

    def on_post_scan(self, req, resp):
        if self._repo is None:
            raise falcon.HTTPBadRequest("scan_unavailable", "No git repository available")
        populate_sqlite(GitCommitSource(self._repo), self._db_path)
        resp.media = {"status": "ok", "commit_count": self._count_commits()}

    def on_get_statistics(self, req, resp):
        start_str = req.get_param("start_date")
        stop_str = req.get_param("stop_date")

        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date() if start_str else None
            stop_date = datetime.strptime(stop_str, "%Y-%m-%d").date() if stop_str else None
        except ValueError:
            raise falcon.HTTPBadRequest("Invalid date format", "Use YYYY-MM-DD")

        data = self._engine.run(start_date=start_date, stop_date=stop_date)
        result = {key: dict(value) for key, value in data.items()}

        resp.media = result

    def _has_data(self) -> bool:
        if not self._db_path.exists():
            return False
        try:
            conn = sqlite3.connect(self._db_path)
            count = conn.execute("SELECT COUNT(*) FROM commits").fetchone()[0]
            conn.close()
            return count > 0
        except Exception:
            return False

    def _count_commits(self) -> int:
        try:
            conn = sqlite3.connect(self._db_path)
            count = conn.execute("SELECT COUNT(*) FROM commits").fetchone()[0]
            conn.close()
            return count
        except Exception:
            return 0


def create_web_app(engine: CommitAnalyticsEngine, db_path: Path, repo=None) -> falcon.App:
    app = falcon.App()
    resource = GitAnalyticsResource(engine=engine, db_path=db_path, repo=repo)

    static_path = os.path.dirname(os.path.abspath(__file__)) + "/static/"
    app.add_static_route("/", static_path)
    app.add_route("/", resource, suffix="index")
    app.add_route("/api/status", resource, suffix="status")
    app.add_route("/api/scan", resource, suffix="scan")
    app.add_route("/api/open-folder", resource, suffix="open_folder")
    app.add_route("/api/statistics", resource, suffix="statistics")

    return app
