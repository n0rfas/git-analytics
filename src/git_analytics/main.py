
import os
from collections import Counter, defaultdict

from flask import Flask, send_from_directory
from git import Repo

repo: Repo = Repo()
app = Flask('GitAnalitics')

app.root_path = os.path.dirname(os.path.abspath(__file__))

dict_authors = Counter()
dict_day_of_week = defaultdict(Counter)
dict_hour_of_day = defaultdict(Counter)
dict_day_of_month = defaultdict(Counter)

dict_tags = Counter()
dict_tags_of_author = defaultdict(Counter)

# feature, fix, docs, style, refactor, test, chore, merge, WIP, not_specified
TYPE_LIST = ['feature', 'fix', 'docs', 'style', 'refactor', 'test', 'chore', 'merge', 'wip',]
def _get_type_list(commit_message: str) -> list[str]:
    part_commit_message = commit_message.split(':')[0]
    return [tag for tag in TYPE_LIST if tag in part_commit_message]


for c in repo.iter_commits():
    dict_authors[c.author.name] += 1
    dict_day_of_week[c.committed_datetime.weekday()][c.author.name] +=1
    dict_hour_of_day[c.committed_datetime.hour][c.author.name] +=1
    dict_day_of_month[c.committed_datetime.day][c.author.name] +=1

    tags = _get_type_list(c.message)
    for tag in tags:
        dict_tags[tag] += 1
        dict_tags_of_author[c.author.name][tag] += 1

@app.route("/")
def index():
    return send_from_directory('.', 'index.html')


@app.route("/about")
def about():
    l = list(repo.iter_commits())
    data = {
        "url_repository" : repo.remotes.origin.url,
        "branch_name": repo.active_branch.name,
        "date_first_commit": l[-1].committed_datetime,
        "date_last_commit": l[0].committed_datetime,
        "total_number_commit": len(l),
    }
    return data


@app.route('/authors')
def authors():
    return dict_authors


@app.route('/week')
def commits_by_day_of_week_detail():
    return {
        'Monday': dict_day_of_week[0],
        'Tuesday': dict_day_of_week[1],
        'Wednesday': dict_day_of_week[2],
        'Thursday': dict_day_of_week[3],
        'Friday': dict_day_of_week[4],
        'Saturday': dict_day_of_week[5],
        'Sunday': dict_day_of_week[6],
    }


@app.route('/day')
def commits_by_hour_of_day_detail():
    return { hour:dict_hour_of_day[hour] for hour in range(0,24)}


@app.route('/month')
def commits_by_day_of_month_detail():
    return { day:dict_day_of_month[day] for day in range(1,32)}


def main():
    app.run(host='0.0.0.0')
