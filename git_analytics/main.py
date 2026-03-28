from wsgiref.simple_server import make_server

from git_analytics.web_app import create_web_app


from git_analytics.engines.repository_composition import RepositoryCompositionEngine
from git_analytics.engines.metrics import GitHistoryWalker, MetricsEngine, InvalidGitRepositoryException
from git_analytics.collectors.authors import AuthorCommitsCounter
from git_analytics.collectors.code_curn_21d import CodeChurnCollector
from git_analytics.collectors.summary import CommitsSummaryCollector
from git_analytics.metrics.bus_factor import BusFactorMetric
from git_analytics.collectors.commit_type import CommitTypeCollector
from git_analytics.collectors.weekly_file_extensions import WeeklyFileExtensionsCollector
from git_analytics.post_engine import enrich_result_data

DAYS = 10_000

# DAYS = 365


def run():
    try:
        history = GitHistoryWalker(since_days=DAYS)
    except InvalidGitRepositoryException as ex:
        print(ex)
        return

    collectors = [
        AuthorCommitsCounter(),
        CodeChurnCollector(),
        CommitsSummaryCollector(),
        CommitTypeCollector(),
        WeeklyFileExtensionsCollector(),
    ]

    metrics_engine = MetricsEngine(history=history, collectors=collectors)
    file_engine = RepositoryCompositionEngine()

    data = metrics_engine.run()

    result_data = {
        "activity": data,
        "codebase": file_engine.run(),
        "risks": {
            "bus_factor": BusFactorMetric(data).compute(),
        },
    }

    # Обогащаем данные дополнительными метриками
    result_data = enrich_result_data(result_data)

    web_app = create_web_app(data=result_data)

    with make_server("", 8000, web_app) as httpd:
        print("Web service started at http://localhost:8000/")
        print("Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping by Ctrl+C...")
        finally:
            httpd.server_close()
            print("Web service stopped")


if __name__ == "__main__":
    run()
