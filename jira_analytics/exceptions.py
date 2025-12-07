"""Модуль пользовательских исключений"""

class JiraAnalyticsError(Exception):
    """Базовое исключение для ошибок аналитики JIRA"""
    pass

class ConfigError(JiraAnalyticsError):
    """Ошибка загрузки конфигурации"""
    pass

class JiraApiError(JiraAnalyticsError):
    """Ошибка API JIRA"""
    pass

class DataProcessingError(JiraAnalyticsError):
    """Ошибка обработки данных"""
    pass

class VisualizationError(JiraAnalyticsError):
    """Ошибка визуализации данных"""
    pass