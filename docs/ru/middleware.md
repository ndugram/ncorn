# Middleware

ncorn включает middleware на уровне сервера для обработки запросов.

## Доступные Middleware

### ValidationMiddleware

Валидирует HTTP методы, заголовки и пути.

### RateLimitMiddleware

IP-based rate limiting для предотвращения злоупотреблений.

## Создание своего middleware

Вы можете создать свой middleware расширив `BaseMiddleware`:

```python
from ncorn.middleware.base import BaseMiddleware, ASGIApp

class CustomMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Обработка запроса
        await self.app(scope, receive, send)
        # Обработка ответа
```

## Порядок выполнения middleware

Middleware выполняется в следующем порядке:

1. ValidationMiddleware
2. RateLimitMiddleware
3. Ваше приложение
