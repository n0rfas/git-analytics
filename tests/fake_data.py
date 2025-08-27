from datetime import datetime, timezone, timedelta

from git_analytics.entities import AnalyticsCommit

FAKE_COMMITS = [
    AnalyticsCommit(
        sha="06f9f86dc0a83997b7800d1df71a677e1d38a996",
        commit_author="Bob",
        committed_datetime=datetime(
            2025, 1, 7, 11, 45, 4, tzinfo=timezone(timedelta(days=-1, seconds=79200))
        ),
        lines_insertions=781,
        lines_deletions=513,
        files_changed=53,
        message="refactor(core): unify error handling",
    ),
    AnalyticsCommit(
        sha="458bb14985083241b2cbb33f9b890422755f967a",
        commit_author="Bob",
        committed_datetime=datetime(
            2025, 1, 7, 18, 35, 7, tzinfo=timezone(timedelta(days=-1, seconds=79200))
        ),
        lines_insertions=760,
        lines_deletions=165,
        files_changed=25,
        message="refactor(core): unify error handling",
    ),
    AnalyticsCommit(
        sha="8d65aa6e01cc7e02b7a25f34e6427c349069c4d0",
        commit_author="Bob",
        committed_datetime=datetime(
            2025, 1, 5, 18, 15, 37, tzinfo=timezone(timedelta(days=-1, seconds=79200))
        ),
        lines_insertions=314,
        lines_deletions=172,
        files_changed=24,
        message="refactor(core): extract domain modules",
    ),
    AnalyticsCommit(
        sha="469aeada82e913c33ae0a56adad7642275f9269f",
        commit_author="Alice",
        committed_datetime=datetime(
            2025, 1, 5, 18, 5, 5, tzinfo=timezone(timedelta(seconds=7200))
        ),
        lines_insertions=517,
        lines_deletions=40,
        files_changed=12,
        message="perf(ui): defer non-critical scripts",
    ),
    AnalyticsCommit(
        sha="0525408aec339f9e7351c4ccf82fbcb7270d3065",
        commit_author="Alice",
        committed_datetime=datetime(
            2025, 1, 5, 15, 15, 59, tzinfo=timezone(timedelta(seconds=7200))
        ),
        lines_insertions=225,
        lines_deletions=164,
        files_changed=9,
        message="style(ui): tweak spacing and typography",
    ),
    AnalyticsCommit(
        sha="69e1bc10926fcac1328c69f8d1ecf11695e2130b",
        commit_author="Dave",
        committed_datetime=datetime(
            2025, 1, 5, 14, 40, 28, tzinfo=timezone(timedelta(seconds=7200))
        ),
        lines_insertions=118,
        lines_deletions=23,
        files_changed=3,
        message="ci: cache pip and node modules",
    ),
    AnalyticsCommit(
        sha="2f92173be965e173dbd7da5fc1230215e69ace2a",
        commit_author="Alice",
        committed_datetime=datetime(
            2025, 1, 4, 14, 35, 1, tzinfo=timezone(timedelta(seconds=7200))
        ),
        lines_insertions=391,
        lines_deletions=162,
        files_changed=2,
        message="chore(ui): update Bootstrap and Popper",
    ),
    AnalyticsCommit(
        sha="a70b198888da997fce325aac67af5c2c4a389a55",
        commit_author="Dave",
        committed_datetime=datetime(
            2025, 1, 4, 14, 5, 6, tzinfo=timezone(timedelta(seconds=7200))
        ),
        lines_insertions=100,
        lines_deletions=54,
        files_changed=7,
        message="ci: add GitHub Actions for test/lint",
    ),
    AnalyticsCommit(
        sha="18527efbeae429ce21ac538e50dcb3a7ab39e9a7",
        commit_author="Oscar",
        committed_datetime=datetime(
            2025, 1, 3, 13, 30, 44, tzinfo=timezone(timedelta(days=-1, seconds=79200))
        ),
        lines_insertions=599,
        lines_deletions=343,
        files_changed=12,
        message="feat: SSR for product page",
    ),
    AnalyticsCommit(
        sha="1471c96f34354d9f4af2f9801192945986e50bcd",
        commit_author="Carol",
        committed_datetime=datetime(2025, 1, 3, 12, 40, 8, tzinfo=timezone.utc),
        lines_insertions=614,
        lines_deletions=305,
        files_changed=12,
        message="feat(api): payment webhook handler",
    ),
    AnalyticsCommit(
        sha="a02f4604ea33b882dbc79b3223a7dc1dbb9412e2",
        commit_author="Oscar",
        committed_datetime=datetime(
            2025, 1, 3, 12, 20, 13, tzinfo=timezone(timedelta(days=-1, seconds=79200))
        ),
        lines_insertions=623,
        lines_deletions=381,
        files_changed=1,
        message="fix: CORS preflight cache mismatch",
    ),
    AnalyticsCommit(
        sha="8f14490b383d3cb41e686d64f554879f44f6e0b2",
        commit_author="Alice",
        committed_datetime=datetime(
            2025, 1, 3, 12, 10, 23, tzinfo=timezone(timedelta(seconds=7200))
        ),
        lines_insertions=572,
        lines_deletions=276,
        files_changed=3,
        message="feat(ui): search bar with debounced fetch",
    ),
    AnalyticsCommit(
        sha="44b3168d31a04e8d4823b36bc12aede6a6e367bd",
        commit_author="Alice",
        committed_datetime=datetime(
            2025, 1, 3, 11, 10, 42, tzinfo=timezone(timedelta(seconds=7200))
        ),
        lines_insertions=582,
        lines_deletions=89,
        files_changed=8,
        message="feat(ui): search bar with debounced fetch",
    ),
    AnalyticsCommit(
        sha="5e6059b5dd6cd31d64f0507a51eb83c8023f7b24",
        commit_author="Dave",
        committed_datetime=datetime(
            2025, 1, 3, 11, 0, 25, tzinfo=timezone(timedelta(seconds=7200))
        ),
        lines_insertions=214,
        lines_deletions=110,
        files_changed=6,
        message="ci: cache pip and node modules",
    ),
    AnalyticsCommit(
        sha="e077cbbcca44a0256e1ebc6b87df951aac9d3c58",
        commit_author="Dave",
        committed_datetime=datetime(
            2025, 1, 3, 10, 35, 51, tzinfo=timezone(timedelta(seconds=7200))
        ),
        lines_insertions=35,
        lines_deletions=6,
        files_changed=9,
        message="deploy: production rollout with canary",
    ),
    AnalyticsCommit(
        sha="1da5b3c170ef9185ad913bbb63a75d425886aae5",
        commit_author="Carol",
        committed_datetime=datetime(2025, 1, 3, 10, 0, 55, tzinfo=timezone.utc),
        lines_insertions=102,
        lines_deletions=273,
        files_changed=6,
        message="feat(api): payment webhook handler",
    ),
    AnalyticsCommit(
        sha="735cc9ed9d4126ae9bd321a2c5f9f1e4f1bb3318",
        commit_author="Oscar",
        committed_datetime=datetime(
            2025, 1, 3, 9, 10, 24, tzinfo=timezone(timedelta(days=-1, seconds=79200))
        ),
        lines_insertions=429,
        lines_deletions=140,
        files_changed=1,
        message="chore: update eslint+ruff config",
    ),
    AnalyticsCommit(
        sha="7a9769f17f83985c2ff833237796787a9a526dc0",
        commit_author="Oscar",
        committed_datetime=datetime(
            2025, 1, 3, 9, 0, 37, tzinfo=timezone(timedelta(days=-1, seconds=79200))
        ),
        lines_insertions=544,
        lines_deletions=276,
        files_changed=8,
        message="fix: timezone on order timestamps",
    ),
    AnalyticsCommit(
        sha="873b26b46f359f80690549ccdb5176c3e0803d38",
        commit_author="Dave",
        committed_datetime=datetime(
            2025, 1, 3, 8, 5, 59, tzinfo=timezone(timedelta(seconds=7200))
        ),
        lines_insertions=52,
        lines_deletions=52,
        files_changed=4,
        message="ci: cache pip and node modules",
    ),
    AnalyticsCommit(
        sha="b588a4af8b4b6637b8f43b732c48c789399d37c5",
        commit_author="Alice",
        committed_datetime=datetime(
            2025, 1, 2, 20, 30, 21, tzinfo=timezone(timedelta(seconds=7200))
        ),
        lines_insertions=179,
        lines_deletions=115,
        files_changed=5,
        message="style(ui): tweak spacing and typography",
    ),
    AnalyticsCommit(
        sha="8a3df08b0aaee274e1213e0bf22e44da89a5c4f4",
        commit_author="Dave",
        committed_datetime=datetime(
            2025, 1, 2, 20, 25, 14, tzinfo=timezone(timedelta(seconds=7200))
        ),
        lines_insertions=140,
        lines_deletions=63,
        files_changed=3,
        message="ci: add GitHub Actions for test/lint",
    ),
    AnalyticsCommit(
        sha="0805edf49339101d0ca74e7853e4a7ecdd4604ae",
        commit_author="Dave",
        committed_datetime=datetime(
            2025, 1, 2, 20, 20, 4, tzinfo=timezone(timedelta(seconds=7200))
        ),
        lines_insertions=243,
        lines_deletions=120,
        files_changed=4,
        message="deploy: staging workflow with tags",
    ),
    AnalyticsCommit(
        sha="82f253bca7a9d128c991a26ceab12e4b86895a61",
        commit_author="Alice",
        committed_datetime=datetime(
            2025, 1, 2, 19, 55, 57, tzinfo=timezone(timedelta(seconds=7200))
        ),
        lines_insertions=109,
        lines_deletions=221,
        files_changed=9,
        message="feat(ui): product detail page with carousel",
    ),
    AnalyticsCommit(
        sha="ad80bfc487b0571b992d53f5fe0bf8e368839e77",
        commit_author="Oscar",
        committed_datetime=datetime(
            2025, 1, 2, 19, 55, 7, tzinfo=timezone(timedelta(days=-1, seconds=79200))
        ),
        lines_insertions=579,
        lines_deletions=389,
        files_changed=11,
        message="fix: CORS preflight cache mismatch",
    ),
    AnalyticsCommit(
        sha="644714208d3a43f4d10c3dd627d7cc25eb3813f4",
        commit_author="Carol",
        committed_datetime=datetime(2025, 1, 2, 18, 50, 10, tzinfo=timezone.utc),
        lines_insertions=280,
        lines_deletions=93,
        files_changed=9,
        message="chore(api): bump dependencies",
    ),
    AnalyticsCommit(
        sha="4c804a9d3b4d8737020654e28413543d7a74ed4c",
        commit_author="Bob",
        committed_datetime=datetime(
            2025, 1, 2, 17, 40, 7, tzinfo=timezone(timedelta(days=-1, seconds=79200))
        ),
        lines_insertions=461,
        lines_deletions=665,
        files_changed=34,
        message="refactor(core): unify error handling",
    ),
    AnalyticsCommit(
        sha="e5e02590613e96dfad16f84a61a74f986bf38ec8",
        commit_author="Oscar",
        committed_datetime=datetime(
            2025, 1, 2, 17, 10, 32, tzinfo=timezone(timedelta(days=-1, seconds=79200))
        ),
        lines_insertions=138,
        lines_deletions=325,
        files_changed=15,
        message="fix: timezone on order timestamps",
    ),
    AnalyticsCommit(
        sha="137ccb40b8fd51a9f03e27e71ccce8c939c7ec56",
        commit_author="Dave",
        committed_datetime=datetime(
            2025, 1, 2, 16, 10, 15, tzinfo=timezone(timedelta(seconds=7200))
        ),
        lines_insertions=147,
        lines_deletions=33,
        files_changed=9,
        message="ci: run E2E on PR",
    ),
    AnalyticsCommit(
        sha="7106b42fd076c99330fac29560e0ff576fbb8c52",
        commit_author="Dave",
        committed_datetime=datetime(
            2025, 1, 2, 15, 50, 20, tzinfo=timezone(timedelta(seconds=7200))
        ),
        lines_insertions=68,
        lines_deletions=105,
        files_changed=1,
        message="deploy: staging workflow with tags",
    ),
    AnalyticsCommit(
        sha="55c52904ec79ace536e409c556941919dfd217f8",
        commit_author="Oscar",
        committed_datetime=datetime(
            2025, 1, 2, 15, 45, 29, tzinfo=timezone(timedelta(days=-1, seconds=79200))
        ),
        lines_insertions=287,
        lines_deletions=288,
        files_changed=9,
        message="feat: add product filters (price, brand)",
    ),
    AnalyticsCommit(
        sha="d3751894ca1dc3eaba5d524dd7bf3d835e4c4a2a",
        commit_author="Bob",
        committed_datetime=datetime(
            2025, 1, 2, 15, 45, 12, tzinfo=timezone(timedelta(days=-1, seconds=79200))
        ),
        lines_insertions=442,
        lines_deletions=146,
        files_changed=55,
        message="feat(core): add DTO mappers",
    ),
    AnalyticsCommit(
        sha="d5155cf8f6dbca83cc639fded18913a6160ff355",
        commit_author="Alice",
        committed_datetime=datetime(
            2025, 1, 2, 15, 15, 28, tzinfo=timezone(timedelta(seconds=7200))
        ),
        lines_insertions=304,
        lines_deletions=8,
        files_changed=10,
        message="fix(ui): responsive navbar collapse issue",
    ),
    AnalyticsCommit(
        sha="3a20223eccc1c736821490443ab6f17c58cb7756",
        commit_author="Dave",
        committed_datetime=datetime(
            2025, 1, 2, 14, 50, 31, tzinfo=timezone(timedelta(seconds=7200))
        ),
        lines_insertions=236,
        lines_deletions=117,
        files_changed=7,
        message="infra: compose file for local stack",
    ),
    AnalyticsCommit(
        sha="87e6afe9d4a4280b316e822cf457b0971f439ae1",
        commit_author="Carol",
        committed_datetime=datetime(2025, 1, 2, 14, 25, 13, tzinfo=timezone.utc),
        lines_insertions=303,
        lines_deletions=369,
        files_changed=11,
        message="feat(api): JWT login and refresh",
    ),
    AnalyticsCommit(
        sha="bdd9f3e7bc45127ee3adab2584535c810252848a",
        commit_author="Alice",
        committed_datetime=datetime(
            2025, 1, 2, 12, 15, 32, tzinfo=timezone(timedelta(seconds=7200))
        ),
        lines_insertions=47,
        lines_deletions=292,
        files_changed=10,
        message="perf(ui): defer non-critical scripts",
    ),
    AnalyticsCommit(
        sha="68e1ca0487ab9b6362b433673ae2a5981f7b79c8",
        commit_author="Bob",
        committed_datetime=datetime(
            2025, 1, 2, 11, 15, 55, tzinfo=timezone(timedelta(days=-1, seconds=79200))
        ),
        lines_insertions=1078,
        lines_deletions=384,
        files_changed=16,
        message="refactor(core): flatten package structure",
    ),
    AnalyticsCommit(
        sha="46c775be37140f8be6a83c96a23ec73059c6fce8",
        commit_author="Dave",
        committed_datetime=datetime(
            2025, 1, 2, 11, 10, 40, tzinfo=timezone(timedelta(seconds=7200))
        ),
        lines_insertions=212,
        lines_deletions=87,
        files_changed=3,
        message="ci: docker build and multi-stage image",
    ),
    AnalyticsCommit(
        sha="f7b50ebdaeb91a276ae60e0c0ce52db8ed26f7df",
        commit_author="Oscar",
        committed_datetime=datetime(
            2025, 1, 2, 10, 20, 27, tzinfo=timezone(timedelta(days=-1, seconds=79200))
        ),
        lines_insertions=494,
        lines_deletions=6,
        files_changed=3,
        message="feat: order history page",
    ),
    AnalyticsCommit(
        sha="c75c45bbe80a8adbc0a279ab5bd0dcc3d7b7e9bd",
        commit_author="Alice",
        committed_datetime=datetime(
            2025, 1, 2, 10, 5, 24, tzinfo=timezone(timedelta(seconds=7200))
        ),
        lines_insertions=387,
        lines_deletions=181,
        files_changed=2,
        message="feat(ui): add product list with Bootstrap cards",
    ),
    AnalyticsCommit(
        sha="9a871bc4c0cad148886b6217e9152c3bdeb443e2",
        commit_author="Alice",
        committed_datetime=datetime(
            2025, 1, 2, 10, 0, 47, tzinfo=timezone(timedelta(seconds=7200))
        ),
        lines_insertions=270,
        lines_deletions=119,
        files_changed=5,
        message="feat(ui): product detail page with carousel",
    ),
]
