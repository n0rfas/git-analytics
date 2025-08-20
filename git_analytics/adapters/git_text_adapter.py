from __future__ import annotations

import re
from datetime import datetime
from typing import Iterable, Iterator

from git_analytics.entities import AnalyticsCommit

# headers
_RE_COMMIT = re.compile(r"^commit\s+(?P<sha>[0-9a-f]{7,40})\s*$", re.I)
_RE_AUTHOR = re.compile(r"^Author:\s*(?P<name>.+?)\s*<(?P<email>[^>]+)>\s*$", re.I)
_RE_DATE = re.compile(r"^Date:\s*(?P<dt>.+?)\s*$", re.I)
# numstat lines: "<insertions>\t<deletions>\t<path>"
_RE_NUMSTAT = re.compile(r"^\s*(?P<ins>-|\d+)\s+(?P<del>-|\d+)\s+(?P<path>.+)$")


def _parse_dt_iso(s: str) -> datetime:
    # Example: 2025-08-16T16:35:39+02:00 — works fine with fromisoformat
    return datetime.fromisoformat(s.strip())


def _yield_commits(lines: Iterable[str]) -> Iterator[AnalyticsCommit]:
    sha: str | None = None
    author: str | None = None
    dt: datetime | None = None

    # collect only the first non-empty message line (subject)
    subject: str | None = None
    in_message_block = False
    headers_done = False

    ins_total = 0
    del_total = 0
    files_changed = 0

    def flush():
        nonlocal sha, author, dt, subject, in_message_block, headers_done
        nonlocal ins_total, del_total, files_changed
        if not sha:
            return
        yield AnalyticsCommit(
            sha=sha,
            commit_author=author or "Unknown",
            committed_datetime=dt or _parse_dt_iso("1970-01-01T00:00:00+00:00"),
            lines_insertions=ins_total,
            lines_deletions=del_total,
            files_changed=files_changed,
            message=subject or "",
        )
        # reset state for the next commit
        sha = author = subject = None
        dt = None
        in_message_block = False
        headers_done = False
        ins_total = del_total = files_changed = 0

    for raw in lines:
        line = raw.rstrip("\n")

        # start of a new commit
        m = _RE_COMMIT.match(line)
        if m:
            # flush the previous commit block
            yield from flush()
            sha = m.group("sha")
            continue

        if sha and not headers_done:
            ma = _RE_AUTHOR.match(line)
            if ma:
                # you only have one commit_author field: join "Name <email>"
                name = ma.group("name").strip()
                email = ma.group("email").strip()
                author = f"{name} <{email}>"
                continue

            md = _RE_DATE.match(line)
            if md:
                dt = _parse_dt_iso(md.group("dt"))
                continue

            if line.strip() == "":
                # empty line separates headers from commit message
                headers_done = True
                in_message_block = True
                continue

        if sha and in_message_block:
            # take the first non-empty line as subject
            if line.strip():
                # if it's already a numstat line — then there's no message
                mn = _RE_NUMSTAT.match(line)
                if mn:
                    in_message_block = False
                    # don't continue — let it be processed as numstat below
                else:
                    subject = line.strip()
                    # later lines may be body text — skip until first numstat
                    continue
            else:
                # ignore empty lines in the body
                continue

        if sha:
            # numstat (may appear right after headers or after subject)
            mn = _RE_NUMSTAT.match(line)
            if mn:
                ins_s, del_s = mn.group("ins"), mn.group("del")
                ins = int(ins_s) if ins_s.isdigit() else 0  # '-' для бинарников
                dels = int(del_s) if del_s.isdigit() else 0
                ins_total += ins
                del_total += dels
                files_changed += 1
                continue

    # flush the last commit
    yield from flush()


def text_commits_to_analytics_commits(path_to_file: str) -> list[AnalyticsCommit]:
    with open(path_to_file, "r", encoding="utf-8") as f:
        return list(_yield_commits(f))
