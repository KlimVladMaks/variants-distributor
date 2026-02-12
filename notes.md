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
