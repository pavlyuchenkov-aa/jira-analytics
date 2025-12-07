"""
JIRA Analytics Package
Аналитика данных из JIRA для визуализации метрик проекта
"""

from .config import load_configuration, validate_config, DEFAULT_CONFIG
from .exceptions import (JiraAnalyticsError, ConfigError, JiraApiError,
                         DataProcessingError, VisualizationError)
from .jira_client import fetch_jira_issues, calculate_resolution_days
from .data_processor import DataProcessor
from .visualizer import JiraVisualizer
from .menu import display_menu, MenuHandler

__all__ = [
    'load_configuration',
    'validate_config',
    'DEFAULT_CONFIG',
    'JiraAnalyticsError',
    'ConfigError',
    'JiraApiError',
    'DataProcessingError',
    'VisualizationError',
    'fetch_jira_issues',
    'calculate_resolution_days',
    'DataProcessor',
    'JiraVisualizer',
    'display_menu',
    'MenuHandler'
]

__version__ = '1.0.0'