# Configuration

## Server Configuration

The server can be configured using command line options or programmatically.

## Configuration Options

### Network Settings

- `host` - IP address to bind to (default: 127.0.0.1)
- `port` - Port number (default: 8000)
- `workers` - Number of worker processes (default: 1)

### Timeouts

- `header_timeout` - Maximum time to read request headers (default: 30.0 seconds)
- `body_timeout` - Maximum time to read request body (default: 60.0 seconds)
- `keepalive_timeout` - Keep-alive connection timeout (default: 5.0 seconds)

### Request Limits

- `max_body_size` - Maximum request body size (default: 16 MB)
- `max_headers` - Maximum number of headers (default: 100)
- `max_keepalive_requests` - Maximum requests per keep-alive connection (default: 100)

### Rate Limiting

- `rate_limit_requests` - Maximum requests per window (default: 100)
- `rate_limit_window` - Time window in seconds (default: 60.0)

## Programmatic Configuration

```python
from ncorn.config import Config
from ncorn.server import HTTPServer
from myapp import app

config = Config(
    host="0.0.0.0",
    port=8080,
    workers=4,
    max_body_size=32 * 1024 * 1024,
)

server = HTTPServer(app, config)
```
