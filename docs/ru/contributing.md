# Контрибьютинг

Спасибо за ваш интерес к контрибьютингу в ncorn!

## Настройка окружения разработки

1. Клонируйте репозиторий:
```bash
git clone https://github.com/ndugram/ncorn.git
cd ncorn
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

3. Установите зависимости для разработки:
```bash
pip install -e .
pip install pytest httpx
```

## Стиль кода

- Следуйте PEP 8
- Используйте type hints
- Добавляйте docstrings через `annotated_doc`

## Тестирование

Запуск тестов:
```bash
pytest
```

Запуск с покрытием:
```bash
pytest --cov=ncorn --cov-report=html
```

## Структура проекта

```
ncorn/
├── __init__.py       # Инициализация пакета
├── cli.py            # Интерфейс командной строки
├── config.py         # Класс конфигурации
├── config_file.py    # Загрузка конфигурации
├── logging.py        # Утилиты логирования
├── main.py           # Основная точка входа
├── protocol.py       # Парсер HTTP протокола
├── reload.py         # Функциональность авто-перезагрузки
├── server.py         # HTTP сервер
├── middleware/       # Модули middleware
│   ├── base.py
│   ├── ipfilter.py
│   ├── ratelimit.py
│   ├── security.py
│   ├── validation.py
│   └── waf.py
└── asgi.py          # ASGI адаптер
```

## Процесс Pull Request

1. Сделайте форк репозитория
2. Создайте ветку для фичи (`git checkout -b feature/awesome-feature`)
3. Внесите изменения
4. Добавьте тесты, если применимо
5. Убедитесь, что все тесты проходят
6. Закоммитьте изменения (`git commit -m 'Add awesome feature'`)
7. Отправьте в ветку (`git push origin feature/awesome-feature`)
8. Откройте Pull Request

## Сообщение об ошибках

Пожалуйста, сообщайте об ошибках и запросах фич через GitHub Issues.

## Лицензия

Контрибьютая, вы соглашаетесь, что ваши изменения будут лицензированы под MIT License.
