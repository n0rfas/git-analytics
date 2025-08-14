import os
from dataclasses import dataclass, asdict
from collections import Counter, defaultdict
from wsgiref.simple_server import make_server

import falcon
from git import Repo


@dataclass
class Author:
    commits: int = 0
    insertions: int = 0
    deletions: int = 0
    maximum_change: int = 0


repo: Repo = Repo()

dict_authors = defaultdict(Author)
dict_day_of_week = defaultdict(Counter)
dict_hour_of_day = defaultdict(Counter)
dict_day_of_month = defaultdict(Counter)

dict_tags = Counter()
dict_tags_of_author = defaultdict(Counter)
dict_number_lines = defaultdict(int)

TYPE_LIST = [
    "feature",
    "fix",
    "docs",
    "style",
    "refactor",
    "test",
    "chore",
    "merge",
    "wip",
]


def _get_type_list(commit_message: str):
    part_commit_message = commit_message.split(":")[0]
    return [tag for tag in TYPE_LIST if tag in part_commit_message]


lines_in_day = {}
for c in repo.iter_commits():
    dict_authors[c.author.name].commits += 1
    dict_authors[c.author.name].insertions += c.stats.total["insertions"]
    dict_authors[c.author.name].deletions += c.stats.total["deletions"]
    if c.stats.total["lines"] > dict_authors[c.author.name].maximum_change:
        dict_authors[c.author.name].maximum_change = c.stats.total["lines"]

    dict_day_of_week[c.committed_datetime.weekday()][c.author.name] += 1
    dict_hour_of_day[c.committed_datetime.hour][c.author.name] += 1
    dict_day_of_month[c.committed_datetime.day][c.author.name] += 1

    lines_in_day[c.committed_date] = (
        c.stats.total["insertions"] - c.stats.total["deletions"]
    )

    tags = _get_type_list(c.message)
    for tag in tags:
        dict_tags[tag] += 1
        dict_tags_of_author[c.author.name][tag] += 1

dict_authors = dict(
    sorted(dict_authors.items(), key=lambda item: item[1].commits, reverse=True)
)

old_rows = 0
sort_day = list(lines_in_day.keys())
sort_day.sort()
for day in sort_day:
    number_rows = lines_in_day[day]
    dict_number_lines[day] = old_rows + number_rows
    old_rows = old_rows + number_rows


class GitAnaliticsResource:
    def on_get_index(self, req, resp):
        raise falcon.HTTPMovedPermanently("index.html")

    def on_get_about(self, req, resp):
        l = list(repo.iter_commits())
        resp.media = {
            "url_repository": repo.remotes.origin.url,
            "branch_name": repo.active_branch.name,
            "date_first_commit": str(l[-1].committed_datetime),
            "date_last_commit": str(l[0].committed_datetime),
            "total_number_commit": len(l),
        }

    def on_get_authors(self, req, resp):
        resp.media = {
            author: asdict(achievements)
            for author, achievements in dict_authors.items()
        }

    def on_get_month(self, req, resp):
        resp.media = {day: dict_day_of_month[day] for day in range(1, 32)}

    def on_get_week(self, req, resp):
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
        resp.media = {hour: dict_hour_of_day[hour] for hour in range(0, 24)}

    def on_get_number_lines(self, req, resp):
        result = [
            {"date": date, "value": value} for date, value in dict_number_lines.items()
        ]
        resp.media = result


app = falcon.App()
analitics_resource = GitAnaliticsResource()

static_path = os.path.dirname(os.path.abspath(__file__)) + "/static/"
app.add_static_route("/", static_path)
app.add_route("/", analitics_resource, suffix="index")
app.add_route("/api/about", analitics_resource, suffix="about")
app.add_route("/api/authors", analitics_resource, suffix="authors")
app.add_route("/api/month", analitics_resource, suffix="month")
app.add_route("/api/week", analitics_resource, suffix="week")
app.add_route("/api/day", analitics_resource, suffix="day")
app.add_route("/api/lines", analitics_resource, suffix="number_lines")


def run():
    with make_server("", 8000, app) as httpd:
        print("Service started at http://localhost:8000/")
        print("Service start")
        httpd.serve_forever()
        print("Service stopped")


if __name__ == "__main__":
    run()
