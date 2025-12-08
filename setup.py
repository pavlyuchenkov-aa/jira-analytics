from setuptools import setup, find_packages
import os

if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "Инструмент для аналитики данных из JIRA с визуализацией метрик проекта"

if os.path.exists("requirements.txt"):
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
else:
    requirements = [
        "matplotlib>=3.5.0",
        "numpy>=1.21.0",
        "requests>=2.28.0"
    ]

data_files = [
    ('config', ['config.json']),  # Конфигурационный файл
]

scripts = []

if os.path.exists("run.sh"):
    scripts.append("run.sh")

setup(
    name="jira-analytics-tool",
    version="1.0.0",
    author="Anton Pavlyuchenkov",
    author_email="a-pavlyuchenkov@bk.ru",
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