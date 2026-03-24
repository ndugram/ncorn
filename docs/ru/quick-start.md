# Быстрый старт

## Установка

```bash
pip install ncorn
```

## Базовое использование

Создайте приложение FastAPI:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from ncorn!"}
```

Запустите с ncorn:

```bash
ncorn module:app
```

## Параметры командной строки

```bash
ncorn module:app --host 0.0.0.0 --port 8080
```

## Опции

- `--host` - Хост для привязки (по умолчанию: 127.0.0.1)
- `--port` - Порт для привязки (по умолчанию: 8000)
- `--reload` - Включить автоперезагрузку при изменении файлов
- `--workers` - Количество рабочих процессов (по умолчанию: 1)
