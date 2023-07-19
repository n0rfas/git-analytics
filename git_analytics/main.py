import os
from dataclasses import dataclass, asdict
from collections import Counter, defaultdict
from wsgiref.simple_server import make_server
from typing import Optional, Iterator

import falcon
from git import Repo, Commit
from git import InvalidGitRepositoryError

TYPE_LIST = ['feature', 'fix', 'docs', 'style', 'refactor', 'test', 'chore', 'merge', 'wip']


def _get_type_list(commit_message: str):
    part_commit_message = commit_message.split(':')[0]
    return [tag for tag in TYPE_LIST if tag in part_commit_message]


@dataclass
class Author:
    commits: int = 0
    insertions: int = 0
    deletions: int = 0
    maximum_change: int = 0


class Stat:
    authors = defaultdict(Author)
    days_of_week = defaultdict(Counter)
    hours_of_day = defaultdict(Counter)
    days_of_month = defaultdict(Counter)

    tags = Counter()
    tags_of_author = defaultdict(Counter)
    number_lines = defaultdict(int)

    def __init__(self, commits: Iterator[Commit]) -> None:
        print('Try to analyze commits...')
        lines_in_day = {}
        for commit in commits:

            self.authors[commit.author.name].commits += 1
            self.authors[commit.author.name].insertions += commit.stats.total['insertions']
            self.authors[commit.author.name].deletions += commit.stats.total['deletions']
            if commit.stats.total['lines'] > self.authors[commit.author.name].maximum_change:
                self.authors[commit.author.name].maximum_change = commit.stats.total['lines']

            self.days_of_week[commit.committed_datetime.weekday()][commit.author.name] += 1
            self.hours_of_day[commit.committed_datetime.hour][commit.author.name] += 1
            self.days_of_month[commit.committed_datetime.day][commit.author.name] += 1

            lines_in_day[commit.committed_date] = commit.stats.total['insertions'] - commit.stats.total['deletions']

            tags = _get_type_list(commit.message)
            for tag in tags:
                self.tags[tag] += 1
                self.tags_of_author[commit.author.name][tag] += 1

        old_rows = 0
        sort_day = list(lines_in_day.keys())
        sort_day.sort()
        for day in sort_day:
            number_rows = lines_in_day[day]
            self.number_lines[day] = old_rows + number_rows
            old_rows = old_rows + number_rows


class GitAnaliticsResource:
    repo: Optional[Repo] = None
    stat: Optional[Stat] = None

    def __init__(self):
        try:
            self.repo = Repo()
            self.stat = Stat(self.repo.iter_commits())
        except InvalidGitRepositoryError as exc:
            print(f'Git not found in: {exc.args[0]}')

    def on_get_index(self, req, resp):
        raise falcon.HTTPMovedPermanently('index.html')

    def on_get_about(self, req, resp):
        l = list(self.repo.iter_commits())
        resp.media = {
            "url_repository": self.repo.remotes.origin.url,
            "branch_name": self.repo.active_branch.name,
            "date_first_commit": str(l[-1].committed_datetime),
            "date_last_commit": str(l[0].committed_datetime),
            "total_number_commit": len(l),
        }

    def on_get_authors(self, req, resp):
        resp.media = {
            author: asdict(achievements)
            for author, achievements in self.stat.authors.items()
        }

    def on_get_month(self, req, resp):
        resp.media = {day: self.stat.days_of_month[day] for day in range(1, 32)}

    def on_get_week(self, req, resp):
        resp.media = {
            'Monday': self.stat.days_of_week[0],
            'Tuesday': self.stat.days_of_week[1],
            'Wednesday': self.stat.days_of_week[2],
            'Thursday': self.stat.days_of_week[3],
            'Friday': self.stat.days_of_week[4],
            'Saturday': self.stat.days_of_week[5],
            'Sunday': self.stat.days_of_week[6],
        }

    def on_get_day(self, req, resp):
        resp.media = {hour: self.stat.hours_of_day[hour] for hour in range(0, 24)}

    def on_get_number_lines(self, req, resp):
        result = [{'date': date, 'value': value} for date, value in self.stat.number_lines.items()]
        resp.media = result


def run():
    analitics_resource = GitAnaliticsResource()
    if not analitics_resource.repo:
        return

    app = falcon.App()
    static_path = os.path.dirname(os.path.abspath(__file__)) + '/static/'
    app.add_static_route('/', static_path)
    app.add_route('/', analitics_resource, suffix='index')
    app.add_route('/api/about', analitics_resource, suffix='about')
    app.add_route('/api/authors', analitics_resource, suffix='authors')
    app.add_route('/api/month', analitics_resource, suffix='month')
    app.add_route('/api/week', analitics_resource, suffix='week')
    app.add_route('/api/day', analitics_resource, suffix='day')
    app.add_route('/api/lines', analitics_resource, suffix='number_lines')

    with make_server('', 8000, app) as httpd:
        print('Service started at http://localhost:8000/')
        httpd.serve_forever()


if __name__ == '__main__':
    run()
