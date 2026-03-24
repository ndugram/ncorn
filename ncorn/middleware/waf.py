from typing import Callable, Annotated

from annotated_doc import Doc

from .base import BaseMiddleware, ASGIApp
from ..config import Config


class WAFMiddleware(BaseMiddleware):
    """Web Application Firewall middleware."""

    def __init__(self, app: Annotated[
        ASGIApp,
        Doc("ASGI application to apply WAF protection to")
    ], config: Annotated[
        Config,
        Doc("Server configuration with WAF settings")
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
        """Apply WAF checks."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        query_string = scope.get("query_string", b"")

        if not self._check_path(path):
            await self._blocked_response(send, "Path contains forbidden pattern")
            return

        if len(query_string) > self.config_obj.waf_max_query_length:
            await self._blocked_response(send, "Query string too long")
            return

        await self.app(scope, receive, send)

    def _check_path(self, path: Annotated[
        str,
        Doc("Request path to check")
    ]) -> Annotated[
        bool,
        Doc("True if path is safe")
    ]:
        """Check path for forbidden patterns."""
        if ".." in path:
            return False
        if "\x00" in path:
            return False
        if path.startswith("/."):
            return False
        dangerous_patterns = [
            "/etc/passwd",
            "/etc/shadow",
            "/.git/",
            "/.env",
            "/wp-config.php",
            "\\\\",
            "//",
        ]
        lower_path = path.lower()
        for pattern in dangerous_patterns:
            if pattern in lower_path:
                return False
        return True

    async def _blocked_response(self, send: Annotated[
        Callable,
        Doc("ASGI send callable")
    ], message: Annotated[
        str,
        Doc("Block reason message")
    ]) -> None:
        """Send blocked response."""
        body = f'{{"error": "Forbidden", "reason": "{message}"}}'.encode()
        await send({
            "type": "http.response.start",
            "status": 403,
            "headers": [[b"content-type", b"application/json"]],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
