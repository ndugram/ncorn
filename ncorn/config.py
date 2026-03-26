from dataclasses import dataclass, field
from typing import Annotated

from annotated_doc import Doc


@dataclass
class Config:
    """Server configuration."""

    host: Annotated[
        str,
        Doc("IP address to bind the server to. Use '0.0.0.0' for all interfaces.")
    ] = "127.0.0.1"
    port: Annotated[
        int,
        Doc("Port number to bind the server to.")
    ] = 8000
    workers: Annotated[
        int,
        Doc("Number of worker processes to run. Use 1 for single process mode.")
    ] = 1
    reload: Annotated[
        bool,
        Doc("Enable auto-reload when source files change. Useful for development.")
    ] = False

    max_body_size: Annotated[
        int,
        Doc("Maximum allowed size of request body in bytes. Default: 16MB.")
    ] = 16 * 1024 * 1024
    max_header_size: Annotated[
        int,
        Doc("Maximum size of a single header in bytes.")
    ] = 8192
    max_headers_total_size: Annotated[
        int,
        Doc("Maximum total size of all headers combined in bytes.")
    ] = 65536

    header_timeout: Annotated[
        float,
        Doc("Timeout in seconds for reading request headers. Protects against Slowloris attacks.")
    ] = 30.0
    body_timeout: Annotated[
        float,
        Doc("Timeout in seconds for reading request body.")
    ] = 60.0
    request_timeout: Annotated[
        float,
        Doc("Timeout in seconds for the entire request processing.")
    ] = 10.0
    response_timeout: Annotated[
        float,
        Doc("Timeout in seconds for sending response to client.")
    ] = 10.0

    keepalive_timeout: Annotated[
        float,
        Doc("Timeout in seconds to keep idle connections alive.")
    ] = 5.0
    keepalive_requests: Annotated[
        int,
        Doc("Maximum number of requests allowed per keep-alive connection.")
    ] = 100

    max_headers: Annotated[
        int,
        Doc("Maximum number of headers allowed in a single request.")
    ] = 100

    max_connections: Annotated[
        int,
        Doc("Maximum number of concurrent connections the server can handle.")
    ] = 1000
    max_connections_per_ip: Annotated[
        int,
        Doc("Maximum number of concurrent connections from a single IP address.")
    ] = 50

    rate_limit_requests: Annotated[
        int,
        Doc("Maximum number of requests allowed per rate limit window.")
    ] = 100
    rate_limit_window: Annotated[
        float,
        Doc("Time window in seconds for rate limiting.")
    ] = 60.0

    write_buffer_limit: Annotated[
        int,
        Doc("Limit for write buffer size in bytes.")
    ] = 65536
    drain_timeout: Annotated[
        float,
        Doc("Timeout in seconds for draining write buffers.")
    ] = 1.0

    ip_whitelist: Annotated[
        list[str],
        Doc("List of IP addresses that are allowed to connect. Empty list means all allowed.")
    ] = field(default_factory=list)
    ip_blacklist: Annotated[
        list[str],
        Doc("List of IP addresses that are not allowed to connect.")
    ] = field(default_factory=list)

    enable_security_headers: Annotated[
        bool,
        Doc("Enable security headers in responses (X-Content-Type-Options, etc.).")
    ] = True

    waf_max_query_length: Annotated[
        int,
        Doc("Maximum length of query string in bytes for WAF protection.")
    ] = 4096

    ssl_keyfile: Annotated[
        str | None,
        Doc("Path to SSL key file for HTTPS. Leave empty to disable SSL.")
    ] = None
    ssl_certfile: Annotated[
        str | None,
        Doc("Path to SSL certificate file for HTTPS.")
    ] = None
    ssl_version: Annotated[
        int,
        Doc("SSL/TLS version: 2=TLSv1, 3=TLSv1.1, 4=TLSv1.2, 5=TLSv1.3. Default: TLSv1.3")
    ] = 5

    def __post_init__(self):
        if self.workers < 1:
            self.workers = 1
        if self.max_body_size < 0:
            self.max_body_size = 16 * 1024 * 1024
        if self.max_header_size < 256:
            self.max_header_size = 8192
        if self.max_headers_total_size < 1024:
            self.max_headers_total_size = 65536
        if self.header_timeout <= 0:
            self.header_timeout = 30.0
        if self.body_timeout <= 0:
            self.body_timeout = 60.0
        if self.request_timeout <= 0:
            self.request_timeout = 10.0
        if self.response_timeout <= 0:
            self.response_timeout = 10.0
        if self.keepalive_timeout <= 0:
            self.keepalive_timeout = 5.0
        if self.keepalive_requests < 1:
            self.keepalive_requests = 100
        if self.max_headers < 10:
            self.max_headers = 100
        if self.max_connections < 10:
            self.max_connections = 1000
        if self.max_connections_per_ip < 1:
            self.max_connections_per_ip = 50
        if self.rate_limit_requests < 1:
            self.rate_limit_requests = 100
        if self.rate_limit_window <= 0:
            self.rate_limit_window = 60.0
        if self.write_buffer_limit < 1024:
            self.write_buffer_limit = 65536
        if self.drain_timeout <= 0:
            self.drain_timeout = 1.0
        if self.waf_max_query_length < 64:
            self.waf_max_query_length = 4096
        if self.ssl_version < 2 or self.ssl_version > 5:
            self.ssl_version = 5
        if (self.ssl_keyfile and not self.ssl_certfile) or (not self.ssl_keyfile and self.ssl_certfile):
            raise ValueError("Both ssl_keyfile and ssl_certfile must be provided for SSL")
