from typing import Dict, Any


class BusFactorMetric:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data["authors_statistics"]

    def compute(self, threshold: float = 0.5) -> Dict[str, Any]:
        authors_stats = {}
        for author, item in self.data.items():
            authors_stats[author] = item.get("insertions", 0) + item.get("deletions", 0)

        total = sum(authors_stats.values())
        acc = 0
        for _, lines in sorted(authors_stats.items(), key=lambda x: x[1], reverse=True):
            acc += lines
            if acc / total >= threshold:
                critical_authors = [a for a in authors_stats if authors_stats[a] >= lines]
                return {
                    "bus_factor": len(critical_authors),
                    "authors": sorted(critical_authors, key=lambda a: authors_stats[a], reverse=True),
                }
