from typing import Any, Dict


class WeeklyLinesHistory:
    def __init__(self, codebase, activity: Dict[str, Any]) -> None:
        self._codebase = codebase
        self._activity = activity

    def compute(self) -> Dict[str, Dict[str, int]]:
        if hasattr(self._codebase, "lines_by_extension"):
            current_lines = self._codebase.lines_by_extension.copy()
        else:
            current_lines = self._codebase.get("lines_by_extension", {})

        weekly_changes = self._activity.get("weekly_file_extensions", {})

        if not weekly_changes:
            return {"current": current_lines.copy()}

        sorted_weeks = sorted(weekly_changes.keys(), reverse=True)

        weekly_history: Dict[str, Dict[str, int]] = {}

        current_state = current_lines.copy()

        for week_key in sorted_weeks:
            weekly_history[week_key] = current_state.copy()

            week_changes = weekly_changes[week_key]

            for extension, net_change in week_changes.items():
                if extension in current_state:
                    current_state[extension] -= net_change
                    if current_state[extension] < 0:
                        current_state[extension] = 0
                else:
                    current_state[extension] = 0

        return dict(sorted(weekly_history.items()))
