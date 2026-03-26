# Settings

ncorn can be configured via command line options, configuration file, or programmatically.

## Command Line Options

```bash
ncorn module:app [OPTIONS]
```

### Basic Options

| Option | Description | Default |
|--------|-------------|---------|
| `app` | Application in format 'module:app' | Required |
| `--host` | Host to bind to | 127.0.0.1 |
| `--port` | Port to bind to | 8000 |
| `--reload` | Enable auto-reload on file changes | false |
| `--workers` | Number of worker processes | 1 |

### Request Limits

| Option | Description | Default |
|--------|-------------|---------|
| `--max-body-size` | Maximum request body size in bytes | 16777216 (16MB) |
| `--max-headers` | Maximum number of headers | 100 |
| `--keepalive-requests` | Max requests per keep-alive connection | 100 |

### Timeouts

| Option | Description | Default |
|--------|-------------|---------|
| `--header-timeout` | Header read timeout in seconds | 30.0 |
| `--body-timeout` | Body read timeout in seconds | 60.0 |
| `--keepalive-timeout` | Keep-alive timeout in seconds | 5.0 |

### Rate Limiting

| Option | Description | Default |
|--------|-------------|---------|
| `--rate-limit` | Rate limit requests per window | 100 |
| `--rate-limit-window` | Rate limit window in seconds | 60.0 |

### SSL/TLS

| Option | Description | Default |
|--------|-------------|---------|
| `--ssl-keyfile` | Path to SSL key file | None |
| `--ssl-certfile` | Path to SSL certificate file | None |
| `--ssl-version` | TLS version (2=TLSv1, 3=TLSv1.1, 4=TLSv1.2, 5=TLSv1.3) | 5 |

### Other Options

| Option | Description | Default |
|--------|-------------|---------|
| `--verbose` | Enable verbose logging | false |

## Configuration File

ncorn can also be configured via `ncorn.json` file:

```json
{
  "host": "0.0.0.0",
  "port": 8000,
  "workers": 4,
  "reload": false,
  "max_body_size": 16777216,
  "ssl_keyfile": "certs/key.pem",
  "ssl_certfile": "certs/cert.pem",
  "ssl_version": 5
}
```

Command line options override config file settings.

## Programmatic Configuration

You can also configure ncorn programmatically:

```python
from ncorn.config import Config
from ncorn.server import HTTPServer
from myapp import app

config = Config(
    host="0.0.0.0",
    port=8080,
    workers=4,
    max_body_size=32 * 1024 * 1024,
    ssl_keyfile="certs/key.pem",
    ssl_certfile="certs/cert.pem",
)

server = HTTPServer(app, config)
```

## Environment Variables

ncorn supports configuration through environment variables:

- `NCORN_HOST` - Server host
- `NCORN_PORT` - Server port
- `NCORN_WORKERS` - Number of workers
- `NCORN_SSL_KEYFILE` - SSL key file path
- `NCORN_SSL_CERTFILE` - SSL certificate file path
