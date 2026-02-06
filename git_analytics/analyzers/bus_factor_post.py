from typing import Any, Dict


def _bus_factor(contributions: Dict[str, int], threshold: float = 0.5) -> int:
    total = sum(contributions.values())
    acc = 0
    for _, lines in sorted(contributions.items(), key=lambda x: x[1], reverse=True):
        acc += lines
        if acc / total >= threshold:
            return len([a for a in contributions if contributions[a] >= lines])
    return 1


def bus_factor_post(data: Dict[str, Any]) -> int:
    author_lines = dict(data.get("authors_statistics", {})).get("authors")

    if author_lines:
        author_data = {}
        for author, item in author_lines.items():
            author_data[author] = item.get("insertions", 0) + item.get("deletions", 0)

        if len(author_data) < 2:
            return 1

        return _bus_factor(author_data)

    return 1
