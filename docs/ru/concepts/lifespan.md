# Lifespan

Протокол lifespan позволяет приложениям выполнять задачи при запуске и остановке.

## Обзор

Протокол lifespan является частью ASGI и позволяет приложениям:

- Инициализировать ресурсы при запуске
- Очищать ресурсы при остановке

## Использование с FastAPI

FastAPI автоматически обрабатывает lifespan, но вы можете определить свои обработчики:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запуск
    print("Запуск...")
    await connect_to_database()
    
    yield
    
    # Остановка
    print("Остановка...")
    await close_database()

app = FastAPI(lifespan=lifespan)
```

## Ручная реализация ASGI

Если вы реализуете ASGI напрямую:

```python
async def app(scope, receive, send):
    if scope["type"] == "lifespan":
        while True:
            message = await receive()
            
            if message["type"] == "lifespan.startup":
                # Инициализация ресурсов
                await send({"type": "lifespan.startup.complete"})
                
            elif message["type"] == "lifespan.shutdown":
                # Очистка ресурсов
                await send({"type": "lifespan.shutdown.complete"})
                break
```

## Lifespan в ncorn

ncorn полностью поддерживает протокол lifespan:

- Вызывает события запуска при старте сервера
- Вызывает события остановки при выключении сервера
- Корректно обрабатывает graceful shutdown

## Событие запуска

Вызывается, когда сервер готов принимать соединения:

```python
{"type": "lifespan.startup"}
```

Ваше приложение должно ответить:

```python
{"type": "lifespan.startup.complete"}
# или
{"type": "lifespan.startup.failed", "message": "причина ошибки"}
```

## Событие остановки

Вызывается, когда сервер выключается:

```python
{"type": "lifespan.shutdown"}
```

Ваше приложение должно ответить:

```python
{"type": "lifespan.shutdown.complete"}
# или
{"type": "lifespan.shutdown.failed", "message": "причина ошибки"}
```
