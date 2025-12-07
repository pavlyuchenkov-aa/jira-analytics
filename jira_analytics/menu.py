"""Модуль меню приложения"""
from jira_analytics.data_processor import DataProcessor
from jira_analytics.visualizer import JiraVisualizer


def display_menu(project_key: str, issue_count: int) -> None:
    """
    Отображение меню выбора аналитических отчетов

    Args:
        project_key: Ключ проекта
        issue_count: Количество загруженных задач
    """
    print("\n" + "=" * 60)
    print(f"JIRA Analytics для проекта: {project_key}")
    print(f"Загружено задач: {issue_count}")
    print("=" * 60)
    print("1. Гистограмма времени в открытом состоянии")
    print("2. Распределение времени по состояниям")
    print("3. График заведенных и закрытых задач")
    print("4. Топ пользователей")
    print("5. Гистограмма затраченного времени")
    print("6. Распределение по приоритетам")
    print("0. Выход")
    print("-" * 60)


class MenuHandler:
    """Обработчик меню"""

    def __init__(self, processor: DataProcessor, visualizer: JiraVisualizer):
        """
        Инициализация обработчика меню

        Args:
            processor: Процессор данных
            visualizer: Визуализатор
        """
        self.processor = processor
        self.visualizer = visualizer

    def handle_choice(self, choice: str) -> bool:
        """
        Обработка выбора пользователя

        Args:
            choice: Выбор пользователя

        Returns:
            True если нужно продолжить, False для выхода
        """
        if choice == '0':
            print("Выход из программы...")
            return False

        if choice == '1':
            times = self.processor.get_resolution_times(0, 3650)
            self.visualizer.plot_open_time_histogram(times)

        elif choice == '2':
            status_groups = self.processor.get_resolution_times_by_status(0, 3650)
            self.visualizer.plot_time_distribution_by_status(status_groups)

        elif choice == '3':
            created_dates, closed_dates = self.processor.get_created_closed_counts()
            self.visualizer.plot_created_vs_closed_timeline(
                created_dates, closed_dates, len(self.processor.issues)
            )

        elif choice == '4':
            user_stats = self.processor.get_user_stats()
            self.visualizer.plot_top_users(user_stats)

        elif choice == '5':
            times = self.processor.get_time_spent_data()
            self.visualizer.plot_time_spent_histogram(times)

        elif choice == '6':
            priority_stats = self.processor.get_priority_distribution()
            self.visualizer.plot_priority_distribution(priority_stats)

        else:
            print("Неверный выбор. Попробуйте снова.")

        return True