from typing import Callable, Annotated

from annotated_doc import Doc

from .base import BaseMiddleware, ASGIApp
from ..config import Config


ALLOWED_METHODS = frozenset({
    "GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"
})

FORBIDDEN_HEADERS = frozenset({
    "transfer-encoding", "connection"
})

REQUIRED_HEADERS = frozenset({
    "host"
})


class ValidationMiddleware(BaseMiddleware):
    """Middleware for request validation."""

    def __init__(self, app: Annotated[
        ASGIApp,
        Doc("ASGI application to validate requests for")
    ], config: Annotated[
        Config,
        Doc("Server configuration")
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
        """Validate request before processing."""
        if scope["type"] != "http":
            await self._error_response(400, "Invalid request type", send)
            return

        if not self._validate_method(scope):
            await self._error_response(405, "Method not allowed", send)
            return

        if not self._validate_headers(scope):
            await self._error_response(400, "Invalid headers", send)
            return

        if not self._validate_path(scope):
            await self._error_response(400, "Invalid path", send)
            return

        await self.app(scope, receive, send)

    def _validate_method(self, scope: Annotated[
        dict,
        Doc("ASGI scope")
    ]) -> Annotated[
        bool,
        Doc("True if method is valid")
    ]:
        """Validate HTTP method."""
        method = scope.get("method", "").upper()
        return method in ALLOWED_METHODS

    def _validate_headers(self, scope: Annotated[
        dict,
        Doc("ASGI scope")
    ]) -> Annotated[
        bool,
        Doc("True if headers are valid")
    ]:
        """Validate request headers."""
        headers = scope.get("headers", [])
        header_names = {name.lower() for name, _ in headers}

        if len(headers) > self.config_obj.max_headers:
            return False

        for name, _ in headers:
            if name.lower() in FORBIDDEN_HEADERS:
                return False

        return True

    def _validate_path(self, scope: Annotated[
        dict,
        Doc("ASGI scope")
    ]) -> Annotated[
        bool,
        Doc("True if path is valid")
    ]:
        """Validate request path."""
        path = scope.get("path", "/")
        if not path.startswith("/"):
            return False
        if "\x00" in path:
            return False
        return True

    async def _error_response(self, status: Annotated[
        int,
        Doc("HTTP status code")
    ], message: Annotated[
        str,
        Doc("Error message")
    ], send: Annotated[
        Callable,
        Doc("ASGI send callable")
    ]) -> None:
        """Send error response."""
        body = f'{{"error": "{message}"}}'.encode()
        await send({
            "type": "http.response.start",
            "status": status,
            "headers": [[b"content-type", b"application/json"]],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
