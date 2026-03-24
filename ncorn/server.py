import asyncio
import time
from typing import Optional, Annotated
from collections import defaultdict

from annotated_doc import Doc

from .config import Config
from .protocol import HttpParser, ResponseWriter, ParserState
from .asgi import build_asgi_scope
from .logging import logger, RequestLog
from .middleware import BaseMiddleware


class ConnectionLimiter:
    """Global and per-IP connection limiter."""

    def __init__(self, max_connections: int, max_per_ip: int):
        self.max_connections = max_connections
        self.max_per_ip = max_per_ip
        self.total_connections = 0
        self.ip_connections = defaultdict(int)
        self._lock = asyncio.Lock()

    async def can_connect(self, ip: Annotated[
        str,
        Doc("Client IP address to check")
    ]) -> Annotated[
        bool,
        Doc("True if connection is allowed, False otherwise")
    ]:
        """Check if connection is allowed."""
        async with self._lock:
            if self.total_connections >= self.max_connections:
                return False
            if self.ip_connections[ip] >= self.max_per_ip:
                return False
            return True

    async def add_connection(self, ip: Annotated[
        str,
        Doc("Client IP address")
    ]) -> None:
        """Add a new connection."""
        async with self._lock:
            self.total_connections += 1
            self.ip_connections[ip] += 1

    async def remove_connection(self, ip: Annotated[
        str,
        Doc("Client IP address")
    ]) -> None:
        """Remove a connection."""
        async with self._lock:
            self.total_connections = max(0, self.total_connections - 1)
            self.ip_connections[ip] = max(0, self.ip_connections[ip] - 1)


class HTTPServer:
    """Async TCP HTTP server for FastAPI applications."""

    def __init__(
        self,
        app: Annotated[
            callable,
            Doc("ASGI application (FastAPI app)")
        ],
        config: Annotated[
            Config,
            Doc("Server configuration")
        ],
        middlewares: Annotated[
            list[BaseMiddleware] | None,
            Doc("List of middleware to apply")
        ] = None,
    ):
        self.app = app
        self.config = config
        self.middlewares = middlewares or []
        self.server: Optional[asyncio.Server] = None
        self.should_stop = False
        self.active_connections = 0
        self.connection_limiter = ConnectionLimiter(
            config.max_connections,
            config.max_connections_per_ip,
        )

    async def start(self, show_banner: Annotated[
        bool,
        Doc("Whether to show startup banner")
    ] = True) -> None:
        """Start the HTTP server."""
        self.server = await asyncio.start_server(
            self._handle_connection,
            self.config.host,
            self.config.port,
            reuse_address=True,
            reuse_port=True,
        )

        if show_banner:
            addr = self.server.sockets[0].getsockname()
            logger.server_start(addr[0], addr[1], self.config.workers)

        try:
            async with self.server:
                await self.server.serve_forever()
        except asyncio.CancelledError:
            self.should_stop = True
            self.server.close()
            await self.server.wait_closed()

    async def stop(self) -> None:
        """Gracefully stop the server."""
        self.should_stop = True
        if self.server:
            self.server.close()
            await self.server.wait_closed()

    def _get_content_length(self, headers: Annotated[
        list[tuple[bytes, bytes]],
        Doc("HTTP headers")
    ]) -> Annotated[
        int,
        Doc("Content-Length value or 0 if not found")
    ]:
        """Get content length from headers."""
        for name, value in headers:
            if name.lower() == b"content-length":
                try:
                    return int(value)
                except ValueError:
                    return 0
        return 0

    def _get_client_ip(self, client: Annotated[
        tuple,
        Doc("Client socket info (host, port)")
    ]) -> Annotated[
        str,
        Doc("Client IP address")
    ]:
        """Get client IP from socket info."""
        if client:
            return client[0]
        return "unknown"

    async def _handle_connection(
        self,
        reader: Annotated[
            asyncio.StreamReader,
            Doc("Stream reader for incoming data")
        ],
        writer: Annotated[
            asyncio.StreamWriter,
            Doc("Stream writer for outgoing data")
        ],
    ) -> None:
        """Handle a single client connection."""
        client = writer.get_extra_info("peername")
        server = writer.get_extra_info("sockname")
        client_ip = self._get_client_ip(client)

        if not await self.connection_limiter.can_connect(client_ip):
            writer.close()
            await writer.wait_closed()
            return

        await self.connection_limiter.add_connection(client_ip)

        try:
            await self._process_requests(reader, writer, client, server, client_ip)
        finally:
            await self.connection_limiter.remove_connection(client_ip)
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def _process_requests(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        client: tuple,
        server: tuple,
        client_ip: str,
    ) -> None:
        """Process requests on a connection."""
        keepalive_requests = 0

        while not self.should_stop and keepalive_requests < self.config.keepalive_requests:
            try:
                request_data = await asyncio.wait_for(
                    reader.read(8192),
                    timeout=self.config.header_timeout,
                )
            except asyncio.TimeoutError:
                break

            if not request_data:
                break

            parser = HttpParser(
                max_headers=self.config.max_headers,
                max_body_size=self.config.max_body_size,
                max_header_size=self.config.max_header_size,
                max_headers_total_size=self.config.max_headers_total_size,
            )

            request = parser.parse(request_data)

            if parser.get_status() == ParserState.ERROR:
                await ResponseWriter.write_response(
                    writer, 400, [], b'{"error": "Bad request"}',
                    keep_alive=False,
                )
                break

            start_time = time.perf_counter()

            scope = build_asgi_scope(request, client, server)

            content_length = self._get_content_length(request.headers)
            body = request.body

            if content_length > len(body):
                body_remaining = content_length - len(body)
                try:
                    additional = await asyncio.wait_for(
                        reader.read(body_remaining),
                        timeout=self.config.body_timeout,
                    )
                    body = body + additional
                except asyncio.TimeoutError:
                    await ResponseWriter.write_response(
                        writer, 408, [], b'{"error": "Request timeout"}',
                        keep_alive=False,
                    )
                    break

            async def receive():
                return {
                    "type": "http.request",
                    "body": body,
                    "more_body": False,
                }

            response_body = b""
            response_started = False
            response_status = 200
            response_headers = []

            async def send(message: dict):
                nonlocal response_body, response_started, response_status, response_headers
                if message["type"] == "http.response.start":
                    response_started = True
                    response_status = message.get("status", 200)
                    response_headers = message.get("headers", [])
                elif message["type"] == "http.response.body":
                    response_body += message.get("body", b"")

            try:
                await asyncio.wait_for(
                    self.app(scope, receive, send),
                    timeout=self.config.request_timeout,
                )
            except asyncio.TimeoutError:
                await ResponseWriter.write_response(
                    writer, 504, [], b'{"error": "Request timeout"}',
                    keep_alive=False,
                )
                break
            except Exception as e:
                logger.error(f"Application error: {e}")
                response_status = 500
                response_body = b'{"error": "Internal server error"}'
                response_headers = [[b"content-type", b"application/json"]]

            latency = time.perf_counter() - start_time

            log_entry = RequestLog(
                method=request.method,
                path=request.path,
                status=response_status,
                latency=latency,
                client_ip=client_ip,
            )
            logger.log_request(log_entry)

            success = await ResponseWriter.write_response(
                writer,
                response_status,
                response_headers,
                response_body,
                keep_alive=True,
            )

            if not success:
                break

            keepalive_requests += 1

            await asyncio.sleep(0.001)
