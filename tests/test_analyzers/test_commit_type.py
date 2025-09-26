
import pytest

from git_analytics.analyzers.commit_type import CommitTypeAnalyzer, _get_type_list
from tests.fakes import FAKE_COMMITS, FakeCommitSource


@pytest.mark.parametrize(
    "commit_message, expected_types",
    [
        ("[JIRA-101] feature: implement checkout page", ["feature"]),
        ("fix: handle null user session | ABC-77", ["fix"]),
        ("#452 docs: update README install section", ["docs"]),
        ("style: reformat css grid | #98", ["style"]),
        ("refactor: split cart service into modules | PROJ-204", ["refactor"]),
        ("test: add unit tests for price calculator #311", ["test"]),
        ("chore: bump dependencies to new version | LIB-55", ["chore"]),
        ("wip: async payment flow proof-of-concept | #1200", ["wip"]),
        ("merge: branch 'dev' into 'main' | MERGE-15", ["merge"]),
        ("unknown: tweak timeout value | OPS-33", ["unknown"]),
        ("FEATURE: add order history page | #909", ["feature"]),
        ("[TKT-44] FIX: timezone bug in reports", ["fix"]),
        ("DOCS: add API usage examples #700", ["docs"]),
        ("STYLE: lint fixes and import sort | LINT-3", ["fix", "style"]),
        ("REFACTOR: extract email sender interface | CORE-20", ["refactor"]),
        ("[QA-12] TEST: integration tests for webhook", ["test"]),
        ("CHORE: rotate staging secrets | #845", ["chore"]),
        ("WIP: redesign header navigation | UI-61", ["wip"]),
        ("[REL-2] MERGE: prepare release branch", ["merge"]),
        ("UNKNOWN: quick experiment with caching | #321", ["unknown"]),
        ("PROJ-888: feature add dark mode toggle", ["feature"]),
        ("fix race condition in job runner | TASK-61", ["fix"]),
        ("docs add contribution guide | #12", ["docs"]),
        ("style align buttons on mobile | APP-5", ["style"]),
        ("refactor | simplify auth middleware #670", ["refactor"]),
        ("test | snapshot tests for components | FE-42", ["test"]),
        ("chore cleanup old flags #400", ["chore"]),
        ("wip migrate to postgres 16 | DB-160", ["wip"]),
        ("merge revert accidental changes | #2004", ["merge"]),
        ("unknown minor tweak in env loader | ENV-7", ["unknown"]),
        ("#1500 | feature: SSO login via OAuth", ["feature"]),
        ("ABC-321 | fix: N+1 query in orders", ["fix"]),
        ("#77 | docs: ADR for architecture decisions", ["docs"]),
        ("XYZ-19 | style: apply prettier defaults", ["style"]),
        ("#901 | refactor: extract price rules engine", ["refactor"]),
        ("PAY-24 | test: contract tests for provider", ["test"]),
        ("#66 | chore: update Makefile targets", ["chore"]),
        ("OPS-88 | wip: k8s manifests for staging", ["wip"]),
        ("#555 | merge: sync fork with upstream", ["merge"]),
        ("CI-11 | unknown: temp debug logs", ["unknown"]),
        ("feature: add CSV export | REPORTS-14", ["feature"]),
        ("[BUG-909] fix: off-by-one in pagination", ["fix"]),
        ("docs: add FAQ section | #740", ["docs"]),
        ("style: remove dead scss variables #213", ["style"]),
        ("refactor: replace globals with DI | ARCH-3", ["refactor"]),
        ("test: e2e checkout happy path | #1010", ["test"]),
        ("chore: rename default branch to main | REPO-1", ["chore"]),
        ("wip: multi-tenant groundwork | #602", ["wip"]),
        ("merge hotfix into release/0.2.0 | REL-020", ["fix", "merge"]),
        ("add small perf tweak | PERF-9 | unknown", ["unknown"]),
        ("#120 test, docs: update API spec and add unit tests", ["docs", "test"]),
        ("fix + refactor: cleanup auth flow and resolve session bug | AUTH-45", ["fix", "refactor"]),
        ("docs & style: polish README and fix markdown formatting | #77", ["fix", "docs", "style"]),
        ("[UI-22] test/refactor: split components and adjust snapshots", ["refactor", "test"]),
        ("feature, docs: implement new search and update user guide | #908", ["feature", "docs"]),
        ("refactor + chore: restructure configs and remove legacy flags | OPS-12", ["refactor", "chore"]),
        ("test & fix: cover edge cases and resolve race condition | #311", ["fix", "test"]),
        ("docs/refactor: move ADRs into separate folder | ARCH-33", ["docs", "refactor"]),
        ("fix, style: adjust lint rules and resolve formatting bugs | LINT-55", ["fix", "style"]),
        ("wip + test: draft for analytics module with early unit tests | #700", ["test", "wip"]),
    ],
)
def test_commit_type_get_type_list(commit_message, expected_types):
    assert _get_type_list(commit_message) == expected_types


def test_commit_type_commit_type_by_week():
    source = FakeCommitSource(FAKE_COMMITS)

    analyzer = CommitTypeAnalyzer()
    for commit in source.iter_commits():
        analyzer.process(commit)
    result = analyzer.result()

    assert result.commit_type_by_week["2024-W01"] == {"unknown": 4}
    assert result.commit_type_by_week["2024-W36"] == {"fix": 1, "refactor": 1, "unknown": 4}
    assert result.commit_type_by_week["2025-W01"] == {"unknown": 3}
    assert result.commit_type_by_week["2025-W05"] == {"chore": 1, "fix": 1, "refactor": 1}
    assert result.commit_type_by_week["2025-W14"] == {"fix": 1, "unknown": 2}
    assert result.commit_type_by_week["2025-W18"] == {"style": 1, "test": 1, "unknown": 1}
    assert result.commit_type_by_week["2025-W22"] == {"fix": 1}
    assert result.commit_type_by_week["2025-W23"] == {"chore": 1, "unknown": 4}
    assert result.commit_type_by_week["2025-W25"] == {"chore": 1, "fix": 1, "test": 1, "unknown": 3}
    assert result.commit_type_by_week["2025-W26"] == {"refactor": 2, "style": 1, "unknown": 2}
    assert result.commit_type_by_week["2025-W27"] == {"refactor": 1}


def test_commit_type_total_counter():
    source = FakeCommitSource(FAKE_COMMITS)

    analyzer = CommitTypeAnalyzer()
    for commit in source.iter_commits():
        analyzer.process(commit)
    result = analyzer.result()

    assert result.commit_type_counter == {"unknown": 23, "refactor": 5, "fix": 5, "chore": 3, "style": 2, "test": 2}


def test_commit_type_author_total_counter():
    source = FakeCommitSource(FAKE_COMMITS)

    analyzer = CommitTypeAnalyzer()
    for commit in source.iter_commits():
        analyzer.process(commit)
    result = analyzer.result()

    assert result.author_commit_type_counter["Alice"] == {"chore": 1, "fix": 1, "style": 2, "unknown": 7}
    assert result.author_commit_type_counter["Bob"] == {"refactor": 5, "unknown": 1}
    assert result.author_commit_type_counter["Carol"] == {"chore": 1, "unknown": 3}
    assert result.author_commit_type_counter["Dave"] == {"test": 2, "unknown": 9}
    assert result.author_commit_type_counter["Oscar"] == {"chore": 1, "fix": 4, "unknown": 3}
