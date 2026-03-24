import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Annotated

import httptools
from annotated_doc import Doc


class ParserState(Enum):
    """HTTP parser states."""
    IDLE = "idle"
    HEADERS = "headers"
    BODY = "body"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class HttpRequest:
    """Parsed HTTP request."""
    method: Annotated[
        str,
        Doc("HTTP method (GET, POST, PUT, DELETE, etc.)")
    ] = "GET"
    path: Annotated[
        str,
        Doc("Request path without query string")
    ] = "/"
    version: Annotated[
        str,
        Doc("HTTP version (1.0, 1.1)")
    ] = "1.1"
    headers: Annotated[
        list[tuple[bytes, bytes]],
        Doc("List of HTTP headers as (name, value) tuples")
    ] = None
    body: Annotated[
        bytes,
        Doc("Request body content")
    ] = b""
    raw_url: Annotated[
        bytes,
        Doc("Raw URL bytes as received")
    ] = b""
    headers_size: Annotated[
        int,
        Doc("Total size of headers in bytes")
    ] = 0

    def __post_init__(self):
        if self.headers is None:
            self.headers = []


class HttpParser:
    """HTTP/1.1 request parser using httptools."""

    def __init__(
        self,
        max_headers: Annotated[
            int,
            Doc("Maximum number of headers allowed in a request")
        ] = 100,
        max_body_size: Annotated[
            int,
            Doc("Maximum size of request body in bytes")
        ] = 16 * 1024 * 1024,
        max_header_size: Annotated[
            int,
            Doc("Maximum size of a single header in bytes")
        ] = 8192,
        max_headers_total_size: Annotated[
            int,
            Doc("Maximum total size of all headers in bytes")
        ] = 65536,
    ):
        self.max_headers = max_headers
        self.max_body_size = max_body_size
        self.max_header_size = max_header_size
        self.max_headers_total_size = max_headers_total_size
        self.state = ParserState.IDLE
        self.request = HttpRequest()
        self._headers_complete = False
        self._body_size = 0
        self._current_header_size = 0
        self._parser = None

    def parse(self, data: Annotated[
        bytes,
        Doc("Raw HTTP request data to parse")
    ]) -> Annotated[
        HttpRequest,
        Doc("Parsed HTTP request object")
    ]:
        """Parse HTTP request from raw bytes."""
        self._parser = httptools.HttpRequestParser(self)
        try:
            self._parser.feed_data(data)
            if self._parser:
                self.request.method = self._parser.get_method().decode("latin-1")
                self.request.version = self._parser.get_http_version()
        except httptools.HttpParserError:
            self.state = ParserState.ERROR
        except Exception:
            self.state = ParserState.ERROR
        return self.request

    def on_message_begin(self) -> None:
        """Called when message begins."""
        self.state = ParserState.HEADERS
        self.request = HttpRequest()
        self._current_header_size = 0

    def on_header(self, name: bytes, value: bytes) -> None:
        """Called for each header."""
        header_size = len(name) + len(value)
        self._current_header_size += header_size

        if header_size > self.max_header_size:
            self.state = ParserState.ERROR
            return
        if self._current_header_size > self.max_headers_total_size:
            self.state = ParserState.ERROR
            return
        if len(self.request.headers) >= self.max_headers:
            self.state = ParserState.ERROR
            return

        self.request.headers.append((name, value))
        self.request.headers_size += header_size

    def on_headers_complete(self) -> None:
        """Called when headers are complete."""
        self._headers_complete = True

    def on_body(self, body: bytes) -> None:
        """Called when body chunk received."""
        self._body_size += len(body)
        if self._body_size > self.max_body_size:
            self.state = ParserState.ERROR
            return
        self.request.body += body

    def on_message_complete(self) -> None:
        """Called when message is complete."""
        self.state = ParserState.COMPLETE

    def on_url(self, url: bytes) -> None:
        """Called when URL is parsed."""
        self.request.raw_url = url
        self.request.path = url.decode("latin-1", errors="replace")

    def get_status(self) -> Annotated[
        ParserState,
        Doc("Current state of the parser")
    ]:
        """Get current parser state."""
        return self.state


class ResponseWriter:
    """Helper to write HTTP responses."""

    @staticmethod
    async def write_response(
        writer: Annotated[
            asyncio.StreamWriter,
            Doc("Stream writer to send response data")
        ],
        status: Annotated[
            int,
            Doc("HTTP status code (200, 404, 500, etc.)")
        ],
        headers: Annotated[
            list[tuple[bytes, bytes]],
            Doc("Response headers as (name, value) tuples")
        ],
        body: Annotated[
            bytes,
            Doc("Response body content")
        ],
        keep_alive: Annotated[
            bool,
            Doc("Whether to keep connection alive after response")
        ] = True,
        version: Annotated[
            str,
            Doc("HTTP version for response")
        ] = "1.1",
    ) -> Annotated[
        bool,
        Doc("True if response was written successfully, False otherwise")
    ]:
        """Write HTTP response to stream."""
        try:
            reason = ResponseWriter._get_reason(status)
            header_lines = [f"HTTP/{version} {status} {reason}".encode()]

            has_content_length = any(k.lower() == b"content-length" for k, _ in headers)
            has_connection = any(k.lower() == b"connection" for k, _ in headers)

            if not has_content_length:
                header_lines.append(b"Content-Length: " + str(len(body)).encode())

            connection_value = b"keep-alive" if keep_alive else b"close"
            if not has_connection:
                header_lines.append(b"Connection: " + connection_value)

            for name, value in headers:
                header_lines.append(b"%s: %s" % (name, value))

            response = b"\r\n".join(header_lines) + b"\r\n\r\n" + body

            writer.write(response)
            await writer.drain()
            return True
        except Exception:
            return False

    @staticmethod
    def _get_reason(status: Annotated[
        int,
        Doc("HTTP status code")
    ]) -> Annotated[
        str,
        Doc("HTTP reason phrase")
    ]:
        """Get HTTP reason phrase for status code."""
        reasons = {
            100: "Continue",
            101: "Switching Protocols",
            200: "OK",
            201: "Created",
            204: "No Content",
            301: "Moved Permanently",
            302: "Found",
            304: "Not Modified",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            408: "Request Timeout",
            413: "Payload Too Large",
            414: "URI Too Long",
            429: "Too Many Requests",
            431: "Request Header Fields Too Large",
            500: "Internal Server Error",
            501: "Not Implemented",
            502: "Bad Gateway",
            503: "Service Unavailable",
            504: "Gateway Timeout",
        }
        return reasons.get(status, "Unknown")
