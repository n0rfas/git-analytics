"""
Weekly Lines History Insight - восстановление истории количества строк кода по неделям.
"""

from typing import Dict, Any


class WeeklyLinesHistory:
    """
    Строит историю количества строк кода по расширениям на конец каждой недели.

    Алгоритм:
    1. Берет текущее состояние из snapshot (конец репозитория)
    2. Берет недельные изменения из collection
    3. Идет назад во времени, вычитая изменения каждой недели
    4. Возвращает хронологически упорядоченную историю
    """

    def __init__(self, codebase, activity: Dict[str, Any]) -> None:
        """
        Args:
            codebase: CodebaseSnapshotReport с текущим состоянием репозитория
            activity: Dict с результатами коллекторов, включая weekly_file_extensions
        """
        self._codebase = codebase
        self._activity = activity

    def compute(self) -> Dict[str, Dict[str, int]]:
        """
        Вычисляет историю количества строк на конец каждой недели.

        Returns:
            Dict[week_key, Dict[extension, lines]]: Количество строк по неделям

        Example:
            {
                "26W10": {".py": 1000, ".js": 500},
                "26W11": {".py": 1150, ".js": 480},
                "26W12": {".py": 1350, ".js": 580}
            }
        """
        # Получаем текущее состояние (на конец репозитория)
        if hasattr(self._codebase, "lines_by_extension"):
            current_lines = self._codebase.lines_by_extension.copy()
        else:
            current_lines = self._codebase.get("lines_by_extension", {})

        # Получаем недельные изменения
        weekly_changes = self._activity.get("weekly_file_extensions", {})

        if not weekly_changes:
            # Если нет недельных данных, возвращаем только текущее состояние
            return {"current": current_lines.copy()}

        # Сортируем недели в обратном порядке (от последней к первой)
        sorted_weeks = sorted(weekly_changes.keys(), reverse=True)

        # Результирующий словарь: week_key -> {extension: lines}
        weekly_history: Dict[str, Dict[str, int]] = {}

        # Начинаем с текущего состояния
        current_state = current_lines.copy()

        # Идем от последней недели к первой, восстанавливая историю
        for week_key in sorted_weeks:
            # Сохраняем состояние на конец этой недели
            weekly_history[week_key] = current_state.copy()

            # Получаем изменения за эту неделю
            week_changes = weekly_changes[week_key]

            # Вычитаем изменения, чтобы получить состояние на начало недели
            # (которое равно состоянию на конец предыдущей недели)
            for extension, net_change in week_changes.items():
                if extension in current_state:
                    current_state[extension] -= net_change
                    # Не допускаем отрицательных значений
                    if current_state[extension] < 0:
                        current_state[extension] = 0
                else:
                    # Если расширения нет в текущем состоянии,
                    # значит все строки были удалены позже
                    current_state[extension] = 0

        # Сортируем результат в хронологическом порядке
        return dict(sorted(weekly_history.items()))
