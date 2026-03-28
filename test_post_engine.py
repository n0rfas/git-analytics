"""
Пример и тесты для post_engine
"""

from git_analytics.post_engine import build_weekly_lines_history, enrich_result_data


def test_build_weekly_lines_history():
    """Тест построения истории количества строк по неделям"""

    # Подготовка тестовых данных
    result_data = {
        "codebase": {
            "lines_by_extension": {
                ".py": 1000,
                ".js": 500,
                ".md": 100,
            }
        },
        "activity": {
            "weekly_file_extensions": {
                "26W10": {".py": 100, ".js": -20},  # неделя 10: +100 py, -20 js
                "26W11": {".py": 150, ".js": 50, ".md": 10},  # неделя 11: +150 py, +50 js, +10 md
                "26W12": {".py": 200, ".js": 50, ".md": 20},  # неделя 12: +200 py, +50 js, +20 md
            }
        },
    }

    # Вызываем функцию
    history = build_weekly_lines_history(result_data)

    print("История количества строк по неделям:")
    print("=" * 60)

    for week_key in sorted(history.keys()):
        print(f"\nНеделя {week_key}:")
        extensions = history[week_key]
        for ext, lines in sorted(extensions.items()):
            print(f"  {ext:15s}: {lines:6d} строк")

    # Проверяем логику:
    # На конец недели 12: .py = 1000 (текущее)
    # На конец недели 11: .py = 1000 - 200 = 800
    # На конец недели 10: .py = 800 - 150 = 650

    assert history["26W12"][".py"] == 1000
    assert history["26W11"][".py"] == 800
    assert history["26W10"][".py"] == 650

    assert history["26W12"][".js"] == 500
    assert history["26W11"][".js"] == 450
    assert history["26W10"][".js"] == 470

    assert history["26W12"][".md"] == 100
    assert history["26W11"][".md"] == 80

    print("\n✓ Все проверки прошли успешно!")


def test_enrich_result_data():
    """Тест обогащения данных"""

    result_data = {
        "codebase": {"lines_by_extension": {".py": 1000}},
        "activity": {
            "weekly_file_extensions": {
                "26W10": {".py": 100},
                "26W11": {".py": 200},
            }
        },
    }

    enriched = enrich_result_data(result_data)

    print("\nПроверка обогащения данных:")
    print("=" * 60)

    assert "derived" in enriched["activity"]
    assert "weekly_lines_history" in enriched["activity"]["derived"]

    history = enriched["activity"]["derived"]["weekly_lines_history"]
    assert "26W10" in history
    assert "26W11" in history

    print("✓ Данные успешно обогащены!")
    print(f"  Добавлена история для {len(history)} недель")


def example_usage():
    """Пример использования"""

    print("\n" + "=" * 70)
    print("ПРИМЕР ИСПОЛЬЗОВАНИЯ POST_ENGINE")
    print("=" * 70)

    # Имитируем данные, как они приходят из основного анализа
    result_data = {
        "codebase": {
            "files_by_extension": {".py": 50, ".js": 30, ".md": 5},
            "lines_by_extension": {".py": 5000, ".js": 3000, ".md": 500},
            "total_files": 85,
            "total_lines": 8500,
        },
        "activity": {
            "weekly_file_extensions": {
                "24W50": {".py": 500, ".js": 200},
                "24W51": {".py": 300, ".js": 150},
                "24W52": {".py": 400, ".js": -100},
                "25W01": {".py": 600, ".js": 300, ".md": 50},
                "25W02": {".py": 800, ".js": 400, ".md": 100},
            }
        },
    }

    print("\n1. Исходное состояние (текущее):")
    for ext, lines in result_data["codebase"]["lines_by_extension"].items():
        print(f"   {ext}: {lines} строк")

    print("\n2. Строим историю...")
    history = build_weekly_lines_history(result_data)

    print("\n3. Результат - количество строк на конец каждой недели:")
    for week_key in sorted(history.keys()):
        print(f"\n   Неделя {week_key}:")
        for ext in [".py", ".js", ".md"]:
            if ext in history[week_key]:
                lines = history[week_key][ext]
                print(f"      {ext:10s}: {lines:5d} строк")


if __name__ == "__main__":
    test_build_weekly_lines_history()
    test_enrich_result_data()
    example_usage()
