# WebSockets

WebSockets обеспечивают полнодуплексную связь между клиентом и сервером.

## Статус

!!! warning "Скоро"
    Поддержка WebSocket планируется в будущем выпуске.

На данный момент ncorn поддерживает только HTTP/1.1. Поддержка WebSocket будет добавлена в будущей версии.

## Что такое WebSockets?

WebSockets отличаются от HTTP:

- **HTTP**: модель запрос-ответ
- **WebSocket**: двустороннее, постоянное соединение

## ASGI WebSocket Scope

```python
{
    "type": "websocket",
    "path": "/ws",
    "query_string": b"",
    "headers": [...],
    "client": ("127.0.0.1", 8000),
    "server": ("127.0.0.1", 8000),
    "subprotocols": [],
    "asgi": {"version": "3.0"},
}
```

## Сообщения WebSocket

### Подключение

```python
{"type": "websocket.connect"}
```

### Получение

```python
{"type": "websocket.receive", "text": "hello"}
# или
{"type": "websocket.receive", "bytes": b"hello"}
```

### Отправка

```python
{"type": "websocket.send", "text": "hello"}
# или
{"type": "websocket.send", "bytes": b"hello"}
```

### Отключение

```python
{"type": "websocket.disconnect", "code": 1000}
```

## Альтернатива

На данный момент вы можете использовать uvicorn вместе с ncorn для поддержки WebSocket, или использовать reverse proxy, который обрабатывает WebSocket upgrading.
