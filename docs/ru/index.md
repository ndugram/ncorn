# Добро пожаловать

![ncorn](../logo.png)

_ncorn — готовый к продакшену ASGI веб-сервер для FastAPI приложений._

---

**Документация**: [https://ncorn.ndugram.dev](https://ncorn.readthedocs.io/)

**Исходный код**: [https://github.com/ndugram/ncorn](https://github.com/ndugram/ncorn)

---

**ncorn** — это реализация ASGI веб-сервера для Python, разработанная специально для FastAPI приложений.

До недавнего времени в Python не было минимального низкоуровневого интерфейса сервер/приложение для асинхронных фреймворков. [Спецификация ASGI](https://asgi.readthedocs.io/en/latest/) заполняет этот пробел, что позволяет создавать общий набор инструментов для всех асинхронных фреймворков.

ncorn построен с упором на **производительность** и **готовность к продакшену**, с встроенными мерами безопасности и поддержкой SSL/TLS.

## Возможности

- **Высокая производительность** — построен на asyncio
- **ASGI совместимость** — полная поддержка ASGI интерфейса для FastAPI
- **Готов к продакшену** — rate limiting, валидация запросов, защита от slowloris
- **SSL/TLS** — нативная поддержка HTTPS без reverse proxy
- **Несколько воркеров** — поддержка нескольких процессов
- **Авто-перезагрузка** — режим разработки с отслеживанием файлов
- **Красивое логирование** — красивый вывод в стиле uvicorn
- **Безопасность** — валидация заголовков, ограничения размера тела, IP rate limiting

## Быстрый старт

ncorn доступен на PyPI, установка проста:

```bash
pip install ncorn
```

Создадим простое FastAPI приложение:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Привет от ncorn!"}
```

Запустим его с ncorn:

```bash
ncorn main:app
```

## Запуск с HTTPS

ncorn имеет встроенную поддержку SSL/TLS — не нужен внешний reverse proxy:

```bash
ncorn main:app --ssl-keyfile certs/key.pem --ssl-certfile certs/cert.pem
```

Сервер запустится на `https://127.0.0.1:8000`

## Требования

- Python 3.11+
- httptools
- rich
- annotated-doc
