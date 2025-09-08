from __future__ import annotations

import re
from datetime import datetime
from typing import Iterable, Iterator

from git_analytics.entities import AnalyticsCommit
from git_analytics.interfaces import CommitSource

# commit header lines
_RE_COMMIT = re.compile(r"^commit\s+(?P<sha>[0-9a-f]{7,40})\s*$", re.I)
_RE_AUTHOR = re.compile(
    r"^Author:\s*(?P<name>[^<]+?)(?:\s*<(?P<email>[^>]+)>)?\s*$",
    re.I,
)
_RE_DATE = re.compile(r"^Date:\s*(?P<dt>.+?)\s*$", re.I)
# numstat: "<insertions>\t<deletions>\t<path>"
_RE_NUMSTAT = re.compile(r"^\s*(?P<ins>-|\d+)\s+(?P<del>-|\d+)\s+(?P<path>.+)$")
# optional merge line we just skip
_RE_MERGE = re.compile(r"^Merge:\s+", re.I)


class GitLogSource(CommitSource):
    def __init__(self, text: str) -> None:
        self._text = text

    def iter_commits(self) -> Iterator[AnalyticsCommit]:
        yield from self.yield_commits(self._text.splitlines())

    @staticmethod
    def yield_commits(lines: Iterable[str]) -> Iterator[AnalyticsCommit]:
        sha: str | None = None
        author_name: str | None = None
        dt: datetime | None = None

        subject: str | None = None
        in_headers = False
        in_message = False

        ins_total = 0
        del_total = 0
        files_changed = 0

        def flush():
            nonlocal sha, author_name, dt, subject, in_headers, in_message
            nonlocal ins_total, del_total, files_changed
            if not sha:
                return
            committed_dt = dt if dt is not None else datetime.fromtimestamp(0)
            yield AnalyticsCommit(
                sha=sha,
                commit_author=author_name or "Unknown",
                committed_datetime=committed_dt,
                lines_insertions=ins_total,
                lines_deletions=del_total,
                files_changed=files_changed,
                message=subject or "",
            )
            sha = None
            author_name = None
            dt = None
            subject = None
            in_headers = False
            in_message = False
            ins_total = 0
            del_total = 0
            files_changed = 0

        for raw in lines:
            line = raw.rstrip("\n")

            m_commit = _RE_COMMIT.match(line)
            if m_commit:
                yield from flush()
                sha = m_commit.group("sha")
                in_headers = True
                in_message = False
                continue

            if sha and in_headers:
                if _RE_MERGE.match(line):
                    continue

                m_author = _RE_AUTHOR.match(line)
                if m_author:
                    author_name = m_author.group("name").strip()
                    continue

                m_date = _RE_DATE.match(line)
                if m_date:
                    dt_str = m_date.group("dt").strip()
                    dt = datetime.fromisoformat(dt_str)
                    continue

                if line.strip() == "":
                    in_headers = False
                    in_message = True
                    continue

            if sha and in_message:
                if line.strip():
                    if _RE_NUMSTAT.match(line):
                        in_message = False
                    else:
                        subject = line.strip()
                        continue
                else:
                    continue

            if sha:
                m_ns = _RE_NUMSTAT.match(line)
                if m_ns:
                    ins_s, del_s = m_ns.group("ins"), m_ns.group("del")
                    ins = int(ins_s) if ins_s.isdigit() else 0
                    dels = int(del_s) if del_s.isdigit() else 0
                    ins_total += ins
                    del_total += dels
                    files_changed += 1
                    in_message = False
                    continue

        yield from flush()
