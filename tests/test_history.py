from git_analytics.history import GitHistoryWalker


def test_git_history_walker():
    walker = GitHistoryWalker()

    commits = list(walker.iter_commits())
    assert len(commits) > 0
