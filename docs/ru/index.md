# Добро пожаловать в ncorn

ncorn - это production-ready ASGI веб-сервер, разработанный специально для приложений FastAPI.

## Возможности

- Асинхронный TCP-сервер с использованием asyncio
- HTTP/1.1 парсер на базе httptools
- ASGI адаптер
- Система middleware (серверного уровня)
- Валидация запросов (заголовки, ограничения размера тела)
- Ограничение частоты запросов (rate limiting)
- Graceful shutdown
- Keep-alive соединения

## Функции безопасности

- Ограничение максимального размера тела запроса
- Валидация заголовков
- Защита от Slowloris (таймауты)
- IP-based rate limiting

## Быстрый старт

```bash
pip install ncorn
ncorn module:app
```

## Требования

- Python 3.11+
- httptools
- rich
