"""Модуль загрузки и валидации конфигурации"""
import json
import os
from typing import Dict, Any
from jira_analytics.exceptions import ConfigError

DEFAULT_CONFIG = {
    "jira_url": "https://issues.apache.org/jira",
    "project_key": "KAFKA",
    "max_results": 500
}

def validate_config(config: Dict[str, Any]) -> None:
    """
    Валидация конфигурации

    Args:
        config: Словарь с конфигурацией

    Raises:
        ConfigError: При невалидной конфигурации
    """
    required_keys = ["jira_url", "project_key", "max_results"]
    missing_keys = [key for key in required_keys if key not in config]

    if missing_keys:
        raise ConfigError(f"Отсутствуют обязательные ключи конфигурации: {missing_keys}")

    # Проверка типов
    if not isinstance(config["project_key"], str):
        raise ConfigError("project_key должен быть строкой")

    if not isinstance(config["max_results"], int):
        raise ConfigError("max_results должен быть целым числом")

    if config["max_results"] <= 0:
        raise ConfigError("max_results должен быть положительным числом")

    # Проверка URL
    if not config["jira_url"].startswith(("http://", "https://")):
        raise ConfigError("jira_url должен быть валидным URL (начинаться с http:// или https://)")

def load_configuration(config_path: str = "config.json", strict: bool = False) -> Dict[str, Any]:
    """
    Загрузка конфигурации из JSON-файла

    Args:
        config_path: Путь к файлу конфигурации
        strict: Если True, требует все обязательные ключи в файле конфигурации

    Returns:
        Dict с настройками

    Raises:
        ConfigError: При ошибках чтения или парсинга конфигурации
    """
    try:
        if not os.path.exists(config_path):
            print(f"Файл {config_path} не найден. Используются настройки по умолчанию")
            config = DEFAULT_CONFIG.copy()
            validate_config(config)
            return config

        with open(config_path, 'r', encoding='utf-8') as file:
            user_config = json.load(file)

        if strict:
            # Строгий режим: все обязательные ключи должны быть в файле
            required_keys = ["jira_url", "project_key", "max_results"]
            missing_keys = [key for key in required_keys if key not in user_config]

            if missing_keys:
                raise ConfigError(f"В конфигурации отсутствуют обязательные ключи: {missing_keys}")

            config = user_config.copy()
        else:
            # Мягкий режим: используем дефолтные значения для отсутствующих ключей
            config = DEFAULT_CONFIG.copy()
            config.update(user_config)

        # Валидируем финальную конфигурацию
        validate_config(config)

        print(f"Конфигурация загружена из {config_path}")
        print(f"Проект: {config['project_key']}, "
              f"URL: {config['jira_url']}, "
              f"Макс. результатов: {config['max_results']}")

        return config

    except json.JSONDecodeError as e:
        raise ConfigError(f"Ошибка парсинга JSON в файле {config_path}: {e}")
    except IOError as e:
        raise ConfigError(f"Ошибка чтения файла {config_path}: {e}")
    except Exception as e:
        if isinstance(e, ConfigError):
            raise e
        raise ConfigError(f"Неожиданная ошибка при загрузке конфигурации: {e}")