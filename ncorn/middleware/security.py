from typing import Callable, Annotated

from annotated_doc import Doc

from .base import BaseMiddleware, ASGIApp
from ..config import Config


SECURITY_HEADERS = {
    b"x-content-type-options": b"nosniff",
    b"x-frame-options": b"DENY",
    b"x-xss-protection": b"1; mode=block",
    b"strict-transport-security": b"max-age=31536000; includeSubDomains",
    b"referrer-policy": b"strict-origin-when-cross-origin",
    b"permissions-policy": b"geolocation=(), microphone=(), camera=()",
}


class SecurityHeadersMiddleware(BaseMiddleware):
    """Add security headers to responses."""

    def __init__(self, app: Annotated[
        ASGIApp,
        Doc("ASGI application to add security headers to")
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
        """Add security headers to response."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        if not self.config_obj.enable_security_headers:
            await self.app(scope, receive, send)
            return

        headers_sent = []
        response_body = b""

        async def custom_send(message: Annotated[
            dict,
            Doc("ASGI message")
        ]) -> None:
            nonlocal headers_sent, response_body

            if message["type"] == "http.response.start":
                original_headers = message.get("headers", [])
                security_headers = list(original_headers)

                existing_headers = {k.lower() for k, _ in original_headers}

                for name, value in SECURITY_HEADERS.items():
                    if name not in existing_headers:
                        security_headers.append((name, value))

                await send({
                    "type": "http.response.start",
                    "status": message.get("status", 200),
                    "headers": security_headers,
                })
                headers_sent.append(True)

            elif message["type"] == "http.response.body":
                response_body += message.get("body", b"")
                await send({
                    "type": "http.response.body",
                    "body": response_body,
                })

        await self.app(scope, receive, custom_send)
