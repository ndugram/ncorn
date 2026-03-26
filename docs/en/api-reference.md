# API Reference

## Command Line Interface

### ncorn

```bash
ncorn module:app [OPTIONS]
```

Main entry point for running ncorn server.

### ncorn config

```bash
ncorn config
```

Creates default `ncorn.json` configuration file.

## Python API

### Config

```python
from ncorn.config import Config
```

Configuration class for ncorn server.

```python
config = Config(
    host="127.0.0.1",
    port=8000,
    workers=1,
    reload=False,
    max_body_size=16 * 1024 * 1024,
    ssl_keyfile=None,
    ssl_certfile=None,
    ssl_version=5,
)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `host` | str | "127.0.0.1" | IP address to bind |
| `port` | int | 8000 | Port number |
| `workers` | int | 1 | Number of worker processes |
| `reload` | bool | False | Enable auto-reload |
| `max_body_size` | int | 16777216 | Max request body size |
| `max_header_size` | int | 8192 | Max single header size |
| `max_headers_total_size` | int | 65536 | Max total headers size |
| `header_timeout` | float | 30.0 | Header read timeout |
| `body_timeout` | float | 60.0 | Body read timeout |
| `request_timeout` | float | 10.0 | Request processing timeout |
| `keepalive_timeout` | float | 5.0 | Keep-alive timeout |
| `keepalive_requests` | int | 100 | Max requests per connection |
| `max_headers` | int | 100 | Max number of headers |
| `max_connections` | int | 1000 | Max concurrent connections |
| `max_connections_per_ip` | int | 50 | Max connections per IP |
| `rate_limit_requests` | int | 100 | Requests per window |
| `rate_limit_window` | float | 60.0 | Rate limit window |
| `ssl_keyfile` | str | None | SSL key file path |
| `ssl_certfile` | str | None | SSL certificate path |
| `ssl_version` | int | 5 | TLS version (2-5) |

### HTTPServer

```python
from ncorn.server import HTTPServer
```

HTTP server class.

```python
server = HTTPServer(app, config)
await server.start()
await server.stop()
```

#### Methods

##### start(show_banner=True)

Start the HTTP server.

##### stop()

Gracefully stop the server.

### CLI Functions

```python
from ncorn.cli import import_app, parse_args, main
```

#### import_app(app_spec: str)

Import FastAPI app from "module:app" string.

#### parse_args(args: Optional[list[str]] = None) -> argparse.Namespace

Parse command line arguments.

#### main(args: Optional[list[str]] = None) -> None

Main entry point.

### Middleware

```python
from ncorn.middleware import (
    ValidationMiddleware,
    RateLimitMiddleware,
    MiddlewareChain,
)
```

#### ValidationMiddleware

Validates HTTP requests (headers, body size).

#### RateLimitMiddleware

Implements IP-based rate limiting.

#### MiddlewareChain

Chains multiple middleware together.

## Exceptions

### ncorn exceptions

ncorn uses standard Python exceptions. Check individual middleware documentation for specific error handling.
