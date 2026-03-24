# Middleware

ncorn includes server-level middleware for request processing.

## Available Middleware

### ValidationMiddleware

Validates HTTP methods, headers, and paths.

### RateLimitMiddleware

IP-based rate limiting to prevent abuse.

## Custom Middleware

You can create custom middleware by extending `BaseMiddleware`:

```python
from ncorn.middleware.base import BaseMiddleware, ASGIApp

class CustomMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Process request
        await self.app(scope, receive, send)
        # Process response
```

## Middleware Order

Middleware is executed in the following order:

1. ValidationMiddleware
2. RateLimitMiddleware
3. Your application
