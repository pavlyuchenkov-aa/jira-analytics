"""Модуль для работы с JIRA API"""
import requests
import json
from typing import Dict, List, Any
from datetime import datetime
from jira_analytics.exceptions import JiraApiError

def calculate_resolution_days(created_str: str, resolved_str: str) -> int:
    """
    Расчет времени между созданием и разрешением задачи в днях

    Args:
        created_str: Дата создания в формате ISO
        resolved_str: Дата разрешения в формате ISO

    Returns:
        Количество дней (0 при ошибке)
    """
    try:
        if not created_str or not resolved_str:
            return 0

        created = datetime.strptime(created_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        resolved = datetime.strptime(resolved_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')

        if resolved < created:
            print(f"Предупреждение: Дата разрешения раньше даты создания")
            return 0

        return (resolved - created).days
    except (ValueError, AttributeError, TypeError) as e:
        print(f"Ошибка при расчете времени: {e}")
        return 0

def fetch_jira_issues(jira_url: str, project_key: str, max_results: int) -> List[Dict[str, Any]]:
    """
    Получение задач из JIRA API

    Args:
        jira_url: URL JIRA сервера
        project_key: Ключ проекта
        max_results: Максимальное количество результатов

    Returns:
        Список задач JIRA

    Raises:
        JiraApiError: При ошибках API JIRA
    """
    url = f"{jira_url}/rest/api/2/search"
    params = {
        "jql": f"project={project_key} AND status in (Closed, Resolved)",
        "maxResults": max_results,
        "fields": "key,created,resolutiondate,status,reporter,assignee,priority,timespent,summary"
    }

    try:
        print(f"Запрос задач проекта {project_key}...")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        total_issues = data.get("total", 0)
        issues = data.get("issues", [])

        print(f"Получено {len(issues)} из {total_issues} задач")
        return issues

    except requests.exceptions.Timeout:
        raise JiraApiError(f"Таймаут при запросе к JIRA ({jira_url})")
    except requests.exceptions.ConnectionError:
        raise JiraApiError(f"Ошибка подключения к JIRA ({jira_url})")
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else "unknown"
        raise JiraApiError(f"HTTP ошибка {status_code} при запросе к JIRA: {e}")
    except json.JSONDecodeError as e:
        raise JiraApiError(f"Ошибка парсинга ответа JIRA: {e}")
    except Exception as e:
        raise JiraApiError(f"Неожиданная ошибка при получении задач: {e}")