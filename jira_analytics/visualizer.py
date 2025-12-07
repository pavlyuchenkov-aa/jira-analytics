"""Модуль для визуализации данных"""
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, DefaultDict
from jira_analytics.exceptions import VisualizationError


class JiraVisualizer:
    """Класс для визуализации данных JIRA"""

    def __init__(self, project_key: str):
        """
        Инициализация визуализатора

        Args:
            project_key: Ключ проекта
        """
        self.project_key = project_key
        self.set_style()

    def set_style(self):
        """Настройка стиля графиков"""
        plt.style.use('seaborn-v0_8-whitegrid')

    def plot_open_time_histogram(self, times: List[int]) -> None:
        """
        Гистограмма времени в открытом состоянии

        Args:
            times: Список времен в днях
        """
        try:
            plt.figure(figsize=(10, 6))
            if times:
                plt.hist(times, bins=15, edgecolor='black', alpha=0.7, color='#2E86AB')
                plt.xlabel('Дни в открытом состоянии')
                plt.ylabel('Количество задач')
                plt.title(f'{self.project_key}: Гистограмма времени в открытом состоянии')
                plt.grid(True, alpha=0.3)
            else:
                plt.text(0.5, 0.5, 'Нет данных для построения графика',
                         ha='center', va='center', transform=plt.gca().transAxes)
                plt.title(f'{self.project_key}: Нет данных')

            plt.tight_layout()
            plt.show()

        except Exception as e:
            raise VisualizationError(f"Ошибка при построении гистограммы времени: {e}")

    def plot_time_distribution_by_status(self, status_groups: Dict[str, List[int]]) -> None:
        """
        Распределение времени по состояниям

        Args:
            status_groups: Словарь {статус: [времена в днях]}
        """
        try:
            if not status_groups:
                plt.figure(figsize=(10, 5))
                plt.text(0.5, 0.5, 'Нет данных для построения графика',
                         ha='center', va='center', transform=plt.gca().transAxes)
                plt.title(f'{self.project_key}: Распределение времени по состояниям')
                plt.show()
                return

            colors = ['#3498db', '#27ae60', '#f39c12', '#9b59b6', '#e74c3c']
            for i, (status, times) in enumerate(list(status_groups.items())[:5]):
                plt.figure(figsize=(10, 5))
                plt.hist(times, bins=10, alpha=0.7, color=colors[i], edgecolor='black')
                plt.xlabel(f'Дни в состоянии {status}')
                plt.ylabel('Количество задач')
                plt.title(f'{self.project_key}: Распределение времени в состоянии {status}')
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.show()

        except Exception as e:
            raise VisualizationError(f"Ошибка при построении распределения по статусам: {e}")

    def plot_created_vs_closed_timeline(self,
                                        created_dates: DefaultDict[datetime.date, int],
                                        closed_dates: DefaultDict[datetime.date, int],
                                        issues_count: int) -> None:
        """
        График заведенных и закрытых задач

        Args:
            created_dates: Количество созданных задач по датам
            closed_dates: Количество закрытых задач по датам
            issues_count: Общее количество задач
        """
        try:
            if not created_dates and not closed_dates:
                plt.figure(figsize=(12, 6))
                plt.text(0.5, 0.5, 'Нет данных для построения графика',
                         ha='center', va='center', transform=plt.gca().transAxes)
                plt.title(f'{self.project_key}: График заведенных и закрытых задач')
                plt.show()
                return

            dates = sorted(set(created_dates.keys()) | set(closed_dates.keys()))
            created_counts = [created_dates.get(date, 0) for date in dates]
            closed_counts = [closed_dates.get(date, 0) for date in dates]

            num_days = len(dates)
            plt.figure(figsize=(14, 8))

            if num_days > 365:
                print(f"Большой объем данных ({num_days} дней). Используется агрегация по месяцам.")
                month_created = defaultdict(int)
                month_closed = defaultdict(int)

                for date, count in created_dates.items():
                    month_key = date.replace(day=1)
                    month_created[month_key] += count

                for date, count in closed_dates.items():
                    month_key = date.replace(day=1)
                    month_closed[month_key] += count

                months = sorted(set(month_created.keys()) | set(month_closed.keys()))
                month_created_counts = [month_created.get(month, 0) for month in months]
                month_closed_counts = [month_closed.get(month, 0) for month in months]

                width = 0.35
                x = range(len(months))

                plt.bar([i - width / 2 for i in x], month_created_counts, width=width,
                        label='Создано', color='#3498db', alpha=0.8)
                plt.bar([i + width / 2 for i in x], month_closed_counts, width=width,
                        label='Закрыто', color='#2ecc71', alpha=0.8)

                plt.xlabel('Месяц')
                plt.ylabel('Количество задач')
                month_labels = [month.strftime('%b %Y') for month in months]

                if len(months) > 12:
                    step = max(1, len(months) // 12)
                    plt.xticks([i for i in x if i % step == 0],
                               [month_labels[i] for i in range(len(month_labels)) if i % step == 0],
                               rotation=45, ha='right')
                else:
                    plt.xticks(x, month_labels, rotation=45, ha='right')

            elif num_days > 90:
                print(f"Достаточно данных ({num_days} дней). Используется скользящее среднее.")
                window_size = 7
                created_smooth = []
                closed_smooth = []

                for i in range(len(created_counts)):
                    start = max(0, i - window_size // 2)
                    end = min(len(created_counts), i + window_size // 2 + 1)
                    created_smooth.append(sum(created_counts[start:end]) / (end - start))
                    closed_smooth.append(sum(closed_counts[start:end]) / (end - start))

                plt.plot(dates, created_smooth, label='Создано (сглаженное)',
                         color='#3498db', linewidth=2.5, alpha=0.9)
                plt.plot(dates, closed_smooth, label='Закрыто (сглаженное)',
                         color='#2ecc71', linewidth=2.5, alpha=0.9)

                plt.fill_between(dates, created_smooth, alpha=0.3, color='#3498db')
                plt.fill_between(dates, closed_smooth, alpha=0.3, color='#2ecc71')

                plt.xlabel('Дата')
                plt.ylabel('Количество задач (скользящее среднее, 7 дней)')
                plt.gca().xaxis.set_major_locator(plt.MaxNLocator(10))
                plt.xticks(rotation=45, ha='right')

            else:
                plt.plot(dates, created_counts, label='Создано',
                         color='#3498db', linewidth=2, marker='o', markersize=4)
                plt.plot(dates, closed_counts, label='Закрыто',
                         color='#2ecc71', linewidth=2, marker='s', markersize=4)

                plt.xlabel('Дата')
                plt.ylabel('Количество задач')
                plt.xticks(rotation=45, ha='right')

            plt.title(
                f'{self.project_key}: График заведенных и закрытых задач\nВсего дней: {num_days}, Всего задач: {issues_count}',
                fontsize=14, fontweight='bold', pad=20)
            plt.legend(loc='upper left', fontsize=11, framealpha=0.9)
            plt.grid(True, alpha=0.3, linestyle='--')

            total_created = sum(created_counts)
            total_closed = sum(closed_counts)

            stats_x = 0.02
            stats_y = 0.95
            plt.text(stats_x, stats_y,
                     f'Всего создано: {total_created}\nВсего закрыто: {total_closed}\nБаланс: {total_created - total_closed}',
                     transform=plt.gca().transAxes,
                     bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                     verticalalignment='top',
                     fontsize=10)

            plt.tight_layout()
            plt.axhline(y=0, color='gray', linestyle='-', alpha=0.3, linewidth=0.5)
            plt.show()

        except Exception as e:
            raise VisualizationError(f"Ошибка при построении временной шкалы: {e}")

    def plot_top_users(self, user_stats: Dict[str, int]) -> None:
        """
        Топ пользователей по количеству задач

        Args:
            user_stats: Статистика по пользователям
        """
        try:
            top_users = sorted(user_stats.items(), key=lambda x: x[1], reverse=True)[:30]

            if not top_users:
                plt.figure(figsize=(10, 6))
                plt.text(0.5, 0.5, 'Нет данных о пользователях',
                         ha='center', va='center', transform=plt.gca().transAxes)
                plt.title(f'{self.project_key}: Топ пользователей')
                plt.show()
                return

            users, counts = zip(*top_users)

            plt.figure(figsize=(10, 6))
            plt.barh(users, counts, color='#2E86AB', alpha=0.7)
            plt.xlabel('Количество задач')
            plt.ylabel('Пользователи')
            plt.title(f'{self.project_key}: Топ пользователей по количеству задач')
            plt.gca().invert_yaxis()
            plt.grid(True, alpha=0.3, axis='x')
            plt.tight_layout()
            plt.show()

        except Exception as e:
            raise VisualizationError(f"Ошибка при построении топа пользователей: {e}")

    def plot_time_spent_histogram(self, times: List[float]) -> None:
        """
        Гистограмма затраченного времени

        Args:
            times: Список затраченного времени в днях
        """
        try:
            plt.figure(figsize=(10, 6))
            if times:
                plt.hist(times, bins=15, edgecolor='black', alpha=0.7, color='#A23B72')
                plt.xlabel('Затраченное время (дни)')
                plt.ylabel('Количество задач')
                plt.title(f'{self.project_key}: Гистограмма затраченного времени')
                plt.grid(True, alpha=0.3)
            else:
                plt.text(0.5, 0.5, 'Нет данных о затраченном времени',
                         ha='center', va='center', transform=plt.gca().transAxes)
                plt.title(f'{self.project_key}: Гистограмма затраченного времени')

            plt.tight_layout()
            plt.show()

        except Exception as e:
            raise VisualizationError(f"Ошибка при построении гистограммы затраченного времени: {e}")

    def plot_priority_distribution(self, priority_stats: Dict[str, int]) -> None:
        """
        Распределение задач по приоритетам

        Args:
            priority_stats: Распределение по приоритетам
        """
        try:
            if not priority_stats:
                print("Нет данных о приоритетах")
                return

            sorted_priorities = sorted(priority_stats.items(), key=lambda x: x[1], reverse=True)
            labels, counts = zip(*sorted_priorities)

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

            colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
            wedges, texts, autotexts = ax1.pie(counts, labels=labels, autopct='%1.1f%%',
                                               colors=colors, startangle=90)

            for autotext in autotexts:
                autotext.set_color('black')
                autotext.set_fontweight('bold')

            ax1.set_title(f'Распределение по приоритетам\nПроект: {self.project_key}',
                          fontsize=14, fontweight='bold')

            bars = ax2.bar(labels, counts, alpha=0.7, color='purple')
            ax2.set_title(f'Количество задач по приоритетам\nПроект: {self.project_key}',
                          fontsize=14, fontweight='bold')
            ax2.set_xlabel('Приоритет', fontsize=12)
            ax2.set_ylabel('Количество задач', fontsize=12)
            ax2.tick_params(axis='x', rotation=45)
            ax2.grid(True, alpha=0.3, axis='y')

            for bar, count in zip(bars, counts):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width() / 2., height,
                         f'{count}', ha='center', va='bottom', fontweight='bold')

            plt.tight_layout()
            plt.show()

            total = sum(counts)
            print("\n" + "=" * 50)
            print(f"Распределение задач по приоритетам ({self.project_key}):")
            print("=" * 50)
            for label, count in sorted_priorities:
                percentage = (count / total) * 100
                print(f"  {label:<20} {count:>5} задач ({percentage:>6.1f}%)")
            print(f"\nВсего задач с приоритетами: {total}")
            print("=" * 50)

        except Exception as e:
            raise VisualizationError(f"Ошибка при построении распределения по приоритетам: {e}")