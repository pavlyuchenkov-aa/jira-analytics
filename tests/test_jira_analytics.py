import unittest
import json
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Добавляем родительскую директорию в путь для импорта модулей
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Импортируем из отдельных модулей
from jira_analytics.config import load_configuration, validate_config, DEFAULT_CONFIG
from jira_analytics.exceptions import ConfigError, JiraApiError
from jira_analytics.jira_client import fetch_jira_issues, calculate_resolution_days
from jira_analytics.data_processor import DataProcessor


class TestJiraAnalyticsKeyFunctions(unittest.TestCase):
    """Ключевые тесты для JIRA Analytics"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.test_issues = [
            {
                'fields': {
                    'created': '2024-01-01T10:00:00.000',
                    'resolutiondate': '2024-01-05T14:30:00.000',
                    'status': {'name': 'Closed'},
                    'assignee': {'displayName': 'John Doe'},
                    'reporter': {'displayName': 'Jane Smith'},
                    'priority': {'name': 'High'},
                    'timespent': 86400  # 1 день в секундах
                }
            },
            {
                'fields': {
                    'created': '2024-01-02T09:00:00.000',
                    'resolutiondate': '2024-01-10T16:00:00.000',
                    'status': {'name': 'Resolved'},
                    'assignee': None,
                    'reporter': {'displayName': 'Jane Smith'},
                    'priority': {'name': 'Medium'},
                    'timespent': None
                }
            }
        ]

    def tearDown(self):
        """Очистка после тестов"""
        if hasattr(self, 'temp_config_file'):
            if os.path.exists(self.temp_config_file):
                os.remove(self.temp_config_file)

    def test_1_load_configuration_default(self):
        """1. Тест загрузки конфигурации по умолчанию (базовый функционал)"""
        # Создаем и удаляем временный файл, чтобы тестировать случай отсутствия конфигурации
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            self.temp_config_file = f.name
        os.remove(self.temp_config_file)

        config = load_configuration(self.temp_config_file)

        # Проверяем, что все обязательные ключи присутствуют
        self.assertIn('jira_url', config)
        self.assertIn('project_key', config)
        self.assertIn('max_results', config)
        # Проверяем значения по умолчанию
        self.assertEqual(config['project_key'], DEFAULT_CONFIG['project_key'])

    def test_2_load_configuration_custom(self):
        """2. Тест загрузки пользовательской конфигурации"""
        test_config = {
            'jira_url': 'https://test-jira.example.com',
            'project_key': 'TEST',
            'max_results': 50
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_config, f)
            self.temp_config_file = f.name

        config = load_configuration(self.temp_config_file)

        # Проверяем, что пользовательские значения загружаются корректно
        self.assertEqual(config['jira_url'], 'https://test-jira.example.com')
        self.assertEqual(config['project_key'], 'TEST')
        self.assertEqual(config['max_results'], 50)

    def test_3_load_configuration_invalid_json(self):
        """3. Тест обработки некорректного JSON (обработка ошибок)"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('invalid json content')
            self.temp_config_file = f.name

        # Проверяем, что при некорректном JSON возникает правильное исключение
        with self.assertRaises(ConfigError):
            load_configuration(self.temp_config_file)

    def test_4_validate_config_valid(self):
        """4. Тест валидации корректной конфигурации"""
        valid_config = {
            'jira_url': 'https://test-jira.example.com',
            'project_key': 'TEST',
            'max_results': 100
        }

        # Не должно вызывать исключение
        validate_config(valid_config)

    def test_5_validate_config_missing_keys(self):
        """5. Тест валидации конфигурации с отсутствующими ключами"""
        invalid_config = {
            'jira_url': 'https://test-jira.example.com'
            # Отсутствуют project_key и max_results
        }

        # Проверяем, что при отсутствии обязательных ключей возникает исключение
        with self.assertRaises(ConfigError):
            validate_config(invalid_config)

    def test_6_calculate_resolution_days_valid(self):
        """6. Тест расчета времени между созданием и разрешением задачи"""
        created = '2024-01-01T10:00:00.000'
        resolved = '2024-01-05T14:30:00.000'

        days = calculate_resolution_days(created, resolved)

        # Проверяем правильность расчета (разница 4 дня)
        self.assertEqual(days, 4)

    def test_7_calculate_resolution_days_invalid_format(self):
        """7. Тест расчета дней для невалидного формата даты"""
        created = 'invalid-date'
        resolved = '2024-01-05T14:30:00.000'

        days = calculate_resolution_days(created, resolved)

        # При ошибке парсинга должна возвращаться 0
        self.assertEqual(days, 0)

    @patch('jira_analytics.jira_client.requests.get')
    def test_8_fetch_jira_issues_success(self, mock_get):
        """8. Тест успешного получения задач из JIRA API"""
        # Настраиваем мок ответа от API
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'total': 2,
            'issues': self.test_issues
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Вызываем тестируемую функцию
        issues = fetch_jira_issues('https://test-jira.example.com', 'TEST', 100)

        # Проверяем результаты
        self.assertEqual(len(issues), 2)
        mock_get.assert_called_once()

    @patch('jira_analytics.jira_client.requests.get')
    def test_9_fetch_jira_issues_timeout(self, mock_get):
        """9. Тест обработки таймаута при запросе к JIRA"""
        # Симулируем таймаут
        mock_get.side_effect = TimeoutError('Request timeout')

        # Проверяем, что при таймауте возникает правильное исключение
        with self.assertRaises(JiraApiError):
            fetch_jira_issues('https://test-jira.example.com', 'TEST', 100)

    def test_10_data_processor_basic_functionality(self):
        """10. Тест базового функционала DataProcessor"""
        processor = DataProcessor(self.test_issues)

        # Тестируем несколько ключевых методов
        times = processor.get_resolution_times()
        user_stats = processor.get_user_stats()
        priority_dist = processor.get_priority_distribution()

        # Проверяем результаты
        self.assertEqual(len(times), 2)
        self.assertEqual(times[0], 4)  # 4 дня для первой задачи
        self.assertEqual(user_stats['John Doe'], 1)
        self.assertEqual(user_stats['Jane Smith'], 2)  # reporter в двух задачах
        self.assertEqual(priority_dist['High'], 1)
        self.assertEqual(priority_dist['Medium'], 1)


if __name__ == '__main__':
    unittest.main()