"""Основной модуль приложения"""
import sys
import os

# Добавляем текущую директорию в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from jira_analytics.config import load_configuration
from jira_analytics.jira_client import fetch_jira_issues
from jira_analytics.data_processor import DataProcessor
from jira_analytics.visualizer import JiraVisualizer
from jira_analytics.menu import display_menu, MenuHandler
from jira_analytics.exceptions import ConfigError, JiraApiError, DataProcessingError

def main() -> None:
    """
    Основная функция приложения
    """
    try:
        # Загрузка конфигурации
        config = load_configuration()

        JIRA_URL = config['jira_url']
        PROJECT_KEY = config['project_key']
        MAX_RESULTS = config['max_results']

        # Получение данных из JIRA
        issues = fetch_jira_issues(JIRA_URL, PROJECT_KEY, MAX_RESULTS)

        if not issues:
            print("Не удалось получить данные. Проверьте настройки и подключение.")
            return

        # Инициализация компонентов
        processor = DataProcessor(issues)
        visualizer = JiraVisualizer(PROJECT_KEY)
        menu_handler = MenuHandler(processor, visualizer)

        # Основной цикл меню
        while True:
            try:
                display_menu(PROJECT_KEY, len(issues))
                choice = input("Выберите опцию (0-6): ").strip()

                if not menu_handler.handle_choice(choice):
                    break

                input("\nНажмите Enter для продолжения...")

            except KeyboardInterrupt:
                print("\nПрограмма прервана пользователем.")
                break
            except DataProcessingError as e:
                print(f"Ошибка обработки данных: {e}")
                input("\nНажмите Enter для продолжения...")
            except Exception as e:
                print(f"Неожиданная ошибка: {e}")
                input("\nНажмите Enter для продолжения...")

    except ConfigError as e:
        print(f"Ошибка конфигурации: {e}")
    except JiraApiError as e:
        print(f"Ошибка JIRA API: {e}")
    except Exception as e:
        print(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    main()