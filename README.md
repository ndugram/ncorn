<p align="center">
  <img src="./docs/logo.png" style="background:white; padding:12px; border-radius:10px; width:350">
</p>

<div align="center">

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://pypi.org/project/ncorn/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>

## Features

- **Fast Performance** - Built on asyncio for high performance
- **ASGI Compatible** - Full ASGI interface support for FastAPI
- **Production Ready** - Rate limiting, request validation, slowloris protection
- **Multi-Worker** - Support for multiple worker processes
- **Auto-Reload** - Development mode with file watching
- **Clean Logging** - Beautiful uvicorn-style console output
- **Security** - Header validation, body size limits, IP rate limiting

## Installation

```bash
pip install ncorn
```

## Quick Start

```bash
ncorn example_app:app
```

With custom host and port:

```bash
ncorn example_app:app --host 0.0.0.0 --port 8080
```

Multiple workers:

```bash
ncorn example_app:app --workers 4
```

Auto-reload on file changes:

```bash
ncorn example_app:app --reload
```

## Configuration

Create a config file:

```bash
ncorn config
```

This creates `ncorn.cnf` with default settings. You can edit this file and ncorn will use these settings by default.

Example configuration:

```json
{
    "host": "127.0.0.1",
    "port": 8000,
    "workers": 1,
    "reload": false,
    "max_body_size": 16777216,
    "header_timeout": 30.0,
    "rate_limit_requests": 100,
    "rate_limit_window": 60.0
}
```

Command line options override config file settings.

## CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `app` | Application in format `module:app` | Required |
| `--host` | Host to bind to | 127.0.0.1 |
| `--port` | Port to bind to | 8000 |
| `--workers` | Number of worker processes | 1 |
| `--reload` | Enable auto-reload on file changes | false |
| `--max-body-size` | Maximum request body size in bytes | 16777216 |
| `--header-timeout` | Header read timeout in seconds | 30.0 |
| `--rate-limit` | Rate limit requests per window | 100 |
| `--rate-limit-window` | Rate limit window in seconds | 60.0 |
| `--verbose` | Enable verbose logging | false |

## Example FastAPI App

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Example App")

class Item(BaseModel):
    name: str
    price: float
    tax: float | None = None

@app.get("/")
async def root():
    return {"message": "Hello from ncorn!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/items")
async def create_item(item: Item):
    total = item.price + (item.tax or 0)
    return {"name": item.name, "total": total}
```

Run it:

```bash
ncorn example_app:app
```

## Security Features

- **Max Body Size** - Limits request body to prevent DoS attacks
- **Header Validation** - Validates HTTP headers and rejects invalid requests
- **Slowloris Protection** - Timeout for header and body reads
- **IP Rate Limiting** - Limits requests per IP address

## Architecture

```
ncorn/
├── __init__.py       # Package init
├── main.py           # Entry point
├── cli.py            # CLI interface
├── server.py         # TCP server
├── protocol.py       # HTTP parser
├── asgi.py           # ASGI adapter
├── config.py         # Configuration
├── logging.py        # Logging
├── reload.py         # Auto-reload
└── middleware/
    ├── base.py       # Middleware base
    ├── validation.py # Request validation
    └── ratelimit.py  # Rate limiting
```

## License

MIT License - see [LICENSE](LICENSE) file for details.
