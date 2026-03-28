"""
Post-processing engine для обработки и обогащения данных аналитики.
"""

from typing import Dict, Any


def build_weekly_lines_history(result_data: Dict[str, Any]) -> Dict[str, Dict[str, int]]:
    """
    Строит историю количества строк кода по расширениям на конец каждой недели.

    Алгоритм:
    1. Берет текущее состояние из codebase.lines_by_extension (конец репозитория)
    2. Берет недельные изменения из activity.weekly_file_extensions
    3. Идет назад во времени, вычитая изменения каждой недели из предыдущего состояния
    4. Затем инвертирует результат, чтобы получить хронологический порядок

    Args:
        result_data: Словарь с данными аналитики, содержащий:
            - codebase.lines_by_extension: текущее количество строк по расширениям
            - activity.weekly_file_extensions: недельные изменения

    Returns:
        Dict[week_key, Dict[extension, lines]]: Количество строк на конец каждой недели

    Example:
        {
            "26W10": {".py": 1000, ".js": 500},
            "26W11": {".py": 1150, ".js": 480},
            "26W12": {".py": 1350, ".js": 580}
        }
    """
    # Извлекаем данные
    codebase = result_data.get("codebase")
    activity = result_data.get("activity", {})

    # Текущее состояние (на конец репозитория)
    # codebase может быть либо словарем, либо объектом RepositoryCompositionReport
    if codebase is None:
        current_lines = {}
    elif hasattr(codebase, "lines_by_extension"):
        # Это объект RepositoryCompositionReport
        current_lines = codebase.lines_by_extension.copy()
    else:
        # Это словарь
        current_lines = codebase.get("lines_by_extension", {})

    # Недельные изменения
    weekly_changes = activity.get("weekly_file_extensions", {})

    if not weekly_changes:
        # Если нет недельных данных, возвращаем только текущее состояние
        return {"current": current_lines.copy()}

    # Сортируем недели в обратном порядке (от последней к первой)
    sorted_weeks = sorted(weekly_changes.keys(), reverse=True)

    # Результирующий словарь: week_key -> {extension: lines}
    weekly_history: Dict[str, Dict[str, int]] = {}

    # Начинаем с текущего состояния
    current_state = current_lines.copy()

    # Идем от последней недели к первой
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
                # Если расширения нет, значит все строки были удалены
                # Устанавливаем в 0, так как не можем точно восстановить
                current_state[extension] = 0

    # Сортируем результат в хронологическом порядке
    result = dict(sorted(weekly_history.items()))

    return result


def enrich_result_data(result_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Обогащает данные аналитики дополнительными вычисляемыми метриками.

    Args:
        result_data: Исходные данные аналитики

    Returns:
        Обогащенные данные с дополнительными полями в activity.derived
    """
    result_data = result_data.copy()

    # Создаем секцию для производных данных, если её нет
    if "activity" not in result_data:
        result_data["activity"] = {}

    if "derived" not in result_data["activity"]:
        result_data["activity"]["derived"] = {}

    # Добавляем историю количества строк по неделям
    weekly_lines_history = build_weekly_lines_history(result_data)
    result_data["activity"]["derived"]["weekly_lines_history"] = weekly_lines_history

    return result_data
