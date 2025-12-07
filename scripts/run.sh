#!/bin/bash

# Скрипт запуска JIRA Analytics Tool для Linux/macOS
# ====================================================

echo "JIRA Analytics Tool - Запуск"
echo ""

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python3 не установлен"
    echo "Установите Python 3.8 или выше"
    exit 1
fi

# Проверка версии Python
PYTHON_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ $PYTHON_MAJOR -lt 3 ] || ([ $PYTHON_MAJOR -eq 3 ] && [ $PYTHON_MINOR -lt 8 ]); then
    echo "Ошибка: Требуется Python версии 3.8 или выше"
    echo "Текущая версия: $PYTHON_VERSION"
    exit 1
fi

# Установка зависимостей (если не установлены)
echo "Проверка зависимостей..."
pip3 install -r requirements.txt > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Предупреждение: Не удалось автоматически установить зависимости"
    echo "Установите зависимости вручную: pip3 install -r requirements.txt"
fi

# Запуск приложения
echo ""
echo "Запуск JIRA Analytics Tool..."
echo ""

# Проверка аргументов командной строки
if [ $# -eq 0 ]; then
    python3 -m jira_analytics.cli
else
    python3 -m jira_analytics.cli "$@"
fi