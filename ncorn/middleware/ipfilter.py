from typing import Callable, Annotated

from annotated_doc import Doc

from .base import BaseMiddleware, ASGIApp
from ..config import Config


class IPFilterMiddleware(BaseMiddleware):
    """IP blacklist/whitelist middleware."""

    def __init__(self, app: Annotated[
        ASGIApp,
        Doc("ASGI application to apply IP filtering to")
    ], config: Annotated[
        Config,
        Doc("Server configuration with IP whitelist/blacklist")
    ]):
        super().__init__(app, {})
        self.config_obj = config

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
        """Apply IP filtering."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        client_ip = self._get_client_ip(scope)

        if not self._is_allowed(client_ip):
            await self._blocked_response(send, client_ip)
            return

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

    def _is_allowed(self, ip: Annotated[
        str,
        Doc("Client IP address to check")
    ]) -> Annotated[
        bool,
        Doc("True if IP is allowed")
    ]:
        """Check if IP is allowed."""
        whitelist = self.config_obj.ip_whitelist
        blacklist = self.config_obj.ip_blacklist

        if whitelist:
            return ip in whitelist

        if blacklist:
            return ip not in blacklist

        return True

    async def _blocked_response(self, send: Annotated[
        Callable,
        Doc("ASGI send callable")
    ], ip: Annotated[
        str,
        Doc("Blocked IP address")
    ]) -> None:
        """Send blocked response."""
        body = f'{{"error": "Access denied", "ip": "{ip}"}}'.encode()
        await send({
            "type": "http.response.start",
            "status": 403,
            "headers": [[b"content-type", b"application/json"]],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
