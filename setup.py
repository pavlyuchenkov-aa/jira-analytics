from setuptools import setup, find_packages
import os

# Читаем README для long_description
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "Инструмент для аналитики данных из JIRA с визуализацией метрик проекта"

# Читаем requirements.txt
if os.path.exists("requirements.txt"):
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
else:
    requirements = [
        "matplotlib>=3.5.0",
        "numpy>=1.21.0",
        "requests>=2.28.0"
    ]

# Список файлов данных для включения в пакет
data_files = [
    ('config', ['config.json']),  # Конфигурационный файл
]

# Скрипты для разных платформ
scripts = []

# Добавляем скрипт для Linux если он существует
if os.path.exists("run.sh"):
    scripts.append("run.sh")

setup(
    name="jira-analytics-tool",
    version="1.0.0",
    author="AAAAA",
    author_email="",
    description="Инструмент для аналитики данных из JIRA с визуализацией метрик проекта",
    long_description=long_description,
    long_description_content_type="text/markdown",

    packages=find_packages(),
    include_package_data=True,
    data_files=data_files,
    scripts=scripts,

    python_requires=">=3.8",
    install_requires=requirements,

    entry_points={
        "console_scripts": [
            "jira-analytics=jira_analytics.cli:main",
        ],
    }
)