# ASGI

ASGI (Asynchronous Server Gateway Interface) — это стандартный интерфейс между Python веб-серверами и приложениями.

## Обзор

ASGI — это спецификация, которая описывает, как асинхронные веб-приложения должны общаться с веб-серверами. Она была разработана для замены WSGI (PEP 333) для асинхронных фреймворков.

## Основные понятия

### Scope

`scope` — это словарь, содержащий информацию о соединении:

```python
{
    "type": "http",
    "method": "GET",
    "path": "/",
    "query_string": b"",
    "headers": [(b"host", b"localhost")],
    "client": ("127.0.0.1", 8000),
    "server": ("127.0.0.1", 8000),
    "scheme": "http",
}
```

### Receive

Функция `receive` ожидает входящие данные:

```python
message = await receive()
# Возвращает: {"type": "http.request", "body": b"...", "more_body": bool}
```

### Send

Функция `send` отправляет данные ответа:

```python
# Начало ответа
await send({
    "type": "http.response.start",
    "status": 200,
    "headers": [(b"content-type", b"application/json")],
})

# Отправка тела
await send({
    "type": "http.response.body",
    "body": b'{"message": "hello"}',
})
```

## Типы HTTP

- `http` — обычные HTTP/1.1 соединения
- `websocket` — WebSocket соединения
- `lifespan` — события жизненного цикла приложения

## Реализация ASGI в ncorn

ncorn реализует полноценный ASGI сервер:

- Парсит HTTP/1.1 запросы
- Строит ASGI scope словарь
- Обрабатывает жизненный цикл запроса/ответа
- Поддерживает keep-alive соединения
- Поддерживает только HTTP/1.1 (WebSocket скоро)
