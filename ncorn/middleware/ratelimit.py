import time
from typing import Callable, Annotated
from collections import defaultdict

from annotated_doc import Doc

from .base import BaseMiddleware, ASGIApp
from ..config import Config


class RateLimitMiddleware(BaseMiddleware):
    """Middleware for IP-based rate limiting."""

    def __init__(self, app: Annotated[
        ASGIApp,
        Doc("ASGI application to apply rate limiting to")
    ], config: Annotated[
        Config,
        Doc("Server configuration with rate limit settings")
    ]):
        super().__init__(app, {})
        self.config_obj = config
        self.requests: dict[str, list[float]] = defaultdict(list)

    async def __call__(self, scope: Annotated[
        dict,
        Doc("ASGI scope dictionary")
    ], receive: Annotated[
        Callable,
        Doc("ASGI receive callable")
    ], send: Annotated[
        Callable,
        Doc("ASGI send callable")
    ]) -> None:
        """Apply rate limiting."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        client_ip = self._get_client_ip(scope)
        if not self._check_rate_limit(client_ip):
            await self._rate_limit_exceeded(send)
            return

        self._record_request(client_ip)
        await self.app(scope, receive, send)

    def _get_client_ip(self, scope: Annotated[
        dict,
        Doc("ASGI scope")
    ]) -> Annotated[
        str,
        Doc("Client IP address")
    ]:
        """Extract client IP from scope."""
        for name, value in scope.get("headers", []):
            if name == b"x-forwarded-for":
                return value.decode().split(",")[0].strip()
            if name == b"x-real-ip":
                return value.decode()

        client = scope.get("client")
        if client:
            return client[0]
        return "unknown"

    def _check_rate_limit(self, client_ip: Annotated[
        str,
        Doc("Client IP address")
    ]) -> Annotated[
        bool,
        Doc("True if client is within rate limit")
    ]:
        """Check if client has exceeded rate limit."""
        now = time.time()
        window = self.config_obj.rate_limit_window

        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip]
            if now - ts < window
        ]

        return len(self.requests[client_ip]) < self.config_obj.rate_limit_requests

    def _record_request(self, client_ip: Annotated[
        str,
        Doc("Client IP address")
    ]) -> None:
        """Record request timestamp."""
        self.requests[client_ip].append(time.time())

    async def _rate_limit_exceeded(self, send: Annotated[
        Callable,
        Doc("ASGI send callable")
    ]) -> None:
        """Send rate limit exceeded response."""
        body = b'{"error": "Rate limit exceeded"}'
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                [b"content-type", b"application/json"],
                [b"retry-after", b"60"],
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
