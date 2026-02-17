# Заметки

## Работа с venv

```
# Создание venv
python3 -m venv .venv

# Активация venv
source .venv/bin/activate

# Деактивация venv
deactivate
```

## Установка Python-пакетов

Список всех установленных Python-пакетов нужно хранить в `requirements.txt`.

```
# Установка всех Python-пакетов из requirements.txt
pip install -r requirements.txt

# Запись всех установленных Python-пакетов в requirements.txt
pip freeze -> requirements.txt
```

## Ограничения длины строки

Установить правило в `.vscode/settings.json`

```
"editor.rulers": [80]
```

## Запуск сервиса

```
python3 -m src.main
```

## Настройка доступа к Google Таблице через `gspread`

1. Зайти в [Google Cloud Console](https://console.cloud.google.com)

2. Создать проект: Select a project -> New Project -> Заполнить "Project name" -> Create

3. Включить Google Sheets API: Navigation menu -> Library -> Найти "Google Sheets API" -> Enable

4. Создать сервисный аккаунт: Navigation menu -> IAM & Admin -> Service Accounts -> Create service account -> Заполнить поле Service account name (поле Service account ID заполнится автоматически) -> Create and continue -> Continue (раздел "Permissions" пропускаем) -> Done (Раздел "Principals with access" пропускаем) -> Создаться аккаунт `<account_name>@<project_name>.iam.gserviceaccount.com`

5. Создать ключ: В разделе "Service accounts" в списке аккаунтов нажать на `<account_name>@<project_name>.iam.gserviceaccount.com` -> Keys -> Add key -> Create new key -> JSON (Recommended) -> Create -> Ключ скачается в формате JSON-файла -> Файл переименовать в `credentials.json` и добавить в проект (также добавить в `.gitignore`)

6. Настройка доступа к Google Таблице: Создать Google Таблицу -> Настройки Доступа -> Добавить `<account_name>@<project_name>.iam.gserviceaccount.com` в качестве редактора -> Готово

7. Доступ к Google Таблице с помощью `gspread` осуществляется либо через URL `https://docs.google.com/spreadsheets/d/<spreadsheet_id>/edit`, либо непосредственно через ID таблицы `<spreadsheet_id>`
