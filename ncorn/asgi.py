import asyncio
from typing import Annotated, Callable

from annotated_doc import Doc

from .protocol import HttpRequest


class ASGIAdapter:
    """Adapter to convert ncorn requests to ASGI scope."""

    def __init__(
        self,
        scope: Annotated[
            dict,
            Doc(
                """
                ASGI scope dictionary containing connection information.
                Includes type, http_version, method, path, query_string, headers, client, server.
                """
            )
        ],
        receive: Annotated[
            Callable,
            Doc(
                """
                ASGI receive callable to get messages from the application.
                Returns messages like {'type': 'http.request', 'body': bytes, 'more_body': bool}.
                """
            )
        ],
        send: Annotated[
            Callable,
            Doc(
                """
                ASGI send callable to send messages to the application.
                Sends {'type': 'http.response.start', ...} and {'type': 'http.response.body', ...}.
                """
            )
        ]
    ) -> None:
        self.scope = scope
        self.receive = receive
        self.send = send

    async def __call__(self, response: dict) -> None:
        """Send response through ASGI interface."""
        await self.send(response)


class ASGIHTTPConnection:
    """ASGI HTTP connection implementation."""

    def __init__(self, scope: dict, receive: Callable, send: Callable):
        self.scope = scope
        self.receive = receive
        self.send = send
        self._response_started = False
        self._response_headers = []

    async def listen_for_disconnect(self) -> None:
        """Wait for client disconnect."""
        while True:
            message = await self.receive()
            if message.get("type") == "http.disconnect":
                break
            await asyncio.sleep(0.1)


def build_asgi_scope(
    request: HttpRequest,
    client: tuple[str, int] | None,
    server: tuple[str, int] | None,
) -> dict:
    """Build ASGI scope from parsed HTTP request."""
    headers = [(k, v) for k, v in request.headers]

    raw_path = request.raw_url or request.path.encode()
    path = raw_path.split(b"?")[0].decode("latin-1", errors="replace")
    query_string = b"".join(raw_path.split(b"?")[1:]) if b"?" in raw_path else b""

    scope = {
        "type": "http",
        "asgi": {
            "version": "3.0",
            "spec_version": "2.4",
        },
        "http_version": request.version,
        "method": request.method,
        "path": path,
        "query_string": query_string,
        "headers": headers,
        "client": client,
        "server": server,
        "root_path": "",
        "scheme": "http",
    }

    return scope


async def read_body(receive: Callable, max_size: int) -> bytes:
    """Read request body from ASGI receive."""
    body = b""
    while True:
        message = await receive()
        if message.get("type") == "http.request":
            chunk = message.get("body", b"")
            if len(body) + len(chunk) > max_size:
                return b""
            body += chunk
            if not message.get("more_body", False):
                break
        elif message.get("type") == "http.disconnect":
            break
    return body


async def send_asgi_response(
    send: Callable,
    status: int,
    headers: list[tuple[bytes, bytes]],
    body: bytes,
) -> None:
    """Send response through ASGI interface."""
    await send({
        "type": "http.response.start",
        "status": status,
        "headers": headers,
    })
    await send({
        "type": "http.response.body",
        "body": body,
    })
