import os
from collections import Counter, defaultdict
from wsgiref.simple_server import make_server

import falcon
from git import Repo


repo: Repo = Repo()

dict_authors = Counter()
dict_day_of_week = defaultdict(Counter)
dict_hour_of_day = defaultdict(Counter)
dict_day_of_month = defaultdict(Counter)

dict_tags = Counter()
dict_tags_of_author = defaultdict(Counter)


TYPE_LIST = ['feature', 'fix', 'docs', 'style', 'refactor', 'test', 'chore', 'merge', 'wip',]
def _get_type_list(commit_message: str):
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


class GitAnaliticsResource:

    def on_get_index(self, req, resp):
        raise falcon.HTTPMovedPermanently('index.html')
        resp.text = 'addsad'
        
    def on_get_about(self, req, resp):
        l = list(repo.iter_commits())
        resp.media = {
            "url_repository" : repo.remotes.origin.url,
            "branch_name": repo.active_branch.name,
            "date_first_commit": str(l[-1].committed_datetime),
            "date_last_commit": str(l[0].committed_datetime),
            "total_number_commit": len(l),
        }
    
    def on_get_authors(self, req, resp):
        resp.media = dict_authors
        
    def on_get_month(self, req, resp):
        resp.media = { day:dict_day_of_month[day] for day in range(1,32)}

    def on_get_week(self, req, resp):
        resp.media = {
            'Monday': dict_day_of_week[0],
            'Tuesday': dict_day_of_week[1],
            'Wednesday': dict_day_of_week[2],
            'Thursday': dict_day_of_week[3],
            'Friday': dict_day_of_week[4],
            'Saturday': dict_day_of_week[5],
            'Sunday': dict_day_of_week[6],
        }

    def on_get_day(self, req, resp):
        resp.media = { hour:dict_hour_of_day[hour] for hour in range(0,24)}


app = falcon.App()
analitics_resource = GitAnaliticsResource()

static_path= os.path.dirname(os.path.abspath(__file__)) + '/static/'
app.add_static_route('/', static_path)
app.add_route('/', analitics_resource, suffix='index')
app.add_route('/api/about', analitics_resource, suffix='about')
app.add_route('/api/authors', analitics_resource, suffix='authors')
app.add_route('/api/month', analitics_resource, suffix='month')
app.add_route('/api/week', analitics_resource, suffix='week')
app.add_route('/api/day', analitics_resource, suffix='day')


if __name__ == '__main__':
    with make_server('', 8000, app) as httpd:
        print('Service started at http://localhost:8000/')
        httpd.serve_forever()
