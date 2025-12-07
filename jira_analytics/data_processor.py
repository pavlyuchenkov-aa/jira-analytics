"""Модуль для обработки данных JIRA"""
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, DefaultDict, Any
from jira_analytics.jira_client import calculate_resolution_days


class DataProcessor:
    """Класс для обработки данных JIRA"""

    def __init__(self, issues: List[Dict[str, Any]]):
        """
        Инициализация процессора данных

        Args:
            issues: Список задач JIRA
        """
        self.issues = issues

    def get_resolution_times(self, min_days: int = 0, max_days: int = 3650) -> List[int]:
        """
        Получить список времен разрешения задач

        Args:
            min_days: Минимальное количество дней (включительно)
            max_days: Максимальное количество дней (включительно)

        Returns:
            Список времен в днях
        """
        times = []
        for issue in self.issues:
            if issue['fields'].get('resolutiondate'):
                days = calculate_resolution_days(
                    issue['fields']['created'],
                    issue['fields']['resolutiondate']
                )
                if min_days <= days <= max_days:
                    times.append(days)
        return times

    def get_resolution_times_by_status(self, min_days: int = 0, max_days: int = 3650) -> Dict[str, List[int]]:
        """
        Получить времена разрешения сгруппированные по статусам

        Args:
            min_days: Минимальное количество дней
            max_days: Максимальное количество дней

        Returns:
            Словарь {статус: [времена в днях]}
        """
        status_groups = defaultdict(list)
        for issue in self.issues:
            status = issue['fields']['status']['name']
            if issue['fields'].get('resolutiondate'):
                days = calculate_resolution_days(
                    issue['fields']['created'],
                    issue['fields']['resolutiondate']
                )
                if min_days <= days <= max_days:
                    status_groups[status].append(days)
        return dict(status_groups)

    def get_created_closed_counts(self) -> Tuple[DefaultDict[datetime.date, int], DefaultDict[datetime.date, int]]:
        """
        Получить количество созданных и закрытых задач по датам

        Returns:
            Кортеж (created_dates, closed_dates)
        """
        created_dates = defaultdict(int)
        closed_dates = defaultdict(int)

        for issue in self.issues:
            try:
                created_date = datetime.strptime(
                    issue['fields']['created'].split('.')[0],
                    '%Y-%m-%dT%H:%M:%S'
                ).date()
                created_dates[created_date] += 1

                if issue['fields'].get('resolutiondate'):
                    closed_date = datetime.strptime(
                        issue['fields']['resolutiondate'].split('.')[0],
                        '%Y-%m-%dT%H:%M:%S'
                    ).date()
                    closed_dates[closed_date] += 1
            except (ValueError, KeyError, TypeError):
                continue

        return created_dates, closed_dates

    def get_user_stats(self) -> Dict[str, int]:
        """
        Получить статистику по пользователям

        Returns:
            Словарь {имя пользователя: количество задач}
        """
        user_counts = defaultdict(int)
        for issue in self.issues:
            if issue['fields'].get('assignee'):
                user_counts[issue['fields']['assignee'].get('displayName', 'Unknown')] += 1
            if issue['fields'].get('reporter'):
                user_counts[issue['fields']['reporter'].get('displayName', 'Unknown')] += 1
        return dict(user_counts)

    def get_time_spent_data(self) -> List[float]:
        """
        Получить данные о затраченном времени

        Returns:
            Список затраченного времени в днях
        """
        times = []
        for issue in self.issues:
            if issue['fields'].get('timespent'):
                days = issue['fields']['timespent'] / 86400
                if 0 < days <= 3650:
                    times.append(days)
            elif issue['fields'].get('resolutiondate'):
                days = calculate_resolution_days(
                    issue['fields']['created'],
                    issue['fields']['resolutiondate']
                )
                if 0 < days <= 3650:
                    times.append(days)
        return times

    def get_priority_distribution(self) -> Dict[str, int]:
        """
        Получить распределение задач по приоритетам

        Returns:
            Словарь {приоритет: количество}
        """
        priorities = []
        for issue in self.issues:
            priority = issue["fields"].get("priority")
            if priority:
                priorities.append(priority.get("name", "Без приоритета"))
            else:
                priorities.append("Без приоритета")

        return dict(Counter(priorities))